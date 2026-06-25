"""Tests for the Markdown report exporter."""

from organizational_memory.reports.base import (
    Report,
    ReportSection,
    ReportTable,
)
from organizational_memory.reports.exporters.markdown import MarkdownExporter
from organizational_memory.utils.time import parse_timestamp

GENERATED = parse_timestamp("2026-02-10T00:00:00Z")


def _report() -> Report:
    return Report(
        title="Weekly report",
        generated_at=GENERATED,
        summary={"decisions": 2},
        metadata={"source": "transcript"},
        sections=[
            ReportSection(
                title="Decisions",
                metrics={"count": 1},
                body=["Adopted mesh"],
                tables=[
                    ReportTable(
                        title="Decisions",
                        columns=("id", "title"),
                        rows=[("d1", "Adopt mesh | network")],
                    )
                ],
            )
        ],
    )


def test_headings_and_metadata() -> None:
    output = MarkdownExporter().export(_report())
    assert output.startswith("# Weekly report")
    assert "_Generated: 2026-02-10T00:00:00Z_" in output
    assert "## Metadata" in output
    assert "- **source**: transcript" in output


def test_summary_and_metrics() -> None:
    output = MarkdownExporter().export(_report())
    assert "## Summary" in output
    assert "- **decisions**: 2" in output
    assert "- **count**: 1" in output
    assert "- Adopted mesh" in output


def test_table_rendering_and_escaping() -> None:
    output = MarkdownExporter().export(_report())
    assert "| id | title |" in output
    assert "| --- | --- |" in output
    assert "| d1 | Adopt mesh \\| network |" in output


def test_metadata_extension() -> None:
    exporter = MarkdownExporter()
    assert exporter.supported_extension == "md"
    assert exporter.content_type == "text/markdown"


def test_deterministic() -> None:
    exporter = MarkdownExporter()
    report = _report()
    assert exporter.export(report) == exporter.export(report)
    assert exporter.export(report).endswith("\n")
