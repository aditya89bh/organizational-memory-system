"""Tests for the stress-test scenario helpers."""

import importlib.util
import sys
from pathlib import Path
from typing import Any

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_stress_tests.py"


def _load() -> Any:
    spec = importlib.util.spec_from_file_location("stress_tests", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


st = _load()


def test_empty_transcript_scenario() -> None:
    result = st.scenario_empty_transcript()
    assert result.passed
    assert "EmptyTranscriptError" in result.detail


def test_very_long_lines_scenario() -> None:
    assert st.scenario_very_long_lines().passed


def test_duplicate_records_scenario() -> None:
    result = st.scenario_duplicate_records()
    assert result.passed
    assert "count=101" in result.detail


def test_many_owners_scenario() -> None:
    assert st.scenario_many_owners().passed


def test_many_open_loops_scenario() -> None:
    assert st.scenario_many_open_loops().passed


def test_many_report_sections_scenario() -> None:
    assert st.scenario_many_report_sections().passed


def test_pagination_extremes_scenario() -> None:
    assert st.scenario_pagination_extremes().passed


def test_run_all_pass() -> None:
    results = st.run_all()
    assert all(result.passed for result in results)
    assert len(results) == 7


def test_main() -> None:
    assert st.main() == 0


def test_format_report() -> None:
    text = st.format_report(st.run_all())
    assert "Stress tests" in text
    assert "PASS" in text
