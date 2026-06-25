"""``analytics`` command: deterministic workflow analytics over the store."""

import argparse
import json

from organizational_memory.analytics.reporting import generate_report
from organizational_memory.cli.common import (
    add_store_arguments,
    open_store_from_args,
)
from organizational_memory.utils.time import parse_timestamp, utc_now


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the ``analytics`` subcommand."""
    parser = subparsers.add_parser(
        "analytics",
        help="Show deterministic workflow analytics for the store.",
        description="Summary metrics, memory health, bottlenecks, and owner load.",
    )
    add_store_arguments(parser)
    parser.add_argument(
        "--format", choices=("text", "json"), default="text",
        help="Output format (default: %(default)s).",
    )
    parser.add_argument("--now", default=None, help="Reference time (ISO-8601 UTC).")
    parser.set_defaults(handler=run)


def run(args: argparse.Namespace) -> int:
    """Execute the ``analytics`` command."""
    now = utc_now()
    try:
        if args.now is not None:
            now = parse_timestamp(args.now)
    except ValueError as error:
        print(f"error: {error}")
        return 1

    store = open_store_from_args(args)
    report = generate_report(store, now=now)

    if args.format == "json":
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
        return 0

    print("Analytics summary")
    for key in ("decisions", "commitments", "open_loops", "overdue", "health_grade"):
        print(f"  {key}: {report.summary[key]}")

    print("Memory health")
    print(f"  score: {report.key_metrics['memory_health_score']}")
    print(f"  grade: {report.summary['health_grade']}")
    if report.recommendations:
        print("  recommendations:")
        for recommendation in report.recommendations:
            print(f"    - {recommendation}")

    print("Bottlenecks")
    print(f"  overloaded_owners: {report.bottlenecks['overloaded_owners']}")
    print(f"  recurring_unresolved: {report.bottlenecks['recurring_unresolved']}")
    print(f"  blocked_records: {report.bottlenecks['blocked_records']}")
    print(f"  low_signal_meetings: {report.bottlenecks['low_signal_meetings']}")

    print("Owner load")
    if report.owner_load:
        for owner, count in report.owner_load.items():
            print(f"  {owner}: {count}")
    else:
        print("  (none)")
    return 0
