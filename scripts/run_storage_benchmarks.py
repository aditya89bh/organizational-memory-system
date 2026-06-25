"""Lightweight throughput benchmarks for the storage layer.

Times the core operations (save, get, list, query) for the JSON and SQLite
stores across a configurable number of records. The script is dependency-free
and deterministic in structure so it can run in CI as a smoke check.
"""

from __future__ import annotations

import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from organizational_memory.models import Decision
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.storage.query import Query
from organizational_memory.storage.sqlite_store import SQLiteStore
from organizational_memory.storage.store import MemoryStore

DEFAULT_COUNT = 500


@dataclass(frozen=True)
class StoreResult:
    """Timings (in seconds) for one store across the benchmark operations."""

    name: str
    count: int
    save: float
    get: float
    list_all: float
    query: float


def _make_records(count: int) -> list[Decision]:
    return [
        Decision(
            id=f"d{i}",
            title=f"Decision {i}",
            description="benchmark record",
            owner_id="alice" if i % 2 == 0 else "bob",
        )
        for i in range(count)
    ]


def benchmark_store(store: MemoryStore, name: str, count: int) -> StoreResult:
    """Run the benchmark operations against ``store`` and return timings."""
    records = _make_records(count)

    start = time.perf_counter()
    for record in records:
        store.save_record(record)
    save = time.perf_counter() - start

    start = time.perf_counter()
    for record in records:
        store.get_record("Decision", record.id)
    get = time.perf_counter() - start

    start = time.perf_counter()
    store.list_records("Decision")
    list_all = time.perf_counter() - start

    start = time.perf_counter()
    store.query(Query(owner_id="alice"))
    query = time.perf_counter() - start

    return StoreResult(
        name=name,
        count=count,
        save=save,
        get=get,
        list_all=list_all,
        query=query,
    )


def run_benchmarks(count: int = DEFAULT_COUNT) -> list[StoreResult]:
    """Benchmark every concrete store and return their results."""
    results: list[StoreResult] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        results.append(
            benchmark_store(JSONStore(root / "bench.json"), "json", count)
        )
        results.append(
            benchmark_store(SQLiteStore(root / "bench.db"), "sqlite", count)
        )
    return results


def format_report(results: list[StoreResult]) -> str:
    """Render a human-readable table of benchmark timings."""
    lines = ["Storage benchmarks", "=================="]
    for result in results:
        lines.append(
            f"{result.name:<7} n={result.count} "
            f"save={result.save:.4f}s get={result.get:.4f}s "
            f"list={result.list_all:.4f}s query={result.query:.4f}s"
        )
    return "\n".join(lines)


def main(count: int = DEFAULT_COUNT) -> int:
    """Run the benchmarks and print a report. Returns a process exit code."""
    results = run_benchmarks(count)
    print(format_report(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
