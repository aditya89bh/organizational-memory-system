"""Risk domain model."""

from dataclasses import dataclass, field

from organizational_memory.models.enums import Likelihood, RiskStatus, Severity
from organizational_memory.schemas import BaseRecord


@dataclass(kw_only=True)
class Risk(BaseRecord):
    """A risk identified by the organization.

    Attributes:
        title: Short statement of the risk.
        description: Fuller description of the risk.
        severity: Impact level if the risk materializes.
        likelihood: Probability that the risk materializes.
        owner_id: Identifier of the participant accountable for the risk.
        status: Lifecycle status of the risk.
        source_meeting_id: Meeting the risk originated from, if any.
        metadata: Free-form string key/value annotations.
    """

    title: str
    description: str
    severity: Severity = Severity.MEDIUM
    likelihood: Likelihood = Likelihood.MEDIUM
    owner_id: str | None = None
    status: RiskStatus = RiskStatus.IDENTIFIED
    source_meeting_id: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)
