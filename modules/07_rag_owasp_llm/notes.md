# RAG Notes

RAG means retrieval augmented generation.

The app does not ask the model to answer factual questions from model memory.
It first retrieves source chunks, then gives those chunks to the model as
context.

This module uses one source document:

```text
data/owasp_top10_llm_applications.pdf
```

## Offline And Online

RAG has two separate pipelines.

The offline indexing pipeline prepares the data:

```text
PDF
  -> Docling Markdown
  -> chunks
  -> embeddings
  -> Chroma index
```

The online answering pipeline handles user questions:

```text
question
  -> retrieve relevant Chroma chunks
  -> format context
  -> load message history from the checkpointer
  -> local Gemma answer
  -> save message history
```

The notebook exposes each intermediate representation so the data flow is easy
to inspect.

The scripts run the full indexing and chat workflows:

```bash
python modules/07_rag_owasp_llm/scripts/19_owasp_llm_build_index.py
python modules/07_rag_owasp_llm/scripts/20_owasp_llm_rag_chat.py
```

Re-running the index script replaces the existing Chroma index in
`data/chroma_owasp_llm`.

## PDF To Markdown With Docling

PDF files are layout files, not clean text files. If we chunk raw PDF-extracted
text directly, headings and section boundaries can be hard to preserve.

This module uses Docling to convert the PDF into Markdown first:

These imports work inside the provided notebook and scripts because they add
`modules/07_rag_owasp_llm` to Python's import path.

```python
from pathlib import Path

from shared.pdf_markdown import pdf_to_markdown

markdown = pdf_to_markdown(Path("data/owasp_top10_llm_applications.pdf"))
print(markdown[:1000])
```

The helper wraps Docling's `DocumentConverter`:

```python
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

pipeline_options = PdfPipelineOptions()
pipeline_options.ocr_options.force_full_page_ocr = True
converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
    }
)
result = converter.convert("document.pdf")
markdown = result.document.export_to_markdown()
```

Docling handles document layout and exports Markdown from its structured
document representation.

This OWASP PDF needs `force_full_page_ocr = True`. With Docling's default
conversion, section headings are extracted but most body text is emitted as
`<!-- image -->` placeholders.

## Documents

LangChain represents retrieved source text with `Document`.

```python
from langchain_core.documents import Document

document = Document(
    page_content="Prompt injection happens when...",
    metadata={
        "source": "data/owasp_top10_llm_applications.pdf",
        "chunk_index": 12,
    },
)
```

`page_content` is embedded and retrieved.

`metadata` is useful for debugging and inspection. The retriever searches
`page_content`, then returns the matching `Document` objects with their metadata.

## Chunking

Chunking decides what the retriever can find.

In this module, chunkers live in:

```text
modules/07_rag_owasp_llm/shared/chunkers.py
```

Each chunker has the same simple contract:

```python
chunks = chunker(markdown_text)
```

The input is one Markdown string.

The output is a list of chunk strings.

That makes chunking functions easy to compare in the notebook.

## Strategy 1: Recursive Chunking

Recursive chunking splits on larger boundaries first:

```text
headings
paragraphs
lines
sentences
words
characters
```

The `chunk_overlap` setting keeps part of the previous chunk inside the next
chunk.

```python
from shared.chunkers import recursive_chunks

chunks = recursive_chunks(markdown)
```

This is fast and deterministic. In this module, it is used for comparison before
building the final semantic index.

## Strategy 2: Gemma Semantic Chunks

The semantic chunker asks the local Gemma chat model to split Markdown sections
by meaning.

The implementation uses LangChain structured output:

```text
ChatPromptTemplate
  -> ChatOllama.with_structured_output(SemanticChunkOutput)
  -> SemanticChunkOutput(chunks=[...])
```

The schema is a Pydantic model:

```python
from pydantic import BaseModel, Field


class SemanticChunkOutput(BaseModel):
    chunks: list[str] = Field(
        description="Markdown chunks in their original wording."
    )
```

```python
from shared.chunkers import gemma_semantic_chunks

chunks = gemma_semantic_chunks(markdown)
```

This strategy can create cleaner topic boundaries, but it is slower and depends
on the local chat model being available.

Use it when semantic boundaries matter more than indexing speed.

The notebook and indexing script use semantic chunks for retrieval.

To build the index:

```bash
python modules/07_rag_owasp_llm/scripts/19_owasp_llm_build_index.py
```

## Embeddings

An embedding model turns text into a vector.

Start Ollama and pull the local models before running embedding or chat code:

```bash
ollama --version
ollama serve
ollama pull embeddinggemma
ollama pull gemma4:e4b
ollama list
```

If `embeddinggemma` is not available, update Ollama and pull the model again.

```python
from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="embeddinggemma")
vector = embeddings.embed_query("What is prompt injection?")
```

The vector is not useful to read directly. Inspect:

```text
vector length
which chunks are closest to a query
whether the closest chunks are actually relevant
```

The notebook embeds a small chunk sample in memory and ranks chunks by vector
similarity.

## Chroma

Chroma stores embedded chunks.

The offline script creates the persistent index:

```bash
python modules/07_rag_owasp_llm/scripts/19_owasp_llm_build_index.py
```

It writes to:

```text
data/chroma_owasp_llm
```

The online chat script reads that index and runs a small LangGraph chat graph:

```bash
python modules/07_rag_owasp_llm/scripts/20_owasp_llm_rag_chat.py
```

The graph has one node:

```text
answer
```

The `answer` node retrieves documents, builds the system message with the
retrieved context, calls the model, and returns only the assistant message.

The checkpointer stores the `messages` list for the selected `thread_id`.
Each new terminal message is sent as a `HumanMessage`; the graph restores older
messages before answering.

Retrieved documents are not stored in graph state. They are local values inside
the node call, which keeps the checkpoint focused on chat history.

The answer node sends the model a real chat message list:

```text
SystemMessage(retrieved context)
previous HumanMessage / AIMessage objects
latest HumanMessage
```

History is not converted into one long string. It stays in `messages`.

## Retriever

A retriever returns `Document` objects.

```python
documents = retriever.invoke("What is prompt injection?")
```

It does not write the final answer.

In the chat script:

```python
retriever = vector_store.as_retriever(search_kwargs={"k": RETRIEVED_CHUNKS})
```

`RETRIEVED_CHUNKS` controls how many chunks the retriever returns.

## Grounded Answering

The chat prompt requires the model to:

```text
answer only from retrieved context
say when the retrieved context is insufficient
avoid guessing
```

RAG reduces unsupported answers. It does not remove the need to inspect
retrieval quality.

The chat prompt is built with message prompt templates:

```python
ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(system_text),
        HumanMessagePromptTemplate.from_template(user_text),
    ]
)
```

## Pipeline Walkthrough

The notebook follows the RAG preparation flow with inspectable intermediate
values:

```text
modules/07_rag_owasp_llm/notebooks/07_rag_pipeline_walkthrough.ipynb
```

```text
Docling PDF to Markdown
recursive chunking
Gemma semantic chunking
in-memory embedding and retrieval inspection
offline index command
online chat command
```

Then build the real index and chat from the terminal:

```bash
python modules/07_rag_owasp_llm/scripts/19_owasp_llm_build_index.py
python modules/07_rag_owasp_llm/scripts/20_owasp_llm_rag_chat.py
```

## Example Questions

Use questions that can be answered from the OWASP document:

```text
What is prompt injection?
How does OWASP describe insecure output handling?
What are the risks of excessive agency?
How can sensitive information disclosure happen in LLM apps?
What mitigations are suggested for supply chain vulnerabilities?
```
