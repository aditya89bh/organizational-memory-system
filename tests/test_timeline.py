"""Tests for timeline models."""

from datetime import UTC, datetime

import pytest

from organizational_memory.exceptions import ValidationError
from organizational_memory.models import OrganizationalTimeline, TimelineEntry


def _entry(hour: int, title: str) -> TimelineEntry:
    return TimelineEntry(
        timestamp=datetime(2026, 6, 24, hour, 0, tzinfo=UTC),
        title=title,
        entity_type="decision",
        entity_id=f"d{hour}",
    )


def test_timeline_entry_requires_title() -> None:
    with pytest.raises(ValidationError, match="title must not be empty"):
        TimelineEntry(
            timestamp=datetime(2026, 6, 24, 9, 0, tzinfo=UTC),
            title="",
            entity_type="decision",
            entity_id="d1",
        )


def test_timeline_orders_entries_by_timestamp() -> None:
    timeline = OrganizationalTimeline()
    timeline.add(_entry(11, "late"))
    timeline.add(_entry(9, "early"))
    timeline.add(_entry(10, "middle"))
    titles = [entry.title for entry in timeline.ordered()]
    assert titles == ["early", "middle", "late"]
    assert len(timeline) == 3


def test_timeline_ordered_does_not_mutate_insertion_order() -> None:
    timeline = OrganizationalTimeline()
    timeline.add(_entry(11, "late"))
    timeline.add(_entry(9, "early"))
    timeline.ordered()
    assert [entry.title for entry in timeline.entries] == ["late", "early"]
