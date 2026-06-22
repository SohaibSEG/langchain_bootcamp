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

## Scenario Checklist

- Create a reusable classifier prompt.
- Keep support instructions in the system message.
- Put ticket-specific values in the human message.
- Invoke the prompt with multiple tickets.
- Reuse the same template later in a chain.

## Practice Lab

Use the prompt template example as your starting point.

1. Create a prompt template that asks for a one-word ticket category.
2. Create a prompt template that asks for a polite two-sentence customer reply.
3. Add a `policy` variable to a prompt template so the model can follow support rules.
4. Invoke the prompt with two different tickets.
5. Replace a vague instruction with a more specific support instruction.
