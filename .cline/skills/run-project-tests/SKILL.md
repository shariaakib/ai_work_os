---
name: run-project-tests
description: Run or add tests for the AI Work OS Python project using its pytest test suite and .venv virtual environment. Use when the user asks to "run the tests", "check tests pass", "add a test", or after making code changes that should be verified.
---

# Run Project Tests

This project uses `pytest` (plus `pytest-asyncio`) inside a local `.venv` virtual
environment on Windows. The workspace is a PowerShell environment, so use
PowerShell-compatible commands (not `&&` chaining).

## 1. Running the full test suite

From the project root (`sakif practuice/`), use the venv's `pytest.exe` directly —
this avoids needing to activate the venv first:

```powershell
.venv\Scripts\pytest.exe -v
```

Equivalent alternative (module form, useful if `pytest.exe` is missing but the
interpreter exists):

```powershell
.venv\Scripts\python.exe -m pytest -v
```

If the venv doesn't exist yet, set it up per `README.md`:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. Running a single test file / class / test

```powershell
.venv\Scripts\pytest.exe tests\test_core.py -v
.venv\Scripts\pytest.exe tests\test_core.py::TestAIManager -v
.venv\Scripts\pytest.exe tests\test_core.py::TestAIManager::test_create_plan -v
```

## 3. Test conventions used in this project

All tests currently live in `tests/test_core.py`. When adding new tests, match
these conventions:

- No `conftest.py` or fixtures yet — each test file manually inserts `src/` onto
  `sys.path` at the top:
  ```python
  import sys
  from pathlib import Path
  sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
  ```
- Tests are grouped into plain classes per component, named `Test<ComponentName>`
  (e.g. `TestAIManager`, `TestWorkGraph`, `TestWorkMemory`, `TestPermissionManager`,
  `TestVerifier`, `TestSpecialistAgents`). No `pytest` fixtures or `setUp` methods
  are used — each test method constructs what it needs directly.
- Test methods are named `test_<behavior>` and use plain `assert` statements (no
  `unittest.TestCase`, no custom assertion helpers).
- Imports at the top of the test file import directly from `src.<package>.<module>`
  (e.g. `from src.core.ai_manager import AIManager, Plan, Task, GoalStatus`).

## 4. Interpreting results

- All tests passing: safe to consider the change verified.
- If `WorkMemory` or `WorkGraph` tests fail unexpectedly, check for leftover state
  in `data/memory.json` / `data/work_graph.json` on disk — these classes persist to
  disk by default (`db_path` defaults to `data/memory.json` and
  `data/work_graph.json`), so tests can leak state across runs since no fixture
  resets/mocks the path. If this causes flaky failures, recommend adding a
  pytest fixture with `tmp_path` to isolate storage — but don't do this
  unprompted, just flag it.
