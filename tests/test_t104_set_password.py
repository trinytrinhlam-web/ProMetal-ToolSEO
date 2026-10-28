"""T-104 (Thợ Máy): ``set_password`` ghi ``.env`` an toàn (LC-T090-1, LC-T090-2).

- Thay **mọi** dòng ``APP_PASSWORD_HASH`` (app, tức python-dotenv, dùng dòng cuối), tách dòng như
  python-dotenv (chỉ CR, LF), bỏ BOM khi tách, giữ nguyên mọi dòng khác kể cả ký tự lạ.
- Ghi nguyên tử (file tạm, ``fsync``, ``os.replace``): lỗi ở bước nào thì ``.env`` cũ còn nguyên
  từng byte, file tạm được dọn, câu báo cố định và đúng sự thật.

Chỉ dùng ``.env`` giả trong thư mục tạm, mật khẩu, khóa đều là chữ giả. Ký tự lạ viết bằng
``chr(…)``, không viết trần.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from dotenv import dotenv_values
from test_hash_password_script import load_script

import seo_app.env_file as env_file
from seo_app.auth import hash_password, verify_password
from seo_app.config import load_settings
from seo_app.env_file import EnvFileError, EnvFileWriteError, set_password_hash

KEY = "APP_PASSWORD_HASH"
# Mật khẩu giả ghép lúc chạy (máy quét bí mật khỏi báo nhầm chữ trong file test).
OLD_PASSWORD = "-".join(["mat", "khau", "cu", "T104"])
NEW_PASSWORD = "-".join(["mat", "khau", "moi", "T104"])
OLD = hash_password(OLD_PASSWORD, iterations=1_000)
OTHER = "WORDPRESS_URL=https://a.vn\nWORDPRESS_USERNAME=bien-tap-vien\nIMAGE_FOLDERS=D:/Anh\n"
BOM = chr(0xFEFF)


def _env(tmp_path: Path, text: str) -> Path:
    env = tmp_path / ".env"
    env.write_bytes(text.encode("utf-8"))
    return env


def _run(project_root: Path, env: Path, monkeypatch) -> tuple[int, object]:
    script = load_script(project_root)
    monkeypatch.setattr(script, "DEFAULT_ENV_FILE", env)
    monkeypatch.setattr(script.getpass, "getpass", lambda prompt="": NEW_PASSWORD)
    monkeypatch.setattr(script, "hash_password", lambda p: hash_password(p, iterations=1_000))
    return script.main([]), script


def _active(env: Path) -> str:
    return load_settings(env_file=env, environ={}).password_hash


def _others(env: Path) -> dict[str, str | None]:
    return {k: v for k, v in dotenv_values(env, encoding="utf-8").items() if k != KEY}


def _leftovers(tmp_path: Path) -> list[str]:
    """File tạm của bộ ghi (``.env.*.tmp``) còn sót trong thư mục."""
    return sorted(p.name for p in tmp_path.iterdir() if p.name.endswith(".tmp"))


# ------------------------------------------------------------------ LC-T090-1: đúng dòng


@pytest.mark.parametrize(
    "text",
    [
        f"# Mã băm\n{KEY}=\n{OTHER}{KEY}={OLD}\n",  # dòng mẫu rồi dòng dán theo lời dặn --print
        f"{KEY}={OLD}\n{OTHER}{KEY}={OLD}\n",
        f"{KEY}=\n{OTHER}{KEY} = {OLD}\n",
        f"{KEY}=\n{OTHER}export {KEY}={OLD}\n",
    ],
    ids=["mau-va-dan", "hai-dong-giong", "co-dau-cach", "export"],
)
def test_every_hash_line_replaced_new_password_works(tmp_path, project_root, monkeypatch, text):
    env = _env(tmp_path, text)
    others = _others(env)
    code, _ = _run(project_root, env, monkeypatch)
    assert code == 0
    active = _active(env)
    assert verify_password(NEW_PASSWORD, active) and not verify_password(OLD_PASSWORD, active)
    assert _others(env) == others
    # Không còn dòng mã băm cũ nào trong file (kể cả dòng không có hiệu lực).
    assert OLD not in env.read_text(encoding="utf-8")


def test_hash_line_inside_other_multiline_value_is_not_touched(tmp_path, project_root, monkeypatch):
    note = f'GHI_CHU="dong 1\n{KEY}=x\ndong 3"\n'
    env = _env(tmp_path, f"{note}{KEY}={OLD}\n{OTHER}")
    assert _run(project_root, env, monkeypatch)[0] == 0
    assert env.read_text(encoding="utf-8").startswith(note)
    assert dotenv_values(env)["GHI_CHU"] == f"dong 1\n{KEY}=x\ndong 3"
    assert verify_password(NEW_PASSWORD, _active(env))


SEPARATORS = {"FF": 0x0C, "VT": 0x0B, "NEL": 0x85, "LS": 0x2028, "PS": 0x2029, "RS": 0x1E}


@pytest.mark.parametrize("quoted", [False, True], ids=["khong-nhay", "trong-nhay"])
@pytest.mark.parametrize("code", SEPARATORS.values(), ids=SEPARATORS.keys())
def test_other_values_with_unicode_separators_kept_byte_for_byte(
    tmp_path, project_root, monkeypatch, code, quoted
):
    value = f"D:/Anh{chr(code)}Moi"
    line = f'GHI_CHU="{value}"\n' if quoted else f"GHI_CHU={value}\n"
    env = _env(tmp_path, f"{line}{KEY}={OLD}\n{OTHER}")
    assert _run(project_root, env, monkeypatch)[0] == 0
    text = env.read_text(encoding="utf-8")
    assert text.startswith(line) and text.endswith(OTHER)
    assert dotenv_values(env)["GHI_CHU"] == value
    assert verify_password(NEW_PASSWORD, _active(env))


def test_bom_with_hash_on_first_line_replaced_in_place(tmp_path, project_root, monkeypatch):
    env = _env(tmp_path, f"{BOM}{KEY}={OLD}\n{OTHER}")
    assert _run(project_root, env, monkeypatch)[0] == 0
    text = env.read_text(encoding="utf-8")
    assert text.startswith(f"{BOM}{KEY}=pbkdf2_sha256:")  # BOM giữ, đúng dòng đầu được thay
    assert text.count(f"{KEY}=") == 1 and text.endswith(OTHER)
    assert verify_password(NEW_PASSWORD, _active(env))


def test_crlf_line_endings_kept(tmp_path, project_root, monkeypatch):
    original = f"# chú thích\n{KEY}={OLD}\n{OTHER}".replace("\n", "\r\n")
    env = _env(tmp_path, original)
    assert _run(project_root, env, monkeypatch)[0] == 0
    raw = env.read_bytes()
    assert raw.count(b"\r\n") == original.count("\r\n") and b"\n" not in raw.replace(b"\r\n", b"")
    assert verify_password(NEW_PASSWORD, _active(env))


def test_missing_line_is_appended(tmp_path, project_root, monkeypatch):
    env = _env(tmp_path, OTHER.rstrip("\n"))  # dòng cuối không có xuống dòng
    assert _run(project_root, env, monkeypatch)[0] == 0
    text = env.read_text(encoding="utf-8")
    assert text.startswith(OTHER) and text.count(f"{KEY}=") == 1
    assert verify_password(NEW_PASSWORD, _active(env))


def test_read_env_lines_splits_like_dotenv(tmp_path, project_root):
    script = load_script(project_root)
    env = _env(tmp_path, f"A=1{chr(0x0C)}2\r\nB=3{chr(0x2028)}4\rC=5\n")
    assert script.read_env_lines(env) == [f"A=1{chr(0x0C)}2", f"B=3{chr(0x2028)}4", "C=5"]


# ------------------------------------------------------------------ LC-T090-2: ghi nguyên tử


def _fail_mkstemp(monkeypatch):
    def fail(*args, **kwargs):
        raise PermissionError(13, "Permission denied")

    monkeypatch.setattr(env_file.tempfile, "mkstemp", fail)


def _fail_fsync(monkeypatch):
    def fail(fd):
        raise OSError(28, "No space left on device")

    monkeypatch.setattr(env_file.os, "fsync", fail)


def _fail_replace(monkeypatch):
    def fail(src, dst):
        raise PermissionError(13, "Permission denied", str(dst))

    monkeypatch.setattr(env_file.os, "replace", fail)


@pytest.mark.parametrize(
    ("fail", "error"),
    [
        (_fail_mkstemp, "PermissionError"),
        (_fail_fsync, "OSError"),
        (_fail_replace, "PermissionError"),
    ],
    ids=["tao-file-tam", "fsync", "os-replace"],
)
def test_write_failure_keeps_env_and_cleans_temp(
    tmp_path, project_root, monkeypatch, capsys, fail, error
):
    env = _env(tmp_path, f"# chú thích\n{KEY}={OLD}\n{OTHER}")
    before = env.read_bytes()
    fail(monkeypatch)
    code, script = _run(project_root, env, monkeypatch)
    assert code == 1
    shown = capsys.readouterr()
    shown = shown.out + shown.err
    assert f"Chưa lưu mật khẩu mới. {script.MSG_ENV_KEPT.format(error=error)}" in shown
    assert "File .env cũ vẫn còn nguyên." in shown
    assert str(tmp_path) not in shown and tmp_path.as_posix() not in shown
    assert "Traceback" not in shown and "Permission denied" not in shown
    assert env.read_bytes() == before  # còn nguyên từng byte
    assert _leftovers(tmp_path) == []  # file tạm đã dọn
    assert verify_password(OLD_PASSWORD, _active(env))


def test_restore_failure_is_not_reported_as_unchanged(tmp_path, monkeypatch):
    """Đọc lại sau khi ghi thấy sai mà trả bản cũ cũng lỗi: không được báo «file cũ còn nguyên»
    (``EnvFileWriteError``), mà là câu riêng dặn kiểm tra file."""
    env = _env(tmp_path, f"{KEY}={OLD}\n{OTHER}")
    real = env_file._atomic_write
    calls: list[str] = []

    def flaky(path, content):
        calls.append(content)
        if len(calls) == 1:
            real(path, "HONG=1\n")  # lần ghi đầu ra nội dung sai
        else:
            raise EnvFileWriteError("giả lỗi", error_name="PermissionError")

    monkeypatch.setattr(env_file, "_atomic_write", flaky)
    with pytest.raises(EnvFileError) as info:
        set_password_hash(hash_password(NEW_PASSWORD, iterations=1_000), env)
    assert not isinstance(info.value, EnvFileWriteError)
    assert "không trả lại được bản cũ (PermissionError)" in str(info.value)


@pytest.mark.parametrize(
    "value",
    ["", "a b", "a\nb", "a\rb", 'a"b', "a'b", "a#b", "a=b", "a$b", "x" * 513, None],
    ids=["rong", "dau-cach", "lf", "cr", "nhay-kep", "nhay-don", "thang", "bang", "do-la", "dai",
         "none"],
)  # fmt: skip
def test_set_password_hash_rejects_unsafe_values_without_echo(tmp_path, value):
    env = _env(tmp_path, OTHER)
    with pytest.raises(EnvFileError) as info:
        set_password_hash(value, env)  # type: ignore[arg-type]
    if value:
        assert value not in str(info.value)
    assert env.read_text(encoding="utf-8") == OTHER


def test_set_password_hash_accepts_real_hash(tmp_path):
    env = _env(tmp_path, OTHER)
    hashed = hash_password(NEW_PASSWORD, iterations=1_000)
    others = _others(env)
    set_password_hash(hashed, env)
    assert _active(env) == hashed and _others(env) == others
    assert env.read_text(encoding="utf-8") == f"{OTHER}{KEY}={hashed}\n"


def test_script_only_writes_password_hash(tmp_path, project_root):
    script = load_script(project_root)
    with pytest.raises(ValueError):
        script.set_env_value(_env(tmp_path, OTHER), "WORDPRESS_URL", "x")
