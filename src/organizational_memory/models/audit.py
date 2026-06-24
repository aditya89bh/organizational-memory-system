"""Audit metadata for tracking provenance of records."""

from dataclasses import dataclass, field, replace
from datetime import datetime

from organizational_memory.utils.time import utc_now


@dataclass(frozen=True, kw_only=True)
class AuditMetadata:
    """Provenance and change-tracking metadata for a record.

    Attributes:
        created_at: UTC timestamp when the record was created.
        updated_at: UTC timestamp of the last modification.
        created_by: Identifier of the actor who created the record.
        updated_by: Identifier of the actor who last modified the record.
        source: System or process the record originated from.
        trace_id: Correlation identifier linking related operations.
    """

    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
    created_by: str | None = None
    updated_by: str | None = None
    source: str | None = None
    trace_id: str | None = None

    def touched(self, *, updated_by: str | None = None) -> "AuditMetadata":
        """Return a copy with ``updated_at`` advanced to the current time."""
        return replace(self, updated_at=utc_now(), updated_by=updated_by)
