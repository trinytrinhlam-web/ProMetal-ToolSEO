"""Bộ lọc hồ sơ doanh nghiệp lọc theo cả ý (khối), không theo từng dòng (T-024)."""

import unicodedata

import pytest

from seo_app.content.rules import BUSINESS_PROFILE_FILE, confirmed_profile

TAG = "[CẦN XÁC NHẬN — lý do]"


def _old_filter(text: str) -> str:
    """Bộ lọc cũ (từng dòng), để đối chiếu trên file thật."""
    lines = [
        line
        for line in text.splitlines()
        if "[CẦN XÁC NHẬN" not in line.upper() and not line.startswith(">")
    ]
    return "\n".join(lines).strip()


@pytest.mark.parametrize("where", [0, 1, 2])
def test_multiline_bullet_dropped_whatever_line_has_tag(where):
    item = ["- Khách đã phục vụ: khoảng 500", "  người trong năm", "  qua Zalo và điện thoại"]
    item[where] += f" {TAG}"
    text = "\n".join(["- Hotline: 0909", *item, "- Bảo hành 2 năm"])
    assert confirmed_profile(text) == "- Hotline: 0909\n- Bảo hành 2 năm"


def test_tag_at_end_of_second_line_as_profile_instructs():
    text = "- Thời gian trả báo giá qua Zalo: khoảng\n  15 phút [CẦN XÁC NHẬN — hai nguồn]"
    assert confirmed_profile(text) == ""


@pytest.mark.parametrize(
    "tag",
    [
        "[cần xác nhận]",
        "[Cần Xác Nhận — lý do]",
        unicodedata.normalize("NFD", "[CẦN XÁC NHẬN]"),
        unicodedata.normalize("NFD", "[cần xác nhận — gõ trên Mac]"),
        "[CẦN  XÁC\tNHẬN]",
        "[ CẦN XÁC NHẬN]",
        "[CẦN XÁC NHẬN]",
    ],
)
def test_tag_variants_recognised(tag):
    text = f"- Email: abc\n  thêm {tag}\n- Hotline: 0909"
    assert confirmed_profile(text) == "- Hotline: 0909"


def test_tag_without_reason_still_matches():
    assert confirmed_profile("- Email: [CẦN XÁC NHẬN]") == ""


@pytest.mark.parametrize("prefix", ["", " ", "  ", "\t", " \t ", " "])
def test_note_lines_dropped_even_with_leading_whitespace(prefix):
    text = f"- Hotline: 0909\n{prefix}> ghi chú riêng của chủ dự án\n- Bảo hành 2 năm"
    assert confirmed_profile(text) == "- Hotline: 0909\n- Bảo hành 2 năm"


def test_note_inside_item_does_not_cut_block():
    text = f"- Khách: khoảng 500\n> ghi chú\n  người {TAG}\n- Hotline: 0909"
    assert confirmed_profile(text) == "- Hotline: 0909"


def test_nested_bullets_drop_whole_parent_item():
    text = "\n".join(
        [
            "- Chi nhánh:",
            "  - Bình Tân",
            f"  - Thủ Đức {TAG}",
            "- Hotline: 0909",
            "  - Zalo cùng số",
        ]
    )
    assert confirmed_profile(text) == "- Hotline: 0909\n  - Zalo cùng số"


def test_tag_on_parent_drops_nested_children():
    text = f"- Chi nhánh {TAG}\n  - Gò Vấp\n  - Hóc Môn\n- Hotline: 0909"
    assert confirmed_profile(text) == "- Hotline: 0909"


@pytest.mark.parametrize("bullet", ["- ", "* ", "+ ", "1. ", "2) "])
def test_bullet_kinds_each_start_own_block(bullet):
    text = f"{bullet}A {TAG}\n{bullet}B"
    assert confirmed_profile(text) == f"{bullet}B"


def test_paragraph_block_is_whole_paragraph():
    text = "\n".join(
        [
            f"{TAG} Chi nhánh: website ghi 3 con số khác nhau",
            '(trang chủ "8 chi nhánh khác", Giới thiệu "3 chi nhánh"),',
            "AI chỉ dùng trụ sở Bình Tân.",
            "",
            "Đoạn sau giữ nguyên.",
        ]
    )
    assert confirmed_profile(text) == "Đoạn sau giữ nguyên."


def test_unindented_continuation_of_bullet_belongs_to_bullet():
    # Gõ Notepad quên hai dấu cách ở dòng sau: vẫn là cùng một ý.
    text = f"- Khách: khoảng 500\nngười {TAG}\n- Hotline: 0909"
    assert confirmed_profile(text) == "- Hotline: 0909"


def test_blank_lines_separate_blocks_and_are_kept():
    text = f"- A\n\n- B {TAG}\n  tiếp\n\n- C"
    assert confirmed_profile(text) == "- A\n\n\n- C"


def test_heading_is_own_block():
    text = f"## 2. Năng lực\n- Đội thợ: khoảng 30 {TAG}\n## 3. Khu vực\n- Bình Tân"
    assert confirmed_profile(text) == "## 2. Năng lực\n## 3. Khu vực\n- Bình Tân"


def test_tag_in_heading_drops_only_heading():
    text = f"## Chi nhánh {TAG}\n- Bình Tân"
    assert confirmed_profile(text) == "- Bình Tân"


def test_paragraph_right_after_heading_is_separate_block():
    text = f"# Hồ sơ\nĐoạn mở {TAG}\ntiếp đoạn\n\n- A"
    assert confirmed_profile(text) == "# Hồ sơ\n\n- A"


def test_windows_line_endings():
    text = f"- A\r\n- B\r\n  tiếp {TAG}\r\n- C\r\n"
    assert confirmed_profile(text) == "- A\n- C"


@pytest.mark.parametrize("text", ["", "\n\n", "   \n\t\n"])
def test_empty_profile(text):
    assert confirmed_profile(text) == ""


def test_profile_with_only_notes():
    assert confirmed_profile("> ghi chú 1\n  > ghi chú 2\n\t>\n>") == ""


def test_lines_kept_verbatim():
    text = "- Hotline:   0909\t\n  tiếp  dòng"
    assert confirmed_profile(text) == text


def test_real_profile_only_drops_what_old_filter_leaked():
    text = BUSINESS_PROFILE_FILE.read_text(encoding="utf-8-sig")
    new = confirmed_profile(text).splitlines()
    old = iter(_old_filter(text).splitlines())
    # Bộ lọc mới chỉ bỏ thêm dòng, không thêm hay đổi dòng nào (dãy con của kết quả cũ).
    assert all(line in old for line in new)
    assert all("[CẦN XÁC NHẬN" not in line.upper() for line in new)
    assert all(not line.lstrip().startswith(">") for line in new)


@pytest.mark.parametrize("space", [" ", " ", " ", "　", "\t", "   ", "   "])
def test_tag_with_any_unicode_whitespace_between_words(space):
    # SL-022-6: NBSP hay khoảng trắng Unicode khác ở mọi chỗ trong nhãn vẫn được nhận.
    tag = f"[{space}CẦN{space}XÁC{space}NHẬN{space}— lý do]"
    assert confirmed_profile(f"- Email: abc {tag}\n- Hotline: 0909") == "- Hotline: 0909"
    nfd = unicodedata.normalize("NFD", tag)
    assert confirmed_profile(f"- Email: abc\n  {nfd}\n- Hotline: 0909") == "- Hotline: 0909"


# --- Lượt 2: SL-024-1 (dòng trống giữa ý), SL-024-2 (ký tự vô hình) ---------------------------


def test_blank_then_unindented_bullet_or_paragraph_is_new_block():
    # Dòng trống + dòng không thụt lề: luôn là ý / đoạn mới, không gộp vào ý có nhãn trước đó.
    text = f"- Email {TAG}\n\n- Hotline 0909\n\nĐoạn sau giữ nguyên."
    assert confirmed_profile(text) == "- Hotline 0909\n\nĐoạn sau giữ nguyên."


def test_blank_then_indented_line_stays_in_clean_item_verbatim():
    text = "- Khách: khoảng 500\n\n  người trong năm\n- Hotline 0909"
    assert confirmed_profile(text) == text


def test_several_blank_lines_and_notes_inside_item():
    text = f"- Khách: khoảng 500\n\n> ghi chú\n  \n  người {TAG}\n\n- Hotline 0909"
    assert confirmed_profile(text) == "- Hotline 0909"


def test_blank_then_indented_after_heading_is_not_merged_into_heading():
    text = f"## Mục {TAG}\n\n  đoạn thụt lề sau tiêu đề"
    # Tiêu đề luôn đứng riêng: dòng thụt lề sau nó không bị bỏ theo (strip() bỏ khoảng trắng đầu).
    assert confirmed_profile(text) == "đoạn thụt lề sau tiêu đề"


def test_invisible_char_kept_in_output():
    # Chỉ bỏ ký tự vô hình khi so khớp; dòng đưa vào prompt giữ nguyên.
    text = "- Hotline​ 0909"
    assert confirmed_profile(text) == text


def test_glued_tag_still_not_recognised_but_invisible_separator_is():
    assert confirmed_profile("- Email x [CẦNXÁC NHẬN]") == "- Email x [CẦNXÁC NHẬN]"
    assert confirmed_profile("- Email x [CẦN​XÁC NHẬN]\n- B") == "- B"
    assert confirmed_profile("- Email x [C‍ẦN XÁC NHẬN]\n- B") == "- B"


@pytest.mark.parametrize("ch", ["͏", "️", "ㅤ", "ﾠ"])
def test_default_ignorable_not_cf_in_tag_or_before_note(ch):
    assert confirmed_profile(f"- Email x [CẦN{ch} XÁC NHẬN]\n- B") == "- B"
    assert confirmed_profile(f"- B\n{ch}> ghi chú") == "- B"


def test_fullwidth_bracket_tag_recognised():
    assert confirmed_profile("- Email x ［CẦN XÁC NHẬN］\n- B") == "- B"
