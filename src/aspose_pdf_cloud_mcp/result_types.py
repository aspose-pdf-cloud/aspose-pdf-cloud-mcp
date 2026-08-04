"""Typed result contracts shared by operations, CLI, and MCP."""

from __future__ import annotations

from typing import Any, NotRequired

from typing_extensions import TypedDict


class ErrorPayload(TypedDict):
    code: str
    message: str
    details: NotRequired[dict[str, Any]]


class ToolResponse(TypedDict):
    ok: bool
    data: NotRequired[Any]
    error: NotRequired[ErrorPayload]


class StorageListResult(TypedDict):
    path: str
    storage_name: str | None
    items: Any


class DownloadResult(TypedDict):
    remote_path: str
    local_path: str
    storage_name: str | None
    version_id: str | None


class OutputResult(TypedDict):
    path: str
    overwrite: bool


class TextExtractionResult(TypedDict):
    name: str
    folder: str | None
    storage: str | None
    text: str
    raw: Any
