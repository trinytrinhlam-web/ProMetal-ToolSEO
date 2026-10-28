"""Lá Chắn T-039: test chứng minh LC-T039-2 (Thấp); đã sửa ở T-096, bỏ ``xfail``.

``place_links`` in lại chữ của nút chữ được chèn link bằng ``html.escape``, không vô hiệu "[" "]"
(T-061): chạy trên HTML đã qua ``sanitize_html`` (thứ tự khuyên dùng) thì "&#91;…&#93;" ở nút
chữ đó trở lại thành shortcode trần cho tới lần lọc cuối. Hôm nay lần lọc cuối luôn có
(``create_draft`` gọi ``sanitize_html``), test canh ở cuối file giữ điều đó.

Không gọi mạng: danh sách bài dựng tay.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from seo_app.onpage.links import InternalLink, apply_links, place_links
from seo_app.sanitize import sanitize_html
from seo_app.storage.site_index import SiteIndex
from seo_app.wordpress import PublishedItem

SITE = "https://suachuacuasat.com"
SERVICE = PublishedItem(
    id=10,
    type="page",
    slug="sua-cua-keo-tphcm",
    link=f"{SITE}/sua-cua-keo-tphcm/",
    title="Sửa cửa kéo tại TP.HCM",
)
INDEX = SiteIndex(
    site=SITE,
    fetched_at=datetime(2026, 10, 22, 9, 0, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh")),
    items=(SERVICE,),
)
LINK = InternalLink(section=0, anchor="dịch vụ sửa cửa kéo", post_id=10)
# Chữ AI bị dụ viết shortcode vào bài (T-061): cùng nút chữ với cụm từ được chèn link.
SHORTCODE_HTML = [
    "<p>Gọi dịch vụ sửa cửa kéo [code_snippet id=1] ngay.</p>",
    "<p>[embed]https://evil.example/x[/embed] rồi gọi dịch vụ sửa cửa kéo.</p>",
    "<p>Gọi dịch vụ sửa cửa kéo [[caption]] hoặc [/caption] nhé.</p>",
]


@pytest.mark.parametrize("raw", SHORTCODE_HTML)
def test_lc2_applied_text_keeps_shortcodes_neutralized(raw):
    # LC-T039-2 đã sửa ở T-096 (``place_links`` vô hiệu lại "[" "]" ở nút chữ đã lọc): bỏ xfail.
    clean = sanitize_html(raw)
    assert "[" not in clean and "]" not in clean  # điều kiện đầu: T-061 đã vô hiệu
    placed = place_links(clean, [LINK], INDEX)
    assert placed.applied == (LINK,)
    assert "[" not in placed.html and "]" not in placed.html


@pytest.mark.parametrize("raw", SHORTCODE_HTML)
def test_lc2_final_filter_still_neutralizes(raw):
    """Canh: lọc → chèn → lọc (thứ tự khuyên dùng) thì không còn "[" "]" trần, link còn."""
    out = sanitize_html(apply_links(sanitize_html(raw), [LINK], INDEX))
    assert "[" not in out and "]" not in out
    assert f'<a href="{SERVICE.link}">dịch vụ sửa cửa kéo</a>' in out
