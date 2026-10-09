# Development

Run the default unit test suite:

```powershell
python -m pytest -q -m "not live"
```

Install development tools with `python -m pip install -e ".[dev]"`.
Run the same unit test and coverage gate used by CI:

```powershell
python -m pytest -q -m "not live" --cov=aspose_pdf_cloud_mcp --cov-report=term-missing
```

Additional local checks (Ruff and mypy currently use their default settings):

```powershell
python -m ruff format --check src test
python -m ruff check src test
python -m mypy src/aspose_pdf_cloud_mcp
python -m pip_audit .
```

See [architecture.md](architecture.md) before adding operations or changing
the CLI/MCP contract.

The MCP server targets the official Python SDK 2.x API. Use `MCPServer` from
`mcp.server.mcpserver`; the v1 `FastMCP` import path is not supported.

The enforced coverage floor is 75%. Raise it as uncovered CLI and error paths
gain tests; do not lower it to accommodate regressions.

Run live Aspose Cloud smoke tests only when you intentionally want to call
the real API:

```powershell
$env:ASPOSE_RUN_LIVE_TESTS = "1"
python -m pytest -q -m live
```

More live-test setup notes are in [live-tests.md](live-tests.md).

Build and validate the package distributions:

```powershell
python -m build
python -m twine check dist/*
```

## Security

Never commit real credentials. Keep `.env` local, prefer short-lived
environment variables in CI, and avoid pasting secrets into issue reports,
test output, logs, or prompts. See [security.md](security.md).

## Publishing

Publishing is handled by GitHub Actions with PyPI trusted publishing.
Follow [publishing.md](publishing.md) for account setup, GitHub environments,
release tags, TestPyPI checks, and troubleshooting. No PyPI token is required.

## Continuous integration

`.github/workflows/ci.yml` runs unit tests on Python 3.11, 3.12, and 3.13,
enforces the 75% coverage floor, builds and validates distributions, and
smoke-tests the installed wheel, console commands, MCP imports, and bundled
skill. Formatting, linting, typing, dependency auditing, and documentation
link checks are additional local checks, not enforced CI gates.

Live cloud tests are isolated in `.github/workflows/live-tests.yml`. They run
only through manual dispatch using credentials stored in the protected
`live-tests` GitHub environment.
