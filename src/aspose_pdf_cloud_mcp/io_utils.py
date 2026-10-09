"""Atomic local file helpers."""

from __future__ import annotations

import os
import shutil
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import BinaryIO

from .errors import AsposePdfToolError


def _prepare_destination(path: str | Path, *, overwrite: bool) -> Path:
    destination = Path(path)
    if not str(destination).strip():
        raise AsposePdfToolError("Local output path must not be empty.", code="validation_error")
    if destination.exists() and destination.is_dir():
        raise AsposePdfToolError(
            f"Local output path is a directory: {destination}", code="validation_error"
        )
    if destination.exists() and not overwrite:
        raise AsposePdfToolError(
            f"Local output already exists: {destination}. Use overwrite to replace it.",
            code="conflict",
        )
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise AsposePdfToolError(
            f"Could not create local output directory: {destination.parent}", code="io_error"
        ) from exc
    return destination


def _commit_temporary(temp_path: Path, destination: Path, *, overwrite: bool) -> None:
    try:
        if overwrite:
            os.replace(temp_path, destination)
        else:
            os.link(temp_path, destination)
            temp_path.unlink()
    except FileExistsError as exc:
        raise AsposePdfToolError(
            f"Local output already exists: {destination}. Use overwrite to replace it.",
            code="conflict",
        ) from exc
    except OSError as exc:
        raise AsposePdfToolError(
            f"Could not finalize local output: {destination}", code="io_error"
        ) from exc


def atomic_write(
        path: str | Path,
        writer: Callable[[BinaryIO], object],
        *,
        overwrite: bool = False,
        mode: int | None = None,
) -> Path:
    """Write a local file through a same-directory temporary file."""

    destination = _prepare_destination(path, overwrite=overwrite)
    descriptor, raw_temp_path = tempfile.mkstemp(
        dir=destination.parent,
        prefix=f".{destination.name}.",
        suffix=".tmp",
    )
    temp_path = Path(raw_temp_path)
    try:
        with os.fdopen(descriptor, "wb") as output:
            writer(output)
            output.flush()
            os.fsync(output.fileno())
        if mode is not None:
            os.chmod(temp_path, mode)
        _commit_temporary(temp_path, destination, overwrite=overwrite)
    except AsposePdfToolError:
        raise
    except OSError as exc:
        raise AsposePdfToolError(
            f"Could not write local output: {destination}", code="io_error"
        ) from exc
    finally:
        temp_path.unlink(missing_ok=True)
    return destination


def atomic_write_bytes(path: str | Path, data: bytes, *, overwrite: bool = False) -> Path:
    """Atomically write bytes to a local file."""

    return atomic_write(path, lambda output: output.write(data), overwrite=overwrite)


def atomic_write_text(
        path: str | Path,
        text: str,
        *,
        overwrite: bool = False,
        mode: int | None = None,
) -> Path:
    """Atomically write UTF-8 text to a local file."""

    return atomic_write(
        path,
        lambda output: output.write(text.encode("utf-8")),
        overwrite=overwrite,
        mode=mode,
    )


def atomic_copy_stream(
        path: str | Path,
        source: BinaryIO,
        *,
        overwrite: bool = False,
) -> Path:
    """Atomically copy a readable binary stream to a local file."""

    return atomic_write(
        path, lambda output: shutil.copyfileobj(source, output), overwrite=overwrite
    )
