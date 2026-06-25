"""Deterministic report generation and organizational memory products.

This package turns persisted memory, recall results, and analytics outputs into
deterministic, reproducible reports and exports (Markdown, JSON, CSV). It uses no
LLMs, embeddings, external APIs, or network calls.
"""

from organizational_memory.reports.accountability_report import accountability_report
from organizational_memory.reports.base import (
    Report,
    ReportSection,
    ReportTable,
    json_safe,
)
from organizational_memory.reports.commitment_report import commitment_report
from organizational_memory.reports.decision_report import decision_report
from organizational_memory.reports.follow_up_report import follow_up_report
from organizational_memory.reports.meeting_summary import meeting_summary
from organizational_memory.reports.monthly_report import monthly_report
from organizational_memory.reports.open_loop_report import open_loop_report
from organizational_memory.reports.organizational_memory_report import (
    organizational_memory_report,
)
from organizational_memory.reports.participant_report import participant_report
from organizational_memory.reports.templates import (
    executive_summary,
    follow_up_memo,
    meeting_summary_template,
    open_loop_review,
    select_sections,
    weekly_review,
)
from organizational_memory.reports.timeline_report import timeline_report
from organizational_memory.reports.visualizations import (
    due_date_aging_table,
    owner_workload_table,
    render_table,
    section_bars,
    status_distribution_table,
)
from organizational_memory.reports.weekly_report import weekly_report

__all__ = [
    "Report",
    "ReportSection",
    "ReportTable",
    "accountability_report",
    "commitment_report",
    "decision_report",
    "due_date_aging_table",
    "executive_summary",
    "follow_up_memo",
    "follow_up_report",
    "json_safe",
    "meeting_summary",
    "meeting_summary_template",
    "monthly_report",
    "open_loop_report",
    "open_loop_review",
    "organizational_memory_report",
    "owner_workload_table",
    "participant_report",
    "render_table",
    "section_bars",
    "select_sections",
    "status_distribution_table",
    "timeline_report",
    "weekly_report",
    "weekly_review",
]
