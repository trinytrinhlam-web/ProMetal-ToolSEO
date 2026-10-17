"""Soi Lỗi kiểm thử rút gọn T-044: chữ từ WordPress và câu lỗi thử mù không thành link/HTML.

Bổ sung cho ``tests/test_app_t044_safe_text.py`` (Họa Sĩ):
- Chữ khó: thực thể HTML (``&#119;ww.``, ``&commat;``), chữ toàn khổ, U+200B có sẵn, ``<https://…>``,
  dòng khai báo link tham chiếu, câu lỗi WordPress nhiều dòng.
- Đi qua client WordPress THẬT (``_plain``, ``_error_from``) với ``tests/fake_wordpress.py``, không
  chỉ thay phương thức của client.
- Dòng «Ảnh đại diện đã tải lên» (``app/views/wordpress.py:134``): giả ``st.file_uploader`` để
  AppTest đi được nhánh có ảnh.
- Thử mù: tên mô hình đi qua ``run_blind_test`` thật (chỉ giả hãng AI), và quét ngẫu nhiên có hạt
  giống cố định trên bảng chữ tên mô hình được phép.

Bộ dò ở đây giải mã Markdown MỘT LƯỢT như CommonMark (``markdown_decode`` của
``test_sanitize_autolink``): "&\\#119;" là chữ thường, không phải thực thể. Bộ dò của
``test_app_t044_safe_text`` giải mã hai lượt nên báo nhầm trường hợp đó.

Không gọi mạng thật (D3).
"""

from __future__ import annotations

import random
from dataclasses import dataclass

import pytest
import streamlit
from fake_wordpress import FakeWordPress, make_session
from streamlit.testing.v1 import AppTest
from test_sanitize_autolink import gfm_autolinks, markdown_decode

import seo_app.config as config
from seo_app.ai import AIError
from seo_app.auth import hash_password
from seo_app.content import blind_test
from seo_app.sanitize import AUTOLINK_BREAK, escape_link_syntax
from seo_app.text import escape_markdown
from seo_app.wordpress import WordPressClient

PASSWORD = "mat-khau-thu-123"
_ESCAPABLE = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
MARKDOWN_KINDS = ("markdown", "caption", "success", "error", "warning", "info", "title", "header")


def cm_problems(markdown: str) -> list[str]:
    """Chỗ có thể thành link/ảnh/HTML khi Streamlit hiện ``markdown`` (CommonMark + GFM).

    Quét một lượt, bỏ qua "\\x": "<" chưa escape (thẻ HTML, ``<scheme:…>``), "]" chưa escape
    đứng ngay trước "(" / "[" / ":" (link, ảnh, link tham chiếu, dòng khai báo), cộng địa chỉ
    trần, ``www.``, email theo remark-gfm sau khi giải mã như CommonMark.
    """
    problems: list[str] = []
    i, n = 0, len(markdown)
    while i < n:
        char = markdown[i]
        if char == "\\" and i + 1 < n and markdown[i + 1] in _ESCAPABLE:
            i += 2
            continue
        if char == "<":
            problems.append(f"'<' chưa escape ở {i}")
        elif char == "]" and markdown[i + 1 : i + 2] in ("(", "[", ":"):
            problems.append(f"']{markdown[i + 1]}' chưa escape ở {i}")
        i += 1
    problems += [f"tự thành link: {link}" for link in gfm_autolinks(markdown)]
    return problems


def shown(markdown: str) -> str:
    """Chữ người đọc thấy (giải mã một lượt như CommonMark, ký tự ngắt rộng 0 không hiện)."""
    return markdown_decode(markdown).replace(AUTOLINK_BREAK, "")


def markdown_elements(at: AppTest, kinds=MARKDOWN_KINDS) -> list:
    return [el for kind in kinds for el in getattr(at, kind)]


def assert_page_plain(at: AppTest, kinds=MARKDOWN_KINDS) -> None:
    assert not at.exception, at.exception
    for el in markdown_elements(at, kinds):
        assert cm_problems(el.value) == [], el.value
        assert not getattr(el.proto, "allow_html", False), el.value


def button(at: AppTest, label: str):
    return next(b for b in at.button if b.label == label)


# ------------------------------------------------- 1. escape_markdown với chữ khó

# (chữ sau ``_plain`` của client, chữ người đọc phải thấy; None = không so)
TRICKY = [
    ("&#119;ww.evil.example", "&#119;ww.evil.example"),
    ("w&#119;w.evil.example", "w&#119;w.evil.example"),
    ("&#x77;&#x77;&#x77;&#x2e;evil.example", "&#x77;&#x77;&#x77;&#x2e;evil.example"),
    ("https&#58;//evil.example", "https&#58;//evil.example"),
    ("https:/&#47;evil.example", "https:/&#47;evil.example"),
    ("ban&#64;evil.example", "ban&#64;evil.example"),
    # Thực thể có tên không bị escape: người đọc thấy chữ đã giải mã, nhưng vẫn không thành link.
    ("ban&commat;evil.example", "ban@evil.example"),
    ("https&colon;&sol;&sol;evil.example", "https://evil.example"),
    ("WWW&period;evil.example", "WWW.evil.example"),
    ("ｗｗｗ．evil．example ｈｔｔｐｓ：／／evil.example", None),
    ("ww​w.evil.example", "www.evil.example"),
    ("www​.evil.example", "www.evil.example"),
    ("https:/​/evil.example", "https://evil.example"),
    ("​www.evil.example ​ban@evil.example", "www.evil.example ban@evil.example"),
    ("WwW.evil.example HTTPS://EVIL.EXAMPLE", "WwW.evil.example HTTPS://EVIL.EXAMPLE"),
    ("<https://evil.example>", "<https://evil.example>"),
    ("<mailto:ban@evil.example> <javascript:alert(1)>", None),
    ("[x]: https://evil.example\n\n[x]", "[x]: https://evil.example [x]"),
    ("Dòng 1\r[nhãn]: <https://evil.example> 'tiêu đề'\r\n\r\n[nhãn][]", None),
    ("[x](<https://evil.example>) ![a](https://evil.example/a.png)", None),
    ("\\[x\\](https://evil.example)", "\\[x\\](https://evil.example)"),
    ("https:\\/\\/evil.example", "https:\\/\\/evil.example"),
    ("mailto:ban@evil.example xmpp:ban@evil.example/x", None),
    (":red[đỏ] :material/home: $x^2$ ~~gạch~~", ":red[đỏ] :material/home: $x^2$ ~~gạch~~"),
    ('<a href="https://evil.example">x</a><img src=x onerror=alert(1)>', None),
]


@pytest.mark.parametrize(("raw", "expected"), TRICKY)
def test_escape_markdown_tricky_text_is_plain(raw, expected):
    escaped = escape_markdown(raw)
    assert cm_problems(escaped) == [], escaped
    if expected is not None:
        assert shown(escaped) == expected


def test_detector_sees_tricky_raw_text():
    # Bộ dò phải bắt được phần lớn chữ khó khi CHƯA escape, nếu không test trên vô nghĩa.
    caught = [raw for raw, _ in TRICKY if cm_problems(raw)]
    assert len(caught) >= 15, caught


# ------------------------------------ 2. trang WordPress, qua client WordPress THẬT

ROOT = {"name": "ProMetal", "home": "https://example.com", "namespaces": ["wp/v2"]}
ME = {
    "name": "Lâm",
    "roles": ["editor"],
    "capabilities": {"edit_posts": True, "publish_posts": True, "upload_files": True},
}


@pytest.fixture
def fake_wp(monkeypatch) -> FakeWordPress:
    """Mọi WordPressClient trên trang dùng WordPress giả (đi qua _request/_json/_plain thật)."""
    monkeypatch.setenv("APP_PASSWORD_HASH", hash_password(PASSWORD, iterations=1_000))
    monkeypatch.setenv("APP_TIMEZONE", "Asia/Ho_Chi_Minh")
    monkeypatch.setenv("WORDPRESS_URL", "https://example.com")
    monkeypatch.setenv("WORDPRESS_USERNAME", "lam")
    monkeypatch.setenv("WORDPRESS_APP_PASSWORD", "abcd efgh")
    fake = FakeWordPress()
    original = WordPressClient.from_settings.__func__

    def from_settings(cls, settings, **kwargs):
        return original(cls, settings, session=make_session(fake), **kwargs)

    monkeypatch.setattr(WordPressClient, "from_settings", classmethod(from_settings))
    return fake


def open_wordpress_page(project_root) -> AppTest:
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    at.text_input[0].input(PASSWORD)
    at.button[0].click().run()
    at.switch_page("views/wordpress.py").run()
    assert not at.exception, at.exception
    return at


@dataclass
class FakeUpload:
    """Thay cho file người dùng chọn ở ``st.file_uploader`` (AppTest không giả lập tải file)."""

    name: str
    data: bytes

    def getvalue(self) -> bytes:
        return self.data


def fake_file_uploader(monkeypatch, upload: FakeUpload | None) -> None:
    monkeypatch.setattr(streamlit, "file_uploader", lambda *args, **kwargs: upload)


HOSTILE_SITE = (
    "&amp;#119;ww.evil.example · &amp;commat; ban&amp;commat;evil.example · "
    "&lt;a href=&quot;https://evil.example/a&quot;&gt;thẻ&lt;/a&gt; · "
    "[bấm](https://evil.example/b) · &lt;https://evil.example/c&gt; · "
    "ｗｗｗ.evil.example · ww​w.evil.example\n[r]: https://evil.example/d"
)


def test_real_client_hostile_connection_info_is_plain(project_root, fake_wp):
    fake_wp.on(
        "GET",
        "/wp-json/",
        {**ROOT, "name": HOSTILE_SITE, "home": "https://evil.example/<b>x</b>?a=[1](2)"},
    )
    fake_wp.on(
        "GET",
        "/wp-json/wp/v2/users/me",
        {**ME, "name": HOSTILE_SITE, "roles": ["<b>quản trị</b>", "www.evil.example", "[x](y)"]},
    )
    at = open_wordpress_page(project_root)
    button(at, "Kiểm tra kết nối").click().run()

    assert_page_plain(at)
    assert len(at.success) == 1
    text = "\n".join(shown(el.value) for el in markdown_elements(at))
    # Người đọc vẫn thấy chữ (đã bỏ thẻ và giải mã một lần ở _plain của client).
    assert "[bấm](https://evil.example/b)" in text
    assert "https://evil.example/<b>x</b>?a=[1](2)" in text
    assert "<b>quản trị</b>, www.evil.example, [x](y)" in text


@pytest.mark.parametrize("action", ["Kiểm tra kết nối", "Tải chuyên mục và thẻ", "Tạo bài nháp"])
def test_real_client_multiline_wordpress_error_is_plain(project_root, fake_wp, action):
    message = (
        "Dòng một\n\n[x]: https://evil.example/a\n\n[x] [y][x]\r\n"
        "&lt;https://evil.example/b&gt; <a href='https://evil.example/c'>c</a>\r"
        "www.evil.example ban@evil.example &amp;#119;ww.evil.example"
    )
    error = (400, {"code": "rest_invalid_param", "message": message}, {})
    for method, path in (
        ("GET", "/wp-json/"),
        ("GET", "/wp-json/wp/v2/categories"),
        ("POST", "/wp-json/wp/v2/posts"),
    ):
        fake_wp.on(method, path, error)
    at = open_wordpress_page(project_root)
    if action == "Tạo bài nháp":
        next(t for t in at.text_input if t.label == "Tiêu đề").input("Bài thử")
    button(at, action).click().run()

    assert len(at.error) == 1
    assert_page_plain(at)
    seen = shown(at.error[0].value)
    assert seen.startswith("WordPress báo lỗi (mã 400). (WordPress: Dòng một [x]: https://")
    assert "\n" not in seen and "\r" not in seen


SOURCE_URLS = (
    "https://evil.example/wp-content/uploads/anh.jpg",
    "www.evil.example/anh.jpg",
    "[anh](https://evil.example/a.jpg)",
    "<https://evil.example/a.jpg>",
    '<img src=x onerror="alert(1)">',
    "ban@evil.example",
)


@pytest.mark.parametrize("source_url", SOURCE_URLS)
def test_uploaded_image_url_line_is_plain(project_root, fake_wp, monkeypatch, source_url):
    # wordpress.py:134: nhánh có ảnh, địa chỉ ảnh do WordPress trả về.
    media = {"id": 9, "source_url": source_url, "alt_text": "cửa"}
    fake_wp.on("POST", "/wp-json/wp/v2/media", (201, media, {}))
    fake_wp.on("POST", "/wp-json/wp/v2/media/9", media)
    fake_wp.on(
        "POST",
        "/wp-json/wp/v2/posts",
        (201, {"id": 42, "status": "draft", "title": {"raw": "Bài [x](https://evil.example)"}}, {}),
    )
    fake_file_uploader(monkeypatch, FakeUpload("anh cua.jpg", b"\xff\xd8\xff anh gia"))
    at = open_wordpress_page(project_root)
    next(t for t in at.text_input if t.label == "Tiêu đề").input("Bài thử")
    next(t for t in at.text_input if t.label.startswith("Mô tả ảnh")).input("cửa")
    button(at, "Tạo bài nháp").click().run()

    assert_page_plain(at)
    lines = [el.value for el in at.markdown if "Ảnh đại diện đã tải lên" in el.value]
    assert len(lines) == 1
    assert shown(lines[0]) == f"Ảnh đại diện đã tải lên: {source_url}"
    assert shown(at.success[0].value) == "Đã tạo bài nháp #42: **Bài [x](https://evil.example)**"
    posted = [r for r in fake_wp.requests if r.url.endswith("/wp/v2/posts")]
    assert len(posted) == 1 and b'"featured_media": 9' in posted[0].body
    assert b'"status": "draft"' in posted[0].body


@pytest.mark.parametrize(
    "upload",
    [
        FakeUpload("www.evil.example.exe", b"MZ"),
        FakeUpload("[x](https:⁄⁄evil.example)ban@evil.example.png", b""),
    ],
    ids=["sai-duoi", "rong"],
)
def test_upload_error_with_hostile_filename_is_plain(project_root, fake_wp, monkeypatch, upload):
    # Câu lỗi chép lại tên file người dùng chọn: cũng không thành link.
    fake_file_uploader(monkeypatch, upload)
    at = open_wordpress_page(project_root)
    next(t for t in at.text_input if t.label == "Tiêu đề").input("Bài thử")
    button(at, "Tạo bài nháp").click().run()

    assert len(at.error) == 1
    assert_page_plain(at)
    assert f"File '{upload.name}'" in shown(at.error[0].value)
    assert not [r for r in fake_wp.requests if "/wp/v2/" in r.url]


@pytest.mark.xfail(
    strict=True,
    reason="SL-T044-1: 'home' không phải chuỗi thì escape_markdown(info.site_url) làm trang hỏng",
)
@pytest.mark.parametrize("home", [123, ["https://evil.example"]], ids=["so", "danh-sach"])
def test_non_string_site_url_does_not_crash_page(project_root, fake_wp, home):
    fake_wp.on("GET", "/wp-json/", {**ROOT, "home": home})
    fake_wp.on("GET", "/wp-json/wp/v2/users/me", ME)
    at = open_wordpress_page(project_root)
    button(at, "Kiểm tra kết nối").click().run()
    assert not at.exception, at.exception
    assert_page_plain(at)


@pytest.mark.xfail(
    strict=True,
    reason="SL-T044-2: 'source_url' null thì escape_markdown(media.source_url) làm trang hỏng",
)
def test_null_source_url_does_not_crash_page(project_root, fake_wp, monkeypatch):
    media = {"id": 9, "source_url": None}
    fake_wp.on("POST", "/wp-json/wp/v2/media", (201, media, {}))
    post = {"id": 42, "status": "draft", "title": "A"}
    fake_wp.on("POST", "/wp-json/wp/v2/posts", (201, post, {}))
    fake_file_uploader(monkeypatch, FakeUpload("anh.jpg", b"\xff\xd8\xff"))
    at = open_wordpress_page(project_root)
    next(t for t in at.text_input if t.label == "Tiêu đề").input("Bài thử")
    button(at, "Tạo bài nháp").click().run()
    assert not at.exception, at.exception
    assert len(at.success) == 1


# --------------------------------------------------------------- 3. thử mù

# Bảng chữ tên mô hình được phép (blind_test._MODEL_CHARS) và các mảnh dễ thành link.
_ALPHABET = "abcxyzWw019._:/@-"
_PIECES = ("https://", "http://", "www.", "WWW.", "@", "mailto:", "xmpp:", ".com", "evil", "//")


def test_model_name_alphabet_matches_blind_test():
    # Nếu Thợ Máy nới bảng chữ (thêm "<", "[", "(", "\\"…) thì quét dưới đây phải xét lại.
    assert blind_test._MODEL_CHARS.pattern == r"[A-Za-z0-9._:/@-]+"


def test_blind_error_escape_fuzz_restricted_alphabet():
    rng = random.Random(44)
    bad = []
    for _ in range(3000):
        model = "".join(
            rng.choice(_PIECES) if rng.random() < 0.4 else rng.choice(_ALPHABET)
            for _ in range(rng.randint(1, 12))
        )
        assert blind_test._MODEL_CHARS.fullmatch(model)
        line = escape_link_syntax(f"Bài B (OpenAI · {model}): Không có mô hình «{model}».")
        if cm_problems(line) or shown(line) != line.replace(AUTOLINK_BREAK, ""):
            bad.append(model)
    assert bad == []


@pytest.mark.parametrize("model", ["_abc1_", "__abc1__", ":smile:", ":material/home:", "a_b_1"])
def test_blind_leftover_formatting_is_not_link_or_html(model):
    # Định dạng còn sót (nghiêng, đậm, biểu tượng) chấp nhận được: không link, không HTML.
    raw = f"Bài B (OpenAI · {model}): Không có mô hình «{model}»."
    line = escape_link_syntax(raw)
    assert cm_problems(line) == []
    assert line == raw  # không cần escape gì: tên không có ký tự mở link/thẻ nào
    assert not set(model) & set("<>[]()&\\")


@pytest.fixture
def blind_env(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_PASSWORD_HASH", hash_password(PASSWORD, iterations=1_000))
    monkeypatch.setattr(config, "DEFAULT_ENV_FILE", tmp_path / ".env")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "khoa-gia-anthropic")
    monkeypatch.setenv("OPENAI_API_KEY", "khoa-gia-openai")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)


class MissingModelProvider:
    """Hãng AI giả: mô hình nào cũng "không có", câu lỗi chép lại tên (như gemini_provider)."""

    def generate(self, task, **kwargs):
        raise AIError(f"Không có mô hình «{task.model}». Kiểm tra lại tên trong config/ai.toml.")


@pytest.mark.usefixtures("blind_env")
@pytest.mark.parametrize(
    "model", ["www.evil.example", "https://evil.example/m1", "ban@evil.example", "mailto:a@b.co"]
)
def test_blind_real_run_reveal_errors_are_plain(project_root, monkeypatch, model):
    monkeypatch.setattr(blind_test, "make_provider", lambda name, settings: MissingModelProvider())
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    at.text_input[0].input(PASSWORD)
    at.button[0].click().run()
    at.switch_page("views/settings.py").run()
    at.text_input(key="blind-keyword").input("cửa sắt")
    at.text_input(key="blind-cand-0-model").input("claude-thu-1")
    at.text_input(key="blind-cand-1-model").input(model)
    at.run()
    at.button(key="blind-run").click().run()
    at.button(key="blind-reveal").click().run()

    assert not at.exception, at.exception
    errors = [e.value for e in at.error if e.value.startswith("Bài ")]
    assert len(errors) == 2
    for value in errors:
        assert cm_problems(value) == [], value
    assert any(f"· {model}): Không có mô hình «{model}»." in shown(v) for v in errors)
    assert_page_plain(at, ("error", "warning"))
