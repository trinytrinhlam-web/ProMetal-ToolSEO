"""Lá Chắn T-089 (xem lại lượt 2 + 3): ghi kết quả «Gửi nháp» kiểu so rồi đặt
(``app/views/write.py``).

Bổ sung cho ``tests/test_t089_send_draft.py`` (Họa Sĩ) và ``tests/test_soi_loi_t089.py`` (Soi
Lỗi), dùng lại ảnh giả, WordPress giả, AI giả của ``tests/test_app_images.py``. Không gọi mạng thật.

- **LC-T089-1** (Thấp, có từ trước: mã lượt 1 và ``main`` cũng vậy): tab 2 thấy khóa «gửi dở» trong
  lúc tab 1 đang gửi, người dùng cố ý tick «Tôi đã kiểm tra…» rồi gửi (Ghi nhận 1 của biên bản
  T-089). Tab 1 tạo xong bài 501 **trước**; kết quả không ghi đè «đang gửi» của tab 2 (đúng thiết
  kế, ``kept_other``). Sau đó lần gửi của tab 2 hỏng mà chưa tạo bài nào (ví dụ website quá tải lúc
  tải ảnh: ``maybe_draft`` tắt), nên ``record_outcome`` của tab 2 ghi «chưa gửi»: xóa dòng trạng
  thái gửi. Nháp không còn dấu vết bài 501; tab 2 và phiên mới mở nháp đều thấy nút «Gửi nháp» bật,
  không nhắc gì, bấm là ra bài thứ hai. Thứ tự ngược lại (tab 2 hỏng trước) là SL-T089-2, đã sửa.
  Đánh dấu ``xfail(strict=True)``: sửa xong thì test tự báo XPASS để gỡ dấu.

Hai lần gửi chồng nhau kiểu «tab 1 bắt đầu, tab 2 bắt đầu, tab 1 xong, tab 2 xong» không dựng
được bằng hai phiên AppTest lồng nhau (lồng thì lần bên trong luôn xong trước). Nên tab 1 là
phiên AppTest thật; tab 2 chạy đúng ``send_and_record`` của trang (lấy từ lần chạy đang gửi của
tab 1) trên một luồng riêng, với ``seen`` và mã bài như ``draft_panel`` tính ở lần vẽ tab 2 thấy
«gửi dở». ``send_and_record``, ``record_outcome`` không đụng ``st.session_state`` nên chạy được
ngoài lần chạy.
"""

from __future__ import annotations

import sys
import threading
from datetime import UTC, datetime

import test_app_images as ui
import test_t086_send_state as t86
from fake_wordpress import BASE_URL

from seo_app.publish.render import ArticlePart, build_article
from seo_app.storage.site_index import SiteIndex
from seo_app.wordpress.client import DraftImagesError

# Fixture dùng chung (mật khẩu thử, cache ảnh xem trước tạm, AI giả, thư mục ảnh, WordPress giả).
env = ui.env
previews = ui.previews
fake_ai = ui.fake_ai
root = ui.root
site = ui.site

button = ui.button
SEND = ui.SEND_LABEL
KEPT = "nháp giữ trạng thái gửi của tab kia"
WAIT = 30  # giây: chỉ để test không treo khi có gì sai, không phải chỗ đợi bình thường


def write_page() -> dict:
    """Biến toàn cục của ``app/views/write.py`` ở lần chạy đang gọi tới đây (AppTest chạy trang bằng
    ``exec``, không nằm trong ``sys.modules``)."""
    frame = sys._getframe(1)
    while frame is not None:
        if "send_and_record" in frame.f_globals and "record_outcome" in frame.f_globals:
            return frame.f_globals
        frame = frame.f_back
    raise LookupError("không thấy app/views/write.py trong ngăn gọi")


class OverloadedSite:
    """Client của tab 2: tải ảnh đầu tiên thì website quá tải (503). Lỗi ở bước tải ảnh nên chưa có
    bài nháp nào (``maybe_draft`` tắt, như ``WordPressClient.create_draft_with_images``). Ghi lại
    đúng lệnh nhận được (T-102: gói của bộ dựng gửi thêm chuyên mục, thẻ, đoạn trích, slug)."""

    def __init__(self) -> None:
        self.started = threading.Event()
        self.release = threading.Event()
        self.calls: list[tuple] = []

    def create_draft_with_images(self, title, parts, **fields):
        self.calls.append((title, list(parts), fields))
        self.started.set()  # tab 2 đã ghi «đang gửi» của nó, đang tải ảnh
        self.release.wait(WAIT)  # tab 1 tạo xong bài 501 trước
        raise DraftImagesError(
            "Lỗi thử: website quá tải lúc tải ảnh.", maybe_uploaded=True, status_code=503
        )


def test_lc_t089_1_confirmed_send_elsewhere_creating_nothing_keeps_this_post(
    project_root, root, fake_ai, site
):
    """Mong đợi: bài 501 của tab 1 có trên website thì nháp vẫn khóa («đã gửi 501», hay «gửi dở»
    để người dùng kiểm trang quản trị), dù lần gửi tab 2 xong sau và chưa tạo gì. Thực tế: tab 2
    ghi «chưa gửi» bằng so rồi đặt với chính «đang gửi» của nó (khớp, vì tab 1 không ghi đè) nên
    xóa dòng; phiên mới mở nháp nút bật."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    draft = at.session_state["draft_id"]
    tab2 = {"draft": draft, "result": None, "state": None}
    # T-102 (R5, Chỉ Huy B duyệt 30/10 18:45): ``send_and_record`` nhận gói của bộ dựng T-096.
    package = build_article(
        title="Bài thử",
        parts=[ArticlePart(heading="Mở bài", body="Đoạn thử.")],
        index=SiteIndex(site=BASE_URL, fetched_at=datetime.now(UTC), items=()),
    )
    client2 = OverloadedSite()
    threads: list[threading.Thread] = []
    steps: list[object] = []
    failures: list[Exception] = []
    original = site.create_post

    def create_post(request):  # website đang tạo bài 501 cho tab 1
        page = write_page()
        saved = ui.store().load_send_state(draft)  # «đang gửi» của tab 1: tab 2 thấy «gửi dở»
        steps.append(saved is not None and saved.pending)

        def send_in_tab2() -> None:
            try:
                page["send_and_record"](
                    client2,
                    ui.store(),
                    tab2,
                    package,
                    list(package.sections),
                    saved.post_id if saved else None,
                    (saved, False),
                )
            except Exception as exc:  # báo ở luồng chính
                failures.append(exc)

        thread = threading.Thread(target=send_in_tab2, daemon=True)
        threads.append(thread)
        thread.start()
        steps.append(client2.started.wait(WAIT))
        return original(request)  # bài 501 của tab 1

    site.fake.on("POST", ui.POSTS, create_post)
    ui.send(at)  # tab 1: bài 501, kết quả không ghi đè «đang gửi» của tab 2
    client2.release.set()
    for thread in threads:
        thread.join(WAIT)
    assert steps == [True, True] and not failures
    assert not any(thread.is_alive() for thread in threads)
    # Lệnh tạo nháp của tab 2 mang đúng gói (không nuốt lặng các trường T-102 gửi thêm).
    assert client2.calls == [
        (
            "Bài thử",
            ["<p>Đoạn thử.</p>"],
            {"categories": (), "tags": (), "excerpt": package.excerpt, "slug": ""},
        )
    ]
    assert tab2.get("claimed") is not None  # tab 2 đã ghi được «đang gửi» của nó (sau tab 1)
    assert tab2["state"] == (False, None)  # tab 2 chưa tạo bài nào
    assert len(site.posts()) == 1
    assert any(f"mã {ui.POST_ID}" in s.value for s in at.success)
    assert any(KEPT in w.value for w in at.warning)
    # Bài 501 có trên website: nháp phải còn khóa.
    assert ui.store().load_send_state(draft) is not None
    fresh = t86.reopen(project_root, draft)
    assert button(fresh, SEND).disabled
