"""Soi Lỗi: kiểm thử T-016 (kho nháp) và T-020 (nhập khóa API trong app).

Mọi test dùng ``tmp_path``: không đọc/ghi ``.env`` hay ``data/`` thật, không gọi mạng.
Lỗi thật chưa sửa được đánh ``xfail(strict=True)`` kèm mã R8-x (xem
``docs/team/reports/T-016-020-soi-loi.md``): khi sửa xong, test sẽ báo XPASS để gỡ dấu xfail.
"""

from __future__ import annotations

import contextlib
import errno
import json
import logging
import os
import sqlite3
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from dotenv import dotenv_values
from streamlit.testing.v1 import AppTest

import seo_app.config as config
from seo_app import env_file
from seo_app.auth import hash_password
from seo_app.content import OutlineItem, Research, Review
from seo_app.sanitize import escape_link_syntax
from seo_app.storage import (
    MAX_DRAFT_BYTES,
    MAX_DRAFTS,
    DraftError,
    DraftPart,
    DraftSnapshot,
    DraftStore,
)
from seo_app.storage import drafts as drafts_module

FAKE_KEY = "sk-ant-api03-SoiLoiKhoaGia_XyZ987-qwertyUIOP"
EVIL_LINK = "[bấm vào đây](https://evil.example/x)"


# ============================================================================ T-020: .env


@pytest.fixture
def env_path(monkeypatch, tmp_path) -> Path:
    path = tmp_path / ".env"
    monkeypatch.setattr(config, "DEFAULT_ENV_FILE", path)
    return path


def write_bytes(path: Path, text: str) -> None:
    path.write_bytes(text.encode("utf-8"))


def read_raw(path: Path) -> str:
    return path.read_bytes().decode("utf-8")


# ---------------------------------------------------------------- giữ nguyên dòng khác


MESSY_ENV = (
    "﻿# Cấu hình SEO App — chú thích tiếng Việt\r\n"
    "APP_PASSWORD_HASH=pbkdf2_sha256$1000$abc$def\r\n"
    "export ANTHROPIC_API_KEY=old-one\r\n"
    "WORDPRESS_URL=https://vi-du.vn\n"  # dòng LF lẫn trong file CRLF
    'MULTI="dòng 1\r\nANTHROPIC_API_KEY_X=khong-phai\r\ndòng 3"\r\n'
    "  ANTHROPIC_API_KEY = 'old-two'  # trùng tên\r\n"
    "ANTHROPIC_API_KEY=\"old\r\nthree\"\r\n"
    "#ANTHROPIC_API_KEY=giu-nguyen-chu-thich\r\n"
    "OPENAI_API_KEY=sk-openai-cu\r\n"
    "LAST=khong-co-xuong-dong"
)


def test_messy_env_only_key_lines_change(env_path):
    write_bytes(env_path, MESSY_ENV)
    env_file.set_api_key("ANTHROPIC_API_KEY", FAKE_KEY)
    result = read_raw(env_path)

    expected = (
        "﻿# Cấu hình SEO App — chú thích tiếng Việt\r\n"
        "APP_PASSWORD_HASH=pbkdf2_sha256$1000$abc$def\r\n"
        f"ANTHROPIC_API_KEY={FAKE_KEY}\r\n"
        "WORDPRESS_URL=https://vi-du.vn\n"
        'MULTI="dòng 1\r\nANTHROPIC_API_KEY_X=khong-phai\r\ndòng 3"\r\n'
        f"ANTHROPIC_API_KEY={FAKE_KEY}\r\n"
        f"ANTHROPIC_API_KEY={FAKE_KEY}\r\n"
        "#ANTHROPIC_API_KEY=giu-nguyen-chu-thich\r\n"
        "OPENAI_API_KEY=sk-openai-cu\r\n"
        "LAST=khong-co-xuong-dong"
    )
    assert result == expected
    values = dotenv_values(env_path, encoding="utf-8")
    assert values["ANTHROPIC_API_KEY"] == FAKE_KEY
    assert values["APP_PASSWORD_HASH"] == "pbkdf2_sha256$1000$abc$def"
    # python-dotenv tự đổi CRLF thành LF khi đọc; byte trong file đã so ở trên
    assert values["MULTI"] == "dòng 1\nANTHROPIC_API_KEY_X=khong-phai\ndòng 3"
    assert values["OPENAI_API_KEY"] == "sk-openai-cu"
    assert "ANTHROPIC_API_KEY_X" not in values


def test_clear_on_messy_env_keeps_other_bytes(env_path):
    write_bytes(env_path, MESSY_ENV)
    env_file.clear_api_key("OPENAI_API_KEY")
    assert read_raw(env_path) == MESSY_ENV.replace(
        "OPENAI_API_KEY=sk-openai-cu\r\n", "OPENAI_API_KEY=\r\n"
    )


def test_repeated_saves_are_stable(env_path):
    write_bytes(env_path, MESSY_ENV)
    env_file.set_api_key("GEMINI_API_KEY", "AIzaKhoaGia1")
    first = read_raw(env_path)
    for _ in range(5):
        env_file.set_api_key("GEMINI_API_KEY", "AIzaKhoaGia1")
    assert read_raw(env_path) == first
    assert first.count("GEMINI_API_KEY=") == 1
    # khi thêm mới vào file CRLF: dùng CRLF; dòng cuối không có xuống dòng được nối đúng
    assert first.endswith("LAST=khong-co-xuong-dong\r\nGEMINI_API_KEY=AIzaKhoaGia1\r\n")


def test_every_allowed_character_round_trips_through_settings(env_path):
    value = "sk-ant_ABCxyz0123456789-._:+/~end"
    env_file.set_api_key("ANTHROPIC_API_KEY", value)
    assert config.load_settings(environ={}).anthropic_api_key == value


# ---------------------------------------------------------------- chèn biến qua ô nhập


@pytest.mark.parametrize(
    "value",
    [
        "sk-a\nAPP_PASSWORD_HASH=x",
        "sk-a\rAPP_PASSWORD_HASH=x",
        "sk-a APP_PASSWORD_HASH=x",  # ngắt dòng Unicode (splitlines coi là xuống dòng)
        "sk-a APP_PASSWORD_HASH=x",
        "sk-a\x85APP_PASSWORD_HASH=x",  # NEL
        "sk-a\x0bAPP_PASSWORD_HASH=x",
        "sk-a\x0cAPP_PASSWORD_HASH=x",
        "sk-a\x1cAPP_PASSWORD_HASH=x",
        "sk-a\x00APP_PASSWORD_HASH=x",
        "sk-a​b",  # dấu cách độ rộng 0
        "sk-a‮b",  # đảo chiều chữ
        "sk-a﻿b",
        "sk-a＝b",  # dấu = toàn khổ
        "sk-a=b",
        "sk-${APP_PASSWORD_HASH}",
        "sk-\\nAPP_PASSWORD_HASH=x",
        '"sk-a" APP_PASSWORD_HASH=x',
        "sk-a;APP_PASSWORD_HASH=x",
        "sk-ạ",
        "sk-٣٤",  # chữ số Ả Rập
        "a" * (env_file.MAX_VALUE_LENGTH + 1),
    ],
)
def test_injection_attempts_rejected_and_file_unchanged(env_path, value):
    original = "APP_PASSWORD_HASH=that\nANTHROPIC_API_KEY=cu\n"
    write_bytes(env_path, original)
    with pytest.raises(env_file.EnvFileError) as info:
        env_file.set_api_key("ANTHROPIC_API_KEY", value)
    assert read_raw(env_path) == original
    message = str(info.value)
    assert "APP_PASSWORD_HASH=x" not in message
    assert value.strip() not in message


@pytest.mark.parametrize("name", ["APP_PASSWORD_HASH", "ANTHROPIC_API_KEY\n", " ANTHROPIC_API_KEY",
                                  "anthropic_api_key", "ANTHROPIC_API_KEY=x", ""])
def test_variable_name_cannot_be_smuggled(env_path, name):
    with pytest.raises(env_file.EnvFileError):
        env_file.set_api_key(name, "sk-abc")
    with pytest.raises(env_file.EnvFileError):
        env_file.clear_api_key(name)
    assert not env_path.exists()


# ---------------------------------------------------------------- khóa không lộ ra


def test_no_log_or_print_of_key(env_path, caplog, capsys):
    caplog.set_level(logging.DEBUG)
    env_file.set_api_key("ANTHROPIC_API_KEY", FAKE_KEY)
    env_file.clear_api_key("ANTHROPIC_API_KEY")
    with pytest.raises(env_file.EnvFileError):
        env_file.set_api_key("ANTHROPIC_API_KEY", FAKE_KEY + "\n#")
    out, err = capsys.readouterr()
    for piece in (FAKE_KEY, FAKE_KEY[-6:]):
        assert piece not in caplog.text
        assert piece not in out + err


def test_validation_error_traceback_has_no_key():
    bad = FAKE_KEY + " #lo"
    with pytest.raises(env_file.EnvFileError) as info:
        env_file.validate_key_value(bad)
    text = "".join(traceback.format_exception(info.value))
    assert FAKE_KEY not in text
    assert FAKE_KEY not in repr(info.value)
    assert info.value.__cause__ is None


def test_settings_repr_does_not_show_key(env_path):
    env_file.set_api_key("ANTHROPIC_API_KEY", FAKE_KEY)
    settings = config.load_settings(environ={})
    assert settings.anthropic_api_key == FAKE_KEY
    assert FAKE_KEY not in repr(settings)
    assert FAKE_KEY not in str(settings)


def test_check_result_repr_has_no_key():
    class Boom:
        class models:  # noqa: N801 - giả client
            @staticmethod
            def list(**_):
                import anthropic

                raise anthropic.AnthropicError(f"bad key {FAKE_KEY}")

    result = env_file.check_api_key("ANTHROPIC_API_KEY", api_key=FAKE_KEY, client=Boom())
    assert result.status == "unknown"
    assert FAKE_KEY not in repr(result)


# ---------------------------------------------------------------- symlink, chỉ đọc


@pytest.mark.skipif(os.name == "nt", reason="tạo symlink trên Windows cần quyền đặc biệt")
@pytest.mark.parametrize("action", ["set", "clear"])
def test_symlink_env_is_refused(tmp_path, action):
    # T-021 (Lá Chắn #3): .env là symlink thì từ chối ghi, không đụng cả liên kết lẫn file đích.
    outside = tmp_path / "ngoai" / "secret.env"
    outside.parent.mkdir()
    original = "A=1\nANTHROPIC_API_KEY=cu\n"
    write_bytes(outside, original)
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    link = app_dir / ".env"
    link.symlink_to(outside)

    with pytest.raises(env_file.EnvFileError) as info:
        if action == "set":
            env_file.set_api_key("ANTHROPIC_API_KEY", FAKE_KEY, link)
        else:
            env_file.clear_api_key("ANTHROPIC_API_KEY", link)

    assert read_raw(outside) == original, "file đích ngoài thư mục app không được bị ghi"
    assert link.is_symlink() and link.readlink() == outside, "liên kết giữ nguyên"
    assert [p.name for p in app_dir.iterdir()] == [".env"], "không sót file tạm"
    message = str(info.value)
    for leak in (str(tmp_path), "ngoai", "secret.env", FAKE_KEY):
        assert leak not in message
    assert "symlink" in message or "liên kết" in message


@pytest.mark.skipif(os.name == "nt", reason="tạo symlink trên Windows cần quyền đặc biệt")
def test_symlink_to_directory_gives_friendly_error_without_path(tmp_path):
    target = tmp_path / "thu-muc-bi-mat"
    target.mkdir()
    link = tmp_path / ".env"
    link.symlink_to(target, target_is_directory=True)
    with pytest.raises(env_file.EnvFileError) as info:
        env_file.set_api_key("ANTHROPIC_API_KEY", FAKE_KEY, link)
    assert str(tmp_path) not in str(info.value)
    assert "thu-muc-bi-mat" not in str(info.value)
    assert list(target.iterdir()) == []


@pytest.mark.skipif(os.name == "nt", reason="tạo symlink trên Windows cần quyền đặc biệt")
@pytest.mark.parametrize("action", ["set", "clear"])
def test_dangling_symlink_is_refused(tmp_path, action):
    folder = tmp_path / "app"
    folder.mkdir()
    link = folder / ".env"
    link.symlink_to(tmp_path / "khong-co")
    # T-021 (Lá Chắn #3): symlink gãy cũng bị từ chối, không tạo file nào.
    with pytest.raises(env_file.EnvFileError) as info:
        if action == "set":
            env_file.set_api_key("ANTHROPIC_API_KEY", FAKE_KEY, link)
        else:
            env_file.clear_api_key("ANTHROPIC_API_KEY", link)
    assert link.is_symlink() and link.readlink() == tmp_path / "khong-co"
    assert not (tmp_path / "khong-co").exists()
    assert [p.name for p in folder.iterdir()] == [".env"]
    assert str(tmp_path) not in str(info.value) and "khong-co" not in str(info.value)


def _permission_error(path) -> PermissionError:
    return PermissionError(errno.EACCES, "Permission denied", str(path))


@pytest.mark.parametrize("where", ["read", "mkstemp", "replace"])
def test_read_only_env_gives_friendly_error_without_path(env_path, monkeypatch, where):
    # Máy chạy test là root nên chmod không chặn được: giả lỗi quyền ở từng chỗ.
    original = "APP_PASSWORD_HASH=that\nANTHROPIC_API_KEY=cu\n"
    write_bytes(env_path, original)
    if where == "read":
        real_open = Path.open

        def fake_open(self, mode="r", *args, **kwargs):
            if self == env_path and "b" not in mode:  # chỉ chặn lần app đọc dạng chữ
                raise _permission_error(self)
            return real_open(self, mode, *args, **kwargs)

        monkeypatch.setattr(Path, "open", fake_open)
    elif where == "mkstemp":

        def fake_mkstemp(*args, dir=None, **kwargs):
            raise _permission_error(Path(dir) / ".env.tmp")

        monkeypatch.setattr(env_file.tempfile, "mkstemp", fake_mkstemp)
    else:

        def fake_replace(src, dst):
            raise _permission_error(dst)

        monkeypatch.setattr(env_file.os, "replace", fake_replace)

    with pytest.raises(env_file.EnvFileError) as info:
        env_file.set_api_key("ANTHROPIC_API_KEY", FAKE_KEY)
    message = str(info.value)
    assert str(env_path.parent) not in message
    assert FAKE_KEY not in message
    assert ".env" in message  # vẫn nói rõ là file .env
    assert read_raw(env_path) == original
    assert sorted(p.name for p in env_path.parent.iterdir()) == [".env"], "không để lại file tạm"


@pytest.mark.skipif(os.name == "nt", reason="quyền kiểu POSIX")
def test_real_read_only_file_never_crashes(env_path):
    original = "APP_PASSWORD_HASH=that\n"
    write_bytes(env_path, original)
    env_path.chmod(0o444)
    try:
        try:
            env_file.set_api_key("ANTHROPIC_API_KEY", FAKE_KEY)
        except env_file.EnvFileError as exc:
            assert str(env_path.parent) not in str(exc)
            assert read_raw(env_path) == original
        else:
            # POSIX: thư mục ghi được thì os.replace thay được file chỉ đọc.
            assert read_raw(env_path) == original + f"ANTHROPIC_API_KEY={FAKE_KEY}\n"
    finally:
        env_path.chmod(0o600)


# ---------------------------------------------------------------- lỗi thật (T-020)


def test_key_line_inside_other_multiline_value(env_path):
    original = 'NOTE="ví dụ\nANTHROPIC_API_KEY=old\n"\nX=1\n'
    write_bytes(env_path, original)
    env_file.set_api_key("ANTHROPIC_API_KEY", FAKE_KEY)
    values = dotenv_values(env_path, encoding="utf-8")
    assert values["NOTE"] == "ví dụ\nANTHROPIC_API_KEY=old\n", "biến khác không được đổi"
    assert values.get("ANTHROPIC_API_KEY") == FAKE_KEY, "khóa phải có hiệu lực"


def test_unicode_line_separator_in_comment(env_path):
    write_bytes(env_path, "# ghi chú ANTHROPIC_API_KEY=old\nX=1\n")
    env_file.set_api_key("ANTHROPIC_API_KEY", FAKE_KEY)
    assert dotenv_values(env_path, encoding="utf-8").get("ANTHROPIC_API_KEY") == FAKE_KEY


def test_single_quote_escape_matches_dotenv(env_path):
    write_bytes(env_path, "ANTHROPIC_API_KEY='abc\\'\nHIDDEN=1'\nX=1\n")
    before = dotenv_values(env_path, encoding="utf-8")
    assert "HIDDEN" not in before
    env_file.set_api_key("ANTHROPIC_API_KEY", FAKE_KEY)
    after = dotenv_values(env_path, encoding="utf-8")
    assert after.get("ANTHROPIC_API_KEY") == FAKE_KEY
    assert "HIDDEN" not in after, "không được sinh thêm biến"


# ---------------------------------------------------------------- giao diện tab Kết nối

PASSWORD = "mat-khau-thu-123"


@pytest.fixture
def ui_env(monkeypatch, tmp_path) -> Path:
    monkeypatch.setenv("APP_PASSWORD_HASH", hash_password(PASSWORD, iterations=1_000))
    path = tmp_path / ".env"
    monkeypatch.setattr(config, "DEFAULT_ENV_FILE", path)
    return path


def open_settings(project_root) -> AppTest:
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    at.text_input[0].input(PASSWORD)
    at.button[0].click().run()
    at.switch_page("views/settings.py").run()
    assert not at.exception, at.exception
    return at


def everything(at: AppTest) -> str:
    parts: list[str] = []
    for kind in ("markdown", "caption", "success", "error", "warning", "info", "toast"):
        parts.extend(str(el.value) for el in getattr(at, kind))
    parts.extend(str(el.value) for el in at.text_input)
    parts.extend(f"{k}={v!r}" for k, v in at.session_state.to_dict().items())
    return "\n".join(parts)


def test_ui_failed_write_shows_friendly_error_without_path_or_key(project_root, ui_env,
                                                                   monkeypatch):
    write_bytes(ui_env, "APP_PASSWORD_HASH=giu\n")

    def fake_replace(src, dst):
        raise _permission_error(dst)

    monkeypatch.setattr(env_file.os, "replace", fake_replace)
    at = open_settings(project_root)
    at.text_input(key="api-key-input-ANTHROPIC_API_KEY").input(FAKE_KEY)
    at.button(key="api-key-save-ANTHROPIC_API_KEY").click().run()
    assert not at.exception
    assert at.error, "phải báo lỗi"
    text = everything(at)
    assert FAKE_KEY not in text and FAKE_KEY[-6:] not in text
    assert str(ui_env.parent) not in text
    assert read_raw(ui_env) == "APP_PASSWORD_HASH=giu\n"


def test_ui_injection_through_input_keeps_env(project_root, ui_env):
    original = "APP_PASSWORD_HASH=giu\nWORDPRESS_URL=https://vi-du.vn\n"
    write_bytes(ui_env, original)
    at = open_settings(project_root)
    at.text_input(key="api-key-input-GEMINI_API_KEY").input(
        "AIzaabc APP_PASSWORD_HASH=hack"
    )
    at.button(key="api-key-save-GEMINI_API_KEY").click().run()
    assert read_raw(ui_env) == original
    assert "hack" not in everything(at)


def test_ui_key_typed_but_not_saved_leaves_session_on_other_page(project_root, ui_env):
    at = open_settings(project_root)
    at.text_input(key="api-key-input-OPENAI_API_KEY").input(FAKE_KEY)
    at.run()
    at.switch_page("views/write.py").run()
    at.run()
    dump = "\n".join(f"{k}={v!r}" for k, v in at.session_state.to_dict().items())
    assert FAKE_KEY not in dump
    assert not ui_env.exists()


# ============================================================================ T-016: kho nháp


@pytest.fixture
def store(tmp_path) -> DraftStore:
    return DraftStore(path=tmp_path / "data" / "drafts.sqlite")


TRICKY_TEXTS = [
    "Tiếng Việt có dấu: Ưu đãi đặc biệt, giá 1.250.000 ₫ — “ngoặc kép” ‘đơn’",
    "Tiếng Việt dạng NFD (tổ hợp)",  # không được chuẩn hóa thành NFC
    "Emoji 🔩🏗️👍🏽 và ký tự ngoài BMP 𠀀",
    "Xuống dòng CRLF\r\nvà CR\rvà tab\tvà NUL\x00 giữa câu",
    "Dấu \\ gạch ngược, \\[đã escape\\], \\](\\) và `code`",
    "'; DROP TABLE drafts; --",
    "Robert'); DELETE FROM drafts WHERE ('1'='1",
    "<b>đậm</b> & &amp; &lt;script&gt;",
    "",
]


def rich_snapshot(**overrides) -> DraftSnapshot:
    data = dict(
        step=3,
        keyword="cổng inox 304 gần biển",
        material={
            "Kinh nghiệm của xưởng": TRICKY_TEXTS[0],
            "Câu hỏi khách hay hỏi": "Có gỉ không?",
        },
        research=Research(
            intent=["Chủ nhà ở Đà Nẵng"],
            article_type="so sánh",
            competitors=[],
            new_angles=["Chi phí sau 5 năm"],
            questions=["Bảo hành bao lâu?"],
        ),
        research_keyword="cổng inox 304 gần biển",
        outline_title="Cổng inox [gần biển]",
        outline=[OutlineItem(heading=t or "trống", points=[t], image="") for t in TRICKY_TEXTS],
        article_title="Cổng inox 304: chọn sao cho bền",
        parts=[
            DraftPart(heading=t or "trống", versions=[t, t + " (bản 2)", "bản 3"], current=i % 3)
            for i, t in enumerate(TRICKY_TEXTS)
        ],
        review=Review.model_validate(
            {
                "scores": {"friendly": 1, "natural": 2, "readable": 3, "specific": 4, "seo": 5},
                "flags": [{"section": 1, "sentence": "Câu", "reason": "máy móc",
                           "replacement": "Câu mới"}],
                "summary": "Ổn.",
            }
        ),
        auto_fixed=2,
        ignored_flags={"câu b", "câu a"},
    )
    data.update(overrides)
    return DraftSnapshot(**data)


def comparable(snap: DraftSnapshot) -> dict:
    return snap.model_dump(exclude={"saved_at"})


def test_round_trip_tricky_text_every_version(store):
    # Chỉ Huy chốt (T-021): chữ AI đọc từ nháp được lọc lại (Lá Chắn #1), nên phần chữ AI so
    # với bản đã lọc ``clean_loaded(saved)``; từ khóa và chất liệu thật vẫn phải nguyên văn.
    snap = rich_snapshot()
    saved = store.save(snap)
    loaded = store.load(snap.id)
    assert comparable(loaded) == comparable(drafts_module.clean_loaded(saved))
    assert loaded.keyword == snap.keyword
    assert loaded.material == snap.material  # gồm cả TRICKY_TEXTS[0] nguyên văn
    assert loaded.research_keyword == snap.research_keyword
    for part, original in zip(loaded.parts, TRICKY_TEXTS, strict=True):
        assert len(part.versions) == 3
        assert part.versions[2] == "bản 3"
        if "<" not in original:  # chữ không có thẻ HTML thì giữ nguyên từng ký tự
            assert part.versions[0] == escape_link_syntax(original)
            assert part.versions[1] == escape_link_syntax(original) + " (bản 2)"
    # NFD, emoji, CRLF/NUL trong thân bài giữ nguyên, không bị chuẩn hóa
    assert loaded.parts[1].versions[0] == TRICKY_TEXTS[1]
    assert loaded.parts[2].versions[0] == TRICKY_TEXTS[2]
    assert loaded.parts[3].versions[0] == TRICKY_TEXTS[3]
    assert [p.current for p in loaded.parts] == [p.current for p in snap.parts]
    assert loaded.ignored_flags == ["câu a", "câu b"]
    assert loaded.saved_at is not None
    assert loaded.saved_at.utcoffset() == timedelta(hours=7)


def test_round_trip_user_text_is_verbatim_even_with_html(store):
    # Từ khóa và chất liệu thật là chữ người dùng gõ: không bị lọc, kể cả có HTML/link.
    raw = f"<b>đậm</b> {EVIL_LINK}\r\nNUL\x00 Tie\u0302\u0301ng"
    snap = DraftSnapshot(keyword=raw, material={"Kinh nghiệm của xưởng": raw})
    loaded = store.load(store.save(snap).id)
    assert loaded.keyword == " ".join(raw.split())  # R9-1: chỉ gộp khoảng trắng
    assert loaded.material == {"Kinh nghiệm của xưởng": raw}


def test_many_save_load_cycles_do_not_change_text(store):
    snap = rich_snapshot(parts=[DraftPart(heading="h", versions=[f"Xem {EVIL_LINK} nhé"])])
    first = store.load(store.save(snap).id)
    current = first
    for _ in range(10):
        current = store.load(store.save(current).id)
    assert comparable(current) == comparable(first), "lưu/mở nhiều lần không được thêm \\"


def test_round_trip_many_versions(store):
    versions = [f"Phiên bản số {i}: nội dung tiếng Việt ạ ơ ư" for i in range(200)]
    snap = DraftSnapshot(parts=[DraftPart(heading="Mở bài", versions=versions, current=137)])
    loaded = store.load(store.save(snap).id)
    assert loaded.parts[0].versions == versions
    assert loaded.parts[0].text == versions[137]


# ---------------------------------------------------------------- giới hạn 30 nháp


def test_limit_30_drops_exactly_the_oldest(store, monkeypatch):
    start = datetime(2026, 10, 14, 8, 0, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh"))
    ticks = iter(range(1000))

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return start + timedelta(minutes=next(ticks))

    monkeypatch.setattr(drafts_module, "datetime", Clock)
    ids = [store.save(DraftSnapshot(keyword=f"từ khóa {i}")).id for i in range(MAX_DRAFTS + 5)]
    listing = store.list_drafts(limit=100)
    assert [d.id for d in listing.drafts] == list(reversed(ids[5:]))
    for old in ids[:5]:
        with pytest.raises(DraftError):
            store.load(old)
    with sqlite3.connect(store.path) as conn:
        assert conn.execute("SELECT count(*) FROM drafts").fetchone() == (MAX_DRAFTS,)


def test_limit_counts_overwrites_once(store):
    snap = DraftSnapshot(keyword="một nháp")
    for _ in range(MAX_DRAFTS + 10):
        snap = store.save(snap)
    assert len(store.list_drafts().drafts) == 1


def test_clock_going_back_does_not_drop_just_saved_draft(store, monkeypatch):
    base = datetime(2026, 10, 14, 8, 0, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh"))
    now = {"t": base}

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return now["t"]

    monkeypatch.setattr(drafts_module, "datetime", Clock)
    for i in range(MAX_DRAFTS):
        now["t"] = base + timedelta(minutes=i)
        store.save(DraftSnapshot(keyword=f"cũ {i}"))
    now["t"] = base - timedelta(hours=1)  # đồng hồ máy bị chỉnh lùi
    saved = store.save(DraftSnapshot(keyword="bài đang viết"))
    assert store.load(saved.id).keyword == "bài đang viết"


# ---------------------------------------------------------------- giới hạn 5 MB


def test_default_limit_is_5_mb():
    assert MAX_DRAFT_BYTES == 5 * 1024 * 1024
    assert DraftStore().max_bytes == MAX_DRAFT_BYTES


def test_limit_counts_utf8_bytes_not_characters(store):
    # ~1,8 triệu ký tự (dưới 5 triệu) nhưng mỗi chữ "ệ" là 3 byte → quá 5 MB.
    text = "ệ" * 1_800_000
    with pytest.raises(DraftError) as info:
        store.save(DraftSnapshot(parts=[DraftPart(heading="h", versions=[text])]))
    assert "5 MB" in str(info.value)


def test_just_under_limit_saves_and_over_limit_keeps_old_copy(tmp_path):
    store = DraftStore(path=tmp_path / "d.sqlite", max_bytes=20_000)
    snap = store.save(DraftSnapshot(keyword="a", parts=[DraftPart(heading="h", versions=["x"])]))
    overhead = len(snap.model_dump_json().encode("utf-8")) - 1
    fits = snap.model_copy(
        update={"parts": [DraftPart(heading="h", versions=["x" * (20_000 - overhead - 50)])]}
    )
    store.save(fits)
    too_big = snap.model_copy(
        update={"parts": [DraftPart(heading="h", versions=["x" * 20_000])]}
    )
    with pytest.raises(DraftError):
        store.save(too_big)
    # bản cũ (vừa giới hạn) vẫn còn nguyên
    assert store.load(snap.id).parts[0].versions == fits.parts[0].versions


def test_oversized_row_planted_in_file_is_skipped_safely(tmp_path):
    store = DraftStore(path=tmp_path / "d.sqlite", max_bytes=10_000)
    snap = store.save(DraftSnapshot(keyword="a"))
    with sqlite3.connect(store.path) as conn:
        conn.execute("UPDATE drafts SET data = ? WHERE id = ?", ("{" + " " * 50_000 + "}", snap.id))
    with pytest.raises(DraftError):
        store.load(snap.id)
    assert [d.id for d in store.list_drafts().drafts] == [snap.id]


# ---------------------------------------------------------------- file hỏng, khuôn sai


@pytest.mark.parametrize(
    "content",
    [
        b"",  # file rỗng: SQLite coi là CSDL trống, dùng tiếp được
        b"\x00" * 4096,
        b"SQLite format 3\x00" + b"\xff" * 2000,  # đầu giống SQLite nhưng hỏng
        "Không phải SQLite — chữ tiếng Việt".encode(),
    ],
)
def test_corrupt_files_never_crash(tmp_path, content):
    path = tmp_path / "drafts.sqlite"
    path.write_bytes(content)
    store = DraftStore(path=path)
    listing = store.list_drafts()
    assert listing.drafts == []
    saved = store.save(DraftSnapshot(keyword="mới"))
    assert store.load(saved.id).keyword == "mới"
    if content:
        assert store.recovered_from is not None
        assert store.recovered_from.read_bytes() == content, "bản hỏng phải được giữ lại"


def test_truncated_real_database_never_crashes(tmp_path):
    path = tmp_path / "drafts.sqlite"
    good = DraftStore(path=path)
    for i in range(10):
        good.save(DraftSnapshot(keyword=f"bài {i}", parts=[DraftPart(heading="h",
                                                                       versions=["x" * 3000])]))
    raw = path.read_bytes()
    path.write_bytes(raw[: len(raw) // 2])
    store = DraftStore(path=path)
    try:
        listing = store.list_drafts()
        for d in listing.drafts:
            with contextlib.suppress(DraftError):
                store.load(d.id)
        store.save(DraftSnapshot(keyword="mới"))
    except DraftError:
        pass  # báo lỗi dễ hiểu là chấp nhận được; không được là lỗi khác


@pytest.mark.parametrize(
    "data",
    [
        "null",
        "[]",
        '"chuỗi"',
        "không phải JSON",
        "{" * 100_000,
        '{"keyword": ' + "[" * 100_000 + "]" * 100_000 + "}",
        '{"keyword": 1e999999}',
    ],
)
def test_bad_json_in_row_gives_draft_error(store, data):
    snap = store.save(DraftSnapshot(keyword="a"))
    with sqlite3.connect(store.path) as conn:
        conn.execute("UPDATE drafts SET data = ? WHERE id = ?", (data, snap.id))
    with pytest.raises(DraftError):
        store.load(snap.id)


@pytest.mark.parametrize(
    "change",
    [
        {"parts": [{"heading": "h", "versions": [], "current": 0, "image": ""}]},
        {"parts": [{"heading": "h", "versions": ["a"], "current": -1, "image": ""}]},
        {"step": -1},
        {"step": 5},
        {"auto_fixed": -3},
        {"material": {f"nhãn {i}": "x" for i in range(21)}},
        {"saved_at": "2026-10-14T08:00:00"},  # thiếu múi giờ
        {"schema_version": 2},
        {"id": "f" * 32},  # không khớp mã dòng
        {"research": {"intent": "không phải danh sách"}},
        {"secret": "sk-ant-abc"},
    ],
)
def test_wrong_shape_rows_give_draft_error(store, change):
    snap = store.save(DraftSnapshot(keyword="a"))
    obj = json.loads(snap.model_dump_json())
    obj.update(change)
    with sqlite3.connect(store.path) as conn:
        conn.execute("UPDATE drafts SET data = ? WHERE id = ?", (json.dumps(obj), snap.id))
    with pytest.raises(DraftError) as info:
        store.load(snap.id)
    assert "sk-ant-abc" not in str(info.value)


@pytest.mark.parametrize("bad_id", [None, 123, b"0" * 32, "0" * 31, "0" * 33, "A" * 32,
                                    "０" * 32, "0" * 32 + "\n", "' OR '1'='1",
                                    "0" * 16 + "'; --" + "0" * 11])
def test_bad_ids_give_draft_error_for_every_operation(store, bad_id):
    store.save(DraftSnapshot(keyword="giữ lại"))
    with pytest.raises(DraftError):
        store.load(bad_id)
    with pytest.raises(DraftError):
        store.delete(bad_id)
    assert len(store.list_drafts().drafts) == 1


def test_sql_in_content_is_stored_as_data(store):
    evil = "x'); DROP TABLE drafts; --"
    snap = store.save(DraftSnapshot(keyword=evil, article_title=evil,
                                    material={evil: evil}))
    other = store.save(DraftSnapshot(keyword="khác"))
    loaded = store.load(snap.id)
    assert loaded.keyword == evil and loaded.material == {evil: evil}
    titles = {d.title for d in store.list_drafts().drafts}
    assert titles == {evil, "khác"}
    assert store.load(other.id).keyword == "khác"


def test_planted_listing_rows_with_wrong_types_are_skipped(store):
    good = store.save(DraftSnapshot(keyword="tốt"))
    with sqlite3.connect(store.path) as conn:
        conn.execute(
            "INSERT INTO drafts VALUES (?, ?, ?, ?, ?, ?)",
            ("1" * 32, b"\xff\xfe", "kw", "2026-10-14T08:00:00+07:00", 1e12, "{}"),
        )
        conn.execute(
            "INSERT INTO drafts VALUES (?, ?, ?, ?, ?, ?)",
            ("2" * 32, "t", "kw", "không phải ngày", 1e12, "{}"),
        )
        conn.execute(
            "INSERT INTO drafts VALUES (?, ?, ?, ?, ?, ?)",
            ("../../etc/passwd", "t", "kw", "2026-10-14T08:00:00+07:00", 1e12, "{}"),
        )
    listing = store.list_drafts()
    assert [d.id for d in listing.drafts] == [good.id]
    assert listing.skipped == 3


def test_unwritable_folder_error_has_no_path(tmp_path, monkeypatch):
    target = tmp_path / "bi-mat" / "drafts.sqlite"

    def boom(self, *args, **kwargs):
        raise PermissionError(errno.EACCES, "Permission denied", str(self))

    monkeypatch.setattr(Path, "mkdir", boom)
    with pytest.raises(DraftError) as info:
        DraftStore(path=target).list_drafts()
    assert "bi-mat" not in str(info.value)
    assert str(tmp_path) not in str(info.value)


def test_snapshot_cannot_carry_secret_fields():
    for field_name in ("api_key", "ANTHROPIC_API_KEY", "password", "env"):
        with pytest.raises(ValueError):
            DraftSnapshot(**{field_name: "x"})


# ---------------------------------------------------------------- nội dung độc trong file


def plant(store: DraftStore, mutate) -> str:
    snap = store.save(DraftSnapshot(keyword="a"))
    obj = json.loads(snap.model_dump_json())
    mutate(obj)
    with sqlite3.connect(store.path) as conn:
        conn.execute("UPDATE drafts SET data = ? WHERE id = ?", (json.dumps(obj), snap.id))
    return snap.id


def has_live_link(text: str) -> bool:
    return escape_link_syntax(text) != text


def test_planted_links_in_article_versions_are_disabled(store):
    draft_id = plant(
        store,
        lambda o: o.update(
            parts=[{"heading": "h", "versions": [EVIL_LINK, "x\n[a]: https://evil.example"],
                    "current": 1, "image": ""}]
        ),
    )
    loaded = store.load(draft_id)
    assert not any(has_live_link(v) for v in loaded.parts[0].versions)


def test_planted_links_and_html_in_research_and_review_are_disabled(store):
    evil = f"{EVIL_LINK} <img src=x onerror=alert(1)><script>alert(1)</script>"

    def mutate(o):
        o["research"] = {
            "intent": [evil],
            "article_type": evil,
            "competitors": [{"title": "t", "url": "https://ok.example", "covers": evil,
                             "missing": evil}],
            "new_angles": [evil],
            "questions": [evil],
        }
        o["review"] = {
            "scores": {"friendly": 1, "natural": 1, "readable": 1, "specific": 1, "seo": 1},
            "flags": [{"section": 0, "sentence": "s", "reason": evil, "replacement": evil}],
            "summary": evil,
        }

    loaded = store.load(plant(store, mutate))
    r, rv = loaded.research, loaded.review
    texts = [*r.intent, r.article_type, r.competitors[0].covers, r.competitors[0].missing,
             *r.new_angles, *r.questions, rv.summary, rv.flags[0].reason,
             rv.flags[0].replacement]
    for text in texts:
        assert not has_live_link(text)
        assert "<script" not in text.lower() and "onerror" not in text.lower()


def test_error_message_does_not_echo_file_content(store):
    draft_id = plant(store, lambda o: o.update(material={EVIL_LINK: 123}))
    with pytest.raises(DraftError) as info:
        store.load(draft_id)
    assert "evil.example" not in str(info.value)


# ---------------------------------------------------------------- lỗi thật (T-016)


@pytest.mark.parametrize("remove", ["file", "folder"])
def test_deleting_drafts_file_while_running_recovers(tmp_path, remove):
    path = tmp_path / "data" / "drafts.sqlite"
    store = DraftStore(path=path)
    store.save(DraftSnapshot(keyword="trước"))
    if remove == "file":
        path.unlink()
    else:
        for child in path.parent.iterdir():
            child.unlink()
        path.parent.rmdir()
    saved = store.save(DraftSnapshot(keyword="sau"))
    assert store.load(saved.id).keyword == "sau"


def test_default_store_follows_patched_default_path():
    assert DraftStore().path == drafts_module.DEFAULT_DRAFTS_FILE


def test_lone_surrogate_gives_draft_error(store):
    with pytest.raises(DraftError):
        store.save(DraftSnapshot(keyword="abc\ud800"))
