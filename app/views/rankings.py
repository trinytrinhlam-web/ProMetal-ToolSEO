"""Thứ hạng (DEMO): số liệu Google Search Console theo từng bài."""

import altair as alt
import streamlit as st

from seo_app import demo
from seo_app.config import load_settings

settings = load_settings()

st.title("Thứ hạng")
demo.banner(6, "Theo dõi Search Console")

# Bộ lọc nằm trên cùng, một hàng.
left, right = st.columns([1, 2])
with left:
    st.selectbox("Khoảng thời gian", ["28 ngày qua", "7 ngày qua", "3 tháng qua"])
with right:
    article = st.selectbox("Bài viết", demo.ARTICLES)

cols = st.columns(4)
cols[0].metric("Lượt click", "412", delta="+22%")
cols[1].metric("Lượt hiển thị", "9.800", delta="+15%")
cols[2].metric("CTR", "4,2%", delta="+0,3 điểm")
cols[3].metric(
    "Vị trí trung bình",
    "6,1",
    delta="-1,4",
    delta_color="inverse",
    help="Số càng nhỏ càng tốt (1 = đứng đầu Google)",
)

trend = demo.weekly_trend(settings.now().date())
base = alt.Chart(alt.Data(values=trend)).encode(
    x=alt.X("Tuần:T", title=None, axis=alt.Axis(format="%d/%m", grid=False)),
)
clicks_chart = base.mark_line(strokeWidth=2, point=alt.OverlayMarkDef(size=40)).encode(
    y=alt.Y("Click:Q", title=None),
    tooltip=[alt.Tooltip("Tuần:T", format="%d/%m/%Y"), "Click:Q"],
)
position_chart = base.mark_line(strokeWidth=2, point=alt.OverlayMarkDef(size=40)).encode(
    y=alt.Y("Vị trí TB:Q", title=None, scale=alt.Scale(reverse=True, zero=False)),
    tooltip=[alt.Tooltip("Tuần:T", format="%d/%m/%Y"), "Vị trí TB:Q"],
)

chart_left, chart_right = st.columns(2)
with chart_left:
    st.markdown(f"**Lượt click mỗi tuần** — {article}")
    st.altair_chart(clicks_chart, width="stretch")
with chart_right:
    st.markdown("**Vị trí trung bình** (càng lên cao càng tốt)")
    st.altair_chart(position_chart, width="stretch")

st.subheader("Từ khóa đưa khách tới bài này")
st.dataframe(demo.keyword_ranking_rows(), hide_index=True)

st.subheader("Tất cả bài viết")
st.dataframe(demo.ranking_rows(), hide_index=True)
