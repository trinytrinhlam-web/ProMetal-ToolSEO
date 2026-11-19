"""T-142: client Cloudflare Workers AI (LC-T140-1 → -4, -7, -8, -18; LC-T141-9, -12).

Cloudflare giả (``tests/fake_cloudflare.py``) gắn vào phiên ``requests``; bộ chặn mạng của
``conftest`` vẫn bật: không ca nào gọi Cloudflare thật.
"""

from __future__ import annotations

import ast
import base64
import json
import threading
from pathlib import Path

import pytest
import requests

from seo_app.ai import cloudflare_images as cf
from seo_app.ai.base import AIError
from seo_app.config import load_settings
from tests.fake_cloudflare import (
    ACCOUNT,
    MA_GIA,
    RUN_URL,
    VERIFY_URL,
    FakeCloudflare,
    failed,
    json_body,
    make_session,
    ok_image,
    token_status,
)

ANH = b"\xff\xd8\xff\xe0 anh gia de thu \xff\xd9"
ROOT = Path(__file__).resolve().parents[1]


def _client(fake: FakeCloudflare, **kwargs) -> cf.CloudflareImageClient:
    return cf.CloudflareImageClient(ACCOUNT, MA_GIA, session=make_session(fake), **kwargs)


def _run(fake: FakeCloudflare, handler, prompt: str = "a rusty gate hinge") -> cf.CloudflareImage:
    fake.on("POST", RUN_URL, handler)
    return _client(fake).generate(prompt)


def _error(fake: FakeCloudflare, handler) -> cf.CloudflareImageError:
    with pytest.raises(cf.CloudflareImageError) as info:
        _run(fake, handler)
    return info.value


# ------------------------------------------------------------------ đường gọi cố định


def test_generate_sends_exactly_two_fields_to_the_fixed_route():
    fake = FakeCloudflare()
    fake.on("POST", RUN_URL, ok_image(ANH))
    session = make_session(fake)
    sent: dict = {}
    original = session.request

    def recording(*args, **kwargs):
        sent.update(kwargs)
        return original(*args, **kwargs)

    session.request = recording
    image = cf.CloudflareImageClient(ACCOUNT, MA_GIA, session=session).generate(
        "a rusty gate hinge"
    )
    # Từng lớp được nối đúng (như LC-T120-18), không chỉ «có nhập».
    assert sent["allow_redirects"] is False
    assert sent["stream"] is True
    assert sent["timeout"] == 60
    assert sent["hooks"] == {"response": [cf._refuse_redirect]}
    assert isinstance(sent["auth"], cf._Bearer)
    assert "params" not in sent and "headers" not in sent
    assert image.data == ANH
    assert (image.model, image.steps, image.prompt) == (cf.FLUX_SCHNELL, 4, "a rusty gate hinge")
    [(request, kwargs)] = fake.calls
    assert request.method == "POST"
    assert request.url == RUN_URL  # không query, đúng máy chủ, đúng đường
    assert json_body(request) == {"prompt": "a rusty gate hinge", "steps": 4}
    assert request.headers["Authorization"] == f"Bearer {MA_GIA}"
    assert request.headers["Content-Type"] == "application/json"
    custom = {name.lower() for name in request.headers} - {
        name.lower() for name in requests.utils.default_headers()
    }
    assert custom == {"authorization", "content-type", "content-length"}
    assert kwargs["timeout"] == 60
    assert kwargs["stream"] is True


def test_session_never_follows_redirects_and_never_retries_by_itself():
    client = cf.CloudflareImageClient(ACCOUNT, MA_GIA)
    assert client._session.max_redirects == 0
    adapter = client._session.get_adapter(RUN_URL)
    assert adapter.max_retries.total == 0  # LC-T140-7: không tự thử lại lệnh tạo ảnh


def test_given_session_is_also_locked_against_redirects():
    session = requests.Session()
    cf.CloudflareImageClient(ACCOUNT, MA_GIA, session=session)
    assert session.max_redirects == 0


def test_timeout_is_capped_at_sixty_seconds():
    assert cf.CloudflareImageClient(ACCOUNT, MA_GIA, timeout=600).timeout == 60
    assert cf.CloudflareImageClient(ACCOUNT, MA_GIA, timeout=0).timeout == 60
    assert cf.CloudflareImageClient(ACCOUNT, MA_GIA, timeout=5).timeout == 5


def test_route_is_built_only_from_constants_and_checked_values(monkeypatch):
    fake = FakeCloudflare()
    monkeypatch.setattr(cf, "API_BASE", "https://gateway.ai.cloudflare.com/v1/")
    with pytest.raises(cf.CloudflareImageError) as info:
        _run(fake, ok_image(ANH))
    assert str(info.value) == cf.MSG_BLOCKED
    assert fake.calls == []


@pytest.mark.parametrize(
    "steps", [True, False, 0, 9, -1, "4", 4.0, None], ids=["t", "f", "0", "9", "-1", "s", "fl", "n"]
)
def test_steps_must_be_a_real_integer_from_one_to_eight(steps):
    fake = FakeCloudflare()
    fake.on("POST", RUN_URL, ok_image(ANH))
    with pytest.raises(cf.CloudflareImageError) as info:
        _client(fake).generate("a gate", steps=steps)
    assert info.value.kind == cf.KIND_BAD_REQUEST
    assert fake.calls == []


@pytest.mark.parametrize("steps", [1, 8])
def test_steps_limits_are_accepted(steps):
    fake = FakeCloudflare()
    fake.on("POST", RUN_URL, ok_image(ANH))
    assert _client(fake).generate("a gate", steps=steps).steps == steps
    assert json_body(fake.requests[0])["steps"] == steps


@pytest.mark.parametrize(
    "prompt",
    ["", "   ", "\n", "x" * 2049, None, 12],
    ids=["rong", "cach", "dong", "dai", "n", "so"],
)
def test_bad_prompt_is_refused_before_any_request(prompt):
    fake = FakeCloudflare()
    fake.on("POST", RUN_URL, ok_image(ANH))
    with pytest.raises(cf.CloudflareImageError) as info:
        _client(fake).generate(prompt)
    assert info.value.kind == cf.KIND_BAD_REQUEST
    assert fake.calls == []


def test_prompt_of_exactly_2048_characters_is_sent_whole():
    fake = FakeCloudflare()
    prompt = "a" * 2048
    _run(fake, ok_image(ANH), prompt=prompt)
    assert json_body(fake.requests[0])["prompt"] == prompt  # không cắt


@pytest.mark.parametrize(
    "model",
    ["@cf/black-forest-labs/flux-1-dev", "../../user/tokens/verify", "", None],
    ids=["khac", "duong", "rong", "n"],
)
def test_model_must_be_in_the_allow_list(model):
    fake = FakeCloudflare()
    with pytest.raises(cf.CloudflareImageError) as info:
        _client(fake).generate("a gate", model=model)
    assert str(info.value) == cf.MSG_MODEL
    assert fake.calls == []


# ------------------------------------------------------------------ mã tài khoản, token


@pytest.mark.parametrize(
    "account",
    [
        ACCOUNT.upper(),
        ACCOUNT[:-1],
        ACCOUNT + "0",
        "../../" + ACCOUNT[6:],
        ACCOUNT[:-1] + "/",
        ACCOUNT[:-1] + "g",
        "",
    ],
    ids=["hoa", "ngan", "dai", "duong", "gach", "g", "rong"],
)
def test_account_id_must_be_32_lowercase_hex(account):
    with pytest.raises(cf.CloudflareImageError) as info:
        cf.CloudflareImageClient(account, MA_GIA)
    assert str(info.value) == cf.MSG_BAD_ACCOUNT
    assert info.value.kind == cf.KIND_AUTH
    if account:
        assert account not in str(info.value)


@pytest.mark.parametrize(
    "value",
    [
        MA_GIA + " ",
        '"' + MA_GIA + '"',
        MA_GIA + "\nX-Them: 1",
        "ngan",
        MA_GIA.replace("_", "."),
        "",
    ],
    ids=["cach", "nhay", "dong", "ngan", "cham", "rong"],
)
def test_token_with_odd_characters_is_refused_without_echo(value):
    with pytest.raises(cf.CloudflareImageError) as info:
        cf.CloudflareImageClient(ACCOUNT, value)
    assert str(info.value) == cf.MSG_BAD_TOKEN
    if value:
        assert value.strip() not in str(info.value)


def test_repr_never_shows_account_or_token():
    client = cf.CloudflareImageClient(ACCOUNT, MA_GIA)
    for text in (repr(client), str(client), repr(client._auth), repr(vars(client))):
        assert MA_GIA not in text
    assert ACCOUNT not in repr(client)


def test_from_settings_needs_both_values():
    settings = load_settings(None, environ={"CLOUDFLARE_ACCOUNT_ID": ACCOUNT})
    with pytest.raises(cf.CloudflareImageError) as info:
        cf.CloudflareImageClient.from_settings(settings)
    assert str(info.value) == cf.MSG_NO_KEYS
    assert info.value.kind == cf.KIND_AUTH
    settings = load_settings(
        None, environ={"CLOUDFLARE_ACCOUNT_ID": ACCOUNT, "CLOUDFLARE_API_TOKEN": MA_GIA}
    )
    fake = FakeCloudflare()
    fake.on("POST", RUN_URL, ok_image(ANH))
    client = cf.CloudflareImageClient.from_settings(settings, session=make_session(fake))
    assert client.generate("a gate").data == ANH


# ------------------------------------------------------------------ mã lỗi Cloudflare


@pytest.mark.parametrize(
    ("status", "body", "kind", "message"),
    [
        (429, failed(3036), cf.KIND_QUOTA_DAY, cf.MSG_QUOTA),
        (200, failed(3036), cf.KIND_QUOTA_DAY, cf.MSG_QUOTA),
        (429, failed(3040), cf.KIND_BUSY, cf.MSG_BUSY),
        (429, failed(9999), cf.KIND_RATE, cf.MSG_BUSY),
        (429, b"", cf.KIND_RATE, cf.MSG_BUSY),
        (401, failed(10000), cf.KIND_AUTH, cf.MSG_AUTH),
        (403, failed(9109), cf.KIND_AUTH, cf.MSG_AUTH),
        (403, failed(3023), cf.KIND_AUTH, cf.MSG_AUTH),
        (200, failed(3023), cf.KIND_AUTH, cf.MSG_AUTH),
        (400, failed(5004), cf.KIND_BAD_REQUEST, cf.MSG_REJECTED.format(code=400)),
        (400, failed(3003), cf.KIND_BAD_REQUEST, cf.MSG_REJECTED.format(code=400)),
        (400, failed(5007), cf.KIND_BAD_REQUEST, cf.MSG_REJECTED.format(code=400)),
        (404, failed(3042), cf.KIND_BAD_REQUEST, cf.MSG_REJECTED.format(code=404)),
        (410, failed(5028), cf.KIND_BAD_REQUEST, cf.MSG_REJECTED.format(code=410)),
        (418, b"<html>tea</html>", cf.KIND_BAD_REQUEST, cf.MSG_REJECTED.format(code=418)),
        (408, b"", cf.KIND_TIMEOUT, cf.MSG_NETWORK),
        (500, failed(9999), cf.KIND_BUSY, cf.MSG_SERVER.format(code=500)),
        (503, b"Service Unavailable", cf.KIND_BUSY, cf.MSG_SERVER.format(code=503)),
        (202, {"success": True}, cf.KIND_SHAPE, cf.MSG_BAD_DATA.format(code=202)),
    ],
    ids=[
        "3036",
        "3036-200",
        "3040",
        "429-la",
        "429-rong",
        "401",
        "403",
        "3023",
        "3023-200",
        "5004",
        "3003",
        "5007",
        "3042",
        "5028",
        "418",
        "408",
        "500",
        "503",
        "202",
    ],
)
def test_errors_become_fixed_vietnamese_messages_with_kind(status, body, kind, message):
    exc = _error(FakeCloudflare(), (status, body, {}))
    assert str(exc) == message
    assert exc.kind == kind
    assert isinstance(exc, AIError)
    assert exc.status_code == status


@pytest.mark.parametrize(
    "code", ["3036", 3036.0, True, None, [3036]], ids=["chu", "thuc", "bool", "none", "list"]
)
def test_error_code_is_read_only_when_it_is_a_real_integer(code):
    exc = _error(FakeCloudflare(), (429, failed(code), {}))
    assert exc.kind == cf.KIND_RATE  # không coi là 3036
    assert exc.error_code is None


def test_server_message_never_reaches_the_user():
    secret = f"tai khoan {ACCOUNT} khoa {MA_GIA} https://evil.example/x"
    for status in (400, 401, 429, 500):
        exc = _error(FakeCloudflare(), (status, failed(5004, secret), {}))
        assert "evil" not in str(exc)
        assert ACCOUNT not in str(exc)
        assert MA_GIA not in str(exc)


def test_failed_call_is_never_retried_by_the_client():
    fake = FakeCloudflare()
    _error(fake, (503, b"", {}))
    _error(FakeCloudflare(), (429, failed(3040), {}))
    assert len(fake.calls) == 1


# ------------------------------------------------------------------ câu trả lời sai khuôn


@pytest.mark.parametrize(
    "body",
    [
        b"khong phai json",
        b"[1, 2]",
        b'{"success": NaN, "result": {"image": "AAAA"}}',
        b'{"success": true, "success": true, "result": {"image": "AAAA"}}',
        b"[" * 100_000 + b"]" * 100_000,
        json.dumps({"success": "true", "result": {"image": "AAAA"}}).encode(),
        json.dumps({"result": {"image": "AAAA"}}).encode(),
        b"\xff\xfe\x00",
    ],
    ids=["chu", "mang", "nan", "trung", "sau", "chu-true", "thieu", "utf8"],
)
def test_odd_json_is_refused(body):
    exc = _error(FakeCloudflare(), (200, body, {}))
    assert exc.kind == cf.KIND_SHAPE
    assert str(exc) == cf.MSG_BAD_DATA.format(code=200)


def test_non_json_content_type_is_refused():
    exc = _error(FakeCloudflare(), (200, ok_image(ANH), {"Content-Type": "text/html"}))
    assert exc.kind == cf.KIND_SHAPE


def test_json_content_type_with_charset_is_fine():
    fake = FakeCloudflare()
    image = _run(fake, (200, ok_image(ANH), {"Content-Type": "application/json; charset=utf-8"}))
    assert image.data == ANH


def _answer(result) -> dict:
    return {"success": True, "errors": [], "messages": [], "result": result}


@pytest.mark.parametrize(
    "answer",
    [
        _answer(None),
        _answer([]),
        _answer({}),
        _answer({"image": None}),
        _answer({"image": 123}),
        _answer({"image": ""}),
        _answer({"image": "https://anh.example/x.png"}),
        _answer({"image": "AAAA BBBB"}),
        _answer({"image": "AAA"}),
        _answer({"image": base64.b64encode(ANH).decode(), "url": "https://anh.example/x"}),
        {**_answer({"image": base64.b64encode(ANH).decode()}), "url": "https://anh.example/x"},
    ],
    ids=[
        "none",
        "mang",
        "thieu",
        "img-none",
        "so",
        "rong",
        "url",
        "cach",
        "le",
        "co-url",
        "url-ngoai",
    ],
)
def test_only_base64_image_is_accepted_never_a_link(answer):
    fake = FakeCloudflare()
    fake.on("GET", "https://anh.example/x.png", (200, b"anh ngoai", {}))
    exc = _error(fake, answer)
    assert exc.kind == cf.KIND_SHAPE
    assert [r.method for r in fake.requests] == ["POST"]  # không tải gì theo địa chỉ


def test_base64_string_length_is_checked_before_decoding(monkeypatch):
    monkeypatch.setattr(cf, "MAX_IMAGE_CHARS", 100)
    exc = _error(FakeCloudflare(), ok_image(b"x" * 90))  # 120 ký tự base64
    assert str(exc) == cf.MSG_IMAGE_TOO_BIG


def test_decoded_image_size_is_limited(monkeypatch):
    monkeypatch.setattr(cf, "MAX_IMAGE_BYTES", 50)
    exc = _error(FakeCloudflare(), ok_image(b"x" * 60))
    assert str(exc) == cf.MSG_IMAGE_TOO_BIG


def test_response_body_is_read_with_a_limit(monkeypatch):
    monkeypatch.setattr(cf, "MAX_RESPONSE_BYTES", 1000)
    exc = _error(FakeCloudflare(), ok_image(b"x" * 2000))
    assert str(exc) == cf.MSG_TOO_BIG
    exc = _error(FakeCloudflare(), (200, ok_image(ANH), {"Content-Length": "999999999"}))
    assert str(exc) == cf.MSG_TOO_BIG


@pytest.mark.parametrize(
    "headers", [{"Location": "https://evil.example/anh"}, {}], ids=["location", "khong"]
)
@pytest.mark.parametrize("status", [301, 302, 307, 308])
def test_redirect_is_refused_and_never_followed(status, headers):
    fake = FakeCloudflare()
    fake.on("GET", "https://evil.example/anh", ok_image(ANH))
    exc = _error(fake, (status, b"than chuyen huong", headers))
    assert str(exc) == cf.MSG_REDIRECT.format(code=status)
    assert exc.kind == cf.KIND_SHAPE
    assert len(fake.calls) == 1


# ------------------------------------------------------------------ lỗi mạng của requests


@pytest.mark.parametrize(
    ("error", "kind", "message"),
    [
        (requests.exceptions.ConnectTimeout, cf.KIND_TIMEOUT, cf.MSG_NETWORK),
        (requests.exceptions.ReadTimeout, cf.KIND_TIMEOUT, cf.MSG_NETWORK),
        (requests.exceptions.ConnectionError, cf.KIND_NETWORK, cf.MSG_NETWORK),
        (requests.exceptions.SSLError, cf.KIND_NETWORK, cf.MSG_SSL),
        (requests.exceptions.ChunkedEncodingError, cf.KIND_NETWORK, None),
        (requests.exceptions.InvalidHeader, cf.KIND_NETWORK, None),
    ],
    ids=["ct", "rt", "conn", "ssl", "chunk", "header"],
)
def test_requests_errors_become_fixed_messages_without_url(error, kind, message):
    fake = FakeCloudflare()
    exc = _error(fake, lambda request: error(f"loi tai {request.url} {MA_GIA}"))
    assert exc.kind == kind
    if message is not None:
        assert str(exc) == message
    else:
        assert str(exc) == cf.MSG_NETWORK_OTHER.format(kind=error.__name__)
    assert ACCOUNT not in str(exc)
    assert MA_GIA not in str(exc)
    assert exc.__suppress_context__ is True  # dấu vết lỗi gốc (có URL) không đi kèm


def test_read_error_after_status_becomes_network_error():
    class Broken:
        def read(self, *_args, **_kwargs):
            raise requests.exceptions.ConnectionError(f"dut {RUN_URL}")

        def stream(self, *_args, **_kwargs):
            raise requests.exceptions.ConnectionError(f"dut {RUN_URL}")

        def close(self):
            pass

    fake = FakeCloudflare()
    real_send = fake.send

    def send(request, **kwargs):
        response = real_send(request, **kwargs)
        response.raw = Broken()
        return response

    fake.send = send
    exc = _error(fake, ok_image(ANH))
    assert exc.kind == cf.KIND_NETWORK
    assert ACCOUNT not in str(exc)


# ------------------------------------------------------------------ kiểm token


@pytest.mark.parametrize("state", ["active", "disabled", "expired"])
def test_verify_token_reads_only_the_status(state):
    fake = FakeCloudflare()
    fake.on("GET", VERIFY_URL, token_status(state))
    assert _client(fake).verify_token() == state
    [(request, kwargs)] = fake.calls
    assert request.url == VERIFY_URL
    assert request.body is None
    assert request.headers["Authorization"] == f"Bearer {MA_GIA}"
    assert kwargs["stream"] is True
    assert state in cf.TOKEN_MESSAGES


@pytest.mark.parametrize(
    "answer",
    [token_status("ACTIVE"), token_status(""), {"success": True, "result": {"status": 1}}],
    ids=["hoa", "rong", "so"],
)
def test_verify_token_odd_status_is_refused(answer):
    fake = FakeCloudflare()
    fake.on("GET", VERIFY_URL, answer)
    with pytest.raises(cf.CloudflareImageError) as info:
        _client(fake).verify_token()
    assert info.value.kind == cf.KIND_SHAPE


def test_verify_token_errors_use_the_same_fixed_messages():
    fake = FakeCloudflare()
    fake.on("GET", VERIFY_URL, (401, failed(1000, "Invalid API Token"), {}))
    with pytest.raises(cf.CloudflareImageError) as info:
        _client(fake).verify_token()
    assert str(info.value) == cf.MSG_AUTH
    assert "Invalid" not in str(info.value)


def test_active_token_message_says_workers_ai_right_is_not_proven():
    assert "Workers AI" in cf.TOKEN_MESSAGES["active"]
    assert "lần tạo ảnh đầu tiên" in cf.TOKEN_MESSAGES["active"]


# ------------------------------------------------------------------ cấu hình [tasks.image]


def _ai_toml(tmp_path, image_block: str) -> Path:
    path = tmp_path / "ai.toml"
    path.write_text(
        '[tasks.write]\nprovider = "anthropic"\nmodel = "claude-x"\n\n' + image_block,
        encoding="utf-8",
    )
    return path


def test_load_image_task_reads_model_and_steps(tmp_path):
    path = _ai_toml(
        tmp_path,
        f'[tasks.image]\nprovider = "cloudflare"\nmodel = "{cf.FLUX_SCHNELL}"\nsteps = 6\n',
    )
    assert cf.load_image_task(path) == cf.ImageTask(model=cf.FLUX_SCHNELL, steps=6)


def test_load_image_task_default_steps_is_four(tmp_path):
    path = _ai_toml(
        tmp_path, f'[tasks.image]\nprovider = "cloudflare"\nmodel = "{cf.FLUX_SCHNELL}"\n'
    )
    assert cf.load_image_task(path).steps == 4


def test_load_image_task_without_image_block(tmp_path):
    with pytest.raises(AIError) as info:
        cf.load_image_task(_ai_toml(tmp_path, ""))
    assert str(info.value) == cf.MSG_NO_IMAGE_TASK


def test_load_image_task_needs_cloudflare(tmp_path):
    path = _ai_toml(tmp_path, '[tasks.image]\nprovider = "gemini"\nmodel = "anh-x"\n')
    with pytest.raises(AIError) as info:
        cf.load_image_task(path)
    assert str(info.value) == cf.MSG_NOT_CLOUDFLARE


def test_load_image_task_refuses_unknown_model(tmp_path):
    path = _ai_toml(tmp_path, '[tasks.image]\nprovider = "cloudflare"\nmodel = "@cf/khac"\n')
    with pytest.raises(AIError) as info:
        cf.load_image_task(path)
    assert str(info.value) == cf.MSG_MODEL
    assert "@cf/khac" not in str(info.value)


# ------------------------------------------------------------------ luồng nền, không Streamlit


@pytest.mark.parametrize(
    "module", ["seo_app/ai/cloudflare_images.py", "seo_app/images/generated.py"], ids=["cf", "gen"]
)
def test_new_modules_never_import_streamlit_or_logging(module):
    tree = ast.parse((ROOT / module).read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert "streamlit" not in imported
    assert "logging" not in imported


def test_generate_works_from_a_plain_thread():
    fake = FakeCloudflare()
    fake.on("POST", RUN_URL, ok_image(ANH))
    results: list[object] = []

    def work() -> None:
        try:
            results.append(_client(fake).generate("a gate").data)
        except BaseException as exc:  # pragma: no cover - chỉ để báo đúng lỗi
            results.append(exc)

    thread = threading.Thread(target=work)
    thread.start()
    thread.join(10)
    assert results == [ANH]
