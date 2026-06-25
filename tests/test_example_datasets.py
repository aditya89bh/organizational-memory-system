"""Validation tests for the bundled example datasets."""

from pathlib import Path

import pytest

from organizational_memory.storage.json_store import JSONStore

_DATASETS_DIR = Path(__file__).resolve().parents[1] / "examples" / "datasets"

_EXPECTED_TOTALS = {
    "startup_operating_memory.json": 14,
    "sprint_operating_memory.json": 15,
    "board_operating_memory.json": 12,
    "company_memory_full.json": 56,
}


@pytest.mark.parametrize("name", sorted(_EXPECTED_TOTALS))
def test_dataset_loads_and_decodes(name: str) -> None:
    store = JSONStore(_DATASETS_DIR / name)
    records = store.list_records()
    assert len(records) == _EXPECTED_TOTALS[name]
    for record in records:
        assert record.id


def test_company_dataset_has_all_meetings() -> None:
    store = JSONStore(_DATASETS_DIR / "company_memory_full.json")
    meeting_ids = {meeting.id for meeting in store.list_records("Meeting")}
    assert {"startup", "sprint", "board", "allhands"} <= meeting_ids


def test_company_dataset_has_overdue_commitment() -> None:
    store = JSONStore(_DATASETS_DIR / "company_memory_full.json")
    ids = {commitment.id for commitment in store.list_records("Commitment")}
    assert "allhands-overdue-1" in ids
