# Lab 07: Branching and Routing

## Goal

Choose different workflow paths for different support tickets.

## Why Routing Appears

A billing refund request, a sign-in problem, and a production API outage should not all follow the same workflow.

In this repo, routing is handled by Gemini through a structured triage schema:

```text
ticket
  -> Gemini classifier
  -> TriageDecision(category, severity, queue, confidence, missing_context)
  -> reply prompt
```

The model-based classification and routing example is in the support pipeline:

```bash
python scripts/05_support_ticket_pipeline.py
```

## Scenario

You are routing tickets into queues before drafting replies. In the final pipeline, Gemini returns a structured triage decision with category, severity, queue, confidence, customer intent, routing reason, and missing context.

## Pipeline Target

```text
ticket
  -> Gemini structured classification
  -> queue and severity decision
  -> reply drafting prompt
  -> customer reply
```

## Practice Lab

Open `scripts/05_support_ticket_pipeline.py` and adjust the structured triage output.

1. Add `cancellation` as an allowed category in the triage schema.
2. Add `Retention` as an allowed queue.
3. Add a cancellation ticket to `data/tickets.jsonl`.
4. Update the triage prompt so Gemini can route cancellation tickets.
5. Print the category, severity, queue, and confidence for every sample ticket.
