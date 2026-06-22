import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_google_genai import ChatGoogleGenerativeAI


def main() -> None:
    # Load GOOGLE_API_KEY and optional GEMINI_MODEL from .env.
    load_dotenv()

    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY is missing. Copy .env.example to .env and set it.")

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # temperature=0 makes the example more repeatable for teaching.
    model = ChatGoogleGenerativeAI(model=model_name, temperature=0)

    # A chat prompt has roles. The system message gives the model its job;
    # the human message carries the runtime input.
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                "Summarize customer support messages for a busy support teammate.",
            ),
            HumanMessagePromptTemplate.from_template(
                "Message:\n{message}\n\nWrite one short sentence.",
            ),
        ]
    )

    # This is the core runnable chain:
    # input dict -> prompt -> Gemini -> plain string output.
    chain = prompt | model | StrOutputParser()

    # The input keys must match the placeholders in the prompt template.
    summary = chain.invoke(
        {
            "message": (
                "I upgraded yesterday and my card shows two annual charges. "
                "Please fix this before my finance team closes the month."
            )
        }
    )

    # Print only the result. Explanation belongs in the lab text and comments.
    print(summary)


if __name__ == "__main__":
    main()
