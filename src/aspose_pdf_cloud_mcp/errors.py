"""Structured, redacted user-facing errors."""

from __future__ import annotations

import os
import re
from collections.abc import Iterable, Mapping
from typing import Any

from .result_types import ErrorPayload

_SECRET_ENV_KEYS = (
    "ASPOSE_CLIENT_ID",
    "ASPOSE_CLIENT_SECRET",
)
_SENSITIVE_PATTERNS = (
    re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s,;]+"),
    re.compile(
        r"(?i)((?:client_secret|client_id|access_token|api[_-]?key|token)\s*[:=]\s*)"
        r"(?:\"[^\"]*\"|'[^']*'|[^\s,;&]+)"
    ),
    re.compile(r"(?i)([?&](?:client_secret|client_id|access_token|api[_-]?key|token)=)[^&#\s]+"),
)


def sanitize_message(message: object, secrets: Iterable[str] = ()) -> str:
    """Redact configured credentials and common credential-shaped values."""

    sanitized = str(message)
    configured = [os.getenv(key, "") for key in _SECRET_ENV_KEYS]
    for secret in [*configured, *secrets]:
        if secret and len(secret.strip()) >= 4:
            sanitized = sanitized.replace(secret.strip(), "<redacted>")
    for pattern in _SENSITIVE_PATTERNS:
        sanitized = pattern.sub(r"\1<redacted>", sanitized)
    return sanitized


class AsposePdfError(RuntimeError):
    """Base class for stable, user-facing errors."""

    default_code = "aspose_pdf_error"

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        self.code = code or self.default_code
        self.message = sanitize_message(message)
        self.details = dict(details or {})
        super().__init__(self.message)

    def as_dict(self) -> ErrorPayload:
        """Return the stable error envelope used by CLI JSON and MCP tools."""

        result: ErrorPayload = {"code": self.code, "message": self.message}
        if self.details:
            result["details"] = self.details
        return result


class ConfigError(AsposePdfError):
    """Raised when required configuration is missing or invalid."""

    default_code = "configuration_error"


class AsposePdfToolError(AsposePdfError):
    """Raised for sanitized user-facing operation failures."""

    default_code = "operation_error"


def error_payload(exc: Exception) -> ErrorPayload:
    """Convert any exception into a safe, stable error payload."""

    if isinstance(exc, AsposePdfError):
        return exc.as_dict()
    return {
        "code": "internal_error",
        "message": "Unexpected internal error.",
    }
