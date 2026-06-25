"""``recall`` command: deterministic keyword/structured search over the store."""

import argparse

from organizational_memory.cli.common import (
    add_store_arguments,
    open_store_from_args,
)
from organizational_memory.recall.engine import RecallResult
from organizational_memory.recall.explanations import explain_result
from organizational_memory.recall.keyword_search import search_keywords
from organizational_memory.recall.pagination import paginate
from organizational_memory.recall.query_parser import parse_query
from organizational_memory.schemas.base import BaseRecord

_LABEL_FIELDS = ("title", "question", "description", "name", "event_type")


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the ``recall`` subcommand."""
    parser = subparsers.add_parser(
        "recall",
        help="Search organizational memory with a deterministic query.",
        description=(
            "Recall memory using keyword search. Supports compact filters like "
            "'type:decision owner:alice pricing'."
        ),
    )
    parser.add_argument("query", help="Query text, optionally with key:value filters.")
    add_store_arguments(parser)
    parser.add_argument(
        "--limit", type=int, default=10, help="Maximum results (default: %(default)s)."
    )
    parser.add_argument(
        "--offset", type=int, default=0, help="Results to skip (default: %(default)s)."
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        help="Show why each result matched and how it was scored.",
    )
    parser.set_defaults(handler=run)


def _label(record: BaseRecord) -> str:
    for field_name in _LABEL_FIELDS:
        value = getattr(record, field_name, None)
        if isinstance(value, str) and value:
            return value
    return record.id


def run(args: argparse.Namespace) -> int:
    """Execute the ``recall`` command."""
    if args.limit < 0 or args.offset < 0:
        print("error: --limit and --offset must be non-negative")
        return 1

    parsed = parse_query(args.query)
    store = open_store_from_args(args)
    records = store.list_records(parsed.record_type)
    query_text = parsed.text.strip() or parsed.raw
    results: list[RecallResult] = search_keywords(records, query_text)

    page = paginate(results, limit=args.limit, offset=args.offset)
    if page.total == 0:
        print("No results.")
        return 0

    last = page.offset + page.returned
    print(f"{page.total} result(s); showing {page.offset + 1}-{last}")
    for index, result in enumerate(page.items, start=page.offset + 1):
        record = result.record
        print(
            f"{index}. [{type(record).__name__}] {record.id} "
            f"(score {result.score}) — {_label(record)}"
        )
        if args.explain:
            for reason in explain_result(result).reasons:
                print(f"     - {reason}")
    return 0
