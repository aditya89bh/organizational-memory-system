"""Tests for query/filter support on both concrete stores."""

from collections.abc import Callable
from datetime import timedelta
from pathlib import Path

import pytest

from organizational_memory.models import Decision, Task
from organizational_memory.models.enums import DecisionStatus
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.storage.query import Query
from organizational_memory.storage.sqlite_store import SQLiteStore
from organizational_memory.storage.store import MemoryStore
from organizational_memory.utils.time import utc_now

StoreFactory = Callable[[Path], MemoryStore]


def _json(tmp_path: Path) -> MemoryStore:
    return JSONStore(tmp_path / "memory.json")


def _sqlite(tmp_path: Path) -> MemoryStore:
    return SQLiteStore(tmp_path / "memory.db")


STORES = [pytest.param(_json, id="json"), pytest.param(_sqlite, id="sqlite")]


def _seed(store: MemoryStore) -> None:
    base = utc_now()
    store.save_record(
        Decision(
            id="d1",
            title="Ship beta",
            description="ship the beta",
            owner_id="alice",
            status=DecisionStatus.ACCEPTED,
            source_meeting_id="m1",
            created_at=base,
        )
    )
    store.save_record(
        Decision(
            id="d2",
            title="Revisit pricing",
            description="pricing review",
            owner_id="bob",
            status=DecisionStatus.PROPOSED,
            created_at=base + timedelta(hours=1),
        )
    )
    store.save_record(
        Task(
            id="t1",
            title="Write docs",
            description="documentation",
            owner_id="alice",
            created_at=base + timedelta(hours=2),
        )
    )


@pytest.mark.parametrize("factory", STORES)
def test_filter_by_type(factory: StoreFactory, tmp_path: Path) -> None:
    store = factory(tmp_path)
    _seed(store)
    assert [r.id for r in store.query(Query(record_type="Task"))] == ["t1"]


@pytest.mark.parametrize("factory", STORES)
def test_filter_by_owner(factory: StoreFactory, tmp_path: Path) -> None:
    store = factory(tmp_path)
    _seed(store)
    assert {r.id for r in store.query(Query(owner_id="alice"))} == {"d1", "t1"}


@pytest.mark.parametrize("factory", STORES)
def test_filter_by_status(factory: StoreFactory, tmp_path: Path) -> None:
    store = factory(tmp_path)
    _seed(store)
    assert [r.id for r in store.query(Query(status="accepted"))] == ["d1"]


@pytest.mark.parametrize("factory", STORES)
def test_filter_by_meeting(factory: StoreFactory, tmp_path: Path) -> None:
    store = factory(tmp_path)
    _seed(store)
    assert [r.id for r in store.query(Query(source_meeting_id="m1"))] == ["d1"]


@pytest.mark.parametrize("factory", STORES)
def test_filter_by_text(factory: StoreFactory, tmp_path: Path) -> None:
    store = factory(tmp_path)
    _seed(store)
    assert [r.id for r in store.query(Query(text_contains="pricing"))] == ["d2"]


@pytest.mark.parametrize("factory", STORES)
def test_filter_by_created_window(factory: StoreFactory, tmp_path: Path) -> None:
    store = factory(tmp_path)
    _seed(store)
    first = store.query(Query())[0]
    result = store.query(
        Query(created_after=first.created_at, created_before=first.created_at)
    )
    assert [r.id for r in result] == ["d1"]
