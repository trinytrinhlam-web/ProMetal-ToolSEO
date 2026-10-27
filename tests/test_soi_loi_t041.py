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
import test_app_images as ui
import test_t041_seo_ui as seo_ui
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
    Level,
    accept_ai_title,
    check_description,
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
from seo_app.text import escape_markdown
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


# ======================================================= 5. giao diện và lượt 3 (Soi Lỗi lượt 2)
#
# Trang Soạn bài thật (``AppTest``), AI giả, WordPress giả của ``tests/test_t041_seo_ui.py`` (Họa
# Sĩ); file cache danh sách bài, kho nháp trong thư mục tạm.

env = ui.env  # mật khẩu thử, không có khóa AI thật (dùng chung với test giao diện)
previews = ui.previews
site_cache = seo_ui.site_cache
seo_ai = seo_ui.seo_ai
wordpress = seo_ui.wordpress
ESC, PRIVATE = chr(0x1B), chr(0xE000)


def _saved_and_edited(snap: DraftSnapshot, change) -> str:
    """Lưu ``snap`` vào kho nháp của trang rồi sửa tay JSON bằng ``change(obj)``."""
    store = ui.store()
    store.save(snap)
    obj = _read_json(store, snap.id)
    change(obj)
    _write_json(store, snap.id, obj)
    return snap.id


def _open_seo_step(project_root, draft_id: str):
    """Phiên mới: mở nháp ``draft_id`` ở trang Soạn bài rồi sang bước SEO."""
    at = ui.pages.open_page(project_root, "write.py")
    ui.run_ok(ui.button(at, "Mở", key=f"open-{draft_id}").click().run())
    at.session_state["step"] = 3
    return ui.run_ok(at.run())


def _captions(at) -> list[str]:
    return [c.value for c in at.caption]


def _seo_runs(site) -> list[dict]:
    return [json.loads(r.body)["input"] for r in site.fake.requests if ui.path_of(r) == seo_ui.RUN]


def _suggest_then_publish_with_seo(at):
    """AI gợi ý meta ở bước SEO, sang bước Xuất bản, bật «Ghi SEO lên website»."""
    ui.run_ok(ui.button(at, "✨ AI gợi ý tiêu đề và mô tả SEO").click().run())
    ui.to_publish(at)
    return ui.run_ok(at.toggle(key="seo_write").set_value(True).run())


@pytest.mark.parametrize("version", [1, 2])
def test_old_drafts_open_and_seo_step_starts_empty(project_root, seo_ai, version):
    """Nháp lưu trước T-041 (khuôn 1 như T-016/T-021, khuôn 2 như ``main`` có ảnh) mở được ở trang
    thật: bước SEO trống, slug gợi ý từ từ khóa, AI gợi ý được, không lỗi."""

    def before_t041(obj):
        del obj["seo"]
        if version == 1:
            obj["schema_version"] = 1
            for part in obj["parts"]:
                part.pop("chosen_image", None)

    at = _open_seo_step(project_root, _saved_and_edited(ui.article(), before_t041))
    assert at.session_state["seo_slug"] == "sua-cong-inox"
    assert sum(b.startswith(":red-badge[Chặn · 0 ký tự") for b in seo_ui.badges(at)) == 2
    ui.run_ok(ui.button(at, "✨ AI gợi ý tiêu đề và mô tả SEO").click().run())
    assert at.session_state["seo_title"] == seo_ui.TITLES[0]
    assert not at.exception and not at.error


ABSURD_TITLES = [
    "<script>alert(1)</script>",
    "x" * 500,
    "[gallery ids=1] Sửa cổng inox",
    f"Sửa cổng inox{ESC} tại nhà",
    "%%sitename%%",
]


def test_absurd_hand_edited_seo_block_keeps_page_working(project_root, seo_ai, wordpress):
    """Khối SEO sửa tay vô lý (thẻ, shortcode, ``%%``, ký tự điều khiển, chữ 500 ký tự, slug có
    «/..», liên kết tới bài không có, một liên kết sai khuôn, «Dùng schema» khi bài không có Hỏi
    đáp): trang vẫn chạy, mọi ô sai là «Chặn» và không chép được, chữ thô không thành HTML, liên kết
    sai khuôn bị bỏ riêng; bật «Ghi SEO» rồi gửi nháp thì chỉ từ khóa chính được ghi."""

    def absurd(obj):
        obj["seo"] = {
            "title": {"versions": ABSURD_TITLES, "current": 3},
            "description": {"versions": ["<b>Mô tả</b> " * 40], "current": 0},
            "slug": "Cửa Sắt/../../etc",
            "links": [
                {"section": 9, "anchor": "không có trong bài", "post_id": 424242, "use": True},
                {"section": 0, "anchor": "x y", "post_id": 1, "use": "có"},  # sai khuôn: bỏ riêng
            ],
            "use_faq": True,
        }

    at = _open_seo_step(project_root, _saved_and_edited(ui.article(), absurd))
    assert not at.exception and not at.error
    assert at.session_state["seo_title"] == ABSURD_TITLES[3]
    assert sum(b.startswith(":red-badge[Chặn") for b in seo_ui.badges(at)) == 3
    for label in ("Tiêu đề SEO", "Mô tả SEO", "Đường dẫn (slug)"):
        assert any(c.startswith(f"{label}: chưa chép được.") for c in _captions(at)), label
    assert not [c for c in at.code if c.language != "json"]  # không khung chép nào
    for block in seo_ui.html_blocks(at):
        assert "<script" not in block and "<b>" not in block
    (table,) = at.dataframe
    assert table.value.to_dict("records") == [
        {"Dùng": True, "Cụm từ trong bài": "không có trong bài", "Trỏ tới bài": "bài #424242"}
    ]
    assert not any(box.key == "seo_use_faq" for box in at.checkbox)
    ui.to_publish(at)
    ui.run_ok(at.toggle(key="seo_write").set_value(True).run())
    ui.send(at)
    assert _seo_runs(wordpress) == [{"postId": seo_ui.POST_ID, "focus_keyphrase": seo_ui.KEYWORD}]
    sent = " ".join(str(r.body) for r in wordpress.fake.requests)
    assert "424242" not in sent and "<script" not in sent and "gallery" not in sent


def test_without_ai_key_meta_is_typed_checked_and_copied(project_root):
    """Chưa có khóa AI: mọi nút AI ở bước SEO mờ, vẫn tự gõ được; tiêu đề gõ tay được đếm cả đuôi
    thương hiệu và hiện ở khung «Chép sang SiteSEO»."""
    at = seo_ui.to_seo(project_root)  # không có ``seo_ai``: môi trường thử không có khóa AI
    keys = ("seo-ai-both", "seo-ai-title", "seo-ai-description")
    ai_buttons = [b for b in at.button if b.key in keys]
    assert len(ai_buttons) == 3 and all(b.disabled for b in ai_buttons)
    title = "Sửa cổng inox tại Tân Phú: thay bản lề gỉ"
    ui.run_ok(at.text_input(key="seo_title").input(title).run())
    assert with_brand(title) in [c.value for c in at.code]
    assert any(escape_markdown("(tính cả đuôi thương hiệu)") in c for c in _captions(at))
    assert not at.exception


@pytest.mark.parametrize(
    "space",
    ["\t", "\n", "\r\n", chr(0x0B), chr(0x0C), chr(0x1C), chr(0x85), chr(0xA0), chr(0x2028),
     chr(0x3000)],
    ids=["tab", "LF", "CRLF", "VT", "FF", "FS", "NEL", "NBSP", "LS", "IDSP"],
)  # fmt: skip
def test_whitespace_controls_are_folded_not_blocked(space):
    """Tab, xuống dòng và các khoảng trắng khác (kể cả loại điều khiển) chỉ gộp thành dấu cách ở
    mọi đường: ô kiểm, khung chép, client WordPress; không bị Chặn."""
    title = f"Cửa sắt bị xệ:{space}tự kiểm tra hay nên gọi thợ?"
    check = check_title(title)
    assert check.level is not Level.BLOCK
    assert check.value == with_brand("Cửa sắt bị xệ: tự kiểm tra hay nên gọi thợ?")
    assert siteseo_copy(title, DESC, "cua-sat-bi-xe").title == check.value
    assert wp_client._seo_text("Tiêu đề SEO", title, 300) == normalize_meta(title)


@pytest.mark.parametrize(
    "text",
    [
        unicodedata.normalize("NFD", DESC),
        DESC + " " + chr(0x2B50),
        DESC + " " + chr(0x2764) + chr(0xFE0F),
    ],
    ids=["tieng-viet-NFD", "emoji-cu", "emoji-co-VS16"],
)
def test_vietnamese_and_known_emoji_are_not_blocked(text):
    assert check_description(text).level is not Level.BLOCK
    assert siteseo_copy("Cửa sắt bị xệ: tự kiểm tra hay nên gọi thợ?", text, "a-b").description


@pytest.mark.parametrize(
    "invisible", [chr(0x200B), chr(0xFEFF), chr(0xAD)], ids=["ZWSP", "BOM", "SHY"]
)
def test_invisible_format_chars_are_dropped_the_same_way_everywhere(invisible):
    """Ký tự định dạng vô hình (Cf: dấu cách rộng 0, BOM, gạch nối mềm) không bị Chặn mà bị bỏ, như
    thiết kế T-036/T-042; chữ khung chép, chữ client ghi và chữ người dùng nhìn thấy là một."""
    title = f"Cửa sắt bị xệ: tự{invisible} kiểm tra hay nên gọi thợ?"
    copied = siteseo_copy(title, DESC, "cua-sat-bi-xe").title
    assert copied == with_brand("Cửa sắt bị xệ: tự kiểm tra hay nên gọi thợ?")
    assert wp_client._seo_text("Tiêu đề SEO", copied, 300) == copied


NEW_EMOJI = chr(0x1FAE9)  # «face with bags under eyes», Unicode 16.0 (2024)
python_without_new_emoji = pytest.mark.skipif(
    unicodedata.category(NEW_EMOJI) != "Cn", reason="Python này đã biết emoji Unicode 16"
)


@python_without_new_emoji
@pytest.mark.xfail(
    strict=True,
    reason="SL-T041-8: emoji mới hơn bảng Unicode của Python 3.12 (15.0) là ký tự «chưa gán» (Cn): "
    "tiêu đề, mô tả có emoji Unicode 16 bị Chặn với câu «ký tự điều khiển hoặc ký tự lạ (không "
    "nhìn thấy…)», gợi ý AI có nó bị bỏ, dù client WordPress ghi được.",
)
def test_sl_t041_8_new_emoji_is_not_blocked():
    title = f"Cửa sắt bị xệ {NEW_EMOJI} tự kiểm tra hay nên gọi thợ?"
    assert not wp_client_problem(title)  # client WordPress ghi được chữ này
    assert check_title(title).level is not Level.BLOCK
    assert check_description(f"{DESC} {NEW_EMOJI}").level is not Level.BLOCK


def wp_client_problem(text: str) -> str:
    try:
        wp_client._seo_text("Tiêu đề SEO", text, 300)
    except WordPressError as exc:
        return str(exc)
    return ""


@pytest.mark.xfail(
    strict=True,
    reason="SL-T041-9: từ khóa chính đi thẳng vào client, không qua bộ kiểm meta: có ký tự điều "
    "khiển thì client từ chối cả lệnh ghi SEO (mất cả tiêu đề, mô tả hợp lệ); có ký tự riêng (Co) "
    "thì bị lặng lẽ bỏ ký tự rồi ghi.",
)
@pytest.mark.parametrize("odd", [ESC, PRIVATE], ids=["ESC", "U+E000"])
def test_sl_t041_9_bad_keyword_is_skipped_alone(project_root, seo_ai, wordpress, odd):
    snap = ui.article(keyword=f"sửa cổng{odd} inox")
    at = _suggest_then_publish_with_seo(seo_ui.to_seo(project_root, snap))
    ui.send(at)
    (payload,) = _seo_runs(wordpress)
    assert payload["title"] == with_brand(seo_ui.TITLES[0])
    assert payload["description"] == seo_ui.DESCRIPTION
    assert "focus_keyphrase" not in payload  # không ghi từ khóa hỏng, không lặng lẽ sửa
    assert not at.exception and not at.error


@pytest.mark.xfail(
    strict=True,
    reason="SL-T041-9: bật «Ghi SEO lên website» không báo trước rằng từ khóa chính có ký tự lạ "
    "sẽ không ghi được (bước Xuất bản chỉ báo trước cho tiêu đề, mô tả).",
)
def test_sl_t041_9_bad_keyword_is_warned_before_sending(project_root, seo_ai, wordpress):
    at = _suggest_then_publish_with_seo(
        seo_ui.to_seo(project_root, ui.article(keyword=f"sửa cổng{ESC} inox"))
    )
    assert any("Từ khóa chính" in c and "ghi" in c for c in _captions(at))


def test_seo_choices_do_not_leak_into_the_next_draft(project_root, seo_ai):
    """Mở nháp khác trong cùng phiên: các bản meta, slug, công tắc ghi SEO của nháp trước bị xóa
    (khóa ``seo_*`` và bản sao ``_kept``), nháp sau bắt đầu trống."""
    at = seo_ui.to_seo(project_root)
    ui.run_ok(ui.button(at, "✨ AI gợi ý tiêu đề và mô tả SEO").click().run())
    ui.run_ok(at.text_input(key="seo_slug").input("cong-inox-nhap-a").run())
    ui.to_publish(at)
    ui.run_ok(at.toggle(key="seo_write").set_value(True).run())
    other = ui.article()
    ui.store().save(other)
    at.session_state["step"] = 0
    ui.run_ok(at.run())
    ui.run_ok(ui.button(at, "Mở", key=f"open-{other.id}").click().run())
    at.session_state["step"] = 3
    ui.run_ok(at.run())
    assert at.session_state["seo_slug"] == "sua-cong-inox"
    assert at.session_state["seo_title"] == "" and at.session_state["seo_description"] == ""
    ui.to_publish(at)
    assert at.toggle(key="seo_write").value is False


DUPLICATE_OF_FIRST_TITLE = seo_ui.published(13, "Bài cũ", "bai-cu", meta_title=seo_ui.TITLES[0])


@pytest.mark.xfail(
    strict=True,
    reason="SL-T041-10: phiên mới mở nháp ở bước Xuất bản (chưa tải danh sách bài): bật «Ghi SEO "
    "lên website» thì lần vẽ đó vừa có dòng «✅ SEO: … đã sẵn sàng» vừa có «Sẽ không ghi Tiêu đề "
    "SEO… đang báo «Chặn»» (dòng kiểm vẽ trước khi công tắc tải danh sách bài).",
)
def test_sl_t041_10_publish_checklist_agrees_with_seo_toggle(project_root, seo_ai, wordpress):
    wordpress.items = [*seo_ui.PUBLISHED, DUPLICATE_OF_FIRST_TITLE]
    at = seo_ui.to_seo(project_root)
    ui.run_ok(ui.button(at, "✨ AI gợi ý tiêu đề và mô tả SEO").click().run())
    ui.to_publish(at)  # nháp lưu ở bước Xuất bản
    fresh = ui.pages.open_page(project_root, "write.py")
    ui.run_ok(ui.button(fresh, "Mở", key=f"open-{at.session_state['draft_id']}").click().run())
    ui.run_ok(fresh.toggle(key="seo_write").set_value(True).run())
    assert any("Sẽ không ghi Tiêu đề SEO" in c for c in _captions(fresh))  # công tắc báo đúng
    ready = "✅ SEO: tiêu đề, mô tả, đường dẫn đã sẵn sàng"
    assert ready not in [m.value for m in fresh.markdown]


CLIENT_REFUSES = [
    "Sửa cổng inox [gallery] tại nhà Tân Phú",
    "Sửa cổng inox cao <2m tại nhà Tân Phú",
    "Sửa cổng inox &#37 giảm tại nhà Tân Phú",
]


@pytest.mark.parametrize("bad", CLIENT_REFUSES, ids=["shortcode", "nho-hon-so", "ma-ky-tu"])
def test_copy_box_refuses_what_client_refuses(project_root, seo_ai, bad):
    at = seo_ui.to_seo(project_root)
    ui.run_ok(at.text_input(key="seo_title").input(bad).run())
    assert any(c.startswith("Tiêu đề SEO: chưa chép được.") for c in _captions(at))
    assert not any(bad in c.value for c in at.code)


@pytest.mark.xfail(
    strict=True,
    reason="SL-T041-11: chữ client WordPress từ chối ghi (shortcode, «<» liền chữ số, mã ký tự "
    "HTML thiếu «;»): nhãn dưới ô vẫn xanh «Nên», chỉ khung «Chép sang SiteSEO» báo «chưa chép "
    "được».",
)
@pytest.mark.parametrize("bad", CLIENT_REFUSES, ids=["shortcode", "nho-hon-so", "ma-ky-tu"])
def test_sl_t041_11_field_badge_is_red_when_copy_is_refused(project_root, seo_ai, bad):
    at = seo_ui.to_seo(project_root)
    ui.run_ok(at.text_input(key="seo_title").input(bad).run())
    assert seo_ui.badges(at)[0].startswith(":red-badge[Chặn")
