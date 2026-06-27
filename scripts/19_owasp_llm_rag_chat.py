import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama, OllamaEmbeddings


COLLECTION_NAME = "owasp_top10_llm"


def repo_root() -> Path:
    current = Path.cwd()
    if (current / "README.md").exists():
        return current
    if (current.parent / "README.md").exists():
        return current.parent
    return Path(__file__).resolve().parents[1]


def repo_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return repo_root() / path


def format_documents(documents) -> str:
    formatted = []

    for index, document in enumerate(documents, start=1):
        page = document.metadata.get("page", "unknown")
        chunk_id = document.metadata.get("chunk_id", "unknown")

        # The citation label is included in the context so the model can cite
        # the source without inventing page or chunk identifiers.
        formatted.append(
            f"[{index}] page={page}; chunk={chunk_id}\n{document.page_content}"
        )

    return "\n\n".join(formatted)


def format_history(history: list[tuple[str, str]]) -> str:
    if not history:
        return "No previous turns."

    # Keep the chat prompt small. Retrieval context is more important than a
    # long conversation transcript for this introductory RAG example.
    recent_turns = history[-4:]
    return "\n".join(
        f"User: {question}\nAssistant: {answer}" for question, answer in recent_turns
    )


def build_rag_chain(retriever, model):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "You answer questions using only the retrieved OWASP Top 10 "
                    "for LLM Applications context.\n"
                    "If the context does not contain enough information, say that "
                    "the retrieved context does not support an answer.\n"
                    "Cite sources using page and chunk ids from the context labels.\n"
                    "Do not use outside knowledge."
                ),
            ),
            (
                "human",
                (
                    "Conversation history:\n{history}\n\n"
                    "Retrieved context:\n{context}\n\n"
                    "Question: {question}"
                ),
            ),
        ]
    )

    return prompt | model | StrOutputParser()


def load_vector_store():
    chroma_dir = repo_path(os.getenv("CHROMA_PERSIST_DIR", "data/chroma_owasp_llm"))

    if not chroma_dir.exists() or not any(chroma_dir.iterdir()):
        raise FileNotFoundError(
            f"Missing Chroma index at {chroma_dir}. "
            "Run notebooks/09_rag_embeddings_chroma_indexing.ipynb first."
        )

    embeddings = OllamaEmbeddings(
        model=os.getenv("OLLAMA_EMBEDDING_MODEL", "embeddinggemma"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(chroma_dir),
    )


def main() -> None:
    load_dotenv()

    try:
        vector_store = load_vector_store()
    except FileNotFoundError as exc:
        print(exc)
        return

    retriever = vector_store.as_retriever(search_kwargs={"k": 4})

    model = ChatOllama(
        model=os.getenv("OLLAMA_CHAT_MODEL", "gemma4:e4b"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0,
    )

    rag_chain = build_rag_chain(retriever, model)
    history = []

    print("OWASP LLM RAG chat. Type 'exit' to stop.")

    while True:
        question = input("\nYou: ").strip()

        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue

        try:
            documents = retriever.invoke(question)
            answer = rag_chain.invoke(
                {
                    "question": question,
                    "context": format_documents(documents),
                    "history": format_history(history),
                }
            )
        except Exception as exc:
            print(f"RAG call failed: {exc}")
            print("Check that Ollama is running and the required models are pulled.")
            continue

        print("\nRetrieved:")
        for document in documents:
            page = document.metadata.get("page", "unknown")
            chunk_id = document.metadata.get("chunk_id", "unknown")
            print(f"- page={page}; chunk={chunk_id}")

        print("\nAssistant:")
        print(answer)

        history.append((question, answer))


if __name__ == "__main__":
    main()
