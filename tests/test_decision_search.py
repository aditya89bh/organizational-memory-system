"""Tests for decision search."""

from pathlib import Path

from organizational_memory.models import Decision
from organizational_memory.models.enums import DecisionStatus
from organizational_memory.recall.decision_search import search_decisions
from organizational_memory.storage.json_store import JSONStore


def _store(tmp_path: Path) -> JSONStore:
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(
        Decision(
            id="d1",
            title="Adopt Kubernetes",
            description="run services on kubernetes",
            owner_id="alice",
            status=DecisionStatus.ACCEPTED,
            source_meeting_id="m1",
            rationale="scales better",
        )
    )
    store.save_record(
        Decision(
            id="d2",
            title="Pricing model",
            description="revisit pricing tiers",
            owner_id="bob",
            status=DecisionStatus.PROPOSED,
            source_meeting_id="m2",
        )
    )
    return store


def test_search_by_text(tmp_path: Path) -> None:
    results = search_decisions(_store(tmp_path), text="kubernetes")
    assert [r.record.id for r in results] == ["d1"]


def test_search_by_owner(tmp_path: Path) -> None:
    results = search_decisions(_store(tmp_path), owner_id="bob")
    assert [r.record.id for r in results] == ["d2"]


def test_search_by_status(tmp_path: Path) -> None:
    results = search_decisions(_store(tmp_path), status=DecisionStatus.ACCEPTED)
    assert [r.record.id for r in results] == ["d1"]
    results_str = search_decisions(_store(tmp_path), status="accepted")
    assert [r.record.id for r in results_str] == ["d1"]


def test_search_by_meeting(tmp_path: Path) -> None:
    results = search_decisions(_store(tmp_path), source_meeting_id="m2")
    assert [r.record.id for r in results] == ["d2"]


def test_search_by_rationale_text(tmp_path: Path) -> None:
    results = search_decisions(_store(tmp_path), text="scales")
    assert [r.record.id for r in results] == ["d1"]


def test_combined_filters(tmp_path: Path) -> None:
    results = search_decisions(
        _store(tmp_path), text="pricing", owner_id="bob", status="proposed"
    )
    assert [r.record.id for r in results] == ["d2"]
    assert search_decisions(_store(tmp_path), text="pricing", owner_id="alice") == []


def test_no_filters_returns_all(tmp_path: Path) -> None:
    results = search_decisions(_store(tmp_path))
    assert [r.record.id for r in results] == ["d1", "d2"]
