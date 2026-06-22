import json
import os
from pathlib import Path
from typing import Literal, TypedDict

from dotenv import load_dotenv
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "data" / "support_policy.md"


class TriageDecision(BaseModel):
    category: Literal["billing", "account", "engineering", "product", "support"]
    severity: Literal["urgent", "high", "normal"]
    queue: Literal["Billing", "Account", "Engineering Escalation", "Support"]
    next_step: Literal["reply", "escalate"]
    reason: str


class ResponseDraft(BaseModel):
    customer_reply: str
    internal_note: str = Field(description="Private note for the support team.")


class TicketState(TypedDict):
    ticket_id: str
    customer: str
    channel: str
    subject: str
    message: str
    policy: str
    category: str
    severity: str
    queue: str
    next_step: str
    reason: str
    customer_reply: str
    internal_note: str


def build_graph():
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    triage_model = ChatGoogleGenerativeAI(model=model_name, temperature=0)
    response_model = ChatGoogleGenerativeAI(model=model_name, temperature=0.2)

    triage_chain = (
        ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(
                    "Triage this support ticket using the support policy.\n\n{policy}",
                ),
                HumanMessagePromptTemplate.from_template(
                    "Ticket: {ticket_id}\n"
                    "Customer: {customer}\n"
                    "Channel: {channel}\n"
                    "Subject: {subject}\n"
                    "Message: {message}\n\n"
                    "Choose next_step='escalate' only when the ticket needs urgent handling.",
                ),
            ]
        )
        | triage_model.with_structured_output(TriageDecision)
    )

    response_chain = (
        ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(
                    "Draft a customer support response using the support policy.\n\n{policy}",
                ),
                HumanMessagePromptTemplate.from_template(
                    "Customer: {customer}\n"
                    "Subject: {subject}\n"
                    "Message: {message}\n\n"
                    "Queue: {queue}\n"
                    "Severity: {severity}\n"
                    "Reason: {reason}\n\n"
                    "Write a customer reply and an internal note.",
                ),
            ]
        )
        | response_model.with_structured_output(ResponseDraft)
    )

    escalation_chain = (
        ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(
                    "Draft an urgent escalation response using the support policy.\n\n{policy}",
                ),
                HumanMessagePromptTemplate.from_template(
                    "Customer: {customer}\n"
                    "Subject: {subject}\n"
                    "Message: {message}\n\n"
                    "Queue: {queue}\n"
                    "Severity: {severity}\n"
                    "Reason: {reason}\n\n"
                    "Write a calm customer reply and an internal escalation note.",
                ),
            ]
        )
        | response_model.with_structured_output(ResponseDraft)
    )

    def triage(state: TicketState) -> TicketState:
        decision = triage_chain.invoke(state)
        return {
            **state,
            "category": decision.category,
            "severity": decision.severity,
            "queue": decision.queue,
            "next_step": decision.next_step,
            "reason": decision.reason,
        }

    def reply(state: TicketState) -> TicketState:
        draft = response_chain.invoke(state)
        return {
            **state,
            "customer_reply": draft.customer_reply,
            "internal_note": draft.internal_note,
        }

    def escalate(state: TicketState) -> TicketState:
        draft = escalation_chain.invoke(state)
        return {
            **state,
            "customer_reply": draft.customer_reply,
            "internal_note": draft.internal_note,
        }

    graph = StateGraph(TicketState)
    graph.add_node("triage", triage)
    graph.add_node("reply", reply)
    graph.add_node("escalate", escalate)

    graph.add_edge(START, "triage")
    graph.add_conditional_edges(
        "triage",
        lambda state: state["next_step"],
        {
            "reply": "reply",
            "escalate": "escalate",
        },
    )
    graph.add_edge("reply", END)
    graph.add_edge("escalate", END)

    return graph.compile()


def main() -> None:
    load_dotenv()

    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY is missing. Copy .env.example to .env and set it.")

    initial_state: TicketState = {
        "ticket_id": "TCK-1004",
        "customer": "Leo",
        "channel": "web",
        "subject": "Production API timeout",
        "message": "Our checkout integration is timing out for every payment request.",
        "policy": POLICY_PATH.read_text(encoding="utf-8"),
        "category": "",
        "severity": "",
        "queue": "",
        "next_step": "",
        "reason": "",
        "customer_reply": "",
        "internal_note": "",
    }

    result = build_graph().invoke(initial_state)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
