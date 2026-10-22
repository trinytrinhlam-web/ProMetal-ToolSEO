"""Soi Lỗi T-065 (rút gọn): quy tắc alt, chữ trong ảnh không chép vào alt lẫn chú thích
(``config/content.toml`` mục ``[alt]``). Báo cáo: ``docs/team/reports/T-065-soi-loi.md``.

Kiểm trên file thật, bằng chính bộ đọc của app (``load_alt_rules``) và hàm dựng lời dặn gửi AI:

- yêu cầu 1–4 của phiếu và ghi chú LC-T062-1 có thật trong file;
- ghi chú «gửi nguyên văn cho hãng AI» là dòng ``#``, không lọt vào lời dặn;
- ví dụ và quy tắc không chứa số điện thoại đủ số, số nhà, địa chỉ trông như thật (đề xuất 1 của
  Ngòi Bút T-065: biến lời nhắc LC-T062-1 thành chốt chặn);
- lời dặn dựng từ quy tắc mới vẫn sạch (không nhãn khung, không ký tự lạ), ảnh AI vẫn ra
  «Minh họa» / «Ảnh minh họa (AI)».

Lỗi tìm thấy được đánh dấu ``xfail(strict=True)`` kèm mã ``SL-T065-n``: sửa xong thì test tự báo
XPASS để gỡ dấu. Không gọi mạng (provider giả), không cần .env.
"""

import io
import re
import unicodedata

import pytest
from PIL import Image

from seo_app.ai.base import ImageInput, TaskConfig
from seo_app.content.rules import BUSINESS_PROFILE_FILE, CONTENT_CONFIG_FILE, load_alt_rules
from seo_app.images.alt import (
    AI_ALT_PREFIX,
    AI_CAPTION_PREFIX,
    AI_PREFIX_NOTE,
    ALT_SYSTEM,
    EXAMPLES_HEADER,
    GUIDANCE_HEADER,
    PRIVATE_INFO_RULE,
    AltSuggestion,
    alt_instructions,
    alt_prompt,
    format_examples,
    format_rules,
    suggest_alt,
)

# Nguyên văn yêu cầu 1 và 2 của phiếu T-065.
YC1_RULE = (
    "Chữ đọc được trong ảnh (biển hiệu, tên cửa hàng, số điện thoại, số nhà, biển số xe, tên "
    "người) không chép vào alt hay chú thích"
)
YC2_SENTENCE = "không ghi vào chú thích điều mà các quy tắc trên cấm ghi trong alt"


def _text() -> str:
    return CONTENT_CONFIG_FILE.read_text(encoding="utf-8")


def _nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def _all_alt_text() -> str:
    """Mọi chữ của mục [alt] sẽ tới hãng AI: quy tắc và đủ 5 trường của từng ví dụ."""
    rules = load_alt_rules()
    parts = list(rules.rules)
    for e in rules.examples:
        parts += [e.image, e.tags, e.good, e.bad, e.why]
    return _nfc("\n".join(parts))


def _comment_block_above(header: str) -> str:
    """Các dòng ``#`` liền ngay trên dòng ``header`` đầu tiên (đọc từ dưới lên, tới dòng khác)."""
    lines = _text().splitlines()
    index = lines.index(header)
    block = []
    for line in reversed(lines[:index]):
        if not line.startswith("#"):
            break
        block.append(line)
    return _nfc(" ".join(reversed(block)))


def _tags(tags: str) -> dict[str, str]:
    out = {}
    for part in tags.split(";"):
        key, sep, value = part.partition(":")
        if sep:
            out[key.strip().casefold()] = value.strip().casefold()
    return out


# ------------------------------------------------------------------ yêu cầu của phiếu


def test_alt_section_still_has_16_rules_and_6_examples_within_limits():
    rules = load_alt_rules()
    assert len(rules.rules) == 16 and len(rules.examples) == 6
    assert (rules.max_chars, rules.caption_max_chars) == (125, 200)
    assert all(len(e.good) <= rules.max_chars for e in rules.examples)
    # Bộ đọc của app báo lỗi khi quá 4.000; giữ chỗ cho bản lưu kiểu Mac (NFD) dài hơn.
    assert len(unicodedata.normalize("NFD", format_rules(rules))) < 4000
    assert len(unicodedata.normalize("NFD", format_examples(rules))) < 4000


def test_yc1_text_in_image_rule_is_verbatim_and_covers_caption():
    rules = [_nfc(r) for r in load_alt_rules().rules]
    assert YC1_RULE in rules
    # Bản cũ (chỉ cấm alt) không còn sót lại song song.
    assert not any(r.endswith("không chép vào alt") for r in rules)


def test_yc2_caption_rule_is_last_and_forbids_what_alt_forbids():
    last = _nfc(load_alt_rules().rules[-1])
    assert last.startswith("Chú thích (caption)")
    assert YC2_SENTENCE in last.casefold()
    assert "caption_max_chars" in last


def test_yc3_no_ward_level_in_alt_section():
    assert "phường" not in _all_alt_text().casefold()
    area_rule = next(r for r in load_alt_rules().rules if r.startswith("Khu vực"))
    assert "chỉ ghi cấp quận/huyện" in area_rule


def test_yc4_good_examples_do_not_state_a_cause():
    # SL-T051-7: «gỉ sét làm cánh cổng xệ» là đoán nguyên nhân. Alt chỉ tả điều thấy được.
    cause = re.compile(r"\b(?:làm cho|làm|do|vì|bởi|nên|khiến)\b")
    found = {e.good: cause.findall(_nfc(e.good).casefold()) for e in load_alt_rules().examples}
    assert {good: words for good, words in found.items() if words} == {}


def test_yc4_before_after_phrase_uses_the_job_named_in_the_tag():
    # SL-T051-7: hạng mục «sơn cửa kéo» mà alt ghi «sau khi sửa». Động từ sau «trước khi» /
    # «sau khi» phải là việc ghi ở thẻ hạng mục.
    checked = 0
    for e in load_alt_rules().examples:
        job = _tags(e.tags).get("hạng mục", "")
        for verb in re.findall(r"\b(?:trước|sau) khi (\w+)", _nfc(e.good).casefold()):
            checked += 1
            assert job.split()[:1] == [verb], (e.good, job)
    assert checked >= 3


def test_lc_t062_1_notes_above_alt_and_examples_say_text_goes_to_ai_verbatim():
    for header in ("[alt]", "[[alt.examples]]"):
        note = _comment_block_above(header).casefold()
        assert "nguyên văn" in note and "hãng ai" in note, header
        assert "bịa" in note and "số điện thoại" in note and "địa chỉ" in note, header
        assert "khách thật" in note, header


def test_comment_lines_never_reach_the_ai():
    system = alt_instructions(load_alt_rules())
    for phrase in ("LƯU Ý", "NGUYÊN VĂN", "người sửa file", "Mọi ví dụ, kể cả bản xau"):
        assert phrase not in system


# ------------------------------------------- không có thông tin trông như thật (LC-T062-1)


def test_rules_and_examples_have_no_real_looking_phone_number():
    # Đề xuất 1 của Ngòi Bút T-065: chỉ chấp nhận số đã che kiểu «0909 xxx xxx».
    squeezed = re.sub(r"[\s.\-()]", "", _all_alt_text())
    assert re.findall(r"(?:\+?84|0)\d{8,10}", squeezed) == []
    assert re.findall(r"\d{7,}", squeezed) == []


def test_rules_and_examples_have_no_house_number_email_or_web_address():
    text = _all_alt_text()
    # Mỗi trường một dòng (``_all_alt_text``): chỉ dò trong một dòng, «Quận 3» cuối dòng này và
    # chữ hoa đầu dòng sau không phải số nhà.
    assert re.findall(r"\b\d+[a-z]?(?:/\d+)* +(?:đường +)?[A-ZĐ]\w*", text) == []
    assert re.findall(r"\bsố +\d+", text.casefold()) == []
    assert re.findall(r"\S+@\S+|https?://|www\.|\.com\b|\.vn\b", text.casefold()) == []


# SL-T065-1: đã sửa ở T-065 lượt 2 (Ngòi Bút đổi «đường Cộng Hòa» thành tên đường bịa), gỡ xfail.
def test_sl_t065_1_example_street_names_are_not_real_addresses_from_profile():
    profile = _nfc(BUSINESS_PROFILE_FILE.read_text(encoding="utf-8")).casefold()
    streets = re.findall(r"\bđường +([A-ZĐ]\w*(?: [A-ZĐ]\w*)*)", _all_alt_text())
    assert streets, "máy dò không thấy tên đường nào để kiểm"
    real = [s.strip() for s in streets if s.strip().casefold() in profile]
    assert real == []


# ------------------------------------------- lời dặn gửi AI dựng từ quy tắc mới


def test_guidance_from_new_rules_has_no_frame_label_or_odd_characters():
    rules = load_alt_rules()
    guidance = format_rules(rules) + "\n" + format_examples(rules)
    assert "<" not in guidance and ">" not in guidance and "du_lieu" not in guidance
    assert "```" not in guidance and "\\" not in guidance
    odd = {
        hex(ord(ch))
        for ch in guidance
        if ch != "\n" and unicodedata.category(ch) in ("Cc", "Cf", "Co", "Cs", "Zl", "Zp")
    }
    assert odd == set()
    assert guidance == _nfc(guidance)


def test_new_rules_stay_after_fixed_frame_in_order():
    rules = load_alt_rules()
    system = alt_instructions(rules)
    assert system.startswith(ALT_SYSTEM)
    assert system.index(PRIVATE_INFO_RULE) < system.index(GUIDANCE_HEADER)
    assert system.index(GUIDANCE_HEADER) < system.index(EXAMPLES_HEADER)
    assert f"- {YC1_RULE}\n" in _nfc(system)
    assert system.count("du_lieu_tham_khao") == ALT_SYSTEM.count("du_lieu_tham_khao")


def _jpeg() -> ImageInput:
    buffer = io.BytesIO()
    Image.new("RGB", (8, 8), (90, 120, 60)).save(buffer, "JPEG")
    return ImageInput(data=buffer.getvalue(), mime="image/jpeg")


class _Returns:
    def __init__(self, value):
        self.value = value
        self.kwargs: dict = {}

    def generate(self, task, **kwargs):
        self.kwargs = kwargs
        return self.value


class _Router:
    def __init__(self, provider):
        self.provider = provider

    def get(self, name):
        return self.provider, TaskConfig(name=name, provider="anthropic", model="claude-x")


@pytest.mark.parametrize(
    ("alt", "caption"),
    [
        ("Cửa cuốn nhà phố mở một nửa", ""),
        ("Hình minh họa cửa cuốn nhà phố", "Cửa cuốn kéo lên một nửa, lá cửa thẳng"),
        ("Cửa cuốn nhà phố.", "Minh họa: cửa cuốn nhà phố"),
    ],
)
def test_ai_image_with_new_project_rules_still_gets_minh_hoa_prefix(alt, caption):
    rules = load_alt_rules()
    provider = _Returns(AltSuggestion(alt=alt, caption=caption))
    result = suggest_alt(_Router(provider), _jpeg(), ai_generated=True, rules=rules)
    assert result.alt.startswith(f"{AI_ALT_PREFIX} ") and result.alt.count(AI_ALT_PREFIX) == 1
    assert result.caption.startswith(AI_CAPTION_PREFIX)
    assert result.caption.casefold().count("minh họa") == 1
    assert len(result.alt) <= rules.max_chars and not result.alt.endswith(".")
    assert provider.kwargs["system"] == alt_instructions(rules)
    assert AI_PREFIX_NOTE in provider.kwargs["prompt"]


def test_ai_image_prompt_with_new_rules_sends_no_tags():
    prompt = alt_prompt(
        {"Hạng mục": "Sửa cửa cuốn", "Khu vực": "Tân Bình"}, "sửa cửa cuốn", ai_generated=True
    )
    frame = prompt.split("<du_lieu_tham_khao>")[1].split("</du_lieu_tham_khao>")[0]
    assert "Tân Bình" not in frame and "Hạng mục" not in frame
