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

## Scenario

You are routing tickets into queues before drafting replies. Start with deterministic rules, then put those rules behind runnable branches.

## Pipeline Target

```text
ticket
  -> route by keyword
  -> choose queue-specific next action
  -> print route and action
```

## Practice Lab

Open `scripts/03_runnable_branching.py` and adjust the routing rules.

1. Add a route for cancellation requests.
2. Change the router so production issues are checked before billing issues.
3. Add a new ticket that should hit the default Support path.
4. Add one more branch for invoice download requests.
5. Print the route and next action for every sample ticket.
