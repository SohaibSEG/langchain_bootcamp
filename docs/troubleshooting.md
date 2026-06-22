# Troubleshooting

## `GOOGLE_API_KEY` is missing

Copy `.env.example` to `.env` and set your key:

```bash
cp .env.example .env
```

Then edit `.env`.

## Import errors

Make sure the virtual environment is active and dependencies are installed:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Notebook kernel does not show up

Install the current environment as a notebook kernel:

```bash
python -m ipykernel install --user --name langchain-day1 --display-name "Python (langchain-day1)"
```

## Gemini quota or authentication errors

Check that the API key is valid, billing or quota is enabled for the account, and the selected model is available for the key.

## Model output differs from the lab

That is expected. Model output is probabilistic. Teach the shape of the workflow, not exact wording.
