# Lab 06: Invocations and Chains

## Goal

Combine prompt templates, Gemini, and output parsing into a complete LangChain chain.

## Run It

```bash
python scripts/04_ticket_classification_chain.py
```

## Core Shape

```text
ticket input -> prompt template -> Gemini chat model -> string parser -> reply
```

## Example

```python
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_google_genai import ChatGoogleGenerativeAI

prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template("You classify support tickets."),
        HumanMessagePromptTemplate.from_template("Subject: {subject}\nMessage: {message}"),
    ]
)

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
chain = prompt | model | StrOutputParser()

result = chain.invoke(
    {
        "subject": "Cannot sign in after password reset",
        "message": "Sign in loops back to the same page.",
    }
)
```

## Scenario

You are building the first complete LangChain classifier for one support ticket. The chain should accept a ticket dictionary and return a short model-generated result.

## Practice Lab

Open `scripts/04_ticket_classification_chain.py` and change one part at a time.

1. Modify the chain so it returns only a category label.
2. Modify the chain so it returns a suggested reply instead of a category.
3. Add one extra input variable named `tone` and use it in the prompt.
4. Change the system message and run the script again.
5. Add a second ticket input and invoke the same chain again.
