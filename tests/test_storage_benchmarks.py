"""Tests for the storage benchmark helpers."""

import importlib.util
import sys
from pathlib import Path
from typing import Any

_SCRIPT = (
    Path(__file__).resolve().parents[1] / "scripts" / "run_storage_benchmarks.py"
)


def _load_module() -> Any:
    spec = importlib.util.spec_from_file_location("storage_benchmarks", _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


bench = _load_module()


def test_run_benchmarks_covers_both_stores() -> None:
    results = bench.run_benchmarks(count=25)
    names = {result.name for result in results}
    assert names == {"json", "sqlite"}
    for result in results:
        assert result.count == 25
        assert result.save >= 0.0
        assert result.get >= 0.0


def test_format_report_contains_stores() -> None:
    results = bench.run_benchmarks(count=10)
    report = bench.format_report(results)
    assert "Storage benchmarks" in report
    assert "json" in report
    assert "sqlite" in report


def test_main_returns_zero() -> None:
    assert bench.main(count=10) == 0
