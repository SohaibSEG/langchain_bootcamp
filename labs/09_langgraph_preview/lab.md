# Lab 09: LangGraph Preview

## Goal

Preview the same ticket workflow as named graph steps.

## Why Graphs

The support pipeline is linear with a small branch:

```text
load -> route -> draft -> print
```

Real support workflows often need more structure:

```text
receive ticket
  -> classify
  -> ask for missing details
  -> escalate if urgent
  -> draft reply
  -> human review
  -> final response
```

At that point, a graph is easier to reason about than one long chain or deeply nested `if` statements.

## Minimal State Machine Sketch

```python
from typing import TypedDict

class TicketState(TypedDict):
    subject: str
    message: str
    route: str
    draft: str
```

In the preview graph:

- state moves through named nodes
- nodes update state
- edges decide what runs next
- conditional edges represent routing

The optional runnable preview is:

```bash
python scripts/06_langgraph_state_machine_preview.py
```

The script uses deterministic Python nodes only.

## Practice Lab

Run the preview script and inspect the graph-shaped ticket state.

```bash
python scripts/06_langgraph_state_machine_preview.py
```

1. Identify the state fields.
2. Identify the graph nodes.
3. Identify where routing happens.
4. Add a new state field named `priority`.
5. Add a node that sets `priority` to `"urgent"` for production API issues.
