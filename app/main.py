"""Giao diện Streamlit của SEO App.

Chạy: uv run streamlit run app/main.py  (hoặc bấm đúp run.bat / run.command)
"""

from __future__ import annotations

import time

import streamlit as st

from seo_app.auth import is_valid_hash, verify_password
from seo_app.config import ConfigError, Settings, load_settings

# Chờ một chút sau mỗi lần nhập sai để việc đoán mật khẩu chậm lại.
WRONG_PASSWORD_DELAY_SECONDS = 1.0


def login_page(settings: Settings) -> None:
    st.title("Đăng nhập SEO App")

    if not is_valid_hash(settings.password_hash):
        st.warning(
            "Chưa đặt mật khẩu đăng nhập (hoặc APP_PASSWORD_HASH trong file .env bị sai).\n\n"
            "Cách đặt mật khẩu: tắt app, bấm đúp **set_password.bat** (Windows) hoặc "
            "**set_password.command** (Mac), nhập mật khẩu, rồi mở lại app."
        )
        return

    with st.form("login"):
        password = st.text_input("Mật khẩu", type="password")
        submitted = st.form_submit_button("Đăng nhập")

    if submitted:
        if verify_password(password, settings.password_hash):
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            time.sleep(WRONG_PASSWORD_DELAY_SECONDS)
            st.error("Mật khẩu không đúng.")


def home_page(settings: Settings) -> None:
    with st.sidebar:
        if st.button("Đăng xuất"):
            st.session_state["authenticated"] = False
            st.rerun()

    st.title("SEO App")
    now = settings.now()
    st.caption(f"Giờ hiện tại: {now:%H:%M %d/%m/%Y} ({settings.timezone_name})")

    st.subheader("Tình trạng cấu hình")
    st.write("Các mục chưa khai báo sẽ được dùng ở những giai đoạn sau, chưa cần điền ngay.")
    for label, configured in settings.status().items():
        icon = "✅" if configured else "⚪"
        note = "đã khai báo" if configured else "chưa khai báo"
        st.markdown(f"{icon} **{label}**: {note}")

    st.info("Các chức năng (WordPress, viết bài bằng AI, ảnh, …) sẽ lần lượt được thêm vào đây.")


def main() -> None:
    st.set_page_config(page_title="SEO App", page_icon="🔎", layout="wide")

    try:
        settings = load_settings()
    except ConfigError as exc:
        st.error(str(exc))
        return

    if st.session_state.get("authenticated"):
        home_page(settings)
    else:
        login_page(settings)


main()
