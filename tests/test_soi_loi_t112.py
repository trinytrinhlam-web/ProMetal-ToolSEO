"""Soi Lỗi T-112 (rút gọn): chuẩn bị bật Hẹn giờ / Đăng ngay (công tắc vẫn mặc định tắt).

Kiểm độc lập, mượn khung trang Soạn bài, Cài đặt và WordPress giả (``live``) của
``test_app_images``, ``test_app_pages``, ``test_t102_publish`` như các file T-102 của Soi Lỗi; mọi
ca, mọi kiểm là của Soi Lỗi. Không gọi WordPress, Google, AI thật.

1. Công tắc không bật được bằng đường nào khác ngoài trang Cài đặt: tham số địa chỉ ở chính trang
   Soạn bài, gán thẳng ``session_state`` (không qua nút); mỗi phiên (mỗi tab
   trình duyệt) một công tắc riêng.
2. Đăng ngay chỉ đăng khi ảnh đại diện và SEO đã lên: thêm các lối hỏng chưa có ca (lệnh ảnh đại
   diện trả lời lạ, ghi SEO ném lỗi lạ) và trường SEO đang «Chặn» (SL-T112-1).
3. README mục 11 đúng với code sau khi gộp T-115 (SL-T112-2, SL-T112-3).
4. Lượt 3 (03/11, SL-T112-1 đã sửa): mọi biến thể chữ SEO (chỉ tiêu đề, chỉ mô tả, trống, ký tự
   lạ, sửa sau khi tick, hai tab), cú bấm lọt có đối chứng, chốt hai ``release_missing``, «Gửi
   nháp» không đổi; README mục 11 sau lượt 2 của Thư Ký (SL-T112-4).
"""

from __future__ import annotations

from pathlib import Path

import pytest
import streamlit as st
import test_app_images as ui
import test_app_pages as pages
import test_t102_publish as t102

from seo_app.onpage import meta as onpage_meta
from seo_app.publish.render import SeoFields
from seo_app.storage import site_index
from seo_app.text import escape_markdown
from seo_app.wordpress import client as wp_client
from seo_app.wordpress.client import SeoWriteResult, WordPressClient, WordPressError

env = ui.env
previews = ui.previews
fake_ai = ui.fake_ai
root = ui.root
site = ui.site
live = t102.live

README = Path(__file__).resolve().parents[1] / "README.md"
SWITCH, ACK, TOGGLE = "_release_enabled", "release_ack", "release_toggle"
SCHEDULE, PUBLISH = "Hẹn giờ", "Đăng ngay"
OFF = "Hẹn giờ và Đăng ngay đang **tắt**"
TITLE_OK, DESC_OK = "Sửa cổng inox tại nhà, thợ tới tận nơi", "Thợ tới tận nơi, báo giá trước."
BLOCKED = "Sửa cổng [gallery] inox tại nhà"  # dạng shortcode: bước SEO báo «Chặn» (T-061)


@pytest.fixture(autouse=True)
def site_cache(monkeypatch, tmp_path_factory):
    """Cache danh sách bài đã đăng trong thư mục tạm (không tạo ``data/site_index.sqlite``)."""
    path = tmp_path_factory.mktemp("danh-sach-bai") / "site_index.sqlite"
    monkeypatch.setattr(site_index, "DEFAULT_SITE_INDEX_FILE", path)
    return path


def run(target):
    at = target.run()
    assert not at.exception, at.exception
    return at


def switch_on(at) -> bool:
    return SWITCH in at.session_state and at.session_state[SWITCH] is True


def publish_step(at, mode: str):
    at.session_state["step"] = 4
    run(at)
    return run(at.segmented_control(key="_wp_mode").set_value(mode))


def has_send_button(at) -> bool:
    return any(b.key == "wp-send" for b in at.button)


# ====================================================================== 1. công tắc
@pytest.mark.parametrize("mode", [SCHEDULE, PUBLISH])
def test_tham_so_dia_chi_o_trang_soan_bai_khong_bat_duoc(project_root, mode):
    at = pages.open_page(project_root, "write.py")
    for name, value in (
        (SWITCH, "true"), ("release_enabled", "1"), (ACK, "true"), (TOGGLE, "true"),
        ("_wp_mode", mode), ("_wp_confirm", "true"),
    ):
        at.query_params[name] = value
    run(at)
    publish_step(at, mode)
    assert not switch_on(at) and not has_send_button(at)
    assert any(OFF in i.value for i in at.info)


@pytest.mark.parametrize(
    "value", ["true", "True", 1, 1.0, [True], {"on": True}],
    ids=["chu-true", "chu-True", "so-1", "so-1-0", "danh-sach", "dict"],
)
def test_gia_tri_gan_dung_cua_cong_tac_khong_bat(project_root, value):
    at = pages.open_page(project_root, "write.py")
    at.session_state[SWITCH] = value
    publish_step(at, PUBLISH)
    assert not has_send_button(at) and any(OFF in i.value for i in at.info)


def test_gan_thang_o_tick_va_nut_khong_qua_bam_khong_bat(project_root):
    """Ô «Tôi hiểu…» và nút bật bị gán thẳng trong ``session_state`` (không qua bấm, không chạy hàm
    ``on_change``): trang dựng lại hai ô theo công tắc thật, công tắc vẫn tắt."""
    at = pages.open_page(project_root, "settings.py")
    at.session_state[ACK] = True
    at.session_state[TOGGLE] = True
    run(at)
    assert not switch_on(at)
    assert at.toggle(key=TOGGLE).value is False
    at.switch_page("views/write.py")
    run(at)
    publish_step(at, SCHEDULE)
    assert not has_send_button(at)


def test_moi_phien_mot_cong_tac_tat_o_tab_khac_khong_tat_tab_nay(project_root):
    """Chỉ trong phiên (Chỉ Huy chọn A): mỗi tab trình duyệt là một phiên. Bật ở tab A không bật
    tab B; tắt ở tab B **không** tắt tab A (xem SL-T112-3: README nói ngược lại)."""
    tab_a = pages.open_page(project_root, "settings.py")
    run(tab_a.checkbox(key=ACK).check())
    run(tab_a.toggle(key=TOGGLE).set_value(True))
    tab_b = pages.open_page(project_root, "settings.py")
    assert switch_on(tab_a) and not switch_on(tab_b)
    run(tab_b.checkbox(key=ACK).check())
    run(tab_b.toggle(key=TOGGLE).set_value(True))
    run(tab_b.toggle(key=TOGGLE).set_value(False))  # tắt ở tab B
    assert not switch_on(tab_b) and switch_on(tab_a)


# ====================================================================== 2. Đăng ngay
def seo_like_client(monkeypatch, calls: list) -> None:
    """``set_seo_meta`` như client thật: ghi các trường còn chữ, báo đã ghi các trường đó."""

    def seo(self, post_id, **fields):
        calls.append(fields)
        sent = tuple(name for name, value in fields.items() if value)
        return SeoWriteResult(bool(sent), "meta", sent, message="Đã ghi SEO vào hộp SiteSEO.")

    monkeypatch.setattr(WordPressClient, "set_seo_meta", seo)


def send_publish(project_root, *, title: str = TITLE_OK, description: str = DESC_OK):
    at, _pid = ui.ready_image(project_root)
    at.session_state["seo_title_versions"] = [title]
    at.session_state["seo_title_ver"] = 0
    at.session_state["seo_description_versions"] = [description]
    at.session_state["seo_description_ver"] = 0
    t102.to_mode(at, PUBLISH)
    t102.run_ok(at.toggle(key="seo_write").set_value(True).run())
    t102.confirm(at)
    assert not t102.send_button(at).disabled
    return t102.run_ok(t102.send_button(at).click().run())


def test_doi_chung_seo_du_thi_dang(project_root, root, fake_ai, live, monkeypatch):
    calls: list = []
    seo_like_client(monkeypatch, calls)
    at = send_publish(project_root)
    assert calls and calls[0]["title"] and calls[0]["description"]
    assert t102.release_bodies(live.site) == [{"status": "publish"}]
    assert any("Đã đăng bài công khai" in s.value for s in at.success)


@pytest.mark.parametrize("blocked", ["title", "description"], ids=["tieu-de-chan", "mo-ta-chan"])
def test_sl_t112_1_dang_ngay_khi_truong_seo_dang_chan_thi_khong_dang(
    project_root, root, fake_ai, live, monkeypatch, blocked
):
    """SL-T112-1 (đã sửa ở T-112 lượt 3; R5 Chỉ Huy 03/11 12:45 (b)): bật «Ghi SEO lên website»,
    tiêu đề hay mô tả SEO đang «Chặn» ở bước SEO (bị bỏ khỏi lệnh ghi) thì màn hình xác nhận có
    dòng Chặn, nút khóa dù đã tick; cú bấm lọt qua nút khóa cũng không gửi gì (LC-T094-39)."""
    calls: list = []
    seo_like_client(monkeypatch, calls)
    texts = {"title": TITLE_OK, "description": DESC_OK, blocked: BLOCKED}
    at, _pid = ui.ready_image(project_root)
    at.session_state["seo_title_versions"] = [texts["title"]]
    at.session_state["seo_title_ver"] = 0
    at.session_state["seo_description_versions"] = [texts["description"]]
    at.session_state["seo_description_ver"] = 0
    t102.to_mode(at, PUBLISH)
    t102.run_ok(at.toggle(key="seo_write").set_value(True).run())
    t102.confirm(at)
    field = {"title": "tiêu đề SEO", "description": "mô tả SEO"}[blocked]
    assert any(f"Đăng ngay mà {field} sẽ không ghi lên website" in e.value for e in at.error)
    assert t102.send_button(at).disabled
    original = st.button  # cú bấm lọt qua nút khóa (bấm đúp, SL-T056-1): AppTest không cho bấm

    def button(label, *args, **kwargs):
        clicked = original(label, *args, **kwargs)
        return True if kwargs.get("key") == "wp-send" else clicked

    monkeypatch.setattr(st, "button", button)
    t102.run_ok(at.run())
    assert calls == []  # không lệnh ghi SEO nào
    assert [r for r in live.site.fake.requests if r.method != "GET"] == []  # không lệnh ghi nào
    assert t102.release_bodies(live.site) == []
    assert ui.store().load_send_state(at.session_state["draft_id"]) is None  # chưa gửi lần nào


def test_anh_dai_dien_tra_loi_la_thi_khong_dang(project_root, root, fake_ai, live, monkeypatch):
    """Lệnh đặt ảnh đại diện trả 200 mà nói về bài khác: client báo hỏng, Đăng ngay giữ nháp."""
    seo_like_client(monkeypatch, [])

    def post_post(request):
        body = ui.body_of(request) or {}
        if "featured_media" in body:
            return {"id": t102.POST_ID + 1, "status": "draft", "modified_gmt": ui.MODIFIED}
        return {"id": t102.POST_ID, "status": "draft", "modified_gmt": ui.MODIFIED, **body}

    live.site.fake.on("POST", t102.POST, post_post)
    at = send_publish(project_root)
    assert t102.release_bodies(live.site) == []
    assert any("Chưa đăng bài" in w.value and "ảnh đại diện" in w.value for w in at.warning)


def test_abilities_hoi_lai_bai_loi_thi_khong_dang(project_root, root, fake_ai, live, monkeypatch):
    """Ghi SEO qua Abilities báo đã ghi, nhưng hỏi lại bài còn là nháp không được (LC-T042-2):
    SEO coi như chưa lên, Đăng ngay giữ nháp."""
    state = {"seo_done": False}

    def seo(self, post_id, **fields):
        state["seo_done"] = True
        sent = tuple(name for name, value in fields.items() if value)
        return SeoWriteResult(True, "abilities", sent, message="Đã ghi SEO vào hộp SiteSEO.")

    original = WordPressClient._own_draft

    def own_draft(self, post_id, **kwargs):
        if state["seo_done"]:  # chỉ lần hỏi lại ngay sau lệnh ghi SEO
            raise WordPressError("Chưa hỏi lại được bài trên website.")
        return original(self, post_id, **kwargs)

    monkeypatch.setattr(WordPressClient, "set_seo_meta", seo)
    monkeypatch.setattr(WordPressClient, "_own_draft", own_draft)
    at = send_publish(project_root)
    assert state["seo_done"] and t102.release_bodies(live.site) == []
    assert any("Chưa đăng bài" in w.value and "SEO" in w.value for w in at.warning)


def test_ghi_seo_nem_loi_la_thi_khong_dang(project_root, root, fake_ai, live, monkeypatch):
    def broken(self, post_id, **fields):
        raise RuntimeError("MOI-T112 lỗi lạ")

    monkeypatch.setattr(WordPressClient, "set_seo_meta", broken)
    at = send_publish(project_root)
    assert t102.release_bodies(live.site) == []
    assert any("Chưa đăng bài" in w.value and "SEO" in w.value for w in at.warning)
    assert not [text for text in ui.texts(at) if "MOI-T112" in text]


# ====================================================================== 3. README
def readme_section_11() -> str:
    text = README.read_text(encoding="utf-8")
    start = text.index("## 11.")
    return text[start:text.index("\n## 12.", start)]


def test_sl_t112_2_readme_hen_gio_anh_dai_dien_hong_khong_hen():
    section = readme_section_11()
    (bullet,) = [line for line in section.splitlines() if line.startswith("- **Hẹn giờ thì vẫn")]
    assert "ảnh đại diện" in bullet  # phải nói riêng ca ảnh đại diện hỏng: không hẹn giờ


def test_sl_t112_3_readme_khong_noi_tat_o_tab_khac_la_tat_tab_nay():
    section = readme_section_11()
    (sentence,) = [line for line in section.splitlines() if line.startswith("Công tắc bị tắt")]
    assert "tab khác" not in sentence


# ====================================================================== 4. lượt 3 (03/11)
# SL-T112-1 sửa ở lượt 3 (Họa Sĩ): dòng Chặn ở màn hình xác nhận + chốt hai ``release_missing``.
NAMES = {"title": "tiêu đề SEO", "description": "mô tả SEO"}
# Chữ bước SEO báo «Chặn» (``siteseo_copy`` trả ``None``); viết bằng ``chr`` cho ký tự lạ.
ODD_TEXTS = {
    "phan-tram": "Sửa cổng %% inox tại nhà",
    "ma-ky-tu-html": "Sửa cổng &#37; inox tại nhà",
    "the-html": "Sửa cổng <b>inox</b> tại nhà",
    "dieu-khien": "Sửa cổng" + chr(7) + " inox tại nhà",
    "ky-tu-rieng": "Sửa cổng" + chr(0xE000) + " inox tại nhà",
    "ngoac-toan-khuon": "Sửa cổng " + chr(0xFF3B) + "gallery" + chr(0xFF3D) + " inox",
    "chi-khoang-trang": "   ",
    "chi-ky-tu-vo-hinh": chr(0x200B) + chr(0x2060),
    "hangul-filler": chr(0x3164),
}
ODD_CASES = [("title", kind) for kind in ODD_TEXTS] + [
    ("description", kind) for kind in ("the-html", "dieu-khien", "ky-tu-rieng", "chi-ky-tu-vo-hinh")
]


def set_seo(at, *, title: str = TITLE_OK, description: str = DESC_OK) -> None:
    at.session_state["seo_title_versions"] = [title]
    at.session_state["seo_title_ver"] = 0
    at.session_state["seo_description_versions"] = [description]
    at.session_state["seo_description_ver"] = 0


def to_confirmed(project_root, mode: str, *, seo_write: bool = True, snap=None, **texts):
    """Bài có chữ SEO ``texts`` (mặc định hợp lệ), chọn ``mode``, bật «Ghi SEO», đã tick."""
    at, _pid = ui.ready_image(project_root, snap)
    set_seo(at, **texts)
    t102.to_mode(at, mode)
    if seo_write:
        t102.run_ok(at.toggle(key="seo_write").set_value(True).run())
    return t102.confirm(at)


def leak_click(monkeypatch) -> None:
    """Cú bấm lọt qua nút ``wp-send`` đang khóa (bấm đúp, SL-T056-1): AppTest không cho bấm nút
    khóa, nên ``st.button`` báo «đã bấm» cho đúng nút đó ở mọi lần chạy sau (mọi phiên)."""
    original = st.button

    def button(label, *args, **kwargs):
        clicked = original(label, *args, **kwargs)
        return True if kwargs.get("key") == "wp-send" else clicked

    monkeypatch.setattr(st, "button", button)


def writes(live) -> list:
    return [r for r in live.site.fake.requests if r.method != "GET"]


def post_bodies(live) -> list[dict]:
    """Thân mọi lệnh ``POST`` vào bài 501 (lệnh tải ảnh là byte, không đọc)."""
    posts = [r for r in live.site.fake.requests if (r.method, ui.path_of(r)) == ("POST", t102.POST)]
    return [ui.body_of(r) or {} for r in posts]


def blocked_line(at, names: str) -> bool:
    return any(f"Đăng ngay mà {names} sẽ không ghi lên website" in e.value for e in at.error)


def left_out_lines(at) -> list[str]:
    return [m.value for m in [*at.error, *at.warning] if "sẽ không ghi lên website" in m.value]


def test_l3_doi_chung_bam_lot_khi_nut_mo_thi_gui_that(
    project_root, root, fake_ai, live, monkeypatch
):
    """Đối chứng cho mọi ca «bấm lọt» (của tôi, của Họa Sĩ): cùng cách giả, nút **mở** thì lần chạy
    sau gửi thật. Thiếu ca này, «không gửi gì» ở ca nút khóa có thể đúng chỉ vì cách giả không
    tới được nhánh gửi."""
    calls: list = []
    seo_like_client(monkeypatch, calls)
    at = to_confirmed(project_root, PUBLISH)
    assert not t102.send_button(at).disabled and left_out_lines(at) == []
    leak_click(monkeypatch)
    t102.run_ok(at.run())
    assert calls and calls[0]["title"].startswith(TITLE_OK)
    assert t102.release_bodies(live.site) == [{"status": "publish"}]


@pytest.mark.parametrize(("field", "kind"), ODD_CASES, ids=[f"{f}-{k}" for f, k in ODD_CASES])
def test_l3_chu_seo_la_dang_ngay_bi_chan_bam_lot_khong_gui(
    project_root, root, fake_ai, live, monkeypatch, field, kind
):
    """Ký tự lạ, chỉ khoảng trắng, chỉ ký tự vô hình: bước SEO báo «Chặn» (đúng như dòng Chặn
    nói), Đăng ngay có dòng Chặn nêu đúng trường, nút khóa, cú bấm lọt không gửi lệnh nào."""
    text = ODD_TEXTS[kind]
    texts = {"title": TITLE_OK, "description": DESC_OK, field: text}
    copy = onpage_meta.siteseo_copy(
        texts["title"], texts["description"], "sua-cong-inox", suffix=" | Pro-Metal"
    )
    assert (copy.title if field == "title" else copy.description) is None  # bước SEO: «Chặn»
    calls: list = []
    seo_like_client(monkeypatch, calls)
    at = to_confirmed(project_root, PUBLISH, **texts)
    assert blocked_line(at, NAMES[field]) and t102.send_button(at).disabled
    leak_click(monkeypatch)
    t102.run_ok(at.run())
    assert calls == [] and writes(live) == [] and t102.release_bodies(live.site) == []
    assert ui.store().load_send_state(at.session_state["draft_id"]) is None


def test_l3_tieu_de_tren_200_ky_tu_khong_chan_truoc_nhung_khong_dang(
    project_root, root, fake_ai, live, monkeypatch
):
    """Ghi nhận: tiêu đề SEO trên 200 ký tự chỉ «Cảnh báo» ở bước SEO nên màn hình xác nhận không
    Chặn; client thật từ chối cả lệnh ghi SEO (quá dài, chưa gửi gì) → SEO chưa lên, Đăng ngay vẫn
    giữ nháp (chốt ``seo_ok`` của lượt 1). Không đăng với SEO mặc định."""
    honor_seo_switch(monkeypatch)
    long_title = "Sửa cổng inox tại nhà " * 10
    assert onpage_meta.siteseo_copy(long_title, DESC_OK, "x", suffix=" | Pro-Metal").title
    at = to_confirmed(project_root, PUBLISH, title=long_title)
    assert left_out_lines(at) == [] and not t102.send_button(at).disabled
    at = t102.run_ok(t102.send_button(at).click().run())
    assert any("quá dài" in i.value for i in at.info)  # câu của client: từ chối cả lệnh ghi
    assert t102.release_bodies(live.site) == []
    assert any("Chưa đăng bài" in w.value and "SEO" in w.value for w in at.warning)


def test_l3_sua_seo_thanh_trong_sau_khi_tick_thi_bo_tick_va_chan(
    project_root, root, fake_ai, live, monkeypatch
):
    calls: list = []
    seo_like_client(monkeypatch, calls)
    at = to_confirmed(project_root, PUBLISH)
    assert not t102.send_button(at).disabled
    at.session_state["seo_description_versions"] = [DESC_OK, ""]  # xóa mô tả ở bước SEO
    at.session_state["seo_description_ver"] = 1
    t102.run_ok(at.run())
    assert at.checkbox(key="_wp_confirm").value is False
    assert any("bỏ tick" in w.value for w in at.warning)
    assert blocked_line(at, "mô tả SEO")
    t102.confirm(at)  # tick lại: vẫn khóa
    assert t102.send_button(at).disabled
    leak_click(monkeypatch)
    t102.run_ok(at.run())
    assert calls == [] and writes(live) == []


def test_l3_sua_seo_chan_thanh_hop_le_thi_mo_va_ghi_dung_chu_moi(
    project_root, root, fake_ai, live, monkeypatch
):
    calls: list = []
    seo_like_client(monkeypatch, calls)
    at = to_confirmed(project_root, PUBLISH, title=BLOCKED)
    assert blocked_line(at, "tiêu đề SEO") and t102.send_button(at).disabled
    at.session_state["seo_title_versions"] = [BLOCKED, TITLE_OK]
    at.session_state["seo_title_ver"] = 1
    t102.run_ok(at.run())
    assert left_out_lines(at) == []
    t102.confirm(at)
    assert not t102.send_button(at).disabled
    t102.run_ok(t102.send_button(at).click().run())
    assert calls[0]["title"].startswith(TITLE_OK) and calls[0]["description"] == DESC_OK
    assert t102.release_bodies(live.site) == [{"status": "publish"}]


def test_l3_hai_tab_cung_bai_moi_tab_xet_chu_seo_cua_minh(
    project_root, root, fake_ai, live, monkeypatch
):
    """Hai tab mở cùng một bài: chữ SEO, ô tick, dòng Chặn là của từng tab. Cùng một cú bấm lọt:
    tab có tiêu đề «Chặn» không gửi gì; tab hợp lệ gửi đúng chữ của nó (đối chứng ngay trong ca)."""
    calls: list = []
    seo_like_client(monkeypatch, calls)
    snap = ui.article()
    tab_a = to_confirmed(project_root, PUBLISH, snap=snap, title=BLOCKED)
    tab_b = to_confirmed(project_root, PUBLISH, snap=snap)
    assert tab_a.session_state["draft_id"] == tab_b.session_state["draft_id"] == snap.id
    t102.run_ok(tab_a.run())
    assert blocked_line(tab_a, "tiêu đề SEO") and t102.send_button(tab_a).disabled
    assert left_out_lines(tab_b) == [] and not t102.send_button(tab_b).disabled
    leak_click(monkeypatch)
    t102.run_ok(tab_a.run())
    assert calls == [] and writes(live) == []
    t102.run_ok(tab_b.run())
    assert len(calls) == 1 and calls[0]["title"].startswith(TITLE_OK)
    assert t102.release_bodies(live.site) == [{"status": "publish"}]


@pytest.mark.parametrize(
    ("texts", "names"),
    [({"description": ""}, "mô tả SEO"), ({"title": BLOCKED, "description": BLOCKED},
                                          "tiêu đề SEO, mô tả SEO")],
    ids=["mo-ta-trong", "ca-hai-chan"],
)
def test_l3_hen_gio_canh_bao_dung_truong_va_van_hen(
    project_root, root, fake_ai, live, monkeypatch, texts, names
):
    calls: list = []
    seo_like_client(monkeypatch, calls)
    at = to_confirmed(project_root, SCHEDULE, **texts)
    assert any(f"Hẹn giờ mà {names} sẽ không ghi lên website" in w.value for w in at.warning)
    assert not any("sẽ không ghi lên website" in e.value for e in at.error)
    at = t102.run_ok(t102.send_button(at).click().run())
    when = t102.tomorrow_8am_utc()
    assert t102.release_bodies(live.site) == [
        {"status": "future", "date_gmt": t102.date_gmt_text(when)}
    ]
    assert any(f"Bài đã hẹn giờ nhưng {names} chưa lên" in w.value for w in at.warning)


@pytest.mark.parametrize("mode", [SCHEDULE, PUBLISH])
def test_l3_tat_ghi_seo_khong_them_dong_moi(project_root, root, fake_ai, live, mode):
    """Tắt «Ghi SEO»: luật cũ của bộ dựng (Đăng ngay Chặn «SEO chưa ghi», Hẹn giờ nhắc chép tay),
    không thêm dòng «… sẽ không ghi lên website» dù tiêu đề, mô tả trống."""
    at = to_confirmed(project_root, mode, seo_write=False, title="", description="")
    assert left_out_lines(at) == []
    if mode == PUBLISH:
        assert any("Đăng ngay mà SEO chưa ghi lên website" in e.value for e in at.error)


def test_l3_gui_nhap_bat_ghi_seo_tieu_de_chan_van_nhu_cu(
    project_root, root, fake_ai, live, monkeypatch
):
    """«Gửi nháp» không đổi: bật «Ghi SEO», tiêu đề «Chặn» thì không có dòng mới, gửi nháp được,
    ghi phần SEO còn lại, không lệnh chuyển trạng thái nào."""
    calls: list = []
    seo_like_client(monkeypatch, calls)
    at, _pid = ui.ready_image(project_root)
    set_seo(at, title=BLOCKED)
    ui.to_publish(at)
    t102.run_ok(at.toggle(key="seo_write").set_value(True).run())
    assert left_out_lines(at) == []
    at = ui.send(at)
    assert calls and calls[0]["title"] == "" and calls[0]["description"] == DESC_OK
    assert t102.release_bodies(live.site) == []
    assert any("Đã tạo bài nháp" in s.value for s in at.success)


def test_l3_chot_hai_release_missing_tung_truong():
    from app.views import write  # noqa: PLC0415

    full = {"title": "Tiêu đề", "description": "Mô tả", "focus_keyword": ""}

    def holder(**fields):
        return {"seo": {"fields": {**full, **fields}, "skipped": []}}

    ok = {"seo_ok": True}
    assert write.release_missing({}, ok) == ""
    assert write.release_missing(holder(), ok) == ""  # từ khóa chính trống: không tính thiếu
    assert write.release_missing(holder(title=""), ok) == "tiêu đề SEO"
    assert write.release_missing(holder(description=""), ok) == "mô tả SEO"
    assert write.release_missing(holder(title="", description=""), ok) == "tiêu đề SEO, mô tả SEO"
    assert write.release_missing(holder(title=""), {"seo_ok": False}) == write.MISSING_SEO
    both = {"seo_ok": True, "featured_missing": True}
    assert write.release_missing(holder(title=""), both) == f"{write.MISSING_FEATURED}, tiêu đề SEO"
    assert write.release_missing({"seo": {"skipped": []}}, ok) == "tiêu đề SEO, mô tả SEO"


def test_l3_seo_notices_theo_hinh_thuc():
    from app.views import write  # noqa: PLC0415

    empty = SeoFields(write=True)
    assert write.seo_notices(SeoFields(), "publish") == []  # tắt «Ghi SEO»: bộ dựng đã xét
    assert write.seo_notices(empty, "draft") == []
    assert write.seo_notices(SeoFields(title="a", description="b", write=True), "publish") == []
    (block,) = write.seo_notices(empty, "publish")
    assert block.level is onpage_meta.Level.BLOCK and "tiêu đề SEO, mô tả SEO" in block.message
    (warn,) = write.seo_notices(SeoFields(title="a", write=True), "future")
    assert warn.level is onpage_meta.Level.WARN and "Hẹn giờ mà mô tả SEO" in warn.message


# ---------------------------------------------------------------- README mục 11 sau lượt 2
def honor_seo_switch(monkeypatch) -> None:
    """Site giả (fixture ``site``) dựng client bỏ qua ``write_seo``: client thật luôn báo «chưa bật
    ghi SEO» mà không gửi gì. Ca cần đường ghi SEO **thật** của client thì cho client nhận công tắc
    như ``WordPressClient.from_settings`` thật."""
    made = WordPressClient.from_settings  # bản fixture ``site`` đã vá (WordPress giả)

    def from_settings(cls, settings, **kwargs):
        client = made(settings)
        client.write_seo = kwargs.get("write_seo") is True
        return client

    monkeypatch.setattr(WordPressClient, "from_settings", classmethod(from_settings))


def meta_route(live, status: int) -> None:
    """SiteSEO không có Abilities (site giả trả 404), khóa meta có trong REST (đường dự phòng);
    lệnh ghi meta trả ``status`` (200: lưu đúng chữ đã gửi)."""

    def get_post(_request):
        meta = {wp_client.SITESEO_TITLE_KEY: "", wp_client.SITESEO_DESC_KEY: ""}
        return (200, {"id": t102.POST_ID, "status": "draft", "modified_gmt": ui.MODIFIED,
                      "meta": meta}, {"Date": t102.http_date()})

    def post_post(request):
        body = ui.body_of(request) or {}
        if "meta" in body and status != 200:
            return (status, {"code": "internal_server_error", "message": t102.BAIT}, {})
        return {"id": t102.POST_ID, "status": "draft", "modified_gmt": ui.MODIFIED, **body}

    live.site.fake.on("GET", t102.POST, get_post)
    live.site.fake.on("POST", t102.POST, post_post)


@pytest.mark.parametrize("status", [500, 200], ids=["loi-giua-chung", "doi-chung-ghi-duoc"])
def test_l3_hen_gio_ghi_seo_duong_meta(project_root, root, fake_ai, live, monkeypatch, status):
    """Hẹn giờ, «Ghi SEO» bật, client thật ghi SEO qua đường meta. Lệnh ghi lỗi giữa chừng (500):
    chỉ thiếu SEO mà app **không** hẹn giờ (client không biết giờ sửa bài, T-115), bài vẫn là nháp;
    README mục 11 nói «Hẹn giờ thì vẫn hẹn khi chỉ thiếu SEO» (SL-T112-4). Đối chứng: ghi được
    thì hẹn giờ, không cảnh báo."""
    honor_seo_switch(monkeypatch)
    meta_route(live, status)
    at = to_confirmed(project_root, SCHEDULE)
    at = t102.run_ok(t102.send_button(at).click().run())
    assert any("meta" in body for body in post_bodies(live))  # đi đúng đường meta của client
    shown = "\n".join(w.value for w in at.warning)
    if status == 200:
        assert len(t102.release_bodies(live.site)) == 1 and "Bài đã hẹn giờ nhưng" not in shown
        return
    assert t102.release_bodies(live.site) == []
    assert escape_markdown("Chưa hẹn giờ, chưa đăng: bài vẫn là nháp.") in shown
    assert "Bài đã hẹn giờ nhưng" not in shown
    assert not any(t102.BAIT in text for text in ui.texts(at))


def test_l3_hen_gio_chua_hoi_duoc_bai_de_dat_anh_dai_dien_thi_van_hen(
    project_root, root, fake_ai, live
):
    """Hẹn giờ, lệnh đặt ảnh đại diện hỏng ngay ở bước hỏi bài (chưa ghi gì): ảnh đại diện chưa lên
    mà app **vẫn** hẹn giờ, kèm cảnh báo. README mục 11 nói ảnh đại diện chưa lên «(lệnh đặt ảnh
    đại diện lỗi)» thì app không hẹn giờ (xem SL-T112-4)."""
    seen = {"get": 0}

    def get_post(_request):
        seen["get"] += 1
        if seen["get"] == 1:  # lần hỏi bài đầu tiên: của lệnh đặt ảnh đại diện
            return (500, {"code": "internal_server_error", "message": t102.BAIT}, {})
        return (200, {"id": t102.POST_ID, "status": "draft", "modified_gmt": ui.MODIFIED},
                {"Date": t102.http_date()})

    live.site.fake.on("GET", t102.POST, get_post)
    at = to_confirmed(project_root, SCHEDULE, seo_write=False)
    at = t102.run_ok(t102.send_button(at).click().run())
    assert not any("featured_media" in body for body in post_bodies(live))
    when = t102.tomorrow_8am_utc()
    assert t102.release_bodies(live.site) == [
        {"status": "future", "date_gmt": t102.date_gmt_text(when)}
    ]
    assert any("Bài đã hẹn giờ nhưng ảnh đại diện chưa lên" in w.value for w in at.warning)


def test_l3_readme_cau_bai_bi_sua_ngoai_app_khop_client():
    section = readme_section_11()
    start = section.index("«Bài nháp trên website đã bị sửa") + 1
    quoted = section[start:section.index("»", start)]
    expected = wp_client._RELEASE_CHANGED.replace(
        "(trong trang quản trị, plugin hay người khác)", "(…)"
    )
    assert quoted == expected


@pytest.mark.xfail(
    strict=True,
    reason="SL-T112-4: README mục 11 chia luật Hẹn giờ theo loại phần thiếu («vẫn hẹn khi chỉ "
    "thiếu SEO», ảnh đại diện thì không); thật ra theo lệnh ghi có lỗi giữa chừng không: ghi SEO "
    "lỗi giữa chừng (đường meta) thì không hẹn, ảnh đại diện hỏng lúc hỏi bài (chưa ghi) thì "
    "vẫn hẹn",
)
def test_sl_t112_4_readme_hen_gio_ghi_seo_loi_giua_chung_khong_hen():
    section = readme_section_11()
    start = section.index("**Ảnh đại diện hay SEO chưa lên kịp**")
    part = section[start:section.index("**Kết quả hẹn giờ, đăng**", start)]
    sentences = [s for line in part.splitlines() for s in line.split(". ")]
    assert any("không hẹn giờ" in s and "SEO" in s for s in sentences)
