from typing import TypedDict

from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, StateGraph


class TicketState(TypedDict, total=False):
    ticket_id: str
    note: str
    status: str


def mark_received(state: TicketState) -> TicketState:
    # A node receives the current state and returns only the fields it wants to
    # add or change. LangGraph merges this update into the state.
    #
    # Default merge rule:
    # - returned keys are written into state
    # - existing keys not returned stay as they are
    # - if a returned key already exists, the new value replaces the old value
    return {"status": "received"}


def build_graph_without_checkpointer():
    graph = StateGraph(TicketState)
    graph.add_node("mark_received", mark_received)
    graph.add_edge(START, "mark_received")

    # No checkpointer means the graph does not remember anything after invoke()
    # finishes. Each run starts from the input you pass to invoke().
    return graph.compile()


def build_graph_with_checkpointer():
    graph = StateGraph(TicketState)
    graph.add_node("mark_received", mark_received)
    graph.add_edge(START, "mark_received")

    # A checkpointer saves graph state after each run.
    # InMemorySaver keeps state only inside this Python process.
    return graph.compile(checkpointer=InMemorySaver())


def main() -> None:
    # Load .env so deterministic graph runs can still be traced in LangSmith.
    load_dotenv()

    print("Graph without a checkpointer:")
    stateless_app = build_graph_without_checkpointer()

    first_result = stateless_app.invoke(
        {"ticket_id": "TCK-A", "note": "customer opened an invoice export ticket"}
    )
    second_result = stateless_app.invoke({"note": "customer added the invoice id"})

    print("first run:")
    print(first_result)
    print("second run:")
    print(second_result)

    print("\nGraph with a checkpointer:")
    app = build_graph_with_checkpointer()

    # This config is not ticket data. It tells LangGraph where to save/load
    # runtime state.
    #
    # "thread_id" is a LangGraph-defined key used by checkpointers.
    # You choose the value ("ticket-a"), but the key name must be "thread_id".
    # Think of it as the memory slot for one conversation or workflow.
    ticket_a = {"configurable": {"thread_id": "ticket-a"}}
    ticket_b = {"configurable": {"thread_id": "ticket-b"}}

    app.invoke(
        {"ticket_id": "TCK-A", "note": "customer opened an invoice export ticket"},
        config=ticket_a,
    )
    app.invoke(
        # Before this run starts, the checkpointer loads ticket-a state:
        # {"ticket_id": "TCK-A", "note": "...", "status": "received"}
        #
        # Then this input is merged into that state:
        # - note is replaced
        # - ticket_id stays because this input does not provide a new ticket_id
        # - status stays until the node writes it again
        {"note": "customer added the invoice id"},
        config=ticket_a,
    )

    app.invoke(
        {"ticket_id": "TCK-B", "note": "customer reported an API timeout"},
        config=ticket_b,
    )

    print("ticket-a latest state:")
    print(app.get_state(ticket_a).values)

    print("\nticket-b latest state:")
    print(app.get_state(ticket_b).values)

    # Read the output:
    # - without a checkpointer, the second run has no ticket_id
    # - with a checkpointer, ticket-a keeps its ticket_id across runs
    # - ticket-a and ticket-b are separate because they use different thread_id values
    # - note changed because new input replaced the old note


if __name__ == "__main__":
    main()
