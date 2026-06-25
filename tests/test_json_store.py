"""Tests for the JSON-file-backed memory store."""

import json
from pathlib import Path

from organizational_memory.models import Decision, Task
from organizational_memory.storage.json_store import JSONStore


def test_empty_store_initializes_file(tmp_path: Path) -> None:
    path = tmp_path / "memory.json"
    JSONStore(path)
    assert path.exists()
    assert json.loads(path.read_text(encoding="utf-8")) == {"records": {}}


def test_save_and_get(tmp_path: Path) -> None:
    store = JSONStore(tmp_path / "memory.json")
    decision = Decision(title="Ship", description="Ship on Friday")
    store.save_record(decision)
    fetched = store.get_record("Decision", decision.id)
    assert fetched is not None
    assert isinstance(fetched, Decision)
    assert fetched.title == "Ship"


def test_deterministic_output(tmp_path: Path) -> None:
    path = tmp_path / "memory.json"
    store = JSONStore(path)
    decision_a = Decision(id="a", title="a", description="a")
    decision_b = Decision(id="b", title="b", description="b")
    store.save_record(decision_b)
    store.save_record(decision_a)
    first = path.read_text(encoding="utf-8")
    store.save_record(decision_a)
    assert path.read_text(encoding="utf-8") == first
    assert first.index('"a"') < first.index('"b"')


def test_list_records_sorted(tmp_path: Path) -> None:
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(Task(id="t2", title="t", description="d", owner_id="x"))
    store.save_record(Decision(id="d1", title="a", description="a"))
    names = [type(r).__name__ for r in store.list_records()]
    assert names == ["Decision", "Task"]


def test_delete_and_clear(tmp_path: Path) -> None:
    store = JSONStore(tmp_path / "memory.json")
    decision = Decision(title="a", description="a")
    store.save_record(decision)
    assert store.delete_record("Decision", decision.id) is True
    assert store.delete_record("Decision", decision.id) is False
    store.save_record(decision)
    store.clear()
    assert store.list_records() == []


def test_persists_across_reopen(tmp_path: Path) -> None:
    path = tmp_path / "memory.json"
    first = JSONStore(path)
    decision = Decision(title="Persist", description="survive reload")
    first.save_record(decision)

    second = JSONStore(path)
    fetched = second.get_record("Decision", decision.id)
    assert fetched is not None
    assert fetched.id == decision.id


def test_preserves_enum_and_datetime(tmp_path: Path) -> None:
    store = JSONStore(tmp_path / "memory.json")
    decision = Decision(title="a", description="a")
    store.save_record(decision)
    reloaded = JSONStore(tmp_path / "memory.json").get_record("Decision", decision.id)
    assert reloaded is not None
    assert isinstance(reloaded, Decision)
    assert reloaded.status == decision.status
    assert reloaded.created_at == decision.created_at
