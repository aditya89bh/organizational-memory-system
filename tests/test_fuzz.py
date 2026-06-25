"""Deterministic pseudo-fuzz tests.

These tests use fixed random seeds to generate many varied inputs and assert
invariants (no crashes, idempotency, round-trip equality, correct escaping).
They do not depend on any external fuzzing library and are fully reproducible.
"""

import csv
import io
import random
import string

import pytest

from organizational_memory.config_validation import (
    EXPORT_FORMATS,
    REPORT_FORMATS,
    SUPPORTED_STORE_TYPES,
    validate_export_format,
    validate_report_format,
    validate_store_type,
)
from organizational_memory.extraction.normalization import normalize_text
from organizational_memory.models import Decision, Task
from organizational_memory.models.enums import DecisionStatus, TaskStatus
from organizational_memory.persistence import from_dict, to_dict
from organizational_memory.recall.keyword_search import normalize
from organizational_memory.recall.query_parser import parse_query
from organizational_memory.reports.base import Report, ReportSection, ReportTable
from organizational_memory.reports.exporters.csv import CSVExporter
from organizational_memory.reports.exporters.markdown import MarkdownExporter
from organizational_memory.utils.time import parse_timestamp

_ALPHABET = string.ascii_letters + string.digits + " \t.,:;|\\-_'\"\n" + "\u2019\u201c"
_FIXED = parse_timestamp("2026-01-01T00:00:00Z")
ITERATIONS = 200


def _random_text(rng: random.Random, max_len: int = 40) -> str:
    length = rng.randint(0, max_len)
    return "".join(rng.choice(_ALPHABET) for _ in range(length))


def test_fuzz_text_normalization() -> None:
    rng = random.Random(1)
    for _ in range(ITERATIONS):
        text = _random_text(rng)
        once = normalize_text(text)
        assert isinstance(once, str)
        assert normalize_text(once) == once


def test_fuzz_keyword_normalize() -> None:
    rng = random.Random(2)
    for _ in range(ITERATIONS):
        text = _random_text(rng)
        once = normalize(text)
        assert normalize(once) == once


def test_fuzz_query_parser() -> None:
    rng = random.Random(3)
    keys = ["owner", "status", "type", "priority", "free", "meeting"]
    for _ in range(ITERATIONS):
        tokens = []
        for _ in range(rng.randint(0, 5)):
            key = rng.choice(keys)
            value = "".join(rng.choice(string.ascii_lowercase) for _ in range(3))
            tokens.append(f"{key}:{value}" if key != "free" else value)
        query = " ".join(tokens)
        parsed = parse_query(query)
        assert parsed.raw == query


def test_fuzz_query_parser_invalid_dates() -> None:
    rng = random.Random(33)
    for _ in range(50):
        value = "".join(rng.choice(string.ascii_lowercase) for _ in range(5))
        with pytest.raises(ValueError, match="invalid date"):
            parse_query(f"after:{value}")


def test_fuzz_serialization_round_trip() -> None:
    rng = random.Random(4)
    for index in range(ITERATIONS):
        title = "T" + _random_text(rng, 20)
        description = "D" + _random_text(rng, 60)
        owner = "u" + _random_text(rng, 8)
        if rng.random() < 0.5:
            model: Decision | Task = Decision(
                id=f"d{index}",
                title=title,
                description=description,
                owner_id=owner,
                status=rng.choice(list(DecisionStatus)),
                created_at=_FIXED,
                updated_at=_FIXED,
            )
        else:
            model = Task(
                id=f"t{index}",
                title=title,
                description=description,
                owner_id=owner,
                status=rng.choice(list(TaskStatus)),
                created_at=_FIXED,
                updated_at=_FIXED,
            )
        data = to_dict(model)
        restored = from_dict(type(model), data)
        assert restored == model


def test_fuzz_config_validation() -> None:
    rng = random.Random(5)
    for _ in range(ITERATIONS):
        candidate = _random_text(rng, 10).strip() or "x"
        store = validate_store_type(candidate)
        assert store.valid == (candidate in SUPPORTED_STORE_TYPES)
        report = validate_report_format(candidate)
        assert report.valid == (candidate in REPORT_FORMATS)
        export = validate_export_format(candidate)
        assert export.valid == (candidate in EXPORT_FORMATS)


def test_fuzz_csv_escaping() -> None:
    rng = random.Random(6)
    exporter = CSVExporter()
    for _ in range(ITERATIONS):
        cells = tuple(_random_text(rng, 15) for _ in range(3))
        table = ReportTable(title="T", columns=("a", "b", "c"), rows=[cells])
        rendered = exporter.export_table(table)
        parsed = list(csv.reader(io.StringIO(rendered)))
        assert parsed[0] == ["T"]
        assert parsed[1] == ["a", "b", "c"]
        assert tuple(parsed[2]) == cells


def test_fuzz_markdown_exporter() -> None:
    rng = random.Random(7)
    exporter = MarkdownExporter()
    for _ in range(ITERATIONS):
        cells = tuple(_random_text(rng, 15) for _ in range(2))
        table = ReportTable(title="T", columns=("a", "b"), rows=[cells])
        section = ReportSection(title=_random_text(rng, 10) or "S", tables=[table])
        report = Report(title="R", generated_at=_FIXED, sections=[section])
        rendered = exporter.export(report)
        assert isinstance(rendered, str)
        assert "#### T" in rendered
        for cell in cells:
            if "|" in cell:
                assert "\\|" in rendered
