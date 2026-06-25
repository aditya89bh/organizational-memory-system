"""Deterministic monthly reports.

Aggregates Phase 6 analytics into a monthly view: decision velocity, commitment
completion, a window-scoped open-loop trend, repeated discussions, an
accountability summary, and the current memory health snapshot. A true health
*trend* requires historical snapshots, which are not stored, so the current
snapshot is reported instead.
"""

from datetime import datetime

from organizational_memory.analytics.accountability import accountability
from organizational_memory.analytics.commitment_completion import (
    commitment_completion,
)
from organizational_memory.analytics.common import iso_week
from organizational_memory.analytics.decision_velocity import decision_velocity
from organizational_memory.analytics.memory_health import memory_health
from organizational_memory.analytics.repeated_discussions import repeated_discussions
from organizational_memory.models import OpenLoop
from organizational_memory.reports.base import Report, ReportSection, ReportTable
from organizational_memory.reports.common import counts_table, in_window, window_label
from organizational_memory.storage.store import MemoryStore


def monthly_report(
    store: MemoryStore,
    *,
    start: datetime,
    end: datetime,
    now: datetime | None = None,
) -> Report:
    """Build a monthly :class:`Report` for the window ``[start, end)``."""
    generated_at = now or end

    velocity = decision_velocity(store)
    completion = commitment_completion(store)
    repeated = repeated_discussions(store)
    accountability_report = accountability(store, now=generated_at)
    health = memory_health(store, now=generated_at)

    loop_trend: dict[str, int] = {}
    for record in store.list_records("OpenLoop"):
        if isinstance(record, OpenLoop) and in_window(record.created_at, start, end):
            bucket = iso_week(record.created_at)
            loop_trend[bucket] = loop_trend.get(bucket, 0) + 1
    loop_trend = dict(sorted(loop_trend.items()))

    repeated_rows: list[tuple[str, ...]] = [
        (cluster.kind, cluster.label, str(cluster.occurrences))
        for cluster in (*repeated.topic_clusters, *repeated.open_loop_clusters)
    ]
    follow_through_rows: list[tuple[str, ...]] = [
        (
            owner.owner,
            str(owner.assigned),
            str(owner.completed),
            str(owner.open),
            f"{owner.follow_through_score}",
        )
        for owner in accountability_report.owners
    ]

    return Report(
        title="Monthly report",
        generated_at=generated_at,
        summary={
            "window": window_label(start, end),
            "decisions_total": velocity.total,
            "active_decisions": velocity.active,
            "commitment_completion_rate": completion.completion_rate,
            "repeated_topics": len(repeated.topic_clusters),
            "health_score": health.score,
            "health_grade": health.grade,
        },
        sections=[
            ReportSection(
                title="Decision velocity",
                metrics={
                    "total": velocity.total,
                    "active": velocity.active,
                    "superseded": velocity.superseded,
                },
                tables=[counts_table("Decisions per week", velocity.per_week)],
            ),
            ReportSection(
                title="Commitment completion",
                metrics={
                    "total": completion.total,
                    "completed": completion.completed,
                    "open": completion.open,
                    "completion_rate": completion.completion_rate,
                },
            ),
            ReportSection(
                title="Open-loop trend",
                tables=[counts_table("Open loops created per week", loop_trend)],
            ),
            ReportSection(
                title="Repeated discussions",
                metrics={
                    "topic_clusters": len(repeated.topic_clusters),
                    "open_loop_clusters": len(repeated.open_loop_clusters),
                },
                tables=[
                    ReportTable(
                        title="Repeated clusters",
                        columns=("kind", "label", "occurrences"),
                        rows=repeated_rows,
                    )
                ],
            ),
            ReportSection(
                title="Accountability summary",
                metrics={
                    "assigned": accountability_report.assigned,
                    "unassigned": accountability_report.unassigned,
                    "commitments_without_due_date": (
                        accountability_report.commitments_without_due_date
                    ),
                    "tasks_without_owner": accountability_report.tasks_without_owner,
                },
                tables=[
                    ReportTable(
                        title="Owner follow-through",
                        columns=(
                            "owner",
                            "assigned",
                            "completed",
                            "open",
                            "follow_through",
                        ),
                        rows=follow_through_rows,
                    )
                ],
            ),
            ReportSection(
                title="Memory health",
                metrics={"score": health.score, "grade": health.grade},
                tables=[
                    ReportTable(
                        title="Health components",
                        columns=("component", "score", "detail"),
                        rows=[
                            (c.name, f"{c.score}", c.detail)
                            for c in health.components
                        ],
                    )
                ],
            ),
        ],
    )
