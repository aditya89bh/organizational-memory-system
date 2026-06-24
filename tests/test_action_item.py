"""Tests for the ActionItem model."""

from datetime import UTC, datetime

from organizational_memory.models import ActionItem


def test_action_item_defaults() -> None:
    item = ActionItem(description="Follow up with vendor")
    assert item.status == "open"
    assert item.owner_id is None
    assert item.due_at is None


def test_action_item_full_construction() -> None:
    item = ActionItem(
        description="Follow up with vendor",
        owner_id="alice",
        due_at=datetime(2026, 7, 1, 9, 0, tzinfo=UTC),
        status="done",
        source_meeting_id="m1",
        metadata={"label": "ops"},
    )
    assert item.owner_id == "alice"
    assert item.status == "done"


def test_action_item_serialization() -> None:
    item = ActionItem(description="Follow up")
    data = item.to_dict()
    assert data["description"] == "Follow up"
    assert data["status"] == "open"
