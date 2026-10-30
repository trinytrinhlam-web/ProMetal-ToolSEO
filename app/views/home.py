"""Bài viết: các bài đang viết, bài tiếp theo trong kế hoạch, bài đã gửi WordPress.

«Tiếp theo trong kế hoạch» và ô «Từ kế hoạch» đọc bản kế hoạch lưu trên máy (cache
``data/plan_cache.sqlite``, không gọi Google khi mở trang); «Đã gửi WordPress» lấy mã bài từ kho
nháp và cột Mã bài WordPress của kế hoạch, trạng thái trên website chỉ hỏi khi bấm (chỉ đọc). Chữ
kế hoạch, tiêu đề bài hiện bằng ``escape_markdown`` (T-101, LC-T094-3). «Bắt đầu» không gửi gì
lên WordPress: chỉ mở Soạn bài (LC-T094-35). Khung «Đang viết» vẫn là bản demo.
"""

import html
from datetime import UTC, date, datetime, timedelta

import streamlit as st

import seo_app.storage.drafts as drafts
from seo_app import demo, ui
from seo_app.config import ConfigError, load_settings
from seo_app.google.service_account import ServiceAccountError
from seo_app.google.sheets import SheetsClient, SheetsError
from seo_app.plan import model, sync
from seo_app.plan.model import PlanRow
from seo_app.storage import plan_cache
from seo_app.storage.drafts import DraftError, DraftStore
from seo_app.text import escape_markdown
from seo_app.wordpress import WordPressClient, WordPressError

settings = load_settings()
S = st.session_state

UPCOMING = 3  # số bài «Chưa viết» gần nhất hiện ở «Tiếp theo trong kế hoạch»
SENT_SHOWN = 8  # số bài đã gửi hiện ở «Đã gửi WordPress»
LATE_AFTER = timedelta(minutes=15)  # bài hẹn giờ quá giờ chừng này mà chưa lên: «Lỡ lịch»
MODE_LABELS = {"draft": "Đã gửi nháp", "future": "Đã hẹn giờ", "publish": "Đã đăng"}
WEB_LABELS = {
    "draft": ("Nháp trên website", "gray"),
    "future": ("Đã hẹn giờ", "violet"),
    "publish": ("Đã đăng", "green"),
    "pending": ("Chờ duyệt", "orange"),
    "private": ("Riêng tư", "gray"),
}
MSG_NO_PLAN = "Chưa có kế hoạch trên máy: mở trang Kế hoạch để tải từ Google Sheets."
MSG_ODD_DATA = "Không đọc được kế hoạch (dữ liệu có chỗ lạ)."
SQLITE_HEADER = b"SQLite format 3\x00"
MSG_DRAFTS_MOVED = (
    "File nháp cũ bị hỏng nên đã được cất sang một bên (tên «{name}», cùng thư mục). App bắt "
    "đầu file nháp mới."
)


def draft_store() -> DraftStore | None:
    """Kho nháp để **đọc** ở trang này. Chưa có file nháp: ``None`` (không tạo file). File không
    phải SQLite (hỏng): ``None``, để trang Soạn bài tự cất file hỏng và báo cho người dùng (mở
    kho ở đây sẽ cất file lặng lẽ, câu báo của Soạn bài không còn hiện)."""
    path = drafts.DEFAULT_DRAFTS_FILE
    try:
        with path.open("rb") as handle:
            if handle.read(len(SQLITE_HEADER)) != SQLITE_HEADER:
                return None
    except OSError:
        return None
    return DraftStore(path)


def note_recovered(store: DraftStore | None) -> None:
    """File nháp hỏng kiểu khác (đúng đầu file SQLite) vẫn bị kho cất sang một bên: báo ở đây."""
    if store is not None and store.recovered_from is not None:
        st.warning(MSG_DRAFTS_MOVED.format(name=escape_markdown(store.recovered_from.name)))


def cached_plan() -> sync.SheetPlan | None:
    """Kế hoạch lưu trên máy (không gọi Google). Chưa khai báo Sheet, chưa tải lần nào: ``None``.
    Chưa có file cache thì không mở kho (mở kho là tạo file): mở trang không ghi gì xuống đĩa."""
    if not settings.google_sheet_id or not plan_cache.DEFAULT_PLAN_CACHE_FILE.exists():
        return None
    store = plan_cache.PlanCacheStore(
        path=plan_cache.DEFAULT_PLAN_CACHE_FILE, timezone=settings.timezone_name
    )
    try:
        cached = store.load(settings.google_sheet_id)
        if cached is None:
            return None
        return sync.parse_sheet(cached.values, fetched_at=cached.fetched_at, from_cache=True)
    except (plan_cache.PlanCacheError, model.PlanKeyError, ValueError):
        return None


def upcoming(plan: sync.SheetPlan | None) -> list[PlanRow]:
    """Bài «Chưa viết» có Mã bài, ngày dự kiến gần nhất trước (chưa có ngày xếp cuối)."""
    if plan is None:
        return []
    rows = [r.plan for r in plan.rows if r.plan.key and r.plan.status == model.STATUS_NEW]
    rows = [r for r in rows if r.kind != model.KIND_UPDATE_OLD]
    return sorted(rows, key=lambda r: r.planned_date or date.max)


def start_writing(key: str) -> None:
    """Như nút «Viết bài» của trang Kế hoạch (thiết kế 1.6; LC-T094-35: không gửi gì lên
    WordPress): đã có nháp của Mã bài này thì mở nháp đó; chưa có thì đọc lại đúng dòng trên Sheet
    rồi mở Soạn bài với từ khóa đã qua ``PlanRow``. Client Google tạo mới mỗi lần bấm. Chỉ đọc
    Sheet, không ghi Sheet; cùng hợp đồng khóa phiên với trang Kế hoạch (``_open_draft``,
    ``_start_keyword``, ``_start_plan_key``; báo cáo T-101)."""
    try:
        key = model.parse_key(key)  # Mã bài đọc từ cache: kiểm lại trước khi dùng
    except ValueError:
        key = ""
    if not key:
        st.error(MSG_ODD_DATA)
        return
    if not (settings.google_sheet_id and settings.google_service_account_file):
        st.error("Chưa kết nối Google Sheets. Vào Cài đặt → 📗 Google để khai báo.")
        return
    try:
        client = SheetsClient.from_settings(settings)
    except (SheetsError, ServiceAccountError, ConfigError) as exc:
        st.error(escape_markdown(str(exc)))
        return
    store = draft_store()
    try:
        existing = store.find_plan_draft(key, client.sheet_hash) if store else None
    except (DraftError, ValueError):
        existing = None
    note_recovered(store)
    if existing:
        S.pop("_start_plan_key", None)  # không để Mã bài của lần bấm trước sót lại
        S["_open_draft"] = existing
        st.switch_page("views/write.py")
    try:
        with st.spinner("Đang đọc lại dòng kế hoạch trên Google Sheet…"):
            row = sync.open_row(client, key, now=settings.now())
        checked = PlanRow.model_validate(row.plan.model_dump())  # dữ liệu Sheet chưa tin cậy
        plan_key = model.parse_key(checked.key)
    except (SheetsError, sync.SheetPlanError) as exc:
        st.error(escape_markdown(str(exc)))
        return
    except ValueError:
        st.error(MSG_ODD_DATA)
        return
    if plan_key != key:
        st.error(MSG_ODD_DATA)
        return
    S["_start_keyword"] = checked.keyword
    S["_start_plan_key"] = plan_key
    st.switch_page("views/write.py")


def sent_items(plan: sync.SheetPlan | None) -> list[dict]:
    """Bài app đã gửi WordPress: mã bài từ kho nháp (trạng thái gửi) và cột Mã bài WordPress."""
    items: dict[int, dict] = {}
    store = draft_store()
    try:
        for summary in store.list_drafts().drafts if store else ():
            state = store.load_send_state(summary.id)
            if state is None or state.post_id is None:
                continue
            label = "Chưa rõ (đang gửi?)" if state.pending else MODE_LABELS[state.mode]
            when = state.scheduled_for or state.updated_at
            # Tiêu đề nháp là chữ người dùng gõ hay AI viết: bỏ ký tự điều khiển, đảo hướng chữ,
            # vô hình trước khi hiện (LC-T094-3), như chữ kế hoạch.
            title = model.clean_text(summary.title) or "Bài chưa đặt tên"
            items[state.post_id] = {"title": title, "label": label, "when": when}
    except (DraftError, ValueError):
        pass
    note_recovered(store)
    for row in plan.rows if plan is not None else ():
        post_id = row.plan.wp_post_id
        if post_id is None or post_id in items:
            continue
        when = row.plan.published_at or row.plan.updated_at
        title = row.plan.title_hint or row.plan.keyword
        items[post_id] = {"title": title, "label": row.plan.status, "when": when}
    ordered = sorted(
        items.items(),
        key=lambda pair: pair[1]["when"] or datetime.min.replace(tzinfo=UTC),
        reverse=True,
    )
    return [{"id": post_id, **item} for post_id, item in ordered[:SENT_SHOWN]]


def ask_website(ids: list[int]) -> bool:
    """Hỏi website trạng thái các bài (chỉ đọc, ``post_statuses``); không sửa bài nào. ``False``:
    lỗi (câu báo đã hiện)."""
    try:
        client = WordPressClient.from_settings(settings)
    except WordPressError as exc:
        st.warning(escape_markdown(str(exc)))
        return False
    try:
        with st.spinner("Đang hỏi trạng thái bài trên website…"):
            states = client.post_statuses(ids)
    except WordPressError as exc:
        st.error(escape_markdown(str(exc)))
        return False
    S.home_web = {post_id: (state.status, state.date_gmt) for post_id, state in states.items()}
    S.home_web_asked = tuple(ids)
    return True


def web_badge(post_id: int) -> str:
    """Nhãn trạng thái trên website (sau khi bấm hỏi); rỗng nếu chưa hỏi bài này."""
    if post_id not in S.get("home_web_asked", ()):
        return ""
    found = S.get("home_web", {}).get(post_id)
    if found is None:
        return ":red-badge[Không thấy trên website]"
    status, date_gmt = found
    if status == "future" and date_gmt:
        try:
            due = datetime.strptime(date_gmt, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=UTC)
        except ValueError:
            due = None
        if due is not None and datetime.now(UTC) - due > LATE_AFTER:
            return ":red-badge[Lỡ lịch]"
    label, color = WEB_LABELS.get(status, ("", "gray"))
    return f":{color}-badge[{label}]" if label else ""


def day_text(moment: datetime | None) -> str:
    if moment is None:
        return ""
    return moment.astimezone(model.TIMEZONE).strftime("%d/%m")


plan = cached_plan()
next_rows = upcoming(plan)

top_left, top_right = st.columns([3, 1], vertical_alignment="bottom")
with top_left:
    ui.page_header(
        "Bài viết",
        f"{len(demo.ARTICLES_IN_PROGRESS)} bài đang viết · {ui.day_label(settings.now())}",
        demo=True,
    )
with top_right, st.popover("✍️ Viết bài mới", type="primary", width="stretch"):
    typed = st.text_input("Từ khóa", placeholder="ví dụ: lan can cầu thang sắt")
    st.caption("hoặc chọn từ kế hoạch")
    by_key = {row.key: row for row in next_rows}
    picked = st.selectbox(
        "Từ kế hoạch",
        list(by_key),
        format_func=lambda key: f"{key} · {by_key[key].keyword}",
        label_visibility="collapsed",
        placeholder="Chưa có bài «Chưa viết» trong kế hoạch",
    )
    if st.button("Bắt đầu", type="primary", width="stretch"):
        if typed.strip():
            # Trang Soạn bài đọc khóa này để mở bài mới với từ khóa đã gõ.
            S["_start_keyword"] = typed.strip()
            st.switch_page("views/write.py")
        elif picked:
            start_writing(picked)
        else:
            st.warning("Gõ từ khóa hoặc chọn một bài trong kế hoạch.")

st.subheader("Đang viết")
cols = st.columns(3)
for col, article in zip(cols, demo.ARTICLES_IN_PROGRESS, strict=False):
    with col, st.container(border=True, height="stretch"):
        step = article["step"]
        st.markdown(
            f'<div class="card-kw">{html.escape(article["keyword"])}</div>'
            f'<div class="card-title">{html.escape(article["title"])}</div>'
            + ui.progress_dots(len(demo.STEPS), step),
            unsafe_allow_html=True,
        )
        badge = f":blue-badge[Bước {step}/{len(demo.STEPS)} · {demo.STEPS[step - 1]}]"
        if article["score"]:
            color = "green" if article["score"] >= 85 else "orange"
            badge += f" :{color}-badge[Văn phong {article['score']}]"
        st.markdown(badge)
        st.markdown(
            f'<div class="card-note">{html.escape(article["note"])} · {article["updated"]}</div>',
            unsafe_allow_html=True,
        )
        if st.button("Mở bài", key=f"open-{article['keyword']}", width="stretch"):
            st.switch_page("views/write.py")

left, right = st.columns([3, 2], gap="large")
with left:
    st.subheader("Tiếp theo trong kế hoạch")
    if plan is None:
        st.caption(MSG_NO_PLAN)
    elif not next_rows:
        st.caption("Kế hoạch không còn bài «Chưa viết».")
    for row in next_rows[:UPCOMING]:
        with st.container(border=True):
            a, b, c = st.columns([5, 2, 2], vertical_alignment="center")
            intent = f"  \n:gray[{escape_markdown(row.intent)}]" if row.intent else ""
            a.markdown(f"**{escape_markdown(row.keyword)}**{intent}")
            when = row.planned_date.strftime("%d/%m") if row.planned_date else "chưa có ngày"
            b.markdown(f":gray[Dự kiến]  \n{when}")
            if c.button("Bắt đầu", key=f"start-{row.key}", width="stretch"):
                start_writing(row.key)
    st.page_link("views/plan.py", label="Xem cả kế hoạch", icon="🗂️")
with right:
    st.subheader("Đã gửi WordPress")
    sent = sent_items(plan)
    with st.container(border=True):
        if not sent:
            st.caption("Chưa có bài nào phần mềm đã gửi lên WordPress.")
        for item in sent:
            badge = web_badge(item["id"]) or f":violet-badge[{escape_markdown(item['label'])}]"
            st.markdown(
                f"**{escape_markdown(item['title'])}**  \n{badge} "
                f":gray[#{item['id']} · {day_text(item['when'])}]"
            )
        asked = sent and st.button(
            "🌐 Hỏi trạng thái trên website", key="home-web", width="stretch"
        )
        if asked and ask_website([item["id"] for item in sent]):
            st.rerun()
