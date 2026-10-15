"""Soi Lỗi T-032: bộ lọc hồ sơ với nhãn gõ sai, nhãn vắt dòng và nhãn trên tiêu đề.

Thử kiểu gõ Notepad (CRLF, tab, BOM), ký tự vô hình, chữ toàn khổ, dấu tổ hợp tách rời, tiêu
đề ``#`` sát chữ, tiêu đề thụt lề, tiêu đề lồng nhau. Lỗi SL-T032-1..3 đã sửa ở lượt 2 của
Thợ Máy, bỏ ``xfail``.
"""

import unicodedata

import pytest

from seo_app.content.rules import BUSINESS_PROFILE_FILE, _is_unconfirmed, confirmed_profile
from tests.timing import assert_scales_linearly

TAG = "[CẦN XÁC NHẬN]"


def _notepad(text: str) -> str:
    """Như file Notepad lưu: BOM đầu file, xuống dòng CRLF."""
    return "\ufeff" + text.replace("\n", "\r\n")


def _cp(text: str) -> str:
    """Lọc rồi bỏ BOM: dòng giữ y nguyên nên BOM ở dòng đầu còn lại (đọc file thật bằng
    ``utf-8-sig`` thì không có BOM)."""
    return confirmed_profile(text).replace("\ufeff", "")


# --- Tiêu chí phiếu -------------------------------------------------------------------------


@pytest.mark.parametrize(
    "tag",
    ["[CẦNXÁC NHẬN]", "[CẦN XÁCNHẬN]", "[CAN XAC NHAN]", "(CẦN XÁC NHẬN)", "[chưa xác nhận]"],
)
def test_misspelled_tag_in_notepad_file(tag):
    text = _notepad(f"- Hotline 0909\n- Bảo hành 5 năm\t{tag}\n- Zalo cùng số")
    assert _cp(text) == "- Hotline 0909\n- Zalo cùng số"


@pytest.mark.parametrize(
    "line",
    [
        "- Khách cần xác nhận lịch trước khi thợ tới.",
        "- KHÁCH CẦN XÁC NHẬN LỊCH",
        "- Khach can xac nhan lich",
        "- Giá [tham khảo] cần xác nhận khi báo khách",
        "- Gọi lại (sau 17h) cần xác nhận",
        "- Mục «cần xác nhận» là của khách",
    ],
)
def test_plain_words_without_opening_bracket_kept(line):
    assert _cp(_notepad(f"{line}\n- B")) == f"{line}\n- B"


@pytest.mark.parametrize(
    ("first", "second"),
    [
        ("- Bảo hành 5 năm [CẦN XÁC", "  NHẬN — lý do]"),
        ("- Bảo hành 5 năm [CẦN", "XÁC NHẬN]"),
        ("- Bảo hành 5 năm (", "\tcan xac nhan)"),
        ("- Bảo hành 5 năm [CẦN XÁC\u200b", "\u00a0NHẬN]"),
    ],
)
def test_tag_split_across_lines_of_one_item_notepad(first, second):
    text = _notepad(f"- A\n{first}\n{second}\n- B")
    assert _cp(text) == "- A\n- B"


def test_heading_tag_hides_until_same_or_higher_heading():
    text = (
        "# Hồ sơ\n\n## 6. Dịch vụ\n- ok6\n\n"
        f"## 7. Chất liệu thật {TAG}\n- bí mật 1\n\n### 7.1 Ảnh\n- bí mật 2\n"
        "#### 7.1.1\n- bí mật 3\n\n## 8. Liên hệ\n- ok8"
    )
    out = _cp(_notepad(text))
    assert "bí mật" not in out and "7." not in out
    assert out == "# Hồ sơ\n\n## 6. Dịch vụ\n- ok6\n\n## 8. Liên hệ\n- ok8"


def test_heading_tag_stops_at_h1():
    text = f"# A\n## 7 {TAG}\n- bí mật\n# B\n- ok"
    assert confirmed_profile(text) == "# A\n# B\n- ok"


def test_real_profile_output_has_no_tag_and_only_file_lines():
    raw = BUSINESS_PROFILE_FILE.read_text(encoding="utf-8-sig")
    out = confirmed_profile(raw)
    assert out
    file_lines = set(raw.splitlines())
    assert all(line in file_lines for line in out.splitlines())
    assert not _is_unconfirmed(out)
    assert not any(line.lstrip().startswith(">") for line in out.splitlines())


# --- Trường hợp xấu -------------------------------------------------------------------------


def test_nfd_tag_with_separated_combining_marks():
    tag = unicodedata.normalize("NFD", "[cần xác nhận]")
    assert confirmed_profile(f"- A {tag}\n- B") == "- B"
    # Dấu tổ hợp đứng sai chỗ (trước chữ, giữa ngoặc và chữ) vẫn bị bỏ khi tìm nhãn.
    assert confirmed_profile("- A [\u0300CA\u0302\u0300N XA\u0301C NHA\u0323\u0302N]\n- B") == "- B"


def test_fullwidth_letters_and_brackets():
    tag = "［ＣẦＮ\u3000ＸÁＣ\u3000ＮＨẬＮ］"
    assert confirmed_profile(f"- A {tag}\n- B") == "- B"
    assert confirmed_profile(f"＃＃ 7 {tag}\n- bí mật\n＃＃ 8\n- ok") == "＃＃ 8\n- ok"


def test_invisible_chars_in_heading_hashes_and_tag():
    text = "\u200b#\u200d# 7 [C\u00adẦN XÁC NHẬN]\n- bí mật\n## 8\n- ok"
    assert confirmed_profile(text) == "## 8\n- ok"


def test_glued_hash_heading_with_tag_and_crlf():
    text = _notepad(f"##7 {TAG}\n- bí mật\n\n###7.1\n- bí mật 2\n## 8\n- ok")
    assert _cp(text) == "## 8\n- ok"


def test_h1_tag_hides_to_end_of_file():
    text = f"# A\n- ok\n\n# B {TAG}\n- x\n## c\n- y\n### d\n\n- z\n## e"
    assert confirmed_profile(text) == "# A\n- ok"


def test_tagged_heading_is_last_line():
    assert confirmed_profile(f"- ok\n\n## 7 {TAG}") == "- ok"
    assert confirmed_profile(f"- ok\n## 7 {TAG}\n") == "- ok"


def test_nested_h2_h3_h2():
    text = f"## A {TAG}\n### B\n- x\n## C\n- ok\n### D {TAG}\n- y\n## E\n- ok2"
    assert confirmed_profile(text) == "## C\n- ok\n## E\n- ok2"


def test_indented_heading_inside_hidden_section_keeps_hiding():
    # Điểm 3 của Thợ Máy: lọc thừa, chấp nhận.
    text = f"## 7 {TAG}\n- bí mật\n  ## 8\n\t## 9\n- vẫn giấu\n## 10\n- ok"
    assert confirmed_profile(text) == "## 10\n- ok"


def test_notes_and_blanks_at_hidden_section_boundary():
    text = f"- trước\n\n> ghi chú\n## 7 {TAG}\n> ghi chú\n\n- bí mật\n\n> ghi chú\n## 8\n- ok"
    assert confirmed_profile(text) == "- trước\n\n## 8\n- ok"


def test_parenthesis_overfilter_is_accepted():
    # Điểm 1 của Thợ Máy: câu thường có ngoặc mở ngay trước cụm chữ bị giấu (an toàn khi nghi ngờ).
    assert confirmed_profile("- Lịch (cần xác nhận với khách)\n- B") == "- B"
    assert confirmed_profile("- [CẠN XÁC NHẬN]\n- B") == "- B"


# --- Lỗi tìm được (đã sửa ở lượt 2) ---------------------------------------------------------


@pytest.mark.parametrize("line", ["#suachuacuasat #cuasat", "#1 khu vực Thủ Đức"])
def test_hash_word_line_does_not_end_hidden_section(line):
    text = f"## 7. Chất liệu thật {TAG}\n- bí mật A\n{line}\n- bí mật B\n## 8\n- ok"
    out = confirmed_profile(text)
    assert "bí mật" not in out


@pytest.mark.parametrize("indent", [" ", "   ", "\t", "\u00a0"])
def test_indented_tagged_heading_hides_section(indent):
    text = f"- ok\n\n{indent}## 7. Chất liệu thật {TAG}\n- bí mật A\n\n## 8\n- ok8"
    assert "bí mật" not in _cp(_notepad(text))


def test_heading_tag_split_across_lines_hides_section():
    text = "## 7. Chất liệu thật [CẦN XÁC\nNHẬN]\n- bí mật A\n## 8\n- ok"
    assert "bí mật" not in confirmed_profile(text)


# --- Tốc độ ---------------------------------------------------------------------------------


def _big(k: int) -> str:
    unit = (
        f"## 7 {TAG}\n- bí mật\n### 7.1\n  - con\n\n## 8\n"
        "- A [CẦN XÁC\n  NHẬN]\n- (( [[ ( [ cần xác\n" + "x " * 40 + "\n#tag\n  ## thụt\n\n"
    )
    return unit * (300 * k)


def test_filter_scales_linearly():
    assert_scales_linearly(confirmed_profile, _big, label="T-032 lẫn lộn")


def test_one_huge_block_with_many_brackets_scales_linearly():
    assert_scales_linearly(
        confirmed_profile,
        lambda k: "- A\n" + "  ([ " * 2000 * k + "\n" + "  [CAN    XAC " * 500 * k,
        label="T-032 khối lớn",
    )
