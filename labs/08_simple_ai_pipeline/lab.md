# Lab 08: Simple AI Pipeline

## Goal

Run a small customer support pipeline backed by Gemini.

## Run It

```bash
python scripts/05_support_ticket_pipeline.py
```

## Pipeline Shape

```text
load tickets -> route ticket -> draft reply with Gemini -> print result
```

## What This Demonstrates

- Plain Python still matters.
- Prompt templates keep instructions consistent.
- LangChain chains compose prompt, model, and parser.
- Routing can stay explicit and understandable.

## What This Is Not

This is not an agent. It does not call tools, search documents, remember conversations, or persist state.

Those topics are intentionally left out of Day 1.
