# Development

Run the default unit test suite:

```powershell
python -m pytest -q
```

Run the same local quality gates used by CI:

```powershell
python -m ruff format --check src test
python -m ruff check src test
python -m mypy
python -m pytest -q --cov=aspose_pdf_cloud_mcp --cov-report=term-missing
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

1. In PyPI, add a trusted publisher for repository
   `aspose-pdf-cloud/aspose-pdf-cloud-mcp`, workflow `publish.yml`, environment `pypi`,
   and project name `aspose-pdf-cloud-mcp`.
2. Ensure the release commit is clean and all tests pass. The package version
   is generated from Git metadata by `setuptools-scm`; do not edit a version
   string in the source tree.
3. Create and push a `vX.Y.Z` version tag, for example:

```powershell
git tag v1.0.0
git push origin v1.0.0
```

## Continuous integration

`.github/workflows/ci.yml` runs unit tests on Python 3.11, 3.12, and 3.13,
enforces formatting, linting, typing, and coverage, audits runtime dependencies,
checks documentation links, and smoke-tests built distributions.

Live cloud tests are isolated in `.github/workflows/live-tests.yml`. They run
only through manual dispatch using credentials stored in the protected
`live-tests` GitHub environment.
