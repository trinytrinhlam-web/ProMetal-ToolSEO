"""Soi Lỗi kiểm thử T-096 (bộ dựng bài cuối: Markdown → HTML, kiểm link, dữ liệu xác nhận).

Lỗi chưa sửa đánh ``xfail(strict=True)`` kèm mã ``SL-T096-n`` (xem
``docs/team/reports/T-096-soi-loi.md``). Không gọi mạng: danh sách bài dựng tay, không client
nào được tạo. Hai bài mẫu ở dưới viết lại theo đúng các dạng gặp trong 20 bài thật của chủ dự án
(danh sách mở đầu bằng chữ đậm, ngoặc kép thẳng, dòng chú thích in nghiêng, chỗ «[Alt ảnh: …]»,
tiêu đề con «### 1. …», danh sách đánh số, trích dẫn, bảng, đường dẫn trong chữ), không chép
nguyên văn.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import re
import subprocess
import sys
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from timing import assert_scales_linearly

from seo_app.content.models import Section
from seo_app.images.process import WebImage
from seo_app.onpage.links import (
    Candidate,
    Candidates,
    InternalLink,
    LinkKind,
    LinkSuggestion,
    LinkSuggestions,
    check_suggestions,
    markdown_blocks,
    place_links,
)
from seo_app.onpage.meta import Level
from seo_app.publish.render import (
    ArticleImage,
    ArticlePart,
    BuildError,
    SeoFields,
    build_article,
)
from seo_app.publish.review import bare_addresses, embedded_urls
from seo_app.sanitize import AUTOLINK_BREAK, clean_ai_text, sanitize_html
from seo_app.storage.site_index import SiteIndex
from seo_app.wordpress import PublishedItem
from seo_app.wordpress.client import DraftImage

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SITE = "https://suachuacuasat.com"
TZ = ZoneInfo("Asia/Ho_Chi_Minh")
BS = chr(92)  # dấu "\"
ZWSP = chr(0x200B)
NBSP = chr(0xA0)
RLO = chr(0x202E)

ITEMS = tuple(
    PublishedItem(id=i, type="post", slug=f"bai-{i}", link=f"{SITE}/bai-{i}/", title=f"Bài {i}")
    for i in range(10, 16)
)
INDEX = SiteIndex(site=SITE, fetched_at=datetime(2026, 10, 28, 9, 0, tzinfo=TZ), items=ITEMS)
LINKS_OF_SITE = {item.link for item in ITEMS}
CANDS = Candidates(tuple(Candidate(item, required=item.id == 10) for item in ITEMS))

# Thẻ có thể có trong HTML cuối: thẻ của bộ chuyển, <h2> tiêu đề phần, <a> của place_links.
FINAL_TAGS = frozenset(
    {"p", "h2", "h3", "h4", "h5", "h6", "strong", "em", "code", "pre", "br", "hr", "ul", "ol",
     "li", "table", "thead", "tbody", "tr", "th", "td", "blockquote", "a"}
)  # fmt: skip


class _Html(HTMLParser):
    """Thẻ, thuộc tính, chú thích/khai báo, ``href`` và chữ trong từng ``<a>``."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[str] = []
        self.bad_attrs: list[str] = []
        self.other: list[str] = []
        self.links: list[tuple[str | None, str]] = []
        self.text: list[str] = []
        self._href: str | None = None
        self._inside: list[str] = []
        self._in_a = False

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        for name, _value in attrs:
            if not ((tag == "a" and name == "href") or (tag == "ol" and name == "start")):
                self.bad_attrs.append(f"{tag}@{name}")
        if tag == "a":
            self._href, self._inside, self._in_a = dict(attrs).get("href"), [], True

    def handle_startendtag(self, tag, attrs):
        self.other.append(f"<{tag}/>")

    def handle_endtag(self, tag):
        if tag == "a" and self._in_a:
            self.links.append((self._href, "".join(self._inside)))
            self._in_a = False

    def handle_data(self, data):
        self.text.append(data)
        if self._in_a:
            self._inside.append(data)

    def handle_comment(self, data):
        self.other.append("comment")

    def handle_decl(self, decl):
        self.other.append("decl")

    def handle_pi(self, data):
        self.other.append("pi")

    def unknown_decl(self, data):
        self.other.append("cdata")


def parse(html_text: str) -> _Html:
    parser = _Html()
    parser.feed(html_text)
    parser.close()
    return parser


def assert_final_html_safe(sections) -> None:
    """HTML cuối: chỉ thẻ cho phép, không thuộc tính lạ, không chú thích, link chỉ trỏ bài đã
    đăng, không «[» «]» trần (T-061), lọc lại không đổi, không ký tự ngắt T-031."""
    for section in sections:
        parsed = parse(section)
        assert set(parsed.tags) <= FINAL_TAGS, set(parsed.tags) - FINAL_TAGS
        assert parsed.bad_attrs == [] and parsed.other == []
        assert {href for href, _ in parsed.links} <= LINKS_OF_SITE
        assert "[" not in section and "]" not in section
        assert sanitize_html(section) == section
        assert AUTOLINK_BREAK not in section


def build(body: str, **kwargs):
    kwargs.setdefault("title", "Bài thử")
    kwargs.setdefault("index", INDEX)
    return build_article(parts=[ArticlePart("", body)], **kwargs)


# ================================================================== bài mẫu (dạng bài thật)

ARTICLE_A = (
    "Cửa kéo bị nặng, khó kéo: nguyên nhân và cách xử lý tại nhà",
    [
        (
            "",
            "Cửa kéo phải dùng cả hai tay mới kéo được thường không do một lỗi duy nhất. Hay "
            "gặp nhất là ray bẩn, bánh xe mòn hoặc khớp lá khô dầu.\n\n"
            "Bài này giúp bạn tìm đúng chỗ nặng trong 5 phút trước khi gọi thợ sửa cửa kéo.",
        ),
        (
            "Kiểm tra nhanh: cửa nặng ở đâu?",
            "Trước khi xịt dầu, bạn kéo thử thật chậm và để ý ba chỗ:\n\n"
            "- **Nặng suốt cả đoạn:** thường do ray dưới đầy cát hoặc bánh xe đã mòn.\n"
            "- **Trơn rồi vấp ở một điểm:** ray bị móp, có sỏi kẹt trong ray.\n"
            '- **Phần trên nghiêng, cửa "đổ" khi kéo:** ray trên cong hoặc dàn cửa đã xệ.\n\n'
            'Ghi lại điểm nặng nhất. Khi gọi thợ, chỉ cần nói "kéo tới giữa thì vấp" là thợ '
            "đoán được bệnh và mang đúng đồ.\n\n"
            "*Ray dưới là nơi gom bụi và nước mưa nhiều nhất.*\n\n"
            "[Alt ảnh: Chân cửa kéo chạy trên ray dưới bám bụi · File: cua-keo-nang-1.jpg]",
        ),
        (
            "Năm nguyên nhân hay gặp",
            "### 1. Ray dưới bẩn hoặc đọng nước\n\n"
            "Ray nằm sát nền nên hứng cát, lá khô và nước lau nhà. Cặn bám lâu làm bánh xe "
            'phải "leo" thay vì lăn.\n\n'
            "### 2. Bánh xe mòn, vỡ bạc đạn\n\n"
            "Dấu hiệu dễ thấy: tiếng lạch cạch theo nhịp mỗi lần kéo.\n\n"
            "1. Nhấc nhẹ lá cửa đầu tiên.\n"
            "2. Xoay thử bánh xe bằng tay.\n"
            "3. Bánh không quay mà trượt thì nên thay bánh xe cửa kéo.\n\n"
            "> Khách ở Tân Phú hay hỏi có cần thay cả ray không. Đa số chỉ cần thay bánh xe.",
        ),
        (
            "Tự làm hay gọi thợ",
            "| Việc | Tự làm | Gọi thợ |\n"
            "|---|---|---|\n"
            "| Lau ray, tra dầu | Được | Không cần |\n"
            "| Thay bánh xe | Khó | Nên gọi |\n"
            "| Nắn ray bị cong | Không | Nên gọi |\n\n"
            "Giá thay bánh xe [cần bổ sung: giá thay bánh xe của xưởng] tùy loại cửa.\n\n"
            "---\n\n"
            "Trang dịch vụ: /sua-cua-keo-tphcm/ -> xem lịch nhận thợ trong ngày.",
        ),
    ],
)

ARTICLE_B = (
    "Cửa sắt bị rỉ sét: nhận biết mức rỉ và cách xử lý",
    [
        (
            "",
            "Cửa sắt để ngoài trời 3–5 năm là bắt đầu rỉ ở chân và bản lề. Rỉ nhẹ thì tự xử lý "
            "được trong một buổi chiều.",
        ),
        (
            "Nhận biết mức rỉ",
            "- Rỉ bề mặt: lớp màu cam, chà giấy nhám là sạch.\n"
            "  - Hay gặp ở cửa hướng Tây.\n"
            "  - Xử lý trong khoảng 30 phút.\n"
            "- Rỉ ăn sâu: sơn phồng lên, bóc ra thấy sắt rỗ.\n"
            "- Rỉ thủng: lá sắt mủn, bấm tay là thủng.\n\n"
            "**Lưu ý:** rỉ thủng ở chân cửa thì đừng sơn chồng lên, phải hàn thay đoạn sắt.",
        ),
        (
            "Các bước tự xử lý rỉ nhẹ",
            "1. Chà sạch rỉ bằng bàn chải sắt.\n"
            "2. Lau bụi rồi để khô hẳn.\n"
            "3. Sơn lót chống rỉ hai lớp.\n"
            "4. Sơn phủ cùng màu cửa.\n\n"
            "Mẹo: sơn lúc trời khô, độ ẩm dưới 70% thì sơn bám tốt hơn.\n\n"
            "Nếu cửa đã xệ vì bản lề rỉ, xem bài cửa sắt bị xệ để biết cách chỉnh lại.",
        ),
    ],
)

ARTICLES = [ARTICLE_A, ARTICLE_B]


def article_parts(article):
    return [ArticlePart(heading, body) for heading, body in article[1]]


def sections_of(article):
    return [Section(heading=heading or "Mở bài", body=body) for heading, body in article[1]]


_TOKEN = re.compile(r"\S+")
_LIST_MARKER = re.compile(r"[-+*]|[0-9]{1,9}[.)]")


def random_suggestions(rng: random.Random, sections, count: int) -> LinkSuggestions:
    """Gợi ý giả lập AI: cụm 2–5 từ chép nguyên văn từ một khối ``markdown_blocks`` ngẫu nhiên.
    Không lấy cụm bắt đầu bằng dấu mục danh sách (dạng đó là SL-T096-2, test riêng)."""
    rows = []
    for _ in range(count):
        k = rng.randrange(len(sections))
        blocks = [b for b in markdown_blocks(sections[k].body) if len(b.split()) >= 2]
        if not blocks:
            continue
        block = rng.choice(blocks)
        lines = [line for line in block.split("\n") if line.strip()]
        words = _TOKEN.findall(rng.choice(lines))
        if len(words) < 2:
            continue
        size = rng.randint(2, min(5, len(words)))
        start = rng.randrange(len(words) - size + 1)
        if _LIST_MARKER.fullmatch(words[start]):
            continue
        anchor = " ".join(words[start : start + size])
        rows.append(LinkSuggestion(post_id=rng.choice(ITEMS).id, section=k, anchor=anchor))
    return LinkSuggestions(links=rows)


@pytest.mark.parametrize("article", ARTICLES, ids=["cua-keo", "cua-sat"])
def test_real_like_article_renders_safely(article):
    built = build_article(title=article[0], parts=article_parts(article), index=INDEX)
    assert_final_html_safe(built.sections)
    assert len(built.sections) == len(article[1])
    assert built.html.count("<h2>") == len(article[1]) - 1
    # Định dạng còn đủ: danh sách, đậm, trích dẫn, bảng, tiêu đề con h3 (không h1, h2 trong thân).
    tags = set(parse(built.html).tags)
    assert {"ul", "li", "strong", "p", "h2"} <= tags
    for section in built.sections:
        body = section.split("</h2>", 1)[-1]
        assert "<h1" not in body and "<h2" not in body
    # Không có link nào ngoài link app chèn; chữ người đọc thấy không còn dấu Markdown.
    assert parse(built.html).links == []
    assert "**" not in built.html and "###" not in built.html


@pytest.mark.parametrize("article", ARTICLES, ids=["cua-keo", "cua-sat"])
def test_every_link_accepted_at_seo_step_is_placed_when_building(article):
    """Khớp chia khối: cụm từ ``check_suggestions`` (đọc ``markdown_blocks``) đã nhận thì bộ dựng
    phải chèn được, đúng chữ, không bỏ qua (đo trên bài thật: 6.822/6.822 link)."""
    rng = random.Random(96)
    sections = sections_of(article)
    accepted = 0
    for _ in range(120):
        review = check_suggestions(random_suggestions(rng, sections, 6), sections, CANDS)
        if not review.links:
            continue
        accepted += len(review.links)
        built = build_article(
            title=article[0], parts=article_parts(article), index=INDEX, links=review.links
        )
        assert built.review.skipped_links == (), [(x.section, x.anchor) for x in review.links]
        placed = parse(built.html).links
        assert len(placed) == len(review.links)
        assert sorted(" ".join(text.split()) for _href, text in placed) == sorted(
            x.anchor for x in review.links
        )
        assert_final_html_safe(built.sections)
    assert accepted > 100


# ================================================================== chữ độc qua cả bộ dựng

HOSTILE = [
    "[a [b] c](https://evil.example)",
    "[![x](https://evil.example/i.png)](https://evil.example)",
    "x[^1]\n\n[^1]: https://evil.example",
    "[x]: <https://evil.example>\n\n[x]",
    "<a@evil.example>",
    "&lt;a href=x&gt;bấm&lt;/a&gt;",
    "[x](javascript&#58;alert(1))",
    "[x](vbscript:msgbox)",
    "<div onclick=alert(1)>dịch vụ</div>",
    "<details open ontoggle=alert(1)>x</details>",
    "<svg><script>alert(1)</script></svg>",
    "<style>*{}</style>",
    "<!---->x<!-- -- -->",
    "<!-- wp:html --><script>alert(1)</script><!-- /wp:html -->",
    '<!-- wp:embed {"url":"https://evil.example"} /-->',
    "<?xml version='1.0'?> <![CDATA[<script>]]>",
    "</p><script>alert(1)</script><p>",
    chr(0xFF1C) + "script" + chr(0xFF1E) + "alert(1)",
    BS + "<script" + BS + ">alert(1)",
    BS + "[x" + BS + "]" + BS + "(https://evil.example" + BS + ")",
    "| `a|b` | [x](https://evil.example) |\n|---|---|\n| c | d |",
    "> - [x](https://evil.example)\n> - <b>y</b>",
    "&#x3C;script&#x3E;alert(1)&#x3C;/script&#x3E;",
    "&#0;&#xD800;&#x110000;&NotANamed;",
    "[embed]https://evil.example[/embed] [audio src=x] [[x]] [x\n]",
    "dịch" + RLO + "vụ" + chr(0x2066) + "x" + chr(0x2069) + chr(0xFEFF),
    "https://evil.example/x www.evil.example a@evil.example",
    "``<a href=x>`` `[x](y)`",
    "# <h1>x</h1>\n## <h2>y</h2>\n### z",
    "1. <li>x</li>\n2) [y](z)",
    "```\n</code></pre><script>\n```",
    "    <script>thụt lề</script>",
    "[dịch vụ sửa cửa kéo](https://evil.example)",
    "<a href='/bai-10/'>dịch vụ sửa cửa kéo</a>",
]


@pytest.mark.parametrize("form", ["raw", "clean_ai_text"])
@pytest.mark.parametrize("raw", HOSTILE)
def test_hostile_text_through_whole_builder(raw, form):
    """Chữ độc ở thân, tiêu đề phần, tiêu đề bài (thô như người gõ, hoặc qua ``clean_ai_text``
    như chữ AI): HTML cuối chỉ có thẻ của bộ chuyển, link duy nhất là link app chèn. Câu đối
    chứng đứng trước chữ độc (chữ độc mở khối mã thì phần sau thành mã: SL-T096-7)."""
    text = raw if form == "raw" else clean_ai_text(raw)
    body = f"Gọi dịch vụ sửa cửa kéo tận nơi.\n\n{text}"
    built = build_article(
        title=raw,
        parts=[ArticlePart("", body), ArticlePart(raw, body)],
        index=INDEX,
        links=[
            InternalLink(section=0, anchor="dịch vụ sửa cửa kéo", post_id=10),
            InternalLink(section=1, anchor="sửa cửa kéo tận nơi", post_id=11),
        ],
    )
    assert_final_html_safe(built.sections)
    hrefs = [href for href, _ in parse(built.html).links]
    assert f"{SITE}/bai-10/" in hrefs and f"{SITE}/bai-11/" in hrefs
    assert set(hrefs) <= LINKS_OF_SITE
    assert all(row.kind is LinkKind.INTERNAL and row.flags == () for row in built.review.links)
    assert "<" not in built.title or "< " in built.title  # tiêu đề không có thẻ


def test_t031_breaks_removed_and_addresses_listed_whole():
    """Chữ AI qua ``clean_ai_text`` có ký tự ngắt rộng 0 (T-031): bộ dựng gỡ ở thân, tiêu đề
    phần, tiêu đề bài; địa chỉ hiện liền mạch trong danh sách địa chỉ trần, không thành link."""
    raw = "Xem https://evil.example/khuyen-mai, www.evil.example hoặc lienhe@evil.example."
    ai = clean_ai_text(raw)
    assert AUTOLINK_BREAK in ai  # điều kiện đầu: T-031 đã chèn ký tự ngắt
    built = build_article(
        title=clean_ai_text("Bài có www.evil.example"),
        parts=[ArticlePart("", ai), ArticlePart(clean_ai_text("Mục www.evil.example"), ai)],
        index=INDEX,
    )
    assert AUTOLINK_BREAK not in built.title and "www.evil.example" in built.title
    assert_final_html_safe(built.sections)
    assert parse(built.html).links == []
    listed = {(address.text, address.kind) for address in built.review.bare}
    assert {
        ("https://evil.example/khuyen-mai", "url"),
        ("www.evil.example", "www"),
        ("lienhe@evil.example", "email"),
    } <= listed


# ================================================================== địa chỉ đứng một mình (nhúng)

VIDEO = "https://www.youtube.com/watch?v=abc"
ALONE = {
    "đoạn": f"Mở đầu.\n\n{VIDEO}\n\nKết.",
    "đoạn sau clean_ai_text": clean_ai_text(f"Mở đầu.\n\n{VIDEO}\n\nKết."),
    "chữ hoa": "HTTPS://WWW.YOUTUBE.COM/watch?v=abc",
    "dấu cách hai đầu": f"   {VIDEO}   ",
    "tab đầu": f"\t{VIDEO}",
    "dấu cách không ngắt đầu": f"{NBSP}{VIDEO}",
    "mục danh sách": f"- {VIDEO}\n- chữ",
    "danh sách thưa": f"- chữ\n\n- {VIDEO}",
    "danh sách số": f"1. {VIDEO}",
    "ô bảng": f"| a |\n|---|\n| {VIDEO} |",
    "tiêu đề con": f"### {VIDEO}",
    "trích dẫn": f"> {VIDEO}",
    "khối mã": f"```\n{VIDEO}\n```",
    "dòng giữa khối mã": f"```\nxem\n{VIDEO}\nhết\n```",
    "mã xuống dòng": f"Xem:&#10;{VIDEO}&#10;nhé",
    "mã xuống dòng kiểu Windows": f"Xem:&#13;&#10;{VIDEO}&#13;&#10;nhé",
    "dấu hai chấm escape": "https" + BS + ":" + "//www.youtube.com/watch?v=abc",
    "mã ký tự dấu hai chấm": "https&#58;//www.youtube.com/watch?v=abc",
    "mã ký tự dấu gạch chéo": "https:&#47;&#47;www.youtube.com/watch?v=abc",
    "có dấu &": "https://www.youtube.com/watch?v=abc&t=10",
    "dấu chấm cuối": f"{VIDEO}.",
}


@pytest.mark.parametrize("mode", ["draft", "future", "publish"])
@pytest.mark.parametrize("body", ALONE.values(), ids=ALONE.keys())
def test_url_alone_is_blocked_in_every_mode(body, mode):
    """LC-T094-6: đoạn, dòng hay khối chỉ có một địa chỉ (WordPress nhúng cả trang) → Chặn ở
    mọi hình thức gửi, kể cả Nháp."""
    built = build(
        body,
        mode=mode,
        date_gmt="2026-11-03T01:00:00" if mode == "future" else "",
        seo=SeoFields("Tiêu đề", "Mô tả", "cửa kéo", write=True),
    )
    assert built.review.embeds
    assert built.review.blocked
    assert any("nhúng" in p.message for p in built.review.problems if p.level is Level.BLOCK)


NOT_ALONE = {
    "giữa câu": f"Xem {VIDEO} nhé.",
    "hai địa chỉ": f"{VIDEO} {VIDEO}",
    "ngoặc nhọn": f"<{VIDEO}>",
    "link Markdown": f"[video]({VIDEO})",
    "ảnh Markdown": f"![video]({VIDEO})",
    "ký tự rộng 0 đứng đầu": f"{ZWSP}{VIDEO}",
    "xuống dòng mềm": f"Xem:\n{VIDEO}\nnhé",
}


@pytest.mark.parametrize("body", NOT_ALONE.values(), ids=NOT_ALONE.keys())
def test_url_with_other_text_is_not_an_embed(body):
    """Địa chỉ có chữ khác cùng dòng/đoạn: WordPress không nhúng, bộ dựng không chặn oan."""
    built = build(body)
    assert built.review.embeds == ()
    assert not built.review.blocked


# ================================================================== mã băm xác nhận

_DIGEST_SCRIPT = """
import json, sys
from datetime import datetime
from zoneinfo import ZoneInfo
from seo_app.onpage.links import InternalLink
from seo_app.publish.render import ArticleImage, ArticlePart, SeoFields, build_article
from seo_app.storage.site_index import SiteIndex
from seo_app.wordpress import PublishedItem
site = "https://suachuacuasat.com"
items = tuple(PublishedItem(id=i, type="post", slug=f"bai-{i}", link=f"{site}/bai-{i}/",
              title=f"Bài {i}") for i in range(10, 16))
index = SiteIndex(site=site, fetched_at=datetime(2026, 10, 28, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh")),
                  items=items)
data = json.loads(sys.stdin.read())
built = build_article(
    title=data["title"], parts=[ArticlePart(h, b) for h, b in data["parts"]], index=index,
    links=[InternalLink(section=1, anchor="ray dưới", post_id=11)],
    images=[ArticleImage(section=1, sha256="b" * 64, alt="Ray dưới", caption="Chú thích",
                         featured=True)],
    seo=SeoFields("Tiêu đề", "Mô tả", "cửa kéo", True), mode="future",
    date_gmt="2026-11-03T01:00:00", categories=[3, 1], tags=[7],
)
print(built.digest)
"""


def test_digest_same_in_every_process():
    """Cùng nội dung thì cùng mã băm, kể cả ở tiến trình khác với hạt băm (hash seed) khác: mã
    tính lúc hiện màn hình xác nhận và lúc gửi phải khớp."""
    data = json.dumps({"title": ARTICLE_A[0], "parts": ARTICLE_A[1]}, ensure_ascii=False)
    digests = set()
    for seed in ("0", "12345"):
        env = {**os.environ, "PYTHONHASHSEED": seed, "PYTHONUTF8": "1"}
        result = subprocess.run(  # noqa: S603 (chạy chính Python của test, không gọi mạng)
            [sys.executable, "-c", _DIGEST_SCRIPT],
            input=data,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=PROJECT_ROOT,
            env=env,
            timeout=120,
            check=True,
        )
        digests.add(result.stdout.strip())
    assert len(digests) == 1 and len(digests.pop()) == 64


def _sent(built) -> str:
    """Mọi thứ sẽ gửi đi (chữ đúng như client nhận), để so với mã băm."""
    return json.dumps(
        [
            built.title,
            built.sections,
            built.excerpt,
            built.slug,
            built.categories,
            built.tags,
            [vars(image) for image in built.images],
            vars(built.seo),
            built.mode,
            built.date_gmt,
        ],
        ensure_ascii=False,
    )


def test_digest_changes_exactly_when_sent_content_changes():
    """Sửa một ký tự ở bất kỳ ô nào: chữ gửi đi đổi thì mã băm đổi; chữ gửi đi không đổi (ví dụ
    thêm dấu cách thừa, ký tự bị bỏ) thì mã băm giữ nguyên. Không bao giờ hai gói gửi khác nhau
    cùng mã."""
    rng = random.Random(28)
    base = {
        "title": ARTICLE_A[0],
        "parts": [list(part) for part in ARTICLE_A[1]],
        "excerpt": "Cửa kéo nặng: 5 nguyên nhân.",
        "slug": "cua-keo-bi-nang",
        "alt": "Ray dưới bám bụi",
        "caption": "Ray dưới",
        "seo_title": "Cửa kéo bị nặng",
    }

    def make(state):
        return build_article(
            title=state["title"],
            parts=[ArticlePart(h, b) for h, b in state["parts"]],
            index=INDEX,
            links=[InternalLink(section=2, anchor="ray dưới bẩn", post_id=11)],
            images=[ArticleImage(section=1, sha256="a" * 64, alt=state["alt"],
                                 caption=state["caption"])],
            excerpt=state["excerpt"],
            slug=state["slug"],
            seo=SeoFields(state["seo_title"], "Mô tả", "cửa kéo"),
        )  # fmt: skip

    original = make(base)
    seen: dict[str, str] = {original.digest: _sent(original)}
    edits = ["x", " ", "  ", "\n", ZWSP, RLO, "*", "[", "&", "<", "é", "đ"]
    changed = 0
    for _ in range(150):
        state = json.loads(json.dumps(base))
        key = rng.choice(["title", "parts", "excerpt", "slug", "alt", "caption", "seo_title"])
        if key == "parts":
            k = rng.randrange(len(state["parts"]))
            j = rng.randrange(2)
            target = state["parts"][k][j]
        else:
            target = state[key]
        pos = rng.randrange(len(target) + 1)
        new = target[:pos] + rng.choice(edits) + target[pos:]
        if key == "parts":
            state["parts"][k][j] = new
        else:
            state[key] = new
        built = make(state)
        sent = _sent(built)
        if built.digest in seen:
            assert seen[built.digest] == sent  # cùng mã băm ⇒ cùng gói gửi đi
        seen[built.digest] = sent
        changed += sent != _sent(original)
        assert (built.digest == original.digest) == (sent == _sent(original))
    assert changed > 100


# ================================================================== dữ liệu xác nhận


def test_review_lists_every_internal_link_with_its_text():
    built = build_article(
        title=ARTICLE_A[0],
        parts=article_parts(ARTICLE_A),
        index=INDEX,
        links=[
            InternalLink(section=0, anchor="ray bẩn", post_id=10),
            InternalLink(section=1, anchor="ray dưới đầy cát", post_id=11),
            InternalLink(section=2, anchor="thay bánh xe cửa kéo", post_id=12),
            InternalLink(section=3, anchor="Lau ray, tra dầu", post_id=13),
        ],
        required_ids=[10],
    )
    rows = built.review.links
    assert [(row.text, row.post_id) for row in rows] == [
        ("ray bẩn", 10),
        ("ray dưới đầy cát", 11),
        ("thay bánh xe cửa kéo", 12),
        ("Lau ray, tra dầu", 13),
    ]
    assert all(row.kind is LinkKind.INTERNAL and row.level is Level.GOOD for row in rows)
    assert all(row.flags == () and row.ascii_host == "suachuacuasat.com" for row in rows)
    assert not built.review.blocked


@pytest.mark.parametrize(
    "address, ascii_host, flags",
    [
        ("https://suachuacuas" + chr(0x430) + "t.com/x", "xn--suachuacuast-79j.com",
         {"chữ ngoài ASCII", "Khác website"}),
        ("https://suachuacuasat.c" + chr(0x43E) + "m/x", "suachuacuasat.xn--cm-fmc",
         {"chữ ngoài ASCII", "Khác website"}),
        ("https://suachuacuasat.com@evil.example/", "evil.example", {"«@»", "Khác website"}),
        ("https://suachuacuasat.com:8080/x", "suachuacuasat.com", {"Cổng lạ"}),
        ("https://xn--suachuacuast-79j.com/", "xn--suachuacuast-79j.com",
         {"dạng mã xn--", "Khác website"}),
        ("lienhe@suachuacuas" + chr(0x430) + "t.com", "xn--suachuacuast-79j.com",
         {"chữ ngoài ASCII", "Khác website"}),
        ("https://suachuacuasat.com.evil.example/", "suachuacuasat.com.evil.example",
         {"Khác website"}),
        ("https://SUACHUACUASAT.COM/x", "suachuacuasat.com", set()),
    ],
)  # fmt: skip
@pytest.mark.parametrize("form", ["raw", "clean_ai_text"])
def test_bare_addresses_in_body_listed_with_flags(address, ascii_host, flags, form):
    text = f"Liên hệ {address} nhé."
    built = build(text if form == "raw" else clean_ai_text(text))
    (bare,) = built.review.bare
    assert bare.text == address and bare.ascii_host == ascii_host
    for flag in flags:
        assert any(flag in f for f in bare.flags), (flag, bare.flags)
    if not flags:
        assert bare.flags == ()


# ================================================================== links.py sau khi sửa LC-T039-2


def test_place_links_on_sanitized_html_never_reopens_shortcodes_fuzz():
    """``place_links`` trên HTML đã lọc (có ``&#91;…&#93;``): chữ được in lại vẫn vô hiệu «[» «]»,
    chữ người đọc thấy không đổi, link mới chỉ trỏ bài đã đăng (LC-T094-10 a)."""
    rng = random.Random(39)
    pieces = [
        "<p>", "</p>", "<ul><li>", "</li></ul>", "<strong>", "</strong>", "[gallery id=1]",
        "[[caption]]", "[/embed]", "[cần bổ sung: giá]", "dịch vụ sửa cửa kéo", "thay bánh xe",
        " ", "\n", "&amp;", "<code>", "</code>", "<h2>", "</h2>", "x]", "[y",
    ]  # fmt: skip
    links = [
        InternalLink(section=s, anchor=a, post_id=p)
        for s in (0, 1)
        for a, p in (("dịch vụ sửa cửa kéo", 10), ("thay bánh xe", 11))
    ]
    applied = 0
    for _ in range(800):
        raw = "".join(rng.choice(pieces) for _ in range(rng.randint(1, 30))) + "</code></p>"
        clean = sanitize_html(raw)
        placed = place_links(clean, rng.sample(links, rng.randint(1, 3)), INDEX)
        assert "[" not in placed.html and "]" not in placed.html, clean
        assert "".join(parse(placed.html).text) == "".join(parse(clean).text)
        assert {href for href, _ in parse(placed.html).links} <= LINKS_OF_SITE
        applied += len(placed.applied)
    assert applied > 100


# ================================================================== lỗi tìm thấy (xfail)

_SL1 = "SL-T096-1: dữ liệu màn hình xác nhận chạy bậc hai (email trần, dòng chỉ có địa chỉ)"


@pytest.mark.parametrize(
    "make",
    [lambda k: "<p>" + "a" * (k * 2500) + "</p>", lambda k: "<p>" + "a." * (k * 1250) + "</p>"],
    ids=["chữ-liền", "chữ-chấm"],
)
def test_sl1_bare_addresses_linear(make):
    """Một «từ» rất dài không dấu cách (AI bị dụ, chuỗi base64…): biểu thức email
    ``[\\w.%+-]+@`` thử lại từ mọi vị trí trong từ."""
    assert_scales_linearly(lambda text: bare_addresses(text, SITE), make, label="địa chỉ trần")


def test_sl1_embedded_urls_linear():
    """Khối mã (hay đoạn có ``&#10;``) có nhiều dòng trống: ``^\\s*`` của biểu thức nhúng ăn qua
    mọi dòng trống phía sau rồi lùi lại, ở từng đầu dòng."""
    assert_scales_linearly(
        embedded_urls,
        lambda k: "<pre><code>x" + "\n" * (k * 2500) + "y</code></pre>",
        label="chỗ nhúng",
    )


def test_sl1_build_article_linear_on_long_word():
    """Ảnh hưởng tới người dùng: dựng bài (mỗi lần hiện màn hình xác nhận) chậm theo bình phương."""
    assert_scales_linearly(build, lambda k: "a" * (k * 2500), label="dựng bài")


_SL2 = "SL-T096-2: bước SEO nhận cụm từ có ký hiệu Markdown mà HTML cuối không có"


@pytest.mark.parametrize(
    "body, anchor",
    [
        ("Các bước:\n\n- Kéo cửa ở giữa rồi lau ray.\n- Tra dầu.", "- Kéo cửa ở giữa"),
        ("+ Kéo cửa ở giữa rồi lau ray.", "+ Kéo cửa ở giữa"),
        ("1. Tháo nắp chụp bánh xe.\n2. Tra dầu.", "1. Tháo nắp chụp"),
        ("1) Tháo nắp chụp bánh xe.", "1) Tháo nắp chụp"),
        ("Gọi dịch vụ sửa  \ncửa kéo tận nơi.", "dịch vụ sửa cửa kéo"),
        ("Gọi dịch vụ sửa cửa k&eacute;o tận nơi.", "sửa cửa k&eacute;o"),
        ("> Kéo cửa thật chậm\nđể nghe tiếng kêu.", "Kéo cửa thật chậm để nghe"),
        ("| Lỗi | Cách |\n|---|---|\n| Kẹt | Lau ray | gọi thợ kiểm tra |", "gọi thợ kiểm tra"),
    ],
    ids=["gạch", "cộng", "số-chấm", "số-ngoặc", "ngắt-dòng-cứng", "mã-ký-tự", "trích-dẫn-lười",
         "ô-bảng-thừa"],
)  # fmt: skip
def test_sl2_accepted_anchor_is_always_placed(body, anchor):
    """Cụm từ bước SEO nhận (``check_suggestions`` đọc ``markdown_blocks``) thì bộ dựng phải chèn
    được; nếu không chèn được thì bước SEO phải bỏ ngay từ đầu. Hiện tại: nhận, rồi bộ dựng bỏ qua,
    link bắt buộc thành «Thiếu link bắt buộc» (Chặn)."""
    sections = [Section(heading="Mở bài", body=body)]
    review = check_suggestions(
        LinkSuggestions(links=[LinkSuggestion(post_id=10, section=0, anchor=anchor)]),
        sections,
        CANDS,
    )
    built = build(body, links=review.links, required_ids=[10])
    assert not review.links or built.review.skipped_links == ()


def test_sl2_link_does_not_take_another_paragraph():
    """``markdown_blocks`` che cả quãng từ dấu «`» đầu tới dấu «`» cuối dòng, HTML chỉ có từng
    `mã`: bước SEO kiểm link «dịch vụ sửa cửa kéo» ở đoạn 2 (đoạn 1 bị che), bộ dựng lại chèn vào
    đoạn 1 (lần xuất hiện đầu), chiếm mất đoạn của link «kẹt ray» nên link đó bị bỏ."""
    body = (
        "Dùng `a` hoặc dịch vụ sửa cửa kéo hoặc `b` khi kẹt ray.\n\n"
        "Gọi dịch vụ sửa cửa kéo tận nơi."
    )
    review = check_suggestions(
        LinkSuggestions(
            links=[
                LinkSuggestion(post_id=11, section=0, anchor="dịch vụ sửa cửa kéo"),
                LinkSuggestion(post_id=12, section=0, anchor="kẹt ray"),
            ]
        ),
        [Section(heading="Mở bài", body=body)],
        CANDS,
    )
    built = build(body, links=review.links)
    assert built.review.skipped_links == ()


def test_sl3_embed_with_ampersand_listed_once():
    """Link YouTube kiểu ``…watch?v=abc&t=10`` đứng một mình: liệt kê hai lần (dạng ``&amp;`` của
    HTML và dạng đã giải mã), câu báo ghi «Có 2 đoạn» dù chỉ có một đoạn."""
    built = build("https://www.youtube.com/watch?v=abc&t=10")
    assert len(built.review.embeds) == 1
    assert "&amp;" not in built.review.embeds[0]  # chữ thô người dùng đọc, không phải mã HTML
    assert any(p.message.startswith("Có 1 đoạn") for p in built.review.problems)


@pytest.mark.parametrize("where", ["title", "excerpt", "alt", "caption"])
def test_sl4_bare_addresses_outside_body_are_listed(where):
    """Tiêu đề bài, đoạn trích, chú thích ảnh hiện công khai (alt đọc được bằng máy): địa chỉ,
    email trong đó cũng phải có ở danh sách địa chỉ trần (LC-T094-7, thiết kế 3.5)."""
    address = "https://evil.example/khuyen-mai"
    fields = {"title": "Bài thử", "excerpt": "", "alt": "Ảnh cửa", "caption": ""}
    fields[where] = f"Xem {address} nhé"
    built = build(
        "Thân bài không có địa chỉ.",
        title=fields["title"],
        excerpt=fields["excerpt"],
        images=[
            ArticleImage(section=0, sha256="c" * 64, alt=fields["alt"], caption=fields["caption"])
        ],
    )
    assert address in {bare.text for bare in built.review.bare}


def _draft_image(data: bytes, alt: str, *, featured: bool = False) -> DraftImage:
    return DraftImage(
        image=WebImage(data=data, width=1, height=1, gps=None), alt=alt, featured=featured
    )


@pytest.mark.parametrize("change", ["byte", "alt", "featured"])
def test_sl5_content_parts_rejects_images_other_than_confirmed(change):
    """Mã băm xác nhận gồm băm byte, alt, ảnh đại diện (LC-T094-8), nhưng ``content_parts`` chỉ
    so số phần: đưa vào một ``DraftImage`` khác ảnh đã băm vẫn được ghép vào bài."""
    data = b"anh-da-duyet"
    built = build(
        "Thân bài.",
        images=[ArticleImage(section=0, sha256=hashlib.sha256(data).hexdigest(), alt="Ray dưới")],
    )
    other = {
        "byte": _draft_image(b"anh-khac", "Ray dưới"),
        "alt": _draft_image(data, "Alt khác"),
        "featured": _draft_image(data, "Ray dưới", featured=True),
    }[change]
    with pytest.raises(BuildError):
        built.content_parts({0: other})


def test_sl6_place_links_keeps_encoded_bracket_next_to_bare_one():
    """Nút chữ có «&#91;» (đã vô hiệu) và «]» trần: chữ in lại thành «[gallery id=1]» trần, tức
    tạo ra shortcode chạy được mà đầu vào không có (phần còn sót của LC-T039-2). Bộ dựng không
    gặp vì luôn lọc trước và sau, nhưng ``apply_links`` là hàm dùng chung."""
    html_text = "<p>&#91;gallery id=1] dịch vụ sửa cửa kéo</p>"
    out = place_links(
        html_text, [InternalLink(section=0, anchor="dịch vụ sửa cửa kéo", post_id=10)], INDEX
    ).html
    assert "<a " in out
    assert "[gallery" not in out


@pytest.mark.parametrize(
    "first_line",
    ["```lệnh``` là lệnh mở cửa.", "``` aa ```", "```` `x`"],
    ids=["mã-ba-dấu-giữa-câu", "ví-dụ-CommonMark", "sau-clean_ai_text"],
)
def test_sl7_backtick_line_with_backticks_after_is_not_a_fence(first_line):
    """CommonMark (Streamlit dùng để hiện bản xem trước): sau rào ```, phần chữ không được có dấu
    «`»; có thì dòng đó là đoạn văn có `mã`, không mở khối mã. Bộ chuyển (và ``markdown_blocks``)
    coi mọi dòng bắt đầu bằng ``` là rào: toàn bộ phần còn lại của mục thành khối mã trên website
    dù bản xem trước hiện chữ thường. ``clean_ai_text`` bỏ thẻ giữa hai cặp dấu huyền
    («``<b>`` `x`» thành «```` `x`») cũng sinh ra dòng như vậy."""
    built = build(f"{first_line}\n\nĐoạn sau là chữ thường.")
    assert "<p>Đoạn sau là chữ thường.</p>" in built.html
    assert "<pre>" not in built.html
