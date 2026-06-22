from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from rich import print


class TicketState(TypedDict):
    subject: str
    message: str
    route: str
    response_type: str


def classify(state: TicketState) -> TicketState:
    text = f"{state['subject']} {state['message']}".lower()

    if "production" in text or "api" in text or "timeout" in text:
        route = "engineering"
    elif "charged" in text or "invoice" in text:
        route = "billing"
    elif "sign in" in text or "password" in text:
        route = "account"
    else:
        route = "support"

    return {**state, "route": route}


def choose_response_type(state: TicketState) -> str:
    if state["route"] == "engineering":
        return "escalate"
    return "draft"


def draft_reply(state: TicketState) -> TicketState:
    return {**state, "response_type": "standard customer reply"}


def escalate(state: TicketState) -> TicketState:
    return {**state, "response_type": "urgent escalation note"}


def build_graph():
    graph = StateGraph(TicketState)
    graph.add_node("classify", classify)
    graph.add_node("draft_reply", draft_reply)
    graph.add_node("escalate", escalate)

    graph.add_edge(START, "classify")
    graph.add_conditional_edges(
        "classify",
        choose_response_type,
        {
            "draft": "draft_reply",
            "escalate": "escalate",
        },
    )
    graph.add_edge("draft_reply", END)
    graph.add_edge("escalate", END)

    return graph.compile()


def main() -> None:
    app = build_graph()
    result = app.invoke(
        {
            "subject": "Production API timeout",
            "message": "Checkout requests are timing out for live payments.",
            "route": "",
            "response_type": "",
        }
    )

    print("[bold]LangGraph preview state[/bold]")
    print(result)


if __name__ == "__main__":
    main()
