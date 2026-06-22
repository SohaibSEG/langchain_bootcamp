from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from rich.console import Console
from rich.panel import Panel


ROOT = Path(__file__).resolve().parents[1]
TICKETS_PATH = ROOT / "data" / "tickets.jsonl"
POLICY_PATH = ROOT / "data" / "support_policy.md"


def load_tickets(path: Path) -> list[dict[str, Any]]:
    tickets: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            tickets.append(json.loads(line))
    return tickets


def route_ticket(ticket: dict[str, Any]) -> str:
    text = f"{ticket['subject']} {ticket['message']}".lower()

    if "production" in text or "api" in text or "timeout" in text:
        return "Engineering Escalation"
    if "charged" in text or "invoice" in text or "billing" in text:
        return "Billing"
    if "sign in" in text or "password" in text or "access" in text:
        return "Account"
    return "Support"


def main() -> None:
    load_dotenv()

    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY is missing. Copy .env.example to .env and set it.")

    policy = POLICY_PATH.read_text(encoding="utf-8")
    tickets = load_tickets(TICKETS_PATH)

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    model = ChatGoogleGenerativeAI(model=model_name, temperature=0.2)

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                "You draft concise customer support replies. Follow the support policy exactly.\n\n{policy}",
            ),
            HumanMessagePromptTemplate.from_template(
                "Queue: {queue}\nCustomer: {customer}\nSubject: {subject}\nMessage: {message}\n\n"
                "Draft a reply in two short paragraphs.",
            ),
        ]
    )

    reply_chain = prompt | model | StrOutputParser()
    console = Console()

    for ticket in tickets:
        queue = route_ticket(ticket)
        reply = reply_chain.invoke(
            {
                "policy": policy,
                "queue": queue,
                "customer": ticket["customer"],
                "subject": ticket["subject"],
                "message": ticket["message"],
            }
        )

        title = f"{ticket['id']} -> {queue}"
        console.print(Panel(reply, title=title, subtitle=ticket["subject"]))


if __name__ == "__main__":
    main()
