---
name: add-tool-integration
description: Add a new tool integration under src/tools/ for the AI Work OS (e.g. connecting to Gmail, Calendar, Slack, Drive, CRM, or another external API/service). Use when the user asks to "add a tool", "integrate an API", or "connect a new service" to the AI Work OS.
---

# Add Tool Integration

Tools live in `src/tools/` and give agents the ability to interact with the outside
world (web pages, documents, external APIs). This project currently has
`WebTool`, `DocumentTool`, and `APITool` in `src/tools/web_tool.py`. Follow their
exact pattern when adding a new tool.

## 1. Decide the shape of the tool

- **Simple, single-purpose tool** (like `WebTool`, `DocumentTool`): a standalone
  class in `src/tools/` with focused methods.
- **Service-integration tool** (like `APITool`, used for Gmail/Calendar/Drive/CRM
  style connections): extend the existing `APITool.connect_service()` /
  `APITool.call()` pattern rather than creating a parallel mechanism, unless the
  user explicitly wants a dedicated class.

## 2. Placeholder-first convention

This codebase intentionally stubs out real external calls until API keys/creds are
wired up (see `note` fields like `"gmail integration coming soon"` in
`APITool.call()`). When adding a new integration:

- If real credentials/SDKs are not yet configured in `config/settings.py`, add the
  method but return a placeholder dict with a `"note"` field, matching:
  ```python
  return {
      "service": service,
      "action": action,
      "status": "pending",
      "note": f"{service} integration coming soon",
  }
  ```
- If the user explicitly asks for a **working** integration and provides
  credentials/config, implement it for real using `httpx` (already a dependency)
  and add any new secrets to `config/settings.py` as `Optional[str] = None`
  fields, following the existing `openrouter_api_key` pattern.

## 3. Example: adding a new standalone tool

```python
class CalendarTool:
    """
    Tool for reading and managing calendar events.
    """

    def __init__(self):
        self.client = httpx.Client(timeout=30.0)

    def list_events(self, date: str) -> list[dict]:
        """List calendar events for a given date (placeholder)."""
        return [
            {
                "title": "Calendar integration coming soon",
                "date": date,
            }
        ]
```

Add this class to `src/tools/web_tool.py` (or a new file `src/tools/calendar_tool.py`
if it's unrelated to web/document/API concerns — prefer a new file per tool family
for anything beyond a few methods, and export it from `src/tools/__init__.py` if
that file re-exports tools).

## 4. Wire the tool to a permission level

Every action a tool performs that isn't pure "read" should be classified via
`PermissionManager.classify_action()` (`src/permissions/permission_manager.py`).
Check whether the action type already falls into an existing bucket:

- `SAFE`: read, search, analyse/analyze, summarise/summarize, draft, list, get,
  find, check
- `HIGH_RISK`: payment, transfer, delete, remove, terminate, security_change,
  legal_action, irreversible
- `APPROVAL`: everything else (default)

If your new tool introduces an action type that should be safe or high-risk but
isn't already covered, update the lists inside `classify_action()` — do not create
a parallel classification system.

## 5. Add a test

Add tests to `tests/test_core.py` (or a new `tests/test_tools.py` if the project
grows a dedicated tools test module) following the existing class-per-component
style, e.g.:

```python
class TestCalendarTool:
    def test_list_events_placeholder(self):
        tool = CalendarTool()
        events = tool.list_events("2025-01-01")
        assert isinstance(events, list)
```

## 6. Verify

Run the test suite (see the `run-project-tests` skill) to confirm nothing is
broken.
