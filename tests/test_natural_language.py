"""Tests for deterministic natural-language recall."""

from datetime import timedelta
from pathlib import Path

from organizational_memory.models import Commitment, Decision, OpenLoop, Task
from organizational_memory.models.enums import OpenLoopStatus, TaskStatus
from organizational_memory.recall.natural_language import answer, interpret
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import utc_now


def test_interpret_who_owns() -> None:
    interpretation = interpret("Who owns the launch task?")
    assert interpretation.intent == "who_owns"
    assert interpretation.record_type == "Task"
    assert interpretation.text == "launch"


def test_interpret_decisions_about_topic() -> None:
    interpretation = interpret("What decisions were made about pricing?")
    assert interpretation.record_type == "Decision"
    assert interpretation.text == "pricing"


def test_interpret_unresolved() -> None:
    interpretation = interpret("What is still unresolved?")
    assert interpretation.record_type == "OpenLoop"
    assert interpretation.status == "open"


def test_interpret_overdue() -> None:
    interpretation = interpret("What is overdue?")
    assert interpretation.overdue is True


def test_interpret_why() -> None:
    interpretation = interpret("Why did we choose Postgres?")
    assert interpretation.intent == "why"
    assert interpretation.record_type == "Decision"
    assert interpretation.text == "postgres"


def _store(tmp_path: Path) -> JSONStore:
    now = utc_now()
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(
        Decision(
            id="d1",
            title="Choose Postgres",
            description="use postgres for pricing",
        )
    )
    store.save_record(
        Task(
            id="t1",
            title="Launch landing page",
            description="ship it",
            owner_id="alice",
        )
    )
    store.save_record(
        OpenLoop(id="o1", question="auth approach?", status=OpenLoopStatus.OPEN)
    )
    store.save_record(
        OpenLoop(id="o2", question="closed item", status=OpenLoopStatus.RESOLVED)
    )
    store.save_record(
        Commitment(
            id="c1",
            owner_id="bob",
            description="late deliverable",
            created_at=now - timedelta(days=3),
            due_at=now - timedelta(days=1),
        )
    )
    store.save_record(
        Task(
            id="t2",
            title="future work",
            description="later",
            owner_id="alice",
            due_at=now + timedelta(days=5),
            status=TaskStatus.TODO,
        )
    )
    return store


def test_answer_decisions(tmp_path: Path) -> None:
    results = answer(_store(tmp_path), "What decisions were made about pricing?")
    assert [r.record.id for r in results] == ["d1"]


def test_answer_who_owns(tmp_path: Path) -> None:
    results = answer(_store(tmp_path), "Who owns the launch task?")
    assert [r.record.id for r in results] == ["t1"]


def test_answer_unresolved(tmp_path: Path) -> None:
    results = answer(_store(tmp_path), "What is still unresolved?")
    assert [r.record.id for r in results] == ["o1"]


def test_answer_overdue(tmp_path: Path) -> None:
    results = answer(_store(tmp_path), "What is overdue?", now=utc_now())
    assert [r.record.id for r in results] == ["c1"]
