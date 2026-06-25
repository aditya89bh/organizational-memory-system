"""Tests for the memory benchmark helpers."""

import importlib.util
import sys
from pathlib import Path
from typing import Any

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_memory_benchmarks.py"


def _load() -> Any:
    spec = importlib.util.spec_from_file_location("mem_bench", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


mb = _load()


def test_generate_records_count() -> None:
    records = mb.generate_synthetic_records(10)
    assert len(records) == 10
    assert records[0].id == "decision-0"
    assert records[1].id == "task-1"


def test_generate_records_deterministic() -> None:
    first = mb.generate_synthetic_records(5)
    second = mb.generate_synthetic_records(5)
    assert [r.id for r in first] == [r.id for r in second]


def test_estimate_json_size_positive() -> None:
    records = mb.generate_synthetic_records(4)
    size = mb.estimate_json_size(records)
    assert size > 0
    assert mb.estimate_json_size(records) == size


def test_store_operation_counts() -> None:
    records = mb.generate_synthetic_records(6)
    json_ops = mb.store_operation_counts(records, "json")
    sqlite_ops = mb.store_operation_counts(records, "sqlite")
    assert json_ops["saved"] == 6
    assert json_ops["listed"] == 6
    assert json_ops == sqlite_ops


def test_run_consistency() -> None:
    result = mb.run(8)
    assert result.record_count == 8
    assert result.backends_consistent


def test_format_report() -> None:
    text = mb.format_report(mb.run(4))
    assert "Memory benchmarks" in text
    assert "estimated_json_bytes" in text


def test_main() -> None:
    assert mb.main(["4"]) == 0
