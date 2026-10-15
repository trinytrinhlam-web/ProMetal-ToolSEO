"""T-028: máy chủ AI trả mã 200 nhưng nội dung hỏng; bỏ qua ``*_CUSTOM_HEADERS``.

- Cả 3 hãng, lúc viết bài (``generate``) lẫn nút Kiểm tra khóa: trang HTML, JSON hỏng, JSON sai
  dạng, luồng SSE hỏng/đứt, thiếu trường → câu tiếng Việt cố định, không chép dữ liệu máy chủ,
  không nhầm sang câu "uv sync" (thư viện lệch phiên bản).
- Lỗi lúc gọi thư viện (trước khi có trả lời) vẫn ra câu "uv sync".
- ``ANTHROPIC_CUSTOM_HEADERS``, ``OPENAI_CUSTOM_HEADERS`` không chèn được header; chế độ ghi/phát
  lại của google-genai tắt; ``HTTPS_PROXY``, ``SSL_CERT_FILE`` giữ nguyên.

Không gọi mạng: thư viện thật chạy với ``MockTransport``.
"""

import json
import os
from types import SimpleNamespace

import anthropic
import httpx
import httpx2
import openai
import pydantic
import pytest
from google import genai
from google.genai import types

from seo_app import env_file
from seo_app.ai import AIError, TaskConfig
from seo_app.ai import base as base_module
from seo_app.ai.anthropic_provider import AnthropicProvider
from seo_app.ai.base import (
    IGNORED_ENV,
    bad_response_message,
    ignoring_custom_headers,
    is_bad_response,
    library_message,
    network_error_kind,
    unreadable_error,
)
from seo_app.ai.gemini_provider import BAD_RESPONSE, GeminiProvider
from seo_app.ai.openai_provider import OpenAIProvider
from seo_app.ai.registry import PROVIDERS

ANTHROPIC_KEY = "sk-ant-api03-T028KhoaGia_1234567890abcdef"
OPENAI_KEY = "sk-proj-T028KhoaGia_1234567890abcdef"
GEMINI_KEY = "AIzaSyT028KhoaGia_1234567890abcdefGH"
# Chuỗi lạ máy chủ/proxy chèn vào trả lời: không bao giờ được hiện ra.
SERVER_TEXT = "T028_CHU_MAY_CHU"

VENDOR = {"anthropic": "Anthropic", "openai": "OpenAI", "gemini": "Gemini"}
NAMES = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY"}
KEYS = {"anthropic": ANTHROPIC_KEY, "openai": OPENAI_KEY, "gemini": GEMINI_KEY}
BAD_SHAPE = "AI trả về dữ liệu không đúng khuôn. Bấm thử lại."


class Answer(pydantic.BaseModel):
    text: str


def task(provider, **kwargs):
    values = {"name": "write", "provider": provider, "model": "mo-hinh-thu", "effort": "high"}
    values.update(kwargs)
    return TaskConfig(**values)


def generate(provider, vendor, **task_kwargs):
    return provider.generate(task(vendor, **task_kwargs), system="s", prompt="p", schema=Answer)


# ------------------------------------------------------------------- client thật + mạng giả


def stainless_client(vendor, handler):
    cls = anthropic.Anthropic if vendor == "anthropic" else openai.OpenAI
    return cls(
        api_key=KEYS[vendor],
        max_retries=0,
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler)),
    )


def gemini_client(handler):
    return genai.Client(
        api_key=GEMINI_KEY,
        vertexai=False,
        http_options=types.HttpOptions(
            retry_options=types.HttpRetryOptions(attempts=1),
            client_args={"transport": httpx.MockTransport(handler)},
        ),
    )


def real_client(vendor, body):
    """Client thật của ``vendor``; máy chủ giả luôn trả mã 200 với ``body`` (dict cho Response)."""
    if vendor == "gemini":
        return gemini_client(lambda request: httpx.Response(200, **body))
    return stainless_client(vendor, lambda request: httpx2.Response(200, **body))


def real_provider(vendor, body):
    cls = {"anthropic": AnthropicProvider, "openai": OpenAIProvider, "gemini": GeminiProvider}
    return cls[vendor](KEYS[vendor], client=real_client(vendor, body))


HTML = {"content-type": "text/html"}
SSE = {"content-type": "text/event-stream"}
JSON_TYPE = {"content-type": "application/json"}

# Trả lời mã 200 không đọc được, như proxy/Wi-Fi công cộng chen vào hoặc máy chủ trục trặc.
GARBAGE = {
    "html": {"text": f"<html><b>Đăng nhập Wi-Fi</b> {SERVER_TEXT}</html>", "headers": HTML},
    "html-khong-content-type": {"text": f"<html>{SERVER_TEXT}</html>"},
    "json-hong": {"text": '{"' + SERVER_TEXT, "headers": JSON_TYPE},
    "json-thuong": {"json": {"loi": SERVER_TEXT}},
    "json-danh-sach": {"json": [SERVER_TEXT, 2]},
    "json-null": {"text": "null", "headers": JSON_TYPE},
    "rong": {"text": ""},
    "sse-hong": {"text": f"event: message_start\ndata: {{{SERVER_TEXT}\n\n", "headers": SSE},
    "sse-rong": {"text": "", "headers": SSE},
    "sse-thieu-truong": {
        "text": 'event: message_start\ndata: {"type": "message_start"}\n\n',
        "headers": SSE,
    },
    "utf8-hong": {"content": b'{"loi": "\xff\xfe"}', "headers": JSON_TYPE},
}


def assert_fixed_message(message):
    assert SERVER_TEXT not in message
    assert "uv sync" not in message
    for key in KEYS.values():
        assert key not in message
    for raw in ("Traceback", "Error", "line ", "char ", "<", "{"):
        assert raw not in message


# ====================================================== viết bài: 3 hãng, mọi dạng trả lời hỏng


@pytest.mark.parametrize("vendor", ["anthropic", "openai", "gemini"])
@pytest.mark.parametrize("kind", list(GARBAGE))
def test_generate_garbage_200_gives_fixed_vietnamese_error(vendor, kind):
    with pytest.raises(AIError) as info:
        generate(real_provider(vendor, GARBAGE[kind]), vendor)
    message = str(info.value)
    assert_fixed_message(message)
    assert message in (bad_response_message(VENDOR[vendor]), BAD_SHAPE)


@pytest.mark.parametrize("kind", list(GARBAGE))
def test_anthropic_garbage_is_strange_data(kind):
    # Anthropic dùng luồng SSE: mọi dạng trên đều là "dữ liệu lạ" (không phải "không đúng khuôn").
    with pytest.raises(AIError) as info:
        generate(real_provider("anthropic", GARBAGE[kind]), "anthropic")
    assert str(info.value) == bad_response_message("Anthropic")
    assert info.value.__cause__ is not None  # giữ lỗi gốc để tra cứu


@pytest.mark.parametrize("kind", ["json-hong", "utf8-hong"])
def test_openai_unreadable_json_is_strange_data(kind):
    with pytest.raises(AIError) as info:
        generate(real_provider("openai", GARBAGE[kind]), "openai")
    assert str(info.value) == bad_response_message("OpenAI")


def test_gemini_message_unchanged():
    # Câu của Gemini giữ đúng như trước T-028, giờ dùng chung một mẫu với 2 hãng kia.
    assert BAD_RESPONSE == (
        "Máy chủ Gemini trả về dữ liệu lạ (có thể do mạng Wi-Fi hoặc proxy). Kiểm tra mạng rồi "
        "thử lại."
    )


@pytest.mark.parametrize(
    "body",
    [
        {"output": 5},
        {"output": SERVER_TEXT},
        {"output": [{"type": "message", "content": 5}]},
        {"output": [{"type": "message", "content": [{"type": "output_text", "text": 5}]}]},
        {"output": [{"type": "message", "content": [{"type": "output_text", "text": ["a"]}]}]},
        {"output": [5, None, "x"]},
        {"status": [1], "output": []},
    ],
)
def test_openai_wrongly_typed_json_is_bad_shape_not_library(body):
    # Trước T-028: "output": 5 làm vòng lặp đọc trả lời ném TypeError → câu "uv sync".
    with pytest.raises(AIError) as info:
        generate(real_provider("openai", {"json": body}), "openai")
    assert str(info.value) == BAD_SHAPE


# ------------------------------------------------------------- Anthropic: luồng SSE cụ thể


def sse(event, data):
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


MESSAGE = {
    "id": "msg_1",
    "type": "message",
    "role": "assistant",
    "model": "mo-hinh-thu",
    "content": [],
    "stop_reason": None,
    "stop_sequence": None,
    "usage": {"input_tokens": 1, "output_tokens": 1},
}
START = sse("message_start", {"type": "message_start", "message": MESSAGE})
BLOCK_START = sse(
    "content_block_start",
    {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}},
)


def text_delta(text):
    return sse(
        "content_block_delta",
        {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": text}},
    )


BLOCK_STOP = sse("content_block_stop", {"type": "content_block_stop", "index": 0})


def message_end(reason):
    return sse(
        "message_delta",
        {
            "type": "message_delta",
            "delta": {"stop_reason": reason, "stop_sequence": None},
            "usage": {"output_tokens": 2},
        },
    ) + sse("message_stop", {"type": "message_stop"})


def anthropic_stream(text):
    return real_provider("anthropic", {"text": text, "headers": SSE})


def test_anthropic_valid_stream_still_works():
    full = (
        START + BLOCK_START + text_delta('{"text": "chào"}') + BLOCK_STOP + message_end("end_turn")
    )
    assert generate(anthropic_stream(full), "anthropic") == Answer(text="chào")


def test_anthropic_cut_at_max_tokens_is_explained():
    # Bài bị cắt vì max_tokens: thư viện đối chiếu khuôn ngay khi khối chữ kết thúc (trước khi
    # biết lý do dừng) và ném ValidationError thô. Trước T-028: Streamlit hiện traceback.
    cut = START + BLOCK_START + text_delta('{"text": "bài dài') + BLOCK_STOP
    with pytest.raises(AIError) as info:
        generate(anthropic_stream(cut + message_end("max_tokens")), "anthropic", max_tokens=900)
    message = str(info.value)
    assert message == (
        "AI trả về dữ liệu không đúng khuôn (có thể bài bị cắt vì quá giới hạn 900 token). Bấm "
        "thử lại; nếu vẫn lỗi, tăng max_tokens của việc «write» trong config/ai.toml."
    )
    assert isinstance(info.value.__cause__, pydantic.ValidationError)


@pytest.mark.parametrize(
    "text",
    [
        text_delta('{"text": "x"}'),  # thiếu message_start: RuntimeError của thư viện
        sse("message_start", {"type": "message_start", "message": {}}),  # message rỗng
        sse("su_kien_la", {"type": SERVER_TEXT}),  # sự kiện lạ, không có bài
        "<html>" + SERVER_TEXT,
        START + sse("content_block_start", {"type": "content_block_start", "index": "x"}),
    ],
    ids=["thieu-message_start", "message-rong", "su-kien-la", "html-trong-sse", "index-sai"],
)
def test_anthropic_broken_stream_is_strange_data(text):
    with pytest.raises(AIError) as info:
        generate(anthropic_stream(text), "anthropic")
    assert str(info.value) == bad_response_message("Anthropic")


def test_anthropic_stream_cut_off_after_start_is_bad_shape():
    # Luồng dừng giữa chừng nhưng đúng dạng: không có bài → câu "không đúng khuôn" như trước.
    with pytest.raises(AIError) as info:
        generate(anthropic_stream(START + BLOCK_START + text_delta('{"te')), "anthropic")
    assert str(info.value) == BAD_SHAPE


class BrokenStream(httpx2.SyncByteStream):
    def __init__(self, error):
        self.error = error

    def __iter__(self):
        yield START.encode()
        raise self.error


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (
            httpx2.ReadError("connection reset " + SERVER_TEXT),
            "Mất kết nối tới Anthropic giữa chừng. Kiểm tra mạng Internet rồi bấm thử lại.",
        ),
        (
            httpx2.RemoteProtocolError("peer closed " + SERVER_TEXT),
            "Mất kết nối tới Anthropic giữa chừng. Kiểm tra mạng Internet rồi bấm thử lại.",
        ),
        (httpx2.ReadTimeout("timed out " + SERVER_TEXT), "Anthropic trả lời quá lâu. Bấm thử lại."),
        (httpx2.DecodingError("gzip " + SERVER_TEXT), bad_response_message("Anthropic")),
    ],
    ids=["ReadError", "RemoteProtocolError", "ReadTimeout", "DecodingError"],
)
def test_anthropic_network_failure_mid_stream(error, expected):
    # Mạng đứt khi đang đọc luồng: thư viện để lọt lỗi thô của httpx2.
    def handler(request):
        return httpx2.Response(200, stream=BrokenStream(error), headers=SSE)

    provider = AnthropicProvider(ANTHROPIC_KEY, client=stainless_client("anthropic", handler))
    with pytest.raises(AIError) as info:
        generate(provider, "anthropic")
    assert str(info.value) == expected
    assert info.value.__cause__ is error


# ====================================== lỗi lúc gọi thư viện vẫn là "uv sync" (không bắt nhầm)


def assert_library_error(info, vendor):
    assert str(info.value) == library_message(PROVIDERS[vendor][0])


@pytest.mark.parametrize("error_type", [TypeError, AttributeError, KeyError, ImportError])
def test_anthropic_library_error_before_response_is_still_library(error_type):
    def stream(**kwargs):
        raise error_type("thư viện đổi")

    client = SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(stream=stream)))
    with pytest.raises(AIError) as info:
        generate(AnthropicProvider(ANTHROPIC_KEY, client=client), "anthropic")
    assert_library_error(info, "anthropic")


@pytest.mark.parametrize("error_type", [TypeError, AttributeError, KeyError, ImportError])
def test_openai_library_error_before_response_is_still_library(error_type):
    def create(**kwargs):
        raise error_type("thư viện đổi")

    client = SimpleNamespace(responses=SimpleNamespace(create=create))
    with pytest.raises(AIError) as info:
        generate(OpenAIProvider(OPENAI_KEY, client=client), "openai")
    assert_library_error(info, "openai")


def test_anthropic_real_client_rejecting_argument_is_library(monkeypatch):
    # Thư viện thật, tham số bị đổi tên: TypeError nảy ra lúc gọi (chưa có trả lời) → "uv sync".
    provider = real_provider("anthropic", {"text": "", "headers": SSE})
    messages_cls = type(provider._client.beta.messages)
    real_stream = messages_cls.stream

    def stream(self, *, fallbacks=None, **kwargs):
        return real_stream(self, **kwargs, khong_co_tham_so_nay=1)

    monkeypatch.setattr(messages_cls, "stream", stream)
    with pytest.raises(AIError) as info:
        generate(provider, "anthropic")
    assert_library_error(info, "anthropic")


@pytest.mark.parametrize("vendor", ["anthropic", "openai"])
def test_other_unknown_errors_still_raise(vendor):
    # Lỗi lạ không phải do đọc trả lời, không phải lệch thư viện: giữ nguyên như trước (ném ra).
    error = OSError("lỗi lạ")

    def boom(**kwargs):
        raise error

    if vendor == "anthropic":
        client = SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(stream=boom)))
        provider = AnthropicProvider(ANTHROPIC_KEY, client=client)
    else:
        provider = OpenAIProvider(OPENAI_KEY, client=SimpleNamespace(
            responses=SimpleNamespace(create=boom)
        ))  # fmt: skip
    with pytest.raises(OSError) as info:
        generate(provider, vendor)
    assert info.value is error


# =============================================== is_bad_response: chỉ lỗi trong hàm đọc trả lời


def raise_in(module, function, error):
    """Ném ``error`` từ hàm tên ``function`` như thể nằm trong module ``module``."""
    namespace = {"__name__": module, "error": error}
    exec(f"def {function}():\n    raise error\n", namespace)  # noqa: S102
    try:
        namespace[function]()
    except Exception as exc:  # noqa: BLE001
        return exc
    raise AssertionError("phải ném lỗi")


@pytest.mark.parametrize(
    ("module", "function"),
    [
        ("anthropic._base_client", "_process_response"),
        ("openai._base_client", "_process_response"),
        ("anthropic._streaming", "__stream__"),
        ("anthropic.lib.streaming._beta_messages", "accumulate_event"),
        ("google.genai.models", "_ListModelsResponse_from_mldev"),
        ("google.genai.models", "_GenerateContentResponse_from_vertex"),
        ("google.genai.types", "_from_response"),
        ("anthropic.types.beta.parsed_beta_message", "parsed_output"),
        ("openai.types.responses.response", "output_text"),
    ],
)
@pytest.mark.parametrize("error_type", [TypeError, AttributeError, KeyError, ValueError])
def test_errors_inside_reading_code_are_bad_response(module, function, error_type):
    assert is_bad_response(raise_in(module, function, error_type("x")))


@pytest.mark.parametrize(
    ("module", "function"),
    [
        ("anthropic._utils._utils", "wrapper"),  # required_args: kiểm tham số lúc gọi
        ("anthropic.resources.beta.messages.messages", "stream"),
        ("openai.resources.responses.responses", "create"),
        ("google.genai.models", "generate_content"),
        ("google.genai.models", "_GenerateContentParameters_to_mldev"),
        ("seo_app.ai.openai_provider", "_process_response"),  # không phải thư viện
        ("tests.fake", "__stream__"),
        ("anthropicx._base_client", "_process_response"),  # tên gần giống
    ],
)
@pytest.mark.parametrize("error_type", [TypeError, AttributeError, KeyError, ValueError])
def test_errors_while_calling_library_are_not_bad_response(module, function, error_type):
    assert not is_bad_response(raise_in(module, function, error_type("x")))


@pytest.mark.parametrize(
    "make_error",
    [
        lambda: json.JSONDecodeError("x", "<html>", 0),
        lambda: UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte"),
        AssertionError,
    ],
    ids=["JSONDecodeError", "UnicodeDecodeError", "AssertionError"],
)
def test_decode_errors_count_only_from_library_code(make_error):
    # Mỗi lần một lỗi mới (ném lại cùng một lỗi thì traceback cũ vẫn dính theo).
    assert is_bad_response(raise_in("anthropic.lib.streaming._beta_messages", "get", make_error()))
    assert is_bad_response(raise_in("google.genai.models", "_list", make_error()))
    # Từ client giả (test) hay code của app: giữ cách báo cũ.
    assert not is_bad_response(raise_in("tests.fake", "list", make_error()))


def test_ai_error_is_never_bad_response():
    assert not is_bad_response(raise_in("anthropic._streaming", "__stream__", AIError("x")))
    assert unreadable_error(AIError("x"), "Anthropic") is None


@pytest.mark.parametrize(
    ("error", "kind"),
    [
        (httpx.ReadTimeout("x"), "timeout"),
        (httpx2.ReadTimeout("x"), "timeout"),
        (httpx.ConnectTimeout("x"), "timeout"),
        (httpx.ReadError("x"), "network"),
        (httpx2.ReadError("x"), "network"),
        (httpx2.RemoteProtocolError("x"), "network"),
        (httpx.ProxyError("x"), "network"),
        (httpx.DecodingError("x"), "decode"),
        (httpx2.DecodingError("x"), "decode"),
        (httpx.StreamConsumed(), None),  # lỗi lập trình, không phải mạng
        (ValueError("x"), None),
        (OSError("x"), None),
    ],
)
def test_network_error_kind(error, kind):
    assert network_error_kind(error) == kind


# ======================================================= nút Kiểm tra khóa: trả lời hỏng


@pytest.mark.parametrize("vendor", ["anthropic", "openai", "gemini"])
@pytest.mark.parametrize("kind", list(GARBAGE))
def test_check_garbage_200_gives_fixed_vietnamese_message(vendor, kind):
    client = real_client(vendor, GARBAGE[kind])
    result = env_file.check_api_key(NAMES[vendor], api_key=KEYS[vendor], client=client)
    assert result.status == "unknown"
    assert result.message == bad_response_message(VENDOR[vendor])
    assert_fixed_message(result.message)


@pytest.mark.parametrize(
    ("vendor", "body"),
    [
        ("anthropic", {"data": [{"id": "claude-x", "type": "model"}], "has_more": False}),
        ("openai", {"object": "list", "data": [{"id": "gpt-x", "object": "model"}]}),
        ("gemini", {"models": [{"name": "models/gemini-x"}]}),
    ],
)
def test_check_valid_listing_is_ok(vendor, body):
    client = real_client(vendor, {"json": body})
    assert env_file.check_api_key(NAMES[vendor], api_key=KEYS[vendor], client=client).ok


@pytest.mark.parametrize(
    ("vendor", "body"),
    [
        ("anthropic", {"data": SERVER_TEXT}),
        ("anthropic", {"data": None}),
        ("openai", {"object": "list"}),
        ("openai", {"data": {"id": "x"}}),
        ("gemini", {"models": []}),
        ("gemini", {"nextPageToken": SERVER_TEXT}),
    ],
)
def test_check_listing_with_missing_field_is_strange_data(vendor, body):
    client = real_client(vendor, {"json": body})
    result = env_file.check_api_key(NAMES[vendor], api_key=KEYS[vendor], client=client)
    assert result.status == "unknown"
    assert result.message == bad_response_message(VENDOR[vendor])


def test_check_anthropic_empty_listing_is_ok():
    # Anthropic/OpenAI: thư viện giữ nguyên trường "data"; danh sách rỗng đúng dạng vẫn là trả
    # lời hợp lệ (chỉ Gemini đổi trường thiếu thành rỗng nên mới coi rỗng là lạ).
    client = real_client("anthropic", {"json": {"data": [], "has_more": False}})
    assert env_file.check_api_key("ANTHROPIC_API_KEY", api_key=ANTHROPIC_KEY, client=client).ok


@pytest.mark.parametrize("vendor", ["anthropic", "openai", "gemini"])
@pytest.mark.parametrize("error_type", [TypeError, AttributeError, ImportError])
def test_check_library_error_before_response_is_still_library(vendor, error_type):
    def boom(**kwargs):
        raise error_type("thư viện đổi")

    client = SimpleNamespace(models=SimpleNamespace(list=boom))
    result = env_file.check_api_key(NAMES[vendor], api_key=KEYS[vendor], client=client)
    label = {"anthropic": "Claude", "openai": "ChatGPT", "gemini": "Gemini"}[vendor]
    assert result.message == library_message(label)


def test_check_gemini_decoding_error_is_strange_data():
    def handler(request):
        raise httpx.DecodingError("gzip " + SERVER_TEXT)

    result = env_file.check_api_key(
        "GEMINI_API_KEY", api_key=GEMINI_KEY, client=gemini_client(handler)
    )
    assert result.message == bad_response_message("Gemini")


# ============================================= mục 3: *_CUSTOM_HEADERS bị bỏ qua, proxy giữ


EVIL_HEADERS = f"X-T028-Chen: {SERVER_TEXT}\nAuthorization: Bearer khoa-la-cua-nguoi-khac"


@pytest.fixture
def custom_headers_env(monkeypatch):
    for name in IGNORED_ENV:
        monkeypatch.setenv(name, EVIL_HEADERS)


@pytest.fixture
def recorded_headers(monkeypatch):
    """Bọc hàm tạo client của anthropic/openai: giữ nguyên tham số app truyền vào, thêm mạng giả
    ghi lại header của mọi yêu cầu. Máy chủ giả trả 400.
    """
    seen: list[httpx2.Headers] = []
    real_anthropic, real_openai = anthropic.Anthropic, openai.OpenAI

    def record(request):
        seen.append(request.headers)
        body = {"type": "error", "error": {"type": "invalid_request_error", "message": "x"}}
        return httpx2.Response(400, json=body)

    def make(real):
        def build(**kwargs):
            transport = httpx2.MockTransport(record)
            return real(**kwargs, http_client=httpx2.Client(transport=transport))

        return build

    monkeypatch.setattr(anthropic, "Anthropic", make(real_anthropic))
    monkeypatch.setattr(openai, "OpenAI", make(real_openai))
    return seen


def test_libraries_would_add_custom_headers_without_fix(custom_headers_env):
    # Chứng minh biến có tác dụng thật nếu không bỏ qua (nên các test dưới có ý nghĩa).
    assert anthropic.Anthropic(api_key=ANTHROPIC_KEY)._custom_headers.get("X-T028-Chen")
    assert openai.OpenAI(api_key=OPENAI_KEY)._custom_headers.get("X-T028-Chen")


def assert_clean(headers, key):
    assert "x-t028-chen" not in {name.lower() for name in headers}
    assert SERVER_TEXT not in str(dict(headers))
    assert "khoa-la-cua-nguoi-khac" not in str(dict(headers))
    auth = headers.get("authorization") or headers.get("x-api-key") or ""
    assert key in auth


@pytest.mark.parametrize("vendor", ["anthropic", "openai"])
def test_generate_ignores_custom_headers_env(custom_headers_env, recorded_headers, vendor):
    cls = AnthropicProvider if vendor == "anthropic" else OpenAIProvider
    with pytest.raises(AIError):
        generate(cls(KEYS[vendor]), vendor)
    assert recorded_headers
    for headers in recorded_headers:
        assert_clean(headers, KEYS[vendor])
    # Trả lại biến như cũ cho phần còn lại của máy.
    for name in IGNORED_ENV:
        assert os.environ[name] == EVIL_HEADERS


@pytest.mark.parametrize("vendor", ["anthropic", "openai"])
def test_check_ignores_custom_headers_env(custom_headers_env, recorded_headers, vendor):
    result = env_file.check_api_key(NAMES[vendor], api_key=KEYS[vendor])
    assert result.status == "unknown"
    assert len(recorded_headers) == 1
    assert_clean(recorded_headers[0], KEYS[vendor])


def test_ignoring_custom_headers_keeps_proxy_and_certificates(monkeypatch):
    kept = {
        "HTTPS_PROXY": "http://proxy.congty.test:8080",
        "HTTP_PROXY": "http://proxy.congty.test:8080",
        "NO_PROXY": "localhost",
        "SSL_CERT_FILE": "/duong/dan/chung-chi.pem",
        "SSL_CERT_DIR": "/duong/dan",
    }
    for name, value in kept.items():
        monkeypatch.setenv(name, value)
    for name in IGNORED_ENV:
        monkeypatch.setenv(name, EVIL_HEADERS)
    with ignoring_custom_headers():
        for name in IGNORED_ENV:
            assert name not in os.environ
        for name, value in kept.items():
            assert os.environ[name] == value
    for name in IGNORED_ENV:
        assert os.environ[name] == EVIL_HEADERS


def test_ignoring_custom_headers_restores_after_error(monkeypatch):
    monkeypatch.setenv("OPENAI_CUSTOM_HEADERS", EVIL_HEADERS)
    monkeypatch.delenv("ANTHROPIC_CUSTOM_HEADERS", raising=False)
    with pytest.raises(RuntimeError), ignoring_custom_headers():
        raise RuntimeError("tạo client hỏng")
    assert os.environ["OPENAI_CUSTOM_HEADERS"] == EVIL_HEADERS
    assert "ANTHROPIC_CUSTOM_HEADERS" not in os.environ
    assert not base_module._ENV_LOCK.locked()


def proxy_hosts(provider):
    """Tên máy proxy mà client (httpx2) của ``provider`` sẽ đi qua."""
    hosts = set()
    for transport in provider._client._client._mounts.values():
        url = getattr(getattr(transport, "_pool", None), "_proxy_url", None)
        if url is not None:
            hosts.add(url.host.decode())
    return hosts


def test_proxy_env_still_used_by_provider_clients(monkeypatch):
    # Mạng công ty cần proxy: client của app vẫn đi qua HTTPS_PROXY (httpx đọc lúc tạo client),
    # kể cả khi đồng thời có *_CUSTOM_HEADERS bị bỏ qua.
    for name in ("HTTPS_PROXY", "https_proxy", "ALL_PROXY", "all_proxy"):
        monkeypatch.delenv(name, raising=False)
    for name in ("NO_PROXY", "no_proxy"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("HTTPS_PROXY", "http://proxy.congty.test:8080")
    monkeypatch.setenv("https_proxy", "http://proxy.congty.test:8080")
    for name in IGNORED_ENV:
        monkeypatch.setenv(name, EVIL_HEADERS)
    for provider in (AnthropicProvider(ANTHROPIC_KEY), OpenAIProvider(OPENAI_KEY)):
        assert proxy_hosts(provider) == {"proxy.congty.test"}


@pytest.mark.parametrize("mode", ["record", "replay", "auto"])
def test_gemini_ignores_replay_env(monkeypatch, tmp_path, mode):
    monkeypatch.setenv("GOOGLE_GENAI_CLIENT_MODE", mode)
    monkeypatch.setenv("GOOGLE_GENAI_REPLAYS_DIRECTORY", str(tmp_path))
    monkeypatch.setenv("GOOGLE_GENAI_REPLAY_ID", "t028")
    # Chứng minh biến có tác dụng nếu không tắt.
    old = genai.Client(api_key=GEMINI_KEY, vertexai=False)
    assert type(old._api_client).__name__ == "ReplayApiClient"
    provider = GeminiProvider(GEMINI_KEY)
    assert type(provider._client._api_client).__name__ == "BaseApiClient"


def test_check_gemini_ignores_replay_env(monkeypatch, tmp_path):
    monkeypatch.setenv("GOOGLE_GENAI_CLIENT_MODE", "replay")
    monkeypatch.setenv("GOOGLE_GENAI_REPLAYS_DIRECTORY", str(tmp_path))
    created = {}
    real = genai.Client

    def build(**kwargs):
        created["client"] = real(**kwargs)
        return SimpleNamespace(
            models=SimpleNamespace(list=lambda **k: SimpleNamespace(page=[object()]))
        )

    monkeypatch.setattr(genai, "Client", build)
    assert env_file.check_api_key("GEMINI_API_KEY", api_key=GEMINI_KEY).ok
    assert type(created["client"]._api_client).__name__ == "BaseApiClient"
