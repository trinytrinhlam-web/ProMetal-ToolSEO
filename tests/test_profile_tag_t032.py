"""T-032: bộ lọc hồ sơ nhận nhãn gõ sai, nhãn vắt qua hai dòng và nhãn trên tiêu đề."""

import re
import time
import unicodedata

import pytest

from seo_app.content import rules
from seo_app.content.rules import BUSINESS_PROFILE_FILE, confirmed_profile

TAG = "[CẦN XÁC NHẬN — lý do]"

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


def test_real_profile_output_unchanged(monkeypatch):
    # Hồ sơ thật gõ nhãn đúng hết và không có tiêu đề nào mang nhãn: phần AI thấy y như khi dùng
    # mẫu nhãn cũ trước T-032 (chỉ nhận «[CẦN XÁC NHẬN» có dấu, đúng dấu cách).
    text = BUSINESS_PROFILE_FILE.read_text(encoding="utf-8-sig")
    new = confirmed_profile(text)
    old_pattern = re.compile(r"\[\s*CẦN\s+XÁC\s+NHẬN")
    monkeypatch.setattr(
        rules, "_is_unconfirmed", lambda block: bool(old_pattern.search(rules._visible(block)))
    )
    assert new == confirmed_profile(text)
    assert "XÁC NHẬN" not in new.upper()
    assert "## 8. Quy tắc khi AI viết về doanh nghiệp" in new


# --- Nhãn trên tiêu đề (#2) --------------------------------------------------------------------

PROFILE = "\n".join(
    [
        "# Hồ sơ",
        "## 6. Kiến thức",
        "- Ý 6",
        "",
        "## 7. Chất liệu thật {tag}",
        "> ghi chú",
        "- Ý 7 bí mật",
        "  dòng tiếp",
        "",
        "Đoạn văn bí mật.",
        "### 7.1 Ca sửa",
        "- Ý 7.1 bí mật",
        "#### 7.1.1 Chi tiết",
        "- Ý 7.1.1 bí mật",
        "{next}",
        "- Ý sau",
    ]
)


@pytest.mark.parametrize("tag", [TAG, "[can xac nhan]", "(CHƯA XÁC NHẬN)", "[CẦNXÁC NHẬN]"])
@pytest.mark.parametrize("next_heading", ["## 8. Quy tắc", "# Phụ lục", "#\tPhụ lục", "##"])
def test_tag_on_h2_hides_section_until_same_or_higher_heading(tag, next_heading):
    out = confirmed_profile(PROFILE.format(tag=tag, next=next_heading))
    assert out == f"# Hồ sơ\n## 6. Kiến thức\n- Ý 6\n\n{next_heading}\n- Ý sau"
    assert "bí mật" not in out


@pytest.mark.parametrize("line", ["##8. Quy tắc", "#suachuacuasat", "#1 khu vực"])
def test_hash_without_space_does_not_end_hidden_section(line):
    # Lượt 2 (SL-T032-1): chỉ tiêu đề thật («#» rồi khoảng trắng) mới thôi giấu; «##8» gõ thiếu
    # dấu cách cũng bị giấu theo (an toàn khi nghi ngờ).
    out = confirmed_profile(PROFILE.format(tag=TAG, next=line))
    assert out == "# Hồ sơ\n## 6. Kiến thức\n- Ý 6"


def test_tag_on_h3_does_not_hide_following_h2():
    text = f"## 7. Chất liệu\n- A\n### 7.1 Ca sửa {TAG}\n- B bí mật\n## 8. Quy tắc\n- C"
    assert confirmed_profile(text) == "## 7. Chất liệu\n- A\n## 8. Quy tắc\n- C"


def test_tag_on_h3_hidden_until_next_h3():
    text = f"## 7\n### 7.1 {TAG}\n- bí mật\n#### 7.1.1\n- bí mật\n### 7.2\n- B"
    assert confirmed_profile(text) == "## 7\n### 7.2\n- B"


def test_tag_on_h1_hides_rest_of_file():
    text = f"- A\n# Phần nháp {TAG}\n## 1\n- bí mật\n### 1.1\n- bí mật"
    assert confirmed_profile(text) == "- A"


def test_tagged_heading_inside_hidden_section_keeps_outer_level():
    text = f"## 7 {TAG}\n### 7.1 {TAG}\n- bí mật\n### 7.2\n- bí mật\n## 8\n- B"
    assert confirmed_profile(text) == "## 8\n- B"


def test_next_heading_with_tag_starts_new_hidden_section():
    text = f"## 7 {TAG}\n- bí mật\n## 8 {TAG}\n- bí mật\n## 9\n- B"
    assert confirmed_profile(text) == "## 9\n- B"


def test_indented_heading_does_not_end_hidden_section():
    # Tiêu đề thụt lề không phải tiêu đề (như trước T-032): không cắt mục đang giấu.
    text = f"## 7 {TAG}\n- bí mật\n  ## 8\n- bí mật\n## 9\n- B"
    assert confirmed_profile(text) == "## 9\n- B"


def test_heading_tag_split_or_with_invisible_char():
    assert confirmed_profile("## 7 [CẦN​XÁC NHẬN]\n- bí mật\n## 8\n- B") == "## 8\n- B"
    assert confirmed_profile("## 7 （can xac nhan）\n- bí mật\n## 8\n- B") == "## 8\n- B"


def test_heading_with_plain_words_not_hidden():
    text = "## Khi nào khách cần xác nhận lịch\n- A"
    assert confirmed_profile(text) == text


def test_hidden_section_crlf_and_fullwidth_hash():
    text = f"## 7 {TAG}\r\n- bí mật\r\n\r\n＃＃ 8\r\n- B\r\n"
    assert confirmed_profile(text) == "＃＃ 8\n- B"


def test_hidden_section_is_linear_on_large_input():
    # Mục giấu rất dài và nhiều mục: chạy một lượt, không lặp lồng (giới hạn rộng cho máy chậm).
    lines = []
    for i in range(2000):
        lines += [f"## Mục {i} {TAG if i % 2 else ''}", "### con", "- ý", "  tiếp", ""]
    start = time.perf_counter()
    out = confirmed_profile("\n".join(lines))
    assert time.perf_counter() - start < 5
    assert out.count("## Mục") == 1000
    assert "XÁC NHẬN" not in out


# --- Lượt 2: tiêu đề thụt lề có nhãn, nhãn vắt hai dòng trên tiêu đề -------------------------


@pytest.mark.parametrize("indent", [" ", "   ", "\t", " "])
def test_indented_tagged_heading_hides_section_and_keeps_item_before(indent):
    text = f"- ok\n\n{indent}## 7 {TAG}\n- bí mật\n  ## 7.1 thụt\n- bí mật\n## 8\n- B"
    assert confirmed_profile(text) == "- ok\n\n## 8\n- B"


def test_indented_heading_without_tag_still_belongs_to_block():
    # Không có nhãn thì giữ cách cũ: dòng thụt lề là dòng tiếp của ý trước.
    text = "- ok\n  ## không phải tiêu đề\n- B"
    assert confirmed_profile(text) == text


@pytest.mark.parametrize(
    "first, second",
    [("[CẦN XÁC", "NHẬN]"), ("[", "CẦN XÁC NHẬN]"), ("(chưa", "xác nhận)"), ("[CAN", "XAC NHAN]")],
)
def test_heading_tag_split_across_lines(first, second):
    text = f"## 6\n- A\n## 7 {first}\n{second} lý do\n- bí mật\n### 7.1\n- bí mật\n## 8\n- B"
    assert confirmed_profile(text) == "## 6\n- A\n## 8\n- B"


def test_heading_tag_split_with_note_between():
    text = "## 7 [CẦN XÁC\n> ghi chú\nNHẬN]\n- bí mật\n## 8\n- B"
    assert confirmed_profile(text) == "## 8\n- B"


@pytest.mark.parametrize(
    "text",
    [
        "## Giá [\n\n- A",
        "## Giá (tham khảo\n- A",
        "## Cần [CẦN\n- A khác",
        "## Câu hỏi (chưa\n- có",
    ],
)
def test_heading_with_open_bracket_not_completed_is_kept(text):
    # Nửa nhãn ở cuối tiêu đề mà dòng kế không ghép thành nhãn: giữ tiêu đề và dòng kế y nguyên.
    assert confirmed_profile(text) == text


def test_heading_with_half_tag_at_end_of_file_is_dropped():
    assert confirmed_profile("- A\n## 7 [CẦN XÁC") == "- A"


def test_half_tag_heading_followed_by_heading():
    assert confirmed_profile("## 7 [CẦN\n## 8\n- B") == "## 7 [CẦN\n## 8\n- B"
