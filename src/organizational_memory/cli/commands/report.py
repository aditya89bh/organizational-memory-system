"""``report`` command: generate a deterministic report and render it."""

import argparse
from datetime import datetime

from organizational_memory.cli.common import (
    add_store_arguments,
    open_store_from_args,
    write_output,
)
from organizational_memory.reports.base import Report
from organizational_memory.reports.commitment_report import commitment_report
from organizational_memory.reports.decision_report import decision_report
from organizational_memory.reports.exporters.json import JSONExporter
from organizational_memory.reports.exporters.markdown import MarkdownExporter
from organizational_memory.reports.follow_up_report import follow_up_report
from organizational_memory.reports.meeting_summary import meeting_summary
from organizational_memory.reports.open_loop_report import open_loop_report
from organizational_memory.reports.organizational_memory_report import (
    organizational_memory_report,
)
from organizational_memory.reports.weekly_report import weekly_report
from organizational_memory.storage.store import MemoryStore
from organizational_memory.utils.time import parse_timestamp, utc_now

REPORT_TYPES = (
    "meeting",
    "weekly",
    "follow-up",
    "organizational-memory",
    "decisions",
    "commitments",
    "open-loops",
)


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the ``report`` subcommand."""
    parser = subparsers.add_parser(
        "report",
        help="Generate a deterministic report from the store.",
        description="Generate reports and render them as Markdown or JSON.",
    )
    parser.add_argument("type", choices=REPORT_TYPES, help="Report type to generate.")
    add_store_arguments(parser)
    parser.add_argument(
        "--format", choices=("markdown", "json"), default="markdown",
        help="Output format (default: %(default)s).",
    )
    parser.add_argument("--output", default=None, help="Write to this path.")
    parser.add_argument("--meeting-id", default=None, help="Meeting id (meeting type).")
    parser.add_argument("--start", default=None, help="Window start (weekly type).")
    parser.add_argument("--end", default=None, help="Window end (weekly type).")
    parser.add_argument("--now", default=None, help="Reference time (ISO-8601 UTC).")
    parser.set_defaults(handler=run)


def _build_report(
    args: argparse.Namespace, store: MemoryStore, now: datetime
) -> Report:
    if args.type == "meeting":
        if not args.meeting_id:
            raise ValueError("--meeting-id is required for the meeting report")
        return meeting_summary(store, args.meeting_id, now=now)
    if args.type == "weekly":
        if not args.start or not args.end:
            raise ValueError("--start and --end are required for the weekly report")
        return weekly_report(
            store,
            start=parse_timestamp(args.start),
            end=parse_timestamp(args.end),
            now=now,
        )
    if args.type == "follow-up":
        return follow_up_report(store, now=now)
    if args.type == "organizational-memory":
        return organizational_memory_report(store, now=now)
    if args.type == "decisions":
        return decision_report(store, now=now)
    if args.type == "commitments":
        return commitment_report(store, now=now)
    return open_loop_report(store, now=now)


def run(args: argparse.Namespace) -> int:
    """Execute the ``report`` command."""
    now = utc_now()
    try:
        if args.now is not None:
            now = parse_timestamp(args.now)
        store = open_store_from_args(args)
        report = _build_report(args, store, now)
    except (ValueError, KeyError) as error:
        print(f"error: {error}")
        return 1

    exporter = MarkdownExporter() if args.format == "markdown" else JSONExporter()
    write_output(exporter.export(report), args.output)
    return 0
