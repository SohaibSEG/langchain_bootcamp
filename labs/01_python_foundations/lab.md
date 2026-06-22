# Lab 01: Python Foundations

## Goal

Build enough Python fluency to understand the rest of Day 1.

You will start the support assistant with plain Python. Before using Gemini or LangChain, you should be comfortable representing a ticket, inspecting fields, transforming text, and organizing repeated logic.

## Notebook Order

1. `notebooks/01_python_values_variables.ipynb`
2. `notebooks/02_python_dictionaries.ipynb`
3. `notebooks/03_python_lists.ipynb`
4. `notebooks/04_python_strings_conditions_loops.ipynb`
5. `notebooks/05_python_functions_type_hints.ipynb`
6. `notebooks/06_python_classes_inheritance.ipynb`

## What You Will Build

Start with one support ticket stored as simple values:

```python
ticket_subject = "Cannot sign in after password reset"
ticket_message = "The reset link worked, but sign in loops back to the same page."
```

Then represent the same ticket as a dictionary:

```python
ticket = {
    "id": "TCK-1002",
    "customer": "Noah",
    "subject": "Cannot sign in after password reset",
    "message": "The reset link worked, but sign in loops back to the same page.",
}
```

Then move to a list of tickets. From there, you will practice filtering, advanced string cleanup and formatting, list access and sorting, dictionary access patterns, JSON conversion, functions, type hints, classes, inheritance, method overrides, and abstract classes.

## Topics You Will Practice

- String cleanup with `.strip()`, `.lower()`, `.title()`, `.replace()`, `.split()`, and `.join()`
- String formatting with f-strings
- List indexing, negative indexing, slicing, appending, sorting, and list comprehensions
- Dictionary required access with `ticket["field"]`
- Dictionary safe access with `ticket.get("field", default)`
- Dictionary destructuring/unpacking with `**`
- Dictionary iteration with `.items()`
- Dictionary to JSON with `json.dumps()`
- JSON to dictionary with `json.loads()`
- Function positional arguments
- Function named arguments
- Function default argument values
- Class inheritance with `super()`
- Method overriding in subclasses
- Abstract classes with `ABC` and `@abstractmethod`

## Scenario Checklist

- Store one incoming ticket.
- Normalize the text fields.
- Add queue and priority fields.
- Convert the ticket to JSON for storage or transport.
- Route several tickets from a list.
- Package repeated logic into functions.
- Model tickets and formatting behavior with classes.

## Practice Lab

Use the notebooks as your workspace. Build one ticket and keep improving it as you move through the notebook sequence.

1. Create variables for a new support ticket: ticket id, customer name, subject, message, and channel.
2. Print a one-line summary with an f-string.
3. Represent the same ticket as a dictionary.
4. Read the subject with required access: `ticket["subject"]`.
5. Read a missing priority with safe access: `ticket.get("priority", "normal")`.
6. Create a new dictionary with `**` destructuring/unpacking and add `priority` and `queue`.
7. Convert the dictionary to JSON with `json.dumps()`, then convert it back with `json.loads()`.
8. Create a list of three ticket dictionaries.
9. Practice first item access, last item access, slicing the first two items, and looping over every ticket id.
10. Create a comma-separated label string such as `"billing,urgent,refund"`, split it into a list, sort it, and print it.
11. Write a function that returns `"urgent"` when the ticket message contains `"blocked"`, `"production"`, or `"charged twice"`.
12. Write a formatting function with `ticket_id`, `subject`, and `priority` parameters. Call it once with positional arguments and once with named arguments.
13. Create a `SupportTicket` class with a display-title method.
14. Create an `EscalatedTicket` subclass that overrides the display-title method and includes `"URGENT"`.
15. Create an abstract `TicketFormatter` class with an abstract `format` method, then create one concrete formatter subclass.
