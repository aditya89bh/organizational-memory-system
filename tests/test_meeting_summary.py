"""Tests for meeting summary reports."""

from pathlib import Path

import pytest

from organizational_memory.models import (
    Commitment,
    Decision,
    Meeting,
    OpenLoop,
    Risk,
    Task,
)
from organizational_memory.reports.meeting_summary import meeting_summary
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import parse_timestamp, utc_now


def _store(tmp_path: Path) -> JSONStore:
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(
        Meeting(
            id="m1",
            title="Kickoff",
            started_at=parse_timestamp("2026-02-02T09:00:00Z"),
            participants=["alice", "bob"],
            source="transcript",
        )
    )
    store.save_record(
        Decision(id="d1", title="Adopt mesh", description="x", owner_id="alice",
                 source_meeting_id="m1")
    )
    store.save_record(
        Commitment(id="c1", owner_id="alice", description="ship",
                   source_meeting_id="m1")
    )
    store.save_record(
        Task(id="t1", title="provision", description="x", owner_id="bob",
             source_meeting_id="m1")
    )
    store.save_record(
        OpenLoop(id="o1", question="scale?", source_meeting_id="m1")
    )
    store.save_record(
        Risk(id="r1", title="risk", description="x", source_meeting_id="m1")
    )
    # Record attributed to a different meeting must be excluded.
    store.save_record(
        Decision(id="d2", title="Other", description="x", source_meeting_id="m2")
    )
    return store


def test_summary_counts(tmp_path: Path) -> None:
    report = meeting_summary(_store(tmp_path), "m1", now=utc_now())
    assert report.summary == {
        "decisions": 1,
        "commitments": 1,
        "tasks": 1,
        "open_loops": 1,
        "risks": 1,
        "participants": 2,
    }


def test_sections_present(tmp_path: Path) -> None:
    report = meeting_summary(_store(tmp_path), "m1", now=utc_now())
    titles = [section.title for section in report.sections]
    assert titles == [
        "Participants",
        "Decisions",
        "Commitments",
        "Tasks",
        "Open loops",
        "Risks",
    ]


def test_excludes_other_meetings(tmp_path: Path) -> None:
    report = meeting_summary(_store(tmp_path), "m1", now=utc_now())
    decisions = report.section("Decisions")
    assert decisions is not None
    ids = {row[0] for row in decisions.tables[0].rows}
    assert ids == {"d1"}


def test_metadata(tmp_path: Path) -> None:
    report = meeting_summary(_store(tmp_path), "m1", now=utc_now())
    assert report.metadata["meeting_id"] == "m1"
    assert report.metadata["source"] == "transcript"
    assert report.metadata["started_at"] == "2026-02-02T09:00:00Z"


def test_to_dict_json_safe(tmp_path: Path) -> None:
    import json

    report = meeting_summary(_store(tmp_path), "m1", now=utc_now())
    json.dumps(report.to_dict())


def test_missing_meeting(tmp_path: Path) -> None:
    with pytest.raises(KeyError):
        meeting_summary(_store(tmp_path), "nope", now=utc_now())
