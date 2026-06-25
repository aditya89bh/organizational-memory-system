"""CSV report exporter.

Exports the tabular sections of a report to CSV. Each :class:`ReportTable` is
rendered as a block (title row, header row, then data rows) using the standard
library writer for correct quoting/escaping. Column ordering is preserved
exactly as defined on the table, and empty tables still emit their header.
"""

import csv
import io

from organizational_memory.reports.base import Report, ReportTable
from organizational_memory.reports.exporters.base import ReportExporter


class CSVExporter(ReportExporter):
    """Export report tables to deterministic CSV blocks."""

    @property
    def supported_extension(self) -> str:
        return "csv"

    @property
    def content_type(self) -> str:
        return "text/csv"

    def export_table(self, table: ReportTable) -> str:
        """Render a single :class:`ReportTable` to a CSV block."""
        buffer = io.StringIO()
        writer = csv.writer(buffer, lineterminator="\n")
        writer.writerow([table.title])
        writer.writerow(list(table.columns))
        for row in table.rows:
            writer.writerow(list(row))
        return buffer.getvalue()

    def export(self, report: Report) -> str:
        blocks = [
            self.export_table(table)
            for section in report.sections
            for table in section.tables
        ]
        return "\n".join(blocks)
