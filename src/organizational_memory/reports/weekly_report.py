"""Deterministic weekly reports.

Builds a report for an explicit half-open date range ``[start, end)`` covering
decisions made, commitments created/completed, open loops created/resolved,
overdue work, owner load, major bottlenecks, and a memory health summary.

Creation timing uses ``created_at`` (and ``decided_at`` for decisions);
completion/resolution timing uses ``updated_at`` so callers can drive it
deterministically.
"""

from datetime import datetime

from organizational_memory.analytics.bottlenecks import bottlenecks
from organizational_memory.analytics.memory_health import memory_health
from organizational_memory.analytics.overdue_tasks import overdue_tasks
from organizational_memory.analytics.ownership_metrics import ownership_metrics
from organizational_memory.models import Commitment, Decision, OpenLoop
from organizational_memory.models.enums import CommitmentStatus, OpenLoopStatus
from organizational_memory.reports.base import Report, ReportSection, ReportTable
from organizational_memory.reports.common import counts_table, in_window, window_label
from organizational_memory.storage.store import MemoryStore


def weekly_report(
    store: MemoryStore,
    *,
    start: datetime,
    end: datetime,
    now: datetime | None = None,
) -> Report:
    """Build a weekly :class:`Report` for the window ``[start, end)``."""
    generated_at = now or end

    decisions = [
        d for d in store.list_records("Decision")
        if isinstance(d, Decision)
        and in_window(d.decided_at or d.created_at, start, end)
    ]
    commitments = [
        c for c in store.list_records("Commitment") if isinstance(c, Commitment)
    ]
    commitments_created = [
        c for c in commitments if in_window(c.created_at, start, end)
    ]
    commitments_completed = [
        c
        for c in commitments
        if c.status is CommitmentStatus.COMPLETED
        and in_window(c.updated_at, start, end)
    ]
    loops = [r for r in store.list_records("OpenLoop") if isinstance(r, OpenLoop)]
    loops_created = [loop for loop in loops if in_window(loop.created_at, start, end)]
    loops_resolved = [
        loop
        for loop in loops
        if loop.status is OpenLoopStatus.RESOLVED
        and in_window(loop.updated_at, start, end)
    ]

    overdue = overdue_tasks(store, now=generated_at)
    ownership = ownership_metrics(store, now=generated_at)
    bottleneck = bottlenecks(store, now=generated_at)
    health = memory_health(store, now=generated_at)

    bottleneck_lines = []
    for owner, count in bottleneck.overloaded_owners.items():
        bottleneck_lines.append(f"Overloaded owner {owner}: {count} overdue")
    for meeting in bottleneck.low_signal_meetings:
        bottleneck_lines.append(
            f"Low-signal meeting {meeting.meeting_id}: "
            f"{meeting.open_loops} open loops, {meeting.decisions} decisions"
        )

    return Report(
        title="Weekly report",
        generated_at=generated_at,
        summary={
            "window": window_label(start, end),
            "decisions": len(decisions),
            "commitments_created": len(commitments_created),
            "commitments_completed": len(commitments_completed),
            "open_loops_created": len(loops_created),
            "open_loops_resolved": len(loops_resolved),
            "overdue": overdue.total,
            "health_score": health.score,
            "health_grade": health.grade,
        },
        sections=[
            ReportSection(
                title="Decisions made",
                metrics={"count": len(decisions)},
                tables=[
                    ReportTable(
                        title="Decisions made",
                        columns=("id", "title", "status"),
                        rows=[
                            (d.id, d.title, d.status.value)
                            for d in sorted(decisions, key=lambda d: d.id)
                        ],
                    )
                ],
            ),
            ReportSection(
                title="Commitments",
                metrics={
                    "created": len(commitments_created),
                    "completed": len(commitments_completed),
                },
            ),
            ReportSection(
                title="Open loops",
                metrics={
                    "created": len(loops_created),
                    "resolved": len(loops_resolved),
                },
            ),
            ReportSection(
                title="Overdue work",
                metrics={"total": overdue.total},
                tables=[counts_table("Overdue by owner", overdue.by_owner)],
            ),
            ReportSection(
                title="Owner load",
                metrics=dict(ownership.open_by_owner),
                tables=[counts_table("Open work by owner", ownership.open_by_owner)],
            ),
            ReportSection(
                title="Bottlenecks",
                body=bottleneck_lines,
            ),
            ReportSection(
                title="Memory health",
                metrics={"score": health.score, "grade": health.grade},
            ),
        ],
    )
