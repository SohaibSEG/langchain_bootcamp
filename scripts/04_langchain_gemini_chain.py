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
    load_dotenv()

    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY is missing. Copy .env.example to .env and set it.")

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    model = ChatGoogleGenerativeAI(model=model_name, temperature=0)

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

    chain = prompt | model | StrOutputParser()

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
