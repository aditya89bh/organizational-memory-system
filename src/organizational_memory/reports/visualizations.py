"""Text-only report visualizations.

Renders reports and tabular data as plain text: horizontal bars for section
sizes and aligned ASCII tables for status distributions, due-date aging, and
owner workload. No plotting dependencies; all output is deterministic.
"""

from collections.abc import Mapping, Sequence

from organizational_memory.analytics.visualizations import (
    EMPTY_PLACEHOLDER,
    render_bar_chart,
)
from organizational_memory.reports.base import Report

AGING_BUCKETS: tuple[tuple[str, float, float], ...] = (
    ("0-7d", 0.0, 7.0),
    ("8-30d", 7.0, 30.0),
    ("31-90d", 30.0, 90.0),
    ("90d+", 90.0, float("inf")),
)


def _section_value(report: Report) -> dict[str, float]:
    values: dict[str, float] = {}
    for section in report.sections:
        count = section.metrics.get("count")
        if isinstance(count, (int, float)):
            values[section.title] = float(count)
        else:
            values[section.title] = float(
                sum(len(table.rows) for table in section.tables)
            )
    return values


def render_table(
    headers: Sequence[str], rows: Sequence[Sequence[str]]
) -> str:
    """Render an aligned ASCII table; returns a placeholder when empty."""
    if not rows:
        return EMPTY_PLACEHOLDER
    widths = [len(header) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))
    lines = [
        " | ".join(header.ljust(widths[index]) for index, header in enumerate(headers))
    ]
    lines.append("-+-".join("-" * width for width in widths))
    for row in rows:
        lines.append(
            " | ".join(cell.ljust(widths[index]) for index, cell in enumerate(row))
        )
    return "\n".join(lines)


def section_bars(report: Report, *, width: int = 40) -> str:
    """Render a bar chart of each section's size."""
    return render_bar_chart(_section_value(report), width=width)


def status_distribution_table(counts: Mapping[str, int]) -> str:
    """Render a status distribution as an aligned table with a total."""
    rows = [(status, str(count)) for status, count in counts.items()]
    if rows:
        rows.append(("total", str(sum(counts.values()))))
    return render_table(("status", "count"), rows)


def owner_workload_table(counts: Mapping[str, int]) -> str:
    """Render owner workload counts as an aligned table."""
    rows = [(owner, str(count)) for owner, count in counts.items()]
    return render_table(("owner", "count"), rows)


def due_date_aging_table(days_overdue: Mapping[str, float]) -> str:
    """Render a count of overdue items bucketed by age."""
    buckets = {label: 0 for label, _, _ in AGING_BUCKETS}
    for value in days_overdue.values():
        for label, low, high in AGING_BUCKETS:
            if low <= value < high:
                buckets[label] += 1
                break
    rows = [(label, str(buckets[label])) for label, _, _ in AGING_BUCKETS]
    return render_table(("bucket", "count"), rows)
