"""Soi Lỗi kiểm thử T-026 (Lá Chắn LC-1 → LC-4): tìm cách làm phần mới hỏng.

- LC-3: câu lỗi 400 của cả 3 hãng không phụ thuộc câu máy chủ (ký tự vô hình, Markdown, HTML,
  khóa không tiền tố, câu rất dài); mã lỗi lạ bị ``safe_code`` bỏ.
- LC-1, LC-2: thư viện đổi chữ ký hàm (``beta.messages.stream``, ``responses.create``,
  ``generate_content``), bỏ thuộc tính (``parsed_output``), đổi tên lớp lỗi.
- Gemini: cấu hình dựng bằng dict gửi đi đúng như bản cũ dựng bằng ``types.*``.
- LC-4: biến môi trường đổi địa chỉ / đổi hãng / đổi khóa không có tác dụng.

Lỗi thật tìm được để ở dạng ``xfail(strict=True)``, có ghi mã lỗi trong báo cáo
``docs/team/reports/T-026-soi-loi.md``. Không gọi mạng: thư viện thật chạy với ``MockTransport``.
"""

import json
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
from seo_app.ai import AIError, TaskConfig
from seo_app.ai import gemini_provider as gemini_module
from seo_app.ai.anthropic_provider import AnthropicProvider
from seo_app.ai.base import bad_request_error, library_message, safe_code
from seo_app.ai.gemini_provider import GeminiProvider
from seo_app.ai.openai_provider import OpenAIProvider
from seo_app.ai.registry import PROVIDERS

ANTHROPIC_KEY = "sk-ant-api03-SoiLoiT026KhoaGia_1234567890abcdef"
OPENAI_KEY = "sk-proj-SoiLoiT026KhoaGia_1234567890abcdef"
GEMINI_KEY = "AIzaSySoiLoiT026KhoaGia_1234567890abcd"
PLAIN_KEY = "soiloit026khoagiakhongtiento4242"

ADVICE = (
    "Kiểm tra tên mô hình và các thông số (max_tokens, effort, web_search) của việc «write» "
    "trong config/ai.toml rồi thử lại."
)


class Answer(pydantic.BaseModel):
    text: str


def task(provider, **kwargs):
    values = {"name": "write", "provider": provider, "model": "mo-hinh-thu", "effort": "high"}
    values.update(kwargs)
    return TaskConfig(**values)


def generate(provider, vendor, **task_kwargs):
    return provider.generate(task(vendor, **task_kwargs), system="s", prompt="p", schema=Answer)


def fixed_400(vendor_text, code_note=""):
    return (
        f"{vendor_text} không nhận yêu cầu (lỗi 400{code_note}) với mô hình «mo-hinh-thu». {ADVICE}"
    )


# --------------------------------------------------------------- thư viện thật + mạng giả


def anthropic_real(handler, key=ANTHROPIC_KEY):
    client = anthropic.Anthropic(
        api_key=key,
        max_retries=0,
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler)),
    )
    return AnthropicProvider(key, client=client)


def openai_real(handler, key=OPENAI_KEY):
    client = openai.OpenAI(
        api_key=key,
        max_retries=0,
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler)),
    )
    return OpenAIProvider(key, client=client)


def gemini_client(handler, key=GEMINI_KEY):
    return genai.Client(
        api_key=key,
        vertexai=False,
        http_options=types.HttpOptions(
            retry_options=types.HttpRetryOptions(attempts=1),
            client_args={"transport": httpx.MockTransport(handler)},
        ),
    )


def gemini_real(handler, key=GEMINI_KEY):
    return GeminiProvider(key, client=gemini_client(handler, key))


def anthropic_400(message, err_type="invalid_request_error"):
    body = {"type": "error", "error": {"type": err_type, "message": message}}
    return lambda request: httpx2.Response(400, json=body)


def openai_400(message, code=None, param=None):
    error = {"message": message, "type": "invalid_request_error", "code": code, "param": param}
    return lambda request: httpx2.Response(400, json={"error": error})


def gemini_400(message, status="INVALID_ARGUMENT", code=400):
    body = {"error": {"code": code, "message": message, "status": status}}
    return lambda request: httpx.Response(code, json=body)


def real_400(vendor, message, code=None):
    """Nhà cung cấp thật (mạng giả) trả 400 với câu ``message`` và mã ``code``."""
    if vendor == "anthropic":
        return anthropic_real(anthropic_400(message, code))
    if vendor == "openai":
        return openai_real(openai_400(message, code, code))
    return gemini_real(gemini_400(message, code))


VENDOR_TEXT = {"anthropic": "Anthropic", "openai": "OpenAI", "gemini": "Gemini"}


# ==================================================== LC-3: câu 400 không phụ thuộc câu máy chủ

# Câu thô máy chủ (hoặc proxy giả máy chủ) có thể gửi về khi lỗi 400.
NASTY_400 = {
    "khóa không tiền tố sau dấu cách": f"Request failed key={PLAIN_KEY} for project",
    "khóa sau apikey:": f"Invalid apikey: {PLAIN_KEY}",
    "link Markdown": "Xem [hướng dẫn sửa](https://evil.example/fix) ngay",
    "ảnh Markdown": "![x](https://evil.example/pixel.png)",
    "tiêu đề Markdown sau xuống dòng": "bad\n\n# Khóa của bạn đã bị lộ, bấm vào đây",
    "HTML script": "<script>alert(document.cookie)</script>",
    "HTML onerror": "<img src=x onerror=alert(1)>",
    "javascript:": "[bấm](javascript:alert(1))",
    "ký tự vô hình": "inva​lid‍ ⁠arg﻿ument",
    "đảo chiều chữ (RLO)": "‮gnp.exe‬ moc.live.www",
    "tiếng Việt có dấu": "Yêu cầu không hợp lệ: tham số sai",
    "màu chữ Streamlit": ":red[Khóa đã hết hạn] :material/warning:",
    "rất dài": "x" * 20_000 + PLAIN_KEY,
    "chuỗi rỗng": "",
}


@pytest.mark.parametrize("vendor", ["anthropic", "openai", "gemini"])
@pytest.mark.parametrize("raw", list(NASTY_400.values()), ids=list(NASTY_400))
def test_400_message_is_exactly_the_fixed_sentence(vendor, raw):
    # Mã lỗi để trống: câu hiện ra phải đúng từng chữ câu cố định, không thêm gì từ máy chủ.
    with pytest.raises(AIError) as info:
        generate(real_400(vendor, raw, None), vendor)
    assert str(info.value) == fixed_400(VENDOR_TEXT[vendor])
    assert PLAIN_KEY not in str(info.value)


@pytest.mark.parametrize("vendor", ["anthropic", "openai", "gemini"])
def test_400_message_does_not_depend_on_server_text(vendor):
    # Hai câu máy chủ khác hẳn nhau (cùng mã lỗi) cho ra đúng một câu báo: không chép gì.
    code = "INVALID_ARGUMENT" if vendor == "gemini" else "invalid_request_error"
    messages = set()
    for raw in ("Request contains an invalid argument.", NASTY_400["link Markdown"]):
        with pytest.raises(AIError) as info:
            generate(real_400(vendor, raw, code), vendor)
        messages.add(str(info.value))
    assert len(messages) == 1


# Mã lỗi lạ trong trường code/param/type/status: không có cái nào được hiện ra.
NASTY_CODES = {
    "chữ vô hình giữa mã": "INVALID​ARGUMENT",
    "BOM đầu mã": "﻿invalid_value",
    "đảo chiều chữ": "invalid‮value",
    "chữ toàn khổ": "ＩＮＶＡＬＩＤ",
    "chữ Kirin giống chữ Latinh": "іnvalid_value",  # "і" là chữ Kirin
    "Kelvin": "KEY",
    "xuống dòng cuối": "invalid_value\n",
    "tab": "invalid\tvalue",
    "dấu cách cuối": "invalid_value ",
    "41 ký tự": "a" * 41,
    "dấu chấm đầu": ".invalid",
    "dấu chấm cuối": "invalid.",
    "hai dấu nối liền": "invalid__value",
    "gạch dưới đầu": "_invalid",
    "dấu nháy ngược": "`invalid`",
    "dấu gạch đứng": "a|b",
    "màu chữ Streamlit": ":red[x]",
    "biểu tượng Streamlit": ":material/warning:",
    "gạch nối": "invalid-value",
    "khóa có số": PLAIN_KEY,
    "khóa sk-": OPENAI_KEY,
    "bytes": b"invalid_value",
    "số thực": 1.5,
    "danh sách": ["invalid_value"],
}


@pytest.mark.parametrize("code", list(NASTY_CODES.values()), ids=list(NASTY_CODES))
def test_safe_code_drops_nasty_codes(code):
    assert safe_code(code) is None
    assert str(bad_request_error("OpenAI", task("openai"), code, code)) == fixed_400("OpenAI")


@pytest.mark.parametrize("vendor", ["anthropic", "openai", "gemini"])
@pytest.mark.parametrize(
    "code",
    ["INVALID​ARGUMENT", "invalid_value\n", "ＩＮＶＡＬＩＤ", "a" * 41, f"key={PLAIN_KEY}"],
    ids=["vo-hinh", "xuong-dong", "toan-kho", "41-ky-tu", "khoa"],
)
def test_nasty_code_from_real_server_is_dropped(vendor, code):
    with pytest.raises(AIError) as info:
        generate(real_400(vendor, "x", code), vendor)
    assert str(info.value) == fixed_400(VENDOR_TEXT[vendor])


def test_safe_code_length_boundary():
    assert safe_code("a" * 40) == "a" * 40
    assert safe_code("a" * 41) is None
    assert safe_code("a.b_c") == "a.b_c"


@pytest.mark.parametrize("code", ["www.evil.com", "WWW.EVIL.COM", "www.phishing.example"])
def test_safe_code_drops_www_autolink(code):
    # Streamlit hiện st.error bằng Markdown có GFM: "www.xxx.yyy" sau dấu cách tự thành link
    # bấm được (StreamlitMarkdown có literalAutolinkWww). Mã lỗi không được là một link.
    assert safe_code(code) is None


@pytest.mark.parametrize("vendor", ["anthropic", "openai", "gemini"])
def test_400_code_from_server_cannot_become_link(vendor):
    with pytest.raises(AIError) as info:
        generate(real_400(vendor, "x", "www.evil.com"), vendor)
    assert "www." not in str(info.value).lower()


# ------------------------------------------------ Gemini: lỗi 400 đã biết (KNOWN_400_HINTS)

HINT = gemini_module.KNOWN_400_HINTS[0][1]


@pytest.mark.parametrize(
    "raw",
    [
        "User location is not supported for the API use.",
        "USER LOCATION IS NOT SUPPORTED for the API use.",
        f"[bấm](https://evil.example) user location is not supported key={PLAIN_KEY} <b>x</b>",
    ],
    ids=["chuan", "chu-hoa", "kem-chuoi-doc"],
)
def test_gemini_known_400_shows_written_hint_only(raw):
    with pytest.raises(AIError) as info:
        generate(gemini_real(gemini_400(raw, "FAILED_PRECONDITION")), "gemini")
    message = str(info.value)
    assert message == (
        "Gemini không nhận yêu cầu (lỗi 400; mã FAILED_PRECONDITION) với mô hình «mo-hinh-thu». "
        + HINT
    )
    assert "for the API use" not in message and PLAIN_KEY not in message


@pytest.mark.parametrize(
    ("code", "status"), [(403, "PERMISSION_DENIED"), (429, "RESOURCE_EXHAUSTED"), (500, "X")]
)
def test_gemini_known_phrase_on_other_codes_gives_no_hint(code, status):
    raw = "User location is not supported for the API use."
    with pytest.raises(AIError) as info:
        generate(gemini_real(gemini_400(raw, status, code)), "gemini")
    assert "VPN" not in str(info.value) and "User location" not in str(info.value)


def test_known_400_hints_are_plain_text():
    # Gợi ý viết sẵn cũng hiện bằng st.error (Markdown): không có ký tự Markdown/HTML, không link.
    for phrase, hint in gemini_module.KNOWN_400_HINTS:
        assert phrase == phrase.lower()  # so với câu máy chủ đã đổi sang chữ thường
        for bad in ("[", "]", "<", ">", "*", "`", "http", "www.", ":red", "#"):
            assert bad not in hint


# ================================ LC-1, LC-2: thư viện đổi chữ ký hàm, bỏ thuộc tính, đổi tên lỗi


def assert_library_error(info, vendor):
    assert str(info.value) == library_message(PROVIDERS[vendor][0])
    assert info.value.__cause__ is not None  # giữ lỗi gốc để tra cứu


def test_openai_responses_create_with_new_signature(monkeypatch):
    # Bản openai khác bỏ tham số "store"/"reasoning" của responses.create (thư viện thật).
    provider = openai_real(lambda request: pytest.fail("không được gọi mạng"))
    responses_cls = type(provider._client.responses)

    def create(self, *, model, input, instructions=None, max_output_tokens=None, text=None):
        pytest.fail("không được tới đây")

    monkeypatch.setattr(responses_cls, "create", create)
    with pytest.raises(AIError) as info:
        generate(provider, "openai")
    assert_library_error(info, "openai")
    assert isinstance(info.value.__cause__, TypeError)


def test_anthropic_beta_messages_stream_with_new_signature(monkeypatch):
    # Bản anthropic khác bỏ tham số "fallbacks" của beta.messages.stream (thư viện thật).
    provider = anthropic_real(lambda request: pytest.fail("không được gọi mạng"))
    messages_cls = type(provider._client.beta.messages)

    def stream(self, *, model, max_tokens, system, messages, output_format, output_config, betas):
        pytest.fail("không được tới đây")

    monkeypatch.setattr(messages_cls, "stream", stream)
    with pytest.raises(AIError) as info:
        generate(provider, "anthropic")
    assert_library_error(info, "anthropic")
    assert isinstance(info.value.__cause__, TypeError)


def test_gemini_generate_content_with_new_signature(monkeypatch):
    # Bản google-genai khác đổi tên tham số "config" của models.generate_content.
    provider = gemini_real(lambda request: pytest.fail("không được gọi mạng"))
    models_cls = type(provider._client.models)

    def generate_content(self, *, model, contents, generation_config=None):
        pytest.fail("không được tới đây")

    monkeypatch.setattr(models_cls, "generate_content", generate_content)
    with pytest.raises(AIError) as info:
        generate(provider, "gemini")
    assert_library_error(info, "gemini")
    assert isinstance(info.value.__cause__, TypeError)


class FakeStream:
    def __init__(self, message):
        self.message = message

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def get_final_message(self):
        return self.message


class StreamWithoutFinalMessage(FakeStream):
    get_final_message = None  # đổi tên hàm: gọi None → TypeError


def anthropic_fake(make_stream):
    client = SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(stream=make_stream)))
    return AnthropicProvider(ANTHROPIC_KEY, client=client)


@pytest.mark.parametrize(
    "make_stream",
    [
        # Message không còn thuộc tính parsed_output.
        lambda **kw: FakeStream(SimpleNamespace(stop_reason="end_turn", content=[])),
        # Message không còn stop_reason.
        lambda **kw: FakeStream(SimpleNamespace(parsed_output=Answer(text="x"))),
        # stream() không còn là context manager.
        lambda **kw: SimpleNamespace(get_final_message=lambda: None),
        # Đổi tên get_final_message.
        lambda **kw: StreamWithoutFinalMessage(None),
    ],
    ids=["mat-parsed_output", "mat-stop_reason", "khong-context-manager", "doi-ten-ham"],
)
def test_anthropic_shape_changes_are_library_errors(make_stream):
    with pytest.raises(AIError) as info:
        generate(anthropic_fake(make_stream), "anthropic")
    assert_library_error(info, "anthropic")


def test_openai_client_without_responses_create():
    provider = OpenAIProvider(OPENAI_KEY, client=SimpleNamespace(responses=SimpleNamespace()))
    with pytest.raises(AIError) as info:
        generate(provider, "openai")
    assert_library_error(info, "openai")
    assert isinstance(info.value.__cause__, AttributeError)


def raising_client(vendor, error):
    def boom(**kwargs):
        raise error

    if vendor == "anthropic":
        return anthropic_fake(boom)
    if vendor == "openai":
        client = SimpleNamespace(responses=SimpleNamespace(create=boom))
        return OpenAIProvider(OPENAI_KEY, client=client)
    client = SimpleNamespace(models=SimpleNamespace(generate_content=boom))
    return GeminiProvider(GEMINI_KEY, client=client)


@pytest.mark.parametrize(
    ("vendor", "module", "attr"),
    [
        ("anthropic", anthropic, "AuthenticationError"),
        ("openai", openai, "BadRequestError"),
        ("openai", openai, "AuthenticationError"),
        ("gemini", errors, "ClientError"),
        ("gemini", errors, "APIError"),
    ],
)
def test_renamed_exception_class_in_provider_is_library_error(monkeypatch, vendor, module, attr):
    # Thư viện đổi tên lớp lỗi: khi có lỗi, chính câu "except thư_viện.TênCũ" ném AttributeError.
    monkeypatch.delattr(module, attr)
    with pytest.raises(AIError) as info:
        generate(raising_client(vendor, RuntimeError("lỗi bất kỳ")), vendor)
    assert_library_error(info, vendor)
    assert isinstance(info.value.__cause__, AttributeError)


def models_list_raising(error):
    def boom(**kwargs):
        raise error

    return SimpleNamespace(models=SimpleNamespace(list=boom))


CHECK_CASES = [
    ("ANTHROPIC_API_KEY", ANTHROPIC_KEY, "Claude", anthropic, "AuthenticationError"),
    ("OPENAI_API_KEY", OPENAI_KEY, "ChatGPT", openai, "AuthenticationError"),
    ("GEMINI_API_KEY", GEMINI_KEY, "Gemini", errors, "APIError"),
]


@pytest.mark.parametrize(("name", "key", "label", "module", "attr"), CHECK_CASES)
def test_check_api_key_renamed_exception_class(monkeypatch, name, key, label, module, attr):
    # Nút Kiểm tra khóa (env_file) cũng phải ra câu "uv sync" khi thư viện lệch (phiếu T-026,
    # yêu cầu 1: "cả 3 hãng, lúc nhập thư viện lẫn lúc gọi"), không ném lỗi thô ra ngoài.
    monkeypatch.delattr(module, attr)
    result = env_file.check_api_key(name, api_key=key, client=models_list_raising(RuntimeError()))
    assert result.status == "unknown"
    assert result.message == library_message(label)


def test_app_bug_inside_generate_keeps_root_cause(monkeypatch):
    # Rủi ro 1 của Thợ Máy: lỗi kiểu Python trong code của chính app (ở đây _block của phần nội
    # dung, gọi ở đường Gemini 2 lượt) cũng bị đổi thành câu "uv sync". Ít nhất lỗi gốc phải
    # còn trong __cause__ và trang không sập (không ném lỗi thô).
    from seo_app.content import prompts

    app_bug = TypeError("lỗi trong code của app")

    def broken_block(*args, **kwargs):
        raise app_bug

    monkeypatch.setattr(prompts, "_block", broken_block)
    part = {"text": "ghi chép"}
    notes = {
        "candidates": [{"content": {"role": "model", "parts": [part]}, "finishReason": "STOP"}]
    }
    provider = gemini_real(lambda request: httpx.Response(200, json=notes))
    with pytest.raises(AIError) as info:
        generate(provider, "gemini", model="gemini-2.5-pro", web_search=True)
    assert info.value.__cause__ is app_bug


# ============================================== dữ liệu lạ từ máy chủ (mã 200, sai định dạng)


@pytest.mark.xfail(
    strict=True,
    reason="SL-T026-3: JSON sai kiểu làm google-genai ném TypeError/AttributeError → câu 'uv sync'",
)
@pytest.mark.parametrize(
    "body",
    [{"candidates": [1]}, {"candidates": [{"finishReason": 5}]}],
    ids=["candidate-la-so", "finishReason-la-so"],
)
def test_gemini_strange_json_is_not_reported_as_library_problem(body):
    provider = gemini_real(lambda request: httpx.Response(200, json=body))
    with pytest.raises(AIError) as info:
        generate(provider, "gemini")
    assert "uv sync" not in str(info.value)


@pytest.mark.parametrize(
    "body",
    [
        {"candidates": "x"},
        {"candidates": [1]},
        {"candidates": [{"content": "x"}]},
        {"candidates": [{"finishReason": 5}]},
        {"usageMetadata": "x"},
        {"promptFeedback": "x"},
        [1, 2],
        "abc",
        None,
    ],
)
def test_gemini_strange_json_never_crashes(body):
    # Dù câu báo chưa trúng (SL-T026-3), mọi dạng JSON lạ đều ra AIError, không lỗi thô.
    provider = gemini_real(lambda request: httpx.Response(200, json=body))
    with pytest.raises(AIError):
        generate(provider, "gemini")


HTML = {"content-type": "text/html"}
SSE = {"content-type": "text/event-stream"}
JSON = {"content-type": "application/json"}


@pytest.mark.parametrize(
    ("vendor", "response"),
    [
        ("anthropic", httpx2.Response(200, text="<html>Wi-Fi</html>", headers=HTML)),
        ("anthropic", httpx2.Response(200, json={"x": 1})),
        (
            "anthropic",
            httpx2.Response(200, text="event: message_start\ndata: {sai\n\n", headers=SSE),
        ),
        ("openai", httpx2.Response(200, text="{sai", headers=JSON)),
    ],
    ids=["anthropic-html", "anthropic-json-thuong", "anthropic-sse-hong", "openai-json-hong"],
)
def test_garbage_200_gives_vietnamese_error(vendor, response):
    make = anthropic_real if vendor == "anthropic" else openai_real
    with pytest.raises(AIError):
        generate(make(lambda request: response), vendor)


# ============================== Gemini: cấu hình dựng bằng dict gửi đi đúng như bản cũ (điểm 4)


def old_style_config(task_config, system, schema, search, thinking=True):
    """Cấu hình dựng đúng như code trên main trước T-026 (types.ThinkingConfig, types.Tool)."""
    config = {"system_instruction": system, "max_output_tokens": task_config.max_tokens}
    if thinking:
        level = gemini_module.THINKING_LEVELS[task_config.effort]
        config["thinking_config"] = types.ThinkingConfig(thinking_level=level)
    if schema is not None:
        config["response_mime_type"] = "application/json"
        config["response_schema"] = schema
    if search:
        config["tools"] = [types.Tool(google_search=types.GoogleSearch())]
    return types.GenerateContentConfig(**config)


def old_call(handler, **kwargs):
    # Giữ biến client tới hết lượt gọi (client bị thu dọn thì thư viện đóng kết nối).
    client = gemini_client(handler)
    return client.models.generate_content(**kwargs)


def recording(responses=()):
    """Mạng giả ghi (địa chỉ, JSON) mọi yêu cầu; trả lần lượt ``responses``, hết thì 400."""
    seen: list = []
    queue = list(responses)

    def handler(request):
        seen.append((str(request.url), json.loads(request.content)))
        if queue:
            return queue.pop(0)
        return httpx.Response(400, json={"error": {"code": 400, "message": "x", "status": "X"}})

    return handler, seen


@pytest.mark.parametrize("effort", ["low", "medium", "high", "xhigh", "max"])
@pytest.mark.parametrize("schema", [Answer, None], ids=["co-khuon", "khong-khuon"])
@pytest.mark.parametrize("search", [True, False], ids=["tim-web", "khong-tim"])
def test_gemini_request_body_same_as_before(effort, schema, search):
    t = task("gemini", effort=effort, max_tokens=12345)
    handler, new = recording()
    with pytest.raises(errors.ClientError):
        gemini_real(handler)._call(
            t, system="hệ thống", prompt="đề bài", schema=schema, search=search
        )
    handler, old = recording()
    with pytest.raises(errors.ClientError):
        old_call(
            handler,
            model=t.model,
            contents="đề bài",
            config=old_style_config(t, "hệ thống", schema, search),
        )
    assert new == old
    body = new[0][1]
    # Thư viện gửi tên trường kiểu "thinking_level" (bản cũ và mới như nhau); chỉ kiểm giá trị.
    thinking = body["generationConfig"]["thinkingConfig"]
    assert list(thinking.values()) == [gemini_module.THINKING_LEVELS[effort].value]
    assert body.get("tools", []) == ([{"googleSearch": {}}] if search else [])


def test_gemini_thinking_retry_body_same_as_before():
    # Lỗi 400 về "thinking": lượt gọi lại bỏ thinking_config, còn lại giữ nguyên như bản cũ.
    thinking_400 = httpx.Response(
        400,
        json={"error": {"code": 400, "message": "Thinking level not supported", "status": "X"}},
    )
    t = task("gemini", web_search=True)
    handler, new = recording([thinking_400])
    with pytest.raises(AIError):
        generate(gemini_real(handler), "gemini", web_search=True)
    assert len(new) == 2
    handler, old = recording()
    with pytest.raises(errors.ClientError):
        old_call(
            handler,
            model=t.model,
            contents="p",
            config=old_style_config(t, "s", Answer, True, False),
        )
    assert new[1] == old[0]
    assert "thinkingConfig" not in new[1][1]["generationConfig"]


def test_gemini_legacy_two_turn_bodies_same_as_before():
    # Gemini 2.x tìm web: lượt 1 chỉ tìm (không khuôn), lượt 2 không công cụ, có khuôn.
    notes = {
        "candidates": [
            {"content": {"role": "model", "parts": [{"text": "ghi chép"}]}, "finishReason": "STOP"}
        ]
    }
    t = task("gemini", model="gemini-2.5-pro", web_search=True)
    handler, new = recording([httpx.Response(200, json=notes)])
    with pytest.raises(AIError):
        generate(gemini_real(handler), "gemini", model="gemini-2.5-pro", web_search=True)
    assert len(new) == 2
    first, second = new[0][1], new[1][1]
    expected_first = old_style_config(t, "s", None, True)
    expected_second = old_style_config(t, "s", Answer, False)
    for body, expected, contents in (
        (first, expected_first, "p" + gemini_module.SEARCH_NOTES_PROMPT),
        (second, expected_second, None),
    ):
        handler, old = recording()
        with pytest.raises(errors.ClientError):
            old_call(
                handler,
                model=t.model,
                contents=contents or second["contents"][0]["parts"][0]["text"],
                config=expected,
            )
        assert body == old[0][1]
    assert first["tools"] == [{"googleSearch": {}}] and "tools" not in second
    assert "<du_lieu_tham_khao>" in second["contents"][0]["parts"][0]["text"]


# ============================ LC-4: biến môi trường đổi địa chỉ / đổi hãng / đổi khóa (thêm)

ENV_KEYS = {
    "OPENAI_API_KEY": "sk-proj-KhoaGiaTuBienMoiTruong_OPENAI_999",
    "ANTHROPIC_API_KEY": "sk-ant-KhoaGiaTuBienMoiTruong_ANTHROPIC_999",
    "ANTHROPIC_AUTH_TOKEN": "TokenGiaTuBienMoiTruong_ANTHROPIC_999",
    "GOOGLE_API_KEY": "AIzaSyKhoaGiaTuBienMoiTruong_GOOGLE_999",
    "GEMINI_API_KEY": "AIzaSyKhoaGiaTuBienMoiTruong_GEMINI_999",
}


@pytest.fixture
def hostile_env(monkeypatch):
    """Phần mềm khác trên máy đặt biến môi trường: đổi địa chỉ, bật Vertex AI, đặt khóa khác."""
    for name in ("OPENAI_BASE_URL", "ANTHROPIC_BASE_URL", "GOOGLE_GEMINI_BASE_URL"):
        monkeypatch.setenv(name, "http://127.0.0.1:8080/")
    monkeypatch.setenv("GOOGLE_VERTEX_BASE_URL", "https://evil.example/")
    monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "true")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "du-an-la")
    monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    for name, value in ENV_KEYS.items():
        monkeypatch.setenv(name, value)


@pytest.fixture
def capture_with_headers(monkeypatch):
    """Bọc hàm tạo client của 3 thư viện (giữ nguyên tham số app truyền), ghi địa chỉ + header."""
    seen: list = []
    real_anthropic, real_openai, real_genai = anthropic.Anthropic, openai.OpenAI, genai.Client

    def record_httpx2(request):
        seen.append((request.url, dict(request.headers)))
        body = {"type": "error", "error": {"type": "invalid_request_error", "message": "x"}}
        return httpx2.Response(400, json=body)

    def record_httpx(request):
        seen.append((request.url, dict(request.headers)))
        return httpx.Response(400, json={"error": {"code": 400, "message": "x", "status": "X"}})

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


OFFICIAL = {
    "anthropic": ("api.anthropic.com", "x-api-key", ANTHROPIC_KEY),
    "openai": ("api.openai.com", "authorization", f"Bearer {OPENAI_KEY}"),
    "gemini": ("generativelanguage.googleapis.com", "x-goog-api-key", GEMINI_KEY),
}


def assert_official_requests(seen, vendor):
    host, header, value = OFFICIAL[vendor]
    assert seen, "phải có ít nhất một yêu cầu"
    for url, headers in seen:
        assert url.scheme == "https" and url.host == host
        assert headers.get(header) == value  # đúng khóa của app, không phải khóa trong biến
        for env_value in ENV_KEYS.values():
            assert env_value not in json.dumps(headers) and env_value not in str(url)


@pytest.mark.parametrize("vendor", ["anthropic", "openai", "gemini"])
def test_generate_ignores_hostile_env(hostile_env, capture_with_headers, vendor):
    cls = {"anthropic": AnthropicProvider, "openai": OpenAIProvider, "gemini": GeminiProvider}
    provider = cls[vendor](OFFICIAL[vendor][2].removeprefix("Bearer "))
    with pytest.raises(AIError, match="không nhận yêu cầu"):
        generate(provider, vendor)
    assert_official_requests(capture_with_headers, vendor)


@pytest.mark.parametrize(
    ("vendor", "name"),
    [
        ("anthropic", "ANTHROPIC_API_KEY"),
        ("openai", "OPENAI_API_KEY"),
        ("gemini", "GEMINI_API_KEY"),
    ],
)
def test_check_api_key_ignores_hostile_env(hostile_env, capture_with_headers, vendor, name):
    key = OFFICIAL[vendor][2].removeprefix("Bearer ")
    result = env_file.check_api_key(name, api_key=key)
    assert result.status in ("unknown", "invalid")
    assert len(capture_with_headers) == 1
    assert_official_requests(capture_with_headers, vendor)


def test_gemini_client_stays_off_vertex_despite_env(hostile_env):
    api_client = GeminiProvider(GEMINI_KEY)._client._api_client
    assert api_client.vertexai is False
    assert api_client._http_options.base_url == "https://generativelanguage.googleapis.com/"


# ===================================================================== Lượt 2 (sau khi sửa)

# --- SL-T026-1: không mã nào lọt qua safe_code mà thành link được khi hiện bằng Markdown GFM

# Mã thật của 3 hãng phải giữ được (để người dùng biết sửa gì trong config/ai.toml).
REAL_CODES = [
    # OpenAI: error.code
    "invalid_value", "invalid_request_error", "context_length_exceeded", "unsupported_parameter",
    "unsupported_value", "invalid_type", "missing_required_parameter", "string_above_max_length",
    "model_not_found", "invalid_prompt", "invalid_json_schema",
    # OpenAI: error.param
    "reasoning.effort", "reasoning.summary", "max_output_tokens", "text.format",
    "text.format.schema", "text.format.name", "text.verbosity", "tools", "tool_choice", "input",
    "instructions", "model", "store", "include", "temperature",
    # Anthropic: error.type
    "authentication_error", "permission_error", "not_found_error", "request_too_large",
    "rate_limit_error", "api_error", "overloaded_error", "billing_error", "timeout_error",
    # Gemini: error.status
    "INVALID_ARGUMENT", "FAILED_PRECONDITION", "OUT_OF_RANGE", "UNAUTHENTICATED",
    "PERMISSION_DENIED", "NOT_FOUND", "RESOURCE_EXHAUSTED", "ABORTED", "CANCELLED", "INTERNAL",
    "UNAVAILABLE", "DEADLINE_EXCEEDED", "UNIMPLEMENTED", "DATA_LOSS", "UNKNOWN", "ALREADY_EXISTS",
]  # fmt: skip


@pytest.mark.parametrize("code", REAL_CODES)
def test_real_vendor_codes_are_still_kept(code):
    assert safe_code(code) == code


# GFM chỉ tự tạo link cho "www." (không phân biệt hoa thường), "http(s)://" và email. Bộ ký tự
# của safe_code không có ":", "/", "@", nên chỉ còn dạng "www." cần chặn, ở bất cứ vị trí nào.
WWW_BYPASS = [
    "WwW.evil.com", "wWw.EVIL.ru", "www.evil", "WWW.x", "a_www.evil", "invalid_www.x",
    "x.www.y", "abc.www.evil.ru", "www.a.b.c.d", "A_WWW.B_C",
]  # fmt: skip


@pytest.mark.parametrize("code", WWW_BYPASS)
def test_www_anywhere_any_case_is_dropped(code):
    assert safe_code(code) is None


@pytest.mark.parametrize(
    "code",
    ["evil.COM", "Evil.Com", "a.b.c.vn", "login.bank.io", "x_y.example", "phish.localhost"],
)
def test_domain_like_codes_with_listed_tld_are_dropped(code):
    assert safe_code(code) is None


@pytest.mark.parametrize(
    "code",
    ["xn--80ak6aa92e.com", "evil.com.", ".evil.com", "evil..com", "ev il.com", "evil.c0m"],
    ids=["punycode", "cham-cuoi", "cham-dau", "hai-cham", "dau-cach", "co-so"],
)
def test_other_domain_shapes_fail_charset(code):
    # IDN/punycode có "-" và số, dấu chấm ở đầu/cuối/liền nhau: bộ ký tự đã chặn.
    assert safe_code(code) is None


def test_no_accepted_code_can_contain_www_property():
    # Thử ngẫu nhiên (cố định hạt giống, không phụ thuộc lần chạy) trên bộ chữ dễ tạo "www.":
    # mọi mã safe_code nhận đều không chứa "www." ở bất kỳ kiểu chữ hoa/thường nào, và câu
    # báo dựng từ mã đó cũng không chứa.
    import random

    rng = random.Random(26026)
    alphabet = "wW._aE"
    accepted = 0
    for _ in range(30_000):
        code = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 14)))
        kept = safe_code(code)
        if kept is None:
            continue
        accepted += 1
        assert "www." not in kept.lower()
        message = str(bad_request_error("OpenAI", task("openai"), kept, kept))
        assert "www." not in message.lower()
    assert accepted > 1000  # phép thử có ý nghĩa: nhiều mã được nhận


# --- SL-T026-2: check_api_key với mọi lớp lỗi bị đổi tên, cả 3 hãng

RENAMED_IN_CHECK = [
    ("ANTHROPIC_API_KEY", ANTHROPIC_KEY, "Claude", anthropic, attr)
    for attr in (
        "AuthenticationError", "PermissionDeniedError", "RateLimitError", "APITimeoutError",
        "APIConnectionError", "APIStatusError", "AnthropicError",
    )
] + [
    ("OPENAI_API_KEY", OPENAI_KEY, "ChatGPT", openai, attr)
    for attr in (
        "AuthenticationError", "PermissionDeniedError", "RateLimitError", "APITimeoutError",
        "APIConnectionError", "APIStatusError",
    )
] + [
    ("GEMINI_API_KEY", GEMINI_KEY, "Gemini", errors, "APIError"),
    ("GEMINI_API_KEY", GEMINI_KEY, "Gemini", httpx, "TimeoutException"),
    ("GEMINI_API_KEY", GEMINI_KEY, "Gemini", httpx, "TransportError"),
]  # fmt: skip


@pytest.mark.parametrize(
    ("name", "key", "label", "module", "attr"),
    RENAMED_IN_CHECK,
    ids=[f"{case[2]}-{case[4]}" for case in RENAMED_IN_CHECK],
)
def test_check_every_renamed_exception_class(monkeypatch, name, key, label, module, attr):
    # Lỗi lạ (ValueError) không khớp nhánh nào nên Python tính mọi câu except, gặp lớp đã mất.
    monkeypatch.delattr(module, attr)
    error = ValueError(f"lỗi bất kỳ {key}")
    result = env_file.check_api_key(name, api_key=key, client=models_list_raising(error))
    assert result.status == "unknown"
    assert result.message == library_message(label)
    assert key not in result.message


@pytest.mark.parametrize(("name", "key", "label"), [case[:3] for case in CHECK_CASES])
@pytest.mark.parametrize("error_type", [ImportError, AttributeError, TypeError])
def test_check_library_error_types_from_call(name, key, label, error_type):
    result = env_file.check_api_key(
        name, api_key=key, client=models_list_raising(error_type(f"lỗi {key}"))
    )
    assert result.status == "unknown"
    assert result.message == library_message(label)


@pytest.mark.parametrize(("name", "key", "label"), [case[:3] for case in CHECK_CASES])
def test_check_key_error_still_only_names_it(name, key, label):
    # KeyError có thể do dữ liệu trả về lạ: chỉ nêu tên lỗi, không nhắc uv sync.
    result = env_file.check_api_key(
        name, api_key=key, client=models_list_raising(KeyError(f"lỗi {key}"))
    )
    assert result.status == "unknown"
    assert result.message == "Lỗi khi kiểm tra khóa (KeyError)."


@pytest.mark.parametrize(("name", "key", "label"), [case[:3] for case in CHECK_CASES])
def test_check_renamed_class_with_key_error_is_library_message(monkeypatch, name, key, label):
    # Thư viện đổi tên lớp lỗi + máy trả KeyError: lỗi thư viện thắng (đúng hãng).
    module, attr = {
        "Claude": (anthropic, "AuthenticationError"),
        "ChatGPT": (openai, "AuthenticationError"),
        "Gemini": (errors, "APIError"),
    }[label]
    monkeypatch.delattr(module, attr)
    result = env_file.check_api_key(name, api_key=key, client=models_list_raising(KeyError("x")))
    assert result.message == library_message(label)
