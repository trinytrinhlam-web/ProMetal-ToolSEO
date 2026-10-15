"""T-032: bộ lọc hồ sơ nhận nhãn gõ sai, nhãn vắt qua hai dòng và nhãn trên tiêu đề."""

import unicodedata

import pytest

from seo_app.content.rules import BUSINESS_PROFILE_FILE, confirmed_profile

MISSPELLED = [
    "[CẦNXÁC NHẬN]",
    "[CẦN XÁCNHẬN]",
    "[CẦNXÁCNHẬN]",
    "[CAN XAC NHAN]",
    "[CAN XAC NHAN — chưa rõ]",
    "[CẦN XAC NHẬN]",
    "[CAN XÁC NHAN]",
    "(CẦN XÁC NHẬN)",
    "(CAN XAC NHAN)",
    "( CẦN XÁC NHẬN — lý do)",
    "（CẦN XÁC NHẬN）",
    "[CHƯA XÁC NHẬN]",
    "[CHUA XAC NHAN]",
    "(CHƯA XÁC NHẬN)",
    "[CHƯAXÁCNHẬN]",
]


@pytest.mark.parametrize("tag", MISSPELLED)
@pytest.mark.parametrize("case", [str, str.lower, str.title])
def test_misspelled_tag_drops_item(tag, case):
    text = f"- Hotline 0909\n- Email x {case(tag)}\n- Zalo cùng số"
    assert confirmed_profile(text) == "- Hotline 0909\n- Zalo cùng số"


@pytest.mark.parametrize("tag", MISSPELLED)
def test_misspelled_tag_typed_on_mac_nfd(tag):
    text = f"- Email x {unicodedata.normalize('NFD', tag.lower())}\n- B"
    assert confirmed_profile(text) == "- B"


@pytest.mark.parametrize("ch", ["​", "‍", "­", "﻿", "͏", "️"])
@pytest.mark.parametrize("tag", ["[CẦN{c}XÁC{c}NHẬN]", "[C{c}AN XAC NHAN]", "({c}CHƯA XÁC NHẬN)"])
def test_misspelled_tag_with_invisible_chars(ch, tag):
    assert confirmed_profile(f"- Email x {tag.format(c=ch)}\n- B") == "- B"


@pytest.mark.parametrize("space", ["\t", " ", "　", "  "])
def test_misspelled_tag_with_odd_spaces(space):
    tag = f"({space}can{space}xac{space}nhan)"
    assert confirmed_profile(f"- Email x {tag}\n- B") == "- B"


@pytest.mark.parametrize(
    "text",
    [
        "- Khách cần xác nhận lịch trước khi thợ tới",
        "- Khách CẦN XÁC NHẬN lịch hẹn qua Zalo",
        "- Khách chưa xác nhận thì thợ gọi lại",
        "Thợ gọi lại để khách cần xác nhận giờ hẹn.",
        "- Can xac nhan lich truoc",
        "- Sau khi báo giá [khách đồng ý] thì thợ cần xác nhận lại",
    ],
)
def test_plain_sentence_with_words_is_kept(text):
    # Không có ngoặc mở đứng ngay trước cụm chữ thì là câu thường: không giấu.
    assert confirmed_profile(text) == text


@pytest.mark.parametrize(
    "first, second",
    [
        ("[CẦN XÁC", "NHẬN — lý do]"),
        ("[CẦN", "XÁC NHẬN]"),
        ("[", "CẦN XÁC NHẬN]"),
        ("(can xac", "nhan)"),
        ("[CHƯA XÁC", "NHẬN]"),
    ],
)
@pytest.mark.parametrize("indent", ["  ", "\t", ""])
def test_tag_split_across_two_lines_of_one_item(first, second, indent):
    text = f"- Hotline 0909\n- Khách: khoảng 500 {first}\n{indent}{second} người\n- Zalo"
    assert confirmed_profile(text) == "- Hotline 0909\n- Zalo"


def test_tag_split_across_lines_with_note_between():
    text = "- Khách: khoảng 500 [CẦN XÁC\n> ghi chú\n  NHẬN] người\n- B"
    assert confirmed_profile(text) == "- B"


def test_tag_split_across_lines_of_paragraph():
    text = "Chi nhánh ở Thủ Đức [CẦN\nXÁC NHẬN]\n\nĐoạn sau."
    assert confirmed_profile(text) == "Đoạn sau."


def test_real_profile_output_unchanged():
    # Hồ sơ thật gõ nhãn đúng hết: phần AI thấy y như trước T-032 (đã so chuỗi khi làm phiếu).
    text = BUSINESS_PROFILE_FILE.read_text(encoding="utf-8-sig")
    out = confirmed_profile(text)
    assert "XÁC NHẬN" not in out.upper()
    assert out.startswith("# Hồ sơ doanh nghiệp")
    assert "## 8. Quy tắc khi AI viết về doanh nghiệp" in out
