import re
from datetime import timedelta
from pathlib import Path

import pytest

from seo_app.config import DEFAULT_TIMEZONE, ENV_VARS, ConfigError, load_settings


def write_env(tmp_path: Path, text: str) -> Path:
    env_file = tmp_path / ".env"
    env_file.write_text(text, encoding="utf-8")
    return env_file


def test_defaults_without_env_file(tmp_path):
    settings = load_settings(tmp_path / "khong-co.env", environ={})
    assert settings.password_hash == ""
    assert settings.timezone_name == DEFAULT_TIMEZONE
    assert settings.image_folders == ()
    assert not any(settings.status().values())


def test_reads_values_from_env_file(tmp_path):
    env_file = write_env(
        tmp_path,
        "WORDPRESS_URL=https://example.com/\n"
        "WORDPRESS_USERNAME=lam\n"
        "WORDPRESS_APP_PASSWORD=abcd efgh\n"
        "IMAGE_FOLDERS=E:/anh cong trinh; /Volumes/USB/anh ;\n",
    )
    settings = load_settings(env_file, environ={})
    assert settings.wordpress_url == "https://example.com"
    assert settings.wordpress_app_password == "abcd efgh"
    assert settings.image_folders == (Path("E:/anh cong trinh"), Path("/Volumes/USB/anh"))
    assert settings.status()["WordPress"] is True


def test_environment_overrides_env_file(tmp_path):
    env_file = write_env(tmp_path, "GOOGLE_SHEET_ID=tu-file\n")
    settings = load_settings(env_file, environ={"GOOGLE_SHEET_ID": "tu-moi-truong"})
    assert settings.google_sheet_id == "tu-moi-truong"


def test_secrets_are_hidden_from_repr(tmp_path):
    env_file = write_env(
        tmp_path,
        "APP_PASSWORD_HASH=pbkdf2_sha256:1:aa:bb\n"
        "WORDPRESS_APP_PASSWORD=wp-secret\n"
        "ANTHROPIC_API_KEY=sk-ant-secret\n"
        "OPENAI_API_KEY=sk-openai-secret\n"
        "GEMINI_API_KEY=gemini-secret\n",
    )
    text = repr(load_settings(env_file, environ={}))
    for secret in [
        "pbkdf2_sha256",
        "wp-secret",
        "sk-ant-secret",
        "sk-openai-secret",
        "gemini-secret",
    ]:
        assert secret not in text


def test_now_uses_vietnam_timezone_by_default(tmp_path):
    now = load_settings(None, environ={}).now()
    assert now.utcoffset() == timedelta(hours=7)


def test_invalid_timezone_raises_clear_error():
    with pytest.raises(ConfigError, match="APP_TIMEZONE"):
        load_settings(None, environ={"APP_TIMEZONE": "Sao/Hoa"})


def test_env_example_lists_every_variable(project_root):
    text = (project_root / ".env.example").read_text(encoding="utf-8")
    names = set(re.findall(r"^([A-Z][A-Z0-9_]*)=", text, flags=re.MULTILINE))
    assert names == set(ENV_VARS)


def test_env_example_has_no_real_secrets(project_root):
    settings = load_settings(project_root / ".env.example", environ={})
    assert settings.password_hash == ""
    assert settings.wordpress_app_password == ""
    assert settings.anthropic_api_key == ""
    assert settings.openai_api_key == ""
    assert settings.gemini_api_key == ""
