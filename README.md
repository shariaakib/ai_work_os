# AI Work OS

An AI-native Work OS — not another chatbot. Humans describe outcomes; specialist agents plan and execute.

**Live (Render free tier):** https://ai-work-os.onrender.com
**Repo:** https://github.com/shariaakib/ai_work_os

> Free-tier cold start can take **30–60 seconds** after idle. Wait, then hit `/api/health` again.

## Architecture

```
ai_work_os/
├── app/server.py + app/static/   # FastAPI API + PWA
├── src/core|agents|permissions|verification|tools
├── config/settings.py
├── tests/
├── render.yaml | Procfile | requirements.txt
└── .github/workflows/ci.yml
```

## Quick start (local)

```bash
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
# set OPENROUTER_API_KEY=sk-or-...
.venv\Scripts\python.exe app/server.py
# open http://localhost:8000
```

## Switching models (zero code change)

The active model is a **single environment variable** — `OPENROUTER_MODEL`. No code edits; change the value and restart.

Free-tier OpenRouter models end in `:free` and cost **$0** (rate-limited):

- `meta-llama/llama-3.3-70b-instruct:free` ← **default**
- `deepseek/deepseek-chat-v3.1:free`
- `qwen/qwen3-coder:free`
- `google/gemma-3-27b-it:free`

Paid (higher limits): `openai/gpt-4o-mini`, `anthropic/claude-3.5-haiku`, `google/gemini-2.0-flash-001`.

See the live active model at `GET /api/models` or in the app header.

## Production (Render)

1. Connect the GitHub repo; the Blueprint reads `render.yaml`.
2. Set **Environment → `OPENROUTER_API_KEY`** (and optionally `OPENROUTER_MODEL`).
3. Start: one gunicorn worker + UvicornWorker; health at `/api/health`.
4. Keep `main` and `master` in sync until the default branch is settled.

### Health check fields

`GET /api/health` returns `status`, `version`, `configured`, `model`, `environment`, `agents`.

- `configured: true` → an `OPENROUTER_API_KEY` is loaded; chat / planning work.
- `configured: false` → the API is up but **no key is set**. Locally it reads `.env`; on Render it reads the dashboard Environment — your local `.env` never ships to Render.

### Rotating your API key

If your key was ever pasted in plaintext anywhere (chat, ticket, log), **revoke it** at openrouter.ai → Keys, create a new one, and set it in both `.env` (local) and Render → Environment (production).

## API (summary)

- `GET /api/health` · `GET /api/agents` · `GET /api/models`
- `POST /api/chat` → `{response, reply}` (503 if no key)
- `POST /api/plan` · `POST /api/execute` (plan then execute)
- Memory + work graph under `/api/memory` and `/api/graph/*`

## Tests

```bash
.venv\Scripts\python.exe -m pytest tests/ -v
```

CI: `.github/workflows/ci.yml` (Python 3.11 + 3.12).

## Design

Outcomes over apps · OpenRouter model independence · user-owned memory · permissions · free-tier friendly (1 worker, slim deps).