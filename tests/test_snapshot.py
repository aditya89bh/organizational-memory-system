"""Tests for store snapshots."""

from pathlib import Path

import pytest

from organizational_memory.models import Decision, Task
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.storage.snapshot import (
    create_snapshot,
    read_snapshot,
    restore_snapshot,
    write_snapshot,
)
from organizational_memory.storage.sqlite_store import SQLiteStore


def _seed(store: JSONStore | SQLiteStore) -> None:
    store.save_record(Decision(id="d1", title="Ship", description="ship"))
    store.save_record(Task(id="t1", title="Docs", description="docs", owner_id="alice"))


def test_snapshot_records_are_deterministic(tmp_path: Path) -> None:
    store = JSONStore(tmp_path / "memory.json")
    _seed(store)
    assert create_snapshot(store)["records"] == create_snapshot(store)["records"]


def test_snapshot_roundtrip_across_stores(tmp_path: Path) -> None:
    source = SQLiteStore(tmp_path / "memory.db")
    _seed(source)
    snapshot = create_snapshot(source)

    target = JSONStore(tmp_path / "memory.json")
    written = restore_snapshot(target, snapshot)

    assert written == 2
    assert target.get_record("Decision", "d1") is not None
    assert target.get_record("Task", "t1") is not None


def test_restore_replaces_by_default(tmp_path: Path) -> None:
    store = JSONStore(tmp_path / "memory.json")
    _seed(store)
    snapshot = create_snapshot(store)
    store.save_record(Decision(id="extra", title="x", description="x"))

    restore_snapshot(store, snapshot)
    assert store.get_record("Decision", "extra") is None


def test_restore_merge_keeps_existing(tmp_path: Path) -> None:
    store = JSONStore(tmp_path / "memory.json")
    _seed(store)
    snapshot = create_snapshot(store)
    store.save_record(Decision(id="extra", title="x", description="x"))

    restore_snapshot(store, snapshot, replace=False)
    assert store.get_record("Decision", "extra") is not None


def test_write_and_read_snapshot(tmp_path: Path) -> None:
    store = JSONStore(tmp_path / "memory.json")
    _seed(store)
    path = tmp_path / "snap" / "snapshot.json"
    write_snapshot(store, path)

    loaded = read_snapshot(path)
    assert loaded["version"] == 1
    assert set(loaded["records"]) == {"Decision", "Task"}


def test_unsupported_version_raises(tmp_path: Path) -> None:
    store = JSONStore(tmp_path / "memory.json")
    with pytest.raises(ValueError, match="snapshot version"):
        restore_snapshot(store, {"version": 99, "records": {}})
