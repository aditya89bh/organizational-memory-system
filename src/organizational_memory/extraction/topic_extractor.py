"""Deterministic discussion-topic extraction from transcript segments."""

import re
from collections.abc import Iterable

from organizational_memory.extraction.provenance import make_metadata
from organizational_memory.extraction.segmentation import Segment, SegmentKind
from organizational_memory.models.discussion_topic import DiscussionTopic

EXTRACTOR_NAME = "topic_extractor"

_TOPIC_PREFIX = re.compile(r"^\s*topic\s*:\s*(?P<title>.+)$", re.IGNORECASE)


def _topic_title(segment: Segment) -> tuple[str, str] | None:
    match = _TOPIC_PREFIX.match(segment.text)
    if match is not None:
        return match.group("title").strip(), "topic:"
    if segment.kind is SegmentKind.HEADING:
        return segment.text.strip(), "heading"
    return None


def extract_topics(segments: Iterable[Segment]) -> list[DiscussionTopic]:
    """Extract de-duplicated :class:`DiscussionTopic` records from ``segments``."""
    topics: list[DiscussionTopic] = []
    seen: set[str] = set()
    for segment in segments:
        result = _topic_title(segment)
        if result is None:
            continue
        title, marker = result
        key = title.lower()
        if not title or key in seen:
            continue
        seen.add(key)
        topics.append(
            DiscussionTopic(
                title=title,
                metadata=make_metadata(
                    extractor=EXTRACTOR_NAME,
                    matched_phrase=marker,
                    segment=segment,
                ),
            )
        )
    return topics
