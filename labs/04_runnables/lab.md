# Lab 04: Runnables

## Goal

Learn the common interface behind LangChain composition. Runnables are the main building block LangChain uses to compose prompts, models, parsers, branches, and full chains.

## Core Idea

A runnable is anything that can be invoked with input and return output through a common interface.

The most important method today is:

```python
runnable.invoke(input_value)
```

Start with the small Python-only runnable example:

```bash
python scripts/02_runnables_building_blocks.py
```

Then run the simplest Gemini-backed chain:

```bash
python scripts/03_gemini_summarization_chain.py
```

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

## Simplest Gemini Chain

The summarization script uses one straight line of runnable composition:

```text
message -> prompt -> Gemini -> string parser -> summary
```

```python
chain = prompt | model | StrOutputParser()
summary = chain.invoke({"message": "..."})
```

This is the most important runnable idea: each piece accepts input, returns output, and can be connected with `|`.

## Components In The Python-Only Script

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

## Python-Only Pipeline Flow

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

## Scenario Checklist

- Wrap ticket cleanup in `RunnableLambda`.
- Use `|` to pass cleaned data to the next step.
- Use `RunnableParallel` to compute queue and priority from the same ticket.
- Use `RunnablePassthrough` to keep the original cleaned ticket.
- Use `.batch()` to run the same pipeline over multiple tickets.

## Practice Lab

Start with `scripts/03_gemini_summarization_chain.py`.

1. Change the input message and run the script again.
2. Change the prompt from one sentence to three bullet points.
3. Add a second message and invoke the same chain twice.

Then open `scripts/02_runnables_building_blocks.py` and try these changes.

1. Create a `RunnableLambda` that converts a ticket subject to lowercase.
2. Create two runnables: one that strips whitespace and one that adds the prefix `"Ticket: "`. Compose them with `|`.
3. Create a runnable that accepts a ticket dictionary and returns only the subject.
