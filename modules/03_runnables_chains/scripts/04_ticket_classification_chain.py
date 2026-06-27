from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from rich import print


def main() -> None:
    # Load GOOGLE_API_KEY and optional GEMINI_MODEL from .env.
    load_dotenv()

    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY is missing. Copy .env.example to .env and set it.")

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Use a low-temperature model for classification so labels are more stable.
    model = ChatGoogleGenerativeAI(model=model_name, temperature=0)

    # The system message defines the classification task.
    # The human message injects one ticket at runtime.
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                "You classify customer support tickets. Return a category and one concise reason.",
            ),
            HumanMessagePromptTemplate.from_template(
                "Subject: {subject}\nMessage: {message}",
            ),
        ]
    )

    # The parser extracts the assistant message text from the chat response.
    chain = prompt | model | StrOutputParser()

    # One dictionary enters the chain. Its keys match {subject} and {message}.
    result = chain.invoke(
        {
            "subject": "Cannot sign in after password reset",
            "message": "The reset link worked, but sign in loops back to the same page.",
        }
    )

    print("[bold]LangChain chain result[/bold]")
    print(result)


if __name__ == "__main__":
    main()
