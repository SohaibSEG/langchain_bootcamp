from operator import add
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langgraph.graph import START, StateGraph


class DefaultMergeState(TypedDict, total=False):
    ticket_id: str
    status: str
    note: str


def mark_received(state: DefaultMergeState) -> DefaultMergeState:
    # Default merge rule for a normal state field:
    # - if this node returns a key, that key is written into state
    # - if the key already exists, the old value is replaced
    # - keys not returned by the node stay unchanged
    return {"status": "received"}


def replace_note(state: DefaultMergeState) -> DefaultMergeState:
    return {"note": "support agent added a newer note"}


def build_default_merge_graph():
    graph = StateGraph(DefaultMergeState)
    graph.add_node("mark_received", mark_received)
    graph.add_node("replace_note", replace_note)

    graph.add_edge(START, "mark_received")
    graph.add_edge("mark_received", "replace_note")

    return graph.compile()


class ReducerState(TypedDict):
    ticket_id: str
    # A reducer tells LangGraph how to combine multiple updates to one field.
    #
    # Annotated[list[str], add] means:
    # - the field value is a list of strings
    # - when a node returns {"notes": [...]}, combine lists with operator.add
    # - for lists, operator.add means list concatenation
    notes: Annotated[list[str], add]


def add_billing_note(state: ReducerState) -> ReducerState:
    return {"notes": ["billing checked duplicate charge history"]}


def add_policy_note(state: ReducerState) -> ReducerState:
    return {"notes": ["policy says billing questions go to Billing queue"]}


def build_reducer_graph():
    graph = StateGraph(ReducerState)
    graph.add_node("add_billing_note", add_billing_note)
    graph.add_node("add_policy_note", add_policy_note)

    graph.add_edge(START, "add_billing_note")
    graph.add_edge("add_billing_note", "add_policy_note")

    return graph.compile()


class ParallelState(TypedDict):
    ticket_id: str
    # Parallel branches often need reducers because two nodes may write to the
    # same field during the same graph step.
    research_notes: Annotated[list[str], add]
    final_summary: str


def check_customer_profile(state: ParallelState) -> ParallelState:
    return {"research_notes": ["customer profile: Pro plan, active account"]}


def check_support_policy(state: ParallelState) -> ParallelState:
    return {"research_notes": ["policy: duplicate charge routes to Billing"]}


def summarize_research(state: ParallelState) -> ParallelState:
    return {
        "final_summary": " | ".join(state["research_notes"]),
    }


def build_parallel_graph():
    graph = StateGraph(ParallelState)
    graph.add_node("check_customer_profile", check_customer_profile)
    graph.add_node("check_support_policy", check_support_policy)
    graph.add_node("summarize_research", summarize_research)

    # Two edges from START means both branches can run before the join node.
    graph.add_edge(START, "check_customer_profile")
    graph.add_edge(START, "check_support_policy")

    # Both branches write to research_notes.
    # That is safe because research_notes has the add reducer.
    graph.add_edge("check_customer_profile", "summarize_research")
    graph.add_edge("check_support_policy", "summarize_research")

    return graph.compile()


def main() -> None:
    # Load .env even though this script is deterministic.
    # That lets LangSmith tracing env vars apply to graph runs:
    # LANGSMITH_TRACING, LANGSMITH_API_KEY, LANGSMITH_PROJECT, etc.
    load_dotenv()

    default_result = build_default_merge_graph().invoke(
        {
            "ticket_id": "TCK-1001",
            "status": "new",
            "note": "customer opened the ticket",
        }
    )
    print("default merge result:")
    print(default_result)

    reducer_result = build_reducer_graph().invoke(
        {
            "ticket_id": "TCK-1001",
            "notes": ["customer reports duplicate annual charge"],
        }
    )
    print("\nreducer result:")
    print(reducer_result)

    parallel_result = build_parallel_graph().invoke(
        {
            "ticket_id": "TCK-1001",
            "research_notes": [],
            "final_summary": "",
        }
    )
    print("\nparallel reducer result:")
    print(parallel_result)


if __name__ == "__main__":
    main()
