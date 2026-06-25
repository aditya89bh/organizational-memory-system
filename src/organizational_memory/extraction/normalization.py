"""Deterministic text normalization helpers for extraction.

These utilities clean raw transcript text without changing its meaning so that
downstream rule-based extractors operate on predictable input.
"""

import re
import unicodedata

_BULLET_CHARS = "-*\u2022\u00b7\u2013\u2014\u25cf\u25aa\u2043"
_BULLET_LINE = re.compile(rf"^(\s*)[{re.escape(_BULLET_CHARS)}]\s+")
_LEADING_TIMESTAMP = re.compile(
    r"^\s*[\[(]?\d{1,2}:\d{2}(?::\d{2})?\s*(?:[AaPp][Mm])?[\])]?\s*[-\u2013]?\s*"
)
_INLINE_SPACES = re.compile(r"[ \t]+")
_BLANK_RUNS = re.compile(r"\n{3,}")

_UNICODE_REPLACEMENTS = {
    "\u00a0": " ",
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2013": "-",
    "\u2014": "-",
}


def normalize_whitespace(text: str) -> str:
    """Collapse runs of inline whitespace and strip trailing spaces per line."""
    lines = [_INLINE_SPACES.sub(" ", line).rstrip() for line in text.splitlines()]
    return "\n".join(lines)


def normalize_bullets(text: str) -> str:
    """Rewrite assorted bullet markers to a canonical ``- `` prefix."""
    lines = [_BULLET_LINE.sub(r"\1- ", line) for line in text.splitlines()]
    return "\n".join(lines)


def strip_timestamps(text: str) -> str:
    """Remove leading timestamps such as ``[10:30]`` or ``(09:05 AM)``."""
    lines = [_LEADING_TIMESTAMP.sub("", line) for line in text.splitlines()]
    return "\n".join(lines)


def remove_empty_lines(text: str) -> str:
    """Collapse three or more consecutive newlines into a single blank line."""
    return _BLANK_RUNS.sub("\n\n", text)


def unicode_cleanup(text: str) -> str:
    """Apply NFKC normalization and replace common typographic characters."""
    normalized = unicodedata.normalize("NFKC", text)
    for source, target in _UNICODE_REPLACEMENTS.items():
        normalized = normalized.replace(source, target)
    return normalized


def normalize_text(text: str) -> str:
    """Apply the full normalization pipeline in a deterministic order."""
    result = unicode_cleanup(text)
    result = normalize_whitespace(result)
    result = normalize_bullets(result)
    result = remove_empty_lines(result)
    return result.strip("\n")


def shorten(text: str, *, limit: int = 80) -> str:
    """Return a single-line summary of ``text`` truncated to ``limit`` chars."""
    collapsed = _INLINE_SPACES.sub(" ", text.replace("\n", " ")).strip()
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 1].rstrip() + "\u2026"
