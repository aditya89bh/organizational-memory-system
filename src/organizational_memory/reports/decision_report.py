"""Deterministic decision reports.

Summarizes decisions by status, owner, and meeting, surfaces rationale excerpts,
and flags stale proposed decisions older than a configurable threshold.
"""

from datetime import datetime

from organizational_memory.analytics.common import (
    count_by,
    meeting_or_none,
    owner_or_unassigned,
    status_value,
)
from organizational_memory.models import Decision
from organizational_memory.models.enums import DecisionStatus
from organizational_memory.reports.base import Report, ReportSection, ReportTable
from organizational_memory.storage.store import MemoryStore
from organizational_memory.utils.time import utc_now

DEFAULT_STALE_DAYS = 30.0
DEFAULT_EXCERPT_LENGTH = 120


def _excerpt(text: str, limit: int) -> str:
    collapsed = " ".join(text.split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 1].rstrip() + "…"


def _counts_table(title: str, counts: dict[str, int]) -> ReportTable:
    return ReportTable(
        title=title,
        columns=("key", "count"),
        rows=[(key, str(value)) for key, value in counts.items()],
    )


def decision_report(
    store: MemoryStore,
    *,
    now: datetime | None = None,
    stale_days: float = DEFAULT_STALE_DAYS,
    excerpt_length: int = DEFAULT_EXCERPT_LENGTH,
) -> Report:
    """Build a :class:`Report` summarizing all decisions in the store."""
    generated_at = now or utc_now()
    decisions = [
        r for r in store.list_records("Decision") if isinstance(r, Decision)
    ]

    by_status = count_by(decisions, lambda d: status_value(d.status))
    by_owner = count_by(decisions, owner_or_unassigned)
    by_meeting = count_by(decisions, meeting_or_none)

    rationale_rows: list[tuple[str, ...]] = [
        (d.id, d.title, _excerpt(d.rationale, excerpt_length))
        for d in sorted(decisions, key=lambda d: d.id)
        if d.rationale
    ]

    stale_rows: list[tuple[str, ...]] = []
    for decision in sorted(decisions, key=lambda d: d.id):
        if decision.status is not DecisionStatus.PROPOSED:
            continue
        moment = decision.decided_at or decision.created_at
        age_days = (generated_at - moment).total_seconds() / 86400.0
        if age_days > stale_days:
            stale_rows.append((decision.id, decision.title, f"{round(age_days, 2)}"))

    return Report(
        title="Decision report",
        generated_at=generated_at,
        summary={
            "total": len(decisions),
            "proposed": by_status.get("proposed", 0),
            "accepted": by_status.get("accepted", 0),
            "rejected": by_status.get("rejected", 0),
            "superseded": by_status.get("superseded", 0),
            "stale": len(stale_rows),
        },
        sections=[
            ReportSection(
                title="By status",
                metrics=dict(by_status),
                tables=[_counts_table("Decisions by status", by_status)],
            ),
            ReportSection(
                title="By owner",
                metrics=dict(by_owner),
                tables=[_counts_table("Decisions by owner", by_owner)],
            ),
            ReportSection(
                title="By meeting",
                metrics=dict(by_meeting),
                tables=[_counts_table("Decisions by meeting", by_meeting)],
            ),
            ReportSection(
                title="Rationale excerpts",
                tables=[
                    ReportTable(
                        title="Rationale excerpts",
                        columns=("id", "title", "rationale"),
                        rows=rationale_rows,
                    )
                ],
            ),
            ReportSection(
                title="Stale decisions",
                metrics={"count": len(stale_rows), "stale_days": stale_days},
                tables=[
                    ReportTable(
                        title="Stale proposed decisions",
                        columns=("id", "title", "age_days"),
                        rows=stale_rows,
                    )
                ],
            ),
        ],
    )
