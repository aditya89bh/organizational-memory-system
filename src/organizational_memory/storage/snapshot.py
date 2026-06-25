"""Point-in-time snapshots of a memory store.

A snapshot is a self-contained, JSON-serializable description of every record in
a store. It can be written to disk and later restored into any concrete store,
making it useful for exports, fixtures, and store-to-store migration.
"""

import json
from pathlib import Path
from typing import Any

from organizational_memory.schemas.base import BaseRecord
from organizational_memory.storage.store import (
    MemoryStore,
    decode_record,
    encode_record,
)
from organizational_memory.utils.time import format_timestamp, utc_now

SNAPSHOT_VERSION = 1


def create_snapshot(store: MemoryStore) -> dict[str, Any]:
    """Return a deterministic, JSON-serializable snapshot of ``store``."""
    records: dict[str, list[dict[str, Any]]] = {}
    for record in store.list_records():
        type_name, _, payload = encode_record(record)
        records.setdefault(type_name, []).append(payload)

    ordered = {
        type_name: sorted(payloads, key=lambda payload: str(payload.get("id", "")))
        for type_name, payloads in sorted(records.items())
    }
    return {
        "version": SNAPSHOT_VERSION,
        "created_at": format_timestamp(utc_now()),
        "records": ordered,
    }


def restore_snapshot(
    store: MemoryStore,
    snapshot: dict[str, Any],
    *,
    replace: bool = True,
    migrate: bool = True,
) -> int:
    """Load ``snapshot`` into ``store`` and return the number of records written.

    When ``replace`` is true the store is cleared first, so it ends up holding
    exactly the snapshot's contents. When ``migrate`` is true, older snapshots
    are upgraded to the current version before loading.
    """
    if migrate and snapshot.get("version") != SNAPSHOT_VERSION:
        from organizational_memory.storage.migrations import migrate_snapshot

        snapshot = migrate_snapshot(snapshot)

    version = snapshot.get("version")
    if version != SNAPSHOT_VERSION:
        raise ValueError(f"unsupported snapshot version: {version!r}")

    if replace:
        store.clear()

    written = 0
    records: dict[str, list[dict[str, Any]]] = snapshot.get("records", {})
    for type_name, payloads in records.items():
        for payload in payloads:
            record: BaseRecord = decode_record(type_name, payload)
            store.save_record(record)
            written += 1
    return written


def write_snapshot(store: MemoryStore, path: Path) -> dict[str, Any]:
    """Create a snapshot of ``store`` and write it to ``path`` as JSON."""
    snapshot = create_snapshot(store)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(snapshot, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return snapshot


def read_snapshot(path: Path) -> dict[str, Any]:
    """Read and return the snapshot stored at ``path``."""
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data
