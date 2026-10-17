"""Soi Lỗi T-043: thử xấu bộ lọc hồ sơ sau khi nới mẫu nhãn (``_GAP``) và viết lại
``_ends_with_partial_tag``. Không gọi mạng."""

import pytest

from seo_app.content import rules
from seo_app.content.rules import confirmed_profile
from tests.timing import assert_scales_linearly


def _item_hidden(tag: str) -> bool:
    out = confirmed_profile(f"- trước\n- x {tag}\n- sau")
    assert out.startswith("- trước") and out.endswith("- sau")
    return "- x" not in out


# --- 3 lỗi của phiếu: kiểm lại theo cách khác với test của Thợ Máy -----------------------------


@pytest.mark.parametrize("blanks", ["\n", "\n\n\n", "\n  \n\t\n", "\n​\n"])
def test_sl_t032_4_blank_lines_of_any_kind_between_halves(blanks):
    text = f"## 7 [**CẦN XÁC{blanks}NHẬN**]\n- bí mật\n## 8\n- ok"
    assert confirmed_profile(text) == "## 8\n- ok"


def test_sl_t032_4_note_and_blank_between_halves():
    text = "## 7 [CẦN\n\n> ghi chú\n\nXÁC NHẬN]\n- bí mật\n## 8\n- ok"
    assert confirmed_profile(text) == "## 8\n- ok"


def test_sl_t032_4_blanks_kept_exactly_when_not_joined():
    text = "## 7 Giá [\n\n\n- ý thường\n## 8"
    assert confirmed_profile(text) == text


@pytest.mark.parametrize("indent", [" ", "   ", "\t", "　"])
def test_sl_t032_5_indented_half_heading_with_symbols(indent):
    text = f"- trước\n{indent}## 7 [⚠ **CẦN\nXÁC NHẬN**]\n- bí mật\n## 8\n- ok"
    assert confirmed_profile(text) == "- trước\n## 8\n- ok"


@pytest.mark.parametrize(
    "tag",
    [
        "[~~**CẦN XÁC NHẬN**~~]",
        "[***CẦN XÁC NHẬN***]",
        "[`CẦN XÁC NHẬN`]",
        "[⚠️ **CẦN XÁC NHẬN**]",
        "[👉🏽👉🏽 CẦN XÁC NHẬN]",
        "[🇻🇳 **CẦN XÁC NHẬN**]",
        "[👨‍👩‍👧‍👦 CẦN XÁC NHẬN]",
        "[*​*​*​*​CẦN XÁC NHẬN]",
        "[*́*́CẦN XÁC NHẬN]",
        "[ ** CẦN XÁC NHẬN]",
        "[　CẦN　XÁC NHẬN]",
        "[⠀CẦN XÁC NHẬN]",
        "(« chưa · xác · nhận »)",
    ],
)
def test_lc_t032_1_symbols_up_to_four_are_hidden(tag):
    assert _item_hidden(tag)


# --- Lọc thừa: chỉ ghi nhận. Ghim hành vi hiện tại -------------------------------------------


@pytest.mark.parametrize(
    "line",
    [
        "khách (cần) xác nhận lịch",
        "[*] cần xác nhận lịch",
        "[ ] cần xác nhận lịch với khách",
        "[x] cần xác nhận lịch với khách",
        "[1] Cần xác nhận lại giá",
        "(xem bảng) cần xác nhận",
        "Gọi trước (≥ 1 ngày, cần xác nhận)",
    ],
)
def test_plain_sentences_not_hidden(line):
    assert not _item_hidden(line)


@pytest.mark.parametrize(
    "line",
    ["(*Cần xác nhận lại với khách*)", "giao hàng (– cần xác nhận lại)"],
)
def test_over_filter_accepted_and_pinned(line):
    # Lọc thừa theo hướng an toàn (báo cáo Thợ Máy đã nêu). Ghim để biết khi hành vi đổi.
    assert _item_hidden(line)


# --- Lọc thiếu: lỗi -------------------------------------------------------------------------


LEAK_FIVE_PLUS = [
    "[❗❗❗ **CẦN XÁC NHẬN**]",
    "[🇻🇳🇻🇳 **CẦN XÁC NHẬN**]",
    "[⚠️👨‍👩‍👧‍👦 CẦN XÁC NHẬN]",
    "[CẦN ** ⚠️ ** XÁC NHẬN]",
    "[*​*​*​*​*CẦN XÁC NHẬN]",
    "[*****CẦN XÁC NHẬN]",
]


@pytest.mark.parametrize("tag", LEAK_FIVE_PLUS)
def test_sl_t043_1_five_or_more_symbols_hidden(tag):
    assert _item_hidden(tag)


def test_sl_t043_1_heading_half_tag_five_symbols():
    text = "## 7 [❗❗❗ **CẦN\nXÁC NHẬN**]\n- bí mật\n## 8\n- ok"
    assert "bí mật" not in confirmed_profile(text)


def test_sl_t043_2_rest_of_tag_on_heading_line():
    text = "## 7 [CẦN XÁC\n## NHẬN]\n- bí mật\n## 8\n- ok"
    assert "bí mật" not in confirmed_profile(text)


# --- _ends_with_partial_tag chỉ xét 64 ký tự cuối ---------------------------------------------


@pytest.mark.parametrize(
    ("head", "rest"),
    [
        ("## 7 [" + " " * 5000 + "CẦN" + "\t" * 5000 + "XÁC", "NHẬN]"),
        ("## 7 [ * * * * CHƯA * * * * XÁC * * * *", "NHẬN]"),
        ("## 7 [\t*\t\t*  *   *\tCHƯA\t* * * * XÁC  *  *  *  *   ", "NHẬN]"),
        ("## 7 " + "chữ " * 1000 + "[**CẦN", "XÁC NHẬN**]"),
        ("## 7 " + "[(" * 1000 + "[**CẦN", "XÁC NHẬN**]"),
        ("## 7 " + "[*****" * 100 + "[**CẦN", "XÁC NHẬN**]"),
        ("## 7 [" + "\u200b" * 5000 + "**CẦN", "XÁC NHẬN**]"),
        ("## 7 [" + "\u00a0" * 5000 + "CẦN XÁC", "NHẬN]"),
        ("## 7 [⚠️ 🇻🇳 CẦN XÁC", "NHẬN]"),
        ("## 7 [**", "CẦN XÁC NHẬN**]"),
    ],
    ids=[
        "spaces",
        "max-gaps",
        "tabs",
        "long-text",
        "brackets",
        "stars",
        "zwsp",
        "nbsp",
        "emoji",
        "open",
    ],
)
def test_partial_tag_window_not_fooled(head, rest):
    text = f"{head}\n{rest}\n- bí mật\n## 8\n- ok"
    assert confirmed_profile(text) == "## 8\n- ok"


def test_partial_tag_longest_valid_half_fits_window():
    # Nửa nhãn hợp lệ dài nhất sau khi gộp khoảng trắng (4 ký tự lạ ở mọi chỗ trống) phải ngắn
    # hơn cửa sổ, nếu không nửa nhãn hợp lệ sẽ không được nhận.
    longest = "[ * * * * CHUA * * * * XAC * * * * NHA"
    assert len(longest) < rules._PARTIAL_TAG_MAX
    assert rules._ends_with_partial_tag(longest)


# --- Tốc độ ---------------------------------------------------------------------------------

MB = 1_000_000


@pytest.mark.parametrize(
    "make",
    [
        lambda k: "- " + "[" * (MB // 4 * k // 4),
        lambda k: "- " + "(" * (MB // 4 * k // 4),
        lambda k: "- [" + "*" * (MB // 4 * k // 4),
        lambda k: "- [" + " " * (MB // 4 * k // 4),
        lambda k: "- [CAN XAC" + " " * (MB // 4 * k // 4) + "N",
        lambda k: "- " + "[ " * (MB // 8 * k // 4),
        lambda k: "## " + "[ * " * (MB // 16 * k // 4),
        lambda k: "## " + " " * (MB // 4 * k // 4) + "[CAN XAC\nNHAN]\n- x",
        lambda k: "- " + "[*CAN*XAC*" * (MB // 40 * k // 4),
        lambda k: "- [" + "*​" * (MB // 8 * k // 4),
        lambda k: "## 7 [CAN XAC" + "\n" * (MB // 4 * k // 4) + "- x",
        lambda k: "- a [CAN\n  ## b [CAN\n" * (MB // 100 * k // 4),
    ],
    ids=[
        "brackets",
        "parens",
        "stars",
        "spaces",
        "can-xac-spaces",
        "spaced-brackets",
        "heading-spaced",
        "heading-spaces-half",
        "starred-words",
        "zwsp-stars",
        "pending-blanks",
        "indented-half-headings",
    ],
)
def test_bad_input_scales_linearly(make):
    assert_scales_linearly(confirmed_profile, make, label="Soi Lỗi T-043")
