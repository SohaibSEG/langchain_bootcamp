# Lab 03: LangChain Overview

## Goal

Map the support-ticket workflow into the LangChain building blocks you will use in the next labs.

## Scenario

You have already called Gemini directly. Now turn the same support-ticket task into a reusable application shape:

```text
ticket dictionary -> prompt template -> Gemini chat model -> string parser -> label or reply
```

The rest of the day builds this shape piece by piece.

## Components

- `ticket dictionary`: the application input
- `prompt template`: turns fields into a model-ready message
- `Gemini chat model`: produces the model response
- `string parser`: turns the chat response into plain text
- `chain`: connects the pieces

## Target Flow

```text
{
  "subject": "Cannot sign in after password reset",
  "message": "Sign in loops back to the same page."
}
        |
        v
ChatPromptTemplate
        |
        v
ChatGoogleGenerativeAI
        |
        v
StrOutputParser
        |
        v
"account"
```

## Practice Lab

Create a small design sketch for the next script before writing code.

1. Choose one ticket from `data/tickets.jsonl`.
2. Write the input dictionary with only `subject` and `message`.
3. Draft the system instruction for a ticket classifier.
4. Draft the human message template with `{subject}` and `{message}` placeholders.
5. Decide whether the final output should be a category label or a customer reply.
