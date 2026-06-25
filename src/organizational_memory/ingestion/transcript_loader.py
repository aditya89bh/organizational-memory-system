"""Load plain-text meeting transcripts into a normalized structure."""

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from organizational_memory.constants import ENCODING


class TranscriptFormat(StrEnum):
    """The source format of a loaded transcript."""

    TEXT = "text"
    MARKDOWN = "markdown"


@dataclass(frozen=True, kw_only=True)
class Transcript:
    """A loaded, in-memory meeting transcript.

    Attributes:
        text: The full transcript text.
        source: Optional description of where the text came from.
        content_format: Whether the text is plain text or markdown.
    """

    text: str
    source: str | None = None
    content_format: TranscriptFormat = TranscriptFormat.TEXT
    lines: list[str] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "lines", self.text.splitlines())

    @property
    def is_empty(self) -> bool:
        """Return whether the transcript has no non-whitespace content."""
        return not self.text.strip()


def load_transcript_from_string(
    text: str,
    *,
    source: str | None = None,
    content_format: TranscriptFormat = TranscriptFormat.TEXT,
) -> Transcript:
    """Build a :class:`Transcript` from in-memory text."""
    return Transcript(text=text, source=source, content_format=content_format)


def load_transcript_from_file(path: str | Path) -> Transcript:
    """Load a :class:`Transcript` from a UTF-8 text file."""
    file_path = Path(path)
    text = file_path.read_text(encoding=ENCODING)
    return Transcript(
        text=text,
        source=str(file_path),
        content_format=TranscriptFormat.TEXT,
    )
