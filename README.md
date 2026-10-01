# AI-Driven System for Idiomatic Code Translation

An AI-assisted code translation system that translates between programming languages, generates alternative implementations, detects design patterns, and provides code analysis and documentation features.

## Requirements

- Python 3.10 or newer
- A Hugging Face access token and a compatible model ID for AI translation

## Setup

From the repository root, create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set `HF_API_TOKEN` and `MODEL_ID`. `API_KEY` is optional for local development. Keep `.env` private.

## Run

```powershell
python backend/app.py
```

Open the main interface at <http://127.0.0.1:5000/new>. The backend API listens on port 5000 by default; set `FLASK_PORT` in `.env` to change it.
