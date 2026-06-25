"""JSON report exporter.

Serializes a report to a deterministic JSON document. Stable key ordering is
guaranteed via ``sort_keys``; datetimes and enums are normalized by the report's
``to_dict`` (and its ``json_safe`` helper) before serialization.
"""

import json

from organizational_memory.reports.base import Report
from organizational_memory.reports.exporters.base import ReportExporter


class JSONExporter(ReportExporter):
    """Export reports to deterministic, JSON-safe documents."""

    def __init__(self, *, indent: int = 2) -> None:
        self._indent = indent

    @property
    def supported_extension(self) -> str:
        return "json"

    @property
    def content_type(self) -> str:
        return "application/json"

    def export(self, report: Report) -> str:
        return (
            json.dumps(
                report.to_dict(),
                indent=self._indent,
                sort_keys=True,
                ensure_ascii=False,
            )
            + "\n"
        )
