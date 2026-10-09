import pytest
from typer.testing import CliRunner

from aspose_pdf_cloud_mcp import cli, mcp_server

runner = CliRunner()


@pytest.mark.parametrize(
    "operation,command,extra",
    [
        ("list_attachments", "list-attachments", []),
        ("extract_attachment", "extract-attachment", ["2", "output.txt"]),
        ("extract_attachments", "extract-attachments", ["output"]),
    ],
)
def test_attachment_transport_contract(monkeypatch, operation, command, extra):
    calls = []

    def fake(*args, **kwargs):
        calls.append((tuple(str(arg) for arg in args), kwargs))
        return {"attachments": []}

    monkeypatch.setattr(cli.operations, operation, fake)
    options = ["--folder", "docs", "--storage", "store"]
    if extra:
        options.append("--overwrite")
    result = runner.invoke(cli.app, ["pdf", command, "sample.pdf", *extra, *options])
    args = ["sample.pdf", *extra, "docs", "store"]
    if operation == "extract_attachment":
        args[1] = 2
    response = getattr(mcp_server, operation)(
        *args, **({"overwrite": True} if extra else {})
    )
    assert result.exit_code == 0, result.output
    assert response["ok"] is True
    assert calls[0] == calls[1]


def test_merge_cli_and_mcp_forward_the_same_operation_contract(monkeypatch):
    calls = []

    def merge(inputs, output_name, folder, storage, from_folder):
        calls.append((inputs, output_name, folder, storage, from_folder))
        return {"inputs": inputs, "output_name": output_name}

    monkeypatch.setattr(cli.operations, "merge_pdfs", merge)

    cli_result = runner.invoke(
        cli.app,
        ["pdf", "merge", "merged.pdf", "/a.pdf", "/b.pdf", "--folder", "out"],
    )
    mcp_result = mcp_server.merge_pdfs(
        ["/a.pdf", "/b.pdf"],
        "merged.pdf",
        folder="out",
    )

    assert cli_result.exit_code == 0
    assert mcp_result["ok"] is True
    assert calls == [
        (["/a.pdf", "/b.pdf"], "merged.pdf", "out", None, None),
        (["/a.pdf", "/b.pdf"], "merged.pdf", "out", None, None),
    ]


def test_download_cli_and_mcp_forward_overwrite_consistently(monkeypatch, tmp_path):
    calls = []

    def download(
        remote_path,
        local_path,
        storage_name,
        version_id,
        *,
        overwrite=False,
    ):
        calls.append(
            (remote_path, str(local_path), storage_name, version_id, overwrite)
        )
        return {"local_path": str(local_path)}

    monkeypatch.setattr(cli.operations, "download_file", download)
    output = tmp_path / "sample.pdf"

    cli_result = runner.invoke(
        cli.app,
        ["storage", "download", "/sample.pdf", str(output), "--overwrite"],
    )
    mcp_result = mcp_server.download_file("/sample.pdf", str(output), overwrite=True)

    assert cli_result.exit_code == 0
    assert mcp_result["ok"] is True
    expected = ("/sample.pdf", str(output), None, None, True)
    assert calls == [expected, expected]
