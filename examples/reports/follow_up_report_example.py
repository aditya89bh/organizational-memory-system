"""Runnable follow-up report example.

Run it with::

    python examples/reports/follow_up_report_example.py

Builds a small memory with outstanding work and prints a deterministic follow-up
report as Markdown. Nothing is left on disk.
"""

import tempfile
from pathlib import Path

from organizational_memory.models import Commitment, OpenLoop, Task
from organizational_memory.models.enums import (
    CommitmentStatus,
    OpenLoopStatus,
    TaskStatus,
)
from organizational_memory.reports.exporters.markdown import MarkdownExporter
from organizational_memory.reports.follow_up_report import follow_up_report
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import parse_timestamp

NOW = parse_timestamp("2026-03-01T00:00:00Z")


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        store = JSONStore(Path(tmp) / "memory.json")
        store.save_record(
            Commitment(id="c1", owner_id="alice", description="Send vendor contract",
                       status=CommitmentStatus.PENDING,
                       created_at=parse_timestamp("2026-02-10T10:00:00Z"),
                       due_at=parse_timestamp("2026-02-20T10:00:00Z"))
        )
        store.save_record(
            Task(id="t1", title="Review designs", description="x", owner_id="bob",
                 status=TaskStatus.TODO,
                 created_at=parse_timestamp("2026-02-22T10:00:00Z"))
        )
        store.save_record(
            OpenLoop(id="o1", question="Who approves the budget?",
                     status=OpenLoopStatus.OPEN,
                     created_at=parse_timestamp("2026-02-01T10:00:00Z"))
        )

        report = follow_up_report(store, now=NOW)
        print(MarkdownExporter().export(report))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
