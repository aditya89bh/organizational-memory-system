"""Deterministic task extraction from transcript segments."""

from collections.abc import Iterable

from organizational_memory.extraction.normalization import shorten
from organizational_memory.extraction.provenance import (
    UNATTRIBUTED_OWNER,
    first_marker,
    make_metadata,
)
from organizational_memory.extraction.segmentation import Segment
from organizational_memory.models.task import Task

EXTRACTOR_NAME = "task_extractor"

TASK_MARKERS: tuple[str, ...] = (
    "todo:",
    "task:",
    "action:",
    "next step:",
    "[ ]",
    "needs to",
)


def extract_tasks(segments: Iterable[Segment]) -> list[Task]:
    """Extract :class:`Task` records from ``segments``."""
    tasks: list[Task] = []
    for segment in segments:
        marker = first_marker(segment.text, TASK_MARKERS)
        if marker is None:
            continue
        owner = segment.speaker or UNATTRIBUTED_OWNER
        tasks.append(
            Task(
                title=shorten(segment.text),
                description=segment.text,
                owner_id=owner,
                metadata=make_metadata(
                    extractor=EXTRACTOR_NAME,
                    matched_phrase=marker,
                    segment=segment,
                ),
            )
        )
    return tasks
