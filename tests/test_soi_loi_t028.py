"""Soi Lỗi · T-028: máy chủ AI trả mã 200 nhưng nội dung hỏng; bỏ qua ``*_CUSTOM_HEADERS``.

Bổ sung cho ``tests/test_ai_t028.py`` (của Thợ Máy), thử các trường hợp xấu hơn:

- (a) luồng SSE hỏng kiểu khác, nén gzip/br hỏng, trả lời bị cắt giữa chừng; dữ liệu hỏng
  không bao giờ ra câu "uv sync"; lỗi lệch phiên bản nảy ra sâu trong thư viện.
- (b) nút Kiểm tra khóa: danh sách mô hình đúng dạng (kể cả rỗng, có trang sau) vẫn là "dùng được".
- (c) ``ignoring_custom_headers`` khi nhiều luồng chạy cùng lúc, có ngoại lệ, giá trị Unicode.
- (d) mọi câu báo là câu cố định: không chép chữ máy chủ, không chứa khóa.

Không gọi mạng: thư viện thật chạy với ``MockTransport`` (dùng lại hàm dựng của test_ai_t028).
"""

import gzip
import json
import os
import threading
import urllib.request
from unittest import mock

import anthropic
import httpx
import httpx2
import openai
import pytest
from test_ai_t028 import (
    BLOCK_START,
    BLOCK_STOP,
    JSON_TYPE,
    KEYS,
    MESSAGE,
    NAMES,
    SERVER_TEXT,
    SSE,
    START,
    VENDOR,
    anthropic_stream,
    gemini_client,
    generate,
    message_end,
    real_client,
    real_provider,
    sse,
    stainless_client,
    text_delta,
)

from seo_app import env_file
from seo_app.ai import AIError
from seo_app.ai import base as base_module
from seo_app.ai.anthropic_provider import AnthropicProvider
from seo_app.ai.base import (
    IGNORED_ENV,
    bad_response_message,
    connection_lost_message,
    ignoring_custom_headers,
    library_message,
)
from seo_app.ai.gemini_provider import GeminiProvider
from seo_app.ai.openai_provider import OpenAIProvider
from seo_app.ai.registry import PROVIDERS

VENDORS = ["anthropic", "openai", "gemini"]
BAD_SHAPE = "AI trả về dữ liệu không đúng khuôn. Bấm thử lại."


def fixed_messages(vendor):
    """Mọi câu cố định được phép hiện khi máy chủ ``vendor`` trả thứ không đọc được."""
    name = VENDOR[vendor]
    return {
        bad_response_message(name),
        connection_lost_message(name),
        f"Không kết nối được tới {name}. Kiểm tra mạng Internet.",
        f"{name} trả lời quá lâu. Bấm thử lại.",
        BAD_SHAPE,
    }


def assert_clean(message, vendor=None):
    """Câu báo không chép chữ máy chủ, không có khóa, không phải lỗi thô, không phải "uv sync"."""
    assert SERVER_TEXT not in message
    for key in KEYS.values():
        assert key not in message
    for raw in ("Traceback", "Error", "<", "{", "line ", "char "):
        assert raw not in message
    assert "uv sync" not in message
    if vendor is not None:
        assert message != library_message(PROVIDERS[vendor][0])


# ================================================ (a) luồng SSE của Anthropic hỏng kiểu khác

OK_END = BLOCK_STOP + message_end("end_turn")


def delta(index, payload):
    return sse(
        "content_block_delta", {"type": "content_block_delta", "index": index, "delta": payload}
    )


BROKEN_STREAMS = {
    "delta-text-la-so": START + BLOCK_START + delta(0, {"type": "text_delta", "text": 5}) + OK_END,
    "delta-index-lech": START
    + BLOCK_START
    + delta(5, {"type": "text_delta", "text": "x"})
    + OK_END,
    "message_delta-thieu-usage": START
    + BLOCK_START
    + text_delta('{"text": "a"}')
    + BLOCK_STOP
    + sse("message_delta", {"type": "message_delta", "delta": {"stop_reason": "end_turn"}})
    + sse("message_stop", {"type": "message_stop"}),
    "message_delta-usage-null": START
    + BLOCK_START
    + text_delta('{"text": "a"}')
    + BLOCK_STOP
    + sse(
        "message_delta",
        {"type": "message_delta", "delta": {"stop_reason": "end_turn"}, "usage": None},
    )
    + sse("message_stop", {"type": "message_stop"}),
    "data-khong-phai-json": START + f"event: content_block_start\ndata: <html>{SERVER_TEXT}\n\n",
    "block_stop-truoc-block_start": START + OK_END,
    "block_start-thieu-content_block": START
    + sse("content_block_start", {"type": "content_block_start", "index": 0})
    + OK_END,
    "message-null": sse("message_start", {"type": "message_start", "message": None}),
    "message-content-la-so": sse(
        "message_start", {"type": "message_start", "message": {**MESSAGE, "content": 5}}
    )
    + OK_END,
    "message-thieu-content": sse(
        "message_start",
        {"type": "message_start", "message": {k: v for k, v in MESSAGE.items() if k != "content"}},
    )
    + message_end("end_turn"),
    "chi-co-ping": sse("ping", {"type": "ping"}),
    "event-error-rac": START + f"event: error\ndata: <html>{SERVER_TEXT}\n\n",
    "event-error-qua-tai": START
    + sse(
        "error", {"type": "error", "error": {"type": "overloaded_error", "message": SERVER_TEXT}}
    ),
}


@pytest.mark.parametrize("kind", list(BROKEN_STREAMS))
def test_anthropic_other_broken_streams_give_fixed_message(kind):
    with pytest.raises(AIError) as info:
        generate(anthropic_stream(BROKEN_STREAMS[kind]), "anthropic")
    assert_clean(str(info.value), "anthropic")


def test_anthropic_utf8_broken_inside_stream_is_strange_data():
    body = START.encode() + b"event: content_block_start\ndata: \xff\xfe\n\n"
    with pytest.raises(AIError) as info:
        generate(real_provider("anthropic", {"content": body, "headers": SSE}), "anthropic")
    assert str(info.value) == bad_response_message("Anthropic")


@pytest.mark.parametrize(
    "kind",
    [
        "delta-text-la-so",
        "delta-index-lech",
        "message_delta-thieu-usage",
        "data-khong-phai-json",
        "block_stop-truoc-block_start",
        "message-null",
        "message-thieu-content",
        "chi-co-ping",
    ],
)
def test_anthropic_broken_stream_is_exactly_strange_data(kind):
    with pytest.raises(AIError) as info:
        generate(anthropic_stream(BROKEN_STREAMS[kind]), "anthropic")
    assert str(info.value) == bad_response_message("Anthropic")


# ============================================ (a) nén gzip / br hỏng, trả lời bị cắt giữa chừng

GZIP_BROKEN = b"\x1f\x8b khong phai gzip " + SERVER_TEXT.encode() * 4
GZIP_CUT = gzip.compress(json.dumps({"data": [{"id": "x"}], "models": [{"name": "m"}]}).encode())[
    :15
]


def compressed(content, encoding, content_type="application/json"):
    return {
        "content": content,
        "headers": {"content-encoding": encoding, "content-type": content_type},
    }


@pytest.mark.parametrize("vendor", VENDORS)
@pytest.mark.parametrize(
    "body",
    [
        compressed(GZIP_BROKEN, "gzip"),
        compressed(GZIP_CUT, "gzip"),
        compressed(b"rac " + SERVER_TEXT.encode(), "br"),
        compressed(GZIP_BROKEN, "gzip", "text/event-stream"),
    ],
    ids=["gzip-hong", "gzip-bi-cat", "br-hong", "gzip-hong-sse"],
)
def test_broken_compression_gives_fixed_message(vendor, body):
    with pytest.raises(AIError) as info:
        generate(real_provider(vendor, body), vendor)
    message = str(info.value)
    assert_clean(message, vendor)
    assert message in fixed_messages(vendor)
    result = env_file.check_api_key(
        NAMES[vendor], api_key=KEYS[vendor], client=real_client(vendor, body)
    )
    assert result.status == "unknown"
    assert_clean(result.message, vendor)


@pytest.mark.xfail(
    strict=True,
    reason="SL-T028-3: Anthropic/OpenAI gzip hỏng (dữ liệu nén sai) ra câu 'Không kết nối được' "
    "thay vì 'dữ liệu lạ' (thư viện bọc httpx2.DecodingError thành APIConnectionError). Có sẵn "
    "trước T-028, câu cố định, chỉ gợi ý sai hướng.",
)
@pytest.mark.parametrize("vendor", ["anthropic", "openai"])
def test_gzip_garbage_is_strange_data(vendor):
    with pytest.raises(AIError) as info:
        generate(real_provider(vendor, compressed(GZIP_BROKEN, "gzip")), vendor)
    assert str(info.value) == bad_response_message(VENDOR[vendor])


class CutStream(httpx2.SyncByteStream):
    """Trả lời bị cắt: gửi nửa đầu rồi máy chủ đóng kết nối."""

    def __init__(self, first):
        self.first = first

    def __iter__(self):
        yield self.first
        raise httpx2.RemoteProtocolError("peer closed " + SERVER_TEXT)


class CutStreamX(httpx.SyncByteStream):
    def __init__(self, first):
        self.first = first

    def __iter__(self):
        yield self.first
        raise httpx.RemoteProtocolError("peer closed " + SERVER_TEXT)


def cut_client(vendor, first):
    if vendor == "gemini":
        return gemini_client(
            lambda request: httpx.Response(200, stream=CutStreamX(first), headers=JSON_TYPE)
        )
    return stainless_client(
        vendor, lambda request: httpx2.Response(200, stream=CutStream(first), headers=JSON_TYPE)
    )


@pytest.mark.parametrize("vendor", VENDORS)
def test_response_cut_off_mid_body_gives_fixed_message(vendor):
    first = b'{"output": [{"type": "mess'
    cls = {"anthropic": AnthropicProvider, "openai": OpenAIProvider, "gemini": GeminiProvider}
    provider = cls[vendor](KEYS[vendor], client=cut_client(vendor, first))
    with pytest.raises(AIError) as info:
        generate(provider, vendor)
    assert_clean(str(info.value), vendor)
    assert str(info.value) in fixed_messages(vendor)
    result = env_file.check_api_key(
        NAMES[vendor], api_key=KEYS[vendor], client=cut_client(vendor, first)
    )
    assert result.status == "unknown"
    assert_clean(result.message, vendor)


@pytest.mark.parametrize("vendor", VENDORS)
def test_truncated_json_without_network_error_is_strange_data(vendor):
    # Máy chủ đóng đúng cách nhưng JSON bị cắt (proxy cắt bớt): "dữ liệu lạ".
    body = {"text": '{"data": [{"id": "cla', "headers": JSON_TYPE}
    result = env_file.check_api_key(
        NAMES[vendor], api_key=KEYS[vendor], client=real_client(vendor, body)
    )
    assert result.message == bad_response_message(VENDOR[vendor])
    with pytest.raises(AIError) as info:
        generate(
            real_provider(vendor, {"text": '{"output": [{"type": "mess', "headers": JSON_TYPE}),
            vendor,
        )
    assert str(info.value) == bad_response_message(VENDOR[vendor])


# ============================== (a) chiều ngược: dữ liệu hỏng không bao giờ ra câu "uv sync"

STRANGE_JSON = [
    {"loi": SERVER_TEXT},
    [SERVER_TEXT],
    {"content": 5, "stop_reason": [1]},
    {"output": {"type": "message"}},
    {"output": [{"type": "message", "content": {"type": "output_text"}}]},
    {"status": {"x": 1}, "incomplete_details": 5},
    {"status": "incomplete", "incomplete_details": "max_output_tokens"},
    {"data": 5, "has_more": "x"},
    {"candidates": {"x": 1}},
    {"models": {"x": 1}},
    "chuỗi",
    5,
    True,
]


@pytest.mark.parametrize("vendor", ["anthropic", "openai"])
@pytest.mark.parametrize("body", STRANGE_JSON, ids=[f"json{i}" for i in range(len(STRANGE_JSON))])
def test_strange_json_never_reported_as_library_problem(vendor, body):
    with pytest.raises(AIError) as info:
        generate(real_provider(vendor, {"json": body}), vendor)
    assert_clean(str(info.value), vendor)
    result = env_file.check_api_key(
        NAMES[vendor], api_key=KEYS[vendor], client=real_client(vendor, {"json": body})
    )
    assert_clean(result.message, vendor)


@pytest.mark.parametrize("body", STRANGE_JSON, ids=[f"json{i}" for i in range(len(STRANGE_JSON))])
def test_gemini_check_strange_json_never_reported_as_library_problem(body):
    # Chỉ nút Kiểm tra (generate của Gemini: SL-T026-3, Chỉ Huy đã chấp nhận, ngoài phạm vi).
    client = real_client("gemini", {"json": body})
    result = env_file.check_api_key("GEMINI_API_KEY", api_key=KEYS["gemini"], client=client)
    assert_clean(result.message, "gemini")


@pytest.mark.parametrize(
    "stop_reason", [5, "ly_do_moi", None, ["end_turn"]], ids=["so", "la", "null", "danh-sach"]
)
def test_anthropic_strange_stop_reason_never_crashes(stop_reason):
    text = START + BLOCK_START + text_delta('{"text": "a"}') + BLOCK_STOP + message_end(stop_reason)
    try:
        generate(anthropic_stream(text), "anthropic")
    except AIError as exc:
        assert_clean(str(exc), "anthropic")


# ====================== (a) lỗi lệch phiên bản nảy ra sâu trong hàm đọc trả lời của thư viện


def _version_mismatch(*args, **kwargs):
    raise TypeError("got an unexpected keyword argument 'x'")


@pytest.mark.parametrize(
    ("vendor", "target"),
    [
        ("openai", "openai._models.construct_type"),
        ("anthropic", "anthropic._models.construct_type"),
        ("openai", "openai._response.APIResponse._parse"),
    ],
)
def test_deep_library_mismatch_never_crashes(vendor, target):
    # Dù nhận nhầm hay không, người dùng luôn thấy câu tiếng Việt cố định, không traceback.
    body = {"json": {"output": []}} if vendor == "openai" else {"text": START, "headers": SSE}
    with mock.patch(target, _version_mismatch), pytest.raises(AIError) as info:
        generate(real_provider(vendor, body), vendor)
    assert SERVER_TEXT not in str(info.value)


@pytest.mark.xfail(
    strict=True,
    reason="SL-T028-1: thư viện lệch phiên bản nhưng lỗi nảy ra bên trong hàm đọc trả lời "
    "(_process_response, construct_type…) bị nhận là 'dữ liệu lạ' thay vì 'uv sync' (Thợ Máy "
    "đã nêu ở rủi ro 2). Câu cố định, không lộ gì, chỉ gợi ý sai hướng.",
)
@pytest.mark.parametrize(
    ("vendor", "target"),
    [
        ("openai", "openai._models.construct_type"),
        ("anthropic", "anthropic._models.construct_type"),
    ],
)
def test_deep_library_mismatch_is_reported_as_library(vendor, target):
    body = {"json": {"output": []}} if vendor == "openai" else {"text": START, "headers": SSE}
    with mock.patch(target, _version_mismatch), pytest.raises(AIError) as info:
        generate(real_provider(vendor, body), vendor)
    assert str(info.value) == library_message(PROVIDERS[vendor][0])


# ================================================ (b) nút Kiểm tra: khóa đúng không bị báo nhầm


@pytest.mark.parametrize(
    ("vendor", "body"),
    [
        ("anthropic", {"data": [], "has_more": False, "first_id": None, "last_id": None}),
        (
            "anthropic",
            {
                "data": [
                    {
                        "id": "claude-x",
                        "type": "model",
                        "display_name": "Claude",
                        "created_at": "2026-01-01T00:00:00Z",
                    }
                ],
                "has_more": True,
                "first_id": "claude-x",
                "last_id": "claude-x",
            },
        ),
        ("openai", {"object": "list", "data": []}),
        (
            "openai",
            {
                "object": "list",
                "data": [{"id": "gpt-x", "object": "model", "created": 1, "owned_by": "openai"}],
            },
        ),
        (
            "gemini",
            {
                "models": [{"name": "models/gemini-x", "displayName": "Gemini X"}],
                "nextPageToken": "abc",
            },
        ),
        (
            "gemini",
            {
                "models": [
                    {"name": "models/gemini-x", "supportedGenerationMethods": ["generateContent"]}
                ]
            },
        ),
    ],
    ids=[
        "anthropic-rong",
        "anthropic-co-trang-sau",
        "openai-rong",
        "openai-1",
        "gemini-trang-sau",
        "gemini-1",
    ],
)
def test_check_realistic_valid_listings_are_ok(vendor, body):
    client = real_client(vendor, {"json": body, "headers": JSON_TYPE})
    result = env_file.check_api_key(NAMES[vendor], api_key=KEYS[vendor], client=client)
    assert result.ok, result.message


@pytest.mark.parametrize(
    ("vendor", "body"),
    [
        ("anthropic", {}),
        ("openai", {}),
        ("gemini", {}),
        ("gemini", {"models": []}),
        ("gemini", {"models": None}),
        ("gemini", {"models": SERVER_TEXT}),
    ],
)
def test_check_empty_or_missing_listing_is_strange_data(vendor, body):
    result = env_file.check_api_key(
        NAMES[vendor], api_key=KEYS[vendor], client=real_client(vendor, {"json": body})
    )
    assert result.status == "unknown"
    assert result.message == bad_response_message(VENDOR[vendor])


# =============================================== (c) ignoring_custom_headers và nhiều luồng

UNICODE_VALUE = "X-Tiếng-Việt: giá trị có dấu ✓ đ Đ ạ ở 𝔘\nAuthorization: Bearer " + SERVER_TEXT


@pytest.fixture
def evil_env(monkeypatch):
    for name in IGNORED_ENV:
        monkeypatch.setenv(name, UNICODE_VALUE)


def test_unicode_value_restored_exactly(evil_env):
    with ignoring_custom_headers():
        for name in IGNORED_ENV:
            assert name not in os.environ
    for name in IGNORED_ENV:
        assert os.environ[name] == UNICODE_VALUE
    assert not base_module._ENV_LOCK.locked()


@pytest.mark.parametrize("error", [KeyboardInterrupt, SystemExit, GeneratorExit, MemoryError])
def test_restored_after_base_exception(evil_env, error):
    with pytest.raises(error), ignoring_custom_headers():
        raise error()
    for name in IGNORED_ENV:
        assert os.environ[name] == UNICODE_VALUE
    assert not base_module._ENV_LOCK.locked()


def test_only_one_of_two_variables_set(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_CUSTOM_HEADERS", UNICODE_VALUE)
    monkeypatch.delenv("OPENAI_CUSTOM_HEADERS", raising=False)
    with ignoring_custom_headers():
        assert "ANTHROPIC_CUSTOM_HEADERS" not in os.environ
    assert os.environ["ANTHROPIC_CUSTOM_HEADERS"] == UNICODE_VALUE
    # Không tự thêm biến vốn không có.
    assert "OPENAI_CUSTOM_HEADERS" not in os.environ


def test_empty_value_is_restored(monkeypatch):
    for name in IGNORED_ENV:
        monkeypatch.setenv(name, "")
    with ignoring_custom_headers():
        assert all(name not in os.environ for name in IGNORED_ENV)
    assert all(os.environ[name] == "" for name in IGNORED_ENV)


def test_many_threads_creating_clients_at_once(evil_env):
    """Nhiều trang tạo client cùng lúc: không client nào nhận header lạ, biến trả lại nguyên vẹn."""
    errors: list[BaseException] = []
    clients: list[object] = []
    barrier = threading.Barrier(16)

    def work(i):
        try:
            barrier.wait()
            for _ in range(5):
                if i % 3 == 0:
                    provider = AnthropicProvider(KEYS["anthropic"])
                elif i % 3 == 1:
                    provider = OpenAIProvider(KEYS["openai"])
                else:
                    with ignoring_custom_headers():
                        pass
                    continue
                clients.append(provider._client)
        except BaseException as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=work, args=(i,)) for i in range(16)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=60)
    assert not any(thread.is_alive() for thread in threads)
    assert errors == []
    assert clients
    for client in clients:
        headers = {name.lower(): value for name, value in client._custom_headers.items()}
        assert "x-tiếng-việt" not in headers
        assert SERVER_TEXT not in json.dumps(headers, ensure_ascii=False)
    for name in IGNORED_ENV:
        assert os.environ[name] == UNICODE_VALUE
    assert not base_module._ENV_LOCK.locked()


def test_other_threads_reading_environment_never_fail(evil_env):
    """Luồng khác đọc/duyệt os.environ (như httpx tìm proxy) lúc biến đang bị gỡ: không lỗi."""
    stop = threading.Event()
    errors: list[BaseException] = []

    def remove_loop():
        while not stop.is_set():
            with ignoring_custom_headers():
                pass

    def read_loop():
        while not stop.is_set():
            try:
                urllib.request.getproxies()
                dict(os.environ)
                os.environ.get("HTTPS_PROXY")
            except BaseException as exc:  # noqa: BLE001
                errors.append(exc)

    threads = [threading.Thread(target=remove_loop) for _ in range(3)]
    threads += [threading.Thread(target=read_loop) for _ in range(3)]
    for thread in threads:
        thread.start()
    stop.wait(0.5)
    stop.set()
    for thread in threads:
        thread.join(timeout=30)
    assert errors == []
    for name in IGNORED_ENV:
        assert os.environ[name] == UNICODE_VALUE


def test_lock_released_when_client_creation_fails(evil_env, monkeypatch):
    def broken(**kwargs):
        raise TypeError("thư viện đổi")

    monkeypatch.setattr(anthropic, "Anthropic", broken)
    with pytest.raises(TypeError):
        AnthropicProvider(KEYS["anthropic"])
    assert not base_module._ENV_LOCK.locked()
    for name in IGNORED_ENV:
        assert os.environ[name] == UNICODE_VALUE
    # Nút Kiểm tra: lỗi khi tạo client ra câu "uv sync", khóa vẫn được nhả.
    result = env_file.check_api_key("ANTHROPIC_API_KEY", api_key=KEYS["anthropic"])
    assert result.message == library_message("Claude")
    assert not base_module._ENV_LOCK.locked()


@pytest.mark.xfail(
    strict=True,
    reason="SL-T028-2: OPENAI_ORG_ID / OPENAI_PROJECT_ID trong môi trường máy vẫn được thư viện "
    "openai gắn vào mọi lời gọi (header OpenAI-Organization / OpenAI-Project). Biến 'tương tự' "
    "*_CUSTOM_HEADERS chưa được bỏ qua; biến sót từ công cụ khác làm khóa đúng bị báo sai.",
)
def test_openai_org_and_project_env_ignored(monkeypatch):
    monkeypatch.setenv("OPENAI_ORG_ID", "org-" + SERVER_TEXT)
    monkeypatch.setenv("OPENAI_PROJECT_ID", "proj_" + SERVER_TEXT)
    seen: list[httpx2.Headers] = []
    real = openai.OpenAI

    def record(request):
        seen.append(request.headers)
        return httpx2.Response(200, json={"object": "list", "data": [{"id": "gpt-x"}]})

    def build(**kwargs):
        return real(**kwargs, http_client=httpx2.Client(transport=httpx2.MockTransport(record)))

    monkeypatch.setattr(openai, "OpenAI", build)
    assert env_file.check_api_key("OPENAI_API_KEY", api_key=KEYS["openai"]).ok
    assert seen
    for headers in seen:
        assert "openai-organization" not in {name.lower() for name in headers}
        assert "openai-project" not in {name.lower() for name in headers}


# ============================================== (d) câu báo cố định, không chép dữ liệu máy chủ


@pytest.mark.parametrize("vendor", VENDORS)
def test_new_messages_are_fixed_text(vendor):
    name = VENDOR[vendor]
    for message in (bad_response_message(name), connection_lost_message(name)):
        assert_clean(message)
        assert name in message
        # Chỉ ghép tên hãng viết sẵn: bỏ tên hãng ra thì câu giống hệt nhau giữa các hãng.
    assert bad_response_message("Anthropic").replace("Anthropic", "") == bad_response_message(
        "OpenAI"
    ).replace("OpenAI", "")


@pytest.mark.parametrize("vendor", ["anthropic", "openai"])
@pytest.mark.parametrize(
    "error",
    [
        lambda: httpx2.ReadError(f"{SERVER_TEXT} {KEYS['anthropic']} {KEYS['openai']}"),
        lambda: httpx2.ReadTimeout(f"{SERVER_TEXT} {KEYS['openai']}"),
        lambda: httpx2.DecodingError(f"{SERVER_TEXT} {KEYS['anthropic']}"),
    ],
    ids=["ReadError", "ReadTimeout", "DecodingError"],
)
def test_network_errors_mid_stream_never_echo_server_or_key(vendor, error):
    exc = error()

    class Broken(httpx2.SyncByteStream):
        def __iter__(self):
            yield (START if vendor == "anthropic" else '{"output": [').encode()
            raise exc

    headers = SSE if vendor == "anthropic" else JSON_TYPE
    client = stainless_client(
        vendor, lambda request: httpx2.Response(200, stream=Broken(), headers=headers)
    )
    cls = AnthropicProvider if vendor == "anthropic" else OpenAIProvider
    with pytest.raises(AIError) as info:
        generate(cls(KEYS[vendor], client=client), vendor)
    assert_clean(str(info.value), vendor)
    assert str(info.value) in fixed_messages(vendor)
