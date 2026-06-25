"""Tests for participant search."""

from pathlib import Path

from organizational_memory.models import Participant
from organizational_memory.recall.participant_search import search_participants
from organizational_memory.storage.json_store import JSONStore


def _store(tmp_path: Path) -> JSONStore:
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(
        Participant(
            id="p1",
            name="Alice Smith",
            email="alice@example.com",
            role="Engineer",
            organization="Acme",
        )
    )
    store.save_record(
        Participant(
            id="p2",
            name="Bob Jones",
            email="bob@example.com",
            role="Manager",
            organization="Globex",
        )
    )
    return store


def test_search_by_text(tmp_path: Path) -> None:
    results = search_participants(_store(tmp_path), text="alice")
    assert [r.record.id for r in results] == ["p1"]


def test_search_by_name(tmp_path: Path) -> None:
    results = search_participants(_store(tmp_path), name="bob jones")
    assert [r.record.id for r in results] == ["p2"]


def test_search_by_email(tmp_path: Path) -> None:
    results = search_participants(_store(tmp_path), email="alice@example.com")
    assert [r.record.id for r in results] == ["p1"]


def test_search_by_role(tmp_path: Path) -> None:
    results = search_participants(_store(tmp_path), role="manager")
    assert [r.record.id for r in results] == ["p2"]


def test_search_by_organization(tmp_path: Path) -> None:
    results = search_participants(_store(tmp_path), organization="Acme")
    assert [r.record.id for r in results] == ["p1"]


def test_no_filters_returns_all(tmp_path: Path) -> None:
    assert [r.record.id for r in search_participants(_store(tmp_path))] == ["p1", "p2"]
