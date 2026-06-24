"""Tests for reusable domain validation helpers."""

from datetime import UTC, datetime

import pytest

from organizational_memory.exceptions import ValidationError
from organizational_memory.validation import (
    require_non_empty,
    require_owner,
    validate_due_after,
    validate_time_range,
)


def test_require_non_empty_returns_value() -> None:
    assert require_non_empty("hello", "title") == "hello"


@pytest.mark.parametrize("value", ["", "   ", "\t\n"])
def test_require_non_empty_rejects_blank(value: str) -> None:
    with pytest.raises(ValidationError, match="title must not be empty"):
        require_non_empty(value, "title")


def test_require_owner_rejects_blank() -> None:
    with pytest.raises(ValidationError, match="owner_id is required"):
        require_owner("  ")


def test_validate_time_range_accepts_valid_order() -> None:
    start = datetime(2026, 6, 24, 9, 0, tzinfo=UTC)
    end = datetime(2026, 6, 24, 10, 0, tzinfo=UTC)
    validate_time_range(start, end)


def test_validate_time_range_rejects_reversed() -> None:
    start = datetime(2026, 6, 24, 10, 0, tzinfo=UTC)
    end = datetime(2026, 6, 24, 9, 0, tzinfo=UTC)
    with pytest.raises(ValidationError, match="ended_at cannot be before started_at"):
        validate_time_range(start, end)


def test_validate_time_range_ignores_missing_values() -> None:
    validate_time_range(None, datetime(2026, 6, 24, 9, 0, tzinfo=UTC))
    validate_time_range(datetime(2026, 6, 24, 9, 0, tzinfo=UTC), None)


def test_validate_due_after_rejects_due_before_reference() -> None:
    created = datetime(2026, 6, 24, 9, 0, tzinfo=UTC)
    due = datetime(2026, 6, 23, 9, 0, tzinfo=UTC)
    with pytest.raises(ValidationError, match="due_at cannot be before created_at"):
        validate_due_after(created, due)
