"""Tests for delete behavior across stores and repositories."""

from collections.abc import Callable
from pathlib import Path

import pytest

from organizational_memory.models import Decision
from organizational_memory.storage.decision_repository import DecisionRepository
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.storage.query import Query
from organizational_memory.storage.sqlite_store import SQLiteStore
from organizational_memory.storage.store import MemoryStore, RecordNotFoundError

StoreFactory = Callable[[Path], MemoryStore]

STORES = [
    pytest.param(lambda p: JSONStore(p / "memory.json"), id="json"),
    pytest.param(lambda p: SQLiteStore(p / "memory.db"), id="sqlite"),
]


@pytest.mark.parametrize("factory", STORES)
def test_delete_record_returns_bool(factory: StoreFactory, tmp_path: Path) -> None:
    store = factory(tmp_path)
    decision = Decision(title="a", description="a")
    store.save_record(decision)
    assert store.delete_record("Decision", decision.id) is True
    assert store.delete_record("Decision", decision.id) is False
    assert store.get_record("Decision", decision.id) is None


@pytest.mark.parametrize("factory", STORES)
def test_remove_missing_raises(factory: StoreFactory, tmp_path: Path) -> None:
    store = factory(tmp_path)
    with pytest.raises(RecordNotFoundError):
        store.remove_record("Decision", "missing")


@pytest.mark.parametrize("factory", STORES)
def test_delete_where(factory: StoreFactory, tmp_path: Path) -> None:
    store = factory(tmp_path)
    store.save_record(Decision(title="a", description="a", owner_id="alice"))
    store.save_record(Decision(title="b", description="b", owner_id="alice"))
    store.save_record(Decision(title="c", description="c", owner_id="bob"))
    removed = store.delete_where(Query(owner_id="alice"))
    assert removed == 2
    assert [r.id for r in store.query(Query())] != []
    assert all(getattr(r, "owner_id", None) == "bob" for r in store.list_records())


def test_repository_remove_missing_raises(tmp_path: Path) -> None:
    repo = DecisionRepository(JSONStore(tmp_path / "memory.json"))
    with pytest.raises(RecordNotFoundError):
        repo.remove("missing")
