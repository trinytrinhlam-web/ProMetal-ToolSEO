"""Lá Chắn T-136 (Opus 5.5): bước đọc đầu file chung ``sqlite_file.newer_file_format``.

LC-T136-1 (Thấp, Mac/Linux): ``newer_file_format`` mở thẳng đường dẫn bằng ``open()`` (chế độ
đọc, có chờ) **trước** khi biết đó là file thường. Ba kho lưu tạm (``site_index``, ``plan_cache``,
``search_cache``) gọi bước này ở mỗi lần mở mà không kiểm «file thường» trước (kho nháp, kho thẻ
ảnh có ``is_file()`` trước nên không bị):

- chỗ đặt file là **FIFO** (Mac/Linux: chương trình lạ ghi được vào ``data/`` tạo bằng
  ``mkfifo``): ``open()`` chờ đầu ghi **mãi**, trang dùng kho đó treo, mỗi lần tải lại thêm một
  luồng treo. Trước T-136 bước đầu tiên chạm file là ``sqlite3.connect`` (SQLite mở đọc-ghi, không
  chờ trên FIFO) nên chỉ báo lỗi;
- chỗ đặt file là **thư mục**: ``open()`` ném lỗi quyền, câu báo đổi (cùng gốc với Soi Lỗi T-136
  G1).

Kỳ vọng: chỗ đặt file không phải file thường thì ``newer_file_format`` trả ``False`` ngay (để
SQLite và kho xét như trước T-136), không chờ, không ném. Không gọi mạng; mọi file trong
``tmp_path``. Ca FIFO chỉ chạy được trên Mac/Linux (chạy cùng các ca Mac, Lá Chắn T-131 B.3).
"""

from __future__ import annotations

import os
import threading

import pytest

from seo_app.storage import sqlite_file


def test_lc_t136_1_header_check_skips_a_folder(tmp_path):
    folder = tmp_path / "site_index.sqlite"
    folder.mkdir()
    assert sqlite_file.newer_file_format(folder) is False


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="FIFO chỉ có trên Mac/Linux")
def test_lc_t136_1_header_check_never_waits_on_a_fifo(tmp_path):
    fifo = tmp_path / "site_index.sqlite"
    os.mkfifo(fifo)
    result: dict[str, object] = {}

    def check() -> None:
        try:
            result["value"] = sqlite_file.newer_file_format(fifo)
        except OSError as exc:
            result["error"] = type(exc).__name__

    thread = threading.Thread(target=check, daemon=True)
    thread.start()
    thread.join(3)
    blocked = thread.is_alive()
    if blocked:
        # Gỡ treo cho ca test: mở đầu ghi (không chờ) rồi đóng ngay; đầu đọc gặp hết file.
        os.close(os.open(fifo, os.O_WRONLY | os.O_NONBLOCK))
        thread.join(3)
    assert not blocked, "newer_file_format chờ mãi khi chỗ đặt file là FIFO"
    assert result == {"value": False}
