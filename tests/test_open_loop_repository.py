"""Tests for the open loop repository."""

from pathlib import Path

from organizational_memory.models import OpenLoop
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.storage.open_loop_repository import OpenLoopRepository


def _repo(tmp_path: Path) -> OpenLoopRepository:
    return OpenLoopRepository(JSONStore(tmp_path / "memory.json"))


def test_add_get(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    loop = repo.add(OpenLoop(question="Who owns billing?"))
    fetched = repo.get(loop.id)
    assert fetched is not None
    assert fetched.question == "Who owns billing?"


def test_list(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    repo.add(OpenLoop(question="a?"))
    repo.add(OpenLoop(question="b?"))
    assert len(repo.list()) == 2


def test_update(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    loop = repo.add(OpenLoop(question="a?"))
    loop.question = "updated?"
    repo.update(loop)
    fetched = repo.get(loop.id)
    assert fetched is not None
    assert fetched.question == "updated?"


def test_delete(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    loop = repo.add(OpenLoop(question="a?"))
    assert repo.delete(loop.id) is True
    assert repo.get(loop.id) is None
