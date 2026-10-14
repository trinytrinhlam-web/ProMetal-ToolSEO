"""Mảnh giao diện dùng chung (HTML nhỏ + tiện ích Streamlit)."""

from __future__ import annotations

import html
import re
from collections.abc import Iterable, Mapping

import streamlit as st


def page_header(title: str, subtitle: str = "", *, demo: bool = False) -> None:
    st.title(title)
    if subtitle:
        st.markdown(f'<p class="page-sub">{html.escape(subtitle)}</p>', unsafe_allow_html=True)
    if demo:
        st.caption(
            ":orange-badge[🧪 Bản demo] dữ liệu mẫu — bấm thử thoải mái, chưa gọi AI thật "
            "và không gửi gì đi đâu."
        )


def progress_dots(total: int, done: int) -> str:
    dots = "".join(f'<span class="{"on" if i < done else ""}"></span>' for i in range(total))
    return f'<div class="progress-dots">{dots}</div>'


def score_panel(overall: int, scores: Mapping[str, int], *, warn_below: int = 80) -> str:
    """Bảng điểm văn phong. Điểm ép về số nguyên 0–100 trước khi chèn vào HTML."""

    def pct(value: object) -> int:
        return max(0, min(100, int(value)))

    overall = pct(overall)
    label = "Tốt" if overall >= 85 else "Khá" if overall >= 75 else "Cần sửa"
    bars = "".join(
        f'<div class="bar {"warn" if v < warn_below else ""}">'
        f'<div class="row"><span>{html.escape(str(k))}</span><b>{v}</b></div>'
        f'<div class="track"><div class="fill" style="width:{v}%"></div></div></div>'
        for k, v in ((k, pct(v)) for k, v in scores.items())
    )
    return (
        f'<div class="score-big"><span class="v">{overall}</span><span class="of">/100</span>'
        f'<span class="tag">{label}</span></div>{bars}'
    )


def serp_preview(title: str, url: str, description: str) -> str:
    return (
        f'<div class="serp"><div class="url">{html.escape(url)}</div>'
        f'<div class="t">{html.escape(title)}</div>'
        f'<div class="d">{html.escape(description)}</div></div>'
    )


def _escape_text(text: str) -> str:
    """Escape ``&``, ``<``, ``>``: đủ để chữ không thành thẻ HTML khi nằm ngoài thuộc tính.

    Không đổi dấu nháy để bài tiếng Việt có ngoặc kép vẫn hiện đúng cả trong đoạn ``code``.
    """
    return html.escape(text, quote=False)


def highlight(text: str, tone: Iterable[str] = (), missing: Iterable[str] = ()) -> str:
    """Tô vàng câu nghe máy móc, tô đỏ chỗ thiếu số liệu (văn bản là markdown).

    Kết quả được hiển thị bằng ``unsafe_allow_html=True`` nên mọi chữ (bài do AI viết, câu
    AI chỉ ra, chữ người dùng tự sửa) đều được escape trước; thẻ HTML duy nhất
    trong kết quả là ``<mark>`` do chính hàm này thêm vào. Tô trong một lượt duy nhất để
    không tô nhầm vào thẻ ``<mark>`` vừa chèn.
    """
    classes: dict[str, str] = {}
    for css_class, parts in (("tone", tone), ("missing", missing)):
        for part in parts:
            if part and part.strip():
                classes.setdefault(_escape_text(part), css_class)
    safe = _escape_text(text)
    if not classes:
        return safe
    pattern = re.compile("|".join(map(re.escape, sorted(classes, key=len, reverse=True))))
    return pattern.sub(lambda m: f'<mark class="{classes[m.group(0)]}">{m.group(0)}</mark>', safe)


WEEKDAYS = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]


def day_label(day) -> str:
    """«Thứ Ba, 06/10»."""
    return f"{WEEKDAYS[day.weekday()]}, {day:%d/%m}"
