"""Smoke-test the installed wheel without credentials or cloud calls."""

from importlib.metadata import version
from importlib.resources import files
from pathlib import Path
import subprocess
import sys
import tempfile

import aspose_pdf_cloud_mcp
from aspose_pdf_cloud_mcp.mcp_server import mcp
from aspose_pdf_cloud_mcp.skill_installer import install_skill


def main() -> None:
    assert aspose_pdf_cloud_mcp.__version__ == version("aspose-pdf-cloud-mcp")
    assert files("aspose_pdf_cloud_mcp").joinpath("py.typed").is_file()
    assert mcp is not None
    for command in ("apdf", "aspose-pdf-cloud-cli"):
        executable = Path(sys.executable).parent / (command + (".exe" if sys.platform == "win32" else ""))
        subprocess.run([str(executable), "--help"], check=True, capture_output=True, text=True, timeout=10)
    with tempfile.TemporaryDirectory() as directory:
        result = install_skill("codex", target_dir=directory)
        assert (result.destination / "SKILL.md").is_file()
        assert (result.destination / "references" / "setup.md").is_file()
        assert (result.destination / "agents" / "openai.yaml").is_file()
    assert Path(aspose_pdf_cloud_mcp.__file__).is_file()
    print(f"Installed wheel smoke test passed: {aspose_pdf_cloud_mcp.__version__}")


if __name__ == "__main__":
    main()
