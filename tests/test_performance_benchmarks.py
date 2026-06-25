"""Tests for the performance benchmark helpers."""

import importlib.util
import sys
from pathlib import Path
from typing import Any

_SCRIPT = (
    Path(__file__).resolve().parents[1] / "scripts" / "run_performance_benchmarks.py"
)


def _load() -> Any:
    spec = importlib.util.spec_from_file_location("perf_bench", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


pb = _load()


def test_ops_per_second() -> None:
    result = pb.BenchmarkResult(name="x", operations=100, elapsed_seconds=2.0)
    assert result.ops_per_second == 50.0


def test_ops_per_second_zero_time() -> None:
    result = pb.BenchmarkResult(name="x", operations=100, elapsed_seconds=0.0)
    assert result.ops_per_second == 0.0


def test_run_timed_counts() -> None:
    calls = {"n": 0}

    def work() -> None:
        calls["n"] += 1

    result = pb.run_timed("demo", 5, work)
    assert calls["n"] == 1
    assert result.operations == 5
    assert result.elapsed_seconds >= 0.0


def test_format_report() -> None:
    results = [
        pb.BenchmarkResult(name="extraction", operations=10, elapsed_seconds=1.0)
    ]
    text = pb.format_report(results)
    assert "Performance benchmarks" in text
    assert "extraction" in text


def test_run_all_smoke() -> None:
    results = pb.run_all(iterations=2)
    names = {result.name for result in results}
    assert {"extraction", "recall", "analytics", "reporting", "cli_parser"} <= names


def test_main_runs() -> None:
    assert pb.main(["2"]) == 0
