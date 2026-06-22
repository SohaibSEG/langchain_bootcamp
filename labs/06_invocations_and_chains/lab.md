# Lab 06: Invocations and Chains

## Goal

Combine prompt templates, Gemini, and output parsing into a complete LangChain chain.

## Run It

```bash
python scripts/04_langchain_gemini_chain.py
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

## What To Notice

The chain is still a model call, but the application code is now organized around reusable pieces.
