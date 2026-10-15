"""Mở lần lượt mọi trang trong menu, và bấm thử các nút chính (AI giả, không gọi mạng)."""

from pathlib import Path

import pytest
from fake_ai import DRAFT, OUTLINE, RESEARCH, STIFF, VAGUE_FIX, FakeProvider
from streamlit.testing.v1 import AppTest

from seo_app import demo
from seo_app.ai import registry as ai_registry
from seo_app.auth import hash_password

PASSWORD = "mat-khau-thu-123"
VIEWS = sorted(p.name for p in (Path(__file__).parent.parent / "app" / "views").glob("*.py"))


@pytest.fixture(autouse=True)
def env(monkeypatch):
    monkeypatch.setenv("APP_PASSWORD_HASH", hash_password(PASSWORD, iterations=1_000))
    monkeypatch.setenv("APP_TIMEZONE", "Asia/Ho_Chi_Minh")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


@pytest.fixture
def fake_ai(monkeypatch):
    provider = FakeProvider()
    monkeypatch.setattr(ai_registry, "make_provider", lambda name, settings: provider)
    return provider


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


def test_plan_reading_shows_proposed_changes(project_root):
    at = open_page(project_root, "plan.py")
    assert "plan_changes" not in at.session_state
    button(at, "🧠 Đọc kế hoạch và đề xuất cập nhật").click().run()
    assert not at.exception
    assert len(at.session_state["plan_changes"]) == len(demo.PLAN_CHANGES)


def test_blind_test_locked_without_api_key(project_root):
    # Chi tiết thử mù (T-019): tests/test_settings_blind.py.
    at = open_page(project_root, "settings.py")
    assert any("Chưa có khóa AI nào" in i.value for i in at.info)


# ------------------------------------------------------------ Soạn bài với AI


def write_page(project_root) -> AppTest:
    return open_page(project_root, "write.py")


def test_without_api_key_ai_buttons_are_locked(project_root):
    at = write_page(project_root)
    assert any("ANTHROPIC_API_KEY" in w.value for w in at.warning)
    at.text_input(key="keyword").input("so sánh inox 201 và 304").run()
    assert button(at, "🔎 Phân tích từ khóa").disabled


def go_to_article(at: AppTest) -> AppTest:
    at.text_input(key="keyword").input("so sánh inox 201 và 304").run()
    button(at, "🔎 Phân tích từ khóa").click().run()
    assert not at.exception, at.exception
    button(at, "Tiếp: tạo dàn ý →").click().run()
    assert at.session_state["step"] == 1
    button(at, "✅ Duyệt dàn ý, viết toàn bài →").click().run()
    assert not at.exception, at.exception
    assert at.session_state["step"] == 2
    return at


def test_full_flow_research_outline_write(project_root, fake_ai):
    at = write_page(project_root)
    at.text_input(key="keyword").input("so sánh inox 201 và 304").run()
    button(at, "🔎 Phân tích từ khóa").click().run()
    assert any(RESEARCH.competitors[0].missing in m.value for m in at.markdown)

    at.text_area(key="real-Kinh nghiệm của xưởng").input("Cổng 201 gần biển hay gỉ").run()
    button(at, "Tiếp: tạo dàn ý →").click().run()
    headings = [at.session_state[f"h-{uid}"] for uid in at.session_state["outline_ids"]]
    assert headings == [item.heading for item in OUTLINE.items]

    # Người dùng xóa mục cuối và sửa tiêu đề mục đầu trước khi duyệt.
    first, *_, last = at.session_state["outline_ids"]
    button(at, "🗑️", key=f"rm-{last}").click().run()
    at.text_input(key=f"h-{first}").input("Inox 201 và 304 khác nhau ở đâu?").run()
    button(at, "✅ Duyệt dàn ý, viết toàn bài →").click().run()
    assert not at.exception, at.exception

    assert fake_ai.tasks() == ["research", "outline", "write", "review", "review"]
    _, _, outline_prompt = fake_ai.calls[1]
    assert "Cổng 201 gần biển hay gỉ" in outline_prompt
    _, _, write_prompt = fake_ai.calls[2]
    assert "Inox 201 và 304 khác nhau ở đâu?" in write_prompt
    assert OUTLINE.items[-1].heading not in write_prompt

    assert at.session_state["step"] == 2
    assert at.session_state["auto_fixed"] == 1
    assert any(VAGUE_FIX in m.value for m in at.markdown)
    assert any(f'<mark class="tone">{STIFF}</mark>' in m.value for m in at.markdown)
    assert any('<mark class="missing">' in m.value for m in at.markdown)


def test_rewrite_section_adds_version_and_undo(project_root, fake_ai):
    at = go_to_article(write_page(project_root))
    pid = at.session_state["part_ids"][1]
    button(at, "Viết lại phần này", key=f"do-rw-{pid}").click().run()
    assert not at.exception, at.exception
    assert at.session_state[f"ver-{pid}"] == 1
    assert any("Bản viết lại số 1." in m.value for m in at.markdown)

    button(at, "↶", key=f"undo-{pid}").click().run()
    assert at.session_state[f"ver-{pid}"] == 0
    assert at.session_state[f"texts-{pid}"][0] == DRAFT.sections[0].body


def test_applying_fix_removes_the_flag(project_root, fake_ai):
    at = go_to_article(write_page(project_root))
    pid = at.session_state["part_ids"][1]
    fix = next(b for b in at.button if b.label == "Áp dụng")
    fix.click().run()
    assert STIFF not in at.session_state[f"texts-{pid}"][0]
    assert not any(b.label == "Áp dụng" for b in at.button)


def test_recheck_replaces_review(project_root, fake_ai):
    at = go_to_article(write_page(project_root))
    button(at, "Kiểm tra lại toàn bài").click().run()
    assert fake_ai.tasks()[-1] == "review"
    assert not at.exception, at.exception
