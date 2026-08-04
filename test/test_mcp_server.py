from mcp.server.mcpserver import MCPServer

from aspose_pdf_cloud_mcp import __version__, mcp_server


def test_server_uses_mcp_v2_and_generated_version():
    assert isinstance(mcp_server.mcp, MCPServer)
    assert mcp_server.mcp.name == "aspose-pdf-cloud"
    assert mcp_server.mcp.version == __version__


def test_mcp_tool_success(monkeypatch):
    monkeypatch.setattr(
        mcp_server.operations,
        "list_files",
        lambda path, storage_name=None: {"path": path, "storage_name": storage_name},
    )

    result = mcp_server.list_files("/", "store")

    assert result == {"ok": True, "data": {"path": "/", "storage_name": "store"}}


def test_mcp_tool_failure(monkeypatch):
    def fail(name, folder=None, storage=None):
        raise RuntimeError("failed")

    monkeypatch.setattr(mcp_server.operations, "extract_text", fail)

    result = mcp_server.extract_text("sample.pdf")

    assert result == {
        "ok": False,
        "error": {
            "code": "internal_error",
            "message": "Unexpected internal error.",
        },
    }


def test_mcp_download_passes_explicit_overwrite(monkeypatch):
    calls = []

    def download(remote_path, local_path, storage_name, version_id, *, overwrite=False):
        calls.append((remote_path, local_path, storage_name, version_id, overwrite))
        return {"local_path": local_path}

    monkeypatch.setattr(mcp_server.operations, "download_file", download)

    result = mcp_server.download_file("/sample.pdf", "sample.pdf", overwrite=True)

    assert result["ok"] is True
    assert calls == [("/sample.pdf", "sample.pdf", None, None, True)]


def test_mcp_extract_tables_passes_page_list(monkeypatch):
    calls = []

    def extract_tables(name, pages=None, folder=None, storage=None):
        calls.append((name, pages, folder, storage))
        return {"tables": []}

    monkeypatch.setattr(mcp_server.operations, "extract_tables", extract_tables)

    result = mcp_server.extract_tables("sample.pdf", "1,3,4-7,10", "docs", "store")

    assert result == {"ok": True, "data": {"tables": []}}
    assert calls == [("sample.pdf", "1,3,4-7,10", "docs", "store")]


def test_mcp_split_pdf_passes_ranges(monkeypatch):
    calls = []

    def split_pdf(name, ranges=None, folder=None, storage=None):
        calls.append((name, ranges, folder, storage))
        return {"documents": []}

    monkeypatch.setattr(mcp_server.operations, "split_pdf", split_pdf)

    result = mcp_server.split_pdf("sample.pdf", "1-3,4,5-8", "docs", "store")

    assert result == {"ok": True, "data": {"documents": []}}
    assert calls == [("sample.pdf", "1-3,4,5-8", "docs", "store")]


def test_mcp_list_pdfa_versions(monkeypatch):
    monkeypatch.setattr(
        mcp_server.operations,
        "list_pdfa_versions",
        lambda: {"versions": [{"value": "PDFA1B", "label": "PDF/A-1B"}]},
    )

    result = mcp_server.list_pdfa_versions()

    assert result == {
        "ok": True,
        "data": {"versions": [{"value": "PDFA1B", "label": "PDF/A-1B"}]},
    }


def test_mcp_convert_pdf_to_pdfa_passes_version(monkeypatch):
    calls = []

    def convert_pdf_to_pdfa(
        name,
        out_path,
        pdfa_version="PDF/A-1B",
        folder=None,
        storage=None,
    ):
        calls.append((name, out_path, pdfa_version, folder, storage))
        return {"out_path": out_path, "pdfa_version": "PDFA1B"}

    monkeypatch.setattr(mcp_server.operations, "convert_pdf_to_pdfa", convert_pdf_to_pdfa)

    result = mcp_server.convert_pdf_to_pdfa(
        "sample.pdf",
        "/archive/sample-pdfa.pdf",
        "PDF/A-1B",
        "docs",
        "store",
    )

    assert result == {
        "ok": True,
        "data": {"out_path": "/archive/sample-pdfa.pdf", "pdfa_version": "PDFA1B"},
    }
    assert calls == [("sample.pdf", "/archive/sample-pdfa.pdf", "PDF/A-1B", "docs", "store")]


def test_mcp_list_images_passes_page_list(monkeypatch):
    calls = []

    def list_images(name, pages=None, folder=None, storage=None):
        calls.append((name, pages, folder, storage))
        return {"images": []}

    monkeypatch.setattr(mcp_server.operations, "list_images", list_images)

    result = mcp_server.list_images("sample.pdf", "1,3,4-7,10", "docs", "store")

    assert result == {"ok": True, "data": {"images": []}}
    assert calls == [("sample.pdf", "1,3,4-7,10", "docs", "store")]


def test_mcp_extract_images_passes_destination(monkeypatch):
    calls = []

    def extract_images(
        name, pages=None, dest_folder=None, image_format="png", folder=None, storage=None
    ):
        calls.append((name, pages, dest_folder, image_format, folder, storage))
        return {"results": []}

    monkeypatch.setattr(mcp_server.operations, "extract_images", extract_images)

    result = mcp_server.extract_images("sample.pdf", "1,3", "out/images", "jpg", "docs", "store")

    assert result == {"ok": True, "data": {"results": []}}
    assert calls == [("sample.pdf", "1,3", "out/images", "jpg", "docs", "store")]


def test_mcp_extract_image_passes_page_index(monkeypatch):
    calls = []

    def extract_image(
        name,
        page,
        index,
        dest_folder=None,
        image_format="png",
        folder=None,
        storage=None,
    ):
        calls.append((name, page, index, dest_folder, image_format, folder, storage))
        return {"image_id": "i1"}

    monkeypatch.setattr(mcp_server.operations, "extract_image", extract_image)

    result = mcp_server.extract_image("sample.pdf", 1, 2, "out/images", "png", "docs", "store")

    assert result == {"ok": True, "data": {"image_id": "i1"}}
    assert calls == [("sample.pdf", 1, 2, "out/images", "png", "docs", "store")]
