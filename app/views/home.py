"""Trang chủ: tổng quan công việc (demo) và tình trạng cấu hình (thật)."""

import streamlit as st

from seo_app import demo
from seo_app.config import load_settings

settings = load_settings()

st.title("SEO App")
st.caption(f"Giờ hiện tại: {settings.now():%H:%M %d/%m/%Y} ({settings.timezone_name})")

st.subheader("Tổng quan")
demo.banner(5, "Số liệu tổng quan (lấy từ WordPress, Google Sheets, Search Console)")
cols = st.columns(4)
cols[0].metric("Bài nháp", 2)
cols[1].metric("Đã hẹn giờ", 2, help="Bài sẽ tự đăng trên WordPress đúng giờ đã chọn")
cols[2].metric("Đã đăng tháng này", 5)
cols[3].metric("Lượt click 28 ngày", "607", delta="+18%")

st.markdown("**Việc cần làm**")
st.markdown(
    "- ✍️ Duyệt dàn ý bài **«So sánh inox 201 và 304»**\n"
    "- 🔢 Bổ sung số liệu thật cho mục *Chi phí* trong bài đang viết\n"
    "- 🖼️ 3 ảnh mới trong thư mục ảnh chưa có alt\n"
    "- 📈 Bài **«Sơn tĩnh điện là gì?»** ở vị trí 14,7 — nên viết thêm phần hỏi đáp"
)

st.divider()
st.subheader("Tình trạng cấu hình")
st.write("Các mục chưa khai báo sẽ được dùng ở những giai đoạn sau, chưa cần điền ngay.")
for label, configured in settings.status().items():
    icon = "✅" if configured else "⚪"
    note = "đã khai báo" if configured else "chưa khai báo"
    st.markdown(f"{icon} **{label}**: {note}")
