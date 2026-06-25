"""Tests for filesystem backup utilities."""

from pathlib import Path

import pytest

from organizational_memory.models import Decision
from organizational_memory.storage.backup import (
    backup_store,
    latest_backup,
    list_backups,
    prune_backups,
    restore_latest,
)
from organizational_memory.storage.json_store import JSONStore


def _store(tmp_path: Path) -> JSONStore:
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(Decision(id="d1", title="Ship", description="ship"))
    return store


def test_backup_creates_file(tmp_path: Path) -> None:
    store = _store(tmp_path)
    backup = backup_store(store, tmp_path / "backups")
    assert backup.exists()
    assert backup.name.startswith("snapshot-")


def test_list_and_latest(tmp_path: Path) -> None:
    store = _store(tmp_path)
    first = backup_store(store, tmp_path / "backups")
    second = backup_store(store, tmp_path / "backups")
    backups = list_backups(tmp_path / "backups")
    assert backups == sorted([first, second], key=lambda p: p.name)
    assert latest_backup(tmp_path / "backups") == backups[-1]


def test_restore_latest(tmp_path: Path) -> None:
    store = _store(tmp_path)
    backup_store(store, tmp_path / "backups")
    store.save_record(Decision(id="d2", title="Extra", description="extra"))

    written = restore_latest(store, tmp_path / "backups")
    assert written == 1
    assert store.get_record("Decision", "d2") is None
    assert store.get_record("Decision", "d1") is not None


def test_restore_latest_without_backups_raises(tmp_path: Path) -> None:
    store = _store(tmp_path)
    with pytest.raises(FileNotFoundError):
        restore_latest(store, tmp_path / "empty")


def test_prune_keeps_newest(tmp_path: Path) -> None:
    store = _store(tmp_path)
    backups = [backup_store(store, tmp_path / "backups") for _ in range(4)]
    removed = prune_backups(tmp_path / "backups", keep=2)
    remaining = list_backups(tmp_path / "backups")

    assert len(remaining) == 2
    assert remaining == backups[-2:]
    assert set(removed) == set(backups[:2])


def test_list_backups_missing_dir(tmp_path: Path) -> None:
    assert list_backups(tmp_path / "nope") == []
    assert latest_backup(tmp_path / "nope") is None
