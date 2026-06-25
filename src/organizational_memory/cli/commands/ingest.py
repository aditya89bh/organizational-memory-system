"""``ingest`` command: extract a transcript and persist it to a store."""

import argparse

from organizational_memory.cli.common import (
    add_store_arguments,
    open_store_from_args,
)
from organizational_memory.exceptions import OrganizationalMemoryError
from organizational_memory.extraction.pipeline import ExtractionResult, run_extraction
from organizational_memory.ingestion.transcript_loader import (
    load_transcript_from_file,
)
from organizational_memory.models import Meeting
from organizational_memory.schemas.base import BaseRecord
from organizational_memory.storage.store import MemoryStore
from organizational_memory.utils.time import utc_now

_GROUPS = (
    ("participants", "participants"),
    ("decisions", "decisions"),
    ("commitments", "commitments"),
    ("tasks", "tasks"),
    ("open_loops", "open_loops"),
    ("dependencies", "dependencies"),
    ("risks", "risks"),
    ("action_items", "action_items"),
    ("topics", "topics"),
)


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the ``ingest`` subcommand."""
    parser = subparsers.add_parser(
        "ingest",
        help="Extract a transcript or notes file and persist the memory.",
        description="Ingest a transcript (.txt/.md) into a memory store.",
    )
    parser.add_argument("path", help="Path to the transcript or notes file.")
    add_store_arguments(parser)
    parser.add_argument(
        "--meeting-id",
        default=None,
        help="Attach a Meeting record and tag extracted records to it.",
    )
    parser.add_argument(
        "--title",
        default="Ingested meeting",
        help="Meeting title used when --meeting-id is given.",
    )
    parser.set_defaults(handler=run)


def _persist(
    store: MemoryStore,
    result: ExtractionResult,
    meeting_id: str | None,
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for attr, label in _GROUPS:
        records: list[BaseRecord] = getattr(result, attr)
        for record in records:
            if meeting_id and hasattr(record, "source_meeting_id"):
                record.source_meeting_id = meeting_id
            store.save_record(record)
        counts[label] = len(records)
    return counts


def run(args: argparse.Namespace) -> int:
    """Execute the ``ingest`` command."""
    try:
        transcript = load_transcript_from_file(args.path)
        result = run_extraction(transcript)
    except OrganizationalMemoryError as error:
        print(f"error: {error}")
        return 1

    store = open_store_from_args(args)
    if args.meeting_id:
        store.save_record(
            Meeting(
                id=args.meeting_id,
                title=args.title,
                started_at=utc_now(),
                participants=[p.name for p in result.participants],
                source=args.path,
            )
        )
    counts = _persist(store, result, args.meeting_id)

    total = sum(counts.values())
    print(f"Ingested {args.path}")
    for _, label in _GROUPS:
        print(f"  {label}: {counts[label]}")
    print(f"  total records: {total}")
    return 0
