from typing import Literal, TypedDict

from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, StateGraph
from langgraph.types import Command, interrupt


class ReviewState(TypedDict):
    ticket_id: str
    customer: str
    issue: str
    draft_reply: str
    review_decision: str
    final_status: str


def draft_reply(state: ReviewState) -> ReviewState:
    # Deterministic draft so the new concept is only human review.
    return {
        "draft_reply": (
            f"Hi {state['customer']}, we received your report: {state['issue']}. "
            "Our support team is reviewing it now."
        )
    }


def human_review(state: ReviewState) -> ReviewState:
    # interrupt(...) pauses the graph and returns this payload to the caller.
    #
    # A checkpointer is required because LangGraph must save the current state
    # and resume this same node later.
    decision: Literal["approve", "reject"] = interrupt(
        {
            "ticket_id": state["ticket_id"],
            "draft_reply": state["draft_reply"],
            "allowed_decisions": ["approve", "reject"],
        }
    )

    if decision == "approve":
        return {
            "review_decision": "approve",
            "final_status": "ready_to_send",
        }

    return {
        "review_decision": "reject",
        "final_status": "needs_rewrite",
    }


def build_graph():
    graph = StateGraph(ReviewState)
    graph.add_node("draft_reply", draft_reply)
    graph.add_node("human_review", human_review)
    graph.add_edge(START, "draft_reply")
    graph.add_edge("draft_reply", "human_review")

    # The checkpointer stores the paused graph state.
    # Without it, Command(resume=...) would not know where to continue.
    return graph.compile(checkpointer=InMemorySaver())


def main() -> None:
    load_dotenv()

    app = build_graph()

    # thread_id selects the saved paused state for this review workflow.
    config = {"configurable": {"thread_id": "review-tck-2001"}}

    first_result = app.invoke(
        {
            "ticket_id": "TCK-2001",
            "customer": "Maya",
            "issue": "duplicate annual charge",
            "draft_reply": "",
            "review_decision": "",
            "final_status": "",
        },
        config=config,
    )

    interrupt_payload = first_result["__interrupt__"][0].value
    print("review payload:")
    print(interrupt_payload)

    decision = input("Decision [approve/reject]: ").strip().lower()
    if decision not in {"approve", "reject"}:
        decision = "reject"

    # Command(resume=...) sends the human decision back into the paused node.
    final_result = app.invoke(Command(resume=decision), config=config)

    print("\nfinal state:")
    print(final_result)


if __name__ == "__main__":
    main()
