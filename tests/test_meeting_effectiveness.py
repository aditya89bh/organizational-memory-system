"""Tests for meeting effectiveness metrics."""

from pathlib import Path

from organizational_memory.analytics.meeting_effectiveness import (
    meeting_effectiveness,
)
from organizational_memory.models import (
    Commitment,
    Decision,
    Meeting,
    OpenLoop,
    Task,
)
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import utc_now


def _store(tmp_path: Path) -> JSONStore:
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(Meeting(id="m1", title="Kickoff", started_at=utc_now()))
    store.save_record(Meeting(id="m2", title="Standup", started_at=utc_now()))
    store.save_record(
        Decision(id="d1", title="x", description="y", source_meeting_id="m1")
    )
    store.save_record(
        Commitment(id="c1", owner_id="a", description="y", source_meeting_id="m1")
    )
    store.save_record(
        Task(id="t1", title="x", description="y", owner_id="a", source_meeting_id="m1")
    )
    store.save_record(OpenLoop(id="o1", question="q?", source_meeting_id="m2"))
    store.save_record(OpenLoop(id="o2", question="q2?", source_meeting_id="m2"))
    return store


def test_counts_per_meeting(tmp_path: Path) -> None:
    report = meeting_effectiveness(_store(tmp_path))
    assert report.total_meetings == 2
    by_id = {m.meeting_id: m for m in report.meetings}
    assert by_id["m1"].decisions == 1
    assert by_id["m1"].commitments == 1
    assert by_id["m1"].tasks == 1
    assert by_id["m2"].open_loops == 2


def test_effectiveness_score(tmp_path: Path) -> None:
    report = meeting_effectiveness(_store(tmp_path))
    by_id = {m.meeting_id: m for m in report.meetings}
    # m1: signal=3, open_loops=0 -> 1.0
    assert by_id["m1"].effectiveness_score == 1.0
    # m2: signal=0, open_loops=2 -> 0.0
    assert by_id["m2"].effectiveness_score == 0.0


def test_structured_outputs(tmp_path: Path) -> None:
    report = meeting_effectiveness(_store(tmp_path))
    by_id = {m.meeting_id: m for m in report.meetings}
    assert by_id["m1"].structured_outputs == 3
    assert by_id["m2"].structured_outputs == 2


def test_meetings_sorted(tmp_path: Path) -> None:
    report = meeting_effectiveness(_store(tmp_path))
    assert [m.meeting_id for m in report.meetings] == ["m1", "m2"]


def test_empty(tmp_path: Path) -> None:
    report = meeting_effectiveness(JSONStore(tmp_path / "e.json"))
    assert report.total_meetings == 0
    assert report.meetings == []
