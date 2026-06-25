"""Filesystem backups built on top of store snapshots.

Each backup is a timestamped snapshot file written to a backup directory. The
helpers here create, list, prune, and restore those files, giving a simple
rotation scheme without any external dependencies.
"""

from datetime import UTC, datetime
from pathlib import Path

from organizational_memory.storage.snapshot import (
    read_snapshot,
    restore_snapshot,
    write_snapshot,
)
from organizational_memory.storage.store import MemoryStore

BACKUP_PREFIX = "snapshot-"
BACKUP_SUFFIX = ".json"


def _timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%S%f")


def backup_store(store: MemoryStore, backup_dir: Path) -> Path:
    """Write a timestamped snapshot of ``store`` into ``backup_dir``."""
    backup_dir.mkdir(parents=True, exist_ok=True)
    path = backup_dir / f"{BACKUP_PREFIX}{_timestamp()}{BACKUP_SUFFIX}"
    write_snapshot(store, path)
    return path


def list_backups(backup_dir: Path) -> list[Path]:
    """Return backup files in ``backup_dir`` sorted oldest to newest."""
    if not backup_dir.is_dir():
        return []
    matches = backup_dir.glob(f"{BACKUP_PREFIX}*{BACKUP_SUFFIX}")
    return sorted(matches, key=lambda path: path.name)


def latest_backup(backup_dir: Path) -> Path | None:
    """Return the most recent backup file, or ``None`` if there are none."""
    backups = list_backups(backup_dir)
    return backups[-1] if backups else None


def restore_latest(
    store: MemoryStore, backup_dir: Path, *, replace: bool = True
) -> int:
    """Restore the newest backup into ``store`` and return records written."""
    newest = latest_backup(backup_dir)
    if newest is None:
        raise FileNotFoundError(f"no backups found in {backup_dir}")
    return restore_snapshot(store, read_snapshot(newest), replace=replace)


def prune_backups(backup_dir: Path, keep: int) -> list[Path]:
    """Keep the ``keep`` newest backups, deleting older ones.

    Returns the list of removed paths.
    """
    if keep < 0:
        raise ValueError("keep must be non-negative")
    backups = list_backups(backup_dir)
    if len(backups) <= keep:
        return []
    stale = backups[: len(backups) - keep]
    for path in stale:
        path.unlink()
    return stale


__all__ = [
    "backup_store",
    "latest_backup",
    "list_backups",
    "prune_backups",
    "restore_latest",
]
