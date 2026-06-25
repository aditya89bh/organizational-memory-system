"""Lightweight, deterministic profiling utilities.

A :class:`Profiler` collects :class:`TimingRecord` entries — either via the
:meth:`Profiler.timer` context manager or by recording elapsed times directly —
and aggregates them into a JSON-safe :class:`ProfileReport`. The clock is
injectable so behavior is fully deterministic in tests.
"""

import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class TimingRecord:
    """A single timed operation."""

    name: str
    elapsed_seconds: float

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible mapping for this record."""
        return {
            "name": self.name,
            "elapsed_seconds": round(self.elapsed_seconds, 6),
        }


@dataclass(frozen=True)
class ProfileReport:
    """An aggregate, JSON-safe profiling report."""

    records: list[TimingRecord] = field(default_factory=list)
    summary: dict[str, dict[str, float]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible mapping for this report."""
        return {
            "records": [record.to_dict() for record in self.records],
            "summary": self.summary,
        }


class Profiler:
    """Collects timing records and aggregates them deterministically."""

    def __init__(self, clock: Callable[[], float] = time.perf_counter) -> None:
        self._clock = clock
        self.records: list[TimingRecord] = []

    @contextmanager
    def timer(self, name: str) -> Iterator[None]:
        """Time the wrapped block and append a :class:`TimingRecord`."""
        start = self._clock()
        try:
            yield
        finally:
            self.record(name, self._clock() - start)

    def record(self, name: str, elapsed_seconds: float) -> TimingRecord:
        """Append a timing record built from an explicit elapsed time."""
        entry = TimingRecord(name=name, elapsed_seconds=elapsed_seconds)
        self.records.append(entry)
        return entry

    def summary(self) -> dict[str, dict[str, float]]:
        """Return per-operation aggregates, keyed and sorted by name."""
        grouped: dict[str, list[float]] = {}
        for entry in self.records:
            grouped.setdefault(entry.name, []).append(entry.elapsed_seconds)
        summary: dict[str, dict[str, float]] = {}
        for name in sorted(grouped):
            times = grouped[name]
            total = sum(times)
            summary[name] = {
                "count": len(times),
                "total_seconds": round(total, 6),
                "average_seconds": round(total / len(times), 6),
                "min_seconds": round(min(times), 6),
                "max_seconds": round(max(times), 6),
            }
        return summary

    def report(self) -> ProfileReport:
        """Return a :class:`ProfileReport` of all collected records."""
        return ProfileReport(records=list(self.records), summary=self.summary())
