"""Deterministic follow-up reports.

Focuses attention on what still needs action: open commitments and tasks, who
owns them, their due dates, dependency blockers, unanswered questions, and the
best candidates for the next review.
"""

from datetime import datetime

from organizational_memory.analytics.common import (
    count_by,
    days_overdue,
    is_open_status,
    is_overdue,
    owner_or_unassigned,
    status_value,
)
from organizational_memory.analytics.dependency_analytics import dependency_analytics
from organizational_memory.analytics.open_loop_metrics import open_loop_metrics
from organizational_memory.models import Commitment, OpenLoop, Task
from organizational_memory.models.enums import OpenLoopStatus
from organizational_memory.reports.base import Report, ReportSection, ReportTable
from organizational_memory.reports.common import counts_table
from organizational_memory.schemas.base import BaseRecord
from organizational_memory.storage.store import MemoryStore
from organizational_memory.utils.time import format_timestamp, utc_now


def _due(record: BaseRecord) -> str:
    due_at = getattr(record, "due_at", None)
    return format_timestamp(due_at) if isinstance(due_at, datetime) else ""


def _due_sort_key(record: BaseRecord) -> tuple[datetime, str]:
    due_at = getattr(record, "due_at", None)
    assert isinstance(due_at, datetime)
    return (due_at, record.id)


def follow_up_report(
    store: MemoryStore,
    *,
    now: datetime | None = None,
    review_limit: int = 5,
) -> Report:
    """Build a follow-up :class:`Report` of outstanding actions."""
    generated_at = now or utc_now()

    commitments = [
        c for c in store.list_records("Commitment")
        if isinstance(c, Commitment) and is_open_status(c.status)
    ]
    tasks = [
        t for t in store.list_records("Task")
        if isinstance(t, Task) and is_open_status(t.status)
    ]
    action_items: list[BaseRecord] = [*commitments, *tasks]
    action_items.sort(key=lambda r: r.id)

    overdue = [r for r in action_items if is_overdue(r, generated_at)]
    with_due = sorted(
        (r for r in action_items if getattr(r, "due_at", None) is not None),
        key=_due_sort_key,
    )

    dependencies = dependency_analytics(store)
    loops = open_loop_metrics(store, now=generated_at, oldest_limit=review_limit)
    unresolved = sorted(
        (
            loop for loop in store.list_records("OpenLoop")
            if isinstance(loop, OpenLoop) and loop.status is OpenLoopStatus.OPEN
        ),
        key=lambda loop: loop.id,
    )

    review_candidates: list[str] = []
    for age in loops.oldest_unresolved[:review_limit]:
        review_candidates.append(
            f"Open loop {age.id} (open {age.age_days} days): {age.question}"
        )

    return Report(
        title="Follow-up report",
        generated_at=generated_at,
        summary={
            "needs_action": len(action_items),
            "overdue": len(overdue),
            "unanswered_questions": len(unresolved),
            "blocked_records": len(dependencies.blocked_records),
        },
        sections=[
            ReportSection(
                title="Needs action",
                metrics={"count": len(action_items)},
                tables=[
                    ReportTable(
                        title="Outstanding action items",
                        columns=("id", "type", "owner", "status", "due"),
                        rows=[
                            (
                                r.id,
                                type(r).__name__,
                                owner_or_unassigned(r),
                                status_value(getattr(r, "status", None)),
                                _due(r),
                            )
                            for r in action_items
                        ],
                    )
                ],
            ),
            ReportSection(
                title="By owner",
                metrics=dict(count_by(action_items, owner_or_unassigned)),
                tables=[
                    counts_table(
                        "Action items by owner",
                        count_by(action_items, owner_or_unassigned),
                    )
                ],
            ),
            ReportSection(
                title="Due dates",
                metrics={"overdue": len(overdue)},
                tables=[
                    ReportTable(
                        title="Items with due dates",
                        columns=("id", "owner", "due", "days_overdue"),
                        rows=[
                            (
                                r.id,
                                owner_or_unassigned(r),
                                _due(r),
                                f"{days_overdue(r, generated_at)}",
                            )
                            for r in with_due
                        ],
                    )
                ],
            ),
            ReportSection(
                title="Blockers",
                metrics={
                    "blocked_records": len(dependencies.blocked_records),
                    "active_blockers": dependencies.active_blockers,
                },
                tables=[
                    counts_table("Multi-blockers", dependencies.multi_blockers)
                ],
            ),
            ReportSection(
                title="Unanswered questions",
                metrics={"count": len(unresolved)},
                tables=[
                    ReportTable(
                        title="Open questions",
                        columns=("id", "question", "owner"),
                        rows=[
                            (loop.id, loop.question, loop.owner_id or "")
                            for loop in unresolved
                        ],
                    )
                ],
            ),
            ReportSection(
                title="Next review candidates",
                body=review_candidates,
            ),
        ],
    )
