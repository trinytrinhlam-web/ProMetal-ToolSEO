"""Tìm đoạn dạng shortcode cho cảnh báo trước nút «Gửi nháp» (T-056, LC-T061-4).

Hàm phải theo đúng quy tắc chặn chữ SEO của client (``_has_shortcode``) trên chữ đã gỡ ký tự vô
hình: có đoạn nào thì client cũng coi là shortcode, và ngược lại.
"""

import random
import time

import pytest

from seo_app.wordpress.client import _drop_invisible, _has_shortcode
from seo_app.wordpress.shortcodes import find_shortcodes


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Bài [code_snippet id=3] cuối", ["[code_snippet id=3]"]),
        ("[embed]https://x.example/v[/embed]", ["[embed]", "[/embed]"]),
        ("[[gallery]]", ["[[gallery]"]),
        ("Chưa có: [cần bổ sung: giá cổng 4 m]", ["[cần bổ sung: giá cổng 4 m]"]),
        ("a [b] c [d e=1] f", ["[b]", "[d e=1]"]),
        ("[a [b] c]", ["[a [b]"]),  # "]" gần nhất sau "[" mở đầu, như _has_shortcode
        # Không phải shortcode: dấu cách, "=" hay ký tự cấm ngay sau "[", hay không có "]" sau.
        ("[ 2026 ]", []),
        ("[=x]", []),
        ("[<b>]", []),
        ("[&#91;]", []),
        ("[]", []),
        ("Mở [code_snippet id=3 không đóng", []),
        ("", []),
        ("Chữ thường, không có ngoặc vuông.", []),
    ],
)
def test_finds_each_segment(text, expected):
    assert find_shortcodes(text) == expected
    assert bool(expected) == _has_shortcode(_drop_invisible(text))


@pytest.mark.parametrize(
    "hidden",
    ["​", "‍", "⁠", "﻿", "‮", "⁦", "­", "͏", "ㅤ"],
)
def test_invisible_characters_are_removed_first(hidden):
    """Ký tự vô hình chen trong tên bị gỡ trước khi tới WordPress: đoạn vẫn là shortcode, và
    hiện ra đúng chữ sẽ thành lệnh (không còn ký tự vô hình)."""
    text = f"[{hidden}code{hidden}_snippet id=3{hidden}]"
    assert find_shortcodes(text) == ["[code_snippet id=3]"]


def test_not_text_is_empty():
    for value in (None, 3, b"[code_snippet]", ["[x]"]):
        assert find_shortcodes(value) == []


def test_same_rule_as_client_on_random_text():
    """Đối chiếu ngẫu nhiên với ``_has_shortcode`` (cố định hạt giống để chạy lại được)."""
    rng = random.Random(56)
    alphabet = "[]/=<>& ab​‮\n\t1é"
    for _ in range(5000):
        text = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 14)))
        found = find_shortcodes(text)
        assert bool(found) == _has_shortcode(_drop_invisible(text)), repr(text)
        cleaned = _drop_invisible(text)
        for segment in found:
            assert segment in cleaned
            assert segment.startswith("[") and segment.endswith("]")
            assert _has_shortcode(segment)


def test_long_text_is_linear():
    """Chữ rất dài nhiều "[" không đóng không làm treo (một lượt, dừng khi không còn "]")."""
    text = "[a" * 200_000
    started = time.perf_counter()
    assert find_shortcodes(text) == []
    many = "[a] " * 50_000
    assert len(find_shortcodes(many)) == 50_000
    assert time.perf_counter() - started < 5
