# Lab 04: Runnables

## Goal

Learn the common interface behind LangChain composition. Runnables are the main building block LangChain uses to compose prompts, models, parsers, branches, and full chains.

## Core Idea

A runnable is anything that can be invoked with input and return output through a common interface.

The most important method today is:

```python
runnable.invoke(input_value)
```

The runnable example is:

```bash
python scripts/02_runnables_building_blocks.py
```

That script prints small flow graphs before each example so you can see how data moves through the runnable pipeline.

## Minimal Example

```python
from langchain_core.runnables import RunnableLambda

uppercase = RunnableLambda(lambda text: text.upper())
result = uppercase.invoke("billing issue")
print(result)
```

## Why It Matters

Once components share a common interface, they can be composed:

```python
trim = RunnableLambda(lambda text: text.strip())
uppercase = RunnableLambda(lambda text: text.upper())

chain = trim | uppercase
print(chain.invoke("  billing issue  "))
```

This prepares you for prompt-model-parser chains.

## Components In The Script

`RunnableLambda` wraps a normal Python function so it can use the LangChain runnable interface.

```python
normalize = RunnableLambda(normalize_ticket)
normalize.invoke(ticket)
```

`RunnableParallel` sends the same input to multiple named steps and returns a dictionary of their outputs.

```python
RunnableParallel(
    ticket=RunnablePassthrough(),
    queue=route,
    priority=priority,
)
```

`RunnablePassthrough` returns the input unchanged. In the runnable script, it keeps the cleaned ticket available while the other branches compute queue and priority.

## Pipeline Flow

```text
ticket dict
   |
   v
normalize
   |
   v
cleaned ticket dict
   |
   +--------------------------+--------------------------+
   |                          |                          |
   v                          v                          v
ticket=RunnablePassthrough    queue=route                priority=priority_for
   |                          |                          |
   +--------------------------+--------------------------+
                              |
                              v
                    {"ticket", "queue", "priority"}
                              |
                              v
                          summarize
                              |
                              v
                       display string
```

## What To Notice

- The first examples do not need a model.
- Plain strings make the runnable interface easier to see.
- The `|` operator means "pass the output to the next step."
- `RunnableParallel` lets one input feed multiple runnable steps.
- `RunnablePassthrough` keeps the original input available inside a parallel step.
- `.batch()` applies the same runnable to many inputs.
