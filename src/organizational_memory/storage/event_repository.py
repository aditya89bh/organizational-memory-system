"""MemoryEvent-specific repository."""

from organizational_memory.models import MemoryEvent
from organizational_memory.storage.repository import Repository
from organizational_memory.storage.store import MemoryStore


class EventRepository(Repository[MemoryEvent]):
    """Typed storage operations for :class:`MemoryEvent` records."""

    def __init__(self, store: MemoryStore) -> None:
        super().__init__(store, MemoryEvent)
