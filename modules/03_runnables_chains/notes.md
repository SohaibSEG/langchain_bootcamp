# Runnables And Chains

This document explains LangChain's composition model.

Scripts:

```bash
python modules/03_runnables_chains/scripts/02_runnables_building_blocks.py
python modules/02_gemini_langchain/scripts/03_gemini_summarization_chain.py
python modules/03_runnables_chains/scripts/04_ticket_classification_chain.py
python modules/03_runnables_chains/scripts/05_support_ticket_pipeline.py
```

## Runnable

A runnable is an object with a common execution interface.

Common methods:

| Method | Meaning |
| --- | --- |
| `invoke(input)` | Run once. |
| `batch(inputs)` | Run many inputs. |
| `stream(input)` | Stream output chunks. |

Why this matters:

```text
prompt templates are runnables
models are runnables
parsers are runnables
custom Python functions can become runnables
```

Because they share the same interface, they can be composed.

## Pipe Operator

The pipe operator connects runnables:

```python
chain = prompt | model | parser
```

Data flows left to right:

```text
input dict
  -> prompt creates messages
  -> model creates AI response
  -> parser extracts final value
```

Example:

```python
result = chain.invoke(
    {"message": "Customer cannot export invoices."}
)
```

## RunnableLambda

`RunnableLambda` wraps a normal Python function.

Example:

```python
from langchain_core.runnables import RunnableLambda


def normalize_ticket(ticket: dict) -> dict:
    return {
        "id": ticket["id"],
        "message": ticket["message"].strip(),
    }


normalize = RunnableLambda(normalize_ticket)
```

Invoke it:

```python
normalize.invoke(
    {
        "id": "TCK-1001",
        "message": "  I was charged twice.  ",
    }
)
```

Result:

```python
{
    "id": "TCK-1001",
    "message": "I was charged twice.",
}
```

Use `RunnableLambda` when regular Python logic should be part of a LangChain pipeline.

## RunnableParallel

`RunnableParallel` runs multiple branches from the same input.

Example:

```python
from langchain_core.runnables import RunnableParallel

parallel = RunnableParallel(
    normalized=normalize_ticket_runnable,
    priority=priority_runnable,
)
```

Input:

```python
{"id": "TCK-1001", "message": "I was charged twice."}
```

Output shape:

```python
{
    "normalized": {...},
    "priority": "high",
}
```

Use it when two calculations do not depend on each other.

## RunnablePassthrough

`RunnablePassthrough` keeps the original input available.

It is often used with `.assign(...)`.

Example shape:

```python
from langchain_core.runnables import RunnablePassthrough

pipeline = RunnablePassthrough.assign(
    normalized=normalize_ticket_runnable,
    priority=priority_runnable,
)
```

Input:

```python
{"id": "TCK-1001", "message": "I was charged twice."}
```

Output:

```python
{
    "id": "TCK-1001",
    "message": "I was charged twice.",
    "normalized": {...},
    "priority": "high",
}
```

Use it when later steps need both the original input and computed fields.

## Runnable Config

Runnables accept optional config:

```python
result = runnable.invoke(
    input_data,
    config={
        "run_name": "support_ticket_pipeline",
        "tags": ["lesson", "runnables"],
        "metadata": {"script": "02"},
    },
)
```

Common uses:

```text
LangSmith tracing
callbacks
run names
tags
runtime options
```

Do not put core business data in config unless a LangChain/LangGraph runtime feature expects it there.

Business data should usually be normal input.

## Chain

A chain is a sequence of runnables.

Example:

```python
chain = prompt | model | StrOutputParser()
```

The chain is also a runnable:

```python
chain.invoke({"message": "Customer says invoice export fails."})
```

This is why LangChain composition scales:

```text
small runnable
  -> bigger chain
  -> reusable component
  -> graph node
  -> agent tool
```

## Support Pipeline

Script:

```bash
python modules/03_runnables_chains/scripts/05_support_ticket_pipeline.py
```

The support pipeline combines:

```text
data loading
prompting
model triage
structured output
reply generation
```

It is still a linear script.

LangGraph is introduced when the same scenario needs named state-machine steps and runtime memory.
