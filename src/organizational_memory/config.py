"""Configuration models for the organizational memory system."""

from dataclasses import dataclass
from pathlib import Path

from organizational_memory import constants

VALID_LOG_LEVELS: frozenset[str] = frozenset(
    {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}
)


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Immutable application configuration.

    Holds the filesystem locations and runtime options the system needs. All
    fields default to the values defined in :mod:`organizational_memory.constants`.
    """

    data_dir: Path = constants.DEFAULT_DATA_DIR
    storage_dir: Path = constants.DEFAULT_STORAGE_DIR
    log_dir: Path = constants.DEFAULT_LOG_DIR
    log_level: str = "INFO"
    encoding: str = constants.ENCODING

    def __post_init__(self) -> None:
        if self.log_level not in VALID_LOG_LEVELS:
            raise ValueError(
                f"Invalid log level {self.log_level!r}; "
                f"expected one of {sorted(VALID_LOG_LEVELS)}."
            )

    @classmethod
    def default(cls) -> "AppConfig":
        """Return a configuration populated entirely with default values."""
        return cls()
