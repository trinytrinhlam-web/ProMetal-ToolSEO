"""T-096: bộ dựng bài cuối (``seo_app/publish/render.py``) và dữ liệu màn hình xác nhận
(``seo_app/publish/review.py``).

Điều kiện Lá Chắn: LC-T094-5 (thứ tự lọc → chèn → lọc → kiểm trên đúng chuỗi sẽ gửi), -6 (chặn
nhúng), -7 (mọi ``href``, tên máy ASCII, địa chỉ trần, shortcode, ảnh GPS), -8 (mã băm), -9 (gỡ ký
tự ngắt rộng 0 trong bộ dựng, trước khi escape), -10 (không ``<h1>``, ``<h2>`` trong thân).
Không gọi mạng: danh sách bài dựng tay.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

import seo_app.publish.render as render
from seo_app.onpage.links import InternalLink, LinkKind, check_links
from seo_app.onpage.meta import Level
from seo_app.publish.render import (
    ArticleImage,
    ArticlePart,
    BuildError,
    SeoFields,
    build_article,
    digest_of,
    plain_line,
)
from seo_app.publish.review import (
    FLAG_AT,
    FLAG_BACKSLASH,
    FLAG_NON_ASCII,
    FLAG_OTHER_SITE,
    FLAG_PORT,
    FLAG_PROTOCOL_RELATIVE,
    FLAG_PUNYCODE,
    address_flags,
    bare_addresses,
    embedded_urls,
    link_rows,
)
from seo_app.sanitize import AUTOLINK_BREAK, clean_ai_text
from seo_app.storage.site_index import SiteIndex
from seo_app.wordpress import PublishedItem

SITE = "https://suachuacuasat.com"
SERVICE = PublishedItem(
    id=10,
    type="page",
    slug="sua-cua-keo-tphcm",
    link=f"{SITE}/sua-cua-keo-tphcm/",
    title="Sửa cửa kéo tại TP.HCM",
)
GUIDE = PublishedItem(
    id=11,
    type="post",
    slug="cua-keo-bi-ket",
    link=f"{SITE}/cua-keo-bi-ket/",
    title="Cửa kéo bị kẹt",
)
INDEX = SiteIndex(
    site=SITE,
    fetched_at=datetime(2026, 10, 27, 9, 0, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh")),
    items=(SERVICE, GUIDE),
)
SHA = "ab" * 32
PARTS = [
    ArticlePart("Mở bài", clean_ai_text("Cửa kéo kêu rít là dấu hiệu cần **tra dầu**.")),
    ArticlePart(
        "Khi nào gọi thợ",
        clean_ai_text("Nếu đã tra dầu mà vẫn kẹt, hãy gọi dịch vụ sửa cửa kéo tận nơi."),
    ),
    ArticlePart("Câu hỏi thường gặp", clean_ai_text("- Cửa kéo bị kẹt có tự sửa được không?")),
]
LINKS = [
    InternalLink(section=1, anchor="dịch vụ sửa cửa kéo", post_id=10),
    InternalLink(section=2, anchor="Cửa kéo bị kẹt", post_id=11),
]


def build(**changes):
    args = {
        "title": "Cửa kéo kêu rít: nguyên nhân và cách xử lý",
        "parts": PARTS,
        "index": INDEX,
        "links": LINKS,
        "required_ids": [10],
        "images": [ArticleImage(section=1, sha256=SHA, alt="Thợ tra dầu ray cửa kéo")],
        "slug": "cua-keo-keu-rit",
        "categories": [3],
        "tags": [7, 8],
        "seo": SeoFields("Cửa kéo kêu rít | Pro-Metal", "Mô tả", "cửa kéo kêu rít", True),
    }
    args.update(changes)
    return build_article(**args)


# ------------------------------------------------------------------ dựng bài


def test_sections_match_old_layout_and_links_are_applied():
    built = build()
    assert built.sections == (
        "<p>Cửa kéo kêu rít là dấu hiệu cần <strong>tra dầu</strong>.</p>",
        "<h2>Khi nào gọi thợ</h2>\n<p>Nếu đã tra dầu mà vẫn kẹt, hãy gọi "
        f'<a href="{SERVICE.link}">dịch vụ sửa cửa kéo</a> tận nơi.</p>',
        f'<h2>Câu hỏi thường gặp</h2>\n<ul>\n<li><a href="{GUIDE.link}">Cửa kéo bị kẹt</a> có tự '
        "sửa được không?</li>\n</ul>",
    )
    assert built.html == "\n".join(built.sections)
    assert built.review.level is Level.GOOD
    assert built.title == "Cửa kéo kêu rít: nguyên nhân và cách xử lý"
    assert built.categories == (3,) and built.tags == (7, 8) and built.slug == "cua-keo-keu-rit"


def test_content_parts_put_image_after_its_section():
    built = build()
    assert built.content_parts({1: "ẢNH"}) == [
        built.sections[0],
        built.sections[1],
        "ẢNH",
        built.sections[2],
    ]
    with pytest.raises(BuildError):
        built.content_parts({})  # thiếu ảnh đã khai
    with pytest.raises(BuildError):
        built.content_parts({1: "ẢNH", 2: "ẢNH LẠ"})  # ảnh chưa qua bộ dựng


def test_order_filter_link_filter_check_on_the_same_string(monkeypatch):
    """LC-T094-5: sanitize_html → place_links → sanitize_html → check_links, mỗi bước nhận đúng
    đầu ra của bước trước; HTML gửi đi (sections) đúng là chuỗi check_links đã kiểm."""
    calls: list[tuple[str, str]] = []
    real_sanitize, real_place, real_check = (
        render.sanitize_html,
        render.place_links,
        render.check_links,
    )

    def sanitize(text):
        out = real_sanitize(text)
        calls.append(("sanitize", text))
        calls.append(("sanitized", out))
        return out

    def place(text, links, index):
        placed = real_place(text, links, index)
        calls.append(("place", text))
        calls.append(("placed", placed.html))
        return placed

    def check(text, index, required):
        calls.append(("check", text))
        return real_check(text, index, required)

    monkeypatch.setattr(render, "sanitize_html", sanitize)
    monkeypatch.setattr(render, "place_links", place)
    monkeypatch.setattr(render, "check_links", check)
    built = build()
    names = [name for name, _ in calls]
    assert names == ["sanitize", "sanitized", "place", "placed", "sanitize", "sanitized", "check"]
    values = dict(zip(range(len(calls)), (v for _, v in calls), strict=True))
    assert values[2] == values[1]  # place nhận HTML đã lọc
    assert values[4] == values[3]  # lọc lần hai nhận HTML đã chèn link
    assert values[6] == values[5]  # check nhận HTML đã lọc lần hai
    assert built.html == values[6]  # gửi đi đúng chuỗi đã kiểm, không bước nào sửa sau


def test_check_links_blocks_missing_required_link():
    built = build(links=[], required_ids=[10])
    assert built.review.blocked
    assert any("Thiếu link bắt buộc" in p.message for p in built.review.problems)


def test_skipped_links_are_reported_not_inserted():
    built = build(
        links=[InternalLink(section=0, anchor="không có trong bài", post_id=11)], required_ids=[]
    )
    assert "<a " not in built.sections[0]
    assert built.review.skipped_links
    assert built.review.level is Level.WARN


# ------------------------------------------------------------------ LC-T094-9: ký tự ngắt


def test_autolink_breaks_removed_and_addresses_never_become_links():
    """Theo gợi ý test của T-031: bài có https://, www., email → HTML gửi đi không còn U+200B,
    không có <a> nào ngoài link nội bộ; địa chỉ được liệt kê ở màn hình xác nhận."""
    body = clean_ai_text(
        "Xem https://evil.example/x, www.evil.example và thư a@evil.example nhé. "
        "Gọi dịch vụ sửa cửa kéo."
    )
    assert AUTOLINK_BREAK in body  # chữ trong nháp có ký tự ngắt (T-031)
    built = build(
        title=clean_ai_text("Tiêu đề có www.evil.example"),
        parts=[ArticlePart("", body)],
        links=[InternalLink(section=0, anchor="dịch vụ sửa cửa kéo", post_id=10)],
        images=[],
    )
    assert AUTOLINK_BREAK not in built.html and AUTOLINK_BREAK not in built.title
    assert built.html.count("<a ") == 1 and built.html.count(f'href="{SERVICE.link}"') == 1
    assert [(a.text, a.kind) for a in built.review.bare] == [
        ("https://evil.example/x", "url"),
        ("www.evil.example", "www"),
        ("a@evil.example", "email"),
    ]
    assert built.title == "Tiêu đề có www.evil.example"


def test_plain_line_removes_breaks_and_link_escapes():
    assert plain_line(clean_ai_text("Xem  https://a.vn \n và [x]")) == "Xem https://a.vn và [x]"
    assert plain_line(None) == ""


# ------------------------------------------------------------------ LC-T094-10: tiêu đề


def test_body_never_has_h1_or_h2_and_one_h2_per_section():
    body = "# một\n## hai\n### ba\nSetext\n===\nCon\n---\n#### bốn"
    built = build(parts=[ArticlePart("A", body), ArticlePart("B", body)], images=[], links=[])
    assert "<h1" not in built.html
    assert built.html.count("<h2>") == 1
    assert built.sections[1].startswith("<h2>B</h2>\n")
    assert built.sections[1][len("<h2>B</h2>") :].count("<h2") == 0


def test_heading_text_is_escaped():
    built = build(
        parts=[ArticlePart("", "a"), ArticlePart("<script>[x]</script>", "b")],
        images=[],
        links=[],
    )
    assert built.sections[1] == "<h2>&lt;script&gt;&#91;x&#93;&lt;/script&gt;</h2>\n<p>b</p>"


# ------------------------------------------------------------------ LC-T094-6: nhúng


@pytest.mark.parametrize(
    "html_text",
    [
        "<p>https://www.youtube.com/watch?v=abc</p>",
        "<p> https://x.example/a </p>",
        '<p class="c">\thttps://x.example/a\n</p>',
        "<ul>\n<li>\nhttps://www.youtube.com/watch?v=abc\n</li>\n</ul>",
        "<li>https://x.example/a</li>",
        "<p>a</p>\r\nhttps://youtube.com/x\r\n<p>b</p>",
        "<pre><code>dòng một\nHTTPS://youtube.com/x\ndòng ba</code></pre>",
    ],
)
def test_embed_patterns_are_found(html_text):
    assert embedded_urls(html_text)


@pytest.mark.parametrize(
    "html_text",
    [
        "<p>Xem https://x.example/a ngay</p>",
        '<p><a href="https://suachuacuasat.com/x/">https://suachuacuasat.com/x/</a> rồi</p>',
        "<p>ftp://x.example</p>",
    ],
)
def test_embed_patterns_not_found(html_text):
    assert embedded_urls(html_text) == ()


@pytest.mark.parametrize("mode", ["draft", "future", "publish"])
def test_url_alone_blocks_every_mode(mode):
    body = clean_ai_text("Xem video:\n\nhttps://www.youtube.com/watch?v=abc\n\n- https://x.vn/a")
    built = build(
        parts=[ArticlePart("", body)],
        images=[],
        links=[],
        required_ids=[],
        mode=mode,
        date_gmt="2026-11-03T01:00:00" if mode == "future" else "",
    )
    assert built.review.blocked
    assert built.review.embeds == ("https://www.youtube.com/watch?v=abc", "https://x.vn/a")


# ------------------------------------------------------------------ LC-T094-7: link, cờ


HOSTILE_LINKS = [
    "https://suachuacuasаt.com/sua-cua-keo-tphcm/",  # «а» Kirin
    "https://suachuacuasat.cоm/",  # «о» Kirin
    "https://suachuacuasat.com@evil.example/",
    "//evil.example/x",
    "/\\evil.example",
    "http://x.example:8080/",
    "https://xn--suachuacuast-79j.com/",
    "mailto:a@b.vn",
    f"{SITE}/sua-cua-keo-tphcm/",
]


def test_link_rows_list_every_href_with_flags():
    html_text = "".join(f'<p><a href="{h}">chữ {i}</a></p>' for i, h in enumerate(HOSTILE_LINKS))
    report = check_links(html_text, INDEX)
    rows = link_rows(html_text, report, SITE)
    assert [row.href for row in rows] == HOSTILE_LINKS
    assert [row.text for row in rows] == [f"chữ {i}" for i in range(len(HOSTILE_LINKS))]
    by_href = {row.href: row for row in rows}
    kirin = by_href[HOSTILE_LINKS[0]]
    assert kirin.ascii_host == "xn--suachuacuast-79j.com"
    assert FLAG_NON_ASCII in kirin.flags and FLAG_OTHER_SITE in kirin.flags
    assert by_href[HOSTILE_LINKS[1]].ascii_host.startswith("suachuacuasat.xn--")
    assert FLAG_AT in by_href[HOSTILE_LINKS[2]].flags
    assert FLAG_PROTOCOL_RELATIVE in by_href[HOSTILE_LINKS[3]].flags
    assert FLAG_BACKSLASH in by_href[HOSTILE_LINKS[4]].flags
    assert FLAG_PORT in by_href[HOSTILE_LINKS[5]].flags
    assert FLAG_PUNYCODE in by_href[HOSTILE_LINKS[6]].flags
    assert by_href["mailto:a@b.vn"].flags == ()
    own = by_href[HOSTILE_LINKS[-1]]
    assert own.flags == () and own.kind is LinkKind.INTERNAL and own.post_id == 10


def test_address_flags_for_bare_addresses():
    assert address_flags("www.suachuacuasat.com", SITE, bare=True) == (
        "www.suachuacuasat.com",
        "www.suachuacuasat.com",
        (),
    )
    host, ascii_host, flags = address_flags("suachuacuasаt.com", SITE, bare=True)
    assert ascii_host == "xn--suachuacuast-79j.com" and FLAG_NON_ASCII in flags
    assert address_flags("a/b", SITE) == ("", "", ())  # link tương đối: không có tên máy


def test_bare_addresses_in_text():
    html_text = (
        "<p>Gọi https://suachuacuasаt.com/km. Hoặc www.evil.example, email "
        "tho@suachuacuasat.com.</p><p>https://evil.example/x</p>"
    )
    found = bare_addresses(html_text, SITE)
    assert [(a.text, a.kind) for a in found] == [
        ("https://suachuacuasаt.com/km", "url"),
        ("www.evil.example", "www"),
        ("tho@suachuacuasat.com", "email"),
        ("https://evil.example/x", "url"),
    ]
    assert found[0].ascii_host == "xn--suachuacuast-79j.com" and FLAG_NON_ASCII in found[0].flags
    assert found[2].flags == ()


def test_review_lists_shortcodes_images_and_needs_escape():
    built = build(
        title="Bài [x]",
        parts=[
            ArticlePart("", clean_ai_text("Mở [code_snippet id=1] bài")),
            ArticlePart("Mục", clean_ai_text("Chữ [embed")),
            ArticlePart("Mục 2", clean_ai_text("tiếp]")),
        ],
        links=[],
        required_ids=[],
        images=[
            ArticleImage(section=0, sha256=SHA, alt="Ảnh [caption]", has_gps=True, featured=True)
        ],
    )
    review = built.review
    assert review.needs_escape is True
    assert ("Tiêu đề bài", "[x]") in review.shortcodes
    assert ("Mở bài", "[code_snippet id=1]") in review.shortcodes
    assert ("Alt ảnh ở Mở bài", "[caption]") in review.shortcodes
    assert any(where == "Nội dung, vắt qua nhiều mục" for where, _ in review.shortcodes)
    assert [(r.section, r.alt, r.has_gps, r.featured) for r in review.images] == [
        (0, "Ảnh [caption]", True, True)
    ]
    assert review.level is Level.WARN  # shortcode, GPS: cảnh báo, không chặn


def test_review_blocks_content_problems():
    built = build(
        title="",
        parts=[ArticlePart("", ""), ArticlePart("", "")],
        images=[ArticleImage(section=1, sha256=SHA, alt="")],
        links=[],
        required_ids=[],
        slug="Sai Slug",
    )
    messages = [p.message for p in built.review.problems if p.level is Level.BLOCK]
    assert "Bài chưa có tiêu đề." in messages
    assert "Bài chưa có nội dung." in messages
    assert "Mục thứ 2 chưa có tiêu đề." in messages
    assert any(m.startswith("Slug") for m in messages)
    assert any("chưa có alt" in m for m in messages)


def test_publish_without_seo_blocks_future_warns():
    seo = SeoFields("t", "d", "k", write=False)
    assert build(seo=seo, mode="publish").review.blocked
    future = build(seo=seo, mode="future", date_gmt="2026-11-03T01:00:00").review
    assert not future.blocked and future.level is Level.WARN
    assert build(seo=seo, mode="draft").review.level is Level.GOOD


# ------------------------------------------------------------------ LC-T094-8: mã băm


def test_digest_is_deterministic_and_canonical():
    assert build().digest == build().digest
    payload = {"b": 1, "a": "ữ", "c": [3, {"z": True, "y": None}]}
    expected = hashlib.sha256('{"a":"ữ","b":1,"c":[3,{"y":null,"z":true}]}'.encode()).hexdigest()
    assert digest_of(payload) == expected
    assert json.dumps(payload, sort_keys=True)  # bản chuẩn hóa dùng sort_keys


@pytest.mark.parametrize(
    "changes",
    [
        {"title": "Cửa kéo kêu rít: nguyên nhân và cách xử lý!"},
        {"parts": [*PARTS[:2], ArticlePart(PARTS[2].heading, PARTS[2].body + "!")]},
        {"parts": [PARTS[0], ArticlePart("Khi nào gọi thợ!", PARTS[1].body), PARTS[2]]},
        {"links": LINKS[:1]},
        {"excerpt": "Đoạn trích"},
        {"slug": "cua-keo-keu-rit-2"},
        {"categories": [4]},
        {"tags": [8, 7]},
        {"images": [ArticleImage(section=1, sha256="cd" * 32, alt="Thợ tra dầu ray cửa kéo")]},
        {"images": [ArticleImage(section=1, sha256=SHA, alt="Thợ tra dầu ray cửa kéo!")]},
        {
            "images": [
                ArticleImage(section=1, sha256=SHA, alt="Thợ tra dầu ray cửa kéo", caption="c")
            ]
        },
        {
            "images": [
                ArticleImage(section=1, sha256=SHA, alt="Thợ tra dầu ray cửa kéo", featured=True)
            ]
        },
        {"images": [ArticleImage(section=2, sha256=SHA, alt="Thợ tra dầu ray cửa kéo")]},
        {"images": []},
        {"seo": SeoFields("Cửa kéo kêu rít | Pro-Metal!", "Mô tả", "cửa kéo kêu rít", True)},
        {"seo": SeoFields("Cửa kéo kêu rít | Pro-Metal", "Mô tả!", "cửa kéo kêu rít", True)},
        {"seo": SeoFields("Cửa kéo kêu rít | Pro-Metal", "Mô tả", "cửa kéo", True)},
        {"seo": SeoFields("Cửa kéo kêu rít | Pro-Metal", "Mô tả", "cửa kéo kêu rít", False)},
        {"mode": "publish"},
        {"mode": "future", "date_gmt": "2026-11-03T01:00:00"},
    ],
)
def test_digest_changes_with_any_part(changes):
    assert build(**changes).digest != build().digest


def test_digest_changes_with_schedule_time():
    first = build(mode="future", date_gmt="2026-11-03T01:00:00")
    second = build(mode="future", date_gmt="2026-11-03T01:00:01")
    assert first.digest != second.digest
    assert first.matches(first.digest) and not first.matches(second.digest)
    assert not first.matches(None)


def test_digest_survives_lone_surrogate():
    built = build(seo=SeoFields("a\ud800", "", "", False))
    assert len(built.digest) == 64


# ------------------------------------------------------------------ đầu vào sai dạng


@pytest.mark.parametrize(
    "changes",
    [
        {"parts": "chữ"},
        {"parts": [("Mở", "bài")]},
        {"images": [ArticleImage(section=5, sha256=SHA, alt="x")]},
        {"images": [ArticleImage(section=1, sha256="xyz", alt="x")]},
        {
            "images": [
                ArticleImage(section=0, sha256=SHA, alt="x", featured=True),
                ArticleImage(section=1, sha256=SHA, alt="x", featured=True),
            ]
        },
        {
            "images": [
                ArticleImage(section=1, sha256=SHA, alt="x"),
                ArticleImage(section=1, sha256=SHA, alt="y"),
            ]
        },
        {"categories": [True]},
        {"tags": ["7"]},
        {"categories": "3"},
        {"required_ids": [0]},
        {"mode": "private"},
        {"mode": "future", "date_gmt": ""},
        {"mode": "future", "date_gmt": "2026-11-03 01:00:00"},
        {"mode": "publish", "date_gmt": "2026-11-03T01:00:00"},
        {"mode": "draft", "date_gmt": "2026-11-03T01:00:00"},
        {"seo": SeoFields("a", "b", "c", write=1)},
        {"title": None},
        {"index": None},
    ],
)
def test_bad_input_raises_fixed_message(changes):
    with pytest.raises(BuildError) as error:
        build(**changes)
    assert "Chưa gửi gì lên website" in str(error.value)


def test_no_parts_is_a_blocked_review_not_a_crash():
    built = build(parts=[], images=[], links=[], required_ids=[])
    assert built.sections == () and built.review.blocked


def test_dataclasses_are_frozen():
    built = build()
    with pytest.raises(dataclasses.FrozenInstanceError):
        built.sections = ()  # type: ignore[misc]
