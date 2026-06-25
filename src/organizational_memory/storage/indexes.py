"""Lightweight in-memory indexes over memory records.

The indexes map field values to the ids of records that carry them. They are
built deterministically from a list of records and are intended for fast,
read-only lookups; they are not persisted.
"""

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from organizational_memory.schemas.base import BaseRecord


@dataclass(frozen=True)
class RecordIndexes:
    """Deterministic value-to-ids indexes for a set of records."""

    by_type: dict[str, list[str]] = field(default_factory=dict)
    by_owner: dict[str, list[str]] = field(default_factory=dict)
    by_meeting: dict[str, list[str]] = field(default_factory=dict)
    by_status: dict[str, list[str]] = field(default_factory=dict)
    by_date: dict[str, list[str]] = field(default_factory=dict)


def _status_value(status: object) -> str:
    return status.value if isinstance(status, Enum) else str(status)


def _date_key(record: BaseRecord) -> str | None:
    moment = getattr(record, "occurred_at", None) or record.created_at
    if isinstance(moment, datetime):
        return moment.date().isoformat()
    return None


def build_indexes(records: Iterable[BaseRecord]) -> RecordIndexes:
    """Build :class:`RecordIndexes` from ``records`` deterministically."""
    by_type: dict[str, list[str]] = defaultdict(list)
    by_owner: dict[str, list[str]] = defaultdict(list)
    by_meeting: dict[str, list[str]] = defaultdict(list)
    by_status: dict[str, list[str]] = defaultdict(list)
    by_date: dict[str, list[str]] = defaultdict(list)

    for record in records:
        by_type[type(record).__name__].append(record.id)

        owner = getattr(record, "owner_id", None)
        if owner:
            by_owner[str(owner)].append(record.id)

        meeting = getattr(record, "source_meeting_id", None)
        if meeting:
            by_meeting[str(meeting)].append(record.id)

        status = getattr(record, "status", None)
        if status is not None:
            by_status[_status_value(status)].append(record.id)

        date_key = _date_key(record)
        if date_key is not None:
            by_date[date_key].append(record.id)

    return RecordIndexes(
        by_type={key: sorted(value) for key, value in sorted(by_type.items())},
        by_owner={key: sorted(value) for key, value in sorted(by_owner.items())},
        by_meeting={key: sorted(value) for key, value in sorted(by_meeting.items())},
        by_status={key: sorted(value) for key, value in sorted(by_status.items())},
        by_date={key: sorted(value) for key, value in sorted(by_date.items())},
    )
