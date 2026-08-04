# Prompt Reference

## Storage

```text
List the files in my default Aspose storage root and summarize the PDFs you find.
```

```text
Upload ./sample.pdf to /codex-demo/sample.pdf in Aspose storage.
```

```text
Download /codex-demo/sample.pdf from Aspose storage to ./downloads/sample.pdf.
```

## PDF Operations

```text
Merge /contracts/part-a.pdf, /contracts/part-b.pdf, and /contracts/appendix.pdf into merged-contract.pdf in Aspose storage.
```

```text
Merge all PDFs in /contracts/parts into merged-contract.pdf in Aspose storage.
```

```text
Split /reports/q1.pdf into one PDF per page.
```

```text
Split /reports/q1.pdf into page-range segments 1 through 3, page 4, and pages 5 through 8.
```

```text
Convert /reports/q1.pdf to PDF/A-1B and save it as /archive/q1-pdfa.pdf in Aspose storage.
```

```text
List every PDF/A conversion target supported by the installed Aspose SDK.
```

```text
Extract text from /reports/q1.pdf and save it locally as ./reports/q1.txt.
```

```text
Extract text from /reports/q1.pdf, summarize the important dates, and tell me what looks missing.
```

```text
Extract all tables from /reports/q1.pdf and save the result locally as ./reports/q1-tables.json.
```

```text
Extract tables from pages 1, 3, 4 through 7, and 10 of /reports/q1.pdf.
```

## Safe Workflows

```text
Before modifying storage, list the target folder and ask me to confirm the upload path.
```

```text
Use the Aspose.PDF MCP tools, but do not print credentials or raw environment variables.
```

```text
Run a small smoke check by listing storage only. Do not upload, download, or delete files.
```
