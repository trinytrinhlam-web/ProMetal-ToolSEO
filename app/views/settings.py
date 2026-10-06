"""Cài đặt: văn phong, mô hình AI (có thử mù), ảnh, kết nối."""

import streamlit as st

from seo_app import demo, ui
from seo_app.config import load_settings

settings = load_settings()
S = st.session_state

head, logout = st.columns([5, 1], vertical_alignment="center")
with head:
    ui.page_header("Cài đặt", "Những thiết lập dùng chung cho mọi bài viết.", demo=True)
if logout.button("Đăng xuất", width="stretch"):
    S.clear()
    st.rerun()

tone, models, images, connections = st.tabs(["✍️ Văn phong", "🤖 Mô hình AI", "🖼️ Ảnh", "🔌 Kết nối"])

with tone:
    left, right = st.columns(2, gap="large")
    with left:
        st.text_input("Cách xưng hô", demo.TONE_SETTINGS["xung_ho"])
        st.select_slider(
            "Mức trang trọng",
            ["Rất thân mật", "Thân thiện", "Vừa phải", "Trang trọng"],
            value="Thân thiện",
        )
        st.select_slider("Độ dài câu", ["Ngắn, gọn", "Vừa", "Dài, chi tiết"], value="Ngắn, gọn")
    with right:
        st.text_area(
            "Câu, cụm từ cấm dùng (mỗi dòng một cụm)",
            "\n".join(demo.TONE_SETTINGS["banned"]),
            height=160,
        )
        st.caption("AI kiểm tra văn phong sẽ đánh dấu mọi chỗ dùng những cụm này.")
    st.text_area(
        "Đoạn văn mẫu đúng giọng của bạn (không bắt buộc)",
        placeholder="Dán một đoạn bạn thấy «đúng giọng» — AI sẽ bắt chước cách viết này.",
        height=100,
    )

with models:
    st.caption(
        "Mỗi việc dùng một mô hình riêng, lưu trong config/ai_models.toml — đổi được mà "
        "không sửa code, tự đồng bộ giữa 2 máy."
    )
    st.dataframe(demo.AI_TASKS, hide_index=True)

    st.markdown("#### 🎭 Thử mù: mô hình nào viết hay hơn?")
    st.caption("Cùng một đề, ẩn tên mô hình. Chấm điểm xong mới biết bài nào của ai.")
    cols = st.columns(len(demo.BLIND_OUTPUTS))
    scores = {}
    for col, (label, text) in zip(cols, demo.BLIND_OUTPUTS.items(), strict=True):
        with col, st.container(border=True, height="stretch"):
            st.markdown(f"**Bài {label}**")
            st.write(text)
            scores[label] = st.slider("Điểm", 1, 10, 5, key=f"score-{label}")
    if st.button("Chấm xong — hiện tên mô hình", type="primary"):
        S.blind_revealed = True
    if S.get("blind_revealed"):
        ranking = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        st.dataframe(
            [{"Bài": k, "Điểm": v, "Mô hình": demo.BLIND_MODELS[k]} for k, v in ranking],
            hide_index=True,
        )

with images:
    st.markdown("**Thư mục ảnh thật**")
    if settings.image_folders:
        for folder in settings.image_folders:
            found = "✅ tìm thấy" if folder.is_dir() else "⚠️ không thấy trên máy này"
            st.markdown(f"- `{folder}` — {found}")
    else:
        st.caption("Chưa khai báo. Điền IMAGE_FOLDERS trong file .env.")
    st.text_input(
        "Phong cách chung cho ảnh AI (thêm vào mọi prompt)",
        "realistic photo, natural daylight, Vietnamese townhouse context, no text, no logo",
    )
    st.select_slider("Chất lượng nén WebP", [60, 70, 75, 80, 85, 90], value=80)

with connections:
    st.caption("Phần này là thật: đọc từ file .env trên máy bạn (không hiện giá trị).")
    for label, configured in settings.status().items():
        st.markdown(
            f"{'✅' if configured else '⚪'} **{label}** — "
            f"{'đã khai báo' if configured else 'chưa khai báo'}"
        )
    st.page_link("views/wordpress.py", label="Mở trang kết nối WordPress", icon="🔌")
