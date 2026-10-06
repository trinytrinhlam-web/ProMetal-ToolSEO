"""Mở lần lượt mọi trang trong menu: không trang nào được lỗi."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from seo_app.auth import hash_password

PASSWORD = "mat-khau-thu-123"
VIEWS = sorted(p.name for p in (Path(__file__).parent.parent / "app" / "views").glob("*.py"))


@pytest.fixture(autouse=True)
def env(monkeypatch):
    monkeypatch.setenv("APP_PASSWORD_HASH", hash_password(PASSWORD, iterations=1_000))
    monkeypatch.setenv("APP_TIMEZONE", "Asia/Ho_Chi_Minh")


def test_every_view_is_in_the_menu(project_root):
    main = (project_root / "app" / "main.py").read_text(encoding="utf-8")
    for view in VIEWS:
        assert f'"views/{view}"' in main


@pytest.mark.parametrize("view", VIEWS)
def test_page_renders_without_error(project_root, view):
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    at.text_input[0].input(PASSWORD)
    at.button[0].click().run()
    at.switch_page(f"views/{view}").run()
    assert not at.exception, at.exception
    assert at.title[0].value


def test_blind_test_reveals_models_only_after_scoring(project_root):
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    at.text_input[0].input(PASSWORD)
    at.button[0].click().run()
    at.switch_page("views/blind_test.py").run()
    assert not at.dataframe

    at.slider[2].set_value(9)
    next(b for b in at.button if b.label.startswith("Chấm xong")).click().run()

    table = at.dataframe[0].value
    assert list(table["Bài"])[0] == "C"
