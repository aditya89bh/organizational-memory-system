"""Tests for the extraction benchmark helpers."""

import importlib.util
import sys
from pathlib import Path
from typing import Any

_SCRIPT = (
    Path(__file__).resolve().parents[1] / "scripts" / "run_extraction_benchmarks.py"
)


def _load_module() -> Any:
    spec = importlib.util.spec_from_file_location("benchmarks", _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


bench = _load_module()


def test_category_accuracy_all_match() -> None:
    results = [
        bench.CaseResult(
            filename="a",
            expected=dict.fromkeys(bench.CATEGORIES, 1),
            actual=dict.fromkeys(bench.CATEGORIES, 1),
        )
    ]
    assert bench.category_accuracy(results) == 1.0


def test_category_accuracy_partial() -> None:
    expected = dict.fromkeys(bench.CATEGORIES, 1)
    actual = dict(expected)
    actual["decisions"] = 99
    results = [bench.CaseResult(filename="a", expected=expected, actual=actual)]
    accuracy = bench.category_accuracy(results)
    assert accuracy == (len(bench.CATEGORIES) - 1) / len(bench.CATEGORIES)


def test_category_accuracy_empty() -> None:
    assert bench.category_accuracy([]) == 0.0


def test_case_result_matched_count() -> None:
    expected = dict.fromkeys(bench.CATEGORIES, 0)
    actual = dict(expected)
    actual["risks"] = 5
    result = bench.CaseResult(filename="a", expected=expected, actual=actual)
    assert result.matched == len(bench.CATEGORIES) - 1


def test_run_real_benchmark_passes() -> None:
    results = [bench.run_case(case) for case in bench.BENCHMARK_CASES]
    assert bench.category_accuracy(results) >= bench.PASS_THRESHOLD
    assert bench.main() == 0


def test_format_report_contains_summary() -> None:
    results = [bench.run_case(case) for case in bench.BENCHMARK_CASES]
    report = bench.format_report(results)
    assert "Category accuracy" in report
    assert "Total files: 3" in report
