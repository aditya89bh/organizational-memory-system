# Release checklist

A deterministic, local checklist for cutting a release. Every step runs offline.

## 1. Quality gate

```bash
ruff check .
mypy .
pytest
```

All three must pass with no errors.

## 2. Build

```bash
python -m build
```

Confirm `dist/` contains a source distribution (`.tar.gz`) and a wheel (`.whl`).

## 3. Package verification

```bash
python scripts/verify_package.py
```

All checks (imports, CLI entry point, version, examples, docs, pyproject
metadata) must report PASS.

## 4. Docs check

- [ ] [README](../README.md) is accurate and shows the current version banner.
- [ ] [docs/index.md](index.md) links all key documents.
- [ ] [Release notes](releases/v0.1.0.md) exist for the version.
- [ ] [Changelog](../CHANGELOG.md) has a section for the version.

## 5. Attribution checks

Tracked text files and recent commits must contain no automated-tool attribution
(no co-author trailers, no generated-by markers, no assistant or agent strings).

```bash
# Scans tracked text files for forbidden attribution markers
pytest tests/test_release_validation.py

# Orchestrated release checks (includes the attribution scan)
python scripts/run_release_validation.py

# Confirm the recent commits are authored only by the maintainer
git shortlog -sne HEAD~21..HEAD
```

The attribution scan must report clean; the shortlog must show only the
maintainer. The forbidden markers themselves are defined in
[`scripts/run_release_validation.py`](../scripts/run_release_validation.py) and in
`tests/test_release_validation.py`.

## 6. Commit count check

```bash
git rev-list --count HEAD
```

For v0.1.0 the expected total is **225** commits.

## 7. Tag check

After all checks pass, create a lightweight tag (no tag message, to avoid any
unwanted attribution):

```bash
git tag v0.1.0
git tag --list "v0.1.0"
```

## 8. Push

```bash
git push origin main
git push origin v0.1.0
```

## 9. Post-release verification

```bash
git status
git rev-list --count HEAD
git tag --list "v0.1.0"
git ls-remote --tags origin v0.1.0
```

Expected: working tree clean, total commits 225, `v0.1.0` present both locally and
on `origin`. A post-release verification script under `scripts/` automates several
of these checks.
