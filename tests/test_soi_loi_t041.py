"""Soi Lỗi T-041 (rút gọn, **phần logic**): bước SEO thật, phần Thợ Máy làm trước giao diện.
Báo cáo: ``docs/team/reports/T-041-soi-loi.md``.

Bổ sung cho các test ``tests/test_t041_*.py`` của Thợ Máy, không lặp lại:

1. Thử độc lập các điều kiện phiếu giao (LC-T038 đk 1–2, LC-T036-1, SL-T036-10, LC-T040-1, nối
   ``[meta]``, LC-T039 đk 2a, 2b) với dữ liệu khác bộ test của Thợ Máy.
2. Trường SEO trong nháp: nháp khuôn 1, khuôn 2 (đúng dạng ``main`` lưu, có ảnh) mở được; khối SEO
   hỏng và ảnh hỏng bị bỏ riêng; không lưu địa chỉ link.
3. Hàm cho Họa Sĩ gọi như giao diện sẽ gọi: client WordPress thật nối site giả trả lỗi đủ kiểu,
   AI giả trả gợi ý độc; không ném lỗi lạ, câu báo tiếng Việt, không chép lời máy chủ.

Lỗi tìm thấy đánh ``xfail(strict=True)`` kèm mã ``SL-T041-n``: sửa xong test tự báo XPASS để gỡ
dấu. Không gọi AI, WordPress hay mạng thật (provider giả, ``tests/fake_wordpress.py``); thư mục
tạm, không cần ``.env``. Ký tự lạ viết bằng ``chr(0x…)`` cho dễ đọc.
"""

from __future__ import annotations

import json
import sqlite3
import unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
import requests
from fake_wordpress import BASE_URL, FakeWordPress, make_session

from seo_app.ai import AIError, AIRouter, TaskConfig
from seo_app.ai import registry as ai_registry
from seo_app.config import Settings
from seo_app.content import ContentWriter, Section
from seo_app.content.prompts import MetaSuggestions
from seo_app.content.rules import ContentRules, MetaRules, load_meta_rules
from seo_app.images.tags import SOURCE_REAL
from seo_app.onpage.links import Candidate, Candidates, apply_links
from seo_app.onpage.meta import (
    TITLE_LIMITS,
    accept_ai_title,
    check_slug_duplicates,
    check_title,
    has_keyword,
    mentions_price,
    normalize_meta,
    site_posts,
    siteseo_copy,
    with_brand,
)
from seo_app.onpage.schema import build_article_faq, find_faq
from seo_app.sanitize import escape_link_syntax, sanitize_html
from seo_app.storage import DraftPart, DraftSnapshot, DraftStore
from seo_app.storage.drafts import (
    MAX_META_VERSIONS,
    DraftImage,
    DraftLink,
    DraftMetaVersions,
    DraftSeo,
    new_draft_id,
)
from seo_app.storage.site_index import (
    MSG_NOT_CONNECTED,
    SiteIndex,
    SiteIndexStore,
    site_listing,
)
from seo_app.wordpress import PublishedItem, WordPressClient, WordPressError
from seo_app.wordpress import client as wp_client

SITE = "https://suachuacuasat.com"
KEYWORD = "cửa sắt bị xệ"
DESC = (
    "Cửa sắt bị xệ, cạ nền khi đóng mở thường do bản lề mòn. Xem cách tự kiểm tra bản lề, lúc nào"
    " chỉnh được và lúc nào nên gọi thợ hàn lại."
)
AVOID = load_meta_rules().avoid
TZ = ZoneInfo("Asia/Ho_Chi_Minh")
# Loại ký tự không được còn trong chữ meta (LC-T036-1) và câu hỏi/trả lời FAQ (LC-T038 đk 1).
_ODD = {"Cc", "Cf", "Cs", "Co", "Cn"}
ODD_CHARS = [
    chr(0x00),  # NUL (Cc)
    chr(0x1B),  # ESC (Cc)
    chr(0x7F),  # DEL (Cc)
    chr(0x9F),  # C1 (Cc)
    chr(0xD800),  # surrogate lẻ (Cs)
    chr(0xDFFF),  # surrogate lẻ (Cs)
    chr(0xE000),  # ký tự riêng (Co)
    chr(0x10FFFD),  # ký tự riêng vùng phụ (Co)
    chr(0x0378),  # chưa gán (Cn)
    chr(0xFFFE),  # không phải ký tự (Cn)
    chr(0x10FFFF),  # không phải ký tự (Cn)
]


def _title_of_length(length: int) -> str:
    base = "Cửa sắt bị xệ: nguyên nhân hay gặp và cách xử lý từng bước tại nhà"
    title = base[:length].rstrip()
    while len(title) < length:
        title += "a"
    assert len(normalize_meta(title)) == length
    return title


def _faq_parts(answer: str, question: str = "Cửa cuốn kêu to có sao không?") -> list[Section]:
    """Bài như trong trang Soạn bài: thân phần đã qua ``escape_link_syntax``."""
    body = escape_link_syntax(f"### {question}\n\n{answer}")
    return [
        Section(heading="Mở bài", body="Cửa cuốn kêu to thường do ray khô dầu."),
        Section(heading="Câu hỏi thường gặp", body=body),
    ]


def _answer_text(result) -> str:
    return json.loads(result.json_ld)["mainEntity"][0]["acceptedAnswer"]["text"]


# ============================================================ 1. điều kiện, thử độc lập


@pytest.mark.parametrize("odd", ODD_CHARS, ids=[f"U+{ord(c):04X}" for c in ODD_CHARS])
def test_lc_t036_1_meta_text_never_keeps_odd_chars(odd):
    """Mọi đường chữ meta đi ra (chuẩn hóa, kiểm ô, chép sang SiteSEO) không còn ký tự lạ nào và
    luôn ghi được ra UTF-8."""
    raw = f"Cửa sắt{odd} bị xệ: tự kiểm tra{odd} hay nên gọi thợ?"
    for text in (
        normalize_meta(raw),
        check_title(raw).value,
        siteseo_copy(raw, DESC + odd, "cua-sat-bi-xe").title or "",
        siteseo_copy(raw, DESC + odd, "cua-sat-bi-xe").description or "",
    ):
        assert not [c for c in text if unicodedata.category(c) in _ODD], repr(text)
        text.encode("utf-8")


@pytest.mark.parametrize("odd", ODD_CHARS, ids=[f"U+{ord(c):04X}" for c in ODD_CHARS])
@pytest.mark.parametrize("where", ["question", "answer"])
def test_lc_t038_1_odd_char_in_faq_is_blocked_without_echo(odd, where):
    question, answer = "Cửa cuốn kêu to có sao không?", "Thường do ray khô dầu."
    if where == "question":
        question = f"Cửa cuốn kêu{odd} to có sao không?"
    else:
        answer = f"Thường do ray{odd} khô dầu."
    result = build_article_faq(_faq_parts(answer, question), site_url=SITE)
    assert result.blocked and result.json_ld is None
    assert all(odd not in issue.message for issue in result.issues)


# Các dạng link Markdown lạ (CommonMark): địa chỉ không bao giờ vào JSON-LD (LC-T038 đk 2).
LINK_FORMS = {
    "inline": "Xem [hướng dẫn](javascript:alert(1)) nhé.",
    "dest-in-angle-brackets": "Xem [hướng dẫn](<javascript:alert(1)>) nhé.",
    "with-title": 'Xem [hướng dẫn](javascript:alert(1) "tiêu đề") nhé.',
    "nested-brackets": "Xem [a [b] c](javascript:alert(1)) nhé.",
    "dest-on-next-line": "Xem [hướng dẫn](\njavascript:alert(1)) nhé.",
    "reference-with-definition": "Xem [hướng dẫn][r] nhé.\n\n[r]: javascript:alert(1)",
    "image": "Ảnh ![bản lề gỉ](https://evil.example/a.png) đây.",
    "entity-colon": "Xem [hướng dẫn](javascript&#58;alert(1)) nhé.",
}


@pytest.mark.parametrize("answer", LINK_FORMS.values(), ids=LINK_FORMS.keys())
def test_lc_t038_2_link_forms_never_put_address_in_json_ld(answer):
    result = build_article_faq(_faq_parts(answer), site_url=SITE)
    assert not result.blocked, result.issues
    text = _answer_text(result)
    for leaked in ("javascript", "evil.example", "](", "**", "`", "&#58;"):
        assert leaked not in text, (leaked, text)


@pytest.mark.parametrize(
    "words", ["7 xu hướng", "vài XU HƯỚNG", "mấy xu  hướng", "2 xu\nhướng", "ba xu hướng mới"]
)
def test_sl_t036_10_xu_huong_is_not_price(words):
    assert not mentions_price(f"Cửa sắt {words} năm nay", KEYWORD)


@pytest.mark.parametrize("money", ["500 xu", "5 xu.", "vài xu", "200.000đ", "1tr5", "giá rẻ"])
def test_sl_t036_10_other_money_words_still_price(money):
    assert mentions_price(f"Cửa sắt bị xệ {money}", KEYWORD)


@pytest.mark.parametrize(
    ("keyword", "text", "price"),
    [
        ("giá sửa cửa sắt", "Giá sửa cửa sắt phụ thuộc vào những gì?", False),
        ("giá sửa cửa sắt", "Giá sửa cửa sắt rẻ: phụ thuộc vào gì?", True),  # vắt qua mép sau
        ("sửa cửa cuốn", "Báo giá tốt sửa cửa cuốn tại nhà", True),  # ngoài từ khóa
        ("làm cổng sắt báo giá", "Làm cổng sắt báo giá tốt nhất mùa này", True),
        ("sửa cửa quận 1", "Sửa cửa quận 1 triệu đồng có đắt không?", True),
        ("cửa cuốn giá rẻ", "Cửa cuốn giá rẻ: chọn loại nào bền lâu", False),  # trọn trong từ khóa
        ("cửa cuốn giá rẻ", "Cửa cuốn giá rẻ: báo giá tốt cho nhà phố", True),  # ngoài từ khóa
    ],
)
def test_lc_t040_1_price_inside_keyword_only(keyword, text, price):
    assert mentions_price(text, keyword) is price


def test_meta_section_is_live_avoid_and_keyword_exception(monkeypatch):
    """``[meta]`` nối thật: cụm nên tránh trong gợi ý AI bị bỏ, trừ khi nằm trọn trong từ khóa."""
    titles = [
        "Cửa sắt bị xệ: thợ uy tín chỉ cách tự chỉnh bản lề",  # «uy tín» ngoài từ khóa: bỏ
        "Cửa sắt bị xệ: tự kiểm tra hay nên gọi thợ?",
    ]
    writer, _ = _writer(monkeypatch, titles, [DESC])
    assert writer.meta(KEYWORD, "Bài", _ARTICLE).titles == [titles[1] + " | Pro-Metal"]
    keyword = "sửa cửa sắt uy tín"
    titles = ["Sửa cửa sắt uy tín: 5 lỗi hay gặp và cách tự xử lý"]
    desc = DESC.replace("Cửa sắt bị xệ,", "Sửa cửa sắt uy tín: cửa sắt bị xệ,")
    writer, _ = _writer(monkeypatch, titles, [desc[:155]])
    assert writer.meta(keyword, "Bài", _ARTICLE).titles == titles


_ARTICLE = [Section(heading="Mở bài", body="Cửa sắt bị xệ thường do bản lề mòn.")]
_TASKS = ("research", "outline", "write", "rewrite", "review", "meta", "links")


class _FakeAI:
    def __init__(self, payload):
        self.payload = payload
        self.prompts: list[str] = []

    def generate(self, task, *, system, prompt, schema):
        self.prompts.append(prompt)
        return schema.model_validate(self.payload)


def _writer(monkeypatch, titles=(), descriptions=(), *, links=None, meta_rules=None, **task):
    payload = {"links": links} if links is not None else {
        "titles": list(titles), "descriptions": list(descriptions)
    }  # fmt: skip
    fake = _FakeAI(payload)
    monkeypatch.setattr(ai_registry, "make_provider", lambda name, settings: fake)
    tasks = {n: TaskConfig(name=n, provider="anthropic", model="claude-opus-5-5") for n in _TASKS}
    tasks["links"] = TaskConfig(name="links", provider="anthropic", model="claude-opus-5-5", **task)
    rules = ContentRules(business_profile="", address="", tone="", banned=(), checklist=())
    return ContentWriter(AIRouter(tasks, Settings()), rules, meta_rules), fake


_STUCK = PublishedItem(
    id=11, type="post", slug="thay-ban-le", link=f"{SITE}/thay-ban-le/",
    title="Thay bản lề cửa sắt bị mòn",
)  # fmt: skip
_PARTS = [
    Section(heading="Mở bài", body="Cửa sắt bị xệ thường do bản lề mòn."),
    Section(heading="Cách xử lý", body="Thay bản lề cửa sắt bị mòn là cách hay gặp nhất."),
]


def test_lc_t039_2a_ai_answer_only_ids_and_checked_anchors(monkeypatch):
    """Câu trả lời AI có trường thừa (``href``, ``url``), ID lạ, cụm từ có dấu Markdown/HTML: chỉ
    gợi ý đúng khuôn, có nguyên văn trong bài được nhận; câu báo không chép chữ AI; lời dặn không
    có địa chỉ hay slug của bài đích."""
    links = [
        {"post_id": 11, "section": 1, "anchor": "Thay bản lề cửa sắt bị mòn", "href": "https://x"},
        {"post_id": 999, "section": 1, "anchor": "bản lề", "url": "javascript:alert(1)"},
        {"post_id": 11, "section": 0, "anchor": "[bản lề](javascript:alert(1))"},
        {"post_id": 11, "section": 0, "anchor": "<b>bản lề mòn</b>"},
    ]
    writer, fake = _writer(monkeypatch, links=links)
    review = writer.internal_links("Bài", _PARTS, Candidates((Candidate(_STUCK),)))
    assert [(link.post_id, link.anchor) for link in review.links] == [
        (11, "Thay bản lề cửa sắt bị mòn")
    ]
    assert len(review.rejected) == 3
    for message in review.rejected:
        assert "javascript" not in message and "<b>" not in message
    prompt = fake.prompts[-1]
    assert "- ID 11: Thay bản lề cửa sắt bị mòn" in prompt
    assert _STUCK.link not in prompt and _STUCK.slug not in prompt and "http" not in prompt


def test_lc_t039_2a_web_search_refused_before_any_call(monkeypatch):
    writer, fake = _writer(monkeypatch, links=[], web_search=True)
    with pytest.raises(AIError, match="web_search"):
        writer.internal_links("Bài", _PARTS, Candidates((Candidate(_STUCK),)))
    assert fake.prompts == []


def test_lc_t039_2b_saved_link_has_only_link_fields_and_reapplies(tmp_path):
    """Nháp lưu đúng 4 trường (không địa chỉ); đọc lại dựng ``InternalLink`` rồi chèn qua
    ``apply_links`` với danh sách bài lúc đó (địa chỉ lấy từ danh sách, không từ nháp)."""
    store = DraftStore(path=tmp_path / "data" / "drafts.sqlite")
    link = DraftLink(section=1, anchor="Thay bản lề cửa sắt bị mòn", post_id=11)
    saved = store.save(_snapshot(seo=DraftSeo(links=[link])))
    raw = _read_json(store, saved.id)
    assert [set(item) for item in raw["seo"]["links"]] == [{"section", "anchor", "post_id", "use"}]
    loaded = store.load(saved.id)
    index = SiteIndex(site=SITE, fetched_at=datetime(2026, 10, 26, tzinfo=TZ), items=(_STUCK,))
    html = (  # mở bài không có <h2> (phần 0), mỗi phần sau đúng một <h2>
        "<p>Cửa sắt bị xệ thường do bản lề mòn.</p>"
        "<h2>Cách xử lý</h2><p>Thay bản lề cửa sắt bị mòn là cách hay gặp nhất.</p>"
    )
    out = sanitize_html(
        apply_links(sanitize_html(html), [d.to_link() for d in loaded.seo.links if d.use], index)
    )
    assert f'<a href="{_STUCK.link}">Thay bản lề cửa sắt bị mòn</a>' in out


# ============================================================ 2. nháp


def _snapshot(seo: DraftSeo | None = None, image: DraftImage | None = None) -> DraftSnapshot:
    parts = [
        DraftPart(heading="Mở bài", versions=["Cửa sắt bị xệ do bản lề mòn."]),
        DraftPart(heading="Thay bản lề", versions=["Thay bản lề mòn."], chosen_image=image),
    ]
    data = {"keyword": KEYWORD, "article_title": "Bài", "parts": parts}
    if seo is not None:
        data["seo"] = seo
    return DraftSnapshot(**data)


def _image() -> DraftImage:
    return DraftImage(
        source=SOURCE_REAL,
        root_index=0,
        rel_path="CT012 - Cổng inox - Tân Phú/truoc/IMG_0001.jpg",
        category="Cổng inox",
        alt="Bản lề cổng inox bị gỉ trước khi sửa",
        alt_approved=True,
        caption="Bản lề gỉ sau 3 năm mưa nắng",
    )


def _full_seo() -> DraftSeo:
    return DraftSeo(
        title=DraftMetaVersions(versions=["Bản AI", "Cửa sắt bị xệ: tự kiểm tra hay gọi thợ?"],
                                current=1),
        description=DraftMetaVersions(versions=[DESC]),
        slug="cua-sat-bi-xe",
        links=[DraftLink(section=1, anchor="Thay bản lề mòn", post_id=11)],
        use_faq=True,
    )  # fmt: skip


def _read_json(store: DraftStore, draft_id: str) -> dict:
    with sqlite3.connect(store.path) as conn:
        (data,) = conn.execute("SELECT data FROM drafts WHERE id = ?", (draft_id,)).fetchone()
    conn.close()
    return json.loads(data)


def _write_json(store: DraftStore, draft_id: str, data: dict) -> None:
    text = json.dumps(data, ensure_ascii=False)
    with sqlite3.connect(store.path) as conn:
        conn.execute("UPDATE drafts SET data = ? WHERE id = ?", (text, draft_id))
    conn.close()


@pytest.fixture
def store(tmp_path) -> DraftStore:
    return DraftStore(path=tmp_path / "data" / "drafts.sqlite")


def test_v2_draft_as_saved_by_main_opens_with_image_and_empty_seo(store):
    """Nháp khuôn 2 đúng như ``main`` (trước T-041) lưu, có ảnh đã chọn: chỉ khác là không có khóa
    ``seo``. Mở được, ảnh giữ nguyên, không ảnh nào bị tính là hỏng, phần SEO trống."""
    saved = store.save(_snapshot(image=_image()))
    data = _read_json(store, saved.id)
    del data["seo"]
    assert data["schema_version"] == 2
    _write_json(store, saved.id, data)
    loaded = store.load(saved.id)
    assert loaded.seo == DraftSeo() and loaded.dropped_images == 0
    assert loaded.parts[1].chosen_image == _image()
    texts = [part.text for part in loaded.parts]
    assert texts == ["Cửa sắt bị xệ do bản lề mòn.", "Thay bản lề mòn."]


def test_v1_draft_opens_with_empty_seo(store):
    draft_id = new_draft_id()
    store.save(DraftSnapshot(id=draft_id, keyword="tạm"))
    _write_json(store, draft_id, {
        "schema_version": 1, "id": draft_id, "saved_at": "2026-10-19T09:15:00+07:00", "step": 2,
        "keyword": "sửa cổng inox", "material": {}, "research": None, "research_keyword": "",
        "outline_title": "", "outline": [], "article_title": "Sửa cổng inox",
        "parts": [{"heading": "Mở bài", "versions": ["Cổng kêu."], "current": 0, "image": ""}],
        "review": None, "auto_fixed": 0, "ignored_flags": [],
    })  # fmt: skip
    loaded = store.load(draft_id)
    assert loaded.seo == DraftSeo() and loaded.parts[0].text == "Cổng kêu."


def test_broken_seo_and_broken_image_are_dropped_separately(store):
    """Khối SEO sửa tay hỏng và ảnh hỏng trong cùng nháp: mỗi thứ bỏ riêng, chữ bài giữ nguyên,
    chỉ ảnh được đếm là hỏng (SEO hỏng bỏ lặng lẽ, như Thợ Máy ghi ở mục Rủi ro)."""
    saved = store.save(_snapshot(seo=_full_seo(), image=_image()))
    data = _read_json(store, saved.id)
    data["seo"]["title"]["current"] = -1
    data["parts"][1]["chosen_image"]["rel_path"] = "../ngoai/thu-muc.jpg"
    _write_json(store, saved.id, data)
    loaded = store.load(saved.id)
    assert loaded.seo == DraftSeo()
    assert loaded.dropped_images == 1 and loaded.parts[1].chosen_image is None
    assert loaded.parts[1].text == "Thay bản lề mòn."


def test_seo_round_trip_keeps_choices_and_no_address(store):
    saved = store.save(_snapshot(seo=_full_seo()))
    loaded = store.load(saved.id)
    assert loaded.seo == _full_seo()
    raw = json.dumps(_read_json(store, saved.id)["seo"], ensure_ascii=False)
    assert "http" not in raw and "href" not in raw and 'link"' not in raw


# ============================================================ 3. hàm cho Họa Sĩ


MAT_KHAU_GIA = "MAT-KHAU-GIA-T041"
SERVER_TEXT = "<script>alert(1)</script> [bấm](javascript:alert(1)) https://evil.example"
WP_FAILURES = {
    "401": lambda r: (401, {"code": "rest_forbidden", "message": SERVER_TEXT}, {}),
    "403-html": lambda r: (403, b"<html>" + SERVER_TEXT.encode() + b"</html>", {}),
    "500": lambda r: (500, {"code": "x", "message": SERVER_TEXT}, {}),
    "html-200": lambda r: (200, b"<html>" + SERVER_TEXT.encode() + b"</html>", {}),
    "json-not-list": lambda r: {"message": SERVER_TEXT},
    "connection": lambda r: requests.ConnectionError(SERVER_TEXT),
    "timeout": lambda r: requests.Timeout(SERVER_TEXT),
    "ssl": lambda r: requests.exceptions.SSLError(SERVER_TEXT),
}


@pytest.mark.parametrize("failure", WP_FAILURES.values(), ids=WP_FAILURES.keys())
@pytest.mark.parametrize("refresh", [False, True])
def test_site_listing_turns_every_wordpress_failure_into_a_notice(tmp_path, failure, refresh):
    fake = FakeWordPress()
    fake.on("GET", "/wp-json/wp/v2/posts", failure)
    fake.on("GET", "/wp-json/wp/v2/pages", lambda r: [])
    client = WordPressClient(BASE_URL, "lam", MAT_KHAU_GIA, session=make_session(fake))
    store = SiteIndexStore(path=tmp_path / "data" / "site_index.sqlite")
    listing = site_listing(store, client, refresh=refresh)
    assert listing.index is None
    assert listing.notice.startswith("Chưa tải được danh sách bài đã đăng. ")
    for leaked in (MAT_KHAU_GIA, "<script", "javascript", "evil.example", BASE_URL):
        assert leaked not in listing.notice


def test_not_connected_rest_of_seo_step_still_works(tmp_path):
    store = SiteIndexStore(path=tmp_path / "data" / "site_index.sqlite")
    listing = site_listing(store, None)
    assert listing == type(listing)(None, MSG_NOT_CONNECTED)
    posts = site_posts(listing.index)
    assert posts == [] and check_slug_duplicates("cua-sat-bi-xe", posts).level == "nen"
    copy = siteseo_copy("Cửa sắt bị xệ: tự kiểm tra hay nên gọi thợ?", DESC, "cua-sat-bi-xe")
    assert copy.title == "Cửa sắt bị xệ: tự kiểm tra hay nên gọi thợ? | Pro-Metal"
    # Chưa kết nối thì không đụng tới file lưu tạm danh sách bài.
    assert not tmp_path.joinpath("data", "site_index.sqlite").exists()


def test_writer_meta_drops_html_and_reports_in_vietnamese(monkeypatch):
    bad = ["Cửa sắt bị xệ <img src=x onerror=alert(1)> nguyên nhân", "Cửa sắt bị xệ %%sitename%%"]
    writer, _ = _writer(monkeypatch, bad, [DESC])
    with pytest.raises(AIError, match="Các meta title AI gợi ý đều không đạt"):
        writer.meta(KEYWORD, "Bài", _ARTICLE)
    with pytest.raises(AIError, match="Chưa có từ khóa chính"):
        writer.meta("  ", "Bài", _ARTICLE)


# ============================================================ 4. lỗi tìm thấy (xfail)

# Chữ SEO mà client WordPress (T-060, T-061) từ chối ghi lên SiteSEO.
SEO_TEXT_CLIENT_REFUSES = [
    "Cửa sắt bị xệ [code_snippet_source id=3] cách sửa",
    "Cửa sắt bị xệ: [gallery] nguyên nhân và cách chỉnh",
    "Cửa sắt bị xệ [<>code_snippet id=1] nguyên nhân sửa",
    "Cửa sắt bị xệ <1> nguyên nhân và cách chỉnh lại cửa",
    "Cửa sắt bị xệ &#37 nguyên nhân và cách chỉnh lại cửa",
]


@pytest.mark.parametrize("title", SEO_TEXT_CLIENT_REFUSES)
def test_client_refuses_these_seo_titles(title):
    with pytest.raises(WordPressError):
        wp_client._seo_text("Tiêu đề SEO", with_brand(title), 300)


@pytest.mark.parametrize("title", SEO_TEXT_CLIENT_REFUSES)
def test_sl_t041_1_copy_and_ai_filter_refuse_what_client_refuses(title):
    assert siteseo_copy(title, DESC, "cua-sat-bi-xe").title is None
    assert accept_ai_title(title, KEYWORD) is None


@pytest.mark.parametrize("length", [38, 43, 48])
def test_sl_t041_2_check_title_judges_the_title_that_will_be_sent(length):
    title = _title_of_length(length)  # như ô sửa: strip_brand, chưa gắn đuôi
    final = with_brand(title, None)
    assert TITLE_LIMITS.good_min <= len(final) <= TITLE_LIMITS.good_max
    assert "hơi ngắn" not in check_title(final, None).messages[0]
    assert "hơi ngắn" not in check_title(title, None).messages[0]


KEYWORD_WORDS = [
    ("sửa cửa uy tín hcm", "Sửa cửa uy tín HCM: 5 lỗi hay gặp và cách xử lý tại nhà"),
    ("cửa cuốn giá rẻ", "Cửa cuốn giá rẻ: nên chọn loại nào để dùng bền lâu"),
    ("sửa cửa cuốn chuyên nghiệp", "Sửa cửa cuốn chuyên nghiệp: 6 lỗi hay gặp, cách tự xử lý"),
]


@pytest.mark.parametrize(("keyword", "title"), KEYWORD_WORDS)
def test_keyword_with_accents_protects_its_words(keyword, title):
    assert accept_ai_title(title, keyword, (), None, AVOID) is not None


@pytest.mark.parametrize(("keyword", "title"), KEYWORD_WORDS)
def test_sl_t041_3_keyword_without_accents_protects_its_words(keyword, title):
    plain = unicodedata.normalize("NFC", keyword)
    plain = "".join(c for c in unicodedata.normalize("NFD", plain) if not unicodedata.combining(c))
    plain = plain.replace("đ", "d")
    assert has_keyword(title, plain)
    assert accept_ai_title(title, plain, (), None, AVOID) is not None


def test_sl_t041_4_version_in_use_is_never_trimmed():
    versions = ["Bản tôi tự viết"] + [f"Gợi ý AI {i}" for i in range(MAX_META_VERSIONS)]
    kept = DraftMetaVersions(versions=versions, current=0)
    assert len(kept.versions) == MAX_META_VERSIONS
    assert kept.text == "Bản tôi tự viết"


def test_sl_t041_5_subheading_without_question_mark_is_not_a_question():
    body = (
        "### Lưu ý trước khi đọc\n\nCác câu dưới đây là tình huống hay gặp.\n\n"
        "### Cửa cuốn kêu to có sao không?\n\nThường do ray khô dầu."
    )
    parts = [Section(heading="Mở bài", body="x"), Section(heading="Câu hỏi thường gặp", body=body)]
    assert [question for question, _ in find_faq(parts)] == ["Cửa cuốn kêu to có sao không?"]


@pytest.mark.parametrize(
    "answer", ["Gõ `[x](javascript:alert(1))` vào ô.", "Gõ ``[x](javascript:alert(1))`` vào ô."]
)
def test_sl_t041_6_code_span_never_carries_link_address(answer):
    result = build_article_faq(_faq_parts(answer), site_url=SITE)
    assert result.blocked or "javascript" not in result.json_ld


@pytest.mark.parametrize("suffix", ["", " | Cơ khí Pro-Metal HCM"])
def test_sl_t041_7_meta_prompt_follows_configured_suffix(monkeypatch, suffix):
    titles = ["Cửa sắt bị xệ: tự kiểm tra hay nên gọi thợ?"]
    writer, fake = _writer(monkeypatch, titles, [DESC], meta_rules=MetaRules(brand_suffix=suffix))
    writer.meta(KEYWORD, "Bài", _ARTICLE)
    assert "40-48" not in fake.prompts[-1]


def test_meta_suggestions_model_is_what_ai_returns():
    """Khuôn AI trả về cho meta không đổi ở T-041 (Họa Sĩ dựa vào đó)."""
    assert set(MetaSuggestions.model_fields) == {"titles", "descriptions"}
