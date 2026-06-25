"""Deterministic checks that relative documentation links resolve."""

import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _markdown_files() -> list[Path]:
    files = [_REPO_ROOT / "README.md", _REPO_ROOT / "CHANGELOG.md"]
    files.extend(sorted((_REPO_ROOT / "docs").rglob("*.md")))
    files.extend(sorted((_REPO_ROOT / "release_artifacts").rglob("*.md")))
    return [path for path in files if path.is_file()]


def _relative_targets(text: str) -> list[str]:
    targets: list[str] = []
    for raw in _LINK_RE.findall(text):
        target = raw.strip()
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        target = target.split("#", 1)[0]
        if target:
            targets.append(target)
    return targets


def test_relative_doc_links_resolve() -> None:
    broken: list[str] = []
    for md in _markdown_files():
        for target in _relative_targets(md.read_text(encoding="utf-8")):
            resolved = (md.parent / target).resolve()
            if not resolved.exists():
                broken.append(f"{md.relative_to(_REPO_ROOT)} -> {target}")
    assert broken == [], broken
