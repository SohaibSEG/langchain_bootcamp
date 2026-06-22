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

## What To Notice

- Plain Python is enough to represent and transform support-ticket data.
- Dictionaries are useful when you need named fields.
- Lists are useful when you need many tickets.
- JSON is text, while a dictionary is a Python object.
- Named arguments can make function calls easier to read.
- Functions help you reuse decisions.
- Classes help when a concept has stable data and behavior.
- Method overrides let subclasses keep the same interface while changing behavior.
- Abstract classes define methods that subclasses must implement.
