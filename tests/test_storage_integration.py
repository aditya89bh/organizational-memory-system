"""End-to-end integration tests across the storage layer.

These exercise the full persistence surface together: repositories, querying,
updates, deletes, snapshots, backups, and migration-aware restore, against both
concrete stores.
"""

from collections.abc import Callable
from pathlib import Path

import pytest

from organizational_memory.models import (
    Commitment,
    Decision,
    Meeting,
    MemoryEvent,
    OpenLoop,
    Task,
)
from organizational_memory.storage.backup import backup_store, restore_latest
from organizational_memory.storage.commitment_repository import CommitmentRepository
from organizational_memory.storage.decision_repository import DecisionRepository
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.storage.meeting_repository import MeetingRepository
from organizational_memory.storage.query import Query
from organizational_memory.storage.snapshot import create_snapshot, restore_snapshot
from organizational_memory.storage.sqlite_store import SQLiteStore
from organizational_memory.storage.store import MemoryStore
from organizational_memory.utils.time import utc_now

StoreFactory = Callable[[Path], MemoryStore]

STORES = [
    pytest.param(lambda p: JSONStore(p / "memory.json"), id="json"),
    pytest.param(lambda p: SQLiteStore(p / "memory.db"), id="sqlite"),
]


def _populate(store: MemoryStore) -> None:
    now = utc_now()
    MeetingRepository(store).add(
        Meeting(id="m1", title="Kickoff", started_at=now)
    )
    DecisionRepository(store).add(
        Decision(
            id="d1",
            title="Adopt SQLite",
            description="use sqlite for storage",
            owner_id="alice",
            source_meeting_id="m1",
        )
    )
    CommitmentRepository(store).add(
        Commitment(
            id="c1",
            owner_id="bob",
            description="write the spec",
            source_meeting_id="m1",
        )
    )
    store.save_record(
        Task(id="t1", title="Draft API", description="draft", owner_id="alice")
    )
    store.save_record(OpenLoop(id="o1", question="What about auth?", owner_id="bob"))
    store.save_record(
        MemoryEvent(
            id="e1",
            event_type="created",
            entity_type="Decision",
            entity_id="d1",
        )
    )


@pytest.mark.parametrize("factory", STORES)
def test_full_lifecycle(factory: StoreFactory, tmp_path: Path) -> None:
    store = factory(tmp_path)
    _populate(store)

    assert len(store.list_records()) == 6
    assert {r.id for r in store.query(Query(owner_id="alice"))} == {"d1", "t1"}
    assert {r.id for r in store.query(Query(source_meeting_id="m1"))} == {"c1", "d1"}

    decisions = DecisionRepository(store)
    decision = decisions.get("d1")
    assert decision is not None
    decision.title = "Adopt SQLite + JSON"
    decisions.update(decision)
    assert decisions.get("d1").title == "Adopt SQLite + JSON"  # type: ignore[union-attr]

    assert store.delete_record("Task", "t1") is True
    assert store.get_record("Task", "t1") is None
    assert len(store.list_records()) == 5


@pytest.mark.parametrize("factory", STORES)
def test_snapshot_round_trip_into_other_store(
    factory: StoreFactory, tmp_path: Path
) -> None:
    source = factory(tmp_path)
    _populate(source)
    snapshot = create_snapshot(source)

    other = JSONStore(tmp_path / "restored.json")
    written = restore_snapshot(other, snapshot)
    assert written == 6
    assert {r.id for r in other.list_records()} == {
        r.id for r in source.list_records()
    }


@pytest.mark.parametrize("factory", STORES)
def test_backup_and_restore_cycle(factory: StoreFactory, tmp_path: Path) -> None:
    store = factory(tmp_path)
    _populate(store)
    backup_store(store, tmp_path / "backups")

    store.clear()
    assert store.list_records() == []

    restored = restore_latest(store, tmp_path / "backups")
    assert restored == 6
    assert store.get_record("Decision", "d1") is not None
