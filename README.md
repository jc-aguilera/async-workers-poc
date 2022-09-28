# Asynchronous worker POC

This is a simple library to retrieve jobs from a DB, run them, then mark them as complete.
## Install

To install, create a Python virtual environment. For example:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

To run: activate your virtual environment and run
```bash
uvicorn asgi_app:app --port 3100
```
