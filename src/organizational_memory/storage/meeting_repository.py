"""Meeting-specific repository."""

from organizational_memory.models import Meeting
from organizational_memory.storage.repository import Repository
from organizational_memory.storage.store import MemoryStore


class MeetingRepository(Repository[Meeting]):
    """Typed storage operations for :class:`Meeting` records."""

    def __init__(self, store: MemoryStore) -> None:
        super().__init__(store, Meeting)
