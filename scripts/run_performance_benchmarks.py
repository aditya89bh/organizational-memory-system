"""Deterministic performance benchmarks for core operations.

Times representative operations (extraction, persistence, recall, analytics,
reporting, and CLI parser construction) over small, fixed workloads and reports
operation counts and elapsed time. It intentionally avoids hard timing
thresholds, which are fragile across machines; the numbers are informational.

Usage::

    python scripts/run_performance_benchmarks.py
"""

from __future__ import annotations

import sys
import tempfile
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from organizational_memory.analytics.reporting import generate_report
from organizational_memory.cli.main import build_parser
from organizational_memory.demos import board, sprint, startup
from organizational_memory.demos.common import (
    REFERENCE_NOW,
    InMemoryStore,
    ingest_meeting,
)
from organizational_memory.extraction.pipeline import run_extraction
from organizational_memory.recall.keyword_search import search_keywords
from organizational_memory.reports.organizational_memory_report import (
    organizational_memory_report,
)
from organizational_memory.storage.json_store import JSONStore

DEFAULT_ITERATIONS = 25


@dataclass(frozen=True)
class BenchmarkResult:
    """The timing outcome of a single benchmark."""

    name: str
    operations: int
    elapsed_seconds: float

    @property
    def ops_per_second(self) -> float:
        """Operations per second, or ``0.0`` when no time elapsed."""
        if self.elapsed_seconds <= 0.0:
            return 0.0
        return round(self.operations / self.elapsed_seconds, 2)


def run_timed(name: str, operations: int, func: Callable[[], None]) -> BenchmarkResult:
    """Run ``func`` once, timing it, and return a :class:`BenchmarkResult`."""
    start = time.perf_counter()
    func()
    elapsed = time.perf_counter() - start
    return BenchmarkResult(name=name, operations=operations, elapsed_seconds=elapsed)


def format_report(results: list[BenchmarkResult]) -> str:
    """Build a human-readable benchmark report."""
    lines = ["Performance benchmarks", ""]
    for result in results:
        lines.append(
            f"  {result.name:<14} ops={result.operations:<6} "
            f"elapsed={result.elapsed_seconds:.4f}s "
            f"ops/s={result.ops_per_second}"
        )
    return "\n".join(lines)


def _build_store() -> InMemoryStore:
    store = InMemoryStore()
    ingest_meeting(store, startup.TRANSCRIPT, meeting_id="startup", title="Startup")
    ingest_meeting(store, sprint.TRANSCRIPT, meeting_id="sprint", title="Sprint")
    ingest_meeting(store, board.TRANSCRIPT, meeting_id="board", title="Board")
    return store


def benchmark_extraction(iterations: int) -> BenchmarkResult:
    def run() -> None:
        for _ in range(iterations):
            run_extraction(startup.TRANSCRIPT)

    return run_timed("extraction", iterations, run)


def benchmark_persistence(iterations: int) -> BenchmarkResult:
    store_records = _build_store().list_records()

    def run() -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = JSONStore(Path(tmp) / "memory.json")
            for record in store_records:
                store.save_record(record)

    return run_timed("persistence", len(store_records), run)


def benchmark_recall(iterations: int) -> BenchmarkResult:
    records = _build_store().list_records()

    def run() -> None:
        for _ in range(iterations):
            search_keywords(records, "launch")

    return run_timed("recall", iterations, run)


def benchmark_analytics(iterations: int) -> BenchmarkResult:
    store = _build_store()

    def run() -> None:
        for _ in range(iterations):
            generate_report(store, now=REFERENCE_NOW)

    return run_timed("analytics", iterations, run)


def benchmark_reporting(iterations: int) -> BenchmarkResult:
    store = _build_store()

    def run() -> None:
        for _ in range(iterations):
            organizational_memory_report(store, now=REFERENCE_NOW)

    return run_timed("reporting", iterations, run)


def benchmark_cli(iterations: int) -> BenchmarkResult:
    def run() -> None:
        for _ in range(iterations):
            build_parser()

    return run_timed("cli_parser", iterations, run)


def run_all(iterations: int = DEFAULT_ITERATIONS) -> list[BenchmarkResult]:
    """Run every benchmark and return the results."""
    return [
        benchmark_extraction(iterations),
        benchmark_persistence(iterations),
        benchmark_recall(iterations),
        benchmark_analytics(iterations),
        benchmark_reporting(iterations),
        benchmark_cli(iterations),
    ]


def main(argv: list[str] | None = None) -> int:
    """Run all performance benchmarks and print a report."""
    iterations = DEFAULT_ITERATIONS
    if argv:
        iterations = int(argv[0])
    print(format_report(run_all(iterations)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
