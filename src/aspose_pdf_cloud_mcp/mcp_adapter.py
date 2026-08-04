"""Shared MCP result and error adaptation."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from .errors import error_payload, sanitize_message
from .result_types import ToolResponse

logger = logging.getLogger(__name__)


def call_tool(func: Callable[..., Any], *args: Any, **kwargs: Any) -> ToolResponse:
    """Invoke an operation and return the stable MCP envelope."""

    try:
        return {"ok": True, "data": func(*args, **kwargs)}
    except Exception as exc:  # noqa: BLE001 - protocol boundary.
        error = error_payload(exc)
        logger.error("MCP tool failed [%s]: %s", error["code"], sanitize_message(exc))
        return {"ok": False, "error": error}
