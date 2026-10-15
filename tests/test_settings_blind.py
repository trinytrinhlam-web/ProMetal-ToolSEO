"""Tab "🤖 Mô hình AI" trong Cài đặt: bảng việc–mô hình và thử mù (phiếu T-019, phần Họa Sĩ).

Không gọi mạng: ``run_blind_test`` được thay bằng hàm giả; khóa API chỉ là chuỗi giả trong biến
môi trường; ``.env`` trỏ sang file tạm.
"""

from __future__ import annotations

import pytest
from streamlit.testing.v1 import AppTest

import seo_app.config as config
from seo_app.ai import AIError
from seo_app.auth import hash_password
from seo_app.content import blind_test
from seo_app.content.blind_test import HIDDEN_ERROR, BlindEntry, BlindReveal

PASSWORD = "mat-khau-thu-123"
KEY_ENVS = ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY")
# Tên mô hình không có trong config/ai.toml, để chắc chữ trên trang không đến từ bảng cấu hình.
MODEL_X = "mo-hinh-bi-mat-x1"
MODEL_Y = "mo-hinh-bi-mat-y2"
MODEL_Z = "mo-hinh-bi-mat-z3"


@pytest.fixture(autouse=True)
def env(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_PASSWORD_HASH", hash_password(PASSWORD, iterations=1_000))
    monkeypatch.setattr(config, "DEFAULT_ENV_FILE", tmp_path / ".env")
    for name in KEY_ENVS:
        monkeypatch.delenv(name, raising=False)


def set_keys(monkeypatch, *names: str) -> None:
    for name in names:
        monkeypatch.setenv(name, f"khoa-gia-{name.lower()}")


class FakeRun:
    """Thay ``run_blind_test``: ghi lại lời gọi, trả kết quả định sẵn."""

    def __init__(self, result=None, exc: Exception | None = None):
        self.calls: list[dict] = []
        self.result = result
        self.exc = exc

    def __call__(self, keyword, note, candidates, settings, rules, **kwargs):
        self.calls.append({"keyword": keyword, "note": note, "candidates": list(candidates)})
        if self.exc:
            raise self.exc
        return self.result


def two_results():
    entries = [
        BlindEntry("A", intro="Mở bài của A.", heading="Mục của A", body="Thân bài A."),
        BlindEntry("B", intro="Mở bài của B.", heading="Mục của B", body="Thân bài B."),
    ]
    reveal = {
        "A": BlindReveal("A", "openai", "OpenAI", MODEL_Y, "medium"),
        "B": BlindReveal("B", "anthropic", "Anthropic (Claude)", MODEL_X, "high"),
    }
    return entries, reveal


@pytest.fixture
def fake_run(monkeypatch):
    fake = FakeRun(result=two_results())
    monkeypatch.setattr(blind_test, "run_blind_test", fake)
    return fake


def open_models_tab(project_root) -> AppTest:
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    at.text_input[0].input(PASSWORD)
    at.button[0].click().run()
    at.switch_page("views/settings.py").run()
    assert not at.exception, at.exception
    return at


def visible_text(at: AppTest) -> str:
    """Chữ trên trang, trừ ô nhập (ô nhập tên mô hình là chữ người dùng tự gõ)."""
    parts: list[str] = []
    for kind in ("markdown", "caption", "success", "error", "warning", "info", "title", "code"):
        parts.extend(str(el.value) for el in getattr(at, kind))
    for widget in (*at.button, *at.slider, *at.selectbox, *at.text_input, *at.text_area):
        parts.extend(str(x) for x in (widget.label, widget.help, widget.key))
    for frame in at.dataframe:
        parts.append(frame.value.to_string())
    return "\n".join(parts)


def fill(at: AppTest, keyword: str = "cửa sắt mỹ thuật", models=(MODEL_X, MODEL_Y)) -> AppTest:
    at.text_input(key="blind-keyword").input(keyword)
    for i, model in enumerate(models):
        at.text_input(key=f"blind-cand-{i}-model").input(model)
    at.run()
    assert not at.exception, at.exception
    return at


def run_button(at: AppTest):
    return at.button(key="blind-run")


# ------------------------------------------------------------ bảng việc–mô hình


def test_model_table_reads_config_ai_toml(project_root):
    at = open_models_tab(project_root)
    table = at.dataframe[0].value
    rows = blind_test.task_models()
    assert list(table["Mô hình"]) == [r.model for r in rows]
    assert list(table["Việc"]) == [r.task_label for r in rows]
    captions = "\n".join(c.value for c in at.caption)
    assert "config/ai.toml" in captions
    assert "ai_models.toml" not in captions


def test_bad_config_shows_vietnamese_error(project_root, monkeypatch):
    def broken():
        raise AIError("File config/ai.toml viết sai.")

    monkeypatch.setattr(blind_test, "task_models", broken)
    at = open_models_tab(project_root)
    assert any("config/ai.toml viết sai" in e.value for e in at.error)


# ------------------------------------------------------------ chọn ứng viên


def test_no_key_locks_blind_test(project_root, fake_run):
    at = open_models_tab(project_root)
    assert any("Chưa có khóa AI nào" in i.value for i in at.info)
    assert not [b for b in at.button if b.key == "blind-run"]
    assert not fake_run.calls


def test_only_providers_with_key_can_be_chosen(project_root, monkeypatch):
    set_keys(monkeypatch, "ANTHROPIC_API_KEY", "GEMINI_API_KEY")
    at = open_models_tab(project_root)
    for i in range(2):
        assert at.selectbox(key=f"blind-cand-{i}-provider").options == [
            "Anthropic (Claude)",
            "Google Gemini",
        ]
    # Mặc định hai ứng viên khác hãng.
    assert at.selectbox(key="blind-cand-0-provider").value == "anthropic"
    assert at.selectbox(key="blind-cand-1-provider").value == "gemini"
    # Không hiện khóa, chỉ đã có / chưa có.
    assert "khoa-gia" not in visible_text(at)
    assert "OpenAI: chưa có khóa" in visible_text(at)


def test_model_name_suggested_from_config_and_follows_provider(project_root, monkeypatch):
    set_keys(monkeypatch, "ANTHROPIC_API_KEY", "OPENAI_API_KEY")
    at = open_models_tab(project_root)
    configured = blind_test.model_suggestions(blind_test.task_models())["anthropic"][0]
    assert at.text_input(key="blind-cand-0-model").value == configured
    at.selectbox(key="blind-cand-0-provider").set_value("openai").run()
    suggested = (blind_test.model_suggestions(blind_test.task_models())["openai"] or [""])[0]
    assert at.text_input(key="blind-cand-0-model").value == suggested


def test_three_candidates(project_root, monkeypatch, fake_run):
    set_keys(monkeypatch, *KEY_ENVS)
    at = open_models_tab(project_root)
    at.segmented_control(key="blind-count").set_value(3).run()
    assert [at.selectbox(key=f"blind-cand-{i}-provider").value for i in range(3)] == [
        "anthropic",
        "openai",
        "gemini",
    ]
    fill(at, models=(MODEL_X, MODEL_Y, MODEL_Z))
    assert any("gọi AI 3 lần" in w.value for w in at.warning)
    run_button(at).click().run()
    assert [c.model for c in fake_run.calls[0]["candidates"]] == [MODEL_X, MODEL_Y, MODEL_Z]


def test_single_vendor_can_compare_its_own_models(project_root, monkeypatch, fake_run):
    set_keys(monkeypatch, "OPENAI_API_KEY")
    at = open_models_tab(project_root)
    fill(at)
    run_button(at).click().run()
    cands = fake_run.calls[0]["candidates"]
    assert [c.provider for c in cands] == ["openai", "openai"]


# ------------------------------------------------------------ cảnh báo tốn tiền, nút chạy


def test_run_disabled_until_inputs_valid_and_cost_warning_shown(project_root, monkeypatch):
    set_keys(monkeypatch, "ANTHROPIC_API_KEY", "OPENAI_API_KEY")
    at = open_models_tab(project_root)
    assert run_button(at).disabled  # chưa có từ khóa
    assert any("Nhập từ khóa" in c.value for c in at.caption)
    assert any("gọi AI 2 lần" in w.value and "tốn tiền" in w.value for w in at.warning)

    fill(at, models=(MODEL_X, "co dau cach"))
    assert run_button(at).disabled
    fill(at)
    assert not run_button(at).disabled


def test_run_passes_inputs(project_root, monkeypatch, fake_run):
    set_keys(monkeypatch, "ANTHROPIC_API_KEY", "OPENAI_API_KEY")
    at = open_models_tab(project_root)
    at.text_area(key="blind-note").input("nhấn vào độ bền")
    at.selectbox(key="blind-cand-1-effort").set_value("high")
    fill(at)
    run_button(at).click().run()
    assert not at.exception, at.exception
    call = fake_run.calls[0]
    assert call["keyword"] == "cửa sắt mỹ thuật"
    assert call["note"] == "nhấn vào độ bền"
    assert call["candidates"] == [
        blind_test.Candidate("anthropic", MODEL_X, "medium"),
        blind_test.Candidate("openai", MODEL_Y, "high"),
    ]


def test_run_error_shown(project_root, monkeypatch):
    fake = FakeRun(exc=AIError("Từ khóa dài quá 200 ký tự."))
    monkeypatch.setattr(blind_test, "run_blind_test", fake)
    set_keys(monkeypatch, "ANTHROPIC_API_KEY")
    at = open_models_tab(project_root)
    fill(at)
    run_button(at).click().run()
    assert any("dài quá" in e.value for e in at.error)
    assert "blind_entries" not in at.session_state


# ------------------------------------------------------------ chấm điểm, hiện tên


def test_names_hidden_until_scored_then_revealed(project_root, monkeypatch, fake_run):
    set_keys(monkeypatch, "ANTHROPIC_API_KEY", "OPENAI_API_KEY")
    at = open_models_tab(project_root)
    fill(at)
    run_button(at).click().run()
    assert not at.exception, at.exception

    # Trước khi chấm: có bài A/B, không có bảng hiện tên, không chữ nào nối nhãn với mô hình.
    markdown = [m.value for m in at.markdown]
    assert "**Bài A**" in markdown and "Mở bài của A." in markdown
    assert len(at.dataframe) == 1  # chỉ bảng việc–mô hình
    page = visible_text(at)
    assert MODEL_X not in page and MODEL_Y not in page
    assert not any(c.value.startswith("```toml") for c in at.code)

    at.slider(key="blind-score-B").set_value(9)
    at.slider(key="blind-score-A").set_value(4)
    at.button(key="blind-reveal").click().run()
    assert not at.exception, at.exception

    revealed = at.dataframe[-1].value
    assert list(revealed["Bài"]) == ["B", "A"]
    assert list(revealed["Mô hình"]) == [MODEL_X, MODEL_Y]
    assert list(revealed["Điểm"]) == [9, 4]
    # Hướng dẫn đổi config/ai.toml theo bài điểm cao nhất.
    code = at.code[-1].value
    assert 'provider = "anthropic"' in code and f'model = "{MODEL_X}"' in code
    assert any("config/ai.toml" in m.value for m in at.markdown)
    # Điểm đã chốt: thanh điểm thành chữ, không chấm lại được.
    assert not [s for s in at.slider if s.key and s.key.startswith("blind-score")]
    assert "Điểm: **9**/10" in [m.value for m in at.markdown]
    assert at.button(key="blind-reveal").disabled


def test_ai_text_is_plain_markdown_not_html(project_root, monkeypatch):
    entries = [
        BlindEntry("A", intro="<b>đậm</b> & chữ", heading="Mục", body="Thân."),
        BlindEntry("B", intro="Mở bài B.", heading="Mục B", body="Thân B."),
    ]
    reveal = {
        "A": BlindReveal("A", "openai", "OpenAI", MODEL_Y, "medium"),
        "B": BlindReveal("B", "anthropic", "Anthropic (Claude)", MODEL_X, "medium"),
    }
    monkeypatch.setattr(blind_test, "run_blind_test", FakeRun(result=(entries, reveal)))
    set_keys(monkeypatch, "ANTHROPIC_API_KEY")
    at = open_models_tab(project_root)
    fill(at)
    run_button(at).click().run()
    shown = [m for m in at.markdown if "đậm" in m.value]
    assert shown
    assert all(not m.proto.allow_html for m in shown)


def test_failed_candidate_shows_fixed_message_then_real_error(project_root, monkeypatch):
    entries = [
        BlindEntry("A", intro="Mở bài A.", heading="Mục A", body="Thân A."),
        BlindEntry("B", error=HIDDEN_ERROR),
    ]
    real_error = f"Mô hình «{MODEL_Y}» không tồn tại."
    reveal = {
        "A": BlindReveal("A", "anthropic", "Anthropic (Claude)", MODEL_X, "medium"),
        "B": BlindReveal("B", "openai", "OpenAI", MODEL_Y, "medium", error=real_error),
    }
    monkeypatch.setattr(blind_test, "run_blind_test", FakeRun(result=(entries, reveal)))
    set_keys(monkeypatch, "ANTHROPIC_API_KEY", "OPENAI_API_KEY")
    at = open_models_tab(project_root)
    fill(at)
    run_button(at).click().run()

    assert any(w.value == HIDDEN_ERROR for w in at.warning)
    assert [s.key for s in at.slider if s.key.startswith("blind-score")] == ["blind-score-A"]
    assert real_error not in visible_text(at)

    at.button(key="blind-reveal").click().run()
    assert any(real_error in e.value for e in at.error)
    revealed = at.dataframe[-1].value
    assert list(revealed["Bài"]) == ["A", "B"]
    assert list(revealed["Điểm"])[0] == 5
    assert list(revealed["Tình trạng"]) == ["có bài", "lỗi (xem dưới)"]


def test_new_run_hides_names_again_and_clear_button(project_root, monkeypatch, fake_run):
    set_keys(monkeypatch, "ANTHROPIC_API_KEY", "OPENAI_API_KEY")
    at = open_models_tab(project_root)
    fill(at)
    run_button(at).click().run()
    at.button(key="blind-reveal").click().run()
    assert MODEL_X in visible_text(at)

    run_button(at).click().run()
    assert at.session_state["blind_revealed"] is False
    assert len(at.dataframe) == 1
    assert at.slider(key="blind-score-A").value == 5

    at.button(key="blind-clear").click().run()
    assert "blind_entries" not in at.session_state
    assert not [s for s in at.slider if s.key and s.key.startswith("blind-score")]
