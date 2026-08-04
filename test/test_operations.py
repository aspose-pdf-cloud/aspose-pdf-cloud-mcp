from pathlib import Path

import pytest

from aspose_pdf_cloud_mcp import operations
from aspose_pdf_cloud_mcp.config import AsposeConfig


class DummyApi:
    def __init__(self):
        self.calls = []
        self.files_list = {"value": [{"name": "sample.pdf", "path": "/sample.pdf", "size": 10}]}

    def get_files_list(self, path, **kwargs):
        self.calls.append(("get_files_list", path, kwargs))
        return self.files_list

    def upload_file(self, remote_path, local_path, **kwargs):
        self.calls.append(("upload_file", remote_path, local_path, kwargs))
        return {"uploaded": [remote_path]}

    def download_file(self, remote_path, **kwargs):
        self.calls.append(("download_file", remote_path, kwargs))
        source = Path(kwargs["source_file"])
        return str(source)

    def put_merge_documents(self, output_name, merge_documents, **kwargs):
        self.calls.append(("put_merge_documents", output_name, merge_documents, kwargs))
        return {"document": output_name}

    def post_split_document(self, name, **kwargs):
        self.calls.append(("post_split_document", name, kwargs))
        return {
            "result": {
                "documents": [
                    {"href": "sample_1.pdf", "title": "sample_1.pdf"},
                    {"href": "sample_2.pdf", "title": "sample_2.pdf"},
                ]
            }
        }

    def post_split_range_pdf_document(self, name, options, **kwargs):
        self.calls.append(("post_split_range_pdf_document", name, options, kwargs))
        return {
            "result": {
                "documents": [
                    {"href": "sample_1-3.pdf", "title": "sample_1-3.pdf"},
                    {"href": "sample_4.pdf", "title": "sample_4.pdf"},
                ]
            }
        }

    def put_pdf_in_storage_to_pdf_a(self, name, out_path, pdfa_type, **kwargs):
        self.calls.append(("put_pdf_in_storage_to_pdf_a", name, out_path, pdfa_type, kwargs))
        return {"document": out_path, "pdfa_type": pdfa_type}

    def get_text(self, name, llx, lly, urx, ury, **kwargs):
        self.calls.append(("get_text", name, llx, lly, urx, ury, kwargs))
        return {
            "text_occurrences": {
                "list": [
                    {"text": "Hello"},
                    {"Text": "world"},
                ]
            }
        }

    def get_document_tables(self, name, **kwargs):
        self.calls.append(("get_document_tables", name, kwargs))
        return _table_response(page=1, table_id="t1")

    def get_page_tables(self, name, page_number, **kwargs):
        self.calls.append(("get_page_tables", name, page_number, kwargs))
        return _table_response(page=page_number, table_id=f"t{page_number}")

    def get_pages(self, name, **kwargs):
        self.calls.append(("get_pages", name, kwargs))
        return {"pages": {"list": [{"number": 1}, {"number": 2}]}}

    def get_images(self, name, page_number, **kwargs):
        self.calls.append(("get_images", name, page_number, kwargs))
        return _images_response(page_number)

    def put_images_extract_as_png(self, name, page_number, **kwargs):
        self.calls.append(("put_images_extract_as_png", name, page_number, kwargs))
        return {"page": page_number, "format": "png"}

    def put_images_extract_as_jpeg(self, name, page_number, **kwargs):
        self.calls.append(("put_images_extract_as_jpeg", name, page_number, kwargs))
        return {"page": page_number, "format": "jpeg"}

    def put_image_extract_as_png(self, name, image_id, **kwargs):
        self.calls.append(("put_image_extract_as_png", name, image_id, kwargs))
        return {"image_id": image_id, "format": "png"}


def _table_response(page, table_id):
    return {
        "tables": {
            "list": [
                {
                    "id": table_id,
                    "page_num": page,
                    "row_list": [
                        {
                            "cell_list": [
                                {"text_rects": {"list": [{"text": f"P{page} A"}]}},
                                {"TextRects": {"List": [{"Text": f"P{page} B"}]}},
                            ]
                        }
                    ],
                }
            ]
        }
    }


def _images_response(page):
    return {
        "images": {
            "list": [
                {
                    "id": f"img-{page}-1",
                    "width": 100,
                    "height": 80,
                    "page_number": page,
                },
                {
                    "Id": f"img-{page}-2",
                    "Width": 200,
                    "Height": 160,
                    "PageNumber": page,
                },
            ]
        }
    }


def test_list_files_uses_sdk_method():
    api = DummyApi()

    result = operations.list_files("/", "store", api=api)

    assert result["path"] == "/"
    assert result["items"]["value"][0]["name"] == "sample.pdf"
    assert api.calls == [("get_files_list", "/", {"storage_name": "store"})]


def test_list_files_uses_config_storage_default():
    api = DummyApi()
    config = AsposeConfig(client_id="id", client_secret="secret", storage_name="default-store")

    result = operations.list_files("/", api=api, config=config)

    assert result["storage_name"] == "default-store"
    assert api.calls == [("get_files_list", "/", {"storage_name": "default-store"})]


def test_auth_test_lists_storage_without_returning_secrets():
    api = DummyApi()
    config = AsposeConfig(client_id="id", client_secret="secret", storage_name="default-store")

    result = operations.test_auth(api=api, config=config)

    assert result == {
        "ok": True,
        "path": "/",
        "storage_name": "default-store",
        "item_count": 1,
    }
    assert api.calls == [("get_files_list", "/", {"storage_name": "default-store"})]


def test_upload_file_uses_sdk_method(tmp_path):
    api = DummyApi()
    source = tmp_path / "sample.pdf"
    source.write_bytes(b"pdf")

    result = operations.upload_file(source, "/sample.pdf", "store", api=api)

    assert result["remote_path"] == "/sample.pdf"
    assert api.calls == [("upload_file", "/sample.pdf", str(source), {"storage_name": "store"})]


def test_upload_file_requires_existing_local_file(tmp_path):
    with pytest.raises(operations.AsposePdfToolError):
        operations.upload_file(tmp_path / "missing.pdf", "/missing.pdf", api=DummyApi())


def test_download_file_copies_sdk_temp_file(tmp_path):
    api = DummyApi()
    source = tmp_path / "source.pdf"
    source.write_bytes(b"downloaded")
    destination = tmp_path / "out" / "sample.pdf"

    original_download = api.download_file

    def download_file(remote_path, **kwargs):
        kwargs["source_file"] = str(source)
        return original_download(remote_path, **kwargs)

    api.download_file = download_file
    result = operations.download_file("/sample.pdf", destination, "store", "v1", api=api)

    assert destination.read_bytes() == b"downloaded"
    assert result["local_path"] == str(destination)
    assert api.calls == [
        (
            "download_file",
            "/sample.pdf",
            {"storage_name": "store", "version_id": "v1", "source_file": str(source)},
        )
    ]


def test_download_file_refuses_existing_destination_before_api_call(tmp_path):
    api = DummyApi()
    destination = tmp_path / "sample.pdf"
    destination.write_bytes(b"original")

    with pytest.raises(operations.AsposePdfToolError) as captured:
        operations.download_file("/sample.pdf", destination, api=api)

    assert captured.value.code == "conflict"
    assert destination.read_bytes() == b"original"
    assert api.calls == []


def test_download_file_atomically_overwrites_when_allowed(tmp_path):
    api = DummyApi()
    source = tmp_path / "source.pdf"
    source.write_bytes(b"replacement")
    destination = tmp_path / "sample.pdf"
    destination.write_bytes(b"original")

    def download_file(remote_path, **kwargs):
        api.calls.append(("download_file", remote_path, kwargs))
        return str(source)

    api.download_file = download_file

    operations.download_file("/sample.pdf", destination, api=api, overwrite=True)

    assert destination.read_bytes() == b"replacement"


def test_merge_pdfs_uses_merge_documents_model(monkeypatch):
    api = DummyApi()

    class FakeMergeDocuments:
        def __init__(self, list):
            self.list = list

    monkeypatch.setattr(operations.asposepdfcloud, "MergeDocuments", FakeMergeDocuments)

    result = operations.merge_pdfs(
        ["/a.pdf", "/b.pdf", "/c.pdf"],
        "merged.pdf",
        "folder",
        "store",
        api=api,
    )

    _, output_name, merge_documents, kwargs = api.calls[0]
    assert output_name == "merged.pdf"
    assert merge_documents.list == ["/a.pdf", "/b.pdf", "/c.pdf"]
    assert kwargs == {"folder": "folder", "storage": "store"}
    assert result["output_name"] == "merged.pdf"
    assert result["inputs"] == ["/a.pdf", "/b.pdf", "/c.pdf"]


def test_merge_pdfs_can_use_all_pdfs_from_folder(monkeypatch):
    api = DummyApi()
    api.files_list = {
        "value": [
            {"name": "notes.txt", "path": "/batch/notes.txt", "is_folder": False},
            {"name": "b.pdf", "path": "/batch/b.pdf", "is_folder": False},
            {"name": "sub", "path": "/batch/sub", "is_folder": True},
            {"name": "a.PDF", "path": "/batch/a.PDF", "is_folder": False},
        ]
    }

    class FakeMergeDocuments:
        def __init__(self, list):
            self.list = list

    monkeypatch.setattr(operations.asposepdfcloud, "MergeDocuments", FakeMergeDocuments)

    result = operations.merge_pdfs(
        None,
        "merged.pdf",
        folder="out",
        storage="store",
        from_folder="/batch",
        api=api,
    )

    _, output_name, merge_documents, kwargs = api.calls[1]
    assert api.calls[0] == ("get_files_list", "/batch", {"storage_name": "store"})
    assert output_name == "merged.pdf"
    assert merge_documents.list == ["/batch/a.PDF", "/batch/b.pdf"]
    assert kwargs == {"folder": "out", "storage": "store"}
    assert result["from_folder"] == "/batch"


def test_merge_pdfs_requires_at_least_two_inputs(monkeypatch):
    class FakeMergeDocuments:
        def __init__(self, list):
            self.list = list

    monkeypatch.setattr(operations.asposepdfcloud, "MergeDocuments", FakeMergeDocuments)

    with pytest.raises(operations.AsposePdfToolError, match="at least two"):
        operations.merge_pdfs(["/a.pdf"], "merged.pdf", api=DummyApi())


def test_merge_pdfs_rejects_inputs_with_folder():
    with pytest.raises(operations.AsposePdfToolError, match="either explicit input files"):
        operations.merge_pdfs(
            ["/a.pdf", "/b.pdf"], "merged.pdf", from_folder="/batch", api=DummyApi()
        )


def test_remote_write_paths_are_validated_before_api_calls(tmp_path):
    api = DummyApi()
    source = tmp_path / "sample.pdf"
    source.write_bytes(b"pdf")

    with pytest.raises(operations.AsposePdfToolError) as captured:
        operations.upload_file(source, "../sample.pdf", api=api)

    assert captured.value.code == "validation_error"
    assert api.calls == []


def test_pdf_operations_require_pdf_paths():
    with pytest.raises(operations.AsposePdfToolError) as captured:
        operations.split_pdf("sample.txt", api=DummyApi())

    assert captured.value.code == "validation_error"


def test_local_output_helpers_require_explicit_overwrite(tmp_path):
    destination = tmp_path / "tables.json"
    destination.write_text("original", encoding="utf-8")

    with pytest.raises(operations.AsposePdfToolError) as captured:
        operations.write_json_output(destination, {"tables": []})

    assert captured.value.code == "conflict"
    operations.write_json_output(destination, {"tables": []}, overwrite=True)
    assert '"tables": []' in destination.read_text(encoding="utf-8")


def test_parse_page_ranges_preserves_segments():
    result = operations.parse_page_ranges("1-3,4,5-8")

    assert result == [(1, 3), (4, 4), (5, 8)]


def test_parse_page_ranges_rejects_invalid_ranges():
    with pytest.raises(operations.AsposePdfToolError, match="start exceeds end"):
        operations.parse_page_ranges("8-5")


def test_split_pdf_splits_document_into_single_pages():
    api = DummyApi()

    result = operations.split_pdf("sample.pdf", folder="docs", storage="store", api=api)

    assert result["mode"] == "pages"
    assert result["ranges"] is None
    assert [document["title"] for document in result["documents"]] == [
        "sample_1.pdf",
        "sample_2.pdf",
    ]
    assert api.calls == [
        (
            "post_split_document",
            "sample.pdf",
            {"format": "pdf", "folder": "docs", "storage": "store"},
        )
    ]


def test_split_pdf_splits_document_into_segments(monkeypatch):
    api = DummyApi()

    class FakePageRange:
        def __init__(self, _from, to):
            self._from = _from
            self.to = to

    class FakeSplitRangePdfOptions:
        def __init__(self, page_ranges):
            self.page_ranges = page_ranges

    monkeypatch.setattr(operations.asposepdfcloud, "PageRange", FakePageRange)
    monkeypatch.setattr(
        operations.asposepdfcloud,
        "SplitRangePdfOptions",
        FakeSplitRangePdfOptions,
    )

    result = operations.split_pdf("sample.pdf", "1-3,4", "docs", "store", api=api)

    _, name, options, kwargs = api.calls[0]
    assert name == "sample.pdf"
    assert [(page_range._from, page_range.to) for page_range in options.page_ranges] == [
        (1, 3),
        (4, 4),
    ]
    assert kwargs == {"folder": "docs", "storage": "store"}
    assert result["mode"] == "ranges"
    assert result["ranges"] == [(1, 3), (4, 4)]
    assert len(result["documents"]) == 2


def test_normalize_pdfa_version_accepts_friendly_values():
    assert operations.normalize_pdfa_version("PDF/A-1B") == "PDFA1B"
    assert operations.normalize_pdfa_version("pdfa3a") == "PDFA3A"
    assert operations.normalize_pdfa_version("3-b") == "PDFA3B"


def test_pdfa_versions_are_discovered_from_sdk(monkeypatch):
    class FakePdfAType:
        PDFA1A = "PDFA1A"
        PDFA1B = "PDFA1B"
        PDFA2B = "PDFA2B"
        PDFA3B = "PDFA3B"
        OTHER = "OTHER"

    monkeypatch.setattr(operations.asposepdfcloud, "PdfAType", FakePdfAType)

    result = operations.list_pdfa_versions()

    assert operations.supported_pdfa_versions() == [
        "PDFA1A",
        "PDFA1B",
        "PDFA2B",
        "PDFA3B",
    ]
    assert operations.normalize_pdfa_version("PDF/A-2B") == "PDFA2B"
    assert result["versions"][2] == {"value": "PDFA2B", "label": "PDF/A-2B"}
    assert result["default"] == "PDFA1B"


def test_normalize_pdfa_version_rejects_unsupported_values():
    with pytest.raises(operations.AsposePdfToolError, match="PDF/A version"):
        operations.normalize_pdfa_version("PDF/A-2B")


def test_convert_pdf_to_pdfa_uses_storage_conversion_method():
    api = DummyApi()

    result = operations.convert_pdf_to_pdfa(
        "sample.pdf",
        "/archive/sample-pdfa.pdf",
        "PDF/A-3B",
        folder="docs",
        storage="store",
        api=api,
    )

    assert result["pdfa_version"] == "PDFA3B"
    assert result["out_path"] == "/archive/sample-pdfa.pdf"
    assert api.calls == [
        (
            "put_pdf_in_storage_to_pdf_a",
            "sample.pdf",
            "/archive/sample-pdfa.pdf",
            "PDFA3B",
            {"folder": "docs", "storage": "store"},
        )
    ]


def test_extract_text_returns_plain_text_and_raw_response():
    api = DummyApi()

    result = operations.extract_text("sample.pdf", "folder", "store", api=api)

    assert result["text"] == "Hello\nworld"
    assert result["raw"]["text_occurrences"]["list"][0]["text"] == "Hello"
    assert api.calls == [
        (
            "get_text",
            "sample.pdf",
            0,
            0,
            10000,
            10000,
            {"folder": "folder", "storage": "store"},
        )
    ]


def test_parse_page_list_expands_ranges_and_removes_duplicates():
    result = operations.parse_page_list("1,3,4-7,7,10")

    assert result == [1, 3, 4, 5, 6, 7, 10]


def test_parse_page_list_rejects_invalid_ranges():
    with pytest.raises(operations.AsposePdfToolError, match="start exceeds end"):
        operations.parse_page_list("7-4")


def test_extract_tables_uses_document_tables_for_whole_document():
    api = DummyApi()

    result = operations.extract_tables("sample.pdf", folder="folder", storage="store", api=api)

    assert result["pages"] is None
    assert result["tables"][0]["id"] == "t1"
    assert result["tables"][0]["page"] == 1
    assert result["tables"][0]["rows"] == [["P1 A", "P1 B"]]
    assert api.calls == [
        ("get_document_tables", "sample.pdf", {"folder": "folder", "storage": "store"})
    ]


def test_extract_tables_uses_page_tables_for_page_list():
    api = DummyApi()

    result = operations.extract_tables("sample.pdf", "1,3-4", "folder", "store", api=api)

    assert result["pages"] == [1, 3, 4]
    assert [table["page"] for table in result["tables"]] == [1, 3, 4]
    assert api.calls == [
        ("get_page_tables", "sample.pdf", 1, {"folder": "folder", "storage": "store"}),
        ("get_page_tables", "sample.pdf", 3, {"folder": "folder", "storage": "store"}),
        ("get_page_tables", "sample.pdf", 4, {"folder": "folder", "storage": "store"}),
    ]


def test_list_images_uses_all_pages_when_page_list_is_omitted():
    api = DummyApi()

    result = operations.list_images("sample.pdf", folder="folder", storage="store", api=api)

    assert result["pages"] == [1, 2]
    assert [
        (image["page"], image["index"], image.get("id") or image.get("Id"))
        for image in result["images"]
    ] == [
        (1, 1, "img-1-1"),
        (1, 2, "img-1-2"),
        (2, 1, "img-2-1"),
        (2, 2, "img-2-2"),
    ]
    assert api.calls == [
        ("get_pages", "sample.pdf", {"folder": "folder", "storage": "store"}),
        ("get_images", "sample.pdf", 1, {"folder": "folder", "storage": "store"}),
        ("get_images", "sample.pdf", 2, {"folder": "folder", "storage": "store"}),
    ]


def test_list_images_uses_page_list():
    api = DummyApi()

    result = operations.list_images("sample.pdf", "1,2", "folder", "store", api=api)

    assert result["pages"] == [1, 2]
    assert api.calls == [
        ("get_images", "sample.pdf", 1, {"folder": "folder", "storage": "store"}),
        ("get_images", "sample.pdf", 2, {"folder": "folder", "storage": "store"}),
    ]


def test_extract_images_extracts_selected_pages_to_destination_folder():
    api = DummyApi()

    result = operations.extract_images(
        "sample.pdf",
        "1,2",
        "out/images",
        "jpg",
        "folder",
        "store",
        api=api,
    )

    assert result["pages"] == [1, 2]
    assert result["format"] == "jpeg"
    assert api.calls == [
        (
            "put_images_extract_as_jpeg",
            "sample.pdf",
            1,
            {"folder": "folder", "storage": "store", "dest_folder": "out/images"},
        ),
        (
            "put_images_extract_as_jpeg",
            "sample.pdf",
            2,
            {"folder": "folder", "storage": "store", "dest_folder": "out/images"},
        ),
    ]


def test_extract_image_uses_one_based_index_on_page():
    api = DummyApi()

    result = operations.extract_image(
        "sample.pdf",
        1,
        2,
        "out/images",
        "png",
        "folder",
        "store",
        api=api,
    )

    assert result["image_id"] == "img-1-2"
    assert api.calls == [
        ("get_images", "sample.pdf", 1, {"folder": "folder", "storage": "store"}),
        (
            "put_image_extract_as_png",
            "sample.pdf",
            "img-1-2",
            {"folder": "folder", "storage": "store", "dest_folder": "out/images"},
        ),
    ]


def test_extract_image_rejects_out_of_range_index():
    with pytest.raises(operations.AsposePdfToolError, match="out of range"):
        operations.extract_image(
            "sample.pdf",
            1,
            3,
            "out/images",
            api=DummyApi(),
        )
