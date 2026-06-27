from dataclasses import dataclass
from typing import TypedDict

from dotenv import load_dotenv
from langgraph.graph import START, StateGraph
from langgraph.runtime import Runtime


@dataclass
class RequestContext:
    # Runtime context is information about this run.
    # It is not state because the graph does not update it.
    #
    # State is the ticket data moving through the graph.
    # Context is app data the graph can read while running.
    customer_id: str
    support_agent: str


class TicketState(TypedDict):
    subject: str
    message: str
    assigned_to: str
    customer_id: str


def attach_request_context(
    state: TicketState,
    runtime: Runtime[RequestContext],
) -> TicketState:
    # runtime.context comes from app.invoke(..., context=...).
    # Use it for values the app already knows, such as the current customer.
    return {
        "customer_id": runtime.context.customer_id,
        "assigned_to": runtime.context.support_agent,
    }


def build_graph():
    # context_schema tells LangGraph what type of context this graph expects.
    # Without it, the node would not receive Runtime[RequestContext].
    graph = StateGraph(TicketState, context_schema=RequestContext)
    graph.add_node("attach_request_context", attach_request_context)
    graph.add_edge(START, "attach_request_context")
    return graph.compile()


def main() -> None:
    # Load .env so LangSmith tracing settings are available for this graph run.
    load_dotenv()

    app = build_graph()

    result = app.invoke(
        # This is graph state. Nodes can update these fields.
        {
            "subject": "Invoice export failed",
            "message": "The export button fails for this customer.",
            "assigned_to": "",
            "customer_id": "",
        },
        # This is runtime context. It is read-only information for this run.
        context=RequestContext(
            customer_id="cust_1001",
            support_agent="Nadia",
        ),
    )

    print(result)


if __name__ == "__main__":
    main()
