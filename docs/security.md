# Security Notes

## Credentials

This project uses Aspose Cloud credentials from environment variables or a
local `.env` file:

- `ASPOSE_CLIENT_ID`
- `ASPOSE_CLIENT_SECRET`
- `ASPOSE_STORAGE_NAME`
- `ASPOSE_BASE_URL`
- `ASPOSE_SELF_HOST`

Never commit real credentials. The `.env` file is ignored by Git and should
remain local to your machine.

## MCP Configuration

Prefer MCP configs that inherit environment variables, such as Codex
`env_vars`, instead of storing secret values directly in MCP config files.

If you need an explicit environment map for a local-only config, keep that
file outside version control.

## Logs and Prompts

Avoid printing credentials in:

- CLI output
- test logs
- GitHub Actions logs
- issue reports
- Codex prompts and chat transcripts

When sharing errors, redact secrets first:

```text
ASPOSE_CLIENT_SECRET=<redacted>
```

CLI and MCP failures use stable error codes such as `validation_error`,
`authentication_failed`, `not_found`, `conflict`, `api_error`, and
`internal_error`. MCP responses contain sanitized messages; raw unexpected
exception messages are written only as redacted stderr diagnostics and are
never returned over the protocol.

## Local Writes

Downloads, extracted text, and JSON exports use same-directory temporary files
and an atomic final commit. Existing files are rejected unless `--overwrite`
or `overwrite=true` is explicit. Credential `.env` updates are also atomic and
are written with owner-only permissions where the platform supports them.

## CI and Publishing

The PyPI publish workflow uses a project-scoped `PYPI_API_TOKEN` secret from
the selected GitHub environment (`pypi` for tag pushes, `testpypi` for manual
rehearsals). Keep those environment secrets scoped to this repository and
rotate them if exposure is suspected.
