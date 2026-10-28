"""T-090 (Thợ Máy), SL-T084-1: file ``.env`` lưu sai bảng mã hay không đọc được.

Trước: ``load_settings`` để lọt ``UnicodeDecodeError`` (``.env`` lưu kiểu «ANSI» của Notepad, hay
UTF-16), ``app/main.py`` chỉ bắt ``ConfigError`` nên mọi trang (cả trước màn đăng nhập) hiện
traceback tiếng Anh có đường dẫn thư mục cài app. Nay: ``ConfigError`` câu tiếng Việt cố định (không
đường dẫn, không nội dung ``.env``, không câu lỗi gốc), app hiện trang báo lỗi; lưu lại ``.env``
bằng UTF-8 rồi tải lại trang là ra màn đăng nhập.

Chỉ dùng ``.env`` giả trong thư mục tạm (không đọc ``.env`` thật, khóa trong test là chữ giả).
"""

from __future__ import annotations

import unicodedata
from pathlib import Path

import pytest
import test_settings_images as si
from streamlit.testing.v1 import AppTest

import seo_app.config as config
from seo_app.auth import hash_password
from seo_app.config import MSG_ENV_NOT_UTF8, ConfigError, load_settings

PASSWORD = "mat-khau-thu-t090"
FOLDER = "C:/Ánh công trình Tân Phú"  # chữ có dấu: lưu kiểu «ANSI» thì không còn là UTF-8
FAKE_KEY = "sk-ant-gia-T090-khong-phai-khoa-that"  # chuỗi mồi, không phải khóa thật
TEXT = f"IMAGE_FOLDERS={FOLDER}\nANTHROPIC_API_KEY={FAKE_KEY}\n"
# Notepad trên Windows tiếng Việt lưu «ANSI» là cp1258: dấu thanh thành ký tự kết hợp riêng.
CP1258 = b"IMAGE_FOLDERS=C:/A\xd2nh c\xf4ng tri\xccnh T\xe2n Phu\xec\n"
BAD_FILES = {
    "ansi-cp1252": TEXT.encode("cp1252"),
    "ansi-cp1258": CP1258,
    "utf16-le-bom": b"\xff\xfe" + TEXT.encode("utf-16-le"),
    "utf16-be-bom": b"\xfe\xff" + TEXT.encode("utf-16-be"),
}
# Không được hiện ở câu báo hay trên trang: nội dung ``.env``, câu lỗi gốc, traceback.
CONTENT = (FOLDER, "Ánh", "Phú", FAKE_KEY, "IMAGE_FOLDERS", "ANTHROPIC_API_KEY")
ERROR_DETAILS = ("codec", "decode", "Traceback", "UnicodeDecodeError", "Errno", "Permission denied")


def assert_no_leak(shown: str, *paths: Path, extra: tuple[str, ...] = ()) -> None:
    for text in (*CONTENT, *ERROR_DETAILS, *extra):
        assert text not in shown, text
    for path in (*paths, Path.home()):
        assert str(path) not in shown and path.as_posix() not in shown, path


def assert_fixed_message(message: str, *paths: Path) -> None:
    # Câu lỗi giải mã gốc có số byte và vị trí: «can't decode byte 0xc1 in position 17».
    assert_no_leak(message, *paths, extra=("byte", "position", "0x"))


def test_cp1258_sample_is_vietnamese_ansi():
    """Mẫu cp1258 đúng là «Ảnh công trình Tân Phú» khi đọc bằng bảng mã đó (mẫu thử có nghĩa)."""
    text = unicodedata.normalize("NFC", CP1258.decode("cp1258"))
    assert text == "IMAGE_FOLDERS=C:/Ảnh công trình Tân Phú\n"


@pytest.mark.parametrize("content", BAD_FILES.values(), ids=BAD_FILES.keys())
def test_env_in_other_encoding_gives_fixed_message(tmp_path, monkeypatch, content):
    """``.env`` sai bảng mã: ``ConfigError`` đúng câu cố định (gợi ý lưu lại bằng UTF-8), cả khi
    truyền đường dẫn lẫn khi dùng ``DEFAULT_ENV_FILE``; không chép đường dẫn, nội dung, câu lỗi
    gốc."""
    env_path = tmp_path / ".env"
    env_path.write_bytes(content)
    with pytest.raises(ConfigError) as given:
        load_settings(env_path, environ={})
    assert str(given.value) == MSG_ENV_NOT_UTF8
    assert "UTF-8" in MSG_ENV_NOT_UTF8 and "Notepad" in MSG_ENV_NOT_UTF8
    assert_fixed_message(str(given.value), env_path, tmp_path)
    monkeypatch.setattr(config, "DEFAULT_ENV_FILE", env_path)
    with pytest.raises(ConfigError, match="không đọc được dạng UTF-8"):
        load_settings()


@pytest.mark.parametrize("bom", [b"", b"\xef\xbb\xbf"], ids=["utf8", "utf8-bom"])
def test_env_saved_again_as_utf8_is_read(tmp_path, bom):
    """Làm theo câu báo (lưu lại bằng UTF-8, kể cả lựa chọn «UTF-8 with BOM» của Notepad): đọc đủ,
    biến ở dòng đầu không bị BOM làm sai tên."""
    env_path = tmp_path / ".env"
    env_path.write_bytes(bom + TEXT.encode("utf-8"))
    settings = load_settings(env_path, environ={})
    assert settings.image_folders == (Path(FOLDER),)
    assert settings.anthropic_api_key == FAKE_KEY


@pytest.mark.parametrize(
    "error",
    [PermissionError(13, "Permission denied"), OSError(22, "Invalid argument")],
    ids=["PermissionError", "OSError"],
)
def test_unreadable_env_gives_fixed_message(tmp_path, monkeypatch, error):
    """``.env`` có mà không mở được (không có quyền, bị khóa, ổ đám mây không tải được): câu cố
    định kèm tên loại lỗi, không đường dẫn (lỗi gốc có đường dẫn đầy đủ)."""
    env_path = tmp_path / ".env"
    env_path.write_text(TEXT, encoding="utf-8")
    error.filename = str(env_path)

    def unreadable(*args, **kwargs):
        raise error

    monkeypatch.setattr(config, "dotenv_values", unreadable)
    with pytest.raises(ConfigError) as given:
        load_settings(env_path, environ={})
    message = str(given.value)
    assert message.startswith(f"Không đọc được file .env ({type(error).__name__}).")
    assert_fixed_message(message, env_path, tmp_path)


def test_env_that_cannot_even_be_checked_gives_fixed_message(tmp_path):
    """Hỏi «có file không» cũng lỗi (``is_file`` ném ``PermissionError``): vẫn câu cố định."""

    class Unreachable(type(tmp_path)):
        def is_file(self):
            raise PermissionError(13, "Permission denied", str(self))

    env_path = Unreachable(tmp_path / ".env")
    with pytest.raises(ConfigError) as given:
        load_settings(env_path, environ={})
    assert str(given.value).startswith("Không đọc được file .env (PermissionError).")
    assert_fixed_message(str(given.value), env_path, tmp_path)


# ============================================================ app: trang báo lỗi, rồi đăng nhập


@pytest.mark.parametrize("name", ["ansi-cp1252", "utf16-le-bom"])
def test_app_shows_clear_error_page_then_login_after_fix(project_root, tmp_path, monkeypatch, name):
    """Mở app với ``.env`` sai bảng mã: trang báo lỗi đúng câu cố định, không traceback, không
    đường dẫn, không nội dung ``.env``, không ô mật khẩu. Lưu lại ``.env`` bằng UTF-8, tải lại
    trang: màn đăng nhập hiện, đăng nhập được."""
    monkeypatch.setenv("APP_PASSWORD_HASH", hash_password(PASSWORD, iterations=1_000))
    env_path = tmp_path / ".env"
    env_path.write_bytes(BAD_FILES[name])
    monkeypatch.setattr(config, "DEFAULT_ENV_FILE", env_path)
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert [e.value for e in at.error] == [MSG_ENV_NOT_UTF8]
    assert not at.text_input  # chưa tới màn đăng nhập
    assert_no_leak(si.page_strings(at), project_root, env_path, tmp_path)

    env_path.write_text(TEXT, encoding="utf-8")  # người dùng lưu lại bằng UTF-8
    at.run()
    assert not at.exception and not at.error
    assert at.text_input[0].label == "Mật khẩu"
    at.text_input[0].input(PASSWORD)
    at.button[0].click().run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["authenticated"]
