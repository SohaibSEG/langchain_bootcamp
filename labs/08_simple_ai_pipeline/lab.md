# Lab 08: Simple AI Pipeline

## Goal

Run a small customer support pipeline backed by Gemini.

## Run It

```bash
python scripts/05_support_ticket_pipeline.py
```

## Pipeline Shape

```text
load tickets -> Gemini triage decision -> draft reply with Gemini -> print result
```

## What This Demonstrates

- Plain Python loads tickets and shapes data.
- Prompt templates keep triage and reply instructions consistent.
- Gemini classifies and routes tickets into a structured schema.
- The reply chain uses the triage decision and support policy.

## Scenario

You are assembling the Day 1 support workflow: load sample tickets, ask Gemini for a structured triage decision, pass the support policy and triage decision into the reply prompt, draft a reply with Gemini, and print the result.

## Practice Lab

Open `scripts/05_support_ticket_pipeline.py` and the files in `data/`.

1. Add a new ticket to `data/tickets.jsonl` and run the pipeline again.
2. Modify the reply prompt so the answer is limited to three bullet points.
3. Add a category named `cancellation` and a queue named `Retention` to the triage schema.
4. Add one rule to `data/support_policy.md`, then pass that policy through the pipeline.
5. Add the selected queue name to the drafted reply prompt.
