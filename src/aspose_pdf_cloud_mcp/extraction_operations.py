"""PDF text, table, image, and attachment extraction operations."""

from pathlib import Path
from typing import Any

from ._operation_core import (
    _api_and_config,
    _call_api,
    _remote_folder,
    _remote_path,
    _storage,
    extract_image,
    extract_images,
    extract_tables,
    extract_text,
    list_images,
    to_plain_data,
)
from .config import AsposeConfig
from .errors import AsposePdfToolError
from .io_utils import atomic_copy_stream, atomic_write_bytes

__all__ = [
    "extract_attachment",
    "extract_attachments",
    "extract_image",
    "extract_images",
    "extract_tables",
    "extract_text",
    "list_attachments",
    "list_images",
]


def list_attachments(
    name: str,
    folder: str | None = None,
    storage: str | None = None,
    *,
    api: Any | None = None,
    config: AsposeConfig | None = None,
) -> dict[str, Any]:
    """List document embedded files with their one-based extraction indexes."""
    name = _remote_path(name, "PDF name", require_pdf=True)
    folder = None if folder is None else _remote_folder(folder, "Document folder")
    pdf_api, cfg = _api_and_config(api, config)
    storage = _storage(storage, cfg)
    raw = to_plain_data(
        _call_api(
            pdf_api.get_document_attachments, name, folder=folder, storage=storage
        )
    )
    container = (
        raw.get("attachments", raw.get("Attachments", {}))
        if isinstance(raw, dict)
        else {}
    )
    items = (
        container.get("list", container.get("List", []))
        if isinstance(container, dict)
        else []
    )
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        raise AsposePdfToolError(
            "Invalid attachment listing response.", code="api_error"
        )
    attachments = []
    for index, item in enumerate(items, 1):
        metadata = to_plain_data(
            _call_api(
                pdf_api.get_document_attachment_by_index,
                name,
                index,
                folder=folder,
                storage=storage,
            )
        )
        detail = (
            metadata.get("attachment", metadata.get("Attachment"))
            if isinstance(metadata, dict)
            else None
        )
        if not isinstance(detail, dict):
            raise AsposePdfToolError(
                "Invalid attachment metadata response.", code="api_error"
            )
        attachments.append({**detail, "index": index})
    return {
        "name": name,
        "folder": folder,
        "storage": storage,
        "attachments": attachments,
    }


def extract_attachment(
    name: str,
    index: int,
    local_path: str | Path,
    folder: str | None = None,
    storage: str | None = None,
    *,
    overwrite: bool = False,
    api: Any | None = None,
    config: AsposeConfig | None = None,
) -> dict[str, Any]:
    """Download one document attachment to an explicit local file."""
    name = _remote_path(name, "PDF name", require_pdf=True)
    if isinstance(index, bool) or index < 1:
        raise AsposePdfToolError(
            "Attachment index must be positive.", code="validation_error"
        )
    folder = None if folder is None else _remote_folder(folder, "Document folder")
    destination = Path(local_path)
    if destination.exists() and not overwrite:
        raise AsposePdfToolError(
            "Local output already exists. Use overwrite to replace it.", code="conflict"
        )
    pdf_api, cfg = _api_and_config(api, config)
    storage = _storage(storage, cfg)
    downloaded = _call_api(
        pdf_api.get_download_document_attachment_by_index,
        name,
        index,
        folder=folder,
        storage=storage,
    )
    if isinstance(downloaded, bytes):
        atomic_write_bytes(destination, downloaded, overwrite=overwrite)
    elif hasattr(downloaded, "read"):
        atomic_copy_stream(destination, downloaded, overwrite=overwrite)
    else:
        source = Path(str(downloaded))
        if not source.is_file():
            raise AsposePdfToolError(
                "Download did not return a readable file.", code="api_error"
            )
        with source.open("rb") as stream:
            atomic_copy_stream(destination, stream, overwrite=overwrite)
    return {
        "name": name,
        "index": index,
        "local_path": str(destination),
        "folder": folder,
        "storage": storage,
    }


def extract_attachments(
    name: str,
    output_dir: str | Path,
    folder: str | None = None,
    storage: str | None = None,
    *,
    overwrite: bool = False,
    api: Any | None = None,
    config: AsposeConfig | None = None,
) -> dict[str, Any]:
    """Download all attachments; prefix safe filenames with their unique index."""
    pdf_api, cfg = _api_and_config(api, config)
    listed = list_attachments(name, folder, storage, api=pdf_api, config=cfg)
    targets = []
    for item in listed["attachments"]:
        filename = item.get("name", item.get("Name")) or "attachment"
        if (
            not isinstance(filename, str)
            or filename in {".", ".."}
            or any(c in filename for c in '/\\\x00<>:"|?*')
            or filename.endswith((".", " "))
        ):
            raise AsposePdfToolError(
                "Attachment has an unsafe filename.", code="validation_error"
            )
        target = Path(output_dir) / f"{item['index']}-{filename}"
        if target.exists() and not overwrite:
            raise AsposePdfToolError(
                "Local output already exists. Use overwrite to replace it.",
                code="conflict",
            )
        targets.append((item["index"], target))
    files = [
        extract_attachment(
            listed["name"],
            index,
            target,
            listed["folder"],
            listed["storage"],
            overwrite=overwrite,
            api=pdf_api,
            config=cfg,
        )
        for index, target in targets
    ]
    return {**listed, "output_dir": str(output_dir), "files": files}
