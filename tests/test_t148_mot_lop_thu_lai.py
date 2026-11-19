"""T-148 (Thợ Máy): một lớp thử lại (LC-T141-12) và gọi được từ luồng thường (LC-T141-9).

- Provider tạo bằng ``single_attempt=True`` gửi **đúng một request** mỗi lần gọi, kể cả khi máy
  chủ trả 503, 429 hay rớt mạng (thư viện không tự thử lại). Mặc định giữ như cũ: Gemini gửi tối
  đa 3 lần, OpenAI và Anthropic tối đa 4 lần (``max_retries=3``).
- ``AIRouter(..., single_attempt=True)`` tạo provider ở chế độ đó; router mặc định gọi
  ``make_provider(hãng, settings)`` như cũ (các test cũ thay ``make_provider`` bằng hàm 2 tham
  số vẫn chạy).
- Các file của phiếu không nhập ``streamlit``; provider chạy được trong ``threading.Thread``.

Đếm request qua đường truyền giả (``MockTransport``) gắn vào client thật của từng thư viện, giữ
nguyên mọi tham số app truyền (``max_retries``, ``retry_options``). Không gọi mạng; ``time.sleep``
được thay để các lần thử lại mặc định không phải chờ.
"""

from __future__ import annotations

import ast
import subprocess
import sys
import threading
import time
from pathlib import Path

import anthropic
import httpx
import httpx2
import openai
import pydantic
import pytest
from google import genai

from seo_app.ai import registry as ai_registry
from seo_app.ai.base import AIError, TaskConfig
from seo_app.ai.registry import AIRouter, make_provider
from seo_app.config import PROJECT_ROOT, Settings

KEY = "khoa-gia-t148"
SETTINGS = Settings(anthropic_api_key=KEY, openai_api_key=KEY, gemini_api_key=KEY)
MODEL = "mo-hinh-thu"
VENDORS = ("gemini", "openai", "anthropic")
# Số request khi máy chủ trả 503 mãi: mặc định (như cũ) và khi lượt chạy yêu cầu một lần.
DEFAULT_REQUESTS = {"gemini": 3, "openai": 4, "anthropic": 4}


class Answer(pydantic.BaseModel):
    text: str


def task(vendor: str) -> TaskConfig:
    return TaskConfig(name="write", provider=vendor, model=MODEL, effort="high")


class Wire:
    """Đường truyền giả cho cả 3 thư viện: ghi mỗi request, trả lời theo ``reply``."""

    def __init__(self, reply):
        self.reply = reply
        self.requests: list[str] = []
        self.kwargs: dict[str, dict] = {}

    def handle(self, vendor: str, response_cls):
        def handler(request):
            self.requests.append(vendor)
            return self.reply(vendor, response_cls)

        return handler


@pytest.fixture
def wire(monkeypatch):
    """Bọc hàm tạo client của 3 thư viện: giữ nguyên tham số app truyền, chỉ gắn đường truyền giả.
    ``time.sleep`` không chờ (ghi lại số giây) để lần thử lại mặc định chạy nhanh."""
    holder: dict[str, Wire] = {}
    slept: list[float] = []
    real_anthropic, real_openai, real_genai = anthropic.Anthropic, openai.OpenAI, genai.Client
    monkeypatch.setattr(time, "sleep", slept.append)

    def make_anthropic(**kwargs):
        holder["wire"].kwargs["anthropic"] = kwargs
        transport = httpx2.MockTransport(holder["wire"].handle("anthropic", httpx2.Response))
        return real_anthropic(**kwargs, http_client=httpx2.Client(transport=transport))

    def make_openai(**kwargs):
        holder["wire"].kwargs["openai"] = kwargs
        transport = httpx2.MockTransport(holder["wire"].handle("openai", httpx2.Response))
        return real_openai(**kwargs, http_client=httpx2.Client(transport=transport))

    def make_genai(**kwargs):
        holder["wire"].kwargs["gemini"] = kwargs
        transport = httpx.MockTransport(holder["wire"].handle("gemini", httpx.Response))
        args = {"client_args": {"transport": transport}}  # giữ retry_options app truyền
        options = kwargs["http_options"].model_copy(update=args)
        return real_genai(**{**kwargs, "http_options": options})

    monkeypatch.setattr(anthropic, "Anthropic", make_anthropic)
    monkeypatch.setattr(openai, "OpenAI", make_openai)
    monkeypatch.setattr(genai, "Client", make_genai)

    def build(reply) -> Wire:
        holder["wire"] = Wire(reply)
        return holder["wire"]

    build.slept = slept
    return build


def status_reply(code: int):
    bodies = {
        "gemini": {"error": {"code": code, "message": "x", "status": "UNAVAILABLE"}},
        "openai": {"error": {"message": "x", "type": "x", "code": None, "param": None}},
        "anthropic": {"type": "error", "error": {"type": "overloaded_error", "message": "x"}},
    }
    return lambda vendor, response_cls: response_cls(code, json=bodies[vendor])


def broken_network(vendor, response_cls):
    raise (httpx.ConnectError if vendor == "gemini" else httpx2.ConnectError)("rớt mạng")


def call(provider, vendor):
    return provider.generate(task(vendor), system="s", prompt="p", schema=Answer)


# ===================================================================== một request mỗi lần


@pytest.mark.parametrize("vendor", VENDORS)
@pytest.mark.parametrize(
    ("reply", "kind"),
    [(status_reply(503), "busy"), (status_reply(429), "rate"), (broken_network, "network")],
    ids=["503", "429", "rot-mang"],
)
def test_single_attempt_sends_exactly_one_request(wire, vendor, reply, kind):
    line = wire(reply)
    provider = make_provider(vendor, SETTINGS, single_attempt=True)
    with pytest.raises(AIError) as info:
        call(provider, vendor)
    assert line.requests == [vendor]  # đúng một request, thư viện không tự gọi lại
    assert info.value.kind == kind
    assert wire.slept == []  # không chờ để thử lại


@pytest.mark.parametrize("vendor", VENDORS)
def test_default_still_retries_like_before(wire, vendor):
    # Các trang đang có (Soạn bài, Kế hoạch, Cài đặt…) giữ cách cũ: thư viện tự thử lại.
    line = wire(status_reply(503))
    with pytest.raises(AIError) as info:
        call(make_provider(vendor, SETTINGS), vendor)
    assert line.requests == [vendor] * DEFAULT_REQUESTS[vendor]
    assert info.value.kind == "busy"
    assert len(wire.slept) == DEFAULT_REQUESTS[vendor] - 1


@pytest.mark.parametrize("single_attempt", [False, True], ids=["mac-dinh", "mot-lan"])
def test_client_options_passed_to_each_library(wire, single_attempt):
    line = wire(status_reply(503))
    for vendor in VENDORS:
        if single_attempt:
            make_provider(vendor, SETTINGS, single_attempt=True)
        else:
            make_provider(vendor, SETTINGS)
    retries = 0 if single_attempt else 3
    assert line.kwargs["anthropic"]["max_retries"] == retries
    assert line.kwargs["openai"]["max_retries"] == retries
    attempts = line.kwargs["gemini"]["http_options"].retry_options.attempts
    assert attempts == (1 if single_attempt else 3)


def test_single_attempt_success_is_one_request(wire):
    answer = {
        "candidates": [
            {
                "content": {"role": "model", "parts": [{"text": '{"text": "xong"}'}]},
                "finishReason": "STOP",
            }
        ]
    }
    line = wire(lambda vendor, response_cls: response_cls(200, json=answer))
    result = call(make_provider("gemini", SETTINGS, single_attempt=True), "gemini")
    assert result == Answer(text="xong") and line.requests == ["gemini"]


# ============================================================================ router


def test_router_single_attempt_builds_providers_in_that_mode(monkeypatch):
    seen: list[tuple[tuple, dict]] = []

    def fake_make(*args, **kwargs):
        seen.append((args, kwargs))
        return object()

    monkeypatch.setattr(ai_registry, "make_provider", fake_make)
    tasks = {"write": task("gemini"), "alt": task("openai")}
    router = AIRouter(tasks, SETTINGS, prepare=(), single_attempt=True)
    assert router.single_attempt is True and seen == []  # lười: chưa tạo gì
    router.get("write")
    router.get("alt")
    router.get("write")  # mỗi hãng một provider, tạo một lần
    assert seen == [
        (("gemini", SETTINGS), {"single_attempt": True}),
        (("openai", SETTINGS), {"single_attempt": True}),
    ]


def test_default_router_calls_make_provider_like_before(monkeypatch):
    # Test cũ thay make_provider bằng hàm đúng 2 tham số (lambda name, settings: …): vẫn chạy.
    built: list[str] = []
    monkeypatch.setattr(
        ai_registry, "make_provider", lambda name, settings: built.append(name) or object()
    )
    router = AIRouter({"write": task("gemini")}, SETTINGS)
    assert router.single_attempt is False and built == ["gemini"]  # prepare mặc định


def test_router_single_attempt_reaches_the_library(wire):
    line = wire(status_reply(503))
    router = AIRouter({"write": task("openai")}, SETTINGS, prepare=(), single_attempt=True)
    provider, config = router.get("write")
    with pytest.raises(AIError):
        provider.generate(config, system="s", prompt="p", schema=Answer)
    assert line.requests == ["openai"]


# ================================================================= LC-T141-9: không streamlit

TICKET_FILES = [
    PROJECT_ROOT / "seo_app" / "ai" / name
    for name in (
        "base.py",
        "gemini_provider.py",
        "openai_provider.py",
        "anthropic_provider.py",
        "limits.py",
        "registry.py",
    )
]


@pytest.mark.parametrize("path", TICKET_FILES, ids=lambda p: p.name)
def test_ticket_files_do_not_import_streamlit(path: Path):
    names: list[str] = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names.append(node.module or "")
    assert names, "phải đọc được các dòng import"
    assert [n for n in names if n.split(".")[0] == "streamlit"] == []


def test_importing_ai_layer_does_not_load_streamlit():
    code = (
        "import sys\n"
        "import seo_app.ai.limits, seo_app.ai.registry, seo_app.ai.gemini_provider\n"
        "import seo_app.ai.openai_provider, seo_app.ai.anthropic_provider\n"
        "print('streamlit' in sys.modules)\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        check=True,
    )
    assert result.stdout.strip() == "False"


def test_provider_runs_in_a_plain_thread(wire):
    # Lượt chạy gọi AI trong threading.Thread thường (không ScriptRunContext): chạy được, lỗi AI
    # về tới luồng gọi với đúng loại.
    parts = [{"text": '{"text": "xong"}'}]
    answer = {"candidates": [{"content": {"role": "model", "parts": parts}}]}
    replies = [(200, answer), (503, {"error": {"code": 503, "status": "UNAVAILABLE"}})]

    def reply(vendor, response_cls):
        code, body = replies.pop(0)
        return response_cls(code, json=body)

    line = wire(reply)
    outcome: dict[str, object] = {}

    def work():
        try:
            provider = make_provider("gemini", SETTINGS, single_attempt=True)  # tạo trong luồng
            outcome["answer"] = call(provider, "gemini")
            try:
                call(provider, "gemini")
            except AIError as exc:
                outcome["error"] = exc
        except Exception as exc:  # noqa: BLE001 - ghi lại mọi lỗi lạ (NoSessionContext…) để kiểm
            outcome["unexpected"] = exc

    thread = threading.Thread(target=work)
    thread.start()
    thread.join(timeout=60)
    assert not thread.is_alive()
    assert "unexpected" not in outcome, outcome.get("unexpected")
    assert outcome["answer"] == Answer(text="xong")
    assert outcome["error"].kind == "busy"  # type: ignore[attr-defined]
    assert line.requests == ["gemini", "gemini"]
