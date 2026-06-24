"""Comprehensive validation tests for invalid domain objects."""

from collections.abc import Callable
from datetime import UTC, datetime

import pytest

from organizational_memory.exceptions import ValidationError
from organizational_memory.models import (
    ActionItem,
    Commitment,
    Decision,
    Dependency,
    DiscussionTopic,
    EntityRef,
    Meeting,
    MemoryEvent,
    OpenLoop,
    OwnerRef,
    OwnershipChange,
    Participant,
    Risk,
    Task,
)

_PAST = datetime(2020, 1, 1, 0, 0, tzinfo=UTC)
_START = datetime(2026, 6, 24, 10, 0, tzinfo=UTC)
_BEFORE_START = datetime(2026, 6, 24, 9, 0, tzinfo=UTC)


def _empty_text_cases() -> list[Callable[[], object]]:
    return [
        lambda: Participant(name=""),
        lambda: Decision(title="", description="d"),
        lambda: Decision(title="t", description=""),
        lambda: Risk(title="", description="d"),
        lambda: OpenLoop(question="   "),
        lambda: ActionItem(description=""),
        lambda: DiscussionTopic(title=""),
        lambda: Dependency(source_id="", target_id="t2"),
        lambda: MemoryEvent(event_type="", entity_type="task", entity_id="t1"),
    ]


@pytest.mark.parametrize("factory", _empty_text_cases())
def test_empty_required_text_is_rejected(factory: Callable[[], object]) -> None:
    with pytest.raises(ValidationError):
        factory()


def test_meeting_invalid_time_range() -> None:
    with pytest.raises(ValidationError, match="ended_at cannot be before started_at"):
        Meeting(title="m", started_at=_START, ended_at=_BEFORE_START)


def test_discussion_topic_invalid_time_range() -> None:
    with pytest.raises(ValidationError, match="ended_at cannot be before started_at"):
        DiscussionTopic(title="t", started_at=_START, ended_at=_BEFORE_START)


def _due_before_created_cases() -> list[Callable[[], object]]:
    return [
        lambda: Commitment(owner_id="a", description="d", due_at=_PAST),
        lambda: Task(title="t", description="d", owner_id="a", due_at=_PAST),
        lambda: OpenLoop(question="q", due_at=_PAST),
        lambda: ActionItem(description="d", due_at=_PAST),
    ]


@pytest.mark.parametrize("factory", _due_before_created_cases())
def test_due_before_created_is_rejected(factory: Callable[[], object]) -> None:
    with pytest.raises(ValidationError, match="due_at cannot be before created_at"):
        factory()


def _missing_owner_cases() -> list[Callable[[], object]]:
    return [
        lambda: Commitment(owner_id="", description="d"),
        lambda: Task(title="t", description="d", owner_id="  "),
        lambda: OwnerRef(owner_id=""),
        lambda: OwnershipChange(entity_type="task", entity_id="t1", new_owner_id=""),
    ]


@pytest.mark.parametrize("factory", _missing_owner_cases())
def test_missing_owner_is_rejected(factory: Callable[[], object]) -> None:
    with pytest.raises(ValidationError):
        factory()


@pytest.mark.parametrize(
    "factory",
    [
        lambda: EntityRef(entity_type="", entity_id="d1"),
        lambda: EntityRef(entity_type="decision", entity_id=""),
    ],
)
def test_invalid_relationship_refs_are_rejected(
    factory: Callable[[], object],
) -> None:
    with pytest.raises(ValidationError):
        factory()
