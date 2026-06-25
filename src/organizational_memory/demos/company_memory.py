"""Company memory demo: answer deterministic questions via recall + reports."""

from datetime import timedelta

from organizational_memory.analytics.common import is_overdue
from organizational_memory.demos.common import (
    BASE_TIME,
    REFERENCE_NOW,
    InMemoryStore,
    heading,
    ingest_meeting,
)
from organizational_memory.models import Commitment, OpenLoop
from organizational_memory.models.enums import CommitmentStatus, OpenLoopStatus
from organizational_memory.recall.keyword_search import search_keywords
from organizational_memory.schemas.base import BaseRecord

TRANSCRIPT = """# Company All-Hands

Attendees: Aditya, Priya, Rahul, Dana

[09:00] Aditya: We decided to delay the launch due to the security review.
[09:03] Priya: I will own the website redesign.
[09:05] Rahul: The redesign is blocked by the branding decision.
[09:06] Dana: What is the final launch date?
TODO: publish the updated roadmap.
Topic: Launch delay
"""


def _label(record: BaseRecord) -> str:
    for field_name in ("title", "question", "description", "name"):
        value = getattr(record, field_name, None)
        if isinstance(value, str) and value:
            return value
    return record.id


def _top(records: list[BaseRecord], query: str) -> BaseRecord | None:
    results = search_keywords(records, query)
    return results[0].record if results else None


def run() -> list[str]:
    """Run the company memory demo and return deterministic output lines."""
    store = InMemoryStore()
    ingest_meeting(store, TRANSCRIPT, meeting_id="allhands", title="Company All-Hands")
    store.save_record(
        Commitment(
            id="allhands-overdue-1",
            owner_id="Priya",
            description="Ship the website redesign mockups",
            status=CommitmentStatus.PENDING,
            created_at=BASE_TIME,
            updated_at=BASE_TIME,
            due_at=REFERENCE_NOW - timedelta(days=5),
            source_meeting_id="allhands",
        )
    )

    records = store.list_records()
    lines = ["Company memory demo"]

    lines += heading("Why did we delay the launch?")
    answer = _top(records, "delay launch security review")
    lines.append(_label(answer) if answer else "(no answer found)")

    lines += heading("Who owns the website redesign?")
    owner = _top(records, "website redesign")
    if owner is not None:
        lines.append(f"{_label(owner)} (owner: {getattr(owner, 'owner_id', '-')})")
    else:
        lines.append("(no answer found)")

    lines += heading("What is still unresolved?")
    unresolved = [
        loop
        for loop in store.list_records("OpenLoop")
        if isinstance(loop, OpenLoop) and loop.status is OpenLoopStatus.OPEN
    ]
    for loop in unresolved:
        lines.append(f"- {loop.question}")
    if not unresolved:
        lines.append("(nothing unresolved)")

    lines += heading("What is overdue?")
    overdue = [
        record
        for record in records
        if is_overdue(record, REFERENCE_NOW)
    ]
    for record in overdue:
        lines.append(f"- {_label(record)}")
    if not overdue:
        lines.append("(nothing overdue)")
    return lines
