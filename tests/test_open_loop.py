"""Tests for the OpenLoop model."""

from datetime import UTC, datetime

from organizational_memory.models import OpenLoop


def test_open_loop_defaults() -> None:
    loop = OpenLoop(question="Who owns billing?")
    assert loop.status == "open"
    assert loop.owner_id is None
    assert loop.due_at is None
    assert loop.created_at.tzinfo is not None


def test_open_loop_full_construction() -> None:
    loop = OpenLoop(
        question="Who owns billing?",
        owner_id="alice",
        status="resolved",
        due_at=datetime(2026, 7, 5, 9, 0, tzinfo=UTC),
        source_meeting_id="m1",
        metadata={"area": "finance"},
    )
    assert loop.status == "resolved"
    assert loop.owner_id == "alice"


def test_open_loop_serialization() -> None:
    loop = OpenLoop(question="Who owns billing?")
    data = loop.to_dict()
    assert data["question"] == "Who owns billing?"
    assert data["status"] == "open"
