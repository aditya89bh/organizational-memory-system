"""Tests for deterministic keyword search."""

from organizational_memory.models import Decision, Task
from organizational_memory.recall.keyword_search import (
    extract_text_fields,
    score_record,
    search_keywords,
    tokenize,
)


def test_tokenize_normalizes() -> None:
    assert tokenize("Hello, World! 123") == ["hello", "world", "123"]


def test_extract_text_fields_excludes_identity() -> None:
    decision = Decision(id="d1", title="Adopt SQLite", description="use sqlite")
    fields = extract_text_fields(decision)
    assert "id" not in fields
    assert "created_at" not in fields
    assert fields["title"] == "Adopt SQLite"
    assert fields["status"] == "proposed"


def test_score_record_token_coverage() -> None:
    decision = Decision(title="Adopt SQLite store", description="use sqlite")
    match = score_record(decision, "sqlite missing")
    assert "sqlite" in match.matched_tokens
    assert match.score == 0.5  # 1 of 2 tokens


def test_score_record_phrase_bonus() -> None:
    decision = Decision(title="Adopt SQLite store", description="use it")
    match = score_record(decision, "adopt sqlite")
    assert match.phrase_match is True
    assert match.score == 1.5  # full coverage (1.0) + phrase bonus (0.5)


def test_score_record_empty_query() -> None:
    decision = Decision(title="x", description="y")
    assert score_record(decision, "   ").score == 0.0


def test_search_keywords_ranks_and_filters() -> None:
    records = [
        Decision(id="d1", title="Adopt SQLite", description="sqlite storage"),
        Decision(id="d2", title="Pricing review", description="discuss pricing"),
        Task(id="t1", title="Migrate to SQLite", description="sqlite", owner_id="a"),
    ]
    results = search_keywords(records, "sqlite")
    ids = [r.record.id for r in results]
    assert "d2" not in ids
    assert set(ids) == {"d1", "t1"}
    assert all(r.score > 0 for r in results)


def test_search_keywords_case_insensitive() -> None:
    records = [Decision(id="d1", title="KUBERNETES rollout", description="ops")]
    assert len(search_keywords(records, "kubernetes")) == 1
