"""Tab "🔌 Kết nối" trong Cài đặt: nhập khóa API AI (phiếu T-020, phần Họa Sĩ).

Mọi test ghi vào ``.env`` trong ``tmp_path`` riêng, không đọc/ghi ``.env`` thật, không gọi mạng
(``check_api_key`` được giả).
"""

from __future__ import annotations

import pytest
from streamlit.proto.TextInput_pb2 import TextInput as TextInputProto
from streamlit.testing.v1 import AppTest

import seo_app.config as config
from seo_app import env_file
from seo_app.auth import hash_password

PASSWORD = "mat-khau-thu-123"
CLAUDE_KEY = "sk-ant-api03-ThuNghiemKhongPhaiKhoaThat_abcXYZ-9876wxyz"
OPENAI_KEY = "sk-proj-KhoaGiaOpenAI1234567890_qrst"


@pytest.fixture(autouse=True)
def env_path(monkeypatch, tmp_path):
    """Trỏ ``.env`` sang file tạm riêng của từng test (không bao giờ đụng .env thật)."""
    monkeypatch.setenv("APP_PASSWORD_HASH", hash_password(PASSWORD, iterations=1_000))
    path = tmp_path / ".env"
    monkeypatch.setattr(config, "DEFAULT_ENV_FILE", path)
    return path


def open_settings(project_root) -> AppTest:
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    at.text_input[0].input(PASSWORD)
    at.button[0].click().run()
    at.switch_page("views/settings.py").run()
    assert not at.exception, at.exception
    return at


def input_key(name: str) -> str:
    return f"api-key-input-{name}"


def visible_text(at: AppTest) -> str:
    """Mọi chữ đang hiện trên trang (thông báo, markdown, chú thích, giá trị ô nhập)."""
    parts: list[str] = []
    for kind in ("markdown", "caption", "success", "error", "warning", "info", "title"):
        parts.extend(str(el.value) for el in getattr(at, kind))
    parts.extend(str(el.value) for el in at.text_input)
    parts.extend(str(el.placeholder) for el in at.text_input)
    return "\n".join(parts)


def session_dump(at: AppTest) -> str:
    return "\n".join(f"{k}={v!r}" for k, v in at.session_state.to_dict().items())


def assert_key_nowhere(at: AppTest, key: str) -> None:
    # Không hiện lại khóa, kể cả vài ký tự cuối, cả trên trang lẫn trong session_state.
    for piece in (key, key[-4:], key[-6:]):
        assert piece not in visible_text(at)
        assert piece not in session_dump(at)


def card_status(at: AppTest, label: str) -> str:
    texts = [m.value for m in at.markdown]
    i = texts.index(f"**{label}**")
    return texts[i + 1]


def save(at: AppTest, name: str, value: str) -> AppTest:
    at.text_input(key=input_key(name)).input(value)
    at.button(key=f"api-key-save-{name}").click().run()
    assert not at.exception, at.exception
    return at


def test_initial_state_shows_three_cards_not_configured(project_root):
    at = open_settings(project_root)
    for name in env_file.ALLOWED_KEYS:
        widget = at.text_input(key=input_key(name))
        assert widget.value == ""
        assert widget.proto.type == TextInputProto.PASSWORD
        assert at.button(key=f"api-key-clear-{name}").disabled
    assert "Chưa khai báo" in card_status(at, "Claude (Anthropic)")
    text = visible_text(at)
    for url in (
        "https://console.anthropic.com",
        "https://platform.openai.com/api-keys",
        "https://aistudio.google.com/apikey",
    ):
        assert url in text


def test_save_writes_env_clears_input_and_never_shows_key(project_root, env_path):
    at = open_settings(project_root)
    save(at, "ANTHROPIC_API_KEY", f"  {CLAUDE_KEY}  ")

    assert f"ANTHROPIC_API_KEY={CLAUDE_KEY}" in env_path.read_text(encoding="utf-8")
    assert at.text_input(key=input_key("ANTHROPIC_API_KEY")).value == ""
    assert at.session_state[input_key("ANTHROPIC_API_KEY")] == ""
    assert any("Đã lưu khóa Claude" in s.value for s in at.success)
    assert "Đã khai báo" in card_status(at, "Claude (Anthropic)")
    assert not at.button(key="api-key-clear-ANTHROPIC_API_KEY").disabled
    assert_key_nowhere(at, CLAUDE_KEY)

    # Chạy lại trang (như khi bấm chỗ khác): khóa vẫn không xuất hiện, thông báo đã tắt.
    at.run()
    assert not at.success
    assert_key_nowhere(at, CLAUDE_KEY)


def test_invalid_value_rejected_and_cleared(project_root, env_path):
    at = open_settings(project_root)
    bad = "sk-abc\nAPP_PASSWORD_HASH=pbkdf2$hack"
    save(at, "OPENAI_API_KEY", bad)

    assert not env_path.exists()
    assert at.error, "phải báo lỗi"
    assert at.session_state[input_key("OPENAI_API_KEY")] == ""
    assert "Chưa khai báo" in card_status(at, "ChatGPT (OpenAI)")
    for piece in ("sk-abc", "hack", "pbkdf2"):
        assert piece not in visible_text(at)
        assert piece not in session_dump(at)


def test_empty_save_shows_friendly_error(project_root, env_path):
    at = open_settings(project_root)
    at.button(key="api-key-save-GEMINI_API_KEY").click().run()
    assert any("Chưa nhập khóa" in e.value for e in at.error)
    assert not env_path.exists()


def test_save_keeps_other_lines(project_root, env_path):
    env_path.write_text("# ghi chú\nAPP_TIMEZONE=Asia/Ho_Chi_Minh\nOPENAI_API_KEY=\n", "utf-8")
    at = open_settings(project_root)
    save(at, "OPENAI_API_KEY", OPENAI_KEY)
    assert env_path.read_text(encoding="utf-8") == (
        f"# ghi chú\nAPP_TIMEZONE=Asia/Ho_Chi_Minh\nOPENAI_API_KEY={OPENAI_KEY}\n"
    )
    assert_key_nowhere(at, OPENAI_KEY)


def test_clear_asks_once_then_clears(project_root, env_path):
    env_path.write_text(f"ANTHROPIC_API_KEY={CLAUDE_KEY}\n", encoding="utf-8")
    at = open_settings(project_root)
    assert "Đã khai báo" in card_status(at, "Claude (Anthropic)")
    assert_key_nowhere(at, CLAUDE_KEY)

    at.button(key="api-key-clear-ANTHROPIC_API_KEY").click().run()
    assert any("Xóa khóa Claude" in w.value for w in at.warning)
    # Chưa xóa cho tới khi bấm "Xóa thật".
    assert CLAUDE_KEY in env_path.read_text(encoding="utf-8")

    at.button(key="api-key-clear-no-ANTHROPIC_API_KEY").click().run()
    assert CLAUDE_KEY in env_path.read_text(encoding="utf-8")
    assert not any("Xóa khóa Claude" in w.value for w in at.warning)

    at.button(key="api-key-clear-ANTHROPIC_API_KEY").click().run()
    at.button(key="api-key-clear-yes-ANTHROPIC_API_KEY").click().run()
    assert not at.exception, at.exception
    assert env_path.read_text(encoding="utf-8") == "ANTHROPIC_API_KEY=\n"
    assert "Chưa khai báo" in card_status(at, "Claude (Anthropic)")
    assert any("Đã xóa khóa Claude" in s.value for s in at.success)


def test_os_environ_override_warning(project_root, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaKhoaTrongMoiTruong123456")
    at = open_settings(project_root)
    warnings = [w.value for w in at.warning]
    assert any("Gemini" in w and "không có hiệu lực" in w for w in warnings)
    assert not any("Claude" in w and "biến môi trường" in w for w in warnings)
    assert_key_nowhere(at, "AIzaKhoaTrongMoiTruong123456")


def test_check_only_for_claude(project_root):
    at = open_settings(project_root)
    # Chưa có khóa: không kiểm tra được.
    assert at.button(key="api-key-check-btn-ANTHROPIC_API_KEY").disabled
    assert at.button(key="api-key-check-btn-OPENAI_API_KEY").disabled
    assert at.button(key="api-key-check-btn-GEMINI_API_KEY").disabled


@pytest.mark.parametrize(
    ("status", "kind"),
    [("ok", "success"), ("invalid", "error"), ("unknown", "warning")],
)
def test_check_shows_result(project_root, env_path, monkeypatch, status, kind):
    env_path.write_text(f"ANTHROPIC_API_KEY={CLAUDE_KEY}\n", encoding="utf-8")
    calls = []

    def fake_check(name, **kwargs):
        calls.append((name, kwargs))
        return env_file.KeyCheckResult(status, f"Kết quả giả: {status}.")

    monkeypatch.setattr(env_file, "check_api_key", fake_check)
    at = open_settings(project_root)
    at.button(key="api-key-check-btn-ANTHROPIC_API_KEY").click().run()
    assert not at.exception, at.exception

    # Giao diện không truyền khóa vào hàm kiểm tra (hàm tự đọc .env).
    assert calls == [("ANTHROPIC_API_KEY", {})]
    assert any(f"Kết quả giả: {status}." in el.value for el in getattr(at, kind))
    assert_key_nowhere(at, CLAUDE_KEY)


def test_saving_new_key_resets_old_check_result(project_root, env_path, monkeypatch):
    env_path.write_text(f"ANTHROPIC_API_KEY={CLAUDE_KEY}\n", encoding="utf-8")
    monkeypatch.setattr(
        env_file,
        "check_api_key",
        lambda name, **kw: env_file.KeyCheckResult("ok", "Khóa Claude dùng được."),
    )
    at = open_settings(project_root)
    at.button(key="api-key-check-btn-ANTHROPIC_API_KEY").click().run()
    assert any("dùng được" in s.value for s in at.success)

    new_key = "sk-ant-api03-KhoaMoiThayKhoaCu_000111222"
    save(at, "ANTHROPIC_API_KEY", new_key)
    assert not any("dùng được" in s.value for s in at.success)
    assert new_key in env_path.read_text(encoding="utf-8")
    assert_key_nowhere(at, new_key)
    assert_key_nowhere(at, CLAUDE_KEY)
