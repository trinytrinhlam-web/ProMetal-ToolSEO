"""Chỗ app ghi dữ liệu trong máy (``data/``) không bị thay bằng liên kết (T-117, LC-T116-1).

Lá Chắn T-116 (Fable): thư mục ``data/`` (hay một thư mục con) mà là junction hay symlink thì cache
ảnh xem trước và kho thẻ ảnh sửa tay ghi file ra nơi liên kết trỏ tới, ngoài thư mục dự án (F1).
Hàm ở đây ``lstat`` từng tầng (không đi theo liên kết, không ``resolve``) từ ngay dưới gốc dự án
xuống tới chỗ cần ghi; gặp liên kết thì nơi gọi không ghi. «Liên kết» dùng đúng định nghĩa của lớp
đọc ảnh (``folders._is_link_stat``): symlink; trên Windows thêm junction và mọi reparse point trỏ
đi chỗ khác (file «chỉ trực tuyến» của OneDrive, Google Drive không tính).

Chỉ chặn liên kết **có sẵn** lúc kiểm; liên kết đặt vào đúng khoảnh khắc giữa lúc kiểm và lúc ghi
thì không chặn được (nơi gọi kiểm lại ở mỗi lần đọc, ghi). Muốn đặt liên kết phải ghi được vào thư
mục cài app (cùng lớp «phải chiếm máy trước» trong sổ rủi ro).

Đặt ở gói ``images`` (cạnh ``folders``) chứ không ở ``storage``: nạp ``seo_app.storage`` là chạy
``storage/__init__`` (kéo theo kho nháp, lớp AI), làm ``process.py`` nạp chậm thêm ~1,9 giây (đo
bằng ``python -X importtime``, T-117). Kho trong ``storage`` nhập từ đây như đã nhập ``folders``.
"""

from __future__ import annotations

import os
from pathlib import Path

# Một định nghĩa «liên kết» chung với lớp đọc ảnh (T-048, T-079), không viết lại.
from seo_app.images.folders import _is_link_stat

# Câu cố định, không đường dẫn.
MSG_DATA_DIR_LINK = (
    "Thư mục dữ liệu của phần mềm (thư mục data nằm trong thư mục phần mềm, hay một thư mục con "
    "của nó) là lối tắt trỏ ra chỗ khác nên phần mềm không ghi vào đó. Hãy thay lối tắt đó bằng "
    "một thư mục thường."
)


def is_link(path: Path) -> bool:
    """Chính ``path`` (không xét các tầng trên) là liên kết. Chưa có trên ổ thì ``False``."""
    try:
        return _is_link_stat(os.lstat(path))
    except (FileNotFoundError, NotADirectoryError):
        return False


def dir_has_link(directory: Path, root: Path) -> bool:
    """Có tầng nào từ ngay dưới ``root`` xuống tới chính ``directory`` là liên kết.

    Không xét ``root`` và các tầng trên nó (thư mục cài app có thể nằm dưới một lối tắt hợp lệ của
    máy). So đường dẫn theo chữ (``abspath``, không ``resolve``). ``directory`` không nằm dưới
    ``root`` (chỉ có trong test, khi trỏ kho sang thư mục tạm) thì xét chính nó và thư mục cha của
    nó, đủ cho kiểu ``data/<thư mục con>``. Tầng chưa có trên ổ thì dừng: app sẽ tự tạo nó là thư
    mục thường. Lỗi đọc khác (``OSError``) để nơi gọi xử lý.
    """
    target = Path(os.path.abspath(directory))
    base = Path(os.path.abspath(root))
    try:
        parts = target.relative_to(base).parts
    except ValueError:
        base = target.parent.parent
        parts = target.parts[len(base.parts) :]
    current = base
    for part in parts:
        current = current / part
        try:
            if _is_link_stat(os.lstat(current)):
                return True
        except (FileNotFoundError, NotADirectoryError):
            return False
    return False
