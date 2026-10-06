"""Thử mù mô hình AI (DEMO): cùng một đề, nhiều mô hình, ẩn tên cho tới khi chấm xong."""

import streamlit as st

from seo_app import demo

st.title("Thử mù mô hình AI")
demo.banner(2, "Thử mù mô hình")
st.caption(
    "Cùng một đề gửi cho nhiều mô hình. Bạn chấm điểm khi chưa biết bài nào của ai, "
    "để chọn mô hình viết hay nhất cho từng việc mà không bị thương hiệu ảnh hưởng."
)

st.text_area("Đề bài", demo.BLIND_PROMPT, height=70)
demo.button("Gửi cho các mô hình", 2)

scores = {}
cols = st.columns(len(demo.BLIND_OUTPUTS))
for col, (label, text) in zip(cols, demo.BLIND_OUTPUTS.items(), strict=True):
    with col, st.container(border=True):
        st.markdown(f"**Bài {label}**")
        st.write(text)
        scores[label] = st.slider("Điểm", 1, 10, 5, key=f"score_{label}")

if st.button("Chấm xong — hiện tên mô hình", type="primary"):
    st.session_state["blind_revealed"] = True

if st.session_state.get("blind_revealed"):
    ranking = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    st.dataframe(
        [
            {"Bài": label, "Điểm": score, "Mô hình": demo.BLIND_MODELS[label]}
            for label, score in ranking
        ],
        hide_index=True,
    )
    st.caption("Kết quả các lần thử được lưu lại để so sánh dần theo thời gian.")
