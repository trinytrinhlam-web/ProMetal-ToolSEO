"""Lớp AI: đọc config/ai.toml, chọn provider, gọi Claude qua client giả (không gọi mạng)."""

from types import SimpleNamespace

import anthropic
import httpx2
import pytest
from pydantic import BaseModel

from seo_app.ai import AIError, AIRouter, TaskConfig, load_ai_config, make_provider
from seo_app.ai.anthropic_provider import FALLBACK_BETA, AnthropicProvider
from seo_app.ai.registry import IMAGE_PROVIDERS, IMAGE_TASK, PROVIDERS
from seo_app.config import Settings

TASK = TaskConfig(name="write", provider="anthropic", model="claude-opus-5-5", effort="high")


class Answer(BaseModel):
    text: str


# ------------------------------------------------------------------ cấu hình


def test_project_ai_config_is_valid():
    # Không có hãng mặc định (chốt 2026-10-15): kiểm từng việc, không đòi mọi việc là anthropic.
    tasks = load_ai_config()
    assert {"research", "outline", "write", "rewrite", "review", "alt"} <= set(tasks)
    assert tasks["research"].web_search is True
    for name, task in tasks.items():
        assert task.provider in PROVIDERS, name
        assert task.model.strip(), name
        assert task.max_tokens > 0, name
        if name != "research":
            assert task.web_search is False, name  # chỉ bước nghiên cứu được tìm web
    if IMAGE_TASK in tasks:  # sau T-053 khối [tasks.image] được bật
        assert tasks[IMAGE_TASK].provider in IMAGE_PROVIDERS


@pytest.mark.parametrize(
    ("body", "message"),
    [
        ('[tasks.x]\nprovider = "abc"\nmodel = "m"', "không biết hãng"),
        ('[tasks.x]\nprovider = "anthropic"\nmodel = "m"\neffort = "rất cao"', "effort"),
        ('[tasks.x]\nprovider = "anthropic"', "model"),
        ("[tasks.x\n", "cú pháp"),
    ],
)
def test_bad_ai_config_gives_vietnamese_error(tmp_path, body, message):
    path = tmp_path / "ai.toml"
    path.write_text(body, encoding="utf-8")
    with pytest.raises(AIError, match=message):
        load_ai_config(path)


def test_missing_api_key_is_reported():
    with pytest.raises(AIError, match="ANTHROPIC_API_KEY"):
        make_provider("anthropic", Settings())


def test_openai_and_gemini_are_supported():
    # T-018: trước đây OpenAI/Gemini báo "chưa được hỗ trợ"; nay tạo đúng provider của hãng.
    from seo_app.ai.gemini_provider import GeminiProvider
    from seo_app.ai.openai_provider import OpenAIProvider

    assert isinstance(make_provider("openai", Settings(openai_api_key="k")), OpenAIProvider)
    assert isinstance(make_provider("gemini", Settings(gemini_api_key="k")), GeminiProvider)


def test_router_builds_one_provider_per_vendor():
    router = AIRouter({"write": TASK}, Settings(anthropic_api_key="sk-test"))
    provider, task = router.get("write")
    assert isinstance(provider, AnthropicProvider)
    assert task is TASK


# ---------------------------------------------------------- provider Anthropic


class FakeStream:
    def __init__(self, message):
        self.message = message

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def get_final_message(self):
        return self.message


class FakeClient:
    """Giả ``anthropic.Anthropic``: trả lần lượt các message soạn sẵn, ghi lại tham số."""

    def __init__(self, *results):
        self.results = list(results)
        self.calls: list[dict] = []
        self.beta = SimpleNamespace(messages=SimpleNamespace(stream=self.stream))

    def stream(self, **kwargs):
        self.calls.append(kwargs)
        result = self.results.pop(0)
        if isinstance(result, Exception):
            raise result
        return FakeStream(result)


def message(stop_reason="end_turn", parsed=None):
    return SimpleNamespace(stop_reason=stop_reason, parsed_output=parsed, content=["…"])


def generate(client, task=TASK):
    provider = AnthropicProvider("sk-test", client=client)
    return provider.generate(task, system="hệ thống", prompt="viết đi", schema=Answer)


def test_returns_parsed_output_and_sends_task_settings():
    client = FakeClient(message(parsed=Answer(text="xong")))
    assert generate(client) == Answer(text="xong")
    call = client.calls[0]
    assert call["model"] == "claude-opus-5-5"
    assert call["output_format"] is Answer
    assert call["output_config"] == {"effort": "high"}
    assert call["betas"] == [FALLBACK_BETA] and call["fallbacks"] == "default"
    assert "tools" not in call
    assert "thinking" not in call  # Opus 5.5 luôn suy nghĩ; chỉ chỉnh bằng effort


def test_web_search_task_adds_tool_and_resumes_after_pause():
    task = TaskConfig(name="research", provider="anthropic", model="m", web_search=True)
    client = FakeClient(message("pause_turn"), message(parsed=Answer(text="ok")))
    assert generate(client, task).text == "ok"
    assert client.calls[0]["tools"][0]["name"] == "web_search"
    resumed = client.calls[1]["messages"]
    assert [m["role"] for m in resumed] == ["user", "assistant"]


@pytest.mark.parametrize(
    ("stop_reason", "message_part"),
    [("refusal", "từ chối"), ("max_tokens", "max_tokens")],
)
def test_bad_stop_reasons_become_vietnamese_errors(stop_reason, message_part):
    with pytest.raises(AIError, match=message_part):
        generate(FakeClient(message(stop_reason)))


def test_unparsable_output_is_an_error():
    with pytest.raises(AIError, match="không đúng khuôn"):
        generate(FakeClient(message(parsed=None)))


def api_error(cls, status):
    response = httpx2.Response(status, request=httpx2.Request("POST", "https://api.test"))
    return cls("lỗi", response=response, body=None)


@pytest.mark.parametrize(
    ("error", "message_part"),
    [
        (api_error(anthropic.AuthenticationError, 401), "ANTHROPIC_API_KEY"),
        (api_error(anthropic.NotFoundError, 404), "config/ai.toml"),
        (api_error(anthropic.RateLimitError, 429), "giới hạn"),
        (api_error(anthropic.InternalServerError, 500), "500"),
        (
            anthropic.APIConnectionError(request=httpx2.Request("POST", "https://api.test")),
            "mạng",
        ),
    ],
)
def test_api_errors_become_vietnamese_errors(error, message_part):
    with pytest.raises(AIError, match=message_part):
        generate(FakeClient(error))
