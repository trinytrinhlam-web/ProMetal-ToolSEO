"""T-083: dọn lỗi chữ nhỏ trong alt, chú thích ảnh AI (Soi Lỗi SL-T068-1, -2, -3, SL-T081-1;
Lá Chắn LC-T068-1; gợi ý G1, G3, G4 của Soi Lỗi T-068).

Kiểm thêm, ngoài các test ``xfail`` đã gỡ trong ``tests/test_soi_loi_t068.py`` và
``tests/test_soi_loi_t081.py``:

- tiền tố AI tự viết kiểu lạ (không dấu, gạch nối, dính liền, «AI» không ngoặc, gọi khác, dấu
  Markdown, dấu đầu dòng, số thứ tự, «(AI)» tách rời) chỉ còn đúng một tiền tố chuẩn; «Minh Hòa»
  (tên riêng) không bị coi là tiền tố; ảnh thật không đổi;
- chú thích ảnh AI không bao giờ cụt giữa chữ; giới hạn không đủ chỗ cho tiền tố thì báo lỗi;
- kết quả là điểm bất động (chạy lại ``clean_suggestion`` không đổi chữ);
- chặn link, shortcode (T-061, T-062, T-081) giữ nguyên với các kiểu tiền tố mới.

Không gọi mạng, không gọi AI.
"""

import pytest
from fake_wordpress import BASE_URL

from seo_app.ai import AIError
from seo_app.content import OutlineItem
from seo_app.images import alt as alt_module
from seo_app.images.alt import (
    AI_ALT_MIN_CHARS,
    AI_ALT_PREFIX,
    AI_CAPTION_MIN_CHARS,
    AI_CAPTION_PREFIX,
    EMPTY_ALT_MESSAGE,
    AltSuggestion,
    clean_suggestion,
)
from seo_app.images.html import figure_html
from seo_app.images.tags import SOURCE_AI
from seo_app.sanitize import escape_link_syntax
from seo_app.storage.drafts import DraftImage as SavedImage
from seo_app.storage.drafts import DraftPart, DraftSnapshot, clean_loaded

BODY = "cửa cuốn khe thoáng màu ghi"
CAPTION_BODY = "lá cửa giúp nhà thông gió"
ALT = f"{AI_ALT_PREFIX} {BODY}"
CAPTION = f"{AI_CAPTION_PREFIX}: {CAPTION_BODY}"


def ai(alt, caption="", **limits):
    return clean_suggestion(AltSuggestion(alt=alt, caption=caption), ai_generated=True, **limits)


# Kiểu tiền tố AI có thể tự viết, mỗi kiểu code phải bỏ trọn để ghi lại đúng một tiền tố chuẩn.
PREFIXES = [
    # SL-T068-1: không dấu, gạch nối, dính liền (G3), «AI» không ngoặc, gọi khác
    "Minh hoa",
    "MINH HOẠ",
    "minh_hoa",
    "Minh-họa",
    "Minh‐họa",  # gạch nối U+2010
    "Minhhọa",
    "Anh minh hoa (AI)",
    "Ảnh minh họa AI",
    "Hinh minh hoa",
    "Hình vẽ minh họa",
    "Hinh ve minh hoa (ai)",
    "Tranh minh họa",
    "Tranh vẽ minh họa",
    "Bức tranh minh họa",
    "Buc anh minh hoa (AI)",
    # SL-T068-2: dấu Markdown, dấu đầu dòng, số thứ tự
    "`Minh họa`",
    "``Minh họa``",
    "_Minh họa_",
    "__Ảnh minh họa (AI)__",
    "- Minh họa",
    "* Minh họa",
    "• Minh họa",
    "1. Minh họa",
    "2) Ảnh minh họa (AI)",
    "10. «Minh họa»",
    # SL-T081-1: «(AI)», «AI» tách khỏi tiền tố hay đứng trước
    "[Minh họa] (AI)",
    "**Ảnh minh họa** (AI)",
    "«Minh họa» (ai)",
    "Minh họa: (AI)",
    "(AI) Minh họa",
    "AI: Minh họa",
]
JOINS = [" ", ": ", " – ", "! "]


@pytest.mark.parametrize("join", JOINS)
@pytest.mark.parametrize("prefix", PREFIXES)
def test_tien_to_ai_tu_viet_chi_con_mot_tien_to_chuan(prefix, join):
    result = ai(f"{prefix}{join}{BODY}", f"{prefix}{join}{CAPTION_BODY}")
    assert result == AltSuggestion(alt=ALT, caption=CAPTION)


@pytest.mark.parametrize("prefix", PREFIXES)
def test_alt_chi_co_tien_to_bi_tu_choi_chu_thich_chi_con_tien_to(prefix):
    with pytest.raises(AIError) as raised:
        ai(prefix)
    assert str(raised.value) == EMPTY_ALT_MESSAGE
    assert ai("Cửa cuốn", prefix).caption == AI_CAPTION_PREFIX


@pytest.mark.parametrize("prefix", PREFIXES)
def test_anh_that_khong_bo_tien_to(prefix):
    text = f"{prefix}: {BODY}"
    result = clean_suggestion(AltSuggestion(alt=text, caption=text))
    assert result == AltSuggestion(alt=escape_link_syntax(text), caption=escape_link_syntax(text))


@pytest.mark.parametrize(
    ("alt", "expected"),
    [
        # Tên riêng, chữ khác: không phải tiền tố, giữ nguyên trong phần thân.
        ("Minh Hòa cửa cuốn", f"{AI_ALT_PREFIX} minh Hòa cửa cuốn"),
        ("Minh Hoàng sơn cổng", f"{AI_ALT_PREFIX} minh Hoàng sơn cổng"),
        ("Minh hoạt cửa cuốn", f"{AI_ALT_PREFIX} minh hoạt cửa cuốn"),
        ("Anh minh cửa cuốn", f"{AI_ALT_PREFIX} anh minh cửa cuốn"),
        ("AIR cửa cuốn", f"{AI_ALT_PREFIX} AIR cửa cuốn"),
        ("Minh họa AIR cửa", f"{AI_ALT_PREFIX} AIR cửa"),
        ("Minh họa ai cũng thích", f"{AI_ALT_PREFIX} ai cũng thích"),
        # Số thứ tự chỉ bỏ khi ngay sau là tiền tố.
        ("1. cửa cuốn", f"{AI_ALT_PREFIX} 1. cửa cuốn"),
        ("Minh họa 2) cửa cuốn", f"{AI_ALT_PREFIX} 2) cửa cuốn"),
        ("2024. Cửa cuốn", f"{AI_ALT_PREFIX} 2024. Cửa cuốn"),
    ],
)
def test_chu_khong_phai_tien_to_duoc_giu(alt, expected):
    assert ai(alt).alt == expected


# G1: phần thân ảnh AI không mở đầu bằng dấu câu, dù AI không viết tiền tố.
@pytest.mark.parametrize("lead", ["- ", ": ", "... ", "… ", "— ", "• ", "| ", "/ ", "· ", "!? "])
def test_dau_cau_dau_phan_than_anh_ai_duoc_bo(lead):
    assert ai(f"{lead}{BODY}", f"{lead}{CAPTION_BODY}") == AltSuggestion(alt=ALT, caption=CAPTION)


# ------------------------------------------------------------- kết quả là điểm bất động


ODD = [
    *(f"{prefix}{join}{BODY}" for prefix in PREFIXES for join in JOINS),
    *(f"{lead}Cửa cuốn" for lead in ["- ", ":", "... ", "(AI) ", "AI "]),
    "(Minh họa cửa cuốn (2 cánh))",
    "«Minh họa” cửa cuốn",
    "„Minh họa“ cửa cuốn",
    "[Minh họa]: [Lưu ý]: Cửa cuốn khe thoáng",
    "[Minh họa] \\: cửa cuốn",
    "Minh họa: \\[lá\\] cửa",
    "Minh họa: «Minh họa» «Minh hoa» - 1. Minh họa: cửa",
    "Minh họa: LED chiếu sáng cổng",
    "Minh họa: " + "cửacuốnnhàphố" * 10,
    "Ảnh minh họa (AI): " + "ray dưới bị mòn, " * 30,
    "Cổng sắt hai cánh đỏ.",
    "2024",
    "门窗",
    "1. Minh_hoa10. Bức ảnh minh họa: cửa",
    "Minhhọacửacuốnnhàphố",
]


@pytest.mark.parametrize(
    ("text", "limit"),
    [("1. Minh_hoa10. Bức ảnh minh họa: cửa", 20), ("Minhhọacửacuốnnhàphố", 16)],
)
def test_cat_giua_chu_lo_ra_tien_to_thi_bo_tiep(text, limit):
    # Phần thân không mở đầu bằng tiền tố («Minh_hoa10», «Minhhọacửa…»), nhưng cắt giữa chữ còn
    # «1. Minh_hoa», «Minhhọa»: bỏ tiếp luôn, không để lần chạy lại mới bỏ (kết quả bất động).
    with pytest.raises(AIError):
        ai(text, max_chars=limit)


@pytest.mark.parametrize("limits", [(20, 20), (29, 21), (57, 40), (125, 200), (500, 1000)])
@pytest.mark.parametrize("text", ODD)
def test_chay_lai_clean_suggestion_khong_doi_chu(text, limits):
    max_chars, caption_max_chars = limits
    kw = {"max_chars": max_chars, "caption_max_chars": caption_max_chars}
    for ai_generated in (True, False):
        try:
            result = clean_suggestion(
                AltSuggestion(alt=text, caption=text), ai_generated=ai_generated, **kw
            )
        except AIError:
            continue
        assert clean_suggestion(result, ai_generated=ai_generated, **kw) == result
        if ai_generated:
            assert result.alt.startswith(f"{AI_ALT_PREFIX} ")
            assert result.caption.startswith(AI_CAPTION_PREFIX)


# --------------------------------------- chú thích ảnh AI không cụt giữa chữ (SL-T068-3)

LONG_CAPTION = "Ray dưới bị mòn, cần thay ray mới và tra dầu bánh xe"


@pytest.mark.parametrize("limit", range(AI_CAPTION_MIN_CHARS, 90))
def test_chu_thich_anh_ai_cat_tron_chu_va_lay_nhieu_chu_nhat(limit):
    result = ai("Cửa cuốn", LONG_CAPTION, caption_max_chars=limit)
    assert result.caption.startswith(AI_CAPTION_PREFIX) and len(result.caption) <= limit
    body = result.caption.removeprefix(AI_CAPTION_PREFIX).removeprefix(": ")
    words = ("r" + LONG_CAPTION[1:]).split(" ")
    room = limit - len(f"{AI_CAPTION_PREFIX}: ")
    if not body:
        # Không đủ chỗ cho chữ đầu tiên thì chỉ còn tiền tố.
        assert len(words[0]) > room
        return
    got = body.split(" ")
    assert got[:-1] == words[: len(got) - 1] and got[-1] == words[len(got) - 1].rstrip(",")
    assert len(got) == len(words) or len(" ".join(words[: len(got) + 1])) > room


@pytest.mark.parametrize("limit", [20, 21, 30, 125])
def test_chu_thich_anh_ai_mot_chu_dai_khong_bi_cat_cut(limit):
    result = ai("Cửa cuốn", "cửacuốnnhàphố" * 20, caption_max_chars=limit)
    assert result.caption == AI_CAPTION_PREFIX


def test_chu_thich_anh_that_van_cat_nhu_truoc():
    # Ảnh thật không đổi cách cắt: một chữ dài vẫn được cắt (không có tiền tố để giữ).
    text = "cửacuốnnhàphố" * 20
    result = clean_suggestion(AltSuggestion(alt="Cửa cuốn", caption=text), caption_max_chars=30)
    assert result.caption == text[:30]


# --------------------------------------------- giới hạn nhỏ: không cắt tiền tố (LC-T068-1)


@pytest.mark.parametrize("limit", range(1, 20))
def test_gioi_han_alt_nho_bao_loi_hay_giu_nguyen_tien_to(limit):
    alt = "Minh họa: 2 cánh cổng sắt sơn đen"
    if limit < AI_ALT_MIN_CHARS:
        with pytest.raises(ValueError, match=f"«{AI_ALT_PREFIX}»"):
            ai(alt, CAPTION_BODY, max_chars=limit)
        return
    result = ai(alt, CAPTION_BODY, max_chars=limit)
    assert result.alt.startswith(f"{AI_ALT_PREFIX} 2") and len(result.alt) <= limit


@pytest.mark.parametrize(
    ("alt", "limit"),
    [
        ("Minh họa: cửa cuốn", 10),
        ("Minh họa: cửa cuốn", 11),
        ("?????????? cửacuốnnhàphốmởmộtnửa", 29),
        ("- Minh họa: " + "cửacuốnnhàphố" * 10, 125),
    ],
)
def test_chu_dau_dai_hon_cho_con_lai_thi_khong_cat_cut(alt, limit):
    # Chữ đầu của phần thân không vừa chỗ sau tiền tố: cắt ra chỉ còn mẩu chữ cụt («cửacuốnnhàp»),
    # không mô tả gì. Alt báo lỗi như alt «???» (SL-T062-1), chú thích chỉ còn tiền tố.
    with pytest.raises(AIError):
        ai(alt, max_chars=limit)
    assert ai("Cửa", alt, caption_max_chars=max(limit, 20)).caption == AI_CAPTION_PREFIX


@pytest.mark.parametrize("limit", range(1, 20))
def test_gioi_han_chu_thich_nho_bao_loi_hay_chi_con_tien_to(limit):
    if limit < AI_CAPTION_MIN_CHARS:
        with pytest.raises(ValueError, match=r"«Ảnh minh họa \(AI\)»"):
            ai(BODY, CAPTION_BODY, caption_max_chars=limit)
        return
    assert ai(BODY, CAPTION_BODY, caption_max_chars=limit).caption == AI_CAPTION_PREFIX


def test_nguong_gioi_han_nho_nhat_dung_bang_tien_to():
    assert len(f"{AI_ALT_PREFIX} x") == AI_ALT_MIN_CHARS
    assert len(AI_CAPTION_PREFIX) == AI_CAPTION_MIN_CHARS


def test_cau_bao_loi_gioi_han_khong_chep_chu_ai():
    with pytest.raises(ValueError) as raised:
        ai("Cửa cuốn bí mật", "chú thích riêng", caption_max_chars=5)
    assert "bí mật" not in str(raised.value) and "riêng" not in str(raised.value)


def test_anh_that_gioi_han_nho_khong_bao_loi():
    result = clean_suggestion(AltSuggestion(alt="Cửa cuốn", caption="Ray"), max_chars=4)
    assert result == AltSuggestion(alt="Cửa", caption="Ray")


# -------------------------------------------- cắt thô trước khi bỏ tiền tố (G4)


def test_bo_tien_to_chi_chay_tren_chu_da_cat_tho(monkeypatch):
    seen = []
    original = alt_module._strip_ai_prefix

    def recording(text):
        seen.append(len(text))
        return original(text)

    monkeypatch.setattr(alt_module, "_strip_ai_prefix", recording)
    text = "Minh họa " * 20_000 + "cửa cuốn"
    result = ai(text, text, max_chars=125, caption_max_chars=200)
    assert {4 * 125, 4 * 200} <= set(seen) and max(seen) == 4 * 200
    # Chữ AI toàn tiền tố lặp, dài quá 4 lần giới hạn: phần thân sau khi cắt thô chỉ còn mẩu tiền
    # tố dở («Minh»), nhưng tiền tố chuẩn vẫn còn nguyên (C6).
    assert result == AltSuggestion(alt=f"{AI_ALT_PREFIX} minh", caption=AI_CAPTION_PREFIX)


def test_tien_to_lap_vai_lan_van_giu_phan_than_o_gioi_han_nho():
    text = "«Ảnh minh họa (AI)»: Ảnh minh họa (AI): Minh họa - cửa kéo sắt"
    assert ai(text, max_chars=20).alt == "Minh họa cửa kéo sắt"


# ------------------------------------- chặn link, shortcode giữ nguyên (T-061, T-062, T-081)

TAILS = [
    "[code_snippet id=1] cửa cuốn",
    "[[code_snippet id=1]] cửa cuốn",
    "[embed]https://example.test/x[/embed] cửa",
    "[cửa cuốn](https://example.test/a) đẹp",
    "<a href='https://example.test/a'>cửa</a> cuốn",
    "<img src=x onerror=alert(1)> cửa",
    "(AI) [gallery ids=1,2] cửa",
]
NEW_PREFIXES = [
    "`Minh họa`",
    "_Minh họa_",
    "- Minh họa:",
    "1. Minh họa",
    "Minh hoa",
    "[Minh họa] (AI):",
]


@pytest.mark.parametrize("tail", TAILS)
@pytest.mark.parametrize("prefix", NEW_PREFIXES)
def test_shortcode_link_sau_tien_to_moi_van_bi_vo_hieu(prefix, tail):
    text = f"{prefix} {tail}"
    result = ai(text, text)
    for stored in (result.alt, result.caption):
        assert escape_link_syntax(stored) == stored
        assert "<" not in stored and "href" not in stored and "onerror" not in stored
    assert clean_suggestion(result, ai_generated=True) == result
    src = f"{BASE_URL}/wp-content/uploads/2026/10/a.webp"
    figure = figure_html(src=src, alt=result.alt, caption=result.caption, width=10, height=10)
    assert "[" not in figure and "]" not in figure and "\\" not in figure
    assert "<a " not in figure and "onerror" not in figure and "javascript" not in figure


# ------------------------------------------ mở lại nháp: đường thứ hai dùng clean_suggestion


def test_mo_lai_nhap_anh_ai_tien_to_kieu_moi_chi_con_mot_tien_to():
    saved = SavedImage(
        source=SOURCE_AI,
        prompt="Cửa cuốn khe thoáng trước nhà phố",
        alt=f"`Minh hoa`: {BODY}",
        caption=f"[Minh họa] (AI): {CAPTION_BODY}",
    )
    snapshot = DraftSnapshot(
        step=2,
        keyword="cửa cuốn khe thoáng",
        outline=[OutlineItem(heading="Mục 1", points=["lá cửa"], image="ảnh cửa cuốn")],
        parts=[DraftPart(heading="Mục 1", versions=["Thân."], image="ảnh", chosen_image=saved)],
    )
    image = clean_loaded(snapshot).parts[0].chosen_image
    assert (image.alt, image.caption) == (ALT, CAPTION)
