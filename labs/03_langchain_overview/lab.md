# Lab 03: LangChain Overview

## Goal

Understand why LangChain exists before you write LangChain code.

## What LangChain Adds

LangChain provides common interfaces for:

- chat models
- prompts
- output parsers
- runnables
- chains

The direct Gemini API is provider-specific. LangChain wraps providers behind consistent interfaces so you can compose application components in a predictable way.

## What You Will Use Today

Today uses only the foundational pieces:

- model wrappers
- prompt templates
- runnable composition
- simple branching

You will not use these topics today:

- RAG
- tools
- agents
- memory
- vector stores
- persistence

## Mental Model

Think of LangChain as a way to connect small components:

```text
input -> prompt -> model -> parser -> output
```

Each component has a common invocation shape. That shared interface is what makes chaining possible.
