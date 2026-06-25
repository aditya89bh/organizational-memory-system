"""Meeting effectiveness metrics.

Counts the structured outputs (decisions, commitments, tasks, open loops, risks)
attributed to each meeting and derives a deterministic signal-to-noise style
score. The score reflects the share of actionable outputs relative to unresolved
open loops; it is a structural indicator, not a measure of real productivity.
"""

from dataclasses import dataclass, field

from organizational_memory.analytics.common import count_by, meeting_or_none, safe_ratio
from organizational_memory.models import Meeting
from organizational_memory.storage.store import MemoryStore

_COUNTED_TYPES = ("Decision", "Commitment", "Task", "OpenLoop", "Risk")


@dataclass(frozen=True)
class MeetingEffectiveness:
    """Structured-output counts and score for a single meeting."""

    meeting_id: str
    title: str
    decisions: int
    commitments: int
    tasks: int
    open_loops: int
    risks: int
    structured_outputs: int
    effectiveness_score: float


@dataclass(frozen=True)
class MeetingEffectivenessReport:
    """Per-meeting effectiveness across all meetings in the store."""

    total_meetings: int
    meetings: list[MeetingEffectiveness] = field(default_factory=list)


def meeting_effectiveness(store: MemoryStore) -> MeetingEffectivenessReport:
    """Compute :class:`MeetingEffectivenessReport` from stored records.

    The effectiveness score is ``signal / (signal + open_loops)`` where signal is
    the count of decisions, commitments, tasks, and risks.
    """
    counts: dict[str, dict[str, int]] = {
        type_name: count_by(store.list_records(type_name), meeting_or_none)
        for type_name in _COUNTED_TYPES
    }

    meetings = [r for r in store.list_records("Meeting") if isinstance(r, Meeting)]
    rows: list[MeetingEffectiveness] = []
    for meeting in sorted(meetings, key=lambda m: m.id):
        decisions = counts["Decision"].get(meeting.id, 0)
        commitments = counts["Commitment"].get(meeting.id, 0)
        tasks = counts["Task"].get(meeting.id, 0)
        open_loops = counts["OpenLoop"].get(meeting.id, 0)
        risks = counts["Risk"].get(meeting.id, 0)
        signal = decisions + commitments + tasks + risks
        rows.append(
            MeetingEffectiveness(
                meeting_id=meeting.id,
                title=meeting.title,
                decisions=decisions,
                commitments=commitments,
                tasks=tasks,
                open_loops=open_loops,
                risks=risks,
                structured_outputs=signal + open_loops,
                effectiveness_score=safe_ratio(signal, signal + open_loops),
            )
        )

    return MeetingEffectivenessReport(total_meetings=len(rows), meetings=rows)
