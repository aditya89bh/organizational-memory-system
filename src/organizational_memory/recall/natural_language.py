"""Conservative, deterministic natural-language-like recall.

This maps a small set of common question shapes onto structured recall using
rule-based heuristics only -- there is no LLM, embedding, or network call. The
mapping is intentionally conservative: unrecognized questions fall back to plain
keyword search so behavior stays predictable.
"""

from dataclasses import dataclass
from datetime import datetime

from organizational_memory.recall.commitment_search import search_commitments
from organizational_memory.recall.decision_search import search_decisions
from organizational_memory.recall.engine import RecallResult
from organizational_memory.recall.filters import status_value
from organizational_memory.recall.keyword_search import search_keywords, tokenize
from organizational_memory.recall.open_loop_search import search_open_loops
from organizational_memory.recall.task_search import search_tasks
from organizational_memory.schemas.base import BaseRecord
from organizational_memory.storage.store import MemoryStore
from organizational_memory.utils.time import utc_now

_STOPWORDS = frozenset(
    {
        "who", "what", "why", "when", "which", "how", "is", "are", "was", "were",
        "did", "do", "does", "the", "a", "an", "we", "i", "still", "about",
        "regarding", "made", "make", "on", "of", "to", "for", "owns", "own",
        "owner", "responsible", "choose", "chose", "decide", "decided",
        "decision", "decisions", "task", "tasks", "commitment", "commitments",
        "promise", "promised", "risk", "risks", "open", "question", "questions",
        "unresolved", "unanswered", "overdue", "pending", "loop", "loops",
    }
)

_TERMINAL_STATUSES = frozenset(
    {"done", "completed", "resolved", "cancelled", "dismissed", "closed"}
)


@dataclass(frozen=True)
class Interpretation:
    """A deterministic interpretation of a natural-language question."""

    intent: str
    record_type: str | None
    text: str
    status: str | None
    overdue: bool


def interpret(question: str) -> Interpretation:
    """Map ``question`` to a structured :class:`Interpretation`."""
    tokens = tokenize(question)
    token_set = set(tokens)

    record_type: str | None = None
    status: str | None = None
    if (
        {"decision", "decisions", "choose", "chose", "decide", "decided"}
        & token_set
    ):
        record_type = "Decision"
    elif {"task", "tasks"} & token_set:
        record_type = "Task"
    elif {"commitment", "commitments", "promise", "promised"} & token_set:
        record_type = "Commitment"
    elif {"risk", "risks"} & token_set:
        record_type = "Risk"
    elif {"unresolved", "unanswered"} & token_set or (
        "open" in token_set and "question" in token_set
    ):
        record_type = "OpenLoop"
        status = "open"

    overdue = "overdue" in token_set

    intent = "search"
    if tokens[:1] == ["who"]:
        intent = "who_owns"
    elif tokens[:1] == ["why"]:
        intent = "why"

    text = " ".join(token for token in tokens if token not in _STOPWORDS)
    return Interpretation(
        intent=intent,
        record_type=record_type,
        text=text,
        status=status,
        overdue=overdue,
    )


def _overdue_results(
    store: MemoryStore, now: datetime
) -> list[RecallResult]:
    matches: list[tuple[datetime, BaseRecord]] = []
    for type_name in ("Task", "Commitment", "OpenLoop"):
        for record in store.list_records(type_name):
            due_at = getattr(record, "due_at", None)
            status = getattr(record, "status", None)
            if not isinstance(due_at, datetime) or due_at >= now:
                continue
            if status is not None and status_value(status) in _TERMINAL_STATUSES:
                continue
            matches.append((due_at, record))
    matches.sort(key=lambda entry: (entry[0], entry[1].id))
    return [RecallResult(record=record, score=1.0) for _, record in matches]


def answer(
    store: MemoryStore,
    question: str,
    *,
    now: datetime | None = None,
) -> list[RecallResult]:
    """Answer ``question`` deterministically against ``store``."""
    interpretation = interpret(question)
    text = interpretation.text or None

    if interpretation.overdue:
        return _overdue_results(store, now or utc_now())

    if interpretation.record_type == "Decision":
        return search_decisions(store, text=text)
    if interpretation.record_type == "Task":
        return search_tasks(store, text=text)
    if interpretation.record_type == "Commitment":
        return search_commitments(store, text=text)
    if interpretation.record_type == "OpenLoop":
        return search_open_loops(store, text=text, status=interpretation.status)

    return search_keywords(store.list_records(), text or "")
