"""Lightweight, deterministic migrations for snapshot payloads.

Snapshots carry a ``version`` field. As the on-disk shape evolves, register a
:class:`Migration` describing how to upgrade a payload from one version to the
next. :func:`migrate_snapshot` chains the registered steps to bring any older
snapshot up to :data:`LATEST_VERSION`.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from organizational_memory.exceptions import StorageError
from organizational_memory.storage.snapshot import SNAPSHOT_VERSION

LATEST_VERSION = SNAPSHOT_VERSION


class MigrationError(StorageError):
    """Raised when a snapshot cannot be migrated to the latest version."""


@dataclass(frozen=True)
class Migration:
    """An upgrade step from one snapshot version to the next."""

    from_version: int
    to_version: int
    description: str
    upgrade: Callable[[dict[str, Any]], dict[str, Any]]


def _upgrade_0_to_1(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Version 0 stored records under ``data``; version 1 uses ``records``."""
    records = snapshot.get("records", snapshot.get("data", {}))
    upgraded = {key: value for key, value in snapshot.items() if key != "data"}
    upgraded["records"] = records
    upgraded["version"] = 1
    return upgraded


MIGRATIONS: list[Migration] = [
    Migration(0, 1, "move records out of the legacy 'data' key", _upgrade_0_to_1),
]


def _find_step(version: int) -> Migration | None:
    for migration in MIGRATIONS:
        if migration.from_version == version:
            return migration
    return None


def migrate_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Return ``snapshot`` upgraded to :data:`LATEST_VERSION`.

    Raises:
        MigrationError: If the version is missing, newer than supported, or no
            migration path exists.
    """
    version = snapshot.get("version")
    if not isinstance(version, int):
        raise MigrationError(f"snapshot has no integer version: {version!r}")
    if version > LATEST_VERSION:
        raise MigrationError(
            f"snapshot version {version} is newer than supported {LATEST_VERSION}"
        )

    current = dict(snapshot)
    while current["version"] < LATEST_VERSION:
        version = current["version"]
        step = _find_step(version)
        if step is None:
            raise MigrationError(f"no migration registered from version {version}")
        current = step.upgrade(current)
        current["version"] = step.to_version
    return current
