"""Soi Lỗi kiểm thử lượt 5: T-013 (khung «Cần xem lại») và T-014 (\\r, R4-4).

Báo cáo: docs/team/reports/T-013-014-soi-loi.md. Test ``xfail(strict=True)`` = lỗi THẬT còn lại,
đánh số khớp với báo cáo (R5-…). Khi sửa xong, test báo XPASS và phải gỡ ``xfail``.

Thước đo "không còn tạo được link" như lượt 4: ``escape_link_syntax(out) == out`` và không còn
"](" / "][" sống. Kết quả đã được đối chiếu bằng bộ hiển thị Markdown thật (markdown-it-py và
micromark + GFM, chạy tạm ngoài dự án, xem báo cáo). Không gọi mạng, không cần .env.
"""

from __future__ import annotations

import ast
import random
import re
import time

import pytest
from fake_ai import DRAFT, SCORES, FakeProvider
from streamlit.testing.v1 import AppTest

from seo_app.ai import registry as ai_registry
from seo_app.auth import hash_password
from seo_app.content.models import Flag, Review
from seo_app.sanitize import (
    clean_ai_text,
    escape_link_syntax,
    strip_markdown_links,
    unescape_link_syntax,
)

E = "https://evil.example"
PASSWORD = "mat-khau-thu-123"
LIVE_BRACKET = re.compile(r"(?<!\\)(?:\\\\)*\][(\[]")


def no_link_left(text: str) -> bool:
    return escape_link_syntax(text) == text and not LIVE_BRACKET.search(text)


def _load_quote_ai_text(project_root):
    """Lấy riêng hàm ``quote_ai_text`` từ write.py (nhập cả file sẽ chạy trang Streamlit)."""
    source = (project_root / "app" / "views" / "write.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    node = next(
        n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "quote_ai_text"
    )
    namespace = {"escape_link_syntax": escape_link_syntax}
    exec(compile(ast.Module([node], []), "write.py", "exec"), namespace)  # noqa: S102
    return namespace["quote_ai_text"]


@pytest.fixture
def quote_ai_text(project_root):
    return _load_quote_ai_text(project_root)


# Bài (đã lọc) có đủ kiểu "[x]:", "](", "\\]" ở giữa dòng: đoạn con nào cũng có thể là "câu".
BODIES = [
    f"Gọi ngay [thợ]: {E}\n[thợ] nhé.",
    f"Xem [a]({E}) và [b][r] rồi.\n\n[r]: {E}",
    f"Ký hiệu \\]({E}) lạ, và [c] [c]: {E} 'x'\n[c]",
    f"- mục [d]: {E}\n  [d] tiếp\n> [e]: {E}\n[e]",
    f"Câu [h\nnhiều dòng]: {E}\n[h nhiều dòng]",
    f"A [x]\\\\({E}) b [y]\\\\: {E}\n[y]",
]


# ============================================ T-013 · quote_ai_text (khung «Cần xem lại»)


@pytest.mark.parametrize("body", BODIES)
def test_quote_of_any_substring_of_safe_body_has_no_link(quote_ai_text, body):
    safe = clean_ai_text(body)
    assert no_link_left(safe)
    for i in range(len(safe)):
        for j in range(i + 1, min(len(safe), i + 60) + 1):
            sentence = safe[i:j].strip()
            if sentence:
                shown = quote_ai_text(sentence)
                assert no_link_left(shown), (sentence, shown)
                assert all(line.startswith(">") for line in shown.split("\n"))


@pytest.mark.parametrize(
    "sentence",
    [
        f"[thợ]: {E}\r[thợ] nhé.",
        f"[thợ]: {E}\r\n[thợ] nhé.",
        f"x\r\r[thợ]: {E}\r\r[thợ]",
        f"[thợ]\r: {E}",
        "",
        "\n\n",
        "   ",
    ],
)
def test_quote_splits_every_line_break_kind(quote_ai_text, sentence):
    shown = quote_ai_text(sentence)
    assert "\r" not in shown
    assert all(line.startswith(">") for line in shown.split("\n"))
    assert no_link_left(shown)


def test_quote_random_text_has_no_link(quote_ai_text):
    alphabet = list("[]():\\\n\r -ab>*1.!#\"'/=x\t`") + [E, "\r\n", "    ", "&#93;"]
    rng = random.Random(20261014)
    for _ in range(3_000):
        text = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 30)))
        assert no_link_left(quote_ai_text(text)), text


# ============================================== T-013 · dòng "**Gợi ý:** {replacement}"
#
# Họa Sĩ suy luận (chưa có test) là dòng này không tạo được link: replacement đã qua
# clean_ai_text, và tiền tố chỉ làm dòng đầu "bớt đầu dòng" so với lúc escape.

SUGGESTIONS = [
    f"[thợ]: {E}\n\n[thợ]",
    f"x\n[thợ]: {E}\n[thợ]",
    f"[a]({E})",
    f"[a][r]\n\n[r]: {E}",
    f"[r]:\n{E}\n\n[r]",
    f"- [r]: {E}\n[r]",
    f"> [r]: {E}\n\n[r]",
    f"[r]\r[r]: {E}\r",
    f"** [r]: {E}\n[r]",
    f"[r]: <{E}>\n[r]",
    f"[^1]: {E}\n[^1]",
]


@pytest.mark.parametrize("raw", SUGGESTIONS)
def test_suggestion_line_has_no_link(raw):
    shown = f"**Gợi ý:** {clean_ai_text(raw)}"
    assert no_link_left(shown), shown


class _SuggestionProvider(FakeProvider):
    """Lần rà soát đầu không có gợi ý; bấm «Kiểm tra lại» thì AI gợi ý câu thay độc."""

    def __init__(self) -> None:
        super().__init__()
        self.reviews = 0

    def generate(self, task, *, system, prompt, schema):
        if schema is Review:
            self.calls.append((task.name, system, prompt))
            self.reviews += 1
            if self.reviews == 1:
                return Review(scores=SCORES, flags=[], summary="Khá ổn.")
            sentence = DRAFT.sections[0].body.split(".")[0]
            flag = Flag(
                section=1,
                sentence=sentence,
                reason="Nghe máy móc",
                replacement=f"[thợ]: {E} gọi\n\n[thợ]: {E} nữa\n[thợ] nhé.",
            )
            return Review(scores=SCORES, flags=[flag], summary="Khá ổn.")
        return super().generate(task, system=system, prompt=prompt, schema=schema)


def test_suggestion_line_on_page_has_no_link(project_root, monkeypatch):
    monkeypatch.setenv("APP_PASSWORD_HASH", hash_password(PASSWORD, iterations=1_000))
    monkeypatch.setenv("APP_TIMEZONE", "Asia/Ho_Chi_Minh")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    provider = _SuggestionProvider()
    monkeypatch.setattr(ai_registry, "make_provider", lambda name, settings: provider)
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    at.text_input[0].input(PASSWORD)
    at.button[0].click().run()
    at.switch_page("views/write.py").run()
    at.text_input(key="keyword").input("sửa cửa cuốn").run()
    for label in (
        "🔎 Phân tích từ khóa",
        "Tiếp: tạo dàn ý →",
        "✅ Duyệt dàn ý, viết toàn bài →",
        "Kiểm tra lại toàn bài",
    ):
        next(b for b in at.button if b.label == label).click().run()
        assert not at.exception, at.exception
    shown = [m.value for m in at.markdown if m.value.startswith("**Gợi ý:**")]
    assert shown, "không thấy dòng Gợi ý trên trang"
    # Dòng khai báo có chữ phía sau nên bước bỏ link giữ lại; escape thêm "\\" sau "]".
    assert any(value.count("[thợ]\\:") == 2 for value in shown), shown
    for value in shown:
        assert no_link_left(value), value


# ============================================== T-014 · "\r" trong escape / unescape


def _random_text(rng: random.Random, newline_weight: int = 3) -> str:
    alphabet = list("[]():\\ -ab>*1.!`\t") + [E, "cần bổ sung:"] + ["\n", "\r"] * newline_weight
    return "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 30)))


def test_carriage_return_behaves_like_newline():
    """Đổi mọi "\\n" thành "\\r" (hoặc "\\r\\n") thì escape/unescape ra đúng kết quả tương ứng."""
    rng = random.Random(5)
    for _ in range(5_000):
        text = _random_text(rng).replace("\r", "")
        for newline in ("\r", "\r\n"):
            other = text.replace("\n", newline)
            assert escape_link_syntax(other) == escape_link_syntax(text).replace("\n", newline)
            escaped = escape_link_syntax(text)
            assert unescape_link_syntax(escaped.replace("\n", newline)) == unescape_link_syntax(
                escaped
            ).replace("\n", newline)


def test_round_trip_with_carriage_returns():
    rng = random.Random(14)
    for _ in range(20_000):
        text = _random_text(rng)
        escaped = escape_link_syntax(text)
        assert escape_link_syntax(escaped) == escaped, text
        assert escape_link_syntax(unescape_link_syntax(escaped)) == escaped, text
        if "\\" not in text:
            assert unescape_link_syntax(escaped) == text, text


@pytest.mark.parametrize(
    "text",
    [
        f"a\r[r]: {E}\r\r[r]",
        f"> a\r> [r]: {E}\r\r[r]",
        f"- a\r  [r]: {E}\r\r[r]",
        f"[r\r]: {E}\r\r[r\r]",
        f"[r]:\r{E}\r\r[r]",
        f"[x]\r[r]\r\r[r]: {E}",
    ],
)
def test_escape_blocks_definitions_after_lone_carriage_return(text):
    assert no_link_left(escape_link_syntax(text))
    assert "]\\:" in escape_link_syntax(text)


# ============================================ T-014 · R4-4: chỉ bỏ "(…)" là địa chỉ thật


@pytest.mark.parametrize(
    "text",
    [
        f'[a]({E} "t")',
        f"[a]({E} 't')",
        f"[a]({E} (t))",
        f"[a](<{E} x>)",
        f"[a]( {E} )",
        f'[a]({E}\n"t")',
        f'[a]({E}  \n  "t")',
        f'[a]({E}\t"t")',
        f"[a](\n{E}\n)",
        f"[a]({E}\r't')",
    ],
)
def test_real_links_with_title_or_spaces_lose_their_address(text):
    """Các dạng này là link thật theo CommonMark (đã đối chiếu markdown-it-py): phải bỏ địa chỉ."""
    out = clean_ai_text(text)
    assert out == "a"


@pytest.mark.parametrize(
    "text",
    [
        "Cửa kêu [rè rè](sau mưa) là sao?",
        "Gõ [a](x\\ y) thử.",  # "\\ " không phải escape → địa chỉ "x\\" rồi chữ thường
        f'[a]({E}\n\n"t")',  # dòng trống cắt đôi: không phải link
    ],
)
def test_not_links_keep_their_text_and_stay_safe(text):
    out = clean_ai_text(text)
    assert unescape_link_syntax(out) == text.strip()
    assert no_link_left(out)


@pytest.mark.xfail(
    strict=True,
    reason="R5-1 (Thấp, chỉ mất chữ): looks_like_destination chỉ xét ký tự ĐẦU của phần sau "
    "địa chỉ; '(dày \"mỏng\" 1mm)' có chữ sau tiêu đề nên CommonMark không coi là link, nhưng "
    "strip_markdown_links vẫn bỏ cả ngoặc (sanitize.py:205). Không ảnh hưởng an toàn.",
)
@pytest.mark.parametrize(
    "text",
    [
        "Xem [Bảng 1](cột 'giá' bên phải).",
        'Cửa [A](dày "mỏng" 1mm) nhé.',
        "Cửa [A](dày (mỏng) 1mm) nhé.",
    ],
)
def test_r5_1_parenthesis_with_quote_then_more_words_keeps_text(text):
    assert unescape_link_syntax(clean_ai_text(text)) == text


def test_strip_never_crashes_on_whitespace_and_backticks():
    alphabet = list("[]()`\\ \t\n\r\f\v <>\"'ab:!*-1.") + ["cần bổ sung:", "``"]
    rng = random.Random(7)
    for _ in range(20_000):
        text = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 25)))
        strip_markdown_links(text)
        assert no_link_left(clean_ai_text(text)), text


# ==================================== Tốc độ: đo TỈ LỆ thay vì mốc giây (ít chập chờn)


def _best_time(fn, text: str, repeat: int = 3) -> float:
    best = float("inf")
    for _ in range(repeat):
        start = time.perf_counter()
        fn(text)
        best = min(best, time.perf_counter() - start)
    return best


@pytest.mark.parametrize("unit", ["[a]( ", "[]( ", "[](\n", "`a`[b](c d)"])
def test_clean_grows_linearly_on_nested_parentheses(unit):
    """Gấp 4 độ dài thì thời gian tăng xa dưới 16 lần (bình phương).

    Máy chậm làm chậm cả hai lần đo nên tỉ lệ gần như không đổi.
    """
    size = 4_000
    small = unit * size + ")" * size
    large = unit * (4 * size) + ")" * (4 * size)
    ratio = _best_time(clean_ai_text, large) / max(_best_time(clean_ai_text, small), 1e-4)
    assert ratio < 9, ratio
