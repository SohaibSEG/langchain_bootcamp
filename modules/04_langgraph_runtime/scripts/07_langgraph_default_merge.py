from typing import TypedDict

from dotenv import load_dotenv
from langgraph.graph import START, StateGraph


class TicketState(TypedDict, total=False):
    ticket_id: str
    status: str
    note: str


def mark_received(state: TicketState) -> TicketState:
    # Normal state fields use replacement.
    # This node returns "status", so the old status is replaced.
    return {"status": "received"}


def add_support_note(state: TicketState) -> TicketState:
    # This node returns "note", so the old note is replaced.
    # Fields not returned by this node stay as they are.
    return {"note": "support agent added a newer note"}


def build_graph():
    graph = StateGraph(TicketState)
    graph.add_node("mark_received", mark_received)
    graph.add_node("add_support_note", add_support_note)

    graph.add_edge(START, "mark_received")
    graph.add_edge("mark_received", "add_support_note")

    return graph.compile()


def main() -> None:
    # Deterministic graphs can still be traced by LangSmith.
    # The tracing configuration comes from .env.
    load_dotenv()

    result = build_graph().invoke(
        {
            "ticket_id": "TCK-1001",
            "status": "new",
            "note": "customer opened the ticket",
        }
    )

    print("default merge result:")
    print(result)


if __name__ == "__main__":
    main()
