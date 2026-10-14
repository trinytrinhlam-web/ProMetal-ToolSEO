"""Test ghi/xóa khóa API trong .env (T-020). Chỉ dùng file tạm, không gọi mạng."""

from __future__ import annotations

import os
import stat

import anthropic
import httpx2
import pytest
from dotenv import dotenv_values

import seo_app.config as config
from seo_app import env_file
from seo_app.env_file import (
    ALLOWED_KEYS,
    MAX_VALUE_LENGTH,
    EnvFileError,
    check_api_key,
    clear_api_key,
    overridden_by_os_environ,
    set_api_key,
    validate_key_value,
)

KEY = "sk-ant-api03-ABCdef_123-xyz"
KEY2 = "sk-ant-api03-NEWNEW_456-abc"


@pytest.fixture
def env_path(tmp_path, monkeypatch):
    """Trỏ DEFAULT_ENV_FILE sang file tạm (không bao giờ đụng .env thật)."""
    path = tmp_path / ".env"
    monkeypatch.setattr(config, "DEFAULT_ENV_FILE", path)
    return path


def read(path):
    with path.open("r", encoding="utf-8", newline="") as fh:
        return fh.read()


def write(path, text):
    with path.open("w", encoding="utf-8", newline="") as fh:
        fh.write(text)


# ---- 1. Danh sách cho phép, mặc định DEFAULT_ENV_FILE ----------------------------------


def test_default_file_is_looked_up_at_call_time(env_path):
    set_api_key("ANTHROPIC_API_KEY", KEY)
    assert env_path.is_file()
    assert config.load_settings().anthropic_api_key == KEY


@pytest.mark.parametrize("name", ALLOWED_KEYS)
def test_all_allowed_keys_can_be_set(env_path, name):
    set_api_key(name, KEY)
    assert dotenv_values(env_path)[name] == KEY


@pytest.mark.parametrize(
    "name",
    ["APP_PASSWORD_HASH", "WORDPRESS_APP_PASSWORD", "anthropic_api_key", "", "PATH", "X"],
)
def test_other_names_rejected(env_path, name):
    with pytest.raises(EnvFileError):
        set_api_key(name, KEY)
    with pytest.raises(EnvFileError):
        clear_api_key(name)
    with pytest.raises(EnvFileError):
        overridden_by_os_environ(name, environ={})
    assert not env_path.exists()


def test_explicit_path_argument(tmp_path, env_path):
    other = tmp_path / "khac.env"
    set_api_key("OPENAI_API_KEY", KEY, env_file=other)
    assert dotenv_values(other)["OPENAI_API_KEY"] == KEY
    assert not env_path.exists()


# ---- 2. Giữ nguyên dòng khác, chú thích, thứ tự ----------------------------------------

ORIGINAL = (
    "# Cấu hình SEO App — chú thích tiếng Việt\n"
    "APP_PASSWORD_HASH=pbkdf2_sha256$1000$muoi$bam\n"
    "\n"
    "# Khóa Claude: https://console.anthropic.com\n"
    "ANTHROPIC_API_KEY=sk-ant-old-value\n"
    "OPENAI_API_KEY=\n"
    "WORDPRESS_URL=https://example.com\n"
)


def test_replace_existing_line_keeps_everything_else(env_path):
    write(env_path, ORIGINAL)
    set_api_key("ANTHROPIC_API_KEY", KEY)
    assert read(env_path) == ORIGINAL.replace("sk-ant-old-value", KEY)


def test_fill_empty_line_in_place(env_path):
    write(env_path, ORIGINAL)
    set_api_key("OPENAI_API_KEY", KEY)
    assert read(env_path) == ORIGINAL.replace("OPENAI_API_KEY=\n", f"OPENAI_API_KEY={KEY}\n")


def test_append_when_missing(env_path):
    write(env_path, ORIGINAL)
    set_api_key("GEMINI_API_KEY", "AIzaSyExample_123")
    assert read(env_path) == ORIGINAL + "GEMINI_API_KEY=AIzaSyExample_123\n"


def test_append_when_last_line_has_no_newline(env_path):
    write(env_path, "WORDPRESS_URL=https://example.com")
    set_api_key("GEMINI_API_KEY", "AIzaSyExample_123")
    assert read(env_path) == "WORDPRESS_URL=https://example.com\nGEMINI_API_KEY=AIzaSyExample_123\n"


def test_create_file_when_missing(env_path):
    assert not env_path.exists()
    set_api_key("ANTHROPIC_API_KEY", KEY)
    assert read(env_path) == f"ANTHROPIC_API_KEY={KEY}\n"


def test_commented_line_not_touched(env_path):
    write(env_path, "# ANTHROPIC_API_KEY=cu\nOTHER=1\n")
    set_api_key("ANTHROPIC_API_KEY", KEY)
    assert read(env_path) == f"# ANTHROPIC_API_KEY=cu\nOTHER=1\nANTHROPIC_API_KEY={KEY}\n"


def test_similar_names_not_touched(env_path):
    write(env_path, "MY_ANTHROPIC_API_KEY=a\nANTHROPIC_API_KEY_OLD=b\n")
    set_api_key("ANTHROPIC_API_KEY", KEY)
    text = read(env_path)
    assert text.startswith("MY_ANTHROPIC_API_KEY=a\nANTHROPIC_API_KEY_OLD=b\n")
    assert dotenv_values(env_path)["ANTHROPIC_API_KEY"] == KEY


def test_export_and_spaces_variants_replaced(env_path):
    write(env_path, "export ANTHROPIC_API_KEY = 'cu'\nA=1\n")
    set_api_key("ANTHROPIC_API_KEY", KEY)
    assert read(env_path) == f"ANTHROPIC_API_KEY={KEY}\nA=1\n"


def test_duplicate_lines_all_replaced(env_path):
    write(env_path, "ANTHROPIC_API_KEY=a\nB=2\nANTHROPIC_API_KEY=b\n")
    set_api_key("ANTHROPIC_API_KEY", KEY)
    assert read(env_path) == f"ANTHROPIC_API_KEY={KEY}\nB=2\nANTHROPIC_API_KEY={KEY}\n"


def test_old_multiline_quoted_value_removed(env_path):
    write(env_path, 'ANTHROPIC_API_KEY="dong1\ndong2"\nAPP_TIMEZONE=Asia/Ho_Chi_Minh\n')
    set_api_key("ANTHROPIC_API_KEY", KEY)
    assert read(env_path) == f"ANTHROPIC_API_KEY={KEY}\nAPP_TIMEZONE=Asia/Ho_Chi_Minh\n"


def test_crlf_line_endings_kept(env_path):
    write(env_path, "A=1\r\nANTHROPIC_API_KEY=cu\r\nB=2\r\n")
    set_api_key("ANTHROPIC_API_KEY", KEY)
    set_api_key("GEMINI_API_KEY", "AIzaX_123456")
    assert (
        read(env_path)
        == f"A=1\r\nANTHROPIC_API_KEY={KEY}\r\nB=2\r\nGEMINI_API_KEY=AIzaX_123456\r\n"
    )


def test_bom_kept(env_path):
    write(env_path, "﻿ANTHROPIC_API_KEY=cu\nB=2\n")
    set_api_key("ANTHROPIC_API_KEY", KEY)
    assert read(env_path) == f"﻿ANTHROPIC_API_KEY={KEY}\nB=2\n"


def test_non_utf8_file_refused_without_change(env_path):
    env_path.write_bytes(b"A=\xff\xfe\n")
    with pytest.raises(EnvFileError, match="UTF-8"):
        set_api_key("ANTHROPIC_API_KEY", KEY)
    assert env_path.read_bytes() == b"A=\xff\xfe\n"


def test_clear_sets_empty_value_in_place(env_path):
    write(env_path, ORIGINAL)
    clear_api_key("ANTHROPIC_API_KEY")
    assert read(env_path) == ORIGINAL.replace("sk-ant-old-value", "")
    assert config.load_settings().anthropic_api_key == ""


def test_clear_missing_variable_or_file_does_nothing(env_path):
    clear_api_key("ANTHROPIC_API_KEY")
    assert not env_path.exists()
    write(env_path, "A=1\n")
    clear_api_key("GEMINI_API_KEY")
    assert read(env_path) == "A=1\n"


def test_set_then_replace_then_clear(env_path):
    set_api_key("ANTHROPIC_API_KEY", KEY)
    set_api_key("ANTHROPIC_API_KEY", KEY2)
    assert read(env_path) == f"ANTHROPIC_API_KEY={KEY2}\n"
    clear_api_key("ANTHROPIC_API_KEY")
    assert read(env_path) == "ANTHROPIC_API_KEY=\n"


# ---- 3. Chặn giá trị nguy hiểm ----------------------------------------------------------


def test_strip_outer_whitespace(env_path):
    set_api_key("ANTHROPIC_API_KEY", f"  \t{KEY} \n")
    assert read(env_path) == f"ANTHROPIC_API_KEY={KEY}\n"


@pytest.mark.parametrize(
    "value",
    [
        f"{KEY}\nAPP_PASSWORD_HASH=bam_cua_ke_xau",
        f"{KEY}\rAPP_PASSWORD_HASH=x",
        f"{KEY}\r\nAPP_PASSWORD_HASH=x",
        f"{KEY} APP_PASSWORD_HASH=x",
        f"{KEY}\x00",
        f"{KEY}\x1b[31m",
        f"{KEY}\x7f",
        f'{KEY}"',
        f"'{KEY}'",
        f"{KEY}`",
        f"{KEY} #chu thich",
        f"{KEY}#x",
        "sk-ant abc",
        "sk-ant\tabc",
        "sk-ant abc",
        "${APP_PASSWORD_HASH}",
        "sk\\nabc",
        "sk=abc",
        "sk-ant-khóa",
        "",
        "   ",
        "a" * (MAX_VALUE_LENGTH + 1),
    ],
)
def test_dangerous_values_rejected(env_path, value):
    write(env_path, ORIGINAL)
    with pytest.raises(EnvFileError) as info:
        set_api_key("ANTHROPIC_API_KEY", value)
    assert read(env_path) == ORIGINAL  # file không đổi
    assert "APP_PASSWORD_HASH=x" not in str(info.value)


def test_max_length_allowed(env_path):
    value = "a" * MAX_VALUE_LENGTH
    set_api_key("ANTHROPIC_API_KEY", value)
    assert dotenv_values(env_path)["ANTHROPIC_API_KEY"] == value


def test_injection_cannot_add_other_variable(env_path):
    write(env_path, "APP_PASSWORD_HASH=that\n")
    with pytest.raises(EnvFileError):
        set_api_key("ANTHROPIC_API_KEY", "x\nAPP_PASSWORD_HASH=gia")
    assert dotenv_values(env_path) == {"APP_PASSWORD_HASH": "that"}


def test_error_messages_never_contain_value():
    secret = "sk-ant-api03-BIMAT_KHONG_DUOC_IN"
    for bad in (secret + " x", secret + "\nX=1", secret + "#", secret + '"', secret * 40):
        with pytest.raises(EnvFileError) as info:
            validate_key_value(bad)
        assert "BIMAT" not in str(info.value)


def test_non_string_rejected():
    with pytest.raises(EnvFileError):
        validate_key_value(None)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "value",
    [
        "sk-ant-api03-AbC_dEf-123",
        "sk-proj-Abc123_-xyz",
        "AIzaSyD-abc_123XYZ",
        "abc.def:ghi+jkl/mno~p",
    ],
)
def test_realistic_keys_accepted(env_path, value):
    set_api_key("ANTHROPIC_API_KEY", value)
    assert dotenv_values(env_path)["ANTHROPIC_API_KEY"] == value


# ---- 4. Ghi an toàn -----------------------------------------------------------------------


@pytest.mark.skipif(os.name == "nt", reason="Quyền 600 chỉ áp dụng Mac/Linux")
def test_permissions_600(env_path):
    write(env_path, "A=1\n")
    env_path.chmod(0o644)
    set_api_key("ANTHROPIC_API_KEY", KEY)
    assert stat.S_IMODE(env_path.stat().st_mode) == 0o600


def test_windows_skips_chmod(env_path, monkeypatch):
    calls = []
    monkeypatch.setattr(env_file, "_is_windows", lambda: True)
    monkeypatch.setattr(env_file.os, "chmod", lambda *a, **k: calls.append(a))
    set_api_key("ANTHROPIC_API_KEY", KEY)
    assert calls == []
    assert dotenv_values(env_path)["ANTHROPIC_API_KEY"] == KEY


def test_uses_os_replace_and_leaves_no_temp_file(env_path, monkeypatch):
    calls = []
    real_replace = os.replace

    def spy(src, dst):
        calls.append((os.path.dirname(src), os.fspath(dst)))
        return real_replace(src, dst)

    monkeypatch.setattr(env_file.os, "replace", spy)
    set_api_key("ANTHROPIC_API_KEY", KEY)
    assert calls == [(str(env_path.parent), str(env_path))]
    assert sorted(p.name for p in env_path.parent.iterdir()) == [".env"]


def test_failed_replace_keeps_old_file_and_cleans_temp(env_path, monkeypatch):
    write(env_path, ORIGINAL)

    def boom(src, dst):
        raise PermissionError(13, "Permission denied", str(dst))

    monkeypatch.setattr(env_file.os, "replace", boom)
    with pytest.raises(EnvFileError) as info:
        set_api_key("ANTHROPIC_API_KEY", KEY)
    assert read(env_path) == ORIGINAL
    assert sorted(p.name for p in env_path.parent.iterdir()) == [".env"]
    # Không lộ đường dẫn máy hay khóa trong thông báo.
    assert str(env_path.parent) not in str(info.value)
    assert KEY not in str(info.value)


def test_missing_parent_folder(tmp_path):
    with pytest.raises(EnvFileError):
        set_api_key("ANTHROPIC_API_KEY", KEY, env_file=tmp_path / "khong-co" / ".env")


def test_env_path_is_directory(tmp_path):
    folder = tmp_path / ".env"
    folder.mkdir()
    with pytest.raises(EnvFileError):
        set_api_key("ANTHROPIC_API_KEY", KEY, env_file=folder)


# ---- Biến môi trường hệ điều hành ưu tiên hơn .env ------------------------------------


def test_overridden_by_os_environ():
    assert overridden_by_os_environ("ANTHROPIC_API_KEY", environ={"ANTHROPIC_API_KEY": "x"})
    assert overridden_by_os_environ("ANTHROPIC_API_KEY", environ={"ANTHROPIC_API_KEY": ""})
    assert not overridden_by_os_environ("ANTHROPIC_API_KEY", environ={})


def test_overridden_reads_real_os_environ(monkeypatch):
    assert not overridden_by_os_environ("GEMINI_API_KEY")
    monkeypatch.setenv("GEMINI_API_KEY", "x")
    assert overridden_by_os_environ("GEMINI_API_KEY")
    assert overridden_by_os_environ("GEMINI_API_KEY") is True


# ---- 5. Kiểm tra khóa Claude (client giả, không gọi mạng) ------------------------------

REQUEST = httpx2.Request("GET", "https://api.test/v1/models")


def status_error(cls, status, message="loi"):
    response = httpx2.Response(status, request=REQUEST)
    return cls(message, response=response, body=None)


class FakeModels:
    def __init__(self, error=None):
        self.error = error
        self.calls = []

    def list(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return []


class FakeClient:
    def __init__(self, error=None):
        self.models = FakeModels(error)


def test_check_ok_calls_models_list_with_timeout():
    client = FakeClient()
    result = check_api_key("ANTHROPIC_API_KEY", api_key=KEY, client=client, timeout=7)
    assert result.ok and result.status == "ok"
    assert client.models.calls == [{"limit": 1, "timeout": 7}]


@pytest.mark.parametrize(
    ("error", "status"),
    [
        (status_error(anthropic.AuthenticationError, 401), "invalid"),
        (status_error(anthropic.PermissionDeniedError, 403), "invalid"),
        (status_error(anthropic.RateLimitError, 429), "unknown"),
        (status_error(anthropic.InternalServerError, 500), "unknown"),
        (anthropic.APITimeoutError(request=REQUEST), "unknown"),
        (anthropic.APIConnectionError(request=REQUEST), "unknown"),
        (anthropic.AnthropicError("boom"), "unknown"),
    ],
)
def test_check_errors_mapped(error, status):
    result = check_api_key("ANTHROPIC_API_KEY", api_key=KEY, client=FakeClient(error))
    assert result.status == status
    assert not result.ok
    assert result.message


def test_check_message_never_contains_key():
    leaky = status_error(anthropic.AuthenticationError, 401, f"x-api-key: {KEY} sai")
    for error in (
        leaky,
        status_error(anthropic.BadRequestError, 400, f"key {KEY}"),
        anthropic.AnthropicError(f"Bearer {KEY}"),
    ):
        result = check_api_key("ANTHROPIC_API_KEY", api_key=KEY, client=FakeClient(error))
        assert KEY not in result.message
        assert "sk-ant" not in result.message


def test_check_reads_key_from_settings_when_not_given(env_path, monkeypatch):
    set_api_key("ANTHROPIC_API_KEY", KEY)
    created = {}

    class Recorder:
        def __init__(self, **kwargs):
            created.update(kwargs)
            self.models = FakeModels()

    monkeypatch.setattr(anthropic, "Anthropic", Recorder)
    result = check_api_key("ANTHROPIC_API_KEY", timeout=5)
    assert result.ok
    assert created == {"api_key": KEY, "timeout": 5, "max_retries": 0}


def test_check_missing_key(env_path):
    result = check_api_key("ANTHROPIC_API_KEY")
    assert result.status == "missing"
    assert check_api_key("ANTHROPIC_API_KEY", api_key="   ").status == "missing"


def test_check_bad_config_does_not_crash(env_path, monkeypatch):
    monkeypatch.setenv("APP_TIMEZONE", "Sao/Hoa")
    result = check_api_key("ANTHROPIC_API_KEY")
    assert result.status == "unknown"


@pytest.mark.parametrize("name", ["OPENAI_API_KEY", "GEMINI_API_KEY"])
def test_check_other_providers_now_supported(name):
    # T-018: trước đây ChatGPT/Gemini trả "unsupported"; nay kiểm tra bằng client của hãng
    # (chi tiết từng lỗi ở tests/test_ai_openai_gemini.py).
    client = FakeClient()
    result = check_api_key(name, api_key=KEY, client=client)
    assert result.status == "ok"
    assert len(client.models.calls) == 1


def test_check_rejects_unknown_name():
    with pytest.raises(EnvFileError):
        check_api_key("APP_PASSWORD_HASH", api_key=KEY)


def test_check_with_real_client_class_hits_network_guard():
    # Client thật của thư viện: lệnh gọi bị conftest chặn, kết quả là "unknown", không lộ khóa.
    result = check_api_key("ANTHROPIC_API_KEY", api_key=KEY, timeout=1)
    assert result.status == "unknown"
    assert KEY not in result.message


# ---- T-021: khớp cách python-dotenv đọc, nháy không đóng, đọc lại sau khi ghi, symlink ----

SECRETS_AFTER = "WORDPRESS_APP_PASSWORD=wp\nAPP_PASSWORD_HASH=pbkdf2$x\n"


@pytest.mark.parametrize(
    "bad_line",
    [
        'ANTHROPIC_API_KEY="sk-old\n',  # quên đóng nháy kép
        "ANTHROPIC_API_KEY='sk-old\n",  # quên đóng nháy đơn
        'ANTHROPIC_API_KEY="sk-old\\"\n',  # nháy đóng bị thoát
        'export ANTHROPIC_API_KEY = "sk-old\n',
    ],
)
@pytest.mark.parametrize("action", ["set", "clear"])
def test_unclosed_quote_refused_and_nothing_lost(env_path, bad_line, action):
    # Lá Chắn T-016-020 #2: trước đây các dòng phía sau (mã băm mật khẩu, mật khẩu WordPress)
    # bị bỏ hết. Nay: báo lỗi dễ hiểu, file giữ nguyên từng byte.
    original = "# đầu file\n" + bad_line + SECRETS_AFTER
    write(env_path, original)
    before = dotenv_values(env_path)
    assert before["APP_PASSWORD_HASH"] == "pbkdf2$x"
    with pytest.raises(EnvFileError, match="ANTHROPIC_API_KEY") as info:
        if action == "set":
            set_api_key("ANTHROPIC_API_KEY", KEY)
        else:
            clear_api_key("ANTHROPIC_API_KEY")
    assert "nháy" in str(info.value)
    assert "sk-old" not in str(info.value)
    assert read(env_path) == original
    assert sorted(p.name for p in env_path.parent.iterdir()) == [".env"]


def test_unclosed_quote_on_other_variable_does_not_block(env_path):
    # Dòng hỏng của biến khác: dotenv bỏ qua nó; app giữ nguyên nó và vẫn ghi được khóa.
    original = 'NOTE="chua dong\n' + SECRETS_AFTER
    write(env_path, original)
    set_api_key("ANTHROPIC_API_KEY", KEY)
    assert read(env_path) == original + f"ANTHROPIC_API_KEY={KEY}\n"
    values = dotenv_values(env_path)
    assert values["APP_PASSWORD_HASH"] == "pbkdf2$x"
    assert values["ANTHROPIC_API_KEY"] == KEY


def test_closed_multiline_value_still_replaced(env_path):
    write(env_path, 'ANTHROPIC_API_KEY="a\nb"\n' + SECRETS_AFTER)
    set_api_key("ANTHROPIC_API_KEY", KEY)
    assert read(env_path) == f"ANTHROPIC_API_KEY={KEY}\n" + SECRETS_AFTER


def test_blank_lines_before_key_kept(env_path):
    write(env_path, "A=1\n\n\n  ANTHROPIC_API_KEY=cu\nB=2\n")
    set_api_key("ANTHROPIC_API_KEY", KEY)
    assert read(env_path) == f"A=1\n\n\nANTHROPIC_API_KEY={KEY}\nB=2\n"


def test_every_other_variable_unchanged_after_save(env_path):
    original = (
        "A=1\nexport B='x y'\nC=\"line1\nline2\"\n# chú thích ANTHROPIC_API_KEY=gia\n"
        "D=${A}\nANTHROPIC_API_KEY=cu\nE  =  5 # ghi chú\n"
    )
    write(env_path, original)
    before = dotenv_values(env_path, interpolate=False)
    set_api_key("ANTHROPIC_API_KEY", KEY)
    after = dotenv_values(env_path, interpolate=False)
    assert after == {**before, "ANTHROPIC_API_KEY": KEY}


def test_mismatch_after_write_restores_old_file(env_path, monkeypatch):
    # Giả lỗi đĩa: lần ghi đầu ghi ra nội dung sai. App phải trả lại bản cũ và báo lỗi.
    original = "ANTHROPIC_API_KEY=cu\n" + SECRETS_AFTER
    write(env_path, original)
    real_write = env_file._atomic_write
    calls = []

    def flaky(path, content):
        calls.append(content)
        real_write(path, "HONG=1\n" if len(calls) == 1 else content)

    monkeypatch.setattr(env_file, "_atomic_write", flaky)
    with pytest.raises(EnvFileError, match="định dạng lạ"):
        set_api_key("ANTHROPIC_API_KEY", KEY)
    assert read(env_path) == original
    assert len(calls) == 2


def test_mismatch_after_write_removes_new_file(env_path, monkeypatch):
    real_write = env_file._atomic_write
    monkeypatch.setattr(env_file, "_atomic_write", lambda p, c: real_write(p, "HONG=1\n"))
    with pytest.raises(EnvFileError):
        set_api_key("ANTHROPIC_API_KEY", KEY)
    assert not env_path.exists()


def test_in_memory_check_blocks_write(env_path, monkeypatch):
    # Nếu nội dung dựng ra không khớp cách dotenv đọc thì không ghi gì cả.
    write(env_path, "A=1\n")
    monkeypatch.setattr(env_file, "_build_content", lambda *a, **k: "A=2\n")
    called = []
    monkeypatch.setattr(env_file, "_atomic_write", lambda *a: called.append(a))
    with pytest.raises(EnvFileError, match="định dạng lạ"):
        set_api_key("ANTHROPIC_API_KEY", KEY)
    assert called == []
    assert read(env_path) == "A=1\n"


@pytest.mark.skipif(os.name == "nt", reason="tạo symlink trên Windows cần quyền đặc biệt")
@pytest.mark.parametrize("action", ["set", "clear"])
def test_symlink_env_refused(tmp_path, action):
    # Lá Chắn T-016-020 #3: không ghi qua liên kết tắt, thông báo không lộ đường dẫn.
    target = tmp_path / "noi-khac" / "that.env"
    target.parent.mkdir()
    write(target, "ANTHROPIC_API_KEY=cu\n")
    link = tmp_path / ".env"
    link.symlink_to(target)
    with pytest.raises(EnvFileError, match="liên kết tắt") as info:
        if action == "set":
            set_api_key("ANTHROPIC_API_KEY", KEY, env_file=link)
        else:
            clear_api_key("ANTHROPIC_API_KEY", env_file=link)
    assert str(tmp_path) not in str(info.value)
    assert "noi-khac" not in str(info.value)
    assert link.is_symlink()
    assert read(target) == "ANTHROPIC_API_KEY=cu\n"
    assert sorted(p.name for p in tmp_path.iterdir()) == [".env", "noi-khac"]


@pytest.mark.skipif(os.name == "nt", reason="tạo symlink trên Windows cần quyền đặc biệt")
def test_dangling_symlink_refused(tmp_path):
    link = tmp_path / ".env"
    link.symlink_to(tmp_path / "khong-co")
    with pytest.raises(EnvFileError, match="liên kết tắt"):
        set_api_key("ANTHROPIC_API_KEY", KEY, env_file=link)
    assert link.is_symlink()
    assert not (tmp_path / "khong-co").exists()
