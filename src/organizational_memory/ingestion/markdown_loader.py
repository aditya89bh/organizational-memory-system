"""Load markdown meeting notes into a normalized transcript structure."""

from dataclasses import dataclass
from pathlib import Path

from organizational_memory.constants import ENCODING
from organizational_memory.ingestion.transcript_loader import (
    Transcript,
    TranscriptFormat,
)

_HEADING_PREFIX = "#"
_BULLET_PREFIXES: tuple[str, ...] = ("- ", "* ", "+ ")


@dataclass(frozen=True)
class MarkdownLine:
    """A single classified markdown line."""

    text: str
    line_number: int
    is_heading: bool
    is_bullet: bool


def _is_heading(stripped: str) -> bool:
    return stripped.startswith(_HEADING_PREFIX) and stripped.lstrip("#").startswith(" ")


def _is_bullet(stripped: str) -> bool:
    return any(stripped.startswith(prefix) for prefix in _BULLET_PREFIXES)


def classify_markdown_lines(text: str) -> list[MarkdownLine]:
    """Classify markdown lines, preserving headings and bullet lines."""
    classified: list[MarkdownLine] = []
    for index, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if not stripped:
            continue
        classified.append(
            MarkdownLine(
                text=raw,
                line_number=index,
                is_heading=_is_heading(stripped),
                is_bullet=_is_bullet(stripped),
            )
        )
    return classified


def heading_texts(text: str) -> list[str]:
    """Return the text of all markdown headings, without leading hashes."""
    return [
        line.text.strip().lstrip("#").strip()
        for line in classify_markdown_lines(text)
        if line.is_heading
    ]


def load_markdown_from_string(text: str, *, source: str | None = None) -> Transcript:
    """Build a markdown :class:`Transcript` from in-memory text."""
    return Transcript(
        text=text,
        source=source,
        content_format=TranscriptFormat.MARKDOWN,
    )


def load_markdown_from_file(path: str | Path) -> Transcript:
    """Load a markdown :class:`Transcript` from a UTF-8 file."""
    file_path = Path(path)
    text = file_path.read_text(encoding=ENCODING)
    return Transcript(
        text=text,
        source=str(file_path),
        content_format=TranscriptFormat.MARKDOWN,
    )
