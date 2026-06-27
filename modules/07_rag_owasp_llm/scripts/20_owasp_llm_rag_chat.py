import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage
from langchain_core.prompts import SystemMessagePromptTemplate
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, MessagesState, StateGraph


COLLECTION_NAME = "owasp_top10_llm"
RETRIEVED_CHUNKS = 4

REPO_ROOT = Path(__file__).resolve().parents[3]
CHROMA_DIR = REPO_ROOT / "data" / "chroma_owasp_llm"


def message_text(message) -> str:
    content = message.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        return "\n".join(part for part in parts if part)
    return str(content)


def latest_user_text(messages) -> str:
    for message in reversed(messages):
        if message.type == "human":
            return message_text(message)
    return ""


def format_documents(documents) -> str:
    formatted = []

    for index, document in enumerate(documents, start=1):
        formatted.append(f"Context chunk {index}:\n{document.page_content}")

    return "\n\n".join(formatted)


def build_system_prompt():
    return SystemMessagePromptTemplate.from_template(
        (
            "You answer questions using only the retrieved OWASP Top 10 "
            "for LLM Applications context.\n"
            "Use the message history only to understand references in the current question.\n"
            "If the context does not contain enough information, say that "
            "the retrieved context does not support an answer.\n"
            "Do not use outside knowledge.\n\n"
            "Retrieved OWASP context:\n{context}"
        )
    )


def load_vector_store():
    if not CHROMA_DIR.exists() or not any(CHROMA_DIR.iterdir()):
        raise FileNotFoundError(
            f"Missing Chroma index at {CHROMA_DIR}. "
            "Run modules/07_rag_owasp_llm/scripts/19_owasp_llm_build_index.py first."
        )

    embeddings = OllamaEmbeddings(
        model=os.getenv("OLLAMA_EMBEDDING_MODEL", "embeddinggemma"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )


def build_graph(retriever, model):
    system_prompt = build_system_prompt()

    def answer(state: MessagesState) -> dict:
        # The checkpointer restores state["messages"] before this node runs.
        # Keep that history as real HumanMessage/AIMessage objects instead of
        # flattening it into a string.
        question = latest_user_text(state["messages"])
        documents = retriever.invoke(question)
        system_message = system_prompt.format(context=format_documents(documents))
        response = model.invoke([system_message, *state["messages"]])
        return {"messages": [response]}

    graph = StateGraph(MessagesState)
    graph.add_node("answer", answer)
    graph.add_edge(START, "answer")

    return graph.compile(checkpointer=InMemorySaver())


def main() -> None:
    load_dotenv()

    try:
        vector_store = load_vector_store()
    except FileNotFoundError as exc:
        print(exc)
        return

    retriever = vector_store.as_retriever(search_kwargs={"k": RETRIEVED_CHUNKS})

    model = ChatOllama(
        model=os.getenv("OLLAMA_CHAT_MODEL", "gemma4:e4b"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0,
    )

    app = build_graph(retriever, model)
    thread_id = input("Thread id [owasp-rag]: ").strip() or "owasp-rag"
    config = {"configurable": {"thread_id": thread_id}}

    print("OWASP LLM RAG chat. Type 'exit' to stop.")

    while True:
        question = input("\nYou: ").strip()

        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue

        try:
            result = app.invoke(
                {"messages": [HumanMessage(content=question)]},
                config=config,
            )
        except Exception as exc:
            print(f"RAG call failed: {exc}")
            print("Check that Ollama is running and the required models are pulled.")
            continue

        print("Assistant:")
        print(message_text(result["messages"][-1]))


if __name__ == "__main__":
    main()
