"""``commitments`` command: inspect commitments in the store."""

import argparse

from organizational_memory.analytics.common import is_open_status, is_overdue
from organizational_memory.cli.common import (
    add_store_arguments,
    open_store_from_args,
)
from organizational_memory.models import Commitment
from organizational_memory.utils.time import format_timestamp, parse_timestamp, utc_now


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the ``commitments`` subcommand."""
    parser = subparsers.add_parser(
        "commitments",
        help="List and filter commitments.",
        description="Inspect open, overdue, owner-, and status-filtered commitments.",
    )
    add_store_arguments(parser)
    parser.add_argument("--owner", default=None, help="Filter by owner id.")
    parser.add_argument("--status", default=None, help="Filter by status value.")
    parser.add_argument("--open", action="store_true", help="Only open commitments.")
    parser.add_argument(
        "--overdue", action="store_true", help="Only overdue commitments."
    )
    parser.add_argument("--now", default=None, help="Reference time (ISO-8601 UTC).")
    parser.set_defaults(handler=run)


def run(args: argparse.Namespace) -> int:
    """Execute the ``commitments`` command."""
    now = utc_now()
    try:
        if args.now is not None:
            now = parse_timestamp(args.now)
    except ValueError as error:
        print(f"error: {error}")
        return 1

    store = open_store_from_args(args)
    commitments = [
        c for c in store.list_records("Commitment") if isinstance(c, Commitment)
    ]
    if args.owner is not None:
        commitments = [c for c in commitments if c.owner_id == args.owner]
    if args.status is not None:
        wanted = args.status.lower()
        commitments = [c for c in commitments if c.status.value == wanted]
    if args.open:
        commitments = [c for c in commitments if is_open_status(c.status)]
    if args.overdue:
        commitments = [c for c in commitments if is_overdue(c, now)]
    commitments.sort(key=lambda c: c.id)

    if not commitments:
        print("No commitments.")
        return 0

    print(f"{len(commitments)} commitment(s)")
    for commitment in commitments:
        due = format_timestamp(commitment.due_at) if commitment.due_at else "-"
        flag = " OVERDUE" if is_overdue(commitment, now) else ""
        print(
            f"  {commitment.id} [{commitment.status.value}] "
            f"owner={commitment.owner_id} due={due}{flag} — "
            f"{commitment.description}"
        )
    return 0
