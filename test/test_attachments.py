import io

import pytest

from aspose_pdf_cloud_mcp import operations
from aspose_pdf_cloud_mcp.errors import AsposePdfToolError


class AttachmentApi:
    def __init__(self, names=None):
        self.names = ["report.txt", "report.txt"] if names is None else names
        self.downloads = []

    def get_document_attachments(self, name, **kwargs):
        return {"attachments": {"list": [{} for _ in self.names]}}

    def get_document_attachment_by_index(self, name, index, **kwargs):
        return {"attachment": {"name": self.names[index - 1], "size": 3}}

    def get_download_document_attachment_by_index(self, name, index, **kwargs):
        self.downloads.append((name, index, kwargs))
        return b"abc"


def test_sdk_stdout_does_not_pollute_transport_output(capsys):
    from aspose_pdf_cloud_mcp._operation_core import _call_api

    def noisy_sdk():
        print("SDK authentication diagnostics")
        return "result"

    assert _call_api(noisy_sdk) == "result"
    assert capsys.readouterr().out == ""


def test_list_and_bulk_extract(tmp_path):
    api = AttachmentApi()
    result = operations.extract_attachments(
        "sample.pdf", tmp_path, "docs", "store", api=api
    )
    assert [item["index"] for item in result["attachments"]] == [1, 2]
    assert (tmp_path / "1-report.txt").read_bytes() == b"abc"
    assert (tmp_path / "2-report.txt").read_bytes() == b"abc"
    assert api.downloads == [
        ("sample.pdf", i, {"folder": "docs", "storage": "store"}) for i in (1, 2)
    ]


@pytest.mark.parametrize("kind", ["bytes", "stream", "file"])
def test_single_download_forms(tmp_path, kind):
    api = AttachmentApi()
    source = tmp_path / "source"
    source.write_bytes(b"data")
    api.get_download_document_attachment_by_index = lambda *a, **kw: {
        "bytes": b"data",
        "stream": io.BytesIO(b"data"),
        "file": str(source),
    }[kind]
    target = tmp_path / "output"
    operations.extract_attachment("sample.pdf", 1, target, api=api)
    assert target.read_bytes() == b"data"
    with pytest.raises(AsposePdfToolError, match="already exists"):
        operations.extract_attachment("sample.pdf", 1, target, api=api)
    operations.extract_attachment("sample.pdf", 1, target, overwrite=True, api=api)


@pytest.mark.parametrize(
    "filename", ["../evil", "a/b", "a\\b", "C:evil", "..", "bad\x00name"]
)
def test_bulk_rejects_unsafe_names_before_download(tmp_path, filename):
    api = AttachmentApi(["ok.txt", filename])
    with pytest.raises(AsposePdfToolError) as exc:
        operations.extract_attachments("sample.pdf", tmp_path, api=api)
    assert exc.value.code == "validation_error"
    assert api.downloads == []


def test_bulk_preflights_conflicts_and_handles_empty(tmp_path):
    api = AttachmentApi()
    (tmp_path / "2-report.txt").write_bytes(b"keep")
    with pytest.raises(AsposePdfToolError):
        operations.extract_attachments("sample.pdf", tmp_path, api=api)
    assert api.downloads == []
    assert (
        operations.extract_attachments("sample.pdf", tmp_path, api=AttachmentApi([]))[
            "files"
        ]
        == []
    )


def test_invalid_index_and_download(tmp_path):
    api = AttachmentApi()
    with pytest.raises(AsposePdfToolError):
        operations.extract_attachment("sample.pdf", 0, tmp_path / "out", api=api)
    api.get_download_document_attachment_by_index = lambda *a, **kw: None
    with pytest.raises(AsposePdfToolError) as exc:
        operations.extract_attachment("sample.pdf", 1, tmp_path / "out", api=api)
    assert exc.value.code == "api_error"
