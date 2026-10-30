"""Lá Chắn T-099 (đầy đủ, soát kỹ nhất): đường hẹn giờ, đăng ngay ``release_draft``.

Lỗi tìm ra (``xfail(strict=True)``; sửa xong thì gỡ dấu):

- **LC-T099-1** (Thấp): ``release_draft`` kiểm «mã bài thuộc ``_created_post_ids``» rồi mới bỏ mã
  khỏi tập **sau** lệnh kiểm nháp (có chờ mạng). Hai luồng dùng **chung một** đối tượng client gọi
  ``release_draft`` cùng một bài thì cả hai cùng qua bước kiểm, cùng gửi lệnh chuyển: 2 lệnh vào
  một bài, trái lời hứa «từ đây không lệnh nào của client sửa tiếp bài này». Thiết kế đã dặn tạo
  client mới cho mỗi lần bấm (LC-T094-23), nên app đúng thiết kế không gặp; đây là lớp phòng cho
  đường quan trọng nhất. Cách sửa gợi ý: giành mã bài ngay đầu hàm (``set.remove``, một bước),
  trả lại mã khi bị chặn trước lệnh chuyển (lỗi lệnh kiểm nháp, giờ, đồng hồ).

Không gọi WordPress thật: ``FakeWordPress`` (bộ chặn mạng của ``tests/conftest.py`` vẫn bật).
"""

from __future__ import annotations

import json
import threading
from datetime import UTC, datetime, timedelta
from email.utils import format_datetime

import pytest
from fake_wordpress import BASE_URL, FakeWordPress, make_session

from seo_app.wordpress import WordPressClient
from seo_app.wordpress import client as client_module
from seo_app.wordpress.client import ReleaseError

POSTS = "/wp-json/wp/v2/posts"
NOW = datetime(2026, 11, 2, 1, 0, tzinfo=UTC)


@pytest.fixture(autouse=True)
def fixed_clock(monkeypatch):
    monkeypatch.setattr(client_module, "_utc_now", lambda: NOW)


def _released(request):
    body = json.loads(request.body)
    return {"id": 42, "status": body["status"], "date_gmt": body.get("date_gmt", ""), "link": ""}


def _site(check) -> FakeWordPress:
    fake = FakeWordPress()
    fake.on("POST", POSTS, (201, {"id": 42, "status": "draft", "title": {"raw": "T"}}, {}))
    fake.on("GET", f"{POSTS}/42", check)
    fake.on("POST", f"{POSTS}/42", _released)
    return fake


def _client(fake: FakeWordPress) -> WordPressClient:
    client = WordPressClient(BASE_URL, "lam", "abcd efgh ijkl", session=make_session(fake))
    client.create_draft("T", "<p>x</p>")
    return client


def _release_posts(fake: FakeWordPress) -> int:
    prefix = f"{POSTS}/"
    return sum(1 for r in fake.requests if r.method == "POST" and r.path_url.startswith(prefix))


DRAFT = (200, {"id": 42, "status": "draft"}, {"Date": format_datetime(NOW, usegmt=True)})


@pytest.mark.xfail(
    strict=True,
    reason="LC-T099-1: release_draft kiểm mã thuộc _created_post_ids rồi mới bỏ mã sau lệnh kiểm "
    "nháp; hai luồng dùng chung một client cùng qua bước kiểm, gửi 2 lệnh chuyển vào một bài",
)
def test_lc_t099_1_hai_luong_chung_mot_client_chi_mot_lenh_chuyen():
    arrived = threading.Condition()
    count = [0]

    def slow_check(_request):
        # Chờ luồng thứ hai tới lệnh kiểm nháp (tối đa 5 giây): code đúng thì luồng thứ hai bị
        # từ chối ngay từ đầu, không tới đây; chờ hết giờ rồi đi tiếp.
        with arrived:
            count[0] += 1
            arrived.notify_all()
            arrived.wait_for(lambda: count[0] >= 2, timeout=5)
        return DRAFT

    fake = _site(slow_check)
    client = _client(fake)
    outcomes: list[str] = []

    def worker():
        try:
            client.release_draft(42, mode="publish")
            outcomes.append("đăng")
        except ReleaseError:
            outcomes.append("từ chối")

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(15)
    assert sorted(outcomes) == ["từ chối", "đăng"]
    assert _release_posts(fake) == 1


def test_lc_t099_1_doi_chung_goi_lan_luot_chi_mot_lenh_chuyen():
    fake = _site(DRAFT)
    client = _client(fake)
    client.release_draft(42, mode="publish")
    with pytest.raises(ReleaseError):
        client.release_draft(42, mode="publish")
    assert _release_posts(fake) == 1


def test_lc_t099_1_doi_chung_bi_chan_truoc_lenh_chuyen_thi_van_goi_lai_duoc():
    """Cách sửa không được làm mất điều này: bị chặn trước lệnh chuyển (thiếu header ``Date``)
    thì bài vẫn là của client, lần sau (đủ điều kiện) hẹn giờ được."""
    answers = iter([(200, {"id": 42, "status": "draft"}, {}), DRAFT])
    fake = _site(lambda _request: next(answers))
    client = _client(fake)
    with pytest.raises(ReleaseError, match="Không đọc được giờ của website"):
        client.release_draft(42, mode="future", when_utc=NOW + timedelta(hours=2))
    assert _release_posts(fake) == 0
    released = client.release_draft(42, mode="future", when_utc=NOW + timedelta(hours=2))
    assert released.status == "future"
    assert _release_posts(fake) == 1
