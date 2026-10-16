"""Soi Lỗi kiểm T-031: địa chỉ trần, "www." và email trong chữ AI không thành link bấm được.

Bộ đối chiếu ở đây viết riêng, không dùng ``gfm_autolinks`` của Thợ Máy:
- Hai biểu thức nhận link tự động được ĐỌC TỪ CHÍNH FILE JS của Streamlit đang cài
  (``StreamlitMarkdown*.js``, remark-gfm / mdast-util-gfm-autolink-literal) rồi đổi sang Python.
  Streamlit nâng phiên bản mà đổi cách nhận link thì ``test_streamlit_autolink_rules_unchanged``
  đỏ, nhắc kiểm lại T-031.
- Giải mã như CommonMark ("\\x" với x là dấu câu ASCII, "&…;" hợp lệ) bằng một biểu thức thay thế,
  cách viết khác với ``seo_app.sanitize._decoded_view``.
- Bộ đối chiếu bỏ điều kiện "ký tự đứng trước" của remark-gfm nên bắt RỘNG hơn bản thật.

Ngoài pytest, Soi Lỗi đã chạy bộ hiển thị thật (react-markdown 9.1.0 + remark-gfm 4.0.1, thêm
rehype-raw cho chỗ ``unsafe_allow_html``) trên 738 ca viết tay và 17 708 ca ngẫu nhiên: 0 link trên
mọi đường thật (xem ``docs/team/reports/T-031-soi-loi.md``). Test không gọi mạng.
"""

from __future__ import annotations

import html
import html.entities
import random
import re
from pathlib import Path

import pytest
import streamlit
from streamlit.testing.v1 import AppTest
from timing import assert_scales_linearly

from seo_app import ui
from seo_app.ai import registry as ai_registry
from seo_app.auth import hash_password
from seo_app.content.blind_test import _mask_names
from seo_app.content.models import Competitor, Draft, Flag, Research, Review, Section
from seo_app.content.workflow import apply_flag, clean_ai_line, clean_flags, clean_research
from seo_app.sanitize import (
    AUTOLINK_BREAK,
    break_autolinks,
    clean_ai_text,
    escape_link_syntax,
    unbreak_autolinks,
    unescape_link_syntax,
)
from seo_app.text import markdown_link
from seo_app.wordpress import ConnectionInfo, WordPressClient

ZW = AUTOLINK_BREAK
PASSWORD = "mat-khau-thu-123"

# ------------------------------------------------------------- bộ đối chiếu độc lập

# Nguyên văn hai biểu thức trong file JS của Streamlit 1.65 (đã đối chiếu với
# mdast-util-gfm-autolink-literal 2.0.1).
JS_URL = r"(https?:\/\/|www(?=\.))([-.\w]+)([^ \t\r\n]*)/gi"
JS_EMAIL = r"([-.\w+]+)@([-\w]+(?:\.[-\w]+)+)/gu"
# Đổi sang Python: cờ "i" của JS (không "u") chỉ gập hoa thường ASCII; "\w" của JS luôn là ASCII.
URL_RE = re.compile(r"(https?://|www(?=\.))([-.\w]+)", re.IGNORECASE | re.ASCII)
EMAIL_RE = re.compile(r"([-.\w+]+)@([-\w]+(?:\.[-\w]+)+)", re.ASCII)
# micromark còn nhận "mailto:"/"xmpp:" + email; email đã bị bắt ở EMAIL_RE nên không cần thêm.

_DECODE = re.compile(
    r"\\([!-/:-@\[-`{-~])"  # "\x" với x là dấu câu ASCII
    r"|&(#[0-9]{1,7};|#[xX][0-9a-fA-F]{1,6};|[A-Za-z][A-Za-z0-9]{0,31};)"
)


def _decode_one(m: re.Match[str]) -> str:
    if m.group(1) is not None:
        return m.group(1)
    ref = m.group(2)
    if ref.startswith("#"):
        digits = ref[1:-1]
        code = int(digits[1:], 16) if digits[:1] in "xX" else int(digits)
        if code == 0 or code > 0x10FFFF or 0xD800 <= code <= 0xDFFF:
            return "\ufffd"
        return chr(code)
    return html.entities.html5.get(ref, "&" + ref)


def decode(text: str) -> str:
    """Chữ mà bộ đọc Markdown thấy sau khi giải mã (một lượt, như CommonMark)."""
    return _DECODE.sub(_decode_one, text)


def autolinks(markdown: str, *, raw_html: bool = False) -> list[str]:
    """Các đoạn mà remark-gfm sẽ biến thành link. ``raw_html``: chuỗi đã escape HTML (``&amp;``)."""
    text = decode(markdown)
    if raw_html:  # rehype-raw: "&amp;" đã được Markdown giải mã thành "&" ở bước trên
        text = re.sub(r"<[^>]*>", "", text)
    return [m.group(0) for m in URL_RE.finditer(text)] + [
        m.group(0) for m in EMAIL_RE.finditer(text)
    ]


def seen(markdown: str) -> str:
    """Chữ người đọc thấy (ký tự ngắt rộng 0 không hiện)."""
    return decode(markdown).replace(ZW, "")


# --------------------------------------------------------------------- các đường hiện chữ


def _quote(text: str) -> str:
    """Như ``quote_ai_text`` trong app/views/write.py (file đó là trang, không import được)."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return escape_link_syntax("\n".join(f"> {line}" if line else ">" for line in lines))


def _edit_box(text: str) -> str:
    """Bài AI → ô «Sửa trực tiếp» → bấm Lưu không đổi gì."""
    return escape_link_syntax(unescape_link_syntax(clean_ai_text(text)))


PATHS = {
    "clean_ai_text": (clean_ai_text, False),
    "clean_ai_line": (clean_ai_line, False),
    "ô sửa + Lưu": (_edit_box, False),
    "trích câu": (lambda t: _quote(clean_ai_text(t)), False),
    "bài (highlight)": (lambda t: ui.highlight(clean_ai_text(t), [clean_ai_text(t)[1:6]]), True),
    "tiêu đề H2": (lambda t: "## " + html.escape(clean_ai_line(t)), True),
    "tên đối thủ (url hỏng)": (lambda t: markdown_link(t, ""), False),
    "nhãn :gray[]": (lambda t: f":gray[{clean_ai_line(t)}]", False),
    "thử mù (che tên)": (lambda t: _mask_names(clean_ai_text(t), ["gpt-5.1", "claude-x-1"]), False),
}

ADDRESSES = [
    # Yêu cầu 3 của phiếu
    "https://evil.example/a?b=1",
    "http://evil.example",
    "HTTPS://EVIL.EXAMPLE",
    "hTtP://evil.example",
    "www.evil.example",
    "WWW.EVIL.EXAMPLE",
    "wWw.evil.example",
    "a@evil.example",
    "A.B+c-d_e@evil.co.uk",
    "a-@evil.example a_@evil.example a+@evil.example a.@evil.example",
    "mailto:a@evil.example",
    "xmpp:a@evil.example/x",
    "Xem https://evil.example.",
    "(https://evil.example)",
    "Xem (www.evil.example), rồi!",
    "Email: a@evil.example;",
    '"https://evil.example"',
    "https://evil.example/đường-dẫn",
    "https://xn--cxa-ssa.vn",
    "www.cửasắt.vn",
    "a@xn--c-kfa.vn",
    # escape "\"
    "www\\.evil.example",
    "https\\://evil.example",
    "https:\\/\\/evil.example",
    "a\\@evil.example",
    "\\\\https://evil.example",
    # mã HTML
    "a&#64;evil.example",
    "a&#x40;evil.example",
    "a&#X40;evil.example",
    "a&commat;evil.example",
    "www&#46;evil.example",
    "www&period;evil.example",
    "https&#58;//evil.example",
    "https:&#47;&#47;evil.example",
    "https:&sol;&sol;evil.example",
    "&#119;ww.evil.example",
    "&#x77;&#x77;&#x77;.evil.example",
    "a&#0000064;evil.example",
    "&amp;www.evil.example",
    "&www.evil.example",
    # ký tự vô hình có sẵn, chữ toàn khổ
    "https:/\u200b/evil.example",
    "www\u200b.evil.example",
    "\u200bhttps://evil.example",
    "https://\u200bevil.example",
    "https:/\u2060/evil.example",
    "ｗｗｗ．evil.example https：／／evil.example a＠evil.example",
    # trong cú pháp Markdown
    "**https://evil.example**",
    "_www.evil.example_",
    "- www.evil.example",
    "> a@evil.example",
    "# www.evil.example",
    "| https://evil.example | x |\n|---|---|\n| www.a.vn | b |",
    "<span>https:/</span>/evil.example",
    "www<b></b>.evil.example",
    "a<i></i>@evil.example",
    "https://evil.example\nwww.evil.example\na@evil.example",
    # tên mô hình nằm giữa địa chỉ (thử mù che tên SAU clean_ai_text)
    "https:/gpt-5.1/evil.example",
    "www_gpt-5.1_.evil.example",
    "claude-x-1@evil.example",
    "a@claude.evil.example",
]


@pytest.mark.parametrize("path", PATHS)
@pytest.mark.parametrize("text", ADDRESSES)
def test_no_autolink_on_any_display_path(text, path):
    fn, raw_html = PATHS[path]
    assert autolinks(fn(text), raw_html=raw_html) == []


def test_oracle_catches_unprotected_text():
    """Bộ đối chiếu không câm: chữ chưa lọc thì bắt được link."""
    for text in ["https://a.vn", "WWW.a.vn", "a@b.vn", "www\\.a.vn", "a&#64;b.vn", "https:&#47;/a"]:
        assert autolinks(text), text


@pytest.mark.parametrize(
    "text",
    [
        "Xem https://evil.example/a nhé",
        "Gọi www.cuasat.vn hoặc lienhe@cuasat.vn",
        "(https://xn--cxa-ssa.vn).",
        "www.cửasắt.vn",
        "HTTPS://A.VN và WWW.B.VN",
    ],
)
def test_reader_still_sees_the_whole_address(text):
    """Người đọc vẫn thấy nguyên địa chỉ: chỉ thêm ký tự rộng 0."""
    assert seen(clean_ai_text(text)) == text
    assert seen(clean_ai_line(text)) == text


@pytest.mark.parametrize(
    "text",
    [
        "TP.HCM",
        "v.v.",
        "1.500.000 đồng",
        "3,14 hay 3.14",
        "8:30/17:30",
        "Ngày 15/10/2026, 10:00:00",
        "Inox 304. Cổng 2.5m.",
        "a/b/c",
        "http: không phải link",
        "www",
        "w.w.w.",
        "ww.w",
        "Dr.www",
        "@suachuacuasat",
        "a @ b",
        "giá: 1.2tr/m²",
        "Hotline 0905.123.456",
    ],
)
def test_ordinary_vietnamese_text_gets_no_break(text):
    assert ZW not in clean_ai_text(text)
    assert ZW not in markdown_link(text, "")


# --------------------------------------------------------------------- ô sửa, round-trip


@pytest.mark.parametrize("text", ADDRESSES)
def test_edit_box_shows_no_zero_width_and_round_trips(text):
    shown = clean_ai_text(text)
    box = unescape_link_syntax(shown)
    if ZW not in text:  # ký tự rộng 0 chỉ có khi AI tự viết ra
        assert ZW not in box
    assert escape_link_syntax(box) == shown
    assert unbreak_autolinks(break_autolinks(box)) == box


def test_round_trip_on_random_strings():
    rng = random.Random(31)
    pieces = [
        "https://", "http:/", "/", "www.", "WWW", "w", "a@", "@", "\\", "&#64;", "&#47;",
        "&#46;", "&#58;", "[a]", "]", "[", "(", ")", ":", " ", "\n", "> ", "- ", "`", "x",
        ".", "&", "đ", "<b>", "</b>", "mailto:", "#", ZW,
    ]  # fmt: skip
    for _ in range(6000):
        text = "".join(rng.choice(pieces) for _ in range(rng.randint(1, 14)))
        for shown in (escape_link_syntax(text), clean_ai_text(text)):
            box = unescape_link_syntax(shown)
            assert escape_link_syntax(box) == shown, (text, shown, box)
            if ZW not in text:
                assert ZW not in box, (text, shown)
        assert escape_link_syntax(escape_link_syntax(text)) == escape_link_syntax(text)


# ------------------------------------------------------- gợi ý văn phong và Áp dụng


@pytest.mark.parametrize("copied_with_break", [False, True])
def test_flag_with_address_is_kept_and_applied_without_link(copied_with_break):
    body = clean_ai_text(
        "Mở bài. Liên hệ https://cuasat.example, www.cuasat.example hoặc a@cuasat.example. Hết."
    )
    sentence = "Liên hệ https://cuasat.example, www.cuasat.example hoặc a@cuasat.example."
    if copied_with_break:
        sentence = break_autolinks(sentence)
    flags = clean_flags(
        [Section(heading="Mở bài", body=body)],
        [Flag(section=0, sentence=sentence, reason="r", replacement="Gọi www.moi.example nhé.")],
    )
    assert len(flags) == 1 and flags[0].sentence in body
    fixed = apply_flag(body, flags[0].sentence, flags[0].replacement)
    assert seen(fixed) == "Mở bài. Gọi www.moi.example nhé. Hết."
    assert autolinks(fixed) == []
    removed = apply_flag(body, flags[0].sentence, "")
    assert seen(removed) == "Mở bài. Hết."


@pytest.mark.parametrize(
    ("before", "sentence", "replacement"),
    [
        ("Xem www", " cũ.", ".evil.example nhé"),
        ("Gửi a", " cũ", "@evil.example"),
        ("Mở https:", " x", "//evil.example"),
        ("Mở https:/", " x", "/evil.example"),
        ("Gửi a&#", " x", "64;evil.example"),
        ("Gửi a\\", " x", "@evil.example"),
    ],
)
def test_apply_flag_seam_cannot_build_an_address(before, sentence, replacement):
    body = escape_link_syntax(before + sentence)
    assert autolinks(apply_flag(body, sentence, replacement)) == []


# ---------------------------------------------------------------- tốc độ: tuyến tính

_UNITS = [
    "www", "www.", "a@", ":/", "https:/", "&#64;", "&#119;", "&", "&#", "&#1", "&a", "\\",
    "\\.", "w" + ZW, "a" + ZW + "@", ":/" + ZW + "/",
]  # fmt: skip


@pytest.mark.parametrize("unit", _UNITS)
def test_break_and_unbreak_scale_linearly(unit):
    count = 20000
    assert_scales_linearly(break_autolinks, lambda k: unit * (count * k // 4), label=unit)
    assert_scales_linearly(unbreak_autolinks, lambda k: unit * (count * k // 4), label=unit)
    assert_scales_linearly(escape_link_syntax, lambda k: unit * (count * k // 4), label=unit)


def test_long_entity_like_runs_are_linear():
    assert_scales_linearly(break_autolinks, lambda k: "&#" + "1" * (40000 * k // 4) + "@")
    assert_scales_linearly(break_autolinks, lambda k: "&" + "a" * (40000 * k // 4) + ";@")
    assert_scales_linearly(break_autolinks, lambda k: "w" * (40000 * k // 4) + ".")


# ------------------------------------------- canary: Streamlit đổi cách nhận link tự động


def test_streamlit_autolink_rules_unchanged():
    """Streamlit nâng phiên bản mà đổi biểu thức nhận link tự động thì phải kiểm lại T-031."""
    js_dir = Path(streamlit.__file__).parent / "static" / "static" / "js"
    bundles = list(js_dir.glob("StreamlitMarkdown*.js"))
    assert bundles, "Không thấy file StreamlitMarkdown*.js: Streamlit đổi cấu trúc, kiểm lại T-031"
    source = "".join(p.read_text(encoding="utf-8") for p in bundles)
    assert JS_URL in source
    assert JS_EMAIL in source


# ------------------------------------------------------------------------ AppTest


@pytest.fixture
def app_env(monkeypatch):
    monkeypatch.setenv("APP_PASSWORD_HASH", hash_password(PASSWORD, iterations=1_000))
    monkeypatch.setenv("APP_TIMEZONE", "Asia/Ho_Chi_Minh")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


EVIL_INTRO = (
    "Gọi ngay https://evil.example hoặc www.evil.example, email a@evil.example.\n\n"
    "Mã: a&#64;evil.example, www\\.evil.example."
)
EVIL_SENTENCE = "Gọi ngay https://evil.example hoặc www.evil.example, email a@evil.example."
EVIL_SENTENCE_2 = "Mã: a&#64;evil.example, www\\.evil.example."


def _provider():
    from fake_ai import DRAFT, SCORES, FakeProvider

    class _Provider(FakeProvider):
        def generate(self, task, *, system, prompt, schema):
            if schema is Research:
                self.calls.append((task.name, system, prompt))
                return Research(
                    intent=["Muốn xem www.evil.example"],
                    article_type="So sánh https://evil.example",
                    competitors=[
                        Competitor(
                            title="Bài ở https\\://evil.example/x và a@evil.example",
                            url="javascript:alert(1)",
                            covers="Có www.evil.example",
                            missing="Thiếu a@evil.example",
                        )
                    ],
                    new_angles=["Thêm https://evil.example"],
                    questions=["Gửi a@evil.example được không?"],
                )
            if schema is Draft:
                self.calls.append((task.name, system, prompt))
                return Draft(
                    title="Cổng www.evil.example", intro=EVIL_INTRO, sections=DRAFT.sections
                )
            if schema is Review:
                # Lượt 1: câu có địa chỉ, có câu thay thế (app tự sửa). Lượt sau: câu có mã HTML
                # và "\\.", không có câu thay thế (hiện cho người dùng Áp dụng).
                self.calls.append((task.name, system, prompt))
                self.reviews += 1
                if self.reviews == 1:
                    flag = Flag(section=0, sentence=EVIL_SENTENCE, reason="Xem a@evil.example",
                                replacement="Gọi thợ qua www.evil.example.")  # fmt: skip
                else:
                    flag = Flag(section=0, sentence=EVIL_SENTENCE_2, reason="Xem a@evil.example",
                                replacement="")  # fmt: skip
                return Review(scores=SCORES, flags=[flag], summary="Ghé https://evil.example")
            return super().generate(task, system=system, prompt=prompt, schema=schema)

    return _Provider()


def _click(at: AppTest, label: str) -> None:
    next(b for b in at.button if b.label == label).click().run()
    assert not at.exception, at.exception


def _no_link_anywhere(at: AppTest) -> None:
    for m in at.markdown:
        raw = bool(getattr(m.proto, "allow_html", False))
        assert autolinks(m.value, raw_html=raw) == [], m.value
    for c in at.caption:
        assert autolinks(c.value) == [], c.value


def _to_write(project_root, monkeypatch) -> AppTest:
    monkeypatch.setattr(ai_registry, "make_provider", lambda name, settings: _provider())
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    at.text_input[0].input(PASSWORD)
    at.button[0].click().run()
    at.switch_page("views/write.py").run()
    at.text_input(key="keyword").input("cổng inox").run()
    _click(at, "🔎 Phân tích từ khóa")
    _no_link_anywhere(at)  # bước Chuẩn bị: kết quả nghiên cứu, tên bài đối thủ
    _click(at, "Tiếp: tạo dàn ý →")
    _click(at, "✅ Duyệt dàn ý, viết toàn bài →")
    return at


def test_compose_page_shows_no_link_and_flag_applies(project_root, monkeypatch, app_env):
    at = _to_write(project_root, monkeypatch)
    _no_link_anywhere(at)
    pid = at.session_state["part_ids"][0]
    # Lượt rà soát 1: app tự áp câu thay thế cho câu có địa chỉ (AI chép câu không có ký tự ngắt)
    assert at.session_state["auto_fixed"] == 1
    body = at.session_state[f"texts-{pid}"][at.session_state[f"ver-{pid}"]]
    assert "Gọi thợ qua www.evil.example." in seen(body) and "Gọi ngay" not in body
    assert autolinks(body) == []
    # Lượt 2: gợi ý cho câu có mã HTML và "\\." vẫn hiện, Áp dụng (bỏ câu) được
    quoted = [m.value for m in at.markdown if m.value.startswith(">")]
    assert any("evil.example" in q for q in quoted)
    next(b for b in at.button if (b.key or "").startswith(f"fix-{pid}-")).click().run()
    assert not at.exception, at.exception
    body = at.session_state[f"texts-{pid}"][at.session_state[f"ver-{pid}"]]
    assert "Mã:" not in body and "Gọi thợ qua" in body
    assert autolinks(body) == []
    _no_link_anywhere(at)


def test_edit_box_rewrite_and_undo_keep_text(project_root, monkeypatch, app_env):
    at = _to_write(project_root, monkeypatch)
    pid = at.session_state["part_ids"][0]
    original = at.session_state[f"texts-{pid}"][0]
    at.button(key=f"edit-{pid}").click().run()
    box = at.text_area(key=f"manual-{pid}").value
    assert ZW not in box and "\\" not in box.replace("www\\.", "")  # "\." do AI tự viết
    assert "qua www.evil.example." in box and "a&#64;evil.example" in box
    at.button(key=f"save-{pid}").click().run()
    assert at.session_state[f"texts-{pid}"][0] == original  # Lưu không đổi gì
    # Viết lại phần này rồi quay về bản trước
    at.button(key=f"do-rw-{pid}").click().run()
    assert not at.exception, at.exception
    assert at.session_state[f"ver-{pid}"] == 1
    at.button(key=f"undo-{pid}").click().run()
    assert at.session_state[f"ver-{pid}"] == 0
    assert at.session_state[f"texts-{pid}"][0] == original
    _no_link_anywhere(at)


def test_competitor_title_from_research_is_not_a_link():
    research = clean_research(
        Research(
            intent=[],
            article_type="",
            competitors=[
                Competitor(title="Xem https\\://evil.example", url="", covers="", missing="")
            ],
            new_angles=[],
            questions=[],
        )
    )
    c = research.competitors[0]
    assert autolinks(markdown_link(c.title, c.url)) == []


# --------------------------------------------- chữ ngoài AI hiện trên trang WordPress


@pytest.mark.xfail(
    strict=True,
    reason="SL-T031-1: tên website / tên tài khoản từ WordPress hiện bằng Markdown không escape",
)
def test_wordpress_site_name_is_not_a_link(project_root, monkeypatch):
    monkeypatch.setenv("APP_PASSWORD_HASH", hash_password(PASSWORD, iterations=1_000))
    monkeypatch.setenv("APP_TIMEZONE", "Asia/Ho_Chi_Minh")
    monkeypatch.setenv("WORDPRESS_URL", "https://example.com")
    monkeypatch.setenv("WORDPRESS_USERNAME", "lam")
    monkeypatch.setenv("WORDPRESS_APP_PASSWORD", "abcd efgh")
    info = ConnectionInfo(
        "Ghé www.evil.example",
        "https://example.com",
        "a@evil.example",
        ("editor",),
        True,
        True,
        True,
    )
    monkeypatch.setattr(WordPressClient, "check_connection", lambda self: info)
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    at.text_input[0].input(PASSWORD)
    at.button[0].click().run()
    at.switch_page("views/wordpress.py").run()
    next(b for b in at.button if b.label == "Kiểm tra kết nối").click().run()
    shown = [at.success[0].value, *(m.value for m in at.markdown)]
    found = [link for text in shown for link in autolinks(text) if "evil" in link]
    assert found == []
