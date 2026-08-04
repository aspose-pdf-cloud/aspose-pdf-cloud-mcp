"""Install the bundled Aspose.PDF Cloud MCP agent skill."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

from .errors import AsposePdfError

SKILL_NAME = "aspose-pdf-cloud-mcp"


class SkillInstallError(AsposePdfError):
    """Raised when bundled skill installation fails."""

    default_code = "skill_install_error"


@dataclass(frozen=True)
class SkillInstallResult:
    client: str
    destination: Path
    overwritten: bool


def _bundled_skill_path() -> Path:
    traversable = resources.files("aspose_pdf_cloud_mcp") / "resources" / "skills" / SKILL_NAME
    try:
        path = Path(str(traversable))
    except TypeError as exc:
        raise SkillInstallError("Unable to resolve bundled skill path.") from exc

    if not path.is_dir():
        raise SkillInstallError(f"Bundled skill not found: {path}")
    return path


def default_skill_root(client: str, project: bool = False) -> Path:
    """Return the default skill root for Codex or Claude Code."""

    normalized = client.strip().lower()
    if normalized == "codex":
        return Path.home() / ".codex" / "skills"
    if normalized in {"claude", "claude-code", "claudecode"}:
        if project:
            return Path.cwd() / ".claude" / "skills"
        return Path.home() / ".claude" / "skills"
    raise SkillInstallError("Client must be 'codex' or 'claude-code'.")


def install_skill(
    client: str,
    *,
    target_dir: str | Path | None = None,
    project: bool = False,
    force: bool = False,
) -> SkillInstallResult:
    """Install the bundled skill into a client skill directory."""

    root = Path(target_dir) if target_dir is not None else default_skill_root(client, project)
    destination = root / SKILL_NAME
    source = _bundled_skill_path()

    overwritten = destination.exists()
    if overwritten:
        if not force:
            raise SkillInstallError(
                f"Skill already exists at {destination}. Re-run with --force to replace it."
            )
        if not destination.is_dir():
            raise SkillInstallError(f"Destination exists and is not a directory: {destination}")
        shutil.rmtree(destination)

    root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)

    return SkillInstallResult(
        client=client,
        destination=destination,
        overwritten=overwritten,
    )
