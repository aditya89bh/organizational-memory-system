"""Deterministic pagination for recall results.

A :class:`Page` wraps a window of items with the metadata callers need to
navigate: the total number of matches, the applied limit/offset, and whether
more results remain.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Page(Generic[T]):
    """A single page of results plus navigation metadata."""

    items: list[T]
    total: int
    offset: int
    limit: int | None
    has_more: bool

    @property
    def returned(self) -> int:
        """Number of items on this page."""
        return len(self.items)

    def as_metadata(self) -> dict[str, Any]:
        """Return JSON-compatible page metadata (without the items)."""
        return {
            "total": self.total,
            "offset": self.offset,
            "limit": self.limit,
            "returned": self.returned,
            "has_more": self.has_more,
        }


def paginate(
    items: Sequence[T],
    *,
    limit: int | None = None,
    offset: int = 0,
) -> Page[T]:
    """Return a :class:`Page` over ``items`` for the given ``limit``/``offset``.

    A negative ``offset`` is treated as ``0``; a negative ``limit`` raises.
    """
    if limit is not None and limit < 0:
        raise ValueError("limit must be non-negative")
    total = len(items)
    start = max(offset, 0)
    window = list(items[start:] if limit is None else items[start : start + limit])
    has_more = start + len(window) < total
    return Page(
        items=window,
        total=total,
        offset=start,
        limit=limit,
        has_more=has_more,
    )
