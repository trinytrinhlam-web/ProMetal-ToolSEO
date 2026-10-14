"""Mở lần lượt mọi trang trong menu, và bấm thử các nút chính của bản demo."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from seo_app import demo
from seo_app.auth import hash_password

PASSWORD = "mat-khau-thu-123"
VIEWS = sorted(p.name for p in (Path(__file__).parent.parent / "app" / "views").glob("*.py"))


@pytest.fixture(autouse=True)
def env(monkeypatch):
    monkeypatch.setenv("APP_PASSWORD_HASH", hash_password(PASSWORD, iterations=1_000))
    monkeypatch.setenv("APP_TIMEZONE", "Asia/Ho_Chi_Minh")


def open_page(project_root, view: str) -> AppTest:
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    at.text_input[0].input(PASSWORD)
    at.button[0].click().run()
    at.switch_page(f"views/{view}").run()
    assert not at.exception, at.exception
    return at


def button(at: AppTest, label: str, key: str | None = None):
    for b in at.button:
        if b.label == label and (key is None or b.key == key):
            return b
    raise AssertionError(f"Không thấy nút {label!r}")


def test_every_view_is_in_the_menu(project_root):
    main = (project_root / "app" / "main.py").read_text(encoding="utf-8")
    for view in VIEWS:
        assert f'"views/{view}"' in main


@pytest.mark.parametrize("view", VIEWS)
def test_page_renders_without_error(project_root, view):
    at = open_page(project_root, view)
    assert at.title[0].value


@pytest.mark.parametrize("step", range(len(demo.STEPS)))
def test_every_writing_step_renders(project_root, step):
    at = open_page(project_root, "write.py")
    at.session_state["step"] = step
    at.run()
    assert not at.exception, at.exception


def test_rewrite_section_switches_version_and_undo(project_root):
    at = open_page(project_root, "write.py")
    first, second = demo.SECTIONS[0]["versions"]
    assert any(first[:40] in m.value for m in at.markdown)

    button(at, "Viết lại phần này", key="do-rw-mo-bai").click().run()
    assert any(second[:40] in m.value for m in at.markdown)
    assert at.session_state["ver-mo-bai"] == 1

    button(at, "↶", key="undo-mo-bai").click().run()
    assert at.session_state["ver-mo-bai"] == 0


def test_applying_tone_fix_removes_sentence_and_raises_score(project_root):
    at = open_page(project_root, "write.py")
    sid, sentence, _reason, replacement = demo.TONE_FLAGS[0]
    before = demo.NATURAL_MAX - demo.NATURAL_PENALTY * len(demo.TONE_FLAGS)
    assert any(f"<b>{before}</b>" in m.value for m in at.markdown)

    button(at, "Áp dụng", key=f"fix-{sentence[:20]}").click().run()

    text = at.session_state[f"texts-{sid}"][0]
    assert sentence not in text
    assert replacement in text
    after = before + demo.NATURAL_PENALTY
    assert any(f"<b>{after}</b>" in m.value for m in at.markdown)


def test_plan_reading_shows_proposed_changes(project_root):
    at = open_page(project_root, "plan.py")
    assert "plan_changes" not in at.session_state
    button(at, "🧠 Đọc kế hoạch và đề xuất cập nhật").click().run()
    assert not at.exception
    assert len(at.session_state["plan_changes"]) == len(demo.PLAN_CHANGES)


def test_blind_test_reveals_models_only_after_scoring(project_root):
    at = open_page(project_root, "settings.py")
    assert not at.session_state["blind_revealed"] if "blind_revealed" in at.session_state else True
    at.slider(key="score-C").set_value(9)
    button(at, "Chấm xong — hiện tên mô hình").click().run()
    revealed = at.dataframe[-1].value
    assert list(revealed["Bài"])[0] == "C"
