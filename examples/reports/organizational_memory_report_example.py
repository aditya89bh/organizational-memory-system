"""Runnable organizational memory report example.

Run it with::

    python examples/reports/organizational_memory_report_example.py

Builds a small mixed memory and prints a deterministic high-level organizational
memory report as Markdown. Nothing is left on disk.
"""

import tempfile
from pathlib import Path

from organizational_memory.models import Commitment, Decision, OpenLoop
from organizational_memory.models.enums import (
    CommitmentStatus,
    DecisionStatus,
    OpenLoopStatus,
)
from organizational_memory.reports.exporters.markdown import MarkdownExporter
from organizational_memory.reports.organizational_memory_report import (
    organizational_memory_report,
)
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import parse_timestamp

NOW = parse_timestamp("2026-03-01T00:00:00Z")


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        store = JSONStore(Path(tmp) / "memory.json")
        store.save_record(
            Decision(id="d1", title="Adopt service mesh", description="x",
                     owner_id="alice", status=DecisionStatus.ACCEPTED,
                     decided_at=parse_timestamp("2026-02-05T10:00:00Z"))
        )
        store.save_record(
            Decision(id="d2", title="Pricing model", description="x",
                     status=DecisionStatus.PROPOSED,
                     created_at=parse_timestamp("2025-12-01T10:00:00Z"))
        )
        store.save_record(
            Commitment(id="c1", owner_id="bob", description="Publish runbook",
                       status=CommitmentStatus.PENDING,
                       created_at=parse_timestamp("2026-02-01T10:00:00Z"),
                       due_at=parse_timestamp("2026-02-15T10:00:00Z"))
        )
        store.save_record(
            OpenLoop(id="o1", question="How do we handle data residency?",
                     status=OpenLoopStatus.OPEN,
                     created_at=parse_timestamp("2026-01-10T10:00:00Z"))
        )

        report = organizational_memory_report(store, now=NOW)
        print(MarkdownExporter().export(report))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
