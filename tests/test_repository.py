"""Tests for the generic repository abstraction."""

from pathlib import Path

from organizational_memory.models import Decision
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.storage.repository import Repository


def _repo(tmp_path: Path) -> Repository[Decision]:
    return Repository(JSONStore(tmp_path / "memory.json"), Decision)


def test_add_and_get(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    decision = Decision(title="Ship", description="ship it")
    assert repo.add(decision) is decision
    fetched = repo.get(decision.id)
    assert fetched is not None
    assert fetched.title == "Ship"


def test_list(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    repo.add(Decision(title="a", description="a"))
    repo.add(Decision(title="b", description="b"))
    assert len(repo.list()) == 2


def test_update(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    decision = Decision(title="a", description="a")
    repo.add(decision)
    decision.title = "updated"
    repo.update(decision)
    fetched = repo.get(decision.id)
    assert fetched is not None
    assert fetched.title == "updated"


def test_delete_and_exists(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    decision = Decision(title="a", description="a")
    repo.add(decision)
    assert repo.exists(decision.id) is True
    assert repo.delete(decision.id) is True
    assert repo.exists(decision.id) is False
    assert repo.delete(decision.id) is False


def test_record_type_property(tmp_path: Path) -> None:
    assert _repo(tmp_path).record_type is Decision
