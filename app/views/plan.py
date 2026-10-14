"""Kế hoạch (DEMO): bạn đưa kế hoạch vào, AI đọc và đề xuất cập nhật danh sách bài."""

import streamlit as st

from seo_app import demo, ui
from seo_app.config import load_settings

settings = load_settings()
S = st.session_state

ui.page_header(
    "Kế hoạch",
    "Đưa kế hoạch của bạn vào — phần mềm đọc, đề xuất thay đổi, bạn duyệt rồi mới cập nhật.",
    demo=True,
)


def read_plan() -> None:
    S.plan_changes = [dict(row) for row in demo.PLAN_CHANGES]


def apply_changes() -> None:
    chosen = [row for row in S.plan_editor_rows if row["Áp dụng"]]
    S.pop("plan_changes", None)
    st.toast(f"Bản demo: đã áp dụng {len(chosen)} thay đổi vào kế hoạch", icon="🧪")


source, brief = st.columns([3, 2], gap="large")

with source, st.container(border=True):
    st.markdown("#### 📥 Cung cấp kế hoạch")
    upload, paste, sheet = st.tabs(["Tải file", "Dán nội dung", "Google Sheets"])
    with upload:
        st.file_uploader(
            "File kế hoạch (Excel, CSV, Word, PDF, TXT)",
            type=["xlsx", "csv", "docx", "pdf", "txt", "md"],
        )
        st.caption("Bảng hay văn bản tự do đều được — AI tự tìm từ khóa, ngày, ưu tiên.")
    with paste:
        st.text_area("Dán kế hoạch hoặc ghi chú định hướng", demo.PLAN_PASTE_EXAMPLE, height=150)
    with sheet:
        st.text_input("Link Google Sheets", placeholder="https://docs.google.com/spreadsheets/d/…")
        st.caption("Phần mềm đọc và ghi lại vào chính Sheet này, nên 2 máy luôn thấy giống nhau.")
    st.button("🧠 Đọc kế hoạch và đề xuất cập nhật", type="primary", on_click=read_plan)

with brief, st.container(border=True):
    st.markdown("#### 🏢 Thông tin nền cho mọi bài")
    st.caption("AI dùng phần này khi viết bất kỳ bài nào, để bài đúng doanh nghiệp, đúng khách.")
    for label, value in demo.BUSINESS_BRIEF.items():
        st.text_input(label, value, key=f"brief-{label}")

if "plan_changes" in S:
    with st.container(border=True):
        st.markdown("#### Đề xuất thay đổi")
        st.caption("Bỏ tick những dòng bạn không muốn áp dụng.")
        S.plan_editor_rows = st.data_editor(
            S.plan_changes,
            hide_index=True,
            disabled=["Loại", "Từ khóa", "Chi tiết"],
            column_config={"Áp dụng": st.column_config.CheckboxColumn(width="small")},
        )
        a, b, _ = st.columns([1.4, 1, 3])
        a.button("✅ Áp dụng thay đổi", type="primary", on_click=apply_changes, width="stretch")
        b.button("Hủy", on_click=lambda: S.pop("plan_changes", None), width="stretch")

st.subheader("Danh sách bài theo kế hoạch")
rows = demo.plan_rows(settings.now().date())
st.dataframe(
    rows,
    hide_index=True,
    column_config={
        "Ngày dự kiến": st.column_config.DateColumn(format="DD/MM/YYYY"),
        "Trạng thái": st.column_config.TextColumn(width="small"),
    },
)
