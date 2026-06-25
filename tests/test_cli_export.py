"""Tests for the export CLI command."""

import json
from pathlib import Path

import pytest

from organizational_memory.cli.main import main
from organizational_memory.models import Commitment, Decision, OpenLoop
from organizational_memory.models.enums import CommitmentStatus, DecisionStatus
from organizational_memory.storage.json_store import JSONStore

NOW = "2026-03-01T00:00:00Z"


def _store(tmp_path: Path) -> Path:
    path = tmp_path / "memory.json"
    store = JSONStore(path)
    store.save_record(
        Decision(id="d1", title="Adopt mesh", description="x", owner_id="alice",
                 status=DecisionStatus.ACCEPTED)
    )
    store.save_record(
        Commitment(id="c1", owner_id="alice", description="ship",
                   status=CommitmentStatus.PENDING)
    )
    store.save_record(OpenLoop(id="o1", question="scale?"))
    return path


def test_snapshot_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _store(tmp_path)
    code = main(["export", "json", "--store", str(path)])
    assert code == 0
    loaded = json.loads(capsys.readouterr().out)
    assert "Decision" in loaded
    assert loaded["Decision"][0]["id"] == "d1"


def test_snapshot_csv(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _store(tmp_path)
    code = main(["export", "csv", "--store", str(path)])
    assert code == 0
    out = capsys.readouterr().out
    assert "type,id,label,owner_id,status,due_at" in out
    assert "Decision,d1" in out


def test_snapshot_markdown_to_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = _store(tmp_path)
    out_path = tmp_path / "snap.md"
    code = main(["export", "markdown", "--store", str(path), "--output", str(out_path)])
    assert code == 0
    text = out_path.read_text(encoding="utf-8")
    assert "# Memory snapshot" in text
    assert "| Decision | d1 |" in text


def test_report_target_json(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = _store(tmp_path)
    code = main(
        ["export", "json", "--store", str(path), "--target", "report",
         "--report-type", "decisions", "--now", NOW]
    )
    assert code == 0
    loaded = json.loads(capsys.readouterr().out)
    assert loaded["title"] == "Decision report"


def test_report_target_csv(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _store(tmp_path)
    code = main(
        ["export", "csv", "--store", str(path), "--target", "report",
         "--report-type", "decisions", "--now", NOW]
    )
    assert code == 0


def test_report_meeting_missing_id_errors(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = _store(tmp_path)
    code = main(
        ["export", "json", "--store", str(path), "--target", "report",
         "--report-type", "meeting", "--now", NOW]
    )
    assert code == 1
    assert "error:" in capsys.readouterr().out
