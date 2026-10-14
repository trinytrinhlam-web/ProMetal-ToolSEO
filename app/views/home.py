"""Bài viết: các bài đang viết, bài tiếp theo trong kế hoạch, bài đã gửi WordPress."""

import html

import streamlit as st

from seo_app import demo, ui
from seo_app.config import load_settings

settings = load_settings()

top_left, top_right = st.columns([3, 1], vertical_alignment="bottom")
with top_left:
    ui.page_header(
        "Bài viết",
        f"{len(demo.ARTICLES_IN_PROGRESS)} bài đang viết · {ui.day_label(settings.now())}",
        demo=True,
    )
with top_right, st.popover("✍️ Viết bài mới", type="primary", width="stretch"):
    st.text_input("Từ khóa", placeholder="ví dụ: lan can cầu thang sắt")
    st.caption("hoặc chọn từ kế hoạch")
    st.selectbox(
        "Từ kế hoạch",
        [
            r["Từ khóa"]
            for r in demo.plan_rows(settings.now().date())
            if r["Trạng thái"] == "Chưa viết"
        ],
        label_visibility="collapsed",
    )
    if st.button("Bắt đầu", type="primary", width="stretch"):
        st.switch_page("views/write.py")

st.subheader("Đang viết")
cols = st.columns(3)
for col, article in zip(cols, demo.ARTICLES_IN_PROGRESS, strict=False):
    with col, st.container(border=True, height="stretch"):
        step = article["step"]
        st.markdown(
            f'<div class="card-kw">{html.escape(article["keyword"])}</div>'
            f'<div class="card-title">{html.escape(article["title"])}</div>'
            + ui.progress_dots(len(demo.STEPS), step),
            unsafe_allow_html=True,
        )
        badge = f":blue-badge[Bước {step}/{len(demo.STEPS)} · {demo.STEPS[step - 1]}]"
        if article["score"]:
            color = "green" if article["score"] >= 85 else "orange"
            badge += f" :{color}-badge[Văn phong {article['score']}]"
        st.markdown(badge)
        st.markdown(
            f'<div class="card-note">{html.escape(article["note"])} · {article["updated"]}</div>',
            unsafe_allow_html=True,
        )
        if st.button("Mở bài", key=f"open-{article['keyword']}", width="stretch"):
            st.switch_page("views/write.py")

left, right = st.columns([3, 2], gap="large")
with left:
    st.subheader("Tiếp theo trong kế hoạch")
    upcoming = [r for r in demo.plan_rows(settings.now().date()) if r["Trạng thái"] == "Chưa viết"]
    for row in upcoming[:3]:
        with st.container(border=True):
            a, b, c = st.columns([5, 2, 2], vertical_alignment="center")
            a.markdown(f"**{row['Từ khóa']}**  \n:gray[{row['Ý định']}]")
            b.markdown(f":gray[Dự kiến]  \n{row['Ngày dự kiến']:%d/%m}")
            if c.button("Bắt đầu", key=f"start-{row['Từ khóa']}", width="stretch"):
                st.switch_page("views/write.py")
    st.page_link("views/plan.py", label="Xem cả kế hoạch", icon="🗂️")
with right:
    st.subheader("Đã gửi WordPress")
    with st.container(border=True):
        for row in demo.SENT_TO_WORDPRESS:
            color = "green" if row["Trạng thái"] == "Đã đăng" else "violet"
            st.markdown(
                f"**{row['Bài']}**  \n:{color}-badge[{row['Trạng thái']}] :gray[{row['Ngày']}]"
            )
