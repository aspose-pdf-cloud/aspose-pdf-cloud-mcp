"""Configuration helpers for Aspose.PDF access."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .errors import ConfigError
from .io_utils import atomic_write_text

ASPOSE_PDF_ENV_KEYS = (
    "ASPOSE_CLIENT_ID",
    "ASPOSE_CLIENT_SECRET",
    "ASPOSE_STORAGE_NAME",
    "ASPOSE_BASE_URL",
    "ASPOSE_SELF_HOST",
)


@dataclass(frozen=True)
class AsposeConfig:
    client_id: str
    client_secret: str
    base_url: str | None = None
    self_host: bool = False
    storage_name: str | None = None


def _truthy(value: str | None) -> bool:
    return value is not None and value.strip().lower() in {"1", "true", "yes", "on"}


def _read_env_file(path: str | Path | None) -> dict[str, str]:
    if path is None:
        return {}

    env_path = Path(path)
    if not env_path.is_file():
        return {}

    values: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def _get_setting(name: str, env_file_values: dict[str, str]) -> str:
    return os.getenv(name, env_file_values.get(name, "")).strip()


def _format_env_value(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _env_key_from_line(line: str) -> str | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        return None
    key, _ = stripped.split("=", 1)
    key = key.strip()
    return key or None


def load_config(env_file: str | Path | None = ".env") -> AsposeConfig:
    """Load Aspose Cloud configuration from environment variables and optional .env."""

    env_file_values = _read_env_file(env_file)

    client_id = _get_setting("ASPOSE_CLIENT_ID", env_file_values)
    client_secret = _get_setting("ASPOSE_CLIENT_SECRET", env_file_values)

    if not client_id or not client_secret:
        raise ConfigError(
            "Missing Aspose credentials. Set ASPOSE_CLIENT_ID and ASPOSE_CLIENT_SECRET."
        )

    base_url = _get_setting("ASPOSE_BASE_URL", env_file_values) or None
    storage_name = _get_setting("ASPOSE_STORAGE_NAME", env_file_values) or None

    return AsposeConfig(
        client_id=client_id,
        client_secret=client_secret,
        base_url=base_url,
        self_host=_truthy(_get_setting("ASPOSE_SELF_HOST", env_file_values)),
        storage_name=storage_name,
    )


def get_auth_status(env_file: str | Path | None = ".env") -> dict[str, object]:
    """Return redacted Aspose.PDF credential status from environment and optional .env."""

    env_file_values = _read_env_file(env_file)
    settings: dict[str, dict[str, str | bool | None]] = {}

    for key in ASPOSE_PDF_ENV_KEYS:
        env_value = os.getenv(key)
        file_value = env_file_values.get(key)
        value = (env_value if env_value is not None else file_value) or ""
        source = "environment" if env_value is not None else "env_file" if file_value else "missing"
        settings[key] = {
            "configured": bool(value.strip()),
            "source": source,
            "value": redact_secret(value),
        }

    configured = bool(
        settings["ASPOSE_CLIENT_ID"]["configured"]
        and settings["ASPOSE_CLIENT_SECRET"]["configured"]
    )
    return {
        "configured": configured,
        "env_file": str(env_file) if env_file is not None else None,
        "settings": settings,
    }


def redact_secret(value: str | None) -> str:
    """Return a display-safe representation of a secret-like value."""

    if not value:
        return ""
    stripped = value.strip()
    if len(stripped) <= 8:
        return "<set>"
    return f"{stripped[:4]}...{stripped[-4:]}"


def write_auth_env_file(
    env_file: str | Path,
    values: dict[str, str | bool | None],
) -> Path:
    """Write Aspose.PDF auth settings to a .env file while preserving unrelated lines."""

    env_path = Path(env_file)
    updates: dict[str, str] = {}
    for key in ASPOSE_PDF_ENV_KEYS:
        value = values.get(key)
        if isinstance(value, bool):
            updates[key] = "true" if value else "false"
        elif value is not None and str(value).strip():
            updates[key] = str(value).strip()

    if not updates.get("ASPOSE_CLIENT_ID") or not updates.get("ASPOSE_CLIENT_SECRET"):
        raise ConfigError("ASPOSE_CLIENT_ID and ASPOSE_CLIENT_SECRET are required.")

    lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
    written_keys: set[str] = set()
    output: list[str] = []

    for line in lines:
        parsed_key = _env_key_from_line(line)
        if parsed_key in updates:
            output.append(f"{parsed_key}={_format_env_value(updates[parsed_key])}")
            written_keys.add(parsed_key)
        else:
            output.append(line)

    if output and any(key not in written_keys for key in updates):
        output.append("")
    for key in ASPOSE_PDF_ENV_KEYS:
        if key in updates and key not in written_keys:
            output.append(f"{key}={_format_env_value(updates[key])}")

    return atomic_write_text(
        env_path,
        "\n".join(output) + "\n",
        overwrite=True,
        mode=0o600,
    )
