import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "data" / "support_policy.md"

CUSTOMERS = {
    "Maya": {
        "plan": "Pro",
        "account_status": "active",
        "recent_ticket": "Duplicate annual charge.",
    },
    "Noah": {
        "plan": "Team",
        "account_status": "active",
        "recent_ticket": "Password reset sign-in loop.",
    },
    "Leo": {
        "plan": "Enterprise",
        "account_status": "active",
        "recent_ticket": "Production checkout API timeout.",
    },
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
    # A tool is a normal Python function the model is allowed to call.
    # The function name, type hints, and docstring tell the model how to use it.
    return CUSTOMERS.get(customer_name, {"error": "Customer not found."})


@tool
def read_support_policy() -> str:
    """Read the support policy for severity, routing, and reply style."""
    # This tool has no arguments because the policy file is fixed for the app.
    return POLICY_PATH.read_text(encoding="utf-8")


def build_agent():
    model = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        temperature=0.2,
    )

    # create_agent returns a LangGraph compiled graph.
    #
    # LangChain's agent state includes a "messages" field by contract.
    # That is why the invoke call below sends {"messages": [HumanMessage(...)]}.
    #
    # The agent graph runs a model loop:
    # 1. read the user message
    # 2. decide whether a tool is needed
    # 3. call the tool if needed
    # 4. use the tool result to answer
    #
    # The checkpointer gives the agent short-term chat memory.
    return create_agent(
        model=model,
        tools=[lookup_customer, read_support_policy],
        system_prompt=(
            "You are a support triage assistant. Use tools when customer "
            "profile or policy details would change the answer. Keep the final "
            "answer short: severity, queue, and first reply."
        ),
        checkpointer=InMemorySaver(),
    )


def main() -> None:
    load_dotenv()

    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY is missing. Copy .env.example to .env and set it.")

    agent = build_agent()
    thread_id = input("Thread id [support-tool-agent]: ").strip() or "support-tool-agent"

    # Same checkpoint rule as before:
    # "thread_id" is the LangGraph-defined key for saved conversation state.
    config = {"configurable": {"thread_id": thread_id}}

    print("Paste a support ticket. Type 'exit' to stop.")
    print("Try: Customer Leo says checkout API requests are timing out.")

    while True:
        text = input("\nTicket: ").strip()
        if text.lower() in {"exit", "quit"}:
            break
        if not text:
            continue

        # This is not the full chat history.
        # It is a state update containing only the newest message.
        #
        # Because this agent has a checkpointer, LangGraph loads the saved
        # state for config["configurable"]["thread_id"] before applying this
        # update. The saved state already contains earlier messages.
        #
        # During the run, the agent may add tool messages and the final AI
        # message to the same "messages" state.
        state_update = {"messages": [HumanMessage(content=text)]}

        result = agent.invoke(
            state_update,
            config=config,
        )
        print(f"Assistant: {message_text(result['messages'][-1])}")


if __name__ == "__main__":
    main()
