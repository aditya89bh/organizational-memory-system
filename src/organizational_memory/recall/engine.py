"""Recall engine interface and shared result type.

A :class:`RecallEngine` retrieves organizational memory records using
deterministic search and ranking. Concrete engines are built on top of the
Phase 4 stores; this module only defines the contract and the immutable result
type returned to callers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from organizational_memory.schemas.base import BaseRecord


@dataclass(frozen=True)
class RecallResult:
    """A single retrieved record with its score and matching context.

    Attributes:
        record: The retrieved memory record.
        score: Deterministic relevance score; higher is more relevant.
        matched_fields: Names of the record fields that matched the query.
        details: Free-form, JSON-compatible context (match tokens, ranking
            components, and similar explainable metadata).
    """

    record: BaseRecord
    score: float = 0.0
    matched_fields: tuple[str, ...] = ()
    details: dict[str, Any] = field(default_factory=dict)


class RecallEngine(ABC):
    """Abstract contract for deterministic recall over stored records."""

    @abstractmethod
    def search(self, query: str) -> list[RecallResult]:
        """Return ranked results for ``query``, best first."""

    @abstractmethod
    def recall_by_id(
        self, record_type: str, record_id: str
    ) -> BaseRecord | None:
        """Return the record of ``record_type`` with ``record_id`` if present."""

    @abstractmethod
    def explain(self, query: str) -> list[RecallResult]:
        """Return results for ``query`` with full explanation details attached."""
