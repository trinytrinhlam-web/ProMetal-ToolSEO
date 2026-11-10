"""Soi Lỗi T-127 (rút gọn): nút «Đưa vào kế hoạch» (từ khóa Google → đề xuất «Thêm» chờ duyệt).

- Chốt chặn (qua): bộ lọc chặt LC-T120-24 bỏ ký tự vô hình, chữ toàn khổ, chữ Nga, chữ Hy Lạp,
  công thức (``=HYPERLINK``…), dấu cách lạ, xuống dòng, gạch dài, dấu tổ hợp lạ, số điện thoại
  nhiều dạng, «www»/«http»; nhận đúng 80 ký tự, chữ tổ hợp tách rời (NFD). Danh sách bài trên máy
  còn mới thì đề xuất cảnh báo trùng bài đã đăng như T-098, không gọi website.
- **SL-T127-1** (Thấp): trang Kế hoạch kiểm trùng bài đã đăng bằng ``cached_index()`` (bản lưu
  tạm, kể cả đã cũ; không có thì bỏ qua), không tải lại, không báo; các đường đề xuất T-098 dùng
  ``fresh_index()`` (cũ hơn 6 giờ thì tải lại, không tải được thì báo câu). Bài đăng sau lần lưu
  danh sách không được so, người dùng không biết.

Không gọi mạng thật (bộ chặn mạng chung của ``conftest``, client giả đếm lệnh); mọi file lưu tạm
trong thư mục tạm.
"""

from __future__ import annotations

import unicodedata
from datetime import UTC, datetime, timedelta

import pytest
import test_app_pages as pages
import test_t125_tracking_page as page_tests
from test_t125_tracking_page import run, texts
from test_t127_dua_vao_ke_hoach import open_keywords

from seo_app.plan import propose
from seo_app.storage import site_index
from seo_app.storage.site_index import SiteIndex, SiteIndexStore
from seo_app.wordpress.client import WordPressError

env = pages.env
private_key = page_tests.private_key
key_file = page_tests.key_file
data_files = page_tests.data_files  # autouse: mọi file lưu tạm trong thư mục tạm
configured = page_tests.configured
no_network = page_tests.no_network

C = chr
REJECTED = {
    "zwsp": "sửa" + C(0x200B) + "cửa",
    "word-joiner": "sửa" + C(0x2060) + "cửa",
    "bom": C(0xFEFF) + "sửa cửa",
    "hangul-filler": "sửa" + C(0x3164) + "cửa",
    "soft-hyphen": "sửa" + C(0x00AD) + "cửa",
    "rlo": "sửa " + C(0x202E) + "cửa",
    "toan-kho": C(0xFF53) + "ửa cửa",
    "so-toan-kho": "cửa " + C(0xFF11),
    "nga-c": "sửa " + C(0x0441) + "ửa",
    "hy-lap-o": "s" + C(0x03BF) + "a",
    "hyperlink": '=HYPERLINK("http://x.vn","bấm")',
    "bang-dau": "=1+1",
    "cong-dau": "+cửa",
    "nbsp": "sửa" + C(0x00A0) + "cửa",
    "tab": "sửa" + C(0x09) + "cửa",
    "xuong-dong": "sửa" + C(0x0A) + "cửa",
    "gach-dai": "cửa " + C(0x2013) + " cuốn",
    "to-hop-la": "cửa" + C(0x0336),
    "dt-lien": "sửa cửa 0909123456",
    "dt-cach": "sửa cửa 0909 123 456",
    "dt-gach": "sửa cửa 0909-123-456",
    "dt-84": "sửa cửa 84 909 123 456",
    "dt-ban": "goi 0283 812 3456",
    "www": "www suachuacuasat com",
    "http": "http suachuacuasat",
    "dai-81": "a" * 81,
}


@pytest.mark.parametrize("name", list(REJECTED), ids=list(REJECTED))
def test_strict_filter_rejects(name):
    assert propose.google_keyword(REJECTED[name]) is None


def test_strict_filter_accepts_80_chars_and_decomposed_vietnamese():
    assert propose.google_keyword("a" * 80) == "a" * 80
    decomposed = unicodedata.normalize("NFD", "sửa cửa cuốn")
    assert decomposed != "sửa cửa cuốn"
    assert propose.google_keyword(decomposed) == "sửa cửa cuốn"
    assert propose.google_keyword("  sửa   cửa  ") == "sửa cửa"


@pytest.fixture
def wordpress(monkeypatch, configured):
    """Đã khai báo đủ tài khoản WordPress (giá trị giả, không gọi mạng): trang Kế hoạch dựng được
    client nên đọc được danh sách bài đã lưu."""
    monkeypatch.setenv("WORDPRESS_USERNAME", "lam")
    monkeypatch.setenv("WORDPRESS_APP_PASSWORD", "abcd efgh")
    return configured


def picked_and_sent(project_root, *, stale_published_list: bool = False):
    at = open_keywords(project_root)  # bài 11 «Sửa cửa kéo bị kẹt ray», danh sách bài đã lưu
    run(at.multiselect(key="trk-plan-pick").set_value(["sửa cửa kéo bị kẹt"]))
    if stale_published_list:
        # Danh sách bài trên máy cũ hơn 6 giờ (lần lấy số liệu Google gần nhất từ hôm trước):
        # trang Theo dõi vẫn vẽ bảng từ bản lưu tạm này.
        old = datetime.now(UTC) - timedelta(hours=site_index.DEFAULT_MAX_AGE_HOURS + 1)
        SiteIndexStore(path=site_index.DEFAULT_SITE_INDEX_FILE).save(
            SiteIndex(page_tests.WORDPRESS, old, page_tests.POSTS)
        )
    run(at.button(key="trk-to-plan").click())
    (proposal,) = at.session_state["plan_proposals"].items
    shown = [*at.session_state["plan_notes"]]
    for kind in ("warning", "info", "caption", "error", "markdown"):
        shown.extend(texts(at, kind))
    return proposal, shown


def test_published_post_duplicate_is_warned_when_the_list_is_fresh(
    project_root, wordpress, no_network
):
    proposal, shown = picked_and_sent(project_root)
    assert propose.WARN_DUPLICATE_POST.format(post_id=11) in proposal.warnings
    assert propose.WARN_DUPLICATE_ROW.format(key="B-012") in proposal.warnings
    assert not proposal.preselected
    assert no_network.count == 0  # danh sách còn mới: không gọi website (như T-098)
    assert not any("danh sách bài đã đăng" in str(text) for text in shown)


def test_sl_t127_1_stale_published_list_is_refreshed_or_told(project_root, wordpress, no_network):
    no_network.error = WordPressError  # website không trả lời: như mất mạng thật
    _proposal, shown = picked_and_sent(project_root, stale_published_list=True)
    refreshed = no_network.count > 0
    told = any("danh sách bài đã đăng" in str(text) for text in shown)
    assert refreshed or told
