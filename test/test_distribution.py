"""Tests for the pre-publish artifact gate, using synthetic distributions."""

from __future__ import annotations

import io
from pathlib import Path
import runpy
import sys
import tarfile
import zipfile

import pytest


ROOT = Path(__file__).resolve().parents[1]


def make_distributions(directory: Path, *, version: str = "1.2.3", omit: str | None = None) -> None:
    package = "aspose_pdf_cloud_mcp"
    files = {f"{package}/__init__.py", f"{package}/_version.py", f"{package}/py.typed"}
    files.update(
        path.relative_to(ROOT / "src").as_posix()
        for path in (ROOT / "src" / package / "resources").rglob("*")
        if path.is_file() and path.suffix in {".md", ".yaml"}
    )
    metadata = f"Metadata-Version: 2.4\nName: aspose-pdf-cloud-mcp\nVersion: {version}\n".encode()
    with zipfile.ZipFile(directory / "package.whl", "w") as archive:
        for name in files - {omit}:
            archive.writestr(name, "placeholder")
        archive.writestr(f"{package}-{version}.dist-info/METADATA", metadata)
        archive.writestr(f"{package}-{version}.dist-info/licenses/LICENSE", "MIT")
    with tarfile.open(directory / "package.tar.gz", "w:gz") as archive:
        for name in {"pyproject.toml", "README.md", "LICENSE", "PKG-INFO"} | {f"src/{f}" for f in files}:
            data = metadata if name == "PKG-INFO" else b"placeholder"
            info = tarfile.TarInfo(f"package/{name}")
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))


def check(directory: Path, monkeypatch: pytest.MonkeyPatch, tag: str = "v1.2.3") -> None:
    monkeypatch.chdir(ROOT)
    monkeypatch.setattr(sys, "argv", ["check_distribution.py", str(directory), "--release-tag", tag])
    runpy.run_path(str(ROOT / "scripts" / "check_distribution.py"), run_name="__main__")


def test_release_distributions_pass(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    make_distributions(tmp_path)
    check(tmp_path, monkeypatch)


@pytest.mark.parametrize("tag", ["v1.2.4", "v1.2.3rc1", "v01.2.3", "1.2.3"])
def test_bad_release_tags_are_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, tag: str) -> None:
    make_distributions(tmp_path)
    with pytest.raises(SystemExit, match="(tags must|does not match)"):
        check(tmp_path, monkeypatch, tag)


def test_missing_bundled_skill_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    make_distributions(tmp_path, omit="aspose_pdf_cloud_mcp/resources/skills/aspose-pdf-cloud-mcp/SKILL.md")
    with pytest.raises(SystemExit, match="missing required files"):
        check(tmp_path, monkeypatch)


def test_local_version_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    make_distributions(tmp_path, version="1.2.3+dirty")
    with pytest.raises(SystemExit, match="does not match"):
        check(tmp_path, monkeypatch)


def test_credentials_in_wheel_are_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    make_distributions(tmp_path)
    with zipfile.ZipFile(tmp_path / "package.whl", "a") as archive:
        archive.writestr(".env", "placeholder")
    with pytest.raises(SystemExit, match="Private or generated file"):
        check(tmp_path, monkeypatch)
