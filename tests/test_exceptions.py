"""Tests for the exception hierarchy."""

import pytest

from organizational_memory.exceptions import (
    ConfigurationError,
    OrganizationalMemoryError,
    StorageError,
    ValidationError,
)


@pytest.mark.parametrize(
    "exc_type",
    [ValidationError, StorageError, ConfigurationError],
)
def test_subclasses_derive_from_base(
    exc_type: type[OrganizationalMemoryError],
) -> None:
    assert issubclass(exc_type, OrganizationalMemoryError)


def test_base_can_be_caught() -> None:
    with pytest.raises(OrganizationalMemoryError):
        raise StorageError("disk full")
