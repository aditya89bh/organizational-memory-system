"""Tests for the DiscussionTopic model."""

from datetime import UTC, datetime

from organizational_memory.models import DiscussionTopic


def test_discussion_topic_defaults() -> None:
    topic = DiscussionTopic(title="Roadmap")
    assert topic.summary is None
    assert topic.participant_ids == []
    assert topic.started_at is None


def test_discussion_topic_full_construction() -> None:
    topic = DiscussionTopic(
        title="Roadmap",
        summary="Discussed Q3 priorities",
        source_meeting_id="m1",
        participant_ids=["alice", "bob"],
        started_at=datetime(2026, 6, 24, 9, 0, tzinfo=UTC),
        ended_at=datetime(2026, 6, 24, 9, 30, tzinfo=UTC),
        metadata={"track": "planning"},
    )
    assert topic.participant_ids == ["alice", "bob"]
    assert topic.summary == "Discussed Q3 priorities"


def test_discussion_topic_serialization() -> None:
    topic = DiscussionTopic(title="Roadmap", participant_ids=["a"])
    data = topic.to_dict()
    assert data["title"] == "Roadmap"
    assert data["participant_ids"] == ["a"]
