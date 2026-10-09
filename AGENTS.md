# Repository guidance

## Project

Aspose.PDF Cloud CLI and MCP server, implemented in Python 3.11+ with a
`src/` layout. `pyproject.toml` declares Aspose SDK 26.x, MCP SDK 2.x, Typer,
Rich, and typing-extensions. Both `aspose-pdf-cloud-cli` and `apdf` invoke
`aspose_pdf_cloud_mcp.cli:main`; `apdf mcp serve` starts the MCP server.

## Code organization

- `src/aspose_pdf_cloud_mcp/`: application code.
- `storage_operations.py`, `document_operations.py`, `extraction_operations.py`,
  and `output_operations.py`: domain operations.
- `operations.py`: stable compatibility facade used by both transports.
- `cli.py`: Typer commands and human/JSON output.
- `mcp_server.py`: MCP tool declarations; `mcp_adapter.py`: response envelopes.
- `config.py` and `client.py`: credentials/configuration and SDK client creation.
- `page_selectors.py`, `result_types.py`, `errors.py`, and `io_utils.py`:
  shared parsing, typed contracts, error sanitization, and atomic writes.
- `test/`: pytest unit, contract, and opt-in live tests.
- `docs/` and `examples/`: usage, architecture, security, and client configuration.
- `src/aspose_pdf_cloud_mcp/resources/skills/aspose-pdf-cloud-mcp/`: bundled
  agent skill and references, installed by `skill_installer.py`.

Read `docs/architecture.md` before changing operations or transport contracts.
Add behavior to the appropriate domain module and export it through
`operations.py`. Keep SDK calls out of CLI and MCP wrappers. Preserve equivalent
arguments and behavior across both surfaces; cover shared changes in
`test/test_contracts.py`.

Use the MCP v2 `MCPServer` API from `mcp.server.mcpserver`, matching existing
code. Follow existing four-space indentation, type annotations, and narrow
module responsibilities. Do not hand-edit generated `_version.py` or replace
the dynamic version with a static version.

## Version and release maintenance

Version 1.0.0 is the existing release; current development targets 1.1.0.
Preserve the `v1.0.0` tag and the historical 1.0.0 changelog entry. Keep
ongoing changes under `Unreleased` until preparing the 1.1.0 release, then
rename that section to `1.1.0` with the actual release date.

Treat 1.1.0 as a backward-compatible minor release: preserve existing CLI
commands, MCP tool names, arguments, response contracts, and error codes.
Flag unavoidable breaking changes for a versioning decision before proceeding.
Dependency/API migrations must also be reflected in installation and client
configuration documentation.

Use `v1.1.0` for the next release tag and `1.1.0` in release verification
examples. Let setuptools-scm derive development versions from Git history;
do not force a stable 1.1.0 version during development. Follow
`docs/publishing.md` for release checks. Create or push release tags and
publish packages only when the user explicitly requests that release action.

## Development and validation

Use the project interpreter/virtual environment. The README documents editable
installation with `python -m pip install -e ".[dev]"`. `pyproject.toml` defines
the dev extra, setuptools build backend, setuptools-scm version provider,
pytest live marker, and 75% coverage floor. Ruff and mypy use default settings;
pass `src/aspose_pdf_cloud_mcp` explicitly to mypy. Check available tooling
before running quality checks. CI enforces unit coverage and distribution
checks; publishing runs those gates before PyPI upload. See `docs/publishing.md`.

Run focused tests for affected behavior, then the unit suite with live tests
explicitly excluded:

```powershell
python -m pytest -q -m "not live"
```

The development docs list these additional quality checks when tooling and
configuration are available:

```powershell
python -m ruff format --check src test
python -m ruff check src test
python -m mypy src/aspose_pdf_cloud_mcp
python -m pytest -q -m "not live" --cov=aspose_pdf_cloud_mcp --cov-report=term-missing
python -m pip_audit .
python -m build
python -m twine check dist/*
```

The documented coverage target is 75%; do not lower it to hide regressions.
Use mocked SDK calls, pytest `monkeypatch`, temporary paths, and Typer's
`CliRunner`, following existing tests. Unit tests must not require credentials.
Report unavailable checks and configuration gaps accurately.

## Credentials, cloud access, and output

Configuration reads `ASPOSE_CLIENT_ID`, `ASPOSE_CLIENT_SECRET`, and optional
`ASPOSE_STORAGE_NAME`, `ASPOSE_BASE_URL`, and `ASPOSE_SELF_HOST`. Environment
variables take precedence over the local `.env` file. Never commit or expose
real credentials in output, logs, fixtures, or configuration examples.

Live tests require credentials plus `ASPOSE_RUN_LIVE_TESTS=1` and make real
cloud calls, including temporary uploads and deletion. Run them only when
intentionally authorized; see `docs/live-tests.md` for setup and cleanup.

Preserve stable error codes, sanitized MCP messages, and redacted stderr
diagnostics. Preserve atomic local writes and rejection of existing output
files unless overwrite is explicit. Keep stdout compatible with JSON output
and the MCP transport. See `docs/security.md` for details.

Update user-facing docs and relevant bundled skill references when changing
commands, tool arguments, installation, or configuration behavior.
