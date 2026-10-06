"""Cài đặt (DEMO): mô hình AI theo từng việc, checklist chất lượng, thư mục ảnh."""

import streamlit as st

from seo_app import demo
from seo_app.config import load_settings

settings = load_settings()

st.title("Cài đặt")
demo.banner(2, "Chọn mô hình AI theo từng việc")

st.subheader("Mô hình AI cho từng việc")
st.caption(
    "Lưu trong file config/ai_models.toml (không phải .env, vì không phải bí mật), nên đổi "
    "được mà không sửa code và tự đồng bộ giữa 2 máy qua GitHub."
)
st.dataframe(demo.AI_TASKS, hide_index=True)

st.subheader("Checklist chất lượng bài viết")
st.caption("AI tự rà soát mọi bài theo danh sách này trước khi đưa bạn xem.")
for item, _ok, _note in demo.CHECKLIST:
    st.markdown(f"- {item}")

st.subheader("Thư mục ảnh")
if settings.image_folders:
    for folder in settings.image_folders:
        found = "✅ tìm thấy" if folder.is_dir() else "⚠️ không tìm thấy trên máy này"
        st.markdown(f"- `{folder}` — {found}")
else:
    st.write("Chưa khai báo. Điền IMAGE_FOLDERS trong file .env.")
