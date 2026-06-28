import asyncio
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver


MCP_SERVER_URL = "http://localhost:8000/mcp"


def message_text(message) -> str:
    content = message.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        return "\n".join(part for part in parts if part)
    return str(content)


async def load_mcp_tools():
    client = MultiServerMCPClient(
        {
            "owasp": {
                "transport": "streamable_http",
                "url": MCP_SERVER_URL,
            }
        }
    )
    return await client.get_tools()


def build_agent(tools):
    model = ChatOllama(
        model=os.getenv("OLLAMA_CHAT_MODEL", "gemma4:e4b"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0,
    )

    return create_agent(
        model=model,
        tools=tools,
        system_prompt=(
            "You answer questions about the OWASP Top 10 for LLM Applications. "
            "Use the MCP tools to search the OWASP index before answering. "
            "If the tools do not return enough context, say that the OWASP index "
            "does not support an answer."
        ),
        checkpointer=InMemorySaver(),
    )


async def main() -> None:
    load_dotenv()

    try:
        tools = await load_mcp_tools()
    except Exception as exc:
        print(f"Could not connect to MCP server at {MCP_SERVER_URL}: {exc}")
        print("Start the server first:")
        print("python modules/08_mcp_owasp_tools/scripts/21_owasp_mcp_server.py")
        return

    agent = build_agent(tools)
    thread_id = input("Thread id [owasp-mcp-agent]: ").strip() or "owasp-mcp-agent"
    config = {"configurable": {"thread_id": thread_id}}

    print("OWASP MCP agent chat. Type 'exit' to stop.")

    while True:
        text = input("\nYou: ").strip()
        if text.lower() in {"exit", "quit"}:
            break
        if not text:
            continue

        try:
            result = await agent.ainvoke(
                {"messages": [HumanMessage(content=text)]},
                config=config,
            )
        except Exception as exc:
            print(f"Agent call failed: {exc}")
            print("Check that Ollama and the MCP server are running.")
            continue

        print("Assistant:")
        print(message_text(result["messages"][-1]))


if __name__ == "__main__":
    asyncio.run(main())
