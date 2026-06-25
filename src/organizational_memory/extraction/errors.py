"""Extraction-specific error hierarchy.

These errors derive from
:class:`~organizational_memory.exceptions.OrganizationalMemoryError` so callers
can catch all package failures uniformly, while still distinguishing
extraction problems from the rest of the system.
"""

from organizational_memory.exceptions import OrganizationalMemoryError


class ExtractionError(OrganizationalMemoryError):
    """Base class for all extraction failures."""


class EmptyTranscriptError(ExtractionError):
    """Raised when a transcript has no extractable content."""


class UnreadableSourceError(ExtractionError):
    """Raised when an input file cannot be read."""


class UnsupportedInputError(ExtractionError):
    """Raised when the extraction input type is not supported."""


class InvalidExtractionConfigError(ExtractionError):
    """Raised when an extraction configuration is invalid."""


__all__ = [
    "EmptyTranscriptError",
    "ExtractionError",
    "InvalidExtractionConfigError",
    "UnreadableSourceError",
    "UnsupportedInputError",
]
