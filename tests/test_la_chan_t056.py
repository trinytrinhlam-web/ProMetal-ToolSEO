"""Lá Chắn T-056: chỗ cần ảnh thật và «Gửi nháp» kèm ảnh trên trang Soạn bài (``write.py``).

Bổ sung cho ``tests/test_app_images.py`` (Họa Sĩ) và ``tests/test_soi_loi_t056.py`` (Soi Lỗi), dùng
lại ảnh giả, WordPress giả, AI giả của hai file đó. Không gọi mạng thật, không dùng ảnh thật.

- **LC-T056-1** (Thấp): khóa «gửi dở» mất khi lần chạy bị dừng **lần nữa** đúng lúc đang ghi khóa.
  Trong Streamlit 1.65 mọi lần đọc/ghi ``st.session_state`` là điểm dừng (Soi Lỗi T-056, mục «Phát
  hiện chính»). ``mark_send_interrupted`` bỏ dấu ``_wp_sending`` **trước**, rồi mới ghi
  ``_wp_result`` và ``_wp_maybe_draft``: một yêu cầu chạy lại (cú bấm thứ ba) tới đúng khe đó thì
  lần chạy dừng khi dấu đã mất mà khóa chưa có; lần sau nút «Gửi nháp» bật, không nhắc gì, bấm là
  bài nháp thứ hai, ảnh (có GPS) tải lần hai. Đánh dấu ``xfail(strict=True)``: sửa xong (ghi khóa
  trước, bỏ dấu sau) thì test tự báo XPASS để gỡ dấu.
- Rủi ro 2 của Họa Sĩ (``walk_to_folder``, nhánh danh sách thư mục cha bị cắt mở thẳng
  ``list_folder`` theo tên lấy từ ``checked.ref``, có thể là chữ trong nháp): Lá Chắn **chấp nhận**.
  Test đối chứng (đang qua) giữ tính chất an toàn của nhánh đó: nháp trỏ vào thư mục là lối tắt
  (junction/symlink) ra ngoài thư mục ảnh thì không mở được, không ảnh nào ngoài thư mục ảnh lên
  khung chọn; nhắc GPS công khai vẫn nằm ngay trước nút khi đang khóa «gửi dở».
"""

from __future__ import annotations

import pytest
import test_app_images as ui
import test_soi_loi_t056 as sl
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.runtime.scriptrunner_utils.script_requests import RerunData
from streamlit.runtime.state.safe_session_state import SafeSessionState

from seo_app.images.folders import FolderListing, ImageLibrary
from seo_app.images.tags import SOURCE_REAL
from seo_app.storage.drafts import DraftImage

# Fixture dùng chung (mật khẩu thử, cache ảnh xem trước tạm, AI giả, thư mục ảnh, WordPress giả).
env = ui.env
previews = ui.previews
fake_ai = ui.fake_ai
root = ui.root
site = ui.site

button = ui.button
run_ok = ui.run_ok
SEND = ui.SEND_LABEL


def interrupt_while_marking(monkeypatch) -> list[str]:
    """Yêu cầu chạy lại tới đúng lúc ``mark_send_interrupted`` ghi câu «gửi dở» (sau khi đã bỏ dấu
    ``_wp_sending``): như cú bấm thứ ba của người dùng bấm liên tục khi app có vẻ treo. Trả danh
    sách ghi lại lúc yêu cầu được gửi (để test biết đã tới đúng chỗ)."""
    original = SafeSessionState.__setitem__
    fired: list[str] = []

    def setitem(self, key, value):
        message = value.get("message", "") if isinstance(value, dict) else ""
        if not fired and key == "_wp_result" and str(message).startswith(ui.INTERRUPTED):
            fired.append(key)
            ctx = get_script_run_ctx()
            ctx.script_requests.request_rerun(RerunData(page_script_hash=ctx.page_script_hash))
        return original(self, key, value)

    monkeypatch.setattr(SafeSessionState, "__setitem__", setitem)
    return fired


@pytest.mark.xfail(
    strict=True,
    reason="LC-T056-1: lần chạy bị dừng lần nữa lúc đang ghi khóa «gửi dở» thì mất khóa",
)
def test_lc_t056_1_second_stop_while_marking_keeps_lock(
    project_root, root, fake_ai, site, monkeypatch
):
    """Gửi nháp; trong lúc gửi người dùng bấm gì đó (lần chạy dừng, dấu ``_wp_sending`` còn); lần
    chạy sau ``init_state`` gọi ``mark_send_interrupted``, và một cú bấm nữa tới đúng lúc nó ghi
    câu «gửi dở». Mong đợi: nút «Gửi nháp» vẫn khóa (phải tick «Tôi đã kiểm tra…»). Thực tế: dấu
    đã bị bỏ trước khi khóa được ghi, nút bật lại, không nhắc gì."""
    sl.interrupt_while_sending(monkeypatch)
    fired = interrupt_while_marking(monkeypatch)
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.send(at)
    assert fired == ["_wp_result"]  # đã ngắt đúng chỗ
    assert len(site.posts()) == 1  # bài nháp đã lên website
    assert "_wp_sending" not in at.session_state
    assert button(at, SEND).disabled, "nút «Gửi nháp» bật lại: bấm là bài nháp thứ hai"


def test_cut_listing_walk_never_opens_link_out_of_root(project_root, tmp_path, monkeypatch):
    """Rủi ro 2 (chấp nhận): nháp ghi ảnh trong thư mục ``zz-loi-tat`` là lối tắt ra ngoài thư mục
    ảnh; danh sách thư mục cha bị cắt (không thấy ``zz-loi-tat``) nên «Mở thư mục chứa ảnh» mở thẳng
    phần còn lại bằng ``list_folder``. ``list_folder`` từ chối lối tắt: khung chọn ở lại thư mục
    cha, không ảnh nào ngoài thư mục ảnh được quét hay hiện; mở nháp thì ảnh không dùng được."""
    images = tmp_path / "Anh cong trinh"
    ui.write(images / ui.REAL_FILE, ui.jpeg())
    for number in range(10):  # xếp trước ``zz-loi-tat``: danh sách bị cắt không thấy nó
        (images / ui.PROJECT / f"A{number:02d}").mkdir()
    outside = tmp_path / "ngoai thu muc anh"
    ui.write(outside / "bi-mat.jpg", ui.jpeg(gps=True))
    ui.make_link(images / ui.PROJECT / "zz-loi-tat", outside)
    monkeypatch.setenv("IMAGE_FOLDERS", str(images))

    def small(cls, settings, **kwargs):
        return cls(settings.image_folders, max_entries=3)

    monkeypatch.setattr(ImageLibrary, "from_settings", classmethod(small))
    calls: list[str] = []
    original = ImageLibrary.list_folder

    def spy(self, root_index, rel_dir="", **kwargs):
        calls.append(rel_dir)
        return original(self, root_index, rel_dir, **kwargs)

    monkeypatch.setattr(ImageLibrary, "list_folder", spy)
    chosen = DraftImage(
        source=SOURCE_REAL,
        root_index=0,
        rel_path=f"{ui.PROJECT}/zz-loi-tat/bi-mat.jpg",
        category="Cổng inox",
        alt="Bản lề cổng inox bị gỉ",
        alt_approved=True,
    )
    at, pid = ui.open_article(project_root, ui.article(chosen))
    assert not at.session_state[f"pick-{pid}"].available  # đi qua lối tắt: không dùng được
    run_ok(ui.by_key(at, f"openfolder-{pid}").click().run())
    scans = at.session_state["_scans"]
    assert scans[(0, ui.PROJECT, 1)].truncated  # đúng nhánh danh sách bị cắt
    assert f"{ui.PROJECT}/zz-loi-tat" in calls  # nhánh đó đã mở thẳng theo tên trong nháp
    assert isinstance(scans[(0, f"{ui.PROJECT}/zz-loi-tat", 1)], str)  # bị từ chối, câu báo
    assert at.session_state["_browse"]["dir"] == ui.PROJECT
    listed = [
        entry.name
        for value in scans.values()
        if isinstance(value, FolderListing)
        for entry in value.images
    ]
    assert "bi-mat.jpg" not in listed  # tên ảnh của nháp vẫn hiện ở khung ảnh (chữ trong nháp)
    shown = "\n".join(ui.texts(at))
    assert str(outside) not in shown and str(tmp_path) not in shown


def test_gps_warning_right_before_button_while_locked(
    project_root, root, fake_ai, site, monkeypatch
):
    """Đang khóa «gửi dở» (có ô xác nhận «Tôi đã kiểm tra…»): nhắc ảnh (có GPS) công khai vẫn nằm
    ngay trước nút «Gửi nháp» (Lá Chắn T-046 số 8, T-054 4b)."""
    sl.interrupt_while_sending(monkeypatch)
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.send(at)
    run_ok(at.checkbox(key="_wp_checked").check().run())
    elements = list(ui.flatten(at.main))
    index = next(i for i, e in enumerate(elements) if getattr(e, "label", "") == SEND)
    assert "xem được công khai" in elements[index - 1].value
    assert not button(at, SEND).disabled
