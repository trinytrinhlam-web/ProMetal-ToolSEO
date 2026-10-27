"""T-041 (Họa Sĩ): bước 4 «SEO» của trang Soạn bài chạy thật, nối logic ``seo_app/onpage`` của Thợ
Máy, và công tắc «Ghi SEO lên website» ở bước 5.

AI giả (``SeoProvider``: gợi ý meta, liên kết nội bộ), WordPress giả (``fake_wordpress``), danh sách
bài đã đăng giả; file cache danh sách bài trỏ sang thư mục tạm. Không gọi AI, WordPress, mạng thật.
Mỗi test ghi điều kiện của phiếu mà nó kiểm (bảng «điều kiện → test» trong
``docs/team/reports/T-041-hoa-si.md``).
"""

from __future__ import annotations

import json
import unicodedata

import pytest
import streamlit as st
import test_app_images as ui
from fake_ai import FakeProvider
from fake_wordpress import BASE_URL, make_session, siteseo_seo_answer

import seo_app.storage.site_index as site_index
from seo_app.ai import registry as ai_registry
from seo_app.content.prompts import MetaSuggestions
from seo_app.onpage import meta as onpage_meta
from seo_app.onpage.links import LinkSuggestion, LinkSuggestions
from seo_app.onpage.schema import MSG_NO_FAQ, MSG_NO_FAQ_QUESTION
from seo_app.storage import DraftPart
from seo_app.storage.drafts import SendState
from seo_app.text import escape_markdown
from seo_app.wordpress.client import (
    ConnectionInfo,
    PublishedItem,
    PublishedList,
    WordPressClient,
)

# Fixture dùng chung: mật khẩu thử, cache ảnh xem trước tạm (Họa Sĩ T-056).
env = ui.env
previews = ui.previews

button = ui.button
run_ok = ui.run_ok
KEYWORD = "sửa cổng inox"  # từ khóa của ``ui.article()``
TITLES = [
    "Sửa cổng inox tại Tân Phú: thay bản lề gỉ",
    "Sửa cổng inox bị xệ cánh: thợ đến tận nhà",
    "Cổng inox xệ cánh? Cách sửa cổng inox bền",
]
REWRITTEN = [
    "Sửa cổng inox nhanh, kiểm tra bản lề tận nơi",
    "Sửa cổng inox xệ cánh tại nhà, bản lề mới",
]
DESCRIPTION = (
    "Cổng inox ở Tân Phú bị xệ cánh, bản lề gỉ sét? Xem cách thợ sửa cổng inox thay cả cặp bản lề, "
    "chỉnh cánh và kiểm tra mối hàn ngay tại nhà bạn."
)
DESCRIPTION_2 = (
    "Sửa cổng inox đúng cách: thay bản lề gỉ, chỉnh cánh xệ, làm sạch mối hàn. Đọc kinh nghiệm "
    "thật của xưởng trước khi gọi thợ đến nhà bạn nhé."
)
EVIL = "<img src=x onerror=alert(1)> [bấm](javascript:alert(1)) **đậm**"
ABILITY = "/wp-json/wp-abilities/v1/abilities/siteseo-posts/seo-data-update"
RUN = ABILITY + "/run"
POSTS = "/wp-json/wp/v2/posts"
POST_ID = 501


class SeoProvider(FakeProvider):
    """AI giả: gợi ý meta theo hàng đợi ``meta_answers``, gợi ý liên kết ``links``."""

    def __init__(self) -> None:
        super().__init__()
        self.meta_answers = [
            MetaSuggestions(titles=TITLES, descriptions=[DESCRIPTION, DESCRIPTION_2]),
            MetaSuggestions(titles=REWRITTEN, descriptions=[]),
        ]
        self.links = LinkSuggestions(
            links=[
                LinkSuggestion(post_id=11, section=0, anchor="Cổng inox"),
                LinkSuggestion(post_id=12, section=1, anchor="Bản lề gỉ"),
                LinkSuggestion(post_id=999, section=0, anchor="xệ cánh"),
            ]
        )

    def generate(self, task, *, system, prompt, schema, images=()):
        if schema is MetaSuggestions:
            self.calls.append((task.name, system, prompt))
            return self.meta_answers.pop(0)
        if schema is LinkSuggestions:
            self.calls.append((task.name, system, prompt))
            return self.links
        return super().generate(task, system=system, prompt=prompt, schema=schema, images=images)


@pytest.fixture
def seo_ai(monkeypatch) -> SeoProvider:
    provider = SeoProvider()
    monkeypatch.setattr(ai_registry, "make_provider", lambda name, settings: provider)
    return provider


@pytest.fixture(autouse=True)
def site_cache(monkeypatch, tmp_path_factory):
    """File cache danh sách bài đã đăng trong thư mục tạm (không đụng ``data/`` thật)."""
    path = tmp_path_factory.mktemp("danh-sach-bai") / "site_index.sqlite"
    monkeypatch.setattr(site_index, "DEFAULT_SITE_INDEX_FILE", path)
    return path


def published(id_: int, title: str, slug: str, meta_title: str = "") -> PublishedItem:
    return PublishedItem(
        id=id_,
        type="post",
        slug=slug,
        link=f"{BASE_URL}/{slug}/",
        title=title,
        meta_title=meta_title,
    )


PUBLISHED = [
    published(11, "Giá cổng inox 304 mới nhất", "gia-cong-inox-304"),
    published(12, "Cách thay bản lề cổng inox đúng cách", "thay-ban-le-cong-inox"),
]


@pytest.fixture
def wordpress(monkeypatch, fake_wp):
    """WordPress giả đã khai báo: client thật nối site giả (nhận ``write_seo`` của app), danh sách
    bài đã đăng ``wordpress.items``, bài nháp mới mã 501, Abilities của SiteSEO bật."""

    class Site:
        items = list(PUBLISHED)
        truncated = False  # site có nhiều trang kết quả hơn mức đọc một lần
        fake = fake_wp
        statuses = ["draft"]  # trạng thái bài 501 lần lượt trả cho các lệnh hỏi lại

    def from_settings(cls, settings, **kwargs):
        return cls(BASE_URL, "lam", "abcd efgh ijkl", session=make_session(fake_wp), **kwargs)

    def list_published(self):
        result = PublishedList(Site.items)
        result.truncated = Site.truncated
        return result

    def post_501(_request):
        status = Site.statuses.pop(0) if len(Site.statuses) > 1 else Site.statuses[0]
        return {"id": POST_ID, "status": status, "meta": {}}

    monkeypatch.setattr(WordPressClient, "from_settings", classmethod(from_settings))
    monkeypatch.setattr(WordPressClient, "list_published", list_published)
    fake_wp.on("POST", POSTS, (201, {"id": POST_ID, "status": "draft", "title": {"raw": "T"}}, {}))
    fake_wp.on("GET", f"{POSTS}/{POST_ID}", post_501)
    fake_wp.on("GET", ABILITY, {"name": "siteseo-posts/seo-data-update"})
    fake_wp.on("POST", RUN, siteseo_seo_answer)  # khuôn thật của SiteSEO 1.4.2 (T-059)
    return Site


def to_seo(project_root, snap=None):
    """Mở bài (``ui.article()``: từ khóa «sửa cổng inox», hai phần) rồi sang bước SEO."""
    at, _pid = ui.open_article(project_root, snap)
    at.session_state["step"] = 3
    return run_ok(at.run())


def badges(at) -> list[str]:
    """Huy hiệu mức (``:green-badge[…]``…): phần tử Markdown."""
    return [m.value for m in at.markdown if "-badge[" in m.value]


def html_blocks(at) -> list[str]:
    """Mọi khối Markdown được phép mang HTML (``unsafe_allow_html``) trên trang."""
    return [m.value for m in at.markdown if m.proto.allow_html]


# ============================================================ bố cục, không cần WordPress


def test_seo_step_is_real_and_works_without_wordpress(project_root, seo_ai):
    """Yêu cầu 6: không còn nhãn «Bản demo» ở bước SEO. Chưa kết nối WordPress: chỉ một câu báo nhẹ
    «chưa kết nối», các phần còn lại (meta, slug, chép SiteSEO, schema) vẫn dùng được (ghi chú
    Chỉ Huy 2026-10-16)."""
    at = to_seo(project_root)
    shown = "\n".join(ui.texts(at) + badges(at))
    assert "Bản demo" not in shown
    assert any(escape_markdown(site_index.MSG_NOT_CONNECTED) in c.value for c in at.caption)
    assert not button(at, "✨ AI gợi ý tiêu đề và mô tả SEO").disabled
    assert button(at, "✨ AI gợi ý liên kết").disabled  # chưa có danh sách bài
    assert at.session_state["seo_slug"] == "sua-cong-inox"  # gợi ý từ từ khóa
    assert any(escape_markdown(MSG_NO_FAQ) in c.value for c in at.caption)
    assert not at.exception


def test_ai_meta_then_rewrite_each_box_and_undo(project_root, seo_ai):
    """Yêu cầu 1: AI gợi ý cả hai ô; 🔄 viết lại riêng một ô (ô kia giữ nguyên); ↶ ↷ quay lại bản
    trước / tới bản sau. Ô sửa giữ title chưa gắn đuôi; gợi ý đã qua bộ kiểm (gợi ý mô tả có cụm
    nên tránh bị bỏ)."""
    at = to_seo(project_root)
    run_ok(button(at, "✨ AI gợi ý tiêu đề và mô tả SEO").click().run())
    assert at.session_state["seo_title_versions"] == TITLES
    assert at.session_state["seo_title"] == TITLES[0]
    assert at.session_state["seo_description_versions"] == [DESCRIPTION, DESCRIPTION_2]
    run_ok(ui.by_key(at, "seo-ai-title").click().run())
    assert at.session_state["seo_title_versions"] == TITLES + REWRITTEN
    assert at.session_state["seo_title"] == REWRITTEN[0]
    assert at.session_state["seo_description_versions"] == [DESCRIPTION, DESCRIPTION_2]
    assert seo_ai.tasks().count("meta") == 2
    run_ok(ui.by_key(at, "seo-undo-title").click().run())
    assert at.session_state["seo_title"] == TITLES[2]
    run_ok(ui.by_key(at, "seo-redo-title").click().run())
    assert at.session_state["seo_title"] == REWRITTEN[0]
    assert any(c.value == "Bản 4/5" for c in at.caption)


def test_user_edit_is_a_new_version_counted_nfc_with_brand(project_root, seo_ai):
    """Yêu cầu 1: chữ người dùng sửa thành bản mới (quay lại được bản AI); đếm ký tự NFC trên title
    sẽ lên Google (tính cả đuôi « | Pro-Metal», SL-T041-2); màu theo mức Nên."""
    at = to_seo(project_root)
    run_ok(button(at, "✨ AI gợi ý tiêu đề và mô tả SEO").click().run())
    typed = unicodedata.normalize("NFD", "Sửa cổng inox Tân Phú, thay bản lề tận nhà")
    run_ok(at.text_input(key="seo_title").input(typed).run())
    expected = unicodedata.normalize("NFC", typed)
    assert at.session_state["seo_title"] == expected
    assert at.session_state["seo_title_versions"][-1] == expected
    final = onpage_meta.with_brand(expected)
    assert final.endswith(" | Pro-Metal")
    assert f":green-badge[Nên · {len(final)} ký tự]" in badges(at)
    run_ok(ui.by_key(at, "seo-undo-title").click().run())
    assert at.session_state["seo_title"] == TITLES[2]


def test_blocked_title_is_red_and_not_copyable(project_root, seo_ai):
    """Yêu cầu 1, SL-T041-1: chữ bị Chặn (thẻ HTML, ``%%``, dạng shortcode) hiện mức «Chặn» và câu
    báo chữ thuần; ô «Chép sang SiteSEO» không cho chép chữ đó."""
    at = to_seo(project_root)
    for bad in ("Sửa cổng inox <b>gấp</b> tại nhà", "Sửa cổng inox %%sitename%% nhanh"):
        run_ok(at.text_input(key="seo_title").input(bad).run())
        assert any(b.startswith(":red-badge[Chặn") for b in badges(at))
        assert not any(bad in c.value for c in at.code)
        assert any(c.value.startswith("Tiêu đề SEO: chưa chép được.") for c in at.caption)
    run_ok(at.text_input(key="seo_title").input("Sửa cổng inox [gallery] tại nhà").run())
    assert not any("[gallery]" in c.value for c in at.code)


def test_siteseo_copy_has_final_texts(project_root, seo_ai):
    """Ghi chú Chỉ Huy 2026-10-16: chép tay sang SiteSEO: title đã gắn đuôi (``with_brand``),
    description, slug, mỗi thứ một khung ``st.code`` (có nút chép)."""
    at = to_seo(project_root)
    run_ok(button(at, "✨ AI gợi ý tiêu đề và mô tả SEO").click().run())
    codes = [c.value for c in at.code]
    assert onpage_meta.with_brand(TITLES[0]) in codes
    assert DESCRIPTION in codes
    assert "sua-cong-inox" in codes


def test_slug_suggest_edit_and_normalize(project_root, seo_ai):
    """Yêu cầu 2: slug gợi ý từ từ khóa, sửa được (đổi về dạng không dấu), 🔄 gợi ý lại."""
    at = to_seo(project_root)
    run_ok(at.text_input(key="seo_slug").input("Sửa Cổng Inox Đẹp Ở Tân Phú").run())
    assert at.session_state["seo_slug"] == "sua-cong-inox-dep-o-tan-phu"
    run_ok(at.text_input(key="seo_slug").input("cong inox!!").run())
    assert at.session_state["seo_slug"] == "cong-inox"
    run_ok(ui.by_key(at, "seo-slug-suggest").click().run())
    assert at.session_state["seo_slug"] == "sua-cong-inox"


def test_serp_preview_escapes_everything(project_root, seo_ai):
    """Yêu cầu 1 (kiểm lại escape của ``ui.serp_preview``): chữ người dùng có thẻ HTML vẫn chỉ là
    chữ trong khối xem trước Google."""
    at = to_seo(project_root)
    run_ok(at.text_input(key="seo_title").input("<script>alert(1)</script> sửa cổng inox").run())
    run_ok(at.text_area(key="seo_description").input('<img src=x onerror="alert(2)">').run())
    (preview,) = [block for block in html_blocks(at) if 'class="serp"' in block]
    assert "<script>" not in preview and "<img" not in preview
    assert "&lt;script&gt;" in preview and "&lt;img" in preview


# ============================================================ có WordPress: kiểm trùng, liên kết


def test_duplicates_from_site_are_plain_text(project_root, seo_ai, wordpress):
    """Yêu cầu 1, 2; LC-T036 số 5, LC-T037: kiểm trùng với bài đã đăng; câu báo có tên bài lấy
    từ website hiện bằng chữ thuần (escape), không bao giờ trong khối HTML."""
    wordpress.items = [
        *PUBLISHED,
        published(13, EVIL, "sua-cong-inox", meta_title=onpage_meta.with_brand(TITLES[0])),
    ]
    at = to_seo(project_root)
    run_ok(button(at, "✨ AI gợi ý tiêu đề và mô tả SEO").click().run())
    captions = [c.value for c in at.caption]
    assert any("trùng hệt bài" in c and escape_markdown(EVIL) in c for c in captions)
    assert any("Slug trùng bài" in c for c in captions)
    assert any(b.startswith(":red-badge[Chặn") for b in badges(at))
    assert not any("onerror" in block for block in html_blocks(at))
    assert not any(EVIL in c for c in captions)  # chữ thô không vào Markdown
    # «Chặn» vì trùng hệt như «Chặn» vì sai dạng: không cho chép (title, slug), mô tả vẫn chép được.
    codes = [c.value for c in at.code]
    assert onpage_meta.with_brand(TITLES[0]) not in codes and "sua-cong-inox" not in codes
    assert DESCRIPTION in codes
    assert any(c.startswith("Tiêu đề SEO: chưa chép được.") and "trùng hệt" in c for c in captions)
    assert any(c.startswith("Đường dẫn (slug): chưa chép được.") for c in captions)


def test_internal_links_from_ai_table_and_saved(project_root, seo_ai, wordpress):
    """Yêu cầu 3, 5; LC-T039 2b, 2c; góp ý G4: AI gợi ý liên kết tới bài do code chọn (không gửi địa
    chỉ), gợi ý sai bị bỏ kèm câu cố định; bảng «Dùng / Cụm từ trong bài / Trỏ tới bài» (tên bài chữ
    thuần); câu «Bài hướng dẫn chưa có trang dịch vụ đích» không hiện; lưu cùng nháp, không địa
    chỉ."""
    at = to_seo(project_root)
    assert not any("trang dịch vụ đích" in c.value for c in at.caption)
    run_ok(button(at, "✨ AI gợi ý liên kết").click().run())
    _task, _system, prompt = next(call for call in seo_ai.calls if call[0] == "links")
    assert all(item.link not in prompt and item.slug not in prompt for item in PUBLISHED)
    (table,) = at.dataframe
    rows = table.value.to_dict("records")
    assert rows == [
        {"Dùng": True, "Cụm từ trong bài": "Cổng inox", "Trỏ tới bài": PUBLISHED[0].title},
        {"Dùng": True, "Cụm từ trong bài": "Bản lề gỉ", "Trỏ tới bài": PUBLISHED[1].title},
    ]
    rejected = escape_markdown("Gợi ý 3: bài đích không có trong danh sách được chọn.")
    assert rejected in [c.value for c in at.caption]
    saved = ui.store().load(at.session_state["draft_id"]).seo
    assert [(link.post_id, link.anchor, link.use) for link in saved.links] == [
        (11, "Cổng inox", True),
        (12, "Bản lề gỉ", True),
    ]
    assert "http" not in saved.model_dump_json()


def test_truncated_listing_is_only_a_notice(project_root, seo_ai, wordpress):
    """LC-T037: danh sách bài chưa đủ (site nhiều trang hơn mức đọc một lần): chỉ báo nhẹ «danh
    sách chưa đủ, kiểm trùng có thể sót», không kết luận link nào hỏng; các phần khác vẫn chạy."""
    wordpress.truncated = True
    at = to_seo(project_root)
    assert any(escape_markdown(site_index.MSG_TRUNCATED) in c.value for c in at.caption)
    run_ok(button(at, "✨ AI gợi ý liên kết").click().run())
    assert len(at.dataframe) == 1
    assert not any("hỏng" in text for text in ui.texts(at))


def test_use_column_untick_is_kept(project_root, seo_ai, wordpress, monkeypatch):
    """Yêu cầu 3, 5: bỏ tick «Dùng» ở bảng thì nháp nhớ ``use=False``. ``AppTest`` không sửa được ô
    bảng nên thay ``st.data_editor`` bằng hàm trả bảng đã sửa (như người dùng bỏ tick dòng 1)."""
    at = to_seo(project_root)
    run_ok(button(at, "✨ AI gợi ý liên kết").click().run())
    original = st.data_editor

    def untick_first(data, *args, **kwargs):
        rows = original(data, *args, **kwargs)
        if hasattr(rows, "to_dict"):
            rows = rows.to_dict("records")
        return [{**row, "Dùng": False} if i == 0 else row for i, row in enumerate(rows)]

    monkeypatch.setattr(st, "data_editor", untick_first)
    run_ok(at.run())
    assert [link.use for link in at.session_state["seo_links"]] == [False, True]
    saved = ui.store().load(at.session_state["draft_id"]).seo
    assert [link.use for link in saved.links] == [False, True]


def test_reload_listing_button_refreshes(project_root, seo_ai, wordpress):
    """Yêu cầu 3: nút «Tải lại danh sách bài» đọc lại danh sách từ website (bài mới đăng hiện ra
    trong kiểm trùng); không bấm thì dùng danh sách đã có trong phiên."""
    at = to_seo(project_root)
    run_ok(at.text_input(key="seo_slug").input("bai-moi-dang").run())
    assert not any("Slug trùng bài" in c.value for c in at.caption)
    wordpress.items = [*PUBLISHED, published(14, "Bài mới đăng", "bai-moi-dang")]
    run_ok(at.run())
    assert not any("Slug trùng bài" in c.value for c in at.caption)  # chưa tải lại
    run_ok(button(at, "🔄 Tải lại danh sách bài").click().run())
    assert any("Slug trùng bài «Bài mới đăng»" in c.value for c in at.caption)


# ============================================================ schema FAQ


FAQ_PART = DraftPart(
    heading="Hỏi đáp",
    versions=[
        "### Cổng inox bị xệ có sửa được không?\n\nĐược, thay bản lề và chỉnh lại cánh.\n\n"
        "### Bao lâu nên kiểm tra bản lề?\n\nMỗi năm một lần, trước mùa mưa."
    ],
)


def test_faq_schema_shown_only_as_code(project_root, seo_ai):
    """Yêu cầu 4; Lá Chắn T-038 đk 3: bài có mục Hỏi đáp thì hiện JSON-LD FAQPage bằng ``st.code``
    (chữ thuần, không HTML), có ô «Dùng schema» lưu cùng nháp."""
    snap = ui.article()
    snap.parts.append(FAQ_PART)
    at = to_seo(project_root, snap)
    (code,) = [c for c in at.code if c.language == "json"]
    data = json.loads(code.value)
    assert data["@type"] == "FAQPage" and len(data["mainEntity"]) == 2
    assert not any("FAQPage" in block for block in html_blocks(at))
    run_ok(at.checkbox(key="seo_use_faq").check().run())
    assert ui.store().load(at.session_state["draft_id"]).seo.use_faq is True


# ============================================================ lưu nháp, mở lại


def test_seo_choices_saved_and_restored(project_root, seo_ai):
    """Yêu cầu 5: mọi lựa chọn ở bước SEO (các bản meta, bản đang dùng, slug, schema) tự lưu cùng
    nháp; phiên mới mở lại nháp thì thấy đúng như cũ."""
    at = to_seo(project_root)
    run_ok(button(at, "✨ AI gợi ý tiêu đề và mô tả SEO").click().run())
    run_ok(ui.by_key(at, "seo-ai-title").click().run())
    run_ok(ui.by_key(at, "seo-undo-title").click().run())
    run_ok(at.text_input(key="seo_slug").input("sua-cong-inox-tan-phu").run())
    draft = at.session_state["draft_id"]
    fresh = ui.pages.open_page(project_root, "write.py")
    run_ok(button(fresh, "Mở", key=f"open-{draft}").click().run())
    fresh.session_state["step"] = 3
    run_ok(fresh.run())
    assert fresh.session_state["seo_title_versions"] == TITLES + REWRITTEN
    assert fresh.session_state["seo_title"] == TITLES[2]
    assert fresh.session_state["seo_description"] == DESCRIPTION
    assert fresh.session_state["seo_slug"] == "sua-cong-inox-tan-phu"


def test_switching_pages_keeps_seo_choices(project_root, seo_ai):
    """Sang trang khác ở menu rồi quay lại: slug, ô schema, các bản meta vẫn còn (``_kept``)."""
    at = to_seo(project_root)
    run_ok(button(at, "✨ AI gợi ý tiêu đề và mô tả SEO").click().run())
    run_ok(at.text_input(key="seo_slug").input("cong-inox-tan-phu").run())
    run_ok(at.switch_page("views/home.py").run())
    run_ok(at.switch_page("views/write.py").run())
    assert at.session_state["seo_slug"] == "cong-inox-tan-phu"
    assert at.session_state["seo_title"] == TITLES[0]


# ============================================================ bước 5: ghi SEO lên website


def test_publish_checklist_shows_real_seo_state(project_root, seo_ai):
    """Yêu cầu 6: dòng SEO ở «Kiểm tra trước khi gửi» (bước Xuất bản) không còn «bản demo»: chưa có
    meta thì báo chưa dùng được; AI gợi ý xong thì sẵn sàng. Chỉ xem bước Xuất bản: không gọi
    website."""
    at = to_seo(project_root)
    at.session_state["step"] = 4
    run_ok(at.run())
    lines = [m.value for m in at.markdown]
    assert "⚠️ SEO: Tiêu đề SEO, Mô tả SEO chưa dùng được (xem bước SEO)" in lines
    assert not any("bản demo" in line for line in lines)
    at.session_state["step"] = 3
    run_ok(at.run())
    run_ok(button(at, "✨ AI gợi ý tiêu đề và mô tả SEO").click().run())
    at.session_state["step"] = 4
    run_ok(at.run())
    assert "✅ SEO: tiêu đề, mô tả, đường dẫn đã sẵn sàng" in [m.value for m in at.markdown]


def send_with_seo(project_root, seo_ai, toggle: bool):
    at = to_seo(project_root)
    run_ok(button(at, "✨ AI gợi ý tiêu đề và mô tả SEO").click().run())
    at.session_state["step"] = 4
    run_ok(at.run())
    assert at.toggle(key="seo_write").value is False  # mặc định tắt (Lá Chắn T-042)
    if toggle:
        run_ok(at.toggle(key="seo_write").set_value(True).run())
    return ui.send(at)


def test_seo_write_is_off_by_default(project_root, seo_ai, wordpress):
    """Lá Chắn T-042: công tắc mặc định tắt: gửi nháp không gọi gì tới SiteSEO, không có câu báo
    nào về ghi SEO (cả lớp chặn thứ hai: client tạo với ``write_seo=False``)."""
    at = send_with_seo(project_root, seo_ai, toggle=False)
    paths = [ui.path_of(r) for r in wordpress.fake.requests]
    assert POSTS in paths and ABILITY not in paths and RUN not in paths
    assert any("Đã tạo bài nháp" in s.value for s in at.success)
    assert not any("SEO" in i.value for i in at.info)


def test_seo_written_after_draft_with_brand_and_rechecked(project_root, seo_ai, wordpress):
    """Bật công tắc: sau khi tạo nháp, ghi tiêu đề (đã gắn đuôi bằng ``with_brand``), mô tả, từ khóa
    chính vào SiteSEO của **chính bài vừa tạo**; ghi qua Abilities xong thì hỏi lại bài còn là nháp
    (LC-T042-2); câu kết quả hiện chữ thường."""
    at = send_with_seo(project_root, seo_ai, toggle=True)
    (run,) = [r for r in wordpress.fake.requests if ui.path_of(r) == RUN]
    payload = json.loads(run.body)["input"]
    assert payload["postId"] == POST_ID
    assert payload["title"] == onpage_meta.with_brand(TITLES[0])
    assert payload["description"] == DESCRIPTION
    assert payload["focus_keyphrase"] == KEYWORD
    after = [r for r in wordpress.fake.requests if r.method == "GET" and str(POST_ID) in r.url]
    assert len(after) == 2  # kiểm còn nháp trước khi ghi, hỏi lại sau khi ghi
    assert any(
        i.value == escape_markdown("Đã ghi SEO vào hộp SiteSEO của bài nháp.") for i in at.info
    )


def test_blocked_duplicate_title_is_not_written(project_root, seo_ai, wordpress):
    """Tiêu đề trùng hệt bài đã đăng (mức «Chặn»): bật công tắc thì báo trước «Sẽ không ghi Tiêu đề
    SEO»; gửi nháp thì không gửi tiêu đề lên SiteSEO (chỉ mô tả, từ khóa chính) và câu kết quả nói
    rõ phần không ghi."""
    wordpress.items = [*PUBLISHED, published(13, EVIL, "bai-cu", meta_title=TITLES[0])]
    at = to_seo(project_root)
    run_ok(button(at, "✨ AI gợi ý tiêu đề và mô tả SEO").click().run())
    at.session_state["step"] = 4
    run_ok(at.run())
    run_ok(at.toggle(key="seo_write").set_value(True).run())
    assert escape_markdown("Sẽ không ghi Tiêu đề SEO: ở bước SEO đang báo «Chặn»") in "\n".join(
        c.value for c in at.caption
    )
    ui.send(at)
    (run,) = [r for r in wordpress.fake.requests if ui.path_of(r) == RUN]
    payload = json.loads(run.body)["input"]
    assert "title" not in payload
    assert payload["description"] == DESCRIPTION and payload["focus_keyphrase"] == KEYWORD
    (info,) = [i.value for i in at.info if "Đã ghi SEO" in i.value]
    assert escape_markdown("Không ghi Tiêu đề SEO: ở bước SEO đang báo «Chặn».") in info


def test_post_published_during_seo_write_is_reported(project_root, seo_ai, wordpress):
    """LC-T042-2: bài bị đăng đúng lúc ghi SEO (lần hỏi lại sau khi ghi thấy không còn nháp): báo
    người dùng kiểm hộp SiteSEO, không im lặng."""
    wordpress.statuses = ["draft", "publish"]
    at = send_with_seo(project_root, seo_ai, toggle=True)
    (info,) = [i.value for i in at.info if "Kiểm lại ngay sau khi ghi SEO" in i.value]
    assert "không còn là bản nháp" in info


def test_seo_write_needs_client_that_created_the_draft(project_root, seo_ai, wordpress):
    """T-086 Ghi nhận 2, Lá Chắn T-042: không ghi SEO cho bài theo mã bài lưu trong nháp (phiên mới,
    client mới không có mã bài đó): không có lệnh ghi nào ngoài lần gửi nháp."""
    send_with_seo(project_root, seo_ai, toggle=True)
    runs = [r for r in wordpress.fake.requests if ui.path_of(r) == RUN]
    assert len(runs) == 1
    client = WordPressClient.from_settings(None, write_seo=True)
    with pytest.raises(Exception, match="Chỉ được ghi SEO cho bài nháp app vừa tạo"):
        client.set_seo_meta(POST_ID, title="x")


def test_reopened_sent_draft_never_writes_seo_to_stored_post(project_root, seo_ai, wordpress):
    """T-086 Ghi nhận 2: nháp đã gửi (mã bài 777 lưu trong nháp), phiên mới mở lại, bật công tắc:
    không có lệnh nào tới bài 777; tạo thêm bài nháp mới thì chỉ ghi SEO cho bài vừa tạo (501)."""
    at = to_seo(project_root)
    run_ok(button(at, "✨ AI gợi ý tiêu đề và mô tả SEO").click().run())
    draft = at.session_state["draft_id"]
    ui.store().save_send_state(draft, SendState.now(pending=False, post_id=777))
    fresh = ui.pages.open_page(project_root, "write.py")
    run_ok(button(fresh, "Mở", key=f"open-{draft}").click().run())
    ui.to_publish(fresh)
    run_ok(fresh.toggle(key="seo_write").set_value(True).run())
    assert button(fresh, ui.SEND_LABEL).disabled  # khóa «đã gửi» của T-086
    assert wordpress.fake.requests == []
    run_ok(fresh.checkbox(key="_wp_again").check().run())
    ui.send(fresh)
    (run,) = [r for r in wordpress.fake.requests if ui.path_of(r) == RUN]
    assert json.loads(run.body)["input"]["postId"] == POST_ID
    assert not any("777" in r.url for r in wordpress.fake.requests)
    assert not any("777" in json.dumps(ui.body_of(r)) for r in wordpress.fake.requests)


def test_unexpected_seo_error_keeps_draft_result(project_root, seo_ai, wordpress, monkeypatch):
    """Lỗi lạ lúc ghi SEO (không phải ``WordPressError``): bài nháp vẫn báo đã tạo, nháp ghi «đã
    gửi (mã 501)»; phần SEO chỉ hiện câu cố định, không hiện lỗi thô, trang không vỡ."""

    def broken(self, post_id, **kwargs):
        raise RuntimeError("chi tiết nội bộ <b>")

    monkeypatch.setattr(WordPressClient, "set_seo_meta", broken)
    at = send_with_seo(project_root, seo_ai, toggle=True)
    assert any("Đã tạo bài nháp" in s.value for s in at.success)
    (info,) = [i.value for i in at.info if "Ghi SEO lên website" in i.value]
    assert info.startswith(escape_markdown("Ghi SEO lên website gặp lỗi không mong đợi."))
    assert not any("chi tiết nội bộ" in text for text in ui.texts(at))
    assert ui.store().load_send_state(at.session_state["draft_id"]).post_id == POST_ID


# ============================================================ lượt 2: trang Kết nối WordPress


@pytest.mark.parametrize("writable", [True, False, None])
def test_wordpress_page_shows_siteseo_status(project_root, wordpress, monkeypatch, writable):
    """Ghi chú Chỉ Huy 2026-10-17 (phần giao diện của T-042): kiểm tra kết nối xong, trang Kết nối
    WordPress hiện «SiteSEO: ghi được / chưa bật / chưa dò được» (``info.siteseo_status``), đã
    thoát Markdown."""
    info = ConnectionInfo(
        "ProMetal", BASE_URL, "Lâm", ("editor",), True, True, True, siteseo_writable=writable
    )
    monkeypatch.setattr(WordPressClient, "check_connection", lambda self: info)
    at = ui.pages.open_page(project_root, "wordpress.py")
    run_ok(button(at, "Kiểm tra kết nối").click().run())
    (listing,) = [m.value for m in at.markdown if "Tài khoản:" in m.value]
    assert listing.endswith(f"- {escape_markdown(info.siteseo_status)}")
    assert info.siteseo_status.startswith("SiteSEO: ")


# ============================================================ lượt 2: chữ bị Chặn vì ký tự lạ

BAD_TITLE = "Sửa cổng inox\x1b tại nhà Tân Phú"  # ESC lẫn vào khi dán từ nơi khác
BAD_DESCRIPTION = DESCRIPTION.replace("Tân Phú", "Tân\x07 Phú")  # BEL


def paste_bad_meta(at):
    run_ok(at.text_input(key="seo_title").input(BAD_TITLE).run())
    return run_ok(at.text_area(key="seo_description").input(BAD_DESCRIPTION).run())


def test_pasted_control_chars_are_blocked_not_copied(project_root, seo_ai):
    """Lượt 2 (Thợ Máy lượt 3): dán chữ có ký tự điều khiển vào ô title/description: nhãn «Chặn» và
    câu nhắc xóa ô gõ lại (chữ thuần), khung chép không cho chép hai ô đó (slug vẫn chép được),
    không lỗi đỏ. Ô và nháp giữ đúng chữ đã dán (không lặng lẽ bỏ ký tự)."""
    at = paste_bad_meta(to_seo(project_root))
    captions = [c.value for c in at.caption]
    for check in (
        onpage_meta.check_title(BAD_TITLE),
        onpage_meta.check_description(BAD_DESCRIPTION),
    ):
        assert check.level is onpage_meta.Level.BLOCK
        (message,) = check.messages
        assert "Xóa ô rồi gõ lại chữ thường" in message
        assert escape_markdown(message) in captions  # dòng dưới ô
    assert sum(b.startswith(":red-badge[Chặn") for b in badges(at)) == 2
    assert any(c.startswith("Tiêu đề SEO: chưa chép được.") for c in captions)
    assert any(c.startswith("Mô tả SEO: chưa chép được.") for c in captions)
    codes = [c.value for c in at.code]
    assert "sua-cong-inox" in codes
    assert not any("\x1b" in c or "\x07" in c for c in codes)
    assert not at.error and not at.exception
    assert at.session_state["seo_title"] == BAD_TITLE
    saved = ui.store().load(at.session_state["draft_id"]).seo
    assert (saved.title.text, saved.description.text) == (BAD_TITLE, BAD_DESCRIPTION)


def test_blocked_control_chars_are_not_written(project_root, seo_ai, wordpress):
    """Lượt 2: title, description bị Chặn vì ký tự điều khiển: bước Xuất bản báo «chưa dùng được»,
    bật «Ghi SEO lên website» thì báo trước; gửi nháp chỉ ghi từ khóa chính, câu kết quả nói rõ
    phần không ghi; không lỗi đỏ, không gửi ký tự lạ nào lên website."""
    at = paste_bad_meta(to_seo(project_root))
    at.session_state["step"] = 4
    run_ok(at.run())
    lines = [m.value for m in at.markdown]
    assert "⚠️ SEO: Tiêu đề SEO, Mô tả SEO chưa dùng được (xem bước SEO)" in lines
    run_ok(at.toggle(key="seo_write").set_value(True).run())
    will_skip = escape_markdown("Sẽ không ghi Tiêu đề SEO, Mô tả SEO: ở bước SEO đang báo «Chặn»")
    assert will_skip in "\n".join(c.value for c in at.caption)
    ui.send(at)
    assert any("Đã tạo bài nháp" in s.value for s in at.success)
    (run,) = [r for r in wordpress.fake.requests if ui.path_of(r) == RUN]
    assert json.loads(run.body)["input"] == {"postId": POST_ID, "focus_keyphrase": KEYWORD}
    bodies = [
        r.body.decode("utf-8", "replace") if isinstance(r.body, bytes) else (r.body or "")
        for r in wordpress.fake.requests
    ]
    odd = ("\x1b", "\x07", "\\u001b", "\\u0007")  # thô hay đã mã hóa JSON
    assert not any(bad in body for body in bodies for bad in odd)
    (info,) = [i.value for i in at.info if "Đã ghi SEO" in i.value]
    assert escape_markdown("Không ghi Tiêu đề SEO, Mô tả SEO: ở bước SEO đang báo «Chặn».") in info
    assert not at.error and not at.exception


FAQ_WITHOUT_QUESTIONS = DraftPart(
    heading="Câu hỏi thường gặp", versions=["Liên hệ xưởng để được tư vấn thêm."]
)


def test_faq_section_without_proper_questions_says_so(project_root, seo_ai):
    """Lượt 2 (Thợ Máy lượt 3, câu ``MSG_NO_FAQ_QUESTION``): bài có mục «Câu hỏi thường gặp» mà
    chưa có câu hỏi đúng dạng: Schema nói đúng điều đó (không còn «chưa có mục Hỏi đáp»), không
    có JSON-LD, không có ô «Dùng schema»."""
    snap = ui.article()
    snap.parts.append(FAQ_WITHOUT_QUESTIONS)
    at = to_seo(project_root, snap)
    captions = [c.value for c in at.caption]
    assert f"⚠️ {escape_markdown(MSG_NO_FAQ_QUESTION)}" in captions
    assert not any(escape_markdown(MSG_NO_FAQ) in c for c in captions)
    assert not [c for c in at.code if c.language == "json"]
    assert not any(box.key == "seo_use_faq" for box in at.checkbox)


# ============================================================ lượt 2: câu liên kết khi nút mờ

NO_AI_HINT = "Nút «AI gợi ý liên kết» đang tắt vì AI chưa dùng được"
NO_LIST_HINT = "Nút «AI gợi ý liên kết» cần danh sách bài đã đăng"
CLICK_HINT = "Chưa có liên kết nội bộ nào: bấm «AI gợi ý liên kết»."


def link_hints(at) -> list[str]:
    return [c.value for c in at.caption if c.value.startswith("Chưa có liên kết nội bộ nào")]


def test_links_hint_without_ai_key(project_root, wordpress):
    """Góp ý 4 (lượt 1): chưa có khóa AI thì nút mờ, câu dưới bảng nói lý do thay cho «bấm…»."""
    at = to_seo(project_root)  # không có ``seo_ai``: môi trường thử không có khóa AI
    assert button(at, "✨ AI gợi ý liên kết").disabled
    (hint,) = link_hints(at)
    assert NO_AI_HINT in hint and CLICK_HINT not in hint


def test_links_hint_without_wordpress(project_root, seo_ai):
    """Chưa kết nối WordPress (không có danh sách bài): nút mờ, câu nói cần danh sách bài."""
    at = to_seo(project_root)
    assert button(at, "✨ AI gợi ý liên kết").disabled
    (hint,) = link_hints(at)
    assert NO_LIST_HINT in hint and CLICK_HINT not in hint


def test_links_hint_when_button_works(project_root, seo_ai, wordpress):
    """Có khóa AI và danh sách bài: nút bấm được, câu vẫn mời bấm như cũ."""
    at = to_seo(project_root)
    assert not button(at, "✨ AI gợi ý liên kết").disabled
    assert link_hints(at) == [CLICK_HINT]


# ============================================================ lượt 3: SL-T041-9, -10, -11

ODD_KEYWORD_MESSAGE = (
    "Từ khóa chính có ký tự điều khiển hoặc ký tự lạ (không nhìn thấy, thường do dán từ nơi khác)."
)
BAD_KEYWORDS = {
    "ESC": ("sửa cổng\x1b inox", ODD_KEYWORD_MESSAGE),
    "U+E000": ("sửa cổng inox", ODD_KEYWORD_MESSAGE),
    "nho-hon-so": (
        "cổng inox <2m",
        onpage_meta.seo_write_problem("Từ khóa chính", "cổng inox <2m"),
    ),
    "qua-dai": ("cổng inox " * 25, "Từ khóa chính quá dài (tối đa 200 ký tự)."),
}


@pytest.mark.parametrize("bad", BAD_KEYWORDS.values(), ids=BAD_KEYWORDS.keys())
def test_bad_keyword_is_flagged_on_seo_and_publish_steps(project_root, seo_ai, bad):
    """SL-T041-9: từ khóa chính (gõ ở bước Chuẩn bị) không ghi được vào SiteSEO: bước SEO có dòng
    «Từ khóa chính» nhãn «Chặn» và câu nhắc sửa ở bước 1 (chữ thuần); bước Xuất bản báo «Từ khóa
    chính chưa dùng được». Không lỗi đỏ, không khung chép nào chép từ khóa đó."""
    keyword, message = bad
    assert message  # bộ kiểm có sẵn thật sự từ chối từ khóa này
    at = to_seo(project_root, ui.article(keyword=keyword))
    assert "Từ khóa chính" in [m.value for m in at.markdown]
    assert badges(at)[-1] == ":red-badge[Chặn]"
    captions = [c.value for c in at.caption]
    assert escape_markdown(f"{message} Sửa từ khóa ở bước 1 · Chuẩn bị.") in captions
    assert not any(keyword.strip() in c.value for c in at.code)
    assert not at.error and not at.exception
    at.session_state["step"] = 4
    run_ok(at.run())
    lines = [m.value for m in at.markdown]
    assert any(line.startswith("⚠️ SEO:") and "Từ khóa chính" in line for line in lines)


def test_bad_keyword_does_not_lose_title_and_description(project_root, seo_ai, wordpress):
    """SL-T041-9: từ khóa hỏng chỉ bị bỏ riêng: lệnh ghi SEO vẫn có tiêu đề (đã gắn đuôi), mô tả;
    câu kết quả nói rõ «Không ghi Từ khóa chính»."""
    at = to_seo(project_root, ui.article(keyword="cổng inox <2m"))
    run_ok(at.text_input(key="seo_title").input(TITLES[0]).run())  # tự gõ: gợi ý AI cần từ khóa
    run_ok(at.text_area(key="seo_description").input(DESCRIPTION).run())
    at.session_state["step"] = 4
    run_ok(at.run())
    run_ok(at.toggle(key="seo_write").set_value(True).run())
    will_skip = escape_markdown("Sẽ không ghi Từ khóa chính: ở bước SEO đang báo «Chặn»")
    assert will_skip in "\n".join(c.value for c in at.caption)
    ui.send(at)
    (run,) = [r for r in wordpress.fake.requests if ui.path_of(r) == RUN]
    assert json.loads(run.body)["input"] == {
        "postId": POST_ID,
        "title": onpage_meta.with_brand(TITLES[0]),
        "description": DESCRIPTION,
    }
    (info,) = [i.value for i in at.info if "Đã ghi SEO" in i.value]
    assert escape_markdown("Không ghi Từ khóa chính: ở bước SEO đang báo «Chặn».") in info


def test_publish_step_loads_listing_only_when_toggle_is_on(project_root, seo_ai, wordpress):
    """SL-T041-10: phiên mới mở nháp ở bước Xuất bản: công tắc tắt thì không tải danh sách bài
    (chỉ xem không gọi website); bật thì tải trước khi vẽ dòng kiểm, dòng kiểm và câu báo của công
    tắc nói cùng một điều."""
    wordpress.items = [*PUBLISHED, published(13, "Bài cũ", "bai-cu", meta_title=TITLES[0])]
    at = to_seo(project_root)
    run_ok(button(at, "✨ AI gợi ý tiêu đề và mô tả SEO").click().run())
    ui.to_publish(at)
    fresh = ui.pages.open_page(project_root, "write.py")
    run_ok(button(fresh, "Mở", key=f"open-{at.session_state['draft_id']}").click().run())
    assert fresh.session_state["step"] == 4
    assert "_site_listing" not in fresh.session_state
    run_ok(fresh.toggle(key="seo_write").set_value(True).run())
    lines = [m.value for m in fresh.markdown]
    assert "⚠️ SEO: Tiêu đề SEO chưa dùng được (xem bước SEO)" in lines
    will_skip = escape_markdown("Sẽ không ghi Tiêu đề SEO: ở bước SEO đang báo «Chặn»")
    assert will_skip in "\n".join(c.value for c in fresh.caption)


def test_description_badge_matches_copy_box(project_root, seo_ai):
    """SL-T041-11 (cả ô mô tả): chữ client WordPress từ chối ghi thì nhãn dưới ô cũng đỏ «Chặn» kèm
    đúng câu lý do của khung chép, không còn xanh «Nên»."""
    at = to_seo(project_root)
    bad = DESCRIPTION.replace("bản lề gỉ sét?", "bản lề [gallery] gỉ sét?")
    run_ok(at.text_area(key="seo_description").input(bad).run())
    title_badge, description_badge = badges(at)[:2]
    assert description_badge.startswith(":red-badge[Chặn")
    (reason,) = onpage_meta.siteseo_copy("", bad, "a-b").checks[1].messages
    captions = [c.value for c in at.caption]
    assert escape_markdown(reason) in captions  # dòng dưới ô
    assert f"Mô tả SEO: chưa chép được. {escape_markdown(reason)}" in captions  # khung chép


# ============================================================ lượt 4: LC-T041-1

PLACEHOLDER_HOST = "website-cua-ban.vn"
SECRET = "MAT-KHAU-GIA-L4"  # chuỗi mồi, không phải mật khẩu thật
SITE_URLS = {
    "ten-mat-khau": (f"https://ten-gia:{SECRET}@suachuacuasat.com", "suachuacuasat.com"),
    "ten-mat-khau-cong-chu-hoa": (
        f"https://ten-gia:{SECRET}@SuaChuaCuaSat.com:8443/wp",
        "suachuacuasat.com",
    ),
    "chi-mat-khau": (f"https://:{SECRET}@suachuacuasat.com", "suachuacuasat.com"),
    "cong": ("https://suachuacuasat.com:8443", "suachuacuasat.com"),
    "truy-van": (f"https://suachuacuasat.com/?token={SECRET}", "suachuacuasat.com"),
    "ipv6": ("https://[2001:db8::1]:8443", "2001:db8::1"),
    "ipv6-thieu-ngoac": ("https://[2001:db8::1", PLACEHOLDER_HOST),  # urlsplit ném ValueError
    "khong-ten-may": (f"https://ten-gia:{SECRET}@", PLACEHOLDER_HOST),
    "thieu-https": ("suachuacuasat.com", PLACEHOLDER_HOST),
    "trong": ("", PLACEHOLDER_HOST),
}


@pytest.mark.parametrize("url, host", SITE_URLS.values(), ids=SITE_URLS.keys())
def test_serp_preview_shows_only_host_of_wordpress_url(
    project_root, seo_ai, monkeypatch, url, host
):
    """LC-T041-1: khung «Xem trước trên Google» chỉ hiện tên máy của ``WORDPRESS_URL`` (không
    tên đăng nhập, mật khẩu, cổng, truy vấn; chữ thường). Địa chỉ trống hay hỏng (kể cả kiểu làm
    ``urlsplit`` ném lỗi) thì chữ mẫu, trang không lỗi."""
    monkeypatch.setenv("WORDPRESS_URL", url)
    at = to_seo(project_root)
    (preview,) = [block for block in html_blocks(at) if 'class="serp"' in block]
    assert f'<div class="url">{host} › sua-cong-inox</div>' in preview
    for hidden in (SECRET, "ten-gia", "8443", "token", "SuaChuaCuaSat"):
        assert hidden not in preview
    assert not any(SECRET in text for text in ui.texts(at))
    assert not at.exception
