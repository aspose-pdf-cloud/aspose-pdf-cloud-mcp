# Live Test Reference

Default tests do not call Aspose Cloud:

```powershell
python -m pytest -q
```

Live tests require:

- `ASPOSE_CLIENT_ID`
- `ASPOSE_CLIENT_SECRET`
- `ASPOSE_RUN_LIVE_TESTS=1`
- `ASPOSE_STORAGE_NAME`, if the account requires named storage

Run live tests:

```powershell
$env:ASPOSE_CLIENT_ID = "your-client-id"
$env:ASPOSE_CLIENT_SECRET = "your-client-secret"
$env:ASPOSE_STORAGE_NAME = "your-storage-name"
$env:ASPOSE_RUN_LIVE_TESTS = "1"
python -m pytest -q -m live
```

The live upload/download smoke test writes under the
`aspose-pdf-cloud-cli-live/` prefix and attempts cleanup. If interrupted,
check that prefix manually in Aspose storage.

Do not enable live tests in public CI unless safe credentials are explicitly configured.
