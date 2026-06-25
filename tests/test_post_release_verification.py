"""Tests for post-release verification helpers.

These do not require the release tag to exist; helpers are exercised with
explicit inputs so the suite stays deterministic before tagging.
"""

import importlib.util
import sys
from pathlib import Path
from typing import Any

_SCRIPT = (
    Path(__file__).resolve().parents[1] / "scripts" / "post_release_verification.py"
)


def _load() -> Any:
    spec = importlib.util.spec_from_file_location("post_release_verification", _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


pr = _load()


def test_verify_tag_exists() -> None:
    assert pr.verify_tag_exists(["v0.1.0", "v0.0.1"])
    assert not pr.verify_tag_exists(["v0.0.1"])


def test_verify_commit_count() -> None:
    assert pr.verify_commit_count(225)
    assert not pr.verify_commit_count(224)


def test_verify_build_artifacts(tmp_path: Path) -> None:
    assert not pr.verify_build_artifacts(tmp_path)
    (tmp_path / "pkg-0.1.0-py3-none-any.whl").write_text("x", encoding="utf-8")
    assert not pr.verify_build_artifacts(tmp_path)
    (tmp_path / "pkg-0.1.0.tar.gz").write_text("x", encoding="utf-8")
    assert pr.verify_build_artifacts(tmp_path)


def test_verify_build_artifacts_missing_dir(tmp_path: Path) -> None:
    assert not pr.verify_build_artifacts(tmp_path / "nope")


def test_verify_release_docs_present() -> None:
    assert pr.verify_release_docs() == []


def test_verify_release_docs_missing(tmp_path: Path) -> None:
    missing = pr.verify_release_docs(root=tmp_path)
    assert set(missing) == set(pr.RELEASE_DOCS)


def test_verify_changelog_has_version() -> None:
    assert pr.verify_changelog_has_version("## [0.1.0] - 2026-06-25")
    assert pr.verify_changelog_has_version("## 0.1.0")
    assert not pr.verify_changelog_has_version("## [0.0.9]")


def test_scan_forbidden(tmp_path: Path) -> None:
    bad = tmp_path / "bad.md"
    bad.write_text(pr.FORBIDDEN_STRINGS[0].upper(), encoding="utf-8")
    assert pr.scan_forbidden([bad], root=tmp_path)
    good = tmp_path / "good.md"
    good.write_text("clean text", encoding="utf-8")
    assert pr.scan_forbidden([good], root=tmp_path) == []


def test_run_all_named_checks() -> None:
    results = pr.run_all()
    names = {result.name for result in results}
    assert names == {
        "tag_exists",
        "commit_count",
        "build_artifacts",
        "release_docs",
        "changelog_version",
        "attribution_scan",
    }


def test_format_report() -> None:
    results = [pr.CheckResult("demo", False, "nope")]
    assert "FAIL demo" in pr.format_report(results)
