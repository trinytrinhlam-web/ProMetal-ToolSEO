"""T-005: lớp bảo vệ thứ hai ở giao diện — chữ của AI hay người dùng không bao giờ thành HTML.

Các test ở đây cố ý đi VÒNG qua bộ lọc kết quả AI (T-004): chữ độc được đưa thẳng vào trang
(qua ô «Sửa trực tiếp» hoặc trạng thái phiên), để chứng minh riêng phần hiển thị đã an toàn.
"""

import pytest
from fake_ai import FakeProvider
from streamlit.testing.v1 import AppTest

from seo_app.ai import registry as ai_registry
from seo_app.auth import hash_password
from seo_app.ui import highlight, score_panel

PASSWORD = "mat-khau-thu-123"
MALICIOUS = [
    "<script>alert('xss')</script>",
    '<img src="x" onerror="alert(1)">',
    '<a href="javascript:alert(1)">bấm</a>',
    '<iframe src="https://evil.example"></iframe>',
    "<svg onload=alert(1)>",
    "<<script>script>alert(1)<</script>/script>",
]
TAGS = ("<script", "<img", "<iframe", "<a ", "<svg")


def _no_raw_tags(value: str) -> bool:
    low = value.lower()
    return not any(tag in low for tag in TAGS)


# ------------------------------------------------------------------- ui.highlight


@pytest.mark.parametrize("payload", MALICIOUS)
def test_highlight_escapes_flagged_sentence(payload):
    """Câu AI chỉ ra (để tô vàng) cũng có thể chứa HTML: phải escape cả câu đó."""
    out = highlight(f"Mở bài. {payload} Hết.", tone=[payload])
    assert _no_raw_tags(out)
    assert out.count('<mark class="tone">') == 1


@pytest.mark.parametrize("payload", MALICIOUS)
def test_highlight_escapes_missing_part(payload):
    out = highlight(f"Giá {payload}", missing=[payload])
    assert _no_raw_tags(out)
    assert '<mark class="missing">' in out


def test_highlight_only_adds_mark_tags():
    out = highlight("a < b & c > d. Câu máy móc.", tone=["Câu máy móc."])
    assert out == 'a &lt; b &amp; c &gt; d. <mark class="tone">Câu máy móc.</mark>'


def test_highlight_keeps_vietnamese_quotes_and_markdown():
    text = 'Khách hỏi: "Inox 304 có gỉ không?" — **không**, nếu vệ sinh đúng.'
    assert highlight(text) == text


def test_highlight_does_not_mark_inside_inserted_tags():
    """Chữ trùng tên lớp CSS («tone», «mark») không được làm hỏng thẻ <mark> vừa chèn."""
    out = highlight("Câu một tone mark.", tone=["Câu một tone mark."], missing=["tone", "mark"])
    assert out == '<mark class="tone">Câu một tone mark.</mark>'


def test_highlight_ignores_empty_parts():
    assert highlight("Bài viết.", tone=["", "  "], missing=[""]) == "Bài viết."


# ----------------------------------------------------------------- ui.score_panel


def test_score_panel_only_inserts_numbers():
    out = score_panel(90, {"<b>Dễ đọc</b>": 70, "Cụ thể": 150})
    assert "<b>Dễ đọc</b>" not in out and "&lt;b&gt;Dễ đọc&lt;/b&gt;" in out
    assert "width:100%" in out  # điểm vượt 100 bị kẹp lại


def test_score_panel_rejects_non_numeric_score():
    with pytest.raises((TypeError, ValueError)):
        score_panel(90, {"Dễ đọc": '70%"><script>alert(1)</script>'})


# ------------------------------------------------------------- trang Soạn bài


@pytest.fixture
def app_env(monkeypatch):
    monkeypatch.setenv("APP_PASSWORD_HASH", hash_password(PASSWORD, iterations=1_000))
    monkeypatch.setenv("APP_TIMEZONE", "Asia/Ho_Chi_Minh")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


def _article(project_root, monkeypatch) -> AppTest:
    monkeypatch.setattr(ai_registry, "make_provider", lambda name, settings: FakeProvider())
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    at.text_input[0].input(PASSWORD)
    at.button[0].click().run()
    at.switch_page("views/write.py").run()
    at.text_input(key="keyword").input("so sánh inox 201 và 304").run()
    for label in ("🔎 Phân tích từ khóa", "Tiếp: tạo dàn ý →", "✅ Duyệt dàn ý, viết toàn bài →"):
        next(b for b in at.button if b.label == label).click().run()
    assert not at.exception, at.exception
    assert at.session_state["part_ids"]
    return at


def _html_blocks(at: AppTest) -> list[str]:
    return [m.value for m in at.markdown if getattr(m.proto, "allow_html", False)]


def test_manual_edit_with_html_is_shown_as_text(project_root, monkeypatch, app_env):
    """Người dùng dán HTML vào ô «Sửa trực tiếp» (không qua bộ lọc AI): vẫn chỉ là chữ."""
    at = _article(project_root, monkeypatch)
    pid = at.session_state["part_ids"][0]
    at.button(key=f"edit-{pid}").click().run()
    at.text_area(key=f"manual-{pid}").input("Mở bài. " + " ".join(MALICIOUS)).run()
    at.button(key=f"save-{pid}").click().run()
    assert not at.exception, at.exception
    blocks = _html_blocks(at)
    assert any("&lt;script&gt;" in b for b in blocks)  # vẫn hiện cho người dùng thấy
    assert all(_no_raw_tags(b) for b in blocks)


def test_unfiltered_ai_text_in_session_is_shown_as_text(project_root, monkeypatch, app_env):
    """Giả sử bộ lọc kết quả AI (T-004) bỏ sót: phần hiển thị vẫn không dựng HTML."""
    at = _article(project_root, monkeypatch)
    for i, pid in enumerate(at.session_state["part_ids"]):
        at.session_state[f"texts-{pid}"] = [MALICIOUS[i % len(MALICIOUS)]]
        at.session_state[f"ver-{pid}"] = 0
        at.session_state[f"heading-{pid}"] = MALICIOUS[(i + 1) % len(MALICIOUS)]
    at.session_state["article_title"] = MALICIOUS[0]
    at.run()
    assert not at.exception, at.exception
    blocks = _html_blocks(at)
    assert blocks
    assert all(_no_raw_tags(b) for b in blocks)
