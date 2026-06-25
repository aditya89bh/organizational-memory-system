"""Deterministic commitment reports.

Summarizes commitments by lifecycle state (open, completed, overdue), by owner
and source meeting, and flags commitments that lack a due date.
"""

from datetime import datetime

from organizational_memory.analytics.common import (
    count_by,
    days_overdue,
    is_overdue,
    meeting_or_none,
    owner_or_unassigned,
)
from organizational_memory.models import Commitment
from organizational_memory.models.enums import CommitmentStatus
from organizational_memory.reports.base import Report, ReportSection, ReportTable
from organizational_memory.storage.store import MemoryStore
from organizational_memory.utils.time import format_timestamp, utc_now


def _counts_table(title: str, counts: dict[str, int]) -> ReportTable:
    return ReportTable(
        title=title,
        columns=("key", "count"),
        rows=[(key, str(value)) for key, value in counts.items()],
    )


def _due(commitment: Commitment) -> str:
    return format_timestamp(commitment.due_at) if commitment.due_at else ""


def commitment_report(
    store: MemoryStore,
    *,
    now: datetime | None = None,
) -> Report:
    """Build a :class:`Report` summarizing all commitments in the store."""
    generated_at = now or utc_now()
    commitments = [
        r for r in store.list_records("Commitment") if isinstance(r, Commitment)
    ]
    ordered = sorted(commitments, key=lambda c: c.id)

    open_items = [
        c for c in ordered
        if c.status in (CommitmentStatus.PENDING, CommitmentStatus.IN_PROGRESS)
    ]
    completed_items = [
        c for c in ordered if c.status is CommitmentStatus.COMPLETED
    ]
    overdue_items = [c for c in ordered if is_overdue(c, generated_at)]
    missing_due = [c for c in ordered if c.due_at is None]

    return Report(
        title="Commitment report",
        generated_at=generated_at,
        summary={
            "total": len(commitments),
            "open": len(open_items),
            "completed": len(completed_items),
            "overdue": len(overdue_items),
            "missing_due_date": len(missing_due),
        },
        sections=[
            ReportSection(
                title="Open commitments",
                metrics={"count": len(open_items)},
                tables=[
                    ReportTable(
                        title="Open commitments",
                        columns=("id", "description", "owner", "status", "due"),
                        rows=[
                            (c.id, c.description, c.owner_id, c.status.value, _due(c))
                            for c in open_items
                        ],
                    )
                ],
            ),
            ReportSection(
                title="Completed commitments",
                metrics={"count": len(completed_items)},
                tables=[
                    ReportTable(
                        title="Completed commitments",
                        columns=("id", "description", "owner"),
                        rows=[
                            (c.id, c.description, c.owner_id)
                            for c in completed_items
                        ],
                    )
                ],
            ),
            ReportSection(
                title="Overdue commitments",
                metrics={"count": len(overdue_items)},
                tables=[
                    ReportTable(
                        title="Overdue commitments",
                        columns=("id", "owner", "days_overdue"),
                        rows=[
                            (
                                c.id,
                                c.owner_id,
                                f"{days_overdue(c, generated_at)}",
                            )
                            for c in overdue_items
                        ],
                    )
                ],
            ),
            ReportSection(
                title="By owner",
                metrics=dict(count_by(commitments, owner_or_unassigned)),
                tables=[
                    _counts_table(
                        "Commitments by owner",
                        count_by(commitments, owner_or_unassigned),
                    )
                ],
            ),
            ReportSection(
                title="By meeting",
                metrics=dict(count_by(commitments, meeting_or_none)),
                tables=[
                    _counts_table(
                        "Commitments by meeting",
                        count_by(commitments, meeting_or_none),
                    )
                ],
            ),
            ReportSection(
                title="Missing due dates",
                metrics={"count": len(missing_due)},
                tables=[
                    ReportTable(
                        title="Commitments without due dates",
                        columns=("id", "owner", "status"),
                        rows=[
                            (c.id, c.owner_id, c.status.value) for c in missing_due
                        ],
                    )
                ],
            ),
        ],
    )
