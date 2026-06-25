"""Tests for the report CLI command."""

import json
from pathlib import Path

import pytest

from organizational_memory.cli.main import main
from organizational_memory.models import Commitment, Decision, Meeting, OpenLoop
from organizational_memory.models.enums import CommitmentStatus, DecisionStatus
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import parse_timestamp

NOW = "2026-03-01T00:00:00Z"


def _store(tmp_path: Path) -> Path:
    path = tmp_path / "memory.json"
    store = JSONStore(path)
    store.save_record(
        Meeting(id="m1", title="Kickoff",
                started_at=parse_timestamp("2026-02-20T09:00:00Z"),
                participants=["alice"])
    )
    store.save_record(
        Decision(id="d1", title="Adopt mesh", description="x", owner_id="alice",
                 status=DecisionStatus.ACCEPTED, source_meeting_id="m1")
    )
    store.save_record(
        Commitment(id="c1", owner_id="alice", description="ship",
                   status=CommitmentStatus.PENDING, source_meeting_id="m1")
    )
    store.save_record(
        OpenLoop(id="o1", question="scale?", source_meeting_id="m1")
    )
    return path


def test_report_followup_markdown(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = _store(tmp_path)
    code = main(["report", "follow-up", "--store", str(path), "--now", NOW])
    assert code == 0
    assert "# Follow-up report" in capsys.readouterr().out


def test_report_decisions_json(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = _store(tmp_path)
    code = main(
        ["report", "decisions", "--store", str(path), "--format", "json",
         "--now", NOW]
    )
    assert code == 0
    loaded = json.loads(capsys.readouterr().out)
    assert loaded["title"] == "Decision report"


def test_report_output_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = _store(tmp_path)
    out_path = tmp_path / "report.md"
    code = main(
        ["report", "organizational-memory", "--store", str(path),
         "--output", str(out_path), "--now", NOW]
    )
    assert code == 0
    assert out_path.exists()
    assert "# Organizational memory report" in out_path.read_text(encoding="utf-8")


def test_report_meeting_requires_meeting_id(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = _store(tmp_path)
    code = main(["report", "meeting", "--store", str(path), "--now", NOW])
    assert code == 1
    assert "error:" in capsys.readouterr().out


def test_report_meeting_ok(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = _store(tmp_path)
    code = main(
        ["report", "meeting", "--store", str(path), "--meeting-id", "m1", "--now", NOW]
    )
    assert code == 0
    assert "Meeting summary" in capsys.readouterr().out


def test_report_weekly_requires_window(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = _store(tmp_path)
    code = main(["report", "weekly", "--store", str(path), "--now", NOW])
    assert code == 1
