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
"""

from __future__ import annotations

from pathlib import Path

import pytest
import test_app_images as ui
import test_app_pages as pages
import test_t102_publish as t102

from seo_app.storage import site_index
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


@pytest.mark.xfail(
    strict=True,
    reason="SL-T112-1: bật «Ghi SEO lên website», tiêu đề hay mô tả SEO đang «Chặn» ở bước SEO "
    "(bị bỏ khỏi lệnh ghi): app ghi phần còn lại, coi SEO đã lên (seo_ok) và Đăng ngay vẫn đăng "
    "công khai với tiêu đề/mô tả SEO mặc định (trái LC-T094-39, yêu cầu 1 T-112)",
)
@pytest.mark.parametrize("blocked", ["title", "description"], ids=["tieu-de-chan", "mo-ta-chan"])
def test_sl_t112_1_dang_ngay_khi_truong_seo_dang_chan_thi_khong_dang(
    project_root, root, fake_ai, live, monkeypatch, blocked
):
    calls: list = []
    seo_like_client(monkeypatch, calls)
    texts = {"title": TITLE_OK, "description": DESC_OK, blocked: BLOCKED}
    at = send_publish(project_root, **texts)
    assert calls and calls[0][blocked] == ""  # trường «Chặn» không được ghi
    assert t102.release_bodies(live.site) == []
    saved = ui.store().load_send_state(at.session_state["draft_id"])
    assert (saved.released, saved.release_unknown) == (False, False)


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


@pytest.mark.xfail(
    strict=True,
    reason="SL-T112-2: README mục 11 nói «Hẹn giờ thì vẫn hẹn» khi ảnh đại diện hay SEO chưa lên; "
    "sau khi gộp T-115, ảnh đại diện hỏng thì client không hẹn giờ (bài vẫn là nháp, câu "
    "«…Chưa hẹn giờ, chưa đăng: bài vẫn là nháp…»)",
)
def test_sl_t112_2_readme_hen_gio_anh_dai_dien_hong_khong_hen():
    section = readme_section_11()
    (bullet,) = [line for line in section.splitlines() if line.startswith("- **Hẹn giờ thì vẫn")]
    assert "ảnh đại diện" in bullet  # phải nói riêng ca ảnh đại diện hỏng: không hẹn giờ


@pytest.mark.xfail(
    strict=True,
    reason="SL-T112-3: README mục 11 nói công tắc bị tắt «ví dụ ở tab khác» thì bấm gửi không gửi "
    "gì; công tắc chỉ trong phiên, mỗi tab một phiên: tắt ở tab khác không tắt tab đang mở",
)
def test_sl_t112_3_readme_khong_noi_tat_o_tab_khac_la_tat_tab_nay():
    section = readme_section_11()
    (sentence,) = [line for line in section.splitlines() if line.startswith("Công tắc bị tắt")]
    assert "tab khác" not in sentence
