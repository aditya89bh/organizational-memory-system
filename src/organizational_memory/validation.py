"""Reusable domain validation helpers.

These helpers raise :class:`~organizational_memory.exceptions.ValidationError`
so that all domain validation failures share a common exception type.
"""

from datetime import datetime

from organizational_memory.exceptions import ValidationError


def require_non_empty(value: str, field_name: str) -> str:
    """Ensure ``value`` contains non-whitespace text.

    Raises:
        ValidationError: If ``value`` is empty or whitespace only.
    """
    if not value.strip():
        raise ValidationError(f"{field_name} must not be empty.")
    return value


def require_owner(owner_id: str, field_name: str = "owner_id") -> str:
    """Ensure an owner identifier is present and non-empty.

    Raises:
        ValidationError: If ``owner_id`` is empty or whitespace only.
    """
    if not owner_id.strip():
        raise ValidationError(f"{field_name} is required and must not be empty.")
    return owner_id


def validate_time_range(
    started_at: datetime | None,
    ended_at: datetime | None,
    *,
    start_field: str = "started_at",
    end_field: str = "ended_at",
) -> None:
    """Ensure ``ended_at`` is not before ``started_at`` when both are set.

    Raises:
        ValidationError: If ``ended_at`` precedes ``started_at``.
    """
    if started_at is not None and ended_at is not None and ended_at < started_at:
        raise ValidationError(f"{end_field} cannot be before {start_field}.")


def validate_due_after(
    reference: datetime | None,
    due_at: datetime | None,
    *,
    reference_field: str = "created_at",
    due_field: str = "due_at",
) -> None:
    """Ensure ``due_at`` is not before ``reference`` when both are set.

    Raises:
        ValidationError: If ``due_at`` precedes ``reference``.
    """
    if reference is not None and due_at is not None and due_at < reference:
        raise ValidationError(f"{due_field} cannot be before {reference_field}.")
