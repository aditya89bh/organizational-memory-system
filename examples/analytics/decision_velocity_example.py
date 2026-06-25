"""Runnable decision velocity example.

Run it with::

    python examples/analytics/decision_velocity_example.py

Stores a few decisions and prints the deterministic decision velocity report.
Nothing is left on disk.
"""

import tempfile
from pathlib import Path

from organizational_memory.analytics.decision_velocity import decision_velocity
from organizational_memory.models import Decision
from organizational_memory.models.enums import DecisionStatus
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import parse_timestamp


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        store = JSONStore(Path(tmp) / "memory.json")
        store.save_record(
            Decision(
                id="d1",
                title="Adopt service mesh",
                description="x",
                owner_id="alice",
                source_meeting_id="m1",
                status=DecisionStatus.ACCEPTED,
                decided_at=parse_timestamp("2026-02-02T10:00:00Z"),
            )
        )
        store.save_record(
            Decision(
                id="d2",
                title="Pricing tiers",
                description="x",
                owner_id="bob",
                source_meeting_id="m1",
                status=DecisionStatus.PROPOSED,
                decided_at=parse_timestamp("2026-02-03T10:00:00Z"),
            )
        )
        store.save_record(
            Decision(
                id="d3",
                title="Legacy approach",
                description="x",
                owner_id="alice",
                source_meeting_id="m2",
                status=DecisionStatus.SUPERSEDED,
                decided_at=parse_timestamp("2026-02-10T10:00:00Z"),
            )
        )

        report = decision_velocity(store)
        print(f"Total decisions: {report.total}")
        print(f"Active: {report.active}  Superseded: {report.superseded}")
        print("Per week:")
        for week, count in report.per_week.items():
            print(f"  - {week}: {count}")
        print("By owner:")
        for owner, count in report.by_owner.items():
            print(f"  - {owner}: {count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
