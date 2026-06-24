"""Tests for the Commitment model."""

from datetime import UTC, datetime

from organizational_memory.models import Commitment, CommitmentStatus


def test_commitment_defaults() -> None:
    commitment = Commitment(owner_id="alice", description="Ship the report")
    assert commitment.owner_id == "alice"
    assert commitment.status is CommitmentStatus.PENDING
    assert commitment.due_at is None
    assert commitment.created_at.tzinfo is not None


def test_commitment_full_construction() -> None:
    commitment = Commitment(
        owner_id="bob",
        description="Prepare slides",
        due_at=datetime(2026, 6, 30, 17, 0, tzinfo=UTC),
        status=CommitmentStatus.IN_PROGRESS,
        source_meeting_id="m1",
        metadata={"channel": "email"},
    )
    assert commitment.status is CommitmentStatus.IN_PROGRESS
    assert commitment.metadata["channel"] == "email"


def test_commitment_serialization() -> None:
    commitment = Commitment(
        owner_id="alice",
        description="Ship the report",
        due_at=datetime(2026, 6, 30, 17, 0, tzinfo=UTC),
    )
    data = commitment.to_dict()
    assert data["owner_id"] == "alice"
    assert data["due_at"] == "2026-06-30T17:00:00Z"
