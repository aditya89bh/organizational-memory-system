"""Task-specific repository."""

from organizational_memory.models import Task
from organizational_memory.storage.repository import Repository
from organizational_memory.storage.store import MemoryStore


class TaskRepository(Repository[Task]):
    """Typed storage operations for :class:`Task` records."""

    def __init__(self, store: MemoryStore) -> None:
        super().__init__(store, Task)
