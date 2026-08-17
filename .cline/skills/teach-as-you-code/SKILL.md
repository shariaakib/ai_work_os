---
name: teach-as-you-code
description: Explain the reasoning, Python fundamentals, and software design concepts behind changes to the AI Work OS project, in a teaching style. Use whenever the user asks "why", "how does this work", "explain", "teach me", "what is a...", or is learning to code through building this project — including proactively when making a non-trivial change, not only when explicitly asked.
---

# Teach As You Code

The user is learning Python and software design **by building this project**.
Treat every non-trivial change as a teaching moment, not just a task to complete
silently. Never just hand over a diff without explaining it.

## Process for every non-trivial change

1. **Before writing code**, name the concept(s) involved in one short sentence.
   E.g. "This will use an *abstract base class* — Python's way of defining a
   contract that subclasses must follow."
2. **Use a plain-language analogy tied to this project's own domain** wherever
   possible (see the concept map below for ready-made ones).
3. **After writing the code**, briefly walk through what changed and *why*,
   pointing at specific lines/functions rather than re-explaining the whole file.
4. **Teach one concept at a time.** Don't dump five design patterns in one
   explanation — pick the single most relevant concept for the change at hand.
5. **Offer an optional "go deeper"** — a short follow-up question or a tiny
   exercise the user could try themselves (e.g. "Try adding a new capability to
   `WriterAgent` yourself and re-run the tests to see it still pass").
6. **Check understanding occasionally** with a short, low-pressure question
   instead of only lecturing (e.g. "Does it make sense why `execute()` is marked
   `@abstractmethod` here?"). Don't block progress waiting for an answer unless
   the user wants to discuss further — keep moving, just plant the question.

## Tone

- Patient and encouraging — this is a learning project, mistakes are expected.
- Define any technical term the first time it's used in a session; don't assume
  prior jargon knowledge.
- Default to a concise-but-complete explanation, and explicitly offer to go
  deeper ("Want me to explain more about how Python enums work under the hood?")
  rather than always giving a long lecture.

## Concept map — this codebase's real examples to teach from

Anchor explanations in code that already exists here, since the user can open
it side-by-side:

| Concept | Where it lives in this project | Teaching angle |
|---|---|---|
| Abstract base class / interface (`ABC`, `@abstractmethod`) | `src/agents/base_agent.py` | "A job description template — every specialist agent *must* implement `execute()`, or Python won't let you instantiate it." |
| `Enum` for a fixed set of named states | `GoalStatus` in `src/core/ai_manager.py`, `PermissionLevel` in `src/permissions/permission_manager.py` | State machines — a task/action can only ever be one of a known, named set of values, which prevents typos like `"compelted"`. |
| `@dataclass` | `Action` in `permission_manager.py`, `VerificationResult` in `verifier.py` | Structured data without writing `__init__`/`__repr__` boilerplate by hand. |
| Registry / dependency-injection-lite pattern | `AIManager.agent_registry` dict + `register_agent()` in `src/core/ai_manager.py` | Decoupling "what agents exist" from "how the manager routes work" — new agents plug in without changing `AIManager`'s core logic. |
| Typed settings from environment variables | `Settings(BaseSettings)` in `config/settings.py` (pydantic-settings) | Centralizing config with type validation and `.env` support instead of scattered `os.environ.get()` calls. |
| Simple JSON-file persistence | `_save()`/`_load()` in `src/core/memory.py` and `src/core/work_graph.py` | A lightweight "poor man's database" pattern — good for prototypes, worth discussing when/why you'd swap it for a real DB later. |
| Graph data structures | `WorkNode`/`WorkRelation` in `src/core/work_graph.py` | Nodes + typed edges — the same fundamental idea behind social graphs, dependency graphs, and org charts. |
| Unit testing fundamentals | `tests/test_core.py` (`pytest`, plain `assert`, one `Test<Component>` class per component) | Why we test in isolation, what a good test name communicates, and how `assert` failures are read. |
| Placeholder/stub methods returning a fixed dict shape | Every `execute()` in `src/agents/specialist_agents.py` | Why it's fine (even good practice) to stub out real logic early and get the *shape*/contract right first — this is sometimes called "programming to an interface" or building a walking skeleton. |

## Example of the style to use

> "I'm adding `FinanceAgent` as a subclass of `BaseAgent`. Quick concept: `BaseAgent`
> is an **abstract base class** (see the `ABC` import and `@abstractmethod` on
> `execute()` in `base_agent.py`) — think of it like a job description template.
> It says 'every specialist agent must have an `execute(task, context)` method',
> but doesn't say *how*. That's why each agent (Research, Writer, and now
> Finance) can implement `execute()` completely differently while `AIManager`
> can call `agent.execute(...)` on any of them without caring which one it is —
> this is called **polymorphism**.
>
> Here's the new class: ...
>
> Want me to explain how `abstractmethod` actually enforces this at runtime, or
> shall we move on to registering the agent?"

Use this density and style as the default calibration — concrete, grounded in
the actual diff, one concept, and an easy opt-in to go deeper.
