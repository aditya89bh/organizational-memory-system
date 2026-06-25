"""End-to-end CLI integration tests across storage backends."""

import json
from pathlib import Path

import pytest

from organizational_memory.cli.main import main
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.storage.sqlite_store import SQLiteStore

TRANSCRIPT = """# Quarter Kickoff

Attendees: Aditya, Priya, Rahul

[09:00] Aditya: We decided to launch the beta on Friday.
[09:02] Priya: I will prepare the onboarding docs.
[09:04] Rahul: The launch is blocked by the security review.
[09:05] Aditya: What is our rollback plan?
Risk: the vendor might miss the deadline.
TODO: finalize the pricing page.
Topic: Beta launch
"""

NOW = "2026-03-01T00:00:00Z"


def _transcript(tmp_path: Path) -> Path:
    path = tmp_path / "kickoff.txt"
    path.write_text(TRANSCRIPT, encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("backend", "store_name"), [("json", "memory.json"), ("sqlite", "memory.db")]
)
def test_end_to_end_pipeline(
    backend: str,
    store_name: str,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    transcript = _transcript(tmp_path)
    store_path = tmp_path / store_name
    common = ["--store", str(store_path), "--backend", backend]

    assert main(["ingest", str(transcript), *common, "--meeting-id", "m1"]) == 0
    assert "Ingested" in capsys.readouterr().out

    assert main(["recall", "launch", *common]) == 0
    recall_out = capsys.readouterr().out
    assert "Decision" in recall_out

    assert main(["analytics", *common, "--now", NOW]) == 0
    assert "Analytics summary" in capsys.readouterr().out

    assert main(["report", "meeting", *common, "--meeting-id", "m1", "--now", NOW]) == 0
    assert "Meeting summary" in capsys.readouterr().out

    out_file = tmp_path / "snapshot.json"
    assert main(["export", "json", *common, "--output", str(out_file)]) == 0
    snapshot = json.loads(out_file.read_text(encoding="utf-8"))
    assert "Decision" in snapshot

    store = (
        JSONStore(store_path)
        if backend == "json"
        else SQLiteStore(str(store_path))
    )
    assert store.list_records("Decision")
    assert store.list_records("Meeting")


def test_report_export_roundtrip(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    transcript = _transcript(tmp_path)
    store_path = tmp_path / "memory.json"
    common = ["--store", str(store_path)]
    assert main(["ingest", str(transcript), *common, "--meeting-id", "m1"]) == 0
    capsys.readouterr()

    md_file = tmp_path / "report.md"
    assert main(
        ["export", "markdown", *common, "--target", "report",
         "--report-type", "follow-up", "--now", NOW, "--output", str(md_file)]
    ) == 0
    assert md_file.read_text(encoding="utf-8").startswith("# Follow-up report")
