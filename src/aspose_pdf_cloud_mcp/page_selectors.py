"""Shared one-based page-selector parsing."""

from __future__ import annotations

from .errors import AsposePdfToolError


def _parse_segments(value: str | None, label: str) -> list[tuple[int, int]] | None:
    if value is None or not value.strip():
        return None

    segments: list[tuple[int, int]] = []
    for raw_part in value.split(","):
        part = raw_part.strip()
        if not part:
            raise AsposePdfToolError(
                f"{label} contains an empty page selector.", code="validation_error"
            )

        bounds = [bound.strip() for bound in part.split("-", 1)]
        if len(bounds) == 1:
            bounds.append(bounds[0])
        if not bounds[0] or not bounds[1]:
            raise AsposePdfToolError(f"Invalid page range: {part}", code="validation_error")
        try:
            start, end = int(bounds[0]), int(bounds[1])
        except ValueError as exc:
            description = "page number" if len(set(bounds)) == 1 else "page range"
            raise AsposePdfToolError(
                f"Invalid {description}: {part}", code="validation_error"
            ) from exc
        if start < 1 or end < 1:
            raise AsposePdfToolError(
                "Page numbers must be positive integers.", code="validation_error"
            )
        if start > end:
            raise AsposePdfToolError(
                f"Page range start exceeds end: {part}", code="validation_error"
            )
        segments.append((start, end))
    return segments


def parse_page_ranges(value: str | None) -> list[tuple[int, int]] | None:
    """Preserve one-based segments such as ``1-3,4,5-8``."""

    return _parse_segments(value, "Range list")


def parse_page_list(value: str | None) -> list[int] | None:
    """Expand and deduplicate a selector such as ``1,3,4-7,10``."""

    segments = _parse_segments(value, "Page list")
    if segments is None:
        return None
    pages: list[int] = []
    seen: set[int] = set()
    for start, end in segments:
        for page in range(start, end + 1):
            if page not in seen:
                pages.append(page)
                seen.add(page)
    return pages
