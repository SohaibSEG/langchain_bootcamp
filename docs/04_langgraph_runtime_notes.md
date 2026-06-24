# LangGraph Runtime

This document explains the runtime concepts used by the LangGraph scripts.

The goal is to understand how LangGraph moves data through a graph before adding agents or complex workflows.

## Scripts Covered

```bash
python scripts/06_langgraph_state_machine_preview.py
python scripts/07_langgraph_reducers_parallel.py
python scripts/08_checkpointer_basics.py
python scripts/09_runtime_context_basics.py
python scripts/10_store_basics.py
python scripts/11_store_with_runtime_context.py
python scripts/12_chat_memory_graph.py
```

## Mental Model

LangGraph is useful when an application has named workflow steps.

In this repo, the workflow is support-ticket processing:

```text
receive ticket
  -> triage
  -> reply or escalate
  -> final response
```

A LangGraph app is built from:

```text
state  -> the data object moving through the graph
node   -> a function that reads state and returns updates
edge   -> a connection from one node to another
graph  -> the compiled workflow
```

The most important rule:

```text
nodes do not mutate state directly
nodes return updates
LangGraph merges those updates into state
```

## Basic State Graph

The smallest useful graph has:

```python
from typing import TypedDict
from langgraph.graph import START, StateGraph


class TicketState(TypedDict):
    ticket_id: str
    message: str
    status: str


def mark_received(state: TicketState) -> dict:
    return {"status": "received"}


graph = StateGraph(TicketState)
graph.add_node("mark_received", mark_received)
graph.add_edge(START, "mark_received")

app = graph.compile()
```

Run it:

```python
result = app.invoke({
    "ticket_id": "TCK-1001",
    "message": "I was charged twice.",
    "status": "new",
})
```

Result:

```python
{
    "ticket_id": "TCK-1001",
    "message": "I was charged twice.",
    "status": "received",
}
```

The node returned:

```python
{"status": "received"}
```

LangGraph merged that update into the existing state.

## Default Merge Rules

By default, state fields are replaced.

Default rules:

```text
new key              -> added to state
existing key         -> replaced by the new value
missing input key    -> old saved value stays, if there is saved state
node returned key    -> written into state
node omitted key     -> current value stays
```

Example:

```python
state = {
    "ticket_id": "TCK-1001",
    "status": "new",
    "note": "customer opened ticket",
}

node_update = {
    "status": "received",
}
```

Merged result:

```python
{
    "ticket_id": "TCK-1001",
    "status": "received",
    "note": "customer opened ticket",
}
```

`status` changed. `ticket_id` and `note` stayed.

## State Machine Preview

Script:

```bash
python scripts/06_langgraph_state_machine_preview.py
```

This script uses Gemini inside LangGraph nodes.

Graph:

```text
START
  |
  v
triage
  |
  |-- next_step = reply ----> reply ----> END
  |
  |-- next_step = escalate -> escalate -> END
```

The state shape:

```python
class TicketState(TypedDict):
    ticket_id: str
    customer: str
    channel: str
    subject: str
    message: str
    policy: str
    category: str
    severity: str
    queue: str
    next_step: str
    reason: str
    customer_reply: str
    internal_note: str
```

The `triage` node writes:

```text
category
severity
queue
next_step
reason
```

The conditional edge reads:

```python
lambda state: state["next_step"]
```

Then LangGraph chooses the next node:

```python
{
    "reply": "reply",
    "escalate": "escalate",
}
```

## Reducers

Script:

```bash
python scripts/07_langgraph_reducers_parallel.py
```

Default merge is replacement. Sometimes replacement is not what you want.

For example, multiple nodes may need to add notes to the same list.

Use a reducer when updates should be combined.

```python
from operator import add
from typing import Annotated, TypedDict


class ReducerState(TypedDict):
    ticket_id: str
    notes: Annotated[list[str], add]
```

This tells LangGraph:

```text
notes is a list[str]
when updates arrive, combine old and new lists with operator.add
```

For lists, `operator.add` means concatenation:

```python
["first note"] + ["second note"]
```

Result:

```python
["first note", "second note"]
```

Node example:

```python
def add_billing_note(state: ReducerState) -> dict:
    return {"notes": ["billing checked duplicate charge history"]}
```

If the starting state is:

```python
{
    "ticket_id": "TCK-1001",
    "notes": ["customer reports duplicate annual charge"],
}
```

After two nodes add notes, the result is:

```python
{
    "ticket_id": "TCK-1001",
    "notes": [
        "customer reports duplicate annual charge",
        "billing checked duplicate charge history",
        "policy says billing questions go to Billing queue",
    ],
}
```

## Parallel Branches

Reducers become important when branches run in parallel.

Graph shape:

```text
START
  |--------------------------|
  v                          v
check_customer_profile   check_support_policy
  |                          |
  |--------------------------|
              v
       summarize_research
```

Both parallel nodes write to the same field:

```python
research_notes: Annotated[list[str], add]
```

Branch one:

```python
def check_customer_profile(state: ParallelState) -> dict:
    return {"research_notes": ["customer profile: Pro plan, active account"]}
```

Branch two:

```python
def check_support_policy(state: ParallelState) -> dict:
    return {"research_notes": ["policy: duplicate charge routes to Billing"]}
```

Because `research_notes` has a reducer, LangGraph can combine both updates.

Without the reducer, two parallel writes to the same field would be ambiguous.

## Checkpointers

Script:

```bash
python scripts/08_checkpointer_basics.py
```

A checkpointer saves graph state by thread.

Compile with a checkpointer:

```python
from langgraph.checkpoint.memory import InMemorySaver

app = graph.compile(checkpointer=InMemorySaver())
```

Invoke with a `thread_id`:

```python
config = {
    "configurable": {
        "thread_id": "ticket-a",
    }
}

app.invoke(input_state, config=config)
```

`thread_id` is a LangGraph-defined key.

You choose the value:

```text
ticket-a
customer-123
session-abc
```

But the key name must be:

```text
thread_id
```

Without a checkpointer:

```text
invoke 1 gets input A
invoke 2 gets input B
invoke 2 does not remember input A
```

With a checkpointer:

```text
invoke 1 saves state under thread_id
invoke 2 with same thread_id loads saved state
invoke 2 input is merged into saved state
```

Example:

```python
app.invoke(
    {"ticket_id": "TCK-A", "note": "customer opened ticket"},
    config={"configurable": {"thread_id": "ticket-a"}},
)

app.invoke(
    {"note": "customer added invoice id"},
    config={"configurable": {"thread_id": "ticket-a"}},
)
```

The second run does not provide `ticket_id`.

The checkpointer loads it from saved state.

Final state:

```python
{
    "ticket_id": "TCK-A",
    "note": "customer added invoice id",
    "status": "received",
}
```

## Runtime Context

Script:

```bash
python scripts/09_runtime_context_basics.py
```

Runtime context is data about the current run.

It is not graph state.

Use context for information the application already knows and the graph should read:

```text
customer_id
support_agent
tenant_id
locale
permissions
```

Define context:

```python
from dataclasses import dataclass


@dataclass
class RequestContext:
    customer_id: str
    support_agent: str
```

Tell the graph about the context type:

```python
graph = StateGraph(TicketState, context_schema=RequestContext)
```

Read it inside a node:

```python
from langgraph.runtime import Runtime


def attach_request_context(
    state: TicketState,
    runtime: Runtime[RequestContext],
) -> dict:
    return {
        "customer_id": runtime.context.customer_id,
        "assigned_to": runtime.context.support_agent,
    }
```

Invoke with context:

```python
result = app.invoke(
    {
        "subject": "Invoice export failed",
        "message": "The export button fails.",
        "assigned_to": "",
        "customer_id": "",
    },
    context=RequestContext(
        customer_id="cust_1001",
        support_agent="Nadia",
    ),
)
```

State is updated by nodes.

Context is read by nodes.

## Store

Script:

```bash
python scripts/10_store_basics.py
```

A store is long-term application memory.

Compare it with a checkpointer:

| Concept | Saves | Scope | Access |
| --- | --- | --- | --- |
| Checkpointer | Graph state | One `thread_id` | `config["configurable"]["thread_id"]` |
| Store | App data | Across threads | namespace + key |

Create a store:

```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
```

Write data:

```python
store.put(
    ("customer_preferences", "cust_1001"),
    "tone",
    {"text": "keep the tone direct and calm"},
)
```

Read one item:

```python
item = store.get(("customer_preferences", "cust_1001"), "tone")
print(item.value)
```

Search a namespace:

```python
items = store.search(("customer_preferences", "cust_1001"))
for item in items:
    print(item.key, item.value)
```

Namespace:

```python
("customer_preferences", "cust_1001")
```

Key:

```python
"tone"
```

Value:

```python
{"text": "keep the tone direct and calm"}
```

## Store With Runtime Context

Script:

```bash
python scripts/11_store_with_runtime_context.py
```

This combines store and context.

The context tells the graph which customer is active:

```python
context=RequestContext(customer_id="cust_1001")
```

The store contains preferences:

```python
store.put(
    ("customer_preferences", "cust_1001"),
    "language",
    {"text": "reply in English"},
)
```

Compile the graph with the store:

```python
app = graph.compile(store=store)
```

Inside a node:

```python
def load_customer_preferences(
    state: TicketState,
    runtime: Runtime[RequestContext],
) -> dict:
    namespace = ("customer_preferences", runtime.context.customer_id)
    memories = runtime.store.search(namespace)
    return {
        "preferences": [item.value["text"] for item in memories],
    }
```

The node uses:

```text
runtime.context -> which customer?
runtime.store   -> what long-term data exists?
```

## Chat Memory Graph

Script:

```bash
python scripts/12_chat_memory_graph.py
```

Chat memory is graph state plus a checkpointer.

The graph state is `MessagesState`.

That state has a `messages` field.

Each turn sends only the newest message:

```python
result = app.invoke(
    {"messages": [HumanMessage(content=text)]},
    config={"configurable": {"thread_id": thread_id}},
)
```

The checkpointer loads earlier messages for the same `thread_id`.

So this input:

```python
{"messages": [HumanMessage(content="What did I ask before?")]}
```

does not mean "this is the whole conversation."

It means:

```text
load old messages for thread_id
append this new HumanMessage
run the graph
save updated messages
```
