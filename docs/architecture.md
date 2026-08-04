# Architecture and Contribution Guide

## Layers

The package has one shared business-operation API and two transport adapters:

1. `storage_operations.py`, `document_operations.py`,
   `extraction_operations.py`, and `output_operations.py` group operations by
   domain.
2. `operations.py` is the stable compatibility facade imported by both
   transports.
3. `cli.py` handles Typer argument parsing and human or JSON presentation.
4. `mcp_server.py` declares MCP SDK v2 tools; `mcp_adapter.py` owns the common
   success and error envelope.

Supporting modules have narrow responsibilities:

- `page_selectors.py`: all page and range parsing.
- `result_types.py`: shared `TypedDict` contracts.
- `errors.py`: stable error codes and redaction.
- `io_utils.py`: atomic local writes.
- `_operation_core.py`: private implementation retained behind the focused
  domain modules. New behavior should be added to the appropriate domain
  module and exposed through `operations.py`.

CLI and MCP wrappers must not call the Aspose SDK directly. Add or change the
domain operation first, then expose it through both transports. Add a contract
test whenever both surfaces accept the same logical arguments.

## Quality Gates

Before opening a pull request, run:

```powershell
python -m ruff format --check src test
python -m ruff check src test
python -m mypy
python -m pytest -q --cov=aspose_pdf_cloud_mcp --cov-report=term-missing
python -m pip_audit .
python -m build
python -m twine check dist/*
```

Unit tests must not require credentials. Live tests remain opt-in and use the
protected `live-tests` GitHub environment.

## Releases

Versions come from Git through `setuptools-scm`. Release commits must pass all
quality gates before a `vX.Y.Z` tag is pushed. The tag triggers trusted PyPI
publishing; never add a static version or PyPI token.
