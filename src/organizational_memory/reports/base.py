"""Shared report data model.

All Phase 7 reports are built from these small, typed containers so they can be
rendered or exported uniformly. A :class:`Report` is a titled, timestamped
collection of :class:`ReportSection` objects; sections may carry bullet bodies,
scalar metrics, and tabular :class:`ReportTable` data. Everything converts to a
deterministic, JSON-safe structure.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from organizational_memory.utils.time import format_timestamp


def json_safe(value: Any) -> Any:
    """Return a deterministic, JSON-serializable view of ``value``."""
    if isinstance(value, datetime):
        return format_timestamp(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return value


@dataclass(frozen=True)
class ReportTable:
    """A simple tabular section component with string cells."""

    title: str
    columns: tuple[str, ...]
    rows: list[tuple[str, ...]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "columns": list(self.columns),
            "rows": [list(row) for row in self.rows],
        }


@dataclass(frozen=True)
class ReportSection:
    """A named section with optional bullet body, metrics, and tables."""

    title: str
    body: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    tables: list[ReportTable] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "body": list(self.body),
            "metrics": json_safe(self.metrics),
            "tables": [table.to_dict() for table in self.tables],
        }


@dataclass(frozen=True)
class Report:
    """A titled, timestamped report composed of sections."""

    title: str
    generated_at: datetime
    summary: dict[str, Any] = field(default_factory=dict)
    sections: list[ReportSection] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "generated_at": format_timestamp(self.generated_at),
            "summary": json_safe(self.summary),
            "sections": [section.to_dict() for section in self.sections],
            "metadata": dict(self.metadata),
        }

    def section(self, title: str) -> ReportSection | None:
        """Return the first section matching ``title``, if any."""
        for section in self.sections:
            if section.title == title:
                return section
        return None
