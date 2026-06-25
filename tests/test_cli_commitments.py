"""Tests for the commitments CLI command."""

from datetime import timedelta
from pathlib import Path

import pytest

from organizational_memory.cli.main import main
from organizational_memory.models import Commitment
from organizational_memory.models.enums import CommitmentStatus
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import format_timestamp, utc_now

NOW_DT = utc_now()
NOW = format_timestamp(NOW_DT)


def _store(tmp_path: Path) -> Path:
    path = tmp_path / "memory.json"
    store = JSONStore(path)
    store.save_record(
        Commitment(id="c1", owner_id="alice", description="ship",
                   status=CommitmentStatus.PENDING,
                   created_at=NOW_DT - timedelta(days=10),
                   due_at=NOW_DT - timedelta(days=1))
    )
    store.save_record(
        Commitment(id="c2", owner_id="bob", description="done",
                   status=CommitmentStatus.COMPLETED)
    )
    store.save_record(
        Commitment(id="c3", owner_id="alice", description="plan",
                   status=CommitmentStatus.IN_PROGRESS)
    )
    return path


def test_list_all(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _store(tmp_path)
    assert main(["commitments", "--store", str(path), "--now", NOW]) == 0
    out = capsys.readouterr().out
    assert "3 commitment(s)" in out


def test_filter_owner(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _store(tmp_path)
    main(["commitments", "--store", str(path), "--owner", "alice", "--now", NOW])
    out = capsys.readouterr().out
    assert "c1" in out and "c3" in out and "c2" not in out


def test_filter_open(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _store(tmp_path)
    main(["commitments", "--store", str(path), "--open", "--now", NOW])
    out = capsys.readouterr().out
    assert "c2" not in out


def test_filter_overdue(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _store(tmp_path)
    main(["commitments", "--store", str(path), "--overdue", "--now", NOW])
    out = capsys.readouterr().out
    assert "c1" in out and "c3" not in out


def test_filter_status(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _store(tmp_path)
    main(["commitments", "--store", str(path), "--status", "completed", "--now", NOW])
    out = capsys.readouterr().out
    assert "c2" in out and "c1" not in out


def test_empty(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "empty.json"
    JSONStore(path)
    main(["commitments", "--store", str(path)])
    assert "No commitments." in capsys.readouterr().out
