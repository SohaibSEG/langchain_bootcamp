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

## Scenario

You are assembling the Day 1 support workflow: load sample tickets, route each ticket, pass the support policy into the prompt, draft a reply with Gemini, and print the result.

## Practice Lab

Open `scripts/05_support_ticket_pipeline.py` and the files in `data/`.

1. Add a new ticket to `data/tickets.jsonl` and run the pipeline again.
2. Modify the reply prompt so the answer is limited to three bullet points.
3. Add a route label named `Cancellation` and decide which queue should handle it.
4. Add one rule to `data/support_policy.md`, then pass that policy through the pipeline.
5. Add the selected queue name to the drafted reply prompt.
