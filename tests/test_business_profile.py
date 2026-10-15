"""T-022 (Soi Lỗi): kiểm thử hồ sơ doanh nghiệp thật ``config/business_profile.md``.

Test bám theo cấu trúc file (tiêu đề "## 8.", nhãn, dòng ghi chú ">", gạch đầu dòng nhiều
dòng), không chép cứng câu chữ: Ngòi Bút còn chỉnh câu sau khi chủ dự án trả lời.
Phần cuối là các trường hợp xấu của bộ lọc từng dòng, T-024 đã sửa (SL-022-1 đến SL-022-6).
"""

from __future__ import annotations

import re
import unicodedata

from seo_app.content.prompts import _neutralize, system_prompt
from seo_app.content.rules import BUSINESS_PROFILE_FILE, confirmed_profile, load_rules

RAW = BUSINESS_PROFILE_FILE.read_text(encoding="utf-8-sig")
RAW_LINES = RAW.splitlines()
VISIBLE = confirmed_profile(RAW)
VISIBLE_LINES = VISIBLE.splitlines()

_HEADING = re.compile(r"^##\s+(\d+)\.")


def _norm(text: str) -> str:
    return unicodedata.normalize("NFC", text).casefold()


TAG = _norm("[CẦN XÁC NHẬN")


def _section(lines: list[str], number: int) -> list[str]:
    """Các dòng nằm dưới tiêu đề "## <number>." cho tới tiêu đề "## " kế tiếp."""
    start = next(
        i for i, line in enumerate(lines) if (m := _HEADING.match(line)) and m[1] == str(number)
    )
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return lines[start + 1 : end]


def _is_note(line: str) -> bool:
    return line.lstrip().startswith(">")


def _blocks(lines: list[str]) -> list[list[int]]:
    """Gạch đầu dòng "- …" cùng các dòng thụt vào ngay sau nó, trả về số thứ tự dòng."""
    blocks: list[list[int]] = []
    for i, line in enumerate(lines):
        if line.startswith("- "):
            blocks.append([i])
        elif (
            blocks
            and blocks[-1][-1] == i - 1
            and line[:1].isspace()
            and line.strip()
            and not _is_note(line)
        ):
            blocks[-1].append(i)
    return blocks


# --- Cấu trúc file thật -------------------------------------------------------------------


def test_profile_file_exists_and_has_sections_1_to_8():
    numbers = [int(m[1]) for line in RAW_LINES if (m := _HEADING.match(line))]
    assert numbers == list(range(1, 9))


def test_profile_has_no_carriage_return_or_bom_after_reading():
    assert "\r" not in RAW
    assert not RAW.startswith("﻿")


# --- Mục 8: quy tắc không được mất ----------------------------------------------------------


def test_every_rule_line_of_section_8_survives_filter():
    rules = [line for line in _section(RAW_LINES, 8) if line.strip() and not _is_note(line)]
    assert len(rules) >= 3, "mục 8 phải có quy tắc"
    lost = [line for line in rules if line.strip() not in VISIBLE]
    assert lost == []


def test_section_8_has_no_tagged_line():
    assert [line for line in _section(RAW_LINES, 8) if TAG in _norm(line)] == []


def test_section_8_is_complete_in_visible_profile():
    raw_rules = [line for line in _section(RAW_LINES, 8) if line.strip() and not _is_note(line)]
    visible_rules = [line for line in _section(VISIBLE_LINES, 8) if line.strip()]
    assert [line.strip() for line in visible_rules] == [line.strip() for line in raw_rules]


# --- Không lọt nhãn, không lọt ghi chú --------------------------------------------------------


def test_no_unconfirmed_tag_reaches_ai_any_case_or_normal_form():
    assert TAG not in _norm(VISIBLE)
    # Phòng biến thể: không còn cả cụm "xác nhận" đi kèm "cần" trong ngoặc vuông.
    assert not re.search(r"\[\s*cần\s+xác\s+nhận", _norm(VISIBLE))


def test_raw_file_really_has_tagged_lines_and_none_survive():
    tagged = [line for line in RAW_LINES if TAG in _norm(line)]
    assert tagged, "file thật phải còn dòng có nhãn để test này có nghĩa"
    for line in tagged:
        assert line not in VISIBLE_LINES


def test_no_note_line_reaches_ai():
    assert [line for line in VISIBLE_LINES if _is_note(line)] == []
    notes = [line for line in RAW_LINES if _is_note(line) and line.lstrip(" >\t").strip()]
    assert notes, "file thật phải có dòng ghi chú để test này có nghĩa"
    for line in notes:
        assert line not in VISIBLE_LINES


def test_multiline_items_are_kept_or_dropped_whole():
    """Một ý nhiều dòng không bị cắt nửa (dòng cụt vào AI hoặc thông tin chưa xác nhận lọt)."""
    kept = set(VISIBLE_LINES)
    broken = []
    for block in _blocks(RAW_LINES):
        status = {RAW_LINES[i] in kept or RAW_LINES[i].strip() in kept for i in block}
        if len(status) > 1:
            broken.append([RAW_LINES[i] for i in block])
    assert broken == []


def test_no_empty_template_bullet_reaches_ai():
    """Gạch đầu dòng chỉ có nhãn mà bỏ trống ("- Câu hỏi khách hay hỏi:") dễ khiến AI bịa."""
    empty = [line for line in VISIBLE_LINES if line.startswith("- ") and line.rstrip()[-1] == ":"]
    assert empty == []


# --- Khung trong system prompt --------------------------------------------------------------


def test_profile_sits_exactly_inside_its_frame_in_system_prompt():
    rules = load_rules()
    assert rules.business_profile == VISIBLE
    prompt = system_prompt(rules)
    # Thẻ mở/đóng của khung đứng riêng một dòng; phần chỉ thị chỉ nhắc tên khung giữa câu.
    assert prompt.count("\n<ho_so_doanh_nghiep>\n") == 1
    assert prompt.count("\n</ho_so_doanh_nghiep>") == 1
    inside = prompt.split("<ho_so_doanh_nghiep>\n", 1)[1].split("\n</ho_so_doanh_nghiep>", 1)[0]
    # _neutralize chuẩn hóa NFKC (vd "…" thành "..."), không bỏ hay thêm dòng nào.
    assert inside == _neutralize(VISIBLE)
    assert len(inside.splitlines()) == len(VISIBLE_LINES)
    outside = prompt.replace(inside, "")
    # Thông tin riêng (hotline) chỉ nằm trong khung, không nằm ở phần chỉ thị.
    phone = re.search(r"0\d(?:[.\s]?\d){8}", VISIBLE)[0]
    assert phone not in outside


# --- Quyết định của chủ dự án (BAN-GIAO.md mục 7.4) -----------------------------------------


def test_no_founding_year_in_visible_profile():
    # Năm 19xx/20xx đứng riêng (không tính ngày quyết định dạng 2026-10-14).
    years = re.findall(r"(?<![\d-])(?:19|20)\d{2}(?![\d-])", VISIBLE)
    assert years == []
    assert not re.search(r"thành lập\s*(năm)?\s*\d", _norm(VISIBLE))
    assert not re.search(r"\d+\s*năm kinh nghiệm", _norm(VISIBLE))


def test_no_vnd_price_in_visible_profile():
    money = re.compile(
        r"\d[\d.,]*\s*(?:đ\b|đồng|vnd|vnđ|k\b|nghìn|ngàn|triệu|tr\b)|(?:giá|chỉ từ|từ)\s*\d",
        re.IGNORECASE,
    )
    assert money.findall(_norm(VISIBLE)) == []


def test_hotline_and_zalo_visible():
    norm = _norm(VISIBLE)
    assert "hotline" in norm
    assert "zalo" in norm
    assert re.search(r"0\d(?:[.\s]?\d){8}", VISIBLE)


def test_call_to_action_uses_same_phone_as_hotline():
    phones = {re.sub(r"\D", "", p) for p in re.findall(r"0\d(?:[.\s]?\d){8}", VISIBLE)}
    assert len(phones) == 1, f"hồ sơ chỉ được có một số điện thoại: {phones}"


def test_section_3_lists_exactly_nine_addresses():
    text = "\n".join(_section(VISIBLE_LINES, 3))
    # Số nhà (vd "728/1", "11A") đứng ngay trước tên đường viết hoa.
    numbers = re.findall(r"(?<![\w./])(\d+[A-Z]?(?:/\d+)?)\s+(?=[A-ZĐÀ-ỹ])", text)
    assert len(numbers) == 9, numbers
    assert len(set(numbers)) == 9, numbers


def test_head_office_of_section_1_is_among_section_3_addresses():
    head = next(line for line in _section(VISIBLE_LINES, 1) if "Trụ sở" in line or "trụ sở" in line)
    number = re.search(r"\d+(?:/\d+)?", head)[0]
    assert number in "\n".join(_section(VISIBLE_LINES, 3))


# --- Trường hợp xấu của bộ lọc từng dòng (T-024 đã sửa) ---------------------------------------


def test_lowercase_tag_is_dropped():
    assert confirmed_profile("- Email: x [cần xác nhận]\n- Hotline: 0909") == "- Hotline: 0909"


def test_multiline_item_with_tag_on_last_line_is_dropped_whole():
    text = "- Khách đã phục vụ: khoảng 500\n  khách [CẦN XÁC NHẬN]\n- Hotline: 0909"
    assert confirmed_profile(text) == "- Hotline: 0909"


def test_multiline_item_with_tag_on_first_line_is_dropped_whole():
    text = "- Khách đã phục vụ: khoảng 500 [CẦN XÁC NHẬN]\n  khách trong năm\n- Hotline: 0909"
    assert confirmed_profile(text) == "- Hotline: 0909"


def test_note_with_leading_space_is_dropped():
    assert confirmed_profile("- Hotline: 0909\n  > ghi chú cho chủ dự án") == "- Hotline: 0909"


def test_note_with_leading_tab_is_dropped():
    assert confirmed_profile("- Hotline: 0909\n\t> ghi chú cho chủ dự án") == "- Hotline: 0909"


def test_nfd_tag_is_dropped():
    text = unicodedata.normalize("NFD", "- Email: x [CẦN XÁC NHẬN]") + "\n- Hotline: 0909"
    assert confirmed_profile(text) == "- Hotline: 0909"


def test_tag_with_nbsp_is_dropped():
    assert confirmed_profile("- Email: x [CẦN XÁC NHẬN]\n- Hotline: 0909") == "- Hotline: 0909"
