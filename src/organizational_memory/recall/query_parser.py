"""Deterministic parser for compact, structured recall queries.

Queries mix free text with ``key:value`` filters, for example::

    owner:aditya status:open kubernetes
    type:decision after:2026-01-01 before:2026-02-01 pricing
    priority:high severity:critical

Parsing is deterministic and rule-based: recognized keys become typed fields and
everything else is collected as free text. There is no LLM or network access.
"""

import re
from dataclasses import dataclass
from datetime import datetime

from organizational_memory.utils.time import parse_timestamp

_TOKEN_RE = re.compile(r"^([a-zA-Z_]+):(.+)$")

TYPE_ALIASES: dict[str, str] = {
    "decision": "Decision",
    "task": "Task",
    "commitment": "Commitment",
    "openloop": "OpenLoop",
    "open_loop": "OpenLoop",
    "meeting": "Meeting",
    "risk": "Risk",
    "participant": "Participant",
    "event": "MemoryEvent",
    "memoryevent": "MemoryEvent",
    "actionitem": "ActionItem",
    "dependency": "Dependency",
}

_FILTER_KEYS = frozenset(
    {"type", "owner", "status", "priority", "severity", "after", "before", "meeting"}
)


@dataclass(frozen=True)
class ParsedQuery:
    """A structured recall query parsed from raw text."""

    raw: str
    text: str = ""
    record_type: str | None = None
    owner: str | None = None
    status: str | None = None
    priority: str | None = None
    severity: str | None = None
    source_meeting_id: str | None = None
    after: datetime | None = None
    before: datetime | None = None


def _parse_date(value: str, key: str) -> datetime:
    try:
        return parse_timestamp(value)
    except ValueError as error:
        raise ValueError(f"invalid date for {key!r}: {value!r}") from error


def parse_query(query: str) -> ParsedQuery:
    """Parse ``query`` into a :class:`ParsedQuery`.

    Unrecognized ``key:value`` tokens are treated as free text so the parser is
    forgiving. Raises ``ValueError`` only for malformed dates.
    """
    record_type: str | None = None
    owner: str | None = None
    status: str | None = None
    priority: str | None = None
    severity: str | None = None
    meeting: str | None = None
    after: datetime | None = None
    before: datetime | None = None
    text_tokens: list[str] = []

    for token in query.split():
        match = _TOKEN_RE.match(token)
        key = match.group(1).lower() if match else ""
        if not match or key not in _FILTER_KEYS:
            text_tokens.append(token)
            continue
        value = match.group(2)
        if key == "type":
            record_type = TYPE_ALIASES.get(value.lower(), value)
        elif key == "owner":
            owner = value
        elif key == "status":
            status = value.lower()
        elif key == "priority":
            priority = value.lower()
        elif key == "severity":
            severity = value.lower()
        elif key == "meeting":
            meeting = value
        elif key == "after":
            after = _parse_date(value, "after")
        elif key == "before":
            before = _parse_date(value, "before")

    return ParsedQuery(
        raw=query,
        text=" ".join(text_tokens),
        record_type=record_type,
        owner=owner,
        status=status,
        priority=priority,
        severity=severity,
        source_meeting_id=meeting,
        after=after,
        before=before,
    )
