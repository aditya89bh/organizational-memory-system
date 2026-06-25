"""Tests for ownership ranking."""

from organizational_memory.models import Decision, Meeting, MemoryEvent, Task
from organizational_memory.recall.ranking.ownership import ownership_score
from organizational_memory.utils.time import utc_now


def test_exact_owner_match() -> None:
    task = Task(title="x", description="y", owner_id="alice")
    assert ownership_score(task, "alice") == 1.0
    assert ownership_score(task, "bob") == 0.0


def test_actor_match() -> None:
    event = MemoryEvent(
        event_type="created",
        entity_type="Decision",
        entity_id="d1",
        actor_id="carol",
    )
    assert ownership_score(event, "carol") == 0.9


def test_participant_match() -> None:
    meeting = Meeting(title="Sync", started_at=utc_now(), participants=["dan", "eve"])
    assert ownership_score(meeting, "dan") == 0.7


def test_assignee_metadata_match() -> None:
    decision = Decision(title="x", description="y", metadata={"assignee": "frank"})
    assert ownership_score(decision, "frank") == 0.6


def test_no_owner_returns_zero() -> None:
    task = Task(title="x", description="y", owner_id="alice")
    assert ownership_score(task, None) == 0.0


def test_owner_beats_actor_priority() -> None:
    event = MemoryEvent(
        event_type="x",
        entity_type="y",
        entity_id="z",
        actor_id="alice",
    )
    assert ownership_score(event, "alice") == 0.9
