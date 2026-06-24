"""Tests for the Risk model."""

from organizational_memory.models import (
    Likelihood,
    Risk,
    RiskStatus,
    Severity,
)


def test_risk_defaults() -> None:
    risk = Risk(title="Vendor delay", description="Vendor may miss deadline")
    assert risk.severity is Severity.MEDIUM
    assert risk.likelihood is Likelihood.MEDIUM
    assert risk.status is RiskStatus.IDENTIFIED
    assert risk.owner_id is None


def test_risk_full_construction() -> None:
    risk = Risk(
        title="Vendor delay",
        description="Vendor may miss deadline",
        severity=Severity.HIGH,
        likelihood=Likelihood.LOW,
        owner_id="alice",
        status=RiskStatus.MITIGATED,
        source_meeting_id="m1",
        metadata={"vendor": "acme"},
    )
    assert risk.severity is Severity.HIGH
    assert risk.status is RiskStatus.MITIGATED


def test_risk_serialization() -> None:
    risk = Risk(title="Vendor delay", description="May miss deadline")
    data = risk.to_dict()
    assert data["title"] == "Vendor delay"
    assert data["severity"] == "medium"
