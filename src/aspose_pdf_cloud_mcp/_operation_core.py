"""Shared Stage 1 Aspose.PDF operations."""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from pathlib import Path, PurePosixPath
from typing import Any

import asposepdfcloud

from .client import create_pdf_api
from .config import AsposeConfig, load_config
from .errors import AsposePdfToolError, sanitize_message
from .io_utils import atomic_copy_stream, atomic_write_bytes, atomic_write_text
from .page_selectors import parse_page_list, parse_page_ranges
from .result_types import DownloadResult, OutputResult, StorageListResult, TextExtractionResult


def _api_error(exc: Exception) -> AsposePdfToolError:
    status = getattr(exc, "status", None)
    reason = sanitize_message(getattr(exc, "reason", None) or "Request failed.")
    code = "api_error"
    if status in {401, 403}:
        code = "authentication_failed"
    elif status == 404:
        code = "not_found"
    elif status == 409:
        code = "conflict"
    message = f"Aspose API request failed: {reason}"
    details = {"status": status} if isinstance(status, int) else None
    return AsposePdfToolError(message, code=code, details=details)


def _call_api(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    try:
        return func(*args, **{k: v for k, v in kwargs.items() if v is not None})
    except Exception as exc:  # noqa: BLE001 - SDK raises several exception shapes.
        api_exception = getattr(getattr(asposepdfcloud, "rest", None), "ApiException", None)
        if api_exception and isinstance(exc, api_exception):
            raise _api_error(exc) from exc
        raise AsposePdfToolError("Aspose API request failed.", code="api_error") from exc


def _require_text(value: str, field: str) -> str:
    clean = value.strip()
    if not clean:
        raise AsposePdfToolError(f"{field} must not be empty.", code="validation_error")
    if "\x00" in clean:
        raise AsposePdfToolError(f"{field} contains an invalid character.", code="validation_error")
    return clean


def _optional_text(value: str | None, field: str) -> str | None:
    return None if value is None else _require_text(value, field)


def _remote_path(
    value: str,
    field: str,
    *,
    allow_root: bool = False,
    allow_folder: bool = False,
    require_pdf: bool = False,
) -> str:
    clean = _require_text(value, field)
    if "\\" in clean:
        raise AsposePdfToolError(f"{field} must use forward slashes.", code="validation_error")
    if clean == "/" and allow_root:
        return clean
    if any(part in {".", ".."} for part in clean.split("/")):
        raise AsposePdfToolError(
            f"{field} must not contain '.' or '..' segments.", code="validation_error"
        )
    if clean.endswith("/") and not allow_folder:
        raise AsposePdfToolError(f"{field} must identify a file.", code="validation_error")
    if require_pdf and PurePosixPath(clean).suffix.lower() != ".pdf":
        raise AsposePdfToolError(f"{field} must identify a PDF file.", code="validation_error")
    return clean


def _remote_folder(value: str, field: str) -> str:
    clean = _require_text(value, field)
    if "\\" in clean:
        raise AsposePdfToolError(f"{field} must use forward slashes.", code="validation_error")
    if any(part in {".", ".."} for part in clean.split("/")):
        raise AsposePdfToolError(
            f"{field} must not contain '.' or '..' segments.", code="validation_error"
        )
    return clean.rstrip("/") or "/"


def _normalized_image_format(image_format: str) -> str:
    normalized = _require_text(image_format, "Image format").lower()
    if normalized not in {"gif", "jpeg", "jpg", "png", "tiff"}:
        raise AsposePdfToolError(
            "Image format must be one of: gif, jpeg, jpg, png, tiff.",
            code="validation_error",
        )
    return "jpeg" if normalized == "jpg" else normalized


def _api_and_config(
    api: Any | None, config: AsposeConfig | None
) -> tuple[Any, AsposeConfig | None]:
    if api is not None:
        return api, config
    cfg = config or load_config()
    return create_pdf_api(cfg), cfg


def _storage(explicit: str | None, config: AsposeConfig | None) -> str | None:
    value = explicit if explicit is not None else (config.storage_name if config else None)
    return _optional_text(value, "Storage name")


def to_plain_data(value: Any) -> Any:
    """Convert SDK model objects into JSON-friendly values."""

    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, list | tuple | set):
        return [to_plain_data(item) for item in value]
    if isinstance(value, dict):
        return {str(key): to_plain_data(item) for key, item in value.items()}
    if hasattr(value, "to_dict"):
        return to_plain_data(value.to_dict())
    if hasattr(value, "__dict__"):
        return {
            key.lstrip("_"): to_plain_data(item)
            for key, item in vars(value).items()
            if not key.startswith("__")
        }
    return str(value)


def list_files(
    path: str,
    storage_name: str | None = None,
    *,
    api: Any | None = None,
    config: AsposeConfig | None = None,
) -> StorageListResult:
    path = _remote_path(path, "Storage path", allow_root=True, allow_folder=True)
    pdf_api, cfg = _api_and_config(api, config)
    effective_storage = _storage(storage_name, cfg)
    response = _call_api(pdf_api.get_files_list, path, storage_name=effective_storage)
    return {"path": path, "storage_name": effective_storage, "items": to_plain_data(response)}


def _storage_list_items(items: Any) -> list[dict[str, Any]]:
    if isinstance(items, dict):
        values = items.get("value") or items.get("Value") or items.get("files") or items
    else:
        values = items
    if isinstance(values, dict):
        values = values.get("value") or values.get("Value") or []
    if not isinstance(values, list):
        return []
    return [item for item in values if isinstance(item, dict)]


def _join_remote_path(folder: str, name: str) -> str:
    return f"{folder.rstrip('/')}/{name.lstrip('/')}"


def _input_path_from_storage_item(item: dict[str, Any], folder: str) -> str | None:
    raw_path = item.get("path") or item.get("Path")
    if isinstance(raw_path, str) and raw_path:
        return raw_path

    name = item.get("name") or item.get("Name")
    if isinstance(name, str) and name:
        return _join_remote_path(folder, name)
    return None


def _folder_pdf_inputs(items: Any, folder: str) -> list[str]:
    inputs: list[str] = []
    for item in _storage_list_items(items):
        if item.get("is_folder") or item.get("IsFolder"):
            continue
        path = _input_path_from_storage_item(item, folder)
        if path and path.lower().endswith(".pdf"):
            inputs.append(path)
    return sorted(inputs, key=str.casefold)


def _validate_merge_inputs(inputs: Sequence[str]) -> list[str]:
    clean_inputs = [_remote_path(path, "Merge input", require_pdf=True) for path in inputs]
    if len(clean_inputs) < 2:
        raise AsposePdfToolError(
            "Merge requires at least two input PDF files.", code="validation_error"
        )
    return clean_inputs


def supported_pdfa_versions() -> list[str]:
    """Return PDF/A conversion targets exposed by the installed Aspose SDK."""

    versions = [
        value
        for attr in dir(asposepdfcloud.PdfAType)
        if attr.startswith("PDFA")
        for value in [getattr(asposepdfcloud.PdfAType, attr)]
        if isinstance(value, str) and value.startswith("PDFA")
    ]
    return sorted(set(versions))


def format_pdfa_version(version: str) -> str:
    """Format an SDK PDF/A enum value for humans."""

    if version.startswith("PDFA") and len(version) > 4:
        return f"PDF/A-{version[4:]}"
    return version


def list_pdfa_versions() -> dict[str, Any]:
    """List PDF/A conversion targets supported by the installed SDK."""

    versions = supported_pdfa_versions()
    return {
        "versions": [
            {"value": version, "label": format_pdfa_version(version)} for version in versions
        ],
        "default": "PDFA1B" if "PDFA1B" in versions else (versions[0] if versions else None),
    }


def normalize_pdfa_version(version: str) -> str:
    """Normalize user-friendly PDF/A versions to Aspose SDK enum values."""

    compact = (
        version.upper()
        .replace("PDF/A", "PDFA")
        .replace("-", "")
        .replace("_", "")
        .replace(" ", "")
        .replace("/", "")
    )
    if compact and compact[0].isdigit():
        compact = f"PDFA{compact}"

    allowed = set(supported_pdfa_versions())
    if compact not in allowed:
        labels = ", ".join(format_pdfa_version(item) for item in sorted(allowed))
        raise AsposePdfToolError(
            f"PDF/A version must be one of: {labels}.", code="validation_error"
        )
    return compact


def test_auth(
    path: str = "/",
    storage_name: str | None = None,
    *,
    api: Any | None = None,
    config: AsposeConfig | None = None,
) -> dict[str, Any]:
    """Validate Aspose.PDF credentials with a harmless storage listing."""

    result = list_files(path, storage_name, api=api, config=config)
    items = result.get("items", {})
    values = items.get("value") or items.get("Value") or items.get("files") or items
    if isinstance(values, dict):
        values = values.get("value") or values.get("Value") or []
    item_count = len(values) if isinstance(values, list) else None
    return {
        "ok": True,
        "path": result["path"],
        "storage_name": result["storage_name"],
        "item_count": item_count,
    }


def upload_file(
    local_path: str | Path,
    remote_path: str,
    storage_name: str | None = None,
    *,
    api: Any | None = None,
    config: AsposeConfig | None = None,
) -> dict[str, Any]:
    source = Path(local_path)
    if not source.is_file():
        raise AsposePdfToolError(f"Local file not found: {source}", code="not_found")
    remote_path = _remote_path(remote_path, "Remote path")

    pdf_api, cfg = _api_and_config(api, config)
    effective_storage = _storage(storage_name, cfg)
    response = _call_api(
        pdf_api.upload_file,
        remote_path,
        str(source),
        storage_name=effective_storage,
    )
    return {
        "local_path": str(source),
        "remote_path": remote_path,
        "storage_name": effective_storage,
        "result": to_plain_data(response),
    }


def download_file(
    remote_path: str,
    local_path: str | Path,
    storage_name: str | None = None,
    version_id: str | None = None,
    *,
    overwrite: bool = False,
    api: Any | None = None,
    config: AsposeConfig | None = None,
) -> DownloadResult:
    remote_path = _remote_path(remote_path, "Remote path")
    destination = Path(local_path)
    if destination.exists() and not overwrite:
        raise AsposePdfToolError(
            f"Local output already exists: {destination}. Use overwrite to replace it.",
            code="conflict",
        )
    version_id = _optional_text(version_id, "Version ID")

    pdf_api, cfg = _api_and_config(api, config)
    effective_storage = _storage(storage_name, cfg)
    downloaded = _call_api(
        pdf_api.download_file,
        remote_path,
        storage_name=effective_storage,
        version_id=version_id,
    )

    if isinstance(downloaded, bytes):
        atomic_write_bytes(destination, downloaded, overwrite=overwrite)
    elif hasattr(downloaded, "read"):
        atomic_copy_stream(destination, downloaded, overwrite=overwrite)
    else:
        downloaded_path = Path(str(downloaded))
        if not downloaded_path.is_file():
            raise AsposePdfToolError("Download did not return a readable file.", code="api_error")
        with downloaded_path.open("rb") as source:
            atomic_copy_stream(destination, source, overwrite=overwrite)

    return {
        "remote_path": remote_path,
        "local_path": str(destination),
        "storage_name": effective_storage,
        "version_id": version_id,
    }


def merge_pdfs(
    inputs: Sequence[str] | None,
    output_name: str,
    folder: str | None = None,
    storage: str | None = None,
    from_folder: str | None = None,
    *,
    api: Any | None = None,
    config: AsposeConfig | None = None,
) -> dict[str, Any]:
    output_name = _remote_path(output_name, "Merge output", require_pdf=True)
    folder = None if folder is None else _remote_folder(folder, "Output folder")
    from_folder = None if from_folder is None else _remote_folder(from_folder, "Source folder")
    pdf_api, cfg = _api_and_config(api, config)
    effective_storage = _storage(storage, cfg)
    if from_folder and inputs:
        raise AsposePdfToolError(
            "Use either explicit input files or --from-folder, not both.",
            code="validation_error",
        )
    if from_folder:
        listed = _call_api(pdf_api.get_files_list, from_folder, storage_name=effective_storage)
        input_paths = _folder_pdf_inputs(to_plain_data(listed), from_folder)
    else:
        input_paths = list(inputs or [])

    input_paths = _validate_merge_inputs(input_paths)
    merge_documents = asposepdfcloud.MergeDocuments(list=input_paths)
    response = _call_api(
        pdf_api.put_merge_documents,
        output_name,
        merge_documents,
        folder=folder,
        storage=effective_storage,
    )
    return {
        "inputs": input_paths,
        "output_name": output_name,
        "folder": folder,
        "storage": effective_storage,
        "from_folder": from_folder,
        "result": to_plain_data(response),
    }


def _normalize_split_documents(data: Any) -> list[dict[str, Any]]:
    plain = to_plain_data(data)
    if not isinstance(plain, dict):
        return []

    result = plain.get("result") or plain.get("Result") or plain
    documents = None
    if isinstance(result, dict):
        documents = result.get("documents") or result.get("Documents")
    if isinstance(documents, dict):
        documents = documents.get("list") or documents.get("List") or documents.get("value")
    if not isinstance(documents, list):
        return []
    return [document for document in documents if isinstance(document, dict)]


def split_pdf(
    name: str,
    ranges: str | None = None,
    folder: str | None = None,
    storage: str | None = None,
    *,
    api: Any | None = None,
    config: AsposeConfig | None = None,
) -> dict[str, Any]:
    """Split a PDF into single pages or explicit page-range segments."""

    name = _remote_path(name, "PDF name", require_pdf=True)
    folder = None if folder is None else _remote_folder(folder, "Document folder")
    pdf_api, cfg = _api_and_config(api, config)
    effective_storage = _storage(storage, cfg)
    page_ranges = parse_page_ranges(ranges)

    if page_ranges is None:
        response = _call_api(
            pdf_api.post_split_document,
            name,
            format="pdf",
            folder=folder,
            storage=effective_storage,
        )
        mode = "pages"
    else:
        options = asposepdfcloud.SplitRangePdfOptions(
            page_ranges=[
                asposepdfcloud.PageRange(_from=start, to=end) for start, end in page_ranges
            ]
        )
        response = _call_api(
            pdf_api.post_split_range_pdf_document,
            name,
            options,
            folder=folder,
            storage=effective_storage,
        )
        mode = "ranges"

    raw = to_plain_data(response)
    return {
        "name": name,
        "folder": folder,
        "storage": effective_storage,
        "mode": mode,
        "ranges": page_ranges,
        "documents": _normalize_split_documents(raw),
        "raw": raw,
    }


def convert_pdf_to_pdfa(
    name: str,
    out_path: str,
    pdfa_version: str,
    folder: str | None = None,
    storage: str | None = None,
    *,
    api: Any | None = None,
    config: AsposeConfig | None = None,
) -> dict[str, Any]:
    """Convert a PDF in Aspose storage to PDF/A and save it back to storage."""

    name = _remote_path(name, "PDF name", require_pdf=True)
    out_path = _remote_path(out_path, "PDF/A output path", require_pdf=True)
    folder = None if folder is None else _remote_folder(folder, "Document folder")
    pdf_api, cfg = _api_and_config(api, config)
    effective_storage = _storage(storage, cfg)
    normalized_version = normalize_pdfa_version(pdfa_version)
    response = _call_api(
        pdf_api.put_pdf_in_storage_to_pdf_a,
        name,
        out_path,
        normalized_version,
        folder=folder,
        storage=effective_storage,
    )
    return {
        "name": name,
        "out_path": out_path,
        "pdfa_version": normalized_version,
        "folder": folder,
        "storage": effective_storage,
        "result": to_plain_data(response),
    }


def _extract_text_from_rects(data: Any) -> str:
    plain = to_plain_data(data)
    fragments: list[str] = []

    def collect(value: Any) -> None:
        if isinstance(value, dict):
            text = value.get("text") or value.get("Text")
            if isinstance(text, str) and text:
                fragments.append(text)
            for item in value.values():
                collect(item)
        elif isinstance(value, list):
            for item in value:
                collect(item)

    collect(plain)
    return "\n".join(fragments)


def _get_list(value: Any, *keys: str) -> list[Any]:
    if isinstance(value, dict):
        for key in keys:
            item = value.get(key)
            if isinstance(item, list):
                return item
            if isinstance(item, dict):
                nested = item.get("list") or item.get("List")
                if isinstance(nested, list):
                    return nested
    return []


def _page_count(data: Any) -> int:
    plain = to_plain_data(data)
    pages = (plain.get("pages") or plain.get("Pages")) if isinstance(plain, dict) else None
    page_list = _get_list(pages, "list", "List")
    if not page_list:
        raise AsposePdfToolError("Could not determine document page count.", code="api_error")
    return len(page_list)


def _normalize_images(data: Any) -> list[dict[str, Any]]:
    plain = to_plain_data(data)
    images_container = (
        plain.get("images") or plain.get("Images") if isinstance(plain, dict) else plain
    )
    images = _get_list(images_container, "list", "List")
    return [image for image in images if isinstance(image, dict)]


def _image_id(image: dict[str, Any]) -> str | None:
    value = image.get("id") or image.get("Id")
    return value if isinstance(value, str) and value else None


def _image_extract_method(pdf_api: Any, image_format: str, *, single: bool) -> Callable[..., Any]:
    suffix = _normalized_image_format(image_format)
    prefix = "put_image_extract_as" if single else "put_images_extract_as"
    return getattr(pdf_api, f"{prefix}_{suffix}")


def _cell_text(cell: dict[str, Any]) -> str:
    fragments: list[str] = []
    for text_rect in _get_list(cell, "text_rects", "TextRects"):
        if not isinstance(text_rect, dict):
            continue
        text = text_rect.get("text") or text_rect.get("Text")
        if isinstance(text, str) and text:
            fragments.append(text)
    return "\n".join(fragments)


def _normalize_tables(data: Any) -> list[dict[str, Any]]:
    plain = to_plain_data(data)
    if isinstance(plain, dict):
        tables_container = plain.get("tables") or plain.get("Tables")
    else:
        tables_container = plain
    tables = _get_list(tables_container, "list", "List")
    normalized: list[dict[str, Any]] = []

    for table in tables:
        if not isinstance(table, dict):
            continue
        rows: list[list[str]] = []
        for row in _get_list(table, "row_list", "RowList"):
            if not isinstance(row, dict):
                continue
            cells = [
                _cell_text(cell)
                for cell in _get_list(row, "cell_list", "CellList")
                if isinstance(cell, dict)
            ]
            rows.append(cells)

        normalized.append(
            {
                "id": table.get("id") or table.get("Id"),
                "page": table.get("page_num") or table.get("PageNum"),
                "rows": rows,
                "raw": table,
            }
        )

    return normalized


def extract_text(
    name: str,
    folder: str | None = None,
    storage: str | None = None,
    *,
    api: Any | None = None,
    config: AsposeConfig | None = None,
) -> TextExtractionResult:
    name = _remote_path(name, "PDF name", require_pdf=True)
    folder = None if folder is None else _remote_folder(folder, "Document folder")
    pdf_api, cfg = _api_and_config(api, config)
    effective_storage = _storage(storage, cfg)
    response = _call_api(
        pdf_api.get_text,
        name,
        0,
        0,
        10000,
        10000,
        folder=folder,
        storage=effective_storage,
    )
    raw = to_plain_data(response)
    text = _extract_text_from_rects(raw)
    return {
        "name": name,
        "folder": folder,
        "storage": effective_storage,
        "text": text,
        "raw": raw,
    }


def extract_tables(
    name: str,
    pages: str | None = None,
    folder: str | None = None,
    storage: str | None = None,
    *,
    api: Any | None = None,
    config: AsposeConfig | None = None,
) -> dict[str, Any]:
    name = _remote_path(name, "PDF name", require_pdf=True)
    folder = None if folder is None else _remote_folder(folder, "Document folder")
    pdf_api, cfg = _api_and_config(api, config)
    effective_storage = _storage(storage, cfg)
    page_numbers = parse_page_list(pages)

    if page_numbers is None:
        raw = to_plain_data(
            _call_api(
                pdf_api.get_document_tables,
                name,
                folder=folder,
                storage=effective_storage,
            )
        )
        tables = _normalize_tables(raw)
    else:
        page_results: list[dict[str, Any]] = []
        tables = []
        for page_number in page_numbers:
            raw_page = to_plain_data(
                _call_api(
                    pdf_api.get_page_tables,
                    name,
                    page_number,
                    folder=folder,
                    storage=effective_storage,
                )
            )
            page_tables = _normalize_tables(raw_page)
            tables.extend(page_tables)
            page_results.append(
                {
                    "page": page_number,
                    "tables": page_tables,
                    "raw": raw_page,
                }
            )
        raw = {"pages": page_results}

    return {
        "name": name,
        "folder": folder,
        "storage": effective_storage,
        "pages": page_numbers,
        "tables": tables,
        "raw": raw,
    }


def list_images(
    name: str,
    pages: str | None = None,
    folder: str | None = None,
    storage: str | None = None,
    *,
    api: Any | None = None,
    config: AsposeConfig | None = None,
) -> dict[str, Any]:
    name = _remote_path(name, "PDF name", require_pdf=True)
    folder = None if folder is None else _remote_folder(folder, "Document folder")
    pdf_api, cfg = _api_and_config(api, config)
    effective_storage = _storage(storage, cfg)
    page_numbers = parse_page_list(pages)
    if page_numbers is None:
        page_numbers = list(
            range(
                1,
                _page_count(
                    _call_api(pdf_api.get_pages, name, folder=folder, storage=effective_storage)
                )
                + 1,
            )
        )

    page_results: list[dict[str, Any]] = []
    images: list[dict[str, Any]] = []
    for page_number in page_numbers:
        raw_page = to_plain_data(
            _call_api(
                pdf_api.get_images,
                name,
                page_number,
                folder=folder,
                storage=effective_storage,
            )
        )
        page_images = _normalize_images(raw_page)
        images.extend(
            {"page": page_number, "index": index, **image}
            for index, image in enumerate(page_images, 1)
        )
        page_results.append({"page": page_number, "images": page_images, "raw": raw_page})

    return {
        "name": name,
        "folder": folder,
        "storage": effective_storage,
        "pages": page_numbers,
        "images": images,
        "raw": {"pages": page_results},
    }


def extract_images(
    name: str,
    pages: str | None = None,
    dest_folder: str | None = None,
    image_format: str = "png",
    folder: str | None = None,
    storage: str | None = None,
    *,
    api: Any | None = None,
    config: AsposeConfig | None = None,
) -> dict[str, Any]:
    name = _remote_path(name, "PDF name", require_pdf=True)
    folder = None if folder is None else _remote_folder(folder, "Document folder")
    if dest_folder is None:
        raise AsposePdfToolError(
            "Image extraction requires a destination folder.", code="validation_error"
        )
    dest_folder = _remote_folder(dest_folder, "Destination folder")
    normalized_format = _normalized_image_format(image_format)

    pdf_api, cfg = _api_and_config(api, config)
    effective_storage = _storage(storage, cfg)
    page_numbers = parse_page_list(pages)
    if page_numbers is None:
        page_numbers = list(
            range(
                1,
                _page_count(
                    _call_api(pdf_api.get_pages, name, folder=folder, storage=effective_storage)
                )
                + 1,
            )
        )

    extract_method = _image_extract_method(pdf_api, normalized_format, single=False)
    page_results = []
    for page_number in page_numbers:
        response = _call_api(
            extract_method,
            name,
            page_number,
            folder=folder,
            storage=effective_storage,
            dest_folder=dest_folder,
        )
        page_results.append({"page": page_number, "result": to_plain_data(response)})

    return {
        "name": name,
        "folder": folder,
        "storage": effective_storage,
        "pages": page_numbers,
        "dest_folder": dest_folder,
        "format": normalized_format,
        "results": page_results,
    }


def extract_image(
    name: str,
    page: int,
    index: int,
    dest_folder: str | None = None,
    image_format: str = "png",
    folder: str | None = None,
    storage: str | None = None,
    *,
    api: Any | None = None,
    config: AsposeConfig | None = None,
) -> dict[str, Any]:
    if page < 1:
        raise AsposePdfToolError("Page numbers must be positive integers.", code="validation_error")
    if index < 1:
        raise AsposePdfToolError("Image index must be a positive integer.", code="validation_error")
    if dest_folder is None:
        raise AsposePdfToolError(
            "Image extraction requires a destination folder.", code="validation_error"
        )
    dest_folder = _remote_folder(dest_folder, "Destination folder")
    folder = None if folder is None else _remote_folder(folder, "Document folder")
    normalized_format = _normalized_image_format(image_format)

    image_result = list_images(name, str(page), folder, storage, api=api, config=config)
    page_images = image_result["raw"]["pages"][0]["images"]
    if index > len(page_images):
        raise AsposePdfToolError(
            f"Page {page} has {len(page_images)} image(s); index {index} is out of range.",
            code="validation_error",
        )
    selected = page_images[index - 1]
    selected_id = _image_id(selected)
    if not selected_id:
        raise AsposePdfToolError(
            f"Image {index} on page {page} does not include an SDK image ID.",
            code="api_error",
        )

    pdf_api, cfg = _api_and_config(api, config)
    effective_storage = _storage(storage, cfg)
    extract_method = _image_extract_method(pdf_api, normalized_format, single=True)
    response = _call_api(
        extract_method,
        name,
        selected_id,
        folder=folder,
        storage=effective_storage,
        dest_folder=dest_folder,
    )
    return {
        "name": name,
        "folder": folder,
        "storage": effective_storage,
        "page": page,
        "index": index,
        "image_id": selected_id,
        "image": selected,
        "dest_folder": dest_folder,
        "format": normalized_format,
        "result": to_plain_data(response),
    }


def write_text_output(
    path: str | Path,
    text: str,
    *,
    overwrite: bool = False,
) -> OutputResult:
    """Atomically write extracted text to a local path."""

    destination = atomic_write_text(path, text, overwrite=overwrite)
    return {"path": str(destination), "overwrite": overwrite}


def write_json_output(
    path: str | Path,
    data: Any,
    *,
    overwrite: bool = False,
) -> OutputResult:
    """Atomically write JSON output to a local path."""

    content = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    destination = atomic_write_text(path, content, overwrite=overwrite)
    return {"path": str(destination), "overwrite": overwrite}
