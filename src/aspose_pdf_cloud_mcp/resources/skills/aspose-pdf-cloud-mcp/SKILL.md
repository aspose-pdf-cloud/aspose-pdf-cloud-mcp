---
name: aspose-pdf-cloud-mcp
description: Use Aspose.PDF Cloud CLI and its Aspose PDF Cloud MCP server for PDF/storage automation. Trigger when the user wants to configure or use the Aspose.PDF MCP server, connect Codex or Claude Code to Aspose PDF Cloud, list/upload/download Aspose storage files, merge or split PDFs, convert PDFs to PDF/A, extract PDF text or tables, write sample agent prompts for Aspose.PDF, run live Aspose.PDF smoke tests, or troubleshoot Aspose.PDF Cloud CLI/MCP setup and credential handling.
---

# Aspose.PDF Cloud MCP

## Core Workflow

Use this skill for Aspose.PDF Cloud CLI / MCP work involving Aspose PDF Cloud.

1. Determine whether the user wants setup, MCP usage, CLI usage, testing, docs, or troubleshooting.
2. Prefer active MCP tools for storage/PDF operations when the Aspose.PDF MCP server is available.
3. Use the `aspose-pdf-cloud-cli` / `apdf` CLI as a fallback when MCP tools are unavailable or the user asks for local commands.
4. If the MCP server is available but does not expose the specific tool needed for the requested operation, fall back to the equivalent `apdf` CLI command and inform the user that the MCP tool was not available for that operation.
5. **Priority rule**: If the user explicitly requests CLI commands, provide CLI commands even when MCP tools are active. Otherwise, default to MCP tools when the server is available.


## MCP Operations

When Aspose.PDF MCP tools are active, use them for:

- `list_files(path, storage_name=None)`
- `upload_file(local_path, remote_path, storage_name=None)`
- `download_file(remote_path, local_path, storage_name=None, version_id=None, overwrite=False)`
- `merge_pdfs(inputs, output_name, folder=None, storage=None, from_folder=None)`
- `split_pdf(name, ranges=None, folder=None, storage=None)`
- `list_pdfa_versions()`
- `convert_pdf_to_pdfa(name, out_path, pdfa_version="PDF/A-1B", folder=None, storage=None)`
- `extract_text(name, folder=None, storage=None)`
- `extract_tables(name, pages=None, folder=None, storage=None)`
- `list_images(name, pages=None, folder=None, storage=None)`
- `extract_images(name, pages=None, dest_folder=None, image_format="png", folder=None, storage=None)`
- `extract_image(name, page, index, dest_folder=None, image_format="png", folder=None, storage=None)`

### Error Handling

If an MCP tool returns an error, report its structured `code` and sanitized `message`, identify the likely cause (e.g., invalid credentials, missing file, wrong storage name), and suggest a corrective action before retrying. Never reconstruct or expose the underlying raw exception.

### Confirmation & Validation

Before executing upload, merge-output, PDF/A conversion output, or download-overwrite operations, confirm the target path unless the user has provided a remote path that includes an explicit filename (e.g., `filename.pdf` or `folder/filename.pdf`) and has not used vague language like "somewhere" or "any folder".

Skip confirmation only when ALL the following are true: (1) the user provided an explicit remote path including a filename, (2) the path contains no vague placeholders like "somewhere" or "any folder", and (3) the path field is not empty. In all other cases, confirm before executing.

For `download_file`, always default to downloading the latest version of a file unless the user explicitly requests a specific version. Only ask for a version ID if the user's request implies a non-latest version (e.g., "the previous version", "version from last week").

Local downloads and CLI output files do not overwrite existing files by default. Set `overwrite=true` or pass `--overwrite` only when the user explicitly requests replacement or has confirmed it.

## Setup

For install/configuration tasks, read `references/setup.md`. If a referenced file cannot be read, tell the user which file is unavailable and what information is missing (e.g., "The full Codex/Claude Code config examples in references/mcp-config.md are unavailable; only the generic TOML snippet below can be provided"). Do not fabricate content that was meant to come from the missing file.

Default install command:

```powershell
python -m pip install aspose-pdf-cloud-mcp
```

Default MCP command:

```powershell
aspose-pdf-cloud-cli mcp serve
```

Required credentials:

- `ASPOSE_CLIENT_ID`
- `ASPOSE_CLIENT_SECRET`

Optional settings:

- `ASPOSE_STORAGE_NAME`
- `ASPOSE_BASE_URL`
- `ASPOSE_SELF_HOST`

## Agent MCP Config

For Codex and Claude Code config examples, read `references/mcp-config.md`.

Prefer inherited environment variables in agent config:

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

## Prompt Writing

For sample agent prompts, read `references/prompts.md`.

Good Aspose.PDF prompts specify:

- Storage path or local path.
- Operation: list, upload, download, merge, split, convert to PDF/A, extract text, extract tables, or extract images.
- Whether writes are allowed.
- Whether to summarize extracted content or save it.

## Security

For security details, read `references/security.md`.

Never print or commit real values for:

- `ASPOSE_CLIENT_ID`
- `ASPOSE_CLIENT_SECRET`

Use `<redacted>` or `your-client-id` / `your-client-secret` in examples.

If the user pastes what appears to be a real credential value (a non-placeholder string) into the conversation, 
do not echo it back, warn the user that credentials should not be shared in chat, and ask them to rotate 
the credential.
