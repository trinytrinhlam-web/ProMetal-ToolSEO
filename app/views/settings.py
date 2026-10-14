"""Cài đặt: văn phong, mô hình AI (có thử mù), ảnh, kết nối."""

import streamlit as st

from seo_app import demo, env_file, ui
from seo_app.config import load_settings

S = st.session_state

# (tên biến trong .env, tên hiện trên giao diện, thuộc tính Settings, nơi lấy khóa)
API_KEY_FIELDS = (
    ("ANTHROPIC_API_KEY", "Claude (Anthropic)", "anthropic_api_key",
     "https://console.anthropic.com"),
    ("OPENAI_API_KEY", "ChatGPT (OpenAI)", "openai_api_key",
     "https://platform.openai.com/api-keys"),
    ("GEMINI_API_KEY", "Gemini (Google)", "gemini_api_key",
     "https://aistudio.google.com/apikey"),
)
CHECKABLE_KEYS = {"ANTHROPIC_API_KEY"}


def _input_key(name: str) -> str:
    return f"api-key-input-{name}"


def _flash(name: str, kind: str, text: str) -> None:
    """Thông báo hiện một lần dưới thẻ khóa. ``text`` không bao giờ chứa khóa."""
    S[f"api-key-flash-{name}"] = (kind, text)


def _save_key(name: str, label: str) -> None:
    # Chạy trong on_click, trước khi trang vẽ lại: ghi .env, rồi xóa khóa khỏi ô nhập và
    # session_state dù lưu được hay không. Trang đọc lại .env ngay sau đó nên trạng thái đổi.
    value = S.get(_input_key(name), "")
    S[_input_key(name)] = ""
    S.pop(f"api-key-check-{name}", None)
    try:
        env_file.set_api_key(name, value)
    except env_file.EnvFileError as exc:
        _flash(name, "error", str(exc))
    else:
        _flash(name, "success", f"Đã lưu khóa {label} vào file .env.")


def _ask_clear(name: str) -> None:
    S[f"api-key-ask-clear-{name}"] = True


def _cancel_clear(name: str) -> None:
    S.pop(f"api-key-ask-clear-{name}", None)


def _clear_key(name: str, label: str) -> None:
    S.pop(f"api-key-ask-clear-{name}", None)
    S.pop(f"api-key-check-{name}", None)
    S[_input_key(name)] = ""
    try:
        env_file.clear_api_key(name)
    except env_file.EnvFileError as exc:
        _flash(name, "error", str(exc))
    else:
        _flash(name, "success", f"Đã xóa khóa {label} khỏi file .env.")


def api_key_card(name: str, label: str, configured: bool, url: str) -> None:
    """Một thẻ khóa: trạng thái, link lấy khóa, ô nhập, Lưu / Kiểm tra / Xóa.

    Không bao giờ hiện giá trị khóa: ô nhập luôn bắt đầu trống, thông báo chỉ là câu cố định
    hoặc lỗi của ``env_file`` (đã không chứa khóa).
    """
    st.markdown(f"**{label}**")
    if configured:
        st.markdown(":green-badge[✅ Đã khai báo]")
    else:
        st.markdown(":gray-badge[⚪ Chưa khai báo]")
    st.caption(f"Lấy khóa ở: [{url.removeprefix('https://')}]({url})")
    if env_file.overridden_by_os_environ(name):
        st.warning(
            f"Khóa {label} đang được đặt trong biến môi trường của máy (được ưu tiên hơn file "
            ".env), nên khóa nhập ở đây sẽ không có hiệu lực. Muốn dùng khóa mới, hãy gỡ biến "
            f"{name} khỏi máy."
        )

    st.text_input(
        f"Khóa {label}",
        key=_input_key(name),
        type="password",
        placeholder="Dán khóa mới để thay khóa cũ" if configured else "Dán khóa vào đây",
        label_visibility="collapsed",
        autocomplete="off",
    )
    save, check, clear = st.columns(3)
    save.button(
        "Lưu",
        key=f"api-key-save-{name}",
        type="primary",
        width="stretch",
        on_click=_save_key,
        args=(name, label),
    )
    checkable = name in CHECKABLE_KEYS
    if check.button(
        "Kiểm tra",
        key=f"api-key-check-btn-{name}",
        width="stretch",
        disabled=not (checkable and configured),
        help=None if checkable else "Chưa kiểm tra được khóa này (chờ cài thư viện của hãng).",
    ):
        S.pop(f"api-key-flash-{name}", None)
        with st.spinner(f"Đang hỏi thử máy chủ {label}..."):
            # Không truyền khóa: hàm tự đọc khóa đang có hiệu lực, giao diện không giữ khóa.
            result = env_file.check_api_key(name)
        S[f"api-key-check-{name}"] = (result.status, result.message)
    clear.button(
        "Xóa",
        key=f"api-key-clear-{name}",
        width="stretch",
        disabled=not configured,
        on_click=_ask_clear,
        args=(name,),
    )

    if S.get(f"api-key-ask-clear-{name}"):
        st.warning(f"Xóa khóa {label} khỏi file .env? Các bước dùng {label} sẽ bị khóa lại.")
        yes, no = st.columns(2)
        yes.button(
            "Xóa thật",
            key=f"api-key-clear-yes-{name}",
            type="primary",
            width="stretch",
            on_click=_clear_key,
            args=(name, label),
        )
        no.button(
            "Thôi",
            key=f"api-key-clear-no-{name}",
            width="stretch",
            on_click=_cancel_clear,
            args=(name,),
        )

    flash = S.pop(f"api-key-flash-{name}", None)
    if flash:
        kind, text = flash
        (st.success if kind == "success" else st.error)(text)
    checked = S.get(f"api-key-check-{name}")
    if checked:
        status, message = checked
        show = {"ok": st.success, "invalid": st.error}.get(status, st.warning)
        show(message)


# Đọc cấu hình sau các callback ở trên, nên trạng thái "đã khai báo" đổi ngay khi vừa lưu.
settings = load_settings()

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
    st.caption(
        "Phần này là thật: đọc và ghi file .env trên máy bạn. Khóa đã lưu không bao giờ hiện "
        "lại, kể cả vài ký tự cuối; ở đây chỉ báo đã khai báo hay chưa."
    )
    st.markdown("#### 🔑 Khóa API cho AI")
    key_columns = st.columns(len(API_KEY_FIELDS), gap="medium")
    for column, (env_name, label, configured_attr, url) in zip(
        key_columns, API_KEY_FIELDS, strict=True
    ):
        with column, st.container(border=True, height="stretch"):
            api_key_card(env_name, label, bool(getattr(settings, configured_attr)), url)
    st.caption(
        "Khóa nằm trong file .env của máy này (không đồng bộ sang máy kia). Máy kia cần nhập "
        "lại một lần."
    )

    st.markdown("#### Các kết nối khác")
    ai_labels = {"Anthropic (Claude)", "OpenAI", "Google Gemini"}
    for label, configured in settings.status().items():
        if label in ai_labels:
            continue
        st.markdown(
            f"{'✅' if configured else '⚪'} **{label}** — "
            f"{'đã khai báo' if configured else 'chưa khai báo'}"
        )
    st.page_link("views/wordpress.py", label="Mở trang kết nối WordPress", icon="🔌")
