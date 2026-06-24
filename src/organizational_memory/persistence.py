"""Persistence-friendly conversion helpers for domain models.

Provides :func:`to_dict` and :func:`from_dict` that convert dataclass-based
domain models to and from JSON-compatible dictionaries, handling datetimes,
enums, nested dataclasses, and optional fields.
"""

import dataclasses
import types
from collections.abc import Mapping
from datetime import datetime
from enum import Enum
from typing import Any, TypeVar, Union, get_args, get_origin, get_type_hints

from organizational_memory.exceptions import ValidationError
from organizational_memory.utils.serialization import to_serializable
from organizational_memory.utils.time import parse_timestamp

T = TypeVar("T")


def to_dict(model: Any) -> dict[str, Any]:
    """Convert a dataclass instance into a JSON-compatible dictionary.

    Raises:
        TypeError: If ``model`` is not a dataclass instance.
    """
    if not dataclasses.is_dataclass(model) or isinstance(model, type):
        raise TypeError("to_dict expects a dataclass instance.")
    result = to_serializable(model)
    if not isinstance(result, dict):  # pragma: no cover - defensive guard
        raise TypeError("Serialized model is not a mapping.")
    return result


def from_dict(cls: type[T], data: Mapping[str, Any]) -> T:
    """Build an instance of dataclass ``cls`` from ``data``.

    Raises:
        TypeError: If ``cls`` is not a dataclass type.
        ValidationError: If ``data`` cannot be converted into ``cls``.
    """
    if not dataclasses.is_dataclass(cls):
        raise TypeError("from_dict expects a dataclass type.")
    hints = get_type_hints(cls)
    try:
        kwargs = {
            f.name: _convert(hints[f.name], data[f.name])
            for f in dataclasses.fields(cls)
            if f.init and f.name in data
        }
        return cls(**kwargs)
    except (TypeError, ValueError) as exc:
        raise ValidationError(
            f"Cannot build {cls.__name__} from data: {exc}"
        ) from exc


def _convert(annotation: Any, value: Any) -> Any:
    """Convert a single JSON value into the type described by ``annotation``."""
    if value is None:
        return None

    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is Union or origin is types.UnionType:
        non_none = [arg for arg in args if arg is not type(None)]
        for arg in non_none:
            try:
                return _convert(arg, value)
            except (TypeError, ValueError):
                continue
        return value

    if origin in (list, tuple):
        item_type = args[0] if args else Any
        converted = [_convert(item_type, item) for item in value]
        return tuple(converted) if origin is tuple else converted

    if origin is dict:
        return dict(value)

    if isinstance(annotation, type):
        if issubclass(annotation, Enum):
            return annotation(value)
        if annotation is datetime:
            return parse_timestamp(value)
        if dataclasses.is_dataclass(annotation):
            return from_dict(annotation, value)

    return value
