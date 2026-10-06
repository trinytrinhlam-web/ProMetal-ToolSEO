"""Giao diện Streamlit của SEO App.

Chạy: uv run streamlit run app/main.py  (hoặc bấm đúp run.bat / run.command)

File này lo đăng nhập, menu và giao diện chung. Nội dung từng trang nằm trong app/views/.
"""

from __future__ import annotations

import time
from pathlib import Path

import streamlit as st

from seo_app.auth import is_valid_hash, verify_password
from seo_app.config import ConfigError, Settings, load_settings

APP_DIR = Path(__file__).parent
ASSETS = APP_DIR / "assets"

# Chờ một chút sau mỗi lần nhập sai để việc đoán mật khẩu chậm lại.
WRONG_PASSWORD_DELAY_SECONDS = 1.0

# Menu trên cùng: (file trong app/views/, tên trang, biểu tượng). Trang đầu là trang mặc định.
PAGES = [
    ("views/home.py", "Bài viết", "📚"),
    ("views/write.py", "Soạn bài", "✍️"),
    ("views/plan.py", "Kế hoạch", "🗂️"),
    ("views/settings.py", "Cài đặt", "⚙️"),
    ("views/wordpress.py", "Kết nối WordPress", "🔌"),
]


def login_page(settings: Settings) -> None:
    _, center, _ = st.columns([1, 1.3, 1])
    with center:
        st.write("")
        st.image(str(ASSETS / "logo.svg"), width=220)
        st.title("Đăng nhập")

        if not is_valid_hash(settings.password_hash):
            st.warning(
                "Chưa đặt mật khẩu đăng nhập (hoặc APP_PASSWORD_HASH trong file .env bị sai).\n\n"
                "Cách đặt mật khẩu: tắt app, bấm đúp **set_password.bat** (Windows) hoặc "
                "**set_password.command** (Mac), nhập mật khẩu, rồi mở lại app."
            )
            return

        with st.form("login"):
            password = st.text_input("Mật khẩu", type="password")
            submitted = st.form_submit_button("Đăng nhập", type="primary", width="stretch")

        if submitted:
            if verify_password(password, settings.password_hash):
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                time.sleep(WRONG_PASSWORD_DELAY_SECONDS)
                st.error("Mật khẩu không đúng.")


def main() -> None:
    st.set_page_config(page_title="SEO App", page_icon="✍️", layout="wide")
    st.html(ASSETS / "style.css")

    try:
        settings = load_settings()
    except ConfigError as exc:
        st.error(str(exc))
        return

    if not st.session_state.get("authenticated"):
        login_page(settings)
        return

    st.logo(str(ASSETS / "logo.svg"), size="large")
    navigation = st.navigation(
        [st.Page(path, title=title, icon=icon) for path, title, icon in PAGES],
        position="top",
    )
    navigation.run()


main()
