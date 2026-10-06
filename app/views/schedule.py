"""Lịch đăng (DEMO): bài nháp, bài hẹn giờ, bài đã đăng trên WordPress."""

import streamlit as st

from seo_app import demo
from seo_app.config import load_settings

settings = load_settings()

st.title("Lịch đăng")
demo.banner(5, "Lịch đăng và hẹn giờ")
st.caption(
    "Lịch lấy thẳng từ WordPress. Bài hẹn giờ do WordPress tự đăng đúng giờ — "
    "máy tắt hay app không mở cũng không sao."
)

rows = demo.schedule_rows(settings.now())
status = st.segmented_control("Xem", ["Tất cả", "Nháp", "Đã hẹn giờ", "Đã đăng"], default="Tất cả")
if status and status != "Tất cả":
    rows = [r for r in rows if r["Trạng thái"] == status]
st.dataframe(rows, hide_index=True)

st.subheader("Hẹn giờ một bài nháp")
with st.form("schedule"):
    st.selectbox("Bài nháp", ["Cách chống gỉ cửa sắt tại nhà", "So sánh inox 201 và 304"])
    left, right = st.columns(2)
    left.date_input("Ngày đăng", format="DD/MM/YYYY")
    right.time_input("Giờ đăng")
    st.caption(f"Giờ theo múi {settings.timezone_name}.")
    if st.form_submit_button("📅 Hẹn giờ"):
        st.toast("Bản demo: hẹn giờ sẽ hoạt động ở Giai đoạn 5.", icon="🧪")
