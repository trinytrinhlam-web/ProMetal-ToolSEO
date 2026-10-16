"""Soi Lỗi · T-019 lượt 2: kiểm lại phần sửa SL-T019-1, SL-T019-2 và câu lỗi giới hạn token.

Không gọi mạng: thư viện thật của 3 hãng chỉ chạy với ``MockTransport``; giao diện dùng AppTest
với provider giả.
"""

from __future__ import annotations

import httpx
import pytest
from fake_ai import FakeProvider
from streamlit.testing.v1 import AppTest
from test_ai_openai_gemini_soi_loi import gemini_real, openai_body, openai_real
from test_ai_t028 import (
    BLOCK_START,
    BLOCK_STOP,
    START,
    anthropic_stream,
    message_end,
    text_delta,
)
from test_app_pages import button, go_to_article
from test_soi_loi_t019 import (
    CANDIDATES,
    KEYS,
    RULES,
    SETTINGS,
    app_env,  # noqa: F401 - fixture dùng chung
    open_models_tab,
    page_text,
    result_markdown,
    set_keys,
)

from seo_app.ai import AIError, TaskConfig, load_ai_config
from seo_app.ai import registry as ai_registry
from seo_app.ai.base import TokenLimitError, token_limit_error
from seo_app.content import blind_test
from seo_app.content.blind_test import (
    HIDDEN_ERROR,
    MASK,
    TOKEN_LIMIT_ERROR,
    BlindSample,
    Candidate,
    _mask_names,
    _maskable,
    run_blind_test,
    validate_request,
)
from seo_app.content.models import Draft, Review


def old_message(max_tokens: int, name: str) -> str:
    """Câu lỗi giới hạn token TRƯỚC lượt 2 (chép từng chữ từ 3 provider ở e3cee76)."""
    return (
        f"Bài dài quá giới hạn ({max_tokens} token). Tăng max_tokens của việc "
        f"«{name}» trong config/ai.toml."
    )


def cfg(provider: str, name: str = "write", max_tokens: int = 16000) -> TaskConfig:
    return TaskConfig(name=name, provider=provider, model="m", effort="high", max_tokens=max_tokens)


# ================================== (1) TokenLimitError không đổi hành vi ngoài thử mù


def openai_cut(request):
    # Bài bị cắt thật thường kèm JSON dở dang: lý do dừng phải được xét trước khuôn.
    return openai_body(
        text='{"text": "bài dài', status="incomplete", incomplete="max_output_tokens"
    )


def gemini_cut(request):
    return httpx.Response(
        200,
        json={
            "candidates": [
                {
                    "content": {"role": "model", "parts": [{"text": '{"text": "bài dài'}]},
                    "finishReason": "MAX_TOKENS",
                }
            ]
        },
    )


@pytest.mark.parametrize("name", ["write", "review", "rewrite"])
@pytest.mark.parametrize("vendor", ["openai", "gemini"])
def test_token_limit_real_library_same_message_and_still_aierror(vendor, name):
    provider = openai_real(openai_cut)[0] if vendor == "openai" else gemini_real(gemini_cut)[0]
    with pytest.raises(AIError) as info:  # nơi gọi cũ chỉ bắt AIError: vẫn bắt được
        provider.generate(cfg(vendor, name, 900), system="s", prompt="p", schema=BlindSample)
    assert type(info.value) is TokenLimitError
    assert str(info.value) == old_message(900, name)


def test_token_limit_anthropic_real_library_message_unchanged():
    # Thư viện anthropic thật đối chiếu khuôn trước khi biết lý do dừng: rơi vào câu của T-028,
    # không phải TokenLimitError. Lượt 2 không đổi câu này (Soạn bài không đổi hành vi).
    cut = START + BLOCK_START + text_delta('{"intro": "bài dài') + BLOCK_STOP
    provider = anthropic_stream(cut + message_end("max_tokens"))
    with pytest.raises(AIError) as info:
        provider.generate(
            cfg("anthropic", "write", 900), system="s", prompt="p", schema=BlindSample
        )
    assert str(info.value) == (
        "AI trả về dữ liệu không đúng khuôn (có thể bài bị cắt vì quá giới hạn 900 token). Bấm "
        "thử lại; nếu vẫn lỗi, tăng max_tokens của việc «write» trong config/ai.toml."
    )


class CutAt(FakeProvider):
    """AI giả của Soạn bài: chạm giới hạn token ở đúng một việc."""

    def __init__(self, task_name: str) -> None:
        super().__init__()
        self.task_name = task_name

    def generate(self, task, *, system, prompt, schema):
        if task.name == self.task_name:
            self.calls.append((task.name, system, prompt))
            raise token_limit_error(task)
        return super().generate(task, system=system, prompt=prompt, schema=schema)


@pytest.fixture
def write_env(monkeypatch):
    from test_app_pages import PASSWORD as WRITE_PASSWORD
    from test_app_pages import hash_password

    monkeypatch.setenv("APP_PASSWORD_HASH", hash_password(WRITE_PASSWORD, iterations=1_000))
    monkeypatch.setenv("APP_TIMEZONE", "Asia/Ho_Chi_Minh")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


@pytest.mark.parametrize(("task_name", "schema"), [("write", Draft), ("review", Review)])
def test_write_page_token_limit_shows_same_message(
    project_root, monkeypatch, write_env, task_name, schema
):
    # Soạn bài, bước viết và bước rà soát: ai_call vẫn bắt được, câu y như trước lượt 2,
    # trang không sập, không nhảy sang bước bài viết.
    from test_app_pages import write_page

    provider = CutAt(task_name)
    monkeypatch.setattr(ai_registry, "make_provider", lambda name, settings: provider)
    at = write_page(project_root)
    at.text_input(key="keyword").input("so sánh inox 201 và 304").run()
    button(at, "🔎 Phân tích từ khóa").click().run()
    button(at, "Tiếp: tạo dàn ý →").click().run()
    button(at, "✅ Duyệt dàn ý, viết toàn bài →").click().run()
    assert not at.exception, at.exception
    task = load_ai_config()[task_name]
    errors = [e.value for e in at.error]
    assert old_message(task.max_tokens, task_name) in errors
    assert TOKEN_LIMIT_ERROR not in errors
    assert at.session_state["step"] == 1
    assert provider.tasks()[-1] == task_name


def test_write_page_full_flow_still_works(project_root, monkeypatch, write_env):
    # Đối chứng: không chạm giới hạn thì luồng cũ vẫn tới bước bài viết.
    provider = FakeProvider()
    monkeypatch.setattr(ai_registry, "make_provider", lambda name, settings: provider)
    from test_app_pages import write_page

    go_to_article(write_page(project_root))


# ====================================== (1b) thử mù: câu giới hạn token với thư viện thật


def patch_real(monkeypatch, providers: dict):
    monkeypatch.setattr(blind_test, "make_provider", lambda name, settings: providers[name])


def reveal_errors(reveal) -> dict[str, str | None]:
    return {info.provider: info.error for info in reveal.values()}


@pytest.mark.parametrize("vendor", ["openai", "gemini"])
def test_blind_token_limit_real_library_points_to_effort(monkeypatch, vendor):
    provider = openai_real(openai_cut)[0] if vendor == "openai" else gemini_real(gemini_cut)[0]
    other = "gemini" if vendor == "openai" else "openai"
    good = (openai_real if other == "openai" else gemini_real)(
        (lambda r: openai_body(text='{"intro": "a", "heading": "b", "body": "c"}'))
        if other == "openai"
        else (
            lambda r: httpx.Response(
                200,
                json={
                    "candidates": [
                        {
                            "content": {
                                "role": "model",
                                "parts": [{"text": '{"intro": "a", "heading": "b", "body": "c"}'}],
                            },
                            "finishReason": "STOP",
                        }
                    ]
                },
            )
        )
    )[0]
    patch_real(monkeypatch, {vendor: provider, other: good})
    cands = [Candidate(vendor, "mo-hinh-x1", "high"), Candidate(other, "mo-hinh-y2", "low")]
    entries, reveal = run_blind_test("sửa cửa cuốn", "", cands, SETTINGS, RULES)
    assert reveal_errors(reveal) == {vendor: TOKEN_LIMIT_ERROR, other: None}
    assert sorted(e.error or "" for e in entries) == ["", HIDDEN_ERROR]


def test_blind_token_limit_anthropic_real_library_points_to_effort(monkeypatch):
    cut = START + BLOCK_START + text_delta('{"intro": "bài dài') + BLOCK_STOP
    provider = anthropic_stream(cut + message_end("max_tokens"))
    patch_real(monkeypatch, {"anthropic": provider})
    cands = [Candidate("anthropic", m, "max") for m in ("mo-hinh-x1", "mo-hinh-y2")]
    _, reveal = run_blind_test("sửa cửa cuốn", "", cands, SETTINGS, RULES)
    for info in reveal.values():
        assert "config/ai.toml" not in info.error
        assert "blind_test" not in info.error


# ======================================== (2) _maskable: tên thật của 3 hãng đều được nhận

REAL_MODELS = [
    # Anthropic
    "claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5", "claude-fable-5-1",
    "claude-opus-4-8", "claude-opus-4-1-20250805", "claude-sonnet-4-5-20250929",
    "claude-3-5-haiku-latest", "claude-3-7-sonnet-latest", "claude-opus-4@20250514",
    # OpenAI
    "gpt-5", "gpt-5.1", "gpt-5-mini", "gpt-5-nano", "gpt-6.1", "gpt-4o", "gpt-4o-mini",
    "gpt-4.1", "gpt-4.1-nano", "o1", "o3", "o3-mini", "o3-pro", "o4-mini", "chatgpt-4o-latest",
    "gpt-5-codex", "codex-mini-latest", "gpt-5-chat-latest", "ft:gpt-4o-mini:org::abc123",
    "computer-use-preview",
    # Google
    "gemini-3-pro", "gemini-3-pro-preview", "gemini-2.5-pro", "gemini-2.5-flash",
    "gemini-2.5-flash-lite", "gemini-flash-latest", "gemini-flash-lite-latest",
    "gemini-pro-latest", "models/gemini-2.5-pro", "gemini-exp-1206", "gemma-3-27b-it",
    "gemini-2.0-flash-thinking-exp-01-21",
]  # fmt: skip


@pytest.mark.parametrize("model", REAL_MODELS)
def test_real_model_names_are_accepted(model):
    assert _maskable(model)
    provider = "anthropic" if "claude" in model else "gemini" if "gem" in model else "openai"
    validate_request("cửa sắt", "", [Candidate(provider, model, "medium")] * 2)


@pytest.mark.parametrize(
    "typo", ["c", "10", "co", "cho", "khi", "con", "nha", "cua", "chung", "gpt", "chatgpt",
             "claude", "gemini", "opus", "a-b", "o", "3", "--", "..", "sonnet"]
)  # fmt: skip
def test_mistyped_names_rejected_before_any_call(monkeypatch, typo):
    calls = []
    monkeypatch.setattr(blind_test, "make_provider", lambda *a: calls.append(a))
    with pytest.raises(AIError, match="quá ngắn hoặc gõ nhầm"):
        cands = [Candidate("openai", typo, "low"), CANDIDATES[0]]
        run_blind_test("cửa sắt", "", cands, SETTINGS, RULES)
    assert calls == []


# ============================ (3) danh sách che mới không che chữ thường của bài tiếng Việt

VIETNAMESE = [
    "Sơn tĩnh điện bền 10 năm, giá 350.000đ/m².",
    "Ô pớt cửa là chốt gài; ô-pớt inox 304 bền hơn ô pớt sắt.",
    "Thợ sơn cửa, son môi màu đỏ, anh Sơn ở Hải Phòng.",
    "Cổng hai cánh, hai ku-pi-đông, chị Hài, cô Hà.",
    "Bản lề cối, khóa tay gạt, chốt âm sàn, ray trượt.",
    "Cửa sổ, cửa cuốn, cửa kéo Đài Loan, cửa xếp.",
    "Thép SS400, inox 304, inox 201, CT3, mạ kẽm nhúng nóng.",
    "Gia công tại xưởng ở Gò Vấp, giao trong 3 ngày.",
    "Bảo hành 12 tháng; gọi 0909 123 456.",
    "Sửa cửa sắt bị xệ, han gỉ, kẹt bánh xe; thay bản lề, hàn lại khung.",
    "Bạn tìm trên Google sẽ thấy nhiều xưởng; hãy hỏi kỹ bảo hành.",
    "Cửa sắt mỹ thuật hoa văn cổ điển, sơn giả gỗ, sơn nhũ đồng.",
    "Gỗ pơ-mu, sơn PU, keo silicon, ốc vít M8.",
]
REAL_CANDIDATES = ["claude-opus-5-5", "gpt-6.1", "gemini-3-pro"]


@pytest.mark.parametrize("text", VIETNAMESE)
def test_vietnamese_door_text_untouched(text):
    assert _mask_names(text, REAL_CANDIDATES) == text


@pytest.mark.parametrize(
    "text",
    ["Tôi là _Claude_.", "**__Gemini__**", "Bản Sonnet, Haiku, Opus và Fable", "Sora, Codex, Gemma",
     "Google DeepMind", "PaLM 2", "dall-e-3", "GPT-5.1-mini", "ChatGPT's"],
)  # fmt: skip
def test_vendor_words_still_masked(text):
    shown = _mask_names(text, REAL_CANDIDATES).lower()
    for word in ("claude", "gemini", "sonnet", "haiku", "opus", "fable", "sora", "codex", "gemma",
                 "deepmind", "palm", "dall", "gpt"):  # fmt: skip
        assert word not in shown, word


@pytest.mark.parametrize(
    ("text", "leak"),
    [("Tôi là Claude Opus 5.5, viết bài này.", "5.5"), ("Tôi là GPT 6.1.", "6.1"),
     ("Gemini 3 Pro viết bài.", "3 Pro")],
)  # fmt: skip
def test_version_number_after_vendor_word_is_masked(text, leak):
    assert leak not in _mask_names(text, REAL_CANDIDATES)


def test_version_like_numbers_in_article_are_kept():
    # Đối chứng cho SL-T019-3: số liệu thật trong bài không được che.
    text = "Thép dày 5.5 mm, khung 6.1 m, cửa 3 cánh."
    assert _mask_names(text, REAL_CANDIDATES) == text


# =================================================== (4) giao diện: đủ luồng thử mù 3 hãng

SECRET = {"anthropic": "mo-hinh-kin-a7", "openai": "mo-hinh-kin-b8", "gemini": "mo-hinh-kin-c9"}


class UIVendor:
    def __init__(self, provider):
        self.provider = provider

    def generate(self, task, *, system, prompt, schema):
        if self.provider == "gemini":
            # Ứng viên lỗi: câu lỗi chứa tên mô hình và tên hãng.
            raise AIError(f"Không tìm thấy mô hình {task.model} của Google Gemini.")
        if self.provider == "openai":
            raise token_limit_error(task)
        return BlindSample(
            intro=f"Tôi là {task.model} (_Claude_). Sơn tĩnh điện bền 10 năm.",
            heading="Bảo dưỡng cửa sắt",
            body="Ô pớt và bản lề nên tra dầu 6 tháng một lần.",
        )


def fill_three(at) -> AppTest:
    at.segmented_control(key="blind-count").set_value(3).run()
    at.text_input(key="blind-keyword").input("bảo dưỡng cửa sắt")
    for i, vendor in enumerate(SECRET):
        at.selectbox(key=f"blind-cand-{i}-provider").set_value(vendor).run()
        at.text_input(key=f"blind-cand-{i}-model").input(SECRET[vendor])
    at.run()
    return at


@pytest.mark.usefixtures("app_env")
def test_ui_full_flow_three_vendors_names_hidden_until_scored(project_root, monkeypatch):
    set_keys(monkeypatch, "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY")
    monkeypatch.setattr(blind_test, "make_provider", lambda name, settings: UIVendor(name))
    at = fill_three(open_models_tab(project_root))
    # Cảnh báo tốn tiền trước khi chạy, đúng số lần gọi.
    assert any("gọi AI 3 lần" in w.value and "tốn tiền" in w.value for w in at.warning)
    run = at.button(key="blind-run")
    assert not run.disabled and "3 lần" in run.label
    run.click().run()
    assert not at.exception, at.exception

    before = page_text(at)
    shown = "\n".join(el.value for el in result_markdown(at))
    for name in SECRET.values():
        assert name not in shown and name not in before, name
    for word in ("Google Gemini", "Claude", "max_tokens", "config/ai.toml"):
        assert word not in shown, word
    assert sum(w.value == HIDDEN_ERROR for w in at.warning) == 2  # 2 ứng viên lỗi y hệt nhau
    assert not at.error
    assert "Sơn tĩnh điện bền 10 năm" in shown and "Ô pớt" in shown
    assert f"_{MASK}_" in shown

    sliders = list(at.slider)
    assert len(sliders) == 1  # chỉ bài có chữ mới được chấm
    sliders[0].set_value(8).run()
    at.button(key="blind-reveal").click().run()
    assert not at.exception, at.exception
    table = at.dataframe[-1].value
    rows = {r["Mô hình"]: r for r in table.to_dict("records")}
    assert set(rows) == set(SECRET.values())
    assert rows[SECRET["anthropic"]]["Điểm"] == 8
    errors = "\n".join(e.value for e in at.error)
    assert TOKEN_LIMIT_ERROR in errors and SECRET["openai"] in errors
    assert f"Không tìm thấy mô hình {SECRET['gemini']}" in errors
    assert at.button(key="blind-reveal").disabled
    for key in KEYS:
        assert key not in page_text(at)


@pytest.mark.usefixtures("app_env")
def test_ui_mistyped_model_blocks_run_without_calling(project_root, monkeypatch):
    set_keys(monkeypatch, "ANTHROPIC_API_KEY", "OPENAI_API_KEY")
    calls = []
    monkeypatch.setattr(blind_test, "make_provider", lambda *a: calls.append(a))
    at = open_models_tab(project_root)
    at.text_input(key="blind-keyword").input("cửa sắt")
    at.text_input(key="blind-cand-0-model").input("cho")
    at.text_input(key="blind-cand-1-model").input("gpt-6.1")
    at.run()
    assert at.button(key="blind-run").disabled
    assert any("quá ngắn hoặc gõ nhầm" in c.value for c in at.caption)
    assert calls == []
