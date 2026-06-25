"""JSON-file-backed implementation of :class:`MemoryStore`.

Records are kept in memory as ``{type: {id: payload}}`` and written to a single
JSON file with deterministic, sorted output on every mutation.
"""

import json
from pathlib import Path
from typing import Any

from organizational_memory.constants import ENCODING
from organizational_memory.schemas.base import BaseRecord
from organizational_memory.storage.store import (
    MemoryStore,
    decode_record,
    encode_record,
)
from organizational_memory.utils.helpers import ensure_directory

_Payload = dict[str, Any]
_Data = dict[str, dict[str, _Payload]]


class JSONStore(MemoryStore):
    """A :class:`MemoryStore` backed by a single deterministic JSON file."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._data: _Data = self._load()
        if not self.path.exists():
            self._flush()

    def _load(self) -> _Data:
        if not self.path.exists():
            return {}
        raw = json.loads(self.path.read_text(encoding=ENCODING))
        records = raw.get("records", {})
        return {
            type_name: dict(by_id) for type_name, by_id in records.items()
        }

    def _flush(self) -> None:
        ensure_directory(self.path.parent)
        document = {"records": self._data}
        self.path.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding=ENCODING,
        )

    def save_record(self, record: BaseRecord) -> None:
        type_name, record_id, payload = encode_record(record)
        self._data.setdefault(type_name, {})[record_id] = payload
        self._flush()

    def get_record(self, record_type: str, record_id: str) -> BaseRecord | None:
        payload = self._data.get(record_type, {}).get(record_id)
        if payload is None:
            return None
        return decode_record(record_type, payload)

    def list_records(self, record_type: str | None = None) -> list[BaseRecord]:
        type_names = [record_type] if record_type is not None else sorted(self._data)
        records: list[BaseRecord] = []
        for name in type_names:
            for record_id in sorted(self._data.get(name, {})):
                records.append(decode_record(name, self._data[name][record_id]))
        return records

    def update_record(self, record: BaseRecord) -> None:
        self.save_record(record)

    def delete_record(self, record_type: str, record_id: str) -> bool:
        bucket = self._data.get(record_type, {})
        if record_id not in bucket:
            return False
        del bucket[record_id]
        if not bucket:
            self._data.pop(record_type, None)
        self._flush()
        return True

    def clear(self) -> None:
        self._data = {}
        self._flush()
