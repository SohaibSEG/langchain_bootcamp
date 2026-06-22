from __future__ import annotations

from typing import Any

from langchain_core.runnables import RunnableBranch, RunnableLambda
from rich import print


Ticket = dict[str, Any]


def has_any(ticket: Ticket, keywords: tuple[str, ...]) -> bool:
    text = f"{ticket['subject']} {ticket['message']}".lower()
    return any(keyword in text for keyword in keywords)


def route_name(ticket: Ticket) -> str:
    if has_any(ticket, ("production", "api", "timeout")):
        return "Engineering Escalation"
    if has_any(ticket, ("charged", "invoice", "billing")):
        return "Billing"
    if has_any(ticket, ("sign in", "password", "access")):
        return "Account"
    return "Support"


def billing_reply(ticket: Ticket) -> str:
    return f"{ticket['id']}: send to Billing and ask for the invoice or charge date."


def account_reply(ticket: Ticket) -> str:
    return f"{ticket['id']}: send to Account and ask for the sign-in email."


def engineering_reply(ticket: Ticket) -> str:
    return f"{ticket['id']}: escalate to Engineering with production impact noted."


def support_reply(ticket: Ticket) -> str:
    return f"{ticket['id']}: keep in Support and answer the product question."


def add_route(output: str, ticket: Ticket) -> dict[str, str]:
    return {
        "ticket_id": ticket["id"],
        "route": route_name(ticket),
        "next_action": output,
    }


def main() -> None:
    tickets = [
        {
            "id": "TCK-1001",
            "subject": "Charged twice for annual plan",
            "message": "My card shows two annual charges.",
        },
        {
            "id": "TCK-1002",
            "subject": "Cannot sign in after password reset",
            "message": "Sign in loops back to the same page.",
        },
        {
            "id": "TCK-1004",
            "subject": "Production API timeout",
            "message": "Checkout requests are timing out for live payments.",
        },
    ]

    branch = RunnableBranch(
        (lambda ticket: has_any(ticket, ("production", "api", "timeout")), RunnableLambda(engineering_reply)),
        (lambda ticket: has_any(ticket, ("charged", "invoice", "billing")), RunnableLambda(billing_reply)),
        (lambda ticket: has_any(ticket, ("sign in", "password", "access")), RunnableLambda(account_reply)),
        RunnableLambda(support_reply),
    )

    annotate = RunnableLambda(lambda ticket: add_route(branch.invoke(ticket), ticket))

    print("[bold]Runnable branching[/bold]")
    for result in annotate.batch(tickets):
        print(result)

if __name__ == "__main__":
    main()
