"""Tests for the report benchmark helpers."""

import importlib.util
import sys
from pathlib import Path
from typing import Any

_SCRIPT = (
    Path(__file__).resolve().parents[1] / "scripts" / "run_report_benchmarks.py"
)


def _load_module() -> Any:
    spec = importlib.util.spec_from_file_location("report_benchmarks", _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


bench = _load_module()


def test_run_benchmarks_covers_all_cases() -> None:
    results = bench.run_benchmarks()
    assert len(results) == len(bench.REPORT_CASES)


def test_all_reports_pass() -> None:
    results = bench.run_benchmarks()
    assert bench.all_passed(results) is True


def test_export_sizes_positive() -> None:
    results = bench.run_benchmarks()
    for result in results:
        assert result.markdown_size > 0
        assert result.json_size > 0


def test_total_sections_positive() -> None:
    results = bench.run_benchmarks()
    assert bench.total_sections(results) > 0


def test_missing_sections_detected() -> None:
    metrics = bench.ReportMetrics(
        name="x",
        section_count=1,
        markdown_size=1,
        json_size=1,
        csv_size=1,
        missing_sections=("A",),
    )
    assert metrics.passed is False


def test_main_returns_zero() -> None:
    assert bench.main() == 0


def test_report_contains_summary() -> None:
    results = bench.run_benchmarks()
    report = bench.format_report(results)
    assert "Report benchmarks" in report
    assert "Total sections:" in report
    assert "Pass: True" in report


def test_deterministic() -> None:
    first = bench.format_report(bench.run_benchmarks())
    second = bench.format_report(bench.run_benchmarks())
    assert first == second
