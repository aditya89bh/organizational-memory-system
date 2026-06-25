"""Tests for commitment completion metrics."""

from pathlib import Path

from organizational_memory.analytics.commitment_completion import (
    commitment_completion,
)
from organizational_memory.models import Commitment
from organizational_memory.models.enums import CommitmentStatus
from organizational_memory.storage.json_store import JSONStore


def _store(tmp_path: Path) -> JSONStore:
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(
        Commitment(
            id="c1",
            owner_id="alice",
            description="ship",
            status=CommitmentStatus.COMPLETED,
            source_meeting_id="m1",
        )
    )
    store.save_record(
        Commitment(
            id="c2",
            owner_id="alice",
            description="write docs",
            status=CommitmentStatus.PENDING,
            source_meeting_id="m1",
        )
    )
    store.save_record(
        Commitment(
            id="c3",
            owner_id="bob",
            description="review",
            status=CommitmentStatus.IN_PROGRESS,
            source_meeting_id="m2",
        )
    )
    store.save_record(
        Commitment(
            id="c4",
            owner_id="bob",
            description="cancelled item",
            status=CommitmentStatus.CANCELLED,
            source_meeting_id="m2",
        )
    )
    return store


def test_totals(tmp_path: Path) -> None:
    report = commitment_completion(_store(tmp_path))
    assert report.total == 4
    assert report.open == 2
    assert report.completed == 1
    assert report.cancelled == 1


def test_completion_rate(tmp_path: Path) -> None:
    report = commitment_completion(_store(tmp_path))
    assert report.completion_rate == 0.25


def test_completion_breakdowns(tmp_path: Path) -> None:
    report = commitment_completion(_store(tmp_path))
    assert report.completed_by_owner == {"alice": 1}
    assert report.completed_by_meeting == {"m1": 1}


def test_empty(tmp_path: Path) -> None:
    report = commitment_completion(JSONStore(tmp_path / "e.json"))
    assert report.total == 0
    assert report.completion_rate == 0.0
