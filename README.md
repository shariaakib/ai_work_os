# AI Work OS

An AI-native Work OS — not another chatbot. Humans describe outcomes; specialist agents plan and execute.

**Live (Render free tier):** https://ai-work-os.onrender.com  
**Repo:** https://github.com/shariaakib/ai_work_os

> Free-tier cold start can take **30–60 seconds** after idle. Wait, then hit /api/health again.

## Architecture

`
ai_work_os/
├── app/server.py + app/static/   # FastAPI API + PWA
├── src/core|agents|permissions|verification|tools
├── config/settings.py
├── tests/
├── render.yaml | Procfile | requirements.txt
└── .github/workflows/ci.yml
`

## Quick start (local)

`ash
py -m venv .venv
.venv\\Scripts\\python.exe -m pip install -r requirements.txt
copy .env.example .env
# set OPENROUTER_API_KEY=sk-or-...
.venv\\Scripts\\python.exe app/server.py
# open http://localhost:8000
`

## Production (Render)

1. Connect GitHub repo; Blueprint uses 
ender.yaml.
2. Set **Environment → OPENROUTER_API_KEY**.
3. Start: one gunicorn worker + UvicornWorker; health /api/health.
4. Keep main and master in sync until default branch is settled.

Health JSON includes status, ersion, configured, environment, gents.

## API (summary)

- GET /api/health · GET /api/agents
- POST /api/chat → {response, reply} (503 if no key)
- POST /api/plan · POST /api/execute (plan then execute)
- Memory + work graph under /api/memory and /api/graph/*

## Tests

`ash
.venv\\Scripts\\python.exe -m pytest tests/ -v
`

CI: .github/workflows/ci.yml (Python 3.11 + 3.12).

## Design

Outcomes over apps · OpenRouter model independence · user-owned memory · permissions · free-tier friendly (1 worker, slim deps).
