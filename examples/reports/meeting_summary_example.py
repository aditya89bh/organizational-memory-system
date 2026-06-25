"""Runnable meeting summary example.

Run it with::

    python examples/reports/meeting_summary_example.py

Builds a small meeting with structured records and prints a deterministic
meeting summary report as Markdown. Nothing is left on disk.
"""

import tempfile
from pathlib import Path

from organizational_memory.models import (
    Commitment,
    Decision,
    Meeting,
    OpenLoop,
    Task,
)
from organizational_memory.reports.exporters.markdown import MarkdownExporter
from organizational_memory.reports.meeting_summary import meeting_summary
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import parse_timestamp

NOW = parse_timestamp("2026-03-01T00:00:00Z")


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        store = JSONStore(Path(tmp) / "memory.json")
        store.save_record(
            Meeting(
                id="m1",
                title="Platform kickoff",
                started_at=parse_timestamp("2026-02-20T09:00:00Z"),
                participants=["alice", "bob"],
                source="transcript",
            )
        )
        store.save_record(
            Decision(id="d1", title="Adopt service mesh", description="x",
                     owner_id="alice", source_meeting_id="m1",
                     rationale="Improves observability and traffic control.")
        )
        store.save_record(
            Commitment(id="c1", owner_id="bob", description="Draft rollout plan",
                       source_meeting_id="m1")
        )
        store.save_record(
            Task(id="t1", title="Provision staging", description="x",
                 owner_id="alice", source_meeting_id="m1")
        )
        store.save_record(
            OpenLoop(id="o1", question="How do we handle multi-region?",
                     source_meeting_id="m1")
        )

        report = meeting_summary(store, "m1", now=NOW)
        print(MarkdownExporter().export(report))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
