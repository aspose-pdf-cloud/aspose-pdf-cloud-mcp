# MCP Configuration Reference

## Codex

Prefer inherited environment variables so secrets remain outside config files:

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

## Claude Code

Claude Code skills can be installed globally under `~/.claude/skills/` or
per project under `.claude/skills/`. Configure the MCP server in the place
where your Claude Code setup manages MCP servers, using this command:

```powershell
aspose-pdf-cloud-cli mcp serve
```

If your Claude Code MCP config uses JSON, adapt this shape:

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

## Explicit Environment Map

Only use explicit values in local-only files. Use placeholders in committed examples:

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
