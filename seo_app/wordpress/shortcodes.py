"""Tìm đoạn dạng shortcode WordPress trong chữ sắp gửi lên website (T-056, LC-T061-4).

App gửi bài lên WordPress đã vô hiệu mọi "[" "]" (``&#91;`` ``&#93;``, T-061), nên shortcode không
chạy lúc tạo nháp. Lớp đó chỉ giữ tới lúc **người** mở bài nháp trong trang quản trị rồi sửa và
lưu: trình soạn có thể đọc ``&#91;`` thành "[" trần, lúc đó WordPress chạy đoạn ấy như lệnh. Nên
trước nút «Gửi nháp», giao diện liệt kê rõ từng đoạn để người dùng xóa.

Cùng quy tắc với chỗ chặn chữ SEO của client (``_has_shortcode``, ``_SHORTCODE_OPEN`` trong
``seo_app/wordpress/client.py``), dùng thẳng hai thứ đó để không lệch nhau: "[" (có thể thêm một
"[" hay "/") ngay trước ký tự ``do_shortcode`` nhận làm tên, và có "]" phía sau. Xét trên chữ đã
gỡ ký tự vô hình (``_drop_invisible``): ký tự rộng 0 chen trong tên (``[code\\u200b_snippet]``) bị
gỡ trước khi tới WordPress, nên đoạn đó vẫn là shortcode.
"""

from __future__ import annotations

from seo_app.wordpress.client import _SHORTCODE_OPEN, _drop_invisible


def find_shortcodes(text: object) -> list[str]:
    """Mọi đoạn dạng shortcode trong ``text``, theo thứ tự, trên chữ đã gỡ ký tự vô hình.

    Mỗi đoạn chạy từ "[" mở đầu tới "]" gần nhất phía sau (``[code_snippet id=3]``,
    ``[/embed]``, ``[[tên]``). Có đoạn nào thì ``_has_shortcode`` của client cũng đúng trên cùng
    chữ, và ngược lại. Không phải chữ thì là danh sách rỗng.

    Một lượt, tuyến tính: "[" mở đầu không có "]" phía sau thì các "[" sau nó cũng không có.
    """
    if not isinstance(text, str) or not text:
        return []
    text = _drop_invisible(text)
    found: list[str] = []
    position = 0
    while True:
        match = _SHORTCODE_OPEN.search(text, position)
        if match is None:
            return found
        close = text.find("]", match.end())
        if close < 0:
            return found
        found.append(text[match.start() : close + 1])
        position = close + 1


__all__ = ["find_shortcodes"]
