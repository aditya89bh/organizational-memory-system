"""Smoke tests for the runnable tutorial scripts."""

import importlib.util
from pathlib import Path
from typing import Any

import pytest

_TUTORIALS_DIR = Path(__file__).resolve().parents[1] / "examples" / "tutorials"
_TUTORIALS = [
    "tutorial_01_ingest_and_extract.py",
    "tutorial_02_persist_and_recall.py",
    "tutorial_03_analytics_and_reports.py",
    "tutorial_04_full_workflow.py",
]


def _load(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(
        f"tutorial_{name}", _TUTORIALS_DIR / name
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("name", _TUTORIALS)
def test_tutorial_runs(name: str, capsys: pytest.CaptureFixture[str]) -> None:
    module = _load(name)
    assert module.main() == 0
    assert capsys.readouterr().out.strip() != ""
