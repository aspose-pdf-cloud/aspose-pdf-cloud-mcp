# Agent Skill Installation

This package ships an `aspose-pdf-cloud-mcp` skill that teaches Codex or Claude
Code how to use the Aspose.PDF Cloud MCP server safely.

Install the Python package:

```powershell
python -m pip install aspose-pdf-cloud-mcp
```

## Codex

Install the bundled skill into your personal Codex skills directory:

```powershell
aspose-pdf-cloud-cli skill install codex
```

Default destination:

```text
~/.codex/skills/aspose-pdf-cloud-mcp
```

If a skill already exists, replace it with:

```powershell
aspose-pdf-cloud-cli skill install codex --force
```

## Claude Code

Install the bundled skill globally for Claude Code:

```powershell
aspose-pdf-cloud-cli skill install claude-code
```

Default destination:

```text
~/.claude/skills/aspose-pdf-cloud-mcp
```

Install it only for the current project:

```powershell
aspose-pdf-cloud-cli skill install claude-code --project
```

Project destination:

```text
./.claude/skills/aspose-pdf-cloud-mcp
```

Claude Code can load skills from project `.claude/skills/<name>/` or
personal `~/.claude/skills/<name>/` folders.

## Custom Destination

Install into any skills' directory:

```powershell
aspose-pdf-cloud-cli skill install codex --target-dir C:\path\to\skills
aspose-pdf-cloud-cli skill install claude-code --target-dir C:\path\to\skills
```

The installer creates:

```text
<target-dir>/aspose-pdf-cloud-mcp/SKILL.md
<target-dir>/aspose-pdf-cloud-mcp/references/
<target-dir>/aspose-pdf-cloud-mcp/agents/openai.yaml
```

## Verify

Check the installed skill:

```powershell
Get-ChildItem ~/.codex/skills/aspose-pdf-cloud-mcp
Get-ChildItem ~/.claude/skills/aspose-pdf-cloud-mcp
```

Restart the agent session if the skill does not appear immediately.
