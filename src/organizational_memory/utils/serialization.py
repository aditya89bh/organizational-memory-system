"""JSON and dataclass serialization helpers.

Converts domain objects (dataclasses, datetimes, paths, enums, and sets) into
JSON-compatible structures and back.
"""

import dataclasses
import json
from collections.abc import Mapping
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from organizational_memory.utils.time import format_timestamp


def to_serializable(obj: Any) -> Any:
    """Recursively convert ``obj`` into JSON-compatible primitives.

    Dataclasses become dicts, datetimes become ISO 8601 strings, paths and enums
    are stringified, and sets are emitted as sorted lists for deterministic output.
    """
    if isinstance(obj, Enum):
        return to_serializable(obj.value)
    if isinstance(obj, datetime):
        return format_timestamp(obj)
    if isinstance(obj, Path):
        return str(obj)
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {
            field.name: to_serializable(getattr(obj, field.name))
            for field in dataclasses.fields(obj)
        }
    if isinstance(obj, Mapping):
        return {str(key): to_serializable(value) for key, value in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_serializable(item) for item in obj]
    if isinstance(obj, (set, frozenset)):
        return [to_serializable(item) for item in sorted(obj, key=str)]
    return obj


def to_json(obj: Any, *, indent: int | None = None, sort_keys: bool = False) -> str:
    """Serialize ``obj`` to a JSON string."""
    return json.dumps(
        to_serializable(obj),
        indent=indent,
        sort_keys=sort_keys,
        ensure_ascii=False,
    )


def from_json(text: str) -> Any:
    """Deserialize a JSON string into Python primitives."""
    return json.loads(text)
