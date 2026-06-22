# Lab 02: Direct Gemini API

## Goal

Call Gemini directly before you use LangChain.

This helps you see the boundary between a model provider SDK and a framework. Underneath every abstraction is still a model call with input, output, credentials, model selection, and error handling.

## Core Idea

The direct SDK flow is:

1. Load environment variables.
2. Create a Gemini client.
3. Send content to a model.
4. Read the text response.

Run the example:

```bash
python scripts/01_gemini_smoke_test.py
```

## Prompt To Try

Ask Gemini to classify a support ticket:

```text
Classify this support ticket as billing, account, technical, or product.

Subject: Charged twice for annual plan
Message: I upgraded yesterday and my card shows two annual charges.
```

## Scenario

You are testing whether Gemini can help triage a single customer ticket before you build a larger workflow. Keep the script small: one ticket in, one model response out.

## Practice Lab

Open `scripts/01_gemini_smoke_test.py` and make one small change at a time.

1. Change the prompt so Gemini returns only one label: `billing`, `account`, `technical`, or `product`.
2. Change the prompt so Gemini drafts a two-sentence response to the customer.
3. Add a different support-ticket subject and message.
4. Add a line to the prompt that says: `Do not promise refunds or timelines.`
5. Change `GEMINI_MODEL` in `.env` and run the script again.
