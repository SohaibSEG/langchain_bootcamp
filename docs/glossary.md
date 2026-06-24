# Glossary

## Chain

A sequence of components where the output of one component becomes the input to the next component.

## Agent

A model-driven loop that can decide to call tools before producing a final answer. In this repo, agents are introduced in `scripts/13_agent_with_tools.py`.

## Checkpointer

LangGraph runtime storage that saves graph state by `thread_id`. It is used for short-term memory and pause/resume workflows. See `scripts/08_checkpointer_basics.py`.

## Gemini

Google's family of generative AI models. Day 1 uses Gemini through the direct Google Gen AI SDK first, then through LangChain.

## Invocation

Calling a model, prompt, chain, or runnable with input and receiving output.

## Human In The Loop

A workflow pattern where the graph pauses before a risky action and resumes after a human decision. See `scripts/15_human_review_basics.py`.

## Interrupt

A LangGraph pause point created with `interrupt(...)`. The graph saves state through a checkpointer and waits for `Command(resume=...)`.

## LangChain

A framework for composing model calls, prompts, parsers, and other application components through common interfaces.

## LangGraph

A framework for building stateful graph workflows. Day 1 only previews why graphs become useful once branching workflows grow.

## Prompt Template

A reusable prompt with placeholders for values supplied at runtime.

## Runnable

The common LangChain interface for things that can be invoked, streamed, batched, or composed. Prompts, models, parsers, and chains are runnables.

## Runtime Context

Per-run application information passed with `context=...`, such as the current customer id or support agent. The graph can read it, but it is not graph state. See `scripts/09_runtime_context_basics.py`.

## Reducer

A function that tells LangGraph how to combine multiple updates to the same state field. For example, `Annotated[list[str], add]` appends list updates instead of replacing the whole list. See `scripts/07_langgraph_reducers_parallel.py`.

## Store

Long-term application memory. Stores keep app data such as customer preferences outside a single graph thread. See `scripts/10_store_basics.py`.

## Tool

A typed Python function the model is allowed to call. The function name, arguments, docstring, and return value form the tool contract.

## Routing

Choosing the next path in a workflow based on input or intermediate output.

## Short-Term Memory

Conversation or graph state saved for one thread, usually through a checkpointer.
