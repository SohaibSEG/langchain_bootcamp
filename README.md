# LangChain + LangGraph Bootcamp: Day 1

This repository is the teaching artifact for Day 1 of a LangChain and LangGraph bootcamp.

The day is documentation-first and instructor-led. Learners use notebooks for Python foundations, Markdown labs for guided explanation, and a small number of scripts for complete runnable examples.

The story for the day is a realistic customer support triage and escalation assistant. Each lesson adds one idea at a time:

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
11. Why LangGraph exists as the bridge to Day 2

Day 1 does not cover RAG, tools, agents, memory, persistence, vector stores, or production deployment.

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

To run a script:

```bash
python scripts/01_gemini_smoke_test.py
python scripts/02_runnables_building_blocks.py
python scripts/03_runnable_branching.py
python scripts/04_langchain_gemini_chain.py
python scripts/05_support_ticket_pipeline.py
python scripts/06_langgraph_state_machine_preview.py
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

  labs/
    00_setup/
      lab.md

    01_python_foundations/
      lab.md
      exercises.md

    02_direct_gemini_api/
      lab.md
      exercises.md

    03_langchain_overview/
      lab.md
      exercises.md

    04_runnables/
      lab.md
      exercises.md

    05_prompt_templates/
      lab.md
      exercises.md

    06_invocations_and_chains/
      lab.md
      exercises.md

    07_branching_and_routing/
      lab.md
      exercises.md

    08_simple_ai_pipeline/
      lab.md
      exercises.md

    09_langgraph_preview/
      lab.md

  scripts/
    01_gemini_smoke_test.py
    02_runnables_building_blocks.py
    03_runnable_branching.py
    04_langchain_gemini_chain.py
    05_support_ticket_pipeline.py
    06_langgraph_state_machine_preview.py

  data/
    tickets.jsonl
    support_policy.md

  docs/
    glossary.md
    troubleshooting.md
    official_docs_links.md
```

## Suggested Schedule

Total: 6 hours.

| Time | Topic | Files |
| --- | --- | --- |
| 00:00-00:30 | Setup and orientation | `labs/00_setup/lab.md` |
| 00:30-02:00 | Python foundations | `notebooks/`, `labs/01_python_foundations/` |
| 02:00-02:35 | Direct Gemini API | `labs/02_direct_gemini_api/`, `scripts/01_gemini_smoke_test.py` |
| 02:35-03:10 | LangChain overview | `labs/03_langchain_overview/` |
| 03:10-03:50 | Runnables | `labs/04_runnables/`, `scripts/02_runnables_building_blocks.py` |
| 03:50-04:30 | Prompt templates | `labs/05_prompt_templates/` |
| 04:30-05:05 | Invocations and chains | `labs/06_invocations_and_chains/`, `scripts/04_langchain_gemini_chain.py` |
| 05:05-05:35 | Branching and routing | `labs/07_branching_and_routing/`, `scripts/03_runnable_branching.py` |
| 05:35-05:50 | Simple AI pipeline | `labs/08_simple_ai_pipeline/`, `scripts/05_support_ticket_pipeline.py` |
| 05:50-06:00 | LangGraph preview | `labs/09_langgraph_preview/`, `scripts/06_langgraph_state_machine_preview.py` |

## Teaching Notes

- Keep the chronology strict. Do not use functions before the functions notebook, classes before the classes notebook, or LangChain before the direct API lab.
- Exercises are prompts for learners, not solved answer files.
- The examples intentionally avoid RAG, tools, agents, memory, checkpointing, vector stores, and deployment.
- The LangGraph preview is conceptual. Day 2 should be the first day that treats graphs as a primary development surface.
