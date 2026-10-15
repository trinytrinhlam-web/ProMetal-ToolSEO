"""T-024 (Soi Lỗi): bộ lọc hồ sơ doanh nghiệp theo khối, thử các kiểu gõ Notepad.

Bổ sung cho ``tests/test_profile_blocks.py`` (test của Thợ Máy). Các lỗi SL-024-1, SL-024-2
(báo cáo ``docs/team/reports/T-024-soi-loi.md``) đã sửa ở lượt 2, bỏ dấu xfail.
"""

from __future__ import annotations

import random
import unicodedata

import pytest

from seo_app.content.rules import confirmed_profile, load_rules

TAG = "[CẦN XÁC NHẬN — lý do]"


def _has_tag(text: str) -> bool:
    norm = unicodedata.normalize("NFC", text).upper()
    return "[CẦN XÁC NHẬN" in " ".join(norm.split()).replace("[ ", "[")


# --- Điểm (1): nhãn ở ý con bỏ cả ý cha; dòng quên thụt lề ------------------------------------


def test_tag_deep_in_nested_numbered_list_drops_whole_top_item_only():
    text = "\n".join(
        [
            "1. Dịch vụ chính",
            "   1. Cửa sắt",
            f"      - Cổng xếp {TAG}",
            "2. Bảo hành 2 năm",
            "   - Có phiếu bảo hành",
        ]
    )
    assert confirmed_profile(text) == "2. Bảo hành 2 năm\n   - Có phiếu bảo hành"


def test_star_bullets_nested_with_four_spaces():
    text = f"* Hotline 0909\n* Chi nhánh\n    * Gò Vấp {TAG}\n* Zalo cùng số"
    assert confirmed_profile(text) == "* Hotline 0909\n* Zalo cùng số"


def test_two_digit_numbering_starts_own_block():
    assert confirmed_profile(f"9. A\n10. B {TAG}\n11. C") == "9. A\n11. C"


def test_tab_indented_continuation_belongs_to_item():
    assert confirmed_profile(f"- Khách: khoảng 500\n\tngười {TAG}\n- B") == "- B"


def test_unindented_line_with_tag_after_clean_item_never_leaks():
    # Quên gạch đầu dòng cho ý sau: ý trước bị giấu theo (mất thông tin đúng, chấp nhận),
    # nhưng dòng có nhãn không bao giờ lọt.
    out = confirmed_profile(f"- Hotline 0909\nEmail x {TAG}\n- Zalo")
    assert "Email" not in out
    assert out.endswith("- Zalo")


def test_clean_items_next_to_tagged_item_are_kept():
    # Viết đúng cú pháp (mỗi ý một gạch đầu dòng) thì không mất ý đúng nào.
    text = f"- Hotline 0909\n- Email {TAG}\n- Zalo cùng số"
    assert confirmed_profile(text) == "- Hotline 0909\n- Zalo cùng số"


def test_paragraph_followed_directly_by_bullet_is_cut_at_bullet():
    assert confirmed_profile(f"Đoạn mở {TAG}\n- Hotline 0909") == "- Hotline 0909"


# --- Điểm (2): tiêu đề thụt lề ----------------------------------------------------------------


def test_indented_heading_after_tagged_item_is_dropped_with_it():
    assert confirmed_profile(f"- A {TAG}\n ## 3. Khu vực\n- B") == "- B"


def test_indented_heading_after_clean_item_is_kept_verbatim():
    text = "- A\n ## 3. Khu vực\n- B"
    assert confirmed_profile(text) == text


def test_heading_without_space_after_hash_still_own_block():
    assert confirmed_profile(f"- A {TAG}\n#Khu vực\n- B") == "#Khu vực\n- B"


# --- Điểm (3): ghi chú «>» chen giữa ý -------------------------------------------------------


def test_note_between_item_lines_with_tag_after_note():
    text = f"- Khách: khoảng 500\n  > ghi chú\n  người {TAG}\n- B"
    assert confirmed_profile(text) == "- B"


def test_note_between_item_lines_with_tag_before_note():
    text = f"- Khách: khoảng 500 {TAG}\n  > ghi chú\n  người trong năm\n- B"
    assert confirmed_profile(text) == "- B"


def test_note_alone_between_paragraph_lines_does_not_split_paragraph():
    text = f"Chi nhánh {TAG}\n> ghi chú\ncòn ở Thủ Đức\n\nĐoạn sau."
    assert confirmed_profile(text) == "Đoạn sau."


# --- Điểm (4): nhãn viết sai hẳn không được nhận (ghi nhận hành vi) ----------------------------


@pytest.mark.parametrize(
    "tag",
    ["CẦN XÁC NHẬN", "[CAN XAC NHAN]", "(CẦN XÁC NHẬN)", "[CẦNXÁC NHẬN]", "[CHƯA XÁC NHẬN]"],
)
def test_misspelled_tags_are_not_recognised(tag):
    # Đúng phạm vi phiếu (không đổi cú pháp nhãn). Đề xuất trong báo cáo: Ngòi Bút ghi rõ cú
    # pháp trong hướng dẫn đầu file.
    text = f"- Email x {tag}"
    assert confirmed_profile(text) == text


# --- Kiểu gõ Notepad ---------------------------------------------------------------------------


def test_windows_crlf_with_notes_blank_lines_and_indent():
    text = (
        "# Hồ sơ\r\n"
        "  > ghi chú cho chủ dự án\r\n"
        "\r\n"
        "- Hotline 0909\r\n"
        f"- Khách: khoảng 500\r\n  người {TAG}\r\n"
        "\r\n"
        "- Zalo cùng số\r\n"
    )
    assert confirmed_profile(text) == "# Hồ sơ\n\n- Hotline 0909\n\n- Zalo cùng số"


def test_old_mac_cr_only_line_endings():
    assert confirmed_profile(f"- A\r  tiếp {TAG}\r- B\r> ghi chú") == "- B"


def test_bom_file_read_through_load_rules(tmp_path):
    content = tmp_path / "content.toml"
    content.write_text(
        '[voice]\naddress = "anh/chị"\ntone = "thân thiện"\nbanned = []\n'
        "[review]\nchecklist = []\n",
        encoding="utf-8",
    )
    profile = tmp_path / "business_profile.md"
    profile.write_bytes(
        f"> ghi chú đầu file\r\n- Hotline 0909\r\n- Email {TAG}\r\n  tiếp\r\n".encode("utf-8-sig")
    )
    assert load_rules(content, profile).business_profile == "- Hotline 0909"


@pytest.mark.parametrize("blank", ["   ", "\t", " \t ", " "])
def test_whitespace_only_line_between_items_separates_them(blank):
    text = f"- A\n{blank}\n- B {TAG}\n  tiếp\n{blank}\n- C"
    assert confirmed_profile(text) == f"- A\n{blank}\n{blank}\n- C"


def test_bare_dash_line_starts_block():
    assert confirmed_profile(f"-\n  tiếp {TAG}\n- B") == "- B"


def test_very_long_profile():
    lines = []
    for i in range(5000):
        if i % 3 == 0:
            lines += [f"- Ý {i}: thông tin", f"  dòng tiếp {TAG}"]
        else:
            lines += [f"- Ý {i}: thông tin", "  dòng tiếp đúng"]
    out = confirmed_profile("\n".join(lines)).splitlines()
    kept = [i for i in range(5000) if i % 3]
    assert len(out) == 2 * len(kept)
    assert out[0] == f"- Ý {kept[0]}: thông tin"
    assert not _has_tag("\n".join(out))


def test_random_notepad_profiles_never_leak_tag_or_note():
    """Thử ngẫu nhiên (cố định hạt giống): nhãn và ghi chú không bao giờ lọt."""
    rng = random.Random(24)
    pieces = [
        "- Ý",
        "* Ý",
        "1. Ý",
        "  tiếp",
        "\ttiếp",
        "    - con",
        "đoạn",
        "## Mục",
        " ## Mục",
        "",
        "   ",
        "  > ghi chú",
        "\t> ghi chú",
        "> ghi chú",
    ]
    tags = [
        TAG,
        "[cần xác nhận]",
        unicodedata.normalize("NFD", "[CẦN XÁC NHẬN]"),
        "[CẦN\tXÁC  NHẬN]",
        "[CẦN XÁC NHẬN]",
    ]
    for _ in range(500):
        lines = []
        for _ in range(rng.randint(1, 25)):
            line = rng.choice(pieces)
            if line.strip() and rng.random() < 0.3:
                line += " " + rng.choice(tags)
            lines.append(line)
        text = rng.choice(["\n", "\r\n"]).join(lines)
        out = confirmed_profile(text)
        assert not _has_tag(out), text
        assert not any(line.lstrip().startswith(">") for line in out.splitlines()), text


# --- SL-024-1, SL-024-2 (đã sửa) -----------------------------------------------------------------


@pytest.mark.parametrize("blank", ["", "  "])
def test_item_with_blank_line_then_indented_tagged_continuation(blank):
    text = f"- Khách đã phục vụ: khoảng 500\n{blank}\n  người {TAG}\n- Hotline 0909"
    assert "500" not in confirmed_profile(text)


def test_tagged_item_with_blank_line_then_indented_continuation():
    text = f"- Khách đã phục vụ: khoảng 500 {TAG}\n\n  người trong năm 2025\n- Hotline 0909"
    assert "2025" not in confirmed_profile(text)


INVISIBLE = ["\u200b", "\u200c", "\u200d", "\u2060", "\ufeff", "\u00ad"]


@pytest.mark.parametrize("ch", INVISIBLE)
@pytest.mark.parametrize("tag", ["[CẦN{c}XÁC NHẬN]", "[CẦN {c}XÁC NHẬN]", "[{c}CẦN XÁC NHẬN]"])
def test_tag_with_invisible_char_is_recognised(ch, tag):
    text = f"- Email x {tag.format(c=ch)}\n- Hotline 0909"
    assert confirmed_profile(text) == "- Hotline 0909"


def test_invisible_char_before_tag_bracket_still_recognised():
    for ch in INVISIBLE:
        assert confirmed_profile(f"- Email x {ch}[CẦN XÁC NHẬN]\n- B") == "- B"


@pytest.mark.parametrize("ch", INVISIBLE)
@pytest.mark.parametrize("indent", ["", "  "])
def test_note_preceded_by_invisible_char_is_dropped(ch, indent):
    assert confirmed_profile(f"- Hotline 0909\n{indent}{ch}> ghi chú riêng") == "- Hotline 0909"


# --- Lượt 2: điểm Thợ Máy tự nêu ---------------------------------------------------------------


def test_word_style_indented_paragraphs_never_leak_tag():
    # (a) Đoạn thụt đầu dòng kiểu Word bị gộp với đoạn có nhãn phía trên (mất thông tin đúng,
    # xem Đề xuất trong báo cáo), nhưng không bao giờ lọt nhãn; tiêu đề cắt chuỗi gộp.
    text = f"\tĐoạn 1 {TAG}\n\n\tĐoạn 2\n\n## Mục\n\tĐoạn 3"
    out = confirmed_profile(text)
    assert "Đoạn 1" not in out
    assert out.endswith("## Mục\n\tĐoạn 3")


def test_unindented_paragraphs_after_tagged_paragraph_are_kept():
    text = f"Đoạn 1 {TAG}\n\nĐoạn 2 đúng\n\nĐoạn 3 đúng"
    assert confirmed_profile(text) == "Đoạn 2 đúng\n\nĐoạn 3 đúng"


@pytest.mark.parametrize("ch", INVISIBLE)
def test_line_of_only_invisible_chars_acts_as_blank(ch):
    # (b) Dòng chỉ có ký tự vô hình là dòng trống: tách hai ý, không làm ý sạch bị bỏ theo.
    assert confirmed_profile(f"- A {TAG}\n{ch}\n- B") == f"{ch}\n- B"
    assert confirmed_profile(f"- A\n{ch}\n  tiếp {TAG}\n- B") == "- B"


def test_fullwidth_note_marker_is_dropped():
    assert confirmed_profile("- B\n＞ ghi chú riêng\n  ＞ ghi chú 2") == "- B"
