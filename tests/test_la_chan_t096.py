"""Lá Chắn T-096: test chứng minh lỗi (``xfail(strict=True)`` tới khi sửa), test canh hướng sửa.

- LC-T096-1 (Trung bình): tiêu đề con Markdown có dãy dấu cách, tab dài ở giữa làm bộ chuyển
  (``markdown_to_html``, cả ``build_article`` mỗi lần hiện màn hình xác nhận) chạy **bậc hai**:
  biểu thức bỏ dấu "#" cuối tiêu đề (``_CLOSING_HASHES``, ``seo_app/publish/markdown.py:60``)
  dùng với ``sub`` thử lại từ mọi vị trí trong dãy khoảng trắng, mỗi lần đọc tới hết dãy.
- LC-T096-2 (Thấp): thẻ ảnh (``ImageTags``: ảnh thật/AI, mã công trình, hạng mục, khu vực) quyết
  định tên file công khai (``minh-hoa-ai-…``, mã công trình, khu vực) và tiêu đề Media «[AI] …»
  (``client._plan_draft_images``, ``_describe_draft_media``), nhưng ``content_parts`` không so thẻ
  và mã xác nhận không có thẻ: thẻ đổi sau khi xác nhận thì vẫn gửi được.
- LC-T096-3 (Thấp): mã ứng dụng có ký tự điều khiển hướng chữ viết trần (kiểu «Trojan Source»,
  CVE-2021-42574; bandit B613): ``seo_app/publish/markdown.py:57`` viết trần U+202A, U+202E,
  U+2066, U+2069 trong biểu thức ``_DROPPED``. Trình soạn thảo, trang so sánh có thể hiện dòng đó
  đảo thứ tự, khác điều chạy thật. Viết bằng mã ``\\u202a-\\u202e`` như các file khác.
- LC-T096-4 (Thấp): lớp chặn nhúng «chặt hơn» (``review.embedded_urls``: khối chỉ có một địa chỉ,
  để trình soạn khối không nhúng tiếp) chỉ bỏ khoảng trắng ASCII ở hai đầu. Trình soạn khối
  (Gutenberg, khối Embed, biến đổi ``raw`` khi «Chuyển thành khối») dùng ``textContent.trim()``
  của JavaScript, bỏ cả ``&nbsp;``, U+FEFF, khoảng trắng Unicode: ``<p>&nbsp;https://…</p>`` thành
  khối nhúng, mà bộ dựng không Chặn.

LC-T096-1 → -4 đã sửa ở lượt 3 (Thợ Máy gỡ dấu ``xfail``, không đổi điều kiện kiểm).

- LC-T096-5 (Thấp, xem lại lượt 3): lớp chặn nhúng chặt hơn vẫn chỉ Chặn đoạn mà **cả** chữ là một
  địa chỉ. Điều kiện của Gutenberg (``isMatch``: ``isURL`` là ``new URL(chữ)`` không lỗi, chữ bắt
  đầu bằng ``https://``, chỉ một ``https://``, tên file cuối không phải đuôi tệp trừ ``html``,
  ``php``) nhận cả đoạn «địa chỉ + chữ phía sau», vì ``new URL`` nhận dấu cách trong đường dẫn,
  tham số: ``<p>https://evil.example/trang nội dung</p>`` thành khối nhúng khi «Chuyển thành khối».

LC-T096-5 đã sửa ở lượt 4 (``review._block_editor_embeds``; Thợ Máy gỡ dấu ``xfail``).

- LC-T096-6 (Thấp, xem lại lượt 4): ``_block_editor_embeds`` tách tên máy đơn giản hơn bộ phân tích
  URL của trình duyệt (WHATWG, ``new URL``): WHATWG bỏ tab, xuống dòng ở mọi chỗ, coi «\\» như «/»,
  bỏ qua «/» thừa sau ``https://``, tên máy là phần sau «@». Đoạn mở đầu bằng các dạng đó rồi tới
  chữ vẫn thành khối nhúng khi «Chuyển thành khối» mà bộ dựng không Chặn.

Không gọi mạng: danh sách bài dựng tay.
"""

import hashlib
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from timing import assert_scales_linearly

from seo_app.images.process import WebImage
from seo_app.images.tags import ImageTags
from seo_app.publish.markdown import markdown_to_html
from seo_app.publish.render import ArticleImage, ArticlePart, BuildError, build_article
from seo_app.storage.site_index import SiteIndex
from seo_app.wordpress import PublishedItem
from seo_app.wordpress.client import DraftImage

SITE = "https://suachuacuasat.com"
INDEX = SiteIndex(
    site=SITE,
    fetched_at=datetime(2026, 10, 28, 9, 0, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh")),
    items=(
        PublishedItem(
            id=10, type="page", slug="sua-cua-keo", link=f"{SITE}/sua-cua-keo/", title="Sửa cửa"
        ),
    ),
)

# ------------------------------------------------------------------ LC-T096-1


@pytest.mark.parametrize(
    "make",
    [
        lambda k: "# a" + " " * (3000 * k) + "b",
        lambda k: "### a" + " \t" * (1500 * k) + "x#y",
    ],
    ids=["dau-cach", "dau-cach-va-tab"],
)
def test_lc1_heading_with_long_whitespace_is_linear(make):
    assert_scales_linearly(markdown_to_html, make)


@pytest.mark.parametrize(
    "markdown, expected",
    [
        ("### Tiêu đề ###", "<h3>Tiêu đề</h3>"),
        ("### a #b", "<h3>a #b</h3>"),
        ("# foo#", "<h3>foo#</h3>"),
        ("## a ## b", "<h3>a ## b</h3>"),
        ("# a  #  ", "<h3>a</h3>"),
        ("#### a\t#\t", "<h4>a</h4>"),
        ("### ###", ""),
    ],
)
def test_lc1_closing_hashes_still_removed_like_commonmark(markdown, expected):
    """Canh hướng sửa LC-T096-1: bỏ dấu "#" đóng tiêu đề như cũ (CommonMark 4.2)."""
    assert markdown_to_html(markdown) == expected


# ------------------------------------------------------------------ LC-T096-2

DATA = b"anh-da-duyet"
ALT = "Cửa kéo sau khi thay ray"


def _built():
    image = ArticleImage(section=0, sha256=hashlib.sha256(DATA).hexdigest(), alt=ALT)
    return build_article(title="T", parts=[ArticlePart("", "Chữ.")], index=INDEX, images=[image])


def _draft(tags: ImageTags | None = None) -> DraftImage:
    image = WebImage(data=DATA, width=1, height=1, gps=None)
    if tags is None:
        return DraftImage(image=image, alt=ALT)
    return DraftImage(image=image, alt=ALT, tags=tags)


def test_lc2_same_image_as_confirmed_is_accepted():
    """Canh: đúng ảnh đã xác nhận (mặc định: ảnh thật, chưa thẻ) thì ghép được."""
    built = _built()
    parts = built.content_parts({0: _draft()})
    assert parts[0] == built.sections[0] and isinstance(parts[1], DraftImage)


@pytest.mark.parametrize(
    "tags",
    [ImageTags(source="ai"), ImageTags(project_code="CT012", area="Tân Phú")],
    ids=["thanh-anh-ai", "them-ma-cong-trinh-khu-vuc"],
)
def test_lc2_image_tags_bound_to_confirmation(tags):
    built = _built()
    with pytest.raises(BuildError):
        built.content_parts({0: _draft(tags)})


# ------------------------------------------------------------------ LC-T096-3

ROOT = Path(__file__).resolve().parents[1]
# Ký tự điều khiển hướng chữ (Unicode bidi): nhúng, đè, cô lập, dấu trái/phải, dấu Ả Rập.
# File test của phiếu (công cụ ghi file từng đổi chuỗi mã thành ký tự thật: xem lại lượt 3).
T096_TESTS = (
    "test_la_chan_t096.py", "test_publish_markdown.py", "test_publish_render.py",
    "test_soi_loi_t096.py",
)  # fmt: skip
_BIDI = frozenset(
    map(chr, [*range(0x202A, 0x202F), *range(0x2066, 0x206A), 0x200E, 0x200F, 0x061C])
)


def test_lc3_no_raw_bidi_control_characters_in_app_source():
    found = []
    paths = [p for folder in ("seo_app", "app", "scripts") for p in (ROOT / folder).rglob("*.py")]
    paths += [ROOT / "tests" / name for name in T096_TESTS]
    for path in sorted(paths):
        text = path.read_text(encoding="utf-8")
        for number, line in enumerate(text.splitlines(), start=1):
            chars = sorted({f"U+{ord(ch):04X}" for ch in line if ch in _BIDI})
            if chars:
                found.append(f"{path.relative_to(ROOT).as_posix()}:{number} {chars}")
    assert found == []


def test_lc3_escaped_pattern_drops_the_same_characters():
    """Canh hướng sửa LC-T096-3: ``_DROPPED`` (nay viết dạng mã) bỏ đúng các ký tự như bản cũ:
    C0 trừ tab, xuống dòng, về đầu dòng; DEL và C1; điều khiển hướng chữ U+202A–U+202E,
    U+2066–U+2069; nửa cặp UTF-16. Tập ký tự ghi bằng số, không chép ký tự trần (xem lại lượt
    3: công cụ ghi file từng đổi chuỗi mã thành ký tự thật ngay trong test này)."""
    from seo_app.publish.markdown import _DROPPED

    intended = {
        *range(0x00, 0x09), 0x0B, 0x0C, *range(0x0E, 0x20), *range(0x7F, 0xA0),
        *range(0x202A, 0x202F), *range(0x2066, 0x206A), *range(0xD800, 0xE000),
    }  # fmt: skip
    for code in range(0x110000):
        assert bool(_DROPPED.match(chr(code))) == (code in intended), f"U+{code:04X}"


# ------------------------------------------------------------------ LC-T096-4

URL = "https://www.youtube.com/watch?v=abc"


def _review(body: str):
    return build_article(title="T", parts=[ArticlePart("", body)], index=INDEX).review


@pytest.mark.parametrize(
    "pad",
    ["&nbsp;", "&#160;", "\N{ZERO WIDTH NO-BREAK SPACE}", "&emsp;", "&#x3000;"],
    ids=lambda pad: repr(pad),
)
def test_lc4_url_alone_after_unicode_space_is_blocked(pad):
    review = _review(f"{pad}{URL}{pad}")
    assert review.blocked and URL in review.embeds


@pytest.mark.parametrize("body", [URL, "\N{NO-BREAK SPACE}" + URL, f"  {URL}\t", f"- {URL}"])
def test_lc4_ascii_or_raw_space_padding_already_blocked(body):
    """Canh: dạng đang Chặn đúng thì vẫn Chặn sau khi sửa LC-T096-4."""
    assert _review(body).blocked


@pytest.mark.parametrize("body", [f"Xem&nbsp;{URL}", f"&nbsp;Xem {URL}", "&nbsp;http://x.vn/a b"])
def test_lc4_url_with_other_text_is_not_blocked(body):
    """Canh: địa chỉ có chữ khác cùng đoạn thì không bị Chặn oan."""
    assert not _review(body).blocked


# ------------------------------------------------------------------ LC-T096-5


@pytest.mark.parametrize(
    "body",
    [
        f"{URL} xem thêm",
        "https://evil.example/trang nội dung bất kỳ",
        "https://evil.example/x, xem thêm.",
        "**https://evil.example/x** xem",
    ],
)
def test_lc5_paragraph_starting_with_one_https_url_is_blocked(body):
    assert _review(body).blocked


@pytest.mark.parametrize(
    "body", [f"Xem {URL}", "https://a.vn/x https://b.vn/y", "http://evil.example/x xem"]
)
def test_lc5_url_not_at_start_or_not_https_is_not_blocked(body):
    """Canh: trình soạn khối không nhúng các đoạn này (không bắt đầu bằng https://, có hai
    https://, hay chỉ http://), nên không Chặn oan."""
    assert not _review(body).blocked


# ------------------------------------------------------------------ LC-T096-6

TAB, BS, NBSP = chr(9), chr(92), chr(0xA0)


@pytest.mark.parametrize(
    "body",
    [
        f"https://evil.ex{TAB}ample/trang nội dung",
        f"https://evil.example{TAB}/trang nội dung",
        f"https://evil.example{BS}{BS}trang nội dung",  # Markdown «\\» → một dấu «\»
        "https:///evil.example/trang nội dung",
        "https://tên đăng nhập@evil.example/trang",
    ],
    ids=["tab-trong-ten-may", "tab-sau-ten-may", "gach-nguoc", "thua-gach", "ten-dang-nhap"],
)
def test_lc6_url_forms_new_url_accepts_are_blocked(body):
    assert _review(body).blocked


@pytest.mark.parametrize(
    "body",
    [
        "https://evil.example xem thêm",
        "https://evil.example: 443/trang xem",
        f"https://evil.example{NBSP}/trang xem",
    ],
    ids=["dau-cach-sau-ten-may", "cong-co-dau-cach", "nbsp-trong-ten-may"],
)
def test_lc6_invalid_url_with_text_is_not_blocked(body):
    """Canh hướng sửa LC-T096-6: ``new URL`` từ chối các đoạn này (tên máy có khoảng trắng: dấu
    cách, cổng có dấu cách, dấu cách không ngắt), trình soạn khối không nhúng: không Chặn oan."""
    assert not _review(body).blocked
