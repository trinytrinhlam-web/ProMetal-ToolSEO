"""T-031: địa chỉ trần, "www." và email trong chữ AI không thành link bấm được.

Streamlit hiện Markdown bằng remark-gfm, tự biến "http(s)://…", "www.…" và email thành link
(autolink literal) trên chữ ĐÃ GIẢI MÃ ("\\." và "&#46;" thành "."). ``gfm_autolinks`` dưới đây
chép lại hai biểu thức của remark-gfm (mdast-util-gfm-autolink-literal, có trong
``streamlit/static/.../StreamlitMarkdown*.js``), bỏ bớt điều kiện nên bắt RỘNG hơn bản thật.
Đã kiểm thêm bằng chính remark-gfm (node) và markdown-it-py + linkify-it-py ngoài pytest
(xem báo cáo T-031).
"""

from __future__ import annotations

import html.entities
import random
import re

import pytest
from timing import assert_scales_linearly

from seo_app.content.workflow import clean_ai_line
from seo_app.sanitize import (
    AUTOLINK_BREAK,
    break_autolinks,
    clean_ai_text,
    escape_link_syntax,
    unbreak_autolinks,
    unescape_link_syntax,
)

B = AUTOLINK_BREAK
_ESCAPABLE = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
_ENTITY = re.compile(r"&(?:#[xX]([0-9a-fA-F]{1,6})|#([0-9]{1,7})|([A-Za-z][A-Za-z0-9]{0,31}));")
# remark-gfm: /(https?:\/\/|www(?=\.))([-.\w]+)([^ \t\r\n]*)/gi và
# /([-.\w+]+)@([-\w]+(?:\.[-\w]+)+)/gu (bỏ điều kiện ký tự đứng trước và kiểm tra tên miền).
_GFM_URL = re.compile(r"(?:https?://|www(?=\.))[-.\w]+", re.IGNORECASE | re.ASCII)
_GFM_EMAIL = re.compile(r"[-.\w+]+@[-\w]+(?:\.[-\w]+)+", re.ASCII)


def markdown_decode(text: str) -> str:
    """Giải mã như CommonMark: "\\x" (x là dấu câu ASCII) và "&…;" hợp lệ."""
    out, i = [], 0
    while i < len(text):
        if text[i] == "\\" and i + 1 < len(text) and text[i + 1] in _ESCAPABLE:
            out.append(text[i + 1])
            i += 2
            continue
        match = _ENTITY.match(text, i) if text[i] == "&" else None
        if match:
            hex_digits, dec_digits, name = match.groups()
            if name is None:
                code = int(hex_digits, 16) if hex_digits else int(dec_digits)
                out.append(chr(code) if 0 < code < 0x110000 and not 0xD800 <= code < 0xE000
                           else "\ufffd")  # fmt: skip
                i = match.end()
                continue
            if name + ";" in html.entities.html5:
                out.append(html.entities.html5[name + ";"])
                i = match.end()
                continue
        out.append(text[i])
        i += 1
    return "".join(out)


def gfm_autolinks(text: str) -> list[str]:
    decoded = markdown_decode(text)
    return _GFM_URL.findall(decoded) + _GFM_EMAIL.findall(decoded)


def shown(text: str) -> str:
    """Chữ người đọc thấy (ký tự ngắt không hiện ra)."""
    return markdown_decode(text).replace(B, "")


# (chữ AI, chữ người đọc thấy sau khi lọc) — đủ các dạng ở yêu cầu 3 của phiếu
CASES = [
    ("Xem https://evil.example/x ngay", "Xem https://evil.example/x ngay"),
    ("Xem http://evil.example", "Xem http://evil.example"),
    ("HTTPS://EVIL.EXAMPLE/A và Http://evil.example", "HTTPS://EVIL.EXAMPLE/A và Http://evil.example"),
    ("Vào www.evil.example nhé", "Vào www.evil.example nhé"),
    ("Vào WWW.evil.example hoặc Www.Evil.Example", "Vào WWW.evil.example hoặc Www.Evil.Example"),
    ("Gửi thư tới an.nguyen+cua@evil.example", "Gửi thư tới an.nguyen+cua@evil.example"),
    ("Liên hệ mailto:a@evil.example hoặc xmpp:a@evil.example/x", None),
    ("Xem https://evil.example.", "Xem https://evil.example."),
    ("Xem www.evil.example, rồi gọi.", "Xem www.evil.example, rồi gọi."),
    ("Hỏi a@evil.example!", "Hỏi a@evil.example!"),
    ("(https://evil.example/x)", "(https://evil.example/x)"),
    ("(xem www.evil.example)", "(xem www.evil.example)"),
    ("«a@evil.example»", "«a@evil.example»"),
    ("*www.evil.example* và _https://evil.example_", None),
    ("https://sửacửa.vn/giá-cửa", "https://sửacửa.vn/giá-cửa"),
    ("https://xn--sacaa-6ra.vn và www.xn--sacaa-6ra.vn", None),
    ("an@xn--sacaa-6ra.vn và an@sửacửa.vn", None),
    ("https://www.evil.example", "https://www.evil.example"),
    ("https://user@evil.example/a@b", None),
    ("- www.evil.example\n> a@evil.example\n1. https://evil.example", None),
    ("| Trang | Thư |\n|---|---|\n| www.evil.example | a@evil.example |", None),
    # Dạng chỉ thành địa chỉ SAU khi Markdown giải mã
    ("www\\.evil.example", "www.evil.example"),
    ("https\\://evil.example", "https://evil.example"),
    ("https:\\/\\/evil.example", "https://evil.example"),
    ("a\\@evil.example", "a@evil.example"),
    ("a&#64;evil.example", "a@evil.example"),
    ("a&commat;evil.example", "a@evil.example"),
    ("www&#46;evil.example", "www.evil.example"),
    ("&#119;ww.evil.example", "www.evil.example"),
    ("&#x77;&#x57;&#x77;&#x2e;evil.example", "wWw.evil.example"),
    ("https&colon;//evil.example", "https://evil.example"),
    ("https:&sol;&sol;evil.example", "https://evil.example"),
]


@pytest.mark.parametrize(("raw", "expected"), CASES)
def test_bare_addresses_are_not_links_but_still_readable(raw, expected):
    for out in (clean_ai_text(raw), clean_ai_line(raw), escape_link_syntax(raw)):
        assert gfm_autolinks(out) == [], out
        want = expected or markdown_decode(raw)
        assert " ".join(shown(out).split()) == " ".join(want.split())


@pytest.mark.parametrize(
    "text",
    [
        "Giá 1.500.000 đ, giao ở TP.HCM, Q.7 (v.v.). Xem mục 2.3.",
        "Theo dõi @suachuacuasat trên mạng; email: an @ suachuacuasat.com",
        "Khe ray 0,5 mm — 3/4 khách hỏi “bao lâu?”. Tỉ lệ 1:2, giờ 8:30/17:30.",
        "Cửa cuốn, cửa sắt, inox 304 — bền 10 năm!",
        "Đường dẫn C:\\thu-muc\\anh.jpg",
        "ww.evil.example và w w w.evil.example",
        "",
    ],
)
def test_ordinary_text_is_unchanged(text):
    assert B not in clean_ai_text(text)
    assert escape_link_syntax(text) == text


def test_break_points_are_exact():
    assert break_autolinks("https://a.vn") == f"https:/{B}/a.vn"
    assert break_autolinks("www.a.vn") == f"www{B}.a.vn"
    assert break_autolinks("a@b.vn") == f"a{B}@b.vn"
    # Ký tự ngắt chèn vào giữa hai phần gốc, không cắt ngang "\\." hay "&#46;"
    assert break_autolinks("www\\.a.vn") == f"www{B}\\.a.vn"
    assert break_autolinks("www&#46;a.vn") == f"www{B}&#46;a.vn"
    assert break_autolinks("a&#64;b.vn") == f"a{B}&#64;b.vn"
    # "&" không thành mã hợp lệ thì giữ nguyên là chữ
    assert break_autolinks("a&foo;@b.vn") == f"a&foo;{B}@b.vn"


def test_unicode_case_folding_is_not_used():
    """GFM chỉ không phân biệt hoa thường ASCII: "K" (Kelvin), "ſ" không phải "k", "s"."""
    for text in ("\u1e86ww.a.vn", "ẉww.a.vn"):
        assert break_autolinks(text) == text


@pytest.mark.parametrize("raw", [raw for raw, _ in CASES])
def test_idempotent_and_edit_box_round_trip(raw):
    """T-012: ô sửa không hiện ký tự lạ; lưu lại (escape) thì ra đúng như trước."""
    cleaned = clean_ai_text(raw)
    assert escape_link_syntax(cleaned) == cleaned
    box = unescape_link_syntax(cleaned)
    assert B not in box
    assert "\\(" not in box
    assert escape_link_syntax(box) == cleaned


def test_unbreak_only_removes_own_breaks():
    text = f"Chữ{B}có ký tự rộng 0 của AI, w{B}ww.a.vn, :{B}//x"
    assert unbreak_autolinks(text) == text
    assert unbreak_autolinks(f"www{B}.a.vn a{B}@b.vn https:/{B}/c.vn") == (
        "www.a.vn a@b.vn https://c.vn"
    )
    # Ký tự ngắt viết bằng mã "&#8203;" là chữ của AI, không phải do app chèn
    assert unbreak_autolinks("www&#8203;.a.vn") == "www&#8203;.a.vn"


_ALPHABET = [
    "w", "W", ".", ":", "/", "@", "a", "h", "t", "p", "s", "\\", "&", "#", "64;", "46;", "x",
    "evil.vn", " ", "\n", "https://", "www.", "(", ")", "[", "]", "*", "_", "<", ">", B,
    "&#119;", "&period;", "&sol;", "-", "+", "ư",
]  # fmt: skip


def test_fuzz_no_autolink_and_round_trip():
    rnd = random.Random(31)
    for _ in range(4000):
        raw = "".join(rnd.choice(_ALPHABET) for _ in range(rnd.randint(1, 16)))
        cleaned = clean_ai_text(raw)
        assert gfm_autolinks(cleaned) == [], (raw, cleaned)
        assert escape_link_syntax(cleaned) == cleaned, raw
        assert escape_link_syntax(unescape_link_syntax(cleaned)) == cleaned, raw
        # chỉ thêm ký tự ngắt, không đổi chữ người đọc thấy
        escaped = escape_link_syntax(raw)
        assert gfm_autolinks(escaped) == [], (raw, escaped)
        if B not in raw:
            assert shown(escaped) == shown(raw), raw


def test_no_html_entity_can_hide_a_break_point():
    """Mã sinh nhiều ký tự không có "/", ".", "@", ":" sau ký tự đầu (không chèn vào giữa được)."""
    for value in html.entities.html5.values():
        assert not any(char in value[1:] for char in "/.@:"), value


@pytest.mark.parametrize("unit", ["www.", "a@", "https://", "a&#64;", "www\\.", "&amp;x"])
def test_autolink_break_is_linear(unit):
    count = 20000
    assert_scales_linearly(clean_ai_text, lambda k: unit * (count * k // 4), label=unit)
    assert_scales_linearly(unescape_link_syntax, lambda k: (B + unit) * (count * k // 4))
