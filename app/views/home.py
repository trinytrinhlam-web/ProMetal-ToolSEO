"""Trang chủ: tình trạng cấu hình."""

import streamlit as st

from seo_app.config import load_settings

settings = load_settings()

st.title("SEO App")
st.caption(f"Giờ hiện tại: {settings.now():%H:%M %d/%m/%Y} ({settings.timezone_name})")

st.subheader("Tình trạng cấu hình")
st.write("Các mục chưa khai báo sẽ được dùng ở những giai đoạn sau, chưa cần điền ngay.")
for label, configured in settings.status().items():
    icon = "✅" if configured else "⚪"
    note = "đã khai báo" if configured else "chưa khai báo"
    st.markdown(f"{icon} **{label}**: {note}")

st.info("Chọn chức năng ở menu bên trái. Các chức năng mới sẽ lần lượt được thêm vào.")
