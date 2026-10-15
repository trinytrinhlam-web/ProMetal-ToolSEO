"""T-026: 4 lỗi mức Thấp của lớp AI (Lá Chắn LC-1 → LC-4, Soi Lỗi SL-3, SL-4).

- LC-1, LC-2: thư viện của hãng lệch phiên bản (thiếu hằng/hàm, đổi tham số, đổi dạng dữ liệu),
  lúc nhập module, lúc tạo client hay lúc gọi, đều ra ``AIError`` tiếng Việt nhắc ``uv sync``.
- LC-3: lỗi 400 của cả 3 hãng chỉ hiện câu cố định + mã lỗi + tên mô hình, không chép câu máy chủ.
- LC-4: client của 3 hãng (cả nút Kiểm tra khóa) luôn gọi địa chỉ chính thức; biến môi trường
  ``OPENAI_BASE_URL``, ``ANTHROPIC_BASE_URL``, ``GOOGLE_GEMINI_BASE_URL`` không có tác dụng.

Không gọi mạng: thư viện thật chạy với mạng giả ``MockTransport`` (conftest vẫn chặn socket).
"""

import sys
from types import SimpleNamespace

import anthropic
import httpx
import httpx2
import openai
import pydantic
import pytest
from google import genai
from google.genai import errors, types

from seo_app import env_file
from seo_app.ai import AIError, AIRouter, TaskConfig, make_provider
from seo_app.ai import gemini_provider as gemini_module
from seo_app.ai.anthropic_provider import AnthropicProvider
from seo_app.ai.base import (
    ANTHROPIC_URL,
    GEMINI_URL,
    OPENAI_URL,
    bad_request_error,
    library_message,
    safe_code,
)
from seo_app.ai.gemini_provider import GeminiProvider
from seo_app.ai.openai_provider import OpenAIProvider
from seo_app.ai.registry import PROVIDERS
from seo_app.config import Settings

ANTHROPIC_KEY = "sk-ant-api03-T026KhoaGia_1234567890abcdef"
OPENAI_KEY = "sk-proj-T026KhoaGia_1234567890abcdef"
GEMINI_KEY = "AIzaSyT026KhoaGia_1234567890abcdefGH"
PLAIN_KEY = "t026khoagiakhongtiento7777"
EVIL = "https://evil.example/"

# Câu thô máy chủ có thể gửi về khi lỗi 400: có khóa không tiền tố sau dấu cách, link Markdown,
# thẻ HTML, chữ đậm. Không phần nào được hiện lên màn hình.
RAW_400 = (
    f"bad thing key={PLAIN_KEY} **xem** [bấm vào đây](https://evil.example/x) "
    "<img src=x onerror=alert(1)>"
)
RAW_PIECES = (PLAIN_KEY, "bad thing", "**", "[bấm", "](", "evil.example", "<img", "onerror")


class Answer(pydantic.BaseModel):
    text: str


def task(provider, **kwargs):
    values = {"name": "write", "provider": provider, "model": "mo-hinh-thu", "effort": "high"}
    values.update(kwargs)
    return TaskConfig(**values)


def generate(provider, vendor, **task_kwargs):
    return provider.generate(task(vendor, **task_kwargs), system="s", prompt="p", schema=Answer)


def assert_library_error(info, vendor):
    message = str(info.value)
    assert message == library_message(PROVIDERS[vendor][0])
    assert "uv sync" in message
    assert isinstance(info.value.__cause__, Exception)  # giữ lỗi gốc để tra cứu


# ============================================================== LC-1: lỗi thư viện lúc gọi


class RaisingAnthropic:
    def __init__(self, error):
        def stream(**kwargs):
            raise error

        self.beta = SimpleNamespace(messages=SimpleNamespace(stream=stream))


class RaisingOpenAI:
    def __init__(self, error):
        def create(**kwargs):
            raise error

        self.responses = SimpleNamespace(create=create)


class RaisingGemini:
    def __init__(self, error):
        def generate_content(**kwargs):
            raise error

        self.models = SimpleNamespace(generate_content=generate_content)


PROVIDER_CLASSES = {
    "anthropic": (AnthropicProvider, RaisingAnthropic, ANTHROPIC_KEY),
    "openai": (OpenAIProvider, RaisingOpenAI, OPENAI_KEY),
    "gemini": (GeminiProvider, RaisingGemini, GEMINI_KEY),
}

LIBRARY_FAILURES = [
    lambda key: AttributeError(f"module has no attribute 'stream' ({key})"),
    lambda key: TypeError(f"create() got an unexpected keyword argument 'output_format' {key}"),
    lambda key: KeyError(f"function {key}"),
    lambda key: ImportError(f"cannot import name '_parsing' {key}"),
    lambda key: ModuleNotFoundError(f"No module named 'jiter' {key}"),
]


@pytest.mark.parametrize("vendor", ["anthropic", "openai", "gemini"])
@pytest.mark.parametrize("make_error", LIBRARY_FAILURES)
def test_library_error_at_call_time_is_vietnamese(vendor, make_error):
    cls, raising, key = PROVIDER_CLASSES[vendor]
    error = make_error(key)
    with pytest.raises(AIError) as info:
        generate(cls(key, client=raising(error)), vendor)
    assert_library_error(info, vendor)
    assert info.value.__cause__ is error
    assert key not in str(info.value) and type(error).__name__ not in str(info.value)


def test_openai_helper_returning_other_shape_is_vietnamese(monkeypatch):
    # openai.pydantic_function_tool còn nhưng đổi dạng kết quả (không còn khóa "function").
    monkeypatch.setattr(openai, "pydantic_function_tool", lambda schema: {"tool": {}})
    with pytest.raises(AIError) as info:
        generate(
            OpenAIProvider(OPENAI_KEY, client=RaisingOpenAI(RuntimeError("không tới"))), "openai"
        )
    assert_library_error(info, "openai")
    assert isinstance(info.value.__cause__, KeyError)


def test_openai_helper_with_new_signature_is_vietnamese(monkeypatch):
    def changed(schema, *, required_new_arg):  # bản mới bắt buộc thêm tham số
        return {}

    monkeypatch.setattr(openai, "pydantic_function_tool", changed)
    with pytest.raises(AIError) as info:
        generate(
            OpenAIProvider(OPENAI_KEY, client=RaisingOpenAI(RuntimeError("không tới"))), "openai"
        )
    assert_library_error(info, "openai")


def _validation_error() -> pydantic.ValidationError:
    try:
        pydantic.TypeAdapter(int).validate_python("không phải số")
    except pydantic.ValidationError as exc:
        return exc
    raise AssertionError("phải ra ValidationError")


def test_gemini_config_rejected_by_library_is_vietnamese(monkeypatch):
    # google-genai không nhận trường lạ (pydantic extra="forbid"): bản mới đổi tên trường cấu
    # hình thì GenerateContentConfig(...) ra ValidationError, phải báo "uv sync".
    error = _validation_error()

    def rejecting(**kwargs):
        raise error

    monkeypatch.setattr(gemini_module.types, "GenerateContentConfig", rejecting)
    client = RaisingGemini(RuntimeError("không được gọi tới máy chủ"))
    with pytest.raises(AIError) as info:
        generate(GeminiProvider(GEMINI_KEY, client=client), "gemini")
    assert_library_error(info, "gemini")
    assert info.value.__cause__ is error


def test_gemini_missing_finish_reason_constant_at_call_time(monkeypatch):
    # Hằng mất sau khi module đã nhập (đọc lúc kiểm tra câu trả lời): vẫn ra "uv sync".
    response = SimpleNamespace(
        prompt_feedback=None,
        candidates=[SimpleNamespace(finish_reason="STOP", content=None)],
    )

    class FakeFinishReason:
        pass  # không còn MAX_TOKENS

    monkeypatch.setattr(gemini_module.types, "FinishReason", FakeFinishReason)
    client = SimpleNamespace(models=SimpleNamespace(generate_content=lambda **k: response))
    with pytest.raises(AIError) as info:
        generate(GeminiProvider(GEMINI_KEY, client=client), "gemini")
    assert_library_error(info, "gemini")


def test_gemini_wrongly_typed_json_is_strange_response_not_crash():
    # Máy chủ (hoặc proxy) trả JSON sai kiểu: thư viện ném ValidationError, báo "dữ liệu lạ".
    def handler(request):
        return httpx.Response(200, json={"usageMetadata": {"promptTokenCount": "abc"}})

    provider, _ = gemini_real(handler)
    with pytest.raises(AIError, match="dữ liệu lạ") as info:
        generate(provider, "gemini")
    assert "abc" not in str(info.value) and "validation" not in str(info.value).lower()


def test_library_errors_do_not_hide_normal_ai_errors():
    # AIError của chính provider (ví dụ AI trả sai khuôn) không bị đổi thành câu "uv sync".
    client = SimpleNamespace(
        responses=SimpleNamespace(
            create=lambda **k: SimpleNamespace(
                status="completed",
                incomplete_details=None,
                output=[
                    SimpleNamespace(
                        type="message",
                        phase=None,
                        content=[SimpleNamespace(type="output_text", text="không phải JSON")],
                    )
                ],
            )
        )
    )
    with pytest.raises(AIError, match="không đúng khuôn"):
        generate(OpenAIProvider(OPENAI_KEY, client=client), "openai")


# ======================================================= LC-2: lỗi thư viện lúc nhập / tạo client


@pytest.mark.parametrize(
    ("vendor", "module", "attr"),
    [
        ("anthropic", anthropic, "Anthropic"),
        ("openai", openai, "OpenAI"),
        ("openai", openai, "pydantic_function_tool"),
        ("gemini", types, "HttpRetryOptions"),
        ("gemini", types, "FinishReason"),
        ("gemini", types, "ThinkingLevel"),
    ],
)
def test_library_missing_name_at_import_or_build(monkeypatch, vendor, module, attr):
    provider_module = {
        "anthropic": "seo_app.ai.anthropic_provider",
        "openai": "seo_app.ai.openai_provider",
        "gemini": "seo_app.ai.gemini_provider",
    }[vendor]
    monkeypatch.delattr(module, attr)
    monkeypatch.delitem(sys.modules, provider_module)  # nhập lại với thư viện "đời khác"
    settings = Settings(
        anthropic_api_key=ANTHROPIC_KEY, openai_api_key=OPENAI_KEY, gemini_api_key=GEMINI_KEY
    )
    try:
        provider = make_provider(vendor, settings)
    except AIError as exc:
        assert str(exc) == library_message(PROVIDERS[vendor][0])
        return
    # pydantic_function_tool chỉ dùng lúc gọi: dựng được provider, gọi thì báo "uv sync".
    assert attr == "pydantic_function_tool"
    provider._client = RaisingOpenAI(RuntimeError("không tới"))
    with pytest.raises(AIError) as info:
        generate(provider, vendor)
    assert str(info.value) == library_message("OpenAI")


@pytest.mark.parametrize(
    ("vendor", "module", "attr"),
    [
        ("anthropic", anthropic, "Anthropic"),
        ("openai", openai, "OpenAI"),
        ("gemini", genai, "Client"),
    ],
)
@pytest.mark.parametrize(
    "error_factory",
    [
        lambda: TypeError("__init__() got an unexpected keyword argument 'base_url'"),
        _validation_error,
    ],
)
def test_client_rejecting_arguments_through_router(
    monkeypatch, vendor, module, attr, error_factory
):
    # Bản thư viện khác không nhận tham số tạo client (TypeError, hoặc ValidationError của
    # pydantic như google-genai): lỗi đi qua AIRouter (đường build_writer dùng), câu tiếng Việt.
    error = error_factory()

    def rejecting(**kwargs):
        raise error

    monkeypatch.setattr(module, attr, rejecting)
    settings = Settings(
        anthropic_api_key=ANTHROPIC_KEY, openai_api_key=OPENAI_KEY, gemini_api_key=GEMINI_KEY
    )
    with pytest.raises(AIError) as info:
        AIRouter({"write": task(vendor)}, settings)
    assert str(info.value) == library_message(PROVIDERS[vendor][0])
    assert info.value.__cause__ is error


def test_provider_labels_match_registry():
    from seo_app.ai import anthropic_provider, openai_provider

    assert PROVIDERS["anthropic"][0] == anthropic_provider.LABEL
    assert PROVIDERS["openai"][0] == openai_provider.LABEL
    assert PROVIDERS["gemini"][0] == gemini_module.LABEL


# ================================================ LC-1/LC-2 ở nút Kiểm tra khóa (check_api_key)

CHECK_NAMES = [
    ("ANTHROPIC_API_KEY", ANTHROPIC_KEY, "Claude"),
    ("OPENAI_API_KEY", OPENAI_KEY, "ChatGPT"),
    ("GEMINI_API_KEY", GEMINI_KEY, "Gemini"),
]
LIBRARY_MODULE = {
    "ANTHROPIC_API_KEY": "anthropic",
    "OPENAI_API_KEY": "openai",
    "GEMINI_API_KEY": "google.genai",
}


@pytest.mark.parametrize(("name", "key", "label"), CHECK_NAMES)
def test_check_library_not_importable(monkeypatch, name, key, label):
    monkeypatch.setitem(sys.modules, LIBRARY_MODULE[name], None)  # nhập là ImportError
    result = env_file.check_api_key(name, api_key=key)
    assert result.status == "unknown"
    assert result.message == library_message(label)


@pytest.mark.parametrize(
    ("name", "key", "label", "module", "attr"),
    [
        ("ANTHROPIC_API_KEY", ANTHROPIC_KEY, "Claude", anthropic, "Anthropic"),
        ("OPENAI_API_KEY", OPENAI_KEY, "ChatGPT", openai, "OpenAI"),
        ("GEMINI_API_KEY", GEMINI_KEY, "Gemini", genai, "Client"),
    ],
)
@pytest.mark.parametrize(
    "error_factory", [lambda: TypeError("unexpected keyword 'base_url'"), _validation_error]
)
def test_check_client_rejecting_arguments(
    monkeypatch, name, key, label, module, attr, error_factory
):
    error = error_factory()

    def rejecting(**kwargs):
        raise error

    monkeypatch.setattr(module, attr, rejecting)
    result = env_file.check_api_key(name, api_key=key)
    assert result.status == "unknown"
    assert result.message == library_message(label)


@pytest.mark.parametrize(("name", "key", "label"), CHECK_NAMES)
@pytest.mark.parametrize("error_type", [AttributeError, TypeError, ImportError])
def test_check_library_error_at_call_time(name, key, label, error_type):
    error = error_type(f"thư viện đổi, khóa {key}")
    client = SimpleNamespace(models=SimpleNamespace(list=lambda **k: (_ for _ in ()).throw(error)))
    result = env_file.check_api_key(name, api_key=key, client=client)
    assert result.status == "unknown"
    assert result.message == library_message(label)
    assert key not in result.message


def test_check_anthropic_other_exception_only_names_it():
    # Trước T-026 Claude chỉ bắt AnthropicError: lỗi lạ khác lọt ra làm sập nút Kiểm tra.
    error = ValueError(f"lỗi lạ {ANTHROPIC_KEY}")
    client = SimpleNamespace(models=SimpleNamespace(list=lambda **k: (_ for _ in ()).throw(error)))
    result = env_file.check_api_key("ANTHROPIC_API_KEY", api_key=ANTHROPIC_KEY, client=client)
    assert result.status == "unknown"
    assert result.message == "Lỗi khi kiểm tra khóa (ValueError)."


# =================================================================== LC-3: lỗi 400 câu cố định


def anthropic_real(handler, key=ANTHROPIC_KEY):
    seen: list = []

    def record(request):
        seen.append(request)
        return handler(request)

    client = anthropic.Anthropic(
        api_key=key,
        max_retries=0,
        http_client=httpx2.Client(transport=httpx2.MockTransport(record)),
    )
    return AnthropicProvider(key, client=client), seen


def openai_real(handler):
    seen: list = []

    def record(request):
        seen.append(request)
        return handler(request)

    client = openai.OpenAI(
        api_key=OPENAI_KEY,
        max_retries=0,
        http_client=httpx2.Client(transport=httpx2.MockTransport(record)),
    )
    return OpenAIProvider(OPENAI_KEY, client=client), seen


def gemini_real(handler):
    seen: list = []

    def record(request):
        seen.append(request)
        return handler(request)

    client = genai.Client(
        api_key=GEMINI_KEY,
        vertexai=False,
        http_options=types.HttpOptions(
            retry_options=types.HttpRetryOptions(attempts=1),
            client_args={"transport": httpx.MockTransport(record)},
        ),
    )
    return GeminiProvider(GEMINI_KEY, client=client), seen


def anthropic_400(message, err_type="invalid_request_error"):
    body = {"type": "error", "error": {"type": err_type, "message": message}}
    return httpx2.Response(400, json=body)


def openai_400(message, code=None, param=None):
    error = {"message": message, "type": "invalid_request_error", "code": code, "param": param}
    return httpx2.Response(400, json={"error": error})


def gemini_400(message, status="INVALID_ARGUMENT"):
    return httpx.Response(400, json={"error": {"code": 400, "message": message, "status": status}})


ADVICE = (
    "Kiểm tra tên mô hình và các thông số (max_tokens, effort, web_search) của việc «write» "
    "trong config/ai.toml rồi thử lại."
)


def assert_no_raw_text(message):
    for piece in RAW_PIECES:
        assert piece not in message, piece


def test_anthropic_400_shows_only_fixed_sentence():
    provider, _ = anthropic_real(lambda r: anthropic_400(RAW_400))
    with pytest.raises(AIError) as info:
        generate(provider, "anthropic")
    message = str(info.value)
    assert message == (
        "Anthropic không nhận yêu cầu (lỗi 400; mã invalid_request_error) với mô hình "
        f"«mo-hinh-thu». {ADVICE}"
    )
    assert_no_raw_text(message)


def test_anthropic_400_credit_message_still_recognised():
    provider, _ = anthropic_real(
        lambda r: anthropic_400("Your credit balance is too low to access the API.")
    )
    with pytest.raises(AIError, match="hết tiền"):
        generate(provider, "anthropic")


def test_openai_400_shows_only_fixed_sentence_with_code_and_param():
    provider, seen = openai_real(
        lambda r: openai_400(RAW_400, "invalid_value", "max_output_tokens")
    )
    with pytest.raises(AIError) as info:
        generate(provider, "openai")
    message = str(info.value)
    assert message == (
        "OpenAI không nhận yêu cầu (lỗi 400; mã invalid_value, tham số max_output_tokens) với "
        f"mô hình «mo-hinh-thu». {ADVICE}"
    )
    assert_no_raw_text(message)
    assert len(seen) == 1  # lỗi 400 khác reasoning: không gọi lại


def test_openai_400_reasoning_retry_still_works_and_final_error_is_fixed():
    response = openai_400(f"reasoning not supported {RAW_400}", None, "reasoning.effort")
    provider, seen = openai_real(lambda r: response)
    with pytest.raises(AIError) as info:
        generate(provider, "openai")
    assert len(seen) == 2
    assert "tham số reasoning.effort" in str(info.value)
    assert_no_raw_text(str(info.value))


def test_gemini_400_shows_only_fixed_sentence():
    provider, _ = gemini_real(lambda r: gemini_400(RAW_400))
    with pytest.raises(AIError) as info:
        generate(provider, "gemini")
    message = str(info.value)
    assert message == (
        "Gemini không nhận yêu cầu (lỗi 400; mã INVALID_ARGUMENT) với mô hình «mo-hinh-thu». "
        f"{ADVICE}"
    )
    assert_no_raw_text(message)


def test_gemini_known_400_gets_written_hint_not_server_text():
    raw = f"User location is not supported for the API use. key={PLAIN_KEY} [x](https://e.x)"
    provider, _ = gemini_real(lambda r: gemini_400(raw, "FAILED_PRECONDITION"))
    with pytest.raises(AIError) as info:
        generate(provider, "gemini")
    message = str(info.value)
    assert message.startswith(
        "Gemini không nhận yêu cầu (lỗi 400; mã FAILED_PRECONDITION) với mô hình «mo-hinh-thu». "
    )
    assert message.endswith(gemini_module.KNOWN_400_HINTS[0][1])
    assert PLAIN_KEY not in message and "[x]" not in message and "for the API use" not in message


@pytest.mark.parametrize(
    "bad_code",
    [
        "[bấm](https://evil.example)",
        "sk-proj-abc123",
        f"key={PLAIN_KEY}",
        "invalid value",  # có dấu cách
        "code_with_digit_1",
        "a" * 41,
        "**đậm**",
        "<b>x</b>",
        "",
        12345,
        {"code": "x"},
        None,
    ],
)
def test_unsafe_codes_are_dropped(bad_code):
    assert safe_code(bad_code) is None
    message = str(bad_request_error("OpenAI", task("openai"), bad_code, bad_code))
    assert message == f"OpenAI không nhận yêu cầu (lỗi 400) với mô hình «mo-hinh-thu». {ADVICE}"


@pytest.mark.parametrize(
    "code", ["invalid_value", "INVALID_ARGUMENT", "reasoning.effort", "max_output_tokens"]
)
def test_safe_codes_are_kept(code):
    assert safe_code(code) == code


def test_openai_bad_code_from_server_is_dropped():
    provider, _ = openai_real(lambda r: openai_400("x", f"key {PLAIN_KEY}", "[a](https://e.x)"))
    with pytest.raises(AIError) as info:
        generate(provider, "openai")
    assert str(info.value) == (
        f"OpenAI không nhận yêu cầu (lỗi 400) với mô hình «mo-hinh-thu». {ADVICE}"
    )


# ===================================================== LC-4: địa chỉ máy chủ chính thức cố định


@pytest.fixture
def evil_base_urls(monkeypatch):
    """Phần mềm khác trên máy đặt biến môi trường đổi địa chỉ máy chủ AI."""
    for name in (
        "OPENAI_BASE_URL",
        "ANTHROPIC_BASE_URL",
        "GOOGLE_GEMINI_BASE_URL",
        "GOOGLE_VERTEX_BASE_URL",
    ):
        monkeypatch.setenv(name, EVIL)


def test_official_urls_are_https_official_hosts():
    assert httpx.URL(ANTHROPIC_URL).host == "api.anthropic.com"
    assert httpx.URL(OPENAI_URL).host == "api.openai.com"
    assert httpx.URL(GEMINI_URL).host == "generativelanguage.googleapis.com"
    for url in (ANTHROPIC_URL, OPENAI_URL, GEMINI_URL):
        assert httpx.URL(url).scheme == "https"


def test_libraries_would_follow_env_without_fixed_base_url(evil_base_urls):
    # Chứng minh biến môi trường có tác dụng thật nếu không truyền base_url (nên test dưới có
    # ý nghĩa): client tạo kiểu cũ trỏ sang máy chủ lạ.
    assert "evil.example" in str(openai.OpenAI(api_key=OPENAI_KEY).base_url)
    assert "evil.example" in str(anthropic.Anthropic(api_key=ANTHROPIC_KEY).base_url)
    old_gemini = genai.Client(api_key=GEMINI_KEY, vertexai=False)
    assert "evil.example" in str(old_gemini._api_client._http_options.base_url)


def test_providers_point_to_official_urls_despite_env(evil_base_urls):
    assert str(AnthropicProvider(ANTHROPIC_KEY)._client.base_url).rstrip("/") == ANTHROPIC_URL
    assert str(OpenAIProvider(OPENAI_KEY)._client.base_url).rstrip("/") == OPENAI_URL
    gemini = GeminiProvider(GEMINI_KEY)._client._api_client._http_options
    assert gemini.base_url == GEMINI_URL


@pytest.fixture
def capture_requests(monkeypatch):
    """Bọc hàm tạo client của 3 thư viện: giữ nguyên tham số app truyền vào, chỉ thêm mạng giả
    để ghi lại địa chỉ mà thư viện thật sẽ gọi. Máy chủ giả luôn trả 400.
    """
    seen: list[str] = []
    real_anthropic, real_openai, real_genai = anthropic.Anthropic, openai.OpenAI, genai.Client

    def record_httpx2(request):
        seen.append(str(request.url))
        body = {"type": "error", "error": {"type": "invalid_request_error", "message": "x"}}
        return httpx2.Response(400, json=body)

    def record_httpx(request):
        seen.append(str(request.url))
        return gemini_400("x")

    def make_anthropic(**kwargs):
        transport = httpx2.MockTransport(record_httpx2)
        return real_anthropic(**kwargs, http_client=httpx2.Client(transport=transport))

    def make_openai(**kwargs):
        transport = httpx2.MockTransport(record_httpx2)
        return real_openai(**kwargs, http_client=httpx2.Client(transport=transport))

    def make_genai(**kwargs):
        options = kwargs["http_options"].model_copy(
            update={
                "client_args": {"transport": httpx.MockTransport(record_httpx)},
                "retry_options": types.HttpRetryOptions(attempts=1),
            }
        )
        return real_genai(**{**kwargs, "http_options": options})

    monkeypatch.setattr(anthropic, "Anthropic", make_anthropic)
    monkeypatch.setattr(openai, "OpenAI", make_openai)
    monkeypatch.setattr(genai, "Client", make_genai)
    return seen


@pytest.mark.parametrize(
    ("vendor", "host"),
    [
        ("anthropic", "api.anthropic.com"),
        ("openai", "api.openai.com"),
        ("gemini", "generativelanguage.googleapis.com"),
    ],
)
def test_generate_calls_official_host_despite_env(evil_base_urls, capture_requests, vendor, host):
    settings = Settings(
        anthropic_api_key=ANTHROPIC_KEY, openai_api_key=OPENAI_KEY, gemini_api_key=GEMINI_KEY
    )
    provider = make_provider(vendor, settings)
    with pytest.raises(AIError, match="không nhận yêu cầu"):
        generate(provider, vendor)
    assert capture_requests, "phải có ít nhất một yêu cầu"
    for url in capture_requests:
        assert httpx.URL(url).host == host and httpx.URL(url).scheme == "https"
        assert "evil" not in url


@pytest.mark.parametrize(
    ("name", "key", "host"),
    [
        ("ANTHROPIC_API_KEY", ANTHROPIC_KEY, "api.anthropic.com"),
        ("OPENAI_API_KEY", OPENAI_KEY, "api.openai.com"),
        ("GEMINI_API_KEY", GEMINI_KEY, "generativelanguage.googleapis.com"),
    ],
)
def test_check_api_key_calls_official_host_despite_env(
    evil_base_urls, capture_requests, name, key, host
):
    result = env_file.check_api_key(name, api_key=key)
    assert result.status in ("unknown", "invalid")  # máy chủ giả trả 400
    assert key not in result.message
    assert len(capture_requests) == 1
    url = httpx.URL(capture_requests[0])
    assert url.host == host and url.scheme == "https"
    assert "evil" not in str(url)


def test_gemini_request_body_unchanged_by_fixed_url(capture_requests):
    # Đổi sang dict cho thinking_config/tools (để mọi lỗi kiểm tham số nằm ở một chỗ) không làm
    # đổi nội dung gửi đi: vẫn đúng một công cụ tìm Google và mức suy nghĩ.
    provider = GeminiProvider(GEMINI_KEY)
    with pytest.raises(AIError):
        generate(provider, "gemini", model="gemini-4-argon", web_search=True)
    assert (
        capture_requests
        and "/v1beta/models/gemini-4-argon:generateContent" in (capture_requests[0])
    )


def test_gemini_config_contents_still_correct():
    client = SimpleNamespace(calls=[])

    def generate_content(**kwargs):
        client.calls.append(kwargs)
        raise errors.ClientError(400, {"error": {"code": 400, "message": "x", "status": "X"}})

    client.models = SimpleNamespace(generate_content=generate_content)
    with pytest.raises(AIError):
        generate(GeminiProvider(GEMINI_KEY, client=client), "gemini", web_search=True)
    config = client.calls[0]["config"]
    assert isinstance(config, types.GenerateContentConfig)
    assert config.thinking_config.thinking_level == types.ThinkingLevel.HIGH
    assert len(config.tools) == 1 and config.tools[0].google_search is not None
    assert config.tools[0].function_declarations is None
    tools = [
        tool.model_dump(mode="json", exclude_none=True, by_alias=True) for tool in config.tools
    ]
    assert tools == [{"googleSearch": {}}]
