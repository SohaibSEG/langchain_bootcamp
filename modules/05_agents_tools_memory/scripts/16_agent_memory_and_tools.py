import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore


# This script lives at modules/05_agents_tools_memory/scripts/.
# parents[3] is the repository root, no matter where the repo was cloned.
ROOT = Path(__file__).resolve().parents[3]
POLICY_PATH = ROOT / "data" / "support_policy.md"

CUSTOMERS = {
    "Maya": {"plan": "Pro", "account_status": "active"},
    "Noah": {"plan": "Team", "account_status": "active"},
    "Leo": {"plan": "Enterprise", "account_status": "active"},
}


def message_text(message) -> str:
    # Gemini may return content as a list of blocks instead of a plain string.
    # For display, keep only text blocks and ignore provider metadata.
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


@tool
def lookup_customer(customer_name: str) -> dict:
    """Look up a customer's support profile by customer name."""
    return CUSTOMERS.get(customer_name, {"error": "Customer not found."})


@tool
def read_support_policy() -> str:
    """Read the support policy for severity, routing, and reply style."""
    return POLICY_PATH.read_text(encoding="utf-8")


@tool
def get_customer_preferences(customer_name: str) -> list[str]:
    """Read saved long-term support preferences for a customer."""
    # This tool reads long-term memory from the store.
    # It is intentionally simple: the global store belongs to this script.
    memories = MEMORY_STORE.search(("customer_preferences", customer_name))
    return [item.value["text"] for item in memories]


def build_memory_store() -> InMemoryStore:
    store = InMemoryStore()

    # Long-term memory is app data, not chat history.
    # These preferences can be used from any conversation thread.
    store.put(
        ("customer_preferences", "Maya"),
        "tone",
        {"text": "Use a direct and calm tone."},
    )
    store.put(
        ("customer_preferences", "Maya"),
        "billing",
        {"text": "For billing issues, mention that finance deadlines are important."},
    )
    store.put(
        ("customer_preferences", "Leo"),
        "technical_detail",
        {"text": "Include technical next steps for API incidents."},
    )

    return store


MEMORY_STORE = build_memory_store()


def build_agent():
    model = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        temperature=0.2,
    )

    return create_agent(
        model=model,
        tools=[lookup_customer, read_support_policy, get_customer_preferences],
        system_prompt=(
            "You are a support triage assistant. Use tools when account, policy, "
            "or saved customer preference details would improve the answer. "
            "Use chat history for follow-up questions in the same thread."
        ),
        # create_agent uses LangGraph state under the hood.
        # LangChain's built-in agent state includes a "messages" list.
        #
        # Checkpointer = short-term chat history for this thread_id.
        # Store = long-term customer preferences read by get_customer_preferences.
        checkpointer=InMemorySaver(),
    )


def main() -> None:
    load_dotenv()

    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY is missing. Copy .env.example to .env and set it.")

    agent = build_agent()
    thread_id = input("Thread id [agent-memory-tools]: ").strip() or "agent-memory-tools"

    # Same thread_id keeps the same chat history.
    # The store is different: it holds customer preferences outside the thread.
    config = {"configurable": {"thread_id": thread_id}}

    print("Paste a support ticket. Type 'exit' to stop.")
    print("Try: Customer Maya says she was charged twice for the annual plan.")
    print("Then ask: Can you rewrite the reply with her preferences?")

    while True:
        text = input("\nTicket: ").strip()
        if text.lower() in {"exit", "quit"}:
            break
        if not text:
            continue

        # Agent input is a state update.
        # The "messages" key is defined by LangChain's agent state contract.
        #
        # We pass only the newest HumanMessage. The checkpointer restores old
        # messages for the same thread_id before the agent runs.
        state_update = {"messages": [HumanMessage(content=text)]}

        result = agent.invoke(
            state_update,
            config=config,
        )
        print(f"Assistant: {message_text(result['messages'][-1])}")


if __name__ == "__main__":
    main()
