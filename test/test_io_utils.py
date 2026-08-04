import pytest

from aspose_pdf_cloud_mcp.errors import AsposePdfToolError
from aspose_pdf_cloud_mcp.io_utils import atomic_write, atomic_write_text


def test_atomic_write_refuses_existing_output_without_overwrite(tmp_path):
    destination = tmp_path / "result.txt"
    destination.write_text("original", encoding="utf-8")

    with pytest.raises(AsposePdfToolError) as captured:
        atomic_write_text(destination, "replacement")

    assert captured.value.code == "conflict"
    assert destination.read_text(encoding="utf-8") == "original"


def test_atomic_write_replaces_existing_output_when_allowed(tmp_path):
    destination = tmp_path / "result.txt"
    destination.write_text("original", encoding="utf-8")

    atomic_write_text(destination, "replacement", overwrite=True)

    assert destination.read_text(encoding="utf-8") == "replacement"


def test_atomic_write_failure_preserves_existing_output(tmp_path):
    destination = tmp_path / "result.txt"
    destination.write_text("original", encoding="utf-8")

    def fail_after_write(output):
        output.write(b"partial")
        raise OSError("disk failure")

    with pytest.raises(AsposePdfToolError) as captured:
        atomic_write(destination, fail_after_write, overwrite=True)

    assert captured.value.code == "io_error"
    assert destination.read_text(encoding="utf-8") == "original"
    assert list(tmp_path.glob("*.tmp")) == []
