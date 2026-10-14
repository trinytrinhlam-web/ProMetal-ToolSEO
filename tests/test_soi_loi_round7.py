"""Soi Lỗi kiểm thử lượt 7: T-015 lần 2 (lọc sau khi ghép, R6-1 địa chỉ <…>, đo bằng CPU).

Báo cáo: docs/team/reports/T-015-soi-loi.md, mục "Lần 2". Không gọi mạng, không cần .env.
"""

from __future__ import annotations

import random
import re

import pytest
from timing import assert_scales_linearly

from seo_app import sanitize
from seo_app.content.workflow import apply_flag
from seo_app.sanitize import (
    clean_ai_text,
    escape_link_syntax,
    strip_markdown_links,
    unescape_link_syntax,
)

E = "https://evil.example"
LIVE_BRACKET = re.compile(r"(?<!\\)(?:\\\\)*\][(\[]")
# Thẻ HTML, comment, khai báo, và autolink "<scheme:…>" / "<a@b.c>" đều bắt đầu bằng "<" + chữ.
TAG_OR_AUTOLINK = re.compile(r"<[A-Za-z/!?]")


def no_link_left(text: str) -> bool:
    return escape_link_syntax(text) == text and not LIVE_BRACKET.search(text)


# ====================================================== 1. apply_flag: chỗ nối


def _random_piece(rng: random.Random, alphabet: list[str], longest: int) -> str:
    return "".join(rng.choice(alphabet) for _ in range(rng.randint(0, longest)))


def test_apply_flag_random_seams_never_make_tag_link_or_autolink():
    alphabet = list("<>[]()\\:!\"' \n/5a") + [
        "img src=x onerror=alert(1)>",
        "https://evil.example>",
        "a@b.c>",
        "script>",
        "!--",
        "Câu.",
        "Câu. ",
    ]
    rng = random.Random(71)
    for _ in range(30_000):
        body = _random_piece(rng, alphabet, 12) or "x"
        start = rng.randint(0, len(body) - 1)
        sentence = body[start : rng.randint(start + 1, len(body))]
        replacement = _random_piece(rng, alphabet, 6)
        out = apply_flag(body, sentence, replacement)
        assert not TAG_OR_AUTOLINK.search(out), (body, sentence, replacement, out)
        assert no_link_left(out), (body, sentence, replacement, out)


@pytest.mark.parametrize(
    ("body", "sentence", "replacement"),
    [
        ("Xem <5 mm là đủ.", "5 mm là đủ.", "https://evil.example>"),  # autolink trái
        ("Xem <5 mm là đủ.", "5 mm là đủ.", "a@b.c>"),  # autolink email
        ("Câu cũ.https://evil.example> hết", "Câu cũ.", "Xem <"),  # autolink phải
        ("Câu cũ.!-- x --> hết", "Câu cũ.", "<"),  # comment
        ("Câu cũ.?php x ?> hết", "Câu cũ.", "<"),  # khai báo
        ("A <1. /textarea><img src=x onerror=alert(1)>", "1.", ""),  # nhánh bỏ câu
        ("A <<1.script>alert(1)</script>", "1.", ""),
    ],
)
def test_apply_flag_named_seams(body, sentence, replacement):
    out = apply_flag(body, sentence, replacement)
    assert not TAG_OR_AUTOLINK.search(out), out
    assert no_link_left(out)


def test_apply_flag_is_stable_when_applied_twice():
    """Áp cùng gợi ý lên kết quả đã lọc: không đổi thêm (không chồng dấu "\\" hay "< ")."""
    once = apply_flag("Xem [a]Câu cũ. <5 mm", "Câu cũ.", f"({E}) <b>mới</b>")
    assert apply_flag(once, "không-có-câu-này", "x") == once


# ====================================================== 2. R6-1: địa chỉ "<…>"


@pytest.mark.parametrize(
    "text",
    [
        f"[a](<{E}>)",
        f'[a](<{E}> "t")',
        f"[a](<{E}> 't')",
        f"[a](<{E}> (t))",
        f"[a]( <{E}> )",
        f'[a](<{E}>\n"t"\n)',
        "[a](<u\\>v>)",  # ">" escape bên trong
        "[a](<5 mm>)",  # địa chỉ có dấu cách trong <…>
        "[a](<>)",
        f"![a](<{E}> 't')",
    ],
)
def test_real_angle_links_lose_address(text):
    assert strip_markdown_links(text) == "a"
    assert clean_ai_text(text) == "a"


@pytest.mark.parametrize(
    "text",
    [
        f'[a](<{E}>"t")',  # thiếu khoảng trắng trước tiêu đề
        f"[a](<{E}>x)",
        f"[a](<{E}\n>)",  # xuống dòng trong <…>
        f"[a](<{E} <b>)",  # "<" trong <…>
        "[a](<u)v>)",  # ")" trong <…>: link thật theo CommonMark, nay giữ chữ
        f'[a](<{E}>  x "t")',
        "[a](<a<b>)",
    ],
)
def test_odd_angle_forms_never_leave_a_link(text):
    out = clean_ai_text(text)
    assert no_link_left(out), out
    assert not TAG_OR_AUTOLINK.search(out), out


@pytest.mark.parametrize(
    "text",
    [
        "Sai số [cho phép](<0,5 mm) thôi.",
        "Khe [tối đa](< 5 mm) là đủ.",
        "Sai số [cho phép](<0,5 mm> là chuẩn) thôi.",
        "Sai số [cho phép](<0,5 mm>, tức rất nhỏ) thôi.",
        "Sai số [cho phép](<0,5\nmm>) thôi.",
        "Sai số [a](<0,5 mm) và [b](<1 mm) thôi.",
    ],
)
def test_angle_text_keeps_its_words(text):
    out = clean_ai_text(text)
    assert unescape_link_syntax(out) == text, out
    assert no_link_left(out)


def _random_angle_text(rng: random.Random) -> str:
    alphabet = list("[]()<>\"'\\ \n5a") + ["](<", f"](<{E}>", f"](<{E}> ", "(t)", '"t"']
    return "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 24)))


def test_random_angle_text_never_leaves_link_and_round_trips():
    rng = random.Random(72)
    for _ in range(20_000):
        text = _random_angle_text(rng)
        strip_markdown_links(text)
        cleaned = clean_ai_text(text)
        assert no_link_left(cleaned), text
        assert escape_link_syntax(unescape_link_syntax(cleaned)) == cleaned, text
        escaped = escape_link_syntax(text)
        assert escape_link_syntax(unescape_link_syntax(escaped)) == escaped, text
        if "\\" not in text:
            assert unescape_link_syntax(escaped) == text, text


# ====================================================== 3–4. Tốc độ: tra tiêu đề / "<…>" NHIỀU lần


# Mỗi tầng có link mà tiêu đề (hoặc ">") nằm rất xa, và phần sau tiêu đề có chữ nên KHÔNG phải
# link: bộ đọc đi tiếp vào tầng trong và tra lại. Code quét thẳng sẽ bình phương (Lá Chắn T-015).
def _far_title(n: int) -> str:
    """ "[a](x (" ... ") y)": tiêu đề "(" khớp ở rất xa, sau đó " y" → không phải link."""
    return "[a](x (" * n + ") y)" * n


def _lt_unclosed(n: int) -> str:
    """ "<" không có ">" hợp lệ; ">" duy nhất nằm ở cuối chữ."""
    return "[a](<5 " * n + ")" * n + ">"


def _lt_interrupted(n: int) -> str:
    """Có ">" ở cuối nhưng "<" khác chen giữa: mỗi lần tra phải biết có "<" trước ">"."""
    return "[a](<5 <" * n + ")" * n + ">"


MANY_LOOKUPS = {
    "tieu-de-ngoac-xa": (_far_title, 5_000),
    "dau-nho-hon-khong-dong": (_lt_unclosed, 8_000),
    "dau-nho-hon-chen": (_lt_interrupted, 6_000),
}


@pytest.mark.parametrize("case", MANY_LOOKUPS.values(), ids=MANY_LOOKUPS.keys())
def test_many_title_and_angle_lookups_scale_linearly(case):
    build, size = case

    def make(k: int) -> str:
        return build(size * k)

    assert_scales_linearly(strip_markdown_links, make)
    assert_scales_linearly(clean_ai_text, make)
    assert no_link_left(clean_ai_text(make(1)))


def _naive_title_end(self, title):
    """Bản lỗi cố ý: quét thẳng tìm ngoặc/nháy đóng (không dùng bảng tra)."""
    text = self._text
    char = text[title]
    if char == "(":
        depth = 0
        for j in range(title, len(text)):
            if text[j] == "(":
                depth += 1
            elif text[j] == ")":
                depth -= 1
                if depth == 0:
                    return j
        return None
    j = text.find(char, title + 1)
    return j if j != -1 else None


def _naive_angle_end(self, dest):
    """Bản lỗi cố ý: tìm ">" trước bằng vòng lặp từ ``dest``, rồi mới xét "<" / xuống dòng."""
    text = self._text
    end = None
    for j in range(dest + 1, len(text)):
        if text[j] == ">":
            end = j
            break
    if end is None:
        return None
    for j in range(dest + 1, end):
        if text[j] in "<\n":
            return None
    return end


@pytest.mark.parametrize(
    ("method", "naive", "build", "size"),
    [
        ("_title_end", _naive_title_end, _far_title, 150),
        ("_angle_destination_end", _naive_angle_end, _lt_unclosed, 300),
        ("_angle_destination_end", _naive_angle_end, _lt_interrupted, 300),
    ],
)
def test_many_lookup_inputs_catch_naive_scan(monkeypatch, method, naive, build, size):
    """Đầu vào ở trên phải đủ mạnh: bản quét thẳng bị helper bắt (tỉ lệ ~16).

    Cỡ nhỏ hơn ở test tốc độ thật, để bản lỗi (bình phương) không chạy quá lâu.
    """
    monkeypatch.setattr(sanitize._Whitespace, method, naive)
    with pytest.raises(AssertionError):
        assert_scales_linearly(strip_markdown_links, lambda k: build(size * k))
