"""Tests for the task repository."""

from pathlib import Path

from organizational_memory.models import Task
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.storage.task_repository import TaskRepository


def _repo(tmp_path: Path) -> TaskRepository:
    return TaskRepository(JSONStore(tmp_path / "memory.json"))


def _task() -> Task:
    return Task(title="Write docs", description="write the docs", owner_id="alice")


def test_add_get(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    task = repo.add(_task())
    fetched = repo.get(task.id)
    assert fetched is not None
    assert fetched.title == "Write docs"


def test_list(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    repo.add(_task())
    repo.add(_task())
    assert len(repo.list()) == 2


def test_update(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    task = repo.add(_task())
    task.title = "Updated"
    repo.update(task)
    fetched = repo.get(task.id)
    assert fetched is not None
    assert fetched.title == "Updated"


def test_delete(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    task = repo.add(_task())
    assert repo.delete(task.id) is True
    assert repo.get(task.id) is None
