"""Tests for the load-test helpers."""

import importlib.util
import sys
from pathlib import Path
from typing import Any

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_load_tests.py"


def _load() -> Any:
    spec = importlib.util.spec_from_file_location("load_tests", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


lt = _load()


def test_generate_transcript_deterministic() -> None:
    assert lt.generate_transcript(3) == lt.generate_transcript(3)
    assert "plan 3" in lt.generate_transcript(3)


def test_ingest_many_persists() -> None:
    store = lt.ingest_many(5)
    records = store.list_records()
    assert len(records) > 0
    meeting_ids = {getattr(r, "source_meeting_id", None) for r in records}
    assert "meeting-0" in meeting_ids


def test_run_aggregates() -> None:
    result = lt.run(6)
    assert result.meetings == 6
    assert result.records_persisted > 0
    assert result.recall_hits > 0
    assert result.report_sections >= 0


def test_run_is_deterministic() -> None:
    first = lt.run(4)
    second = lt.run(4)
    assert first == second


def test_format_report() -> None:
    text = lt.format_report(lt.run(3))
    assert "Load test" in text
    assert "records_persisted" in text


def test_main() -> None:
    assert lt.main(["3"]) == 0
