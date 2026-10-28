"""T-090 (Thợ Máy), SL-T041-8: câu báo đúng nghĩa cho ký tự phần mềm chưa nhận ra trong chữ SEO.

Soi Lỗi T-041 tìm ra: emoji mới hơn bảng Unicode của Python (emoji Unicode 16 như U+1FAE9 với
Python 3.12, bảng 15.0) là ký tự «chưa gán» (loại Cn), bị Chặn với câu «có ký tự điều khiển hoặc
ký tự lạ (không nhìn thấy…)», sai với emoji nhìn thấy rõ. Lá Chắn T-041 quyết **giữ Chặn**
(``normalize_meta`` và client WordPress bỏ ký tự này: cho qua là lặng lẽ mất ký tự khi ghi), chỉ
sửa câu báo. Ký tự điều khiển, surrogate lẻ, ký tự riêng, «không phải ký tự» (U+FFFE, U+FDD0…: không
bao giờ được gán) và mã để dành cho ký tự vô hình (U+FFF0, U+E0080…) giữ câu cũ.

Lượt 2 (đề xuất 2): câu hỏi, trả lời của mục Hỏi đáp (schema FAQ) tách câu báo cùng cách, vẫn Chặn
như điều kiện 1 của Lá Chắn T-038.

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
from seo_app.onpage.schema import _check_text as faq_check_text
from seo_app.onpage.schema import build_faq_page, normalize_text
from seo_app.storage import DraftPart
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


# ============================================================ lượt 2: mục Hỏi đáp (schema FAQ)

SITE = "https://suachuacuasat.com"
FAQ_Q = "Cổng inox bị xệ có sửa được không?"
FAQ_A = "Được, thay bản lề và chỉnh lại cánh trong một buổi."
# ``normalize_text`` của schema bỏ hẳn ký tự «mặc định bỏ qua» U+2065, U+FFF0–U+FFF8 như ký tự vô
# hình loại Cf (thiết kế T-038), nên chúng không tới bộ kiểm ký tự lạ: bỏ khỏi danh sách FAQ.
DROPPED_BY_FAQ = (chr(0x2065), chr(0xFFF0), chr(0xFFF8))
FAQ_OLD_MESSAGE_CHARS = [c for c in OLD_MESSAGE_CHARS if c not in DROPPED_BY_FAQ]


def faq_with(ch: str, where: str):
    q = FAQ_Q.replace("bị xệ", f"bị {ch} xệ") if where == "q" else FAQ_Q
    a = FAQ_A.replace("Được,", f"Được {ch},") if where == "a" else FAQ_A
    article = f"# Bài\n\nMở bài.\n\n## Hỏi đáp\n\n### {q}\n\n{a}\n"
    return build_faq_page([(q, a)], article_text=article, site_url=SITE)


@python_without_new_emoji
@pytest.mark.parametrize("where", ["q", "a"])
@pytest.mark.parametrize("ch", NEW_EMOJI + UNASSIGNED, ids=ids(NEW_EMOJI + UNASSIGNED))
def test_faq_unknown_char_stays_blocked_with_accurate_message(ch, where):
    """Câu hỏi hay trả lời có ký tự chưa nhận ra: vẫn Chặn, không dựng JSON-LD (Lá Chắn T-038 đk
    1); câu báo nói phần mềm chưa nhận ra ký tự, chỉ cách sửa trong bài, không nói «không nhìn
    thấy», không chép lại ký tự."""
    result = faq_with(ch, where)
    assert result.blocked and result.json_ld is None
    (issue,) = result.issues
    label = "Câu hỏi 1" if where == "q" else "Trả lời 1"
    assert issue.message.startswith(f"{label}: có ký tự phần mềm chưa nhận ra")
    assert "biểu tượng cảm xúc" in issue.message and "Sửa trong bài" in issue.message
    assert INVISIBLE not in issue.message and "điều khiển" not in issue.message
    assert ch not in issue.message


@pytest.mark.parametrize("where", ["q", "a"])
@pytest.mark.parametrize("ch", FAQ_OLD_MESSAGE_CHARS, ids=ids(FAQ_OLD_MESSAGE_CHARS))
def test_faq_control_invisible_and_noncharacters_keep_old_message(ch, where):
    """Ký tự điều khiển, surrogate lẻ, ký tự riêng, «không phải ký tự», mã để dành cho ký tự vô
    hình còn lại sau chuẩn hóa: Chặn với câu «ký tự điều khiển hoặc ký tự lạ (không nhìn thấy…)»."""
    result = faq_with(ch, where)
    assert result.blocked and result.json_ld is None
    (issue,) = result.issues
    assert OLD in issue.message and INVISIBLE in issue.message and "Sửa trong bài" in issue.message
    assert NEW not in issue.message
    assert ch not in issue.message


@pytest.mark.parametrize("ch", DROPPED_BY_FAQ, ids=ids(DROPPED_BY_FAQ))
def test_faq_drops_reserved_ignorable_chars_as_before(ch):
    """Canh: ba mã «mặc định bỏ qua» chưa gán vẫn bị bỏ như trước (không Chặn), JSON-LD không có
    chúng; lượt 2 chỉ đổi câu báo, không đổi chuẩn hóa."""
    result = faq_with(ch, "a")
    assert not result.blocked and result.json_ld is not None
    assert ch not in result.json_ld


def test_faq_blocks_exactly_the_same_chars_as_before():
    """Canh: tách câu báo không đổi tập ký tự bị Chặn ở FAQ: Chặn đúng khi chữ đã chuẩn hóa còn ký
    tự loại Cc, Cs, Co, Cn (Lá Chắn T-038 đk 1). Quét mỗi 11 mã một trên cả bảng mã."""
    odd_categories = {"Cc", "Cs", "Co", "Cn"}
    for code in range(0, 0x110000, 11):
        text = f"Cửa{chr(code)}cuốn"
        issues, _ = faq_check_text(text, label="Câu hỏi 1", max_length=300, article=None)
        blocked = any(OLD in issue.message or NEW in issue.message for issue in issues)
        expected = any(unicodedata.category(c) in odd_categories for c in normalize_text(text))
        assert blocked is expected, f"U+{code:04X}"


@python_without_new_emoji
def test_faq_both_kinds_give_two_issues():
    result = faq_with(f"{chr(0x1B)}{NEW_EMOJI[0]}", "a")
    assert result.blocked and result.json_ld is None
    messages = [issue.message for issue in result.issues]
    assert len(messages) == 2
    assert OLD in messages[0] and NEW in messages[1]


@python_without_new_emoji
def test_seo_step_faq_shows_accurate_message_for_new_emoji(project_root):
    """Bước SEO: mục Hỏi đáp của bài có emoji mới trong câu trả lời: không có JSON-LD, câu báo dưới
    phần Schema là câu mới (không có «không nhìn thấy»)."""
    snap = seo_ui.ui.article()
    answer = FAQ_A.replace("Được,", f"Được {NEW_EMOJI[0]},")
    snap.parts.append(DraftPart(heading="Hỏi đáp", versions=[f"### {FAQ_Q}\n\n{answer}"]))
    at = seo_ui.to_seo(project_root, snap)
    faq = [c.value for c in at.caption if "Trả lời 1" in c.value]
    assert len(faq) == 1
    assert escape_markdown(faq_with(NEW_EMOJI[0], "a").issues[0].message) in faq[0]
    assert NEW in faq[0] and INVISIBLE not in faq[0]
    assert not [c for c in at.code if c.language == "json"]
    assert not at.exception
