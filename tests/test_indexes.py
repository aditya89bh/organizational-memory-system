"""Tests for in-memory record indexes."""

from organizational_memory.models import Decision, Task
from organizational_memory.models.enums import DecisionStatus
from organizational_memory.storage.indexes import build_indexes


def test_index_by_type() -> None:
    records = [
        Decision(id="d1", title="a", description="a"),
        Task(id="t1", title="t", description="d", owner_id="alice"),
    ]
    indexes = build_indexes(records)
    assert indexes.by_type == {"Decision": ["d1"], "Task": ["t1"]}


def test_index_by_owner() -> None:
    records = [
        Task(id="t1", title="t", description="d", owner_id="alice"),
        Task(id="t2", title="t", description="d", owner_id="alice"),
        Task(id="t3", title="t", description="d", owner_id="bob"),
    ]
    indexes = build_indexes(records)
    assert indexes.by_owner == {"alice": ["t1", "t2"], "bob": ["t3"]}


def test_index_by_meeting() -> None:
    records = [Decision(id="d1", title="a", description="a", source_meeting_id="m1")]
    assert build_indexes(records).by_meeting == {"m1": ["d1"]}


def test_index_by_status() -> None:
    records = [
        Decision(id="d1", title="a", description="a", status=DecisionStatus.ACCEPTED),
        Decision(id="d2", title="b", description="b", status=DecisionStatus.PROPOSED),
    ]
    indexes = build_indexes(records)
    assert indexes.by_status["accepted"] == ["d1"]
    assert indexes.by_status["proposed"] == ["d2"]


def test_index_by_date() -> None:
    decision = Decision(id="d1", title="a", description="a")
    indexes = build_indexes([decision])
    key = decision.created_at.date().isoformat()
    assert indexes.by_date == {key: ["d1"]}


def test_empty_records() -> None:
    indexes = build_indexes([])
    assert indexes.by_type == {}
    assert indexes.by_owner == {}
