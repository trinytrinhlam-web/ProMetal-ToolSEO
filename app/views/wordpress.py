"""Trang WordPress: kiểm tra kết nối, xem chuyên mục/thẻ, tạo thử bài nháp (chữ thuần).

Mọi chữ lấy từ WordPress (tên site, tên tài khoản, vai trò, tiêu đề bài, câu lỗi có chữ của máy
chủ) đều qua ``escape_markdown`` trước khi vào Markdown: không thành link, không thành định dạng,
không thành HTML (T-044, SL-T031-1). Bảng chuyên mục/thẻ dùng ``st.dataframe`` (chữ thường, không
đọc Markdown). Trang này không dùng ``unsafe_allow_html``.

Bài nháp thử không có ảnh (T-108, LC-T093-1): ảnh chỉ lên website qua «Gửi nháp» của trang Soạn
bài, sau bước làm sạch ảnh (quyết định 2A).
"""

import streamlit as st

from seo_app.config import load_settings
from seo_app.plan.sync import safe_text
from seo_app.text import escape_markdown, paragraphs_to_html
from seo_app.wordpress import ConnectionInfo, WordPressClient, WordPressError

# Vai trò WordPress mặc định có quyền ``unfiltered_html`` trên site đơn (T-106).
_UNFILTERED_ROLES = frozenset({"editor", "administrator"})


def plain(value: object) -> str:
    """Chữ từ WordPress -> Markdown chỉ hiện chữ thường.

    WordPress có thể trả sai kiểu (số, danh sách, null): ép sang chuỗi để trang không hỏng
    (Soi Lỗi SL-T044-1, SL-T044-2); ``None`` thành chuỗi rỗng.
    """
    if value is None:
        return ""
    return escape_markdown(value if isinstance(value, str) else str(value))


def cell(value: object) -> object:
    """Ô chữ của bảng chuyên mục/thẻ: mở đầu bằng ``=``, ``+``, ``-``, ``@``, tab, CR thì thêm một
    dấu cách đầu (``safe_text``), để bảng tải về CSV (nút trên thanh công cụ của ``st.dataframe``)
    mở bằng Excel không thành công thức (như LC-T101-1, Lá Chắn T-102 Ghi nhận 3). Giá trị không
    phải chữ giữ nguyên."""
    return safe_text(value) if isinstance(value, str) else value


def unfiltered_html_note(info: ConnectionInfo) -> tuple[str, str] | None:
    """Câu báo về quyền ``unfiltered_html`` của tài khoản (T-106): ``("warning", câu)`` khi biết là
    thiếu, ``("info", câu)`` khi không biết, ``None`` khi có quyền.

    Thiếu quyền thì WordPress lọc bài khi lưu, bỏ ``srcset`` app ghi cho ảnh: điện thoại tải bản
    thu nhỏ đã mất GPS (T-059, T-091). «Không biết» khi website không cho biết quyền viết bài (câu
    trả lời thiếu ``capabilities``, hay tài khoản quá thấp để xét). Có quyền thì không báo gì: REST
    trả quyền theo vai, không thấy ``DISALLOW_UNFILTERED_HTML`` nên đó chỉ là dấu hiệu tốt. Câu cố
    định: không tên đăng nhập, mật khẩu, đường dẫn; không khuyên nâng lên Quản trị viên (Lá Chắn
    T-059).
    """
    has_it = getattr(info, "can_unfiltered_html", None)
    if has_it is True:
        return None
    if has_it is not False or info.can_edit_posts is not True:
        return (
            "info",
            "Chưa biết ảnh trong bài có giữ được vị trí GPS khi xem trên điện thoại không: website "
            "chưa cho biết đủ quyền của tài khoản này. Bấm «Kiểm tra kết nối» lại sau khi tài "
            "khoản có quyền viết bài.",
        )
    lost = (
        "Ảnh trong bài có thể **mất vị trí GPS khi xem trên điện thoại**: tài khoản này không có "
        "quyền giữ nguyên mã HTML của bài (quyền `unfiltered_html`), nên khi lưu bài WordPress bỏ "
        "phần chỉ cho điện thoại dùng ảnh đầy đủ 1600 px, điện thoại tải bản thu nhỏ đã mất GPS."
    )
    if any(isinstance(role, str) and role in _UNFILTERED_ROLES for role in info.roles):
        return (
            "warning",
            f"{lost}\n\nTài khoản đã ở vai trò Biên tập viên trở lên mà website đã bỏ quyền này "
            "khỏi vai trò (thường do plugin quản lý quyền hoặc cấu hình website): báo người làm "
            "web xem lại. Đừng nâng tài khoản lên Quản trị viên chỉ vì việc này.",
        )
    return (
        "warning",
        f"{lost}\n\nCách sửa: nhờ người quản trị website đặt tài khoản này ở vai trò **Biên tập "
        "viên (Editor)**. Không cần, và không nên, nâng lên Quản trị viên.",
    )


settings = load_settings()

st.title("WordPress")

try:
    client = WordPressClient.from_settings(settings)
except WordPressError as exc:
    st.warning(
        f"{plain(exc)}\n\nCách làm: xem mục **Kết nối WordPress** trong "
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
            st.error(plain(exc))

info = st.session_state.get("wp_info")
if info:
    roles = ", ".join(plain(role) for role in info.roles) or "không rõ"
    st.success(
        f"Kết nối thành công tới **{plain(info.site_name)}** "
        f"({plain(info.site_url)})."
    )
    st.markdown(
        f"- Tài khoản: **{plain(info.user_name)}** — vai trò: {roles}\n"
        f"- Viết bài: {'✅' if info.can_edit_posts else '❌'} · "
        f"Đăng bài: {'✅' if info.can_publish_posts else '❌'} · "
        f"Tải ảnh lên: {'✅' if info.can_upload_files else '❌'}\n"
        # T-041 (phần giao diện của T-042): «SiteSEO: ghi được / chưa bật / chưa dò được»
        f"- {plain(info.siteseo_status)}"
    )
    if not (info.can_edit_posts and info.can_upload_files):
        st.warning(
            "Tài khoản thiếu quyền viết bài hoặc tải ảnh. Nên dùng tài khoản có vai trò "
            "Biên tập viên (Editor) hoặc Quản trị viên (Administrator)."
        )
    note = unfiltered_html_note(info)
    if note:
        kind, text = note
        (st.warning if kind == "warning" else st.info)(text)

# ------------------------------------------------------- 2. Chuyên mục và thẻ
st.header("2. Chuyên mục và thẻ")
if st.button("Tải chuyên mục và thẻ"):
    with st.spinner("Đang tải..."):
        try:
            st.session_state["wp_categories"] = client.list_categories()
            st.session_state["wp_tags"] = client.list_tags()
        except WordPressError as exc:
            st.error(plain(exc))

categories = st.session_state.get("wp_categories")
tags = st.session_state.get("wp_tags")
if categories is not None and tags is not None:
    left, right = st.columns(2)
    for column, label, terms in ((left, "Chuyên mục", categories), (right, "Thẻ", tags)):
        with column:
            st.subheader(f"{label} ({len(terms)})")
            if terms:
                st.dataframe(
                    [
                        {"ID": t.id, "Tên": cell(t.name), "Slug": cell(t.slug), "Số bài": t.count}
                        for t in terms
                    ],
                    hide_index=True,
                )
            else:
                st.write("Chưa có.")

# --------------------------------------------------------- 3. Tạo bài nháp thử
st.header("3. Tạo thử một bài nháp")
st.caption(
    "Bài chỉ được lưu **NHÁP** trên WordPress: khách không thấy cho tới khi bạn tự đăng trong "
    "trang quản trị. Kiểm tra xong có thể xóa bài thử trong WordPress. Bài thử chỉ có chữ, không "
    "có ảnh: muốn thử gửi ảnh, dùng «Gửi nháp» ở trang Soạn bài (ảnh đã qua bước làm sạch)."
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
    submitted = st.form_submit_button("Tạo bài nháp")

if submitted:
    try:
        with st.spinner("Đang gửi sang WordPress..."):
            post = client.create_draft(
                title,
                paragraphs_to_html(content),
                categories=[t.id for t in chosen_categories],
                tags=[t.id for t in chosen_tags],
                featured_media=None,  # bài thử không có ảnh (T-108)
            )
    except WordPressError as exc:
        st.error(plain(exc))
    else:
        st.success(f"Đã tạo bài nháp #{post.id}: **{plain(post.title)}**")
        st.link_button("Mở bài trong trang quản trị WordPress", post.edit_link)
