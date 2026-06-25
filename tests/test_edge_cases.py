"""Edge-case tests across stores, models, parsing, and the CLI."""

from pathlib import Path

import pytest

from organizational_memory.analytics.reporting import generate_report
from organizational_memory.cli.main import main
from organizational_memory.demos.common import InMemoryStore
from organizational_memory.exceptions import ValidationError
from organizational_memory.models import Decision
from organizational_memory.models.enums import DecisionStatus
from organizational_memory.persistence import from_dict
from organizational_memory.recall.keyword_search import search_keywords
from organizational_memory.recall.query_parser import parse_query
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.utils.time import parse_timestamp

FIXED = parse_timestamp("2026-03-01T00:00:00Z")


def _decision(record_id: str = "d1", title: str = "Adopt plan") -> Decision:
    return Decision(
        id=record_id,
        title=title,
        description="A decision.",
        owner_id="alice",
        status=DecisionStatus.ACCEPTED,
        created_at=FIXED,
        updated_at=FIXED,
    )


def test_empty_store_report() -> None:
    store = InMemoryStore()
    report = generate_report(store, now=FIXED)
    assert report is not None
    assert store.list_records() == []


def test_empty_store_recall() -> None:
    assert search_keywords([], "anything") == []


def test_missing_owner_handled_gracefully() -> None:
    store = InMemoryStore()
    unowned = Decision(
        id="d",
        title="Unowned decision",
        description="No owner assigned.",
        owner_id="",
        status=DecisionStatus.ACCEPTED,
        created_at=FIXED,
        updated_at=FIXED,
    )
    store.save_record(unowned)
    report = generate_report(store, now=FIXED)
    assert report is not None
    assert len(store.list_records()) == 1


def test_unknown_status_rejected() -> None:
    data = _decision().to_dict()
    data["status"] = "not-a-real-status"
    with pytest.raises(ValidationError):
        from_dict(Decision, data)


def test_invalid_timestamp_rejected() -> None:
    with pytest.raises(ValueError):
        parse_timestamp("not-a-timestamp")


def test_query_parser_invalid_date() -> None:
    with pytest.raises(ValueError, match="invalid date"):
        parse_query("after:bogus")


def test_duplicate_ids_overwrite() -> None:
    store = InMemoryStore()
    store.save_record(_decision("dup", "First"))
    store.save_record(_decision("dup", "Second"))
    records = store.list_records()
    assert len(records) == 1
    fetched = store.get_record("Decision", "dup")
    assert isinstance(fetched, Decision)
    assert fetched.title == "Second"


def test_corrupted_json_store(tmp_path: Path) -> None:
    bad = tmp_path / "memory.json"
    bad.write_text("{ not valid json", encoding="utf-8")
    with pytest.raises(ValueError):
        JSONStore(bad)


def test_unsupported_export_format() -> None:
    with pytest.raises(SystemExit):
        main(["export", "xml"])


def test_malformed_cli_missing_required() -> None:
    with pytest.raises(SystemExit):
        main(["report"])


def test_unknown_cli_command() -> None:
    with pytest.raises(SystemExit):
        main(["does-not-exist"])
