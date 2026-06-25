"""Tests for commitment search."""

from datetime import timedelta
from pathlib import Path

from organizational_memory.models import Commitment
from organizational_memory.models.enums import CommitmentStatus
from organizational_memory.recall.commitment_search import search_commitments
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import utc_now


def _store(tmp_path: Path) -> JSONStore:
    now = utc_now()
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(
        Commitment(
            id="c1",
            owner_id="alice",
            description="ship the onboarding flow",
            status=CommitmentStatus.IN_PROGRESS,
            due_at=now + timedelta(days=5),
            source_meeting_id="m1",
        )
    )
    store.save_record(
        Commitment(
            id="c2",
            owner_id="bob",
            description="write the pricing doc",
            status=CommitmentStatus.PENDING,
            due_at=now + timedelta(days=30),
            source_meeting_id="m2",
        )
    )
    return store


def test_search_by_text(tmp_path: Path) -> None:
    results = search_commitments(_store(tmp_path), text="onboarding")
    assert [r.record.id for r in results] == ["c1"]


def test_search_by_owner(tmp_path: Path) -> None:
    results = search_commitments(_store(tmp_path), owner_id="bob")
    assert [r.record.id for r in results] == ["c2"]


def test_search_by_status(tmp_path: Path) -> None:
    results = search_commitments(_store(tmp_path), status="in_progress")
    assert [r.record.id for r in results] == ["c1"]


def test_search_by_due_window(tmp_path: Path) -> None:
    now = utc_now()
    results = search_commitments(
        _store(tmp_path), due_before=now + timedelta(days=10)
    )
    assert [r.record.id for r in results] == ["c1"]


def test_search_by_meeting(tmp_path: Path) -> None:
    results = search_commitments(_store(tmp_path), source_meeting_id="m2")
    assert [r.record.id for r in results] == ["c2"]


def test_no_filters_returns_all(tmp_path: Path) -> None:
    results = search_commitments(_store(tmp_path))
    assert [r.record.id for r in results] == ["c1", "c2"]
