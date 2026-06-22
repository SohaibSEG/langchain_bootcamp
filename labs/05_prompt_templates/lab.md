# Lab 05: Prompt Templates

## Goal

Turn hand-written prompts into reusable templates.

## Problem

This prompt works for one ticket:

```text
Classify this ticket:
Subject: Charged twice for annual plan
Message: I upgraded yesterday and my card shows two annual charges.
```

In an application, you need to fill in different subjects and messages many times. A prompt template gives you one reusable structure.

## Prompt Template

```python
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template("You classify support tickets."),
        HumanMessagePromptTemplate.from_template("Subject: {subject}\nMessage: {message}"),
    ]
)

messages = prompt.invoke(
    {
        "subject": "Charged twice for annual plan",
        "message": "I upgraded yesterday and my card shows two annual charges.",
    }
)
```

## What To Notice

- Templates make repeated prompts consistent.
- Variables make prompts reusable.
- Chat templates preserve message roles.
- Prompt templates can be chained into models.
