"""Tests for the ingest CLI command."""

from pathlib import Path

import pytest

from organizational_memory.cli.main import main
from organizational_memory.storage.json_store import JSONStore

TRANSCRIPT = """# Product Sync

Attendees: Aditya, Priya, Rahul

[10:00] Aditya: We decided to launch the beta on Friday.
[10:02] Priya: I will prepare the onboarding docs.
[10:04] Rahul: The launch is blocked by the security review.
[10:05] Aditya: What is our rollback plan?
Risk: the vendor might miss the deadline.
TODO: finalize the pricing page.
Topic: Beta launch
"""


def _write_transcript(tmp_path: Path) -> Path:
    path = tmp_path / "meeting.txt"
    path.write_text(TRANSCRIPT, encoding="utf-8")
    return path


def test_ingest_persists_records(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    transcript = _write_transcript(tmp_path)
    store_path = tmp_path / "memory.json"
    code = main(["ingest", str(transcript), "--store", str(store_path)])
    assert code == 0
    out = capsys.readouterr().out
    assert "Ingested" in out
    assert "decisions: 1" in out

    store = JSONStore(store_path)
    assert len(store.list_records("Decision")) == 1
    assert len(store.list_records("Commitment")) == 1
    assert len(store.list_records("OpenLoop")) == 1


def test_ingest_with_meeting_id_tags_records(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    transcript = _write_transcript(tmp_path)
    store_path = tmp_path / "memory.json"
    code = main(
        ["ingest", str(transcript), "--store", str(store_path), "--meeting-id", "m1"]
    )
    assert code == 0
    store = JSONStore(store_path)
    meetings = store.list_records("Meeting")
    assert len(meetings) == 1
    decisions = store.list_records("Decision")
    assert all(getattr(d, "source_meeting_id", None) == "m1" for d in decisions)


def test_ingest_missing_file_returns_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = main(["ingest", str(tmp_path / "nope.txt")])
    assert code == 1
    assert "error:" in capsys.readouterr().out


def test_ingest_sqlite_backend(tmp_path: Path) -> None:
    transcript = _write_transcript(tmp_path)
    store_path = tmp_path / "memory.db"
    code = main(
        ["ingest", str(transcript), "--store", str(store_path), "--backend", "sqlite"]
    )
    assert code == 0
    from organizational_memory.storage.sqlite_store import SQLiteStore

    store = SQLiteStore(str(store_path))
    assert len(store.list_records("Decision")) == 1
