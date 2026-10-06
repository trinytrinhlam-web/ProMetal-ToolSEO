"""Mảnh giao diện dùng chung (HTML nhỏ + tiện ích Streamlit)."""

from __future__ import annotations

import html
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
    label = "Tốt" if overall >= 85 else "Khá" if overall >= 75 else "Cần sửa"
    bars = "".join(
        f'<div class="bar {"warn" if v < warn_below else ""}">'
        f'<div class="row"><span>{html.escape(k)}</span><b>{v}</b></div>'
        f'<div class="track"><div class="fill" style="width:{v}%"></div></div></div>'
        for k, v in scores.items()
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


def highlight(text: str, tone: Iterable[str] = (), missing: Iterable[str] = ()) -> str:
    """Tô vàng câu nghe máy móc, tô đỏ chỗ thiếu số liệu (văn bản là markdown)."""
    for sentence in tone:
        text = text.replace(sentence, f'<mark class="tone">{sentence}</mark>')
    for part in missing:
        text = text.replace(part, f'<mark class="missing">{part}</mark>')
    return text


WEEKDAYS = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]


def day_label(day) -> str:
    """«Thứ Ba, 06/10»."""
    return f"{WEEKDAYS[day.weekday()]}, {day:%d/%m}"
