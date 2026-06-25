"""Deterministic report generation and organizational memory products.

This package turns persisted memory, recall results, and analytics outputs into
deterministic, reproducible reports and exports (Markdown, JSON, CSV). It uses no
LLMs, embeddings, external APIs, or network calls.
"""

from organizational_memory.reports.base import (
    Report,
    ReportSection,
    ReportTable,
    json_safe,
)
from organizational_memory.reports.commitment_report import commitment_report
from organizational_memory.reports.decision_report import decision_report
from organizational_memory.reports.meeting_summary import meeting_summary
from organizational_memory.reports.open_loop_report import open_loop_report

__all__ = [
    "Report",
    "ReportSection",
    "ReportTable",
    "commitment_report",
    "decision_report",
    "json_safe",
    "meeting_summary",
    "open_loop_report",
]
