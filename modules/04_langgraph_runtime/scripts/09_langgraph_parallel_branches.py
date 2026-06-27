from operator import add, or_
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langgraph.graph import START, StateGraph


def highest_severity(current: str, update: str) -> str:
    # Reducers are normal Python functions with this shape:
    # reducer(current_value, incoming_update) -> merged_value
    #
    # Use a custom reducer when a scalar field needs a business rule.
    # Here, if two parallel branches produce different severities, the
    # ticket keeps the highest severity instead of choosing an arbitrary value.
    severity_rank = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4,
    }

    # The reducer may receive the channel's empty starting value before it sees
    # the value supplied in the graph input.
    if not current:
        return update

    if severity_rank[update] > severity_rank[current]:
        return update

    return current


class TicketState(TypedDict, total=False):
    ticket_id: str

    # Parallel branches often write to the same field in the same graph step.
    # A reducer gives LangGraph a clear rule for merging those updates.
    #
    # Common reducer choices:
    # - operator.add for list accumulation, such as research notes.
    # - operator.or_ for booleans where any branch can turn the value on.
    # - custom functions for scalar business rules, such as highest severity.
    # - langgraph.graph.message.add_messages for chat history. It appends new
    #   messages and can replace existing messages with the same message id.
    #
    # Without a reducer, only one parallel branch may write to a field in the
    # same graph step. If two branches write to the same normal field, LangGraph
    # raises INVALID_CONCURRENT_GRAPH_UPDATE.
    research_notes: Annotated[list[str], add]
    severity: Annotated[str, highest_severity]
    needs_human_review: Annotated[bool, or_]

    # final_summary does not need a reducer because only summarize_research
    # writes to it after the parallel branches have joined.
    final_summary: str


def check_customer_profile(state: TicketState) -> TicketState:
    return {
        "research_notes": ["customer profile: Pro plan, active account"],
        "severity": "medium",
        "needs_human_review": False,
    }


def check_support_policy(state: TicketState) -> TicketState:
    return {
        "research_notes": ["policy: duplicate charge routes to Billing"],
        "severity": "high",
        "needs_human_review": True,
    }


def summarize_research(state: TicketState) -> TicketState:
    return {
        "final_summary": (
            f"severity={state['severity']}; "
            f"needs_human_review={state['needs_human_review']}; "
            f"notes={' | '.join(state['research_notes'])}"
        )
    }


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
            "severity": "low",
            "needs_human_review": False,
            "final_summary": "",
        }
    )

    print("parallel branch result:")
    print(result)


if __name__ == "__main__":
    main()
