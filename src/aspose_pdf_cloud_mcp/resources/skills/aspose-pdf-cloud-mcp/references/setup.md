# Setup Reference

## Install

Install the published package:

```powershell
python -m pip install aspose-pdf-cloud-mcp
```

Verify commands:

```powershell
aspose-pdf-cloud-cli --help
apdf --help
```

Install from a local checkout for development:

```powershell
python -m pip install -e ".[dev]"
```

## Environment

Set required credentials:

```powershell
$env:ASPOSE_CLIENT_ID = "your-client-id"
$env:ASPOSE_CLIENT_SECRET = "your-client-secret"
```

Set optional values when needed:

```powershell
$env:ASPOSE_STORAGE_NAME = "your-storage-name"
$env:ASPOSE_BASE_URL = "https://api.aspose.cloud/v3.0"
$env:ASPOSE_SELF_HOST = "false"
```

Local `.env` files are supported by the Aspose.PDF CLI, but they must remain untracked.

## CLI Commands

```powershell
aspose-pdf-cloud-cli storage list /
aspose-pdf-cloud-cli storage upload .\sample.pdf /sample.pdf
aspose-pdf-cloud-cli storage download /sample.pdf .\sample.pdf
aspose-pdf-cloud-cli pdf merge merged.pdf /a.pdf /b.pdf /c.pdf
aspose-pdf-cloud-cli pdf merge merged.pdf --from-folder /contracts
aspose-pdf-cloud-cli pdf split sample.pdf
aspose-pdf-cloud-cli pdf split sample.pdf --ranges 1-3,4,5-8
aspose-pdf-cloud-cli pdf pdfa-versions
aspose-pdf-cloud-cli pdf convert-pdfa sample.pdf /archive/sample-pdfa.pdf --pdfa-version PDF/A-1B
aspose-pdf-cloud-cli pdf convert-pdfa sample.pdf /archive/sample-pdfa.pdf --type PDFA3B
aspose-pdf-cloud-cli pdf extract-text sample.pdf --output sample.txt
aspose-pdf-cloud-cli pdf extract-tables sample.pdf --output tables.json
aspose-pdf-cloud-cli pdf extract-tables sample.pdf --pages 1,3,4-7,10 --output tables.json
aspose-pdf-cloud-cli mcp serve
```

Use `apdf` as the short alias when convenient.
