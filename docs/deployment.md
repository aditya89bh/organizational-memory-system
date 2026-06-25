# Deployment

This guide covers installing and running the organizational-memory toolkit
locally. The toolkit is a local, deterministic command-line tool and library; it
runs on a single machine, makes no network calls, and uses no external models.

## Requirements

- Python 3.11 or newer
- `git` (for cloning the repository)

## Local install (from source)

```bash
git clone https://github.com/aditya89bh/organizational-memory-system.git
cd organizational-memory-system
python -m venv .venv
source .venv/bin/activate
pip install .
```

This installs the package and the `organizational-memory` console script.

## Editable install (for development)

```bash
pip install -e ".[dev]"
```

The editable install adds the development dependencies (ruff, mypy, pytest,
pytest-cov, build). See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Wheel install (from a built artifact)

Build distributions and install the wheel:

```bash
python -m build           # writes dist/*.whl and dist/*.tar.gz
pip install dist/organizational_memory-*.whl
```

## CLI usage

After installation the CLI is available as `organizational-memory`:

```bash
organizational-memory --version
organizational-memory --help
organizational-memory demo all
```

See the [user guide](user_guide.md) and
[interactive walkthrough](interactive_walkthrough.md) for full command coverage.

## Local JSON store setup

The JSON store keeps all records in a single, human-readable file:

```bash
organizational-memory ingest meeting.txt --store memory.json --backend json
organizational-memory recall "release" --store memory.json --backend json
```

The file is created on first use. It is rewritten on every mutation, which keeps
output deterministic and easy to inspect or back up.

## Local SQLite store setup

The SQLite store keeps records in a single database file and is the better choice
for larger datasets:

```bash
organizational-memory ingest meeting.txt --store memory.db --backend sqlite
organizational-memory recall "release" --store memory.db --backend sqlite
```

Both backends implement the same interface, so commands are identical apart from
`--backend`.

## CI expectations

A continuous-integration run should reproduce the local quality gate exactly:

```bash
pip install -e ".[dev]"
ruff check .
mypy .
pytest
python -m build
```

Optionally enforce coverage and verify the package:

```bash
pytest --cov --cov-report=json
python scripts/check_coverage.py --coverage-file coverage.json --min 80
python scripts/verify_package.py
```

CI must remain green and must not introduce any tool attribution into commits.

## Release artifact verification

Before publishing or sharing build artifacts:

```bash
# Build and inspect the artifacts
python -m build
ls -l dist/

# Validate the source tree is release-ready
pytest tests/test_release_validation.py
python scripts/verify_package.py

# Smoke-test the built wheel in a clean environment
python -m venv /tmp/om-verify
/tmp/om-verify/bin/pip install dist/organizational_memory-*.whl
/tmp/om-verify/bin/organizational-memory --version
```

If all checks pass, the artifacts in `dist/` are ready to distribute.
