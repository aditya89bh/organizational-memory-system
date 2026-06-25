"""Text-only analytics visualizations.

Renders simple ASCII charts from analytics reports with no plotting
dependencies. All output is deterministic and depends only on the supplied data.
"""

from collections.abc import Mapping

from organizational_memory.analytics.open_loop_metrics import OpenLoopReport
from organizational_memory.analytics.ownership_metrics import OwnershipReport
from organizational_memory.analytics.timeline_analytics import TimelineAnalytics

DEFAULT_WIDTH = 40
EMPTY_PLACEHOLDER = "(no data)"


def _format_value(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.2f}"


def render_bar_chart(
    data: Mapping[str, float],
    *,
    width: int = DEFAULT_WIDTH,
    mark: str = "#",
) -> str:
    """Render ``data`` as a horizontal ASCII bar chart.

    Bars are scaled to the largest value. Labels are left-padded to a common
    width for alignment. Returns :data:`EMPTY_PLACEHOLDER` for empty input.
    """
    if not data:
        return EMPTY_PLACEHOLDER
    label_width = max(len(label) for label in data)
    max_value = max(data.values())
    lines: list[str] = []
    for label, value in data.items():
        bar_length = round(value / max_value * width) if max_value > 0 else 0
        lines.append(
            f"{label.ljust(label_width)} | {mark * bar_length} {_format_value(value)}"
        )
    return "\n".join(lines)


def timeline_chart(report: TimelineAnalytics, *, width: int = DEFAULT_WIDTH) -> str:
    """Render activity-by-date counts as a bar chart."""
    return render_bar_chart(report.activity_by_date, width=width)


def owner_load_chart(report: OwnershipReport, *, width: int = DEFAULT_WIDTH) -> str:
    """Render open work per owner as a bar chart."""
    return render_bar_chart(report.open_by_owner, width=width)


def open_loop_aging_chart(
    report: OpenLoopReport, *, width: int = DEFAULT_WIDTH
) -> str:
    """Render the ages of the oldest unresolved open loops as a bar chart."""
    data = {age.id: age.age_days for age in report.oldest_unresolved}
    return render_bar_chart(data, width=width)
