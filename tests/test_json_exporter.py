"""Tests for the JSON report exporter."""

import json

from organizational_memory.models.enums import DecisionStatus
from organizational_memory.reports.base import Report, ReportSection
from organizational_memory.reports.exporters.json import JSONExporter
from organizational_memory.utils.time import parse_timestamp

GENERATED = parse_timestamp("2026-02-10T00:00:00Z")


def _report() -> Report:
    return Report(
        title="Decision report",
        generated_at=GENERATED,
        summary={"status": DecisionStatus.ACCEPTED, "count": 2},
        sections=[ReportSection(title="By status", metrics={"accepted": 2})],
    )


def test_round_trips_to_dict() -> None:
    output = JSONExporter().export(_report())
    loaded = json.loads(output)
    assert loaded["title"] == "Decision report"
    assert loaded["generated_at"] == "2026-02-10T00:00:00Z"


def test_enum_serialized_as_value() -> None:
    loaded = json.loads(JSONExporter().export(_report()))
    assert loaded["summary"]["status"] == "accepted"


def test_stable_key_ordering() -> None:
    output = JSONExporter().export(_report())
    loaded = json.loads(output)
    assert list(loaded["summary"].keys()) == ["count", "status"]


def test_metadata() -> None:
    exporter = JSONExporter()
    assert exporter.supported_extension == "json"
    assert exporter.content_type == "application/json"


def test_deterministic() -> None:
    exporter = JSONExporter()
    report = _report()
    assert exporter.export(report) == exporter.export(report)
