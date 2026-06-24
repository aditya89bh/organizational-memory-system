"""Tests for the Participant model."""

from organizational_memory.models import Participant


def test_participant_minimal_construction() -> None:
    participant = Participant(name="Alice")
    assert participant.name == "Alice"
    assert participant.email is None
    assert participant.role is None
    assert participant.organization is None
    assert participant.id


def test_participant_full_construction() -> None:
    participant = Participant(
        name="Bob",
        email="bob@example.com",
        role="Engineer",
        organization="Acme",
        metadata={"team": "platform"},
    )
    assert participant.email == "bob@example.com"
    assert participant.metadata["team"] == "platform"


def test_participant_serialization() -> None:
    participant = Participant(name="Carol", email="carol@example.com")
    data = participant.to_dict()
    assert data["name"] == "Carol"
    assert data["email"] == "carol@example.com"
