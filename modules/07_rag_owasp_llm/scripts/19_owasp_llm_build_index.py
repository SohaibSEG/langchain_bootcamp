import os
import shutil
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings


MODULE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(MODULE_ROOT))

from shared.chunkers import gemma_semantic_chunks
from shared.pdf_markdown import pdf_to_markdown


COLLECTION_NAME = "owasp_top10_llm"
PDF_PATH = REPO_ROOT / "data" / "owasp_top10_llm_applications.pdf"
CHROMA_DIR = REPO_ROOT / "data" / "chroma_owasp_llm"


def log_step(step: str) -> None:
    print(f"\n{step}", flush=True)


def build_documents(chunks: list[str], source: Path) -> list[Document]:
    documents = []

    for index, chunk in enumerate(chunks, start=1):
        documents.append(
            Document(
                page_content=chunk,
                metadata={
                    "source": str(source),
                    "chunk_index": index,
                },
            )
        )

    return documents


def main() -> None:
    load_dotenv()

    if not PDF_PATH.exists():
        raise FileNotFoundError(f"Missing PDF at {PDF_PATH}")

    log_step("1. Converting PDF to Markdown with Docling")
    markdown = pdf_to_markdown(PDF_PATH)
    print({"markdown_characters": len(markdown)}, flush=True)

    log_step("2. Creating semantic chunks with Gemma")
    chunks = gemma_semantic_chunks(markdown)
    print({"chunks": len(chunks)}, flush=True)

    log_step("3. Wrapping chunks as LangChain Document objects")
    documents = build_documents(chunks, PDF_PATH)
    print({"documents": len(documents)}, flush=True)

    log_step("4. Loading Ollama embedding model")
    embeddings = OllamaEmbeddings(
        model=os.getenv("OLLAMA_EMBEDDING_MODEL", "embeddinggemma"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )

    log_step("5. Rebuilding persistent Chroma index")
    print(
        {
            "rebuilding_chroma_index": str(CHROMA_DIR),
            "existing_index_found": CHROMA_DIR.exists(),
        },
        flush=True,
    )

    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)

    Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR),
    )

    log_step("6. Index build complete")
    print({"chroma_index": str(CHROMA_DIR), "documents_indexed": len(documents)}, flush=True)


if __name__ == "__main__":
    main()
