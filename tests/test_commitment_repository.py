"""Tests for the commitment repository."""

from pathlib import Path

from organizational_memory.models import Commitment
from organizational_memory.storage.commitment_repository import (
    CommitmentRepository,
)
from organizational_memory.storage.json_store import JSONStore


def _repo(tmp_path: Path) -> CommitmentRepository:
    return CommitmentRepository(JSONStore(tmp_path / "memory.json"))


def test_add_get(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    commitment = repo.add(Commitment(owner_id="alice", description="draft"))
    fetched = repo.get(commitment.id)
    assert fetched is not None
    assert fetched.owner_id == "alice"


def test_list(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    repo.add(Commitment(owner_id="a", description="a"))
    repo.add(Commitment(owner_id="b", description="b"))
    assert len(repo.list()) == 2


def test_update(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    commitment = repo.add(Commitment(owner_id="a", description="draft"))
    commitment.description = "final"
    repo.update(commitment)
    fetched = repo.get(commitment.id)
    assert fetched is not None
    assert fetched.description == "final"


def test_delete(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    commitment = repo.add(Commitment(owner_id="a", description="a"))
    assert repo.delete(commitment.id) is True
    assert repo.get(commitment.id) is None
