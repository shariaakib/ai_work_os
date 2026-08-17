"""
Pytest fixtures for the whole test suite.

The problem this solves: WorkGraph and WorkMemory save to real files
(data/work_graph.json, data/memory.json) on every operation. If tests
share that file, one test's data leaks into another (we saw this in
TestWorkGraph.test_add_relation: `assert 2 == 1`).

The fix: an "autouse" fixture that redirects BOTH storage paths to a
fresh temporary directory before every test, then cleans up after.
That makes every test fully isolated — the professional way.
"""

import pytest


@pytest.fixture(autouse=True)
def isolated_data_dir(tmp_path, monkeypatch):
    """Give WorkGraph/WorkMemory a throwaway storage path per test."""
    monkeypatch.setattr("src.core.work_graph.WorkGraph.default_db_path", tmp_path / "work_graph.json")
    monkeypatch.setattr("src.core.memory.WorkMemory.default_db_path", tmp_path / "memory.json")
    yield
