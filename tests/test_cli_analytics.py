"""Tests for the analytics CLI command."""

import json
from datetime import timedelta
from pathlib import Path

import pytest

from organizational_memory.cli.main import main
from organizational_memory.models import Commitment, Decision, OpenLoop
from organizational_memory.models.enums import CommitmentStatus, DecisionStatus
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import format_timestamp, utc_now

NOW_DT = utc_now()
NOW = format_timestamp(NOW_DT)


def _store(tmp_path: Path) -> Path:
    path = tmp_path / "memory.json"
    store = JSONStore(path)
    store.save_record(
        Decision(id="d1", title="Adopt mesh", description="x", owner_id="alice",
                 status=DecisionStatus.ACCEPTED)
    )
    store.save_record(
        Commitment(id="c1", owner_id="alice", description="ship",
                   status=CommitmentStatus.PENDING,
                   created_at=NOW_DT - timedelta(days=10),
                   due_at=NOW_DT - timedelta(days=1))
    )
    store.save_record(OpenLoop(id="o1", question="scale?"))
    return path


def test_analytics_text(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _store(tmp_path)
    code = main(["analytics", "--store", str(path), "--now", NOW])
    assert code == 0
    out = capsys.readouterr().out
    assert "Analytics summary" in out
    assert "Memory health" in out
    assert "Bottlenecks" in out
    assert "Owner load" in out


def test_analytics_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _store(tmp_path)
    code = main(["analytics", "--store", str(path), "--format", "json", "--now", NOW])
    assert code == 0
    loaded = json.loads(capsys.readouterr().out)
    assert "summary" in loaded
    assert loaded["summary"]["decisions"] == 1


def test_analytics_bad_now(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _store(tmp_path)
    code = main(["analytics", "--store", str(path), "--now", "not-a-date"])
    assert code == 1
    assert "error:" in capsys.readouterr().out


def test_analytics_deterministic(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = _store(tmp_path)
    main(["analytics", "--store", str(path), "--format", "json", "--now", NOW])
    first = capsys.readouterr().out
    main(["analytics", "--store", str(path), "--format", "json", "--now", NOW])
    second = capsys.readouterr().out
    assert first == second
