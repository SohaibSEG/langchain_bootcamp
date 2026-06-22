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

## What To Notice

The direct API gives you:

- simple model access
- a direct dependency on the provider SDK
- provider-specific request and response shapes

As your app grows, these parts can become repetitive:

- prompt formatting
- parsing output
- composing multiple steps
- swapping components
- branching workflow logic
