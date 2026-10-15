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

import anthropic
import httpx
import httpx2
import openai
import pydantic
import pytest
from google import genai
from google.genai import types

from seo_app.ai import AIError, TaskConfig
from seo_app.ai import gemini_provider as gemini_module
from seo_app.ai.anthropic_provider import AnthropicProvider
from seo_app.ai.base import bad_request_error, safe_code
from seo_app.ai.gemini_provider import GeminiProvider
from seo_app.ai.openai_provider import OpenAIProvider

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


@pytest.mark.xfail(
    strict=True,
    reason="SL-T026-1: safe_code giữ 'www.evil.com'; st.error hiện Markdown GFM nên thành link",
)
@pytest.mark.parametrize("code", ["www.evil.com", "WWW.EVIL.COM", "www.phishing.example"])
def test_safe_code_drops_www_autolink(code):
    # Streamlit hiện st.error bằng Markdown có GFM: "www.xxx.yyy" sau dấu cách tự thành link
    # bấm được (StreamlitMarkdown có literalAutolinkWww). Mã lỗi không được là một link.
    assert safe_code(code) is None


@pytest.mark.xfail(strict=True, reason="SL-T026-1: mã lỗi 'www.…' của máy chủ thành link bấm được")
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
