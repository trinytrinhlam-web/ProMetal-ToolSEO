"""T-034: lỗi Thấp còn lại của lớp AI và thử mù (sau T-019).

Không gọi mạng: thư viện thật chỉ chạy với ``MockTransport``.
"""

from __future__ import annotations

import gzip
import importlib
import os
import threading

import httpx2
import pytest
from test_ai_t028 import (
    BLOCK_START,
    BLOCK_STOP,
    KEYS,
    SSE,
    START,
    VENDOR,
    anthropic_stream,
    generate,
    message_end,
    real_provider,
    stainless_client,
    text_delta,
)

from seo_app import env_file
from seo_app.ai import AIError, load_ai_config
from seo_app.ai import base as base_module
from seo_app.ai.anthropic_provider import AnthropicProvider, _cut_by_token_limit
from seo_app.ai.base import (
    IGNORED_ENV,
    TokenLimitError,
    bad_response_message,
    caused_by_decoding,
    ignoring_custom_headers,
)
from seo_app.content.blind_test import Candidate, _mask_names, validate_request

NAMES = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY"}

# ================================================= SL-T019-4: Claude bị cắt vì max_tokens


def test_anthropic_cut_raises_token_limit_error_with_old_message():
    cut = START + BLOCK_START + text_delta('{"text": "bài dài') + BLOCK_STOP
    with pytest.raises(TokenLimitError) as info:
        generate(anthropic_stream(cut + message_end("max_tokens")), "anthropic", max_tokens=900)
    assert "giới hạn 900 token" in str(info.value)


@pytest.mark.parametrize("reason", ["end_turn", "refusal", None, 5])
def test_anthropic_bad_schema_not_cut_stays_plain_aierror(reason):
    # JSON sai khuôn mà không phải bị cắt: vẫn là AIError thường (không gợi ý hạ effort nhầm).
    bad = START + BLOCK_START + text_delta('{"khac": 1}') + BLOCK_STOP
    with pytest.raises(AIError) as info:
        generate(anthropic_stream(bad + message_end(reason)), "anthropic")
    assert not isinstance(info.value, TokenLimitError)


def test_anthropic_bad_schema_stream_ends_without_reason():
    bad = START + BLOCK_START + text_delta('{"text": "dở') + BLOCK_STOP
    with pytest.raises(AIError) as info:
        generate(anthropic_stream(bad), "anthropic")
    assert not isinstance(info.value, TokenLimitError)


class _Raw:
    def __init__(self, events):
        self._events = events

    def __iter__(self):
        yield from self._events


class _Broken:
    def __iter__(self):
        raise httpx2.RemoteProtocolError("đứt")


class _Stream:
    def __init__(self, raw):
        self._raw_stream = raw


def test_cut_detection_never_raises():
    assert _cut_by_token_limit(object()) is False
    assert _cut_by_token_limit(_Stream(_Broken())) is False
    assert _cut_by_token_limit(_Stream(_Raw([object()] * 100))) is False
    assert _cut_by_token_limit(_Stream(_Raw(["chuỗi", 5, None]))) is False


# ======================================= SL-T019-5: không gỡ biến khỏi os.environ, luồng khác


@pytest.fixture
def evil_env(monkeypatch):
    for name in IGNORED_ENV:
        monkeypatch.setenv(name, "X-T034: chen\nAuthorization: Bearer khoa-la")


def test_os_environ_never_changes_inside(evil_env):
    before = dict(os.environ)
    with ignoring_custom_headers():
        assert dict(os.environ) == before
        for name in ("anthropic._client", "openai._client"):
            view = importlib.import_module(name).os.environ
            assert all(n not in view for n in IGNORED_ENV)
            assert all(n not in dict(view) for n in IGNORED_ENV)
            assert view.get("PATH") == os.environ.get("PATH")
    assert dict(os.environ) == before
    for name in ("anthropic._client", "openai._client"):
        assert importlib.import_module(name).os is os


def test_clients_never_get_custom_headers(evil_env):
    provider = AnthropicProvider(KEYS["anthropic"])
    headers = {k.lower(): v for k, v in provider._client._custom_headers.items()}
    assert "x-t034" not in headers


def test_fallback_when_library_does_not_use_module_os(evil_env, monkeypatch):
    # Bản thư viện khác không đọc biến qua tên ``os`` của module: quay về gỡ biến tạm thời.
    module = importlib.import_module("anthropic._client")
    monkeypatch.setattr(module, "os", object())
    with ignoring_custom_headers():
        assert all(name not in os.environ for name in IGNORED_ENV)
    assert all(name in os.environ for name in IGNORED_ENV)


# ================================================== LC-T028-1: gọi lồng không treo


def test_nested_call_same_thread_does_not_hang(evil_env):
    done = threading.Event()

    def nested():
        with ignoring_custom_headers(), ignoring_custom_headers():
            assert base_module._ENV_LOCK.locked()
        done.set()

    thread = threading.Thread(target=nested, daemon=True)
    thread.start()
    thread.join(timeout=10)
    assert done.is_set()
    assert not base_module._ENV_LOCK.locked()
    for name in ("anthropic._client", "openai._client"):
        assert importlib.import_module(name).os is os


def test_lock_reports_held_by_other_thread():
    entered, release = threading.Event(), threading.Event()

    def hold():
        with base_module._ENV_LOCK:
            entered.set()
            release.wait(10)

    thread = threading.Thread(target=hold)
    thread.start()
    entered.wait(10)
    assert base_module._ENV_LOCK.locked()
    release.set()
    thread.join(10)
    assert not base_module._ENV_LOCK.locked()


# ==================================================== LC-T028-3: nén hỏng → "dữ liệu lạ"

GZIP_BROKEN = b"\x1f\x8b khong phai gzip " * 8


def gzip_body():
    return {
        "content": GZIP_BROKEN,
        "headers": {"content-encoding": "gzip", "content-type": "application/json"},
    }


@pytest.mark.parametrize("vendor", ["anthropic", "openai"])
def test_check_key_gzip_garbage_is_strange_data(vendor):
    client = stainless_client(vendor, lambda request: httpx2.Response(200, **gzip_body()))
    result = env_file.check_api_key(NAMES[vendor], api_key=KEYS[vendor], client=client)
    assert result.status == "unknown"
    assert result.message == bad_response_message(VENDOR[vendor])


def test_anthropic_gzip_garbage_sse_is_strange_data():
    body = {"content": GZIP_BROKEN, "headers": {**SSE, "content-encoding": "gzip"}}
    with pytest.raises(AIError) as info:
        generate(real_provider("anthropic", body), "anthropic")
    assert str(info.value) == bad_response_message("Anthropic")


@pytest.mark.parametrize("vendor", ["anthropic", "openai"])
def test_real_connection_error_still_says_no_connection(vendor):
    def refuse(request):
        raise httpx2.ConnectError("từ chối")

    client = stainless_client(vendor, refuse)
    result = env_file.check_api_key(NAMES[vendor], api_key=KEYS[vendor], client=client)
    assert result.message.startswith("Không kết nối được tới")


def test_caused_by_decoding_follows_chain_and_stops_on_cycle():
    inner = httpx2.DecodingError("gzip")
    try:
        try:
            raise inner
        except httpx2.DecodingError as exc:
            raise RuntimeError("bọc") from exc
    except RuntimeError as outer:
        assert caused_by_decoding(outer)
    a, b = ValueError("a"), ValueError("b")
    a.__cause__, b.__cause__ = b, a
    assert caused_by_decoding(a) is False
    assert gzip.compress(b"x")  # gzip thật vẫn giải được (đối chứng dữ liệu test)


# ================================================== LC-T019-1: ký tự lạ trong tên mô hình


@pytest.mark.parametrize(
    "model",
    ["[a1](https://x.y)", "a1<b>", "gpt-6.1*", "claude_`x`1", "mô-hình-1", "a1)", "gpt#6", "a1|b"],
)
def test_model_name_with_markdown_characters_rejected(model):
    with pytest.raises(AIError) as info:
        validate_request("cửa sắt", "", [Candidate("openai", model), Candidate("openai", "o3")])
    message = str(info.value)
    assert "chỉ gồm chữ không dấu" in message
    assert model not in message


# ================================================== SL-T019-3: thêm các dạng số phiên bản


@pytest.mark.parametrize(
    ("text", "leak"),
    [
        ("Tôi là Claude Sonnet 4.5.", "4.5"),
        ("Viết bởi Gemini 2.5 Flash.", "2.5"),
        ("Viết bởi Gemini 2.5 Flash.", "Flash"),
        ("ChatGPT 5 mini trả lời", "5 mini"),
        ("tôi là gpt-6.1 bản 2", "gpt"),
    ],
)
def test_more_version_forms_masked(text, leak):
    assert leak not in _mask_names(text, ["claude-opus-5-5", "gpt-6.1", "gemini-3-pro"])


def test_numbers_not_right_after_vendor_kept():
    text = "Claude viết: cửa dày 1.2 mm, rộng 3 m.\nGPT\n5.5 triệu"
    shown = _mask_names(text, ["gpt-6.1"])
    assert "1.2 mm, rộng 3 m" in shown
    assert "5.5 triệu" in shown  # khác dòng: không che


# ================================================== LC-T019-2: không lộ đường dẫn máy


def test_missing_ai_config_hides_full_path(tmp_path):
    path = tmp_path / "thu-muc-rieng" / "ai.toml"
    with pytest.raises(AIError) as info:
        load_ai_config(path)
    message = str(info.value)
    assert message == "Không thấy file cấu hình AI: config/ai.toml."
    assert str(tmp_path) not in message
    assert "thu-muc-rieng" not in message
