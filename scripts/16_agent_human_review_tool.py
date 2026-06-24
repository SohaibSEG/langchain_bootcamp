import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command


@tool
def create_internal_note(ticket_id: str, note: str) -> str:
    """Create an internal support note."""
    return f"Created internal note for {ticket_id}: {note}"


@tool
def send_customer_email(to: str, subject: str, body: str) -> str:
    """Send an email to a customer."""
    return f"Sent email to {to} with subject {subject!r}."


def build_agent():
    model = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        temperature=0.2,
    )

    safe_note_tool_name = create_internal_note.name
    risky_email_tool_name = send_customer_email.name

    # Middleware wraps part of the agent runtime.
    # This middleware watches tool calls before they execute.
    #
    # Use tool.name instead of repeated string literals so the middleware config
    # stays correct if the Python function/tool is renamed.
    human_review_middleware = HumanInTheLoopMiddleware(
        interrupt_on={
            # This tool writes private support context, so it can run directly.
            safe_note_tool_name: False,
            # This tool contacts a customer, so it pauses for approval first.
            risky_email_tool_name: {
                "allowed_decisions": ["approve", "reject"],
            },
        },
        description_prefix="Customer email requires review",
    )

    return create_agent(
        model=model,
        tools=[create_internal_note, send_customer_email],
        system_prompt=(
            "You are a support operations assistant. Create internal notes when "
            "useful. If asked to contact a customer, use send_customer_email."
        ),
        middleware=[human_review_middleware],
        # Required for pause/resume.
        checkpointer=InMemorySaver(),
    )


def get_interrupt_payload(result):
    # A paused graph returns an interrupt payload.
    # For normal graph results it is stored under "__interrupt__".
    # Some wrappers expose the same information through an interrupts attribute.
    if isinstance(result, dict) and "__interrupt__" in result:
        return result["__interrupt__"][0].value
    if hasattr(result, "interrupts") and result.interrupts:
        return result.interrupts[0].value
    return None


def get_messages(result):
    if isinstance(result, dict):
        return result["messages"]
    return result.value["messages"]


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


def print_review_payload(payload: dict) -> None:
    print("Review required:")

    action_requests = payload.get("action_requests", [])
    review_configs = payload.get("review_configs", [])

    allowed_by_action = {
        config.get("action_name"): config.get("allowed_decisions", [])
        for config in review_configs
    }

    for index, action in enumerate(action_requests, start=1):
        name = action.get("name", "unknown_action")
        args = action.get("args", {})
        allowed = allowed_by_action.get(name, [])

        print(f"\nAction {index}: {name}")

        if allowed:
            print(f"Allowed decisions: {', '.join(allowed)}")

        print("Arguments:")
        for key, value in args.items():
            if isinstance(value, str) and "\n" in value:
                print(f"- {key}:")
                for line in value.splitlines():
                    print(f"  {line}")
            else:
                print(f"- {key}: {value}")


def main() -> None:
    load_dotenv()

    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY is missing. Copy .env.example to .env and set it.")

    agent = build_agent()
    config = {"configurable": {"thread_id": "agent-human-review"}}

    print("Chat with the support assistant. Type 'exit' to stop.")
    print("To trigger review, ask it to email a customer.")
    print("Example: Ticket TCK-3001. Maya cannot export invoices. Email maya@example.com.")

    while True:
        text = input("\nYou: ").strip()
        if text.lower() in {"exit", "quit"}:
            break
        if not text:
            continue

        result = agent.invoke(
            {"messages": [HumanMessage(content=text)]},
            config=config,
        )

        interrupt_payload = get_interrupt_payload(result)

        if interrupt_payload is None:
            print("Assistant:")
            print(message_text(get_messages(result)[-1]))
            continue

        print_review_payload(interrupt_payload)

        decision = input("Decision [approve/reject]: ").strip().lower()
        if decision not in {"approve", "reject"}:
            decision = "reject"

        final_result = agent.invoke(
            Command(resume={"decisions": [{"type": decision}]}),
            config=config,
        )

        print("\nAssistant:")
        print(message_text(get_messages(final_result)[-1]))


if __name__ == "__main__":
    main()
