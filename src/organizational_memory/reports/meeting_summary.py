"""Deterministic meeting summary reports.

Builds a :class:`Report` for a single meeting, collecting the structured records
attributed to it: participants, decisions, commitments, tasks, open loops, and
risks, plus source metadata. All output is derived deterministically from the
store.
"""

from datetime import datetime

from organizational_memory.models import (
    Commitment,
    Decision,
    Meeting,
    OpenLoop,
    Risk,
    Task,
)
from organizational_memory.reports.base import Report, ReportSection, ReportTable
from organizational_memory.storage.store import MemoryStore
from organizational_memory.utils.time import format_timestamp, utc_now


def meeting_summary(
    store: MemoryStore,
    meeting_id: str,
    *,
    now: datetime | None = None,
) -> Report:
    """Build a meeting summary :class:`Report` for ``meeting_id``.

    Raises:
        KeyError: If no meeting with ``meeting_id`` exists in the store.
    """
    generated_at = now or utc_now()
    meeting = store.get_record("Meeting", meeting_id)
    if not isinstance(meeting, Meeting):
        raise KeyError(f"meeting {meeting_id!r} not found")

    decisions = [
        r for r in store.list_records("Decision")
        if isinstance(r, Decision) and r.source_meeting_id == meeting_id
    ]
    commitments = [
        r for r in store.list_records("Commitment")
        if isinstance(r, Commitment) and r.source_meeting_id == meeting_id
    ]
    tasks = [
        r for r in store.list_records("Task")
        if isinstance(r, Task) and r.source_meeting_id == meeting_id
    ]
    open_loops = [
        r for r in store.list_records("OpenLoop")
        if isinstance(r, OpenLoop) and r.source_meeting_id == meeting_id
    ]
    risks = [
        r for r in store.list_records("Risk")
        if isinstance(r, Risk) and r.source_meeting_id == meeting_id
    ]

    participants_section = ReportSection(
        title="Participants",
        body=list(meeting.participants),
        metrics={"count": len(meeting.participants)},
    )
    decisions_section = ReportSection(
        title="Decisions",
        metrics={"count": len(decisions)},
        tables=[
            ReportTable(
                title="Decisions",
                columns=("id", "title", "status", "owner"),
                rows=[
                    (d.id, d.title, d.status.value, d.owner_id or "")
                    for d in sorted(decisions, key=lambda d: d.id)
                ],
            )
        ],
    )
    commitments_section = ReportSection(
        title="Commitments",
        metrics={"count": len(commitments)},
        tables=[
            ReportTable(
                title="Commitments",
                columns=("id", "description", "status", "owner"),
                rows=[
                    (c.id, c.description, c.status.value, c.owner_id)
                    for c in sorted(commitments, key=lambda c: c.id)
                ],
            )
        ],
    )
    tasks_section = ReportSection(
        title="Tasks",
        metrics={"count": len(tasks)},
        tables=[
            ReportTable(
                title="Tasks",
                columns=("id", "title", "status", "owner"),
                rows=[
                    (t.id, t.title, t.status.value, t.owner_id)
                    for t in sorted(tasks, key=lambda t: t.id)
                ],
            )
        ],
    )
    open_loops_section = ReportSection(
        title="Open loops",
        metrics={"count": len(open_loops)},
        tables=[
            ReportTable(
                title="Open loops",
                columns=("id", "question", "status", "owner"),
                rows=[
                    (loop.id, loop.question, loop.status.value, loop.owner_id or "")
                    for loop in sorted(open_loops, key=lambda loop: loop.id)
                ],
            )
        ],
    )
    risks_section = ReportSection(
        title="Risks",
        metrics={"count": len(risks)},
        tables=[
            ReportTable(
                title="Risks",
                columns=("id", "title", "severity", "status"),
                rows=[
                    (r.id, r.title, r.severity.value, r.status.value)
                    for r in sorted(risks, key=lambda r: r.id)
                ],
            )
        ],
    )

    metadata = {
        "meeting_id": meeting.id,
        "source": meeting.source,
        "started_at": format_timestamp(meeting.started_at),
    }
    if meeting.ended_at is not None:
        metadata["ended_at"] = format_timestamp(meeting.ended_at)

    return Report(
        title=f"Meeting summary: {meeting.title}",
        generated_at=generated_at,
        summary={
            "decisions": len(decisions),
            "commitments": len(commitments),
            "tasks": len(tasks),
            "open_loops": len(open_loops),
            "risks": len(risks),
            "participants": len(meeting.participants),
        },
        sections=[
            participants_section,
            decisions_section,
            commitments_section,
            tasks_section,
            open_loops_section,
            risks_section,
        ],
        metadata=metadata,
    )
