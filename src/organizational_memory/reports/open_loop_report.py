"""Deterministic open loop reports.

Summarizes unresolved and resolved questions, the oldest outstanding ones, open
loops by owner and meeting, and overdue open loops. Ages are measured against an
explicit reference time for reproducibility.
"""

from datetime import datetime

from organizational_memory.analytics.common import (
    count_by,
    days_overdue,
    is_overdue,
    meeting_or_none,
    owner_or_unassigned,
)
from organizational_memory.analytics.open_loop_metrics import open_loop_metrics
from organizational_memory.models import OpenLoop
from organizational_memory.models.enums import OpenLoopStatus
from organizational_memory.reports.base import Report, ReportSection, ReportTable
from organizational_memory.storage.store import MemoryStore
from organizational_memory.utils.time import utc_now


def _counts_table(title: str, counts: dict[str, int]) -> ReportTable:
    return ReportTable(
        title=title,
        columns=("key", "count"),
        rows=[(key, str(value)) for key, value in counts.items()],
    )


def open_loop_report(
    store: MemoryStore,
    *,
    now: datetime | None = None,
    oldest_limit: int = 5,
) -> Report:
    """Build a :class:`Report` summarizing all open loops in the store."""
    generated_at = now or utc_now()
    loops = [r for r in store.list_records("OpenLoop") if isinstance(r, OpenLoop)]
    ordered = sorted(loops, key=lambda loop: loop.id)

    unresolved = [loop for loop in ordered if loop.status is OpenLoopStatus.OPEN]
    resolved = [loop for loop in ordered if loop.status is OpenLoopStatus.RESOLVED]
    overdue = [loop for loop in ordered if is_overdue(loop, generated_at)]

    metrics = open_loop_metrics(
        store, now=generated_at, oldest_limit=oldest_limit
    )
    oldest_rows: list[tuple[str, ...]] = [
        (age.id, age.question, f"{age.age_days}")
        for age in metrics.oldest_unresolved
    ]

    return Report(
        title="Open loop report",
        generated_at=generated_at,
        summary={
            "total": len(loops),
            "unresolved": len(unresolved),
            "resolved": len(resolved),
            "overdue": len(overdue),
            "average_age_days": metrics.average_age_days,
        },
        sections=[
            ReportSection(
                title="Unresolved",
                metrics={"count": len(unresolved)},
                tables=[
                    ReportTable(
                        title="Unresolved open loops",
                        columns=("id", "question", "owner"),
                        rows=[
                            (loop.id, loop.question, loop.owner_id or "")
                            for loop in unresolved
                        ],
                    )
                ],
            ),
            ReportSection(
                title="Resolved",
                metrics={"count": len(resolved)},
                tables=[
                    ReportTable(
                        title="Resolved open loops",
                        columns=("id", "question", "owner"),
                        rows=[
                            (loop.id, loop.question, loop.owner_id or "")
                            for loop in resolved
                        ],
                    )
                ],
            ),
            ReportSection(
                title="Oldest unresolved",
                tables=[
                    ReportTable(
                        title="Oldest unresolved questions",
                        columns=("id", "question", "age_days"),
                        rows=oldest_rows,
                    )
                ],
            ),
            ReportSection(
                title="By owner",
                metrics=dict(count_by(loops, owner_or_unassigned)),
                tables=[
                    _counts_table(
                        "Open loops by owner", count_by(loops, owner_or_unassigned)
                    )
                ],
            ),
            ReportSection(
                title="By meeting",
                metrics=dict(count_by(loops, meeting_or_none)),
                tables=[
                    _counts_table(
                        "Open loops by meeting", count_by(loops, meeting_or_none)
                    )
                ],
            ),
            ReportSection(
                title="Overdue",
                metrics={"count": len(overdue)},
                tables=[
                    ReportTable(
                        title="Overdue open loops",
                        columns=("id", "owner", "days_overdue"),
                        rows=[
                            (
                                loop.id,
                                loop.owner_id or "",
                                f"{days_overdue(loop, generated_at)}",
                            )
                            for loop in overdue
                        ],
                    )
                ],
            ),
        ],
    )
