"""Dependency domain model."""

from dataclasses import dataclass, field

from organizational_memory.schemas import BaseRecord


@dataclass(kw_only=True)
class Dependency(BaseRecord):
    """A directed dependency between two records.

    Attributes:
        source_id: Identifier of the dependent (downstream) record.
        target_id: Identifier of the depended-upon (upstream) record.
        dependency_type: Nature of the dependency (e.g. ``"blocks"``).
        description: Optional human-readable explanation.
        status: Lifecycle status of the dependency.
        metadata: Free-form string key/value annotations.
    """

    source_id: str
    target_id: str
    dependency_type: str = "blocks"
    description: str | None = None
    status: str = "pending"
    metadata: dict[str, str] = field(default_factory=dict)
