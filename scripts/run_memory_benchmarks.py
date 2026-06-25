"""Deterministic memory/storage benchmarks.

Generates synthetic records and reports their count, an estimated JSON payload
size, and the number of store operations performed against both the JSON and
SQLite backends. It deliberately avoids fragile process-memory assertions;
payload size is estimated from the serialized records, which is stable across
machines.

Usage::

    python scripts/run_memory_benchmarks.py 500
"""

from __future__ import annotations

import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from organizational_memory.models import Decision, Task
from organizational_memory.models.enums import DecisionStatus, TaskStatus
from organizational_memory.schemas.base import BaseRecord
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.storage.sqlite_store import SQLiteStore
from organizational_memory.utils.time import parse_timestamp

DEFAULT_COUNT = 200
_BASE_TIME = parse_timestamp("2026-01-01T00:00:00Z")
_OWNERS = ("alice", "bob", "carol", "dave")


def generate_synthetic_records(count: int) -> list[BaseRecord]:
    """Return ``count`` deterministic synthetic records."""
    records: list[BaseRecord] = []
    for index in range(count):
        owner = _OWNERS[index % len(_OWNERS)]
        if index % 2 == 0:
            records.append(
                Decision(
                    id=f"decision-{index}",
                    title=f"Decision {index}",
                    description=f"Synthetic decision number {index}.",
                    owner_id=owner,
                    status=DecisionStatus.ACCEPTED,
                    created_at=_BASE_TIME,
                    updated_at=_BASE_TIME,
                )
            )
        else:
            records.append(
                Task(
                    id=f"task-{index}",
                    title=f"Task {index}",
                    description=f"Synthetic task number {index}.",
                    owner_id=owner,
                    status=TaskStatus.TODO,
                    created_at=_BASE_TIME,
                    updated_at=_BASE_TIME,
                )
            )
    return records


def estimate_json_size(records: list[BaseRecord]) -> int:
    """Return the total serialized JSON size (bytes) of ``records``."""
    total = 0
    for record in records:
        payload = json.dumps(record.to_dict(), sort_keys=True)
        total += len(payload.encode("utf-8"))
    return total


def store_operation_counts(records: list[BaseRecord], backend: str) -> dict[str, int]:
    """Persist ``records`` to ``backend`` and return operation counts."""
    with tempfile.TemporaryDirectory() as tmp:
        if backend == "sqlite":
            store: JSONStore | SQLiteStore = SQLiteStore(str(Path(tmp) / "memory.db"))
        else:
            store = JSONStore(Path(tmp) / "memory.json")
        saved = 0
        for record in records:
            store.save_record(record)
            saved += 1
        listed = len(store.list_records())
    return {"saved": saved, "listed": listed, "total": saved + listed}


@dataclass(frozen=True)
class MemoryBenchmarkResult:
    """Aggregate results of a memory/storage benchmark run."""

    record_count: int
    json_bytes: int
    json_store_ops: dict[str, int]
    sqlite_store_ops: dict[str, int]

    @property
    def backends_consistent(self) -> bool:
        """Whether both backends performed the same logical operation counts."""
        return self.json_store_ops == self.sqlite_store_ops


def run(count: int = DEFAULT_COUNT) -> MemoryBenchmarkResult:
    """Run the memory benchmark for ``count`` synthetic records."""
    records = generate_synthetic_records(count)
    return MemoryBenchmarkResult(
        record_count=len(records),
        json_bytes=estimate_json_size(records),
        json_store_ops=store_operation_counts(records, "json"),
        sqlite_store_ops=store_operation_counts(records, "sqlite"),
    )


def format_report(result: MemoryBenchmarkResult) -> str:
    """Build a human-readable memory benchmark report."""
    return "\n".join(
        [
            "Memory benchmarks",
            "",
            f"  records: {result.record_count}",
            f"  estimated_json_bytes: {result.json_bytes}",
            f"  json_store_ops: {result.json_store_ops}",
            f"  sqlite_store_ops: {result.sqlite_store_ops}",
            f"  backends_consistent: {result.backends_consistent}",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    """Run the memory benchmark and print a report."""
    count = DEFAULT_COUNT
    if argv:
        count = int(argv[0])
    print(format_report(run(count)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
