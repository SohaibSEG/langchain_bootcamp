# MCP OWASP Tools Notes

MCP means Model Context Protocol.

MCP gives a standard shape to tool integration:

```text
MCP server -> exposes tools
MCP client -> consumes tools
tool       -> callable capability
transport  -> how client and server communicate
```

This module reuses the OWASP RAG index from module 07. The MCP server exposes
search over that index as remote tools. The MCP client loads those tools into a
LangChain agent.

## Run Order

Build the OWASP index first:

```bash
python modules/07_rag_owasp_llm/scripts/19_owasp_llm_build_index.py
```

Start the MCP server in one terminal:

```bash
python modules/08_mcp_owasp_tools/scripts/21_owasp_mcp_server.py
```

Start the MCP client in another terminal:

```bash
python modules/08_mcp_owasp_tools/scripts/22_owasp_mcp_agent_client.py
```

## Why HTTP

This module uses HTTP so the boundary is visible:

```text
agent process
  -> MCP client
  -> HTTP transport
  -> MCP server
  -> Chroma index
```

The server runs at:

```text
http://localhost:8000/mcp
```

## Server Tools

The server exposes two tools.

```python
search_owasp_chunks(query: str, k: int = 4) -> list[dict]
```

This searches the OWASP Chroma index and returns simple dictionaries:

```python
{
    "chunk_index": 12,
    "text": "..."
}
```

```python
get_owasp_index_status() -> dict
```

This reports whether the Chroma index exists.

## Client Flow

The client uses `MultiServerMCPClient`:

```python
client = MultiServerMCPClient(
    {
        "owasp": {
            "transport": "streamable_http",
            "url": "http://localhost:8000/mcp",
        }
    }
)
```

Then it loads the remote MCP tools:

```python
tools = await client.get_tools()
```

Those tools are passed to a LangChain agent:

```python
agent = create_agent(model=model, tools=tools, checkpointer=InMemorySaver())
```

The model decides when to call the MCP tools. Tool calls and tool outputs are
best inspected in LangSmith traces.

## Example Questions

```text
What is prompt injection?
What does OWASP say about excessive agency?
Search the OWASP index for insecure output handling.
What does the index contain about sensitive information disclosure?
```
