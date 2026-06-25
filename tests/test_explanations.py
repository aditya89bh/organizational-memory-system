"""Tests for the explanation engine."""

from organizational_memory.models import Decision
from organizational_memory.recall.engine import RecallResult
from organizational_memory.recall.explanations import (
    explain_result,
    explain_results,
)


def _result() -> RecallResult:
    return RecallResult(
        record=Decision(id="d1", title="Adopt SQLite", description="x"),
        score=1.5,
        matched_fields=("title",),
        details={
            "matched_tokens": ["adopt", "sqlite"],
            "phrase_match": True,
            "ranking": {"keyword": 1.5, "recency": 0.0, "importance": 0.6},
        },
    )


def test_explanation_core_fields() -> None:
    explanation = explain_result(_result())
    assert explanation.record_id == "d1"
    assert explanation.record_type == "Decision"
    assert explanation.score == 1.5
    assert explanation.matched_fields == ("title",)
    assert explanation.matched_tokens == ("adopt", "sqlite")
    assert explanation.phrase_match is True


def test_explanation_reasons() -> None:
    explanation = explain_result(_result())
    joined = " | ".join(explanation.reasons)
    assert "matched fields: title" in joined
    assert "matched tokens: adopt, sqlite" in joined
    assert "exact phrase" in joined
    assert "keyword score contributed 1.5" in joined
    assert "recency score contributed" not in joined  # zero is omitted


def test_explanation_minimal_result() -> None:
    result = RecallResult(record=Decision(id="d2", title="x", description="y"))
    explanation = explain_result(result)
    assert explanation.reasons == ()
    assert explanation.ranking == {}


def test_explain_results_preserves_order() -> None:
    results = [
        _result(),
        RecallResult(record=Decision(id="d3", title="x", description="y")),
    ]
    explanations = explain_results(results)
    assert [e.record_id for e in explanations] == ["d1", "d3"]
