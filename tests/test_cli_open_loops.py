"""Tests for the open-loops CLI command."""

from datetime import timedelta
from pathlib import Path

import pytest

from organizational_memory.cli.main import main
from organizational_memory.models import OpenLoop
from organizational_memory.models.enums import OpenLoopStatus
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import format_timestamp, utc_now

NOW_DT = utc_now()
NOW = format_timestamp(NOW_DT)


def _store(tmp_path: Path) -> Path:
    path = tmp_path / "memory.json"
    store = JSONStore(path)
    store.save_record(
        OpenLoop(id="o1", question="scale?", owner_id="alice",
                 source_meeting_id="m1", status=OpenLoopStatus.OPEN,
                 created_at=NOW_DT - timedelta(days=20),
                 due_at=NOW_DT - timedelta(days=1))
    )
    store.save_record(
        OpenLoop(id="o2", question="budget?", owner_id="bob",
                 source_meeting_id="m2", status=OpenLoopStatus.RESOLVED,
                 created_at=NOW_DT - timedelta(days=5))
    )
    store.save_record(
        OpenLoop(id="o3", question="vendor?", owner_id="alice",
                 source_meeting_id="m1", status=OpenLoopStatus.OPEN,
                 created_at=NOW_DT - timedelta(days=2))
    )
    return path


def test_list_all(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _store(tmp_path)
    assert main(["open-loops", "--store", str(path), "--now", NOW]) == 0
    assert "3 open loop(s)" in capsys.readouterr().out


def test_unresolved(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _store(tmp_path)
    main(["open-loops", "--store", str(path), "--unresolved", "--now", NOW])
    out = capsys.readouterr().out
    assert "o1" in out and "o3" in out and "o2" not in out


def test_overdue(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _store(tmp_path)
    main(["open-loops", "--store", str(path), "--overdue", "--now", NOW])
    out = capsys.readouterr().out
    assert "o1" in out and "o3" not in out


def test_filter_meeting(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _store(tmp_path)
    main(["open-loops", "--store", str(path), "--meeting", "m2", "--now", NOW])
    out = capsys.readouterr().out
    assert "o2" in out and "o1" not in out


def test_oldest_first(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _store(tmp_path)
    main(["open-loops", "--store", str(path), "--oldest-first", "--now", NOW])
    out = capsys.readouterr().out
    assert out.index("o1") < out.index("o2") < out.index("o3")


def test_empty(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "empty.json"
    JSONStore(path)
    main(["open-loops", "--store", str(path)])
    assert "No open loops." in capsys.readouterr().out
