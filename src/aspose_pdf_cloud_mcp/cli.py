"""Command-line interface for Aspose.PDF tools."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Annotated, Never, TypeVar

import typer
from rich.console import Console
from rich.table import Table

from . import operations
from .config import ConfigError, get_auth_status, write_auth_env_file
from .errors import error_payload
from .skill_installer import SkillInstallError, install_skill

app = typer.Typer(help="Aspose.PDF CLI tools.")
auth_app = typer.Typer(help="Credential setup and validation.")
storage_app = typer.Typer(help="Cloud storage operations.")
pdf_app = typer.Typer(help="PDF operations.")
mcp_app = typer.Typer(help="MCP server commands.")
skill_app = typer.Typer(help="Install bundled agent skills.")
app.add_typer(auth_app, name="auth")
app.add_typer(storage_app, name="storage")
app.add_typer(pdf_app, name="pdf")
app.add_typer(mcp_app, name="mcp")
app.add_typer(skill_app, name="skill")

console = Console()
T = TypeVar("T")


def _json(data: object) -> None:
    console.print_json(json.dumps(data, ensure_ascii=False))


def _handle_error(exc: Exception) -> Never:
    error = error_payload(exc)
    typer.echo(f"Error [{error['code']}]: {error['message']}", err=True)
    raise typer.Exit(code=1) from exc


def _run(action: Callable[[], T]) -> T:
    try:
        return action()
    except (operations.AsposePdfToolError, ConfigError) as exc:
        _handle_error(exc)


@auth_app.command("status")
def auth_status(
        env_file: Annotated[
            Path | None,
            typer.Option("--env-file", help="Local .env file to inspect."),
        ] = Path(".env"),
        as_json: Annotated[bool, typer.Option("--json", help="Emit JSON output.")] = False,
) -> None:
    """Show redacted Aspose.PDF credential configuration status."""

    status = get_auth_status(env_file)
    if as_json:
        _json(status)
        return

    console.print(
        "[green]Configured[/green]"
        if status["configured"]
        else "[yellow]Missing required credentials[/yellow]"
    )
    table = Table(title=f"Auth status: {status['env_file'] or 'environment only'}")
    table.add_column("Setting")
    table.add_column("Source")
    table.add_column("Value")

    settings = status["settings"]
    if isinstance(settings, dict):
        for key, details in settings.items():
            if not isinstance(details, dict):
                continue
            table.add_row(
                key,
                str(details.get("source") or "missing"),
                str(details.get("value") or ""),
            )
    console.print(table)


@auth_app.command("login")
def auth_login(
        env_file: Annotated[
            Path,
            typer.Option("--env-file", help="Local .env file to write."),
        ] = Path(".env"),
        client_id: Annotated[
            str | None,
            typer.Option("--client-id", help="Aspose Cloud client ID."),
        ] = None,
        client_secret: Annotated[
            str | None,
            typer.Option("--client-secret", help="Aspose Cloud client secret."),
        ] = None,
        storage_name: Annotated[
            str | None,
            typer.Option("--storage", help="Default Aspose storage name."),
        ] = None,
        base_url: Annotated[
            str | None,
            typer.Option("--base-url", help="Alternate Aspose PDF Cloud base URL."),
        ] = None,
        self_host: Annotated[
            bool,
            typer.Option("--self-host/--no-self-host", help="Use self-hosted Aspose PDF Cloud."),
        ] = False,
        force: Annotated[
            bool,
            typer.Option("--force", help="Overwrite existing Aspose.PDF values in the env file."),
        ] = False,
) -> None:
    """Save Aspose.PDF credentials to a local .env file."""

    status = get_auth_status(env_file)
    settings = status.get("settings", {})
    has_existing_file_values = isinstance(settings, dict) and any(
        isinstance(details, dict) and details.get("source") == "env_file"
        for details in settings.values()
    )
    if has_existing_file_values and not force:
        typer.confirm(
            f"{env_file} already contains Aspose.PDF settings. Overwrite them?",
            abort=True,
        )

    prompt_optional = client_id is None or client_secret is None
    if client_id is None:
        client_id = typer.prompt("Aspose client ID")
    if client_secret is None:
        client_secret = typer.prompt("Aspose client secret", hide_input=True)
    if prompt_optional and storage_name is None:
        storage_name = typer.prompt(
            "Default storage name (optional)",
            default="",
            show_default=False,
        )
    if prompt_optional and base_url is None:
        base_url = typer.prompt(
            "Base URL (optional)",
            default="",
            show_default=False,
        )

    result = _run(
        lambda: write_auth_env_file(
            env_file,
            {
                "ASPOSE_CLIENT_ID": client_id,
                "ASPOSE_CLIENT_SECRET": client_secret,
                "ASPOSE_STORAGE_NAME": storage_name,
                "ASPOSE_BASE_URL": base_url,
                "ASPOSE_SELF_HOST": self_host,
            },
        )
    )
    console.print(f"Saved Aspose.PDF credentials to [bold]{result}[/bold].")


@auth_app.command("test")
def auth_test(
        path: Annotated[
            str,
            typer.Option("--path", help="Storage folder path to list during validation."),
        ] = "/",
        storage: Annotated[str | None, typer.Option("--storage", help="Storage name.")] = None,
        as_json: Annotated[bool, typer.Option("--json", help="Emit JSON output.")] = False,
) -> None:
    """Validate Aspose.PDF credentials with a harmless storage API call."""

    result = _run(lambda: operations.test_auth(path, storage))
    if as_json:
        _json(result)
        return
    console.print(
        "[green]Aspose.PDF credentials are valid.[/green] "
        f"Listed [bold]{result['path']}[/bold]"
        + (f" in storage [bold]{result['storage_name']}[/bold]." if result["storage_name"] else ".")
    )


@storage_app.command("list")
def list_storage_files(
        path: Annotated[str, typer.Argument(help="Folder path in Aspose storage.")],
        storage: Annotated[str | None, typer.Option("--storage", help="Storage name.")] = None,
        as_json: Annotated[bool, typer.Option("--json", help="Emit JSON output.")] = False,
) -> None:
    """List files and folders in Aspose storage."""

    result = _run(lambda: operations.list_files(path, storage))
    if as_json:
        _json(result)
        return

    table = Table(title=f"Storage: {storage or 'default'}  Path: {path}")
    table.add_column("Name")
    table.add_column("Path")
    table.add_column("Size", justify="right")
    table.add_column("Folder")

    items = result.get("items", {})
    values = items.get("value") or items.get("Value") or items.get("files") or items
    if isinstance(values, dict):
        values = values.get("value") or values.get("Value") or []
    if not isinstance(values, list):
        values = []

    for item in values:
        if not isinstance(item, dict):
            continue
        table.add_row(
            str(item.get("name") or item.get("Name") or ""),
            str(item.get("path") or item.get("Path") or ""),
            str(item.get("size") or item.get("Size") or ""),
            str(item.get("is_folder") or item.get("IsFolder") or False),
        )
    console.print(table)


@storage_app.command("upload")
def upload_storage_file(
        local_path: Annotated[Path, typer.Argument(help="Local file to upload.")],
        remote_path: Annotated[str, typer.Argument(help="Remote storage path.")],
        storage: Annotated[str | None, typer.Option("--storage", help="Storage name.")] = None,
) -> None:
    """Upload a local file to Aspose storage."""

    result = _run(lambda: operations.upload_file(local_path, remote_path, storage))
    console.print(f"Uploaded [bold]{result['local_path']}[/bold] to [bold]{remote_path}[/bold].")


@storage_app.command("download")
def download_storage_file(
        remote_path: Annotated[str, typer.Argument(help="Remote storage path.")],
        local_path: Annotated[Path, typer.Argument(help="Local output path.")],
        storage: Annotated[str | None, typer.Option("--storage", help="Storage name.")] = None,
        version_id: Annotated[str | None, typer.Option("--version-id", help="File version ID.")] = None,
        overwrite: Annotated[
            bool,
            typer.Option("--overwrite", help="Replace an existing local output file."),
        ] = False,
) -> None:
    """Download a file from Aspose storage."""

    result = _run(
        lambda: operations.download_file(
            remote_path,
            local_path,
            storage,
            version_id,
            overwrite=overwrite,
        )
    )
    console.print(f"Downloaded [bold]{remote_path}[/bold] to [bold]{result['local_path']}[/bold].")


@pdf_app.command("merge")
def merge_pdf_files(
        output_name: Annotated[str, typer.Argument(help="Output PDF name.")],
        inputs: Annotated[
            list[str] | None,
            typer.Argument(help="Input PDF paths in storage."),
        ] = None,
        folder: Annotated[str | None, typer.Option("--folder", help="Output folder.")] = None,
        storage: Annotated[str | None, typer.Option("--storage", help="Storage name.")] = None,
        from_folder: Annotated[
            str | None,
            typer.Option("--from-folder", help="Merge all PDF files from this storage folder."),
        ] = None,
) -> None:
    """Merge PDF files already present in Aspose storage."""

    result = _run(lambda: operations.merge_pdfs(inputs, output_name, folder, storage, from_folder))
    console.print(
        f"Merged [bold]{len(result['inputs'])}[/bold] PDFs into "
        f"[bold]{result['output_name']}[/bold]."
    )


@pdf_app.command("split")
def split_pdf_document(
        name: Annotated[str, typer.Argument(help="PDF name/path in storage.")],
        ranges: Annotated[
            str | None,
            typer.Option("--ranges", help="Segments to create, for example 1-3,4,5-8."),
        ] = None,
        folder: Annotated[str | None, typer.Option("--folder", help="Document folder.")] = None,
        storage: Annotated[str | None, typer.Option("--storage", help="Storage name.")] = None,
        as_json: Annotated[bool, typer.Option("--json", help="Emit JSON output.")] = False,
) -> None:
    """Split a PDF into single pages or page-range segments."""

    result = _run(lambda: operations.split_pdf(name, ranges, folder, storage))
    if as_json:
        _json(result)
        return

    segment_label = "segment(s)" if result["mode"] == "ranges" else "page document(s)"
    count = len(result["ranges"] or result["documents"])
    console.print(f"Split [bold]{result['name']}[/bold] into [bold]{count}[/bold] {segment_label}.")


@pdf_app.command("pdfa-versions")
def list_pdfa_versions(
        as_json: Annotated[bool, typer.Option("--json", help="Emit JSON output.")] = False,
) -> None:
    """List PDF/A conversion targets supported by the installed SDK."""

    result = operations.list_pdfa_versions()
    if as_json:
        _json(result)
        return

    table = Table(title="Supported PDF/A conversion targets")
    table.add_column("Value")
    table.add_column("Label")
    table.add_column("Default")
    for item in result["versions"]:
        is_default = item["value"] == result["default"]
        table.add_row(item["value"], item["label"], "yes" if is_default else "")
    console.print(table)


@pdf_app.command("convert-pdfa")
def convert_pdf_to_pdfa(
        name: Annotated[str, typer.Argument(help="PDF name/path in storage.")],
        out_path: Annotated[str, typer.Argument(help="Output PDF/A path in storage.")],
        pdfa_version: Annotated[
            str,
            typer.Option(
                "--pdfa-version",
                "--type",
                help="PDF/A type/version. Run `pdf pdfa-versions` to list supported values.",
            ),
        ] = "PDF/A-1B",
        folder: Annotated[str | None, typer.Option("--folder", help="Document folder.")] = None,
        storage: Annotated[str | None, typer.Option("--storage", help="Storage name.")] = None,
        as_json: Annotated[bool, typer.Option("--json", help="Emit JSON output.")] = False,
) -> None:
    """Convert a PDF in Aspose storage to a selected PDF/A version."""

    result = _run(
        lambda: operations.convert_pdf_to_pdfa(
            name,
            out_path,
            pdfa_version,
            folder,
            storage,
        )
    )
    if as_json:
        _json(result)
        return

    console.print(
        f"Converted [bold]{result['name']}[/bold] to [bold]{result['pdfa_version']}[/bold] "
        f"at [bold]{result['out_path']}[/bold]."
    )


@pdf_app.command("extract-text")
def extract_pdf_text(
        name: Annotated[str, typer.Argument(help="PDF name/path in storage.")],
        folder: Annotated[str | None, typer.Option("--folder", help="Document folder.")] = None,
        storage: Annotated[str | None, typer.Option("--storage", help="Storage name.")] = None,
        as_json: Annotated[bool, typer.Option("--json", help="Emit JSON output.")] = False,
        output: Annotated[
            Path | None, typer.Option("--output", help="Write plain text to a file.")
        ] = None,
        overwrite: Annotated[
            bool,
            typer.Option("--overwrite", help="Replace an existing local output file."),
        ] = False,
) -> None:
    """Extract text from a PDF in Aspose storage."""

    result = _run(lambda: operations.extract_text(name, folder, storage))
    if output:
        _run(lambda: operations.write_text_output(output, result["text"], overwrite=overwrite))

    if as_json:
        _json(result)
    elif output:
        console.print(f"Wrote extracted text to [bold]{output}[/bold].")
    else:
        console.print(result["text"])


@pdf_app.command("extract-tables")
def extract_pdf_tables(
        name: Annotated[str, typer.Argument(help="PDF name/path in storage.")],
        pages: Annotated[
            str | None,
            typer.Option("--pages", help="Pages to scan, for example 1,3,4-7,10."),
        ] = None,
        folder: Annotated[str | None, typer.Option("--folder", help="Document folder.")] = None,
        storage: Annotated[str | None, typer.Option("--storage", help="Storage name.")] = None,
        output: Annotated[
            Path | None,
            typer.Option("--output", help="Write extracted table data as JSON."),
        ] = None,
        overwrite: Annotated[
            bool,
            typer.Option("--overwrite", help="Replace an existing local output file."),
        ] = False,
) -> None:
    """Extract tables from a PDF in Aspose storage."""

    result = _run(lambda: operations.extract_tables(name, pages, folder, storage))
    if output:
        _run(lambda: operations.write_json_output(output, result, overwrite=overwrite))
        console.print(f"Wrote extracted tables to [bold]{output}[/bold].")
        return

    _json(result)


@pdf_app.command("list-images")
def list_pdf_images(
        name: Annotated[str, typer.Argument(help="PDF name/path in storage.")],
        pages: Annotated[
            str | None,
            typer.Option("--pages", help="Pages to scan, for example 1,3,4-7,10."),
        ] = None,
        folder: Annotated[str | None, typer.Option("--folder", help="Document folder.")] = None,
        storage: Annotated[str | None, typer.Option("--storage", help="Storage name.")] = None,
        output: Annotated[
            Path | None,
            typer.Option("--output", help="Write image metadata as JSON."),
        ] = None,
        overwrite: Annotated[
            bool,
            typer.Option("--overwrite", help="Replace an existing local output file."),
        ] = False,
) -> None:
    """List images in a PDF in Aspose storage."""

    result = _run(lambda: operations.list_images(name, pages, folder, storage))
    if output:
        _run(lambda: operations.write_json_output(output, result, overwrite=overwrite))
        console.print(f"Wrote image metadata to [bold]{output}[/bold].")
        return

    _json(result)


@pdf_app.command("extract-images")
def extract_pdf_images(
        name: Annotated[str, typer.Argument(help="PDF name/path in storage.")],
        dest_folder: Annotated[
            str,
            typer.Argument(help="Aspose storage folder to receive extracted images."),
        ],
        pages: Annotated[
            str | None,
            typer.Option("--pages", help="Pages to extract, for example 1,3,4-7,10."),
        ] = None,
        image_format: Annotated[
            str,
            typer.Option("--format", help="Output format: gif, jpeg, jpg, png, or tiff."),
        ] = "png",
        folder: Annotated[str | None, typer.Option("--folder", help="Document folder.")] = None,
        storage: Annotated[str | None, typer.Option("--storage", help="Storage name.")] = None,
) -> None:
    """Extract all images from a PDF or selected pages."""

    result = _run(
        lambda: operations.extract_images(name, pages, dest_folder, image_format, folder, storage)
    )
    console.print(
        f"Extracted images from [bold]{len(result['pages'])}[/bold] page(s) "
        f"to [bold]{dest_folder}[/bold]."
    )


@pdf_app.command("extract-image")
def extract_pdf_image(
        name: Annotated[str, typer.Argument(help="PDF name/path in storage.")],
        page: Annotated[int, typer.Argument(help="One-based page number.")],
        index: Annotated[int, typer.Argument(help="One-based image index on the page.")],
        dest_folder: Annotated[
            str,
            typer.Argument(help="Aspose storage folder to receive the extracted image."),
        ],
        image_format: Annotated[
            str,
            typer.Option("--format", help="Output format: gif, jpeg, jpg, png, or tiff."),
        ] = "png",
        folder: Annotated[str | None, typer.Option("--folder", help="Document folder.")] = None,
        storage: Annotated[str | None, typer.Option("--storage", help="Storage name.")] = None,
) -> None:
    """Extract one image by its one-based index on a page."""

    result = _run(
        lambda: operations.extract_image(
            name,
            page,
            index,
            dest_folder,
            image_format,
            folder,
            storage,
        )
    )
    console.print(
        f"Extracted image [bold]{result['index']}[/bold] from page "
        f"[bold]{result['page']}[/bold] to [bold]{dest_folder}[/bold]."
    )


@mcp_app.command("serve")
def serve_mcp() -> None:
    """Run the MCP server over stdio."""

    from .mcp_server import main

    main()


@skill_app.command("install")
def install_agent_skill(
        client: Annotated[
            str,
            typer.Argument(help="Target client: codex or claude-code."),
        ],
        target_dir: Annotated[
            Path | None,
            typer.Option("--target-dir", help="Custom skills directory to install into."),
        ] = None,
        project: Annotated[
            bool,
            typer.Option("--project", help="For Claude Code, install into ./.claude/skills."),
        ] = False,
        force: Annotated[
            bool,
            typer.Option("--force", help="Replace an existing aspose-pdf-cloud-mcp skill."),
        ] = False,
) -> None:
    """Install the bundled Aspose.PDF Cloud MCP skill for Codex or Claude Code."""

    try:
        result = install_skill(client, target_dir=target_dir, project=project, force=force)
    except SkillInstallError as exc:
        _handle_error(exc)

    action = "Reinstalled" if result.overwritten else "Installed"
    console.print(
        f"{action} [bold]aspose-pdf-cloud-mcp[/bold] skill to [bold]{result.destination}[/bold]."
    )


def main() -> None:
    app()


if __name__ == "__main__":
    main()
