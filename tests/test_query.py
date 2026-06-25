"""Tests for the query API."""

from datetime import timedelta

from organizational_memory.models import Decision, Task
from organizational_memory.models.enums import DecisionStatus
from organizational_memory.storage.query import Query, apply_query, matches
from organizational_memory.utils.time import utc_now


def _records() -> list[Decision | Task]:
    base = utc_now()
    return [
        Decision(
            id="d1",
            title="Ship beta",
            description="ship the beta",
            owner_id="alice",
            status=DecisionStatus.ACCEPTED,
            source_meeting_id="m1",
            created_at=base,
        ),
        Decision(
            id="d2",
            title="Revisit pricing",
            description="pricing review",
            owner_id="bob",
            status=DecisionStatus.PROPOSED,
            created_at=base + timedelta(hours=1),
        ),
        Task(
            id="t1",
            title="Write docs",
            description="documentation",
            owner_id="alice",
            created_at=base + timedelta(hours=2),
        ),
    ]


def test_filter_by_record_type() -> None:
    result = apply_query(_records(), Query(record_type="Task"))
    assert [r.id for r in result] == ["t1"]


def test_filter_by_owner() -> None:
    result = apply_query(_records(), Query(owner_id="alice"))
    assert {r.id for r in result} == {"d1", "t1"}


def test_filter_by_status() -> None:
    result = apply_query(_records(), Query(status="accepted"))
    assert [r.id for r in result] == ["d1"]


def test_filter_by_meeting() -> None:
    result = apply_query(_records(), Query(source_meeting_id="m1"))
    assert [r.id for r in result] == ["d1"]


def test_text_contains() -> None:
    result = apply_query(_records(), Query(text_contains="pricing"))
    assert [r.id for r in result] == ["d2"]


def test_created_window() -> None:
    records = _records()
    base = records[0].created_at
    result = apply_query(
        records, Query(created_after=base, created_before=base)
    )
    assert [r.id for r in result] == ["d1"]


def test_limit_and_offset() -> None:
    records = _records()
    assert [r.id for r in apply_query(records, Query(limit=2))] == ["d1", "d2"]
    assert [r.id for r in apply_query(records, Query(offset=1))] == ["d2", "t1"]
    assert [r.id for r in apply_query(records, Query(offset=1, limit=1))] == ["d2"]


def test_matches_single_record() -> None:
    decision = _records()[0]
    assert matches(decision, Query(owner_id="alice")) is True
    assert matches(decision, Query(owner_id="bob")) is False
