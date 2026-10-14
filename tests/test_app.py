"""Kiểm thử màn hình đăng nhập bằng bộ giả lập của Streamlit (không mở trình duyệt)."""

import pytest
from streamlit.testing.v1 import AppTest

from seo_app.auth import hash_password

PASSWORD = "mat-khau-thu-123"


@pytest.fixture
def app(project_root, monkeypatch):
    monkeypatch.setenv("APP_PASSWORD_HASH", hash_password(PASSWORD, iterations=1_000))
    monkeypatch.setenv("APP_TIMEZONE", "Asia/Ho_Chi_Minh")
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    return at


def test_shows_login_form_first(app):
    assert app.title[0].value == "Đăng nhập"
    assert len(app.text_input) == 1
    assert not app.exception


def test_wrong_password_shows_error(app, monkeypatch):
    app.text_input[0].input("sai-roi")
    app.button[0].click().run()
    assert app.error[0].value == "Mật khẩu không đúng."
    assert app.title[0].value == "Đăng nhập"


def test_correct_password_opens_home_and_logout_works(app):
    app.text_input[0].input(PASSWORD)
    app.button[0].click().run()
    assert app.title[0].value == "Bài viết"
    assert app.session_state["authenticated"] is True

    app.switch_page("views/settings.py").run()
    next(b for b in app.button if b.label == "Đăng xuất").click().run()
    assert app.title[0].value == "Đăng nhập"


def test_without_password_hash_login_is_impossible(project_root, monkeypatch):
    monkeypatch.setenv("APP_PASSWORD_HASH", "")
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    assert "Chưa đặt mật khẩu" in at.warning[0].value
    assert len(at.text_input) == 0


def test_invalid_timezone_shows_error(project_root, monkeypatch):
    monkeypatch.setenv("APP_TIMEZONE", "Sao/Hoa")
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    assert "APP_TIMEZONE" in at.error[0].value
