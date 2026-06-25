"""Tests for profiling utilities."""

import json
from collections.abc import Callable

from organizational_memory.performance.profiling import Profiler, TimingRecord


def _fake_clock(values: list[float]) -> Callable[[], float]:
    iterator = iter(values)
    return lambda: next(iterator)


def test_timer_records_elapsed() -> None:
    profiler = Profiler(clock=_fake_clock([0.0, 1.5]))
    with profiler.timer("extract"):
        pass
    assert len(profiler.records) == 1
    assert profiler.records[0].name == "extract"
    assert profiler.records[0].elapsed_seconds == 1.5


def test_record_direct() -> None:
    profiler = Profiler()
    record = profiler.record("op", 0.25)
    assert isinstance(record, TimingRecord)
    assert profiler.records == [record]


def test_summary_aggregates() -> None:
    profiler = Profiler()
    profiler.record("a", 1.0)
    profiler.record("a", 3.0)
    profiler.record("b", 2.0)
    summary = profiler.summary()
    assert summary["a"]["count"] == 2
    assert summary["a"]["total_seconds"] == 4.0
    assert summary["a"]["average_seconds"] == 2.0
    assert summary["a"]["min_seconds"] == 1.0
    assert summary["a"]["max_seconds"] == 3.0
    assert list(summary) == ["a", "b"]


def test_report_is_json_safe() -> None:
    profiler = Profiler()
    profiler.record("a", 0.5)
    report = profiler.report()
    data = report.to_dict()
    json.dumps(data)
    assert data["records"][0]["name"] == "a"
    assert data["summary"]["a"]["count"] == 1


def test_timer_records_on_exception() -> None:
    profiler = Profiler(clock=_fake_clock([0.0, 2.0]))
    try:
        with profiler.timer("boom"):
            raise ValueError("x")
    except ValueError:
        pass
    assert profiler.records[0].elapsed_seconds == 2.0
