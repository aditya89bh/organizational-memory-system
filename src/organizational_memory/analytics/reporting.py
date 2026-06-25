"""Analytics report generation.

Composes the individual analytics into a single structured report and an
equivalent dashboard snapshot, both derived deterministically from persisted
records.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from organizational_memory.analytics.bottlenecks import bottlenecks
from organizational_memory.analytics.commitment_completion import (
    commitment_completion,
)
from organizational_memory.analytics.common import is_open_status
from organizational_memory.analytics.dashboard import (
    AnalyticsCard,
    AnalyticsDashboard,
    AnalyticsSection,
    DashboardSnapshot,
)
from organizational_memory.analytics.decision_velocity import decision_velocity
from organizational_memory.analytics.memory_health import memory_health
from organizational_memory.analytics.open_loop_metrics import open_loop_metrics
from organizational_memory.analytics.overdue_tasks import overdue_tasks
from organizational_memory.analytics.ownership_metrics import ownership_metrics
from organizational_memory.analytics.productivity import productivity
from organizational_memory.models import Risk
from organizational_memory.storage.store import MemoryStore
from organizational_memory.utils.time import utc_now

DEFAULT_RISK_LIMIT = 10


@dataclass(frozen=True)
class AnalyticsReport:
    """A structured analytics report assembled from persisted memory."""

    summary: dict[str, Any] = field(default_factory=dict)
    key_metrics: dict[str, Any] = field(default_factory=dict)
    risks: list[dict[str, Any]] = field(default_factory=list)
    bottlenecks: dict[str, Any] = field(default_factory=dict)
    owner_load: dict[str, int] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "key_metrics": self.key_metrics,
            "risks": self.risks,
            "bottlenecks": self.bottlenecks,
            "owner_load": self.owner_load,
            "recommendations": self.recommendations,
        }


def generate_report(
    store: MemoryStore,
    *,
    now: datetime | None = None,
    risk_limit: int = DEFAULT_RISK_LIMIT,
) -> AnalyticsReport:
    """Build an :class:`AnalyticsReport` from the persisted records."""
    reference = now or utc_now()

    decisions = decision_velocity(store)
    completion = commitment_completion(store)
    loops = open_loop_metrics(store, now=reference)
    overdue = overdue_tasks(store, now=reference)
    ownership = ownership_metrics(store, now=reference)
    health = memory_health(store, now=reference)
    prod = productivity(store)
    bottleneck = bottlenecks(store, now=reference)

    summary = {
        "decisions": decisions.total,
        "commitments": completion.total,
        "open_loops": loops.total,
        "overdue": overdue.total,
        "health_grade": health.grade,
    }

    key_metrics = {
        "decision_total": decisions.total,
        "active_decisions": decisions.active,
        "commitment_completion_rate": completion.completion_rate,
        "unresolved_open_loops": loops.unresolved,
        "overdue_total": overdue.total,
        "closed_work_ratio": prod.closed_work_ratio,
        "memory_health_score": health.score,
    }

    risks: list[dict[str, Any]] = []
    open_risks = [
        r
        for r in store.list_records("Risk")
        if isinstance(r, Risk) and is_open_status(r.status)
    ]
    for risk in sorted(open_risks, key=lambda r: r.id):
        risks.append(
            {
                "type": "risk",
                "id": risk.id,
                "detail": risk.title,
                "severity": risk.severity.value,
            }
        )
    for item in overdue.items[:risk_limit]:
        risks.append(
            {
                "type": "overdue",
                "id": item.id,
                "detail": (
                    f"{item.record_type} overdue by {item.days_overdue} days"
                ),
            }
        )

    bottleneck_summary = {
        "overloaded_owners": bottleneck.overloaded_owners,
        "recurring_unresolved": len(bottleneck.recurring_unresolved),
        "blocked_records": list(bottleneck.blocked_records),
        "low_signal_meetings": [
            meeting.meeting_id for meeting in bottleneck.low_signal_meetings
        ],
    }

    return AnalyticsReport(
        summary=summary,
        key_metrics=key_metrics,
        risks=risks,
        bottlenecks=bottleneck_summary,
        owner_load=ownership.open_by_owner,
        recommendations=health.recommendations,
    )


def build_dashboard_snapshot(
    store: MemoryStore,
    *,
    now: datetime | None = None,
    title: str = "Organizational Memory Analytics",
) -> DashboardSnapshot:
    """Build a :class:`DashboardSnapshot` summarizing the analytics report."""
    reference = now or utc_now()
    report = generate_report(store, now=reference)

    summary_cards = [
        AnalyticsCard(title="Decisions", value=report.summary["decisions"]),
        AnalyticsCard(title="Commitments", value=report.summary["commitments"]),
        AnalyticsCard(title="Open loops", value=report.summary["open_loops"]),
        AnalyticsCard(title="Overdue", value=report.summary["overdue"]),
    ]
    health_cards = [
        AnalyticsCard(
            title="Health score",
            value=report.key_metrics["memory_health_score"],
            unit="points",
        ),
        AnalyticsCard(title="Grade", value=report.summary["health_grade"]),
        AnalyticsCard(
            title="Closed work ratio",
            value=report.key_metrics["closed_work_ratio"],
            unit="ratio",
        ),
    ]
    dashboard = AnalyticsDashboard(
        title=title,
        sections=[
            AnalyticsSection(name="Summary", cards=summary_cards),
            AnalyticsSection(name="Health", cards=health_cards),
        ],
    )
    return DashboardSnapshot(dashboard=dashboard, generated_at=reference)
