"""Kiểm thử trang WordPress trên giao diện (WordPress được giả lập, không gọi mạng)."""

import pytest
from streamlit.testing.v1 import AppTest

from seo_app.auth import hash_password
from seo_app.wordpress import ConnectionInfo, Media, Post, Term, WordPressClient, WordPressError

PASSWORD = "mat-khau-thu-123"


def open_wordpress_page(project_root) -> AppTest:
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    at.text_input[0].input(PASSWORD)
    at.button[0].click().run()
    at.switch_page("views/wordpress.py").run()
    assert not at.exception
    return at


def button(at: AppTest, label: str):
    return next(b for b in at.button if b.label == label)


@pytest.fixture(autouse=True)
def env(monkeypatch):
    monkeypatch.setenv("APP_PASSWORD_HASH", hash_password(PASSWORD, iterations=1_000))
    monkeypatch.setenv("APP_TIMEZONE", "Asia/Ho_Chi_Minh")
    monkeypatch.setenv("WORDPRESS_URL", "https://example.com")
    monkeypatch.setenv("WORDPRESS_USERNAME", "lam")
    monkeypatch.setenv("WORDPRESS_APP_PASSWORD", "abcd efgh")


def test_not_configured_shows_instructions(project_root, monkeypatch):
    monkeypatch.setenv("WORDPRESS_APP_PASSWORD", "")
    at = open_wordpress_page(project_root)
    assert "Chưa khai báo WordPress" in at.warning[0].value
    assert not any(b.label == "Kiểm tra kết nối" for b in at.button)


def test_check_connection_success(project_root, monkeypatch):
    info = ConnectionInfo("ProMetal", "https://example.com", "Lâm", ("editor",), True, True, True)
    monkeypatch.setattr(WordPressClient, "check_connection", lambda self: info)
    at = open_wordpress_page(project_root)

    button(at, "Kiểm tra kết nối").click().run()

    assert "Kết nối thành công" in at.success[0].value
    assert "ProMetal" in at.success[0].value


def test_check_connection_error_is_shown(project_root, monkeypatch):
    def fail(self):
        raise WordPressError("WordPress từ chối đăng nhập.")

    monkeypatch.setattr(WordPressClient, "check_connection", fail)
    at = open_wordpress_page(project_root)

    button(at, "Kiểm tra kết nối").click().run()

    assert at.error[0].value == "WordPress từ chối đăng nhập."


def test_create_draft_from_form(project_root, monkeypatch):
    calls = {}

    def fake_create_draft(self, title, content, **kwargs):
        calls.update(title=title, content=content, **kwargs)
        return Post(42, "draft", title, "", self.edit_link(42))

    monkeypatch.setattr(
        WordPressClient, "list_categories", lambda self: [Term(3, "Cửa sắt", "cua-sat", 1)]
    )
    monkeypatch.setattr(WordPressClient, "list_tags", lambda self: [Term(7, "inox", "inox", 0)])
    monkeypatch.setattr(WordPressClient, "create_draft", fake_create_draft)
    monkeypatch.setattr(
        WordPressClient, "upload_media", lambda *a, **k: Media(9, "https://x/a.jpg")
    )
    at = open_wordpress_page(project_root)

    button(at, "Tải chuyên mục và thẻ").click().run()
    title_input = next(t for t in at.text_input if t.label == "Tiêu đề")
    title_input.input("Bài thử")
    at.text_area[0].input("Đoạn 1\n\nĐoạn 2")
    at.multiselect[0].select(at.multiselect[0].options[0])
    button(at, "Tạo bài nháp").click().run()

    assert not at.exception
    assert "Đã tạo bài nháp #42" in at.success[-1].value
    assert calls["title"] == "Bài thử"
    assert calls["content"] == "<p>Đoạn 1</p>\n<p>Đoạn 2</p>"
    assert calls["categories"] == [3]
    assert calls["featured_media"] is None
