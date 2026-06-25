"""SQLite-backed implementation of :class:`MemoryStore`.

Records are stored one row per record, with the JSON payload kept verbatim in a
``payload`` column and the type, id, and timestamps mirrored into dedicated
columns for inspection and filtering.
"""

import json
import sqlite3
from pathlib import Path
from types import TracebackType
from typing import Any

from organizational_memory.schemas.base import BaseRecord
from organizational_memory.storage.store import (
    MemoryStore,
    decode_record,
    encode_record,
)

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS records (
    type TEXT NOT NULL,
    id TEXT NOT NULL,
    created_at TEXT,
    updated_at TEXT,
    payload TEXT NOT NULL,
    PRIMARY KEY (type, id)
)
"""


class SQLiteStore(MemoryStore):
    """A :class:`MemoryStore` backed by a local SQLite database file."""

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        self._connection = sqlite3.connect(self.path)
        self._connection.execute(_CREATE_TABLE)
        self._connection.commit()

    def close(self) -> None:
        """Close the underlying database connection."""
        self._connection.close()

    def __enter__(self) -> "SQLiteStore":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def _write(self, record: BaseRecord) -> None:
        type_name, record_id, payload = encode_record(record)
        self._connection.execute(
            "INSERT OR REPLACE INTO records "
            "(type, id, created_at, updated_at, payload) VALUES (?, ?, ?, ?, ?)",
            (
                type_name,
                record_id,
                _as_text(payload.get("created_at")),
                _as_text(payload.get("updated_at")),
                json.dumps(payload, sort_keys=True),
            ),
        )
        self._connection.commit()

    def save_record(self, record: BaseRecord) -> None:
        self._write(record)

    def get_record(self, record_type: str, record_id: str) -> BaseRecord | None:
        cursor = self._connection.execute(
            "SELECT type, payload FROM records WHERE type = ? AND id = ?",
            (record_type, record_id),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return _row_to_record(row)

    def list_records(self, record_type: str | None = None) -> list[BaseRecord]:
        if record_type is None:
            cursor = self._connection.execute(
                "SELECT type, payload FROM records ORDER BY type, id"
            )
        else:
            cursor = self._connection.execute(
                "SELECT type, payload FROM records WHERE type = ? ORDER BY id",
                (record_type,),
            )
        return [_row_to_record(row) for row in cursor.fetchall()]

    def update_record(self, record: BaseRecord) -> None:
        self._write(record)

    def delete_record(self, record_type: str, record_id: str) -> bool:
        cursor = self._connection.execute(
            "DELETE FROM records WHERE type = ? AND id = ?",
            (record_type, record_id),
        )
        self._connection.commit()
        return cursor.rowcount > 0

    def clear(self) -> None:
        self._connection.execute("DELETE FROM records")
        self._connection.commit()


def _as_text(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _row_to_record(row: tuple[str, str]) -> BaseRecord:
    type_name, payload = row
    return decode_record(type_name, json.loads(payload))
