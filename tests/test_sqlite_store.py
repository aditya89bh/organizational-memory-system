"""Tests for the SQLite-backed memory store."""

from pathlib import Path

from organizational_memory.models import Commitment, Decision, Task
from organizational_memory.storage.sqlite_store import SQLiteStore


def _db(tmp_path: Path) -> SQLiteStore:
    return SQLiteStore(tmp_path / "memory.db")


def test_save_and_get(tmp_path: Path) -> None:
    store = _db(tmp_path)
    decision = Decision(title="Ship", description="Ship on Friday")
    store.save_record(decision)
    fetched = store.get_record("Decision", decision.id)
    assert fetched is not None
    assert isinstance(fetched, Decision)
    assert fetched.id == decision.id
    assert fetched.title == "Ship"
    store.close()


def test_get_missing_returns_none(tmp_path: Path) -> None:
    store = _db(tmp_path)
    assert store.get_record("Decision", "missing") is None
    store.close()


def test_list_filters_by_type(tmp_path: Path) -> None:
    store = _db(tmp_path)
    store.save_record(Decision(title="a", description="a"))
    store.save_record(Task(title="t", description="d", owner_id="alice"))
    assert len(store.list_records("Decision")) == 1
    assert len(store.list_records()) == 2
    store.close()


def test_replace_existing(tmp_path: Path) -> None:
    store = _db(tmp_path)
    commitment = Commitment(owner_id="alice", description="draft")
    store.save_record(commitment)
    commitment.description = "final"
    store.save_record(commitment)
    fetched = store.get_record("Commitment", commitment.id)
    assert fetched is not None
    assert isinstance(fetched, Commitment)
    assert fetched.description == "final"
    assert len(store.list_records("Commitment")) == 1
    store.close()


def test_delete_and_clear(tmp_path: Path) -> None:
    store = _db(tmp_path)
    decision = Decision(title="a", description="a")
    store.save_record(decision)
    assert store.delete_record("Decision", decision.id) is True
    assert store.delete_record("Decision", decision.id) is False
    store.save_record(decision)
    store.clear()
    assert store.list_records() == []
    store.close()


def test_persists_across_reopen(tmp_path: Path) -> None:
    path = tmp_path / "memory.db"
    first = SQLiteStore(path)
    decision = Decision(title="Persist", description="survive reload")
    first.save_record(decision)
    first.close()

    second = SQLiteStore(path)
    fetched = second.get_record("Decision", decision.id)
    assert fetched is not None
    assert fetched.id == decision.id
    second.close()


def test_context_manager(tmp_path: Path) -> None:
    with SQLiteStore(tmp_path / "memory.db") as store:
        store.save_record(Decision(title="a", description="a"))
        assert len(store.list_records()) == 1
