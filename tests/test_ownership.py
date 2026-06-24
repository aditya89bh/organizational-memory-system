"""Tests for ownership models."""

import pytest

from organizational_memory.exceptions import ValidationError
from organizational_memory.models import Assignment, OwnerRef, OwnershipChange


def test_owner_ref_construction() -> None:
    owner = OwnerRef(owner_id="alice", display_name="Alice")
    assert owner.owner_id == "alice"
    assert owner.display_name == "Alice"


def test_owner_ref_rejects_blank_owner() -> None:
    with pytest.raises(ValidationError, match="owner_id is required"):
        OwnerRef(owner_id="  ")


def test_assignment_construction() -> None:
    assignment = Assignment(entity_type="task", entity_id="t1", owner_id="alice")
    assert assignment.entity_type == "task"
    assert assignment.assigned_at.tzinfo is not None
    assert assignment.role is None


def test_assignment_requires_owner() -> None:
    with pytest.raises(ValidationError, match="owner_id is required"):
        Assignment(entity_type="task", entity_id="t1", owner_id="")


def test_ownership_change_construction() -> None:
    change = OwnershipChange(
        entity_type="decision",
        entity_id="d1",
        new_owner_id="bob",
        previous_owner_id="alice",
        reason="reassigned",
    )
    assert change.new_owner_id == "bob"
    assert change.previous_owner_id == "alice"


def test_ownership_change_requires_new_owner() -> None:
    with pytest.raises(ValidationError, match="new_owner_id is required"):
        OwnershipChange(entity_type="decision", entity_id="d1", new_owner_id="")
