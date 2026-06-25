"""Tests for configuration validation."""

from pathlib import Path

import pytest

from organizational_memory.config_validation import (
    ValidationResult,
    validate_benchmark_type,
    validate_cli_config_file,
    validate_export_format,
    validate_extractors,
    validate_report_format,
    validate_report_type,
    validate_store_path,
    validate_store_type,
)
from organizational_memory.exceptions import ConfigurationError


def test_validation_result_valid() -> None:
    assert ValidationResult().valid
    assert not ValidationResult(["x"]).valid


def test_raise_if_invalid() -> None:
    ValidationResult().raise_if_invalid()
    with pytest.raises(ConfigurationError):
        ValidationResult(["bad"]).raise_if_invalid()


def test_store_path(tmp_path: Path) -> None:
    assert validate_store_path("memory.json").valid
    assert not validate_store_path("   ").valid
    assert not validate_store_path(tmp_path).valid


def test_store_type() -> None:
    assert validate_store_type("json").valid
    assert validate_store_type("sqlite").valid
    assert not validate_store_type("redis").valid


def test_cli_config_file(tmp_path: Path) -> None:
    good = tmp_path / "cfg.json"
    good.write_text('{"store": "m.json", "backend": "json"}', encoding="utf-8")
    assert validate_cli_config_file(good).valid

    bad = tmp_path / "bad.json"
    bad.write_text('{"backend": "redis"}', encoding="utf-8")
    assert not validate_cli_config_file(bad).valid

    assert not validate_cli_config_file(tmp_path / "missing.json").valid


def test_extractors() -> None:
    assert validate_extractors(["decision_extractor", "task_extractor"]).valid
    result = validate_extractors(["decision_extractor", "nope_extractor"])
    assert not result.valid
    assert "nope_extractor" in result.errors[0]


def test_formats() -> None:
    assert validate_report_format("markdown").valid
    assert not validate_report_format("pdf").valid
    assert validate_export_format("csv").valid
    assert not validate_export_format("xml").valid


def test_report_type() -> None:
    assert validate_report_type("weekly").valid
    assert not validate_report_type("daily").valid


def test_benchmark_type() -> None:
    assert validate_benchmark_type("all").valid
    assert not validate_benchmark_type("network").valid
