# RAG Notes

RAG means retrieval augmented generation.

The model does not answer only from its internal training data. The app first
retrieves relevant source text, then gives that source text to the model as
context.

This module uses one source document:

```text
data/owasp_top10_llm_applications.pdf
```

The document is the OWASP Top 10 for LLM Applications PDF from:

```text
https://github.com/GURPREETKAURJETHRA/LLM-SECURITY/blob/main/OWASP%20TOP%2010%20FOR%20LLM%20APPLICATIONS.pdf
```

## Two Pipelines

RAG has two different pipelines.

The first pipeline runs before users ask questions:

```text
PDF
  -> parsed pages
  -> cleaned text
  -> chunks
  -> embeddings
  -> Chroma vector store
```

This is the offline indexing pipeline. In this repo, it is taught with
notebooks so students can inspect every intermediate object.

The second pipeline runs when a user asks a question:

```text
question
  -> retrieve relevant chunks
  -> format context
  -> prompt local LLM
  -> grounded answer with citations
```

This is the online answering pipeline. In this repo, it is taught with a chat
script because that is how a user would actually use the RAG system.

## Why The Work Is Split

Parsing, cleaning, chunking, and indexing are data preparation steps. They are
slow compared with answering one question, and they only need to rerun when the
source document or chunking strategy changes.

Answering is interactive. It should load the existing index, retrieve relevant
chunks, and call the model.

Do not rebuild the vector store inside the chat script.

## Documents

LangChain represents source text with `Document`.

```python
from langchain_core.documents import Document

document = Document(
    page_content="Prompt injection happens when...",
    metadata={
        "source": "data/owasp_top10_llm_applications.pdf",
        "page": 12,
    },
)
```

`page_content` is the text that can be embedded and retrieved.

`metadata` is information about where the text came from. Metadata is important
because answers need citations.

For this module, every page and chunk should keep:

```text
source file
page number
chunk id
chunking strategy
```

## PDF Parsing

PDF files are presentation files. They are not always clean text files.

When text is extracted from a PDF, you may see:

```text
page headers
page footers
broken line breaks
extra spaces
empty pages
```

The cleaning step in this module should stay light. It should normalize
whitespace and remove empty pages, but it should keep headings because headings
help retrieval.

## Chunking

Most vector stores search chunks, not whole books or whole PDFs.

A chunk should be large enough to contain a useful idea, but small enough that
retrieval does not return too much unrelated text.

This module compares four chunking styles.

### Page As Chunk

```python
page_chunks = page_documents
```

This is easy and preserves page citations, but a page can contain multiple
topics.

Use this as the baseline.

### Fixed Size Chunks

```python
text[i : i + chunk_size]
```

This is easy to understand but can split important sentences, lists, and
headings in awkward places.

Use this to show why naive chunking can be weak.

### Recursive Chunks

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=900,
    chunk_overlap=150,
)
chunks = splitter.split_documents(documents)
```

Recursive splitting tries larger separators first, then smaller ones. It tends
to preserve paragraphs better than fixed-size slicing.

This is the default strategy for the final index.

### Heading-Aware Chunks

Heading-aware chunks try to keep sections together.

For Markdown this can be very clean. For PDF-extracted text, headings may be
less reliable. In this module, heading-aware chunking is a comparison strategy,
not the default.

## Embeddings

An embedding model turns text into a vector.

```python
from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="embeddinggemma")
vector = embeddings.embed_query("What is prompt injection?")
```

The vector is not useful to read directly. Students should inspect:

```text
vector length
which chunks are closest to a query
whether close chunks actually look relevant
```

Do not print full vectors.

## Chroma

Chroma stores embedded chunks and lets the app search them later.

```python
from langchain_chroma import Chroma

vector_store = Chroma(
    collection_name="owasp_top10_llm",
    embedding_function=embeddings,
    persist_directory="data/chroma_owasp_llm",
)
```

The indexing notebook writes to Chroma.

The chat script reads from Chroma.

## Retriever

A retriever is a standard LangChain interface:

```python
documents = retriever.invoke("What is prompt injection?")
```

The retriever returns `Document` objects. It does not write the final answer.

In this module:

```python
retriever = vector_store.as_retriever(search_kwargs={"k": 4})
```

`k=4` means the retriever returns the four most relevant chunks.

## Grounded Answering

The chat script should give the model retrieved context and strict instructions:

```text
Answer only from the retrieved context.
If the context does not support an answer, say so.
Cite page and chunk ids.
Do not guess.
```

The model can still make mistakes. RAG reduces unsupported answers, but it does
not remove the need to inspect retrieval quality.

## Local LLM

This module uses Ollama for local models.

Default chat model:

```text
gemma4:e4b
```

Default embedding model:

```text
embeddinggemma
```

Setup:

```bash
ollama pull gemma4:e4b
ollama pull embeddinggemma
```

If a machine cannot run Gemma 4 comfortably, use a smaller Ollama chat model and
update `OLLAMA_CHAT_MODEL` in `.env`.

## Notebook Order

Run the notebooks in order:

```text
notebooks/07_rag_pdf_parsing_cleaning.ipynb
notebooks/08_rag_chunking_strategies.ipynb
notebooks/09_rag_embeddings_chroma_indexing.ipynb
```

Then run the chat script:

```bash
python scripts/19_owasp_llm_rag_chat.py
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

Avoid questions that require outside knowledge. The point of this module is to
answer from the retrieved document.
