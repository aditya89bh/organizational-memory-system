"""Tests for the decision repository."""

from pathlib import Path

from organizational_memory.models import Decision
from organizational_memory.storage.decision_repository import DecisionRepository
from organizational_memory.storage.json_store import JSONStore


def _repo(tmp_path: Path) -> DecisionRepository:
    return DecisionRepository(JSONStore(tmp_path / "memory.json"))


def test_add_get(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    decision = repo.add(Decision(title="Ship", description="ship it"))
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
    decision = repo.add(Decision(title="a", description="a"))
    decision.title = "Renamed"
    repo.update(decision)
    fetched = repo.get(decision.id)
    assert fetched is not None
    assert fetched.title == "Renamed"


def test_delete(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    decision = repo.add(Decision(title="a", description="a"))
    assert repo.delete(decision.id) is True
    assert repo.get(decision.id) is None
