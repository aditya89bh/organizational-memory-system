"""Report exporter interface.

Defines the typed contract all report exporters implement: a pure ``export``
that renders a report to a string, plus metadata describing the produced
artifact (file extension and content type).
"""

from abc import ABC, abstractmethod

from organizational_memory.reports.base import Report


class ReportExporter(ABC):
    """Abstract base class for deterministic report exporters."""

    @property
    @abstractmethod
    def supported_extension(self) -> str:
        """Return the file extension (without dot) for exported artifacts."""

    @property
    @abstractmethod
    def content_type(self) -> str:
        """Return the MIME content type for exported artifacts."""

    @abstractmethod
    def export(self, report: Report) -> str:
        """Render ``report`` to a deterministic serialized string."""

    def filename(self, stem: str) -> str:
        """Return ``stem`` with this exporter's extension appended."""
        return f"{stem}.{self.supported_extension}"
