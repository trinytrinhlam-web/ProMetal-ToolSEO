"""T-090 (Thợ Máy), SL-T041-8: câu báo đúng nghĩa cho ký tự phần mềm chưa nhận ra trong chữ SEO.

Soi Lỗi T-041 tìm ra: emoji mới hơn bảng Unicode của Python (emoji Unicode 16 như U+1FAE9 với
Python 3.12, bảng 15.0) là ký tự «chưa gán» (loại Cn), bị Chặn với câu «có ký tự điều khiển hoặc
ký tự lạ (không nhìn thấy…)», sai với emoji nhìn thấy rõ. Lá Chắn T-041 quyết **giữ Chặn**
(``normalize_meta`` và client WordPress bỏ ký tự này: cho qua là lặng lẽ mất ký tự khi ghi), chỉ
sửa câu báo. Ký tự điều khiển, surrogate lẻ, ký tự riêng, «không phải ký tự» (U+FFFE, U+FDD0…: không
bao giờ được gán) và mã để dành cho ký tự vô hình (U+FFF0, U+E0080…) giữ câu cũ.

Không gọi AI hay mạng; test giao diện dùng fixture của ``tests/test_t041_seo_ui.py``.
"""

from __future__ import annotations

import unicodedata

import pytest
import test_t041_seo_ui as seo_ui

from seo_app.onpage.meta import (
    BRAND_SUFFIX,
    Level,
    accept_ai_description,
    accept_ai_title,
    check_description,
    check_title,
    has_odd_chars,
    normalize_meta,
    odd_char_messages,
    siteseo_copy,
)
from seo_app.text import escape_markdown

# Fixture dùng chung: mật khẩu thử, cache ảnh xem trước tạm, cache danh sách bài tạm.
env = seo_ui.env
previews = seo_ui.previews
site_cache = seo_ui.site_cache

KEYWORD = "cửa sắt bị xệ"
CLEAN_TITLE = "Cửa sắt bị xệ tự kiểm tra hay nên gọi thợ?"
CLEAN_DESC = (
    "Cửa sắt bị xệ cạ nền khi đóng mở thường do bản lề mòn. Xem cách tự kiểm tra bản lề, lúc nào "
    "chỉnh được và lúc nào nên gọi thợ hàn lại tận nhà."
)
NEW = "chưa nhận ra"  # câu mới: ký tự phần mềm chưa nhận ra, có thể là biểu tượng rất mới
OLD = "ký tự điều khiển hoặc ký tự lạ"  # câu cũ: ký tự điều khiển, vô hình, ký tự riêng
INVISIBLE = "không nhìn thấy"


def title_with(ch: str) -> str:
    return CLEAN_TITLE.replace("xệ ", f"xệ {ch} ")


def desc_with(ch: str) -> str:
    return CLEAN_DESC.replace("xệ ", f"xệ {ch} ")


def ids(chars) -> list[str]:
    return [f"U+{ord(c):04X}" for c in chars]


# Emoji Unicode 16 (2024): mặt có bọng mắt, dấu vân tay, vết bắn tóe, cây trụi lá.
NEW_EMOJI = [chr(0x1FAE9), chr(0x1FAC6), chr(0x1FADF), chr(0x1FABE)]
python_without_new_emoji = pytest.mark.skipif(
    any(unicodedata.category(c) != "Cn" for c in NEW_EMOJI),
    reason="Python này đã biết emoji Unicode 16 (không còn là ký tự chưa gán)",
)
# Mã chưa gán khác (có thể được gán thành ký tự nhìn thấy): vùng chữ Hy Lạp, mặt phẳng 2, 14.
UNASSIGNED = [chr(0x0378), chr(0x2FFFD), chr(0xE1000)]
# «Không phải ký tự»: 32 mã U+FDD0–U+FDEF và hai mã cuối của mỗi mặt phẳng trong 17 mặt phẳng.
NONCHARACTERS = [chr(c) for c in range(0xFDD0, 0xFDF0)] + [
    chr(plane * 0x10000 + low) for plane in range(17) for low in (0xFFFE, 0xFFFF)
]
# Mã để dành cho ký tự vô hình (Unicode «mặc định bỏ qua», hiện ra không nhìn thấy).
RESERVED_INVISIBLE = [chr(c) for c in (0x2065, 0xFFF0, 0xFFF8, 0xE0000, 0xE0002, 0xE001F)] + [
    chr(c) for c in (0xE0080, 0xE00FF, 0xE01F0, 0xE0FFF)
]
# Điều khiển (Cc), surrogate lẻ (Cs), ký tự riêng (Co).
CONTROL_AND_PRIVATE = [chr(c) for c in (0x00, 0x1B, 0x7F, 0x9F, 0xD800, 0xDFFF, 0xE000, 0x10FFFD)]
OLD_MESSAGE_CHARS = CONTROL_AND_PRIVATE + NONCHARACTERS + RESERVED_INVISIBLE


def messages_of(check) -> str:
    return " ".join(check.messages)


# ============================================================ câu báo theo loại ký tự


@python_without_new_emoji
@pytest.mark.parametrize("ch", NEW_EMOJI + UNASSIGNED, ids=ids(NEW_EMOJI + UNASSIGNED))
def test_unknown_char_stays_blocked_with_accurate_message(ch):
    """Ô title (có và không đuôi thương hiệu), ô description: vẫn Chặn, câu báo nói phần mềm chưa
    nhận ra ký tự (không nói «không nhìn thấy», không nói ký tự điều khiển), không chép lại ký tự;
    chữ ``value`` đã bỏ ký tự, khung «Chép sang SiteSEO» không cho chép."""
    checks = (
        check_title(title_with(ch)),
        check_title(title_with(ch), ""),
        check_description(desc_with(ch)),
    )
    for check in checks:
        assert check.level is Level.BLOCK
        message = messages_of(check)
        assert NEW in message and "biểu tượng cảm xúc" in message
        assert INVISIBLE not in message and "điều khiển" not in message
        assert ch not in message and ch not in check.value
    copy = siteseo_copy(title_with(ch), desc_with(ch), "cua-sat-bi-xe")
    assert copy.title is None and copy.description is None and copy.slug == "cua-sat-bi-xe"


@python_without_new_emoji
@pytest.mark.parametrize("emoji", NEW_EMOJI, ids=ids(NEW_EMOJI))
def test_new_emoji_is_still_dropped_where_text_is_written(emoji):
    """Lý do giữ Chặn (Lá Chắn T-041): chữ đem ghi (``normalize_meta``, cũng là bước chuẩn hóa của
    client WordPress) mất emoji; gợi ý AI có emoji đó vẫn bị bỏ, bản không có emoji thì nhận."""
    assert normalize_meta(title_with(emoji)) == CLEAN_TITLE
    assert accept_ai_title(title_with(emoji), KEYWORD) is None
    assert accept_ai_description(desc_with(emoji), KEYWORD) is None
    assert accept_ai_title(CLEAN_TITLE, KEYWORD) == CLEAN_TITLE + BRAND_SUFFIX
    assert accept_ai_description(CLEAN_DESC, KEYWORD) == CLEAN_DESC


@pytest.mark.parametrize("ch", OLD_MESSAGE_CHARS, ids=ids(OLD_MESSAGE_CHARS))
def test_control_invisible_and_noncharacters_keep_old_message(ch):
    """Ký tự điều khiển, surrogate lẻ, ký tự riêng, «không phải ký tự», mã để dành cho ký tự vô
    hình: Chặn với câu cũ (không nhìn thấy, thường do dán), không phải câu «chưa nhận ra»."""
    for check in (check_title(title_with(ch)), check_description(desc_with(ch))):
        assert check.level is Level.BLOCK
        message = messages_of(check)
        assert OLD in message and INVISIBLE in message
        assert NEW not in message
        assert ch not in message


@python_without_new_emoji
def test_both_kinds_give_both_messages():
    """Chữ có cả ký tự điều khiển lẫn emoji mới: hai câu, mỗi loại một câu (mỗi câu một vấn đề)."""
    text = title_with(f"{chr(0x1B)}{NEW_EMOJI[0]}")
    check = check_title(text, "")
    assert check.level is Level.BLOCK
    assert len(check.messages) == 2
    assert OLD in check.messages[0] and NEW in check.messages[1]
    assert odd_char_messages("Meta title", text) == list(check.messages)


@pytest.mark.parametrize(
    "text",
    [
        CLEAN_TITLE,
        "Cửa\tsắt\nbị\x0bxệ\x1c\x85gọn",
        "Cửa sắt ⭐ ✅ 🫨 \N{HEAVY BLACK HEART}\N{VARIATION SELECTOR-16} bị xệ",
        "tự\N{ZERO WIDTH SPACE} kiểm",
    ],
    ids=["chu-thuong", "khoang-trang", "emoji-quen", "ZWSP"],
)
def test_no_message_without_odd_chars(text):
    """Chữ thường, khoảng trắng loại điều khiển (tab, xuống dòng…), emoji quen, ký tự vô hình loại
    Cf (bị bỏ, không Chặn): không có câu báo ký tự lạ."""
    assert odd_char_messages("Meta title", text) == []
    assert not has_odd_chars(text)


def test_messages_cover_exactly_what_has_odd_chars_sees():
    """Câu báo và ``has_odd_chars`` (dùng ở gợi ý AI, đuôi thương hiệu, từ khóa chính) thấy cùng
    các ký tự: quét đều cả bảng mã (mỗi 11 mã một) và mọi mã của các nhóm trên."""
    chars = [chr(c) for c in range(0, 0x110000, 11)]
    chars += NEW_EMOJI + UNASSIGNED + OLD_MESSAGE_CHARS + [" ", "\t", "\x85", "a", "ữ"]
    for ch in chars:
        messages = odd_char_messages("X", ch)
        assert bool(messages) is has_odd_chars(ch), f"U+{ord(ch):04X}"
        assert len(messages) <= 1


def test_noncharacter_list_is_complete_and_cn():
    """Danh sách «không phải ký tự» của test đủ 66 mã, Python xếp loại Cn (nếu Python sau này xếp
    khác thì câu báo của chúng cần xem lại)."""
    assert len(set(NONCHARACTERS)) == 66
    assert {unicodedata.category(c) for c in NONCHARACTERS + RESERVED_INVISIBLE} == {"Cn"}


# ============================================================ trên trang SEO


@python_without_new_emoji
def test_seo_step_shows_accurate_message_for_new_emoji(project_root):
    """Bước SEO của Soạn bài: tự gõ title có emoji mới (chưa có khóa AI) thì nhãn «Chặn», câu dưới
    ô là câu mới (không có «không nhìn thấy»), khung chép không chép title đó."""
    at = seo_ui.to_seo(project_root)
    title = title_with(NEW_EMOJI[0])
    seo_ui.run_ok(at.text_input(key="seo_title").input(title).run())
    captions = [c.value for c in at.caption]
    title_captions = [c for c in captions if c.startswith("Meta title")]
    assert escape_markdown(odd_char_messages("Meta title", title)[0]) in title_captions
    assert not any(INVISIBLE in c for c in title_captions)
    assert any(b.startswith(":red-badge[Chặn") for b in seo_ui.badges(at))
    assert any(c.startswith("Tiêu đề SEO: chưa chép được.") for c in captions)
    assert not any(NEW_EMOJI[0] in c.value or CLEAN_TITLE in c.value for c in at.code)
    assert not at.exception
