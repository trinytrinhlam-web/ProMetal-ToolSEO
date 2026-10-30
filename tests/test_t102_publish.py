"""T-102 (Họa Sĩ): bước «Xuất bản» thật của trang Soạn bài: gửi bằng gói của bộ dựng T-096 cho cả
Nháp, Hẹn giờ, Đăng ngay; màn hình xác nhận có mã băm; ``release_draft`` là lệnh cuối cùng trên
client; khóa gửi trùng phủ cả bước chuyển trạng thái; công tắc Hẹn giờ / Đăng ngay mặc định tắt.

Điều kiện Lá Chắn: LC-T094-1 → -3 (chung), LC-T094-36 → -41 (T-102), Lá Chắn T-099 điều kiện 2
(L2-1 → L2-3). Bảng «điều kiện → test» trong ``docs/team/reports/T-102-hoa-si.md``.

Kế hoạch (thiết kế 1.6, 1.7; T-100; hợp đồng ``_start_plan_key`` với T-101; Lá Chắn T-103 đk 2):
Google Sheet giả có trạng thái (``FakePlanSheet`` trên ``FakeGoogle``) nối vào ``SheetsClient``
thật.

WordPress giả (``FakeWordPress``), AI giả, ảnh tự tạo bằng Pillow; file cache danh sách bài, bản lưu
kế hoạch trỏ sang thư mục tạm. Không gọi WordPress, Google, AI, mạng thật.
"""

from __future__ import annotations

import json
from datetime import UTC, date, datetime, time, timedelta
from email.utils import format_datetime
from zoneinfo import ZoneInfo

import pytest
import streamlit as st
import test_app_images as ui
import test_t041_seo_ui as seo_ui
from fake_google import SHEET_ID, FakeGoogle, key_info, make_session, new_private_key
from fake_plan_sheet import HEADER, FakePlanSheet
from fake_wordpress import BASE_URL
from streamlit.runtime.scriptrunner_utils.exceptions import StopException

from seo_app.content import rules
from seo_app.google.service_account import load_service_account
from seo_app.google.sheets import SheetsClient
from seo_app.onpage import links as onpage_links
from seo_app.plan import model as plan_model
from seo_app.publish.render import ArticlePart, build_article
from seo_app.publish.schedule import date_gmt_text, local_to_utc, schedule_label
from seo_app.sanitize import break_autolinks
from seo_app.storage import DraftPart, DraftSnapshot, plan_cache
from seo_app.storage.drafts import DraftLink, DraftPlanRef, DraftSeo
from seo_app.storage.plan_cache import sheet_hash
from seo_app.storage.site_index import SiteIndex, SiteIndexStore
from seo_app.text import escape_markdown
from seo_app.wordpress.client import (
    ConnectionInfo,
    PublishedItem,
    PublishedList,
    WordPressClient,
)

# Fixture dùng chung: mật khẩu thử, cache ảnh xem trước tạm, AI giả, thư mục ảnh, WordPress giả,
# cache danh sách bài tạm (T-041).
env = ui.env
previews = ui.previews
fake_ai = ui.fake_ai
root = ui.root
site = ui.site
sent = ui.sent
site_cache = seo_ui.site_cache
seo_ai = seo_ui.seo_ai
wordpress = seo_ui.wordpress

button = ui.button
run_ok = ui.run_ok
POSTS, MEDIA, POST_ID = ui.POSTS, ui.MEDIA, ui.POST_ID
POST = f"{POSTS}/{POST_ID}"
SWITCH = "_release_enabled"  # công tắc Hẹn giờ / Đăng ngay (mặc định tắt)
TIMEZONE = "Asia/Ho_Chi_Minh"
SEND_DRAFT = "📤 Gửi nháp"
PUBLISH_NOW = "🚀 Gửi và đăng công khai ngay"
BAIT = "MỒI-lỗi-gốc <b>evil</b>"


# ============================================================ dữ liệu, WordPress giả


def http_date() -> str:
    return format_datetime(datetime.now(UTC), usegmt=True)


@pytest.fixture
def live(site, monkeypatch):
    """WordPress giả cho Hẹn giờ / Đăng ngay: bài 501 trả kèm header ``Date`` (giờ máy chủ = giờ
    thật), tài khoản có quyền đăng bài, website giờ Việt Nam. Lệnh chuyển trạng thái trả đúng như
    đã gửi; ``answers`` (lần lượt) thay câu trả lời của lệnh chuyển."""

    class Live:
        answers: list = []
        site = None

    Live.site = site
    info = ConnectionInfo(
        "ProMetal",
        BASE_URL,
        "Biên tập",
        ("editor",),
        True,
        True,
        True,
        timezone_string=TIMEZONE,
        gmt_offset=7.0,
    )

    def get_post(_request):
        return (200, {"id": POST_ID, "status": "draft"}, {"Date": http_date()})

    def post_post(request):
        body = ui.body_of(request)
        if "status" in body and Live.answers:
            answer = Live.answers.pop(0)
            return answer(request) if callable(answer) else answer
        return {"id": POST_ID, "status": "draft", **body}

    site.fake.on("GET", POST, get_post)
    site.fake.on("POST", POST, post_post)
    monkeypatch.setattr(WordPressClient, "check_connection", lambda self: info)
    return Live


def paths(site) -> list[tuple[str, str]]:
    return [(request.method, ui.path_of(request)) for request in site.fake.requests]


def release_bodies(site) -> list[dict]:
    """Thân các lệnh chuyển trạng thái (``POST`` bài 501 có ``status``)."""
    return [
        ui.body_of(r)
        for r in site.fake.requests
        if (r.method, ui.path_of(r)) == ("POST", POST) and "status" in (ui.body_of(r) or {})
    ]


def send_button(at):
    return next(b for b in at.button if b.key == "wp-send")


def open_snap(project_root, snap: DraftSnapshot):
    """Mở nháp ``snap`` ở trang Soạn bài (bài không cần có chỗ cần ảnh)."""
    ui.store().save(snap)
    at = ui.pages.open_page(project_root, "write.py")
    return run_ok(button(at, "Mở", key=f"open-{snap.id}").click().run())


def to_mode(at, mode: str, *, switch: bool = True):
    """Sang bước Xuất bản, chọn hình thức ``mode`` (bật công tắc Hẹn giờ / Đăng ngay nếu cần)."""
    if switch:
        at.session_state[SWITCH] = True
    ui.to_publish(at)
    return run_ok(at.segmented_control(key="_wp_mode").set_value(mode).run())


def confirm(at):
    return run_ok(at.checkbox(key="_wp_confirm").check().run())


def tomorrow_8am_utc() -> datetime:
    """Giờ hẹn mặc định: ngày mai lúc 08:00 giờ Việt Nam (``[plan].default_time``)."""
    today = datetime.now(ZoneInfo(TIMEZONE)).date()
    return local_to_utc(today + timedelta(days=1), datetime.min.time().replace(hour=8), TIMEZONE)


MARKDOWN_ARTICLE = DraftSnapshot(
    step=2,
    keyword="sửa cổng inox",
    article_title="Sửa cổng inox Tân Phú",
    parts=[
        DraftPart(heading="Mở bài", versions=["Cổng inox ở Tân Phú **bị xệ** cánh."]),
        DraftPart(heading="Bản lề cổng", versions=["- Thay cả cặp bản lề\n- Tra dầu mỗi năm"]),
    ],
)


# ============================================================ Nháp: gói của bộ dựng


def test_draft_sends_exactly_the_builder_package(project_root, site, sent):
    """LC-T094-36: Nháp cũng gửi đúng HTML do bộ dựng T-096 trả (Markdown ra đậm, danh sách; mỗi
    phần một khối, ``<h2>`` cho tiêu đề phần), không đường nào khác ghép HTML. Bài không có link
    nội bộ thì không gọi website trước lệnh tải ảnh, tạo nháp."""
    at = open_snap(project_root, MARKDOWN_ARTICLE.model_copy(update={"id": "a" * 32}))
    ui.to_publish(at)
    assert site.fake.requests == []
    run_ok(button(at, SEND_DRAFT).click().run())
    ((title, parts),) = sent.calls
    expected = build_article(
        title="Sửa cổng inox Tân Phú",
        parts=[ArticlePart(p.heading, p.versions[0]) for p in MARKDOWN_ARTICLE.parts],
        index=SiteIndex(site=BASE_URL, fetched_at=datetime.now(UTC), items=()),
    )
    assert title == expected.title
    assert parts == list(expected.sections)
    assert "<strong>bị xệ</strong>" in parts[0] and "<ul>" in parts[1]
    assert paths(site) == [("POST", POSTS)]
    (post,) = site.posts()
    assert post["status"] == "draft"


def test_draft_review_lists_every_link_and_bare_address(project_root, site):
    """LC-T094-37: Nháp có màn hình rút gọn nhưng vẫn có bảng mọi link và địa chỉ trần, chữ
    thường (ô bảng), bỏ ký tự đổi hướng chữ (LC-T094-3)."""
    snap = MARKDOWN_ARTICLE.model_copy(
        update={
            "id": "b" * 32,
            "parts": [
                DraftPart(heading="Mở bài", versions=["Gọi thợ qua www.vi‮du-tho.com nhé."]),
                DraftPart(heading="Bản lề", versions=["Xem thêm tại https://x.example/a."]),
            ],
        }
    )
    at = open_snap(project_root, snap)
    ui.to_publish(at)
    tables = [t.value.to_dict("records") for t in at.dataframe]
    bare = next(rows for rows in tables if rows and "Địa chỉ" in rows[0] and "Loại" in rows[0])
    shown = [row["Địa chỉ"] for row in bare]
    assert any("www.vi" in text for text in shown) and any("x.example" in text for text in shown)
    assert not any("‮" in text for text in shown)
    assert any("Bài không có link nào" in c.value for c in at.caption)


def test_review_flags_odd_hosts_and_sends_no_zero_width(project_root, site, sent):
    """Thiết kế mục 7 dòng 3, 7, 11 (LC-T039-1, T-031): địa chỉ trong bài hiện ở bảng với tên máy
    dạng ASCII (``xn--…``), cờ cho tên máy ngoài ASCII và «@» trong phần tên máy; HTML gửi đi
    không còn ký tự rộng 0 mà T-031 chèn vào địa chỉ trần."""
    kirin = "https://suachuacuas" + chr(0x0430) + "t.com/gia"  # «а» Nga trong tên
    kirin_tld = "https://suachuacuasat.c" + chr(0x043E) + "m/lien-he"  # «о» Nga ở đuôi
    body = break_autolinks(
        f"Xem bảng giá {kirin}, {kirin_tld} hay https://suachuacuasat.com@evil.example/x. "
        "Gọi www.vi-du.com nhé."
    )
    assert chr(0x200B) in body
    snap = MARKDOWN_ARTICLE.model_copy(
        update={"id": "7" * 32, "parts": [DraftPart(heading="Mở bài", versions=[body])]}
    )
    at = open_snap(project_root, snap)
    ui.to_publish(at)
    (bare,) = [
        t.value.to_dict("records")
        for t in at.dataframe
        if "Địa chỉ" in t.value.columns and "Chữ neo" not in t.value.columns
    ]
    hosts = {row["Tên máy (dạng ASCII)"]: row["Dấu hiệu lạ"] for row in bare}
    puny = [host for host in hosts if "xn--" in host]  # thiết kế mục 7 dòng 11: cả hai địa chỉ
    assert len(puny) == 2 and all("ngoài ASCII" in hosts[host] for host in puny)
    assert "«@»" in hosts["evil.example"]
    run_ok(button(at, SEND_DRAFT).click().run())
    ((_title, parts),) = sent.calls
    assert not any(chr(0x200B) in part for part in parts)
    (post,) = site.posts()
    assert chr(0x200B) not in post["content"] and "www.vi-du.com" in post["content"]


def published_item() -> PublishedItem:
    return PublishedItem(
        id=11,
        type="post",
        slug="thay-ban-le",
        link=f"{BASE_URL}/thay-ban-le/",
        title="Cách thay bản lề cổng inox",
    )


def test_internal_link_reloads_listing_right_before_sending(project_root, site, sent, monkeypatch):
    """LC-T094-36 (thiết kế 4 dòng 9): bài có link nội bộ thì tải lại danh sách bài ngay trước khi
    dựng gói sẽ gửi (trước mọi lệnh ghi); link nằm trong HTML gửi đi, có dòng trong bảng link."""
    calls: list[int] = []

    def list_published(self):
        calls.append(len(site.fake.requests))  # số lệnh đã gửi tới website lúc tải danh sách
        return PublishedList([published_item()])

    monkeypatch.setattr(WordPressClient, "list_published", list_published)
    snap = MARKDOWN_ARTICLE.model_copy(
        update={
            "id": "c" * 32,
            "seo": DraftSeo(links=[DraftLink(section=1, anchor="Thay cả cặp bản lề", post_id=11)]),
        }
    )
    at = open_snap(project_root, snap)
    ui.to_publish(at)
    (links,) = [t.value.to_dict("records") for t in at.dataframe if "Chữ neo" in t.value.columns]
    assert links[0]["Chữ neo"] == "Thay cả cặp bản lề" and links[0]["Loại"] == "Nội bộ"
    before = len(calls)
    run_ok(button(at, SEND_DRAFT).click().run())
    assert len(calls) == before + 1 and calls[-1] == 0  # tải lại trước mọi lệnh ghi
    ((_title, parts),) = sent.calls
    assert f'<a href="{BASE_URL}/thay-ban-le/">Thay cả cặp bản lề</a>' in parts[1]


def test_review_cells_cannot_become_excel_formulas(project_root, site, monkeypatch):
    """Loại LC-T101-1 (Lá Chắn T-101): ô bảng xác nhận mở đầu bằng ``=``, ``+``, ``-``, ``@`` được
    thêm một dấu cách đầu (``sync.safe_text``): tải CSV từ thanh công cụ của bảng rồi mở bằng
    Excel thì không thành công thức. Chữ gửi lên website không đổi."""
    monkeypatch.setattr(
        WordPressClient, "list_published", lambda self: PublishedList([published_item()])
    )
    snap = MARKDOWN_ARTICLE.model_copy(
        update={
            "id": "8" * 32,
            "parts": [
                DraftPart(heading="Mở bài", versions=["Cổng inox ở Tân Phú bị xệ cánh."]),
                DraftPart(heading="Bản lề", versions=["=HYPERLINK cửa sắt là cách gọi vui."]),
            ],
            "seo": DraftSeo(links=[DraftLink(section=1, anchor="=HYPERLINK cửa sắt", post_id=11)]),
        }
    )
    at = open_snap(project_root, snap)
    ui.to_publish(at)
    (links,) = [t.value.to_dict("records") for t in at.dataframe if "Chữ neo" in t.value.columns]
    assert links[0]["Chữ neo"] == " =HYPERLINK cửa sắt"
    cells = [
        value
        for table in at.dataframe
        for row in table.value.to_dict("records")
        for value in row.values()
        if isinstance(value, str)
    ]
    assert not any(value.startswith(("=", "+", "-", "@", "\t", "\r")) for value in cells)


def test_seo_links_table_cells_cannot_become_excel_formulas(project_root, seo_ai, wordpress):
    """LC-T101-1 ở bước SEO: bảng liên kết nội bộ (``st.data_editor``, có nút tải CSV) hiện cụm từ
    AI chọn và tên bài trên website qua ``safe_text`` (thêm một dấu cách đầu cho ô dạng công
    thức); nháp vẫn giữ đúng cụm từ, cột «Dùng» vẫn đọc lại đúng."""
    title = '=WEBSERVICE("https://evil.example") cổng inox'
    wordpress.items = [seo_ui.published(11, title, "cong-inox")]
    snap = ui.article(seo=DraftSeo(links=[DraftLink(section=1, anchor="=SUM cửa sắt", post_id=11)]))
    at, _pid = ui.open_article(project_root, snap)
    at.session_state["step"] = 3
    run_ok(at.run())
    (rows,) = [
        t.value.to_dict("records") for t in at.dataframe if "Cụm từ trong bài" in t.value.columns
    ]
    assert rows == [{"Dùng": True, "Cụm từ trong bài": " =SUM cửa sắt", "Trỏ tới bài": " " + title}]
    assert [link.anchor for link in at.session_state["seo_links"]] == ["=SUM cửa sắt"]


def test_changed_between_view_and_click_sends_nothing(project_root, site, sent, monkeypatch):
    """LC-T094-38: lúc bấm dựng lại gói (danh sách bài vừa tải lại khác: bài đích đổi địa chỉ) và
    so mã băm với bài người dùng vừa xem: khác thì không gửi gì, báo xem lại."""
    links = [PublishedList([published_item()])]

    def list_published(self):
        return links[0]

    monkeypatch.setattr(WordPressClient, "list_published", list_published)
    snap = MARKDOWN_ARTICLE.model_copy(
        update={
            "id": "d" * 32,
            "seo": DraftSeo(links=[DraftLink(section=1, anchor="Thay cả cặp bản lề", post_id=11)]),
        }
    )
    at = open_snap(project_root, snap)
    ui.to_publish(at)
    moved = PublishedItem(
        id=11, type="post", slug="ban-le", link=f"{BASE_URL}/ban-le/", title="Bản lề"
    )
    links[0] = PublishedList([moved])
    run_ok(button(at, SEND_DRAFT).click().run())
    assert sent.calls == [] and site.fake.requests == []
    assert any("Bài vừa thay đổi sau khi bạn xem lại" in e.value for e in at.error)


# ============================================================ công tắc mặc định tắt


@pytest.mark.parametrize("mode", ["Hẹn giờ", "Đăng ngay"])
def test_switch_off_hides_schedule_and_publish(project_root, site, mode, monkeypatch):
    """LC-T094-41: công tắc Hẹn giờ / Đăng ngay mặc định tắt: không có nút gửi, câu nói rõ lý do,
    không có đường nào tới ``release_draft`` (không lệnh nào tới website)."""
    called = []
    monkeypatch.setattr(WordPressClient, "release_draft", lambda self, *a, **k: called.append(a))
    at = open_snap(project_root, MARKDOWN_ARTICLE.model_copy(update={"id": "e" * 32}))
    to_mode(at, mode, switch=False)
    assert not any(b.key == "wp-send" for b in at.button)
    assert any("Hẹn giờ và Đăng ngay đang **tắt**" in i.value for i in at.info)
    assert site.fake.requests == [] and called == []


# ============================================================ Hẹn giờ


def test_schedule_flow_confirms_then_releases_last(project_root, root, fake_ai, live):
    """Thiết kế 3.2, 3.5; LC-T094-37, -38; Lá Chắn T-099 đk 2: màn hình xác nhận đầy đủ (giờ Việt
    Nam kèm thứ, bài, SEO, ảnh, link); chưa tick thì nút khóa; tick rồi gửi: tải ảnh → tạo nháp →
    ảnh đại diện → **lệnh cuối cùng** hẹn giờ đúng ``date_gmt`` của ``local_to_utc``; nháp ghi
    «đã hẹn giờ»."""
    at, _pid = ui.ready_image(project_root)
    to_mode(at, "Hẹn giờ")
    when = tomorrow_8am_utc()
    label = schedule_label(when, TIMEZONE)
    assert any(label in m.value for m in at.markdown)  # «Thứ …, dd/mm/yyyy lúc 08:00 (giờ …)»
    assert "Hình thức:" in "\n".join(m.value for m in at.markdown)
    assert send_button(at).disabled  # chưa tick xác nhận
    assert send_button(at).label.startswith("📅 Gửi và hẹn giờ ")
    confirm(at)
    assert not send_button(at).disabled
    run_ok(send_button(at).click().run())
    sequence = paths(live.site)
    assert sequence[0] == ("POST", MEDIA) and ("POST", POSTS) in sequence
    assert sequence[-2:] == [("GET", POST), ("POST", POST)]  # hỏi còn nháp, rồi chuyển: cuối cùng
    assert release_bodies(live.site) == [{"status": "future", "date_gmt": date_gmt_text(when)}]
    assert any("Đã hẹn giờ đăng bài" in s.value for s in at.success)
    saved = ui.store().load_send_state(at.session_state["draft_id"])
    assert (saved.mode, saved.released, saved.release_unknown, saved.pending) == (
        "future",
        True,
        False,
        False,
    )
    assert saved.scheduled_for == when and saved.post_id == POST_ID
    assert send_button(at).disabled  # đã gửi: phải xác nhận tạo thêm bài mới


def test_send_uses_a_fresh_client_made_in_the_click(project_root, root, fake_ai, live, monkeypatch):
    """Lá Chắn T-099 L2-1, L2-2: lần bấm tạo client mới; tạo nháp và lệnh hẹn giờ chạy trên cùng
    client đó, không phải client lúc vẽ trang (hỏi quyền đăng bài)."""
    used: dict[str, object] = {}
    originals = {
        name: getattr(WordPressClient, name)
        for name in ("check_connection", "create_draft_with_images", "release_draft")
    }

    def spy(name):
        def call(self, *args, **kwargs):
            used[name] = self
            return originals[name](self, *args, **kwargs)

        return call

    for name in originals:
        monkeypatch.setattr(WordPressClient, name, spy(name))
    at, _pid = ui.ready_image(project_root)
    to_mode(at, "Hẹn giờ")
    confirm(at)
    run_ok(send_button(at).click().run())
    assert used["create_draft_with_images"] is used["release_draft"]
    assert used["release_draft"] is not used["check_connection"]
    assert len(release_bodies(live.site)) == 1


def test_untick_when_schedule_changes_after_confirming(project_root, root, fake_ai, live):
    """LC-T094-38: tick rồi đổi giờ hẹn: mã băm khác, ô tick bị bỏ, phải xem lại rồi tick lại."""
    at, _pid = ui.ready_image(project_root)
    to_mode(at, "Hẹn giờ")
    confirm(at)
    at.session_state["_wp_time"] = datetime.min.time().replace(hour=9, minute=30)
    run_ok(at.run())
    assert at.checkbox(key="_wp_confirm").value is False
    assert any("app đã bỏ tick" in w.value for w in at.warning)
    assert send_button(at).disabled
    assert live.site.fake.requests == []


@pytest.mark.parametrize("change", ["chữ bài", "alt ảnh", "công tắc SEO"])
def test_untick_when_article_image_or_seo_switch_changes(project_root, root, fake_ai, live, change):
    """LC-T094-38: tick rồi sửa chữ bài, alt ảnh hay bật «Ghi SEO lên website»: mã băm khác, ô
    tick bị bỏ, nút khóa, không gửi gì."""
    at, pid = ui.ready_image(project_root)
    to_mode(at, "Hẹn giờ")
    confirm(at)
    assert not send_button(at).disabled
    if change == "chữ bài":
        first = at.session_state["part_ids"][0]
        at.session_state[f"texts-{first}"] = ["Mở bài đã sửa sau khi xác nhận."]
        at.session_state[f"ver-{first}"] = 0
        run_ok(at.run())
    elif change == "alt ảnh":
        at.session_state[f"alt-{pid}"] = "Bản lề cổng inox đã thay, chụp gần"
        run_ok(at.run())
    else:
        run_ok(at.toggle(key="seo_write").set_value(True).run())
    assert at.checkbox(key="_wp_confirm").value is False
    assert send_button(at).disabled
    # Bật «Ghi SEO» thì tải danh sách bài để kiểm trùng (chỉ đọc, T-041); không lệnh ghi nào.
    assert [r for r in live.site.fake.requests if r.method != "GET"] == []


def test_schedule_too_soon_is_blocked(project_root, root, fake_ai, live):
    """Thiết kế 3.4: giờ hẹn chưa tới 10 phút nữa (hay đã qua) là Chặn: nút khóa, không gửi gì."""
    at, _pid = ui.ready_image(project_root)
    now = datetime.now(ZoneInfo(TIMEZONE))
    at.session_state["_wp_day"] = now.date()
    at.session_state["_wp_time"] = (
        (now + timedelta(minutes=2)).time().replace(second=0, microsecond=0)
    )
    to_mode(at, "Hẹn giờ")
    if at.session_state["_wp_day"] != now.date():  # vừa qua nửa đêm: ô ngày tự sang ngày mai
        pytest.skip("chạy đúng lúc qua ngày")
    assert any("ít nhất 10 phút" in e.value or "đã qua" in e.value for e in at.error)
    assert send_button(at).disabled


def test_release_needs_publish_right(project_root, root, fake_ai, live, monkeypatch):
    """Thiết kế 3.1: tài khoản thiếu quyền ``publish_posts`` thì khóa nút, nói rõ lý do."""
    info = ConnectionInfo("ProMetal", BASE_URL, "Tác giả", ("author",), True, False, True)
    monkeypatch.setattr(WordPressClient, "check_connection", lambda self: info)
    at, _pid = ui.ready_image(project_root)
    to_mode(at, "Hẹn giờ")
    confirm(at)
    assert any("không có quyền đăng bài" in e.value for e in at.error)
    assert send_button(at).disabled


# ============================================================ Đăng ngay


def test_publish_now_needs_seo_written(project_root, root, fake_ai, live):
    """Thiết kế 3.2; LC-T094-39: Đăng ngay khi SEO chưa ghi lên website là Chặn (nút khóa dù đã
    tick); nút ghi rõ «đăng công khai ngay»."""
    at, _pid = ui.ready_image(project_root)
    to_mode(at, "Đăng ngay")
    assert any("Hiện công khai ngay khi bấm" in m.value for m in at.markdown)
    confirm(at)
    assert send_button(at).label == PUBLISH_NOW
    assert any("Đăng ngay mà SEO chưa ghi lên website" in e.value for e in at.error)
    assert send_button(at).disabled


def test_publish_now_with_seo_written(project_root, root, fake_ai, live, monkeypatch):
    """Đăng ngay khi bật «Ghi SEO lên website»: chưa tick xác nhận thì nút khóa (đăng ngay cần
    xác nhận, ý của ``test_publish_now_requires_confirmation`` cũ); ghi SEO rồi mới đăng
    (Abilities chỉ ghi được bài còn nháp); lệnh đăng là lệnh cuối cùng, thân đúng
    ``{"status": "publish"}``."""
    from seo_app.wordpress.client import SeoWriteResult

    order: list[str] = []
    original_release = WordPressClient.release_draft

    def seo(self, post_id, **fields):
        order.append("seo")
        return SeoWriteResult(True, route="meta", message="Đã ghi SEO vào hộp SiteSEO.")

    def release(self, post_id, **kwargs):
        order.append("release")
        return original_release(self, post_id, **kwargs)

    monkeypatch.setattr(WordPressClient, "set_seo_meta", seo)
    monkeypatch.setattr(WordPressClient, "release_draft", release)
    at, _pid = ui.ready_image(project_root)
    to_mode(at, "Đăng ngay")
    run_ok(at.toggle(key="seo_write").set_value(True).run())
    assert send_button(at).disabled and order == []  # chưa tick «Tôi đã đọc lại…»
    confirm(at)
    assert not send_button(at).disabled
    run_ok(send_button(at).click().run())
    assert order == ["seo", "release"]
    assert release_bodies(live.site) == [{"status": "publish"}]
    assert any("Đã đăng bài công khai" in s.value for s in at.success)
    saved = ui.store().load_send_state(at.session_state["draft_id"])
    assert (saved.mode, saved.released) == ("publish", True)


# ============================================================ lỗi giữa chừng


def answer(status: int, body: object):
    return lambda _request: (status, body, {})


def test_release_unsure_locks_and_never_resends(project_root, root, fake_ai, live):
    """LC-T094-25, -39: lệnh hẹn giờ lỗi 5xx (không biết đã chạy chưa): «có thể đã hẹn giờ», khóa
    gửi lại, dặn kiểm trang quản trị, không tự gửi lại; nháp ghi «không rõ kết quả»."""
    live.answers = [answer(502, {"code": "bad_gateway", "message": BAIT})]
    at, _pid = ui.ready_image(project_root)
    to_mode(at, "Hẹn giờ")
    confirm(at)
    run_ok(send_button(at).click().run())
    assert len(release_bodies(live.site)) == 1
    assert any("có thể đã" in e.value for e in at.error)
    assert not any(BAIT in text for text in ui.texts(at))
    saved = ui.store().load_send_state(at.session_state["draft_id"])
    assert saved.release_unknown and not saved.released
    run_ok(at.run())
    assert any("có thể đã" in e.value and "hẹn giờ" in e.value for e in at.error)
    assert send_button(at).disabled
    assert len(release_bodies(live.site)) == 1


def test_schedule_that_went_public_is_urgent(project_root, root, fake_ai, live):
    """LC-T094-25: chọn hẹn giờ mà website đăng ngay: câu báo khẩn cố định, nháp ghi đúng là đã
    đăng công khai, không gửi thêm lệnh nào vào bài."""
    live.answers = [answer(200, {"id": POST_ID, "status": "publish", "date_gmt": "x"})]
    at, _pid = ui.ready_image(project_root)
    to_mode(at, "Hẹn giờ")
    confirm(at)
    run_ok(send_button(at).click().run())
    assert any("KHẨN" in e.value for e in at.error)
    saved = ui.store().load_send_state(at.session_state["draft_id"])
    assert (saved.mode, saved.released, saved.scheduled_for) == ("publish", True, None)
    assert len(release_bodies(live.site)) == 1


def test_release_refused_keeps_draft(project_root, root, fake_ai, live):
    """Lời từ chối rõ ràng (403): bài vẫn là nháp, câu báo nói rõ; nháp ghi «đã gửi nháp, chưa
    hẹn giờ»; mở lại thì nhắc hẹn giờ trong trang quản trị."""
    live.answers = [answer(403, {"code": "rest_cannot_publish", "message": BAIT})]
    at, _pid = ui.ready_image(project_root)
    to_mode(at, "Hẹn giờ")
    confirm(at)
    run_ok(send_button(at).click().run())
    assert any("bài vẫn là nháp" in w.value for w in at.warning)
    saved = ui.store().load_send_state(at.session_state["draft_id"])
    assert (saved.mode, saved.released, saved.release_unknown) == ("future", False, False)
    fresh = ui.pages.open_page(project_root, "write.py")
    run_ok(button(fresh, "Mở", key=f"open-{at.session_state['draft_id']}").click().run())
    ui.to_publish(fresh)
    assert any("chưa hẹn giờ/đăng" in i.value for i in fresh.info)


def test_unexpected_error_around_release_counts_as_maybe_sent(
    project_root, root, fake_ai, live, monkeypatch
):
    """Lá Chắn T-099 L2-3: lỗi lạ quanh ``release_draft`` (không phải ``ReleaseError``): câu cố định
    «có thể đã…», khóa gửi lại, không hiện lời lỗi gốc."""

    def broken(self, post_id, **kwargs):
        raise RuntimeError(BAIT)

    monkeypatch.setattr(WordPressClient, "release_draft", broken)
    at, _pid = ui.ready_image(project_root)
    to_mode(at, "Hẹn giờ")
    confirm(at)
    run_ok(send_button(at).click().run())
    assert any("lỗi không mong đợi" in e.value for e in at.error)
    assert not any(BAIT in text for text in ui.texts(at))
    saved = ui.store().load_send_state(at.session_state["draft_id"])
    assert saved.release_unknown


def test_interrupted_after_release_keeps_result_and_lock(
    project_root, root, fake_ai, live, monkeypatch
):
    """LC-T094-39: lần chạy bị dừng ngay khi thoát vòng quay «Đang gửi bài…» (bấm nút khác): lần
    chạy sau vẫn có kết quả hẹn giờ (ghi trước lệnh ``st.*`` kế tiếp) và vẫn khóa gửi lại."""
    original = st.spinner

    from contextlib import contextmanager

    @contextmanager
    def spinner(text="", *args, **kwargs):
        with original(text, *args, **kwargs):
            yield
        if text.startswith("Đang gửi bài"):
            raise StopException()

    at, _pid = ui.ready_image(project_root)
    to_mode(at, "Hẹn giờ")
    confirm(at)
    monkeypatch.setattr(st, "spinner", spinner)
    send_button(at).click().run()
    monkeypatch.setattr(st, "spinner", original)
    saved = ui.store().load_send_state(at.session_state["draft_id"])
    assert saved.released and saved.mode == "future"
    run_ok(at.run())
    assert any("Đã hẹn giờ đăng bài" in s.value for s in at.success)
    assert send_button(at).disabled
    assert len(release_bodies(live.site)) == 1


# ============================================================ bấm hai lần, hai tab


def test_double_click_releases_once(project_root, root, fake_ai, live, monkeypatch):
    """Bấm đúp nút hẹn giờ: cú bấm thứ hai tới sau khi lần trước đã gửi xong: không tạo thêm nháp,
    không gửi thêm lệnh chuyển (SL-T056-1, LC-T094-39)."""
    at, _pid = ui.ready_image(project_root)
    to_mode(at, "Hẹn giờ")
    confirm(at)
    label = send_button(at).label
    run_ok(send_button(at).click().run())
    original = st.button
    pending = [True]

    def second_click(text, *args, **kwargs):
        clicked = original(text, *args, **kwargs)
        if text == label and pending:
            pending.pop()
            return True
        return clicked

    monkeypatch.setattr(st, "button", second_click)
    run_ok(at.run())
    assert len(live.site.posts()) == 1 and len(release_bodies(live.site)) == 1


def test_two_tabs_only_one_release(project_root, root, fake_ai, live):
    """Hai tab cùng mở một bài ở bước Xuất bản, cùng tick xác nhận: tab A gửi; tab B vẽ lại thì
    thấy khóa «đã gửi và hẹn giờ», bấm cũng không gửi gì: một bài nháp, một lệnh hẹn giờ."""
    at, _pid = ui.ready_image(project_root)
    draft = at.session_state["draft_id"]
    to_mode(at, "Hẹn giờ")
    confirm(at)
    other = ui.pages.open_page(project_root, "write.py")
    run_ok(button(other, "Mở", key=f"open-{draft}").click().run())
    to_mode(other, "Hẹn giờ")
    confirm(other)
    run_ok(send_button(at).click().run())
    run_ok(send_button(other).click().run())
    assert len(live.site.posts()) == 1 and len(release_bodies(live.site)) == 1
    assert any("đã gửi và hẹn giờ" in i.value for i in other.info)
    assert send_button(other).disabled


def test_other_tab_sends_while_preparing(project_root, root, fake_ai, live, monkeypatch):
    """Cuộc đua hai tab (T-089, SL-T086-1) ở Hẹn giờ: tab này đã bấm (nút còn mở), tab kia ghi
    «đang gửi» đúng lúc tab này đọc ảnh để nén: tab này không ghi được «đang gửi» nên không gửi gì
    lên website (không tạo nháp, không lệnh hẹn giờ), báo rõ."""
    from seo_app.images.folders import ImageLibrary
    from seo_app.storage.drafts import SendState

    at, _pid = ui.ready_image(project_root)
    draft = at.session_state["draft_id"]
    to_mode(at, "Hẹn giờ")
    confirm(at)
    original = ImageLibrary.read_image_bytes
    once = [True]

    def read(self, ref):
        if once:
            once.pop()
            ui.store().save_send_state(
                draft,
                SendState.now(
                    pending=True, post_id=None, mode="future", scheduled_for=tomorrow_8am_utc()
                ),
            )
        return original(self, ref)

    monkeypatch.setattr(ImageLibrary, "read_image_bytes", read)
    run_ok(send_button(at).click().run())
    assert live.site.fake.requests == []
    assert any("Chưa gửi gì lên website" in e.value for e in at.error)


# ============================================================ chuyên mục, chữ thuần


def test_categories_loaded_on_click_and_sent(project_root, site, sent):
    """Thiết kế dòng T-102: chuyên mục thật từ ``list_categories`` (chỉ đọc, tải khi bấm), tên
    chuyên mục hiện chữ thường (bỏ ký tự đổi hướng); chuyên mục đã chọn đi vào lệnh tạo nháp."""
    site.fake.on(
        "GET",
        "/wp-json/wp/v2/categories",
        (
            200,
            [
                {"id": 3, "name": "Cổng inox", "slug": "cong-inox", "count": 4},
                {"id": 5, "name": "Lan ‮can", "slug": "lan-can", "count": 1},
            ],
            {"X-WP-TotalPages": "1"},
        ),
    )
    at = open_snap(project_root, MARKDOWN_ARTICLE.model_copy(update={"id": "f" * 32}))
    ui.to_publish(at)
    assert site.fake.requests == []  # chỉ xem: không gọi website
    run_ok(button(at, "🔄 Tải chuyên mục từ website").click().run())
    box = at.multiselect(key="_wp_cats")
    assert "‮" not in "".join(box.options)
    run_ok(box.set_value([3]).run())
    run_ok(button(at, SEND_DRAFT).click().run())
    (post,) = site.posts()
    assert post["categories"] == [3]


def test_review_shows_site_and_ai_text_plain(project_root, root, fake_ai, live, monkeypatch):
    """LC-T094-3, -37: chữ trên màn hình xác nhận (tiêu đề, alt, link) hiện thuần: không HTML,
    không link Markdown bấm được, không ký tự đổi hướng chữ."""
    evil = "Sửa cổng [bấm](javascript:alert(1)) <b>đậm</b> ‮đảo"
    snap = ui.article(article_title=evil)
    at, _pid = ui.open_article(project_root, snap)
    ui.choose_real(at, _pid)
    ui.write_alt(at, _pid)
    ui.approve(at, _pid)
    to_mode(at, "Hẹn giờ")
    shown = "\n".join(t.value for t in at.text)
    assert "Tiêu đề bài:" in shown and "‮" not in shown
    html_blocks = [m.value for m in at.markdown if m.proto.allow_html]
    assert not any("javascript" in block or "<b>" in block for block in html_blocks)
    assert not any("](javascript:" in m.value for m in at.markdown if not m.proto.allow_html)


def test_date_label_has_weekday(project_root, root, fake_ai, live):
    """LC-T094-27: nhãn giờ hẹn có thứ, ngày, giờ Việt Nam, tính từ giờ đã chọn."""
    at, _pid = ui.ready_image(project_root)
    at.session_state["_wp_day"] = date(2099, 1, 1)  # quá một năm: Chặn, nhưng vẫn có nhãn
    to_mode(at, "Hẹn giờ")
    assert any("Thứ Năm, 01/01/2099 lúc 08:00 (giờ Việt Nam)" in c.value for c in at.caption)
    assert any("xa hơn một năm" in e.value for e in at.error)
    assert send_button(at).disabled


# ============================================================ kế hoạch (T-100, T-103)

KEY = "B-001"
OTHER_SHEET = "1" + "KhacSheet" * 4  # mã Sheet giả khác Sheet đang kết nối (chỉ để băm)
COL = {name: position for position, (name, _label) in enumerate(plan_model.SHEET_COLUMNS)}
TARGET = PublishedItem(
    id=12, type="page", slug="sua-cong-inox", link=f"{BASE_URL}/sua-cong-inox/", title="Sửa cổng"
)
NOTE = "Khách chị Lan 0903 123 456 hỏi cổng 304 giá 5 triệu, gần biển"


def plan_line(key: str = KEY, keyword: str = "sửa cổng inox", **fields) -> list:
    """Một dòng Sheet theo đúng thứ tự cột của ``HEADER``."""
    cells = [""] * len(HEADER)
    cells[COL["key"]], cells[COL["keyword"]] = key, keyword
    for name, value in fields.items():
        cells[COL[name]] = value
    return cells


def serial(day: date) -> int:
    """Ngày dạng số của Google Sheets."""
    return (day - date(1899, 12, 30)).days


def plan_ref_of(sheet: str = SHEET_ID) -> DraftPlanRef:
    return DraftPlanRef(
        key=KEY,
        sheet_hash=sheet_hash(sheet),
        status=plan_model.STATUS_WRITING,
        opened_at=datetime.now(UTC),
    )


@pytest.fixture(scope="module")
def private_key():
    return new_private_key()


@pytest.fixture
def plan(tmp_path, private_key, monkeypatch) -> FakePlanSheet:
    """Google Sheet giả có trạng thái (T-100) nối vào ``SheetsClient`` thật; trang lấy client qua
    ``SheetsClient.from_settings``. ``GOOGLE_SHEET_ID`` khai báo; bản lưu kế hoạch ở thư mục tạm.
    Dòng ``B-001`` đang «Đang viết»."""
    google = FakeGoogle()
    folder = tmp_path / "bi-mat"
    folder.mkdir()
    key_file = folder / "du-an-thu-0123abcd.json"
    key_file.write_text(json.dumps(key_info(private_key)), encoding="utf-8")
    project = tmp_path / "du-an"
    project.mkdir()
    account = load_service_account(key_file, project_root=project)
    client = SheetsClient(SHEET_ID, account, session=make_session(google), sleep=lambda _s: None)
    monkeypatch.setattr(SheetsClient, "from_settings", classmethod(lambda cls, *a, **k: client))
    monkeypatch.setenv("GOOGLE_SHEET_ID", SHEET_ID)
    monkeypatch.setattr(plan_cache, "DEFAULT_PLAN_CACHE_FILE", tmp_path / "plan_cache.sqlite")
    return FakePlanSheet(google, [HEADER, plan_line(status=plan_model.STATUS_WRITING)])


def start_from(project_root, key: str = KEY, keyword: str = "sửa cổng inox"):
    """Như nút «Viết bài» của T-101 (hợp đồng ``_start_plan_key``): đặt từ khóa của dòng vừa đọc
    lại và Mã bài rồi mở Soạn bài."""
    at = ui.pages.open_page(project_root, "write.py")
    at.session_state["_start_keyword"] = keyword
    at.session_state["_start_plan_key"] = key
    return run_ok(at.run())


def test_write_from_plan_rereads_row_fills_compose_and_marks_writing(project_root, site, plan):
    """Thiết kế 1.6, hợp đồng ``_start_plan_key`` (T-101), Lá Chắn T-100 đk 5, T-103 đk 2b: chỉ tin
    Mã bài: đọc lại đúng dòng (Mã bài viết khác dạng vẫn nhận), gắn ``DraftPlanRef``, điền sẵn ghi
    chú (che số điện thoại, nhắc giá), slug, trang dịch vụ đích (danh sách bài lưu trên máy), loại
    bài, ngày giờ hẹn; ghi «Đang viết» qua T-100. Không gọi WordPress (LC-T094-35)."""
    day = datetime.now(ZoneInfo(TIMEZONE)).date() + timedelta(days=20)
    plan.grid = [
        HEADER,
        plan_line(
            keyword="sửa cổng inox tại nhà",
            status=plan_model.STATUS_NEW,
            kind=plan_model.KIND_SERVICE,
            planned_date=serial(day),
            planned_time="9h30",
            title_hint="Sửa cổng inox tại nhà: 5 lỗi hay gặp",
            slug="sua-cong-inox-tai-nha",
            target_id=TARGET.link,
            notes=NOTE,
        ),
    ]
    SiteIndexStore().save(SiteIndex(site=BASE_URL, fetched_at=datetime.now(UTC), items=(TARGET,)))
    at = start_from(project_root, key="b-1", keyword="sửa cổng inox tại nhà")
    state = at.session_state
    assert state["keyword"] == "sửa cổng inox tại nhà"
    assert "_start_plan_key" not in state and "_start_keyword" not in state
    experience = state["real-Kinh nghiệm của xưởng"]
    assert plan_model.MASK in experience and "0903" not in experience and "gần biển" in experience
    assert state["seo_slug"] == "sua-cong-inox-tai-nha"
    assert state["_plan_required"] == (12,) and state["_plan_kind"] == plan_model.KIND_SERVICE
    assert (state["_wp_day"], state["_wp_time"]) == (day, time(9, 30))
    shown = " ".join(i.value for i in at.info)  # câu cố định, đã escape
    assert escape_markdown("Đã mở bài mới từ dòng kế hoạch B-001.") in shown
    assert "số điện thoại hay email" in shown and "nhắc giá" in shown
    assert escape_markdown("Đã cập nhật trạng thái dòng B-001") in shown
    assert plan.cell(2, COL["status"]) == plan_model.STATUS_WRITING
    assert plan.cell(2, COL["wp_post_id"]) == ""
    assert ui.store().list_plan_writes() == []
    saved = ui.store().load(state["draft_id"])
    assert (saved.plan.key, saved.plan.sheet_hash) == (KEY, sheet_hash(SHEET_ID))
    assert saved.plan.status == plan_model.STATUS_NEW  # trạng thái lúc mở (để kiểm xung đột)
    assert site.fake.requests == []
    reads = plan.reads  # đọc lại dòng (open_row), đọc lại trước khi ghi (write_status)
    run_ok(at.run())  # lần chạy sau: không đọc lại, không ghi lại
    assert plan.reads == reads == 2 and len(plan.updates) == 1
    at.session_state[SWITCH] = True
    ui.to_publish(at)
    run_ok(at.segmented_control(key="_wp_mode").set_value("Hẹn giờ").run())
    assert at.date_input(key="_wp_day").value == day
    assert at.time_input(key="_wp_time").value == time(9, 30)


def test_planned_title_is_only_a_hint(project_root, plan, fake_ai):
    """Thiết kế 1.6: «Tiêu đề dự kiến» chỉ hiện làm gợi ý ở bước Dàn ý (chữ thường), không vào lời
    dặn AI (Lá Chắn T-103 đk 2a: chữ kế hoạch chỉ qua từ khóa và chất liệu thật)."""
    hint = f"Tiêu đề <b>dự kiến</b> {chr(0x202E)}đảo"
    plan.grid = [HEADER, plan_line(title_hint=hint)]
    at = start_from(project_root)
    at.session_state["research"] = ui.RESEARCH
    at.session_state["step"] = 1
    run_ok(at.run())
    run_ok(button(at, "🧠 Tạo dàn ý").click().run())
    (shown,) = [t.value for t in at.text if t.value.startswith("Tiêu đề dự kiến trong kế hoạch: ")]
    assert chr(0x202E) not in shown and "<b>dự kiến</b>" in shown  # chữ thường, không thẻ
    assert not any("dự kiến</b>" in m.value for m in at.markdown)
    assert not any("dự kiến</b>" in str(call) for call in fake_ai.calls)


def test_write_from_plan_reopens_its_draft_without_reading_sheet(project_root, plan):
    """Thiết kế 1.6 bước 2; Lá Chắn T-100 đk 5: đã có nháp gắn Mã bài này **trên Sheet đang kết
    nối** thì mở nháp đó, không tạo nháp thứ hai, không đọc, không ghi Sheet. Nháp gắn Sheet khác
    thì không mở."""
    other = ui.store().save(DraftSnapshot(keyword="cổng sắt", plan=plan_ref_of(OTHER_SHEET)))
    mine = ui.store().save(DraftSnapshot(keyword="sửa cổng inox", plan=plan_ref_of()))
    at = start_from(project_root, keyword="sửa cổng inox")
    assert at.session_state["draft_id"] == mine.id != other.id
    assert plan.reads == 0 and plan.updates == []
    assert len(ui.store().list_drafts().drafts) == 2


def test_draft_of_another_sheet_is_not_reused(project_root, plan):
    """Lá Chắn T-100 đk 5: nháp gắn Mã bài B-001 của **Sheet khác** không được mở thay: bài mới,
    đọc lại dòng trên Sheet đang kết nối."""
    other = ui.store().save(DraftSnapshot(keyword="cổng sắt", plan=plan_ref_of(OTHER_SHEET)))
    at = start_from(project_root)
    assert at.session_state["draft_id"] != other.id
    assert plan.reads == 2  # đọc lại dòng, rồi đọc lại trước khi ghi «Đang viết»
    assert at.session_state["_plan_ref"].sheet_hash == sheet_hash(SHEET_ID)


@pytest.mark.parametrize("keyword", ["lan can cầu thang", "sửa cổng inox cũ"])
def test_plan_key_with_another_keyword_is_not_attached(project_root, plan, keyword):
    """G1 Soi Lỗi T-101: Mã bài chỉ được nhận khi đi cùng đúng lần bấm «Viết bài» trên dòng đó
    (từ khóa lần bấm trùng dòng đọc lại). Mã bài sót lại đi cùng từ khóa gõ tay, hay dòng vừa đổi
    từ khóa: không gắn ``DraftPlanRef``, không ghi Sheet, giữ từ khóa của lần bấm, câu báo."""
    at = start_from(project_root, keyword=keyword)
    assert at.session_state["keyword"] == keyword
    assert "_plan_ref" not in at.session_state
    assert plan.updates == [] and ui.store().list_plan_writes() == []
    assert any(escape_markdown("chưa gắn với dòng kế hoạch B-001") in i.value for i in at.info)


def test_plan_row_unreadable_opens_keyword_only(project_root, plan):
    """LC-T094-2: Sheet lỗi lúc đọc lại dòng: câu cố định (không chép lời máy chủ), bài mới chỉ có
    từ khóa, không gắn kế hoạch, không ghi gì."""
    plan.fail("read", (403, {"error": {"code": 403, "message": BAIT}}))
    at = start_from(project_root, keyword="sửa cổng inox")
    assert at.session_state["keyword"] == "sửa cổng inox"
    assert "_plan_ref" not in at.session_state
    assert any(escape_markdown("Chưa gắn bài với dòng kế hoạch B-001") in i.value for i in at.info)
    assert not any(BAIT in text for text in ui.texts(at))
    assert plan.updates == []


def test_plan_without_google_opens_keyword_only(project_root, plan, monkeypatch):
    """Chưa khai báo Google Sheets: câu báo, bài mới chỉ có từ khóa; không gọi Google."""
    monkeypatch.delenv("GOOGLE_SHEET_ID")
    at = start_from(project_root, keyword="sửa cổng inox")
    assert at.session_state["keyword"] == "sửa cổng inox"
    assert any("Chưa kết nối Google Sheets" in i.value for i in at.info)
    assert plan.reads == 0


def plan_article(draft_id: str, sheet: str = SHEET_ID) -> DraftSnapshot:
    return MARKDOWN_ARTICLE.model_copy(update={"id": draft_id, "plan": plan_ref_of(sheet)})


def test_draft_send_writes_plan_status_and_post_id(project_root, site, plan):
    """Thiết kế 1.7; LC-T094-40: gửi nháp xong ghi đúng các ô của dòng qua T-100 (Trạng thái «Đã
    gửi nháp», Mã bài WordPress, Cập nhật lúc; không có ngày đăng); câu báo cố định của T-100."""
    at = open_snap(project_root, plan_article("1" * 32))
    ui.to_publish(at)
    run_ok(button(at, SEND_DRAFT).click().run())
    assert plan.cell(2, COL["status"]) == plan_model.STATUS_DRAFT_SENT
    assert plan.cell(2, COL["wp_post_id"]) == POST_ID
    assert plan.cell(2, COL["published_at"]) == ""
    written = {column for _row, column, _value in plan.written_cells()}
    assert written == {COL["status"], COL["wp_post_id"], COL["updated_at"]}
    assert any(escape_markdown("Đã cập nhật trạng thái dòng B-001") in i.value for i in at.info)
    assert at.session_state["_plan_ref"].wp_post_id == POST_ID
    assert ui.store().list_plan_writes() == []


def test_schedule_writes_scheduled_with_time(project_root, live, plan):
    """Thiết kế 1.7: hẹn giờ xong ghi «Đã hẹn giờ» và ngày đăng thực tế là giờ hẹn (giờ Việt Nam
    kèm múi giờ), sau lệnh chuyển trạng thái."""
    at = open_snap(project_root, plan_article("2" * 32))
    to_mode(at, "Hẹn giờ")
    confirm(at)
    run_ok(send_button(at).click().run())
    when = tomorrow_8am_utc().astimezone(ZoneInfo(TIMEZONE))
    assert plan.cell(2, COL["status"]) == plan_model.STATUS_SCHEDULED
    assert plan.cell(2, COL["published_at"]) == when.isoformat(sep=" ", timespec="minutes")
    assert plan.cell(2, COL["wp_post_id"]) == POST_ID


def test_schedule_that_went_public_writes_published(project_root, live, plan):
    """Hẹn giờ mà website đăng ngay (``went_public``): dòng ghi «Đã đăng», đúng với website."""
    live.answers = [answer(200, {"id": POST_ID, "status": "publish", "date_gmt": "x"})]
    at = open_snap(project_root, plan_article("3" * 32))
    to_mode(at, "Hẹn giờ")
    confirm(at)
    run_ok(send_button(at).click().run())
    assert plan.cell(2, COL["status"]) == plan_model.STATUS_PUBLISHED
    assert plan.cell(2, COL["published_at"]) != ""


def test_sheet_failure_after_send_keeps_debt_and_never_resends(project_root, site, plan):
    """Thiết kế 1.7; LC-T094-40: ghi Sheet lỗi sau khi gửi: bài đã lên website, không gửi lại;
    việc ghi còn nợ nằm trong kho nháp (thử lại ở trang Kế hoạch, chỉ ghi Sheet); câu cố định."""
    at = open_snap(project_root, plan_article("4" * 32))
    ui.to_publish(at)
    plan.fail("read", (403, {"error": {"code": 403, "message": BAIT}}))
    run_ok(button(at, SEND_DRAFT).click().run())
    ((draft, write),) = ui.store().list_plan_writes()
    assert draft == "4" * 32
    assert (write.status, write.wp_post_id) == (plan_model.STATUS_DRAFT_SENT, POST_ID)
    assert plan.updates == []
    assert any(escape_markdown("Chưa ghi được trạng thái dòng B-001") in i.value for i in at.info)
    assert not any(BAIT in text for text in ui.texts(at))
    run_ok(at.run())
    assert len(site.posts()) == 1


def test_draft_from_another_sheet_is_blocked_and_kept(project_root, site, plan):
    """Lá Chắn T-100 (LC-T100-3): nháp mở từ Sheet khác Sheet đang kết nối: không đọc, không ghi
    Sheet đang kết nối (``BLOCKED``), hiện câu báo, giữ việc còn nợ."""
    at = open_snap(project_root, plan_article("5" * 32, sheet=OTHER_SHEET))
    ui.to_publish(at)
    run_ok(button(at, SEND_DRAFT).click().run())
    assert plan.reads == 0 and plan.updates == []
    assert any("mở từ một Google Sheet khác" in i.value for i in at.info)
    ((_draft, write),) = ui.store().list_plan_writes()
    assert write.sheet_hash == sheet_hash(OTHER_SHEET)


def test_plan_kind_and_target_reach_link_choice(project_root, seo_ai, wordpress, monkeypatch):
    """Thiết kế 1.6: loại trang và trang dịch vụ đích của dòng kế hoạch vào ``select_candidates``
    (``kind``, ``required``) ở bước SEO."""
    seen: list[dict] = []
    original = onpage_links.select_candidates

    def spy(index, **kwargs):
        seen.append(kwargs)
        return original(index, **kwargs)

    monkeypatch.setattr(onpage_links, "select_candidates", spy)
    at, _pid = ui.open_article(project_root)
    at.session_state["_plan_kind"] = plan_model.KIND_SERVICE
    at.session_state["_plan_required"] = (12,)
    at.session_state["step"] = 3
    run_ok(at.run())
    assert seen[-1]["kind"] is onpage_links.ArticleKind.SERVICE
    assert tuple(seen[-1]["required"]) == (12,)


@pytest.mark.parametrize(
    ("written", "expected"),
    [('"19:30"', time(19, 30)), ('"25:00"', time(8, 0)), ("[1, 2]", time(8, 0))],
)
def test_default_time_from_plan_config(
    project_root, live, tmp_path, monkeypatch, written, expected
):
    """Lá Chắn T-103 đk 2c: ô Giờ của «Hẹn giờ» điền sẵn ``[plan].default_time`` đọc qua
    ``parse_plan_time``; sai dạng thì 08:00."""
    config = tmp_path / "content.toml"
    config.write_text(f"[plan]\ndefault_time = {written}\n", encoding="utf-8")
    monkeypatch.setattr(rules, "CONTENT_CONFIG_FILE", config)
    at = open_snap(project_root, MARKDOWN_ARTICLE.model_copy(update={"id": "6" * 32}))
    to_mode(at, "Hẹn giờ")
    assert at.session_state["_wp_time"] == expected
