"""Meta title, meta description, slug (T-036): đếm NFC, kiểm ngưỡng, slug, kiểm trùng, AI gợi ý."""

import unicodedata

import pytest

from seo_app.onpage import meta
from seo_app.onpage.meta import (
    BRAND_SUFFIX,
    Level,
    check_description,
    check_slug,
    check_title,
    make_slug,
    meta_length,
    normalize_meta,
    resolve_brand_suffix,
    strip_brand,
    with_brand,
)

# 54 ký tự NFC, nhiều chữ có dấu chồng (ữ, ặ, ằ…)
TITLE_54 = "Sửa chữa cửa sắt bị xệ tại nhà: dấu hiệu và cách xử lý"
DESC_140 = (
    "Cửa sắt bị xệ, cạ nền khi đóng mở? Xem 5 dấu hiệu sớm, nguyên nhân hay gặp và việc "
    "bạn tự làm được trước khi gọi thợ Pro-Metal đến tận nhà."
)


def nfd(text: str) -> str:
    return unicodedata.normalize("NFD", text)


# ------------------------------------------------------------------ chuẩn hóa, đếm


def test_nfd_counts_like_nfc():
    raw = nfd(TITLE_54)
    assert len(raw) > len(TITLE_54) + 15  # đếm thô dài hơn hẳn
    assert meta_length(raw) == len(TITLE_54) == 54
    assert normalize_meta(raw) == TITLE_54
    assert check_title(raw).level is Level.GOOD
    assert check_title(raw).length == 54


def test_nfd_double_length_text_still_good():
    """Chữ toàn dấu chồng: NFD dài gần gấp đôi (vượt ngưỡng Cảnh báo) mà NFC vẫn Nên."""
    title = "Ữ" * 55
    assert len(nfd(title)) >= 2 * 55
    result = check_title(nfd(title))
    assert result.length == 55
    assert result.level is Level.GOOD


def test_normalize_drops_invisible_and_newlines():
    raw = "Cửa\u200b sắt\u00a0\u00a0bị xệ\n\r\n  ở \u034fđâu\ufeff "
    assert normalize_meta(raw) == "Cửa sắt bị xệ ở đâu"


def test_invisible_char_inside_letter_recombines():
    # "ư" + ZWSP + dấu ngã kết hợp: bỏ ZWSP rồi ghép lại thành "ữ"
    raw = "sư​̃a"
    assert normalize_meta(raw) == "sữa"


# ------------------------------------------------------------------ ngưỡng title / description


@pytest.mark.parametrize(
    ("length", "level"),
    [(10, Level.WARN), (29, Level.WARN), (30, Level.GOOD), (49, Level.GOOD), (50, Level.GOOD),
     (60, Level.GOOD), (61, Level.GOOD), (65, Level.GOOD), (66, Level.WARN), (200, Level.WARN)],
)  # fmt: skip
def test_title_thresholds(length, level):
    result = check_title("a" * length)
    assert result.level is level
    assert result.length == length
    assert result.messages


@pytest.mark.parametrize(
    ("length", "level"),
    [(69, Level.WARN), (70, Level.GOOD), (120, Level.GOOD), (155, Level.GOOD),
     (160, Level.GOOD), (161, Level.WARN)],
)  # fmt: skip
def test_description_thresholds(length, level):
    assert check_description("b" * length).level is level


def test_gray_zone_has_hint():
    assert "hơi ngắn" in check_title("a" * 40).messages[0]
    assert "hơi dài" in check_title("a" * 63).messages[0]
    assert "dài vừa" in check_title(TITLE_54).messages[0]
    assert check_description(DESC_140).level is Level.GOOD


@pytest.mark.parametrize("check", [check_title, check_description])
@pytest.mark.parametrize("raw", ["", "   ", "\n​\t"])
def test_empty_is_blocked(check, raw):
    result = check(raw)
    assert result.level is Level.BLOCK
    assert "trống" in result.messages[0]


@pytest.mark.parametrize("check", [check_title, check_description])
@pytest.mark.parametrize(
    "raw",
    [
        "Cửa sắt <b>bền</b> cho nhà phố",
        "Cửa sắt <script>alert(1)</script> bền",
        "Cửa sắt <img src=x onerror=alert(1)",
        "Cửa sắt <!-- ghi chú --> bền",
    ],
)
def test_html_is_blocked(check, raw):
    result = check(raw)
    assert result.level is Level.BLOCK
    assert any("HTML" in m for m in result.messages)


def test_less_than_sign_alone_is_not_html():
    assert check_title("Cửa rộng < 3 m thì chọn bản lề nào cho bền và êm").level is Level.GOOD


@pytest.mark.parametrize("check", [check_title, check_description])
@pytest.mark.parametrize("raw", ["%%post_title%% | Pro-Metal", "Giảm 50%% hôm nay", "a %​% b"])
def test_double_percent_is_blocked(check, raw):
    result = check(raw)
    assert result.level is Level.BLOCK
    assert any("%%" in m for m in result.messages)


def test_single_percent_is_fine():
    assert check_title("Cửa cuốn khe thoáng giảm 30% nhiệt so với loại kín").level is Level.GOOD


# ------------------------------------------------------------------ hậu tố thương hiệu


def test_brand_added_when_room():
    base = "Cửa sắt bị xệ: nguyên nhân và cách sửa"  # 38 ký tự
    assert with_brand(base) == base + " | Pro-Metal"
    assert len(with_brand(base)) <= 60


def test_brand_not_added_when_no_room():
    base = "a" * 50
    assert with_brand(base) == base


def test_brand_replaces_old_forms():
    for old in (" | Pro Metal", " - Pro-Metal", " – ProMetal", "|pro-metal", " : PRO METAL "):
        assert with_brand("Cửa sắt bị xệ" + old) == "Cửa sắt bị xệ | Pro-Metal"
        assert strip_brand("Cửa sắt bị xệ" + old) == "Cửa sắt bị xệ"


def test_brand_suffix_can_be_turned_off():
    assert with_brand("Cửa sắt bị xệ | Pro Metal", suffix="") == "Cửa sắt bị xệ"


@pytest.mark.parametrize("bad", [None, 123, ["x"], "<b>x</b>", "%%sitetitle%%", "x" * 40])
def test_bad_brand_config_falls_back_to_default(bad):
    assert resolve_brand_suffix(bad) == BRAND_SUFFIX


def test_custom_brand_suffix():
    assert resolve_brand_suffix("— Cơ khí Pro-Metal") == " — Cơ khí Pro-Metal"
    assert with_brand("Cửa sắt", suffix="· Pro") == "Cửa sắt · Pro"


def test_default_constant_is_single_switch(monkeypatch):
    monkeypatch.setattr(meta, "BRAND_SUFFIX", "")
    assert meta.with_brand("Cửa sắt bị xệ") == "Cửa sắt bị xệ"


# ------------------------------------------------------------------ slug


def test_make_slug_basic():
    assert make_slug("Sửa cửa cuốn bị kẹt tại nhà") == "sua-cua-cuon-bi-ket-tai-nha"


def test_make_slug_cut_at_60_on_word_boundary():
    slug = make_slug("cửa sắt " * 30)
    assert len(slug) <= 60
    assert not slug.endswith("-")
    assert set(slug.split("-")) == {"cua", "sat"}


def test_make_slug_drops_trailing_stopwords():
    assert make_slug("Cách chọn bản lề cho cửa sắt và") == "cach-chon-ban-le-cho-cua-sat"
    assert make_slug("Cửa cuốn nên sửa hay thay như thế nào") == "cua-cuon-nen-sua-hay-thay"


def test_make_slug_keeps_cua_door_at_end():
    """«của» là từ nối nhưng «cửa» thì không, dù bỏ dấu đều thành "cua"."""
    assert make_slug("Sửa chữa cửa") == "sua-chua-cua"
    assert make_slug("Bản lề của") == "ban-le"


def test_make_slug_stopword_after_cut():
    # cắt 60 ký tự rơi đúng sau "và" thì "và" cũng bị bỏ
    text = "a" * 55 + " và cửa"
    assert make_slug(text) == "a" * 55


def test_make_slug_all_stopwords_kept():
    assert make_slug("và của") == "va-cua"
    assert make_slug("!!!") == ""


def test_given_slug_wins():
    assert make_slug("Sửa cửa cuốn", given="cua-cuon-quan-7") == "cua-cuon-quan-7"
    assert make_slug("Sửa cửa cuốn", given="Cửa Cuốn Quận 7") == "cua-cuon-quan-7"
    long_given = "-".join(["cua"] * 30)
    assert make_slug("x", given=long_given) == long_given  # không cắt slug người dùng
    assert make_slug("Sửa cửa cuốn", given="   ") == "sua-cua-cuon"


def test_make_slug_nfd_input():
    assert make_slug(nfd("Sửa cửa cuốn")) == "sua-cua-cuon"


@pytest.mark.parametrize(
    ("slug", "level"),
    [
        ("sua-cua-cuon-bi-ket", Level.GOOD),
        ("cua-cuon", Level.GOOD),
        ("", Level.BLOCK),
        ("Sua-cua", Level.BLOCK),
        ("sửa-cửa", Level.BLOCK),
        ("sua_cua", Level.BLOCK),
        ("sua cua", Level.BLOCK),
        ("sua/cua", Level.BLOCK),
        ("sua--cua-cuon", Level.WARN),
        ("-sua-cua-cuon", Level.WARN),
        ("-".join(["ab"] * 8), Level.WARN),
        ("a" * 61, Level.WARN),
    ],
)
def test_check_slug(slug, level):
    result = check_slug(slug)
    assert result.level is level
    assert result.messages


def test_auto_slug_passes_check():
    for text in ("Cửa sắt 2 cánh — giá bao nhiêu?", "cửa sắt " * 30, TITLE_54):
        assert check_slug(make_slug(text)).level is not Level.BLOCK
