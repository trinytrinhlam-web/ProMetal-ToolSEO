import importlib.util

from seo_app.auth import verify_password
from seo_app.config import load_settings


def load_script(project_root):
    path = project_root / "scripts" / "hash_password.py"
    spec = importlib.util.spec_from_file_location("hash_password", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_creates_env_from_template(tmp_path, project_root):
    script = load_script(project_root)
    template = tmp_path / ".env.example"
    template.write_text("# chú thích\nAPP_PASSWORD_HASH=\nWORDPRESS_URL=\n", encoding="utf-8")
    env_file = tmp_path / ".env"

    script.set_env_value(env_file, "APP_PASSWORD_HASH", "pbkdf2_sha256:1:aa:bb", template)

    assert env_file.read_text(encoding="utf-8") == (
        "# chú thích\nAPP_PASSWORD_HASH=pbkdf2_sha256:1:aa:bb\nWORDPRESS_URL=\n"
    )


def test_replaces_existing_value_and_keeps_other_lines(tmp_path, project_root):
    script = load_script(project_root)
    env_file = tmp_path / ".env"
    env_file.write_text("WORDPRESS_URL=https://a.vn\nAPP_PASSWORD_HASH=cu\n", encoding="utf-8")

    script.set_env_value(env_file, "APP_PASSWORD_HASH", "moi")

    assert (
        env_file.read_text(encoding="utf-8")
        == "WORDPRESS_URL=https://a.vn\nAPP_PASSWORD_HASH=moi\n"
    )


def test_appends_when_missing(tmp_path, project_root):
    script = load_script(project_root)
    env_file = tmp_path / ".env"
    env_file.write_text("WORDPRESS_URL=https://a.vn", encoding="utf-8")

    script.set_env_value(env_file, "APP_PASSWORD_HASH", "moi")

    assert (
        env_file.read_text(encoding="utf-8")
        == "WORDPRESS_URL=https://a.vn\nAPP_PASSWORD_HASH=moi\n"
    )


def test_main_writes_a_hash_that_verifies(tmp_path, project_root, monkeypatch):
    script = load_script(project_root)
    env_file = tmp_path / ".env"
    monkeypatch.setattr(script, "DEFAULT_ENV_FILE", env_file)
    monkeypatch.setattr(script.getpass, "getpass", lambda prompt="": "mat-khau-123")

    assert script.main([]) == 0

    # .env được tạo từ .env.example thật, rồi điền mã băm vào đúng dòng
    settings = load_settings(env_file, environ={})
    assert verify_password("mat-khau-123", settings.password_hash)
    assert "WORDPRESS_URL=" in env_file.read_text(encoding="utf-8")
