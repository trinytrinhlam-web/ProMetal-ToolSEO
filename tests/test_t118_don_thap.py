"""T-118 (Thợ Máy): dọn lỗi Thấp sau rà soát Fable.

- Lỗi bất ngờ trên trang chỉ hiện loại lỗi (``client.showErrorDetails = "type"``, chủ dự án chọn
  2026-11-02): không câu lỗi gốc, không traceback, không đường dẫn trên máy.
- LC-T034-1: tên mô hình chèn vào câu báo của lớp AI (``st.error``, Markdown) không bao giờ thành
  link, dù viết dạng ``https://…``, ``www.…``, email hay ``[chữ](…)``. Đo bằng bộ dò link của T-044.
  Lượt 2 (Soi Lỗi SL-T118-1): cả dạng ngoặc nhọn ``<scheme:…>`` và thẻ HTML, ở 3 kiểu trang hiện
  câu báo (hiện thẳng, ``escape_link_syntax``, ``escape_markdown``).
- LC-T034-2: khung nhìn ``os`` đã lọc che cả ``environb``, ``getenvb`` (Mac/Linux); trên Windows
  (``os`` thật không có hai tên này) thì lỗi y như ``os`` thật.
- LC-T034-3: nạp module thứ hai lỗi lạ thì module thứ nhất vẫn được trả lại ``os`` thật.
- SL-T105-1: ``.env`` bị chương trình khác sửa đúng lúc vừa lưu: câu báo nói file bị thay đổi
  (không nói dòng sai định dạng), file trả về bản trước khi lưu. Ca của Soi Lỗi ở
  ``tests/test_soi_loi_t105.py`` (đã gỡ dấu ``xfail``); ở đây so đúng nguyên câu.

LC-T113-2 (giờ tải sửa tay trong cache): ``tests/test_la_chan_t113.py`` (đã gỡ dấu ``xfail``).
Không gọi AI, WordPress, Google thật: client AI giả của ``test_ai.py``,
``test_ai_openai_gemini.py``.
"""

from __future__ import annotations

import html
import importlib
import os
import re
import sys
import tomllib
from pathlib import Path
from types import SimpleNamespace

import anthropic
import openai
import pytest
from streamlit import config as st_config
from streamlit.testing.v1 import AppTest
from test_ai import FakeClient, api_error, generate
from test_ai_openai_gemini import (
    FakeGemini,
    FakeOpenAI,
    gm_error,
    gm_generate,
    oa_generate,
    openai_error,
    task,
)
from test_app_t044_safe_text import link_problems
from test_hash_password_script import load_script

import seo_app.ai.base as base
import seo_app.env_file as env_file
from seo_app.ai import AIError
from seo_app.ai.base import TaskConfig, bad_request_error, model_label
from seo_app.auth import hash_password
from seo_app.config import PROJECT_ROOT
from seo_app.env_file import EnvFileChangedError, EnvFileFormatError, set_api_key
from seo_app.sanitize import AUTOLINK_BREAK, escape_link_syntax
from seo_app.text import escape_markdown

# ======================================================== lỗi bất ngờ: chỉ hiện loại lỗi

CONFIG = tomllib.loads((PROJECT_ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8"))
PATH_IN_ERROR = r"C:\Users\chu-du-an\ProMetal\seo_app\bi-mat.py"
CRASHING_PAGE = f'raise RuntimeError(r"Lỗi ở {PATH_IN_ERROR} dòng 7")\n'


@pytest.fixture
def error_details():
    """Đặt ``client.showErrorDetails`` cho lần chạy ``AppTest``, trả lại giá trị cũ sau test."""
    old = st_config.get_option("client.showErrorDetails")
    yield lambda value: st_config.set_option("client.showErrorDetails", value)
    st_config.set_option("client.showErrorDetails", old)


def test_config_shows_only_error_type():
    assert CONFIG["client"]["showErrorDetails"] == "type"


def test_unexpected_error_shows_type_only(error_details):
    """Với giá trị trong ``.streamlit/config.toml``: lỗi bất ngờ chỉ hiện loại lỗi và câu chung của
    Streamlit; không câu lỗi gốc, không traceback, không đường dẫn trên máy."""
    error_details(CONFIG["client"]["showErrorDetails"])
    at = AppTest.from_string(CRASHING_PAGE).run(timeout=30)
    shown = at.exception[0]
    assert shown.proto.type == "RuntimeError"
    assert list(shown.stack_trace) == []
    text = shown.message + "".join(shown.stack_trace)
    for leak in (PATH_IN_ERROR, "chu-du-an", "Users", "Lỗi ở", "dòng 7", "File "):
        assert leak not in text


def test_full_details_would_show_the_path(error_details):
    """Đối chứng: để mặc định của Streamlit (``full``) thì trang hiện cả đường dẫn, nên test trên
    đúng là bắt được lỗi lộ đường dẫn."""
    error_details("full")
    at = AppTest.from_string(CRASHING_PAGE).run(timeout=30)
    assert PATH_IN_ERROR in at.exception[0].message
    assert at.exception[0].stack_trace


# ======================================================== LC-T034-1: tên mô hình không thành link

HOSTILE_MODELS = (
    "https://x.y",
    "http://x.y/duong-dan",
    "www.x.y",
    "ban@evil.example",
    "mailto:ban@evil.example",
    "[bấm](https://evil.example)",
)
REAL_MODELS = ("claude-opus-5-5", "gpt-5.1", "gemini-2.5-pro", "models/gemini-1.5-pro", "o3")


def _message(case: str, model: str) -> str:
    """Câu báo của lớp AI cho ``case`` khi tên mô hình là ``model`` (client giả, không gọi mạng)."""
    with pytest.raises(AIError) as info:
        if case.startswith("anthropic"):
            cls = (
                anthropic.PermissionDeniedError if case.endswith("403") else anthropic.NotFoundError
            )
            t = TaskConfig(name="write", provider="anthropic", model=model, effort="high")
            generate(FakeClient(api_error(cls, int(case[-3:]))), task=t)
        elif case.startswith("openai"):
            cls = openai.PermissionDeniedError if case.endswith("403") else openai.NotFoundError
            oa_generate(FakeOpenAI(openai_error(cls, int(case[-3:]))), task("openai", model=model))
        elif case.startswith("gemini"):
            status = "PERMISSION_DENIED" if case.endswith("403") else "NOT_FOUND"
            error = gm_error(int(case[-3:]), "lỗi", status)
            gm_generate(FakeGemini(error), task("gemini", model=model))
        else:
            raise bad_request_error(case, task("openai", model=model))
    return str(info.value)


CASES = (
    "anthropic-403",
    "anthropic-404",
    "openai-403",
    "openai-404",
    "gemini-403",
    "gemini-404",
    "OpenAI",  # lỗi 400 (câu chung của cả 3 hãng)
)


@pytest.mark.parametrize("case", CASES)
@pytest.mark.parametrize("model", HOSTILE_MODELS)
def test_model_name_never_becomes_a_link(case, model):
    message = _message(case, model)
    assert "mô hình «" in message
    assert link_problems(message) == [], message
    # Trang có làm sạch thêm cả câu (như thử mù ở Cài đặt) cũng không đổi gì.
    assert escape_link_syntax(message) == message


@pytest.mark.parametrize("case", CASES)
@pytest.mark.parametrize("model", REAL_MODELS)
def test_real_model_names_unchanged(case, model):
    assert f"«{model}»" in _message(case, model)


@pytest.mark.parametrize("model", HOSTILE_MODELS + REAL_MODELS)
def test_model_label_is_idempotent(model):
    assert model_label(model_label(model)) == model_label(model)


# Lượt 2, SL-T118-1 (Soi Lỗi): link tự động «ngoặc nhọn» của CommonMark, ``<scheme:…>`` (không cần
# «//»), và thẻ HTML. Mẫu dò giống ``tests/test_soi_loi_t118.py``.
AUTOLINK = re.compile(r"(?<!\\)<[A-Za-z][A-Za-z0-9+.\-]{1,31}:[^\x00-\x20<>]*>")
ANGLE_MODELS = (
    "<https:evil.example/khong-gach>",
    "<https://evil.example/goc>",
    "<mailto:ban@evil.example>",
    "<b>đậm</b>",
)


@pytest.mark.parametrize("case", CASES)
@pytest.mark.parametrize("model", ANGLE_MODELS)
def test_angle_bracket_model_never_becomes_a_link_on_any_page(case, model):
    """Ba kiểu trang hiện câu báo: hiện thẳng (``st.error(str(exc))``), qua ``escape_link_syntax``
    (Cài đặt), qua ``escape_markdown`` (trang Kế hoạch, Bài viết). Không kiểu nào còn dấu «<» thật,
    nên không thành link tự động hay thẻ HTML."""
    message = _message(case, model)
    for shown in (message, escape_link_syntax(message), escape_markdown(message)):
        assert "<" not in shown and not AUTOLINK.search(shown), shown
        assert link_problems(shown) == [], shown


@pytest.mark.parametrize("model", ANGLE_MODELS + HOSTILE_MODELS + REAL_MODELS)
def test_model_label_still_reads_as_the_name(model):
    """Người đọc vẫn thấy đúng tên đã ghi: giải mã «&lt;», bỏ ký tự rộng 0 và dấu «\\» mà
    ``escape_link_syntax`` thêm trước «(» thì ra tên gốc. Tên thật của 3 hãng không đổi chút nào."""
    label = model_label(model)
    shown = html.unescape(label).replace(AUTOLINK_BREAK, "").replace("]\\(", "](")
    assert shown == model
    if model in REAL_MODELS:
        assert label == model
    assert model_label(label) == label  # chạy lại không đổi gì


# ======================================================== LC-T034-2: environb, getenvb


def test_environb_attributes_mirror_real_os():
    """Trên Windows ``os`` thật không có ``environb``/``getenvb``: khung lọc cũng không có (lỗi y
    như thật). Trên Mac/Linux thì có."""
    for name in ("environb", "getenvb"):
        assert hasattr(base._OS_WITHOUT_IGNORED, name) is hasattr(os, name)


def test_environb_filtered_simulated(monkeypatch):
    """Giả lập ``os`` của Mac/Linux (có ``environb``): khung lọc không thấy ``IGNORED_ENV`` qua
    ``environb``, ``getenvb``; biến khác đọc như thật; tên khác của ``os`` đi thẳng."""
    real = {b"OPENAI_ORG_ID": b"org-la", b"ANTHROPIC_CUSTOM_HEADERS": b"X-La: 1", b"PATH": b"/bin"}
    fake_os = SimpleNamespace(
        environb=real, getenvb=lambda key, default=None: real.get(key, default),
        fsdecode=os.fsdecode, environ=os.environ, sep="/",
    )  # fmt: skip
    monkeypatch.setattr(base, "os", fake_os)
    view = base._OS_WITHOUT_IGNORED
    assert view.getenvb(b"OPENAI_ORG_ID") is None
    assert view.getenvb(b"ANTHROPIC_CUSTOM_HEADERS", b"mac-dinh") == b"mac-dinh"
    assert view.getenvb(b"PATH") == b"/bin"
    assert dict(view.environb) == {b"PATH": b"/bin"}
    assert b"OPENAI_ORG_ID" not in view.environb and len(view.environb) == 1
    with pytest.raises(KeyError):
        view.environb[b"OPENAI_ORG_ID"]
    assert view.sep == "/"


@pytest.mark.skipif(not os.supports_bytes_environ, reason="Windows không có os.environb")
def test_environb_filtered_real(monkeypatch):
    monkeypatch.setenv("OPENAI_ORG_ID", "org-la")
    view = base._OS_WITHOUT_IGNORED
    assert os.getenvb(b"OPENAI_ORG_ID") == b"org-la"
    assert view.getenvb(b"OPENAI_ORG_ID") is None
    assert b"OPENAI_ORG_ID" not in view.environb


# ======================================================== LC-T034-3: lỗi lạ khi nạp module


def test_patched_module_restored_when_second_module_fails(monkeypatch):
    """``openai._client`` nạp lỗi lạ (gói hỏng, không phải ``ImportError``): lỗi được báo lên, và
    ``anthropic._client.os`` đã bị trỏ sang khung lọc vẫn được trả lại ``os`` thật; khóa được
    nhả."""
    anthropic_client = importlib.import_module("anthropic._client")
    monkeypatch.delitem(sys.modules, "openai._client", raising=False)
    real_import = importlib.import_module

    def broken(name, *args, **kwargs):
        if name == "openai._client":
            raise RuntimeError("gói hỏng")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(importlib, "import_module", broken)
    with pytest.raises(RuntimeError, match="gói hỏng"), base.ignoring_custom_headers():
        pass
    assert anthropic_client.os is os
    assert not base._ENV_LOCK.locked()


def test_patched_module_restored_normally():
    """Canh: đường thường vẫn trỏ trong lúc tạo client và trả lại sau đó."""
    anthropic_client = importlib.import_module("anthropic._client")
    with base.ignoring_custom_headers():
        assert anthropic_client.os is base._OS_WITHOUT_IGNORED
    assert anthropic_client.os is os


# ======================================================== SL-T105-1: .env bị sửa đúng lúc lưu

ENV_OLD = "WORDPRESS_URL=https://a.vn\nAPP_PASSWORD_HASH=cu\nIMAGE_FOLDERS=D:/Anh\n"
ENV_BY_OTHER_PROGRAM = "WORDPRESS_URL=https://a.vn\nAPP_PASSWORD_HASH=khac\nIMAGE_FOLDERS=D:/Anh\n"


def _other_program_writes_right_after_replace(monkeypatch) -> None:
    """Ngay sau lần thay ``.env`` đầu tiên, «chương trình khác» ghi đè một nội dung hợp lệ khác."""
    real = env_file._atomic_write
    done: list[int] = []

    def write(path, content):
        real(path, content)
        if not done:
            done.append(1)
            Path(path).write_bytes(ENV_BY_OTHER_PROGRAM.encode("utf-8"))

    monkeypatch.setattr(env_file, "_atomic_write", write)


def test_sl_t105_1_set_password_says_file_changed(project_root, tmp_path, monkeypatch, capsys):
    env = tmp_path / ".env"
    env.write_bytes(ENV_OLD.encode("utf-8"))
    script = load_script(project_root)
    monkeypatch.setattr(script, "DEFAULT_ENV_FILE", env)
    monkeypatch.setattr(script.getpass, "getpass", lambda prompt="": "mat-khau-moi-T118")
    monkeypatch.setattr(script, "hash_password", lambda p: hash_password(p, iterations=1_000))
    _other_program_writes_right_after_replace(monkeypatch)
    assert script.main([]) == 1
    out = capsys.readouterr().out
    assert out.strip() == f"Chưa lưu mật khẩu mới. {script.MSG_ENV_CHANGED}"
    assert env.read_bytes() == ENV_OLD.encode("utf-8")  # trả bản trước khi lưu
    assert not [p for p in tmp_path.iterdir() if p.name.endswith(".tmp")]


def test_sl_t105_1_settings_writer_says_file_changed(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_bytes(ENV_OLD.encode("utf-8"))
    _other_program_writes_right_after_replace(monkeypatch)
    with pytest.raises(EnvFileChangedError) as info:
        set_api_key("GEMINI_API_KEY", "AIzaKhoaGiaT118", env)
    assert not isinstance(info.value, EnvFileFormatError)
    assert str(info.value) == env_file._CHANGED_RESTORED
    assert str(tmp_path) not in str(info.value) and "AIza" not in str(info.value)
    assert env.read_bytes() == ENV_OLD.encode("utf-8")
