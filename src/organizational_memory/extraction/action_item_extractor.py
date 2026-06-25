"""Deterministic action-item extraction from transcript segments.

Action items are a lightweight, unified view over task-like bullets and
explicit speaker commitments. Duplicate lines are collapsed so the same
sentence is not emitted twice.
"""

from collections.abc import Iterable

from organizational_memory.extraction.commitment_extractor import (
    COMMITMENT_MARKERS,
)
from organizational_memory.extraction.provenance import first_marker, make_metadata
from organizational_memory.extraction.segmentation import Segment
from organizational_memory.extraction.task_extractor import TASK_MARKERS
from organizational_memory.models.action_item import ActionItem

EXTRACTOR_NAME = "action_item_extractor"

_ACTION_MARKERS: tuple[str, ...] = TASK_MARKERS + COMMITMENT_MARKERS


def extract_action_items(segments: Iterable[Segment]) -> list[ActionItem]:
    """Extract de-duplicated :class:`ActionItem` records from ``segments``."""
    action_items: list[ActionItem] = []
    seen: set[str] = set()
    for segment in segments:
        marker = first_marker(segment.text, _ACTION_MARKERS)
        if marker is None:
            continue
        fingerprint = segment.text.strip().lower()
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        action_items.append(
            ActionItem(
                description=segment.text,
                owner_id=segment.speaker,
                metadata=make_metadata(
                    extractor=EXTRACTOR_NAME,
                    matched_phrase=marker,
                    segment=segment,
                ),
            )
        )
    return action_items
