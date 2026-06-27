import json
import os
from pathlib import Path
from typing import Any, Literal

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field


# This script lives at modules/03_runnables_chains/scripts/.
# parents[3] is the repository root, no matter where the repo was cloned.
ROOT = Path(__file__).resolve().parents[3]
TICKETS_PATH = ROOT / "data" / "tickets.jsonl"
POLICY_PATH = ROOT / "data" / "support_policy.md"


class TriageDecision(BaseModel):
    # Gemini will fill this schema through with_structured_output().
    # Literal values keep the routing options small and predictable.
    category: Literal["billing", "account", "engineering", "product", "support"]
    severity: Literal["urgent", "high", "normal"]
    queue: Literal["Billing", "Account", "Engineering Escalation", "Support"]
    reason: str = Field(description="One short reason for the routing decision.")


def load_tickets(path: Path) -> list[dict[str, Any]]:
    # JSON Lines format: one ticket dictionary per line.
    tickets: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            tickets.append(json.loads(line))
    return tickets


def main() -> None:
    # Load GOOGLE_API_KEY and optional GEMINI_MODEL from .env.
    load_dotenv()

    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY is missing. Copy .env.example to .env and set it.")

    # The policy is plain Markdown, but it becomes context in both prompts.
    policy = POLICY_PATH.read_text(encoding="utf-8")
    tickets = load_tickets(TICKETS_PATH)

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Use one stable model instance for triage and one slightly freer instance
    # for customer-facing reply wording.
    classifier = ChatGoogleGenerativeAI(model=model_name, temperature=0)
    writer = ChatGoogleGenerativeAI(model=model_name, temperature=0.2)

    # First chain: ticket -> Gemini -> validated TriageDecision object.
    triage_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                "Classify and route support tickets using this policy:\n\n{policy}",
            ),
            HumanMessagePromptTemplate.from_template(
                "Subject: {subject}\nMessage: {message}",
            ),
        ]
    )
    triage_chain = triage_prompt | classifier.with_structured_output(TriageDecision)

    # Second chain: ticket + triage decision -> Gemini -> reply text.
    reply_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                "Draft concise customer support replies using this policy:\n\n{policy}",
            ),
            HumanMessagePromptTemplate.from_template(
                "Customer: {customer}\n"
                "Subject: {subject}\n"
                "Message: {message}\n\n"
                "Category: {category}\n"
                "Severity: {severity}\n"
                "Queue: {queue}\n"
                "Routing reason: {reason}\n\n"
                "Write two short paragraphs.",
            ),
        ]
    )
    reply_chain = reply_prompt | writer | StrOutputParser()

    for ticket in tickets:
        # Gemini performs classification and routing here.
        decision = triage_chain.invoke(
            {
                "policy": policy,
                "subject": ticket["subject"],
                "message": ticket["message"],
            }
        )

        # The reply prompt receives the model's routing decision as structured
        # context, instead of recalculating routing in Python.
        reply = reply_chain.invoke(
            {
                "policy": policy,
                "customer": ticket["customer"],
                "subject": ticket["subject"],
                "message": ticket["message"],
                "category": decision.category,
                "severity": decision.severity,
                "queue": decision.queue,
                "reason": decision.reason,
            }
        )

        print(f"\n{ticket['id']} -> {decision.queue} ({decision.severity})")
        print(f"Reason: {decision.reason}")
        print(reply)


if __name__ == "__main__":
    main()
