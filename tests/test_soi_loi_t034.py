"""Soi Lỗi · T-034: 7 lỗi Thấp của lớp AI và trang thử mù.

Bổ sung cho ``tests/test_ai_t034.py`` (của Thợ Máy), thử các trường hợp xấu hơn:

- SL-T019-5: header lạ không tới client ở cả 4 chỗ tạo client, kể cả song song; luồng khác dùng
  ``os`` của module thư viện đúng lúc đang trỏ tạm vẫn chạy đúng; ngoại lệ, gọi lồng, thư viện
  đổi cấu trúc; chứng minh hàm phụ ``library_sees`` (dùng trong 4 test đã đổi) không rỗng nghĩa.
- SL-T019-3: số phiên bản / biến thể sau tên đã che; số đứng riêng và chữ tiếng Việt giữ nguyên.
- SL-T019-4: Claude bị cắt ra đúng câu hạ effort; các nhánh lỗi khác của Anthropic giữ nguyên.
- LC-T028-3: gzip / br hỏng ra "dữ liệu lạ" (cả nút Kiểm tra khóa); mất mạng thật thì không.
- LC-T019-1, LC-T019-2: ký tự lạ trong tên mô hình; câu thiếu file không lộ đường dẫn máy.

Lỗi chưa sửa: ``xfail(strict=True)`` kèm mã ``SL-T034-n``. Không gọi mạng thật.
"""

from __future__ import annotations

import importlib
import json
import os
import re
import sys
import threading
import time
from pathlib import Path
from types import SimpleNamespace

import anthropic
import httpx2
import openai
import pytest
from test_ai_t028 import (
    BLOCK_START,
    BLOCK_STOP,
    KEYS,
    NAMES,
    SERVER_TEXT,
    START,
    VENDOR,
    anthropic_stream,
    generate,
    library_sees,
    message_end,
    real_provider,
    sse,
    stainless_client,
    text_delta,
)
from test_soi_loi_t019 import (
    RULES,
    SETTINGS,
    app_env,  # noqa: F401 - fixture dùng chung
    open_models_tab,
    set_keys,
)
from test_soi_loi_t019_luot2 import REAL_MODELS, VIETNAMESE

from seo_app import env_file
from seo_app.ai import AIError, load_ai_config
from seo_app.ai import base as base_module
from seo_app.ai.anthropic_provider import AnthropicProvider
from seo_app.ai.base import (
    IGNORED_ENV,
    TokenLimitError,
    bad_response_message,
    ignoring_custom_headers,
)
from seo_app.ai.openai_provider import OpenAIProvider
from seo_app.content import blind_test
from seo_app.content.blind_test import (
    MASK,
    TOKEN_LIMIT_ERROR,
    Candidate,
    _mask_names,
    run_blind_test,
    validate_request,
)

CLIENT_MODULES = ("anthropic._client", "openai._client")
EVIL = f"X-T034-Soi: {SERVER_TEXT}\nAuthorization: Bearer khoa-nguoi-khac-T034"
PROXY = "http://proxy.congty.test:3128"
REAL_CANDIDATES = ["claude-opus-5-5", "gpt-6.1", "gemini-3-pro"]


def client_module(name):
    return importlib.import_module(name)


def assert_modules_restored():
    for name in CLIENT_MODULES:
        assert client_module(name).os is os, name
    assert not base_module._ENV_LOCK.locked()


@pytest.fixture
def evil_env(monkeypatch):
    for name in IGNORED_ENV:
        monkeypatch.setenv(name, EVIL)
    monkeypatch.setenv("HTTPS_PROXY", PROXY)


@pytest.fixture
def recorder(monkeypatch):
    """Client thật của anthropic/openai, mạng giả trả 400; ghi header của mọi yêu cầu."""
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


def assert_no_evil(headers):
    # Header tổ chức/dự án của OpenAI có mặt nhưng giá trị là ``Omit`` (không gửi): chỉ cấm giá trị
    # là chữ thật.
    lowered = {name.lower(): value for name, value in dict(headers).items()}
    assert "x-t034-soi" not in lowered
    for name in ("openai-organization", "openai-project"):
        assert not isinstance(lowered.get(name), str), name
    text = json.dumps({k: str(v) for k, v in lowered.items()}, ensure_ascii=False)
    assert SERVER_TEXT not in text
    assert "khoa-nguoi-khac-T034" not in text


# ==================================== SL-T019-5 (1): hàm phụ của 4 test đã đổi không rỗng nghĩa


@pytest.mark.usefixtures("evil_env")
def test_library_sees_helper_detects_visible_variable():
    """4 test cũ đổi ``name not in os.environ`` thành ``library_sees(name) == []``. Bất biến mới
    chỉ có nghĩa nếu ``library_sees`` thật sự thấy biến khi chưa che: kiểm điều đó ở đây.
    """
    for name in IGNORED_ENV:
        assert library_sees(name) == list(CLIENT_MODULES)
    with ignoring_custom_headers():
        for name in IGNORED_ENV:
            assert library_sees(name) == []
            assert os.environ[name] == EVIL  # và phần còn lại của máy không bị đụng
    for name in IGNORED_ENV:
        assert library_sees(name) == list(CLIENT_MODULES)


def test_only_client_modules_read_ignored_env():
    """Bất biến mới chỉ che ``os`` của 2 module ``_client``. Bảo đảm trong thư viện đang cài, chỉ
    các module đó (và client Azure / Google Cloud mà app không dùng) đọc các biến bị bỏ qua.
    Nâng thư viện mà chỗ đọc biến dời đi nơi khác thì test này đỏ trước khi header lạ lọt.
    """
    allowed = {
        "anthropic._client",
        "openai._client",
        "anthropic.lib.google_cloud._client",  # AnthropicGoogleCloud: app không dùng
        "openai.lib.azure",  # AzureOpenAI: app không dùng
    }
    readers = set()
    for package in (anthropic, openai):
        root = Path(package.__file__).parent
        for file in root.rglob("*.py"):
            text = file.read_text(encoding="utf-8", errors="replace")
            if any(name in text for name in IGNORED_ENV):
                parts = file.relative_to(root.parent).with_suffix("").parts
                readers.add(".".join(p for p in parts if p != "__init__"))
    assert readers <= allowed, readers - allowed
    for name in CLIENT_MODULES:
        source = Path(client_module(name).__file__).read_text(encoding="utf-8")
        for line in source.splitlines():
            if any(f'"{var}"' in line for var in IGNORED_ENV) and "environ" in line:
                assert "os.environ.get(" in line, line
    app_source = "\n".join(
        p.read_text(encoding="utf-8")
        for p in (Path(__file__).resolve().parents[1] / "seo_app").rglob("*.py")
    )
    for unused in ("AzureOpenAI", "AnthropicGoogleCloud", "AnthropicVertex", "AnthropicBedrock"):
        assert unused not in app_source


# ============================== SL-T019-5 (2): header lạ không tới client, cả 4 chỗ, song song


@pytest.mark.usefixtures("evil_env")
def test_all_four_creation_sites_in_parallel(recorder):
    """2 provider + 2 hàm Kiểm tra khóa, 16 luồng cùng lúc, mỗi luồng 4 lần."""
    errors: list[BaseException] = []
    clients: list[object] = []
    barrier = threading.Barrier(16)

    def work(i):
        try:
            barrier.wait()
            for _ in range(4):
                kind = i % 4
                if kind == 0:
                    clients.append(AnthropicProvider(KEYS["anthropic"])._client)
                elif kind == 1:
                    clients.append(OpenAIProvider(KEYS["openai"])._client)
                else:
                    vendor = "anthropic" if kind == 2 else "openai"
                    result = env_file.check_api_key(NAMES[vendor], api_key=KEYS[vendor])
                    assert result.status in {"invalid", "unknown"}
        except BaseException as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=work, args=(i,)) for i in range(16)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=60)
    assert not any(thread.is_alive() for thread in threads)
    assert errors == []
    assert len(clients) == 32
    for client in clients:
        assert_no_evil(client._custom_headers)
        assert_no_evil(client.default_headers)
    assert len(recorder) == 32  # 8 luồng × 4 lần Kiểm tra khóa
    for headers in recorder:
        assert_no_evil(headers)
    for name in IGNORED_ENV:
        assert os.environ[name] == EVIL
    assert_modules_restored()


# ============ SL-T019-5 (3): luồng khác dùng os của module thư viện đúng lúc đang trỏ tạm


def _library_os_checks(lib_os):
    """Mọi kiểu dùng ``os`` thường gặp; trả về danh sách chỗ sai (rỗng là đúng)."""
    wrong = []
    if lib_os.name != os.name:
        wrong.append("name")
    if lib_os.sep != os.sep or lib_os.path.join("a", "b") != os.path.join("a", "b"):
        wrong.append("path")
    if lib_os.fspath(Path("x")) != "x" or lib_os.getpid() != os.getpid():
        wrong.append("hàm")
    if lib_os.getenv("PATH") != os.environ.get("PATH"):
        wrong.append("getenv")
    if lib_os.environ.get("HTTPS_PROXY") != PROXY or lib_os.environ["HTTPS_PROXY"] != PROXY:
        wrong.append("HTTPS_PROXY")
    if "PATH" not in lib_os.environ or lib_os.getenv("KHONG_CO_T034", "mac-dinh") != "mac-dinh":
        wrong.append("contains/default")
    snapshot = dict(lib_os.environ)
    if snapshot.get("HTTPS_PROXY") != PROXY or len(snapshot) < 2:
        wrong.append("dict")
    return wrong


@pytest.mark.usefixtures("evil_env")
def test_other_threads_using_library_os_while_patched():
    stop = threading.Event()
    errors: list[object] = []
    patched_seen = threading.Event()

    def patch_loop():
        while not stop.is_set():
            with ignoring_custom_headers():
                time.sleep(0.0005)  # giữ khối mở một chút để luồng đọc bắt được lúc đang trỏ tạm

    def use_loop(name):
        module = client_module(name)
        while not stop.is_set():
            try:
                lib_os = module.os
                if lib_os is not os:
                    patched_seen.set()
                wrong = _library_os_checks(lib_os)
                if wrong:
                    errors.append((name, wrong))
            except BaseException as exc:  # noqa: BLE001
                errors.append(exc)

    threads = [threading.Thread(target=patch_loop) for _ in range(3)]
    threads += [threading.Thread(target=use_loop, args=(n,)) for n in CLIENT_MODULES * 2]
    for thread in threads:
        thread.start()
    stop.wait(0.6)
    stop.set()
    for thread in threads:
        thread.join(timeout=30)
    assert errors == []
    assert patched_seen.is_set()  # test có chạy đúng lúc đang trỏ tạm
    assert_modules_restored()


@pytest.mark.usefixtures("evil_env")
def test_filtered_view_inside_block_behaves_like_os():
    with ignoring_custom_headers():
        for name in CLIENT_MODULES:
            lib_os = client_module(name).os
            assert lib_os is not os
            assert _library_os_checks(lib_os) == []
            view = lib_os.environ
            assert set(view) == set(os.environ) - set(IGNORED_ENV)
            assert len(view) == len(os.environ) - len(IGNORED_ENV)
            assert view.copy() == {k: v for k, v in os.environ.items() if k not in IGNORED_ENV}
            for var in IGNORED_ENV:
                assert lib_os.getenv(var) is None
                assert view.get(var) is None
                with pytest.raises(KeyError):
                    view[var]


# ==================================== SL-T019-5 (4): ngoại lệ giữa chừng, gọi lồng, khóa nhả


@pytest.mark.usefixtures("evil_env")
@pytest.mark.parametrize("error", [ValueError, KeyboardInterrupt, SystemExit, GeneratorExit])
def test_exception_inside_restores_module_os_and_lock(error):
    with pytest.raises(error), ignoring_custom_headers():
        assert client_module("anthropic._client").os is not os
        raise error()
    assert_modules_restored()
    for name in IGNORED_ENV:
        assert os.environ[name] == EVIL


@pytest.mark.usefixtures("evil_env")
def test_exception_in_nested_inner_block_keeps_outer_protected():
    with ignoring_custom_headers():
        with pytest.raises(RuntimeError), ignoring_custom_headers():
            raise RuntimeError("trong")
        # Khối ngoài còn hiệu lực: thư viện vẫn không thấy biến.
        for name in IGNORED_ENV:
            assert library_sees(name) == []
        client = anthropic.Anthropic(api_key=KEYS["anthropic"])
        assert_no_evil(client._custom_headers)
    assert_modules_restored()


@pytest.mark.usefixtures("evil_env")
def test_deeply_nested_and_other_thread_waits():
    """Gọi lồng 5 tầng không treo; luồng khác chờ tới khi khối ngoài cùng xong mới vào được."""
    order: list[str] = []
    inside = threading.Event()

    def other():
        inside.wait(10)
        with ignoring_custom_headers():
            order.append("khac")

    thread = threading.Thread(target=other)
    thread.start()
    with ignoring_custom_headers():
        with (
            ignoring_custom_headers(),
            ignoring_custom_headers(),
            ignoring_custom_headers(),
            ignoring_custom_headers(),
        ):
            inside.set()
            time.sleep(0.05)
            order.append("trong")
        assert library_sees("ANTHROPIC_CUSTOM_HEADERS") == []
        time.sleep(0.05)
        order.append("ngoai")
    thread.join(timeout=10)
    assert not thread.is_alive()
    assert order == ["trong", "ngoai", "khac"]
    assert_modules_restored()


# ========================== SL-T019-5 (5): thư viện đổi cấu trúc → quay về cách cũ, vẫn an toàn


@pytest.mark.usefixtures("evil_env")
@pytest.mark.parametrize("module_name", CLIENT_MODULES)
def test_library_reading_env_another_way_falls_back(monkeypatch, module_name):
    """Thư viện đọc biến qua một tên khác ``os`` thật (ví dụ ``import os as _os``, hay một lớp bọc):
    quay về gỡ biến tạm thời, client tạo ra vẫn không có header lạ."""
    module = client_module(module_name)
    monkeypatch.setattr(module, "os", SimpleNamespace(environ=os.environ))  # đọc env thật, khác tên
    with ignoring_custom_headers():
        assert all(name not in os.environ for name in IGNORED_ENV)
        assert library_sees("ANTHROPIC_CUSTOM_HEADERS") == []
        a = anthropic.Anthropic(api_key=KEYS["anthropic"])
        o = openai.OpenAI(api_key=KEYS["openai"])
    assert module.os.environ is os.environ  # không bị thay bằng khung nhìn lọc
    for client in (a, o):
        assert_no_evil(client._custom_headers)
        assert_no_evil(client.default_headers)
    for name in IGNORED_ENV:
        assert os.environ[name] == EVIL
    assert not base_module._ENV_LOCK.locked()
    other = client_module(next(n for n in CLIENT_MODULES if n != module_name))
    assert other.os is os


@pytest.mark.usefixtures("evil_env")
@pytest.mark.parametrize("module_name", CLIENT_MODULES)
def test_library_without_os_attribute_falls_back(monkeypatch, module_name):
    monkeypatch.delattr(client_module(module_name), "os")
    with ignoring_custom_headers():
        assert all(name not in os.environ for name in IGNORED_ENV)
    assert all(os.environ[name] == EVIL for name in IGNORED_ENV)
    assert not hasattr(client_module(module_name), "os")  # không tự thêm tên ``os``
    assert not base_module._ENV_LOCK.locked()


@pytest.mark.usefixtures("evil_env")
def test_fallback_nested_keeps_variables_hidden_until_outer_ends(monkeypatch):
    monkeypatch.setattr(client_module("anthropic._client"), "os", object())
    with ignoring_custom_headers():
        with ignoring_custom_headers():
            pass
        assert all(name not in os.environ for name in IGNORED_ENV)
    assert all(os.environ[name] == EVIL for name in IGNORED_ENV)


@pytest.mark.usefixtures("evil_env")
@pytest.mark.parametrize("module_name", CLIENT_MODULES)
def test_library_without_client_module_falls_back(monkeypatch, module_name):
    package = module_name.split(".")[0]
    assert importlib.import_module(package)  # gói vẫn cài
    monkeypatch.setitem(sys.modules, module_name, None)  # nhập module này sẽ báo ImportError
    with ignoring_custom_headers():
        # Không biết thư viện mới đọc biến ở đâu: phải gỡ biến tạm thời như cách cũ.
        assert all(name not in os.environ for name in IGNORED_ENV)
    assert all(os.environ[name] == EVIL for name in IGNORED_ENV)


# ======================================= SL-T019-3: số phiên bản / biến thể sau tên đã che


@pytest.mark.parametrize(
    ("text", "leaks"),
    [
        ("Tôi là Claude Opus 5.5, viết bài này.", ["5.5", "Opus", "Claude"]),
        ("Tôi là GPT 6.1.", ["6.1"]),
        ("Gemini 3 Pro viết bài.", ["3 Pro", "Pro"]),
        ("Gemini 3 Pro Preview viết bài.", ["Pro", "Preview"]),
        ("Gemini 2.5 Flash Lite viết.", ["2.5", "Flash", "Lite"]),
        ("Claude 3.5 Sonnet trả lời.", ["3.5", "Sonnet"]),
        ("GPT-4o mini trả lời.", ["4o", "mini"]),
        ("GPT 4 Turbo trả lời.", ["4", "Turbo"]),
        ("Claude Opus 4.5 Thinking.", ["4.5", "Thinking"]),
        ("Tôi là gpt-6.1 v2.", ["v2", "6.1"]),
        ("Tôi là claude-opus-5-5 5.5.", ["5.5", "5-5"]),
        ("Mô hình: **Claude Opus 5.5**.", ["5.5"]),
        ("Gemini\t3 Pro (tab).", ["3 Pro"]),
    ],
)
def test_version_after_masked_name_is_masked(text, leaks):
    shown = _mask_names(text, REAL_CANDIDATES)
    assert MASK in shown
    for leak in leaks:
        assert leak not in shown, (leak, shown)


@pytest.mark.parametrize(
    ("text", "leak"),
    [
        ("Viết bởi Gemini 2.5 Flash-Lite.", "Flash-Lite"),
        ("Tôi là Claude Opus 5.5-preview.", "5.5-preview"),
        ("Tôi là Gemini 1.5 Pro-002.", "Pro-002"),
    ],
)
def test_hyphenated_variant_after_version_is_masked(text, leak):
    assert leak not in _mask_names(text, REAL_CANDIDATES)


@pytest.mark.parametrize(
    "text",
    [
        "Thép dày 5.5 mm, khung 6.1 m.",
        "Cổng 3 cánh, cửa 2 cánh mở quay.",
        "Năm 2025 giá thép tăng; bảo hành 5 năm.",
        "Giá 3.500.000đ/bộ, giảm 10% trong tháng 12.",
        "Sơn 2 lớp, mỗi lớp cách nhau 4 giờ, dày 60 micron.",
        "Bản lề 3 vòng bi, ray 2,5 m, bánh xe 75 mm.",
        "Cửa sắt pro, cửa mini, khóa max an toàn, bản lite.",
        "Dòng cửa Turbo Flash của hãng khác, mẫu Plus 2.",
        "Cửa 4 cánh xếp gọn, 1 cánh phụ.",
    ],
)
def test_numbers_and_words_without_vendor_untouched(text):
    assert _mask_names(text, REAL_CANDIDATES) == text


@pytest.mark.parametrize("text", VIETNAMESE)
def test_vietnamese_door_text_still_untouched(text):
    assert _mask_names(text, REAL_CANDIDATES) == text


@pytest.mark.parametrize(
    ("text", "kept"),
    [
        ("Claude viết: cửa dày 5.5 mm.", "cửa dày 5.5 mm"),
        ("Theo Gemini, cổng 3 cánh rộng 4 m.", "cổng 3 cánh rộng 4 m"),
        ("GPT.\n2025 là năm giá thép tăng.", "2025 là năm"),
        ("Claude: 5 năm bảo hành.", "5 năm bảo hành"),
        ("Opus 5.5mm là sai đơn vị.", "5.5mm"),
    ],
)
def test_numbers_not_glued_to_name_are_kept(text, kept):
    shown = _mask_names(text, REAL_CANDIDATES)
    assert MASK in shown
    assert kept in shown


@pytest.mark.parametrize(
    "text",
    [
        "Claude" + " " * 40000 + "x",
        "Claude 1" + ".1" * 40000 + "a",
        "gpt " * 40000,
        "Claude " + "1 " * 40000 + "x",
        ("Gemini" + " " * 60 + "pro- ") * 2000,
    ],
    ids=["nhieu-cach", "so-dai", "lap-ten", "nhieu-so", "lap-cach"],
)
def test_masking_adversarial_text_is_fast(text):
    start = time.perf_counter()
    _mask_names(text, REAL_CANDIDATES)
    assert time.perf_counter() - start < 2.0


def test_mask_never_builds_markdown_link():
    shown = _mask_names("[Claude 5.5](https://x.y) và [GPT 6.1][1]", REAL_CANDIDATES)
    assert "5.5" not in shown and "6.1" not in shown
    assert "https://x.y" in shown  # chữ ngoài tên không bị đụng
    assert not re.search(r"«đã ẩn tên mô hình»[\[\(]", shown)


# ========================================= SL-T019-4: Claude bị cắt → câu hạ effort


def _patch_blind(monkeypatch, provider):
    monkeypatch.setattr(blind_test, "make_provider", lambda name, settings: provider)


def test_blind_anthropic_cut_gives_exact_effort_message(monkeypatch):
    cut = START + BLOCK_START + text_delta('{"intro": "bài dài ' + SERVER_TEXT) + BLOCK_STOP
    _patch_blind(monkeypatch, anthropic_stream(cut + message_end("max_tokens")))
    cands = [Candidate("anthropic", m, "high") for m in ("mo-hinh-x1", "mo-hinh-y2")]
    _, reveal = run_blind_test("sửa cửa cuốn", "", cands, SETTINGS, RULES)
    for info in reveal.values():
        assert info.error == TOKEN_LIMIT_ERROR
        assert SERVER_TEXT not in info.error


def ping():
    return sse("ping", {"type": "ping"})


def test_anthropic_cut_found_after_pings():
    cut = START + BLOCK_START + text_delta('{"text": "dài') + BLOCK_STOP
    stream = cut + ping() * 5 + message_end("max_tokens")
    with pytest.raises(TokenLimitError) as info:
        generate(anthropic_stream(stream), "anthropic", max_tokens=1234)
    assert "giới hạn 1234 token" in str(info.value)
    assert SERVER_TEXT not in str(info.value)


def test_anthropic_cut_too_far_away_keeps_plain_message():
    # Lý do dừng nằm quá xa (hơn 50 sự kiện, "ping" không tính vì thư viện bỏ qua): giữ câu cũ,
    # không đọc mãi.
    cut = START + BLOCK_START + text_delta('{"text": "dài') + BLOCK_STOP
    filler = text_delta(" thêm") * 60
    with pytest.raises(AIError) as info:
        generate(anthropic_stream(cut + filler + message_end("max_tokens")), "anthropic")
    assert type(info.value) is AIError
    assert "không đúng khuôn" in str(info.value)


def test_anthropic_cut_then_error_event_keeps_plain_message():
    cut = START + BLOCK_START + text_delta('{"text": "dài') + BLOCK_STOP
    error = sse(
        "error", {"type": "error", "error": {"type": "overloaded_error", "message": SERVER_TEXT}}
    )
    with pytest.raises(AIError) as info:
        generate(anthropic_stream(cut + error), "anthropic")
    assert type(info.value) is AIError
    assert SERVER_TEXT not in str(info.value)


@pytest.mark.parametrize("reason", ["end_turn", "stop_sequence", "refusal", "pause_turn"])
def test_anthropic_bad_schema_other_reasons_not_token_limit(reason):
    bad = START + BLOCK_START + text_delta('{"khac": 1}') + BLOCK_STOP
    with pytest.raises(AIError) as info:
        generate(anthropic_stream(bad + message_end(reason)), "anthropic")
    assert not isinstance(info.value, TokenLimitError)


@pytest.mark.parametrize(
    ("status", "body", "expected"),
    [
        (401, {"type": "error", "error": {"type": "authentication_error", "message": "x"}}, "khóa"),
        (429, {"type": "error", "error": {"type": "rate_limit_error", "message": "x"}}, "giới hạn"),
    ],
)
def test_anthropic_status_branches_unchanged(status, body, expected):
    client = stainless_client(
        "anthropic", lambda request: httpx2.Response(status, json=body | {"t": SERVER_TEXT})
    )
    with pytest.raises(AIError) as info:
        generate(AnthropicProvider(KEYS["anthropic"], client=client), "anthropic")
    message = str(info.value)
    assert not isinstance(info.value, TokenLimitError)
    assert expected in message.lower()
    assert SERVER_TEXT not in message
    assert KEYS["anthropic"] not in message


# ===================================== LC-T028-3: nén hỏng → "dữ liệu lạ"; mất mạng thật thì không

GZIP_BROKEN = b"\x1f\x8b khong phai gzip " + SERVER_TEXT.encode() * 4
BR_BROKEN = b"rac br " + SERVER_TEXT.encode()
DEFLATE_BROKEN = b"x\x9c khong phai deflate " + SERVER_TEXT.encode()
BAD_SHAPE = "AI trả về dữ liệu không đúng khuôn. Bấm thử lại."


def compressed(content, encoding, content_type="application/json"):
    return {
        "content": content,
        "headers": {"content-encoding": encoding, "content-type": content_type},
    }


BROKEN_BODIES = {
    "gzip": compressed(GZIP_BROKEN, "gzip"),
    "gzip-sse": compressed(GZIP_BROKEN, "gzip", "text/event-stream"),
    "gzip-text": compressed(GZIP_BROKEN, "gzip", "text/plain"),
    "deflate": compressed(DEFLATE_BROKEN, "deflate"),
    "deflate-sse": compressed(DEFLATE_BROKEN, "deflate", "text/event-stream"),
}


@pytest.mark.parametrize("vendor", ["anthropic", "openai"])
@pytest.mark.parametrize("kind", list(BROKEN_BODIES))
def test_broken_compression_is_strange_data_everywhere(vendor, kind):
    body = BROKEN_BODIES[kind]
    expected = bad_response_message(VENDOR[vendor])
    with pytest.raises(AIError) as info:
        generate(real_provider(vendor, body), vendor)
    assert str(info.value) == expected
    client = stainless_client(vendor, lambda request: httpx2.Response(200, **body))
    result = env_file.check_api_key(NAMES[vendor], api_key=KEYS[vendor], client=client)
    assert result.status == "unknown"
    assert result.message == expected


@pytest.mark.parametrize("vendor", ["anthropic", "openai"])
@pytest.mark.parametrize("content_type", ["application/json", "text/event-stream", "text/plain"])
def test_br_without_decoder_gives_fixed_message(vendor, content_type):
    """Máy không cài ``brotli`` (uv.lock không có): httpx không giải nén ``br`` mà để nguyên byte,
    nên đây không phải lỗi giải nén. Câu báo vẫn phải là câu cố định, không chép chữ máy chủ.
    """
    body = compressed(BR_BROKEN, "br", content_type)
    with pytest.raises(AIError) as info:
        generate(real_provider(vendor, body), vendor)
    assert str(info.value) in {bad_response_message(VENDOR[vendor]), BAD_SHAPE}
    client = stainless_client(vendor, lambda request: httpx2.Response(200, **body))
    result = env_file.check_api_key(NAMES[vendor], api_key=KEYS[vendor], client=client)
    assert result.message == bad_response_message(VENDOR[vendor])
    assert SERVER_TEXT not in str(info.value) + result.message


NETWORK_ERRORS = {
    "connect": (httpx2.ConnectError, "Không kết nối được tới"),
    "remote-protocol": (httpx2.RemoteProtocolError, "Không kết nối được tới"),
    "read": (httpx2.ReadError, "Không kết nối được tới"),
}


@pytest.mark.parametrize("vendor", ["anthropic", "openai"])
@pytest.mark.parametrize("kind", list(NETWORK_ERRORS))
def test_real_network_loss_still_says_no_connection(vendor, kind):
    error, expected = NETWORK_ERRORS[kind]

    def fail(request):
        raise error("mất mạng " + SERVER_TEXT)

    with pytest.raises(AIError) as info:
        generate(real_provider_with(vendor, fail), vendor)
    assert str(info.value).startswith(expected)
    assert SERVER_TEXT not in str(info.value)
    result = env_file.check_api_key(
        NAMES[vendor], api_key=KEYS[vendor], client=stainless_client(vendor, fail)
    )
    assert result.message.startswith(expected)
    assert SERVER_TEXT not in result.message


def real_provider_with(vendor, handler):
    cls = AnthropicProvider if vendor == "anthropic" else OpenAIProvider
    return cls(KEYS[vendor], client=stainless_client(vendor, handler))


@pytest.mark.parametrize("vendor", ["anthropic", "openai"])
@pytest.mark.parametrize("first", ["gzip", "connect"])
def test_retry_mix_reports_last_error(monkeypatch, vendor, first):
    """Thư viện thử lại: lần đầu nén hỏng rồi mất mạng (hoặc ngược lại). Câu báo theo lần cuối."""
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        gzip_now = (calls["n"] == 1) == (first == "gzip")
        if gzip_now:
            return httpx2.Response(200, **BROKEN_BODIES["gzip"])
        raise httpx2.ConnectError("từ chối")

    cls = anthropic.Anthropic if vendor == "anthropic" else openai.OpenAI
    client = cls(
        api_key=KEYS[vendor],
        max_retries=2,
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler)),
    )
    provider_cls = AnthropicProvider if vendor == "anthropic" else OpenAIProvider
    monkeypatch.setattr(time, "sleep", lambda seconds: None)  # bỏ thời gian chờ thử lại
    with pytest.raises(AIError) as info:
        generate(provider_cls(KEYS[vendor], client=client), vendor)
    if first == "gzip":
        assert str(info.value).startswith("Không kết nối được tới")
    else:
        assert str(info.value) == bad_response_message(VENDOR[vendor])


# ============================================ LC-T019-1: ký tự lạ trong tên mô hình


@pytest.mark.parametrize(
    "model",
    [
        "[a1](https://x.y)", "gpt-6.1](https://x.y)", "<img src=x onerror=alert(1)>",
        "gpt-6.1<script>", "**gpt-6.1**", "~~gpt-6.1~~", "gpt-6.1!", "gpt-6.1&x",
        "gpt-6.1'", 'gpt-6.1"', "gpt-6.1%20", "gpt\\6.1", "gpt-6.1+1", "gpt-6.1=1",
        "gpt-6.1,1", "gpt-6.1;1", "gpt-6.1#1", "gpt-6.1?x=1", "gpt-６.1", "gpt-6.1​",
        "gpt-6.1‮", "cửa-sắt-1", "gpt-6.1\x00", "gpt-6.1{}", "gpt-6.1$",
    ],
)  # fmt: skip
def test_strange_model_characters_rejected_without_echo(model):
    with pytest.raises(AIError) as info:
        validate_request("cửa sắt", "", [Candidate("openai", model), Candidate("openai", "o3")])
    message = str(info.value)
    assert message.startswith("Ứng viên 1: tên mô hình")
    assert model not in message
    assert "http" not in message and "<" not in message


MORE_REAL_MODELS = [
    "claude-3-haiku-20240307", "claude-sonnet-4-5@20250929",
    "anthropic.claude-3-5-sonnet-20240620-v1:0", "us.anthropic.claude-opus-4-1-20250805-v1:0",
    "gpt-4o-2024-08-06", "gpt-4o-realtime-preview", "o1-preview", "gpt-5.1-codex-max",
    "gemini-2.0-flash-001", "gemini-1.5-pro-002", "models/gemini-3-pro-preview",
    "gemini-2.5-flash-preview-05-20",
]  # fmt: skip


@pytest.mark.parametrize("model", REAL_MODELS + MORE_REAL_MODELS)
def test_real_model_names_pass_new_character_check(model):
    assert len(REAL_MODELS) == 42
    assert blind_test._MODEL_CHARS.fullmatch(model)
    provider = "anthropic" if "claude" in model else "gemini" if "gem" in model else "openai"
    validate_request("cửa sắt", "", [Candidate(provider, model, "medium")] * 2)


@pytest.mark.usefixtures("app_env")
def test_ui_markdown_model_name_blocked_no_link(project_root, monkeypatch):
    set_keys(monkeypatch, "ANTHROPIC_API_KEY", "OPENAI_API_KEY")
    calls = []
    monkeypatch.setattr(blind_test, "make_provider", lambda *a: calls.append(a))
    at = open_models_tab(project_root)
    at.text_input(key="blind-keyword").input("cửa sắt")
    at.text_input(key="blind-cand-0-model").input("[a1](https://x.y)")
    at.text_input(key="blind-cand-1-model").input("gpt-6.1")
    at.run()
    assert not at.exception
    assert at.button(key="blind-run").disabled
    captions = [c.value for c in at.caption]
    assert any("chỉ gồm chữ không dấu" in c for c in captions)
    shown = "\n".join(captions + [m.value for m in at.markdown] + [e.value for e in at.error])
    assert "https://x.y" not in shown
    assert calls == []


# ============================================ LC-T019-2: câu thiếu file không lộ đường dẫn


@pytest.mark.parametrize("sub", ["Người Dùng/Tài liệu", "C__Users_an/seo app", "thu-muc-x/con-y"])
def test_missing_config_message_has_no_machine_path(tmp_path, sub):
    path = tmp_path / sub / "ai.toml"
    with pytest.raises(AIError) as info:
        load_ai_config(path)
    message = str(info.value)
    assert message == "Không thấy file cấu hình AI: config/ai.toml."
    assert str(tmp_path) not in message
    for part in Path(sub).parts:
        assert part not in message


def test_other_config_read_errors_have_no_machine_path(tmp_path):
    folder = tmp_path / "thu-muc-bi-mat"
    folder.mkdir()
    as_dir = folder / "ai.toml"
    as_dir.mkdir()  # đường dẫn là thư mục: lỗi đọc khác (OSError)
    bad_text = folder / "ai2.toml"
    bad_text.write_bytes(b"\xff\xfe\x00rac")
    bad_toml = folder / "ai3.toml"
    bad_toml.write_text("[tasks\nx = ", encoding="utf-8")
    for path in (as_dir, bad_text, bad_toml):
        with pytest.raises(AIError) as info:
            load_ai_config(path)
        message = str(info.value)
        assert str(tmp_path) not in message
        assert "thu-muc-bi-mat" not in message


# ============================================================================ Lượt 2
# SL-T034-2: gói còn cài mà mất ``_client`` → gỡ biến như cũ; chỉ bỏ qua khi chính gói chưa cài.


@pytest.mark.usefixtures("evil_env")
@pytest.mark.parametrize("module_name", CLIENT_MODULES)
def test_l2_missing_client_module_hides_env_from_any_reader(monkeypatch, module_name):
    """Thư viện bản mới (giả lập) đọc biến ở một module khác: trong khối không thấy biến nào."""
    monkeypatch.setitem(sys.modules, module_name, None)
    with ignoring_custom_headers():
        assert all(os.environ.get(name) is None for name in IGNORED_ENV)
        assert os.environ.get("HTTPS_PROXY") == PROXY  # proxy vẫn giữ
        # Module còn lại vẫn được trỏ tạm như bình thường.
        other = next(n for n in CLIENT_MODULES if n != module_name)
        assert client_module(other).os is not os
    assert all(os.environ[name] == EVIL for name in IGNORED_ENV)
    assert not base_module._ENV_LOCK.locked()
    other_module = client_module(next(n for n in CLIENT_MODULES if n != module_name))
    assert other_module.os is os


@pytest.mark.usefixtures("evil_env")
@pytest.mark.parametrize("error", [ValueError, KeyboardInterrupt])
def test_l2_missing_client_module_restored_after_exception(monkeypatch, error):
    monkeypatch.setitem(sys.modules, "openai._client", None)
    with pytest.raises(error), ignoring_custom_headers():
        assert "OPENAI_CUSTOM_HEADERS" not in os.environ
        raise error()
    assert all(os.environ[name] == EVIL for name in IGNORED_ENV)
    assert client_module("anthropic._client").os is os
    assert not base_module._ENV_LOCK.locked()


@pytest.mark.usefixtures("evil_env")
def test_l2_missing_client_module_clients_still_clean(monkeypatch):
    """Một gói mất ``_client``, gói kia vẫn tạo client thật: client vẫn sạch."""
    monkeypatch.setitem(sys.modules, "openai._client", None)
    with ignoring_custom_headers():
        client = anthropic.Anthropic(api_key=KEYS["anthropic"])
    assert_no_evil(client._custom_headers)
    assert_no_evil(client.default_headers)
    assert all(os.environ[name] == EVIL for name in IGNORED_ENV)


@pytest.mark.usefixtures("evil_env")
@pytest.mark.parametrize("package", ["anthropic", "openai"])
def test_l2_package_not_installed_is_skipped_without_touching_env(monkeypatch, package):
    """Chính gói chưa cài: bỏ qua, không gỡ biến (gói kia vẫn được che qua ``os`` riêng)."""
    module_name = f"{package}._client"
    monkeypatch.setitem(sys.modules, package, None)
    monkeypatch.setitem(sys.modules, module_name, None)
    with ignoring_custom_headers():
        assert all(os.environ[name] == EVIL for name in IGNORED_ENV)
        other = next(n for n in CLIENT_MODULES if n != module_name)
        assert client_module(other).os is not os
    assert all(os.environ[name] == EVIL for name in IGNORED_ENV)
    assert not base_module._ENV_LOCK.locked()


@pytest.mark.usefixtures("evil_env")
def test_l2_missing_client_module_parallel_threads(monkeypatch):
    """Đường dự phòng (gỡ biến) chạy nhiều luồng: biến luôn được trả đủ, khóa nhả, không treo."""
    monkeypatch.setitem(sys.modules, "openai._client", None)
    errors: list[BaseException] = []
    seen: list[str | None] = []
    barrier = threading.Barrier(8)

    def work():
        try:
            barrier.wait()
            for _ in range(20):
                with ignoring_custom_headers():
                    seen.append(os.environ.get("OPENAI_CUSTOM_HEADERS"))
        except BaseException as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=work) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=60)
    assert not any(thread.is_alive() for thread in threads)
    assert errors == []
    assert seen == [None] * 160
    assert all(os.environ[name] == EVIL for name in IGNORED_ENV)
    assert not base_module._ENV_LOCK.locked()


# SL-T034-1: đuôi nối gạch sau số phiên bản bị che; số liệu, mã hàng trong bài giữ nguyên.


@pytest.mark.parametrize(
    ("text", "leaks"),
    [
        ("Viết bởi Gemini 2.5 Flash-Lite.", ["Flash", "Lite", "2.5"]),
        ("Tôi là Claude Opus 5.5-preview.", ["5.5", "preview"]),
        ("Tôi là Gemini 1.5 Pro-002.", ["Pro", "002"]),
        ("Gemini 2.5 Flash-Lite-preview-06-17 viết.", ["Lite", "preview", "06-17"]),
        ("Tôi là gpt-6.1 5.5-preview.", ["5.5", "preview"]),
    ],
)
def test_l2_hyphenated_suffixes_masked(text, leaks):
    shown = _mask_names(text, REAL_CANDIDATES)
    for leak in leaks:
        assert leak not in shown, (leak, shown)


@pytest.mark.parametrize(
    "text",
    [
        "Thép dày 5.5 mm.",
        "Cổng 3 cánh.",
        "Làm từ năm 2025.",
        "Sơn loại 2-3 lớp.",
        "Mã SP-002, mã CS-15.2.",
        "Bản lề 3-4 cái, khóa 2-3-5.",
        "Cửa pro-max, cửa mini-2, ray lite-3.",
    ],
)
def test_l2_article_numbers_and_codes_untouched(text):
    assert _mask_names(text, REAL_CANDIDATES) == text


@pytest.mark.parametrize(
    ("text", "kept"),
    [
        ("Claude: sơn loại 2-3 lớp.", "loại 2-3 lớp"),
        ("Gemini nói mã SP-002 bền.", "mã SP-002"),
        ("Opus 5.5mm sai đơn vị.", "5.5mm"),
        ("GPT 6.1 - bản thử.", "- bản thử"),
        ("Claude Sonnet 4.5 – nhanh.", "– nhanh"),
    ],
)
def test_l2_text_after_masked_name_but_not_glued_kept(text, kept):
    shown = _mask_names(text, REAL_CANDIDATES)
    assert MASK in shown
    assert kept in shown


@pytest.mark.parametrize(
    "text",
    [
        "Claude 1" + "-1.1" * 5000 + "x",
        "Claude pro" + "-a.1" * 5000 + "_x",
        ("Claude 1-" + "1." * 20 + "x ") * 2000,
        "gpt 1-" * 20000,
    ],
    ids=["gach-so", "gach-chu", "lap", "lap-gach"],
)
def test_l2_hyphen_suffix_adversarial_text_is_fast(text):
    # Bài thử mù tối đa BLIND_MAX_TOKENS (2000) token, cỡ 10.000 ký tự; ở đây 20.000+.
    start = time.perf_counter()
    _mask_names(text, REAL_CANDIDATES)
    assert time.perf_counter() - start < 3.0
