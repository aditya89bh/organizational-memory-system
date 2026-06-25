"""Tests for update behavior across stores and repositories."""

from collections.abc import Callable
from datetime import timedelta
from pathlib import Path

import pytest

from organizational_memory.models import Decision
from organizational_memory.storage.decision_repository import DecisionRepository
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.storage.sqlite_store import SQLiteStore
from organizational_memory.storage.store import MemoryStore, RecordNotFoundError

StoreFactory = Callable[[Path], MemoryStore]

STORES = [
    pytest.param(lambda p: JSONStore(p / "memory.json"), id="json"),
    pytest.param(lambda p: SQLiteStore(p / "memory.db"), id="sqlite"),
]


@pytest.mark.parametrize("factory", STORES)
def test_update_existing(factory: StoreFactory, tmp_path: Path) -> None:
    store = factory(tmp_path)
    decision = Decision(title="a", description="a")
    store.save_record(decision)
    decision.title = "updated"
    store.update_record(decision)
    fetched = store.get_record("Decision", decision.id)
    assert isinstance(fetched, Decision)
    assert fetched.title == "updated"
    assert fetched.id == decision.id


@pytest.mark.parametrize("factory", STORES)
def test_update_missing_raises(factory: StoreFactory, tmp_path: Path) -> None:
    store = factory(tmp_path)
    with pytest.raises(RecordNotFoundError):
        store.update_record(Decision(title="a", description="a"))


@pytest.mark.parametrize("factory", STORES)
def test_update_touches_updated_at(factory: StoreFactory, tmp_path: Path) -> None:
    store = factory(tmp_path)
    decision = Decision(title="a", description="a")
    store.save_record(decision)
    decision.updated_at = decision.created_at - timedelta(days=1)
    store.save_record(decision)
    store.update_record(decision)
    fetched = store.get_record("Decision", decision.id)
    assert fetched is not None
    assert fetched.updated_at > decision.created_at - timedelta(days=1)


def test_repository_update_missing_raises(tmp_path: Path) -> None:
    repo = DecisionRepository(JSONStore(tmp_path / "memory.json"))
    with pytest.raises(RecordNotFoundError):
        repo.update(Decision(title="a", description="a"))
