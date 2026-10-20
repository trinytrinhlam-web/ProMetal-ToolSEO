"""Đặt tên file ảnh chuẩn SEO (phiếu T-049, thiết kế T-046 mục 2 "Đặt tên file").

- Tên không dấu, chữ thường, nối bằng ``-`` (dùng ``slugify`` có sẵn), tối đa ``MAX_NAME_CHARS``
  ký tự (chưa tính đuôi ``.webp``).
- Theo nội dung: ``hạng mục + khu vực + mã công trình``; thiếu thẻ thì dùng alt đã duyệt; cuối cùng
  là ``anh``. Ảnh AI có tiền tố ``minh-hoa-ai-`` và không bao giờ mang mã công trình thật.
- Tránh trùng trong cùng một bài: thêm ``-2``, ``-3``…
- **Không** nhận tên thư mục hay tên file gốc (góp ý Lá Chắn T-046 số 3): tên thư mục có thể chứa
  tên, địa chỉ khách, mà tên file ảnh thì công khai trên web. Hàm chỉ nhận thẻ đã chuẩn hóa (khu vực
  khớp danh sách quận/huyện cố định, việc của T-052) và alt người dùng đã duyệt. Mã công trình chỉ
  nhận đúng mẫu ``CT`` + số, sai mẫu thì bỏ.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

from seo_app.text import slugify

MAX_NAME_CHARS = 60  # chưa tính đuôi file (thiết kế T-046)
WEB_EXTENSION = ".webp"
AI_PREFIX = "minh-hoa-ai"
FALLBACK_NAME = "anh"
MAX_DUPLICATES = 999  # quá số này thì báo lỗi thay vì lặp mãi

_PROJECT_CODE = re.compile(r"CT\d{1,6}", re.IGNORECASE)
# Tên thiết bị của Windows: ``con.webp`` không lưu được thành file trên Windows.
_WINDOWS_DEVICE_NAMES = frozenset(
    {"con", "prn", "aux", "nul"} | {f"{dev}{n}" for dev in ("com", "lpt") for n in "123456789"}
)


def _project_code(value: str) -> str:
    """Mã công trình đúng mẫu ``CT012``; sai mẫu thì bỏ (không đưa chữ tự do vào tên file)."""
    value = value.strip()
    return value if _PROJECT_CODE.fullmatch(value) else ""


def _base_name(category: str, area: str, project_code: str, alt: str, ai_generated: bool) -> str:
    prefix = f"{AI_PREFIX}-" if ai_generated else ""
    limit = MAX_NAME_CHARS - len(prefix)
    code = "" if ai_generated else _project_code(project_code)
    slug = slugify(" ".join((category, area, code)), max_length=limit)
    if not slug:
        slug = slugify(alt, max_length=limit)
    if not slug or slug in _WINDOWS_DEVICE_NAMES:
        slug = f"{slug}-{FALLBACK_NAME}" if slug else FALLBACK_NAME
    return prefix + slug


def _with_suffix(base: str, number: int) -> str:
    suffix = f"-{number}"
    return base[: MAX_NAME_CHARS - len(suffix)].rstrip("-") + suffix


def image_file_name(
    *,
    category: str = "",
    area: str = "",
    project_code: str = "",
    alt: str = "",
    ai_generated: bool = False,
    taken: Iterable[str] = (),
    extension: str = WEB_EXTENSION,
) -> str:
    """Tên file cho một ảnh trong bài, ví dụ ``cong-inox-tan-phu-ct012.webp``.

    ``category`` (hạng mục), ``area`` (khu vực) phải là thẻ đã chuẩn hóa; ``alt`` là alt người dùng
    đã duyệt. ``taken``: các tên đã dùng trong bài (có hoặc không có đuôi, không phân biệt hoa
    thường); trùng thì thêm ``-2``, ``-3``… ``ai_generated=True``: thêm tiền tố ``minh-hoa-ai-``
    và bỏ mã công trình.
    """
    base = _base_name(category, area, project_code, alt, ai_generated)
    used = set()
    for name in taken:
        key = name.casefold()
        used.add(key.removesuffix(extension.casefold()))
    if base not in used:
        return base + extension
    for number in range(2, MAX_DUPLICATES + 1):
        candidate = _with_suffix(base, number)
        if candidate not in used:
            return candidate + extension
    raise ValueError("Quá nhiều ảnh trùng tên trong một bài.")
