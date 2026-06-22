from __future__ import annotations

from typing import Any

from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough
from rich import print


Ticket = dict[str, Any]


def normalize_ticket(ticket: Ticket) -> Ticket:
    """Clean user-provided text fields without changing the original dictionary."""
    return {
        **ticket,
        "subject": ticket["subject"].strip(),
        "message": ticket["message"].strip(),
    }


def route_ticket(ticket: Ticket) -> str:
    """Choose the support queue from simple keyword rules."""
    text = f"{ticket['subject']} {ticket['message']}".lower()

    if "production" in text or "api" in text or "timeout" in text:
        return "Engineering Escalation"
    if "charged" in text or "invoice" in text or "billing" in text:
        return "Billing"
    if "sign in" in text or "password" in text or "access" in text:
        return "Account"
    return "Support"


def priority_for(ticket: Ticket) -> str:
    """Choose a priority label from simple keyword rules."""
    text = f"{ticket['subject']} {ticket['message']}".lower()

    if "production" in text or "timeout" in text or "charged twice" in text:
        return "urgent"
    return "normal"


def format_summary(result: dict[str, Any]) -> str:
    """Turn the parallel runnable output into one readable string."""
    ticket = result["ticket"]
    return (
        f"{ticket['id']} | {result['priority'].upper()} | {result['queue']} | "
        f"{ticket['subject']}"
    )


def main() -> None:
    ticket = {
        "id": "TCK-1004",
        "subject": "  Production API timeout  ",
        "message": "  Checkout requests are timing out for live payments.  ",
    }

    # RunnableLambda wraps a regular Python callable so it can use the LangChain
    # runnable interface: .invoke(), .batch(), composition with |, and more.
    normalize = RunnableLambda(normalize_ticket)
    route = RunnableLambda(route_ticket)
    priority = RunnableLambda(priority_for)
    summarize = RunnableLambda(format_summary)

    # RunnableParallel sends the same input to multiple child runnables and
    # returns a dictionary with one result per named child.
    #
    # RunnablePassthrough returns the input unchanged. Here it keeps the cleaned
    # ticket available next to the derived queue and priority values.
    #
    # The | operator composes runnables from left to right:
    # output from normalize becomes input to RunnableParallel,
    # output from RunnableParallel becomes input to summarize.
    #
    # Flow:
    # ticket -> normalize -> parallel(ticket, queue, priority) -> summarize
    runnable_pipeline = (
        normalize
        | RunnableParallel(
            ticket=RunnablePassthrough(),
            queue=route,
            priority=priority,
        )
        | summarize
    )

    print("[bold]One RunnableLambda[/bold]")
    print(normalize.invoke(ticket))

    print("\n[bold]Composed runnable pipeline[/bold]")
    print(runnable_pipeline.invoke(ticket))

    print("\n[bold]Batch invocation[/bold]")
    # .batch() runs the same runnable once for each item in the input list.
    print(
        runnable_pipeline.batch(
            [
                ticket,
                {
                    "id": "TCK-1001",
                    "subject": "Charged twice for annual plan",
                    "message": "My card shows two annual charges.",
                },
            ]
        )
    )


if __name__ == "__main__":
    main()
