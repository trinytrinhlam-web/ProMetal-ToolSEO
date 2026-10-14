"""T-008: gia cố bộ lọc sau T-004 (Soi Lỗi #1–#3, Lá Chắn #1–#4). Không gọi mạng."""

import re
import time

import pytest
from fake_ai import OUTLINE, RESEARCH, FakeProvider

from seo_app.ai import AIRouter, TaskConfig
from seo_app.ai import registry as ai_registry
from seo_app.config import Settings
from seo_app.content import ContentWriter
from seo_app.content.models import Competitor, Draft, Outline, OutlineItem, Research, Section
from seo_app.content.rules import ContentRules
from seo_app.content.workflow import clean_outline, clean_research
from seo_app.sanitize import clean_ai_text, is_safe_url, sanitize_html, strip_tags

# ------------------------------------------------ không thể làm treo app (Lá Chắn #1)

SIZE = 200_000  # ≈ 200 KB, lớn hơn bài dài nhất AI được phép trả (≈ 100 KB)
SLOW_INPUTS = {
    "script": "<script>" * (SIZE // 8),
    "ngoac-vuong": "[" * SIZE,
    "the-long-nhau": "<" * (SIZE // 3) + "a>" * (SIZE // 3),
    "script-khong-dong-ngoac": "<script" * (SIZE // 7),
    "comment-khong-dong": "<!--" * (SIZE // 4),
    "link-mo": "[x](" * (SIZE // 4),
    "dau-link": "](" * (SIZE // 2),
    "ngoac-tron": "(" * SIZE,
    "nhan-nhieu-dong": "[a\n" * (SIZE // 3),
    "khai-bao-link": "[a]:\n" * (SIZE // 5),
    "ngoac-long-sau": "[" * (SIZE // 2) + "](x)" * (SIZE // 8),
    "tron-lan": "<script><style>[x](<iframe>" * (SIZE // 30),
    "the-dong-le": "</script>" * (SIZE // 9),
}


@pytest.mark.parametrize("text", SLOW_INPUTS.values(), ids=SLOW_INPUTS.keys())
def test_filters_run_fast_on_huge_malicious_input(text):
    start = time.perf_counter()
    out = clean_ai_text(text)
    sanitize_html(text)
    assert time.perf_counter() - start < 1.0
    assert not re.search(r"<[A-Za-z/!?]", out)


def test_deeply_nested_tags_leave_no_real_tag():
    # Lồng sâu hơn số lượt bóc: phần còn sót chỉ là chữ, "<" không còn mở được thẻ.
    out = strip_tags("<" * 20 + "script>" + "x>" * 20 + "alert(1)")
    assert not re.search(r"<[A-Za-z/!?]", out)


def test_strip_tags_still_drops_dangerous_blocks_case_insensitively():
    assert strip_tags("A<SCRIPT type=x>alert(1)</script >B") == "AB"
    assert strip_tags("A<script <style>x</style>B") == "A< script B"  # chỉ còn là chữ
    assert strip_tags("A<script>x") == "Ax"  # không có thẻ đóng: chỉ bỏ thẻ


# ------------------------------------------ link Markdown (Soi Lỗi #1, #2)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Xem [a [b] c](https://evil.example) nhé", "Xem a [b] c nhé"),
        ("[x](https://evil.example/a(b(c)))", "x"),
        ("[Xem bảng\ngiá](\nhttps://evil.example\n'tiêu đề')", "Xem bảng\ngiá"),
        ("[a [b](javascript:1)](javascript:2)", "a b"),
        ("Ảnh ![cổng\nsắt](https://evil.example/x.png) đẹp", "Ảnh cổng\nsắt đẹp"),
        ("> [r]: https://evil.example\n\n[x][r]", "[x][r]"),
        ("- [r]:\n  https://evil.example\n\n[x][r]", "[x][r]"),
        ("[nhãn\nhai dòng]:\n https://evil.example\n\n[nhãn hai dòng]", "[nhãn hai dòng]"),
    ],
)
def test_markdown_link_variants_lose_their_target(text, expected):
    assert clean_ai_text(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "Giá (đã gồm VAT) là [cần bổ sung: giá] (chưa có số liệu).",  # "] (" không phải link
        "Mục [1] và [2]: xem bên dưới.",
        "Ngoặc chưa đóng (ví dụ",
        "Cửa [loại A](chưa chốt\n\nđoạn sau) vẫn còn",  # link không vượt dòng trống
        "Escape \\[không phải link\\](x)",
    ],
)
def test_normal_brackets_are_kept(text):
    assert clean_ai_text(text) == text


# ------------------------------------------ is_safe_url (Lá Chắn #2)


@pytest.mark.parametrize(
    "url",
    ["//evil.example", "/\\evil.example", "\\/evil.example", "/\t/evil.example", " //evil"],
)
def test_protocol_relative_urls_are_blocked(url):
    assert not is_safe_url(url)
    assert "href" not in sanitize_html(f'<a href="{url}">x</a>')


@pytest.mark.parametrize("url", ["/lien-he", "?trang=2", "anh.webp", "#muc", "/a//b"])
def test_relative_urls_still_allowed(url):
    assert is_safe_url(url)


# ------------------------------------------ thẻ rỗng nguy hiểm (Soi Lỗi #3, Lá Chắn #4)


@pytest.mark.parametrize("tag", ["input", "base", "link", "meta", "embed", "frame"])
def test_dangerous_void_tags_are_dropped_without_eating_the_rest(tag):
    out = sanitize_html(f"<p>A</p><{tag} src=x onerror=alert(1)><p>B</p>")
    assert out == "<p>A</p><p>B</p>"


def test_dangerous_tags_with_content_still_drop_the_rest_when_unclosed():
    assert sanitize_html("<p>A</p><iframe><p>B</p>") == "<p>A</p>"


# ------------------------------------------ lớp lọc 1 cho nghiên cứu, dàn ý (Lá Chắn #3)

XSS = '<img src=x onerror="alert(1)">'
EVIL_RESEARCH = Research(
    intent=[f"Ý định {XSS}", "Xem [đây](https://evil.example)"],
    article_type="Hướng dẫn<script>x()</script>",
    competitors=[
        Competitor(
            title=f"Đối thủ{XSS}",
            url="https://doithu.vn/bai<script>x</script>",
            covers="Nói về [giá](javascript:alert(1))",
            missing=f"Thiếu ảnh {XSS}",
        )
    ],
    new_angles=["Góc mới<b>"],
    questions=["Hỏi ![a](https://evil.example/t.png)"],
)
EVIL_OUTLINE = Outline(
    title="Tiêu đề<script>x()</script>",
    items=[
        OutlineItem(
            heading=f"Mục 1{XSS}",
            points=["Ý [một](https://evil.example)", f"Ý hai {XSS}"],
            image="Ảnh <iframe src=x></iframe>thật",
        )
    ],
)


def _assert_clean(text: str) -> None:
    lower = text.lower()
    for bad in ("<script", "<img", "<iframe", "<b>", "onerror", "javascript", "evil.example"):
        assert bad not in lower, text


def _strings(model) -> list[str]:
    found: list[str] = []

    def walk(value):
        if isinstance(value, str):
            found.append(value)
        elif isinstance(value, list):
            for item in value:
                walk(item)
        elif hasattr(value, "model_dump"):
            for item in value.__dict__.values():
                walk(item)

    walk(model)
    return found


def test_clean_research_and_outline_clean_every_field():
    research = clean_research(EVIL_RESEARCH)
    outline = clean_outline(EVIL_OUTLINE)
    strings = _strings(research) + _strings(outline)
    assert len(strings) == 14
    for text in strings:
        _assert_clean(text)
    assert research.competitors[0].url == "https://doithu.vn/bai"
    assert outline.title == "Tiêu đề"
    assert outline.items[0].points == ["Ý một", "Ý hai"]


def test_clean_research_keeps_normal_data():
    assert clean_research(RESEARCH) == RESEARCH
    assert clean_outline(OUTLINE) == OUTLINE


TASKS = {
    name: TaskConfig(name=name, provider="anthropic", model="claude-opus-5-5")
    for name in ("research", "outline", "write", "rewrite", "review")
}
RULES = ContentRules(business_profile="", address="", tone="", banned=(), checklist=())


class EvilProvider(FakeProvider):
    def generate(self, task, *, system, prompt, schema):
        self.calls.append((task.name, system, prompt))
        if schema is Research:
            return EVIL_RESEARCH
        if schema is Outline:
            return EVIL_OUTLINE
        if schema is Draft:  # AI bỏ trống tiêu đề → dùng tiêu đề dàn ý
            return Draft(title="", intro="Mở bài.", sections=[Section(heading="M", body="B")])
        return super().generate(task, system=system, prompt=prompt, schema=schema)


@pytest.fixture
def writer(monkeypatch):
    provider = EvilProvider()
    monkeypatch.setattr(ai_registry, "make_provider", lambda name, settings: provider)
    return ContentWriter(AIRouter(TASKS, Settings()), RULES)


def test_research_and_outline_are_cleaned_at_ai_boundary(writer):
    for text in _strings(writer.research("cửa sắt")) + _strings(
        writer.outline("cửa sắt", RESEARCH, {})
    ):
        _assert_clean(text)


def test_title_falls_back_to_cleaned_outline_title(writer):
    # Dàn ý chưa lọc (ví dụ người dùng sửa tay) vẫn không đưa thẻ vào tiêu đề bài.
    title, _ = writer.write("cửa sắt", RESEARCH, {}, EVIL_OUTLINE)
    assert title == "Tiêu đề"
