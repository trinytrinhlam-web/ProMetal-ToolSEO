"""Trang WordPress: kiểm tra kết nối, xem chuyên mục/thẻ, tạo thử bài nháp.

Mọi chữ lấy từ WordPress (tên site, tên tài khoản, vai trò, tiêu đề bài, địa chỉ ảnh, câu lỗi có
chữ của máy chủ) đều qua ``escape_markdown`` trước khi vào Markdown: không thành link, không thành
định dạng, không thành HTML (T-044, SL-T031-1). Bảng chuyên mục/thẻ dùng ``st.dataframe`` (chữ
thường, không đọc Markdown). Trang này không dùng ``unsafe_allow_html``.
"""

import streamlit as st

from seo_app.config import load_settings
from seo_app.text import escape_markdown, paragraphs_to_html
from seo_app.wordpress import WordPressClient, WordPressError

settings = load_settings()

st.title("WordPress")

try:
    client = WordPressClient.from_settings(settings)
except WordPressError as exc:
    st.warning(
        f"{escape_markdown(str(exc))}\n\nCách làm: xem mục **Kết nối WordPress** trong "
        "README.md. Điền xong thì tắt app rồi mở lại."
    )
    st.stop()

st.caption(
    f"Website: {escape_markdown(client.base_url)} · "
    f"Tài khoản: {escape_markdown(settings.wordpress_username)}"
)
if not client.uses_https:
    st.warning(
        "Địa chỉ website đang dùng http (không bảo mật). WordPress thường chỉ cho dùng "
        "Application Password qua https. Nên đổi WORDPRESS_URL sang https://."
    )

# ----------------------------------------------------------------- 1. Kết nối
st.header("1. Kiểm tra kết nối")
if st.button("Kiểm tra kết nối"):
    with st.spinner("Đang kết nối tới WordPress..."):
        try:
            st.session_state["wp_info"] = client.check_connection()
        except WordPressError as exc:
            st.session_state.pop("wp_info", None)
            st.error(escape_markdown(str(exc)))

info = st.session_state.get("wp_info")
if info:
    roles = ", ".join(escape_markdown(role) for role in info.roles) or "không rõ"
    st.success(
        f"Kết nối thành công tới **{escape_markdown(info.site_name)}** "
        f"({escape_markdown(info.site_url)})."
    )
    st.markdown(
        f"- Tài khoản: **{escape_markdown(info.user_name)}** — vai trò: {roles}\n"
        f"- Viết bài: {'✅' if info.can_edit_posts else '❌'} · "
        f"Đăng bài: {'✅' if info.can_publish_posts else '❌'} · "
        f"Tải ảnh lên: {'✅' if info.can_upload_files else '❌'}"
    )
    if not (info.can_edit_posts and info.can_upload_files):
        st.warning(
            "Tài khoản thiếu quyền viết bài hoặc tải ảnh. Nên dùng tài khoản có vai trò "
            "Biên tập viên (Editor) hoặc Quản trị viên (Administrator)."
        )

# ------------------------------------------------------- 2. Chuyên mục và thẻ
st.header("2. Chuyên mục và thẻ")
if st.button("Tải chuyên mục và thẻ"):
    with st.spinner("Đang tải..."):
        try:
            st.session_state["wp_categories"] = client.list_categories()
            st.session_state["wp_tags"] = client.list_tags()
        except WordPressError as exc:
            st.error(escape_markdown(str(exc)))

categories = st.session_state.get("wp_categories")
tags = st.session_state.get("wp_tags")
if categories is not None and tags is not None:
    left, right = st.columns(2)
    for column, label, terms in ((left, "Chuyên mục", categories), (right, "Thẻ", tags)):
        with column:
            st.subheader(f"{label} ({len(terms)})")
            if terms:
                st.dataframe(
                    [{"ID": t.id, "Tên": t.name, "Slug": t.slug, "Số bài": t.count} for t in terms],
                    hide_index=True,
                )
            else:
                st.write("Chưa có.")

# --------------------------------------------------------- 3. Tạo bài nháp thử
st.header("3. Tạo thử một bài nháp")
st.caption(
    "Bài chỉ được lưu **NHÁP** trên WordPress: khách không thấy cho tới khi bạn tự đăng trong "
    "trang quản trị. Kiểm tra xong có thể xóa bài thử trong WordPress."
)
if categories is None:
    st.caption("Muốn chọn chuyên mục/thẻ: bấm **Tải chuyên mục và thẻ** ở mục 2 trước.")

with st.form("draft", clear_on_submit=False):
    title = st.text_input("Tiêu đề")
    content = st.text_area("Nội dung (mỗi đoạn cách nhau một dòng trống)", height=200)
    chosen_categories = st.multiselect(
        "Chuyên mục", categories or [], format_func=lambda t: t.name, placeholder="Chọn..."
    )
    chosen_tags = st.multiselect(
        "Thẻ", tags or [], format_func=lambda t: t.name, placeholder="Chọn..."
    )
    image = st.file_uploader(
        "Ảnh đại diện (không bắt buộc)", type=["jpg", "jpeg", "png", "webp", "gif"]
    )
    alt_text = st.text_input("Mô tả ảnh (alt) — nói rõ ảnh chụp gì")
    submitted = st.form_submit_button("Tạo bài nháp")

if submitted:
    try:
        with st.spinner("Đang gửi sang WordPress..."):
            media = None
            if image is not None:
                media = client.upload_media(image.getvalue(), image.name, alt_text=alt_text)
            post = client.create_draft(
                title,
                paragraphs_to_html(content),
                categories=[t.id for t in chosen_categories],
                tags=[t.id for t in chosen_tags],
                featured_media=media.id if media else None,
            )
    except WordPressError as exc:
        st.error(escape_markdown(str(exc)))
    else:
        st.success(f"Đã tạo bài nháp #{post.id}: **{escape_markdown(post.title)}**")
        if media:
            st.markdown(f"Ảnh đại diện đã tải lên: {escape_markdown(media.source_url)}")
        st.link_button("Mở bài trong trang quản trị WordPress", post.edit_link)
