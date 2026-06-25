"""Human-readable explanations for recall results.

An :class:`Explanation` turns the structured ``details`` carried by a
:class:`RecallResult` into an inspectable record of why it matched and how it was
scored. Explanations are derived deterministically from the result itself.
"""

from dataclasses import dataclass, field

from organizational_memory.recall.engine import RecallResult


@dataclass(frozen=True)
class Explanation:
    """Why a record matched a query and how it was scored."""

    record_id: str
    record_type: str
    score: float
    matched_fields: tuple[str, ...] = ()
    matched_tokens: tuple[str, ...] = ()
    phrase_match: bool = False
    ranking: dict[str, float] = field(default_factory=dict)
    reasons: tuple[str, ...] = ()


def _build_reasons(
    matched_fields: tuple[str, ...],
    matched_tokens: tuple[str, ...],
    phrase_match: bool,
    ranking: dict[str, float],
) -> tuple[str, ...]:
    reasons: list[str] = []
    if matched_fields:
        reasons.append(f"matched fields: {', '.join(matched_fields)}")
    if matched_tokens:
        reasons.append(f"matched tokens: {', '.join(matched_tokens)}")
    if phrase_match:
        reasons.append("matched the query as an exact phrase")
    for component, value in sorted(ranking.items()):
        if value > 0:
            reasons.append(f"{component} score contributed {value}")
    return tuple(reasons)


def explain_result(result: RecallResult) -> Explanation:
    """Return an :class:`Explanation` derived from ``result``."""
    details = result.details
    matched_tokens = tuple(details.get("matched_tokens", ()))
    phrase_match = bool(details.get("phrase_match", False))
    raw_ranking = details.get("ranking", {})
    ranking = dict(raw_ranking) if isinstance(raw_ranking, dict) else {}

    return Explanation(
        record_id=result.record.id,
        record_type=type(result.record).__name__,
        score=result.score,
        matched_fields=result.matched_fields,
        matched_tokens=matched_tokens,
        phrase_match=phrase_match,
        ranking=ranking,
        reasons=_build_reasons(
            result.matched_fields, matched_tokens, phrase_match, ranking
        ),
    )


def explain_results(results: list[RecallResult]) -> list[Explanation]:
    """Return explanations for every result, preserving order."""
    return [explain_result(result) for result in results]
