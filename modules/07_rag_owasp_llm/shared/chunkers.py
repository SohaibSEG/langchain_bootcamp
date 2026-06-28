import os
import re

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field


RECURSIVE_CHUNK_SIZE = 1200
RECURSIVE_CHUNK_OVERLAP = 180
SEMANTIC_PRECHUNK_TARGET_CHARS = 5000


def log_chunker_step(message: str) -> None:
    print(message, flush=True)


class SemanticChunkOutput(BaseModel):
    chunks: list[str] = Field(
        description=(
            "Markdown chunks in their original wording. Headings should stay "
            "with the content they introduce."
        )
    )


def recursive_chunks(
    text: str,
    chunk_size: int = RECURSIVE_CHUNK_SIZE,
    chunk_overlap: int = RECURSIVE_CHUNK_OVERLAP,
) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_text(text)


def split_markdown_for_llm_calls(
    text: str,
    target_chars: int = SEMANTIC_PRECHUNK_TARGET_CHARS,
) -> list[str]:
    # First split on H1/H2 Markdown headings so we keep section boundaries.
    # Then combine nearby small sections into one model input. This avoids
    # wasting a model call on tiny sections like a title or short introduction.
    # If a section is already longer than the target, keep it whole and let the
    # semantic model split it.
    raw_sections = re.split(r"(?=\n#{1,2}\s)", text)
    sections = [section.strip() for section in raw_sections if section.strip()]
    batches = []
    current_batch = []
    current_chars = 0

    for section in sections:
        section_chars = len(section)
        next_chars = current_chars + section_chars + 2

        if current_batch and next_chars > target_chars:
            batches.append("\n\n".join(current_batch))
            current_batch = []
            current_chars = 0

        current_batch.append(section)
        current_chars += section_chars + 2

    if current_batch:
        batches.append("\n\n".join(current_batch))

    return batches


def gemma_semantic_chunks(
    text: str,
    model: str | None = None,
    base_url: str | None = None,
    prechunk_target_chars: int = SEMANTIC_PRECHUNK_TARGET_CHARS,
) -> list[str]:
    model = model or os.getenv("OLLAMA_CHAT_MODEL", "gemma4:e4b")
    base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    llm = ChatOllama(
        model=model,
        base_url=base_url,
        temperature=0,
    )
    structured_llm = llm.with_structured_output(
        SemanticChunkOutput,
        method="json_schema",
        include_raw=True,
    )
    chunks = []
    sections = split_markdown_for_llm_calls(
        text,
        target_chars=prechunk_target_chars,
    )

    log_chunker_step(
        f"Semantic chunker: {len(sections)} model calls after batching sections"
    )

    for index, section in enumerate(sections, start=1):
        log_chunker_step(
            f"Semantic chunker: processing section {index}/{len(sections)} "
            f"({len(section)} characters)"
        )
        result = structured_llm.invoke(
            [
                SystemMessage(
                    content=(
                        "Split Markdown into semantic RAG chunks.\n"
                        "Preserve the original wording.\n"
                        "Keep headings with the content they introduce.\n"
                        "Do not summarize.\n"
                        "Merge short headings or short paragraphs with nearby related content.\n"
                        "Split long sections into coherent retrieval chunks.\n"
                        "Do not return empty chunks or heading-only chunks.\n"
                        "Each chunk should be useful on its own when retrieved by a vector search.\n"
                        "Return structured output that matches this schema: "
                        '{"chunks": ["first chunk", "second chunk"]}'
                    )
                ),
                HumanMessage(content=section),
            ]
        )
        if result["parsing_error"] or result["parsed"] is None:
            raw_content = getattr(result["raw"], "content", "")
            raise ValueError(
                "Ollama returned a response that did not match the semantic "
                "chunk schema. Check that Ollama is running, the chat model is "
                f"pulled, and the model supports structured output. Raw response: {raw_content!r}"
            )

        for chunk in result["parsed"].chunks:
            chunk = chunk.strip()
            if chunk:
                chunks.append(chunk)

        log_chunker_step(f"Semantic chunker: total chunks so far {len(chunks)}")

    return chunks
