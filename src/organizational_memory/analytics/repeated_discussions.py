"""Repeated discussion detector.

Finds discussion topics and unresolved questions that recur, using deterministic
text normalization (lowercased, tokenized) and exact normalized matching. It
reports recurring clusters with the records and meetings involved, plus keywords
shared across multiple topics.
"""

from dataclasses import dataclass, field

from organizational_memory.models import DiscussionTopic, OpenLoop
from organizational_memory.recall.keyword_search import tokenize
from organizational_memory.storage.store import MemoryStore

DEFAULT_MIN_OCCURRENCES = 2
DEFAULT_MIN_KEYWORD_LENGTH = 3


@dataclass(frozen=True)
class RepeatedCluster:
    """A cluster of records sharing the same normalized text."""

    key: str
    label: str
    kind: str
    occurrences: int
    record_ids: tuple[str, ...]
    meeting_ids: tuple[str, ...]


@dataclass(frozen=True)
class RepeatedDiscussionReport:
    """Recurring topics, recurring open loops, and shared keywords."""

    topic_clusters: list[RepeatedCluster] = field(default_factory=list)
    open_loop_clusters: list[RepeatedCluster] = field(default_factory=list)
    repeated_keywords: dict[str, int] = field(default_factory=dict)


def _normalize(text: str) -> str:
    return " ".join(tokenize(text))


def _cluster(
    items: list[tuple[str, str, str | None]],
    kind: str,
    min_occurrences: int,
) -> list[RepeatedCluster]:
    """Group ``(text, record_id, meeting_id)`` tuples by normalized text."""
    groups: dict[str, list[tuple[str, str, str | None]]] = {}
    for text, record_id, meeting_id in items:
        key = _normalize(text)
        if not key:
            continue
        groups.setdefault(key, []).append((text, record_id, meeting_id))

    clusters: list[RepeatedCluster] = []
    for key, members in groups.items():
        if len(members) < min_occurrences:
            continue
        meeting_ids = sorted(
            {meeting for _, _, meeting in members if meeting}
        )
        clusters.append(
            RepeatedCluster(
                key=key,
                label=members[0][0],
                kind=kind,
                occurrences=len(members),
                record_ids=tuple(sorted(record_id for _, record_id, _ in members)),
                meeting_ids=tuple(meeting_ids),
            )
        )
    clusters.sort(key=lambda cluster: (-cluster.occurrences, cluster.key))
    return clusters


def _repeated_keywords(
    texts: list[str], min_length: int, min_documents: int
) -> dict[str, int]:
    document_frequency: dict[str, int] = {}
    for text in texts:
        for token in set(tokenize(text)):
            if len(token) >= min_length:
                document_frequency[token] = document_frequency.get(token, 0) + 1
    repeated = {
        token: count
        for token, count in document_frequency.items()
        if count >= min_documents
    }
    return dict(sorted(repeated.items(), key=lambda item: (-item[1], item[0])))


def repeated_discussions(
    store: MemoryStore,
    *,
    min_occurrences: int = DEFAULT_MIN_OCCURRENCES,
    min_keyword_length: int = DEFAULT_MIN_KEYWORD_LENGTH,
) -> RepeatedDiscussionReport:
    """Compute :class:`RepeatedDiscussionReport` from stored records."""
    topics = [
        r for r in store.list_records("DiscussionTopic")
        if isinstance(r, DiscussionTopic)
    ]
    loops = [r for r in store.list_records("OpenLoop") if isinstance(r, OpenLoop)]

    topic_clusters = _cluster(
        [(t.title, t.id, t.source_meeting_id) for t in topics],
        "topic",
        min_occurrences,
    )
    open_loop_clusters = _cluster(
        [(loop.question, loop.id, loop.source_meeting_id) for loop in loops],
        "open_loop",
        min_occurrences,
    )
    repeated_keywords = _repeated_keywords(
        [t.title for t in topics], min_keyword_length, min_occurrences
    )

    return RepeatedDiscussionReport(
        topic_clusters=topic_clusters,
        open_loop_clusters=open_loop_clusters,
        repeated_keywords=repeated_keywords,
    )
