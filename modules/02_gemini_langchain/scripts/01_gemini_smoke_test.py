from __future__ import annotations

import os

from dotenv import load_dotenv
from google import genai
from rich import print


def main() -> None:
    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is missing. Copy .env.example to .env and set it.")

    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    client = genai.Client(api_key=api_key)

    prompt = """
Classify this support ticket as billing, account, technical, or product.

Subject: Charged twice for annual plan
Message: I upgraded yesterday and my card shows two annual charges.

Return a short explanation for your classification.
""".strip()

    response = client.models.generate_content(model=model, contents=prompt)
    print("[bold]Gemini response[/bold]")
    print(response.text)


if __name__ == "__main__":
    main()
