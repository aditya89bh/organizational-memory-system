"""Tests for report templates."""

from pathlib import Path

from organizational_memory.models import Commitment, Decision, Meeting, OpenLoop
from organizational_memory.models.enums import DecisionStatus
from organizational_memory.reports import templates
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import parse_timestamp, utc_now

START = parse_timestamp("2026-02-02T00:00:00Z")
END = parse_timestamp("2026-02-09T00:00:00Z")


def _store(tmp_path: Path) -> JSONStore:
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(
        Meeting(id="m1", title="Kickoff",
                started_at=parse_timestamp("2026-02-03T09:00:00Z"),
                participants=["alice"])
    )
    store.save_record(
        Decision(id="d1", title="Adopt mesh", description="x", owner_id="alice",
                 status=DecisionStatus.ACCEPTED, source_meeting_id="m1",
                 decided_at=parse_timestamp("2026-02-03T10:00:00Z"))
    )
    store.save_record(
        Commitment(id="c1", owner_id="alice", description="ship",
                   source_meeting_id="m1",
                   created_at=parse_timestamp("2026-02-03T10:00:00Z"))
    )
    store.save_record(
        OpenLoop(id="o1", question="scale?", source_meeting_id="m1",
                 created_at=parse_timestamp("2026-02-03T10:00:00Z"))
    )
    return store


def test_executive_summary_sections(tmp_path: Path) -> None:
    report = templates.executive_summary(_store(tmp_path), now=utc_now())
    assert report.title == "Executive summary"
    titles = [s.title for s in report.sections]
    assert titles == ["Memory health", "Key decisions", "Unresolved loops",
                      "Bottlenecks"]


def test_meeting_summary_template(tmp_path: Path) -> None:
    report = templates.meeting_summary_template(_store(tmp_path), "m1", now=utc_now())
    titles = [s.title for s in report.sections]
    assert titles == ["Participants", "Decisions", "Commitments", "Open loops"]


def test_weekly_review(tmp_path: Path) -> None:
    report = templates.weekly_review(_store(tmp_path), start=START, end=END)
    assert report.title == "Weekly review"
    assert report.section("Memory health") is not None


def test_open_loop_review(tmp_path: Path) -> None:
    report = templates.open_loop_review(_store(tmp_path), now=utc_now())
    titles = [s.title for s in report.sections]
    assert titles == ["Unresolved", "Oldest unresolved", "Overdue"]


def test_follow_up_memo(tmp_path: Path) -> None:
    report = templates.follow_up_memo(_store(tmp_path), now=utc_now())
    assert report.title == "Follow-up memo"
    assert report.section("Needs action") is not None


def test_select_sections_skips_missing(tmp_path: Path) -> None:
    source = templates.executive_summary(_store(tmp_path), now=utc_now())
    curated = templates.select_sections(
        source, ("Memory health", "Nonexistent"), title="Curated"
    )
    assert [s.title for s in curated.sections] == ["Memory health"]
