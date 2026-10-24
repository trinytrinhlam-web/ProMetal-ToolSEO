"""Soi Lỗi T-056: chỗ cần ảnh thật và «Gửi nháp» kèm ảnh trên trang Soạn bài (``write.py``).

Bổ sung cho ``tests/test_app_images.py`` của Họa Sĩ (dùng lại ảnh giả, WordPress giả, AI giả của
file đó), thử như người dùng thật:

- gửi nháp bị ngắt giữa chừng, ảnh bị thay file sau khi duyệt alt, một ảnh dùng ở hai chỗ;
- đoạn dạng shortcode vắt qua hai mục của bài; số điện thoại viết kiểu khác;
- sang trang khác rồi quay lại (``remember_inputs``): «Viết bài mới» ở trang Bài viết, xóa nháp
  đang mở, ảnh đại diện đã chọn, khóa «bài nháp có thể đã có»;
- tên lấy từ máy (NFD, ký tự rộng 0, RLO, Markdown, ``$``), thư mục rỗng, thư mục 3.000 ảnh, ảnh
  hỏng, HEIC; chữ độc do AI viết alt; ảnh AI theo tên file/tên thư mục;
- hai chỗ test cũ không bắt được khi gỡ chỗ sửa (thử trên bản sao ``git archive``): dấu ảnh AI
  trong phiên ở chỗ thứ hai khi lưu thẻ hỏng; câu báo file thẻ hỏng chỉ có tên file.

Lỗi tìm được đánh dấu ``xfail(strict=True)`` kèm mã SL-T056-x (xem
``docs/team/reports/T-056-soi-loi.md``). Mọi test dùng thư mục tạm, ảnh giả; không gọi mạng thật
(WordPress giả, AI giả).
"""

from __future__ import annotations

import io
import threading
import unicodedata

import fake_ai as fake_ai_module
import pytest
import test_app_images as ui
from PIL import ExifTags, Image
from streamlit.runtime.scriptrunner_utils.exceptions import StopException

import seo_app.storage.image_tags as image_tags
from seo_app.images.alt import AI_ALT_PREFIX, AltSuggestion
from seo_app.images.folders import ImageLibrary
from seo_app.images.tags import SOURCE_AI, SOURCE_REAL
from seo_app.storage import DraftPart
from seo_app.storage.drafts import DraftImage
from seo_app.storage.image_tags import ImageTagStore, ImageTagStoreError
from seo_app.wordpress.client import WordPressClient, _has_shortcode

# Fixture dùng chung với test giao diện ảnh của Họa Sĩ (mật khẩu thử, cache xem trước tạm…).
env = ui.env
previews = ui.previews
fake_ai = ui.fake_ai
root = ui.root
site = ui.site
sent = ui.sent

button = ui.button
run_ok = ui.run_ok
by_key = ui.by_key
PROJECT = ui.PROJECT
REAL_FILE = ui.REAL_FILE
SEND = "📤 Gửi nháp"


def two_spots():
    """Bài có hai chỗ cần ảnh (mục «Bản lề» và «Cánh cổng»)."""
    return ui.article(
        parts=[
            DraftPart(heading="Mở bài", versions=["Mở bài."]),
            DraftPart(heading="Bản lề", versions=["Phần một."], image="Ảnh một"),
            DraftPart(heading="Cánh cổng", versions=["Phần hai."], image="Ảnh hai"),
        ]
    )


def same_image_twice(project_root):
    """Mở bài hai chỗ cần ảnh, chọn cùng ảnh ``IMG_0001.jpg`` cho cả hai: (trang, chỗ 1, chỗ 2)."""
    at, first = ui.open_article(project_root, two_spots())
    second = at.session_state["part_ids"][2]
    ui.choose_real(at, first)
    ui.browse(at, second)  # mở lại đúng thư mục vừa xem
    ui.choose(at, "IMG_0001.jpg")
    return at, first, second


def set_alt(at, pid: int, alt: str):
    run_ok(at.text_input(key=f"alt-{pid}").input(alt).run())
    return ui.approve(at, pid)


def gps_of(data: bytes) -> dict:
    with Image.open(io.BytesIO(data)) as image:
        return dict(image.getexif().get_ifd(ExifTags.IFD.GPSInfo))


# ============================================================== gửi nháp: ngắt giữa chừng, ảnh đổi


def test_interrupted_send_locks_resend(project_root, root, fake_ai, site, monkeypatch):
    """Đang gửi (tải ảnh, tạo nháp mất vài chục giây), người dùng bấm nút khác hay bấm đúp «Gửi
    nháp»: Streamlit dừng lần chạy ở lệnh ``st.*`` kế tiếp (ở đây là lúc thoát ``st.spinner``) bằng
    ``RerunException``/``StopException``, là ``BaseException`` nên lọt qua ``except Exception`` của
    ``send_draft``. Bài nháp và ảnh đã lên website nhưng ``_wp_result``, ``_wp_sent``,
    ``_wp_maybe_draft`` chưa kịp ghi: lần chạy sau nút vẫn bật, không có câu nhắc nào, bấm lại là
    thêm một bài nháp và tải ảnh (có GPS) lần nữa.

    Mong đợi: như ``maybe_draft`` (Lá Chắn T-071 3b), lần chạy sau nhắc «bài nháp có thể đã có» và
    khóa nút tới khi người dùng xác nhận đã kiểm trang quản trị."""
    original = WordPressClient.create_draft_with_images

    def interrupted(self, title, parts, **kwargs):
        original(self, title, parts, **kwargs)
        raise StopException()  # như Streamlit dừng lần chạy ngay sau khi gửi xong

    monkeypatch.setattr(WordPressClient, "create_draft_with_images", interrupted)
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.send(at)
    assert len(site.posts()) == 1 and len(site.uploads()) == 1  # bài nháp, ảnh đã lên website
    run_ok(at.run())  # lần chạy kế tiếp (người dùng vừa bấm gì đó)
    assert any("bài nháp có thể đã có" in e.value for e in at.error)
    assert button(at, SEND).disabled


def test_replaced_file_after_approval_stops_send(project_root, root, fake_ai, site):
    """Chọn ảnh «sau» (không có GPS), duyệt alt; trước khi bấm «Gửi nháp», file bị thay bằng ảnh
    khác cùng tên, **có GPS** (Drive đồng bộ bản mới, chép đè lô ảnh mới cùng tên IMG_…). Kiểm lại
    ngay trước khi tải (``recheck``/``changed``) chỉ so tên, thư mục, ảnh AI, alt: ảnh khác vẫn lên
    website công khai kèm vị trí GPS mà người dùng chưa xem, với alt duyệt cho ảnh cũ.

    Mong đợi: như khi ảnh đổi tên hay thành ảnh AI, dừng («ảnh vừa thay đổi»), chưa gửi gì; người
    dùng xem lại ảnh, alt rồi duyệt lại (so ``entry`` cỡ, giờ sửa, ``file_id`` của lần chọn)."""
    at, pid = ui.open_article(project_root)
    ui.browse(at, pid)
    ui.open_sub(at, PROJECT)
    ui.open_sub(at, "sau")
    ui.choose(at, "IMG_0002.jpg")
    assert "Ảnh không có vị trí GPS." in [c.value for c in at.caption]
    ui.write_alt(at, pid)
    ui.approve(at, pid)
    ui.to_publish(at)
    ui.write(root / PROJECT / "sau" / "IMG_0002.jpg", ui.jpeg((640, 480), (10, 10, 10), gps=True))
    ui.send(at)
    uploaded = [gps_of(upload.body) for upload in site.uploads()]
    assert uploaded == [], f"đã tải lên ảnh khác, GPS: {uploaded}"


# ===================================================================== cảnh báo trước khi gửi


def test_shortcode_across_sections_listed(project_root, root, fake_ai, site):
    """«[code_snippet id=3» ở cuối mục này, «]» ở mục sau: xét riêng từng mục thì không có đoạn
    nào, nhưng nội dung gửi WordPress là một chuỗi (``<p>…[code_snippet id=3</p><h2>…</h2><p>…]
    …</p>``) và ``_has_shortcode`` (cùng quy tắc với WordPress) nhận ra shortcode ở đó. Mong đợi:
    liệt kê như mọi đoạn khác (LC-T061-4: «mọi đoạn dạng shortcode trong … nội dung»)."""
    snap = ui.article(
        parts=[
            DraftPart(heading="Mở bài", versions=["Mã nhúng [code_snippet id=3"]),
            DraftPart(
                heading="Bản lề cổng",
                versions=["Bản lề gỉ thì thay cả cặp (bảng giá ở cuối bài]."],
                image="Ảnh bản lề",
            ),
        ]
    )
    at, _pid = ui.open_article(project_root, snap)
    ui.to_publish(at)
    content = (
        "<p>Mã nhúng [code_snippet id=3</p><h2>Bản lề cổng</h2>"
        "<p>Bản lề gỉ thì thay cả cặp (bảng giá ở cuối bài].</p>"
    )
    assert _has_shortcode(content)  # quy tắc của client: nội dung này có đoạn dạng shortcode
    assert any("đoạn dạng shortcode" in w.value for w in at.warning)


PHONE_VARIANTS = [
    "Gọi 1900 6868 để được tư vấn",  # tổng đài 8 số
    "Hotline 1800.6789 miễn phí",
    "0909–123–456 anh Tư",  # gạch ngang dài (Word, điện thoại tự đổi)
    "0909/123/456",
]


@pytest.mark.parametrize("alt", PHONE_VARIANTS)
def test_phone_like_variants_warn(project_root, root, fake_ai, alt):
    """Nhắc khi alt có dãy số giống số điện thoại (Lá Chắn T-050 3d): ``PHONE_LIKE`` cần 9 chữ số
    trở lên, ngăn bằng dấu cách, chấm, gạch nối, ngoặc; bỏ sót tổng đài 8 số (1900/1800 …) và số
    ngăn bằng «–», «/»."""
    at, pid = ui.open_article(project_root)
    ui.choose_real(at, pid)
    run_ok(at.text_input(key=f"alt-{pid}").input(alt).run())
    assert any("số điện thoại" in w.value for w in at.warning)


# ============================================================= sang trang khác rồi quay lại


def test_featured_image_kept_after_switching_pages(project_root, root, fake_ai, site):
    """Chọn ảnh đại diện là ảnh thứ hai, sang trang Bài viết rồi quay lại: ô «Ảnh đại diện» về
    ảnh đầu (khóa ``_featured`` không nằm trong ``KEEP_KEYS`` của ``remember_inputs``), bấm «Gửi
    nháp» là ảnh đại diện khác ý người dùng. Cùng loại lỗi Họa Sĩ đã sửa cho ô nhập khác; thấy cả
    trên trình duyệt thật."""
    at, first = ui.open_article(project_root, two_spots())
    second = at.session_state["part_ids"][2]
    ui.choose_real(at, first)
    ui.browse(at, second)
    run_ok(by_key(at, "browse-up").click().run())
    ui.open_sub(at, "sau")
    ui.choose(at, "IMG_0002.jpg")
    for pid in (first, second):
        ui.write_alt(at, pid)
        ui.approve(at, pid)
    ui.to_publish(at)
    run_ok(at.selectbox(key="_featured").select(second).run())
    run_ok(at.switch_page("views/home.py").run())
    run_ok(at.switch_page("views/write.py").run())
    assert at.session_state["step"] == 4  # bước, alt đã duyệt vẫn còn (remember_inputs)
    assert at.selectbox(key="_featured").value == second


def test_new_article_from_home_page_starts_clean_and_keeps_old_draft(project_root, root, fake_ai):
    """«Viết bài mới» ở trang Bài viết khi đang có bài kèm ảnh, alt đã duyệt: trang Soạn bài mở bài
    trống với từ khóa mới (bản sao ``_kept`` không đưa alt, ảnh, bước cũ trở lại), nháp cũ còn
    nguyên, bài mới lưu thành nháp khác (Họa Sĩ đề nghị thử, Rủi ro 6)."""
    at, _pid = ui.ready_image(project_root)
    old_id = at.session_state["draft_id"]
    run_ok(at.switch_page("views/home.py").run())
    at.text_input[0].input("lan can cầu thang").run()
    run_ok(button(at, "Bắt đầu").click().run())
    assert at.session_state["keyword"] == "lan can cầu thang"
    assert at.session_state["step"] == 0
    assert not [k for k in at.session_state if str(k).startswith(("pick-", "alt-", "altok-"))]
    assert at.session_state["draft_id"] != old_id
    old = ui.store().load(old_id)
    assert old.keyword == "sửa cổng inox"
    assert old.parts[1].chosen_image.alt_approved is True
    run_ok(at.run())
    keywords = sorted(d.keyword for d in ui.store().list_drafts().drafts)
    assert keywords == ["lan can cầu thang", "sửa cổng inox"]


def test_delete_open_draft_clears_page_and_is_not_recreated(project_root, root, fake_ai):
    """Xóa đúng nháp đang mở (có ảnh, alt đã duyệt): trang trống, sang trang khác rồi quay lại thì
    bản sao ô nhập không làm sống lại bài, lần tự lưu không tạo lại nháp."""
    at, _pid = ui.ready_image(project_root)
    old_id = at.session_state["draft_id"]
    at.session_state["step"] = 0
    run_ok(at.run())
    run_ok(button(at, "Xóa hẳn", key=f"del-{old_id}").click().run())
    run_ok(at.run())
    run_ok(at.switch_page("views/home.py").run())
    run_ok(at.switch_page("views/write.py").run())
    assert ui.store().list_drafts().drafts == []
    assert at.session_state["keyword"] == ""


def test_maybe_draft_lock_survives_page_switch(project_root, root, fake_ai, site):
    """Lỗi đúng lúc tạo nháp (``maybe_draft``): sang trang khác rồi quay lại vẫn khóa nút và nhắc
    kiểm Bài viết → Nháp (Lá Chắn T-071 3b)."""
    site.fake.on("POST", ui.POSTS, lambda _r: (502, {"code": "x", "message": "Bad gateway"}, {}))
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.send(at)
    run_ok(at.switch_page("views/home.py").run())
    run_ok(at.switch_page("views/write.py").run())
    assert button(at, SEND).disabled
    assert any("bài nháp có thể đã có" in e.value for e in at.error)


def test_unexpected_send_error_fixed_message_and_lock(
    project_root, root, fake_ai, site, monkeypatch
):
    """Lỗi lạ khi gửi (không phải ``WordPressError``): câu cố định, không lộ chữ của lỗi gốc (đường
    dẫn, mật khẩu), khóa nút như ``maybe_draft``."""

    def boom(self, title, parts, **kwargs):
        raise RuntimeError(r"C:\Users\bi-mat\anh.jpg mat-khau=abcd efgh")

    monkeypatch.setattr(WordPressClient, "create_draft_with_images", boom)
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.send(at)
    shown = "\n".join(ui.texts(at))
    assert "bi-mat" not in shown and "abcd" not in shown
    assert any("Gửi nháp gặp lỗi không mong đợi" in e.value for e in at.error)
    assert button(at, SEND).disabled


# ================================================================ một ảnh ở hai chỗ, ảnh AI


def test_mark_ai_shows_in_other_spot_with_same_image(project_root, root, fake_ai):
    """Cùng ảnh ở hai chỗ, bấm «Đây là ảnh AI» ở chỗ 1: chỗ 2 vẫn hiện «📷 Ảnh thật», thẻ mã công
    trình, nút «Đây là ảnh AI» và «Đã duyệt» cho alt viết như ảnh thật, trong khi dòng dưới ô alt
    lại nói «Ảnh AI: alt mở đầu «Minh họa»…» (``slot_tags`` đã coi là ảnh AI). Khi gửi thì dừng và
    bắt duyệt lại nên không lên web sai, nhưng điều kiện Lá Chắn T-052 b là «hiện rõ Ảnh thật / Ảnh
    AI từng ảnh» trước khi viết alt. Thấy cả trên trình duyệt thật."""
    at, first, second = same_image_twice(project_root)
    run_ok(by_key(at, f"markai-{first}").click().run())
    assert at.session_state[f"pick-{first}"].is_ai
    assert not any(b.key == f"markai-{second}" for b in at.button)
    assert at.session_state[f"pick-{second}"].is_ai


def test_two_spots_mark_ai_store_failure_both_sent_as_ai(
    project_root, root, monkeypatch, fake_ai, site, sent
):
    """Lấp chỗ test cũ không bắt (gỡ nhánh ``_ai_marked`` của ``slot_tags`` mà test vẫn qua): cùng
    ảnh ở hai chỗ, lưu dấu «ảnh AI» hỏng (file thẻ bận), chỗ 2 đã có alt «Minh họa…» duyệt từ
    trước: khi gửi, **cả hai** chỗ lên web như ảnh AI (Lá Chắn T-074 j), không chỗ nào mang mã công
    trình hay tên file ảnh thật."""

    def busy(self, ref, tags):
        raise ImageTagStoreError("File lưu thẻ ảnh đang bận, thử lại sau.")

    monkeypatch.setattr(ImageTagStore, "set", busy)
    at, first, second = same_image_twice(project_root)
    set_alt(at, first, "Bản lề cổng inox bị gỉ")
    set_alt(at, second, f"{AI_ALT_PREFIX} cánh cổng inox sau khi sửa")
    run_ok(by_key(at, f"markai-{first}").click().run())
    assert at.session_state[f"altok-{first}"] is False  # alt thêm «Minh họa»: duyệt lại
    ui.approve(at, first)
    ui.to_publish(at)
    ui.send(at)
    ((_title, parts),) = sent.calls
    images = [part for part in parts if not isinstance(part, str)]
    assert len(images) == 2
    assert all(image.tags.source == SOURCE_AI and not image.tags.project_code for image in images)
    assert site.file_names() and all(n.startswith("minh-hoa-ai-") for n in site.file_names())


def test_ai_by_file_name_and_folder_name_with_reason(project_root, root, fake_ai):
    """Ảnh AI theo tên file (tên công cụ tạo ảnh) và theo tên thư mục («CongAI», tách chữ hoa):
    hiện «🤖 Ảnh AI» kèm lý do (Lá Chắn T-070 h), không có nút «Đây là ảnh AI»."""
    ui.write(root / PROJECT / "truoc" / "cong-midjourney.png", ui.jpeg())
    ui.write(root / PROJECT / "CongAI" / "x.jpg", ui.jpeg())
    at, pid = ui.open_article(project_root)
    reason = "tên thư mục hoặc tên file có chữ AI hoặc tên công cụ tạo ảnh"
    ui.browse(at, pid)
    ui.open_sub(at, PROJECT)
    ui.open_sub(at, "truoc")
    ui.choose(at, "cong-midjourney.png")
    assert at.session_state[f"pick-{pid}"].is_ai
    assert any(reason in c.value for c in at.caption)
    ui.browse(at, pid)
    run_ok(by_key(at, "browse-up").click().run())
    ui.open_sub(at, "CongAI")
    ui.choose(at, "x.jpg")
    assert at.session_state[f"pick-{pid}"].is_ai
    assert any(reason in c.value for c in at.caption)
    assert not any(b.key == f"markai-{pid}" for b in at.button)


# ============================================================ quét thư mục của ảnh trong nháp


def test_draft_image_not_rescanned_in_page_thread(project_root, root, monkeypatch, fake_ai):
    """Ảnh của nháp (chưa có trong lần quét nào của phiên) được kiểm khi mở nháp; sau đó mỗi lần
    «AI viết alt», «Đây là ảnh AI», «Gửi nháp», ``check_chosen_image`` lại xem danh sách từng tầng
    thư mục cha (``list_folder``) ngay trong luồng của trang, không qua ``_scan_pool``. Ổ Google
    Drive chậm: mỗi tầng tới 10 giây (giới hạn của ``ImageLibrary``), trang không báo "đang quét ở
    nền" (điều kiện Soi Lỗi T-048: quét trong luồng riêng). Mong đợi: bấm «AI viết alt» không quét
    thư mục trong luồng trang (giữ kết quả của lần kiểm khi mở nháp, hoặc quét trong luồng riêng).
    """
    chosen = DraftImage(
        source=SOURCE_REAL, root_index=0, rel_path=REAL_FILE, alt="Bản lề", alt_approved=True
    )
    calls: list[str] = []
    original = ImageLibrary.list_folder

    def spy(self, *args, **kwargs):
        calls.append(threading.current_thread().name)
        return original(self, *args, **kwargs)

    monkeypatch.setattr(ImageLibrary, "list_folder", spy)
    at, pid = ui.open_article(project_root, ui.article(chosen))
    assert calls  # mở nháp: kiểm tên thư mục từng tầng (lớp phòng thứ hai của T-055)
    calls.clear()
    run_ok(by_key(at, f"altai-{pid}").click().run())
    assert [name for name in calls if not name.startswith("quet-anh")] == []


# =========================================================== thư mục, tên file, ảnh lạ


def heic(size=(400, 300)) -> bytes:
    import pillow_heif

    pillow_heif.register_heif_opener()
    buffer = io.BytesIO()
    Image.new("RGB", size, (120, 60, 30)).save(buffer, "HEIF")
    return buffer.getvalue()


def test_heic_chosen_and_truncated_jpeg_blocked(project_root, root, fake_ai):
    """Ảnh HEIC của iPhone (quyết định 1A): xem trước, chọn, AI viết alt được. JPEG bị cắt giữa
    chừng (chép dở từ USB): nút «Chọn» khóa, kèm câu tiếng Việt."""
    folder = root / PROJECT / "truoc"
    ui.write(folder / "IMG_0100.HEIC", heic())
    ui.write(folder / "IMG_0101.jpg", ui.jpeg(size=(800, 600))[:600])
    at, pid = ui.open_article(project_root)
    ui.browse(at, pid)
    ui.open_sub(at, PROJECT)
    ui.open_sub(at, "truoc")
    names = [entry.name for entry in ui.listing(at).images]
    assert not by_key(at, f"choose-{names.index('IMG_0100.HEIC')}").disabled
    assert by_key(at, f"choose-{names.index('IMG_0101.jpg')}").disabled
    ui.choose(at, "IMG_0100.HEIC")
    assert "Ảnh không có vị trí GPS." in [c.value for c in at.caption]
    ui.write_alt(at, pid)
    assert at.session_state[f"alt-{pid}"] == fake_ai_module.ALT.alt
    assert len(fake_ai.image_calls) == 1


def test_empty_folder_and_big_folder_paged(project_root, tmp_path, monkeypatch):
    """Thư mục rỗng: câu báo, không lỗi. Thư mục 3.000 ảnh: 12 ảnh/trang, 250 trang, sang trang
    được (mỗi trang chỉ tạo 12 ảnh xem trước)."""
    base = tmp_path / "Anh"
    big = base / "CT500 - Cổng sắt - Quận 1"
    big.mkdir(parents=True)
    (base / "Thu muc rong").mkdir()
    data = ui.jpeg(size=(16, 12))
    for number in range(3000):
        (big / f"IMG_{number:05d}.jpg").write_bytes(data)
    monkeypatch.setenv("IMAGE_FOLDERS", str(base))
    at, pid = ui.open_article(project_root)
    ui.browse(at, pid)
    ui.open_sub(at, "Thu muc rong")
    assert any("không có ảnh dùng được" in c.value for c in at.caption)
    run_ok(by_key(at, "browse-up").click().run())
    ui.open_sub(at, big.name)
    listing = ui.listing(at)
    assert (listing.total_images, listing.page_count, len(listing.images)) == (3000, 250, 12)
    assert not listing.truncated
    run_ok(by_key(at, "page-next").click().run())
    assert ui.listing(at).page == 2
    assert "Trang 2/250 · 3000 ảnh" in [c.value for c in at.caption]


def test_weird_names_nfd_rlo_markdown(project_root, tmp_path, monkeypatch, fake_ai):
    """Thư mục gốc tên có RLO (U+202E), ``$…$`` (công thức), Markdown; thư mục con tên dạng NFD
    (Mac); file có ký tự rộng 0: không ký tự đảo hướng/vô hình nào lên trang, chữ không thành định
    dạng, thẻ đọc đúng từ tên NFD."""
    nfd = unicodedata.normalize("NFD", "Cổng inox Tân Phú")
    base = tmp_path / "Ảnh \u202egpj.exe $x^2$ red[đỏ] _y_"
    ui.write(base / nfd / "a\u200bb.jpg", ui.jpeg())
    monkeypatch.setenv("IMAGE_FOLDERS", str(base))
    at, pid = ui.open_article(project_root)
    ui.browse(at, pid)
    (option,) = at.selectbox(key="_browse_root").options
    assert option == "\u2068Ảnh \ufffdgpj.exe $x^2$ red[đỏ] _y_\u2069"
    place = next(c.value for c in at.caption if c.value.startswith("Đang xem"))
    assert "\\$x^2\\$" in place and "\\_y\\_" in place and "red\\[đỏ\\]" in place
    ui.open_sub(at, nfd)
    ui.choose(at, "a\u200bb.jpg")
    shown = "\n".join(ui.texts(at))
    assert "\u202e" not in shown and "\u200b" not in shown
    assert "Thẻ: Cổng inox · Tân Phú" in [c.value for c in at.caption]


def test_evil_ai_alt_stays_text_and_listed(project_root, root, fake_ai, site, monkeypatch):
    """AI (bị ảnh có chữ "ra lệnh") trả alt có link, thẻ HTML, số điện thoại, shortcode: alt chỉ nằm
    trong ô nhập (đã lọc link, thẻ), có nhắc số điện thoại, đoạn shortcode được liệt kê; lên
    WordPress thì «[» «]» đã vô hiệu, không còn thẻ HTML nào của AI (U1, LC-T061-4)."""
    evil = AltSuggestion(
        alt="[bấm](javascript:alert(1)) <img src=x onerror=alert(1)> gọi 0909123456 "
        "[code_snippet id=3]",
        caption="**đậm** <script>alert(2)</script> www.evil.example",
    )
    monkeypatch.setattr(fake_ai_module, "ALT", evil)
    at, pid = ui.open_article(project_root)
    ui.choose_real(at, pid)
    ui.write_alt(at, pid)
    alt = at.session_state[f"alt-{pid}"]
    assert "javascript" not in alt and "<img" not in alt and "onerror" not in alt
    assert "<script" not in at.session_state[f"cap-{pid}"]
    assert any("số điện thoại" in w.value for w in at.warning)
    for element in [*at.markdown, *at.caption]:
        if element.proto.allow_html:
            assert "onerror" not in element.value and "javascript" not in element.value
    ui.approve(at, pid)
    ui.to_publish(at)
    assert any("code\\_snippet id=3" in w.value for w in at.warning if "shortcode" in w.value)
    ui.send(at)
    (post,) = site.posts()
    assert "[code_snippet" not in post["content"] and "&#91;code_snippet" in post["content"]
    assert "<script" not in post["content"] and "onerror" not in post["content"]
    (media,) = site.media_writes()
    assert "[" not in media["alt_text"] and "<" not in media["caption"]


def test_alt_after_file_deleted_shows_message_without_ai_call(project_root, root, fake_ai):
    """Ảnh bị xóa sau khi chọn: bấm «AI viết alt» hiện câu tiếng Việt của module ảnh, không gửi gì
    cho AI, ảnh thành «không dùng được»."""
    at, pid = ui.open_article(project_root)
    ui.choose_real(at, pid)
    (root / REAL_FILE).unlink()
    ui.write_alt(at, pid)
    assert any("Không tìm thấy ảnh" in e.value for e in at.error)
    assert fake_ai.image_calls == []
    assert not at.session_state[f"pick-{pid}"].available


def test_broken_tag_file_note_has_no_folder_path(project_root, root):
    """Lấp chỗ test cũ không bắt (đổi câu báo sang đường dẫn đầy đủ mà test vẫn qua, vì test so
    đường dẫn thô với chữ đã escape Markdown): bỏ dấu escape rồi mới so, câu báo chỉ có tên file
    (Lá Chắn T-052 d)."""
    path = image_tags.DEFAULT_IMAGE_TAGS_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"day khong phai SQLite " * 50)
    at, pid = ui.open_article(project_root)
    ui.browse(at, pid)
    ui.open_sub(at, PROJECT)
    ui.open_sub(at, "truoc")
    (note,) = [w.value for w in at.warning if "File lưu thẻ ảnh sửa tay bị hỏng" in w.value]
    plain = note.replace("\\", "")
    (moved,) = path.parent.glob("image_tags.hong-*")
    assert moved.name in plain
    assert path.parent.name not in plain and path.parent.parent.name not in plain
