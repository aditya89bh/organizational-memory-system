"""Tests for the recall CLI command."""

from pathlib import Path

import pytest

from organizational_memory.cli.main import main
from organizational_memory.models import Decision, Task
from organizational_memory.models.enums import DecisionStatus
from organizational_memory.storage.json_store import JSONStore


def _store(tmp_path: Path) -> Path:
    path = tmp_path / "memory.json"
    store = JSONStore(path)
    store.save_record(
        Decision(id="d1", title="Adopt Kubernetes", description="run on kubernetes",
                 owner_id="alice", status=DecisionStatus.ACCEPTED)
    )
    store.save_record(
        Task(id="t1", title="Launch website", description="ship the site",
             owner_id="bob")
    )
    return path


def test_recall_keyword(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _store(tmp_path)
    code = main(["recall", "kubernetes", "--store", str(path)])
    assert code == 0
    out = capsys.readouterr().out
    assert "d1" in out
    assert "t1" not in out


def test_recall_no_results(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _store(tmp_path)
    code = main(["recall", "nonexistentterm", "--store", str(path)])
    assert code == 0
    assert "No results." in capsys.readouterr().out


def test_recall_type_filter(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _store(tmp_path)
    code = main(["recall", "type:task launch", "--store", str(path)])
    assert code == 0
    out = capsys.readouterr().out
    assert "t1" in out
    assert "d1" not in out


def test_recall_explain(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _store(tmp_path)
    code = main(["recall", "kubernetes", "--store", str(path), "--explain"])
    assert code == 0
    assert "     - " in capsys.readouterr().out


def test_recall_negative_limit(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = _store(tmp_path)
    code = main(["recall", "kubernetes", "--store", str(path), "--limit", "-1"])
    assert code == 1


def test_recall_offset_pagination(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = _store(tmp_path)
    code = main(
        ["recall", "kubernetes", "--store", str(path), "--limit", "1", "--offset", "1"]
    )
    assert code == 0
