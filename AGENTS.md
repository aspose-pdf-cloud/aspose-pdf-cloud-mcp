# Repository Guidelines

## Project Structure & Module Organization

This repository is a Python CLI and MCP server for Aspose.PDF.

- `src/aspose_pdf_cloud_mcp/`: application package.
- `config.py`: environment and `.env` configuration loading.
- `client.py`: Aspose SDK client factory.
- `storage_operations.py`, `document_operations.py`, `extraction_operations.py`, and `output_operations.py`: focused business-operation domains.
- `operations.py`: stable facade shared by CLI and MCP transports.
- `page_selectors.py`: shared page/range parsing.
- `result_types.py`: typed operation and protocol contracts.
- `mcp_adapter.py`: common MCP success/error adaptation.
- `cli.py`: Typer command-line interface.
- `mcp_server.py`: FastMCP tool server.
- `skill_installer.py`: installs the bundled `aspose-pdf-cloud-mcp` agent skill.
- `resources/skills/aspose-pdf-cloud-mcp/`: packaged Codex/Claude Code skill.
- `test/`: pytest unit and live smoke tests.
- `docs/`: install, MCP, Codex prompt, live test, and security notes.
- `examples/`: copy-pasteable local configuration examples.
- `README.md`: user-facing setup and command examples.

Keep new behavior in the appropriate domain operation module first, export it through `operations.py`, then expose it through CLI and MCP wrappers. Never duplicate Aspose SDK calls in transport code.

## Build, Test, and Development Commands

Install locally in editable mode:

```powershell
python -m pip install -e ".[dev]"
```

Run the full default test suite:

```powershell
python -m pytest -q
```

Run only live Aspose Cloud smoke tests:

```powershell
$env:ASPOSE_RUN_LIVE_TESTS = "1"
python -m pytest -q -m live
```

Check CLI help:

```powershell
python -m aspose_pdf_cloud_mcp.cli --help
```

Install the bundled Aspose.PDF skill locally:

```powershell
python -m aspose_pdf_cloud_mcp.cli skill install codex --force
python -m aspose_pdf_cloud_mcp.cli skill install claude-code --project --force
```

Build and validate PyPI distributions:

```powershell
python -m build
python -m twine check dist/*
```

Review docs for packaging/rendering issues:

```powershell
python -m twine check dist/*
```

## Coding Style & Naming Conventions

Use Python 3.11+ syntax, four-space indentation, type hints for public functions, and concise docstrings for modules and commands. Prefer small, testable functions. Use `snake_case` for modules, functions, variables, CLI command callbacks, and MCP tools. Keep SDK-specific details inside `client.py` or `operations.py`; do not duplicate Aspose calls in CLI/MCP code.

## Testing Guidelines

Tests use `pytest` and live tests are marked with `@pytest.mark.live`. Name tests `test_<behavior>.py` and test functions `test_<expected_behavior>`. Unit tests should mock Aspose SDK calls and must not require credentials. Live tests must be opt-in and gated by `ASPOSE_RUN_LIVE_TESTS=1` plus valid credentials.

## Security & Configuration Tips

Never commit real credentials. Local `.env` files are ignored and may contain `ASPOSE_CLIENT_ID`, `ASPOSE_CLIENT_SECRET`, optional `ASPOSE_STORAGE_NAME`, `ASPOSE_BASE_URL`, and `ASPOSE_SELF_HOST`. Environment variables take precedence over `.env` values. Avoid printing secrets in tests, logs, or error messages.

## Release & Publishing Guidelines

Publishing uses GitHub Actions and PyPI trusted publishing. Versions are generated from Git metadata by `setuptools-scm`; do not hard-code a version in `pyproject.toml` or the package. Publish by pushing a `vX.Y.Z` tag after tests pass. The PyPI trusted publisher should target repository `aspose-pdf-cloud/aspose-pdf-cloud-mcp`, workflow `publish.yml`, environment `pypi`, and project `aspose-pdf-cloud-mcp`.

## Commit & Pull Request Guidelines

The current history uses short imperative commit messages, for example `Initial Aspose.PDF CLI project skeleton`. Continue with concise messages like `Add live storage smoke tests` or `Expose split PDF command`. Pull requests should include a brief summary, testing performed, any credential or live-test notes, and linked issues when applicable.
