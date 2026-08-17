---
name: new-specialist-agent
description: Create a new specialist agent for the AI Work OS (src/agents/). Use when the user asks to "add an agent", "create a new agent type", or wants a new specialist worker (e.g. Finance Agent, HR Agent, Marketing Agent, Sales Agent) added to the system.
---

# New Specialist Agent

This project (AI Work OS) coordinates specialist agents through `AIManager`. Every
specialist agent lives in `src/agents/specialist_agents.py` and inherits from
`BaseAgent` (`src/agents/base_agent.py`). Follow this exact process when adding one.

## 1. Confirm the agent's purpose

Ask (if not already clear from the request):
- What is the agent's name (e.g. "Finance", "HR", "Marketing")?
- What capabilities should it expose (short snake_case strings, e.g. `budget_analysis`)?
- One-sentence description matching the style already used (see VISION.md's
  "Specialist AI Workers" section for tone, e.g. "Analyses datasets, trends and
  business information.").

## 2. Add the class to `src/agents/specialist_agents.py`

Follow the exact shape of existing agents (`ResearchAgent`, `AnalystAgent`,
`WriterAgent`, `DeveloperAgent`, `ExecutiveAssistantAgent`) in that file:

```python
class FinanceAgent(BaseAgent):
    """
    Specialist agent for finance tasks.

    Capabilities:
    - Budget analysis
    - Financial forecasting
    """

    def __init__(self):
        super().__init__(
            name="Finance",
            description="Analyses budgets, forecasts and financial information",
        )
        self.capabilities = [
            "budget_analysis",
            "financial_forecasting",
        ]

    def execute(self, task: str, context: Optional[dict] = None) -> dict:
        """Execute a finance task."""
        return {
            "agent": "finance",
            "task": task,
            "status": "pending",
            "output": None,
            "note": "Finance agent ready - full capabilities coming soon",
        }
```

Rules to follow (match existing conventions exactly):
- Class name is `PascalCase` + `Agent` suffix.
- `name=` passed to `super().__init__` is a short display name (Title Case, no
  "Agent" suffix), e.g. `"Finance"` not `"Finance Agent"`.
- `description=` is one sentence, present tense, third person ("Analyses...",
  "Creates...", "Manages...").
- `capabilities` is a `list[str]` of snake_case capability names.
- `execute()` currently returns a placeholder dict (this project has not yet
  wired up real AI model calls). Match the existing placeholder shape:
  `{"agent": "<snake_case_agent_key>", "task": task, "status": "pending", ...,
  "note": "<Name> agent ready - ... coming soon"}`.
- Do not add real AI/API calls unless explicitly asked — the codebase intentionally
  stubs `execute()` for now (see `note` fields in every existing agent).

## 3. Register the agent in `main.py`

In `AIWorkOS._register_agents()` in `main.py`, add one line following the existing
pattern (key is snake_case, matching the `"agent"` value used in step 2):

```python
self.manager.register_agent("finance", FinanceAgent())
```

Also add the import at the top of `main.py` alongside the other specialist agent
imports:

```python
from src.agents.specialist_agents import (
    ResearchAgent,
    AnalystAgent,
    WriterAgent,
    DeveloperAgent,
    ExecutiveAssistantAgent,
    FinanceAgent,
)
```

## 4. Add a test to `tests/test_core.py`

Add a test method inside the existing `TestSpecialistAgents` class, matching the
style of `test_research_agent` / `test_writer_agent`:

```python
    def test_finance_agent(self):
        agent = FinanceAgent()
        assert agent.name == "Finance"
        result = agent.execute("Analyze Q3 budget")
        assert result["agent"] == "finance"
```

Also add `FinanceAgent` to the import line at the top of `tests/test_core.py`:
`from src.agents.specialist_agents import ResearchAgent, WriterAgent, FinanceAgent`.

## 5. Verify

Run the project's test suite (see the `run-project-tests` skill) and confirm the
new test passes along with all existing tests.
