"""Tests for the recall engine interface."""

from organizational_memory.models import Decision
from organizational_memory.recall.engine import RecallEngine, RecallResult
from organizational_memory.schemas.base import BaseRecord


class FakeRecallEngine(RecallEngine):
    """Minimal in-memory engine used to exercise the interface."""

    def __init__(self, records: list[BaseRecord]) -> None:
        self._records = records

    def search(self, query: str) -> list[RecallResult]:
        results = [
            RecallResult(record=record, score=1.0, matched_fields=("title",))
            for record in self._records
            if query.lower() in getattr(record, "title", "").lower()
        ]
        return results

    def recall_by_id(self, record_type: str, record_id: str) -> BaseRecord | None:
        for record in self._records:
            if type(record).__name__ == record_type and record.id == record_id:
                return record
        return None

    def explain(self, query: str) -> list[RecallResult]:
        return [
            RecallResult(
                record=result.record,
                score=result.score,
                matched_fields=result.matched_fields,
                details={"query": query},
            )
            for result in self.search(query)
        ]


def _engine() -> FakeRecallEngine:
    return FakeRecallEngine(
        [
            Decision(id="d1", title="Adopt SQLite", description="use sqlite"),
            Decision(id="d2", title="Revisit pricing", description="pricing"),
        ]
    )


def test_search_returns_results() -> None:
    results = _engine().search("sqlite")
    assert [r.record.id for r in results] == ["d1"]
    assert results[0].score == 1.0
    assert results[0].matched_fields == ("title",)


def test_search_no_match() -> None:
    assert _engine().search("nonexistent") == []


def test_recall_by_id() -> None:
    engine = _engine()
    found = engine.recall_by_id("Decision", "d2")
    assert found is not None
    assert found.id == "d2"
    assert engine.recall_by_id("Decision", "missing") is None


def test_explain_attaches_details() -> None:
    results = _engine().explain("pricing")
    assert results[0].details == {"query": "pricing"}


def test_result_is_frozen() -> None:
    result = RecallResult(record=Decision(title="x", description="y"))
    assert result.score == 0.0
    assert result.matched_fields == ()
