"""Tests for the CSV report exporter."""

from organizational_memory.reports.base import Report, ReportSection, ReportTable
from organizational_memory.reports.exporters.csv import CSVExporter
from organizational_memory.utils.time import parse_timestamp

GENERATED = parse_timestamp("2026-02-10T00:00:00Z")


def _table() -> ReportTable:
    return ReportTable(
        title="Decisions",
        columns=("id", "title"),
        rows=[("d1", "Adopt mesh, and scale"), ("d2", 'Quote "x"')],
    )


def _report() -> Report:
    return Report(
        title="Decision report",
        generated_at=GENERATED,
        sections=[ReportSection(title="By status", tables=[_table()])],
    )


def test_export_table_escaping() -> None:
    output = CSVExporter().export_table(_table())
    lines = output.splitlines()
    assert lines[0] == "Decisions"
    assert lines[1] == "id,title"
    assert lines[2] == 'd1,"Adopt mesh, and scale"'
    assert lines[3] == 'd2,"Quote ""x"""'


def test_export_report() -> None:
    output = CSVExporter().export(_report())
    assert "id,title" in output


def test_empty_table_keeps_header() -> None:
    table = ReportTable(title="Empty", columns=("a", "b"), rows=[])
    output = CSVExporter().export_table(table)
    assert output.splitlines() == ["Empty", "a,b"]


def test_empty_report_is_blank() -> None:
    report = Report(title="x", generated_at=GENERATED, sections=[])
    assert CSVExporter().export(report) == ""


def test_metadata_and_determinism() -> None:
    exporter = CSVExporter()
    assert exporter.supported_extension == "csv"
    assert exporter.content_type == "text/csv"
    assert exporter.export(_report()) == exporter.export(_report())
