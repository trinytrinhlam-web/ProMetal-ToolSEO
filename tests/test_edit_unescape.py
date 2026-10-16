"""T-012: ô sửa chữ không hiện dấu "\\" do ``escape_link_syntax`` thêm; lưu lại thì escape lại.

- Unit: ``unescape_link_syntax`` đúng là nghịch đảo của ``escape_link_syntax``.
- AppTest: ô «Sửa trực tiếp» và ô tiêu đề dàn ý trên trang Soạn bài (AI giả, không gọi mạng).
"""

import random

import pytest
from fake_ai import DRAFT, OUTLINE, SCORES, FakeProvider
from streamlit.testing.v1 import AppTest
from test_sanitize_autolink import gfm_autolinks

from seo_app.ai import registry as ai_registry
from seo_app.auth import hash_password
from seo_app.content.models import Draft, Flag, Outline, OutlineItem, Review
from seo_app.sanitize import (
    break_autolinks,
    clean_ai_text,
    escape_link_syntax,
    unescape_link_syntax,
)

PASSWORD = "mat-khau-thu-123"

# (chữ người đọc thấy, chữ sau escape) — trường hợp tiêu biểu trong bài tiếng Việt
PAIRS = [
    ("Giá [cần bổ sung: giá](tạm tính)", "Giá [cần bổ sung: giá]\\(tạm tính)"),
    ("Cổng [A][B] đẹp", "Cổng [A]\\[B] đẹp"),
    ("[Lưu ý]: đo khe ray", "[Lưu ý]\\: đo khe ray"),
    ("- [Mẹo]: lau khô", "- [Mẹo]\\: lau khô"),
    ("> [Ghi chú]: xem lại", "> [Ghi chú]\\: xem lại"),
    ("Mục [1] và [2]: giữ nguyên", "Mục [1] và [2]: giữ nguyên"),
    # Địa chỉ trần có ký tự ngắt rộng 0 (T-031), ô sửa cũng không hiện nó
    ("Xem [bảng giá](https://evil.example)", "Xem [bảng giá]\\(https:/\u200b/evil.example)"),
    ("Dòng 1\n[nhãn]: https://evil.example", "Dòng 1\n[nhãn]\\: https:/\u200b/evil.example"),
    ("Không có ngoặc vuông.", "Không có ngoặc vuông."),
]


# ------------------------------------------------------------------------- unit


@pytest.mark.parametrize(("plain", "escaped"), PAIRS)
def test_unescape_is_inverse_of_escape(plain, escaped):
    assert escape_link_syntax(plain) == escaped
    assert unescape_link_syntax(escaped) == plain
    assert escape_link_syntax(unescape_link_syntax(escaped)) == escaped


@pytest.mark.parametrize(
    "text",
    [
        "Đường dẫn C:\\thu-muc\\anh.jpg",  # "\" của người dùng, không do escape thêm
        "Ký hiệu \\[ và \\] giữ nguyên",
        "Giá 5\\* sao",
        "x]\\y",  # "\" sau "]" nhưng ký tự sau không phải ( [ :
        "Câu [a]\\: giữa dòng",  # ":" giữa dòng không bao giờ được escape -> không bỏ "\"
    ],
)
def test_unescape_keeps_other_backslashes(text):
    assert unescape_link_syntax(text) == text


def test_unescape_on_clean_ai_text_round_trips():
    """Chữ AI đã lọc: bỏ "\\" để sửa, escape lại thì ra đúng như trước."""
    for raw in [
        "Giá [cần bổ sung: giá](tạm)\n\n[x]: https://a.example\n[A][B]",
        "> - [Mẹo]: lau khô\n1. [Bước 1](chuẩn bị)",
    ]:
        cleaned = clean_ai_text(raw)
        assert escape_link_syntax(unescape_link_syntax(cleaned)) == cleaned


def test_round_trip_on_random_strings():
    rng = random.Random(12)
    alphabet = "[]():\\\n >-*1a "
    for _ in range(20_000):
        plain = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 16)))
        escaped = escape_link_syntax(plain)
        assert escape_link_syntax(unescape_link_syntax(escaped)) == escaped
        if "]\\" not in plain:  # chữ gốc không tự có "]\" thì lấy lại đúng chữ gốc
            assert unescape_link_syntax(escaped) == plain


# ---------------------------------------------------------------------- AppTest


class _Provider(FakeProvider):
    def __init__(self, outline: Outline = OUTLINE) -> None:
        super().__init__()
        self.outline = outline

    def generate(self, task, *, system, prompt, schema):
        if schema is Outline:
            self.calls.append((task.name, system, prompt))
            return self.outline
        return super().generate(task, system=system, prompt=prompt, schema=schema)


@pytest.fixture
def app_env(monkeypatch):
    monkeypatch.setenv("APP_PASSWORD_HASH", hash_password(PASSWORD, iterations=1_000))
    monkeypatch.setenv("APP_TIMEZONE", "Asia/Ho_Chi_Minh")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


def _click(at: AppTest, label: str) -> None:
    next(b for b in at.button if b.label == label).click().run()
    assert not at.exception, at.exception


def _to_outline(project_root, monkeypatch, provider) -> AppTest:
    monkeypatch.setattr(ai_registry, "make_provider", lambda name, settings: provider)
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    at.text_input[0].input(PASSWORD)
    at.button[0].click().run()
    at.switch_page("views/write.py").run()
    at.text_input(key="keyword").input("so sánh inox 201 và 304").run()
    _click(at, "🔎 Phân tích từ khóa")
    _click(at, "Tiếp: tạo dàn ý →")
    return at


def test_outline_boxes_show_text_without_escape_backslash(project_root, monkeypatch, app_env):
    outline = Outline(
        title="Cổng [A][B] đẹp",
        items=[
            OutlineItem(heading="Giá [cần bổ sung: giá](tạm tính)", points=["a"], image=""),
            *OUTLINE.items[1:],
        ],
    )
    at = _to_outline(project_root, monkeypatch, _Provider(outline))
    assert at.text_input(key="outline_title").value == "Cổng [A][B] đẹp"
    uid = at.session_state["outline_ids"][0]
    assert at.text_input(key=f"h-{uid}").value == "Giá [cần bổ sung: giá](tạm tính)"


def test_outline_edits_are_escaped_again_when_approved(project_root, monkeypatch, app_env):
    provider = _Provider()
    at = _to_outline(project_root, monkeypatch, provider)
    uid = at.session_state["outline_ids"][0]
    at.text_input(key=f"h-{uid}").input("Gọi [thợ](https://evil.example)").run()
    at.text_input(key="outline_title").input("Bài [x][y]").run()
    _click(at, "✅ Duyệt dàn ý, viết toàn bài →")
    prompt = next(p for task, _, p in provider.calls if task == "write")
    assert "Gọi [thợ]\\(https://evil.example)" in prompt
    assert "[thợ](https" not in prompt
    assert "Bài [x]\\[y]" in prompt
    assert "[x][y]" not in prompt


def _to_article(project_root, monkeypatch) -> AppTest:
    at = _to_outline(project_root, monkeypatch, _Provider())
    _click(at, "✅ Duyệt dàn ý, viết toàn bài →")
    assert at.session_state["part_ids"]
    return at


def test_manual_edit_box_hides_backslash_and_save_escapes_again(project_root, monkeypatch, app_env):
    at = _to_article(project_root, monkeypatch)
    pid = at.session_state["part_ids"][-1]
    escaped = "Chênh [cần bổ sung: giá](tạm tính). [Mẹo]: lau khô"
    escaped = escape_link_syntax(escaped)
    assert "\\" in escaped
    at.session_state[f"texts-{pid}"] = [escaped]
    at.session_state[f"ver-{pid}"] = 0
    at.run()

    at.button(key=f"edit-{pid}").click().run()
    box = at.text_area(key=f"manual-{pid}")
    assert box.value == "Chênh [cần bổ sung: giá](tạm tính). [Mẹo]: lau khô"
    assert "\\" not in box.value

    # Lưu không sửa gì: chữ lưu lại y như trước (vẫn escape).
    at.button(key=f"save-{pid}").click().run()
    assert at.session_state[f"texts-{pid}"] == [escaped]

    # Người dùng tự gõ link: lưu xong không còn là link Markdown.
    at.button(key=f"edit-{pid}").click().run()
    at.text_area(key=f"manual-{pid}").input(
        "Gọi [thợ](https://evil.example)\n[a]: https://b.example"
    ).run()
    at.button(key=f"save-{pid}").click().run()
    assert not at.exception, at.exception
    saved = at.session_state[f"texts-{pid}"][0]
    assert saved == "Gọi [thợ]\\(https:/\u200b/evil.example)\n[a]\\: https:/\u200b/b.example"
    assert gfm_autolinks(saved) == []  # địa chỉ trần cũng không thành link (T-031)
    assert not any("](https" in m.value for m in at.markdown)


def test_draft_text_from_ai_is_unchanged_without_editing(project_root, monkeypatch, app_env):
    """Không bấm Sửa thì không đổi gì: chữ bài vẫn là chữ AI đã lọc."""
    at = _to_article(project_root, monkeypatch)
    pid = at.session_state["part_ids"][-1]
    assert at.session_state[f"texts-{pid}"][0] == clean_ai_text(DRAFT.sections[-1].body)


# ------------------------------------------------- T-013: khung «Cần xem lại»

EVIL = "https://evil.example"
EVIL_BODY = f"Gọi ngay [thợ]: {EVIL}\n[thợ] nhé.\n\nĐoạn sau."
EVIL_SENTENCE = f"[thợ]: {EVIL}\n[thợ] nhé."
# Địa chỉ như hiện trên trang: có ký tự ngắt rộng 0 nên không thành link (T-031)
EVIL_SHOWN = "https:/\u200b/evil.example"


class _FlagProvider(FakeProvider):
    """Bài có "[thợ]:" giữa dòng; AI chỉ ra đoạn con bắt đầu bằng "[thợ]:" (Soi Lỗi R4-1)."""

    def generate(self, task, *, system, prompt, schema):
        if schema is Draft:
            self.calls.append((task.name, system, prompt))
            return Draft(title=DRAFT.title, intro=EVIL_BODY, sections=DRAFT.sections)
        if schema is Review:
            self.calls.append((task.name, system, prompt))
            flag = Flag(section=0, sentence=EVIL_SENTENCE, reason="Nghe máy móc", replacement="")
            return Review(scores=SCORES, flags=[flag], summary="Khá ổn.")
        return super().generate(task, system=system, prompt=prompt, schema=schema)


def _to_review(project_root, monkeypatch) -> AppTest:
    at = _to_outline(project_root, monkeypatch, _FlagProvider())
    _click(at, "✅ Duyệt dàn ý, viết toàn bài →")
    return at


def _quoted(at: AppTest) -> list[str]:
    return [m.value for m in at.markdown if m.value.startswith(">")]


def test_flagged_sentence_is_quoted_line_by_line_without_link(project_root, monkeypatch, app_env):
    at = _to_review(project_root, monkeypatch)
    quoted = _quoted(at)
    assert quoted
    for value in quoted:
        assert escape_link_syntax(value) == value  # không còn "](", "][", "[nhãn]:" chưa escape
        assert all(line.startswith(">") for line in value.split("\n"))
        assert gfm_autolinks(value) == []  # địa chỉ trần cũng không thành link (T-031)
    assert f"> [thợ]\\: {EVIL_SHOWN}\n> [thợ] nhé." in quoted


def _button(at: AppTest, prefix: str):
    return next(b for b in at.button if (b.key or "").startswith(prefix))


def test_apply_and_ignore_still_use_original_sentence(project_root, monkeypatch, app_env):
    shown = f"> [thợ]\\: {EVIL_SHOWN}\n> [thợ] nhé."
    at = _to_review(project_root, monkeypatch)
    pid = at.session_state["part_ids"][0]
    assert shown in _quoted(at)
    _button(at, f"fix-{pid}-").click().run()
    assert not at.exception, at.exception
    text = at.session_state[f"texts-{pid}"][at.session_state[f"ver-{pid}"]]
    assert "[thợ] nhé." not in text and "Đoạn sau." in text
    assert shown not in _quoted(at)

    at = _to_review(project_root, monkeypatch)
    pid = at.session_state["part_ids"][0]
    _button(at, f"skip-{pid}-").click().run()
    # Câu đã được clean_flags ngắt địa chỉ như trong bài (T-031)
    assert break_autolinks(EVIL_SENTENCE) in at.session_state["ignored_flags"]
    assert shown not in _quoted(at)
