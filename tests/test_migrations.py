"""Tests for snapshot migrations."""

from pathlib import Path

import pytest

from organizational_memory.storage.json_store import JSONStore
from organizational_memory.storage.migrations import (
    LATEST_VERSION,
    MigrationError,
    migrate_snapshot,
)
from organizational_memory.storage.snapshot import restore_snapshot


def _legacy_snapshot() -> dict[str, object]:
    return {
        "version": 0,
        "data": {
            "Decision": [
                {
                    "id": "d1",
                    "title": "Ship",
                    "description": "ship",
                    "created_at": "2026-01-01T00:00:00Z",
                    "updated_at": "2026-01-01T00:00:00Z",
                    "metadata": {},
                    "status": "proposed",
                    "owner_id": None,
                    "rationale": None,
                    "source_meeting_id": None,
                }
            ]
        },
    }


def test_migrate_upgrades_version() -> None:
    migrated = migrate_snapshot(_legacy_snapshot())
    assert migrated["version"] == LATEST_VERSION
    assert "data" not in migrated
    assert "Decision" in migrated["records"]


def test_migrate_current_is_noop() -> None:
    snapshot = {"version": LATEST_VERSION, "records": {}}
    assert migrate_snapshot(snapshot) == snapshot


def test_migrate_newer_version_raises() -> None:
    with pytest.raises(MigrationError, match="newer than supported"):
        migrate_snapshot({"version": LATEST_VERSION + 1, "records": {}})


def test_migrate_missing_version_raises() -> None:
    with pytest.raises(MigrationError, match="no integer version"):
        migrate_snapshot({"records": {}})


def test_restore_migrates_legacy_snapshot(tmp_path: Path) -> None:
    store = JSONStore(tmp_path / "memory.json")
    written = restore_snapshot(store, _legacy_snapshot())
    assert written == 1
    assert store.get_record("Decision", "d1") is not None
