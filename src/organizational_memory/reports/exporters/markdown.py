"""Markdown report exporter.

Renders a report to deterministic Markdown with headings, metadata blocks,
bullet lists for summaries and metrics, and GitHub-style tables.
"""

from organizational_memory.reports.base import Report, ReportTable, json_safe
from organizational_memory.reports.exporters.base import ReportExporter


def _escape_cell(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def _render_table(table: ReportTable) -> list[str]:
    lines = [f"#### {table.title}", ""]
    header = "| " + " | ".join(table.columns) + " |"
    divider = "| " + " | ".join("---" for _ in table.columns) + " |"
    lines.append(header)
    lines.append(divider)
    for row in table.rows:
        lines.append("| " + " | ".join(_escape_cell(cell) for cell in row) + " |")
    lines.append("")
    return lines


def _render_mapping(title: str, mapping: dict[str, object]) -> list[str]:
    if not mapping:
        return []
    lines = [f"## {title}", ""]
    for key, value in mapping.items():
        lines.append(f"- **{key}**: {json_safe(value)}")
    lines.append("")
    return lines


class MarkdownExporter(ReportExporter):
    """Export reports to deterministic Markdown."""

    @property
    def supported_extension(self) -> str:
        return "md"

    @property
    def content_type(self) -> str:
        return "text/markdown"

    def export(self, report: Report) -> str:
        lines: list[str] = [f"# {report.title}", ""]
        lines.append(f"_Generated: {report.to_dict()['generated_at']}_")
        lines.append("")

        if report.metadata:
            lines.append("## Metadata")
            lines.append("")
            for key in sorted(report.metadata):
                lines.append(f"- **{key}**: {report.metadata[key]}")
            lines.append("")

        lines.extend(_render_mapping("Summary", report.summary))

        for section in report.sections:
            lines.append(f"## {section.title}")
            lines.append("")
            for key, value in section.metrics.items():
                lines.append(f"- **{key}**: {json_safe(value)}")
            if section.metrics:
                lines.append("")
            for item in section.body:
                lines.append(f"- {item}")
            if section.body:
                lines.append("")
            for table in section.tables:
                lines.extend(_render_table(table))

        return "\n".join(lines).rstrip("\n") + "\n"
