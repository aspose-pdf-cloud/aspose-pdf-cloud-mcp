from pathlib import Path

import pytest
from typer.testing import CliRunner

from aspose_pdf_cloud_mcp import cli
from aspose_pdf_cloud_mcp.skill_installer import (
    SKILL_NAME,
    SkillInstallError,
    default_skill_root,
    install_skill,
)

runner = CliRunner()


def test_default_skill_roots(monkeypatch, tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.chdir(project_dir)

    assert default_skill_root("codex") == tmp_path / ".codex" / "skills"
    assert default_skill_root("claude-code") == tmp_path / ".claude" / "skills"
    assert default_skill_root("claude-code", project=True) == project_dir / ".claude" / "skills"


def test_install_skill_copies_bundled_skill(tmp_path):
    result = install_skill("codex", target_dir=tmp_path)
    skill_dir = tmp_path / SKILL_NAME

    assert result.destination == skill_dir
    assert result.overwritten is False
    assert (skill_dir / "SKILL.md").is_file()
    assert (skill_dir / "references" / "mcp-config.md").is_file()


def test_install_skill_requires_force_for_existing_destination(tmp_path):
    install_skill("codex", target_dir=tmp_path)

    with pytest.raises(SkillInstallError):
        install_skill("codex", target_dir=tmp_path)

    result = install_skill("codex", target_dir=tmp_path, force=True)

    assert result.overwritten is True


def test_cli_skill_install(tmp_path):
    result = runner.invoke(
        cli.app,
        ["skill", "install", "codex", "--target-dir", str(tmp_path)],
    )

    assert result.exit_code == 0
    assert "Installed" in result.output
    assert (tmp_path / SKILL_NAME / "SKILL.md").is_file()
