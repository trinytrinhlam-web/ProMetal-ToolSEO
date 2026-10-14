"""Xử lý chuỗi tiếng Việt."""

from __future__ import annotations

import html
import re
import unicodedata


def remove_accents(text: str) -> str:
    """Bỏ dấu tiếng Việt: "Cửa sắt Đà Nẵng" -> "Cua sat Da Nang"."""
    text = text.replace("đ", "d").replace("Đ", "D")
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def slugify(text: str, max_length: int = 80) -> str:
    """Chuỗi chữ thường không dấu, nối bằng "-": "Cửa sắt 2 cánh!" -> "cua-sat-2-canh"."""
    ascii_text = remove_accents(text).lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    if len(slug) > max_length:
        slug = slug[:max_length].rsplit("-", 1)[0] or slug[:max_length]
    return slug


def paragraphs_to_html(text: str) -> str:
    """Văn bản thường -> HTML: mỗi đoạn (cách nhau dòng trống) thành một thẻ <p>.

    Ký tự đặc biệt được mã hóa để không bị hiểu nhầm thành thẻ HTML.
    """
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text.replace("\r\n", "\n"))]
    return "\n".join("<p>" + html.escape(p).replace("\n", "<br>") + "</p>" for p in paragraphs if p)
