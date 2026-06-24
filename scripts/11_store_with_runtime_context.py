from dataclasses import dataclass
from typing import TypedDict

from dotenv import load_dotenv
from langgraph.graph import START, StateGraph
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore


@dataclass
class RequestContext:
    # The graph will use this id to choose which store namespace to read.
    customer_id: str


class TicketState(TypedDict):
    message: str
    preferences: list[str]
    response: str


def load_customer_preferences(
    state: TicketState,
    runtime: Runtime[RequestContext],
) -> TicketState:
    # This node combines two ideas:
    # - runtime.context tells us which customer this run is for
    # - runtime.store lets us read long-term memory
    assert runtime.store is not None

    namespace = ("customer_preferences", runtime.context.customer_id)
    memories = runtime.store.search(namespace)

    return {
        "preferences": [item.value["text"] for item in memories],
    }


def draft_plain_response(state: TicketState) -> TicketState:
    # This is intentionally not an LLM call.
    # The goal is to show how data moves through the graph.
    preferences = ", ".join(state["preferences"]) or "no saved preferences"
    return {
        "response": f"Draft for: {state['message']} | Preferences: {preferences}",
    }


def build_graph(store: InMemoryStore):
    # This graph introduces no new LangGraph shape:
    # START -> load preferences -> draft response
    #
    # The only new idea is how the graph gets long-term memory:
    # - context chooses the customer
    # - store contains the saved preferences
    graph = StateGraph(TicketState, context_schema=RequestContext)
    graph.add_node("load_customer_preferences", load_customer_preferences)
    graph.add_node("draft_plain_response", draft_plain_response)
    graph.add_edge(START, "load_customer_preferences")
    graph.add_edge("load_customer_preferences", "draft_plain_response")

    # compile(store=...) makes the store available as runtime.store inside nodes.
    # This is different from a checkpointer. A checkpointer saves graph state.
    # A store provides long-term app data to graph nodes.
    return graph.compile(store=store)


def main() -> None:
    # Load .env so LangSmith tracing settings are available for this graph run.
    load_dotenv()

    store = InMemoryStore()
    store.put(
        ("customer_preferences", "cust_1001"),
        "language",
        {"text": "reply in English"},
    )
    store.put(
        ("customer_preferences", "cust_1001"),
        "tone",
        {"text": "keep the tone direct and calm"},
    )

    app = build_graph(store)

    result = app.invoke(
        {
            "message": "Maya cannot export invoices again.",
            "preferences": [],
            "response": "",
        },
        # context is not state. It tells this run which customer to load.
        context=RequestContext(customer_id="cust_1001"),
    )

    print(result)


if __name__ == "__main__":
    main()
