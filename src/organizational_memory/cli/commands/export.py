"""``export`` command: export a memory snapshot or a report."""

import argparse
import csv
import io
import json

from organizational_memory.cli.common import (
    add_store_arguments,
    open_store_from_args,
    write_output,
)
from organizational_memory.cli.report_builder import REPORT_TYPES, build_report
from organizational_memory.reports.exporters.csv import CSVExporter
from organizational_memory.reports.exporters.json import JSONExporter
from organizational_memory.reports.exporters.markdown import MarkdownExporter
from organizational_memory.schemas.base import BaseRecord
from organizational_memory.storage.store import RECORD_TYPES, MemoryStore
from organizational_memory.utils.time import parse_timestamp, utc_now

_SNAPSHOT_COLUMNS = ("type", "id", "label", "owner_id", "status", "due_at")
_LABEL_FIELDS = ("title", "question", "description", "name", "event_type")


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the ``export`` subcommand."""
    parser = subparsers.add_parser(
        "export",
        help="Export a memory snapshot or a report.",
        description="Export the raw memory snapshot or a report as json/markdown/csv.",
    )
    parser.add_argument("format", choices=("json", "markdown", "csv"))
    add_store_arguments(parser)
    parser.add_argument(
        "--target", choices=("snapshot", "report"), default="snapshot",
        help="What to export (default: %(default)s).",
    )
    parser.add_argument(
        "--report-type", choices=REPORT_TYPES, default="organizational-memory",
        help="Report type when --target report (default: %(default)s).",
    )
    parser.add_argument("--output", default=None, help="Write to this path.")
    parser.add_argument("--meeting-id", default=None, help="Meeting id (meeting type).")
    parser.add_argument("--start", default=None, help="Window start (weekly type).")
    parser.add_argument("--end", default=None, help="Window end (weekly type).")
    parser.add_argument("--now", default=None, help="Reference time (ISO-8601 UTC).")
    parser.set_defaults(handler=run)


def _label(record: BaseRecord) -> str:
    for field_name in _LABEL_FIELDS:
        value = getattr(record, field_name, None)
        if isinstance(value, str) and value:
            return value
    return record.id


def _sorted_records(store: MemoryStore) -> list[tuple[str, BaseRecord]]:
    pairs: list[tuple[str, BaseRecord]] = []
    for type_name in sorted(RECORD_TYPES):
        for record in store.list_records(type_name):
            pairs.append((type_name, record))
    pairs.sort(key=lambda item: (item[0], item[1].id))
    return pairs


def _snapshot_json(store: MemoryStore) -> str:
    data: dict[str, list[dict[str, object]]] = {}
    for type_name in sorted(RECORD_TYPES):
        records = sorted(store.list_records(type_name), key=lambda r: r.id)
        if records:
            data[type_name] = [record.to_dict() for record in records]
    return json.dumps(data, indent=2, sort_keys=True)


def _snapshot_csv(store: MemoryStore) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(_SNAPSHOT_COLUMNS)
    for type_name, record in _sorted_records(store):
        due = getattr(record, "due_at", None)
        status = getattr(record, "status", None)
        writer.writerow(
            [
                type_name,
                record.id,
                _label(record),
                getattr(record, "owner_id", "") or "",
                status.value if status is not None else "",
                due.isoformat() if due is not None else "",
            ]
        )
    return buffer.getvalue().rstrip("\n")


def _snapshot_markdown(store: MemoryStore) -> str:
    lines = ["# Memory snapshot", ""]
    for type_name in sorted(RECORD_TYPES):
        count = len(store.list_records(type_name))
        if count:
            lines.append(f"- {type_name}: {count}")
    lines.append("")
    lines.append("| type | id | label |")
    lines.append("| --- | --- | --- |")
    for type_name, record in _sorted_records(store):
        label = _label(record).replace("|", "\\|")
        lines.append(f"| {type_name} | {record.id} | {label} |")
    return "\n".join(lines)


def _export_snapshot(store: MemoryStore, fmt: str) -> str:
    if fmt == "json":
        return _snapshot_json(store)
    if fmt == "csv":
        return _snapshot_csv(store)
    return _snapshot_markdown(store)


def run(args: argparse.Namespace) -> int:
    """Execute the ``export`` command."""
    now = utc_now()
    try:
        if args.now is not None:
            now = parse_timestamp(args.now)
        store = open_store_from_args(args)
        if args.target == "snapshot":
            content = _export_snapshot(store, args.format)
        else:
            report = build_report(
                store,
                args.report_type,
                now=now,
                start=parse_timestamp(args.start) if args.start else None,
                end=parse_timestamp(args.end) if args.end else None,
                meeting_id=args.meeting_id,
            )
            exporters = {
                "json": JSONExporter(),
                "markdown": MarkdownExporter(),
                "csv": CSVExporter(),
            }
            content = exporters[args.format].export(report)
    except (ValueError, KeyError) as error:
        print(f"error: {error}")
        return 1

    write_output(content, args.output)
    return 0
