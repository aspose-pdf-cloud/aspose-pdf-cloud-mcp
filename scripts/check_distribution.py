"""Verify release metadata and required files in the wheel and source archive."""

from __future__ import annotations

import argparse
from email.parser import BytesParser
from pathlib import Path
import re
import tarfile
import zipfile


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--release-tag")
    args = parser.parse_args()
    wheels = list(args.directory.glob("*.whl"))
    sdists = list(args.directory.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise SystemExit("Expected exactly one wheel and one source distribution.")

    package = "aspose_pdf_cloud_mcp"
    required = {f"{package}/__init__.py", f"{package}/_version.py", f"{package}/py.typed"}
    resources = Path("src") / package / "resources"
    required.update(
        str(path.relative_to(Path("src"))).replace("\\", "/")
        for path in resources.rglob("*")
        if path.is_file() and path.suffix in {".md", ".yaml"}
    )
    with zipfile.ZipFile(wheels[0]) as archive:
        names = set(archive.namelist())
        reject_private_files(names)
        missing = required - names
        if missing:
            raise SystemExit(f"Wheel is missing required files: {sorted(missing)}")
        metadata_paths = [name for name in names if name.endswith(".dist-info/METADATA")]
        if len(metadata_paths) != 1:
            raise SystemExit("Expected exactly one wheel metadata file.")
        metadata = BytesParser().parsebytes(archive.read(metadata_paths[0]))
        if not any(name.endswith(".dist-info/licenses/LICENSE") for name in names):
            raise SystemExit("Wheel is missing the license.")

    with tarfile.open(sdists[0], "r:gz") as archive:
        members = archive.getmembers()
        names = {member.name.split("/", 1)[-1] for member in members}
        reject_private_files(names)
        required_sdist = {"pyproject.toml", "README.md", "LICENSE", "PKG-INFO"}
        required_sdist.update(f"src/{name}" for name in required)
        if missing := required_sdist - names:
            raise SystemExit(f"Source distribution is missing: {sorted(missing)}")
        pkg_info = next(member for member in members if member.name.split("/", 1)[-1] == "PKG-INFO")
        stream = archive.extractfile(pkg_info)
        if stream is None:
            raise SystemExit("Cannot read source distribution metadata.")
        source_metadata = BytesParser().parsebytes(stream.read())

    if metadata["Name"] != "aspose-pdf-cloud-mcp" or source_metadata["Name"] != metadata["Name"]:
        raise SystemExit("Unexpected distribution name.")
    version = metadata["Version"]
    if source_metadata["Version"] != version:
        raise SystemExit("Wheel and source distribution versions differ.")
    if args.release_tag:
        if not re.fullmatch(r"v(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", args.release_tag):
            raise SystemExit("Release tags must use vX.Y.Z with no prerelease or local suffix.")
        if version != args.release_tag[1:]:
            raise SystemExit(f"Tag {args.release_tag} does not match package version {version}.")
    print(f"Verified wheel and source distribution: {metadata['Name']} {version}")


def reject_private_files(names: set[str]) -> None:
    for name in names:
        parts = name.split("/")
        if any(
            part in {".git", ".venv", "__pycache__"}
            or (part.startswith(".env") and part != ".env.example")
            for part in parts
        ):
            raise SystemExit(f"Private or generated file included in distribution: {name}")


if __name__ == "__main__":
    main()
