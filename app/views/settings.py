"""Cài đặt: văn phong, mô hình AI (có thử mù), ảnh, kết nối, Google Sheets."""

import os
import unicodedata
from pathlib import Path

import streamlit as st

from seo_app import demo, env_file, ui
from seo_app.ai import AIError
from seo_app.ai.base import EFFORTS, redact_secrets
from seo_app.ai.registry import PROVIDERS
from seo_app.config import ConfigError, load_settings
from seo_app.content import blind_test, load_rules
from seo_app.google.service_account import ServiceAccountError, load_service_account
from seo_app.google.sheets import SheetsClient, SheetsError, mask_sheet_id, sheet_id_from_link
from seo_app.images.folders import ImageLibrary
from seo_app.plan import sync as plan_sync
from seo_app.sanitize import escape_link_syntax
from seo_app.text import escape_markdown

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
    if check.button(
        "Kiểm tra",
        key=f"api-key-check-btn-{name}",
        width="stretch",
        disabled=not configured,
        help=f"Hỏi thử máy chủ {label} xem khóa có dùng được không (không tốn tiền)."
        if configured
        else "Lưu khóa trước rồi mới kiểm tra được.",
    ):
        S.pop(f"api-key-flash-{name}", None)
        with st.spinner(f"Đang hỏi thử máy chủ {label}..."):
            try:
                # Không truyền khóa: hàm tự đọc khóa đang có hiệu lực, giao diện không giữ khóa.
                result = env_file.check_api_key(name)
            except Exception as exc:  # nút Kiểm tra không được làm sập trang
                # Chỉ nêu tên loại lỗi: thông điệp gốc có thể chứa khóa.
                checked = (
                    "unknown",
                    f"Không kiểm tra được khóa ({type(exc).__name__}). Thử lại sau.",
                )
            else:
                # Che thêm một lần (phòng thủ lớp hai), dù check_api_key đã tự che.
                checked = (result.status, redact_secrets(result.message))
        S[f"api-key-check-{name}"] = checked
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


# ------------------------------------------------------------------ tab Mô hình AI + thử mù
# Thử mù (T-019): tên hãng / mô hình của từng bài A/B/C nằm trong ``S.blind_reveal`` và chỉ
# hiện sau khi bấm "Chấm xong". Không đưa chúng vào nhãn, ``help=``, ``key=`` hay chữ nào
# khác trên trang trước lúc đó. Chữ AI hiện bằng ``st.markdown`` thường (không HTML).

PROVIDER_LABELS = {pid: label for pid, (label, _env) in PROVIDERS.items()}


def _cand_key(i: int, field: str) -> str:
    return f"blind-cand-{i}-{field}"


def _suggest(provider: str, suggestions: dict[str, list[str]], i: int) -> str:
    names = suggestions.get(provider) or []
    return names[i % len(names)] if names else ""


def _on_provider_change(i: int, suggestions: dict[str, list[str]]) -> None:
    # Đổi hãng thì đổi luôn tên mô hình sang gợi ý của hãng mới (tên cũ chắc chắn sai hãng).
    S[_cand_key(i, "model")] = _suggest(S.get(_cand_key(i, "provider"), ""), suggestions, i)


def _reset_blind() -> None:
    for name in ("blind_entries", "blind_reveal", "blind_revealed", "blind_scores"):
        S.pop(name, None)


def _model_table() -> dict[str, list[str]]:
    """Bảng việc–mô hình đọc từ config/ai.toml. Trả về tên mô hình gợi ý theo hãng."""
    try:
        rows = blind_test.task_models()
    except AIError as exc:
        st.error(str(exc))
        return {pid: [] for pid in PROVIDERS}
    st.dataframe(
        [
            {
                "Việc": r.task_label,
                "Hãng": r.provider_label,
                "Mô hình": r.model,
                "Mức nghĩ (effort)": r.effort,
            }
            for r in rows
        ],
        hide_index=True,
    )
    return blind_test.model_suggestions(rows)


def _candidate_inputs(
    count: int, available: list[str], suggestions: dict[str, list[str]]
) -> list[blind_test.Candidate]:
    cands: list[blind_test.Candidate] = []
    for i, col in enumerate(st.columns(count, gap="medium")):
        pkey, mkey, ekey = _cand_key(i, "provider"), _cand_key(i, "model"), _cand_key(i, "effort")
        # Khóa vừa bị xóa ở tab Kết nối: hãng cũ không còn trong danh sách thì chọn lại từ đầu.
        if S.get(pkey) not in available:
            S[pkey] = available[i % len(available)]
            S[mkey] = _suggest(S[pkey], suggestions, i)
        S.setdefault(mkey, _suggest(S[pkey], suggestions, i))
        S.setdefault(ekey, "medium")
        with col, st.container(border=True):
            st.markdown(f"**Ứng viên {i + 1}**")
            provider = st.selectbox(
                "Hãng",
                available,
                key=pkey,
                format_func=PROVIDER_LABELS.get,
                on_change=_on_provider_change,
                args=(i, suggestions),
            )
            model = st.text_input(
                "Tên mô hình",
                key=mkey,
                max_chars=blind_test.MAX_MODEL_CHARS,
                placeholder="Gõ đúng tên mô hình của hãng",
            )
            hints = suggestions.get(provider) or []
            if hints:
                st.caption("Đang dùng trong config/ai.toml: " + ", ".join(f"`{m}`" for m in hints))
            else:
                st.caption(
                    "config/ai.toml chưa dùng mô hình nào của hãng này: gõ tên mô hình theo "
                    "tài liệu của hãng."
                )
            effort = st.selectbox("Mức nghĩ (effort)", EFFORTS, key=ekey)
        cands.append(blind_test.Candidate(provider=provider, model=model, effort=effort))
    return cands


def _show_entries() -> None:
    entries = S.blind_entries
    for col, entry in zip(st.columns(len(entries), gap="medium"), entries, strict=True):
        with col, st.container(border=True, height="stretch"):
            st.markdown(f"**Bài {entry.label}**")
            if not entry.ok:
                st.warning(entry.error)
                continue
            # Chữ AI đã qua clean_ai_text: hiện bằng Markdown thường, không HTML.
            st.markdown(entry.intro)
            if entry.heading:
                st.markdown(f"##### {entry.heading}")
            st.markdown(entry.body)
            if S.get("blind_revealed"):
                st.markdown(f"Điểm: **{S.blind_scores[entry.label]}**/10")
            else:
                st.slider("Điểm", 1, 10, 5, key=f"blind-score-{entry.label}")


def _show_reveal() -> None:
    reveal = S.blind_reveal
    rows = []
    for entry in S.blind_entries:
        info = reveal[entry.label]
        rows.append(
            {
                "Bài": entry.label,
                "Điểm": S.blind_scores.get(entry.label),  # trống nếu bài lỗi
                "Tình trạng": "có bài" if entry.ok else "lỗi (xem dưới)",
                "Hãng": info.provider_label,
                "Mô hình": info.model,
                "Mức nghĩ (effort)": info.effort,
            }
        )
    rows.sort(key=lambda r: r["Điểm"] or 0, reverse=True)
    st.dataframe(rows, hide_index=True)
    for label, info in reveal.items():
        if info.error:
            # Tên mô hình do người dùng gõ (có thể là "https://…", "www.…", email): không để thành
            # link trong câu lỗi (Lá Chắn LC-T034-1, T-044).
            st.error(
                escape_link_syntax(
                    f"Bài {label} ({info.provider_label} · {info.model}): {info.error}"
                )
            )

    best = next((r for r in rows if r["Điểm"] is not None), None)
    if best is None:
        return
    info = reveal[best["Bài"]]
    st.markdown("#### Muốn dùng mô hình này cho một việc?")
    st.markdown(
        "1. Mở file `config/ai.toml` trong thư mục phần mềm (bằng Notepad hoặc TextEdit).\n"
        "2. Tìm mục của việc cần đổi, ví dụ `[tasks.write]` là viết bài, `[tasks.review]` là "
        "kiểm tra văn phong.\n"
        "3. Sửa hai dòng `provider` và `model` như dưới đây, lưu file, rồi tải lại trang (F5).\n"
        "4. Máy kia nhận thay đổi khi đồng bộ code qua GitHub."
    )
    st.code(
        f'provider = "{info.provider}"\nmodel = "{info.model}"\neffort = "{info.effort}"',
        language="toml",
    )
    st.caption("Mô hình của hãng nào thì phải có khóa của hãng đó trong tab 🔌 Kết nối.")


def blind_models_tab(settings) -> None:
    st.caption(
        "Mỗi việc dùng một mô hình riêng, lưu trong config/ai.toml — đổi được mà không sửa "
        "code, tự đồng bộ giữa 2 máy. Bảng dưới đây đọc thật từ file đó."
    )
    suggestions = _model_table()

    st.markdown("#### 🎭 Thử mù: mô hình nào viết hay hơn?")
    st.caption(
        "Phần này là thật: cùng một đề gửi cho 2–3 mô hình, mỗi mô hình viết một mở bài và một "
        "mục ngắn. Bài hiện dưới tên A/B/C theo thứ tự ngẫu nhiên; chấm điểm xong mới biết bài "
        "nào của ai."
    )
    statuses = blind_test.provider_status(settings)
    st.markdown(
        " ".join(
            f":green-badge[✅ {p.label}]"
            if p.has_key
            else f":gray-badge[⚪ {p.label}: chưa có khóa]"
            for p in statuses
        )
    )
    available = [p.provider for p in statuses if p.has_key]
    if not available:
        st.info("Chưa có khóa AI nào. Vào tab 🔌 Kết nối nhập ít nhất một khóa để thử mù.")
        return

    keyword = st.text_input(
        "Từ khóa thử",
        key="blind-keyword",
        max_chars=blind_test.MAX_KEYWORD_CHARS,
        placeholder="Ví dụ: cửa sắt mỹ thuật",
    )
    note = st.text_area(
        "Ghi chú cho đề (không bắt buộc)",
        key="blind-note",
        max_chars=blind_test.MAX_NOTE_CHARS,
        height=80,
        placeholder="Ví dụ: nhấn vào độ bền khi ở gần biển",
    )
    count = (
        st.segmented_control(
            "Số mô hình so sánh",
            [2, 3],
            default=2,
            key="blind-count",
            format_func=lambda n: f"{n} mô hình",
        )
        or 2
    )
    if len(available) == 1:
        st.caption(
            "Mới có khóa của một hãng: vẫn thử được giữa các mô hình cùng hãng (gõ tên khác nhau)."
        )
    cands = _candidate_inputs(count, available, suggestions)

    try:
        blind_test.validate_request(keyword, note, cands)
    except AIError as exc:
        problem = str(exc)
    else:
        problem = ""
    calls = blind_test.estimate_calls(cands)
    st.warning(
        f"Bấm chạy sẽ gọi AI {calls} lần (mỗi mô hình một lần) và **có tốn tiền** theo bảng giá "
        "của từng hãng. Mỗi bài ngắn, không tìm web."
    )
    if problem:
        st.caption(f"Chưa chạy được: {escape_link_syntax(problem)}")
    if st.button(
        f"▶️ Chạy thử mù (gọi AI {calls} lần)",
        key="blind-run",
        type="primary",
        disabled=bool(problem),
    ):
        _reset_blind()
        with st.spinner(f"Đang gửi đề cho {calls} mô hình..."):
            try:
                entries, reveal = blind_test.run_blind_test(
                    keyword, note, cands, settings, load_rules()
                )
            except AIError as exc:
                st.error(escape_link_syntax(str(exc)))
            else:
                for entry in entries:
                    S.pop(f"blind-score-{entry.label}", None)
                S.blind_entries, S.blind_reveal = entries, reveal
                S.blind_revealed = False

    if not S.get("blind_entries"):
        return
    st.markdown("#### Chấm điểm")
    _show_entries()
    reveal_col, again_col = st.columns([3, 1])
    if reveal_col.button(
        "Chấm xong — hiện tên mô hình",
        key="blind-reveal",
        type="primary",
        disabled=bool(S.get("blind_revealed")),
    ):
        # Chốt điểm lúc bấm: sau đó thanh điểm được thay bằng chữ, không chấm lại được.
        S.blind_scores = {
            e.label: S.get(f"blind-score-{e.label}", 5) for e in S.blind_entries if e.ok
        }
        S.blind_revealed = True
        st.rerun()
    again_col.button("🔄 Xóa kết quả", key="blind-clear", on_click=_reset_blind, width="stretch")
    if S.get("blind_revealed"):
        _show_reveal()


# ------------------------------------------------------------------ tab Ảnh: thư mục ảnh thật
# Hiện như trang Soạn bài (T-084, ghi chú U2 của Lá Chắn T-048): chỉ tên thư mục gốc lấy từ
# ``ImageLibrary.roots()``, không bao giờ in đường dẫn khai báo trong IMAGE_FOLDERS. Tên lấy từ máy
# là dữ liệu chưa tin cậy: ký tự vô hình hiện thành «�», cô lập hướng chữ, escape Markdown, không
# qua ``unsafe_allow_html`` (U1). ``folder_name_md`` và ``through_link`` chép theo ``name_md`` và
# ``_through_link`` của ``views/write.py`` (file trang, không nhập được): sửa bên nào thì sửa cả
# bên kia.

# Ký tự không nhìn thấy hoặc làm tên trông khác thật (như ``_HIDDEN_IN_NAME`` của Soạn bài).
_HIDDEN_IN_NAME = frozenset({"Cc", "Cf", "Cs", "Co", "Cn", "Zl", "Zp"})


def folder_name_md(name: str) -> str:
    """Tên thư mục để hiện bằng Markdown: «�» thay ký tự vô hình, cô lập hướng chữ, escape."""
    visible = "".join(
        "\ufffd" if unicodedata.category(ch) in _HIDDEN_IN_NAME else ch for ch in name
    )
    return escape_markdown(f"\u2068{visible}\u2069")


def through_link(folder: Path) -> bool:
    """Đường dẫn thư mục gốc có tầng nào là lối tắt (symlink, junction) không."""
    try:
        folder = folder.expanduser()
        return any(part.is_symlink() or part.is_junction() for part in (folder, *folder.parents))
    except (OSError, RuntimeError, ValueError):
        return False


def image_folders_list(settings) -> None:
    """Thư mục ảnh thật theo thứ tự khai báo: tên cuối, tìm thấy hay không, có đi qua lối tắt."""
    st.markdown("**Thư mục ảnh thật**")
    folders = settings.image_folders
    if not folders:
        st.caption("Chưa khai báo. Điền IMAGE_FOLDERS trong file .env.")
        return
    try:
        roots = ImageLibrary.from_settings(settings).roots()
    except (OSError, ValueError):
        # Câu lỗi của hệ điều hành có đường dẫn đầy đủ: chỉ báo câu cố định.
        st.warning(
            "Không đọc được thư mục ảnh trên máy này (không có quyền hoặc ổ đĩa vừa bị ngắt). "
            "Tải lại trang để thử lại."
        )
        return
    lines, linked = [], False
    for root in roots:
        # ``root.message`` là câu cố định của ImageLibrary (số thứ tự, không có đường dẫn).
        found = "✅ tìm thấy" if root.available else f"⚠️ {escape_markdown(root.message)}"
        line = f"{root.index + 1}. {folder_name_md(root.label)} — {found}"
        if through_link(folders[root.index]):
            line += " · ↪️ đi qua lối tắt"
            linked = True
        lines.append(line)
    st.markdown("\n".join(lines))
    if linked:
        st.warning(
            "Thư mục ghi «đi qua lối tắt» là lối tắt (symlink/junction) hoặc nằm trong một lối "
            "tắt: app đọc thư mục mà lối tắt trỏ tới. Hãy chắc đó đúng là thư mục ảnh bạn muốn "
            "(khai báo thẳng ổ đĩa, ví dụ E:/, thì không bị)."
        )
    st.caption(
        "Đọc từ IMAGE_FOLDERS trong file .env, theo thứ tự khai báo. App chỉ hiện tên thư mục "
        "cuối, không hiện đường dẫn đầy đủ."
    )


# ------------------------------------------------------------------ tab Google (T-101)
# Cài đặt → Google (thiết kế T-094 mục 2.1, 2.4; Lá Chắn LC-T094-12, -15, -31, -34; điều kiện 3
# Lá Chắn T-097): chỉ hiện «đã khai báo / chưa», **tên** file khóa (không đường dẫn), email tài
# khoản dịch vụ (để chia sẻ Sheet), tên Sheet đọc từ Google; mã Sheet chỉ 4 ký tự cuối. Không in
# nội dung file khóa. ``GOOGLE_SERVICE_ACCOUNT_FILE`` không ghi được từ đây; ``GOOGLE_SHEET_ID`` ghi
# qua ``env_file.set_google_sheet_id`` (bộ kiểm riêng). Client Google tạo mới mỗi lần bấm, không
# giữ client, tài khoản dịch vụ hay đối tượng lỗi trong phiên. «Kiểm tra kết nối», «Chuẩn bị trang
# tính» chỉ chạy khi bấm.

GOOGLE_SHEET_VAR = "GOOGLE_SHEET_ID"
GOOGLE_LINK_KEY = "google-sheet-link"


def visible(text: str) -> str:
    """Chữ lấy từ file (tên file, email): ký tự vô hình, điều khiển, đảo hướng chữ thành «�»."""
    hidden = _HIDDEN_IN_NAME
    return "".join("\ufffd" if unicodedata.category(ch) in hidden else ch for ch in str(text))


def google_flash(kind: str, text: str) -> None:
    S["google-flash"] = (kind, text)


def _save_sheet() -> None:
    # Chạy trong on_click, trước khi trang đọc lại .env: ghi rồi xóa ô nhập dù lưu được hay không.
    value = S.get(GOOGLE_LINK_KEY, "")
    S[GOOGLE_LINK_KEY] = ""
    for name in ("google-check", "google-missing"):
        S.pop(name, None)
    try:
        sheet_id = sheet_id_from_link(value)
        env_file.set_google_sheet_id(sheet_id)
    except (SheetsError, env_file.EnvFileError) as exc:
        google_flash("error", str(exc))
    else:
        google_flash(
            "success",
            f"Đã lưu Sheet kế hoạch (mã {mask_sheet_id(sheet_id)}) vào file .env. Bấm «Kiểm tra "
            "kết nối» để xem phần mềm đọc được chưa.",
        )


def _clear_sheet() -> None:
    for name in ("google-check", "google-missing"):
        S.pop(name, None)
    try:
        env_file.clear_google_sheet_id()
    except env_file.EnvFileError as exc:
        google_flash("error", str(exc))
    else:
        google_flash("success", "Đã bỏ Sheet kế hoạch khỏi file .env (Sheet trên Google vẫn còn).")


def google_client(settings) -> tuple[SheetsClient | None, str]:
    """Client mới mỗi lần bấm; ``(None, câu báo)`` khi chưa khai báo hay khai báo sai."""
    if not (settings.google_sheet_id and settings.google_service_account_file):
        return None, "Chưa khai báo đủ file khóa và Sheet kế hoạch."
    try:
        return SheetsClient.from_settings(settings), ""
    except (SheetsError, ServiceAccountError, ConfigError) as exc:
        return None, str(exc)


def account_card(settings) -> bool:
    """Tài khoản dịch vụ: đã khai báo chưa, tên file, email, cảnh báo. ``True`` nếu dùng được."""
    st.markdown("#### 🔑 Tài khoản dịch vụ Google (file khóa)")
    if not settings.google_service_account_file:
        st.markdown(":gray-badge[⚪ Chưa khai báo]")
        st.caption(
            "Ghi đường dẫn đầy đủ của file khóa JSON vào dòng GOOGLE_SERVICE_ACCOUNT_FILE trong "
            "file .env (ô này không nhập ở đây được). File phải nằm ngoài thư mục phần mềm, ngoài "
            "thư mục ảnh và thư mục đồng bộ (Google Drive, OneDrive…). Xem README."
        )
        return False
    try:
        account = load_service_account(
            settings.google_service_account_file, image_folders=settings.image_folders
        )
    except ServiceAccountError as exc:
        st.markdown(":orange-badge[⚠️ Đã khai báo nhưng chưa dùng được]")
        st.error(escape_markdown(str(exc)))
        return False
    st.markdown(":green-badge[✅ Đã khai báo]")
    st.markdown(f"File khóa: {folder_name_md(account.file_name)}")
    st.caption("Email của tài khoản dịch vụ, để chia sẻ Sheet kế hoạch (quyền Người chỉnh sửa):")
    st.code(visible(account.email), language=None)
    for warning in account.warnings:  # câu cố định; có thể chứa tên file (đã làm sạch)
        st.warning(escape_markdown(visible(warning)))
    return True


def sheet_card(settings) -> None:
    st.markdown("#### 📗 Google Sheet kế hoạch")
    if settings.google_sheet_id:
        st.markdown(":green-badge[✅ Đã khai báo]")
        st.caption(f"Mã Sheet {mask_sheet_id(settings.google_sheet_id)} (chỉ hiện 4 ký tự cuối).")
    else:
        st.markdown(":gray-badge[⚪ Chưa khai báo]")
    # ``env_file.overridden_by_os_environ`` chỉ nhận tên biến khóa AI: kiểm thẳng biến môi trường.
    if os.environ.get(GOOGLE_SHEET_VAR, "").strip():
        st.warning(
            "Mã Sheet đang được đặt trong biến môi trường của máy (được ưu tiên hơn file .env), "
            f"nên link nhập ở đây sẽ không có hiệu lực. Muốn đổi, hãy gỡ biến {GOOGLE_SHEET_VAR} "
            "khỏi máy."
        )
    st.text_input(
        "Link Google Sheet kế hoạch",
        key=GOOGLE_LINK_KEY,
        placeholder="https://docs.google.com/spreadsheets/d/…",
        autocomplete="off",
    )
    st.caption(
        "Mở Sheet trên trình duyệt, chép link ở thanh địa chỉ rồi dán vào đây. Phần mềm chỉ lấy "
        "mã Sheet trong link, không mở link."
    )
    save, clear, _ = st.columns([1, 1.5, 1.5])
    save.button(
        "Lưu", key="google-sheet-save", type="primary", width="stretch", on_click=_save_sheet
    )
    clear.button(
        "Bỏ Sheet",
        key="google-sheet-clear",
        width="stretch",
        disabled=not settings.google_sheet_id,
        on_click=_clear_sheet,
    )


def check_card(settings, ready: bool) -> None:
    st.markdown("#### 🔎 Kiểm tra và chuẩn bị")
    usable = ready and bool(settings.google_sheet_id)
    check, prepare = st.columns(2)
    if check.button(
        "Kiểm tra kết nối", key="google-check-btn", width="stretch", disabled=not usable
    ):
        S.pop("google-missing", None)
        client, problem = google_client(settings)
        if client is None:
            S["google-check"] = ("error", problem)
        else:
            try:
                with st.spinner("Đang hỏi Google Sheets…"):
                    info = client.get_info()
            except SheetsError as exc:
                S["google-check"] = ("error", str(exc))
            else:
                tab = (
                    "đã có"
                    if info.plan_tab is not None
                    else "chưa có (bấm «Chuẩn bị trang tính» để tạo)"
                )
                S["google-check"] = (
                    "success",
                    f"Kết nối được Google Sheet «{info.title}». Trang tính «KeHoach»: {tab}.",
                )
    if prepare.button(
        "Chuẩn bị trang tính",
        key="google-prepare-btn",
        width="stretch",
        disabled=not usable,
        help="Tạo trang tính «KeHoach» nếu chưa có, ghi dòng tiêu đề cột, cố định dòng tiêu đề, "
        "định dạng cột ngày và danh sách chọn. Không xóa, không dời cột có sẵn.",
    ):
        prepare_plan_sheet(settings, add_missing=False)
    if S.get("google-missing") and st.button(
        "Thêm cột còn thiếu", key="google-add-columns", disabled=not usable
    ):
        prepare_plan_sheet(settings, add_missing=True)
    checked = S.get("google-check")
    if checked:
        kind, text = checked
        (st.success if kind == "success" else st.error)(escape_markdown(visible(text)))


def prepare_plan_sheet(settings, *, add_missing: bool) -> None:
    """«Chuẩn bị trang tính» / «Thêm cột còn thiếu»: chỉ khi bấm (LC-T094-31)."""
    client, problem = google_client(settings)
    if client is None:
        S["google-check"] = ("error", problem)
        return
    try:
        with st.spinner("Đang chuẩn bị trang tính trên Google Sheets…"):
            result = plan_sync.prepare_sheet(client, add_missing=add_missing)
    except (SheetsError, plan_sync.SheetPlanError) as exc:
        S["google-check"] = ("error", str(exc))
        return
    S["google-missing"] = bool(result.missing)
    S["google-check"] = ("success", result.message)


def google_tab(settings) -> None:
    st.caption(
        "Kế hoạch bài viết nằm trên Google Sheets để hai máy luôn thấy giống nhau. Phần mềm đọc, "
        "ghi Sheet bằng một tài khoản dịch vụ (service account) chỉ được chia sẻ đúng Sheet đó."
    )
    flash = S.pop("google-flash", None)
    if flash:
        kind, text = flash
        (st.success if kind == "success" else st.error)(escape_markdown(text))
    left, right = st.columns(2, gap="large")
    with left, st.container(border=True, height="stretch"):
        ready = account_card(settings)
    with right, st.container(border=True, height="stretch"):
        sheet_card(settings)
    check_card(settings, ready)
    st.page_link("views/plan.py", label="Mở trang Kế hoạch", icon="🗂️")


# Đọc cấu hình sau các callback ở trên, nên trạng thái "đã khai báo" đổi ngay khi vừa lưu.
settings = load_settings()

head, logout = st.columns([5, 1], vertical_alignment="center")
with head:
    ui.page_header("Cài đặt", "Những thiết lập dùng chung cho mọi bài viết.", demo=True)
if logout.button("Đăng xuất", width="stretch"):
    S.clear()
    st.rerun()

# Tab Google đặt cuối: giữ thứ tự các tab đã có (test cũ tìm tab theo vị trí).
tone, models, images, connections, google = st.tabs(
    ["✍️ Văn phong", "🤖 Mô hình AI", "🖼️ Ảnh", "🔌 Kết nối", "📗 Google"]
)

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
    blind_models_tab(settings)

with images:
    image_folders_list(settings)
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

with google:
    google_tab(settings)
