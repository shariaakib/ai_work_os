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