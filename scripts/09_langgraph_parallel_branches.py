from operator import add
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langgraph.graph import START, StateGraph


class TicketState(TypedDict):
    ticket_id: str
    # Parallel branches often write to the same field in the same graph step.
    # A reducer gives LangGraph a clear rule for merging those updates.
    research_notes: Annotated[list[str], add]
    final_summary: str


def check_customer_profile(state: TicketState) -> TicketState:
    return {"research_notes": ["customer profile: Pro plan, active account"]}


def check_support_policy(state: TicketState) -> TicketState:
    return {"research_notes": ["policy: duplicate charge routes to Billing"]}


def summarize_research(state: TicketState) -> TicketState:
    return {"final_summary": " | ".join(state["research_notes"])}


def build_graph():
    graph = StateGraph(TicketState)
    graph.add_node("check_customer_profile", check_customer_profile)
    graph.add_node("check_support_policy", check_support_policy)
    graph.add_node("summarize_research", summarize_research)

    # Two edges from START create two branches for the same input state.
    graph.add_edge(START, "check_customer_profile")
    graph.add_edge(START, "check_support_policy")

    # The branches join at summarize_research.
    # research_notes can accept both branch outputs because it has a reducer.
    graph.add_edge("check_customer_profile", "summarize_research")
    graph.add_edge("check_support_policy", "summarize_research")

    return graph.compile()


def main() -> None:
    load_dotenv()

    result = build_graph().invoke(
        {
            "ticket_id": "TCK-1001",
            "research_notes": [],
            "final_summary": "",
        }
    )

    print("parallel branch result:")
    print(result)


if __name__ == "__main__":
    main()
