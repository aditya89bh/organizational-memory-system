"""Tests for the Risk model."""

from organizational_memory.models import Risk


def test_risk_defaults() -> None:
    risk = Risk(title="Vendor delay", description="Vendor may miss deadline")
    assert risk.severity == "medium"
    assert risk.likelihood == "medium"
    assert risk.status == "identified"
    assert risk.owner_id is None


def test_risk_full_construction() -> None:
    risk = Risk(
        title="Vendor delay",
        description="Vendor may miss deadline",
        severity="high",
        likelihood="low",
        owner_id="alice",
        status="mitigated",
        source_meeting_id="m1",
        metadata={"vendor": "acme"},
    )
    assert risk.severity == "high"
    assert risk.status == "mitigated"


def test_risk_serialization() -> None:
    risk = Risk(title="Vendor delay", description="May miss deadline")
    data = risk.to_dict()
    assert data["title"] == "Vendor delay"
    assert data["severity"] == "medium"
