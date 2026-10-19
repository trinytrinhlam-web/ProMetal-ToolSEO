"""T-044 (Họa Sĩ): chữ lấy từ WordPress và câu lỗi thử mù không thành link trên trang.

- Trang Kết nối WordPress: tên site, địa chỉ site, tên tài khoản, vai trò, chuyên mục, thẻ, tiêu
  đề bài nháp, câu lỗi có chữ của máy chủ (Soi Lỗi SL-T031-1).
- Cài đặt → thử mù: câu lỗi có tên mô hình người dùng gõ dạng ``https://…``, ``www.…``, email
  (Lá Chắn LC-T034-1).

WordPress và AI đều giả (thay phương thức của client / ``run_blind_test``), không gọi mạng (D3).
Bộ dò link viết riêng ở đây: giải mã Markdown như CommonMark rồi tìm địa chỉ trần, ``www.``, email
theo hai biểu thức của remark-gfm (bản Streamlit dùng); cộng thêm link ``[chữ](…)`` / ``[chữ][…]``
và dấu ``<`` chưa escape (thẻ HTML hoặc ``<https://…>``).
"""

from __future__ import annotations

import html
import re

import pytest
from streamlit.testing.v1 import AppTest

import seo_app.config as config
from seo_app.ai import AIError
from seo_app.auth import hash_password
from seo_app.content import blind_test
from seo_app.content.blind_test import HIDDEN_ERROR, BlindEntry, BlindReveal
from seo_app.sanitize import AUTOLINK_BREAK
from seo_app.wordpress import ConnectionInfo, Post, Term, WordPressClient, WordPressError

PASSWORD = "mat-khau-thu-123"

# Chữ "độc" WordPress có thể trả về: link Markdown, địa chỉ trần, www., email, thẻ HTML, định dạng.
HOSTILE = (
    "[Bấm vào đây](https://evil.example/a)",
    "Ghé https://evil.example/b nhé",
    "Xem www.evil.example",
    "Thư: ban@evil.example",
    '<a href="https://evil.example/c">thẻ a</a>',
    "<b>đậm</b> <img src=x onerror=alert(1)>",
    "**đậm** _nghiêng_ `code` # tiêu đề",
    "![ảnh](https://evil.example/d.png)",
    "<https://evil.example/e>",
    "[nhãn][ref]",
)

_PUNCT = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
_BACKSLASH_ESCAPE = re.compile(r"\\([!-/:-@\[-`{-~])")
# Hai biểu thức nhận link tự động của remark-gfm (mdast-util-gfm-autolink-literal), đổi sang Python.
_URL = re.compile(r"(https?://|www(?=\.))[-.\w]+", re.IGNORECASE | re.ASCII)
_EMAIL = re.compile(r"[-.\w+]+@[-\w]+(?:\.[-\w]+)+", re.ASCII)
MARKDOWN_KINDS = ("markdown", "caption", "success", "error", "warning", "info", "title", "header")


def decode(markdown: str) -> str:
    """Chữ bộ đọc Markdown thấy: bỏ dấu escape, giải mã ký tự HTML (rộng hơn CommonMark)."""
    return html.unescape(_BACKSLASH_ESCAPE.sub(r"\1", markdown))


def seen(markdown: str) -> str:
    """Chữ người đọc thấy (ký tự ngắt rộng 0 không hiện)."""
    return decode(markdown).replace(AUTOLINK_BREAK, "")


def link_problems(markdown: str) -> list[str]:
    """Những chỗ trong một đoạn Markdown có thể thành link hay HTML khi hiện."""
    problems: list[str] = []
    i, n = 0, len(markdown)
    while i < n:
        char = markdown[i]
        if char == "\\" and i + 1 < n and markdown[i + 1] in _PUNCT:
            i += 2
            continue
        if char == "]" and markdown[i + 1 : i + 2] in ("(", "["):
            problems.append(f"link Markdown ở vị trí {i}")
        elif char == "<":
            problems.append(f"'<' chưa escape ở vị trí {i}")
        i += 1
    text = decode(markdown)
    problems += [f"địa chỉ: {m.group(0)}" for m in _URL.finditer(text)]
    problems += [f"email: {m.group(0)}" for m in _EMAIL.finditer(text)]
    return problems


def markdown_elements(at: AppTest, kinds=MARKDOWN_KINDS) -> list:
    return [el for kind in kinds for el in getattr(at, kind)]


def assert_no_links(at: AppTest, kinds=MARKDOWN_KINDS) -> None:
    assert not at.exception, at.exception
    for el in markdown_elements(at, kinds):
        assert link_problems(el.value) == [], el.value
        assert not getattr(el.proto, "allow_html", False), el.value


def button(at: AppTest, label: str):
    return next(b for b in at.button if b.label == label)


# --------------------------------------------------------------- tự kiểm bộ dò


@pytest.mark.parametrize("raw", HOSTILE)
def test_detector_catches_raw_hostile_text(raw):
    # Bộ dò phải bắt được chữ độc khi CHƯA escape, nếu không các test dưới vô nghĩa.
    assert link_problems(raw) or "**" in raw


# ------------------------------------------------------------ trang WordPress


@pytest.fixture
def wp_env(monkeypatch):
    monkeypatch.setenv("APP_PASSWORD_HASH", hash_password(PASSWORD, iterations=1_000))
    monkeypatch.setenv("APP_TIMEZONE", "Asia/Ho_Chi_Minh")
    monkeypatch.setenv("WORDPRESS_URL", "https://example.com")
    monkeypatch.setenv("WORDPRESS_USERNAME", "lam")
    monkeypatch.setenv("WORDPRESS_APP_PASSWORD", "abcd efgh")


def open_wordpress_page(project_root) -> AppTest:
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    at.text_input[0].input(PASSWORD)
    at.button[0].click().run()
    at.switch_page("views/wordpress.py").run()
    assert not at.exception, at.exception
    return at


@pytest.mark.usefixtures("wp_env")
@pytest.mark.parametrize("hostile", HOSTILE)
def test_wordpress_texts_never_become_links(project_root, monkeypatch, hostile):
    info = ConnectionInfo(
        f"Site {hostile}",
        "https://evil.example/site",
        f"Người {hostile}",
        (f"vai {hostile}", "editor"),
        True,
        True,
        True,
    )
    terms = [Term(3, f"Mục {hostile}", "muc", 1)]
    monkeypatch.setattr(WordPressClient, "check_connection", lambda self: info)
    monkeypatch.setattr(WordPressClient, "list_categories", lambda self: terms)
    monkeypatch.setattr(WordPressClient, "list_tags", lambda self: [Term(7, hostile, "the", 0)])
    def fake_create_draft(self, title, content, **kwargs):
        return Post(42, "draft", f"Bài {hostile}", "", self.edit_link(42))

    monkeypatch.setattr(WordPressClient, "create_draft", fake_create_draft)
    at = open_wordpress_page(project_root)
    button(at, "Kiểm tra kết nối").click().run()
    button(at, "Tải chuyên mục và thẻ").click().run()
    next(t for t in at.text_input if t.label == "Tiêu đề").input("Bài thử")
    button(at, "Tạo bài nháp").click().run()

    assert_no_links(at)
    shown = "\n".join(seen(el.value) for el in markdown_elements(at))
    collapsed = " ".join(hostile.split())
    # Người đọc vẫn thấy nguyên chữ (chỉ là chữ thường).
    for expected in (f"Site {collapsed}", f"Người {collapsed}", f"vai {collapsed}",
                     "https://evil.example/site", f"Bài {collapsed}"):
        assert expected in shown
    # Bảng chuyên mục/thẻ (st.dataframe, chữ thường) giữ nguyên tên.
    names = [list(frame.value["Tên"]) for frame in at.dataframe]
    assert names == [[f"Mục {hostile}"], [hostile]]


@pytest.mark.usefixtures("wp_env")
@pytest.mark.parametrize("action", ["Kiểm tra kết nối", "Tải chuyên mục và thẻ", "Tạo bài nháp"])
def test_wordpress_error_with_site_text_is_plain(project_root, monkeypatch, action):
    message = "WordPress báo lỗi (mã 400). (WordPress: " + " · ".join(HOSTILE) + ")"

    def fail(self, *args, **kwargs):
        raise WordPressError(message, status_code=400)

    for name in ("check_connection", "list_categories", "create_draft"):
        monkeypatch.setattr(WordPressClient, name, fail)
    at = open_wordpress_page(project_root)
    if action == "Tạo bài nháp":
        next(t for t in at.text_input if t.label == "Tiêu đề").input("Bài thử")
    button(at, action).click().run()

    assert len(at.error) == 1
    assert_no_links(at)
    assert seen(at.error[0].value) == " ".join(message.split())


@pytest.mark.usefixtures("wp_env")
def test_wrong_types_from_wordpress_do_not_crash_page(project_root, monkeypatch):
    # Lượt 2 (SL-T044-1, SL-T044-2): mọi trường lấy từ WordPress sai kiểu vẫn hiện được.
    info = ConnectionInfo(None, ["www.evil.example"], 7, (1, None, "editor"), True, True, True)
    monkeypatch.setattr(WordPressClient, "check_connection", lambda self: info)

    def fake_create_draft(self, title, content, **kwargs):
        return Post(42, "draft", None, "", self.edit_link(42))

    monkeypatch.setattr(WordPressClient, "create_draft", fake_create_draft)
    at = open_wordpress_page(project_root)
    button(at, "Kiểm tra kết nối").click().run()
    next(t for t in at.text_input if t.label == "Tiêu đề").input("Bài thử")
    button(at, "Tạo bài nháp").click().run()

    assert_no_links(at)
    shown = "\n".join(seen(el.value) for el in markdown_elements(at))
    assert "(['www.evil.example'])" in shown
    assert "Tài khoản: **7** — vai trò: 1, , editor" in shown
    assert any(b.label == "Mở bài trong trang quản trị WordPress" for b in at.get("link_button"))


@pytest.mark.usefixtures("wp_env")
def test_bad_wordpress_url_message_is_plain(project_root, monkeypatch):
    # Câu lỗi cấu hình chép lại WORDPRESS_URL: địa chỉ đó cũng không thành link.
    monkeypatch.setenv("WORDPRESS_URL", "www.evil.example")
    at = open_wordpress_page(project_root)
    assert "không hợp lệ" in at.warning[0].value
    assert_no_links(at)
    assert "'www.evil.example'" in seen(at.warning[0].value)


@pytest.mark.usefixtures("wp_env")
def test_account_email_in_caption_is_plain(project_root, monkeypatch):
    monkeypatch.setenv("WORDPRESS_USERNAME", "ban@evil.example")
    at = open_wordpress_page(project_root)
    assert_no_links(at)
    assert "Tài khoản: ban@evil.example" in seen(at.caption[0].value)


# --------------------------------------------------------- Cài đặt → thử mù

# Trang Cài đặt có link cố định (nơi lấy khóa API) ở tab khác: chỉ xét ô lỗi và cảnh báo.
BLIND_KINDS = ("error", "warning")


@pytest.fixture
def blind_env(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_PASSWORD_HASH", hash_password(PASSWORD, iterations=1_000))
    monkeypatch.setattr(config, "DEFAULT_ENV_FILE", tmp_path / ".env")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "khoa-gia-anthropic")
    monkeypatch.setenv("OPENAI_API_KEY", "khoa-gia-openai")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)


def open_models_tab(project_root) -> AppTest:
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    at.text_input[0].input(PASSWORD)
    at.button[0].click().run()
    at.switch_page("views/settings.py").run()
    assert not at.exception, at.exception
    return at


class FakeRun:
    def __init__(self, result=None, exc: Exception | None = None):
        self.result, self.exc = result, exc

    def __call__(self, keyword, note, candidates, settings, rules, **kwargs):
        if self.exc:
            raise self.exc
        return self.result


URL_MODELS = ("https://x.y", "www.evil.example", "ban@evil.example", "http://evil.example/m")


@pytest.mark.usefixtures("blind_env")
@pytest.mark.parametrize("model", URL_MODELS)
def test_blind_reveal_error_with_url_model_is_plain(project_root, monkeypatch, model):
    entries = [
        BlindEntry("A", intro="Mở bài A.", heading="Mục A", body="Thân A."),
        BlindEntry("B", error=HIDDEN_ERROR),
    ]
    real_error = f"Không có mô hình «{model}» ở hãng này."
    reveal = {
        "A": BlindReveal("A", "anthropic", "Anthropic (Claude)", "claude-thu-1", "medium"),
        "B": BlindReveal("B", "openai", "OpenAI", model, "medium", error=real_error),
    }
    monkeypatch.setattr(blind_test, "run_blind_test", FakeRun(result=(entries, reveal)))
    at = open_models_tab(project_root)
    at.text_input(key="blind-keyword").input("cửa sắt")
    at.text_input(key="blind-cand-0-model").input("claude-thu-1")
    at.text_input(key="blind-cand-1-model").input(model)
    at.run()
    assert not at.button(key="blind-run").disabled  # tên kiểu địa chỉ vẫn qua bộ lọc tên
    at.button(key="blind-run").click().run()
    at.button(key="blind-reveal").click().run()

    errors = [e for e in at.error if "Bài B" in e.value]
    assert len(errors) == 1
    assert_no_links(at, BLIND_KINDS)
    assert seen(errors[0].value) == f"Bài B (OpenAI · {model}): {real_error}"


@pytest.mark.usefixtures("blind_env")
@pytest.mark.parametrize("model", URL_MODELS)
def test_blind_run_error_with_url_model_is_plain(project_root, monkeypatch, model):
    message = f"Ứng viên 2: không gọi được mô hình «{model}»."
    monkeypatch.setattr(blind_test, "run_blind_test", FakeRun(exc=AIError(message)))
    at = open_models_tab(project_root)
    at.text_input(key="blind-keyword").input("cửa sắt")
    at.text_input(key="blind-cand-0-model").input("claude-thu-1")
    at.text_input(key="blind-cand-1-model").input(model)
    at.run()
    at.button(key="blind-run").click().run()

    assert [seen(e.value) for e in at.error] == [message]
    assert_no_links(at, BLIND_KINDS)
