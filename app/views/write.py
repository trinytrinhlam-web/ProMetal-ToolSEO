"""Viết bài (DEMO): 7 bước theo quy trình nội dung trong CLAUDE.md."""

import streamlit as st

from seo_app import demo

st.title("Viết bài")
demo.banner(2, "Quy trình viết bài bằng AI (phần SEO on-page ở Giai đoạn 4)")

st.markdown(f"Từ khóa đang viết: **{demo.DEMO_KEYWORD}**")

steps = st.tabs(
    [
        "1. Ý định tìm kiếm",
        "2. Nghiên cứu đối thủ",
        "3. Chất liệu thật",
        "4. Dàn ý",
        "5. Bài viết & rà soát",
        "6. SEO on-page",
        "7. Gửi WordPress",
    ]
)

with steps[0]:
    st.caption("AI xác định người tìm từ khóa này thật sự muốn gì, trước khi viết chữ nào.")
    for label, value in demo.INTENT.items():
        st.markdown(f"**{label}:** {value}")
    demo.button("Phân tích lại", 2, key="intent")

with steps[1]:
    st.caption("AI đọc các bài đang đứng đầu Google: họ đã nói gì, còn thiếu gì.")
    st.dataframe(demo.COMPETITORS, hide_index=True)
    st.markdown("**Bài của mình phải có thêm:**")
    for angle in demo.NEW_ANGLES:
        st.markdown(f"- {angle}")

with steps[2]:
    st.caption(
        "Phần chỉ bạn có: kinh nghiệm, số liệu, câu hỏi thật của khách, ảnh thật. "
        "AI không được bịa phần này — chỗ nào thiếu sẽ để trống cho bạn điền."
    )
    for label, value in demo.REAL_MATERIAL.items():
        st.text_area(label, value, height=90)
    st.multiselect(
        "Ảnh thật dùng trong bài",
        [img["Tên mới"] for img in demo.IMAGES],
        default=[demo.IMAGES[0]["Tên mới"], demo.IMAGES[1]["Tên mới"]],
    )

with steps[3]:
    st.caption("Duyệt dàn ý trước — AI chỉ viết toàn bài sau khi bạn bấm Duyệt.")
    st.text_area("Dàn ý (sửa trực tiếp được)", demo.OUTLINE, height=360)
    left, right = st.columns(2)
    with left:
        demo.button("✅ Duyệt dàn ý, viết toàn bài", 2, key="approve", primary=True)
    with right:
        demo.button("🔁 Tạo dàn ý khác", 2, key="new_outline")

with steps[4]:
    article, review = st.columns([3, 2])
    with article:
        st.markdown("**Bản viết (AI đã tự rà soát và sửa một lượt)**")
        with st.container(border=True):
            st.markdown(demo.DRAFT_ARTICLE)
    with review:
        st.markdown("**Rà soát theo checklist chất lượng**")
        for item, ok, note in demo.CHECKLIST:
            line = f"{'✅' if ok else '⚠️'} {item}"
            if note:
                line += f"  \n  <small>{note}</small>"
            st.markdown(line, unsafe_allow_html=True)
        demo.button("Rà soát lại", 2, key="review")

with steps[5]:
    st.caption("Phần này sẽ được làm thật ở Giai đoạn 4.")
    title = st.text_input("Meta title", demo.META["title"])
    st.caption(f"{len(title)}/60 ký tự")
    description = st.text_area("Meta description", demo.META["description"], height=80)
    st.caption(f"{len(description)}/155 ký tự")
    st.text_input("Đường dẫn (slug)", demo.META["slug"])
    st.markdown("**Gợi ý liên kết nội bộ** (từ các bài đã có trên website)")
    st.dataframe(demo.INTERNAL_LINKS, hide_index=True)
    with st.expander("Schema JSON-LD"):
        st.code(demo.SCHEMA_PREVIEW, language="json")

with steps[6]:
    mode = st.radio(
        "Gửi sang WordPress dưới dạng",
        ["Nháp (mặc định)", "Hẹn giờ đăng", "Đăng ngay"],
        horizontal=True,
    )
    if mode == "Hẹn giờ đăng":
        left, right = st.columns(2)
        left.date_input("Ngày đăng", format="DD/MM/YYYY")
        right.time_input("Giờ đăng")
        st.caption("WordPress tự đăng đúng giờ — không cần mở app lúc đó.")
    confirmed = True
    if mode == "Đăng ngay":
        st.warning("Bài sẽ hiện công khai ngay trên website.")
        confirmed = st.checkbox("Tôi đã đọc lại bài và đồng ý đăng ngay")
    st.multiselect("Chuyên mục", ["Inox", "Cổng inox", "Bảo dưỡng"], default=["Inox"])
    if confirmed:
        demo.button("📤 Gửi sang WordPress", 2, key="send", primary=True)
