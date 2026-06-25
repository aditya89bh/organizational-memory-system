"""Tests for text-only analytics visualizations."""

from organizational_memory.analytics.open_loop_metrics import (
    OpenLoopAge,
    OpenLoopReport,
)
from organizational_memory.analytics.ownership_metrics import OwnershipReport
from organizational_memory.analytics.timeline_analytics import TimelineAnalytics
from organizational_memory.analytics.visualizations import (
    EMPTY_PLACEHOLDER,
    open_loop_aging_chart,
    owner_load_chart,
    render_bar_chart,
    timeline_chart,
)


def test_empty_chart() -> None:
    assert render_bar_chart({}) == EMPTY_PLACEHOLDER


def test_bar_chart_scaling() -> None:
    chart = render_bar_chart({"a": 10, "b": 5}, width=10)
    lines = chart.splitlines()
    assert lines[0].startswith("a |")
    assert lines[0].count("#") == 10
    assert lines[1].count("#") == 5
    assert lines[0].endswith("10")


def test_bar_chart_float_formatting() -> None:
    chart = render_bar_chart({"x": 0.5}, width=10)
    assert chart.endswith("0.50")


def test_timeline_chart() -> None:
    report = TimelineAnalytics(
        total=3,
        activity_by_date={"2026-01-05": 2, "2026-01-06": 1},
    )
    chart = timeline_chart(report)
    assert "2026-01-05" in chart


def test_owner_load_chart() -> None:
    report = OwnershipReport(open_by_owner={"alice": 3, "bob": 1})
    chart = owner_load_chart(report)
    assert "alice" in chart
    assert "bob" in chart


def test_open_loop_aging_chart() -> None:
    report = OpenLoopReport(
        total=1,
        unresolved=1,
        resolved=0,
        average_age_days=10.0,
        oldest_unresolved=[OpenLoopAge(id="o1", question="q?", age_days=10.0)],
    )
    chart = open_loop_aging_chart(report)
    assert "o1" in chart
