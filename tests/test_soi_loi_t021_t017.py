"""Soi Lỗi lần 2: kiểm lại T-021 (sửa kho nháp và ghi ``.env``) và kiểm thử T-017 (tự lưu, mở,
xóa nháp trên trang Soạn bài).

Mọi test dùng thư mục tạm: không đọc/ghi ``.env`` hay ``data/`` thật, không gọi mạng.
"""

from __future__ import annotations

import json
import random
import sqlite3
from pathlib import Path

import pytest
import test_app_pages as pages
from dotenv import dotenv_values
from test_app_pages import button, go_to_article, write_page

import seo_app.config as config
import seo_app.storage.drafts as drafts
from seo_app import env_file
from seo_app.content.models import OutlineItem, Research, Review
from seo_app.sanitize import escape_link_syntax
from seo_app.storage import DraftError, DraftPart, DraftSnapshot, DraftStore
from seo_app.text import markdown_link

env = pages.env  # mật khẩu thử, không có khóa AI thật
fake_ai = pages.fake_ai

FAKE_KEY = "sk-ant-api03-SoiLoiLan2_KhoaGia-0123456789abcd"
EVIL = (
    "[bấm vào đây](https://evil.example/x) ![ảnh](https://evil.example/a.png) "
    "<img src=x onerror=alert(1)><script>alert(1)</script> [ref]\n[ref]: https://evil.example/r"
)


# ============================================================================ T-021 phần A


def store_at(tmp_path: Path) -> DraftStore:
    return DraftStore(path=tmp_path / "data" / "drafts.sqlite")


def plant(store: DraftStore, obj: dict) -> None:
    with sqlite3.connect(store.path) as conn:
        conn.execute("UPDATE drafts SET data = ? WHERE id = ?", (json.dumps(obj), obj["id"]))


def has_live_link(text: str) -> bool:
    return escape_link_syntax(text) != text


def full_poisoned(store: DraftStore) -> dict:
    """Một nháp có MỌI trường chữ bị cài nội dung độc."""
    snap = store.save(DraftSnapshot(keyword="a"))
    obj = json.loads(snap.model_dump_json())
    obj.update(
        keyword=EVIL,
        research_keyword=EVIL,
        material={"Kinh nghiệm của xưởng": EVIL},
        research={
            "intent": [EVIL],
            "article_type": EVIL,
            "competitors": [
                {"title": EVIL, "url": "javascript:alert(1)", "covers": EVIL, "missing": EVIL}
            ],
            "new_angles": [EVIL],
            "questions": [EVIL],
        },
        outline_title=EVIL,
        outline=[{"heading": EVIL, "points": [EVIL], "image": EVIL}],
        article_title=EVIL,
        parts=[{"heading": EVIL, "versions": [EVIL, EVIL], "current": 1, "image": EVIL}],
        review={
            "scores": {"friendly": 1, "natural": 1, "readable": 1, "specific": 1, "seo": 1},
            "flags": [{"section": 0, "sentence": EVIL, "reason": EVIL, "replacement": EVIL}],
            "summary": EVIL,
        },
    )
    plant(store, obj)
    return obj


# Trường người dùng gõ (không phải chữ AI): giữ nguyên theo quyết định T-021.
USER_FIELDS = {"keyword", "material"}
# Câu chép nguyên văn từ bài để tìm chỗ sửa, không hiển thị như Markdown.
NOT_RENDERED = {("review", "flags", 0, "sentence")}


def string_leaves(value, path=()):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for k, v in value.items():
            yield from string_leaves(v, (*path, k))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from string_leaves(v, (*path, i))


def test_poison_is_disabled_in_every_ai_field(tmp_path):
    store = store_at(tmp_path)
    obj = full_poisoned(store)
    loaded = store.load(obj["id"]).model_dump(mode="json", exclude={"saved_at", "id"})
    checked = 0
    for path, text in string_leaves(loaded):
        if path[0] in USER_FIELDS or path in NOT_RENDERED or path[0] == "ignored_flags":
            continue
        checked += 1
        low = text.lower()
        assert "<script" not in low and "onerror" not in low and "<img" not in low, path
        if path[0] == "parts" and path[2] == "versions":
            assert not has_live_link(text), path  # thân bài: link bị escape
        elif path[:2] == ("research", "competitors") and path[-1] == "url":
            assert not text.lower().startswith("javascript"), path
        elif path[:2] == ("research", "competitors") and path[-1] == "title":
            # Tên bài đối thủ chỉ bỏ thẻ (clean_research); giao diện hiện qua markdown_link,
            # hàm này escape mọi ký tự Markdown nên link không sống lại.
            shown = markdown_link(text, loaded["research"]["competitors"][0]["url"])
            assert not has_live_link(shown), path
        else:
            # dàn ý lưu ở dạng ô sửa (chưa escape): giao diện escape lại khi dùng; mọi chữ
            # AI khác thì địa chỉ link bị bỏ hẳn.
            assert "evil.example" not in text, path
    assert checked >= 18


def test_user_fields_are_kept_verbatim_when_poisoned(tmp_path):
    store = store_at(tmp_path)
    obj = full_poisoned(store)
    loaded = store.load(obj["id"])
    # R9-1: từ khóa chỉ được gộp khoảng trắng về một dòng, chữ giữ nguyên
    assert loaded.keyword == " ".join(EVIL.split())
    # research_keyword hiện trong st.warning nên được lọc như chữ một dòng (Lá Chắn #4)
    assert "evil.example" not in loaded.research_keyword
    assert loaded.material == {"Kinh nghiệm của xưởng": EVIL}


def realistic_snapshot() -> DraftSnapshot:
    """Nháp như luồng thật tạo ra: chữ AI đã qua bộ lọc (dùng chính ``clean_loaded``)."""
    raw = DraftSnapshot(
        step=3,
        keyword="cửa cuốn [Austdoor] giá bao nhiêu?",
        material={"Số liệu của bạn": "Cửa 3×3 m giá 12–15 triệu, lắp trong 1 ngày"},
        research=Research(
            intent=["Chủ nhà ở Q.7 muốn biết giá *trọn gói*"],
            article_type="bảng giá + hướng dẫn",
            competitors=[],
            new_angles=["Giá thật sau khi thêm motor [cần bổ sung: giá motor]"],
            questions=["Bảo hành bao lâu?"],
        ),
        research_keyword="cửa cuốn [Austdoor] giá bao nhiêu?",
        outline_title="Giá cửa cuốn [2026]: bảng giá thật",
        outline=[OutlineItem(heading="Giá [theo m²]", points=["`code` và \\ gạch"], image="")],
        article_title="Giá cửa cuốn: bảng giá thật",
        parts=[
            DraftPart(
                heading="Mở bài",
                versions=[
                    "Giá [cần bổ sung: giá 1 m²]: chênh khoảng…\r\n- ý 1\n- ý *2*",
                    "Xem [mục giá](#gia) nhé",
                ],
                current=1,
            )
        ],
        review=Review.model_validate(
            {
                "scores": {"friendly": 80, "natural": 70, "readable": 90, "specific": 60,
                           "seo": 85},
                "flags": [{"section": 0, "sentence": "Mở bài", "reason": "chung chung",
                           "replacement": "Câu cụ thể hơn"}],
                "summary": "Cần thêm ví dụ [thật].",
            }
        ),
        auto_fixed=1,
        ignored_flags=["x"],
    )
    return drafts.clean_loaded(raw)


def test_clean_draft_unchanged_after_many_save_open_cycles(tmp_path):
    store = store_at(tmp_path)
    clean = realistic_snapshot()
    first = store.load(store.save(clean).id)
    assert first.model_dump(exclude={"saved_at"}) == clean.model_dump(exclude={"saved_at"})
    current = first
    for _ in range(8):
        current = store.load(store.save(current).id)
    assert current.model_dump(exclude={"saved_at"}) == clean.model_dump(exclude={"saved_at"})


ALPHABET = list("ab ệ[]()<>!`*\\:#\r\n\t-1.") + ["](", "<b>", "</b>", "http://x.vn", "<!--"]


@pytest.mark.parametrize("seed", range(3))
def test_cleaning_is_idempotent_on_random_text(seed):
    # Bản đã lọc một lần, lọc lại phải không đổi: nếu không, mỗi lần mở nháp chữ lại đổi.
    rng = random.Random(seed)

    def text() -> str:
        return "".join(rng.choice(ALPHABET) for _ in range(rng.randint(0, 30)))

    for _ in range(300):
        snap = DraftSnapshot(
            outline_title=text(),
            outline=[OutlineItem(heading=text(), points=[text()], image=text())],
            article_title=text(),
            parts=[DraftPart(heading=text(), versions=[text(), text()], image=text())],
            research=Research(intent=[text()], article_type=text(), competitors=[],
                              new_angles=[text()], questions=[text()]),
        )
        once = drafts.clean_loaded(snap)
        twice = drafts.clean_loaded(once)
        assert twice.model_dump() == once.model_dump(), snap.model_dump()


def test_recreated_after_delete_keeps_limit_and_reports_nothing_wrong(tmp_path):
    store = store_at(tmp_path)
    store.save(DraftSnapshot(keyword="trước"))
    store.path.unlink()
    saved = store.save(DraftSnapshot(keyword="sau"))
    assert [d.id for d in store.list_drafts().drafts] == [saved.id]
    assert store.recovered_from is None  # file mất không phải file hỏng


def test_error_messages_never_echo_planted_text(tmp_path):
    store = store_at(tmp_path)
    snap = store.save(DraftSnapshot(keyword="a"))
    for change in (
        {"material": {"[x](https://evil.example)": 1}},
        {"https://evil.example": 1},
        {"parts": [{"heading": 1, "versions": ["https://evil.example"], "current": 0,
                    "image": ""}]},
        {"step": "https://evil.example"},
    ):
        obj = json.loads(snap.model_dump_json())
        obj.update(change)
        plant(store, obj)
        with pytest.raises(DraftError) as info:
            store.load(snap.id)
        assert "evil.example" not in str(info.value), change


# ============================================================================ T-021 phần B


@pytest.fixture
def env_path(monkeypatch, tmp_path) -> Path:
    path = tmp_path / ".env"
    monkeypatch.setattr(config, "DEFAULT_ENV_FILE", path)
    return path


def raw(path: Path) -> str:
    return path.read_bytes().decode("utf-8")


AFTER = "APP_PASSWORD_HASH=pbkdf2$giu\nWORDPRESS_APP_PASSWORD=abcd efgh\n# cuối\nX=1\n"


@pytest.mark.parametrize(
    "broken",
    [
        'ANTHROPIC_API_KEY="sk-cu\n',
        "ANTHROPIC_API_KEY='sk-cu\n",
        'export ANTHROPIC_API_KEY = "sk-cu\n',
        '\n\n  ANTHROPIC_API_KEY="sk-cu\n',  # dòng trống phía trước
        'ANTHROPIC_API_KEY="sk-cu\\"\n',
    ],
)
@pytest.mark.parametrize("action", ["set", "clear"])
def test_unclosed_quote_never_loses_following_lines(env_path, broken, action):
    original = "# đầu\n" + broken + AFTER
    env_path.write_bytes(original.encode("utf-8"))
    with pytest.raises(env_file.EnvFileError) as info:
        if action == "set":
            env_file.set_api_key("ANTHROPIC_API_KEY", FAKE_KEY)
        else:
            env_file.clear_api_key("ANTHROPIC_API_KEY")
    assert raw(env_path) == original
    assert "sk-cu" not in str(info.value)
    assert sorted(p.name for p in env_path.parent.iterdir()) == [".env"]


def test_unclosed_quote_on_other_variable_keeps_every_line(env_path):
    original = 'OTHER="chưa đóng\n' + AFTER
    env_path.write_bytes(original.encode("utf-8"))
    before = dotenv_values(env_path, encoding="utf-8", interpolate=False)
    env_file.set_api_key("ANTHROPIC_API_KEY", FAKE_KEY)
    text = raw(env_path)
    assert text.startswith(original), "mọi dòng cũ phải còn nguyên"
    after = dotenv_values(env_path, encoding="utf-8", interpolate=False)
    assert after.pop("ANTHROPIC_API_KEY") == FAKE_KEY
    assert after == before


def test_other_variable_referencing_key_is_untouched(env_path):
    original = "ALIAS=${ANTHROPIC_API_KEY}\nANTHROPIC_API_KEY=cu\n"
    env_path.write_bytes(original.encode("utf-8"))
    env_file.set_api_key("ANTHROPIC_API_KEY", FAKE_KEY)
    assert raw(env_path) == f"ALIAS=${{ANTHROPIC_API_KEY}}\nANTHROPIC_API_KEY={FAKE_KEY}\n"
    assert config.load_settings(environ={}).anthropic_api_key == FAKE_KEY


def corrupting_first_write(monkeypatch):
    """Giả đĩa ghi sai ở lần ghi đầu (ví dụ phần mềm đồng bộ chen vào); lần sau ghi đúng."""
    real = env_file._atomic_write
    calls: list[str] = []

    def fake(path, content):
        calls.append(content)
        real(path, content.replace(FAKE_KEY, "sk-hong") if len(calls) == 1 else content)

    monkeypatch.setattr(env_file, "_atomic_write", fake)
    return calls


def test_restore_old_file_when_read_back_differs(env_path, monkeypatch):
    original = "﻿# BOM và CRLF\r\nAPP_PASSWORD_HASH=giu\r\nANTHROPIC_API_KEY=cu\r\n"
    env_path.write_bytes(original.encode("utf-8"))
    calls = corrupting_first_write(monkeypatch)
    with pytest.raises(env_file.EnvFileError) as info:
        env_file.set_api_key("ANTHROPIC_API_KEY", FAKE_KEY)
    assert len(calls) == 2, "phải ghi lại bản cũ"
    assert raw(env_path) == original, "khôi phục đúng từng byte, kể cả BOM và CRLF"
    assert FAKE_KEY not in str(info.value)
    assert "Đã lưu" not in str(info.value)


def test_restore_removes_new_file_when_none_existed(env_path, monkeypatch):
    corrupting_first_write(monkeypatch)
    with pytest.raises(env_file.EnvFileError):
        env_file.set_api_key("ANTHROPIC_API_KEY", FAKE_KEY)
    assert not env_path.exists()
    assert list(env_path.parent.iterdir()) == []


def test_restore_failure_still_gives_friendly_error(env_path, monkeypatch):
    env_path.write_bytes(b"ANTHROPIC_API_KEY=cu\n")
    real = env_file._atomic_write
    calls: list[int] = []

    def fake(path, content):
        calls.append(1)
        if len(calls) == 1:
            real(path, content.replace(FAKE_KEY, "sk-hong"))
        else:
            raise env_file.EnvFileError("Không ghi được file .env (PermissionError).")

    monkeypatch.setattr(env_file, "_atomic_write", fake)
    with pytest.raises(env_file.EnvFileError) as info:
        env_file.set_api_key("ANTHROPIC_API_KEY", FAKE_KEY)
    assert FAKE_KEY not in str(info.value)
    assert str(env_path.parent) not in str(info.value)


def test_ui_reports_format_error_not_saved(project_root, monkeypatch, tmp_path):
    from streamlit.testing.v1 import AppTest

    from seo_app.auth import hash_password

    monkeypatch.setenv("APP_PASSWORD_HASH", hash_password("mk-thu-123", iterations=1_000))
    path = tmp_path / ".env"
    monkeypatch.setattr(config, "DEFAULT_ENV_FILE", path)
    original = 'ANTHROPIC_API_KEY="sk-cu\n' + AFTER
    path.write_bytes(original.encode("utf-8"))

    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    at.text_input[0].input("mk-thu-123")
    at.button[0].click().run()
    at.switch_page("views/settings.py").run()
    at.text_input(key="api-key-input-ANTHROPIC_API_KEY").input(FAKE_KEY)
    at.button(key="api-key-save-ANTHROPIC_API_KEY").click().run()
    assert not at.exception
    assert any("sai định dạng" in e.value for e in at.error)
    assert not any("Đã lưu" in s.value for s in at.success)
    assert raw(path) == original
    dump = repr(at.session_state.to_dict())
    assert FAKE_KEY not in dump


# ============================================================================ T-017


def store() -> DraftStore:
    return DraftStore(drafts.DEFAULT_DRAFTS_FILE)


def sample(**changes) -> DraftSnapshot:
    data = dict(
        step=2,
        keyword="cổng inox gần biển",
        material={"Kinh nghiệm của xưởng": "Chất liệu bài A"},
        research_keyword="cổng inox gần biển",
        outline_title="Tiêu đề A",
        outline=[OutlineItem(heading="Mục A1", points=["ý"], image="")],
        article_title="Bài A",
        parts=[DraftPart(heading="Mở đầu", versions=["Thân bài A."])],
    )
    data.update(changes)
    return DraftSnapshot(**data)


def material_keys(at) -> dict:
    return {k: v for k, v in at.session_state.to_dict().items() if str(k).startswith("real-")}


def test_opening_draft_b_does_not_carry_material_of_open_draft_a(project_root):
    a = store().save(sample())
    b = store().save(
        sample(keyword="cửa sắt", material={"Số liệu của bạn": "Chất liệu bài B"},
               article_title="Bài B", outline=[], parts=[])
    )
    at = write_page(project_root)
    button(at, "Mở", key=f"open-{a.id}").click().run()
    assert at.session_state["real-Kinh nghiệm của xưởng"] == "Chất liệu bài A"
    at.session_state["step"] = 0
    at.run()
    button(at, "Mở", key=f"open-{b.id}").click().run()
    assert not at.exception, at.exception
    assert at.session_state["draft_id"] == b.id
    assert material_keys(at) == {"real-Số liệu của bạn": "Chất liệu bài B"}
    assert at.session_state["outline_ids"] == [] and at.session_state["part_ids"] == []
    assert not any(str(k).startswith(("h-", "texts-")) for k in at.session_state.to_dict())
    # nháp A không bị bài B ghi đè
    assert store().load(a.id).material == {"Kinh nghiệm của xưởng": "Chất liệu bài A"}
    assert store().load(a.id).article_title == "Bài A"


def test_new_article_after_opened_draft_starts_clean(project_root):
    a = store().save(sample())
    at = write_page(project_root)
    button(at, "Mở", key=f"open-{a.id}").click().run()
    at.session_state["_start_keyword"] = "lan can kính"
    at.session_state["step"] = 0
    at.run()
    assert not at.exception, at.exception
    assert at.session_state.get("draft_id") != a.id
    assert all(v == "" for v in material_keys(at).values())
    assert at.session_state["part_ids"] == []
    assert store().load(a.id).material == {"Kinh nghiệm của xưởng": "Chất liệu bài A"}


def test_failed_open_keeps_current_work(project_root):
    a = store().save(sample())
    bad = store().save(sample(keyword="hỏng"))
    obj = json.loads(bad.model_dump_json())
    obj["step"] = 99
    with sqlite3.connect(store().path) as conn:
        conn.execute("UPDATE drafts SET data = ? WHERE id = ?", (json.dumps(obj), bad.id))
    at = write_page(project_root)
    button(at, "Mở", key=f"open-{a.id}").click().run()
    at.session_state["_open_draft"] = bad.id
    at.run()
    assert not at.exception, at.exception
    assert at.error, "phải báo nháp hỏng"
    assert at.session_state["draft_id"] == a.id
    assert at.session_state["real-Kinh nghiệm của xưởng"] == "Chất liệu bài A"


def test_deleting_other_draft_keeps_open_one(project_root):
    a = store().save(sample())
    other = store().save(sample(keyword="khác"))
    at = write_page(project_root)
    button(at, "Mở", key=f"open-{a.id}").click().run()
    at.session_state["step"] = 0
    at.run()
    button(at, "Xóa hẳn", key=f"del-{other.id}").click().run()
    assert not at.exception, at.exception
    assert at.session_state["draft_id"] == a.id
    assert at.session_state["keyword"] == "cổng inox gần biển"
    assert [d.id for d in store().list_drafts().drafts] == [a.id]


def test_poisoned_draft_does_not_render_links_or_html(project_root):
    st = store()
    obj = full_poisoned(st)
    obj["step"] = 0  # bước Chuẩn bị hiện kết quả nghiên cứu
    # Chữ người dùng gõ (giữ nguyên theo T-021) kiểm riêng ở test R9-1; ở đây chỉ chữ AI.
    obj["keyword"] = obj["research_keyword"] = "cổng inox"
    obj["material"] = {}
    plant(st, obj)
    at = write_page(project_root)
    button(at, "Mở", key=f"open-{obj['id']}").click().run()
    assert not at.exception, at.exception
    for step in range(5):
        at.session_state["step"] = step
        at.run()
        assert not at.exception, (step, at.exception)
        for kind in ("markdown", "caption", "info", "warning", "success", "error"):
            for el in getattr(at, kind):
                text = str(el.value)
                assert "](https://evil.example" not in text, (step, kind, text)
                assert "<script" not in text.lower() and "onerror" not in text.lower()


def test_tests_never_write_real_data_folder(project_root, fake_ai):
    real = config.PROJECT_ROOT / "data" / "drafts.sqlite"
    before = real.stat().st_mtime_ns if real.exists() else None
    assert real != drafts.DEFAULT_DRAFTS_FILE
    assert DraftStore().path == drafts.DEFAULT_DRAFTS_FILE
    at = go_to_article(write_page(project_root))
    assert at.session_state.get("draft_id")
    assert store().list_drafts().drafts, "nháp phải nằm trong kho tạm"
    after = real.stat().st_mtime_ns if real.exists() else None
    assert after == before


def test_inputs_keep_text_after_leaving_step_one(project_root, fake_ai):
    at = write_page(project_root)
    texts = {
        "real-Kinh nghiệm của xưởng": "Xưởng ở Bình Dương, 12 năm làm cổng",
        "real-Số liệu của bạn": "Cổng 4 m giá 18 triệu",
        "real-Câu hỏi khách hay hỏi": "Có gỉ không?",
    }
    for key, value in texts.items():
        at.text_area(key=key).input(value).run()
    at = go_to_article(at)
    uid = at.session_state["outline_ids"][0]
    heading = at.session_state[f"h-{uid}"]
    title = at.session_state["outline_title"]
    for _ in range(4):  # Streamlit bỏ giá trị ô không vẽ sau vài lần chạy
        at.run()
    for key, value in texts.items():
        assert at.session_state[key] == value
    assert at.session_state["keyword"] == "so sánh inox 201 và 304"
    assert at.session_state[f"h-{uid}"] == heading
    assert at.session_state["outline_title"] == title
    # Quay lại bước 1: các ô hiện đúng chữ đã gõ
    at.session_state["step"] = 0
    at.run()
    assert not at.exception, at.exception
    for key, value in texts.items():
        assert at.text_area(key=key).value == value
    assert at.text_input(key="keyword").value == "so sánh inox 201 và 304"
    saved = store().load(at.session_state["draft_id"])
    assert saved.material == {k.removeprefix("real-"): v for k, v in texts.items()}


def test_planted_keyword_cannot_render_links(project_root):
    st = store()
    snap = st.save(sample(step=0))
    obj = json.loads(snap.model_dump_json())
    obj["keyword"] = "cổng\n\n[bấm vào đây](https://evil.example/k)"
    obj["research_keyword"] = "[bấm vào đây](https://evil.example/r)"
    obj["research"] = {"intent": ["ý"], "article_type": "x", "competitors": [],
                       "new_angles": [], "questions": []}
    plant(st, obj)
    at = write_page(project_root)
    button(at, "Mở", key=f"open-{snap.id}").click().run()
    assert not at.exception, at.exception
    for kind in ("markdown", "caption", "info", "warning", "success", "error"):
        for el in getattr(at, kind):
            text = str(el.value)
            if 'class="page-sub"' in text:
                assert "\n\n" not in text, text  # không thoát khỏi khối HTML
            else:
                assert "](https://evil.example" not in text, (kind, text)
