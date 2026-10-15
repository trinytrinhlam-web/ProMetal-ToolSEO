"""Soi Lỗi · T-023: nút Kiểm tra khóa ChatGPT và Gemini trong Cài đặt → 🔌 Kết nối.

Chỉ kiểm phần giao diện. Mọi test ghi ``.env`` vào ``tmp_path`` riêng, không gọi mạng:
``check_api_key`` được giả, hoặc (test đầu-cuối) lớp client của thư viện hãng được giả.
"""

from __future__ import annotations

import pytest
from streamlit.testing.v1 import AppTest

import seo_app.config as config
from seo_app import env_file
from seo_app.auth import hash_password

PASSWORD = "mat-khau-thu-123"
KEYS = {
    "ANTHROPIC_API_KEY": "sk-ant-api03-SoiLoiT023KhoaGiaClaude_aaaa-QzKwJx",
    "OPENAI_API_KEY": "sk-proj-SoiLoiT023KhoaGiaOpenAI_bbbbXjVpRq",
    "GEMINI_API_KEY": "AIzaSySoiLoiT023KhoaGiaGemini_ccccWmHfTb",
}
LABELS = {
    "ANTHROPIC_API_KEY": "Claude (Anthropic)",
    "OPENAI_API_KEY": "ChatGPT (OpenAI)",
    "GEMINI_API_KEY": "Gemini (Google)",
}
ALERTS = ("success", "error", "warning", "info", "exception")


@pytest.fixture(autouse=True)
def env_path(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_PASSWORD_HASH", hash_password(PASSWORD, iterations=1_000))
    for name in KEYS:
        monkeypatch.delenv(name, raising=False)
    path = tmp_path / ".env"
    monkeypatch.setattr(config, "DEFAULT_ENV_FILE", path)
    return path


def write_env(path, names) -> None:
    path.write_text("".join(f"{n}={KEYS[n]}\n" for n in names), encoding="utf-8")


def open_settings(project_root) -> AppTest:
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    at.text_input[0].input(PASSWORD)
    at.button[0].click().run()
    at.switch_page("views/settings.py").run()
    assert not at.exception, at.exception
    return at


def everything(at: AppTest) -> str:
    """Mọi chữ có trong cây phần tử của trang (cả nhãn, chú thích, help, lỗi) và session_state."""
    parts = [str(node.proto) for node in _walk(at._tree)]
    parts.extend(f"{k}={v!r}" for k, v in at.session_state.to_dict().items())
    return "\n".join(parts)


def _walk(node):
    proto = getattr(node, "proto", None)
    if proto is not None:
        yield node
    for child in getattr(node, "children", {}).values():
        yield from _walk(child)


def assert_no_key(at: AppTest) -> None:
    dump = everything(at)
    for key in KEYS.values():
        for piece in (key, key[-4:], key[-8:], key[:-4]):
            assert piece not in dump


def card(at: AppTest, name: str):
    """Cột chứa thẻ khóa ``name`` (cột lớn có cả 3 nút Lưu / Kiểm tra / Xóa của khóa đó)."""
    for col in at.tabs[3].columns:
        keys = {b.key for b in col.button}
        if {f"api-key-save-{name}", f"api-key-check-btn-{name}", f"api-key-clear-{name}"} <= keys:
            return col
    raise AssertionError(f"không thấy thẻ {name}")


def alerts(node) -> list[tuple[str, str]]:
    return [(kind, str(el.value)) for kind in ALERTS for el in getattr(node, kind)]


def fake_checker(monkeypatch, results=None):
    calls: list[tuple[str, dict]] = []

    def fake(name, **kwargs):
        calls.append((name, kwargs))
        status, message = (results or {}).get(name, ("ok", f"Giả {name} ok."))
        return env_file.KeyCheckResult(status, message)

    monkeypatch.setattr(env_file, "check_api_key", fake)
    return calls


# ---------- 1. Nút bật/tắt theo từng khóa ----------


@pytest.mark.parametrize("only", list(KEYS))
def test_button_enabled_only_for_configured_key(project_root, env_path, only):
    write_env(env_path, [only])
    at = open_settings(project_root)
    for name in KEYS:
        assert at.button(key=f"api-key-check-btn-{name}").disabled is (name != only), name
    assert_no_key(at)


def test_help_text_matches_state(project_root, env_path):
    write_env(env_path, ["GEMINI_API_KEY"])
    at = open_settings(project_root)
    assert "Lưu khóa trước" in at.button(key="api-key-check-btn-OPENAI_API_KEY").help
    assert "Gemini" in at.button(key="api-key-check-btn-GEMINI_API_KEY").help
    assert "chờ cài thư viện" not in everything(at)


def test_os_environ_key_also_enables_check(project_root, env_path, monkeypatch):
    # Khóa đặt trong biến môi trường máy (không có trong .env) vẫn là "đã khai báo".
    monkeypatch.setenv("OPENAI_API_KEY", KEYS["OPENAI_API_KEY"])
    calls = fake_checker(monkeypatch)
    at = open_settings(project_root)
    btn = at.button(key="api-key-check-btn-OPENAI_API_KEY")
    assert not btn.disabled
    btn.click().run()
    assert calls == [("OPENAI_API_KEY", {})]
    assert_no_key(at)


def test_clear_key_disables_check_and_drops_result(project_root, env_path, monkeypatch):
    write_env(env_path, ["GEMINI_API_KEY"])
    fake_checker(monkeypatch)
    at = open_settings(project_root)
    at.button(key="api-key-check-btn-GEMINI_API_KEY").click().run()
    assert ("success", "Giả GEMINI_API_KEY ok.") in alerts(card(at, "GEMINI_API_KEY"))
    at.button(key="api-key-clear-GEMINI_API_KEY").click().run()
    at.button(key="api-key-clear-yes-GEMINI_API_KEY").click().run()
    assert at.button(key="api-key-check-btn-GEMINI_API_KEY").disabled
    assert "Giả GEMINI_API_KEY" not in everything(at)


# ---------- 2. Gọi đúng tên biến, đúng màu ----------


@pytest.mark.parametrize("name", list(KEYS))
@pytest.mark.parametrize(
    ("status", "kind"),
    [
        ("ok", "success"),
        ("invalid", "error"),
        ("unknown", "warning"),
        ("missing", "warning"),
        ("unsupported", "warning"),
        ("trang-thai-la", "warning"),
    ],
)
def test_click_calls_right_name_and_color(project_root, env_path, monkeypatch, name, status, kind):
    write_env(env_path, KEYS)
    message = f"Kết quả {status} của {name}."
    calls = fake_checker(monkeypatch, {name: (status, message)})
    at = open_settings(project_root)
    at.button(key=f"api-key-check-btn-{name}").click().run()
    assert not at.exception, at.exception
    assert calls == [(name, {})]
    assert alerts(card(at, name)) == [(kind, message)]
    assert_no_key(at)


# ---------- 3. Kết quả không lạc sang thẻ khác ----------


def test_results_stay_in_their_own_card(project_root, env_path, monkeypatch):
    write_env(env_path, KEYS)
    results = {
        "ANTHROPIC_API_KEY": ("ok", "Claude xanh."),
        "OPENAI_API_KEY": ("invalid", "ChatGPT đỏ."),
        "GEMINI_API_KEY": ("unknown", "Gemini vàng."),
    }
    calls = fake_checker(monkeypatch, results)
    at = open_settings(project_root)
    for name in ("OPENAI_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY"):
        at.button(key=f"api-key-check-btn-{name}").click().run()
    assert [c[0] for c in calls] == ["OPENAI_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY"]
    assert alerts(card(at, "ANTHROPIC_API_KEY")) == [("success", "Claude xanh.")]
    assert alerts(card(at, "OPENAI_API_KEY")) == [("error", "ChatGPT đỏ.")]
    assert alerts(card(at, "GEMINI_API_KEY")) == [("warning", "Gemini vàng.")]
    # Chạy lại trang (bấm chỗ khác): kết quả vẫn ở đúng thẻ, không gọi lại máy chủ.
    at.run()
    assert len(calls) == 3
    assert alerts(card(at, "GEMINI_API_KEY")) == [("warning", "Gemini vàng.")]
    assert_no_key(at)


def test_check_one_card_does_not_call_others(project_root, env_path, monkeypatch):
    write_env(env_path, KEYS)
    calls = fake_checker(monkeypatch)
    at = open_settings(project_root)
    at.button(key="api-key-check-btn-GEMINI_API_KEY").click().run()
    assert calls == [("GEMINI_API_KEY", {})]
    assert alerts(card(at, "ANTHROPIC_API_KEY")) == []
    assert alerts(card(at, "OPENAI_API_KEY")) == []


# ---------- 4. Lưu khóa mới xóa kết quả cũ (chỉ của thẻ đó) ----------


@pytest.mark.parametrize("name", ["OPENAI_API_KEY", "GEMINI_API_KEY"])
def test_saving_new_key_drops_only_that_cards_result(project_root, env_path, monkeypatch, name):
    write_env(env_path, KEYS)
    results = {n: ("invalid", f"Sai {n}.") for n in KEYS}
    fake_checker(monkeypatch, results)
    at = open_settings(project_root)
    for n in KEYS:
        at.button(key=f"api-key-check-btn-{n}").click().run()
    at.text_input(key=f"api-key-input-{name}").input(KEYS[name] + "moi")
    at.button(key=f"api-key-save-{name}").click().run()
    assert not at.exception, at.exception
    mine = alerts(card(at, name))
    assert ("error", f"Sai {name}.") not in mine
    assert any(k == "success" and "Đã lưu khóa" in v for k, v in mine)
    for other in KEYS:
        if other != name:
            assert alerts(card(at, other)) == [("error", f"Sai {other}.")]
    assert KEYS[name] + "moi" not in everything(at)
    assert_no_key(at)


def test_failed_save_still_drops_old_result(project_root, env_path, monkeypatch):
    write_env(env_path, KEYS)
    fake_checker(monkeypatch, {"OPENAI_API_KEY": ("ok", "Cũ: dùng được.")})
    at = open_settings(project_root)
    at.button(key="api-key-check-btn-OPENAI_API_KEY").click().run()
    # Lưu ô trống -> lỗi; kết quả "dùng được" cũ không được ở lại gây hiểu nhầm.
    at.button(key="api-key-save-OPENAI_API_KEY").click().run()
    assert "Cũ: dùng được." not in everything(at)


# ---------- 5. Không bao giờ hiện khóa ----------


def test_end_to_end_real_check_api_key_with_leaky_library(project_root, env_path, monkeypatch):
    """Dùng ``check_api_key`` thật; chỉ giả lớp client của thư viện, lỗi trả về chứa khóa."""
    import anthropic
    import openai
    from google import genai

    write_env(env_path, KEYS)

    class Boom:
        def __init__(self, *args, api_key=None, **kwargs):
            self.models = self
            self._key = api_key

        def list(self, *args, **kwargs):
            raise ValueError(f"máy chủ trả về: khóa {self._key} bị từ chối")

    class AnthropicBoom(Boom):
        def list(self, *args, **kwargs):
            raise anthropic.AnthropicError(f"khóa {self._key} sai")

    monkeypatch.setattr(anthropic, "Anthropic", AnthropicBoom)
    monkeypatch.setattr(openai, "OpenAI", Boom)
    monkeypatch.setattr(genai, "Client", Boom)
    at = open_settings(project_root)
    for name in KEYS:
        at.button(key=f"api-key-check-btn-{name}").click().run()
        assert not at.exception, at.exception
        shown = alerts(card(at, name))
        assert len(shown) == 1 and shown[0][0] == "warning", shown
    assert_no_key(at)


@pytest.mark.parametrize("name", list(KEYS))
def test_message_containing_key_is_not_shown(project_root, env_path, monkeypatch, name):
    write_env(env_path, KEYS)
    fake_checker(monkeypatch, {name: ("invalid", f"Khóa {KEYS[name]} không đúng.")})
    at = open_settings(project_root)
    at.button(key=f"api-key-check-btn-{name}").click().run()
    assert_no_key(at)


# ---------- 6. Trường hợp xấu ----------


@pytest.mark.parametrize("name", list(KEYS))
def test_unexpected_exception_does_not_crash_or_leak(project_root, env_path, monkeypatch, name):
    write_env(env_path, KEYS)

    def boom(n, **kwargs):
        raise RuntimeError(f"lỗi lạ, khóa {KEYS[n]}")

    monkeypatch.setattr(env_file, "check_api_key", boom)
    at = open_settings(project_root)
    at.button(key=f"api-key-check-btn-{name}").click().run()
    assert not at.exception
    assert len(alerts(card(at, name))) == 1
    assert_no_key(at)


@pytest.mark.parametrize("name", list(KEYS))
def test_unexpected_exception_after_crash_page_recovers(project_root, env_path, monkeypatch, name):
    """Dù sập ở lượt bấm, lượt chạy sau trang mở lại bình thường và không nhớ khóa."""
    write_env(env_path, KEYS)

    def boom(n, **kwargs):
        raise RuntimeError("lỗi lạ")

    monkeypatch.setattr(env_file, "check_api_key", boom)
    at = open_settings(project_root)
    at.button(key=f"api-key-check-btn-{name}").click().run()
    at.run()
    assert not at.exception, at.exception
    assert not at.button(key=f"api-key-check-btn-{name}").disabled
    assert "lỗi lạ" not in "\n".join(f"{k}={v!r}" for k, v in at.session_state.to_dict().items())


@pytest.mark.parametrize(
    "message",
    [
        "<script>alert(1)</script><img src=x onerror=alert(2)>",
        "[bấm vào đây](javascript:alert(1)) **đậm** `mã` # tiêu đề",
        "Lỗi rất dài. " * 2000,  # Streamlit bỏ khoảng trắng cuối, chỉ thế thôi
        "",
        "Khóa Gemini 😀 có dấu: Đ đ Ư ư ọ ẫ\nxuống dòng\ttab",
    ],
    ids=["html", "markdown", "dai", "rong", "unicode"],
)
def test_odd_messages_shown_as_plain_alert(project_root, env_path, monkeypatch, message):
    write_env(env_path, KEYS)
    fake_checker(monkeypatch, {"GEMINI_API_KEY": ("unknown", message)})
    at = open_settings(project_root)
    at.button(key="api-key-check-btn-GEMINI_API_KEY").click().run()
    assert not at.exception, at.exception
    shown = alerts(card(at, "GEMINI_API_KEY"))
    if message:
        assert shown == [("warning", message.strip())]
    # Không phần tử markdown nào bật unsafe_allow_html với nội dung này.
    for md in at.markdown:
        if message and message[:20] in str(md.value):
            assert not md.proto.allow_html
    assert_no_key(at)
