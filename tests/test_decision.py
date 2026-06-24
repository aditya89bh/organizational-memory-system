"""Tests for the Decision model."""

from datetime import UTC, datetime

from organizational_memory.models import Decision


def test_decision_defaults() -> None:
    decision = Decision(title="Adopt CI", description="Use GitHub Actions")
    assert decision.status == "proposed"
    assert decision.owner_id is None
    assert decision.decided_at is None
    assert decision.id


def test_decision_full_construction() -> None:
    decision = Decision(
        title="Adopt CI",
        description="Use GitHub Actions for all checks",
        owner_id="alice",
        rationale="Reduces manual toil",
        decided_at=datetime(2026, 6, 24, 9, 0, tzinfo=UTC),
        status="accepted",
        source_meeting_id="m1",
        metadata={"priority": "high"},
    )
    assert decision.owner_id == "alice"
    assert decision.status == "accepted"


def test_decision_serialization() -> None:
    decision = Decision(
        title="Adopt CI",
        description="Use GitHub Actions",
        decided_at=datetime(2026, 6, 24, 9, 0, tzinfo=UTC),
    )
    data = decision.to_dict()
    assert data["title"] == "Adopt CI"
    assert data["decided_at"] == "2026-06-24T09:00:00Z"
