"""Runnable memory health example.

Run it with::

    python examples/analytics/memory_health_example.py

Builds a small mixed memory and prints the deterministic memory health score,
grade, component breakdown, and recommendations. Nothing is left on disk.
"""

import tempfile
from pathlib import Path

from organizational_memory.analytics.memory_health import memory_health
from organizational_memory.models import Commitment, Decision, OpenLoop, Task
from organizational_memory.models.enums import (
    CommitmentStatus,
    DecisionStatus,
    OpenLoopStatus,
    TaskStatus,
)
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import parse_timestamp

NOW = parse_timestamp("2026-03-01T00:00:00Z")


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        store = JSONStore(Path(tmp) / "memory.json")
        store.save_record(
            OpenLoop(
                id="o1",
                question="How to scale auth?",
                status=OpenLoopStatus.OPEN,
                created_at=parse_timestamp("2026-02-02T10:00:00Z"),
            )
        )
        store.save_record(
            Task(
                id="t1",
                title="Write migration",
                description="x",
                owner_id="alice",
                status=TaskStatus.IN_PROGRESS,
                created_at=parse_timestamp("2026-02-10T10:00:00Z"),
                due_at=parse_timestamp("2026-02-20T10:00:00Z"),
            )
        )
        store.save_record(
            Commitment(
                id="c1",
                owner_id="bob",
                description="Get budget",
                status=CommitmentStatus.PENDING,
                created_at=parse_timestamp("2026-02-10T10:00:00Z"),
            )
        )
        store.save_record(
            Decision(
                id="d1",
                title="Old proposal",
                description="x",
                status=DecisionStatus.PROPOSED,
                created_at=parse_timestamp("2025-11-01T10:00:00Z"),
            )
        )

        report = memory_health(store, now=NOW)
        print(f"Memory health score: {report.score} (grade {report.grade})")
        print("Components:")
        for component in report.components:
            print(
                f"  - {component.name}: {component.score} "
                f"(weight {component.weight}) — {component.detail}"
            )
        print("Recommendations:")
        for recommendation in report.recommendations:
            print(f"  - {recommendation}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
