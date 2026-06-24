"""Tests for typed identifier helpers."""

from collections.abc import Callable

import pytest

from organizational_memory.models.identifiers import (
    new_commitment_id,
    new_decision_id,
    new_event_id,
    new_meeting_id,
    new_open_loop_id,
    new_participant_id,
    new_task_id,
)

_GENERATORS: list[Callable[[], str]] = [
    new_meeting_id,
    new_participant_id,
    new_decision_id,
    new_commitment_id,
    new_task_id,
    new_open_loop_id,
    new_event_id,
]


@pytest.mark.parametrize("generator", _GENERATORS)
def test_generator_returns_hex_string(generator: Callable[[], str]) -> None:
    value = generator()
    assert isinstance(value, str)
    assert len(value) == 32
    assert all(char in "0123456789abcdef" for char in value)


@pytest.mark.parametrize("generator", _GENERATORS)
def test_generator_returns_unique_values(generator: Callable[[], str]) -> None:
    assert generator() != generator()
