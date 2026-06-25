"""Deterministic accountability reports.

Wraps the Phase 6 accountability metrics into a report covering assigned vs
unassigned work, per-owner load and overdue work, commitments missing due dates,
tasks missing owners, and a follow-through summary.
"""

from datetime import datetime

from organizational_memory.analytics.accountability import accountability
from organizational_memory.reports.base import Report, ReportSection, ReportTable
from organizational_memory.reports.common import counts_table
from organizational_memory.storage.store import MemoryStore
from organizational_memory.utils.time import utc_now


def accountability_report(
    store: MemoryStore,
    *,
    now: datetime | None = None,
) -> Report:
    """Build an accountability :class:`Report` from work records."""
    generated_at = now or utc_now()
    metrics = accountability(store, now=generated_at)

    owner_rows: list[tuple[str, ...]] = [
        (
            owner.owner,
            str(owner.assigned),
            str(owner.open),
            str(owner.overdue),
        )
        for owner in metrics.owners
    ]
    follow_through_rows: list[tuple[str, ...]] = [
        (owner.owner, str(owner.completed), str(owner.open),
         f"{owner.follow_through_score}")
        for owner in metrics.owners
    ]
    total_overdue = sum(owner.overdue for owner in metrics.owners)

    return Report(
        title="Accountability report",
        generated_at=generated_at,
        summary={
            "assigned": metrics.assigned,
            "unassigned": metrics.unassigned,
            "overdue": total_overdue,
            "commitments_without_due_date": metrics.commitments_without_due_date,
            "tasks_without_owner": metrics.tasks_without_owner,
            "owners": len(metrics.owners),
        },
        sections=[
            ReportSection(
                title="Assignment overview",
                metrics={
                    "assigned": metrics.assigned,
                    "unassigned": metrics.unassigned,
                },
            ),
            ReportSection(
                title="Owner load",
                tables=[
                    ReportTable(
                        title="Work by owner",
                        columns=("owner", "assigned", "open", "overdue"),
                        rows=owner_rows,
                    )
                ],
            ),
            ReportSection(
                title="Overdue work",
                metrics={"total": total_overdue},
                tables=[
                    counts_table(
                        "Unresolved by owner", metrics.unresolved_by_owner
                    )
                ],
            ),
            ReportSection(
                title="Commitments without due dates",
                metrics={"count": metrics.commitments_without_due_date},
            ),
            ReportSection(
                title="Tasks without owners",
                metrics={"count": metrics.tasks_without_owner},
            ),
            ReportSection(
                title="Follow-through summary",
                tables=[
                    ReportTable(
                        title="Follow-through by owner",
                        columns=("owner", "completed", "open", "follow_through"),
                        rows=follow_through_rows,
                    )
                ],
            ),
        ],
    )
