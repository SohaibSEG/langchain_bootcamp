# Lab 00: Setup

## Goal

Prepare your local Python environment and learn where each part of the Day 1 repo lives.

You will use notebooks for Python practice, Markdown labs for guided reading, and scripts for complete examples you can run from the terminal.

## Environment

Use Python 3.11 or newer.

```bash
python --version
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and set:

```env
GOOGLE_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
```

## Repository Tour

- `notebooks/`: Python foundations. Open these, edit values, and rerun cells.
- `labs/`: Guided Markdown lessons. Read these before and during each topic.
- `scripts/`: Complete examples you can run end to end.
- `data/`: Small support ticket data and policy text.
- `docs/`: Reference material you can return to later.

## First Check

Run:

```bash
python scripts/01_gemini_smoke_test.py
```

If this fails because credentials are missing, fix `.env` before moving to the Gemini labs.
