"""Tests for extraction text normalization."""

from organizational_memory.extraction.normalization import (
    normalize_bullets,
    normalize_text,
    normalize_whitespace,
    remove_empty_lines,
    shorten,
    strip_timestamps,
    unicode_cleanup,
)


def test_normalize_whitespace() -> None:
    assert normalize_whitespace("a   b\t c  ") == "a b c"


def test_normalize_bullets() -> None:
    text = "* one\n\u2022 two\n  - three"
    assert normalize_bullets(text) == "- one\n- two\n  - three"


def test_strip_timestamps() -> None:
    assert strip_timestamps("[10:30] Rahul: hi") == "Rahul: hi"
    assert strip_timestamps("(09:05 AM) - note") == "note"


def test_remove_empty_lines() -> None:
    assert remove_empty_lines("a\n\n\n\nb") == "a\n\nb"


def test_unicode_cleanup() -> None:
    assert unicode_cleanup("we\u2019ll \u201cship\u201d\u00a0it") == 'we\'ll "ship" it'


def test_normalize_text_pipeline() -> None:
    raw = "#  Topic  \n\n\n*   we   decided\u00a0to ship  \n\n"
    assert normalize_text(raw) == "# Topic\n\n- we decided to ship"


def test_shorten_short_text() -> None:
    assert shorten("hello world") == "hello world"


def test_shorten_long_text() -> None:
    result = shorten("word " * 30, limit=20)
    assert len(result) == 20
    assert result.endswith("\u2026")
