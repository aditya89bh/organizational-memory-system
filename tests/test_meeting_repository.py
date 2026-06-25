"""Tests for the meeting repository."""

from pathlib import Path

from organizational_memory.models import Meeting
from organizational_memory.storage.json_store import JSONStore
from organizational_memory.storage.meeting_repository import MeetingRepository
from organizational_memory.utils.time import utc_now


def _repo(tmp_path: Path) -> MeetingRepository:
    return MeetingRepository(JSONStore(tmp_path / "memory.json"))


def _meeting() -> Meeting:
    return Meeting(title="Weekly Sync", started_at=utc_now())


def test_add_get(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    meeting = repo.add(_meeting())
    fetched = repo.get(meeting.id)
    assert fetched is not None
    assert fetched.title == "Weekly Sync"


def test_list(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    repo.add(_meeting())
    repo.add(_meeting())
    assert len(repo.list()) == 2


def test_update(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    meeting = repo.add(_meeting())
    meeting.title = "Renamed"
    repo.update(meeting)
    fetched = repo.get(meeting.id)
    assert fetched is not None
    assert fetched.title == "Renamed"


def test_delete(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    meeting = repo.add(_meeting())
    assert repo.delete(meeting.id) is True
    assert repo.get(meeting.id) is None
