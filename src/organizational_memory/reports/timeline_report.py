"""Deterministic timeline reports.

Produces a chronological view across meetings, decisions, commitments, tasks,
open loops, risks, and memory events, reusing the Phase 5 timeline search for
timestamp selection and ordering.
"""

from datetime import datetime

from organizational_memory.recall.timeline_search import search_timeline
from organizational_memory.reports.base import Report, ReportSection, ReportTable
from organizational_memory.reports.common import counts_table
from organizational_memory.schemas.base import BaseRecord
from organizational_memory.storage.store import MemoryStore
from organizational_memory.utils.time import utc_now

_LABEL_FIELDS = ("title", "question", "description", "event_type")


def _label(record: BaseRecord) -> str:
    for field_name in _LABEL_FIELDS:
        value = getattr(record, field_name, None)
        if isinstance(value, str) and value:
            return value
    return record.id


def timeline_report(
    store: MemoryStore,
    *,
    after: datetime | None = None,
    before: datetime | None = None,
    ascending: bool = True,
    record_types: tuple[str, ...] | None = None,
    now: datetime | None = None,
) -> Report:
    """Build a chronological :class:`Report` across timeline record types."""
    generated_at = now or utc_now()
    results = search_timeline(
        store,
        after=after,
        before=before,
        ascending=ascending,
        record_types=record_types,
    )

    rows: list[tuple[str, ...]] = []
    by_type: dict[str, int] = {}
    for result in results:
        record = result.record
        type_name = type(record).__name__
        by_type[type_name] = by_type.get(type_name, 0) + 1
        rows.append(
            (
                str(result.details.get("timestamp", "")),
                type_name,
                record.id,
                _label(record),
            )
        )

    return Report(
        title="Timeline report",
        generated_at=generated_at,
        summary={"total": len(results), "by_type": by_type},
        sections=[
            ReportSection(
                title="Timeline",
                metrics={"count": len(results)},
                tables=[
                    ReportTable(
                        title="Chronological entries",
                        columns=("timestamp", "type", "id", "summary"),
                        rows=rows,
                    )
                ],
            ),
            ReportSection(
                title="By type",
                metrics=dict(by_type),
                tables=[counts_table("Entries by type", by_type)],
            ),
        ],
    )
