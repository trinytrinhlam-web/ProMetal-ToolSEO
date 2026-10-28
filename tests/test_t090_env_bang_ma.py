"""T-090 (Thợ Máy), SL-T084-1: file ``.env`` lưu sai bảng mã hay không đọc được.

Trước: ``load_settings`` để lọt ``UnicodeDecodeError`` (``.env`` lưu kiểu «ANSI» của Notepad, hay
UTF-16), ``app/main.py`` chỉ bắt ``ConfigError`` nên mọi trang (cả trước màn đăng nhập) hiện
traceback tiếng Anh có đường dẫn thư mục cài app. Nay: ``ConfigError`` câu tiếng Việt cố định (không
đường dẫn, không nội dung ``.env``, không câu lỗi gốc), app hiện trang báo lỗi; lưu lại ``.env``
bằng UTF-8 rồi tải lại trang là ra màn đăng nhập.

Lượt 2 (đề xuất 3): ``scripts/hash_password.py`` (bấm đúp ``set_password``) cũng báo câu tiếng Việt
cố định thay cho traceback: ``.env`` sai bảng mã thì báo ngay, chưa bắt gõ mật khẩu; không đọc hay
ghi được ``.env`` thì báo kèm tên loại lỗi; file giữ nguyên.

Chỉ dùng ``.env`` giả trong thư mục tạm (không đọc ``.env`` thật, khóa trong test là chữ giả).
"""

from __future__ import annotations

import unicodedata
from pathlib import Path

import pytest
import test_settings_images as si
from streamlit.testing.v1 import AppTest
from test_hash_password_script import load_script

import seo_app.config as config
from seo_app.auth import hash_password, verify_password
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


# ============================================================ lượt 2: set_password


def never_asked(prompt=""):
    raise AssertionError("không được bắt gõ mật khẩu khi .env hỏng")


def typed(prompt=""):
    return PASSWORD


def run_set_password(project_root, monkeypatch, env_path: Path, getpass, argv=()):
    """Chạy ``main`` của ``scripts/hash_password.py`` với ``.env`` giả, trả (mã thoát, module)."""
    script = load_script(project_root)
    monkeypatch.setattr(script, "DEFAULT_ENV_FILE", env_path)
    monkeypatch.setattr(script.getpass, "getpass", getpass)
    return script.main(list(argv)), script


@pytest.mark.parametrize("content", BAD_FILES.values(), ids=BAD_FILES.keys())
def test_set_password_with_env_in_other_encoding_stops_before_asking(
    project_root, tmp_path, monkeypatch, capsys, content
):
    """Bấm set_password khi ``.env`` lưu sai bảng mã: báo ngay câu cố định (lưu lại bằng UTF-8 rồi
    chạy lại set_password), chưa bắt gõ mật khẩu, không traceback, không đường dẫn, không nội dung
    ``.env``; file giữ nguyên từng byte."""
    env_path = tmp_path / ".env"
    env_path.write_bytes(content)
    code, script = run_set_password(project_root, monkeypatch, env_path, never_asked)
    assert code == 1
    shown = capsys.readouterr()
    assert shown.out.strip() == f"Chưa đặt được mật khẩu. {script.MSG_ENV_NOT_UTF8}"
    assert script.MSG_ENV_NOT_UTF8.endswith("lưu đè rồi chạy lại set_password.")
    assert_no_leak(shown.out + shown.err, project_root, env_path, tmp_path)
    assert env_path.read_bytes() == content


@pytest.mark.parametrize("bom", [b"", b"\xef\xbb\xbf"], ids=["utf8", "utf8-bom"])
def test_set_password_after_resave_as_utf8_works(project_root, tmp_path, monkeypatch, bom):
    """Làm theo câu báo (lưu lại UTF-8, có hay không BOM) rồi chạy lại: mật khẩu mới được lưu, app
    đọc được, các dòng khác giữ nguyên."""
    env_path = tmp_path / ".env"
    env_path.write_bytes(bom + TEXT.encode("utf-8"))
    code, _ = run_set_password(project_root, monkeypatch, env_path, typed)
    assert code == 0
    settings = load_settings(env_path, environ={})
    assert verify_password(PASSWORD, settings.password_hash)
    assert settings.image_folders == (Path(FOLDER),) and settings.anthropic_api_key == FAKE_KEY


def test_set_password_cannot_write_env(project_root, tmp_path, monkeypatch, capsys):
    """Đọc được mà không ghi được ``.env`` (chỉ đọc, đang bị khóa): sau khi gõ mật khẩu thì báo câu
    cố định kèm tên loại lỗi, không traceback, không đường dẫn; file giữ nguyên."""

    class Unwritable(type(tmp_path)):
        def write_text(self, *args, **kwargs):
            raise PermissionError(13, "Permission denied", str(self))

    env_path = Unwritable(tmp_path / ".env")
    env_path.write_bytes(TEXT.encode("utf-8"))
    code, _ = run_set_password(project_root, monkeypatch, env_path, typed)
    assert code == 1
    shown = capsys.readouterr()
    assert "Chưa lưu mật khẩu mới. Không ghi được file .env (PermissionError)." in shown.out
    assert_no_leak(shown.out + shown.err, project_root, env_path, tmp_path)
    assert env_path.read_text(encoding="utf-8") == TEXT


def test_set_password_env_unreadable_gives_fixed_message(project_root, tmp_path):
    """``.env`` có mà không mở được để đọc: câu cố định kèm tên loại lỗi, không đường dẫn."""
    script = load_script(project_root)

    class Unreadable(type(tmp_path)):
        def read_text(self, *args, **kwargs):
            raise PermissionError(13, "Permission denied", str(self))

    env_path = Unreadable(tmp_path / ".env")
    env_path.write_bytes(TEXT.encode("utf-8"))
    with pytest.raises(ConfigError) as given:
        script.read_env_lines(env_path)
    assert str(given.value).startswith("Không đọc được file .env (PermissionError).")
    assert_no_leak(str(given.value), env_path, tmp_path)


def test_set_password_cannot_create_env_from_template(project_root, tmp_path, monkeypatch):
    """Chưa có ``.env`` mà chép ``.env.example`` sang không được: câu cố định, không đường dẫn."""
    script = load_script(project_root)
    template = tmp_path / ".env.example"
    template.write_text("APP_PASSWORD_HASH=\n", encoding="utf-8")
    env_path = tmp_path / ".env"

    def no_copy(*args, **kwargs):
        raise PermissionError(13, "Permission denied", str(env_path))

    monkeypatch.setattr(script.shutil, "copyfile", no_copy)
    with pytest.raises(ConfigError) as given:
        script.set_env_value(env_path, script.KEY, "moi", template)
    assert str(given.value).startswith("Không ghi được file .env (PermissionError).")
    assert_no_leak(str(given.value), env_path, tmp_path)
    assert not env_path.exists()


def test_print_mode_does_not_need_env(project_root, tmp_path, monkeypatch, capsys):
    """Canh: ``--print`` (chỉ in mã băm, không ghi file) vẫn chạy khi ``.env`` hỏng, không đụng
    file."""
    env_path = tmp_path / ".env"
    env_path.write_bytes(BAD_FILES["ansi-cp1252"])
    code, script = run_set_password(project_root, monkeypatch, env_path, typed, ["--print"])
    assert code == 0
    assert f"{script.KEY}=" in capsys.readouterr().out
    assert env_path.read_bytes() == BAD_FILES["ansi-cp1252"]
