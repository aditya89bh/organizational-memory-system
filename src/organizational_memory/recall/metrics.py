"""Deterministic evaluation metrics for recall quality.

Metrics are computed over a set of :class:`QueryOutcome` values, each pairing the
expected (relevant) record ids with the ids actually returned, in rank order.
All metrics are simple, explainable, and offline.
"""

from dataclasses import dataclass

DEFAULT_K = 3


@dataclass(frozen=True)
class QueryOutcome:
    """Expected vs. returned ids for a single evaluated query."""

    expected_ids: tuple[str, ...]
    returned_ids: tuple[str, ...]


@dataclass(frozen=True)
class RecallMetrics:
    """Aggregate recall metrics over a set of query outcomes."""

    hit_rate: float
    top_k_hit_rate: float
    mean_reciprocal_rank: float
    zero_result_rate: float
    average_result_count: float
    k: int


def hit_rate(outcomes: list[QueryOutcome]) -> float:
    """Return the mean fraction of expected ids found anywhere in results."""
    if not outcomes:
        return 0.0
    total = 0.0
    for outcome in outcomes:
        if not outcome.expected_ids:
            total += 1.0
            continue
        returned = set(outcome.returned_ids)
        found = sum(1 for rid in outcome.expected_ids if rid in returned)
        total += found / len(outcome.expected_ids)
    return total / len(outcomes)


def top_k_hit_rate(outcomes: list[QueryOutcome], k: int = DEFAULT_K) -> float:
    """Return the fraction of queries with an expected id in the top ``k``."""
    if not outcomes:
        return 0.0
    hits = 0
    for outcome in outcomes:
        top = set(outcome.returned_ids[:k])
        if any(rid in top for rid in outcome.expected_ids):
            hits += 1
    return hits / len(outcomes)


def mean_reciprocal_rank(outcomes: list[QueryOutcome]) -> float:
    """Return the mean reciprocal rank of the first relevant result."""
    if not outcomes:
        return 0.0
    total = 0.0
    for outcome in outcomes:
        expected = set(outcome.expected_ids)
        for index, rid in enumerate(outcome.returned_ids, start=1):
            if rid in expected:
                total += 1.0 / index
                break
    return total / len(outcomes)


def zero_result_rate(outcomes: list[QueryOutcome]) -> float:
    """Return the fraction of queries that returned no results."""
    if not outcomes:
        return 0.0
    empty = sum(1 for outcome in outcomes if not outcome.returned_ids)
    return empty / len(outcomes)


def average_result_count(outcomes: list[QueryOutcome]) -> float:
    """Return the mean number of results returned per query."""
    if not outcomes:
        return 0.0
    return sum(len(outcome.returned_ids) for outcome in outcomes) / len(outcomes)


def compute_metrics(
    outcomes: list[QueryOutcome], k: int = DEFAULT_K
) -> RecallMetrics:
    """Compute all recall metrics over ``outcomes``."""
    return RecallMetrics(
        hit_rate=round(hit_rate(outcomes), 6),
        top_k_hit_rate=round(top_k_hit_rate(outcomes, k), 6),
        mean_reciprocal_rank=round(mean_reciprocal_rank(outcomes), 6),
        zero_result_rate=round(zero_result_rate(outcomes), 6),
        average_result_count=round(average_result_count(outcomes), 6),
        k=k,
    )
