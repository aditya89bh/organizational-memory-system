"""Decision-specific repository."""

from organizational_memory.models import Decision
from organizational_memory.storage.repository import Repository
from organizational_memory.storage.store import MemoryStore


class DecisionRepository(Repository[Decision]):
    """Typed storage operations for :class:`Decision` records."""

    def __init__(self, store: MemoryStore) -> None:
        super().__init__(store, Decision)
