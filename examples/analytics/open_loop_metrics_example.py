"""Runnable open loop metrics example.

Run it with::

    python examples/analytics/open_loop_metrics_example.py

Stores open loops with fixed timestamps and prints the deterministic open loop
metrics against a fixed reference time. Nothing is left on disk.
"""

import tempfile
from pathlib import Path

from organizational_memory.analytics.open_loop_metrics import open_loop_metrics
from organizational_memory.models import OpenLoop
from organizational_memory.models.enums import OpenLoopStatus
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
                owner_id="alice",
                status=OpenLoopStatus.OPEN,
                created_at=parse_timestamp("2026-02-02T10:00:00Z"),
            )
        )
        store.save_record(
            OpenLoop(
                id="o2",
                question="Budget approval?",
                owner_id="bob",
                status=OpenLoopStatus.OPEN,
                created_at=parse_timestamp("2026-02-20T10:00:00Z"),
            )
        )
        store.save_record(
            OpenLoop(
                id="o3",
                question="Vendor choice?",
                status=OpenLoopStatus.RESOLVED,
                created_at=parse_timestamp("2026-02-20T10:00:00Z"),
            )
        )

        report = open_loop_metrics(store, now=NOW)
        print(f"Total: {report.total}")
        print(f"Unresolved: {report.unresolved}  Resolved: {report.resolved}")
        print(f"Average age (days): {report.average_age_days}")
        print("Oldest unresolved:")
        for age in report.oldest_unresolved:
            print(f"  - {age.id}: {age.age_days} days ({age.question})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
