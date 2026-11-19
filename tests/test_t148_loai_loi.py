"""T-148 (Thợ Máy): loại lỗi AI (``AIError.kind``) ở cả 3 hãng, ``retry_after``, mẫu ``cfut_``.

- Lớp provider đặt ``kind`` từ mã lỗi số và trạng thái chuỗi cố định (thiết kế T-141 2.4,
  LC-T141-13); câu tiếng Việt giữ nguyên (so từng chữ với câu cũ).
- 429 có chữ thanh toán đã dùng từ trước (``billing``, ``credit``, ``prepayment``) là
  ``quota_day``; mọi 429 khác là ``rate``. Hàm đọc chi tiết lỗi 429 (QuotaFailure «PerDay»,
  RetryInfo) có test nhưng **đang tắt** bằng ``READ_QUOTA_DETAILS``.
- Câu báo không bao giờ chép chữ máy chủ (S2): dấu nhận ``MAY-CHU-T148`` không lọt ra.

Thư viện thật của từng hãng chạy với đường truyền giả (``MockTransport``), không gọi mạng.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

import anthropic
import httpx
import httpx2
import openai
import pydantic
import pytest
from google import genai
from google.genai import types

from seo_app.ai import gemini_provider
from seo_app.ai.anthropic_provider import AnthropicProvider
from seo_app.ai.base import (
    AI_ERROR_KINDS,
    MAX_RETRY_AFTER,
    AIError,
    TaskConfig,
    TokenLimitError,
    bad_request_error,
    bad_response_error,
    bad_response_message,
    redact_secrets,
    status_kind,
    token_limit_error,
)
from seo_app.ai.gemini_provider import GeminiProvider, duration_seconds, quota_details
from seo_app.ai.openai_provider import OpenAIProvider

KEY = "khoa-gia-t148"  # thư viện chỉ cần chuỗi khác rỗng; không giống khóa thật
SERVER = "MAY-CHU-T148"  # chữ máy chủ viết: không được lọt vào câu báo
MODEL = "mo-hinh-thu"
ADVICE = (
    "Kiểm tra tên mô hình và các thông số (max_tokens, effort, web_search) của việc «write» "
    "trong config/ai.toml rồi thử lại."
)


class Answer(pydantic.BaseModel):
    text: str


def task(provider: str, **kwargs) -> TaskConfig:
    values = {"name": "write", "provider": provider, "model": MODEL, "effort": "high"}
    values.update(kwargs)
    return TaskConfig(**values)


def caught(provider, vendor: str) -> AIError:
    with pytest.raises(AIError) as info:
        provider.generate(task(vendor), system="s", prompt="p", schema=Answer)
    error = info.value
    assert error.kind in AI_ERROR_KINDS
    assert SERVER not in str(error)  # S2: không chép chữ máy chủ
    return error


def bad_400(vendor: str, code: str | None = None) -> str:
    note = f"; mã {code}" if code else ""
    return f"{vendor} không nhận yêu cầu (lỗi 400{note}) với mô hình «{MODEL}». {ADVICE}"


# ============================================================ AIError, TokenLimitError, bảng mã


def test_aierror_default_kind_is_other_and_retry_after_unknown():
    error = AIError("Câu báo")
    assert (error.kind, error.retry_after, str(error)) == ("other", None, "Câu báo")


def test_kind_must_be_one_of_the_fixed_names():
    names = {
        "busy", "rate", "quota_day", "network", "timeout", "auth", "model", "bad_request",
        "shape", "refusal", "token_limit", "other",
    }  # fmt: skip
    assert names == AI_ERROR_KINDS  # đúng tên bảng T-141 2.4
    with pytest.raises(ValueError):
        AIError("x", kind="ban")


def test_token_limit_error_has_its_kind_and_old_message():
    error = token_limit_error(task("gemini", max_tokens=16000))
    assert isinstance(error, TokenLimitError) and error.kind == "token_limit"
    assert str(error) == (
        "Bài dài quá giới hạn (16000 token). Tăng max_tokens của việc «write» trong config/ai.toml."
    )
    assert TokenLimitError("x").kind == "token_limit"


@pytest.mark.parametrize(
    ("value", "expected"),
    [(0, 0.0), (13, 13.0), (1.5, 1.5), (120, 120.0), (121, 120.0), (10**9, 120.0),
     (-1, None), (float("nan"), None), (float("inf"), None), (True, None), ("13", None)],
    ids=["0", "13", "1.5", "120", "121", "rat-lon", "am", "nan", "vo-cuc", "bool", "chuoi"],
)  # fmt: skip
def test_retry_after_is_capped_at_120_seconds(value, expected):
    assert MAX_RETRY_AFTER == 120
    assert AIError("x", kind="rate", retry_after=value).retry_after == expected


@pytest.mark.parametrize(
    ("code", "kind"),
    [(500, "busy"), (502, "busy"), (503, "busy"), (504, "busy"), (529, "busy"), (429, "rate"),
     (401, "auth"), (403, "model"), (404, "model"), (400, "bad_request"), (408, "timeout"),
     (409, "other"), (501, "other"), (None, "other"), ("503", "other"), (True, "other")],
    ids=lambda v: str(v),
)  # fmt: skip
def test_status_kind_reads_only_numbers(code, kind):
    assert status_kind(code) == kind


def test_shared_builders_carry_kinds():
    assert bad_request_error("Gemini", task("gemini"), "INVALID_ARGUMENT").kind == "bad_request"
    assert bad_response_error("Gemini").kind == "shape"


# ================================================================ Gemini (thư viện thật)


def gemini(handler) -> GeminiProvider:
    client = genai.Client(
        api_key=KEY,
        vertexai=False,
        http_options=types.HttpOptions(
            retry_options=types.HttpRetryOptions(attempts=1),
            client_args={"transport": httpx.MockTransport(handler)},
        ),
    )
    return GeminiProvider(KEY, client=client)


def gemini_status(code: int, status: str | None, message: str = SERVER, details=None):
    error = {"code": code, "message": message, "status": status}
    if details is not None:
        error["details"] = details
    return lambda request: httpx.Response(code, json={"error": error})


GEMINI_RATE = "Gemini đang giới hạn số lần gọi. Đợi một phút rồi thử lại."
GEMINI_CASES = [
    (500, "INTERNAL", "busy", "Gemini báo lỗi 500. Thử lại sau ít phút."),
    (502, None, "busy", "Gemini báo lỗi 502. Thử lại sau ít phút."),
    (503, "UNAVAILABLE", "busy", "Gemini báo lỗi 503. Thử lại sau ít phút."),
    (504, "DEADLINE_EXCEEDED", "busy", "Gemini báo lỗi 504. Thử lại sau ít phút."),
    (429, "RESOURCE_EXHAUSTED", "rate", GEMINI_RATE),
    (401, "UNAUTHENTICATED", "auth", "Khóa GEMINI_API_KEY trong file .env không đúng."),
    (403, "PERMISSION_DENIED", "model", f"Tài khoản Gemini không được dùng mô hình «{MODEL}»."),
    (404, "NOT_FOUND", "model",
     f"Không có mô hình «{MODEL}». Kiểm tra lại tên trong config/ai.toml."),
    (400, "INVALID_ARGUMENT", "bad_request", bad_400("Gemini", "INVALID_ARGUMENT")),
    (408, None, "timeout", "Gemini báo lỗi 408. Thử lại sau ít phút."),
    (418, None, "other", "Gemini báo lỗi 418. Thử lại sau ít phút."),
]  # fmt: skip


@pytest.mark.parametrize(
    ("code", "status", "kind", "message"), GEMINI_CASES, ids=[str(c[0]) for c in GEMINI_CASES]
)
def test_gemini_status_codes_give_kind_and_same_message(code, status, kind, message):
    error = caught(gemini(gemini_status(code, status)), "gemini")
    assert (error.kind, str(error), error.retry_after) == (kind, message, None)


@pytest.mark.parametrize("word", ["billing", "credit", "prepayment"])
def test_gemini_429_with_billing_words_is_quota_day(word):
    handler = gemini_status(429, "RESOURCE_EXHAUSTED", f"{SERVER} please check your {word}")
    error = caught(gemini(handler), "gemini")
    assert error.kind == "quota_day"
    assert str(error) == "Tài khoản Gemini đã hết tiền hoặc hết hạn mức (quota) trong ngày."


def test_gemini_bad_key_400_is_auth():
    details = [{"@type": "type.googleapis.com/google.rpc.ErrorInfo", "reason": "API_KEY_INVALID"}]
    error = caught(gemini(gemini_status(400, "INVALID_ARGUMENT", details=details)), "gemini")
    assert (error.kind, str(error)) == ("auth", "Khóa GEMINI_API_KEY trong file .env không đúng.")


def test_gemini_status_string_without_usable_code_is_busy():
    # Mã số lạ mà trạng thái chuỗi cố định nói máy chủ bận (500, 503, 504 của Google).
    for status in ("INTERNAL", "UNAVAILABLE", "DEADLINE_EXCEEDED"):
        error = gemini_provider._api_error(
            gemini_provider.errors.ServerError(599, {"error": {"status": status}}), task("gemini")
        )
        assert error.kind == "busy", status


def raising(exc: Exception):
    def handler(request):
        raise exc

    return handler


@pytest.mark.parametrize(
    ("exc", "kind", "message"),
    [
        (httpx.ConnectError("x"), "network",
         "Không kết nối được tới Gemini. Kiểm tra mạng Internet."),
        (httpx.ReadTimeout("x"), "timeout", "Gemini trả lời quá lâu. Bấm thử lại."),
    ],
    ids=["mang", "qua-gio"],
)  # fmt: skip
def test_gemini_network_and_timeout(exc, kind, message):
    error = caught(gemini(raising(exc)), "gemini")
    assert (error.kind, str(error)) == (kind, message)


def test_gemini_html_page_is_shape():
    handler = lambda request: httpx.Response(200, text=f"<html>{SERVER}</html>")  # noqa: E731
    error = caught(gemini(handler), "gemini")
    assert error.kind == "shape" and "trả về dữ liệu lạ" in str(error)


def gm_response(text='{"text": "xong"}', finish=types.FinishReason.STOP, block=None):
    return types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(role="model", parts=[types.Part(text=text)]),
                finish_reason=finish,
            )
        ],
        prompt_feedback=(
            types.GenerateContentResponsePromptFeedback(block_reason=block) if block else None
        ),
    )


class FakeGemini:
    def __init__(self, response):
        self.response = response
        self.models = SimpleNamespace(generate_content=lambda **kwargs: self.response)


REFUSAL = "AI từ chối yêu cầu này. Thử diễn đạt lại từ khóa hoặc ghi chú."
SHAPE = "AI trả về dữ liệu không đúng khuôn. Bấm thử lại."


@pytest.mark.parametrize(
    ("response", "kind", "message"),
    [
        (gm_response(finish=types.FinishReason.SAFETY), "refusal", REFUSAL),
        (gm_response(block=types.BlockedReason.SAFETY), "refusal", REFUSAL),
        (gm_response(finish=types.FinishReason.MAX_TOKENS), "token_limit", None),
        (gm_response(text="  "), "shape", SHAPE),
        (gm_response(text="{sai"), "shape", SHAPE),
        (types.GenerateContentResponse(candidates=[]), "shape", SHAPE),
    ],
    ids=["chan", "chan-loi-dan", "max-tokens", "rong", "json-hong", "khong-ung-vien"],
)
def test_gemini_answers_that_cannot_be_used(response, kind, message):
    error = caught(GeminiProvider(KEY, client=FakeGemini(response)), "gemini")
    assert error.kind == kind
    if message is not None:
        assert str(error) == message


# ------------------------------------------------- chi tiết lỗi 429 (đang tắt, LC-T141-13)

PER_DAY = {
    "@type": "type.googleapis.com/google.rpc.QuotaFailure",
    "violations": [{"quotaMetric": "m", "quotaId": "GenerateRequestsPerDayPerProjectPerModel"}],
}
PER_MINUTE = {
    "@type": "type.googleapis.com/google.rpc.QuotaFailure",
    "violations": [{"quotaId": "GenerateRequestsPerMinutePerProjectPerModel-FreeTier"}],
}


def retry_info(delay):
    return {"@type": "type.googleapis.com/google.rpc.RetryInfo", "retryDelay": delay}


def test_reading_429_details_is_off_until_the_real_shape_is_seen():
    # Tắt tới khi Chỉ Huy chép được khuôn thật ở buổi thử (T-141 7.4.2): mọi 429 là «rate».
    assert gemini_provider.READ_QUOTA_DETAILS is False
    handler = gemini_status(429, "RESOURCE_EXHAUSTED", details=[PER_DAY, retry_info("13s")])
    error = caught(gemini(handler), "gemini")
    assert (error.kind, error.retry_after) == ("rate", None)


@pytest.mark.parametrize(
    ("details", "kind", "retry_after"),
    [
        ([PER_DAY, retry_info("13s")], "quota_day", 13.0),
        ([PER_MINUTE, retry_info("1.5s")], "rate", 1.5),
        ([retry_info("600s")], "rate", 120.0),
        ([PER_MINUTE], "rate", None),
    ],
    ids=["theo-ngay", "theo-phut", "tran-120", "khong-retry-info"],
)
def test_when_turned_on_429_details_set_kind_and_retry_after(
    monkeypatch, details, kind, retry_after
):
    monkeypatch.setattr(gemini_provider, "READ_QUOTA_DETAILS", True)
    error = caught(gemini(gemini_status(429, "RESOURCE_EXHAUSTED", details=details)), "gemini")
    assert (error.kind, error.retry_after) == (kind, retry_after)
    # Câu báo là câu đã có sẵn trong mã (không chép chữ trong chi tiết lỗi).
    assert str(error) in {
        "Gemini đang giới hạn số lần gọi. Đợi một phút rồi thử lại.",
        "Tài khoản Gemini đã hết tiền hoặc hết hạn mức (quota) trong ngày.",
    }


@pytest.mark.parametrize(
    "details",
    [None, "chuoi", [], {"error": "x"}, {"error": {"details": "x"}},
     {"error": {"details": [1, "a"]}},
     {"error": {"details": [{"@type": "type.googleapis.com/google.rpc.QuotaFailure",
                             "violations": "x"}]}},
     {"error": {"details": [{"@type": "type.googleapis.com/google.rpc.QuotaFailure",
                             "violations": [{"quotaId": 5}, "x"]}]}},
     {"error": {"details": [{"@type": "QuotaFailure", "violations": [{"quotaId": "PerDay"}]}]}}],
    ids=["none", "chuoi", "list", "error-chuoi", "details-chuoi", "phan-tu-la", "violations-chuoi",
         "quotaid-so", "type-sai"],
)  # fmt: skip
def test_quota_details_ignores_unknown_shapes(details):
    assert quota_details(details) == (False, None)


def test_quota_details_reads_wrapped_and_unwrapped_error():
    assert quota_details({"error": {"details": [PER_DAY]}}) == (True, None)
    assert quota_details({"details": [PER_DAY, retry_info("2s")]}) == (True, 2.0)
    # Đọc tối đa 20 phần tử (phòng JSON lạ rất dài).
    assert quota_details({"error": {"details": [retry_info("x")] * 20 + [PER_DAY]}}) == (
        False,
        None,
    )


@pytest.mark.parametrize(
    ("value", "seconds"),
    [("13s", 13.0), ("0.5s", 0.5), ("1.000000001s", 1.000000001), ("0s", 0.0), ("-1s", None),
     ("13", None), ("1e3s", None), (" 13s", None), (13, None), (None, None), ("13ms", None)],
    ids=["13s", "0.5s", "nano", "0s", "am", "thieu-s", "mu", "cach", "so", "none", "ms"],
)  # fmt: skip
def test_duration_seconds(value, seconds):
    assert duration_seconds(value) == seconds


# ================================================================ OpenAI (thư viện thật)


def openai_provider(handler) -> OpenAIProvider:
    client = openai.OpenAI(
        api_key=KEY,
        max_retries=0,
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler)),
    )
    return OpenAIProvider(KEY, client=client)


def openai_status(code: int, error_code: str | None = None):
    body = {"error": {"message": SERVER, "type": "x", "code": error_code, "param": None}}
    return lambda request: httpx2.Response(code, json=body)


OPENAI_CASES = [
    (401, None, "auth", "Khóa OPENAI_API_KEY trong file .env không đúng."),
    (403, None, "model", f"Tài khoản OpenAI không được dùng mô hình «{MODEL}»."),
    (404, None, "model", f"Không có mô hình «{MODEL}». Kiểm tra lại tên trong config/ai.toml."),
    (429, None, "rate", "OpenAI đang giới hạn số lần gọi. Đợi một phút rồi thử lại."),
    (429, "insufficient_quota", "quota_day",
     "Tài khoản OpenAI đã hết tiền (credit) hoặc hết hạn mức."),
    (400, None, "bad_request", bad_400("OpenAI")),
    (500, None, "busy", "OpenAI báo lỗi 500. Thử lại sau ít phút."),
    (502, None, "busy", "OpenAI báo lỗi 502. Thử lại sau ít phút."),
    (503, None, "busy", "OpenAI báo lỗi 503. Thử lại sau ít phút."),
    (504, None, "busy", "OpenAI báo lỗi 504. Thử lại sau ít phút."),
    (408, None, "timeout", "OpenAI báo lỗi 408. Thử lại sau ít phút."),
    (409, None, "other", "OpenAI báo lỗi 409. Thử lại sau ít phút."),
]  # fmt: skip


@pytest.mark.parametrize(
    ("code", "error_code", "kind", "message"),
    OPENAI_CASES,
    ids=[f"{c[0]}-{c[1] or ''}" for c in OPENAI_CASES],
)
def test_openai_status_codes_give_kind_and_same_message(code, error_code, kind, message):
    error = caught(openai_provider(openai_status(code, error_code)), "openai")
    assert (error.kind, str(error)) == (kind, message)


@pytest.mark.parametrize(
    ("exc", "kind", "message"),
    [
        (httpx2.ConnectError("x"), "network",
         "Không kết nối được tới OpenAI. Kiểm tra mạng Internet."),
        (httpx2.ReadTimeout("x"), "timeout", "OpenAI trả lời quá lâu. Bấm thử lại."),
    ],
    ids=["mang", "qua-gio"],
)  # fmt: skip
def test_openai_network_and_timeout(exc, kind, message):
    error = caught(openai_provider(raising(exc)), "openai")
    assert (error.kind, str(error)) == (kind, message)


def test_openai_html_page_is_shape():
    handler = lambda request: httpx2.Response(  # noqa: E731
        200, text=f"<html>{SERVER}</html>", headers={"content-type": "application/json"}
    )
    error = caught(openai_provider(handler), "openai")
    assert error.kind == "shape" and "trả về dữ liệu lạ" in str(error)


def oa_response(text='{"text": "xong"}', status="completed", reason=None, content=None):
    if content is None:
        content = [SimpleNamespace(type="output_text", text=text)]
    return SimpleNamespace(
        status=status,
        incomplete_details=SimpleNamespace(reason=reason) if reason else None,
        output=[SimpleNamespace(type="message", phase=None, content=content)],
    )


class FakeOpenAI:
    def __init__(self, response):
        self.responses = SimpleNamespace(create=lambda **kwargs: response)


@pytest.mark.parametrize(
    ("response", "kind", "message"),
    [
        (oa_response(content=[SimpleNamespace(type="refusal", refusal="Không")]), "refusal",
         REFUSAL),
        (oa_response(status="incomplete", reason="content_filter"), "refusal", REFUSAL),
        (oa_response(status="incomplete", reason="max_output_tokens"), "token_limit", None),
        (oa_response(status="failed"), "shape", "OpenAI chưa trả lời xong. Bấm thử lại."),
        (oa_response(status="incomplete", reason="khac"), "shape",
         "OpenAI chưa trả lời xong. Bấm thử lại."),
        (oa_response(content=[]), "shape", SHAPE),
        (oa_response(text="{sai"), "shape", SHAPE),
    ],
    ids=["tu-choi", "bo-loc", "max-tokens", "failed", "incomplete-khac", "rong", "json-hong"],
)  # fmt: skip
def test_openai_answers_that_cannot_be_used(response, kind, message):
    error = caught(OpenAIProvider(KEY, client=FakeOpenAI(response)), "openai")
    assert error.kind == kind
    if message is not None:
        assert str(error) == message


# ============================================================= Anthropic (thư viện thật)


def anthropic_provider(handler) -> AnthropicProvider:
    client = anthropic.Anthropic(
        api_key=KEY,
        max_retries=0,
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler)),
    )
    return AnthropicProvider(KEY, client=client)


def anthropic_status(code: int, message: str = SERVER):
    body = {"type": "error", "error": {"type": "invalid_request_error", "message": message}}
    return lambda request: httpx2.Response(code, json=body)


ANTHROPIC_CASES = [
    (401, SERVER, "auth", "Khóa ANTHROPIC_API_KEY trong file .env không đúng."),
    (403, SERVER, "model", f"Tài khoản Anthropic không được dùng mô hình «{MODEL}»."),
    (404, SERVER, "model", f"Không có mô hình «{MODEL}». Kiểm tra lại tên trong config/ai.toml."),
    (429, SERVER, "rate", "Anthropic đang giới hạn số lần gọi. Đợi một phút rồi thử lại."),
    (400, SERVER, "bad_request", bad_400("Anthropic", "invalid_request_error")),
    (400, f"{SERVER} Your credit balance is too low", "quota_day",
     "Tài khoản Anthropic đã hết tiền (credit)."),
    (500, SERVER, "busy", "Anthropic báo lỗi 500. Thử lại sau ít phút."),
    (502, SERVER, "busy", "Anthropic báo lỗi 502. Thử lại sau ít phút."),
    (503, SERVER, "busy", "Anthropic báo lỗi 503. Thử lại sau ít phút."),
    (504, SERVER, "busy", "Anthropic báo lỗi 504. Thử lại sau ít phút."),
    (529, SERVER, "busy", "Anthropic báo lỗi 529. Thử lại sau ít phút."),
    (408, SERVER, "timeout", "Anthropic báo lỗi 408. Thử lại sau ít phút."),
    (409, SERVER, "other", "Anthropic báo lỗi 409. Thử lại sau ít phút."),
]  # fmt: skip


@pytest.mark.parametrize(
    ("code", "server_message", "kind", "message"),
    ANTHROPIC_CASES,
    ids=[f"{c[0]}-{c[2]}" for c in ANTHROPIC_CASES],
)
def test_anthropic_status_codes_give_kind_and_same_message(code, server_message, kind, message):
    error = caught(anthropic_provider(anthropic_status(code, server_message)), "anthropic")
    assert (error.kind, str(error)) == (kind, message)


@pytest.mark.parametrize(
    ("exc", "kind"),
    [(httpx2.ConnectError("x"), "network"), (httpx2.ReadTimeout("x"), "timeout")],
    ids=["mang", "qua-gio"],
)
def test_anthropic_network_and_timeout_keep_old_message(exc, kind):
    error = caught(anthropic_provider(raising(exc)), "anthropic")
    assert error.kind == kind
    assert str(error) == "Không kết nối được tới Anthropic. Kiểm tra mạng Internet."


MESSAGE_START = "event: message_start\ndata: " + json.dumps(
    {
        "type": "message_start",
        "message": {
            "id": "msg_1", "type": "message", "role": "assistant", "model": MODEL,
            "content": [], "stop_reason": None, "stop_sequence": None,
            "usage": {"input_tokens": 1, "output_tokens": 1},
        },
    }
) + "\n\n"  # fmt: skip
LOST = "Mất kết nối tới Anthropic giữa chừng. Kiểm tra mạng Internet rồi bấm thử lại."


class BrokenStream(httpx2.SyncByteStream):
    """Trả lời đã bắt đầu (mã 200, sự kiện đầu) rồi mạng đứt: thư viện để lọt lỗi thô."""

    def __init__(self, error):
        self.error = error

    def __iter__(self):
        yield MESSAGE_START.encode()
        raise self.error


@pytest.mark.parametrize(
    ("error", "kind", "message"),
    [
        (httpx2.ReadError(SERVER), "network", LOST),
        (httpx2.RemoteProtocolError(SERVER), "network", LOST),
        (httpx2.ReadTimeout(SERVER), "timeout", "Anthropic trả lời quá lâu. Bấm thử lại."),
        (httpx2.DecodingError(SERVER), "shape", bad_response_message("Anthropic")),
    ],
    ids=["read-error", "dong-giua-chung", "qua-gio", "nen-hong"],
)
def test_anthropic_failure_while_reading_the_answer(error, kind, message):
    def handler(request):
        headers = {"content-type": "text/event-stream"}
        return httpx2.Response(200, stream=BrokenStream(error), headers=headers)

    found = caught(anthropic_provider(handler), "anthropic")
    assert (found.kind, str(found)) == (kind, message)


def test_anthropic_html_page_is_shape():
    handler = lambda request: httpx2.Response(200, text=f"<html>{SERVER}</html>")  # noqa: E731
    error = caught(anthropic_provider(handler), "anthropic")
    assert error.kind == "shape" and "trả về dữ liệu lạ" in str(error)


class FakeStream:
    def __init__(self, message):
        self.message = message

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def get_final_message(self):
        return self.message


class FakeAnthropic:
    def __init__(self, message):
        self.beta = SimpleNamespace(
            messages=SimpleNamespace(stream=lambda **kwargs: FakeStream(message))
        )


def message(stop_reason="end_turn", parsed=None):
    return SimpleNamespace(stop_reason=stop_reason, parsed_output=parsed, content=["…"])


@pytest.mark.parametrize(
    ("result", "kind", "text"),
    [
        (message("refusal"), "refusal", REFUSAL),
        (message("max_tokens"), "token_limit", None),
        (message("pause_turn"), "timeout", "AI tìm kiếm quá lâu chưa xong. Bấm thử lại."),
        (message(parsed=None), "shape", SHAPE),
    ],
    ids=["tu-choi", "max-tokens", "tim-qua-lau", "khong-khuon"],
)
def test_anthropic_answers_that_cannot_be_used(result, kind, text):
    error = caught(AnthropicProvider(KEY, client=FakeAnthropic(result)), "anthropic")
    assert error.kind == kind
    if text is not None:
        assert str(error) == text


def test_anthropic_schema_error_kinds():
    from seo_app.ai.anthropic_provider import _schema_error

    t = task("anthropic")
    assert _schema_error(t, AIError).kind == "shape"
    cut = _schema_error(t, TokenLimitError)
    assert isinstance(cut, TokenLimitError) and cut.kind == "token_limit"
    assert str(cut) == str(_schema_error(t, AIError))  # câu giữ như cũ, chỉ khác loại


# ======================================================================== cfut_ (LC-T140-2)

CFUT = "cfut_" + "T148abc_def-" * 3  # dạng token Cloudflare mới, 36 ký tự sau tiền tố


@pytest.mark.parametrize(
    "text",
    [CFUT, f"Lỗi 401: token {CFUT} hết hạn", f"x{CFUT}y", f"Authorization: Bearer {CFUT}",
     CFUT.upper(), f"url?a=1&t={CFUT}"],
    ids=["tran", "giua-cau", "dinh-chu", "bearer", "chu-hoa", "url"],
)  # fmt: skip
def test_redact_hides_cloudflare_tokens(text):
    out = redact_secrets(text)
    assert "t148abc" not in out.lower() and "[đã ẩn]" in out


def test_redact_keeps_short_cfut_words_and_plain_text():
    assert redact_secrets("cfut_ngan") == "cfut_ngan"  # dưới 20 ký tự: không phải token
    assert redact_secrets("Cửa sắt 2 cánh") == "Cửa sắt 2 cánh"
