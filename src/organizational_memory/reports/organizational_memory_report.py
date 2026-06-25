"""Deterministic organizational memory reports.

A high-level rollup combining Phase 6 analytics into one report: the memory
health score, key (accepted) decisions, the oldest unresolved loops, bottleneck
signals, repeated discussions, dependency risks, and suggested follow-ups.
"""

from datetime import datetime

from organizational_memory.analytics.bottlenecks import bottlenecks
from organizational_memory.analytics.dependency_analytics import dependency_analytics
from organizational_memory.analytics.memory_health import memory_health
from organizational_memory.analytics.open_loop_metrics import open_loop_metrics
from organizational_memory.analytics.repeated_discussions import repeated_discussions
from organizational_memory.models import Decision
from organizational_memory.models.enums import DecisionStatus
from organizational_memory.reports.base import Report, ReportSection, ReportTable
from organizational_memory.reports.common import counts_table
from organizational_memory.storage.store import MemoryStore
from organizational_memory.utils.time import utc_now


def organizational_memory_report(
    store: MemoryStore,
    *,
    now: datetime | None = None,
    key_decision_limit: int = 10,
    unresolved_limit: int = 10,
) -> Report:
    """Build a high-level organizational memory :class:`Report`."""
    generated_at = now or utc_now()

    health = memory_health(store, now=generated_at)
    bottleneck = bottlenecks(store, now=generated_at)
    dependencies = dependency_analytics(store)
    repeated = repeated_discussions(store)
    loops = open_loop_metrics(store, now=generated_at, oldest_limit=unresolved_limit)

    key_decisions = [
        d for d in store.list_records("Decision")
        if isinstance(d, Decision) and d.status is DecisionStatus.ACCEPTED
    ]
    key_decisions.sort(key=lambda d: d.id)
    key_decisions = key_decisions[:key_decision_limit]

    follow_ups = list(health.recommendations)
    for age in loops.oldest_unresolved[:3]:
        follow_ups.append(
            f"Resolve open loop {age.id} (open {age.age_days} days): {age.question}"
        )
    for owner, count in bottleneck.overloaded_owners.items():
        follow_ups.append(f"Rebalance {owner}: {count} overdue items")

    return Report(
        title="Organizational memory report",
        generated_at=generated_at,
        summary={
            "health_score": health.score,
            "health_grade": health.grade,
            "key_decisions": len(key_decisions),
            "unresolved_loops": loops.unresolved,
            "bottleneck_owners": len(bottleneck.overloaded_owners),
            "repeated_topics": len(repeated.topic_clusters),
            "dependency_blocked": len(dependencies.blocked_records),
        },
        sections=[
            ReportSection(
                title="Memory health",
                metrics={"score": health.score, "grade": health.grade},
                body=list(health.recommendations),
            ),
            ReportSection(
                title="Key decisions",
                metrics={"count": len(key_decisions)},
                tables=[
                    ReportTable(
                        title="Accepted decisions",
                        columns=("id", "title", "owner"),
                        rows=[
                            (d.id, d.title, d.owner_id or "")
                            for d in key_decisions
                        ],
                    )
                ],
            ),
            ReportSection(
                title="Unresolved loops",
                metrics={"count": loops.unresolved},
                tables=[
                    ReportTable(
                        title="Oldest unresolved questions",
                        columns=("id", "question", "age_days"),
                        rows=[
                            (age.id, age.question, f"{age.age_days}")
                            for age in loops.oldest_unresolved
                        ],
                    )
                ],
            ),
            ReportSection(
                title="Bottlenecks",
                metrics={
                    "overloaded_owners": len(bottleneck.overloaded_owners),
                    "low_signal_meetings": len(bottleneck.low_signal_meetings),
                },
                tables=[
                    counts_table(
                        "Overloaded owners", bottleneck.overloaded_owners
                    )
                ],
            ),
            ReportSection(
                title="Repeated discussions",
                metrics={"count": len(repeated.topic_clusters)},
                tables=[
                    ReportTable(
                        title="Repeated topics",
                        columns=("label", "occurrences"),
                        rows=[
                            (cluster.label, str(cluster.occurrences))
                            for cluster in repeated.topic_clusters
                        ],
                    )
                ],
            ),
            ReportSection(
                title="Dependency risks",
                metrics={
                    "active_blockers": dependencies.active_blockers,
                    "blocked_records": len(dependencies.blocked_records),
                    "longest_chain": dependencies.longest_chain,
                },
                tables=[
                    counts_table("Multi-blockers", dependencies.multi_blockers)
                ],
            ),
            ReportSection(
                title="Suggested follow-ups",
                body=follow_ups,
            ),
        ],
    )
