"""Verify the committed CLI capture files stay deterministic."""

import contextlib
import io
import os
import tempfile
from collections.abc import Sequence
from pathlib import Path

import pytest

from organizational_memory.cli.main import main

_ROOT = Path(__file__).resolve().parents[1]
_CAPTURES = _ROOT / "docs" / "assets" / "cli_captures"
_NOW = "2026-03-02T09:00:00Z"
_DATASET = str(_ROOT / "examples" / "datasets" / "startup_operating_memory.json")


def _capture(args: Sequence[str]) -> str:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        assert main(list(args)) == 0
    return buffer.getvalue()


def test_recall_capture_matches() -> None:
    actual = _capture(["recall", "launch", "--store", _DATASET])
    assert actual == (_CAPTURES / "recall_output.txt").read_text(encoding="utf-8")


def test_analytics_capture_matches() -> None:
    actual = _capture(["analytics", "--store", _DATASET, "--now", _NOW])
    assert actual == (_CAPTURES / "analytics_output.txt").read_text(encoding="utf-8")


def test_report_capture_matches() -> None:
    actual = _capture(["report", "follow-up", "--store", _DATASET, "--now", _NOW])
    assert actual == (_CAPTURES / "report_output.md").read_text(encoding="utf-8")


def test_demo_capture_matches() -> None:
    actual = _capture(["demo", "startup"])
    assert actual == (_CAPTURES / "demo_output.txt").read_text(encoding="utf-8")


def test_ingest_capture_matches() -> None:
    transcript = "examples/transcripts/startup_product_meeting.txt"
    previous = Path.cwd()
    os.chdir(_ROOT)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            store = str(Path(tmp) / "memory.json")
            actual = _capture(["ingest", transcript, "--store", store])
    finally:
        os.chdir(previous)
    assert actual == (_CAPTURES / "ingest_output.txt").read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "name",
    [
        "ingest_output.txt",
        "recall_output.txt",
        "analytics_output.txt",
        "report_output.md",
        "demo_output.txt",
    ],
)
def test_capture_files_present(name: str) -> None:
    assert (_CAPTURES / name).read_text(encoding="utf-8").strip()
