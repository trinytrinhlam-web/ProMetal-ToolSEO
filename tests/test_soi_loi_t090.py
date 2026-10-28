"""Soi Lỗi T-090: câu báo emoji mới trong chữ SEO (SL-T041-8), ``.env`` không phải UTF-8
(SL-T084-1); lượt 2: câu báo ký tự lạ ở FAQ, ``set_password`` khi ``.env`` sai bảng mã.

Ngoài test của Thợ Máy (``tests/test_t090_meta_emoji_moi.py``, ``tests/test_t090_env_bang_ma.py``):

- emoji mới nằm trong chuỗi ghép (dấu nối ZWJ, VS16), lặp lại, ở đầu, ở cuối sát đuôi thương hiệu:
  vẫn Chặn, đúng **một** câu mới; emoji quen (cả emoji Unicode 15.0 mới nhất Python 3.12 biết, chuỗi
  ghép, màu da, cờ, phím số) và tiếng Việt dựng sẵn hay tổ hợp (NFD): không bị chặn oan;
- FAQ nhiều câu hỏi: câu báo đúng số thứ tự, đúng loại;
- app với ``.env`` có byte lạ khác (surrogate kiểu CESU-8, mã hóa dài thừa, byte hỏng nằm sâu trong
  một dòng chú thích, «ANSI» tiếng Việt cp1258): trang báo lỗi câu cố định; ``.env`` bị chương
  trình khác **khóa thật** (Windows): app và ``set_password`` báo câu cố định, mở khóa là dùng được;
- ``set_password`` với ``.env`` UTF-8 có BOM mà dòng mã băm nằm ngay dòng đầu.

Ký tự lạ viết bằng ``chr(0x…)``, byte bằng ``bytes([...])`` (công cụ soạn có thể đổi mã thoát
thành ký tự thật). Chỉ dùng ``.env`` giả trong thư mục tạm; không gọi AI hay mạng.
"""

from __future__ import annotations

import os
import unicodedata
from pathlib import Path

import pytest
import test_settings_images as si
from streamlit.testing.v1 import AppTest
from test_hash_password_script import load_script

import seo_app.config as config
from seo_app.auth import hash_password, verify_password
from seo_app.config import MSG_ENV_NOT_UTF8, MSG_ENV_UNREADABLE, load_settings
from seo_app.onpage.meta import Level, check_description, check_title
from seo_app.onpage.schema import build_faq_page

IS_WINDOWS = os.name == "nt"
NEW = "chưa nhận ra"
OLD = "ký tự điều khiển hoặc ký tự lạ"
INVISIBLE = "không nhìn thấy"
TITLE = "Cửa sắt bị xệ tự kiểm tra hay nên gọi thợ?"
DESC = (
    "Cửa sắt bị xệ cạ nền khi đóng mở thường do bản lề mòn. Xem cách tự kiểm tra bản lề, lúc nào "
    "chỉnh được và lúc nào nên gọi thợ hàn lại tận nhà."
)

ZWJ, VS16 = chr(0x200D), chr(0xFE0F)
FACE_BAGS, FINGERPRINT = chr(0x1FAE9), chr(0x1FAC6)  # emoji Unicode 16 (2024)
FIRE, HEART, BIRD = chr(0x1F525), chr(0x2764), chr(0x1F426)
python_without_new_emoji = pytest.mark.skipif(
    unicodedata.category(FACE_BAGS) != "Cn",
    reason="Python này đã biết emoji Unicode 16 (không còn là ký tự chưa gán)",
)


def messages(check) -> str:
    return " ".join(check.messages)


# ===================================================== SL-T041-8: emoji mới trong chuỗi ghép


NEW_CASES = [
    ("vs16", f"{FACE_BAGS}{VS16}", "giua"),
    ("zwj-sau", f"{FACE_BAGS}{ZWJ}{FIRE}", "giua"),
    ("zwj-truoc", f"{HEART}{VS16}{ZWJ}{FINGERPRINT}", "giua"),
    ("lap-3-lan", FACE_BAGS * 3, "giua"),
    ("hai-emoji-moi", f"{FACE_BAGS} {FINGERPRINT}", "giua"),
    ("o-dau", FACE_BAGS, "dau"),
    ("o-cuoi", FACE_BAGS, "cuoi"),
]


def place(text: str, piece: str, where: str) -> str:
    if where == "dau":
        return f"{piece} {text}"
    if where == "cuoi":
        return f"{text} {piece}"
    return text.replace("xệ ", f"xệ {piece} ", 1)


@python_without_new_emoji
@pytest.mark.parametrize(
    ("piece", "where"), [c[1:] for c in NEW_CASES], ids=[c[0] for c in NEW_CASES]
)
def test_new_emoji_in_sequences_blocked_with_one_new_message(piece, where):
    """Emoji mới nằm trong chuỗi ghép, lặp lại, ở đầu, ở cuối (sát đuôi « | Pro-Metal» khi title
    còn chỗ): vẫn Chặn, đúng một câu báo mới (không lặp, không kèm câu «không nhìn thấy» vì dấu
    nối ZWJ, VS16 không phải ký tự lạ), câu không chép lại ký tự."""
    title = place(TITLE, piece, where)
    description = place(DESC, piece, where)
    for check in (check_title(title), check_title(title, ""), check_description(description)):
        assert check.level is Level.BLOCK
        odd = [m for m in check.messages if NEW in m or OLD in m]
        assert len(odd) == 1 and NEW in odd[0], check.messages
        assert INVISIBLE not in messages(check)
        assert FACE_BAGS not in messages(check) and FINGERPRINT not in messages(check)


KNOWN = {
    "unicode15-mat-rung": chr(0x1FAE8),
    "unicode15-tim-hong": chr(0x1FA77),
    "unicode15-ngong": chr(0x1FABF),
    "unicode15-con-nai": chr(0x1FACE),
    "zwj-phuong-hoang": f"{BIRD}{ZWJ}{FIRE}",
    "zwj-gia-dinh": f"{chr(0x1F468)}{ZWJ}{chr(0x1F469)}{ZWJ}{chr(0x1F467)}",
    "tim-lua": f"{HEART}{VS16}{ZWJ}{FIRE}",
    "mau-da": f"{chr(0x1F44D)}{chr(0x1F3FD)}",
    "co-viet-nam": f"{chr(0x1F1FB)}{chr(0x1F1F3)}",
    "phim-so": f"1{VS16}{chr(0x20E3)}",
    "sao-tick": f"{chr(0x2B50)} {chr(0x2705)}",
}


@pytest.mark.parametrize("emoji", KNOWN.values(), ids=KNOWN.keys())
def test_known_emoji_not_blocked_as_odd(emoji):
    """Không chặn oan: emoji Python 3.12 đã biết (kể cả Unicode 15.0), chuỗi ghép, màu da, cờ,
    phím số không có câu báo ký tự lạ nào (mức có thể là Cảnh báo vì độ dài, không phải Chặn vì
    ký tự)."""
    title = TITLE.replace("xệ ", f"xệ {emoji} ")
    for check in (check_title(title), check_description(DESC.replace("xệ ", f"xệ {emoji} "))):
        assert NEW not in messages(check) and OLD not in messages(check), check.messages
        assert check.level is not Level.BLOCK


@pytest.mark.parametrize("form", ["NFC", "NFD"])
def test_vietnamese_all_tones_not_blocked(form):
    """Tiếng Việt đủ dấu, dựng sẵn (NFC) hay tổ hợp (NFD, gõ trên Mac hay chép từ PDF): không bị
    chặn oan vì ký tự lạ."""
    text = unicodedata.normalize(
        form, "Ống đồng ửng đỏ, ầm ĩ, ẵm ỹ, ợ ụ ữ, Đà Nẵng, Huế, Thủ Đức: sửa cửa sắt ổn"
    )
    for check in (check_title(text), check_description(f"{DESC} {text}")):
        assert NEW not in messages(check) and OLD not in messages(check), check.messages


# ============================================================== FAQ nhiều câu hỏi (lượt 2)

SITE = "https://suachuacuasat.com"
PAIRS = [
    ("Cổng inox bị xệ có sửa được không?", "Được, thay bản lề và chỉnh lại cánh trong một buổi."),
    ("Bản lề cổng nên thay loại nào?", "Nên dùng bản lề cối inox 304, chịu được mưa nắng."),
    ("Sửa cổng mất bao lâu?", "Thường xong trong buổi sáng nếu không phải hàn lại khung."),
]


def _article(pairs) -> str:
    return "## Câu hỏi thường gặp\n\n" + "\n\n".join(f"### {q}\n\n{a}" for q, a in pairs)


@python_without_new_emoji
def test_faq_messages_name_the_right_question_and_kind():
    """FAQ ba câu: ký tự điều khiển ở «Câu hỏi 2», emoji mới ở «Trả lời 3»: Chặn, mỗi chỗ đúng một
    câu báo đúng loại, đúng số thứ tự; câu không đúng chỗ không bị báo."""
    pairs = [list(p) for p in PAIRS]
    pairs[1][0] = pairs[1][0].replace("nên", f"n{chr(0x1B)}ên")
    pairs[2][1] = pairs[2][1].replace("sáng", f"sáng {FACE_BAGS}")
    pairs = [tuple(p) for p in pairs]
    result = build_faq_page(pairs, article_text=_article(pairs), site_url=SITE)
    assert result.blocked and result.json_ld is None
    odd = [i.message for i in result.issues if NEW in i.message or OLD in i.message]
    assert len(odd) == 2, odd
    assert odd[0].startswith("Câu hỏi 2:") and OLD in odd[0] and INVISIBLE in odd[0]
    assert odd[1].startswith("Trả lời 3:") and NEW in odd[1] and INVISIBLE not in odd[1]
    assert not any(i.message.startswith(("Câu hỏi 1", "Trả lời 1")) for i in result.issues)


# ======================================================== .env: byte lạ khác, trang báo lỗi

PASSWORD = "-".join(["mat", "khau", "thu", "t090", "soi", "loi"])  # mật khẩu thử, viết tách
TEXT = "APP_TIMEZONE=Asia/Ho_Chi_Minh\nIMAGE_FOLDERS=C:/Anh cong trinh\n"
BAD = {
    "surrogate-cesu8": b"IMAGE_FOLDERS=C:/" + bytes([0xED, 0xA0, 0x80]) + b"x\n",
    "dai-thua": b"IMAGE_FOLDERS=C:/" + bytes([0xC0, 0x80]) + b"x\n",
    "hong-sau-chu-thich": TEXT.encode() * 40 + b"# ghi ch" + bytes([0xFA]) + b" sau\n",
    # cp1258 («ANSI» của Windows tiếng Việt): A + dấu hỏi tách rời (0xD2), ô (0xF4)
    "ansi-cp1258": b"IMAGE_FOLDERS=C:/A" + bytes([0xD2]) + b"nh c" + bytes([0xF4]) + b"ng tr\n",
}


def open_app(project_root, env_path: Path, monkeypatch) -> AppTest:
    monkeypatch.delenv("APP_PASSWORD_HASH", raising=False)
    monkeypatch.setattr(config, "DEFAULT_ENV_FILE", env_path)
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    return at.run()


def assert_error_page(at, message: str, *paths: Path) -> None:
    assert not at.exception, [e.value for e in at.exception]
    assert [e.value for e in at.error] == [message]
    assert not at.text_input  # chưa tới màn đăng nhập
    shown = si.page_strings(at)
    for text in ("Traceback", "codec", "decode", "byte", "position", "Errno", "IMAGE_FOLDERS"):
        assert text not in shown, text
    for path in (*paths, Path.home()):
        assert str(path) not in shown and path.as_posix() not in shown, path


@pytest.mark.parametrize("content", BAD.values(), ids=BAD.keys())
def test_app_error_page_for_other_bad_bytes(project_root, tmp_path, monkeypatch, content):
    """``.env`` có byte lạ khác cách Notepad «ANSI»: surrogate mã hóa kiểu CESU-8, mã hóa dài thừa,
    một byte hỏng nằm sâu trong dòng chú thích sau 80 dòng đúng, chữ cp1258 tiếng Việt: trang báo
    lỗi đúng câu cố định, không traceback, không đường dẫn, không nội dung ``.env``."""
    env_path = tmp_path / ".env"
    env_path.write_bytes(content)
    at = open_app(project_root, env_path, monkeypatch)
    assert_error_page(at, MSG_ENV_NOT_UTF8, project_root, env_path, tmp_path)


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
def test_app_with_env_locked_by_other_program_then_unlocked(project_root, tmp_path, monkeypatch):
    """``.env`` đang bị chương trình khác khóa (khóa thật, không giả lỗi): trang báo lỗi «Không đọc
    được file .env (PermissionError)…», không traceback, không đường dẫn. Mở khóa, tải lại trang:
    màn đăng nhập, đăng nhập được."""
    env_path = tmp_path / ".env"
    env_path.write_text(
        TEXT + f"APP_PASSWORD_HASH={hash_password(PASSWORD, iterations=1_000)}\n", encoding="utf-8"
    )
    handle = _lock(env_path)
    try:
        at = open_app(project_root, env_path, monkeypatch)
        expected = MSG_ENV_UNREADABLE.format(error="PermissionError")
        assert_error_page(at, expected, project_root, env_path, tmp_path)
    finally:
        _unlock(handle, env_path)
    at.run()
    assert not at.exception and not at.error
    at.text_input[0].input(PASSWORD)
    at.button[0].click().run()
    assert at.session_state["authenticated"]


# ================================================================ set_password (lượt 2)


def never_asked(prompt=""):
    raise AssertionError("không được bắt gõ mật khẩu khi .env hỏng")


@pytest.mark.skipif(not IS_WINDOWS, reason="khóa vùng byte của Windows (msvcrt)")
def test_set_password_with_env_locked_stops_before_asking(
    project_root, tmp_path, monkeypatch, capsys
):
    """``set_password`` khi ``.env`` đang bị khóa thật: báo ngay câu cố định kèm tên loại lỗi, chưa
    bắt gõ mật khẩu, file giữ nguyên; mở khóa rồi chạy lại thì lưu được."""
    env_path = tmp_path / ".env"
    env_path.write_text(TEXT, encoding="utf-8")
    before = env_path.read_bytes()
    script = load_script(project_root)
    monkeypatch.setattr(script, "DEFAULT_ENV_FILE", env_path)
    monkeypatch.setattr(script.getpass, "getpass", never_asked)
    handle = _lock(env_path)
    try:
        assert script.main([]) == 1
    finally:
        _unlock(handle, env_path)
    out = capsys.readouterr()
    expected = script.MSG_ENV_UNREADABLE.format(error="PermissionError")
    assert out.out.strip() == f"Chưa đặt được mật khẩu. {expected}"
    assert str(env_path) not in out.out + out.err and "Traceback" not in out.out + out.err
    assert env_path.read_bytes() == before
    monkeypatch.setattr(script.getpass, "getpass", lambda prompt="": PASSWORD)
    assert script.main([]) == 0
    assert verify_password(PASSWORD, load_settings(env_file=env_path, environ={}).password_hash)


def test_set_password_bom_hash_on_first_line(project_root, tmp_path, monkeypatch):
    """``.env`` lưu lại «UTF-8 with BOM» (như câu báo dặn) mà dòng ``APP_PASSWORD_HASH`` nằm ngay
    dòng đầu: đặt mật khẩu mới xong, app đăng nhập được bằng mật khẩu mới (dù dòng cũ còn đó, xem
    báo cáo)."""
    env_path = tmp_path / ".env"
    env_path.write_bytes(bytes([0xEF, 0xBB, 0xBF]) + b"APP_PASSWORD_HASH=cu\n" + TEXT.encode())
    script = load_script(project_root)
    monkeypatch.setattr(script, "DEFAULT_ENV_FILE", env_path)
    monkeypatch.setattr(script.getpass, "getpass", lambda prompt="": PASSWORD)
    assert script.main([]) == 0
    settings = load_settings(env_file=env_path, environ={})
    assert verify_password(PASSWORD, settings.password_hash)
    assert settings.image_folders == (Path("C:/Anh cong trinh"),)
