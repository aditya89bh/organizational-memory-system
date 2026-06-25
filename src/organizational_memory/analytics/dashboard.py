"""Typed analytics dashboard models.

Lightweight, presentation-oriented containers for surfacing metrics. Each model
converts to a JSON-safe structure (only ``str``/``int``/``float``/``bool``/
``None`` plus lists and dicts) so dashboards can be serialized directly.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from organizational_memory.utils.time import format_timestamp, utc_now

CardValue = str | int | float | bool


@dataclass(frozen=True)
class AnalyticsCard:
    """A single labelled metric value."""

    title: str
    value: CardValue
    unit: str | None = None
    detail: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {"title": self.title, "value": self.value}
        if self.unit is not None:
            data["unit"] = self.unit
        if self.detail is not None:
            data["detail"] = self.detail
        return data


@dataclass(frozen=True)
class AnalyticsSection:
    """A named group of analytics cards."""

    name: str
    cards: list[AnalyticsCard] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "cards": [card.to_dict() for card in self.cards],
        }


@dataclass(frozen=True)
class AnalyticsDashboard:
    """A titled collection of analytics sections."""

    title: str
    sections: list[AnalyticsSection] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "sections": [section.to_dict() for section in self.sections],
        }


@dataclass(frozen=True)
class DashboardSnapshot:
    """A dashboard captured at a point in time."""

    dashboard: AnalyticsDashboard
    generated_at: datetime = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": format_timestamp(self.generated_at),
            "dashboard": self.dashboard.to_dict(),
        }
