"""Lá Chắn T-090: test chứng minh lỗi (``xfail(strict=True)`` tới khi sửa), test canh hướng sửa.

Cả hai lỗi có từ trước T-090, nằm ở ``set_password`` (``scripts/hash_password.py``), nơi lượt 2
của T-090 sửa câu báo:

- LC-T090-1 (Thấp): ``set_env_value`` sửa ``.env`` theo dòng tự chế, khác cách python-dotenv (app)
  đọc. (a) ``.env`` có hai dòng ``APP_PASSWORD_HASH`` (dòng mẫu rỗng chép từ ``.env.example`` còn
  đó, dòng người dùng dán theo lời dặn «Dán dòng sau vào file .env» của ``--print``): script thay
  dòng **đầu**, app dùng dòng **cuối**, nên mật khẩu mới không có hiệu lực, mật khẩu cũ vẫn đăng
  nhập được, dù script báo «Đã lưu mật khẩu mới». (b) ``str.splitlines`` cắt cả ở ký tự
  python-dotenv không coi là xuống dòng (FF, VT, RS, NEL, U+2028, U+2029): giá trị của biến
  **khác** bị cắt cụt hay đổi.
- LC-T090-2 (Thấp): ghi ``.env`` bằng ``write_text``: mở kiểu "w" là cắt file về 0 byte trước rồi
  mới ghi. Chương trình khác giữ ``.env`` bằng khóa vùng byte kiểu chia sẻ (Windows: đọc được,
  không ghi được): mở để ghi vẫn được và cắt file, ghi thì lỗi, nên ``.env`` thành rỗng (mất khóa
  API, mật khẩu ứng dụng WordPress, thư mục ảnh) trong khi câu báo mới bảo «Đóng chương trình đang
  mở file… rồi chạy lại set_password»; chạy lại thì ``.env`` chỉ còn ``APP_PASSWORD_HASH``.

Hướng sửa (đã giả lập, 0 vấn đề): ``set_password`` ghi bằng bộ ghi của ``seo_app/env_file.py``
(tách bằng ``parse_stream`` của python-dotenv, thay mọi dòng của biến, ghi file tạm rồi
``os.replace``, đọc lại để kiểm).

Chỉ dùng ``.env`` giả trong thư mục tạm, không có khóa thật; test gọi ``main()`` của script (như
bấm đúp ``set_password``) với ``getpass`` giả.
"""

from __future__ import annotations

import contextlib
import os
from pathlib import Path

import pytest
from dotenv import dotenv_values
from test_hash_password_script import load_script

from seo_app.auth import hash_password, verify_password
from seo_app.config import load_settings

KEY = "APP_PASSWORD_HASH"
# Mật khẩu giả ghép lúc chạy (máy quét bí mật khỏi báo nhầm chữ trong file test).
OLD_PASSWORD = "-".join(["mat", "khau", "cu", "T090"])
NEW_PASSWORD = "-".join(["mat", "khau", "moi", "T090"])
OLD = hash_password(OLD_PASSWORD, iterations=1_000)
OTHER = "WORDPRESS_URL=https://a.vn\nWORDPRESS_USERNAME=bien-tap-vien\nIMAGE_FOLDERS=D:/Anh\n"
IS_WINDOWS = os.name == "nt"


def _env(tmp_path: Path, text: str) -> Path:
    env = tmp_path / ".env"
    env.write_bytes(text.encode("utf-8"))
    return env


def _set_password(project_root: Path, env: Path, monkeypatch) -> int:
    """Chạy ``set_password`` (``main([])``) với ``.env`` giả, gõ mật khẩu mới."""
    script = load_script(project_root)
    monkeypatch.setattr(script, "DEFAULT_ENV_FILE", env)
    monkeypatch.setattr(script.getpass, "getpass", lambda prompt="": NEW_PASSWORD)
    monkeypatch.setattr(script, "hash_password", lambda p: hash_password(p, iterations=1_000))
    return script.main([])


def _active_hash(env: Path) -> str:
    return load_settings(env_file=env, environ={}).password_hash


def _others(env: Path) -> dict[str, str | None]:
    return {k: v for k, v in dotenv_values(env, encoding="utf-8").items() if k != KEY}


# ------------------------------------------------------------------ LC-T090-1 (a)

DUPLICATES = {
    # .env chép từ .env.example (dòng mẫu «APP_PASSWORD_HASH=»), dán dòng của --print xuống cuối.
    "dong-mau-roi-dong-dan": f"# Mã băm mật khẩu\n{KEY}=\n{OTHER}{KEY}={OLD}\n",
    "dong-sau-co-dau-cach": f"{KEY}=\n{OTHER}{KEY} = {OLD}\n",
    "dong-sau-co-export": f"{KEY}=\n{OTHER}export {KEY}={OLD}\n",
    # Dòng giống hệt nằm trong giá trị nhiều dòng (có nháy) của một biến khác.
    "trong-gia-tri-nhieu-dong": f'GHI_CHU="dong 1\n{KEY}=x\ndong 3"\n{KEY}={OLD}\n{OTHER}',
}


@pytest.mark.parametrize("text", DUPLICATES.values(), ids=DUPLICATES.keys())
def test_lc1_duplicate_lines_old_password_is_the_active_one_before(tmp_path, text):
    """Canh tiền đề: trước khi đặt lại, app (python-dotenv: dòng sau thắng) dùng mật khẩu cũ."""
    assert verify_password(OLD_PASSWORD, _active_hash(_env(tmp_path, text)))


@pytest.mark.xfail(
    strict=True,
    reason="LC-T090-1: .env có hai dòng APP_PASSWORD_HASH: set_password thay dòng đầu, app dùng "
    "dòng cuối, nên mật khẩu mới không có hiệu lực, mật khẩu cũ vẫn đăng nhập được",
)
@pytest.mark.parametrize("text", DUPLICATES.values(), ids=DUPLICATES.keys())
def test_lc1_new_password_takes_effect_with_duplicate_lines(
    tmp_path, project_root, monkeypatch, text
):
    env = _env(tmp_path, text)
    others = _others(env)
    assert _set_password(project_root, env, monkeypatch) == 0  # script báo «Đã lưu mật khẩu mới»
    active = _active_hash(env)
    assert verify_password(NEW_PASSWORD, active) and not verify_password(OLD_PASSWORD, active)
    assert _others(env) == others


# ------------------------------------------------------------------ LC-T090-1 (b)

BREAKS = {"FF": 0x0C, "VT": 0x0B, "RS": 0x1E, "NEL": 0x85, "LS": 0x2028, "PS": 0x2029}


@pytest.mark.xfail(
    strict=True,
    reason="LC-T090-1: set_password tách dòng bằng str.splitlines (cắt cả ở FF, VT, NEL, U+2028…) "
    "rồi nối lại bằng xuống dòng: giá trị của biến khác bị cắt cụt hay đổi",
)
@pytest.mark.parametrize("quoted", [False, True], ids=["khong-nhay", "trong-nhay"])
@pytest.mark.parametrize("code", BREAKS.values(), ids=BREAKS.keys())
def test_lc1_other_values_kept_when_they_hold_unicode_line_separators(
    tmp_path, project_root, monkeypatch, code, quoted
):
    value = f"D:/Anh{chr(code)}Moi"
    line = f'GHI_CHU="{value}"' if quoted else f"GHI_CHU={value}"
    env = _env(tmp_path, f"{line}\n{KEY}={OLD}\n{OTHER}")
    others = _others(env)
    assert others["GHI_CHU"] == value  # tiền đề: python-dotenv đọc nguyên giá trị
    assert _set_password(project_root, env, monkeypatch) == 0
    assert _others(env) == others


SAFE = {
    "mot-dong": f"# chú thích\n{KEY}={OLD}\n{OTHER}",
    "crlf": f"# chú thích\n{KEY}={OLD}\n{OTHER}".replace("\n", "\r\n"),
    "bom-dong-dau": f"{chr(0xFEFF)}{KEY}={OLD}\n{OTHER}",
    "export": f"export {KEY}={OLD}\n{OTHER}",
    "chua-co-dong": OTHER,
    "khong-xuong-dong-cuoi": f"{OTHER}{KEY}={OLD}",
}


@pytest.mark.parametrize("text", SAFE.values(), ids=SAFE.keys())
def test_lc1_guard_single_line_cases_keep_working(tmp_path, project_root, monkeypatch, text):
    """Canh hướng sửa: các dạng đang đúng thì vẫn đúng (mật khẩu mới có hiệu lực, biến khác giữ
    nguyên, kể cả «UTF-8 with BOM» mà dòng mã băm nằm ngay dòng đầu)."""
    env = _env(tmp_path, text)
    others = _others(env)
    assert _set_password(project_root, env, monkeypatch) == 0
    active = _active_hash(env)
    assert verify_password(NEW_PASSWORD, active) and not verify_password(OLD_PASSWORD, active)
    assert _others(env) == others


# ------------------------------------------------------------------ LC-T090-2


@contextlib.contextmanager
def _shared_byte_range_lock(path: Path):
    """Chương trình khác giữ ``.env`` bằng khóa vùng byte kiểu chia sẻ (``LockFileEx`` không cờ độc
    quyền): mọi tiến trình đọc được, không tiến trình nào ghi được vùng đó, kể cả tiến trình đang
    giữ khi ghi qua một handle khác."""
    import ctypes
    import msvcrt
    from ctypes import wintypes

    class Overlapped(ctypes.Structure):
        _fields_ = [
            ("internal", ctypes.c_void_p),
            ("internal_high", ctypes.c_void_p),
            ("offset", wintypes.DWORD),
            ("offset_high", wintypes.DWORD),
            ("event", wintypes.HANDLE),
        ]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    lock, unlock = kernel32.LockFileEx, kernel32.UnlockFileEx
    lock.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD,
                     wintypes.DWORD, ctypes.POINTER(Overlapped)]  # fmt: skip
    unlock.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD,
                       ctypes.POINTER(Overlapped)]  # fmt: skip
    lock.restype = unlock.restype = wintypes.BOOL
    with path.open("rb") as holder:
        handle = msvcrt.get_osfhandle(holder.fileno())
        # 1 = LOCKFILE_FAIL_IMMEDIATELY, không có 2 (LOCKFILE_EXCLUSIVE_LOCK): khóa chia sẻ.
        if not lock(handle, 1, 0, 0xFFFFFFFF, 0, ctypes.byref(Overlapped())):
            raise OSError(ctypes.get_last_error(), "LockFileEx")
        try:
            yield
        finally:
            unlock(handle, 0, 0xFFFFFFFF, 0, ctypes.byref(Overlapped()))


@pytest.mark.skipif(not IS_WINDOWS, reason="khóa vùng byte của Windows (LockFileEx)")
def test_lc2_shared_lock_lets_others_read_but_not_write(tmp_path):
    """Canh tiền đề của LC-T090-2: dưới khóa chia sẻ, đọc ``.env`` được (nên bước kiểm đầu của
    ``set_password`` qua), ghi thì lỗi."""
    env = _env(tmp_path, f"{KEY}={OLD}\n{OTHER}")
    with _shared_byte_range_lock(env):
        assert env.read_text(encoding="utf-8").startswith(KEY)
        with pytest.raises(OSError), env.open("r+b") as other:
            other.write(b"x")
            other.flush()


@pytest.mark.skipif(not IS_WINDOWS, reason="khóa vùng byte của Windows (LockFileEx)")
@pytest.mark.xfail(
    strict=True,
    reason="LC-T090-2: set_password mở .env kiểu 'w' (cắt về 0 byte) rồi mới ghi; ghi lỗi vì "
    "chương trình khác giữ khóa chia sẻ thì .env thành rỗng, mất mọi biến khác",
)
def test_lc2_env_never_emptied_when_write_fails(tmp_path, project_root, monkeypatch, capsys):
    env = _env(tmp_path, f"{KEY}={OLD}\n{OTHER}")
    before, others = env.read_bytes(), _others(env)
    with _shared_byte_range_lock(env):
        code = _set_password(project_root, env, monkeypatch)
    shown = capsys.readouterr()
    shown = shown.out + shown.err
    assert str(tmp_path) not in shown and "Traceback" not in shown  # câu báo cố định (đúng)
    assert _others(env) == others  # không mất biến nào
    if code != 0:
        assert env.read_bytes() == before  # báo «Chưa lưu» thì file phải còn nguyên
    else:
        assert verify_password(NEW_PASSWORD, _active_hash(env))
