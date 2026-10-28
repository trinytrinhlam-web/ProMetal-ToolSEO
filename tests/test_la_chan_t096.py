"""Lá Chắn T-096: test chứng minh lỗi, ``xfail(strict=True)`` tới khi sửa; kèm test canh hướng sửa.

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


@pytest.mark.xfail(
    strict=True, reason="LC-T096-1: tiêu đề có dãy khoảng trắng dài làm bộ chuyển chạy bậc hai"
)
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


@pytest.mark.xfail(
    strict=True,
    reason="LC-T096-2: thẻ ảnh (thật/AI, nơi chụp) không được ràng vào ảnh đã xác nhận",
)
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
_BIDI = frozenset(
    map(chr, [*range(0x202A, 0x202F), *range(0x2066, 0x206A), 0x200E, 0x200F, 0x061C])
)


@pytest.mark.xfail(
    strict=True,
    reason="LC-T096-3: markdown.py:57 viết trần ký tự điều khiển hướng chữ (Trojan Source)",
)
def test_lc3_no_raw_bidi_control_characters_in_app_source():
    found = []
    for folder in ("seo_app", "app", "scripts"):
        for path in sorted((ROOT / folder).rglob("*.py")):
            text = path.read_text(encoding="utf-8")
            for number, line in enumerate(text.splitlines(), start=1):
                chars = sorted({f"U+{ord(ch):04X}" for ch in line if ch in _BIDI})
                if chars:
                    found.append(f"{path.relative_to(ROOT).as_posix()}:{number} {chars}")
    assert found == []


def test_lc3_escaped_pattern_drops_the_same_characters():
    """Canh hướng sửa LC-T096-3: viết bằng mã ``\\uXXXX`` thì bỏ đúng các ký tự như cũ."""
    import re

    from seo_app.publish.markdown import _DROPPED

    escaped = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f‪-‮⁦-⁩\ud800-\udfff]")
    for code in range(0x110000):
        ch = chr(code)
        assert bool(_DROPPED.match(ch)) == bool(escaped.match(ch)), f"U+{code:04X}"


# ------------------------------------------------------------------ LC-T096-4

URL = "https://www.youtube.com/watch?v=abc"


def _review(body: str):
    return build_article(title="T", parts=[ArticlePart("", body)], index=INDEX).review


@pytest.mark.xfail(
    strict=True,
    reason="LC-T096-4: lớp chặn nhúng chặt hơn chỉ bỏ khoảng trắng ASCII, trình soạn khối bỏ cả "
    "khoảng trắng Unicode (trim của JavaScript)",
)
@pytest.mark.parametrize(
    "pad", ["&nbsp;", "&#160;", "﻿", "&emsp;", "&#x3000;"], ids=lambda pad: repr(pad)
)
def test_lc4_url_alone_after_unicode_space_is_blocked(pad):
    review = _review(f"{pad}{URL}{pad}")
    assert review.blocked and URL in review.embeds


@pytest.mark.parametrize("body", [URL, f" {URL}", f"  {URL}\t", f"- {URL}"])
def test_lc4_ascii_or_raw_space_padding_already_blocked(body):
    """Canh: dạng đang Chặn đúng thì vẫn Chặn sau khi sửa LC-T096-4."""
    assert _review(body).blocked


@pytest.mark.parametrize("body", [f"Xem&nbsp;{URL}", f"&nbsp;Xem {URL}", "&nbsp;http://x.vn/a b"])
def test_lc4_url_with_other_text_is_not_blocked(body):
    """Canh: địa chỉ có chữ khác cùng đoạn thì không bị Chặn oan."""
    assert not _review(body).blocked
