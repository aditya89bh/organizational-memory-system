"""OpenLoop-specific repository."""

from organizational_memory.models import OpenLoop
from organizational_memory.storage.repository import Repository
from organizational_memory.storage.store import MemoryStore


class OpenLoopRepository(Repository[OpenLoop]):
    """Typed storage operations for :class:`OpenLoop` records."""

    def __init__(self, store: MemoryStore) -> None:
        super().__init__(store, OpenLoop)
