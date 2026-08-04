# Live Test Instructions

The default test suite does not call Aspose Cloud.

```powershell
python -m pytest -q
```

Live tests are marked with `@pytest.mark.live` and are opt-in. They require:

- `ASPOSE_CLIENT_ID`
- `ASPOSE_CLIENT_SECRET`
- `ASPOSE_RUN_LIVE_TESTS=1`

In GitHub Actions, run the **Live Aspose.PDF Cloud tests** workflow manually.
Store `ASPOSE_CLIENT_ID` and `ASPOSE_CLIENT_SECRET` as secrets in the protected
`live-tests` environment. Optional Aspose settings may be stored there as
secrets with their matching environment-variable names.
- `ASPOSE_STORAGE_NAME`, if your account requires a named storage

Run live smoke tests:

```powershell
$env:ASPOSE_CLIENT_ID = "your-client-id"
$env:ASPOSE_CLIENT_SECRET = "your-client-secret"
$env:ASPOSE_STORAGE_NAME = "your-storage-name"
$env:ASPOSE_RUN_LIVE_TESTS = "1"
python -m pytest -q -m live
```

The live upload/download smoke test creates a temporary object under an
`aspose-pdf-cloud-cli-live/` prefix and attempts to delete it after the
test. If a run is interrupted, check that folder in your Aspose storage.

To run all tests including live tests:

```powershell
$env:ASPOSE_RUN_LIVE_TESTS = "1"
python -m pytest -q
```

Do not enable live tests in public pull requests unless the CI environment
is explicitly configured with safe credentials.
