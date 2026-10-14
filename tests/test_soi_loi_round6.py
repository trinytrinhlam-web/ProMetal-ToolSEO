"""Soi Lỗi kiểm thử lượt 6: T-015 (apply_flag bỏ thẻ, R5-1, helper đo tốc độ theo tỉ lệ).

Báo cáo: docs/team/reports/T-015-soi-loi.md. Test ``xfail(strict=True)`` = lỗi THẬT còn lại,
đánh số khớp với báo cáo (R6-…). Khi sửa xong, test báo XPASS và phải gỡ ``xfail``.

Thước đo "không còn tạo được link" giống các lượt trước: ``escape_link_syntax(out) == out`` và
không còn "](" / "][" sống. Không gọi mạng, không cần .env.
"""

from __future__ import annotations

import random
import re

import pytest
import timing
from timing import assert_scales_linearly

from seo_app.content.models import Flag, Review, Scores, Section
from seo_app.content.workflow import apply_flag, apply_replacements, clean_review
from seo_app.sanitize import (
    clean_ai_text,
    escape_link_syntax,
    strip_markdown_links,
    unescape_link_syntax,
)

E = "https://evil.example"
SCORES = Scores(friendly=8, natural=8, readable=8, specific=8, seo=8)
LIVE_BRACKET = re.compile(r"(?<!\\)(?:\\\\)*\][(\[]")
TAG = re.compile(r"<[A-Za-z/!?]")


def no_link_left(text: str) -> bool:
    return escape_link_syntax(text) == text and not LIVE_BRACKET.search(text)


# ====================================================== 1. apply_flag: câu thay thế


@pytest.mark.parametrize(
    "replacement",
    [
        "<scr<script>ipt>alert(1)</script>Câu mới.",
        "<<b>img src=x onerror=alert(1)>Câu mới.",
        "<!-- <script>alert(1)</script> -->Câu mới.",
        "<svg/onload=alert(1)>Câu mới.",
        "<a href='javascript:alert(1)'>Câu mới.</a>",
        "<STYLE>body{}</STYLE>Câu mới.",
        "Câu mới.<img src=x onerror=alert(1)",  # thẻ chưa đóng
    ],
)
def test_apply_flag_replacement_never_brings_tags(replacement):
    out = apply_flag("Câu cũ. Câu sau.", "Câu cũ.", replacement)
    assert not TAG.search(out), out
    assert out.endswith(" Câu sau.")
    assert no_link_left(out)


@pytest.mark.parametrize(
    ("body", "sentence", "replacement"),
    [
        ("Xem [a] Câu cũ.", "Câu cũ.", f"({E})"),  # có dấu cách: không phải link, vẫn an toàn
        ("Xem [a]Câu cũ.", "Câu cũ.", f"({E})"),  # nối "]" với "(" thành "]("
        ("Xem [a]\\Câu", "\\Câu", f"({E})"),  # bỏ dấu "\" escape cũ
        ("Câu cũ.(x) [a]", "Câu cũ.", "[b]"),  # "[b]" nối với "(x)"
        ("Câu cũ.[ref]", "Câu cũ.", "[b]"),  # "[b][ref]": link tham chiếu
        ("Câu cũ.: x", "Câu cũ.", "[b]"),  # "[b]:" ở đầu dòng: khai báo link
        ("[a]\\\\Câu cũ.", "Câu cũ.", f"({E})"),  # "\\\\" là "\" thật, "]" vẫn sống
    ],
)
def test_apply_flag_seams_never_make_links(body, sentence, replacement):
    assert no_link_left(apply_flag(body, sentence, replacement))
    assert no_link_left(apply_flag(body, sentence, ""))


def test_apply_flag_random_seams_never_make_links():
    alphabet = list("[]()<>\\:!\"' \nab") + ["Câu", "img", "script"]
    rng = random.Random(61)
    for _ in range(20_000):
        body = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 20)))
        start = rng.randint(0, len(body) - 1)
        sentence = body[start : rng.randint(start + 1, len(body))]
        replacement = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 10)))
        out = apply_flag(body, sentence, replacement)
        assert no_link_left(out), (body, sentence, replacement)


def test_review_flow_strips_tags_end_to_end():
    """Đường đi thật: gợi ý AI → clean_review → apply_replacements."""
    parts = [Section(heading="Mở bài", body="Câu cũ. Câu sau.")]
    review = Review(
        scores=SCORES,
        flags=[
            Flag(
                section=0,
                sentence="Câu cũ.",
                reason="x",
                replacement=f"<script>alert(1)</script>Câu [mới]({E}).",
            )
        ],
        summary="",
    )
    new_parts, remaining = apply_replacements(parts, clean_review(review).flags)
    assert remaining == []
    body = new_parts[0].body
    assert not TAG.search(body) and "alert" not in body and E not in body, body
    assert no_link_left(body)


@pytest.mark.parametrize(
    ("body", "sentence", "replacement"),
    [
        # "<5" giữ nguyên sau clean_ai_text (sau "<" là chữ số); AI chọn câu bắt đầu từ "5".
        ("Nhiệt độ <5 độ là tốt.", "5 độ là tốt.", "img src=x onerror=alert(1)>"),
        # Bỏ câu (không có câu thay thế): phần sau câu nối vào "<".
        ("Nhiệt độ <1. img src=x onerror=alert(1)>", "1.", ""),
    ],
)
def test_r6_2_seam_with_lt_in_body_makes_tag(body, sentence, replacement):
    assert clean_ai_text(body) == body  # thân bài này đã "sạch" theo bộ lọc hiện tại
    review = Review(
        scores=SCORES,
        flags=[Flag(section=0, sentence=sentence, reason="x", replacement=replacement)],
        summary="",
    )
    flags = clean_review(review).flags
    if replacement:
        new_parts, _ = apply_replacements([Section(heading="H", body=body)], flags)
        out = new_parts[0].body
    else:
        out = apply_flag(body, sentence, "")
    assert not TAG.search(out), out


# ====================================================== 2. looks_like_destination (R5-1)


@pytest.mark.parametrize(
    "text",
    [
        f'[a]({E} "t")',
        f"[a]({E} 't')",
        f"[a]({E} (t))",
        f'[a]({E} "t"   )',
        f'[a]({E} "t"\n)',
        f'[a]({E}\n"t"\n)',
        f'[a]({E} "a\\"b")',  # dấu nháy escape trong tiêu đề
        f'[a]({E} "a\\\\")',  # "\\\\" rồi nháy đóng
        f"[a]({E} 'a\\'b')",
        f'[a]({E} "x (y) z")',  # ngoặc trong tiêu đề nháy
        f"[a]({E} \"nói 'thêm'\")",  # nháy khác loại trong tiêu đề
        f'[a](<{E} x> "t")',
        f'[a]( {E} "t" )',
        f'[a]({E} "")',
        f'![a]({E} "t")',
    ],
)
def test_real_links_with_title_still_lose_address(text):
    out = clean_ai_text(text)
    assert out == "a", out
    assert no_link_left(out)


@pytest.mark.parametrize(
    "text",
    [
        f'[a]({E} "a)b")',  # tiêu đề chứa ")": link thật, nay giữ nguyên chữ (an toàn)
        f'[a]({E} "t" x "u")',
        f'[a]({E} "t")x)',
    ],
)
def test_odd_titles_stay_safe(text):
    out = clean_ai_text(text)
    assert no_link_left(out), out


@pytest.mark.parametrize(
    "text",
    [
        'Cửa [A](dày "mỏng"1mm) nhé.',  # chữ dính ngay sau nháy đóng
        'Cửa [A](dày "mỏng" "dày") nhé.',  # hai tiêu đề
        "Cửa [A](dày 'nó's') nhé.",
        'Cửa [A](dày "mỏng\\") nhé.',  # nháy đóng bị escape: tiêu đề không đóng
        "Cửa [A](dày (mỏng) 1mm) nhé.",
        "Cửa [A](dày (mỏng)1mm) nhé.",
        "Cửa [A](dày “mỏng” 1mm) nhé.",  # nháy cong tiếng Việt không phải tiêu đề
        'Cửa [A](dày "mỏng\n\n" 1mm) nhé.',  # dòng trống cắt đôi
        'Xem [Bảng 1](cột "giá" bên phải) và [Bảng 2](cột "giá" bên trái).',
    ],
)
def test_not_links_keep_their_text(text):
    out = clean_ai_text(text)
    assert unescape_link_syntax(out) == text.strip(), out
    assert no_link_left(out)


@pytest.mark.parametrize(
    "text",
    [
        "Khe hở [tối đa](< 5 mm) là đủ.",
        "Sai số [cho phép](<0,5 mm) thôi.",
        "Sai số [cho phép](<0,5 mm> là chuẩn) thôi.",
    ],
)
def test_r6_1_angle_bracket_without_valid_destination_keeps_text(text):
    assert unescape_link_syntax(clean_ai_text(text)) == text


def _random_link_text(rng: random.Random) -> str:
    alphabet = list("[]()\"'\\ \n<>ab") + ["(x)", '"t"', "'t'", "](", f"]({E} "]
    return "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 24)))


def test_random_quote_heavy_text_never_leaves_link():
    rng = random.Random(62)
    for _ in range(20_000):
        text = _random_link_text(rng)
        strip_markdown_links(text)
        assert no_link_left(clean_ai_text(text)), text


def test_round_trip_still_holds_with_quotes():
    rng = random.Random(63)
    for _ in range(20_000):
        text = _random_link_text(rng)
        escaped = escape_link_syntax(text)
        assert escape_link_syntax(escaped) == escaped, text
        assert escape_link_syntax(unescape_link_syntax(escaped)) == escaped, text
        if "\\" not in text:
            assert unescape_link_syntax(escaped) == text, text
        cleaned = clean_ai_text(text)
        assert escape_link_syntax(unescape_link_syntax(cleaned)) == cleaned, text


TITLE_INPUTS = {
    "nhay-kep-khong-dong": lambda k: '[a](u "' * (12_000 * k),
    "nhay-don-khong-dong": lambda k: "[a](u '" * (12_000 * k),
    "nhay-escape": lambda k: '[a](u "\\"' * (10_000 * k),
    "tieu-de-ngoac-long": lambda k: "[a](u (" * (12_000 * k) + ")" * (24_000 * k),
    "tieu-de-dong-roi-chu": lambda k: '[a](u "t" x ' * (8_000 * k) + ")" * (8_000 * k),
    "nhay-roi-ngoac": lambda k: '"' * (40_000 * k) + "[a](u " * (12_000 * k),
}


@pytest.mark.parametrize("make", TITLE_INPUTS.values(), ids=TITLE_INPUTS.keys())
def test_title_lookup_scales_linearly(make):
    assert_scales_linearly(clean_ai_text, make)
    assert no_link_left(clean_ai_text(make(1)))


# ====================================================== 3. Helper đo tốc độ


def _quadratic(text: str) -> None:
    """Cố ý bình phương: đếm lại từ đầu cho mỗi vị trí (kiểu lỗi hay gặp)."""
    for i in range(0, len(text), 16):
        text.count("a", 0, i)


def test_helper_catches_quadratic_function():
    with pytest.raises(AssertionError):
        assert_scales_linearly(_quadratic, lambda k: "ab" * (20_000 * k))


def test_helper_accepts_linear_function():
    assert_scales_linearly(clean_ai_text, lambda k: "Câu [a](b) <i>c</i>. " * (5_000 * k))


class _BusyClock:
    """Đồng hồ giả mô phỏng máy đang bận (nhiều chương trình khác cùng chạy).

    Lần chạy ngắn (≤ 25 ms) thỉnh thoảng may mắn chạy trọn không bị ngắt; lần chạy dài luôn chỉ
    được 1/3 CPU. Đồng hồ thời gian CPU (``process_time``, ``thread_time``) chỉ tính phần việc
    thật, không tính lúc chờ.
    """

    def __init__(self) -> None:
        self.wall = 0.0
        self.cpu = 0.0
        self._short_runs = 0

    def run(self, work: float) -> None:
        self.cpu += work
        if work <= 0.025:
            self._short_runs += 1
            self.wall += work if self._short_runs % 3 == 2 else 3 * work
        else:
            self.wall += 3 * work

    def perf_counter(self) -> float:
        return self.wall

    monotonic = time = perf_counter

    def perf_counter_ns(self) -> int:
        return int(self.wall * 1e9)

    monotonic_ns = time_ns = perf_counter_ns

    def process_time(self) -> float:
        return self.cpu

    thread_time = process_time

    def process_time_ns(self) -> int:
        return int(self.cpu * 1e9)

    thread_time_ns = process_time_ns


def test_r6_3_helper_stable_on_busy_machine(monkeypatch):
    clock = _BusyClock()
    monkeypatch.setattr(timing, "time", clock)
    # Hàm tuyến tính: 1 µs mỗi ký tự (cỡ nhỏ 20 ms, cỡ lớn 80 ms).
    assert_scales_linearly(lambda text: clock.run(len(text) * 1e-6), lambda k: "a" * 20_000 * k)
