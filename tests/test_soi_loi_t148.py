"""Soi Lỗi T-148: một lớp thử lại, loại lỗi AI, mục ``[auto]``, ngày Thái Bình Dương, mẫu che token.

Không gọi AI thật. Khác test của Thợ Máy (đường truyền giả gắn vào client qua ``http_client`` /
``client_args``), ở đây chặn ở **tầng cuối** ``HTTPTransport.handle_request`` của ``httpx`` (Gemini)
và ``httpx2`` (OpenAI, Anthropic): thư viện tự dựng client mặc định với đúng tham số app truyền,
nên mọi lần gọi lại ngầm ở bất kỳ tầng nào phía trên đều bị đếm. ``time.sleep`` được thay.

- Chế độ ``single_attempt``: đúng 1 request với mọi lỗi thư viện vẫn tự thử lại (500, 502, 503,
  504, 408, 429, 529, quá giờ, rớt mạng), kể cả khi máy chủ gửi ``x-should-retry``, ``retry-after``.
- Chế độ thường: số request như cũ (Gemini 3, OpenAI 4, Anthropic 4).
- Các request phụ do chính app gửi (không phải thư viện thử lại): đúng số đã ghi trong báo cáo
  Thợ Máy, để sổ đếm của T-149 biết phải cộng thêm.
- Lớp bảo vệ cũ (T-026 W4, T-028, T-034) giữ nguyên khi ``single_attempt=True``.
- Lỗi mới:
  - SL-T148-1: lỗi giữa luồng SSE của Anthropic ra loại ``other``;
  - SL-T148-2: mẫu che chỉ có ``cfut_``, thiếu ``cfat_``, ``cfk_`` của Cloudflare;
  - SL-T148-3: ``[auto]`` sai giá trị thì báo lỗi, thay vì dùng mặc định như LC-T144-4;
  - SL-T148-4: số nguyên rất lớn ném ``OverflowError``.
"""

from __future__ import annotations

import json
import random
import time
from datetime import UTC, date, datetime, timedelta
from datetime import time as dtime

import httpx
import httpx2
import pydantic
import pytest

from seo_app.ai import registry as ai_registry
from seo_app.ai.base import AI_ERROR_KINDS, AIError, TaskConfig, clamp_retry_after, redact_secrets
from seo_app.ai.limits import (
    PACIFIC,
    VIETNAM,
    AutoLimits,
    load_auto_limits,
    pacific_day,
    reset_at_vn,
    seconds_to_wait,
)
from seo_app.ai.registry import AIRouter, make_provider
from seo_app.config import Settings

KEY = "khoa-gia-sl148"  # thư viện chỉ cần chuỗi khác rỗng; không giống khóa thật
SERVER = "MAYCHU-SL148"  # chữ máy chủ viết: không được lọt vào câu báo
SETTINGS = Settings(anthropic_api_key=KEY, openai_api_key=KEY, gemini_api_key=KEY)
VENDORS = ("gemini", "openai", "anthropic")
LIBS = {"gemini": httpx, "openai": httpx2, "anthropic": httpx2}
DEFAULT_REQUESTS = {"gemini": 3, "openai": 4, "anthropic": 4}
HOSTS = {
    "gemini": "generativelanguage.googleapis.com",
    "openai": "api.openai.com",
    "anthropic": "api.anthropic.com",
}


class Answer(pydantic.BaseModel):
    text: str


def task(vendor: str, **kwargs) -> TaskConfig:
    return TaskConfig(name="write", provider=vendor, model=kwargs.pop("model", "mo-hinh-thu"),
                      effort="high", **kwargs)  # fmt: skip


class Wire:
    """Ghi mọi request tới tầng ``HTTPTransport`` và trả lời theo ``reply(vendor, mod, request, n)``
    (``n``: thứ tự request trong ca, từ 0)."""

    def __init__(self) -> None:
        self.calls: list[dict] = []
        self.slept: list[float] = []
        self.reply = None
        self.vendor = ""


@pytest.fixture
def wire(monkeypatch):
    line = Wire()

    def install(mod, lib):
        def handle_request(self, request):
            line.calls.append(
                {"lib": lib, "host": request.url.host, "headers": dict(request.headers)}
            )
            return line.reply(line.vendor, mod, request, len(line.calls) - 1)

        monkeypatch.setattr(mod.HTTPTransport, "handle_request", handle_request)

    install(httpx, "httpx")
    install(httpx2, "httpx2")
    monkeypatch.setattr(time, "sleep", line.slept.append)
    return line


def status_body(vendor: str, code: int, message: str = SERVER, error_code=None) -> dict:
    if vendor == "gemini":
        status = {429: "RESOURCE_EXHAUSTED", 503: "UNAVAILABLE", 400: "INVALID_ARGUMENT"}
        return {"error": {"code": code, "message": message, "status": status.get(code, "X")}}
    if vendor == "openai":
        return {"error": {"message": message, "type": "x", "code": error_code,
                          "param": None}}  # fmt: skip
    return {"type": "error", "error": {"type": "api_error", "message": message}}


def status(code: int, headers: dict | None = None):
    def reply(vendor, mod, request, n):
        return mod.Response(code, json=status_body(vendor, code), headers=headers or {})

    return reply


def raising(name: str):
    def reply(vendor, mod, request, n):
        raise getattr(mod, name)(SERVER, request=request)

    return reply


def run(wire: Wire, vendor: str, reply, *, single: bool, **task_kwargs):
    wire.vendor, wire.reply = vendor, reply
    if single:
        provider = make_provider(vendor, SETTINGS, single_attempt=True)
    else:
        provider = make_provider(vendor, SETTINGS)
    return provider.generate(task(vendor, **task_kwargs), system="s", prompt="p", schema=Answer)


def failed(wire: Wire, vendor: str, reply, *, single: bool, **task_kwargs) -> AIError:
    with pytest.raises(AIError) as info:
        run(wire, vendor, reply, single=single, **task_kwargs)
    error = info.value
    assert SERVER not in str(error) and KEY not in str(error)
    assert {c["host"] for c in wire.calls} <= {HOSTS[vendor]}
    return error


# ======================================================= (1) một lớp thử lại: đếm request thật

ONE_SHOT = [
    (status(500), "busy"),
    (status(502), "busy"),
    (status(503), "busy"),
    (status(504), "busy"),
    (status(529), "busy"),
    (status(408), "timeout"),
    (status(429), "rate"),
    (raising("ConnectError"), "network"),
    (raising("RemoteProtocolError"), "network"),
    (raising("ReadTimeout"), "timeout"),
    (raising("ConnectTimeout"), "timeout"),
    (raising("PoolTimeout"), "timeout"),
]
ONE_SHOT_IDS = ["500", "502", "503", "504", "529", "408", "429", "mang", "dong-giua",
                "doc-qua-gio", "noi-qua-gio", "cho-qua-gio"]  # fmt: skip


@pytest.mark.parametrize("vendor", VENDORS)
@pytest.mark.parametrize(("reply", "kind"), ONE_SHOT, ids=ONE_SHOT_IDS)
def test_mot_lan_gui_dung_mot_request_o_tang_cuoi(wire, vendor, reply, kind):
    error = failed(wire, vendor, reply, single=True)
    assert len(wire.calls) == 1, [c["host"] for c in wire.calls]
    assert wire.slept == []  # không thư viện nào ngủ chờ thử lại
    assert error.kind == kind


@pytest.mark.parametrize("vendor", ("openai", "anthropic"))
@pytest.mark.parametrize(
    "headers",
    [{"x-should-retry": "true"}, {"retry-after": "30"}, {"retry-after-ms": "500"}],
    ids=["x-should-retry", "retry-after", "retry-after-ms"],
)
@pytest.mark.parametrize("code", [400, 401, 429, 503], ids=["400", "401", "429", "503"])
def test_mot_lan_khong_nghe_may_chu_bao_thu_lai(wire, vendor, headers, code):
    # Máy chủ (hay proxy) bảo «thử lại đi» bằng header: chế độ một lần vẫn chỉ 1 request.
    failed(wire, vendor, status(code, headers), single=True)
    assert len(wire.calls) == 1 and wire.slept == []


@pytest.mark.parametrize("vendor", VENDORS)
@pytest.mark.parametrize(
    "reply",
    [status(500), status(408), status(429), raising("ConnectError"), raising("ReadTimeout")],
    ids=["500", "408", "429", "mang", "qua-gio"],
)
def test_mac_dinh_van_thu_lai_nhu_cu(wire, vendor, reply):
    failed(wire, vendor, reply, single=False)
    assert len(wire.calls) == DEFAULT_REQUESTS[vendor]
    assert len(wire.slept) == DEFAULT_REQUESTS[vendor] - 1


def test_thanh_cong_mot_request(wire):
    answer = {"candidates": [{"content": {"role": "model", "parts": [{"text": '{"text": "ok"}'}]},
                              "finishReason": "STOP"}]}  # fmt: skip
    result = run(wire, "gemini", lambda v, mod, r, n: mod.Response(200, json=answer), single=True)
    assert result == Answer(text="ok") and len(wire.calls) == 1


@pytest.mark.parametrize("single", [False, True], ids=["mac-dinh", "mot-lan"])
def test_router_ca_ba_hang_den_tang_cuoi(wire, single):
    tasks = {name: task(name) for name in VENDORS}
    router = AIRouter(tasks, SETTINGS, prepare=(), single_attempt=single)
    for vendor in VENDORS:
        wire.calls.clear()
        wire.vendor, wire.reply = vendor, status(503)
        provider, config = router.get(vendor)
        with pytest.raises(AIError):
            provider.generate(config, system="s", prompt="p", schema=Answer)
        assert len(wire.calls) == (1 if single else DEFAULT_REQUESTS[vendor]), vendor


# ---------------------------------------- request phụ do chính app gửi (ghi nhận cho T-149)

THINK = f"{SERVER} thinking level is not supported"
REASONING = f"{SERVER} Unsupported parameter: 'reasoning.effort'"


def then_503(first_code: int, first_message: str, error_code: str | None = None):
    def reply(vendor, mod, request, n):
        if n == 0:
            body = status_body(vendor, first_code, first_message, error_code)
            return mod.Response(first_code, json=body)
        return mod.Response(503, json=status_body(vendor, 503))

    return reply


def gemini_two_rounds(vendor, mod, request, n):
    text = "ghi chép" if n == 0 else '{"text": "ok"}'
    parts = [{"text": text}]
    body = {"candidates": [{"content": {"role": "model", "parts": parts}, "finishReason": "STOP"}]}
    return mod.Response(200, json=body)


def sse(*events: tuple[str, dict]) -> bytes:
    return "".join(f"event: {name}\ndata: {json.dumps(data)}\n\n" for name, data in events).encode()


START = (
    "message_start",
    {
        "type": "message_start",
        "message": {
            "id": "msg_1",
            "type": "message",
            "role": "assistant",
            "model": "mo-hinh-thu",
            "content": [],
            "stop_reason": None,
            "stop_sequence": None,
            "usage": {"input_tokens": 1, "output_tokens": 1},
        },
    },
)
TEXT = [
    ("content_block_start", {"type": "content_block_start", "index": 0,
                             "content_block": {"type": "text", "text": ""}}),
    ("content_block_delta", {"type": "content_block_delta", "index": 0,
                             "delta": {"type": "text_delta", "text": '{"text": "ok"}'}}),
    ("content_block_stop", {"type": "content_block_stop", "index": 0}),
]  # fmt: skip


def anthropic_stream(*events):
    def reply(vendor, mod, request, n):
        headers = {"content-type": "text/event-stream"}
        return mod.Response(200, content=sse(START, *events), headers=headers)

    return reply


PAUSE = anthropic_stream(
    *TEXT,
    ("message_delta", {"type": "message_delta", "delta": {"stop_reason": "pause_turn",
                       "stop_sequence": None}, "usage": {"output_tokens": 1}}),
    ("message_stop", {"type": "message_stop"}),
)  # fmt: skip


@pytest.mark.parametrize(
    ("vendor", "reply", "task_kwargs", "requests", "kind"),
    [
        ("gemini", then_503(400, THINK), {}, 2, "busy"),
        ("gemini", gemini_two_rounds, {"model": "gemini-2.5-flash", "web_search": True}, 2, None),
        ("openai", then_503(400, REASONING, "unsupported_parameter"), {}, 2, "busy"),
        ("anthropic", PAUSE, {}, 5, "timeout"),
    ],
    ids=["gemini-thinking", "gemini-tim-web-2-luot", "openai-reasoning", "anthropic-pause-turn"],
)
def test_request_phu_cua_app_dung_so_da_ghi(wire, vendor, reply, task_kwargs, requests, kind):
    # Mỗi request phụ là app gọi lại với thông số khác (không phải thư viện thử lại): chế độ một
    # lần vẫn gửi chúng, và lần gọi sau cũng không bị thư viện nhân lên. Sổ đếm theo lần gọi
    # generate (T-149) phải cộng đúng chừng này (báo cáo Thợ Máy, mục «Ghi nhận»).
    if kind is None:
        assert run(wire, vendor, reply, single=True, **task_kwargs) == Answer(text="ok")
    else:
        assert failed(wire, vendor, reply, single=True, **task_kwargs).kind == kind
    assert len(wire.calls) == requests and wire.slept == []


# ================================================= (5) lớp bảo vệ cũ khi single_attempt=True


@pytest.mark.parametrize("vendor", VENDORS)
@pytest.mark.parametrize("single", [False, True], ids=["mac-dinh", "mot-lan"])
def test_bien_moi_truong_khong_doi_duong_goi_hay_header(wire, monkeypatch, tmp_path, vendor,
                                                         single):  # fmt: skip
    replay = tmp_path / "replay"
    replay.mkdir()
    for name, value in {
        "ANTHROPIC_BASE_URL": "https://lech.example",
        "OPENAI_BASE_URL": "https://lech.example/v1",
        "GOOGLE_GEMINI_BASE_URL": "https://lech.example",
        "ANTHROPIC_CUSTOM_HEADERS": "X-Lech-Anthropic: 1",
        "OPENAI_CUSTOM_HEADERS": "X-Lech-OpenAI: 1",
        "GOOGLE_GENAI_CLIENT_MODE": "replay",
        "GOOGLE_GENAI_REPLAYS_DIRECTORY": str(replay),
        "GOOGLE_GENAI_REPLAY_ID": "sl148",
    }.items():
        monkeypatch.setenv(name, value)
    failed(wire, vendor, status(503), single=single)
    assert wire.calls and {c["host"] for c in wire.calls} == {HOSTS[vendor]}
    assert all(c["lib"] == ("httpx" if vendor == "gemini" else "httpx2") for c in wire.calls)
    headers = {name.lower() for c in wire.calls for name in c["headers"]}
    assert not {name for name in headers if "lech" in name}
    assert list(replay.iterdir()) == []


# ======================================================== (2) loại lỗi: lỗi giữa luồng SSE


def stream_error(error_type: str):
    event = {"type": "error", "error": {"type": error_type, "message": SERVER}}
    return anthropic_stream(("error", event))


@pytest.mark.xfail(
    strict=True,
    reason="SL-T148-1: lỗi đến giữa luồng SSE (mã 200) thành APIStatusError status_code 200, "
    "status_kind(200) = other; nên đọc loại lỗi cố định error.type như Gemini đọc status",
)
@pytest.mark.parametrize(
    ("error_type", "kind"),
    [("overloaded_error", "busy"), ("api_error", "busy"), ("rate_limit_error", "rate")],
    ids=["overloaded", "api-error", "rate-limit"],
)
def test_anthropic_loi_giua_luong_sse_dung_loai(wire, error_type, kind):
    error = failed(wire, "anthropic", stream_error(error_type), single=True)
    assert len(wire.calls) == 1
    assert error.kind == kind


def test_anthropic_loi_giua_luong_sse_khong_lo_chu_may_chu(wire):
    # Phần chạy được hôm nay: câu cố định (có từ trước), một request, không chép chữ máy chủ.
    error = failed(wire, "anthropic", stream_error("overloaded_error"), single=True)
    assert str(error) == "Anthropic báo lỗi 200. Thử lại sau ít phút."
    assert len(wire.calls) == 1


# ------------------------------------------- 429 của Gemini theo khuôn người dùng dán (2025)

# Lỗi 429 người dùng dán trên diễn đàn Google AI (12/2025): câu chung có chữ «billing», chi tiết
# ghi hạn mức THEO PHÚT, máy chủ bảo chờ 7 giây.
QUOTA_TEXT = f"{SERVER} You exceeded your current quota, please check your plan and billing details"
PER_MINUTE = "GenerateRequestsPerMinutePerProjectPerModel-FreeTier"


def gemini_429(quota_id: str, delay: str = "7s"):
    violation = {"quotaMetric": "generate_content_free_tier_requests", "quotaId": quota_id}
    details = [
        {"@type": "type.googleapis.com/google.rpc.QuotaFailure", "violations": [violation]},
        {"@type": "type.googleapis.com/google.rpc.RetryInfo", "retryDelay": delay},
    ]
    error = {"code": 429, "message": QUOTA_TEXT, "status": "RESOURCE_EXHAUSTED", "details": details}
    return lambda vendor, mod, request, n: mod.Response(429, json={"error": error})


@pytest.mark.xfail(
    strict=True,
    reason="SL-T148-5: câu 429 thật của Gemini có chữ «billing» cả khi chỉ vượt hạn mức theo phút; "
    "phiếu (yêu cầu 3) xếp mọi 429 có «billing» là quota_day, lượt chạy tự động sẽ dừng cả lô",
)
def test_gemini_429_theo_phut_khuon_that_la_rate(wire):
    error = failed(wire, "gemini", gemini_429(PER_MINUTE), single=True)
    assert len(wire.calls) == 1
    assert error.kind == "rate"


# ================================================ (3) che token Cloudflare (LC-T140-2)

# Token giả dựng lúc chạy, dạng tài liệu Cloudflare: tiền tố + 40 ký tự + mã kiểm (CRC32, hex).
BODY = "SoiLoiT148" * 4
CHECK = "0badc0de"


@pytest.mark.parametrize(
    "template",
    [
        "Lỗi: {t}",
        '{{"errors": [{{"message": "bad {t}"}}]}}',
        "https://api.cloudflare.com/client/v4/x/{t}/y",
        "x{t}",
        "a={t}&b=1",
    ],
    ids=["cau", "json", "duong-dan", "dinh-chu", "tham-so"],
)
def test_che_cfut_o_moi_cho(template):
    text = redact_secrets(template.format(t="cfut_" + BODY + CHECK))
    assert BODY not in text and "[đã ẩn]" in text


@pytest.mark.xfail(
    strict=True,
    reason="SL-T148-2: tài liệu Cloudflare (token-formats) có cfat_ (token tài khoản, dùng được "
    "Workers AI) và cfk_ (Global API Key); mẫu chỉ có cfut_",
)
@pytest.mark.parametrize("prefix", ["cfat_", "cfk_"], ids=["cfat", "cfk"])
def test_che_token_cloudflare_cac_tien_to_khac(prefix):
    text = redact_secrets(f"Lỗi khi gọi Cloudflare: {prefix}{BODY}{CHECK}")
    assert BODY not in text and "[đã ẩn]" in text


# ============================================ (4) ngày Thái Bình Dương, giãn nhịp, trần ngày


def test_moc_dat_lai_ca_nam_2026_moi_15_phut():
    # Mọi thời điểm năm 2026 (bước 15 phút, cả hai ngày đổi giờ của Mỹ): lần đặt lại kế tiếp là
    # nửa đêm Los Angeles ngay sau đó, 14:00 hoặc 15:00 giờ Việt Nam, cách không quá 25 giờ.
    now = datetime(2026, 1, 1, tzinfo=UTC)
    end = datetime(2027, 1, 1, tzinfo=UTC)
    while now < end:
        reset = reset_at_vn(now)
        assert reset.utcoffset() == timedelta(hours=7) and reset > now
        assert reset - now <= timedelta(hours=25)
        assert reset.astimezone(PACIFIC).time() == dtime(0)
        assert (reset.hour, reset.minute) in ((14, 0), (15, 0))
        assert pacific_day(reset) == pacific_day(now) + timedelta(days=1)
        assert pacific_day(reset - timedelta(microseconds=1)) == pacific_day(now)
        now += timedelta(minutes=15)


@pytest.mark.parametrize(
    ("vn", "day", "reset"),
    [
        # 08/03/2026: Mỹ sang giờ mùa hè lúc 2:00 sáng; nửa đêm 08/03 còn giờ mùa đông.
        ((2026, 3, 8, 14, 59), date(2026, 3, 7), (2026, 3, 8, 15, 0)),
        ((2026, 3, 8, 15, 0), date(2026, 3, 8), (2026, 3, 9, 14, 0)),
        ((2026, 3, 9, 13, 59), date(2026, 3, 8), (2026, 3, 9, 14, 0)),
        ((2026, 3, 9, 14, 0), date(2026, 3, 9), (2026, 3, 10, 14, 0)),
        # 01/11/2026: Mỹ về giờ mùa đông lúc 2:00 sáng; nửa đêm 01/11 còn giờ mùa hè.
        ((2026, 11, 1, 13, 59), date(2026, 10, 31), (2026, 11, 1, 14, 0)),
        ((2026, 11, 1, 14, 0), date(2026, 11, 1), (2026, 11, 2, 15, 0)),
        ((2026, 11, 2, 14, 30), date(2026, 11, 1), (2026, 11, 2, 15, 0)),
        ((2026, 11, 20, 15, 0), date(2026, 11, 20), (2026, 11, 21, 15, 0)),
    ],
    ids=["0803-truoc", "0803-dat-lai", "0903-truoc", "0903-dat-lai", "0111-truoc",
         "0111-dat-lai", "0211-giua", "2011-hom-nay"],
)  # fmt: skip
def test_ngay_doi_gio_cua_my(vn, day, reset):
    now = datetime(*vn, tzinfo=VIETNAM)
    assert pacific_day(now) == day
    assert reset_at_vn(now) == datetime(*reset, tzinfo=VIETNAM)


def test_cho_khong_am_khong_qua_mot_nhip():
    rng = random.Random(148)
    for _ in range(5000):
        min_seconds = rng.uniform(1, 120)
        last = rng.uniform(0, 1e6)
        now = last + rng.uniform(-300, 300)
        wait = seconds_to_wait(last, now, min_seconds)
        assert 0.0 <= wait <= min_seconds
        if now >= last:
            assert wait == pytest.approx(max(0.0, min_seconds - (now - last)))
    assert seconds_to_wait(None, 5.0, 6) == 0.0


# --------------------------------------------- [auto] chịu lỗi (LC-T144-4) và số rất lớn


def toml(tmp_path, body: str):
    path = tmp_path / "ai.toml"
    path.write_text(body, encoding="utf-8")
    return path


@pytest.mark.xfail(
    strict=True,
    reason="SL-T148-3: LC-T144-4 (Lá Chắn T-144, 20/11 13:31, sau khi viết mã) đòi giá trị "
    "[auto] sai thì dùng 6 và 0, câu báo cố định, app không sập; mã hiện báo AIError dừng",
)
@pytest.mark.parametrize(
    "line",
    [
        'min_seconds_between_calls = "6"',
        "min_seconds_between_calls = true",
        "min_seconds_between_calls = -5",
        "min_seconds_between_calls = 100000",
        "min_seconds_between_calls = nan",
        'gemini_requests_per_day = "250"',
        "gemini_requests_per_day = -1",
        "gemini_requests_per_day = 1000000",
    ],
    ids=["giay-chu", "giay-bool", "giay-am", "giay-qua-lon", "giay-nan", "ngay-chu", "ngay-am",
         "ngay-qua-lon"],
)  # fmt: skip
def test_auto_sai_gia_tri_dung_mac_dinh(tmp_path, line):
    assert load_auto_limits(toml(tmp_path, f"[auto]\n{line}\n")) == AutoLimits(6, 0)


@pytest.mark.xfail(
    strict=True,
    reason="SL-T148-4: math.isfinite(số nguyên > ~1e308) ném OverflowError (không phải AIError)",
)
def test_auto_so_nguyen_rat_lon_khong_lot_overflow(tmp_path):
    path = toml(tmp_path, "[auto]\nmin_seconds_between_calls = 1" + "0" * 400 + "\n")
    try:
        limits = load_auto_limits(path)
    except AIError:
        return  # cách của phiếu: câu báo tiếng Việt
    assert limits == AutoLimits(6, 0)  # cách của LC-T144-4: dùng mặc định


@pytest.mark.xfail(
    strict=True,
    reason="SL-T148-4: clamp_retry_after(10**400) ném OverflowError; dựng AIError cũng hỏng theo",
)
def test_retry_after_so_nguyen_rat_lon_bi_chan_tran():
    assert clamp_retry_after(10**400) in (120.0, None)
    assert AIError("x", kind="rate", retry_after=10**400).retry_after in (120.0, None)


# ============================================= gộp với T-142 (bỏ qua khi chưa có T-142)


def test_loai_loi_cloudflare_cung_bang_ten():
    cloudflare = pytest.importorskip("seo_app.ai.cloudflare_images")
    kinds = {value for name, value in vars(cloudflare).items() if name.startswith("KIND_")}
    assert kinds and kinds <= AI_ERROR_KINDS
    error = cloudflare.CloudflareImageError("x", kind=cloudflare.KIND_BUSY)
    assert isinstance(error, AIError) and error.kind == "busy" and error.retry_after is None


def test_make_provider_cloudflare_van_bi_chan_khi_mot_lan():
    if not hasattr(ai_registry, "IMAGE_ONLY_PROVIDERS"):
        pytest.skip("chưa gộp T-142")
    with pytest.raises(AIError, match="chỉ dùng để tạo ảnh"):
        make_provider("cloudflare", SETTINGS, single_attempt=True)
