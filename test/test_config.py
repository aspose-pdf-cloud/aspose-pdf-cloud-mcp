import pytest

from aspose_pdf_cloud_mcp.config import (
    ConfigError,
    get_auth_status,
    load_config,
    write_auth_env_file,
)


def test_load_config_requires_credentials(monkeypatch):
    monkeypatch.delenv("ASPOSE_CLIENT_ID", raising=False)
    monkeypatch.delenv("ASPOSE_CLIENT_SECRET", raising=False)

    with pytest.raises(ConfigError):
        load_config(env_file=None)


def test_load_config_reads_required_and_optional_env(monkeypatch):
    monkeypatch.setenv("ASPOSE_CLIENT_ID", "client")
    monkeypatch.setenv("ASPOSE_CLIENT_SECRET", "secret")
    monkeypatch.setenv("ASPOSE_BASE_URL", "https://example.test/v3.0")
    monkeypatch.setenv("ASPOSE_SELF_HOST", "true")
    monkeypatch.setenv("ASPOSE_STORAGE_NAME", "storage")

    config = load_config(env_file=None)

    assert config.client_id == "client"
    assert config.client_secret == "secret"
    assert config.base_url == "https://example.test/v3.0"
    assert config.self_host is True
    assert config.storage_name == "storage"


def test_load_config_reads_dotenv_when_env_is_absent(monkeypatch, tmp_path):
    monkeypatch.delenv("ASPOSE_CLIENT_ID", raising=False)
    monkeypatch.delenv("ASPOSE_CLIENT_SECRET", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        'ASPOSE_CLIENT_ID="file-client"\nASPOSE_CLIENT_SECRET="file-secret"\n',
        encoding="utf-8",
    )

    config = load_config(env_file=env_file)

    assert config.client_id == "file-client"
    assert config.client_secret == "file-secret"


def test_load_config_env_overrides_dotenv(monkeypatch, tmp_path):
    monkeypatch.setenv("ASPOSE_CLIENT_ID", "env-client")
    monkeypatch.setenv("ASPOSE_CLIENT_SECRET", "env-secret")
    env_file = tmp_path / ".env"
    env_file.write_text(
        'ASPOSE_CLIENT_ID="file-client"\nASPOSE_CLIENT_SECRET="file-secret"\n',
        encoding="utf-8",
    )

    config = load_config(env_file=env_file)

    assert config.client_id == "env-client"
    assert config.client_secret == "env-secret"


def test_get_auth_status_redacts_values_and_reports_sources(monkeypatch, tmp_path):
    monkeypatch.delenv("ASPOSE_CLIENT_ID", raising=False)
    monkeypatch.setenv("ASPOSE_CLIENT_SECRET", "env-secret-value")
    env_file = tmp_path / ".env"
    env_file.write_text(
        'ASPOSE_CLIENT_ID="file-client-value"\nASPOSE_CLIENT_SECRET="file-secret"\n',
        encoding="utf-8",
    )

    status = get_auth_status(env_file)

    settings = status["settings"]
    assert status["configured"] is True
    assert settings["ASPOSE_CLIENT_ID"]["source"] == "env_file"
    assert settings["ASPOSE_CLIENT_ID"]["value"] == "file...alue"
    assert settings["ASPOSE_CLIENT_SECRET"]["source"] == "environment"
    assert settings["ASPOSE_CLIENT_SECRET"]["value"] == "env-...alue"


def test_write_auth_env_file_preserves_unrelated_lines(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "# local settings\nOTHER=value\nASPOSE_CLIENT_ID=old\n",
        encoding="utf-8",
    )

    write_auth_env_file(
        env_file,
        {
            "ASPOSE_CLIENT_ID": "new-client",
            "ASPOSE_CLIENT_SECRET": "new-secret",
            "ASPOSE_STORAGE_NAME": "store",
            "ASPOSE_BASE_URL": "",
            "ASPOSE_SELF_HOST": False,
        },
    )

    assert env_file.read_text(encoding="utf-8") == (
        "# local settings\n"
        "OTHER=value\n"
        'ASPOSE_CLIENT_ID="new-client"\n'
        "\n"
        'ASPOSE_CLIENT_SECRET="new-secret"\n'
        'ASPOSE_STORAGE_NAME="store"\n'
        'ASPOSE_SELF_HOST="false"\n'
    )
