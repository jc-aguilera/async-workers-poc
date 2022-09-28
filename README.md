# Asynchronous worker POC

This is a simple library to retrieve jobs from a DB, run them, then mark them as complete.
## Install

To install, clone the repo, then create a Python virtual environment. For example:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Or, with [Poetry](https://python-poetry.org/):
```bash
poetry install
```

To run: activate your virtual environment and run
```bash
uvicorn examples.asgi_app:app --port 8050
```

Or, with Poetry:
```
poetry run app
```
