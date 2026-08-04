"""Compatibility facade for shared Aspose.PDF operations.

New implementation belongs in the focused domain modules. CLI and MCP code
import this facade so both surfaces continue to share one stable operation API.
"""

import asposepdfcloud

from ._operation_core import AsposePdfToolError, to_plain_data
from .document_operations import (
    convert_pdf_to_pdfa,
    format_pdfa_version,
    list_pdfa_versions,
    merge_pdfs,
    normalize_pdfa_version,
    split_pdf,
    supported_pdfa_versions,
)
from .extraction_operations import (
    extract_image,
    extract_images,
    extract_tables,
    extract_text,
    list_images,
)
from .output_operations import write_json_output, write_text_output
from .page_selectors import parse_page_list, parse_page_ranges
from .storage_operations import download_file, list_files, test_auth, upload_file

__all__ = [
    "AsposePdfToolError",
    "asposepdfcloud",
    "convert_pdf_to_pdfa",
    "download_file",
    "extract_image",
    "extract_images",
    "extract_tables",
    "extract_text",
    "format_pdfa_version",
    "list_files",
    "list_images",
    "list_pdfa_versions",
    "merge_pdfs",
    "normalize_pdfa_version",
    "parse_page_list",
    "parse_page_ranges",
    "split_pdf",
    "supported_pdfa_versions",
    "test_auth",
    "to_plain_data",
    "upload_file",
    "write_json_output",
    "write_text_output",
]
