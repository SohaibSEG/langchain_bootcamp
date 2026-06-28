# LangChain + LangGraph Bootcamp: Day 1

This repository is the teaching artifact for Day 1 of a LangChain and LangGraph bootcamp.

The repo is documentation-first. Learners use notebooks for inspectable walkthroughs, Markdown notes for explanations, and focused scripts for runnable examples.

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
12. Default state merge rules
13. Reducers
14. Parallel branches
15. Checkpointers, runtime context, and stores
16. Chat memory
17. Agents with tools
18. Agents with chat history and long-term memory
19. Human review for risky actions
20. RAG indexing and retrieval
21. Local RAG chat with OWASP Top 10 for LLM Applications
22. MCP server and client for OWASP RAG tools

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

For the local RAG module, install Ollama and start the Ollama app or server.

```bash
# macOS, with Homebrew
brew install ollama
ollama serve

# Windows
# Install Ollama from https://ollama.com/download and start it from the Start menu.
```

`ollama serve` keeps running while the API is active. Open another terminal,
activate the virtual environment again, then pull the models once:

```bash
ollama --version
ollama pull embeddinggemma
ollama pull gemma4:e4b
ollama list
```

By default, Ollama serves its local API at `http://localhost:11434`. This repo
uses that default through `OLLAMA_BASE_URL` in `.env`.

If `ollama pull embeddinggemma` fails, update Ollama and retry. The embedding
model requires a recent Ollama release.

To open the notebooks:

```bash
jupyter lab
```

## Notes

Read these in order:

```text
modules/00_course_overview/notes.md
modules/01_setup_python/notes.md
modules/02_gemini_langchain/notes.md
modules/03_runnables_chains/notes.md
modules/04_langgraph_runtime/notes.md
modules/05_agents_tools_memory/notes.md
modules/06_human_in_the_loop/notes.md
modules/07_rag_owasp_llm/notes.md
modules/08_mcp_owasp_tools/notes.md
```

Reference docs:

```text
modules/reference/glossary.md
modules/reference/troubleshooting.md
modules/reference/official_docs_links.md
```

## Scripts

Run scripts from the repo root:

```bash
python modules/02_gemini_langchain/scripts/01_gemini_smoke_test.py
python modules/03_runnables_chains/scripts/02_runnables_building_blocks.py
python modules/02_gemini_langchain/scripts/03_gemini_summarization_chain.py
python modules/03_runnables_chains/scripts/04_ticket_classification_chain.py
python modules/03_runnables_chains/scripts/05_support_ticket_pipeline.py
python modules/04_langgraph_runtime/scripts/06_langgraph_state_machine_preview.py
python modules/04_langgraph_runtime/scripts/07_langgraph_default_merge.py
python modules/04_langgraph_runtime/scripts/08_langgraph_reducers.py
python modules/04_langgraph_runtime/scripts/09_langgraph_parallel_branches.py
python modules/04_langgraph_runtime/scripts/10_checkpointer_basics.py
python modules/04_langgraph_runtime/scripts/11_runtime_context_basics.py
python modules/04_langgraph_runtime/scripts/12_store_basics.py
python modules/04_langgraph_runtime/scripts/13_store_with_runtime_context.py
python modules/04_langgraph_runtime/scripts/14_chat_memory_graph.py
python modules/05_agents_tools_memory/scripts/15_agent_with_tools.py
python modules/05_agents_tools_memory/scripts/16_agent_memory_and_tools.py
python modules/06_human_in_the_loop/scripts/17_human_review_basics.py
python modules/06_human_in_the_loop/scripts/18_agent_human_review_tool.py
python modules/07_rag_owasp_llm/scripts/19_owasp_llm_build_index.py
python modules/07_rag_owasp_llm/scripts/20_owasp_llm_rag_chat.py
python modules/08_mcp_owasp_tools/scripts/21_owasp_mcp_server.py
python modules/08_mcp_owasp_tools/scripts/22_owasp_mcp_agent_client.py
```

## Repository Map

```text
langchain-day1/
  README.md
  requirements.txt
  .env.example
  .gitignore

  modules/
    00_course_overview/
      notes.md
    01_setup_python/
      notes.md
      notebooks/
    02_gemini_langchain/
      notes.md
      scripts/
    03_runnables_chains/
      notes.md
      scripts/
    04_langgraph_runtime/
      notes.md
      scripts/
    05_agents_tools_memory/
      notes.md
      scripts/
    06_human_in_the_loop/
      notes.md
      scripts/
    07_rag_owasp_llm/
      notes.md
      notebooks/
      scripts/
      shared/
    08_mcp_owasp_tools/
      notes.md
      scripts/
    reference/
      glossary.md
      troubleshooting.md
      official_docs_links.md

  data/
    tickets.jsonl
    support_policy.md
    owasp_top10_llm_applications.pdf

```

## Suggested Schedule

Total: 6 hours.

| Time | Topic | Files |
| --- | --- | --- |
| 00:00-00:30 | Setup and orientation | `modules/01_setup_python/notes.md` |
| 00:30-02:00 | Python foundations | `modules/01_setup_python/notebooks/`, `modules/01_setup_python/notes.md` |
| 02:00-02:35 | Direct Gemini API | `modules/02_gemini_langchain/notes.md`, `modules/02_gemini_langchain/scripts/01_gemini_smoke_test.py` |
| 02:35-03:20 | LangChain overview, prompts, chains | `modules/02_gemini_langchain/notes.md`, `modules/03_runnables_chains/notes.md` |
| 03:20-04:15 | Runnables and support pipeline | `modules/03_runnables_chains/scripts/02_runnables_building_blocks.py`, `modules/02_gemini_langchain/scripts/03_gemini_summarization_chain.py`, `modules/03_runnables_chains/scripts/04_ticket_classification_chain.py`, `modules/03_runnables_chains/scripts/05_support_ticket_pipeline.py` |
| 04:15-05:15 | LangGraph state and runtime | `modules/04_langgraph_runtime/notes.md`, `modules/04_langgraph_runtime/scripts/06_langgraph_state_machine_preview.py`, `modules/04_langgraph_runtime/scripts/07_langgraph_default_merge.py`, `modules/04_langgraph_runtime/scripts/08_langgraph_reducers.py`, `modules/04_langgraph_runtime/scripts/09_langgraph_parallel_branches.py`, `modules/04_langgraph_runtime/scripts/10_checkpointer_basics.py`, `modules/04_langgraph_runtime/scripts/11_runtime_context_basics.py`, `modules/04_langgraph_runtime/scripts/12_store_basics.py`, `modules/04_langgraph_runtime/scripts/13_store_with_runtime_context.py` |
| 05:15-05:45 | Chat memory and agents | `modules/05_agents_tools_memory/notes.md`, `modules/04_langgraph_runtime/scripts/14_chat_memory_graph.py`, `modules/05_agents_tools_memory/scripts/15_agent_with_tools.py`, `modules/05_agents_tools_memory/scripts/16_agent_memory_and_tools.py` |
| 05:45-06:00 | Human review preview | `modules/06_human_in_the_loop/notes.md`, `modules/06_human_in_the_loop/scripts/17_human_review_basics.py`, `modules/06_human_in_the_loop/scripts/18_agent_human_review_tool.py` |
| Next module | RAG with local models | `modules/07_rag_owasp_llm/notes.md`, `modules/07_rag_owasp_llm/notebooks/07_rag_pipeline_walkthrough.ipynb`, `modules/07_rag_owasp_llm/scripts/19_owasp_llm_build_index.py`, `modules/07_rag_owasp_llm/scripts/20_owasp_llm_rag_chat.py` |
| Next module | MCP over OWASP RAG tools | `modules/08_mcp_owasp_tools/notes.md`, `modules/08_mcp_owasp_tools/scripts/21_owasp_mcp_server.py`, `modules/08_mcp_owasp_tools/scripts/22_owasp_mcp_agent_client.py` |

## Learning Notes

- The course starts with Python, then direct model calls, LangChain composition,
  LangGraph runtime, agents, human review, and RAG.
- Each script focuses on one main runtime concept before later examples combine
  multiple concepts.
- Script output is mainly for inspected runtime values such as state, messages,
  retrieved chunks, and final answers.
- Most examples use the support-ticket scenario. The RAG module uses OWASP Top
  10 for LLM Applications because parsing and chunking need a longer source
  document.
