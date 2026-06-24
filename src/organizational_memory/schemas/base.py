"""Base record shared by all organizational memory entities.

Concrete entities (decisions, commitments, tasks, open loops) subclass
:class:`BaseRecord` to inherit identity, timestamps, and serialization behavior.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from organizational_memory.utils.helpers import generate_id
from organizational_memory.utils.serialization import to_json, to_serializable
from organizational_memory.utils.time import utc_now


@dataclass(kw_only=True)
class BaseRecord:
    """Common fields and serialization helpers for memory records.

    Attributes:
        id: Stable unique identifier, generated automatically by default.
        created_at: UTC creation timestamp.
        updated_at: UTC timestamp of the last modification.
    """

    id: str = field(default_factory=generate_id)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def touch(self) -> None:
        """Update :attr:`updated_at` to the current time."""
        self.updated_at = utc_now()

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible dictionary representation of the record."""
        result: Any = to_serializable(self)
        if not isinstance(result, dict):  # pragma: no cover - defensive guard
            raise TypeError("Serialized record is not a mapping.")
        return result

    def to_json(self, *, indent: int | None = None, sort_keys: bool = False) -> str:
        """Return a JSON string representation of the record."""
        return to_json(self, indent=indent, sort_keys=sort_keys)
