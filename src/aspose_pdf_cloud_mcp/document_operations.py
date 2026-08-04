"""PDF merge, split, and archival-conversion operations."""

from ._operation_core import (
    convert_pdf_to_pdfa,
    format_pdfa_version,
    list_pdfa_versions,
    merge_pdfs,
    normalize_pdfa_version,
    split_pdf,
    supported_pdfa_versions,
)

__all__ = [
    "convert_pdf_to_pdfa",
    "format_pdfa_version",
    "list_pdfa_versions",
    "merge_pdfs",
    "normalize_pdfa_version",
    "split_pdf",
    "supported_pdfa_versions",
]
