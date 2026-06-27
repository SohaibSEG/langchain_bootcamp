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

## RAG Notebook Cannot Import Docling, Chroma, Or Ollama

Install the updated requirements:

```bash
python -m pip install -r requirements.txt
```

## RAG Chat Cannot Find The Chroma Index

Build the offline index:

```bash
python modules/07_rag_owasp_llm/scripts/19_owasp_llm_build_index.py
```

The Chroma index is created by the offline indexing script.

## RAG Chat Cannot Reach Ollama

Start Ollama.

On macOS or Linux, if the app is not already running:

```bash
ollama serve
```

On Windows, start Ollama from the Start menu.

`ollama serve` keeps running. Open another terminal before pulling the local
models:

```bash
ollama --version
ollama pull embeddinggemma
ollama pull gemma4:e4b
ollama list
```

The default Ollama API address is `http://localhost:11434`.

If `ollama pull embeddinggemma` fails, update Ollama and retry. The embedding
model requires a recent Ollama release.

## Gemini quota or authentication errors

Check that the API key is valid, billing or quota is enabled for the account, and the selected model is available for the key.

## Model output differs from the lab

That is expected. Model output is probabilistic. Teach the shape of the workflow, not exact wording.
