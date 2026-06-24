# Setup And Python Foundations

This document explains the environment and the Python shapes used across the repo.

## Environment Setup

Create and activate the virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m ipykernel install --user --name langchain-day1 --display-name "Python (langchain-day1)"
cp .env.example .env
```

Set the Gemini key:

```text
GOOGLE_API_KEY=...
```

Optional LangSmith settings:

```text
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=langchain-day1
```

Most scripts call:

```python
from dotenv import load_dotenv

load_dotenv()
```

That loads `.env` before the script creates models or graphs.

## Running Scripts

Run scripts from the repo root:

```bash
python scripts/10_checkpointer_basics.py
```

This matters because scripts read files from paths relative to the repo root.

## Python Concepts Used By The Repo

### Dictionaries

Many examples pass ticket data as dictionaries:

```python
ticket = {
    "id": "TCK-1001",
    "customer": "Maya",
    "message": "I was charged twice.",
}
```

Read values:

```python
ticket["message"]
```

Add or replace values:

```python
ticket["queue"] = "Billing"
```

### Lists

Messages, notes, and tool outputs often use lists:

```python
notes = [
    "customer reports duplicate charge",
    "billing policy applies",
]
```

Reducers later show how LangGraph can concatenate list updates.

### Functions

Nodes and tools are Python functions.

Graph node:

```python
def mark_received(state: dict) -> dict:
    return {"status": "received"}
```

Tool:

```python
@tool
def lookup_customer(customer_name: str) -> dict:
    """Look up a customer's support profile by customer name."""
    return CUSTOMERS[customer_name]
```

The difference is who calls them:

```text
graph node -> called by LangGraph edge flow
tool       -> called when the model requests it
```

### TypedDict

`TypedDict` documents the expected shape of a dictionary.

```python
from typing import TypedDict


class TicketState(TypedDict):
    ticket_id: str
    message: str
    status: str
```

This is still a dictionary at runtime:

```python
state = {
    "ticket_id": "TCK-1001",
    "message": "I was charged twice.",
    "status": "new",
}
```

LangGraph uses the type to understand the state schema.

### dataclass

`dataclass` is used for runtime context:

```python
from dataclasses import dataclass


@dataclass
class RequestContext:
    customer_id: str
    support_agent: str
```

Context is not state. It is read-only app information for one run.

## State As A Dictionary

LangGraph beginner examples use dictionary-shaped state.

State:

```python
{
    "ticket_id": "TCK-1001",
    "message": "I was charged twice.",
    "status": "new",
}
```

Node:

```python
def mark_received(state: TicketState) -> dict:
    return {"status": "received"}
```

Result after merge:

```python
{
    "ticket_id": "TCK-1001",
    "message": "I was charged twice.",
    "status": "received",
}
```

The returned dictionary is not a full replacement for the whole state.

It is an update.

## Comments And Output

In this repo:

```text
comments explain concepts
print output shows inspected values
markdown docs explain contracts and behavior
```

Avoid using `print()` as lecture text inside scripts. Keep explanations in comments and docs.
