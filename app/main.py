"""Giao diện Streamlit của SEO App.

Chạy: uv run streamlit run app/main.py  (hoặc bấm đúp run.bat / run.command)

File này lo đăng nhập. Chỉ khi đăng nhập xong mới hiện menu và các trang trong app/views/.
"""

from __future__ import annotations

import time

import streamlit as st

from seo_app.auth import is_valid_hash, verify_password
from seo_app.config import ConfigError, Settings, load_settings

# Chờ một chút sau mỗi lần nhập sai để việc đoán mật khẩu chậm lại.
WRONG_PASSWORD_DELAY_SECONDS = 1.0

PAGES = [
    ("views/home.py", "Trang chủ", "🏠"),
    ("views/wordpress.py", "WordPress", "📝"),
]


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


def main() -> None:
    st.set_page_config(page_title="SEO App", page_icon="🔎", layout="wide")

    try:
        settings = load_settings()
    except ConfigError as exc:
        st.error(str(exc))
        return

    if not st.session_state.get("authenticated"):
        login_page(settings)
        return

    navigation = st.navigation(
        [st.Page(path, title=title, icon=icon) for path, title, icon in PAGES]
    )
    with st.sidebar:
        if st.button("Đăng xuất"):
            st.session_state.clear()
            st.rerun()
    navigation.run()


main()
