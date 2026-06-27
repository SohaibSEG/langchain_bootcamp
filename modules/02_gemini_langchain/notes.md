# Gemini And LangChain

This document explains the first model scripts and the LangChain pieces used later.

Scripts:

```bash
python modules/02_gemini_langchain/scripts/01_gemini_smoke_test.py
python modules/02_gemini_langchain/scripts/03_gemini_summarization_chain.py
python modules/03_runnables_chains/scripts/04_ticket_classification_chain.py
python modules/03_runnables_chains/scripts/05_support_ticket_pipeline.py
```

## Direct Gemini API

The first model script calls Gemini directly.

Purpose:

```text
verify GOOGLE_API_KEY
verify the selected Gemini model works
separate provider setup from LangChain concepts
```

Typical setup:

```python
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Reply with one short sentence.",
)

print(response.text)
```

This is provider-specific code.

It is useful for smoke testing.

It is not yet a LangChain chain.

## LangChain Model Wrapper

LangChain wraps provider models behind common interfaces.

Gemini through LangChain:

```python
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2,
)
```

The wrapper lets you compose:

```text
prompt -> model -> parser
```

The model wrapper does not remove the need to understand the provider.

It gives you a common interface for:

```text
messages
runnables
chains
tools
agents
tracing
```

## Message Classes

For chat models, inputs are messages.

Common message types:

```python
from langchain_core.messages import HumanMessage, SystemMessage

messages = [
    SystemMessage(content="You are a support assistant."),
    HumanMessage(content="Customer Maya was charged twice."),
]

response = model.invoke(messages)
```

Use message classes when you want to see the chat message shape directly.

Prompt templates can create these messages for you.

## Prompt Templates

A prompt template is a reusable message builder.

Example:

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a support assistant."),
        ("human", "Ticket: {message}"),
    ]
)
```

Invoke it:

```python
messages = prompt.invoke(
    {"message": "I was charged twice for the annual plan."}
)
```

The placeholder is filled:

```text
{message} -> "I was charged twice for the annual plan."
```

Prompt templates are useful because the prompt structure stays stable while runtime values change.

## Output Parsers

Model responses are message objects.

For simple text output, use:

```python
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()
```

In a chain:

```python
chain = prompt | model | StrOutputParser()
```

Input:

```python
{"message": "Long customer ticket text..."}
```

Output:

```python
"Short summary text..."
```

## Simple Summarization Chain

Script:

```bash
python modules/02_gemini_langchain/scripts/03_gemini_summarization_chain.py
```

Concept:

```text
prompt -> Gemini -> string parser
```

Minimal shape:

```python
chain = prompt | model | StrOutputParser()

summary = chain.invoke(
    {
        "message": "Customer says invoice export fails every time."
    }
)
```

This script comes before more complex runnable examples because it shows the smallest useful chain first.

## Classification Chain

Script:

```bash
python modules/03_runnables_chains/scripts/04_ticket_classification_chain.py
```

The classification chain asks Gemini to classify a support ticket.

The important design choice:

```text
low temperature
clear category options
short output
```

Classification is used later for routing and support workflows.

## Structured Output

For routing or graph decisions, plain text is fragile.

Structured output gives code predictable fields.

Example schema:

```python
from typing import Literal
from pydantic import BaseModel


class TriageDecision(BaseModel):
    category: Literal["billing", "account", "engineering", "product", "support"]
    severity: Literal["urgent", "high", "normal"]
    queue: Literal["Billing", "Account", "Engineering Escalation", "Support"]
    reason: str
```

Use it with the model:

```python
structured_model = model.with_structured_output(TriageDecision)
decision = structured_model.invoke(messages)
```

Then code can safely read:

```python
decision.category
decision.severity
decision.queue
```

This is better than parsing a paragraph.

## Support Ticket Pipeline

Script:

```bash
python modules/03_runnables_chains/scripts/05_support_ticket_pipeline.py
```

The pipeline introduces a realistic support flow:

```text
load ticket
  -> classify / triage
  -> route to queue
  -> draft reply
```

The script still runs as a normal Python script.

LangGraph is introduced later when the workflow needs named steps, branching, memory, and runtime state.
