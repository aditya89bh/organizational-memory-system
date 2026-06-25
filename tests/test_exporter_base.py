"""Tests for the report exporter interface."""

import pytest

from organizational_memory.reports.base import Report, ReportSection
from organizational_memory.reports.exporters.base import ReportExporter
from organizational_memory.utils.time import utc_now


class _FakeExporter(ReportExporter):
    @property
    def supported_extension(self) -> str:
        return "txt"

    @property
    def content_type(self) -> str:
        return "text/plain"

    def export(self, report: Report) -> str:
        lines = [report.title]
        lines.extend(section.title for section in report.sections)
        return "\n".join(lines)


def _report() -> Report:
    return Report(
        title="Sample",
        generated_at=utc_now(),
        sections=[ReportSection(title="One"), ReportSection(title="Two")],
    )


def test_cannot_instantiate_abstract() -> None:
    with pytest.raises(TypeError):
        ReportExporter()  # type: ignore[abstract]


def test_fake_exporter_metadata() -> None:
    exporter = _FakeExporter()
    assert exporter.supported_extension == "txt"
    assert exporter.content_type == "text/plain"


def test_fake_exporter_export() -> None:
    exporter = _FakeExporter()
    assert exporter.export(_report()) == "Sample\nOne\nTwo"


def test_filename_helper() -> None:
    exporter = _FakeExporter()
    assert exporter.filename("weekly") == "weekly.txt"


def test_export_is_deterministic() -> None:
    exporter = _FakeExporter()
    report = _report()
    assert exporter.export(report) == exporter.export(report)
