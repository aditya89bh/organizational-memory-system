"""Composite ranking combining keyword, recency, importance, and ownership.

The composite score is a weighted sum of the individual signals. Weights are
configurable, and every component is retained so the result remains fully
explainable.
"""

from dataclasses import dataclass, field
from datetime import datetime

from organizational_memory.recall.engine import RecallResult
from organizational_memory.recall.ranking.importance import importance_score
from organizational_memory.recall.ranking.ownership import ownership_score
from organizational_memory.recall.ranking.recency import recency_score
from organizational_memory.schemas.base import BaseRecord


@dataclass(frozen=True)
class RankingWeights:
    """Relative weights for each ranking component."""

    keyword: float = 1.0
    recency: float = 0.3
    importance: float = 0.5
    ownership: float = 0.4


@dataclass(frozen=True)
class CompositeScore:
    """A composite score plus its component breakdown."""

    total: float
    components: dict[str, float] = field(default_factory=dict)


DEFAULT_WEIGHTS = RankingWeights()


def composite_score(
    record: BaseRecord,
    *,
    keyword_score: float = 0.0,
    now: datetime | None = None,
    owner: str | None = None,
    weights: RankingWeights = DEFAULT_WEIGHTS,
) -> CompositeScore:
    """Return the weighted composite score and its components for ``record``."""
    components = {
        "keyword": round(keyword_score, 6),
        "recency": recency_score(record, now=now),
        "importance": importance_score(record),
        "ownership": ownership_score(record, owner),
    }
    total = (
        weights.keyword * components["keyword"]
        + weights.recency * components["recency"]
        + weights.importance * components["importance"]
        + weights.ownership * components["ownership"]
    )
    return CompositeScore(total=round(total, 6), components=components)


def rank_composite(
    results: list[RecallResult],
    *,
    now: datetime | None = None,
    owner: str | None = None,
    weights: RankingWeights = DEFAULT_WEIGHTS,
) -> list[RecallResult]:
    """Re-rank ``results`` by composite score, best first.

    Each input result's existing ``score`` is used as the keyword component. The
    returned results carry the composite total as their score and a
    ``ranking`` entry in ``details`` with the component breakdown.
    """
    ranked: list[RecallResult] = []
    for result in results:
        scored = composite_score(
            result.record,
            keyword_score=result.score,
            now=now,
            owner=owner,
            weights=weights,
        )
        details = dict(result.details)
        details["ranking"] = scored.components
        ranked.append(
            RecallResult(
                record=result.record,
                score=scored.total,
                matched_fields=result.matched_fields,
                details=details,
            )
        )
    ranked.sort(key=lambda result: (-result.score, result.record.id))
    return ranked
