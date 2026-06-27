# Troubleshooting

## `GOOGLE_API_KEY` is missing

Copy `.env.example` to `.env` and set your key:

```bash
cp .env.example .env
```

Then edit `.env`.

## Import errors

Make sure the virtual environment is active and dependencies are installed:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Notebook kernel does not show up

Install the current environment as a notebook kernel:

```bash
python -m ipykernel install --user --name langchain-day1 --display-name "Python (langchain-day1)"
```

## RAG Notebook Cannot Import Chroma Or Ollama

Install the updated requirements:

```bash
python -m pip install -r requirements.txt
```

## RAG Chat Cannot Find The Chroma Index

Run the RAG notebooks in order:

```text
notebooks/07_rag_pdf_parsing_cleaning.ipynb
notebooks/08_rag_chunking_strategies.ipynb
notebooks/09_rag_embeddings_chroma_indexing.ipynb
```

The chat script reads `data/chroma_owasp_llm`. It does not build the index.

## RAG Chat Cannot Reach Ollama

Start Ollama and pull the local models:

```bash
ollama pull gemma4:e4b
ollama pull embeddinggemma
```

## Gemini quota or authentication errors

Check that the API key is valid, billing or quota is enabled for the account, and the selected model is available for the key.

## Model output differs from the lab

That is expected. Model output is probabilistic. Teach the shape of the workflow, not exact wording.
