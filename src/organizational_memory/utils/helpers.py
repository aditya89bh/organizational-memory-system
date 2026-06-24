"""Common, dependency-free helper functions."""

import re
import uuid
from pathlib import Path

_SLUG_NON_ALNUM = re.compile(r"[^a-z0-9]+")
_SLUG_TRIM = re.compile(r"^-+|-+$")


def generate_id() -> str:
    """Return a random, URL-safe identifier (32 hex characters)."""
    return uuid.uuid4().hex


def slugify(text: str) -> str:
    """Convert arbitrary text into a lowercase, hyphen-separated slug.

    Raises:
        ValueError: If ``text`` contains no alphanumeric characters.
    """
    lowered = text.strip().lower()
    hyphenated = _SLUG_NON_ALNUM.sub("-", lowered)
    slug = _SLUG_TRIM.sub("", hyphenated)
    if not slug:
        raise ValueError(f"Cannot derive a slug from {text!r}")
    return slug


def ensure_directory(path: Path) -> Path:
    """Create ``path`` (and parents) if needed and return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path
