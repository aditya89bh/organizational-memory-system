"""Memory health score.

Combines several deterministic signals into a single 0-100 health score with a
letter grade, per-component breakdown, and actionable recommendations. Each
component is expressed as a 0-1 sub-score where 1 is healthy; the overall score
is a fixed weighted average.
"""

from dataclasses import dataclass, field
from datetime import datetime

from organizational_memory.analytics.common import is_open_status, is_overdue
from organizational_memory.analytics.repeated_discussions import repeated_discussions
from organizational_memory.models import Decision, OpenLoop
from organizational_memory.models.enums import DecisionStatus, OpenLoopStatus
from organizational_memory.schemas.base import BaseRecord
from organizational_memory.storage.store import MemoryStore
from organizational_memory.utils.time import utc_now

DEFAULT_STALE_DECISION_DAYS = 30.0
WORK_TYPES = ("Task", "Commitment", "OpenLoop", "ActionItem")

_WEIGHTS = {
    "open_loop_resolution": 0.20,
    "overdue_work": 0.25,
    "ownership_coverage": 0.20,
    "decision_freshness": 0.15,
    "discussion_focus": 0.10,
    "metadata_completeness": 0.10,
}

_RECOMMENDATIONS = {
    "open_loop_resolution": "Resolve outstanding open loops to reduce unresolved load.",
    "overdue_work": "Address overdue work items or renegotiate their due dates.",
    "ownership_coverage": "Assign owners to unowned work items.",
    "decision_freshness": "Revisit stale proposed decisions and finalize them.",
    "discussion_focus": "Close recurring unresolved questions to avoid rehashing.",
    "metadata_completeness": "Enrich records with metadata for better traceability.",
}

_HEALTHY_THRESHOLD = 0.7


@dataclass(frozen=True)
class HealthComponent:
    """A single weighted contributor to the memory health score."""

    name: str
    score: float
    weight: float
    detail: str


@dataclass(frozen=True)
class MemoryHealthReport:
    """Overall memory health score, grade, components, and recommendations."""

    score: float
    grade: str
    components: list[HealthComponent] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


def _ratio(part: int, whole: int) -> float:
    return part / whole if whole else 0.0


def _grade(score: float) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def memory_health(
    store: MemoryStore,
    *,
    now: datetime | None = None,
    stale_decision_days: float = DEFAULT_STALE_DECISION_DAYS,
) -> MemoryHealthReport:
    """Compute :class:`MemoryHealthReport` from stored records."""
    reference = now or utc_now()
    all_records = store.list_records()

    loops = [r for r in store.list_records("OpenLoop") if isinstance(r, OpenLoop)]
    unresolved = sum(1 for loop in loops if loop.status is OpenLoopStatus.OPEN)

    work: list[BaseRecord] = []
    for type_name in WORK_TYPES:
        work.extend(store.list_records(type_name))
    overdue = sum(1 for r in work if is_overdue(r, reference))
    open_work = [r for r in work if is_open_status(getattr(r, "status", "open"))]
    unowned = sum(1 for r in open_work if not getattr(r, "owner_id", None))

    decisions = [r for r in store.list_records("Decision") if isinstance(r, Decision)]
    stale = sum(
        1
        for d in decisions
        if d.status is DecisionStatus.PROPOSED
        and (reference - d.created_at).total_seconds() / 86400.0 > stale_decision_days
    )

    recurring = sum(
        cluster.occurrences
        for cluster in repeated_discussions(store).open_loop_clusters
    )
    missing_metadata = sum(
        1 for r in all_records if not getattr(r, "metadata", {})
    )

    raw = {
        "open_loop_resolution": (
            1.0 - _ratio(unresolved, len(loops)),
            f"{unresolved}/{len(loops)} open loops unresolved",
        ),
        "overdue_work": (
            1.0 - _ratio(overdue, len(work)),
            f"{overdue}/{len(work)} work items overdue",
        ),
        "ownership_coverage": (
            1.0 - _ratio(unowned, len(open_work)),
            f"{unowned}/{len(open_work)} open work items unowned",
        ),
        "decision_freshness": (
            1.0 - _ratio(stale, len(decisions)),
            f"{stale}/{len(decisions)} decisions stale",
        ),
        "discussion_focus": (
            1.0 - min(1.0, _ratio(recurring, len(loops))),
            f"{recurring} recurring unresolved occurrences",
        ),
        "metadata_completeness": (
            1.0 - _ratio(missing_metadata, len(all_records)),
            f"{missing_metadata}/{len(all_records)} records missing metadata",
        ),
    }

    components = [
        HealthComponent(
            name=name,
            score=round(score, 6),
            weight=_WEIGHTS[name],
            detail=detail,
        )
        for name, (score, detail) in raw.items()
    ]
    overall = round(
        100.0 * sum(c.score * c.weight for c in components), 2
    )
    recommendations = [
        _RECOMMENDATIONS[c.name]
        for c in components
        if c.score < _HEALTHY_THRESHOLD
    ]

    return MemoryHealthReport(
        score=overall,
        grade=_grade(overall),
        components=components,
        recommendations=recommendations,
    )
