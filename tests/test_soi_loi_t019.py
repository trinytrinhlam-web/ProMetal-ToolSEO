"""Soi Lỗi kiểm thử T-019 (thử mù mô hình): tìm cách làm phần mới hỏng.

- Thử mù có "mù" thật không: thứ tự nhãn, chữ AI tự xưng tên, câu lỗi, trang trước khi chấm.
- Một hãng lỗi / thiếu khóa / thiếu thư viện: các hãng khác vẫn có bài, câu lỗi tiếng Việt,
  không lộ khóa, không traceback.
- Chữ AI hiện an toàn trên trang (không HTML, không link Markdown).
- Không có hãng mặc định ngầm.

Lỗi thật tìm được để ở dạng ``xfail(strict=True)``, có mã trong báo cáo
``docs/team/reports/T-019-soi-loi.md``. Không gọi mạng (thư viện thật dùng ``MockTransport``).
"""

from __future__ import annotations

import dataclasses
import sys
from collections import Counter

import httpx2
import openai
import pytest
from streamlit.testing.v1 import AppTest

import seo_app.config as config
from seo_app.ai import AIError, make_provider
from seo_app.ai.base import library_message
from seo_app.auth import hash_password
from seo_app.config import Settings
from seo_app.content import blind_test
from seo_app.content.blind_test import (
    HIDDEN_ERROR,
    MASK,
    UNEXPECTED_ERROR,
    BlindSample,
    Candidate,
    run_blind_test,
)
from seo_app.content.rules import ContentRules, ContentRulesError

RULES = ContentRules(
    business_profile="- Hotline: 0909",
    address="Xưng chúng tôi, gọi bạn",
    tone="thân thiện",
    banned=(),
    checklist=(),
)
ANTHROPIC_KEY = "sk-ant-api03-SoiLoiT019KhoaGia_1234567890abcdef"
OPENAI_KEY = "sk-proj-SoiLoiT019KhoaGia_1234567890abcdef"
GEMINI_KEY = "AIzaSySoiLoiT019KhoaGia_1234567890abcd"
KEYS = (ANTHROPIC_KEY, OPENAI_KEY, GEMINI_KEY)
SETTINGS = Settings(
    anthropic_api_key=ANTHROPIC_KEY, openai_api_key=OPENAI_KEY, gemini_api_key=GEMINI_KEY
)
CANDIDATES = [
    Candidate("anthropic", "mo-hinh-bi-mat-x1", "high"),
    Candidate("openai", "mo-hinh-bi-mat-y2", "medium"),
    Candidate("gemini", "mo-hinh-bi-mat-z3", "low"),
]
MODELS = [c.model for c in CANDIDATES]
# Chữ nhận ra được hãng / dòng mô hình nếu còn trong bài trước khi chấm.
IDENTIFYING = ("claude", "anthropic", "openai", "chatgpt", "gpt", "gemini", "opus", "sonnet",
               "deepmind", "bard")  # fmt: skip


def visible(entries) -> str:
    return "\n".join(str(dataclasses.asdict(e)) for e in entries)


class WritingVendor:
    """Provider giả: viết ``text`` (hàm của tên mô hình) vào mọi phần của bài."""

    def __init__(self, write):
        self.write = write

    def generate(self, task, *, system, prompt, schema):
        text = self.write(task)
        return BlindSample(intro=text, heading=text, body=text)


def patch_vendors(monkeypatch, write=lambda task: "Bài viết thường.", real=()):
    """Thay ``make_provider``: hãng trong ``real`` dùng hàm thật, còn lại dùng provider giả."""

    def factory(provider, settings):
        if provider in real:
            return make_provider(provider, settings)
        return WritingVendor(write)

    monkeypatch.setattr(blind_test, "make_provider", factory)


def run(candidates=CANDIDATES, settings=SETTINGS, **kwargs):
    return run_blind_test("sửa cửa cuốn", "", candidates, settings, RULES, **kwargs)


# ============================================================ thứ tự nhãn không đoán được


def test_label_order_is_uniform_without_fixed_seed(monkeypatch):
    # Không truyền rng (như giao diện): mỗi ứng viên rơi vào mỗi nhãn gần đều nhau. Ứng viên
    # nhập đầu tiên KHÔNG luôn là A. 600 lượt, kỳ vọng 200 mỗi ô; dưới 120 gần như không thể.
    patch_vendors(monkeypatch)
    seen: Counter = Counter()
    for _ in range(600):
        _, reveal = run()
        for label, info in reveal.items():
            seen[(info.model, label)] += 1
    for model in MODELS:
        for label in "ABC":
            assert seen[(model, label)] > 120, seen


def test_entries_have_same_shape_for_every_vendor(monkeypatch):
    # Cùng bài thì phần hiện ra của mọi nhãn y hệt nhau (trừ nhãn): không trường nào lộ hãng.
    patch_vendors(monkeypatch)
    entries, _ = run()
    shapes = {(e.intro, e.heading, e.body, e.error, e.ok) for e in entries}
    assert len(shapes) == 1
    assert {f.name for f in dataclasses.fields(entries[0])} == {
        "label", "intro", "heading", "body", "error"
    }  # fmt: skip


# ======================================================= AI tự xưng tên: phải bị che hết

MASKED_OK = {
    "đậm": "Tôi là **Claude**.",
    "sở hữu": "Theo Claude's ghi chú.",
    "ChatGPT": "ChatGPT gợi ý thế này.",
    "GPT có số": "Bản GPT-5.1-mini viết.",
    "Google Gemini": "Google Gemini cho rằng.",
    "link": "[Claude](https://anthropic.com) nói.",
    "chữ hoa": "CLAUDE và OPENAI.",
    "tên ứng viên": "Viết bởi mo-hinh-bi-mat-y2-preview.",
}


@pytest.mark.parametrize("text", list(MASKED_OK.values()), ids=list(MASKED_OK))
def test_ai_naming_itself_is_masked(monkeypatch, text):
    patch_vendors(monkeypatch, write=lambda task: text)
    entries, _ = run()
    shown = visible(entries).lower()
    assert MASK in visible(entries)
    for word in IDENTIFYING + tuple(m.lower() for m in MODELS):
        assert word not in shown, word


LEAKING = {
    "nghiêng bằng gạch dưới": "Tôi là _Claude_, rất vui.",
    "đậm bằng gạch dưới": "Bài do __Gemini__ viết.",
    "dòng mô hình Opus": "Tôi là Claude Opus 5.5.",
    "dòng mô hình Sonnet": "Bản Sonnet viết nhanh.",
    "DeepMind": "Theo nghiên cứu của Google DeepMind.",
}


@pytest.mark.xfail(
    strict=True,
    reason="SL-T019-1: bỏ sót tên đứng sau '_' (Markdown nghiêng) và tên dòng mô hình",
)
@pytest.mark.parametrize("text", list(LEAKING.values()), ids=list(LEAKING))
def test_ai_naming_itself_markdown_underscore_and_family_names(monkeypatch, text):
    patch_vendors(monkeypatch, write=lambda task: text)
    entries, _ = run()
    shown = visible(entries).lower()
    for word in IDENTIFYING:
        assert word not in shown, word


# ======================================== một hãng lỗi / thiếu khóa / thiếu thư viện


def test_missing_library_for_one_vendor(monkeypatch):
    # google-genai không nhập được (thư viện lệch): ứng viên Gemini lỗi "uv sync", hai ứng viên
    # kia vẫn có bài. Dùng make_provider thật cho Gemini.
    monkeypatch.setitem(sys.modules, "seo_app.ai.gemini_provider", None)
    patch_vendors(monkeypatch, real=("gemini",))
    entries, reveal = run()
    errors = {label: info.error for label, info in reveal.items() if info.error}
    assert len(errors) == 1
    label, message = errors.popitem()
    assert reveal[label].provider == "gemini"
    assert message == library_message("Google Gemini")
    assert [e.ok for e in entries].count(False) == 1
    assert next(e for e in entries if e.label == label).error == HIDDEN_ERROR


def test_missing_key_for_one_vendor(monkeypatch):
    patch_vendors(monkeypatch, real=("openai",))
    settings = Settings(anthropic_api_key=ANTHROPIC_KEY, gemini_api_key=GEMINI_KEY)
    entries, reveal = run(settings=settings)
    failed = [info for info in reveal.values() if info.error]
    assert [f.provider for f in failed] == ["openai"]
    assert "Chưa có khóa" in failed[0].error and "OPENAI_API_KEY" in failed[0].error
    assert sum(e.ok for e in entries) == 2


def test_wrong_key_real_library_never_shows_key(monkeypatch):
    # Thư viện openai thật, mạng giả trả 401 kèm khóa trong câu: câu lỗi cố định, không có khóa.
    real_openai = openai.OpenAI

    def handler(request):
        body = {"error": {"message": f"Incorrect API key provided: {OPENAI_KEY}", "code": None}}
        return httpx2.Response(401, json=body)

    def make_openai(**kwargs):
        transport = httpx2.MockTransport(handler)
        return real_openai(**kwargs, http_client=httpx2.Client(transport=transport))

    monkeypatch.setattr(openai, "OpenAI", make_openai)
    patch_vendors(monkeypatch, real=("openai",))
    entries, reveal = run()
    failed = [info for info in reveal.values() if info.error]
    assert [f.provider for f in failed] == ["openai"]
    assert failed[0].error == "Khóa OPENAI_API_KEY trong file .env không đúng."
    everything = visible(entries) + str(reveal)
    for key in KEYS:
        assert key not in everything


def test_all_fail_differently_but_look_the_same(monkeypatch):
    # Ba lỗi khác nhau (thiếu thư viện, thiếu khóa, lỗi lạ có khóa trong câu): phần bài trước
    # khi chấm y hệt nhau, nên không đoán được nhãn nào là hãng nào.
    monkeypatch.setitem(sys.modules, "seo_app.ai.gemini_provider", None)

    def factory(provider, settings):
        if provider == "anthropic":
            raise ValueError(f"lỗi lạ {ANTHROPIC_KEY}")
        return make_provider(provider, settings)

    monkeypatch.setattr(blind_test, "make_provider", factory)
    settings = Settings(anthropic_api_key=ANTHROPIC_KEY, gemini_api_key=GEMINI_KEY)
    entries, reveal = run(settings=settings)
    assert {(e.intro, e.heading, e.body, e.error) for e in entries} == {("", "", "", HIDDEN_ERROR)}
    by_provider = {info.provider: info.error for info in reveal.values()}
    assert by_provider["anthropic"] == UNEXPECTED_ERROR
    assert "Chưa có khóa" in by_provider["openai"]
    assert "uv sync" in by_provider["gemini"]
    for key in KEYS:
        assert key not in str(reveal)


def test_no_default_vendor():
    # Không có hãng mặc định: ứng viên không ghi hãng thì bị từ chối trước khi gọi AI.
    with pytest.raises(AIError, match="chưa chọn hãng"):
        run([Candidate("", "mo-hinh-a"), Candidate("openai", "mo-hinh-b")])
    with pytest.raises(TypeError):
        Candidate(model="mo-hinh-a")  # type: ignore[call-arg]  # hãng là tham số bắt buộc


# ================================================== giao diện (AppTest, AI giả, không mạng)

PASSWORD = "mat-khau-thu-123"
KEY_ENVS = {"ANTHROPIC_API_KEY": ANTHROPIC_KEY, "OPENAI_API_KEY": OPENAI_KEY,
            "GEMINI_API_KEY": GEMINI_KEY}  # fmt: skip


@pytest.fixture
def app_env(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_PASSWORD_HASH", hash_password(PASSWORD, iterations=1_000))
    monkeypatch.setattr(config, "DEFAULT_ENV_FILE", tmp_path / ".env")
    for name in KEY_ENVS:
        monkeypatch.delenv(name, raising=False)


def set_keys(monkeypatch, *names):
    for name in names:
        monkeypatch.setenv(name, KEY_ENVS[name])


def open_models_tab(project_root) -> AppTest:
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    at.text_input[0].input(PASSWORD)
    at.button[0].click().run()
    at.switch_page("views/settings.py").run()
    assert not at.exception, at.exception
    return at


def fill_and_run(at, models=("mo-hinh-bi-mat-x1", "mo-hinh-bi-mat-y2")) -> AppTest:
    at.text_input(key="blind-keyword").input("cửa sắt mỹ thuật")
    for i, model in enumerate(models):
        at.text_input(key=f"blind-cand-{i}-model").input(model)
    at.run()
    at.button(key="blind-run").click().run()
    assert not at.exception, at.exception
    return at


def page_text(at) -> str:
    parts = []
    for kind in ("markdown", "caption", "success", "error", "warning", "info", "code"):
        parts.extend(str(el.value) for el in getattr(at, kind))
    for frame in at.dataframe:
        parts.append(frame.value.to_string())
    return "\n".join(parts)


def result_markdown(at) -> list:
    """Các ô Markdown của phần kết quả (sau tiêu đề "Chấm điểm")."""
    md = list(at.markdown)
    start = next(i for i, el in enumerate(md) if "Chấm điểm" in el.value)
    # Tab sau ("🖼️ Ảnh") bắt đầu bằng "Thư mục ảnh thật": dừng ở đó.
    end = next(i for i, el in enumerate(md) if "Thư mục ảnh thật" in el.value)
    return md[start + 1 : end]


def test_ui_end_to_end_names_hidden_until_reveal(project_root, monkeypatch, app_env):
    # Chạy run_blind_test THẬT (chỉ thay provider): AI tự xưng tên mô hình và hãng trong bài.
    set_keys(monkeypatch, "ANTHROPIC_API_KEY", "OPENAI_API_KEY")
    patch_vendors(monkeypatch, write=lambda t: f"Tôi là {t.model}, một mô hình của OpenAI.")
    at = fill_and_run(open_models_tab(project_root))
    shown = "\n".join(el.value for el in result_markdown(at)).lower()
    assert "bài a" in shown and "bài b" in shown
    for word in ("mo-hinh-bi-mat", "openai", "anthropic"):
        assert word not in shown, word
    at.button(key="blind-reveal").click().run()
    assert not at.exception
    table = at.dataframe[-1].value.to_string()
    assert "mo-hinh-bi-mat-x1" in table and "mo-hinh-bi-mat-y2" in table


def test_ui_ai_html_and_links_are_not_rendered(project_root, monkeypatch, app_env):
    set_keys(monkeypatch, "ANTHROPIC_API_KEY", "OPENAI_API_KEY")
    nasty = (
        "Mở bài <img src=x onerror=alert(1)> <script>alert(2)</script> "
        "[bấm vào](javascript:alert(3)) ![ảnh](https://evil.example/p.png) "
        "[tham chiếu][1]\n\n[1]: https://evil.example/ref"
    )
    patch_vendors(monkeypatch, write=lambda t: nasty)
    at = fill_and_run(open_models_tab(project_root))
    shown = result_markdown(at)
    text = "\n".join(el.value for el in shown)
    for bad in ("<img", "onerror", "<script", "javascript:", "](", "]:", "evil.example/p.png"):
        assert bad not in text, bad
    assert all(not el.proto.allow_html for el in shown)


def test_ui_all_candidates_fail_no_traceback_no_key(project_root, monkeypatch, app_env):
    # Hai hãng đều thiếu thư viện: trang không sập, chỉ câu cố định; sau khi hiện tên mới có
    # câu "uv sync" của đúng hãng. Khóa không xuất hiện ở đâu.
    set_keys(monkeypatch, "OPENAI_API_KEY", "GEMINI_API_KEY")
    monkeypatch.setitem(sys.modules, "seo_app.ai.openai_provider", None)
    monkeypatch.setitem(sys.modules, "seo_app.ai.gemini_provider", None)
    at = fill_and_run(open_models_tab(project_root))
    warnings = [w.value for w in at.warning if w.value == HIDDEN_ERROR]
    assert len(warnings) == 2
    assert "uv sync" not in page_text(at)
    at.button(key="blind-reveal").click().run()
    assert not at.exception
    errors = "\n".join(e.value for e in at.error)
    assert library_message("OpenAI") in errors and library_message("Google Gemini") in errors
    for key in KEYS:
        assert key not in page_text(at)


def test_ui_broken_content_rules_shows_vietnamese_error(project_root, monkeypatch, app_env):
    import seo_app.content as content

    def broken():
        raise ContentRulesError("File config/content.toml viết sai cú pháp: dòng 3")

    set_keys(monkeypatch, "ANTHROPIC_API_KEY")
    monkeypatch.setattr(content, "load_rules", broken)
    patch_vendors(monkeypatch)
    at = fill_and_run(open_models_tab(project_root))
    assert any("content.toml" in e.value for e in at.error)
    assert not any("Chấm điểm" in el.value for el in at.markdown)  # không có kết quả cũ/nửa vời


def test_ui_only_keyed_vendor_offered_no_hidden_default(project_root, monkeypatch, app_env):
    # Chỉ có khóa Gemini: mọi ô hãng chỉ có Gemini; Claude (hãng đầu danh sách) không được
    # chọn sẵn ngầm.
    set_keys(monkeypatch, "GEMINI_API_KEY")
    at = open_models_tab(project_root)
    for i in range(2):
        box = at.selectbox(key=f"blind-cand-{i}-provider")
        assert box.options == ["Google Gemini"] and box.value == "gemini"
