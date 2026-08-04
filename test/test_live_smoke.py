from __future__ import annotations

import os
import uuid
from pathlib import Path

import pytest

from aspose_pdf_cloud_mcp import operations
from aspose_pdf_cloud_mcp.client import create_pdf_api
from aspose_pdf_cloud_mcp.config import ConfigError, load_config

pytestmark = pytest.mark.live


def _credentials_available() -> bool:
    try:
        load_config()
    except ConfigError:
        return False
    return True


def _live_enabled() -> bool:
    return os.getenv("ASPOSE_RUN_LIVE_TESTS", "").strip().lower() in {"1", "true", "yes"}


live_credentials = pytest.mark.skipif(
    not _credentials_available() or not _live_enabled(),
    reason=(
        "ASPOSE_CLIENT_ID, ASPOSE_CLIENT_SECRET, and ASPOSE_RUN_LIVE_TESTS=1 "
        "are required for live tests."
    ),
)


@live_credentials
def test_live_storage_list_root():
    result = operations.list_files("/")

    assert result["path"] == "/"
    assert "items" in result


@live_credentials
def test_live_upload_download_roundtrip(tmp_path: Path):
    config = load_config()
    api = create_pdf_api(config)
    local_source = tmp_path / "source.txt"
    local_download = tmp_path / "downloaded.txt"
    content = f"aspose-pdf-cloud-cli live smoke {uuid.uuid4()}\n"
    remote_path = f"aspose-pdf-cloud-cli-live/{uuid.uuid4()}.txt"
    local_source.write_text(content, encoding="utf-8")

    try:
        upload = operations.upload_file(local_source, remote_path, api=api, config=config)
        download = operations.download_file(remote_path, local_download, api=api, config=config)

        assert upload["remote_path"] == remote_path
        assert download["local_path"] == str(local_download)
        assert local_download.read_text(encoding="utf-8") == content
    finally:
        try:
            api.delete_file(remote_path, storage_name=config.storage_name)
        except Exception:
            pass
