"""Tests for audit metadata."""

from organizational_memory.models import AuditMetadata


def test_audit_metadata_defaults() -> None:
    audit = AuditMetadata()
    assert audit.created_at.tzinfo is not None
    assert audit.updated_at.tzinfo is not None
    assert audit.created_by is None
    assert audit.trace_id is None


def test_audit_metadata_full() -> None:
    audit = AuditMetadata(
        created_by="alice",
        updated_by="bob",
        source="import",
        trace_id="trace-123",
    )
    assert audit.created_by == "alice"
    assert audit.source == "import"
    assert audit.trace_id == "trace-123"


def test_audit_touched_advances_updated_at() -> None:
    audit = AuditMetadata(created_by="alice")
    updated = audit.touched(updated_by="bob")
    assert updated.created_at == audit.created_at
    assert updated.created_by == "alice"
    assert updated.updated_by == "bob"
    assert updated.updated_at >= audit.updated_at
