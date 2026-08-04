# Security Reference

## Credentials

Never commit or print real values for:

- `ASPOSE_CLIENT_ID`
- `ASPOSE_CLIENT_SECRET`

Treat these as sensitive too:

- `ASPOSE_STORAGE_NAME`
- `ASPOSE_BASE_URL`
- `ASPOSE_SELF_HOST`

## Config Files

Prefer MCP configs that inherit environment variables. If explicit secret
values are necessary for a local-only config, keep that file outside version
control.

Use placeholders in examples:

```text
ASPOSE_CLIENT_ID=your-client-id
ASPOSE_CLIENT_SECRET=your-client-secret
```

## Logs and Prompts

Before sharing logs, issue reports, or agent transcripts, redact secrets:

```text
ASPOSE_CLIENT_SECRET=<redacted>
```

Do not echo raw environment variables unless the user explicitly asks and the
values are already placeholders.

MCP failures return a stable error `code` and sanitized `message`. Never expose
raw unexpected exceptions to the user. Diagnostics must remain on stderr so
the MCP stdio protocol on stdout is not corrupted.

Local downloads and output files are atomic and refuse replacement unless
`overwrite=true` or `--overwrite` is explicit.
