"""Tests for speaker turn parsing."""

from organizational_memory.extraction.speakers import (
    match_speaker,
    parse_speaker_turns,
)


def test_colon_separator() -> None:
    match = match_speaker("Aditya: We should ship this by Friday.")
    assert match is not None
    assert match.speaker == "Aditya"
    assert match.text == "We should ship this by Friday."
    assert match.timestamp is None


def test_dash_separator() -> None:
    match = match_speaker("Priya - I will prepare the proposal.")
    assert match is not None
    assert match.speaker == "Priya"
    assert match.text == "I will prepare the proposal."


def test_timestamp_prefix() -> None:
    match = match_speaker("[10:30] Rahul: The API is blocked.")
    assert match is not None
    assert match.speaker == "Rahul"
    assert match.timestamp == "10:30"
    assert match.text == "The API is blocked."


def test_multiword_speaker() -> None:
    match = match_speaker("Maria Garcia: Sounds good.")
    assert match is not None
    assert match.speaker == "Maria Garcia"


def test_non_speaker_lines() -> None:
    assert match_speaker("We should ship - maybe next week") is None
    assert match_speaker("- a bullet item") is None
    assert match_speaker("## Heading") is None
    assert match_speaker("just a sentence.") is None


def test_parse_speaker_turns_line_numbers() -> None:
    text = "Intro line\nAlice: hello\n\nBob: hi there"
    turns = parse_speaker_turns(text)
    assert [(t.speaker, t.line_number) for t in turns] == [
        ("Alice", 2),
        ("Bob", 4),
    ]
