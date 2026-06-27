from dotenv import load_dotenv
from langgraph.store.memory import InMemoryStore


def main() -> None:
    # Load .env for consistency with graph examples and LangSmith settings.
    # This script does not create a graph, so there may be nothing to trace.
    load_dotenv()

    # A store is long-term application memory.
    # Unlike a checkpointer, it is not tied to one graph thread.
    #
    # Checkpointer:
    # - saves graph state
    # - uses config["configurable"]["thread_id"]
    # - remembers one conversation/workflow thread
    #
    # Store:
    # - saves app data you choose
    # - uses namespaces and keys
    # - can be read from many different graph threads
    store = InMemoryStore()

    # Store data is organized by:
    # 1. namespace: a tuple that groups related records
    # 2. key: the id of one record inside that namespace
    # 3. value: a JSON-like dictionary
    namespace = ("customer_preferences", "cust_1001")

    store.put(namespace, "language", {"text": "reply in English"})
    store.put(namespace, "tone", {"text": "keep the tone direct and calm"})

    other_namespace = ("customer_preferences", "cust_1002")
    store.put(other_namespace, "language", {"text": "reply in French"})

    one_memory = store.get(namespace, "language")
    print("one memory:")
    print(one_memory.value)

    print("\nall customer preferences:")
    for item in store.search(namespace):
        print(item.key, item.value)

    print("\nother customer preferences:")
    for item in store.search(other_namespace):
        print(item.key, item.value)

    # Read the output:
    # - namespace separates one customer's memories from another
    # - key identifies one memory inside that namespace
    # - value is the actual saved data


if __name__ == "__main__":
    main()
