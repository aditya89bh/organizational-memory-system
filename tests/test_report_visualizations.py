"""Tests for text-only report visualizations."""

from organizational_memory.reports.base import Report, ReportSection, ReportTable
from organizational_memory.reports.visualizations import (
    due_date_aging_table,
    owner_workload_table,
    render_table,
    section_bars,
    status_distribution_table,
)
from organizational_memory.utils.time import utc_now


def _report() -> Report:
    return Report(
        title="x",
        generated_at=utc_now(),
        sections=[
            ReportSection(title="Decisions", metrics={"count": 3}),
            ReportSection(
                title="Open loops",
                tables=[
                    ReportTable(title="t", columns=("a",), rows=[("1",), ("2",)])
                ],
            ),
        ],
    )


def test_section_bars() -> None:
    output = section_bars(_report())
    assert "Decisions" in output
    assert "Open loops" in output


def test_status_distribution_total() -> None:
    output = status_distribution_table({"open": 2, "closed": 1})
    assert "total" in output
    assert output.splitlines()[-1].startswith("total")


def test_owner_workload() -> None:
    output = owner_workload_table({"alice": 2})
    assert "owner" in output
    assert "alice" in output


def test_due_date_aging_buckets() -> None:
    output = due_date_aging_table({"a": 1.0, "b": 10.0, "c": 200.0})
    lines = {line.split("|")[0].strip(): line for line in output.splitlines()[2:]}
    assert lines["0-7d"].strip().endswith("1")
    assert lines["8-30d"].strip().endswith("1")
    assert lines["90d+"].strip().endswith("1")


def test_render_table_empty() -> None:
    assert render_table(("a", "b"), []) == "(no data)"


def test_deterministic() -> None:
    report = _report()
    assert section_bars(report) == section_bars(report)
