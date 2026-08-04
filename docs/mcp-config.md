# MCP Configuration

Install the package first:

```powershell
python -m pip install aspose-pdf-cloud-mcp
```

The MCP server runs over stdio:

```powershell
aspose-pdf-cloud-cli mcp serve
```

## Codex

Add an MCP server entry to your Codex `config.toml`.

```toml
[mcp_servers.aspose_pdf_cloud]
command = "aspose-pdf-cloud-cli"
args = ["mcp", "serve"]
env_vars = [
  "ASPOSE_CLIENT_ID",
  "ASPOSE_CLIENT_SECRET",
  "ASPOSE_STORAGE_NAME",
  "ASPOSE_BASE_URL",
  "ASPOSE_SELF_HOST"
]
startup_timeout_sec = 20
tool_timeout_sec = 120
```

Use `env_vars` so Codex inherits credentials from your shell or user
environment instead of storing secret values directly in the config file.

## Codex With Explicit Environment Values

If your MCP client supports explicit environment maps, use placeholders only
in committed examples:

```toml
[mcp_servers.aspose_pdf_cloud]
command = "aspose-pdf-cloud-cli"
args = ["mcp", "serve"]
startup_timeout_sec = 20
tool_timeout_sec = 120

[mcp_servers.aspose_pdf_cloud.env]
ASPOSE_CLIENT_ID = "your-client-id"
ASPOSE_CLIENT_SECRET = "your-client-secret"
ASPOSE_STORAGE_NAME = "your-storage-name"
```

Prefer the inherited `env_vars` form for real credentials.

## Generic MCP JSON Shape

Some MCP clients use JSON instead of TOML. Adapt the exact field names to
your client:

```json
{
  "mcpServers": {
    "aspose_pdf_cloud": {
      "command": "aspose-pdf-cloud-cli",
      "args": ["mcp", "serve"],
      "env": {
        "ASPOSE_CLIENT_ID": "your-client-id",
        "ASPOSE_CLIENT_SECRET": "your-client-secret",
        "ASPOSE_STORAGE_NAME": "your-storage-name"
      }
    }
  }
}
```

## Available Tools

The MCP server exposes wrappers around the same shared operations used by
the CLI:

- `list_files`
- `upload_file`
- `download_file`
- `merge_pdfs` with `inputs` or `from_folder`
- `split_pdf` with optional `ranges`, for example `1-3,4,5-8`
- `list_pdfa_versions`
- `convert_pdf_to_pdfa` with `pdfa_version`, for example `PDF/A-1B` or `PDFA3B`
- `extract_text`
- `extract_tables` with optional `pages`, for example `1,3,4-7,10`
- `list_images` with optional `pages`, for example `1,3,4-7,10`
- `extract_images` with optional `pages`
- `extract_image` by one-based page and image index

## Agent Skill

Install the bundled skill so Codex or Claude Code also has Aspose.PDF-specific
workflow instructions:

```powershell
aspose-pdf-cloud-cli skill install codex
aspose-pdf-cloud-cli skill install claude-code
```

See [agent-skill.md](agent-skill.md) for project-local and custom-directory
installation.
