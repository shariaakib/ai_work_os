# AI Work OS

An AI-native Work OS — not another chatbot, not just a collection of AI tools, and not simply a prettier ChatGPT interface.

## The Vision

Instead of humans learning how to operate dozens of software applications, humans describe what they want to accomplish, and AI figures out how to get it done.

**From apps to outcomes. From software users to AI-assisted workers. From individual AI chats to an intelligent workplace.**

## Project Structure

```
ai-work-os/
├── src/
│   ├── core/           # Core system: AI Manager, Work Graph, Memory
│   ├── agents/         # Specialist AI workers
│   ├── tools/          # Tool integrations (web, docs, APIs)
│   ├── permissions/    # Permission & safety system
│   └── verification/   # Result verification
├── config/             # Configuration
├── tests/              # Test suite
└── VISION.md           # Full vision document
```

## Getting Started

```bash
# Create virtual environment
py -m venv .venv

# Activate it
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Core Concepts

- **AI Manager** — Coordinates specialist agents to accomplish user goals
- **Work Graph** — Understands relationships between work items
- **Persistent Memory** — Learns user preferences and context
- **Specialist Agents** — Research, Analysis, Writing, Development, etc.
- **Permissions System** — Safe (auto), Approval (ask), High-risk (confirm)
- **Model Independence** — Works with Claude, GPT, Gemini, DeepSeek, etc.

## Web Server & Mobile App

The project includes a **FastAPI REST backend** and a **Progressive Web App (PWA)** frontend that can be installed on any device (desktop, Android, iOS).

### Start the Server

```bash
python app/server.py
```

The server starts at `http://localhost:8000`. Open it in any browser.

### Install on Mobile (Android/iOS)

1. Open `http://<your-computer-ip>:8000` in Chrome/Safari
2. Tap the browser menu → **"Add to Home Screen"** or **"Install App"**
3. The app installs like a native app with its own icon

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Server health check |
| GET | `/api/agents` | List all specialist agents |
| POST | `/api/chat` | Chat with AI |
| POST | `/api/plan` | Create execution plan |
| POST | `/api/execute` | Execute goal with agents |
| GET | `/api/memory` | Get all memories |
| POST | `/api/memory` | Add a memory |
| DELETE | `/api/memory/{key}` | Delete a memory |
| POST | `/api/graph/node` | Add work graph node |
| POST | `/api/graph/relation` | Add work graph relation |
| POST | `/api/graph/query` | Query the work graph |

### Run Tests

```bash
pytest tests/ -v
```

All **39 tests** cover agents, AI manager, work graph, memory, permissions, verification, and LLM client.