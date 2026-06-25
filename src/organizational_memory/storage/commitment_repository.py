"""Commitment-specific repository."""

from organizational_memory.models import Commitment
from organizational_memory.storage.repository import Repository
from organizational_memory.storage.store import MemoryStore


class CommitmentRepository(Repository[Commitment]):
    """Typed storage operations for :class:`Commitment` records."""

    def __init__(self, store: MemoryStore) -> None:
        super().__init__(store, Commitment)
