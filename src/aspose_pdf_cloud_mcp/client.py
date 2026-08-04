"""Aspose.PDF SDK client factory."""

from __future__ import annotations

import asposepdfcloud

from .config import AsposeConfig, load_config


def create_pdf_api(config: AsposeConfig | None = None) -> asposepdfcloud.PdfApi:
    """Create an authenticated Aspose PdfApi instance."""

    cfg = config or load_config()
    api_client = asposepdfcloud.ApiClient(
        cfg.client_secret,
        cfg.client_id,
        cfg.base_url,
        cfg.self_host,
    )
    return asposepdfcloud.PdfApi(api_client)
