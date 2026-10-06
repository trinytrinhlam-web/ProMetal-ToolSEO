"""Kế hoạch từ khóa (DEMO): đồng bộ với Google Sheets."""

import streamlit as st

from seo_app import demo
from seo_app.config import load_settings

settings = load_settings()

st.title("Kế hoạch từ khóa")
demo.banner(5, "Đồng bộ kế hoạch với Google Sheets")

st.caption(
    "Kế hoạch nằm trên Google Sheets nên máy công ty và máy nhà luôn thấy giống nhau. "
    "Sửa trên Sheets hoặc ngay tại đây đều được."
)

left, right = st.columns([3, 1])
with left:
    chosen = st.multiselect("Lọc theo trạng thái", demo.STATUSES, placeholder="Tất cả")
with right:
    st.write("")
    demo.button("🔄 Đồng bộ Google Sheets", 5)

rows = demo.keyword_rows(settings.now().date())
if chosen:
    rows = [r for r in rows if r["Trạng thái"] in chosen]

st.dataframe(
    rows,
    hide_index=True,
    column_config={"Ngày dự kiến": st.column_config.DateColumn(format="DD/MM/YYYY")},
)

st.subheader("Bắt đầu viết")
keyword = st.selectbox(
    "Chọn từ khóa chưa viết",
    [
        r["Từ khóa"]
        for r in demo.keyword_rows(settings.now().date())
        if r["Trạng thái"] == "Chưa viết"
    ],
)
demo.button(f"✍️ Viết bài cho «{keyword}»", 2, primary=True)
