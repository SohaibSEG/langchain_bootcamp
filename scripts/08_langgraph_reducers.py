from operator import add
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langgraph.graph import START, StateGraph


class TicketState(TypedDict):
    ticket_id: str
    # A reducer changes the merge rule for one field.
    # Annotated[list[str], add] tells LangGraph to combine note lists.
    notes: Annotated[list[str], add]


def add_billing_note(state: TicketState) -> TicketState:
    return {"notes": ["billing checked duplicate charge history"]}


def add_policy_note(state: TicketState) -> TicketState:
    return {"notes": ["policy says billing questions go to Billing queue"]}


def build_graph():
    graph = StateGraph(TicketState)
    graph.add_node("add_billing_note", add_billing_note)
    graph.add_node("add_policy_note", add_policy_note)

    graph.add_edge(START, "add_billing_note")
    graph.add_edge("add_billing_note", "add_policy_note")

    return graph.compile()


def main() -> None:
    load_dotenv()

    result = build_graph().invoke(
        {
            "ticket_id": "TCK-1001",
            "notes": ["customer reports duplicate annual charge"],
        }
    )

    print("reducer result:")
    print(result)


if __name__ == "__main__":
    main()
