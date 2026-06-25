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
from organizational_memory.recall.explanations import (
    Explanation,
    explain_result,
    explain_results,
)
from organizational_memory.recall.keyword_search import (
    KeywordMatch,
    extract_text_fields,
    score_record,
    search_keywords,
    tokenize,
)
from organizational_memory.recall.open_loop_search import search_open_loops
from organizational_memory.recall.participant_search import search_participants
from organizational_memory.recall.relationship_search import search_relationships
from organizational_memory.recall.task_search import search_tasks
from organizational_memory.recall.timeline_search import (
    TIMELINE_TYPES,
    search_timeline,
    timeline_timestamp,
)

__all__ = [
    "TIMELINE_TYPES",
    "Explanation",
    "KeywordMatch",
    "RecallEngine",
    "RecallResult",
    "explain_result",
    "explain_results",
    "extract_text_fields",
    "score_record",
    "search_commitments",
    "search_decisions",
    "search_keywords",
    "search_open_loops",
    "search_participants",
    "search_relationships",
    "search_tasks",
    "search_timeline",
    "timeline_timestamp",
    "tokenize",
]
