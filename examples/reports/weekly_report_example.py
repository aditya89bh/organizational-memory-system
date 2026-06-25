"""Runnable weekly report example.

Run it with::

    python examples/reports/weekly_report_example.py

Builds a small memory and prints a deterministic weekly report for an explicit
date range. Nothing is left on disk.
"""

import tempfile
from pathlib import Path

from organizational_memory.models import Commitment, Decision, OpenLoop
from organizational_memory.models.enums import CommitmentStatus, OpenLoopStatus
from organizational_memory.reports.exporters.markdown import MarkdownExporter
from organizational_memory.reports.weekly_report import weekly_report
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import parse_timestamp

START = parse_timestamp("2026-02-16T00:00:00Z")
END = parse_timestamp("2026-02-23T00:00:00Z")


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        store = JSONStore(Path(tmp) / "memory.json")
        store.save_record(
            Decision(id="d1", title="Pick database", description="x",
                     owner_id="alice",
                     decided_at=parse_timestamp("2026-02-17T10:00:00Z"),
                     created_at=parse_timestamp("2026-02-17T10:00:00Z"))
        )
        store.save_record(
            Commitment(id="c1", owner_id="bob", description="Migrate schema",
                       status=CommitmentStatus.PENDING,
                       created_at=parse_timestamp("2026-02-18T10:00:00Z"),
                       due_at=parse_timestamp("2026-02-20T10:00:00Z"))
        )
        store.save_record(
            OpenLoop(id="o1", question="Backups strategy?",
                     status=OpenLoopStatus.OPEN,
                     created_at=parse_timestamp("2026-02-19T10:00:00Z"))
        )

        report = weekly_report(store, start=START, end=END, now=END)
        print(MarkdownExporter().export(report))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
