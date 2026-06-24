"""Tests for base schemas."""

from dataclasses import dataclass

from organizational_memory.schemas import BaseRecord
from organizational_memory.utils.time import parse_timestamp


@dataclass(kw_only=True)
class Note(BaseRecord):
    text: str


def test_records_get_unique_ids() -> None:
    first = Note(text="a")
    second = Note(text="b")
    assert first.id != second.id


def test_timestamps_are_timezone_aware() -> None:
    note = Note(text="hello")
    assert note.created_at.tzinfo is not None
    assert note.updated_at.tzinfo is not None


def test_touch_advances_updated_at() -> None:
    note = Note(text="hello")
    original = note.updated_at
    note.touch()
    assert note.updated_at >= original


def test_to_dict_includes_subclass_fields() -> None:
    note = Note(text="hello", id="fixed-id")
    data = note.to_dict()
    assert data["id"] == "fixed-id"
    assert data["text"] == "hello"
    parse_timestamp(data["created_at"])


def test_to_json_round_trips() -> None:
    note = Note(text="hello")
    payload = note.to_json(sort_keys=True)
    assert '"text": "hello"' in payload
