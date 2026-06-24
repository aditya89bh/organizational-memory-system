"""Tests for status and grading enumerations."""

import pytest

from organizational_memory.models.enums import (
    CommitmentStatus,
    DecisionStatus,
    DependencyStatus,
    Likelihood,
    OpenLoopStatus,
    Priority,
    RiskStatus,
    Severity,
    TaskStatus,
)


@pytest.mark.parametrize(
    ("enum_cls", "expected_values"),
    [
        (DecisionStatus, {"proposed", "accepted", "rejected", "superseded"}),
        (CommitmentStatus, {"pending", "in_progress", "completed", "cancelled"}),
        (TaskStatus, {"todo", "in_progress", "blocked", "done", "cancelled"}),
        (OpenLoopStatus, {"open", "resolved", "dismissed"}),
        (RiskStatus, {"identified", "mitigated", "accepted", "closed"}),
        (DependencyStatus, {"pending", "resolved", "blocked"}),
        (Priority, {"low", "medium", "high", "urgent"}),
        (Severity, {"low", "medium", "high", "critical"}),
        (Likelihood, {"low", "medium", "high"}),
    ],
)
def test_enum_member_values(
    enum_cls: type[DecisionStatus | Priority],
    expected_values: set[str],
) -> None:
    assert {member.value for member in enum_cls} == expected_values


def test_enums_are_strings() -> None:
    assert isinstance(DecisionStatus.ACCEPTED, str)
    assert DecisionStatus.ACCEPTED.value == "accepted"
    assert Priority.HIGH.value == "high"


def test_enum_round_trips_through_value() -> None:
    assert TaskStatus(TaskStatus.DONE.value) is TaskStatus.DONE
