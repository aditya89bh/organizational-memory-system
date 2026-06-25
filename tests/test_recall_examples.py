"""Smoke tests for the recall examples."""

import importlib.util
from pathlib import Path
from typing import Any

import pytest

_EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples" / "recall"
_EXAMPLES = [
    "keyword_search_example.py",
    "decision_recall_example.py",
    "open_loop_recall_example.py",
    "natural_language_recall_example.py",
]


def _load(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(
        f"recall_example_{name}", _EXAMPLES_DIR / name
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
