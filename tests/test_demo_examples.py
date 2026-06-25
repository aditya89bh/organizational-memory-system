"""Smoke tests for the runnable demo examples."""

import importlib.util
from pathlib import Path
from typing import Any

import pytest

_EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples" / "demos"
_EXAMPLES = [
    "startup_meeting_demo.py",
    "sprint_planning_demo.py",
    "board_meeting_demo.py",
    "organizational_timeline_demo.py",
]


def _load(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(
        f"demo_example_{name}", _EXAMPLES_DIR / name
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("name", _EXAMPLES)
def test_example_runs(name: str, capsys: pytest.CaptureFixture[str]) -> None:
    module = _load(name)
    assert module.main() == 0
    assert capsys.readouterr().out.strip() != ""
