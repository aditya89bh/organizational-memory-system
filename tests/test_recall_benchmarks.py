"""Tests for the recall benchmark helpers."""

import importlib.util
import sys
from pathlib import Path
from typing import Any

_SCRIPT = (
    Path(__file__).resolve().parents[1] / "scripts" / "run_recall_benchmarks.py"
)


def _load_module() -> Any:
    spec = importlib.util.spec_from_file_location("recall_benchmarks", _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


bench = _load_module()


def test_case_result_hit_rate() -> None:
    result = bench.CaseResult(
        name="x", expected_ids=("a", "b"), returned_ids=("a", "z")
    )
    assert result.hit_rate == 0.5


def test_case_result_top_k_hit() -> None:
    result = bench.CaseResult(
        name="x", expected_ids=("a",), returned_ids=("a", "b", "c")
    )
    assert result.top_k_hit is True


def test_run_benchmarks_all_hit() -> None:
    results = bench.run_benchmarks()
    assert len(results) == len(bench.BENCHMARK_CASES)
    assert bench.overall_hit_rate(results) == 1.0


def test_top_k_accuracy_full() -> None:
    results = bench.run_benchmarks()
    assert bench.top_k_accuracy(results) == 1.0


def test_main_returns_zero() -> None:
    assert bench.main() == 0


def test_report_contains_summary() -> None:
    results = bench.run_benchmarks()
    report = bench.format_report(results)
    assert "Recall benchmarks" in report
    assert "Overall hit rate" in report
    assert "Total queries: 6" in report
