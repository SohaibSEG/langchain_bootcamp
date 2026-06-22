# Lab 07: Branching and Routing

## Goal

Choose different workflow paths for different support tickets.

## Why Branching Appears

A billing refund request, a sign-in problem, and a production API outage should not all follow the same workflow.

The simplest router can be plain Python:

```python
def route_ticket(ticket: dict) -> str:
    text = f"{ticket['subject']} {ticket['message']}".lower()

    if "charged" in text or "invoice" in text:
        return "billing"
    if "sign in" in text or "password" in text:
        return "account"
    if "production" in text or "api" in text or "timeout" in text:
        return "technical"
    return "support"
```

The runnable branching example is:

```bash
python scripts/03_runnable_branching.py
```

## What To Notice

Branching does not require an agent. A simple deterministic function is often the clearest first version.

Once this version is clear, you can compare it with a model-based classifier and decide which one is easier to trust.

Runnable branching keeps the workflow inside the runnable interface, but it also introduces more places to track conditions, outputs, and state. That added complexity is the opening for the LangGraph discussion.

## What Comes Next

The final Day 1 script combines:

- ticket loading
- deterministic routing
- Gemini-backed response drafting
- concise terminal output
