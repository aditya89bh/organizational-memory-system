"""Typed identifier helpers for domain entities.

Each identifier is a :func:`typing.NewType` over ``str`` so that identifiers for
different entity kinds are distinguishable by static type checkers while
remaining plain strings at runtime.
"""

from typing import NewType

from organizational_memory.utils.helpers import generate_id

MeetingId = NewType("MeetingId", str)
ParticipantId = NewType("ParticipantId", str)
DecisionId = NewType("DecisionId", str)
CommitmentId = NewType("CommitmentId", str)
TaskId = NewType("TaskId", str)
OpenLoopId = NewType("OpenLoopId", str)
EventId = NewType("EventId", str)


def new_meeting_id() -> MeetingId:
    """Return a fresh, unique meeting identifier."""
    return MeetingId(generate_id())


def new_participant_id() -> ParticipantId:
    """Return a fresh, unique participant identifier."""
    return ParticipantId(generate_id())


def new_decision_id() -> DecisionId:
    """Return a fresh, unique decision identifier."""
    return DecisionId(generate_id())


def new_commitment_id() -> CommitmentId:
    """Return a fresh, unique commitment identifier."""
    return CommitmentId(generate_id())


def new_task_id() -> TaskId:
    """Return a fresh, unique task identifier."""
    return TaskId(generate_id())


def new_open_loop_id() -> OpenLoopId:
    """Return a fresh, unique open loop identifier."""
    return OpenLoopId(generate_id())


def new_event_id() -> EventId:
    """Return a fresh, unique memory event identifier."""
    return EventId(generate_id())
