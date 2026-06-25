"""Deterministic recall and query engine for organizational memory.

This package retrieves records persisted by the Phase 4 storage layer using
deterministic search and ranking only. It does not use embeddings, LLMs,
external APIs, or any network access.
"""

from organizational_memory.recall.engine import (
    RecallEngine,
    RecallResult,
)

__all__ = [
    "RecallEngine",
    "RecallResult",
]
