"""Project-wide constants.

Centralizes application identifiers, default filesystem paths, and the set of
input file types the system can ingest.
"""

from pathlib import Path
from typing import Final

APP_NAME: Final = "organizational-memory"
"""Distribution / package identifier."""

APP_DISPLAY_NAME: Final = "Organizational Memory System"
"""Human-readable application name."""

ENCODING: Final = "utf-8"
"""Default text encoding used for reading and writing files."""

DEFAULT_DATA_DIR: Final = Path.home() / ".organizational_memory"
"""Root directory for persisted organizational memory data."""

DEFAULT_STORAGE_DIR: Final = DEFAULT_DATA_DIR / "storage"
"""Directory holding structured memory records."""

DEFAULT_LOG_DIR: Final = DEFAULT_DATA_DIR / "logs"
"""Directory holding application log files."""

SUPPORTED_FILE_TYPES: Final[frozenset[str]] = frozenset(
    {".txt", ".md", ".vtt", ".srt", ".json"}
)
"""File extensions accepted by the ingestion pipeline (lower-cased, dotted)."""
