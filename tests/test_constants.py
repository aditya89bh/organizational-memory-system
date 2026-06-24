"""Tests for project constants."""

from pathlib import Path

from organizational_memory import constants


def test_app_identifiers_are_set() -> None:
    assert constants.APP_NAME == "organizational-memory"
    assert constants.APP_DISPLAY_NAME


def test_default_paths_are_under_data_dir() -> None:
    assert isinstance(constants.DEFAULT_DATA_DIR, Path)
    assert constants.DEFAULT_STORAGE_DIR.parent == constants.DEFAULT_DATA_DIR
    assert constants.DEFAULT_LOG_DIR.parent == constants.DEFAULT_DATA_DIR


def test_supported_file_types_are_normalized() -> None:
    assert ".md" in constants.SUPPORTED_FILE_TYPES
    for ext in constants.SUPPORTED_FILE_TYPES:
        assert ext.startswith(".")
        assert ext == ext.lower()
