"""Custom exception hierarchy for the organizational memory system.

All errors raised by the package derive from :class:`OrganizationalMemoryError`
so callers can catch every domain-specific failure with a single except clause.
"""


class OrganizationalMemoryError(Exception):
    """Base class for all errors raised by the package."""


class ValidationError(OrganizationalMemoryError):
    """Raised when data fails validation rules."""


class StorageError(OrganizationalMemoryError):
    """Raised when persisting or retrieving memory records fails."""


class ConfigurationError(OrganizationalMemoryError):
    """Raised when the application configuration is invalid or incomplete."""


__all__ = [
    "ConfigurationError",
    "OrganizationalMemoryError",
    "StorageError",
    "ValidationError",
]
