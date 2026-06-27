# Course Notes

This repo teaches LangChain and LangGraph through one recurring scenario:

```text
customer support triage and escalation
```

The examples intentionally reuse the same domain so students can focus on one new technical idea at a time.

## Documentation Structure

Read the notes in this order:

```text
01_setup_and_python_notes.md
02_gemini_langchain_notes.md
03_runnables_and_chains_notes.md
04_langgraph_runtime_notes.md
05_agents_tools_memory_notes.md
06_human_in_the_loop_notes.md
07_rag_notes.md
```

Reference pages:

```text
glossary.md
troubleshooting.md
official_docs_links.md
```

## Learning Progression

The course moves from plain Python to agents:

```text
Python data
  -> direct Gemini API
  -> LangChain prompt/model/parser composition
  -> runnables and chains
  -> LangGraph state machines
  -> reducers, branches, checkpointers, context, stores
  -> chat memory
  -> agents with tools
  -> agents with chat history and long-term memory
  -> human review for risky actions
  -> RAG over a document with local models
```

This order matters. Do not introduce agents before students understand:

```text
messages
state updates
checkpointers
tools as Python functions
```

## Script Index

| Script | Main Concept |
| --- | --- |
| `01_gemini_smoke_test.py` | Direct Gemini call |
| `02_runnables_building_blocks.py` | Runnable building blocks |
| `03_gemini_summarization_chain.py` | Small prompt-model-parser chain |
| `04_ticket_classification_chain.py` | Classification chain |
| `05_support_ticket_pipeline.py` | Simple AI support pipeline |
| `06_langgraph_state_machine_preview.py` | LangGraph nodes and conditional edges |
| `07_langgraph_default_merge.py` | Default state merge rules |
| `08_langgraph_reducers.py` | Reducers |
| `09_langgraph_parallel_branches.py` | Parallel branches |
| `10_checkpointer_basics.py` | Checkpointer and `thread_id` |
| `11_runtime_context_basics.py` | Runtime context |
| `12_store_basics.py` | Store namespaces and keys |
| `13_store_with_runtime_context.py` | Store + runtime context |
| `14_chat_memory_graph.py` | Chat memory with `MessagesState` |
| `15_agent_with_tools.py` | Agent loop and tools |
| `16_agent_memory_and_tools.py` | Agent with chat history and long-term memory |
| `17_human_review_basics.py` | Basic interrupt and resume |
| `18_agent_human_review_tool.py` | Human review before risky agent tool |
| `19_owasp_llm_rag_chat.py` | Chat over the OWASP LLM RAG index |

## Core Contracts

### Runnable Contract

```python
output = runnable.invoke(input)
```

Most LangChain components are runnables:

```text
prompt
model
parser
chain
```

### Graph Node Contract

```python
def node(state: StateType) -> dict:
    return {"field": "new value"}
```

Nodes receive state and return updates.

### Checkpointer Contract

```python
config = {"configurable": {"thread_id": "ticket-a"}}
```

`thread_id` is the key LangGraph checkpointers use to load and save thread state.

### Store Contract

```python
store.put(namespace, key, value)
store.get(namespace, key)
store.search(namespace)
```

Stores hold application data, not graph state.

### Agent Input Contract

```python
agent.invoke(
    {"messages": [HumanMessage(content=text)]},
    config={"configurable": {"thread_id": "support-agent"}},
)
```

The `messages` key is part of LangChain's built-in agent state.

### RAG Contracts

```python
documents = retriever.invoke(question)
```

A retriever returns `Document` objects, not final answers.

```python
answer = rag_chain.invoke(
    {
        "question": question,
        "context": formatted_documents,
        "history": formatted_history,
    }
)
```

The online RAG script loads an existing Chroma index. The notebooks build that
index from the OWASP PDF.

## Teaching Guidance

For each script, identify:

```text
the input
the state shape
the new concept
the line that connects to LangChain or LangGraph
the expected output shape
```

Keep explanations close to the code comments. Script output should print inspected values, not lecture text.
