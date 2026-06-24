# Agents, Tools, And Memory

This document explains the agent examples.

Scripts:

```bash
python scripts/13_agent_with_tools.py
python scripts/14_agent_memory_and_tools.py
```

## What `create_agent` Returns

`create_agent` returns a compiled LangGraph graph.

That matters because the agent follows LangGraph runtime rules:

```text
state updates
checkpointers
thread_id
messages state
tool messages
```

Basic shape:

```python
from langchain.agents import create_agent

agent = create_agent(
    model=model,
    tools=[lookup_customer, read_support_policy],
    system_prompt="You are a support triage assistant.",
    checkpointer=InMemorySaver(),
)
```

The agent is then invoked like a graph:

```python
result = agent.invoke(
    {"messages": [HumanMessage(content="Customer Maya was charged twice.")]},
    config={"configurable": {"thread_id": "support-tool-agent"}},
)
```

## Agent State Contract

LangChain's built-in agent state includes a `messages` field.

That is why the input uses:

```python
{"messages": [HumanMessage(content=text)]}
```

This is a state update, not the whole conversation.

If the agent has a checkpointer:

```text
thread_id
  -> load saved agent state
  -> merge newest messages
  -> run agent loop
  -> save updated state
```

During one run, the `messages` list can receive:

```text
HumanMessage
AIMessage requesting a tool call
ToolMessage containing the tool result
AIMessage with final answer
```

The script prints:

```python
result["messages"][-1].content
```

That means:

```text
show only the final message from the updated state
```

## What A Tool Is

A tool is a typed Python function the model is allowed to call.

Example:

```python
from langchain.tools import tool


@tool
def lookup_customer(customer_name: str) -> dict:
    """Look up a customer's support profile by customer name."""
    return CUSTOMERS.get(customer_name, {"error": "Customer not found."})
```

The tool contract includes:

| Part | Why It Matters |
| --- | --- |
| Function name | The model sees the tool name. Use clear names. |
| Type hints | LangChain builds an argument schema from them. |
| Docstring | The model uses this to decide when to call the tool. |
| Return value | The model receives this data after the tool runs. |

The function body is normal Python.

The model does not run arbitrary code. It can only request tools you provide.

## Agent Loop With Tools

Script:

```bash
python scripts/13_agent_with_tools.py
```

Tools:

```python
@tool
def lookup_customer(customer_name: str) -> dict:
    """Look up a customer's support profile by customer name."""
```

```python
@tool
def read_support_policy() -> str:
    """Read the support policy for severity, routing, and reply style."""
```

Loop:

```text
user sends ticket
  -> model reads message
  -> model decides it needs customer info
  -> lookup_customer runs
  -> model decides it needs policy
  -> read_support_policy runs
  -> model writes final answer
```

The code does not call the tools manually.

The model decides whether to call them based on:

```text
tool name
tool docstring
system prompt
user message
```

## Checkpointer In Agent Scripts

The agent is created with:

```python
checkpointer=InMemorySaver()
```

The run uses:

```python
config = {"configurable": {"thread_id": thread_id}}
```

Same `thread_id` means:

```text
continue the same agent conversation
```

Different `thread_id` means:

```text
use a different saved conversation
```

The checkpointer stores the agent's message state.

## Agent With Short-Term And Long-Term Memory

Script:

```bash
python scripts/14_agent_memory_and_tools.py
```

This script combines:

```text
tools
short-term chat history
long-term customer preferences
```

Short-term memory:

```text
checkpointer + thread_id
```

Long-term memory:

```text
store + namespace/key
```

The script creates long-term memory:

```python
store.put(
    ("customer_preferences", "Maya"),
    "tone",
    {"text": "Use a direct and calm tone."},
)
```

The agent reads it through a tool:

```python
@tool
def get_customer_preferences(customer_name: str) -> list[str]:
    """Read saved long-term support preferences for a customer."""
    memories = MEMORY_STORE.search(("customer_preferences", customer_name))
    return [item.value["text"] for item in memories]
```

The model can call this tool when preferences matter.

## Important Separation

These are different concepts:

| Concept | Example | Meaning |
| --- | --- | --- |
| Agent state update | `{"messages": [HumanMessage(...)]}` | New input for this run |
| Checkpoint key | `thread_id` | Short-term memory slot |
| Store namespace | `("customer_preferences", "Maya")` | Long-term memory location |
| Tool | `get_customer_preferences` | Function the model may call |

Do not treat a store as chat history.

Do not treat `thread_id` as a customer id unless your app intentionally chooses that mapping.

Do not put business input in config unless a LangChain or LangGraph runtime feature expects it there.

## Example Conversation

First turn:

```text
Customer Maya says she was charged twice for the annual plan.
```

The agent may call:

```text
lookup_customer("Maya")
read_support_policy()
get_customer_preferences("Maya")
```

Follow-up turn:

```text
Can you rewrite the reply with her preferences?
```

The agent can understand "her" because the checkpointer restored the earlier messages for the same `thread_id`.

The preferences still come from the store.
