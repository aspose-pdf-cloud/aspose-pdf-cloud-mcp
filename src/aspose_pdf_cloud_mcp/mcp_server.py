"""MCP server exposing Aspose.PDF Stage 1 tools."""

from __future__ import annotations

from mcp.server.mcpserver import MCPServer

from . import __version__, operations
from .mcp_adapter import call_tool
from .result_types import ToolResponse

mcp = MCPServer(
    "aspose-pdf-cloud",
    title="Aspose.PDF Cloud MCP",
    description="PDF and storage automation backed by Aspose.PDF Cloud.",
    version=__version__,
)


@mcp.tool()
def list_files(path: str, storage_name: str | None = None) -> ToolResponse:
    """List files and folders in Aspose storage."""

    return call_tool(operations.list_files, path, storage_name)


@mcp.tool()
def upload_file(
        local_path: str,
        remote_path: str,
        storage_name: str | None = None,
) -> ToolResponse:
    """Upload a local file to Aspose storage."""

    return call_tool(operations.upload_file, local_path, remote_path, storage_name)


@mcp.tool()
def download_file(
        remote_path: str,
        local_path: str,
        storage_name: str | None = None,
        version_id: str | None = None,
        overwrite: bool = False,
) -> ToolResponse:
    """Download a file from Aspose storage."""

    return call_tool(
        operations.download_file,
        remote_path,
        local_path,
        storage_name,
        version_id,
        overwrite=overwrite,
    )


@mcp.tool()
def merge_pdfs(
        inputs: list[str] | None,
        output_name: str,
        folder: str | None = None,
        storage: str | None = None,
        from_folder: str | None = None,
) -> ToolResponse:
    """Merge PDF files already present in Aspose storage."""

    return call_tool(operations.merge_pdfs, inputs, output_name, folder, storage, from_folder)


@mcp.tool()
def split_pdf(
        name: str,
        ranges: str | None = None,
        folder: str | None = None,
        storage: str | None = None,
) -> ToolResponse:
    """Split a PDF into single pages or page-range segments."""

    return call_tool(operations.split_pdf, name, ranges, folder, storage)


@mcp.tool()
def list_pdfa_versions() -> ToolResponse:
    """List PDF/A conversion targets supported by the installed SDK."""

    return call_tool(operations.list_pdfa_versions)


@mcp.tool()
def convert_pdf_to_pdfa(
        name: str,
        out_path: str,
        pdfa_version: str = "PDF/A-1B",
        folder: str | None = None,
        storage: str | None = None,
) -> ToolResponse:
    """Convert a PDF in Aspose storage to a selected PDF/A version."""

    return call_tool(
        operations.convert_pdf_to_pdfa,
        name,
        out_path,
        pdfa_version,
        folder,
        storage,
    )


@mcp.tool()
def extract_text(
        name: str,
        folder: str | None = None,
        storage: str | None = None,
) -> ToolResponse:
    """Extract text from a PDF in Aspose storage."""

    return call_tool(operations.extract_text, name, folder, storage)


@mcp.tool()
def extract_tables(
        name: str,
        pages: str | None = None,
        folder: str | None = None,
        storage: str | None = None,
) -> ToolResponse:
    """Extract tables from a PDF in Aspose storage."""

    return call_tool(operations.extract_tables, name, pages, folder, storage)


@mcp.tool()
def list_images(
        name: str,
        pages: str | None = None,
        folder: str | None = None,
        storage: str | None = None,
) -> ToolResponse:
    """List images in a PDF in Aspose storage."""

    return call_tool(operations.list_images, name, pages, folder, storage)


@mcp.tool()
def extract_images(
        name: str,
        pages: str | None = None,
        dest_folder: str | None = None,
        image_format: str = "png",
        folder: str | None = None,
        storage: str | None = None,
) -> ToolResponse:
    """Extract all images from a PDF or selected pages."""

    return call_tool(
        operations.extract_images,
        name,
        pages,
        dest_folder,
        image_format,
        folder,
        storage,
    )


@mcp.tool()
def extract_image(
        name: str,
        page: int,
        index: int,
        dest_folder: str | None = None,
        image_format: str = "png",
        folder: str | None = None,
        storage: str | None = None,
) -> ToolResponse:
    """Extract one image by its one-based index on a page."""

    return call_tool(
        operations.extract_image,
        name,
        page,
        index,
        dest_folder,
        image_format,
        folder,
        storage,
    )


@mcp.tool()
def list_attachments(
    name: str, folder: str | None = None, storage: str | None = None
) -> ToolResponse:
    """List embedded attachments with one-based indexes and metadata."""
    return call_tool(operations.list_attachments, name, folder, storage)


@mcp.tool()
def extract_attachment(
    name: str,
    index: int,
    local_path: str,
    folder: str | None = None,
    storage: str | None = None,
    overwrite: bool = False,
) -> ToolResponse:
    """Download one embedded attachment to a local file."""
    return call_tool(
        operations.extract_attachment,
        name,
        index,
        local_path,
        folder,
        storage,
        overwrite=overwrite,
    )


@mcp.tool()
def extract_attachments(
    name: str,
    output_dir: str,
    folder: str | None = None,
    storage: str | None = None,
    overwrite: bool = False,
) -> ToolResponse:
    """Download all embedded attachments to a local directory."""
    return call_tool(
        operations.extract_attachments,
        name,
        output_dir,
        folder,
        storage,
        overwrite=overwrite,
    )


def main() -> None:
    mcp.run()
