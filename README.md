# LangChain + LangGraph Bootcamp: Day 1

This repository is the teaching artifact for Day 1 of a LangChain and LangGraph bootcamp.

The course is documentation-first and instructor-led. Learners use notebooks for Python foundations, Markdown notes for explanation, and focused scripts for runnable examples.

The story is a realistic customer support triage and escalation assistant. Each lesson adds one idea at a time:

1. Plain Python data handling
2. Functions and reusable logic
3. Classes and inheritance
4. Direct Gemini API call
5. LangChain model wrapper
6. Runnables
7. Prompt templates
8. Chains
9. Branching and routing
10. Simple Gemini-backed AI pipeline
11. LangGraph state machines
12. Reducers and parallel branches
13. Checkpointers, runtime context, and stores
14. Chat memory
15. Agents with tools
16. Agents with chat history and long-term memory
17. Human review for risky actions

## Setup

Use Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m ipykernel install --user --name langchain-day1 --display-name "Python (langchain-day1)"
cp .env.example .env
```

Edit `.env` and set `GOOGLE_API_KEY`.

To open the notebooks:

```bash
jupyter lab
```

## Notes

Read these in order:

```text
docs/00_course_notes.md
docs/01_setup_and_python_notes.md
docs/02_gemini_langchain_notes.md
docs/03_runnables_and_chains_notes.md
docs/04_langgraph_runtime_notes.md
docs/05_agents_tools_memory_notes.md
docs/06_human_in_the_loop_notes.md
```

Reference docs:

```text
docs/glossary.md
docs/troubleshooting.md
docs/official_docs_links.md
```

## Scripts

Run scripts from the repo root:

```bash
python scripts/01_gemini_smoke_test.py
python scripts/02_runnables_building_blocks.py
python scripts/03_gemini_summarization_chain.py
python scripts/04_ticket_classification_chain.py
python scripts/05_support_ticket_pipeline.py
python scripts/06_langgraph_state_machine_preview.py
python scripts/07_langgraph_reducers_parallel.py
python scripts/08_checkpointer_basics.py
python scripts/09_runtime_context_basics.py
python scripts/10_store_basics.py
python scripts/11_store_with_runtime_context.py
python scripts/12_chat_memory_graph.py
python scripts/13_agent_with_tools.py
python scripts/14_agent_memory_and_tools.py
python scripts/15_human_review_basics.py
python scripts/16_agent_human_review_tool.py
```

## Repository Map

```text
langchain-day1/
  README.md
  requirements.txt
  .env.example
  .gitignore

  notebooks/
    01_python_values_variables.ipynb
    02_python_dictionaries.ipynb
    03_python_lists.ipynb
    04_python_strings_conditions_loops.ipynb
    05_python_functions_type_hints.ipynb
    06_python_classes_inheritance.ipynb

  scripts/
    01_gemini_smoke_test.py
    02_runnables_building_blocks.py
    03_gemini_summarization_chain.py
    04_ticket_classification_chain.py
    05_support_ticket_pipeline.py
    06_langgraph_state_machine_preview.py
    07_langgraph_reducers_parallel.py
    08_checkpointer_basics.py
    09_runtime_context_basics.py
    10_store_basics.py
    11_store_with_runtime_context.py
    12_chat_memory_graph.py
    13_agent_with_tools.py
    14_agent_memory_and_tools.py
    15_human_review_basics.py
    16_agent_human_review_tool.py

  data/
    tickets.jsonl
    support_policy.md

  docs/
    00_course_notes.md
    01_setup_and_python_notes.md
    02_gemini_langchain_notes.md
    03_runnables_and_chains_notes.md
    04_langgraph_runtime_notes.md
    05_agents_tools_memory_notes.md
    06_human_in_the_loop_notes.md
    glossary.md
    troubleshooting.md
    official_docs_links.md
```

## Suggested Schedule

Total: 6 hours.

| Time | Topic | Files |
| --- | --- | --- |
| 00:00-00:30 | Setup and orientation | `docs/01_setup_and_python_notes.md` |
| 00:30-02:00 | Python foundations | `notebooks/`, `docs/01_setup_and_python_notes.md` |
| 02:00-02:35 | Direct Gemini API | `docs/02_gemini_langchain_notes.md`, `scripts/01_gemini_smoke_test.py` |
| 02:35-03:20 | LangChain overview, prompts, chains | `docs/02_gemini_langchain_notes.md`, `docs/03_runnables_and_chains_notes.md` |
| 03:20-04:15 | Runnables and support pipeline | `scripts/02_runnables_building_blocks.py`, `scripts/03_gemini_summarization_chain.py`, `scripts/04_ticket_classification_chain.py`, `scripts/05_support_ticket_pipeline.py` |
| 04:15-05:15 | LangGraph state and runtime | `docs/04_langgraph_runtime_notes.md`, `scripts/06_langgraph_state_machine_preview.py`, `scripts/07_langgraph_reducers_parallel.py`, `scripts/08_checkpointer_basics.py`, `scripts/09_runtime_context_basics.py`, `scripts/10_store_basics.py`, `scripts/11_store_with_runtime_context.py` |
| 05:15-05:45 | Chat memory and agents | `docs/05_agents_tools_memory_notes.md`, `scripts/12_chat_memory_graph.py`, `scripts/13_agent_with_tools.py`, `scripts/14_agent_memory_and_tools.py` |
| 05:45-06:00 | Human review preview | `docs/06_human_in_the_loop_notes.md`, `scripts/15_human_review_basics.py`, `scripts/16_agent_human_review_tool.py` |

## Teaching Notes

- Keep the chronology strict: Python first, direct API second, LangChain composition third, LangGraph runtime fourth, agents last.
- Introduce one runtime concept at a time before combining concepts.
- Explanations belong in comments and Markdown notes. Script output should show inspected values, not lecture text.
- The support-ticket scenario should stay consistent across examples.
