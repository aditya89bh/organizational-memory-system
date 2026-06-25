# Testing

The project uses `pytest` for testing and ships a deterministic test suite that
runs without any network access or external services.

## Running the suite

```bash
pytest
```

The full quality gate is:

```bash
ruff check .
mypy .
pytest
```

## Coverage reporting

Coverage is measured with [`pytest-cov`](https://pytest-cov.readthedocs.io/),
which is included in the development extras (`pip install -e ".[dev]"`).

Coverage is configured in `pyproject.toml` under `[tool.coverage.*]`:

- `branch = true` enables branch coverage.
- `source = ["organizational_memory"]` scopes coverage to the package.
- `[tool.coverage.json]` writes a machine-readable `coverage.json`.

Coverage is intentionally **not** enabled by default in `addopts`, so a plain
`pytest` run stays fast and stable. Opt in explicitly:

```bash
# Terminal report with missing lines
pytest --cov --cov-report=term-missing

# Machine-readable JSON (used by the coverage gate)
pytest --cov --cov-report=json
```

The JSON report is written to `coverage.json` and can be consumed by the
coverage gate (see [`scripts/check_coverage.py`](../scripts/check_coverage.py)).

## Notes

- Tests avoid fragile timing assertions; performance work reports counts and
  elapsed time rather than enforcing hard thresholds.
- Time-dependent behavior is exercised with explicit reference timestamps so the
  suite is reproducible across machines.
