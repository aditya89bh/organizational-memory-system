"""Tests for utility helpers."""

from pathlib import Path

import pytest

from organizational_memory.utils import ensure_directory, generate_id, slugify


def test_generate_id_is_unique_hex() -> None:
    first = generate_id()
    second = generate_id()
    assert first != second
    assert len(first) == 32
    assert all(c in "0123456789abcdef" for c in first)


def test_slugify_normalizes_text() -> None:
    assert slugify("  Quarterly Planning Meeting!  ") == "quarterly-planning-meeting"
    assert slugify("Q3 / 2026 Review") == "q3-2026-review"


def test_slugify_rejects_empty_result() -> None:
    with pytest.raises(ValueError, match="Cannot derive a slug"):
        slugify("!!!")


def test_ensure_directory_creates_path(tmp_path: Path) -> None:
    target = tmp_path / "a" / "b"
    result = ensure_directory(target)
    assert result == target
    assert target.is_dir()
