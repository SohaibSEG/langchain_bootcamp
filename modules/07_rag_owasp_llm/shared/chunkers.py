import os
import re

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field


RECURSIVE_CHUNK_SIZE = 1200
RECURSIVE_CHUNK_OVERLAP = 180
SEMANTIC_MAX_SECTION_CHARS = 5000


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
        separators=[
            "\n# ",
            "\n## ",
            "\n### ",
            "\n#### ",
            "\n##### ",
            "\n###### ",
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
    )
    return splitter.split_text(text)


def split_markdown_for_llm_calls(
    text: str,
    max_chars: int = SEMANTIC_MAX_SECTION_CHARS,
) -> list[str]:
    # Semantic chunking still needs a maximum input size per model call.
    # This split is only a prompt-size guardrail; Gemma does the semantic split.
    raw_sections = re.split(r"(?=\n#{1,6}\s)", text)
    sections = []

    for section in raw_sections:
        section = section.strip()
        if not section:
            continue
        if len(section) <= max_chars:
            sections.append(section)
            continue

        for start in range(0, len(section), max_chars):
            sections.append(section[start : start + max_chars].strip())

    return sections


def gemma_semantic_chunks(
    text: str,
    model: str | None = None,
    base_url: str | None = None,
    max_section_chars: int = SEMANTIC_MAX_SECTION_CHARS,
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

    for section in split_markdown_for_llm_calls(text, max_chars=max_section_chars):
        result = structured_llm.invoke(
            [
                SystemMessage(
                    content=(
                        "Split Markdown into semantic RAG chunks.\n"
                        "Preserve the original wording.\n"
                        "Keep headings with the content they introduce.\n"
                        "Do not summarize.\n"
                        "Return only chunks that contain source text.\n"
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

    return chunks
