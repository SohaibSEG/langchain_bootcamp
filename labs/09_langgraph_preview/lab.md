# Lab 09: LangGraph Preview

## Goal

Understand why LangGraph becomes useful after simple chains and branches.

## Why Graphs

The Day 1 pipeline is linear with a small branch:

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

This is the bridge to Day 2. In a graph:

- state moves through named nodes
- nodes update state
- edges decide what runs next
- conditional edges represent routing

The optional runnable preview is:

```bash
python scripts/06_langgraph_state_machine_preview.py
```

It uses deterministic Python nodes only. It does not introduce agents, tools, memory, or persistence.

## What To Take Away

You do not need to build a full graph today. The goal is to recognize the problem LangGraph solves: coordinating stateful workflows with named steps and branching paths.
