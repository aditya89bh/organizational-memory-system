"""Deterministic recall and query engine for organizational memory.

This package retrieves records persisted by the Phase 4 storage layer using
deterministic search and ranking only. It does not use embeddings, LLMs,
external APIs, or any network access.
"""

from organizational_memory.recall.commitment_search import search_commitments
from organizational_memory.recall.decision_search import search_decisions
from organizational_memory.recall.engine import (
    RecallEngine,
    RecallResult,
)
from organizational_memory.recall.keyword_search import (
    KeywordMatch,
    extract_text_fields,
    score_record,
    search_keywords,
    tokenize,
)
from organizational_memory.recall.task_search import search_tasks

__all__ = [
    "KeywordMatch",
    "RecallEngine",
    "RecallResult",
    "extract_text_fields",
    "score_record",
    "search_commitments",
    "search_decisions",
    "search_keywords",
    "search_tasks",
    "tokenize",
]
