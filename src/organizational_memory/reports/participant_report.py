"""Deterministic participant reports.

Summarizes one participant's footprint across organizational memory: meetings
attended, owned decisions, commitments, tasks, and open loops, plus overdue work
and a follow-up load count. This is a workload view only and intentionally makes
no employee-performance judgements.
"""

from datetime import datetime

from organizational_memory.analytics.common import is_open_status, is_overdue
from organizational_memory.models import (
    Commitment,
    Decision,
    Meeting,
    OpenLoop,
    Participant,
    Task,
)
from organizational_memory.reports.base import Report, ReportSection, ReportTable
from organizational_memory.storage.store import MemoryStore
from organizational_memory.utils.time import utc_now


def participant_report(
    store: MemoryStore,
    participant_id: str,
    *,
    now: datetime | None = None,
) -> Report:
    """Build a workload :class:`Report` for ``participant_id``."""
    generated_at = now or utc_now()

    display_name = participant_id
    person = store.get_record("Participant", participant_id)
    if isinstance(person, Participant):
        display_name = person.name

    meetings = [
        m for m in store.list_records("Meeting")
        if isinstance(m, Meeting) and participant_id in m.participants
    ]
    decisions = [
        d for d in store.list_records("Decision")
        if isinstance(d, Decision) and d.owner_id == participant_id
    ]
    commitments = [
        c for c in store.list_records("Commitment")
        if isinstance(c, Commitment) and c.owner_id == participant_id
    ]
    tasks = [
        t for t in store.list_records("Task")
        if isinstance(t, Task) and t.owner_id == participant_id
    ]
    open_loops = [
        loop for loop in store.list_records("OpenLoop")
        if isinstance(loop, OpenLoop) and loop.owner_id == participant_id
    ]

    overdue = [
        record
        for record in (*commitments, *tasks, *open_loops)
        if is_overdue(record, generated_at)
    ]
    follow_up = [
        record
        for record in (*commitments, *tasks, *open_loops)
        if is_open_status(getattr(record, "status", None))
    ]

    return Report(
        title=f"Participant report: {display_name}",
        generated_at=generated_at,
        summary={
            "participant_id": participant_id,
            "meetings_attended": len(meetings),
            "decisions": len(decisions),
            "commitments": len(commitments),
            "tasks": len(tasks),
            "open_loops": len(open_loops),
            "overdue": len(overdue),
            "follow_up_load": len(follow_up),
        },
        sections=[
            ReportSection(
                title="Meetings attended",
                metrics={"count": len(meetings)},
                tables=[
                    ReportTable(
                        title="Meetings attended",
                        columns=("id", "title"),
                        rows=[
                            (m.id, m.title)
                            for m in sorted(meetings, key=lambda m: m.id)
                        ],
                    )
                ],
            ),
            ReportSection(
                title="Owned decisions",
                metrics={"count": len(decisions)},
                tables=[
                    ReportTable(
                        title="Owned decisions",
                        columns=("id", "title", "status"),
                        rows=[
                            (d.id, d.title, d.status.value)
                            for d in sorted(decisions, key=lambda d: d.id)
                        ],
                    )
                ],
            ),
            ReportSection(
                title="Owned commitments",
                metrics={"count": len(commitments)},
                tables=[
                    ReportTable(
                        title="Owned commitments",
                        columns=("id", "description", "status"),
                        rows=[
                            (c.id, c.description, c.status.value)
                            for c in sorted(commitments, key=lambda c: c.id)
                        ],
                    )
                ],
            ),
            ReportSection(
                title="Owned tasks",
                metrics={"count": len(tasks)},
                tables=[
                    ReportTable(
                        title="Owned tasks",
                        columns=("id", "title", "status"),
                        rows=[
                            (t.id, t.title, t.status.value)
                            for t in sorted(tasks, key=lambda t: t.id)
                        ],
                    )
                ],
            ),
            ReportSection(
                title="Open loops",
                metrics={"count": len(open_loops)},
                tables=[
                    ReportTable(
                        title="Owned open loops",
                        columns=("id", "question", "status"),
                        rows=[
                            (loop.id, loop.question, loop.status.value)
                            for loop in sorted(open_loops, key=lambda loop: loop.id)
                        ],
                    )
                ],
            ),
            ReportSection(
                title="Overdue work",
                metrics={"count": len(overdue)},
                tables=[
                    ReportTable(
                        title="Overdue work",
                        columns=("id", "type"),
                        rows=[
                            (record.id, type(record).__name__)
                            for record in sorted(overdue, key=lambda r: r.id)
                        ],
                    )
                ],
            ),
            ReportSection(
                title="Follow-up load",
                metrics={"count": len(follow_up)},
            ),
        ],
    )
