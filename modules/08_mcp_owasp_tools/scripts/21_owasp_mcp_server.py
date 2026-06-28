import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from mcp.server.fastmcp import FastMCP


COLLECTION_NAME = "owasp_top10_llm"
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000
MCP_PATH = "/mcp"
DEFAULT_RESULTS = 4

REPO_ROOT = Path(__file__).resolve().parents[3]
CHROMA_DIR = REPO_ROOT / "data" / "chroma_owasp_llm"
BUILD_INDEX_COMMAND = "python modules/07_rag_owasp_llm/scripts/19_owasp_llm_build_index.py"

mcp = FastMCP(
    "OWASP LLM RAG Tools",
    host=SERVER_HOST,
    port=SERVER_PORT,
    streamable_http_path=MCP_PATH,
)


def index_exists() -> bool:
    return CHROMA_DIR.exists() and any(CHROMA_DIR.iterdir())


def load_vector_store() -> Chroma | None:
    if not index_exists():
        return None

    embeddings = OllamaEmbeddings(
        model=os.getenv("OLLAMA_EMBEDDING_MODEL", "embeddinggemma"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )


@mcp.tool()
def get_owasp_index_status() -> dict:
    """Check whether the OWASP Chroma index is available."""
    return {
        "index_exists": index_exists(),
        "chroma_dir": str(CHROMA_DIR),
        "build_command": BUILD_INDEX_COMMAND,
    }


@mcp.tool()
def search_owasp_chunks(query: str, k: int = DEFAULT_RESULTS) -> list[dict]:
    """Search the OWASP Top 10 for LLM Applications index."""
    vector_store = load_vector_store()

    if vector_store is None:
        return [
            {
                "chunk_index": None,
                "text": f"Missing Chroma index. Run: {BUILD_INDEX_COMMAND}",
            }
        ]

    documents = vector_store.similarity_search(query, k=k)
    results = []

    for document in documents:
        results.append(
            {
                "chunk_index": document.metadata.get("chunk_index"),
                "text": document.page_content,
            }
        )

    return results


def main() -> None:
    load_dotenv()
    print(f"OWASP MCP server: http://{SERVER_HOST}:{SERVER_PORT}{MCP_PATH}")
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()

