"""Deterministic keyword search over stored records.

Search is purely lexical: queries and record text are normalized into tokens,
matched case-insensitively, and scored by token coverage with a bonus for exact
phrase matches. There are no embeddings, models, or network calls.
"""

import dataclasses
import re
from collections.abc import Iterable
from enum import Enum
from typing import Any

from organizational_memory.recall.engine import RecallResult
from organizational_memory.schemas.base import BaseRecord

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_EXCLUDED_FIELDS = frozenset({"id", "created_at", "updated_at"})


def tokenize(text: str) -> list[str]:
    """Split ``text`` into lowercase alphanumeric tokens."""
    return _TOKEN_RE.findall(text.lower())


def normalize(text: str) -> str:
    """Return ``text`` lowercased with tokens collapsed to single spaces."""
    return " ".join(tokenize(text))


def _stringify(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, Enum):
        return str(value.value)
    if isinstance(value, (list, tuple)):
        return " ".join(_stringify(item) for item in value)
    if isinstance(value, dict):
        return " ".join(_stringify(item) for item in value.values())
    return ""


def extract_text_fields(record: BaseRecord) -> dict[str, str]:
    """Return a mapping of field name to searchable text for ``record``.

    Identity and timestamp fields are excluded; enums, string lists, and string
    dictionaries are flattened to plain text.
    """
    fields: dict[str, str] = {}
    for field in dataclasses.fields(record):
        if field.name in _EXCLUDED_FIELDS:
            continue
        text = _stringify(getattr(record, field.name)).strip()
        if text:
            fields[field.name] = text
    return fields


@dataclasses.dataclass(frozen=True)
class KeywordMatch:
    """The outcome of scoring a single record against a keyword query."""

    score: float
    matched_tokens: tuple[str, ...]
    matched_fields: tuple[str, ...]
    phrase_match: bool


def score_record(record: BaseRecord, query: str) -> KeywordMatch:
    """Score ``record`` against ``query`` deterministically.

    The base score is the fraction of distinct query tokens found anywhere in
    the record. An exact phrase match (the normalized query appearing as a
    substring of a field) adds a fixed bonus.
    """
    query_tokens = list(dict.fromkeys(tokenize(query)))
    if not query_tokens:
        return KeywordMatch(0.0, (), (), False)

    field_texts = extract_text_fields(record)
    matched_tokens: list[str] = []
    matched_fields: set[str] = set()
    phrase = normalize(query)
    phrase_match = False

    for field_name, text in field_texts.items():
        field_tokens = set(tokenize(text))
        field_hit = False
        for token in query_tokens:
            if token in field_tokens:
                field_hit = True
                if token not in matched_tokens:
                    matched_tokens.append(token)
        if phrase and len(query_tokens) > 1 and phrase in normalize(text):
            phrase_match = True
            field_hit = True
        if field_hit:
            matched_fields.add(field_name)

    base = len(matched_tokens) / len(query_tokens)
    score = base + (0.5 if phrase_match else 0.0)
    return KeywordMatch(
        score=round(score, 6),
        matched_tokens=tuple(matched_tokens),
        matched_fields=tuple(sorted(matched_fields)),
        phrase_match=phrase_match,
    )


def search_keywords(
    records: Iterable[BaseRecord],
    query: str,
    *,
    min_score: float = 0.0,
) -> list[RecallResult]:
    """Return ranked :class:`RecallResult` objects for ``query``.

    Results with a score at or below ``min_score`` are excluded. Ties are broken
    deterministically by record id.
    """
    results: list[RecallResult] = []
    for record in records:
        match = score_record(record, query)
        if match.score <= min_score:
            continue
        results.append(
            RecallResult(
                record=record,
                score=match.score,
                matched_fields=match.matched_fields,
                details={
                    "matched_tokens": list(match.matched_tokens),
                    "phrase_match": match.phrase_match,
                },
            )
        )
    results.sort(key=lambda result: (-result.score, result.record.id))
    return results
