"""``open-loops`` command: inspect open loops (unresolved questions)."""

import argparse

from organizational_memory.analytics.common import is_overdue
from organizational_memory.cli.common import (
    add_store_arguments,
    open_store_from_args,
)
from organizational_memory.models import OpenLoop
from organizational_memory.models.enums import OpenLoopStatus
from organizational_memory.utils.time import format_timestamp, parse_timestamp, utc_now


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the ``open-loops`` subcommand."""
    parser = subparsers.add_parser(
        "open-loops",
        help="List and filter open loops.",
        description="Inspect unresolved and overdue open loops with filters.",
    )
    add_store_arguments(parser)
    parser.add_argument("--owner", default=None, help="Filter by owner id.")
    parser.add_argument("--meeting", default=None, help="Filter by source meeting id.")
    parser.add_argument(
        "--unresolved", action="store_true", help="Only unresolved open loops."
    )
    parser.add_argument(
        "--overdue", action="store_true", help="Only overdue open loops."
    )
    parser.add_argument(
        "--oldest-first", action="store_true", help="Sort by creation time ascending."
    )
    parser.add_argument("--now", default=None, help="Reference time (ISO-8601 UTC).")
    parser.set_defaults(handler=run)


def run(args: argparse.Namespace) -> int:
    """Execute the ``open-loops`` command."""
    now = utc_now()
    try:
        if args.now is not None:
            now = parse_timestamp(args.now)
    except ValueError as error:
        print(f"error: {error}")
        return 1

    store = open_store_from_args(args)
    loops = [r for r in store.list_records("OpenLoop") if isinstance(r, OpenLoop)]
    if args.owner is not None:
        loops = [loop for loop in loops if loop.owner_id == args.owner]
    if args.meeting is not None:
        loops = [loop for loop in loops if loop.source_meeting_id == args.meeting]
    if args.unresolved:
        loops = [loop for loop in loops if loop.status is OpenLoopStatus.OPEN]
    if args.overdue:
        loops = [loop for loop in loops if is_overdue(loop, now)]

    if args.oldest_first:
        loops.sort(key=lambda loop: (loop.created_at, loop.id))
    else:
        loops.sort(key=lambda loop: loop.id)

    if not loops:
        print("No open loops.")
        return 0

    print(f"{len(loops)} open loop(s)")
    for loop in loops:
        due = format_timestamp(loop.due_at) if loop.due_at else "-"
        flag = " OVERDUE" if is_overdue(loop, now) else ""
        print(
            f"  {loop.id} [{loop.status.value}] owner={loop.owner_id or '-'} "
            f"meeting={loop.source_meeting_id or '-'} due={due}{flag} — "
            f"{loop.question}"
        )
    return 0
