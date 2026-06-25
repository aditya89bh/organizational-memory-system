"""Tests for relationship search."""

from organizational_memory.models import EntityRef, EntityRelationship, RelationshipType
from organizational_memory.recall.relationship_search import search_relationships


def _relationships() -> list[EntityRelationship]:
    return [
        EntityRelationship(
            id="r1",
            source=EntityRef(entity_type="decision", entity_id="d1"),
            target=EntityRef(entity_type="task", entity_id="t1"),
            relationship_type=RelationshipType.DECISION_TO_TASK,
        ),
        EntityRelationship(
            id="r2",
            source=EntityRef(entity_type="risk", entity_id="rk1"),
            target=EntityRef(entity_type="decision", entity_id="d1"),
            relationship_type=RelationshipType.RISK_AFFECTS_DECISION,
        ),
    ]


def test_search_by_source() -> None:
    results = search_relationships(_relationships(), source_id="d1")
    assert [r.record.id for r in results] == ["r1"]


def test_search_by_target_type() -> None:
    results = search_relationships(_relationships(), target_type="decision")
    assert [r.record.id for r in results] == ["r2"]


def test_search_by_relationship_type() -> None:
    results = search_relationships(
        _relationships(), relationship_type=RelationshipType.DECISION_TO_TASK
    )
    assert [r.record.id for r in results] == ["r1"]
    results_str = search_relationships(
        _relationships(), relationship_type="risk_affects_decision"
    )
    assert [r.record.id for r in results_str] == ["r2"]


def test_search_by_related_id_matches_either_endpoint() -> None:
    results = search_relationships(_relationships(), related_id="d1")
    assert {r.record.id for r in results} == {"r1", "r2"}


def test_details_populated() -> None:
    results = search_relationships(_relationships(), source_id="d1")
    assert results[0].details["source"] == "decision:d1"
    assert results[0].details["target"] == "task:t1"
    assert results[0].details["relationship_type"] == "decision_to_task"


def test_no_filters_returns_all_sorted() -> None:
    results = search_relationships(_relationships())
    assert [r.record.id for r in results] == ["r1", "r2"]
