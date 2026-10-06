"""Ảnh (DEMO): ảnh thật từ thư mục đã khai báo, và tạo ảnh bằng AI."""

import streamlit as st
from PIL import Image, ImageDraw

from seo_app import demo
from seo_app.config import load_settings

settings = load_settings()

st.title("Ảnh")
demo.banner(3, "Xử lý ảnh")


@st.cache_data
def placeholder(name: str, shade: int) -> Image.Image:
    """Ảnh xám thay cho ảnh thật trong bản demo."""
    image = Image.new("RGB", (400, 280), (shade, shade, shade + 8))
    ImageDraw.Draw(image).text((16, 250), name, fill=(255, 255, 255))
    return image


real, generated = st.tabs(["Ảnh thật", "Tạo ảnh bằng AI"])

with real:
    folders = [str(f) for f in settings.image_folders] or ["G:/My Drive/Anh SEO (ví dụ)"]
    st.selectbox("Thư mục ảnh (khai báo trong .env)", folders)

    cols = st.columns(len(demo.IMAGES))
    for i, (col, img) in enumerate(zip(cols, demo.IMAGES, strict=True)):
        with col:
            st.image(placeholder(img["Ảnh gốc"], 90 + i * 25))
            st.checkbox(f"Chọn {img['Ảnh gốc']}", value=i < 2, key=f"pick_{i}")

    st.markdown("**Sau khi xử lý**")
    st.dataframe(demo.IMAGES, hide_index=True)
    st.caption(
        "Mỗi ảnh được: nén sang WebP, đổi tên không dấu theo nội dung, xóa vị trí GPS trong "
        "dữ liệu ảnh (để không lộ địa chỉ nhà khách), và AI viết alt mô tả đúng ảnh chụp gì. "
        "Ảnh gốc trong thư mục của bạn được giữ nguyên."
    )
    left, right = st.columns(2)
    with left:
        demo.button("⚙️ Xử lý ảnh đã chọn", 3, key="process", primary=True)
    with right:
        demo.button("📤 Tải lên thư viện WordPress", 3, key="upload")

with generated:
    st.caption(
        "Chỉ dùng khi không có ảnh thật phù hợp (ví dụ ảnh minh họa khái niệm). "
        "Ảnh thật của xưởng luôn tốt hơn cho SEO và lòng tin của khách."
    )
    st.text_area(
        "Mô tả ảnh cần tạo",
        "Sơ đồ đơn giản so sánh lớp bảo vệ bề mặt của inox 201 và 304, nền trắng, không chữ.",
        height=80,
    )
    st.radio("Tỉ lệ", ["16:9 (ảnh đầu bài)", "1:1", "4:3"], horizontal=True)
    demo.button("🎨 Tạo ảnh", 3, key="generate", primary=True)
