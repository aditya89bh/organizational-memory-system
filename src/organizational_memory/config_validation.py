"""Deterministic validation for user-supplied configuration values.

These helpers centralize the rules the CLI and library rely on: valid store
paths and types, well-formed CLI config files, known extractor names, supported
report/export formats, and known benchmark types. Each validator returns a
:class:`ValidationResult`; nothing here performs network access.
"""

from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from organizational_memory.cli.common import BACKENDS
from organizational_memory.cli.config_file import load_config
from organizational_memory.exceptions import ConfigurationError
from organizational_memory.extraction.config import ALL_EXTRACTORS

SUPPORTED_STORE_TYPES: tuple[str, ...] = tuple(sorted(BACKENDS))
REPORT_FORMATS: tuple[str, ...] = ("markdown", "json")
EXPORT_FORMATS: tuple[str, ...] = ("json", "markdown", "csv")
REPORT_TYPES: tuple[str, ...] = (
    "meeting",
    "weekly",
    "follow-up",
    "organizational-memory",
    "decisions",
    "commitments",
    "open-loops",
)
BENCHMARK_TYPES: tuple[str, ...] = (
    "extraction",
    "recall",
    "reports",
    "analytics",
    "all",
)


@dataclass(frozen=True)
class ValidationResult:
    """The outcome of a validation: an (optionally empty) list of errors."""

    errors: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        """Return whether validation produced no errors."""
        return not self.errors

    def raise_if_invalid(self) -> None:
        """Raise :class:`ConfigurationError` if there are any errors."""
        if self.errors:
            raise ConfigurationError("; ".join(self.errors))


def _one_of(value: str, allowed: tuple[str, ...], label: str) -> list[str]:
    if value not in allowed:
        return [f"unknown {label}: {value!r}; expected one of {list(allowed)}"]
    return []


def validate_store_path(path: str | Path) -> ValidationResult:
    """Validate that ``path`` is usable as a store file path."""
    errors: list[str] = []
    text = str(path).strip()
    if not text:
        errors.append("store path must not be empty")
    elif Path(path).is_dir():
        errors.append(f"store path is a directory, not a file: {path}")
    return ValidationResult(errors)


def validate_store_type(store_type: str) -> ValidationResult:
    """Validate a store backend name."""
    return ValidationResult(_one_of(store_type, SUPPORTED_STORE_TYPES, "store type"))


def validate_cli_config_file(path: str | Path) -> ValidationResult:
    """Validate that ``path`` is a readable, well-formed CLI config file."""
    try:
        load_config(path)
    except ValueError as error:
        return ValidationResult([str(error)])
    return ValidationResult()


def validate_extractors(names: Iterable[str]) -> ValidationResult:
    """Validate that every name in ``names`` is a known extractor."""
    unknown = sorted(set(names) - ALL_EXTRACTORS)
    if unknown:
        return ValidationResult(
            [f"unknown extractors: {', '.join(unknown)}"]
        )
    return ValidationResult()


def validate_report_format(fmt: str) -> ValidationResult:
    """Validate a report output format."""
    return ValidationResult(_one_of(fmt, REPORT_FORMATS, "report format"))


def validate_export_format(fmt: str) -> ValidationResult:
    """Validate an export output format."""
    return ValidationResult(_one_of(fmt, EXPORT_FORMATS, "export format"))


def validate_report_type(report_type: str) -> ValidationResult:
    """Validate a report type name."""
    return ValidationResult(_one_of(report_type, REPORT_TYPES, "report type"))


def validate_benchmark_type(benchmark_type: str) -> ValidationResult:
    """Validate a benchmark type name."""
    return ValidationResult(
        _one_of(benchmark_type, BENCHMARK_TYPES, "benchmark type")
    )
