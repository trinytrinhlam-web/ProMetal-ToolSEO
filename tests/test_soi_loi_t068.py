"""Soi Lỗi T-068: dọn lỗi Thấp bước code tự sửa alt.

Báo cáo: ``docs/team/reports/T-068-soi-loi.md``.

Kiểm thêm (ngoài test của Thợ Máy trong ``tests/test_t062_alt_prompt.py``):

- C6 (Lá Chắn T-051) vẫn giữ cả với kiểu tiền tố code chưa nhận ra (không dấu, dấu Markdown,
  dấu đầu dòng, ngoặc lạ), giới hạn nhỏ (20) và lớn: alt ảnh AI luôn có tiền tố hoặc báo lỗi.
- Alt chỉ có chữ số hay chữ hệ khác vẫn được nhận; ảnh thật không bao giờ bị code thêm tiền tố.

Test ``xfail(strict=True)`` = lỗi tìm được, mã SL-T068-… khớp báo cáo. Sửa xong thì test báo
XPASS: người sửa gỡ dấu ``xfail``. Không gọi mạng, không gọi AI, không cần .env.
"""

from __future__ import annotations

import unicodedata

import pytest

from seo_app.ai import AIError
from seo_app.images.alt import (
    AI_ALT_PREFIX,
    AI_CAPTION_PREFIX,
    EMPTY_ALT_MESSAGE,
    AltSuggestion,
    clean_suggestion,
)

CAPTION = "ray dưới bị mòn"


def _nfd(text: str) -> str:
    return unicodedata.normalize("NFD", text)


# ------------------------------------------------- C6: ảnh AI luôn có tiền tố


# Kiểu tiền tố AI có thể viết mà code chưa bỏ được (SL-T068-1, -2) hay viết lạ: tiền tố có thể
# lặp, nhưng alt và chú thích vẫn luôn bắt đầu bằng tiền tố chuẩn.
STYLES = [
    "Minh hoa cửa cuốn",
    "MINH HOA: cửa cuốn",
    "Minh hoa",
    "Minh-họa cửa cuốn",
    "Anh minh hoa (AI): ray dưới",
    "Ảnh minh họa AI: ray dưới",
    "Tranh minh họa cửa cuốn",
    "`Minh họa` cửa cuốn",
    "_Minh họa_ cửa cuốn",
    "****Minh họa**** cửa cuốn",
    "- Minh họa cửa cuốn",
    "1. Minh họa cửa cuốn",
    "- Minh họa",
    "`Minh họa`",
    "Minh họa → cửa cuốn",
    "... cửa cuốn",
    "«Minh họa” cửa cuốn",
    "(Minh họa cửa cuốn (2 cánh))",
    "„Minh họa“ cửa cuốn",
    "「Minh họa」 cửa cuốn",
    _nfd("MINH HOẠ!!! «Minh họa» cửa cuốn"),
    "Minh​họa cửa cuốn",
    "Minh họa (AI) Minh hoạ (AI) Minh họa: cửa cuốn",
    "Minh họa: " + "cửacuốnnhàphố" * 10,
    "1️⃣2️⃣",
    "2024",
    "门窗",
]


@pytest.mark.parametrize("limit", [20, 29, 125, 1000])
@pytest.mark.parametrize("text", STYLES)
def test_c6_holds_for_prefix_styles_code_does_not_strip(text, limit):
    raw = AltSuggestion(alt=text, caption=text)
    try:
        result = clean_suggestion(raw, ai_generated=True, max_chars=limit, caption_max_chars=limit)
    except AIError as exc:
        # Báo lỗi nghĩa là không có alt nào được dùng: C6 vẫn giữ.
        assert str(exc) == EMPTY_ALT_MESSAGE
        return
    assert result.alt.startswith(f"{AI_ALT_PREFIX} ") and len(result.alt) <= limit
    assert result.caption == AI_CAPTION_PREFIX or result.caption.startswith(
        f"{AI_CAPTION_PREFIX}: "
    )
    assert len(result.caption) <= limit
    assert any(ch.isalnum() for ch in result.alt.removeprefix(AI_ALT_PREFIX))
    assert unicodedata.is_normalized("NFC", result.alt + result.caption)
    assert "\n" not in result.alt + result.caption and not result.alt.endswith(".")


@pytest.mark.parametrize("ai_generated", [False, True])
@pytest.mark.parametrize("alt", ["2024", "3", "门窗", "Дверь", "ประตู", "باب", "Cửa số 2"])
def test_alt_with_only_digits_or_other_scripts_is_kept(alt, ai_generated):
    # SL-T062-1 chỉ bỏ alt không có chữ cái hay chữ số nào; chữ số và chữ hệ khác vẫn là chữ.
    result = clean_suggestion(AltSuggestion(alt=alt, caption=""), ai_generated=ai_generated)
    body = result.alt.removeprefix(f"{AI_ALT_PREFIX} ") if ai_generated else result.alt
    assert body.casefold() == alt.casefold()
    assert result.alt.startswith(f"{AI_ALT_PREFIX} ") is ai_generated


REAL_TEXTS = [
    "Cửa cuốn kẹt.",
    "Cổng sắt hai cánh đỏ.",
    "- cửa cuốn",
    "`cửa` cuốn",
    "«Cửa cuốn» nhà phố",
    "2024",
    "门窗",
    "cửa cuốn rất dài " * 20,
    _nfd("CỬA CUỐN NHÀ PHỐ"),
]


@pytest.mark.parametrize("limit", [20, 125])
@pytest.mark.parametrize("text", REAL_TEXTS)
def test_real_photo_never_gets_ai_prefix_whatever_the_limit(text, limit):
    raw = AltSuggestion(alt=text, caption=text)
    result = clean_suggestion(raw, max_chars=limit, caption_max_chars=limit)
    for out in (result.alt, result.caption):
        assert "minh" not in out.casefold() and "(ai)" not in out.casefold()
        assert len(out) <= limit


# SL-T068-1 (Thấp): tiền tố AI tự viết không dấu, nối bằng gạch, thiếu ngoặc quanh «AI» hay
# gọi khác («Tranh minh họa», «Hình vẽ minh họa») không được nhận ra: code ghép thêm tiền tố
# chuẩn, alt thành «Minh họa minh hoa cửa cuốn», chú thích «Ảnh minh họa (AI): AI: ray…». Tiền
# tố vẫn còn (C6 giữ). Có từ trước T-068 (``main`` cũng vậy).
@pytest.mark.xfail(strict=True, reason="SL-T068-1: tiền tố không dấu / gọi khác bị lặp")
@pytest.mark.parametrize(
    ("alt", "caption"),
    [
        ("Minh hoa cửa cuốn", f"Anh minh hoa (AI): {CAPTION}"),
        ("MINH HOA: cửa cuốn", f"ANH MINH HOA (AI): {CAPTION}"),
        ("Minh-họa cửa cuốn", f"Ảnh minh họa AI: {CAPTION}"),
        ("Tranh minh họa cửa cuốn", f"Tranh minh họa: {CAPTION}"),
        ("Hình vẽ minh họa cửa cuốn", f"Hình vẽ minh họa (AI) – {CAPTION}"),
    ],
)
def test_sl_t068_1_unaccented_or_renamed_prefix_is_written_once(alt, caption):
    result = clean_suggestion(AltSuggestion(alt=alt, caption=caption), ai_generated=True)
    assert result.alt == "Minh họa cửa cuốn"
    assert result.caption == f"Ảnh minh họa (AI): {CAPTION}"


# Alt chỉ có tiền tố viết như vậy không mô tả gì (như «Minh họa.», SL-T062-1) mà vẫn được nhận.
@pytest.mark.xfail(strict=True, reason="SL-T068-1: alt chỉ có tiền tố không dấu vẫn được nhận")
@pytest.mark.parametrize("alt", ["Minh hoa", "MINH HOA!", "Tranh minh họa"])
def test_sl_t068_1_alt_that_is_only_such_a_prefix_is_refused(alt):
    with pytest.raises(AIError, match="không viết được alt"):
        clean_suggestion(AltSuggestion(alt=alt, caption=""), ai_generated=True)


# SL-T068-2 (Thấp): tiền tố trong dấu Markdown khác «*» («`», «_», «__») hay sau dấu đầu dòng
# («- », «1. », «• ») không được nhận ra: alt thành «Minh họa - Minh họa cửa cuốn», «Minh họa
# `Minh họa` cửa cuốn». Tiền tố vẫn còn (C6 giữ). Có từ trước T-068.
@pytest.mark.xfail(strict=True, reason="SL-T068-2: tiền tố trong Markdown / sau dấu đầu dòng")
@pytest.mark.parametrize(
    ("alt", "caption"),
    [
        ("`Minh họa` cửa cuốn", f"`Ảnh minh họa (AI)` {CAPTION}"),
        ("_Minh họa_ cửa cuốn", f"_Ảnh minh họa (AI)_: {CAPTION}"),
        ("__Minh họa__: cửa cuốn", f"__Ảnh minh họa (AI)__ {CAPTION}"),
        ("- Minh họa cửa cuốn", f"- Ảnh minh họa (AI): {CAPTION}"),
        ("1. Minh họa: cửa cuốn", f"1. Ảnh minh họa (AI): {CAPTION}"),
        ("• Minh họa cửa cuốn", f"• Ảnh minh họa (AI) {CAPTION}"),
    ],
)
def test_sl_t068_2_markdown_or_bulleted_prefix_is_written_once(alt, caption):
    result = clean_suggestion(AltSuggestion(alt=alt, caption=caption), ai_generated=True)
    assert result.alt == "Minh họa cửa cuốn"
    assert result.caption == f"Ảnh minh họa (AI): {CAPTION}"


# Alt chỉ có tiền tố như vậy thành «Minh họa - Minh họa», «Minh họa 1. Minh họa»: không mô tả
# gì mà vẫn được nhận (chạy lại ``clean_suggestion`` trên chính kết quả đó thì lại báo lỗi).
@pytest.mark.xfail(strict=True, reason="SL-T068-2: alt chỉ có tiền tố Markdown vẫn được nhận")
@pytest.mark.parametrize(
    "alt", ["- Minh họa", "`Minh họa`", "_Minh họa_", "1. Minh họa", "• Minh họa"]
)
def test_sl_t068_2_alt_that_is_only_such_a_prefix_is_refused(alt):
    with pytest.raises(AIError, match="không viết được alt"):
        clean_suggestion(AltSuggestion(alt=alt, caption=""), ai_generated=True)


# SL-T068-3 (Thấp): chú thích ảnh AI với ``caption_max_chars`` 20–21 (bộ đọc cho phép từ 20):
# tiền tố «Ảnh minh họa (AI): » chiếm 19 ký tự, phần thân còn 1–2 ký tự nên bị cắt giữa chữ:
# «Ảnh minh họa (AI): r», «Ảnh minh họa (AI): cử». Chú thích được phép chỉ có tiền tố, nên mong
# đợi: không đủ chỗ cho một chữ trọn thì bỏ phần thân. Thợ Máy T-068 đã nêu (Rủi ro, mục 3); có
# từ trước T-068. Sửa ở ``config/`` (nâng mức thấp nhất) không đủ: hàm vẫn nhận giới hạn 20.
@pytest.mark.xfail(strict=True, reason="SL-T068-3: chú thích ảnh AI bị cắt giữa chữ ở 20–21")
@pytest.mark.parametrize(
    ("caption", "limit"), [(CAPTION, 20), (CAPTION, 21), ("cửa cuốn", 20), ("cửa cuốn", 21)]
)
def test_sl_t068_3_ai_caption_body_is_never_a_cut_word(caption, limit):
    raw = AltSuggestion(alt="Cửa cuốn", caption=caption)
    result = clean_suggestion(raw, ai_generated=True, caption_max_chars=limit)
    body = result.caption.removeprefix(AI_CAPTION_PREFIX).removeprefix(": ")
    assert result.caption.startswith(AI_CAPTION_PREFIX) and len(result.caption) <= limit
    assert body == "" or (caption + " ").startswith(body + " ")
