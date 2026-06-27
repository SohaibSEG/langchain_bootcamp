# Human In The Loop

This document explains human review with LangGraph interrupts and agent tool approval.

Scripts:

```bash
python modules/06_human_in_the_loop/scripts/17_human_review_basics.py
python modules/06_human_in_the_loop/scripts/18_agent_human_review_tool.py
```

## Why Human Review Exists

Some workflow steps should not happen automatically.

Examples:

```text
send customer email
issue refund
close account
change billing plan
delete data
escalate to on-call engineer
```

The model can draft or propose the action. In these scripts, the human can approve or reject risky actions.

## Core Runtime Contract

Human review uses three pieces:

```text
interrupt(...)       -> pause the graph and return a review payload
checkpointer         -> save paused state
Command(resume=...)  -> continue from the pause point
```

The checkpointer is required. Without it, LangGraph cannot resume the exact paused graph state.

## Basic Interrupt Flow

Script:

```bash
python modules/06_human_in_the_loop/scripts/17_human_review_basics.py
```

Graph:

```text
START -> draft_reply -> human_review
```

The review node pauses:

```python
from langgraph.types import interrupt

decision = interrupt(
    {
        "ticket_id": state["ticket_id"],
        "draft_reply": state["draft_reply"],
        "allowed_decisions": ["approve", "reject"],
    }
)
```

The value passed to `interrupt(...)` is returned to the caller.

The caller receives a result containing:

```python
{
    "__interrupt__": [
        Interrupt(
            value={
                "ticket_id": "TCK-2001",
                "draft_reply": "...",
                "allowed_decisions": ["approve", "reject"],
            }
        )
    ]
}
```

## Resume Flow

After the reviewer chooses a decision, resume with:

```python
from langgraph.types import Command

final_result = app.invoke(
    Command(resume="approve"),
    config=config,
)
```

The `config` must use the same `thread_id`:

```python
config = {"configurable": {"thread_id": "review-tck-2001"}}
```

Same `thread_id` means:

```text
resume the same paused workflow
```

Different `thread_id` means:

```text
there is no matching paused state to resume
```

## State After Review

The review node receives the resumed value as the return value of `interrupt(...)`.

```python
decision = interrupt(...)
```

If approved:

```python
{
    "review_decision": "approve",
    "final_status": "ready_to_send",
}
```

If rejected:

```python
{
    "review_decision": "reject",
    "final_status": "needs_rewrite",
}
```

## Agent Tool Review

Script:

```bash
python modules/06_human_in_the_loop/scripts/18_agent_human_review_tool.py
```

This script uses an agent with two tools:

```python
@tool
def create_internal_note(ticket_id: str, note: str) -> str:
    """Create an internal support note."""
```

```python
@tool
def send_customer_email(to: str, subject: str, body: str) -> str:
    """Send an email to a customer."""
```

Internal notes are allowed automatically. Customer email requires review.

The script runs as a chat loop.

Normal support questions can be answered normally.

Messages that ask the agent to email a customer should trigger the risky tool:

```text
Ticket TCK-3001. Maya cannot export invoices. Email maya@example.com.
```

That flow should pause for review before `send_customer_email` executes.

The script formats the review payload before printing it:

```text
Review required:

Action 1: send_customer_email
Allowed decisions: approve, reject
Arguments:
- subject: ...
- to: ...
- body:
  ...
```

The underlying interrupt payload is a dictionary with `action_requests` and `review_configs`, but the formatted output is easier to inspect.

## Middleware

Middleware is code that wraps part of the agent runtime.

In this example, middleware watches tool calls before they execute.

Without middleware:

```text
agent decides to call send_customer_email
  -> tool executes immediately
```

With human-in-the-loop middleware:

```text
agent decides to call send_customer_email
  -> middleware pauses the graph
  -> human approves or rejects
  -> tool executes only if approved
```

This is useful because the tool code does not need to contain review logic.

The review policy lives at the agent boundary.

## HumanInTheLoopMiddleware

The agent uses middleware:

```python
from langchain.agents.middleware import HumanInTheLoopMiddleware

safe_note_tool_name = create_internal_note.name
risky_email_tool_name = send_customer_email.name

HumanInTheLoopMiddleware(
    interrupt_on={
        safe_note_tool_name: False,
        risky_email_tool_name: {
            "allowed_decisions": ["approve", "reject"],
        },
    },
    description_prefix="Customer email requires review",
)
```

Read this as:

```text
create_internal_note -> does not pause
send_customer_email  -> pauses before tool execution
```

Use `tool.name` instead of repeating raw strings. The `@tool` decorator creates a tool object with a stable `.name` property.

The risky action is not executed until the reviewer resumes with approval.

## Agent Review Flow

```text
user request
  -> agent may call create_internal_note
  -> agent proposes send_customer_email
  -> middleware interrupts before email tool runs
  -> reviewer approves or rejects
  -> same thread_id resumes agent
  -> email tool runs only if approved
```

## Resume Decision Shape

The agent middleware expects decisions in this shape:

```python
Command(
    resume={
        "decisions": [
            {"type": "approve"}
        ]
    }
)
```

Reject:

```python
Command(
    resume={
        "decisions": [
            {"type": "reject"}
        ]
    }
)
```

This is different from the basic interrupt script, where `Command(resume="approve")` is enough.

Why the difference?

```text
basic graph interrupt -> your node decides the resume value shape
agent HITL middleware -> middleware expects a decisions list
```

## What To Teach

Human review is not a model feature. It is a workflow feature.

The model can propose an action. The graph controls whether that action actually happens.

Key separation:

```text
model decision  -> "I want to send this email"
human decision  -> "approved" or "rejected"
tool execution  -> happens only after approval
```

This example intentionally supports only `approve` and `reject`.

An `edit` decision is possible in broader HITL designs, but it should be introduced separately after the basic pause/resume contract is clear.

## Common Mistakes

Do not resume with a different `thread_id`.

Do not run risky tools before review.

Do not store the human decision only in local variables; put the result into state if later nodes need it.

Do not use human review for every tiny step. Use it for actions with real risk.
