# Aspose.PDF Cloud CLI + MCP Tools

Aspose.PDF Cloud CLI exposes Aspose PDF Cloud storage and PDF operations through
both a command-line interface and an MCP server.

## How to Get Your Aspose.PDF Cloud Credentials

1. Go to the [Dashboard](https://dashboard.aspose.cloud/).
2. After logging in, navigate to the **Applications** section in the main menu.
3. Select the first (default) application or create a new one.
4. Copy the **Client ID** and **Client Secret** for later use.

## Installation

Install from PyPI:

```powershell
python -m pip install aspose-pdf-cloud-mcp
```

Check that the CLI is available:

```powershell
aspose-pdf-cloud-cli --help
apdf --help
```

For local development from a checkout:

```powershell
python -m pip install -e ".[dev]"
```

## Configuration

Set credentials before running CLI commands or the MCP server. The easiest
local setup path is:

```powershell
apdf auth login
apdf auth status
apdf auth test
```

You can also set credentials directly in your shell:

```powershell
$env:ASPOSE_CLIENT_ID = "your-client-id"
$env:ASPOSE_CLIENT_SECRET = "your-client-secret"
```

Optional environment variables:

- `ASPOSE_STORAGE_NAME`: default Aspose storage name.
- `ASPOSE_BASE_URL`: alternate Aspose PDF Cloud base URL.
- `ASPOSE_SELF_HOST`: set to `1`, `true`, `yes`, or `on` for self-hosted use.

You can also create a local `.env` file. See
[`.env.example`](.env.example) for a template. Environment variables take
precedence over `.env` values.

## CLI Usage

The canonical executable is `aspose-pdf-cloud-cli`. A shorter `apdf` alias is
also installed for convenience.

```powershell
aspose-pdf-cloud-cli storage list /
aspose-pdf-cloud-cli auth status
aspose-pdf-cloud-cli auth test
aspose-pdf-cloud-cli storage upload .\sample.pdf /sample.pdf
aspose-pdf-cloud-cli storage download /sample.pdf .\sample.pdf
aspose-pdf-cloud-cli storage download /sample.pdf .\sample.pdf --overwrite
aspose-pdf-cloud-cli pdf merge merged.pdf /a.pdf /b.pdf /c.pdf
aspose-pdf-cloud-cli pdf merge merged.pdf --from-folder /contracts
aspose-pdf-cloud-cli pdf split sample.pdf
aspose-pdf-cloud-cli pdf split sample.pdf --ranges 1-3,4,5-8
aspose-pdf-cloud-cli pdf pdfa-versions
aspose-pdf-cloud-cli pdf convert-pdfa sample.pdf /archive/sample-pdfa.pdf --pdfa-version PDF/A-1B
aspose-pdf-cloud-cli pdf convert-pdfa sample.pdf /archive/sample-pdfa.pdf --type PDFA3B
aspose-pdf-cloud-cli pdf extract-text sample.pdf --output sample.txt
aspose-pdf-cloud-cli pdf extract-text sample.pdf --output sample.txt --overwrite
aspose-pdf-cloud-cli pdf extract-tables sample.pdf --output tables.json
aspose-pdf-cloud-cli pdf extract-tables sample.pdf --pages 1,3,4-7,10 --output tables.json
aspose-pdf-cloud-cli pdf list-images sample.pdf
aspose-pdf-cloud-cli pdf extract-images sample.pdf /extracted-images
aspose-pdf-cloud-cli pdf extract-images sample.pdf /extracted-images --pages 1,3,7-10
aspose-pdf-cloud-cli pdf extract-image sample.pdf 1 1 /extracted-images
aspose-pdf-cloud-cli mcp serve
```

## MCP Usage

After installing the package, configure your MCP client to launch:

```powershell
aspose-pdf-cloud-cli mcp serve
```

Codex MCP configuration examples are available in
[docs/mcp-config.md](docs/mcp-config.md), with a copy-pasteable helper at
[examples/codex-mcp-config.toml](examples/codex-mcp-config.toml).

## Codex Prompts

Sample prompts for using this MCP server with Codex are in
[docs/codex-prompts.md](docs/codex-prompts.md).

## Install as an Agent Skill

The package includes an `aspose-pdf-cloud-mcp` skill for Codex and Claude Code.
Install the package first, then install the bundled skill:

```powershell
python -m pip install aspose-pdf-cloud-mcp
aspose-pdf-cloud-cli skill install codex
aspose-pdf-cloud-cli skill install claude-code
```

For Claude Code project-local installation:

```powershell
aspose-pdf-cloud-cli skill install claude-code --project
```

Use `--force` to replace an existing installed copy. More details are in
[docs/agent-skill.md](docs/agent-skill.md).
