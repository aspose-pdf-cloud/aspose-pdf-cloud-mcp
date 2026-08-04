from typer.testing import CliRunner

from aspose_pdf_cloud_mcp import cli

runner = CliRunner()


def test_storage_list_json(monkeypatch):
    monkeypatch.setattr(
        cli.operations,
        "list_files",
        lambda path, storage: {"path": path, "storage_name": storage, "items": []},
    )

    result = runner.invoke(cli.app, ["storage", "list", "/", "--storage", "s", "--json"])

    assert result.exit_code == 0
    assert '"path": "/"' in result.output
    assert '"storage_name": "s"' in result.output


def test_auth_status_json(monkeypatch, tmp_path):
    monkeypatch.delenv("ASPOSE_CLIENT_ID", raising=False)
    monkeypatch.delenv("ASPOSE_CLIENT_SECRET", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        'ASPOSE_CLIENT_ID="client-value"\nASPOSE_CLIENT_SECRET="secret-value"\n',
        encoding="utf-8",
    )

    result = runner.invoke(
        cli.app,
        ["auth", "status", "--env-file", str(env_file), "--json"],
    )

    assert result.exit_code == 0
    assert '"configured": true' in result.output
    assert "secret-value" not in result.output


def test_auth_login_writes_env_file(tmp_path):
    env_file = tmp_path / ".env"

    result = runner.invoke(
        cli.app,
        [
            "auth",
            "login",
            "--env-file",
            str(env_file),
            "--client-id",
            "client",
            "--client-secret",
            "secret",
            "--storage",
            "store",
            "--force",
        ],
        input="\n\n",
    )

    assert result.exit_code == 0
    text = env_file.read_text(encoding="utf-8")
    assert 'ASPOSE_CLIENT_ID="client"' in text
    assert 'ASPOSE_CLIENT_SECRET="secret"' in text
    assert 'ASPOSE_STORAGE_NAME="store"' in text


def test_auth_test_json(monkeypatch):
    monkeypatch.setattr(
        cli.operations,
        "test_auth",
        lambda path, storage: {
            "ok": True,
            "path": path,
            "storage_name": storage,
            "item_count": 0,
        },
    )

    result = runner.invoke(
        cli.app,
        ["auth", "test", "--path", "/", "--storage", "store", "--json"],
    )

    assert result.exit_code == 0
    assert '"ok": true' in result.output
    assert '"storage_name": "store"' in result.output


def test_extract_text_writes_output(monkeypatch, tmp_path):
    monkeypatch.setattr(
        cli.operations,
        "extract_text",
        lambda name, folder, storage: {"text": "hello", "raw": {}},
    )
    output = tmp_path / "text.txt"

    result = runner.invoke(
        cli.app,
        ["pdf", "extract-text", "sample.pdf", "--output", str(output)],
    )

    assert result.exit_code == 0
    assert output.read_text(encoding="utf-8") == "hello"


def test_extract_tables_passes_page_list_and_writes_output(monkeypatch, tmp_path):
    calls = []

    def extract_tables(name, pages, folder, storage):
        calls.append((name, pages, folder, storage))
        return {"name": name, "pages": [1, 3], "tables": [{"rows": [["a"]]}]}

    monkeypatch.setattr(cli.operations, "extract_tables", extract_tables)
    output = tmp_path / "tables.json"

    result = runner.invoke(
        cli.app,
        [
            "pdf",
            "extract-tables",
            "sample.pdf",
            "--pages",
            "1,3",
            "--folder",
            "docs",
            "--storage",
            "store",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0
    assert calls == [("sample.pdf", "1,3", "docs", "store")]
    assert '"tables"' in output.read_text(encoding="utf-8")


def test_list_images_passes_page_list_and_writes_output(monkeypatch, tmp_path):
    calls = []

    def list_images(name, pages, folder, storage):
        calls.append((name, pages, folder, storage))
        return {"name": name, "pages": [1, 3], "images": [{"id": "i1"}]}

    monkeypatch.setattr(cli.operations, "list_images", list_images)
    output = tmp_path / "images.json"

    result = runner.invoke(
        cli.app,
        [
            "pdf",
            "list-images",
            "sample.pdf",
            "--pages",
            "1,3",
            "--folder",
            "docs",
            "--storage",
            "store",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0
    assert calls == [("sample.pdf", "1,3", "docs", "store")]
    assert '"images"' in output.read_text(encoding="utf-8")


def test_extract_images_passes_page_list_and_destination(monkeypatch):
    calls = []

    def extract_images(name, pages, dest_folder, image_format, folder, storage):
        calls.append((name, pages, dest_folder, image_format, folder, storage))
        return {"pages": [1, 3], "dest_folder": dest_folder}

    monkeypatch.setattr(cli.operations, "extract_images", extract_images)

    result = runner.invoke(
        cli.app,
        [
            "pdf",
            "extract-images",
            "sample.pdf",
            "out/images",
            "--pages",
            "1,3",
            "--format",
            "jpg",
            "--folder",
            "docs",
            "--storage",
            "store",
        ],
    )

    assert result.exit_code == 0
    assert calls == [("sample.pdf", "1,3", "out/images", "jpg", "docs", "store")]
    assert "Extracted images from 2 page(s)" in result.output


def test_extract_image_passes_page_index_and_destination(monkeypatch):
    calls = []

    def extract_image(name, page, index, dest_folder, image_format, folder, storage):
        calls.append((name, page, index, dest_folder, image_format, folder, storage))
        return {"page": page, "index": index, "dest_folder": dest_folder}

    monkeypatch.setattr(cli.operations, "extract_image", extract_image)

    result = runner.invoke(
        cli.app,
        [
            "pdf",
            "extract-image",
            "sample.pdf",
            "1",
            "2",
            "out/images",
            "--format",
            "png",
            "--folder",
            "docs",
            "--storage",
            "store",
        ],
    )

    assert result.exit_code == 0
    assert calls == [("sample.pdf", 1, 2, "out/images", "png", "docs", "store")]
    assert "Extracted image" in result.output


def test_merge_accepts_multiple_input_files(monkeypatch):
    calls = []

    def merge_pdfs(inputs, output_name, folder, storage, from_folder):
        calls.append((inputs, output_name, folder, storage, from_folder))
        return {"inputs": inputs, "output_name": output_name}

    monkeypatch.setattr(cli.operations, "merge_pdfs", merge_pdfs)

    result = runner.invoke(
        cli.app,
        ["pdf", "merge", "merged.pdf", "/a.pdf", "/b.pdf", "/c.pdf", "--storage", "store"],
    )

    assert result.exit_code == 0
    assert calls == [(["/a.pdf", "/b.pdf", "/c.pdf"], "merged.pdf", None, "store", None)]
    assert "Merged 3 PDFs into" in result.output


def test_merge_accepts_from_folder(monkeypatch):
    calls = []

    def merge_pdfs(inputs, output_name, folder, storage, from_folder):
        calls.append((inputs, output_name, folder, storage, from_folder))
        return {"inputs": ["/batch/a.pdf", "/batch/b.pdf"], "output_name": output_name}

    monkeypatch.setattr(cli.operations, "merge_pdfs", merge_pdfs)

    result = runner.invoke(
        cli.app,
        ["pdf", "merge", "merged.pdf", "--from-folder", "/batch", "--folder", "out"],
    )

    assert result.exit_code == 0
    assert calls == [(None, "merged.pdf", "out", None, "/batch")]
    assert "Merged 2 PDFs into" in result.output


def test_split_defaults_to_single_pages(monkeypatch):
    calls = []

    def split_pdf(name, ranges, folder, storage):
        calls.append((name, ranges, folder, storage))
        return {
            "name": name,
            "mode": "pages",
            "ranges": None,
            "documents": [{"title": "sample_1.pdf"}, {"title": "sample_2.pdf"}],
        }

    monkeypatch.setattr(cli.operations, "split_pdf", split_pdf)

    result = runner.invoke(
        cli.app,
        ["pdf", "split", "sample.pdf", "--folder", "docs", "--storage", "store"],
    )

    assert result.exit_code == 0
    assert calls == [("sample.pdf", None, "docs", "store")]
    assert "Split sample.pdf into 2 page document(s)" in result.output


def test_split_accepts_ranges_and_json(monkeypatch):
    calls = []

    def split_pdf(name, ranges, folder, storage):
        calls.append((name, ranges, folder, storage))
        return {
            "name": name,
            "mode": "ranges",
            "ranges": [(1, 3), (4, 4), (5, 8)],
            "documents": [],
        }

    monkeypatch.setattr(cli.operations, "split_pdf", split_pdf)

    result = runner.invoke(
        cli.app,
        [
            "pdf",
            "split",
            "sample.pdf",
            "--ranges",
            "1-3,4,5-8",
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert calls == [("sample.pdf", "1-3,4,5-8", None, None)]
    assert '"mode": "ranges"' in result.output


def test_pdfa_versions_json(monkeypatch):
    monkeypatch.setattr(
        cli.operations,
        "list_pdfa_versions",
        lambda: {
            "versions": [{"value": "PDFA1B", "label": "PDF/A-1B"}],
            "default": "PDFA1B",
        },
    )

    result = runner.invoke(cli.app, ["pdf", "pdfa-versions", "--json"])

    assert result.exit_code == 0
    assert '"value": "PDFA1B"' in result.output
    assert '"label": "PDF/A-1B"' in result.output


def test_convert_pdfa_passes_version_and_paths(monkeypatch):
    calls = []

    def convert_pdf_to_pdfa(name, out_path, pdfa_version, folder, storage):
        calls.append((name, out_path, pdfa_version, folder, storage))
        return {
            "name": name,
            "out_path": out_path,
            "pdfa_version": "PDFA3B",
        }

    monkeypatch.setattr(cli.operations, "convert_pdf_to_pdfa", convert_pdf_to_pdfa)

    result = runner.invoke(
        cli.app,
        [
            "pdf",
            "convert-pdfa",
            "sample.pdf",
            "/archive/sample-pdfa.pdf",
            "--pdfa-version",
            "PDF/A-3B",
            "--folder",
            "docs",
            "--storage",
            "store",
        ],
    )

    assert result.exit_code == 0
    assert calls == [("sample.pdf", "/archive/sample-pdfa.pdf", "PDF/A-3B", "docs", "store")]
    assert "Converted sample.pdf to PDFA3B" in result.output


def test_convert_pdfa_accepts_type_alias(monkeypatch):
    calls = []

    def convert_pdf_to_pdfa(name, out_path, pdfa_version, folder, storage):
        calls.append((name, out_path, pdfa_version, folder, storage))
        return {
            "name": name,
            "out_path": out_path,
            "pdfa_version": "PDFA1A",
        }

    monkeypatch.setattr(cli.operations, "convert_pdf_to_pdfa", convert_pdf_to_pdfa)

    result = runner.invoke(
        cli.app,
        [
            "pdf",
            "convert-pdfa",
            "sample.pdf",
            "/archive/sample-pdfa.pdf",
            "--type",
            "1a",
        ],
    )

    assert result.exit_code == 0
    assert calls == [("sample.pdf", "/archive/sample-pdfa.pdf", "1a", None, None)]


def test_cli_errors_are_user_friendly(monkeypatch):
    def fail(path, storage):
        raise cli.operations.AsposePdfToolError("boom")

    monkeypatch.setattr(cli.operations, "list_files", fail)

    result = runner.invoke(cli.app, ["storage", "list", "/"])

    assert result.exit_code == 1
    assert "Error [operation_error]: boom" in result.output


def test_extract_text_requires_overwrite_for_existing_output(monkeypatch, tmp_path):
    output = tmp_path / "text.txt"
    output.write_text("original", encoding="utf-8")
    monkeypatch.setattr(
        cli.operations,
        "extract_text",
        lambda name, folder, storage: {"text": "replacement"},
    )

    refused = runner.invoke(cli.app, ["pdf", "extract-text", "sample.pdf", "--output", str(output)])
    replaced = runner.invoke(
        cli.app,
        ["pdf", "extract-text", "sample.pdf", "--output", str(output), "--overwrite"],
    )

    assert refused.exit_code == 1
    assert "Error [conflict]" in refused.output
    assert replaced.exit_code == 0
    assert output.read_text(encoding="utf-8") == "replacement"
