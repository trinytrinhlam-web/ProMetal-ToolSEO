"""T-105 (Thợ Máy): ``set_password`` báo đúng nguyên nhân (SL-T104-1, SL-T104-2).

- SL-T104-1: bộ ghi ``.env`` thay file xong thì đọc lại để kiểm. **Không đọc lại được** (chương
  trình khác giữ file đúng lúc đó, file vừa ghi biến mất…) thì báo đúng là không đọc lại được để
  kiểm, không nói tới «dòng sai định dạng». Bỏ được bản vừa ghi thì nói file cũ còn nguyên; không bỏ
  được thì nói chưa chắc đã lưu. **Đọc lại được mà khác** thì vẫn báo «định dạng lạ» như cũ.
- SL-T104-2: máy có biến môi trường ``APP_PASSWORD_HASH`` (app dùng biến đó trước ``.env``, kể cả
  khi rỗng) thì ``set_password`` dừng trước khi hỏi mật khẩu, giải thích cách gỡ biến, không in giá
  trị biến, không đụng ``.env``. ``--print`` (không ghi file) vẫn in mã băm, kèm lời lưu ý.

Chỉ dùng ``.env`` giả trong thư mục tạm; mật khẩu giả ghép lúc chạy.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from test_hash_password_script import load_script

import seo_app.config as config
import seo_app.env_file as env_file
from seo_app.auth import hash_password, verify_password
from seo_app.config import load_settings
from seo_app.env_file import (
    EnvFileError,
    EnvFileFormatError,
    EnvFileReadBackError,
    EnvFileReadError,
    EnvFileWriteError,
    password_hash_overridden,
    set_api_key,
    set_password_hash,
)

KEY = "APP_PASSWORD_HASH"
IS_WINDOWS = os.name == "nt"
# Mật khẩu giả ghép lúc chạy (máy quét bí mật khỏi báo nhầm chữ trong file test).
OLD_PASSWORD = "-".join(["mat", "khau", "cu", "T105"])
NEW_PASSWORD = "-".join(["mat", "khau", "moi", "T105"])
OLD = hash_password(OLD_PASSWORD, iterations=1_000)
OTHER = f"WORDPRESS_URL=https://a.vn\n{KEY}={OLD}\nIMAGE_FOLDERS=D:/Anh\n"


def typed(prompt=""):
    return NEW_PASSWORD


def never_asked(prompt=""):
    raise AssertionError("không được bắt gõ mật khẩu")


def run_set_password(project_root, monkeypatch, env: Path, getpass=typed, argv=()):
    """Chạy ``main`` của ``scripts/hash_password.py`` với ``.env`` giả, trả (mã thoát, module)."""
    script = load_script(project_root)
    monkeypatch.setattr(script, "DEFAULT_ENV_FILE", env)
    monkeypatch.setattr(script.getpass, "getpass", getpass)
    monkeypatch.setattr(script, "hash_password", lambda p: hash_password(p, iterations=1_000))
    return script.main(list(argv)), script


def make_env(tmp_path: Path, text: str = OTHER) -> Path:
    env = tmp_path / ".env"
    env.write_bytes(text.encode("utf-8"))
    return env


def active(env: Path) -> str:
    """Mã băm app đang dùng nếu máy không có biến môi trường."""
    return load_settings(env_file=env, environ={}).password_hash


def leftovers(folder: Path) -> list[str]:
    """File tạm của bộ ghi (``.env.*.tmp``) còn sót trong thư mục."""
    return sorted(p.name for p in folder.iterdir() if p.name.endswith(".tmp"))


def assert_clean(out: str, *paths: Path) -> None:
    """Không traceback, không đường dẫn máy, không lời lỗi gốc tiếng Anh."""
    assert "Traceback" not in out and "Permission denied" not in out
    for path in paths:
        assert str(path) not in out and path.as_posix() not in out


def fail_readback(monkeypatch, error: Exception | None) -> None:
    """Lần đọc thứ hai của bộ ghi (đọc lại ngay sau ``os.replace``) lỗi ``error``; ``None``: như
    file vừa ghi đã biến mất (``_read_env_text`` trả ``None``)."""
    real = env_file._read_env_text
    calls: list[int] = []

    def flaky(path):
        calls.append(1)
        if len(calls) == 2:
            if error is None:
                return None
            raise error
        return real(path)

    monkeypatch.setattr(env_file, "_read_env_text", flaky)


def fail_restore(monkeypatch) -> None:
    """Lần ghi đầu (bản mới) thật; lần ghi sau (trả bản cũ) bị từ chối."""
    real = env_file._atomic_write
    calls: list[int] = []

    def flaky(path, content):
        calls.append(1)
        if len(calls) == 1:
            return real(path, content)
        raise EnvFileWriteError("giả lỗi", error_name="PermissionError")

    monkeypatch.setattr(env_file, "_atomic_write", flaky)


PERMISSION = EnvFileReadError(
    "Không đọc được file .env (PermissionError).", error_name="PermissionError"
)

# ====================================================== SL-T104-1: đọc lại sau khi thay bị lỗi


def test_readback_failure_tells_real_cause_and_old_file_kept(
    project_root, tmp_path, monkeypatch, capsys
):
    """Đọc lại ngay sau khi thay lỗi (chương trình khác giữ file đúng lúc đó): câu cố định nói đúng
    là không đọc lại được để kiểm, đã bỏ bản vừa ghi, file cũ còn nguyên; không nói tới dòng sai
    định dạng hay dấu nháy; file giữ nguyên từng byte, mật khẩu cũ vẫn là mật khẩu có hiệu lực."""
    env = make_env(tmp_path)
    fail_readback(monkeypatch, PERMISSION)
    code, script = run_set_password(project_root, monkeypatch, env)
    out = capsys.readouterr().out
    assert code == 1
    expected = script.MSG_ENV_READBACK.format(error="PermissionError")
    assert out.strip() == f"Chưa lưu mật khẩu mới. {expected}"
    assert "Không đọc lại được file .env để kiểm sau khi ghi (PermissionError)" in out
    assert "File .env cũ vẫn còn nguyên." in out
    assert "sai định dạng" not in out and "định dạng lạ" not in out and "dấu nháy" not in out
    assert_clean(out, tmp_path)
    assert env.read_bytes() == OTHER.encode()
    assert leftovers(tmp_path) == []
    assert verify_password(OLD_PASSWORD, active(env))


@pytest.mark.parametrize(
    ("error", "name"),
    [
        (PERMISSION, "PermissionError"),
        (EnvFileReadError("Không đọc được dạng UTF-8.", not_utf8=True), "UnicodeDecodeError"),
        (None, "FileNotFoundError"),
        (EnvFileError("File .env đang là liên kết tắt (symlink)."), "EnvFileError"),
    ],
    ids=["bi-giu", "sai-bang-ma", "bien-mat", "lien-ket-tat"],
)
def test_readback_failure_is_its_own_error_not_format(tmp_path, monkeypatch, error, name):
    """Mọi kiểu không đọc lại được (bị giữ, file bị đổi bảng mã, file vừa ghi biến mất, bị thay
    bằng liên kết tắt) đều ra ``EnvFileReadBackError`` (không phải ``EnvFileFormatError``) kèm tên
    loại lỗi; bản vừa ghi đã được bỏ, file giữ nguyên từng byte."""
    env = make_env(tmp_path)
    fail_readback(monkeypatch, error)
    with pytest.raises(EnvFileReadBackError) as info:
        set_password_hash(hash_password(NEW_PASSWORD, iterations=1_000), env)
    assert not isinstance(info.value, EnvFileFormatError)
    assert info.value.error_name == name and info.value.restored is True
    message = str(info.value)
    assert f"Không đọc lại được file .env để kiểm sau khi ghi ({name})" in message
    assert "định dạng" not in message and "dấu nháy" not in message
    assert env.read_bytes() == OTHER.encode()
    assert leftovers(tmp_path) == []


def test_readback_and_restore_both_fail_never_claims_old_file_kept(
    project_root, tmp_path, monkeypatch, capsys
):
    """Đọc lại lỗi mà trả bản cũ cũng lỗi: không được nói «file cũ còn nguyên» hay «chưa lưu», mà
    nói chưa chắc đã lưu (file có thể đã mang mật khẩu mới chưa kiểm), dặn chạy lại. Đúng là bản vừa
    ghi còn trên đĩa: mật khẩu mới đang có hiệu lực."""
    env = make_env(tmp_path)
    fail_readback(monkeypatch, PERMISSION)
    fail_restore(monkeypatch)
    code, script = run_set_password(project_root, monkeypatch, env)
    out = capsys.readouterr().out
    assert code == 1
    expected = script.MSG_ENV_READBACK_UNSURE.format(error="PermissionError")
    assert out.strip() == f"Chưa chắc đã lưu được mật khẩu mới. {expected}"
    assert "còn nguyên" not in out and "Chưa lưu mật khẩu mới" not in out
    assert "Đã lưu" not in out and "định dạng" not in out
    assert_clean(out, tmp_path)
    assert verify_password(NEW_PASSWORD, active(env))
    assert leftovers(tmp_path) == []


def test_readback_mismatch_still_reported_as_format(project_root, tmp_path, monkeypatch, capsys):
    """Canh: đọc lại **được** mà nội dung khác (đĩa ghi sai) thì vẫn là câu «dòng sai định dạng» như
    cũ, file trả về bản cũ. Hai trường hợp không bị gộp lại."""
    env = make_env(tmp_path)
    real = env_file._atomic_write
    calls: list[int] = []

    def flaky(path, content):
        calls.append(1)
        real(path, "HONG=1\n" if len(calls) == 1 else content)

    monkeypatch.setattr(env_file, "_atomic_write", flaky)
    code, script = run_set_password(project_root, monkeypatch, env)
    out = capsys.readouterr().out
    assert code == 1
    assert out.strip() == f"Chưa lưu mật khẩu mới. {script.MSG_ENV_FORMAT}"
    assert env.read_bytes() == OTHER.encode()


def test_settings_page_writer_gets_true_message_without_old_file(tmp_path, monkeypatch):
    """Bộ ghi dùng chung (trang Cài đặt lưu khóa AI) khi **chưa có** ``.env``: đọc lại lỗi thì xóa
    file vừa tạo, câu báo nói đúng (không đọc lại được, ``.env`` như trước khi lưu), không
    «định dạng lạ», không chứa khóa."""
    env = tmp_path / ".env"
    fail_readback(monkeypatch, PERMISSION)
    key = "-".join(["sk", "khoa", "gia", "T105"])
    with pytest.raises(EnvFileReadBackError) as info:
        set_api_key("ANTHROPIC_API_KEY", key, env)
    assert info.value.restored is True
    message = str(info.value)
    assert message == env_file._READBACK_RESTORED.format(error="PermissionError")
    assert "file .env vẫn như trước khi lưu" in message
    assert key not in message and "định dạng" not in message
    assert not env.exists()
    assert leftovers(tmp_path) == []


def test_new_file_that_cannot_be_removed_is_not_reported_as_kept(tmp_path, monkeypatch):
    """Chưa có ``.env``, đọc lại lỗi, xóa file vừa tạo cũng lỗi: ``restored`` là ``False``, câu báo
    nói file có thể đã mang giá trị mới chưa kiểm (không nói «như trước khi lưu»)."""
    env = tmp_path / ".env"
    fail_readback(monkeypatch, PERMISSION)

    def refuse(self, *args, **kwargs):
        raise PermissionError(13, "Permission denied", str(self))

    monkeypatch.setattr(type(env), "unlink", refuse)
    with pytest.raises(EnvFileReadBackError) as info:
        set_api_key("OPENAI_API_KEY", "-".join(["sk", "gia", "T105"]), env)
    assert info.value.restored is False
    message = str(info.value)
    assert message == env_file._READBACK_UNSURE.format(error="PermissionError")
    assert "như trước khi lưu" not in message and "còn nguyên" not in message
    assert_clean(message, tmp_path)
    assert env.exists()


def test_mismatch_new_file_that_cannot_be_removed_is_not_reported_as_kept(tmp_path, monkeypatch):
    """Chưa có ``.env``, đọc lại thấy khác, xóa file vừa tạo cũng lỗi: trước đây bị bỏ qua lặng lẽ
    rồi báo «đã giữ nguyên file cũ»; nay là câu «không trả lại được bản cũ» như khi có file cũ."""
    env = tmp_path / ".env"
    real = env_file._atomic_write
    monkeypatch.setattr(env_file, "_atomic_write", lambda p, c: real(p, "HONG=1\n"))

    def refuse(self, *args, **kwargs):
        raise PermissionError(13, "Permission denied", str(self))

    monkeypatch.setattr(type(env), "unlink", refuse)
    with pytest.raises(EnvFileError) as info:
        set_api_key("GEMINI_API_KEY", "AIzaKhoaGiaT105", env)
    assert not isinstance(info.value, (EnvFileFormatError, EnvFileReadBackError))
    assert "không trả lại được bản cũ (PermissionError)" in str(info.value)
    assert_clean(str(info.value), tmp_path)


def _lock(path: Path):
    """Khóa cả file như một chương trình khác đang giữ (khóa vùng byte của Windows)."""
    import msvcrt

    handle = path.open("r+b")
    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, path.stat().st_size)
    return handle


def _unlock(handle, path: Path) -> None:
    import msvcrt

    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, path.stat().st_size)
    handle.close()


@pytest.mark.skipif(not IS_WINDOWS, reason="khóa vùng byte của Windows (msvcrt)")
def test_real_lock_during_readback_only(project_root, tmp_path, monkeypatch, capsys):
    """Lỗi thật của Windows (không giả): chương trình khác khóa ``.env`` đúng lúc bộ ghi đọc lại,
    rồi nhả ra. Lần đọc lại lỗi ``PermissionError`` thật, bộ ghi trả bản cũ được: câu «không đọc
    lại được… file cũ còn nguyên», file giữ nguyên từng byte."""
    env = make_env(tmp_path)
    real = env_file._read_env_text
    calls: list[int] = []

    def locked_once(path):
        calls.append(1)
        if len(calls) != 2:
            return real(path)
        handle = _lock(path)
        try:
            return real(path)
        finally:
            _unlock(handle, path)

    monkeypatch.setattr(env_file, "_read_env_text", locked_once)
    code, script = run_set_password(project_root, monkeypatch, env)
    out = capsys.readouterr().out
    assert code == 1
    expected = script.MSG_ENV_READBACK.format(error="PermissionError")
    assert out.strip() == f"Chưa lưu mật khẩu mới. {expected}"
    assert env.read_bytes() == OTHER.encode()
    assert leftovers(tmp_path) == []


@pytest.mark.skipif(not IS_WINDOWS, reason="khóa vùng byte của Windows (msvcrt)")
def test_real_lock_after_replace_until_end(project_root, tmp_path, monkeypatch, capsys):
    """Lỗi thật của Windows: chương trình khác khóa ``.env`` ngay sau khi bộ ghi thay file và giữ
    tới lúc ``set_password`` kết thúc. Đọc lại lỗi, trả bản cũ cũng bị Windows từ chối: câu «chưa
    chắc đã lưu được», không nói «còn nguyên». Nhả khóa ra thì đúng là bản mới đang trên đĩa."""
    env = make_env(tmp_path)
    real = env_file._atomic_write
    holder: list = []

    def write_then_lock(path, content):
        real(path, content)
        if not holder:
            holder.append(_lock(path))

    monkeypatch.setattr(env_file, "_atomic_write", write_then_lock)
    try:
        code, script = run_set_password(project_root, monkeypatch, env)
    finally:
        for handle in holder:
            _unlock(handle, env)
    out = capsys.readouterr().out
    assert code == 1
    expected = script.MSG_ENV_READBACK_UNSURE.format(error="PermissionError")
    assert out.strip() == f"Chưa chắc đã lưu được mật khẩu mới. {expected}"
    assert verify_password(NEW_PASSWORD, active(env))
    assert leftovers(tmp_path) == []


# ======================================= SL-T104-2: biến môi trường APP_PASSWORD_HASH đè lên .env


@pytest.mark.parametrize(
    ("environ", "expected"),
    [
        ({}, False),
        ({KEY: "x"}, True),
        ({KEY: ""}, True),
        ({KEY: "   "}, True),
        ({"ANTHROPIC_API_KEY": "x", "GOOGLE_SHEET_ID": "y"}, False),
    ],
    ids=["khong-co", "co-gia-tri", "rong", "dau-cach", "bien-khac"],
)
def test_password_hash_overridden(environ, expected):
    assert password_hash_overridden(environ) is expected


@pytest.mark.parametrize(
    "environ",
    [{}, {KEY: "khac"}, {KEY: ""}, {KEY: "  "}, {"WORDPRESS_URL": "https://b.vn"}],
    ids=["khong-co", "co-gia-tri", "rong", "dau-cach", "bien-khac"],
)
def test_overridden_matches_how_app_reads(tmp_path, environ):
    """Cùng điều kiện với ``load_settings`` (app): biến có mặt (kể cả rỗng) là ``.env`` mất tác
    dụng với mật khẩu; không có thì ``.env`` quyết định."""
    env = make_env(tmp_path)
    assert KEY in config.ENV_VARS
    ignores_file = load_settings(env_file=env, environ=environ).password_hash != OLD
    assert password_hash_overridden(environ) is ignores_file


def test_overridden_reads_real_os_environ_like_app(tmp_path, monkeypatch):
    """Mặc định đọc biến môi trường thật của máy, giống ``load_settings()``. Tên viết thường: trên
    Windows là cùng một biến (cả hai cùng thấy), trên Mac/Linux là biến khác (cả hai cùng bỏ
    qua)."""
    env = make_env(tmp_path)
    assert password_hash_overridden() is False
    other = "khac"
    monkeypatch.setenv(KEY.lower(), other)
    app_uses_it = load_settings(env_file=env).password_hash == other
    assert password_hash_overridden() is app_uses_it
    monkeypatch.delenv(KEY.lower(), raising=False)
    monkeypatch.setenv(KEY, OLD)
    assert password_hash_overridden() is True


@pytest.mark.parametrize("value", [OLD, ""], ids=["ma-bam-cu", "rong"])
def test_set_password_stops_before_asking_when_env_var_set(
    project_root, tmp_path, monkeypatch, capsys, value
):
    """Máy có biến môi trường ``APP_PASSWORD_HASH``: dừng ngay (chưa bắt gõ mật khẩu), mã thoát 1,
    câu cố định nói rõ vì sao mật khẩu ghi vào ``.env`` không có hiệu lực và cách gỡ biến; không in
    giá trị biến; ``.env`` giữ nguyên từng byte. Gỡ biến rồi chạy lại thì đặt được, có hiệu lực."""
    env = make_env(tmp_path)
    monkeypatch.setenv(KEY, value)
    code, script = run_set_password(project_root, monkeypatch, env, never_asked)
    out = capsys.readouterr().out
    assert code == 1
    assert out.strip() == f"Chưa đặt được mật khẩu. {script.MSG_ENV_OVERRIDDEN}"
    assert "biến môi trường" in out and KEY in out and "không có hiệu lực" in out
    assert OLD not in out and "pbkdf2" not in out
    assert "Đã lưu" not in out
    assert_clean(out, tmp_path)
    assert env.read_bytes() == OTHER.encode()
    assert leftovers(tmp_path) == []

    monkeypatch.delenv(KEY)
    code, _ = run_set_password(project_root, monkeypatch, env)
    assert code == 0
    assert verify_password(NEW_PASSWORD, load_settings(env_file=env).password_hash)


def test_overridden_message_is_plain_and_fixed(project_root):
    """Câu dặn gỡ biến: cố định (không chèn giá trị nào lúc chạy), có các bước làm cho người không
    rành kỹ thuật (Windows, Mac, tắt app, chạy lại)."""
    script = load_script(project_root)
    message = script.MSG_ENV_OVERRIDDEN
    assert "{" not in message and "}" not in message
    for part in ("Windows", "Mac", "tắt hẳn app", "Chạy lại set_password"):
        assert part in message


def test_print_mode_with_env_var_prints_hash_and_note(project_root, tmp_path, monkeypatch, capsys):
    """``--print`` không ghi file nên vẫn in mã băm, nhưng kèm lời lưu ý: dán vào ``.env`` sẽ chưa
    có hiệu lực khi máy còn biến môi trường đó. Không in giá trị biến, không đụng ``.env``."""
    env = make_env(tmp_path)
    monkeypatch.setenv(KEY, OLD)
    code, script = run_set_password(project_root, monkeypatch, env, argv=["--print"])
    out = capsys.readouterr().out
    assert code == 0
    assert f"\n{KEY}=pbkdf2_sha256:" in out
    assert script.MSG_PRINT_OVERRIDDEN in out
    assert OLD not in out
    assert env.read_bytes() == OTHER.encode()


def test_print_mode_without_env_var_has_no_note(project_root, tmp_path, monkeypatch, capsys):
    env = make_env(tmp_path)
    code, script = run_set_password(project_root, monkeypatch, env, argv=["--print"])
    out = capsys.readouterr().out
    assert code == 0
    assert f"\n{KEY}=pbkdf2_sha256:" in out
    assert "biến môi trường" not in out
