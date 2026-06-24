import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, MessagesState, StateGraph


def build_graph():
    model = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        temperature=0.2,
    )

    def call_model(state: MessagesState) -> dict:
        # MessagesState has one field: messages.
        # With a checkpointer, LangGraph reloads the old messages for this
        # thread before this node runs.
        messages = [
            SystemMessage(
                content=(
                    "You are a support assistant. Remember details from this "
                    "conversation and use them in later replies."
                )
            ),
            *state["messages"],
        ]
        response = model.invoke(messages)
        return {"messages": [response]}

    graph = StateGraph(MessagesState)
    graph.add_node("chat", call_model)
    graph.add_edge(START, "chat")

    # The checkpointer saves the message list after every turn.
    # Without this, each invoke() would only see the newest message.
    return graph.compile(checkpointer=InMemorySaver())


def main() -> None:
    load_dotenv()

    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY is missing. Copy .env.example to .env and set it.")

    app = build_graph()
    thread_id = input("Thread id [ticket-tck-2001]: ").strip() or "ticket-tck-2001"

    # "thread_id" is the LangGraph checkpoint key.
    # Same thread_id = continue the same chat memory.
    # Different thread_id = start/use a different chat memory.
    config = {"configurable": {"thread_id": thread_id}}

    print("Type a message. Type 'exit' to stop.")

    while True:
        text = input("\nYou: ").strip()
        if text.lower() in {"exit", "quit"}:
            break
        if not text:
            continue

        result = app.invoke(
            # Send only the new message. The checkpointer supplies the older
            # messages for this thread.
            {"messages": [HumanMessage(content=text)]},
            config=config,
        )
        print(f"Assistant: {result['messages'][-1].content}")


if __name__ == "__main__":
    main()
