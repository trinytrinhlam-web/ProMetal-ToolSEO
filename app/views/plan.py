"""Kế hoạch (Giai đoạn 5, T-101; thiết kế T-094 mục 1.2–1.8): đưa kế hoạch vào (tải file, dán chữ,
link Google Sheets), phần mềm đề xuất thay đổi kèm lý do, bạn tick duyệt rồi «Áp dụng» mới ghi
Google Sheets. Danh sách bài đọc từ Google Sheets (cache ``data/plan_cache.sqlite``).

An toàn (Lá Chắn T-094 LC-T094-1 → -3, -32 → -35; điều kiện của T-097, T-098, T-100 cho T-101):

- Chữ từ Sheet, file, chữ dán, AI, website (``PlanRow``, đề xuất, lý do, ``Conflict.now``) chỉ hiện
  bằng ô bảng ``st.dataframe``, ``st.text`` hoặc ``escape_markdown``: không ``unsafe_allow_html``,
  không ``st.table`` (``st.table`` đọc Markdown trong ô). ``PlanRow`` đã bỏ ký tự điều khiển, đảo
  hướng chữ, vô hình (``plan.model.clean_text``). Nhãn ô tick chỉ có loại đề xuất và Mã bài.
- Câu báo lỗi là ``str(err)`` của lớp lỗi app (câu cố định), hiện bằng chữ thường; không
  ``st.exception``. Không giữ client Google, tài khoản dịch vụ, đối tượng lỗi trong
  ``st.session_state``; client tạo mới mỗi lần dùng.
- Đề xuất chỉ dựng bằng ``propose.compare_rows`` và ``ContentWriter.plan_changes`` (``from_ai``).
  «Bỏ» và dòng có cảnh báo không tick sẵn (``Proposal.preselected``). Bản kế hoạch người dùng đã
  xem (``plan_base``) giữ trong phiên tới lúc «Áp dụng» (``apply_proposals`` so với bản đó).
- Tải file: kiểm cỡ bằng code trước khi đọc byte (≤ 1 MB), chỉ .csv/.tsv/.txt/.md, không ghi đĩa.
- AI chỉ đọc khi bấm «Gửi AI đọc»; chữ có số điện thoại, email thì cảnh báo trước (A3).
- «Viết bài» không gửi gì lên WordPress: chỉ mở Soạn bài với từ khóa đã qua ``PlanRow``.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import streamlit as st

import seo_app.storage.drafts as drafts
from seo_app import ui
from seo_app.ai import AIError, AIRouter, load_ai_config
from seo_app.ai.base import TokenLimitError
from seo_app.config import ConfigError, load_settings
from seo_app.content import ContentWriter, load_rules
from seo_app.content.workflow import PersonalInfoError
from seo_app.google.service_account import ServiceAccountError, load_service_account
from seo_app.google.sheets import SheetsClient, SheetsError, sheet_id_from_link
from seo_app.plan import model, parse, propose, sync
from seo_app.plan.model import FIELD_LABELS, PlanRow
from seo_app.storage import plan_cache
from seo_app.storage import site_index as site_storage
from seo_app.storage.drafts import DraftError, DraftStore
from seo_app.text import escape_markdown
from seo_app.wordpress import WordPressClient, WordPressError

settings = load_settings()
S = st.session_state

TAB_FILE, TAB_PASTE, TAB_SHEET = "Tải file", "Dán nội dung", "Google Sheets"
SOURCE_TABS = [TAB_FILE, TAB_PASTE, TAB_SHEET]
PASTE_PLACEHOLDER = (
    "Dán bảng chép từ Excel hay Google Sheets (có cột «Từ khóa chính»), hoặc ghi chú định hướng, "
    "ví dụ:\nTháng 11: tập trung cửa cuốn ở Bình Tân.\n- Thêm bài «sửa cửa cuốn kêu to»\n- Dời "
    "bài «sơn lại cổng sắt» sang cuối tháng"
)
# Cột của danh sách bài (theo thứ tự thiết kế 2.4; bỏ cột app tự ghi «Cập nhật lúc»).
LIST_FIELDS = (
    "key", "keyword", "intent", "kind", "priority", "planned_date", "planned_time", "status",
    "title_hint", "wp_post_id", "published_at",
)  # fmt: skip
# Trường hiện ở «Xem đủ một đề xuất» (mọi trường đề xuất được, đủ chữ, không cắt).
DETAIL_FIELDS = (
    "key", "keyword", "secondary", "intent", "kind", "priority", "planned_date", "planned_time",
    "status", "title_hint", "slug", "target_id", "notes",
)  # fmt: skip
LONG_FIELDS = ("secondary", "title_hint", "notes")
WEB_LABELS = {
    "draft": "Nháp",
    "future": "Đã hẹn giờ",
    "publish": "Đã đăng",
    "pending": "Chờ duyệt",
    "private": "Riêng tư",
}
SQLITE_HEADER = b"SQLite format 3\x00"
MSG_DRAFTS_MOVED = (
    "File nháp cũ bị hỏng nên đã được cất sang một bên (tên «{name}», cùng thư mục). App bắt "
    "đầu file nháp mới."
)
LATE_AFTER = timedelta(minutes=15)  # bài hẹn giờ quá giờ chừng này mà chưa lên: «Lỡ lịch»

MSG_NO_GOOGLE = (
    "Chưa kết nối Google Sheets nên chưa có kế hoạch để so và ghi. Vào Cài đặt → 📗 Google để "
    "khai báo (xem README mục «Kế hoạch và Google Sheets»)."
)
MSG_NO_BASE = "Chưa đọc được kế hoạch hiện tại trên Google Sheets nên chưa đề xuất được."
MSG_EMPTY_SOURCE = {
    TAB_FILE: "Chưa chọn file kế hoạch.",
    TAB_PASTE: "Chưa dán nội dung nào.",
    TAB_SHEET: "Chưa dán link Google Sheets.",
}
MSG_NO_CHANGES = "Không có thay đổi nào so với kế hoạch hiện tại."
MSG_RELOADED = "Đây là Sheet kế hoạch chính: đã tải lại kế hoạch."
MSG_ODD_DATA = "Không đọc được kế hoạch (dữ liệu có chỗ lạ). Kiểm tra lại nguồn rồi thử lại."
MSG_AI_TOO_LONG = (
    "Ghi chú dài hoặc AI đề xuất nhiều thay đổi quá, vượt giới hạn trả lời. Chia ghi chú thành "
    "vài phần nhỏ rồi đưa vào từng phần."
)
MSG_AI_COST = "Đây là chữ tự do: AI sẽ đọc và đề xuất thay đổi (gọi AI 1 lần, có tốn tiền)."
MSG_APPLY_FAILED = "Chưa ghi gì lên Google Sheet."
MSG_WEB_NONE = "Chưa có dòng nào có Mã bài WordPress để hỏi website."
MSG_WEB_NOTE = (
    "Cột «Trên website» chỉ để xem: phần mềm chưa tự đổi cột Trạng thái trên Google Sheet theo "
    "website. «Lỡ lịch»: bài hẹn giờ đã quá giờ 15 phút mà chưa lên (thường do lịch chạy của "
    "WordPress chạy trễ); mở trang quản trị WordPress để kiểm tra."
)


# ================================================================ kết nối (mỗi lần tạo mới)


def sheets_client() -> tuple[SheetsClient | None, str]:
    """Client Google Sheets mới mỗi lần gọi (điều kiện 3 Lá Chắn T-097): không cache, không giữ
    trong phiên. ``(None, "")`` khi chưa khai báo; ``(None, câu báo)`` khi khai báo sai."""
    if not (settings.google_sheet_id and settings.google_service_account_file):
        return None, ""
    try:
        return SheetsClient.from_settings(settings), ""
    except (SheetsError, ServiceAccountError, ConfigError) as exc:
        return None, str(exc)


def wordpress_client() -> WordPressClient | None:
    try:
        return WordPressClient.from_settings(settings)
    except WordPressError:
        return None


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


def plan_store() -> plan_cache.PlanCacheStore:
    # Đọc đường dẫn lúc chạy (không lúc import) để test trỏ file cache sang thư mục tạm.
    return plan_cache.PlanCacheStore(
        path=plan_cache.DEFAULT_PLAN_CACHE_FILE, timezone=settings.timezone_name
    )


def site_store() -> site_storage.SiteIndexStore:
    return site_storage.SiteIndexStore(site_storage.DEFAULT_SITE_INDEX_FILE)


def cached_index() -> site_storage.SiteIndex | None:
    """Danh sách bài đã đăng từ cache trên máy (không gọi mạng), để đổi «Trang dịch vụ đích»."""
    client = wordpress_client()
    return site_store().load(client.base_url) if client is not None else None


def fresh_index() -> tuple[site_storage.SiteIndex | None, str]:
    """Danh sách bài đã đăng cho kiểm trùng khi đề xuất (cache còn mới thì không gọi mạng)."""
    with st.spinner("Đang tải danh sách bài đã đăng trên website…"):
        found = site_storage.site_listing(site_store(), wordpress_client())
    return found.index, found.notice


def today() -> date:
    return settings.now().date()


# ================================================================ chữ hiện ra (chữ thuần)


def plain(text: object) -> str:
    """Chữ (câu báo, chữ dữ liệu) để đưa vào Markdown: escape, không thành link, định dạng."""
    return escape_markdown("" if text is None else str(text))


def show(kind: str, text: object) -> None:
    {"error": st.error, "warning": st.warning, "info": st.info, "success": st.success}.get(
        kind, st.caption
    )(plain(text))


def cell(name: str, value: object) -> str:
    """Giá trị một trường ``PlanRow`` thành chữ cho ô bảng (chữ thuần)."""
    if value in (None, ""):
        return ""
    if isinstance(value, datetime):
        return value.astimezone(model.TIMEZONE).strftime("%d/%m/%Y %H:%M")
    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")
    if name == "target_id":
        return f"bài #{value}"  # chỉ mã bài trên website, không địa chỉ (LC-T094-20)
    return str(value)


def proposal_change(item: propose.Proposal) -> str:
    if item.action is propose.Action.ADD:
        return "Bài mới"
    if item.action is propose.Action.DROP:
        return "Trạng thái → Bỏ"
    return ", ".join(FIELD_LABELS[name] for name in item.changes) or "Không đổi"


def pick_label(number: int, item: propose.Proposal) -> str:
    """Nhãn ô tick: số dòng, loại đề xuất, Mã bài (đúng dạng ``B-001``); không chữ dữ liệu."""
    mark = " ⚠️" if item.warnings else ""
    return f"Dòng {number}: {item.action.value} {item.key or '(chưa có mã)'}{mark}"


# ================================================================ đọc kế hoạch, đề xuất


def keep_proposals(found: propose.ProposalSet, base: sync.SheetPlan, index, notes) -> None:
    S.plan_round = S.get("plan_round", 0) + 1  # khóa ô tick mới cho bộ đề xuất mới
    S.pop("plan_result", None)
    S.pop("plan_ai", None)
    if not found.items:
        S.pop("plan_proposals", None)
        S.pop("plan_base", None)
        S.plan_flash = ("info", " ".join([*notes, *found.notes, MSG_NO_CHANGES]))
        return
    S.plan_proposals, S.plan_base, S.plan_index = found, base, index
    S.plan_notes = (*notes, *found.notes)


def parsed_notes(parsed: parse.ParsedPlan) -> list[str]:
    notes = list(parsed.warnings)
    if parsed.skipped:
        notes.append(f"{parsed.skipped} dòng bỏ qua (thiếu từ khóa chính hoặc sai khuôn).")
    return notes


def read_source(base: sync.SheetPlan | None, upload) -> bool:
    """Nút «Đọc kế hoạch và đề xuất cập nhật»: đọc đúng nguồn của tab đang mở. ``True``: đã có
    đề xuất mới (hay chữ chờ AI đọc) để vẽ lại trang; lỗi thì hiện câu báo ngay, trả ``False``."""
    source = S.get("plan_source") or TAB_FILE
    if source == TAB_SHEET:
        return read_sheet_link(base)
    if base is None:
        show("warning", MSG_NO_BASE)
        return False
    index, notice = fresh_index()
    try:
        if source == TAB_PASTE:
            text = S.get("plan_paste", "")
            if not text.strip():
                show("warning", MSG_EMPTY_SOURCE[TAB_PASTE])
                return False
            parsed = parse.read_paste(text, index=index)
        else:
            if upload is None:
                show("warning", MSG_EMPTY_SOURCE[TAB_FILE])
                return False
            # Kiểm cỡ bằng code trước khi lấy byte (LC-T094-33): không dựa vào maxUploadSize.
            if getattr(upload, "size", model.MAX_FILE_BYTES + 1) > model.MAX_FILE_BYTES:
                show("error", parse.FILE_TOO_BIG)
                return False
            parsed = parse.read_file(upload.getvalue(), upload.name, index=index)
        notes = [*parsed_notes(parsed), *([notice] if notice else [])]
        if not parsed.is_table:
            S.pop("plan_proposals", None)
            S.pop("plan_result", None)
            S.plan_ai = {"text": parsed.free_text, "notes": tuple(notes)}
            S.plan_base, S.plan_index = base, index
            return True
        found = propose.compare_rows(
            base.plan_rows(), parsed.rows, posts=index.items if index else (), today=today()
        )
    except (parse.PlanSourceError, model.PlanKeyError) as exc:
        show("error", exc)
        return False
    except ValueError:  # dữ liệu lạ chưa lường trước: câu cố định, không khung lỗi (T-098 đk 1)
        show("error", MSG_ODD_DATA)
        return False
    keep_proposals(found, base, index, notes)
    return True


def read_sheet_link(base: sync.SheetPlan | None) -> bool:
    """Tab «Google Sheets»: link Sheet chính thì tải lại; Sheet khác thì đọc **một lần** như file
    nguồn (tab «KeHoach» của Sheet đó). Phần mềm chỉ lấy mã Sheet trong link, không mở link."""
    link = S.get("plan_link", "")
    if not link.strip():
        show("warning", MSG_EMPTY_SOURCE[TAB_SHEET])
        return False
    try:
        sheet_id = sheet_id_from_link(link)
    except SheetsError as exc:
        show("error", exc)
        return False
    if sheet_id == settings.google_sheet_id:
        S._plan_reload = True
        S.plan_flash = ("success", MSG_RELOADED)
        return True
    if base is None:
        show("warning", MSG_NO_BASE)
        return False
    index, notice = fresh_index()
    try:
        account = load_service_account(
            settings.google_service_account_file, image_folders=settings.image_folders
        )
        with st.spinner("Đang đọc Google Sheet nguồn…"):
            values = SheetsClient(sheet_id, account).read_plan_values()
        other = sync.parse_sheet(values, fetched_at=settings.now(), index=index)
        found = propose.compare_rows(
            base.plan_rows(), other.plan_rows(), posts=index.items if index else (), today=today()
        )
    except (SheetsError, ServiceAccountError, model.PlanKeyError) as exc:
        show("error", exc)
        return False
    except ValueError:
        show("error", MSG_ODD_DATA)
        return False
    notes = [*other.warnings, *([notice] if notice else [])]
    if other.skipped:
        notes.append(f"{other.skipped} dòng bỏ qua (thiếu từ khóa chính hoặc sai khuôn).")
    keep_proposals(found, base, index, notes)
    return True


def personal_keys(rows: tuple[PlanRow, ...]) -> list[str]:
    """Mã bài của các dòng mà từ khóa có số điện thoại, email (từ khóa cũng gửi AI)."""
    return [row.key or "(chưa có mã)" for row in rows if any(model.personal_info(row.keyword))]


def ai_box() -> None:
    """Chữ tự do chờ gửi AI: báo tốn tiền, báo số điện thoại/email (A3, LC-T094-21; điều kiện 3
    Lá Chắn T-098: «Che» chỉ che được chữ dán, số trong từ khóa kế hoạch thì báo rõ dòng nào)."""
    pending = S.plan_ai
    base: sync.SheetPlan = S.plan_base
    text = pending["text"]
    with st.container(border=True):
        st.markdown("#### 🤖 Gửi AI đọc ghi chú")
        for note in pending.get("notes", ()):
            show("caption", note)
        show("info", MSG_AI_COST)
        phones, emails = model.personal_info(text)
        keys = personal_keys(base.plan_rows())
        if phones or emails:
            show(
                "warning",
                f"Chữ dán có {phones} số điện thoại, {emails} email. Thông tin khách không nên gửi "
                "cho AI: bấm «Che rồi gửi» để thay chúng bằng [đã ẩn].",
            )
        if keys:
            shown = ", ".join(keys[:10]) + (", …" if len(keys) > 10 else "")
            show(
                "warning",
                f"Từ khóa chính của dòng {shown} trong kế hoạch có số điện thoại hoặc email. Nút "
                "«Che» không che được chỗ này: sửa trên Google Sheet rồi bấm «Tải lại», hoặc bấm "
                "«Vẫn gửi».",
            )
        go, mask, anyway, cancel = st.columns(4)
        clean = not (phones or emails or keys)
        if go.button("🤖 Gửi AI đọc", key="plan-ai-go", type="primary", disabled=not clean):
            run_ai(text, allow_personal=False)
        if mask.button(
            "Che rồi gửi", key="plan-ai-mask", disabled=not (phones or emails) or bool(keys)
        ):
            run_ai(model.mask_personal_info(text), allow_personal=False)
        if anyway.button("Vẫn gửi", key="plan-ai-anyway", disabled=clean):
            run_ai(text, allow_personal=True)
        if cancel.button("Hủy", key="plan-ai-cancel"):
            S.pop("plan_ai", None)
            st.rerun()


def run_ai(text: str, *, allow_personal: bool) -> None:
    base: sync.SheetPlan = S.plan_base
    index = S.get("plan_index")
    notes = S.plan_ai.get("notes", ())
    try:
        writer = ContentWriter(AIRouter(load_ai_config(), settings), load_rules())
        with st.spinner("AI đang đọc ghi chú và đề xuất thay đổi…", show_time=True):
            found = writer.plan_changes(
                base.plan_rows(),
                text,
                today=today(),
                posts=index.items if index else (),
                allow_personal=allow_personal,
            )
    except PersonalInfoError as exc:
        show("warning", exc)
        return
    except TokenLimitError:
        show("error", MSG_AI_TOO_LONG)
        return
    except AIError as exc:
        show("error", exc)
        return
    except ValueError:
        show("error", MSG_ODD_DATA)
        return
    keep_proposals(found, base, index, notes)
    st.rerun()


# ================================================================ duyệt, áp dụng


def proposal_rows(items: tuple[propose.Proposal, ...]) -> list[dict[str, object]]:
    return [
        {
            "Dòng": number,
            "Loại": item.action.value,
            "Mã bài": item.key,
            "Từ khóa chính": item.after.keyword,
            "Thay đổi": proposal_change(item),
            "Lý do": item.reason,
            "Cảnh báo": " ".join(item.warnings),
            "Nguồn": item.source,
        }
        for number, item in enumerate(items, start=1)
    ]


def proposal_detail(item: propose.Proposal) -> None:
    """Đủ chữ một đề xuất (điều kiện (a) Lá Chắn T-100 lượt 3–4: không cắt ngắn), chữ thuần."""
    before = item.before
    rows = []
    for name in DETAIL_FIELDS:
        now = cell(name, getattr(before, name)) if before is not None else ""
        then = cell(name, getattr(item.after, name))
        if now or then:
            mark = "✏️" if before is not None and now != then else ""
            rows.append({"Cột": FIELD_LABELS[name], "Hiện tại": now, "Đề xuất": then, "Đổi": mark})
    st.dataframe(rows, hide_index=True)
    for name in LONG_FIELDS:
        value = getattr(item.after, name)
        if value:
            st.caption(f"{FIELD_LABELS[name]} (đề xuất, đủ chữ):")
            st.text(value)
    if item.reason:
        st.caption("Lý do (đủ chữ):")
        st.text(item.reason)
    for warning in item.warnings:
        show("warning", warning)


def proposals_box() -> None:
    found: propose.ProposalSet = S.plan_proposals
    items = found.items
    round_ = S.get("plan_round", 0)
    with st.container(border=True):
        st.markdown("#### Đề xuất thay đổi")
        st.caption(
            "Tick những dòng muốn áp dụng. Dòng «Bỏ» và dòng có cảnh báo (⚠️) không tick sẵn: xem "
            "kỹ trước khi tick. Phần mềm không bao giờ xóa dòng trên Google Sheet."
        )
        for note in S.get("plan_notes", ()):
            show("caption", note)
        st.dataframe(
            proposal_rows(items),
            hide_index=True,
            column_config={
                "Dòng": st.column_config.NumberColumn(width="small"),
                "Lý do": st.column_config.TextColumn(width="large"),
                "Cảnh báo": st.column_config.TextColumn(width="large"),
            },
        )
        columns = st.columns(3)
        for number, item in enumerate(items, start=1):
            columns[(number - 1) % 3].checkbox(
                pick_label(number, item), value=item.preselected, key=f"plan-pick-{round_}-{number}"
            )
        picked = st.selectbox(
            "Xem đủ một đề xuất",
            range(len(items)),
            format_func=lambda i: f"Dòng {i + 1}: {items[i].action.value} {items[i].key}",
            key=f"plan-detail-{round_}",
        )
        if picked is not None:
            proposal_detail(items[picked])
        chosen = [
            item
            for number, item in enumerate(items, start=1)
            if S.get(f"plan-pick-{round_}-{number}")
        ]
        apply_col, cancel_col, _ = st.columns([1.6, 1, 3])
        if apply_col.button(
            f"✅ Áp dụng thay đổi ({len(chosen)})",
            key="plan-apply",
            type="primary",
            width="stretch",
            disabled=not chosen,
        ):
            apply_chosen(chosen)
        if cancel_col.button("Hủy", key="plan-cancel", width="stretch"):
            for name in ("plan_proposals", "plan_base", "plan_notes"):
                S.pop(name, None)
            st.rerun()


def apply_chosen(chosen: list[propose.Proposal]) -> None:
    """«Áp dụng thay đổi»: chỉ chạy khi bấm (LC-T094-34). ``apply_proposals`` đọc lại Sheet, so
    với bản đã xem (``plan_base``), dòng đã khác thì không ghi (``Conflict``)."""
    client, problem = sheets_client()
    if client is None:
        show("error", problem or MSG_NO_GOOGLE)
        return
    try:
        with st.spinner("Đang ghi lên Google Sheet…"):
            result = sync.apply_proposals(
                client, S.plan_base, chosen, index=S.get("plan_index"), now=settings.now()
            )
    except (SheetsError, sync.SheetPlanError, model.PlanKeyError) as exc:
        show("error", f"{exc} {MSG_APPLY_FAILED}")
        return
    except ValueError:
        show("error", f"{MSG_ODD_DATA} {MSG_APPLY_FAILED}")
        return
    S.plan_result = result
    for name in ("plan_proposals", "plan_base", "plan_notes"):
        S.pop(name, None)
    S._plan_reload = True
    st.rerun()


def conflict_rows(result: sync.ApplyResult) -> list[dict[str, str]]:
    """«Trước / bây giờ / đề xuất» của từng thay đổi chưa ghi (chữ thuần)."""
    rows = []
    for conflict in result.conflicts:
        proposal = conflict.proposal
        names = conflict.fields or proposal.changes or ("keyword",)
        for name in names:
            before = proposal.before
            rows.append(
                {
                    "Mã bài": conflict.label,
                    "Cột": FIELD_LABELS.get(name, name),
                    "Trước (lúc duyệt)": cell(name, getattr(before, name)) if before else "",
                    "Bây giờ trên Sheet": (
                        cell(name, getattr(conflict.now, name)) if conflict.now else "(không thấy)"
                    ),
                    "Đề xuất": cell(name, getattr(proposal.after, name)),
                    "Vì sao chưa ghi": conflict.reason,
                }
            )
    return rows


def result_box() -> None:
    result: sync.ApplyResult = S.plan_result
    with st.container(border=True):
        st.markdown("#### Kết quả áp dụng")
        bad = result.conflicts or result.unsure or result.error or result.not_written
        show("warning" if bad else "success", result.message)
        if result.conflicts:
            st.caption("Các thay đổi chưa ghi vì dòng trên Google Sheet đã khác bản bạn đã xem:")
            st.dataframe(conflict_rows(result), hide_index=True)
            st.caption(
                "Bấm «Đọc kế hoạch và đề xuất cập nhật» lần nữa để đề xuất lại trên bản mới."
            )
        if st.button("Đóng", key="plan-result-close"):
            S.pop("plan_result", None)
            st.rerun()


# ================================================================ danh sách bài


def plan_listing(client: SheetsClient | None) -> sync.PlanListing | None:
    if not settings.google_sheet_id:
        return None
    if client is None and not plan_cache.DEFAULT_PLAN_CACHE_FILE.exists():
        # Không đọc được Google, chưa có bản lưu: như ``get_plan`` nhưng không mở kho cache (mở
        # kho là tạo file), để mở trang không ghi gì xuống đĩa.
        return sync.PlanListing(None, sync.MSG_NOT_CONNECTED)
    refresh = bool(S.pop("_plan_reload", False))
    try:
        with st.spinner("Đang đọc kế hoạch…"):
            return sync.get_plan(
                plan_store(),
                settings.google_sheet_id,
                client,
                index=cached_index(),
                refresh=refresh,
                now=settings.now(),
            )
    except (plan_cache.PlanCacheError, sync.SheetPlanError, model.PlanKeyError) as exc:
        return sync.PlanListing(None, str(exc))
    except ValueError:
        return sync.PlanListing(None, MSG_ODD_DATA)


def web_label(row: PlanRow, states: dict[int, tuple[str, str]], now: datetime) -> str:
    """Cột «Trên website» (chỉ xem): trạng thái website trả, «Lỡ lịch» khi hẹn giờ đã quá giờ."""
    if row.wp_post_id is None or row.wp_post_id not in S.get("plan_web_asked", ()):
        return ""
    found = states.get(row.wp_post_id)
    if found is None:
        return "Không thấy (đã xóa hay vào thùng rác?)"
    status, date_gmt = found
    if status == "future" and date_gmt:
        try:
            due = datetime.strptime(date_gmt, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=UTC)
        except ValueError:
            due = None
        if due is not None and now - due > LATE_AFTER:
            return "Lỡ lịch"
    return WEB_LABELS.get(status, "")


def list_rows(plan: sync.SheetPlan) -> list[dict[str, object]]:
    states = S.get("plan_web", {})
    now = settings.now()
    rows = []
    for row in plan.rows:
        line: dict[str, object] = {}
        for name in LIST_FIELDS:
            value = getattr(row.plan, name)
            line[FIELD_LABELS[name]] = value if name == "planned_date" else cell(name, value)
        if states:
            line["Trên website"] = web_label(row.plan, states, now)
        rows.append(line)
    return rows


def ask_website(plan: sync.SheetPlan) -> None:
    """«Cập nhật trạng thái từ website»: chỉ **đọc** (``post_statuses``), không ghi Sheet, không
    sửa bài. Mã bài WordPress đọc từ Sheet (chưa tin cậy) chỉ dùng để hỏi."""
    ids = sorted({row.plan.wp_post_id for row in plan.rows if row.plan.wp_post_id})
    if not ids:
        show("info", MSG_WEB_NONE)
        return
    client = wordpress_client()
    if client is None:
        show("warning", "Chưa kết nối WordPress nên chưa hỏi được website.")
        return
    try:
        with st.spinner("Đang hỏi trạng thái bài trên website…"):
            states = client.post_statuses(ids)
    except WordPressError as exc:
        show("error", exc)
        return
    S.plan_web = {post_id: (state.status, state.date_gmt) for post_id, state in states.items()}
    S.plan_web_asked = tuple(ids)


def start_writing(key: str) -> None:
    """Nút «Viết bài» (thiết kế 1.6; Chỉ Huy chọn A ngày 30/10). Chỉ đọc Sheet (``open_row``),
    không ghi Sheet, không gửi gì lên WordPress (LC-T094-35); không sửa ``write.py``, chỉ dùng khóa
    phiên của nó:

    - đã có nháp của Mã bài này (Sheet đang dùng, ``find_plan_draft``): ``_open_draft`` = mã nháp;
    - chưa có: đọc lại đúng dòng trên Sheet, dựng lại qua ``PlanRow`` (lớp kiểm của lõi), rồi
      ``_start_keyword`` = từ khóa, ``_start_plan_key`` = Mã bài (hợp đồng cho T-102: xem báo cáo
      T-101 mục «Hợp đồng ``_start_plan_key``»)."""
    try:
        key = model.parse_key(key)  # Mã bài đọc từ Sheet/cache: kiểm lại trước khi dùng
    except ValueError:
        key = ""
    if not key:
        show("error", MSG_ODD_DATA)
        return
    client, problem = sheets_client()
    if client is None:
        show("error", problem or MSG_NO_GOOGLE)
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
            row = sync.open_row(client, key, index=cached_index(), now=settings.now())
        checked = PlanRow.model_validate(row.plan.model_dump())  # dữ liệu Sheet chưa tin cậy
        plan_key = model.parse_key(checked.key)
    except (SheetsError, sync.SheetPlanError) as exc:
        show("error", exc)
        return
    except ValueError:
        show("error", MSG_ODD_DATA)
        return
    if plan_key != key:
        show("error", MSG_ODD_DATA)
        return
    S["_start_keyword"] = checked.keyword
    S["_start_plan_key"] = plan_key
    st.switch_page("views/write.py")


def write_picker(plan: sync.SheetPlan) -> None:
    rows = [row.plan for row in plan.rows if row.plan.key]
    if not rows:
        return
    by_key = {row.key: row for row in rows}
    pick_col, go_col = st.columns([4, 1], vertical_alignment="bottom")
    key = pick_col.selectbox(
        "Chọn bài để viết",
        list(by_key),
        format_func=lambda k: f"{k} · {by_key[k].keyword} · {by_key[k].status}",
        key="plan-write-pick",
    )
    row = by_key.get(key)
    blocked = ""
    if row is not None and row.kind == model.KIND_UPDATE_OLD:
        blocked = propose.WARN_UPDATE_OLD
    elif row is not None and row.status == model.STATUS_DROPPED:
        blocked = "Dòng này đã «Bỏ»."
    if go_col.button(
        "✍️ Viết bài", key="plan-write", type="primary", width="stretch", disabled=bool(blocked)
    ):
        start_writing(row.key)
    if blocked:
        show("caption", blocked)


def pending_box(client: SheetsClient | None) -> None:
    """Việc ghi trạng thái lên Sheet còn nợ (sau khi gửi WordPress, mất mạng): chỉ thử lại khi bấm,
    **chỉ** ghi Sheet, không bao giờ gửi lại WordPress (``retry_pending``, LC-T094-30)."""
    if client is None:
        return
    store = draft_store()
    if store is None:
        return
    try:
        waiting = [w for _, w in store.list_plan_writes() if w.sheet_hash == client.sheet_hash]
    except (DraftError, ValueError):
        return
    finally:
        note_recovered(store)
    if not waiting:
        return
    show("warning", f"Còn {len(waiting)} dòng kế hoạch chưa ghi được trạng thái sau khi gửi bài.")
    if st.button("Thử ghi lại", key="plan-retry"):
        try:
            with st.spinner("Đang ghi trạng thái lên Google Sheet…"):
                done = sync.retry_pending(
                    client, store, settings.google_sheet_id, now=settings.now()
                )
        except (SheetsError, DraftError, ValueError) as exc:
            show("error", exc if isinstance(exc, SheetsError | DraftError) else MSG_ODD_DATA)
            return
        for item in done:
            show("caption", item.result.message)
        S._plan_reload = True


def plan_list(listing: sync.PlanListing | None, client: SheetsClient | None) -> None:
    head, reload_col, web_col = st.columns([3, 1, 1.4], vertical_alignment="bottom")
    head.subheader("Danh sách bài theo kế hoạch")
    if listing is None:
        show("info", MSG_NO_GOOGLE)
        return
    if reload_col.button("🔄 Tải lại", key="plan-reload", width="stretch"):
        S._plan_reload = True
        S.pop("plan_web", None)
        st.rerun()
    if listing.notice:
        show("warning", listing.notice)
    plan = listing.plan
    if plan is None:
        return
    if web_col.button("🌐 Trạng thái trên website", key="plan-web", width="stretch"):
        ask_website(plan)
    when = plan.fetched_at.astimezone(model.TIMEZONE).strftime("%H:%M %d/%m/%Y")
    st.caption(
        f"{len(plan.rows)} bài · đọc từ Google Sheets lúc {when}"
        + (" (bản lưu trên máy)" if plan.from_cache else "")
    )
    for warning in plan.warnings:
        show("caption", warning)
    pending_box(client)
    if not plan.rows:
        show("info", "Kế hoạch chưa có bài nào. Đưa kế hoạch vào ở khung «Cung cấp kế hoạch».")
        return
    st.dataframe(
        list_rows(plan),
        hide_index=True,
        column_config={
            FIELD_LABELS["planned_date"]: st.column_config.DateColumn(format="DD/MM/YYYY"),
            FIELD_LABELS["status"]: st.column_config.TextColumn(width="small"),
        },
    )
    if S.get("plan_web"):
        st.caption(MSG_WEB_NOTE)
    write_picker(plan)


# ================================================================ thông tin nền


def business_box() -> None:
    """Khung «Thông tin nền cho mọi bài»: hồ sơ doanh nghiệp AI đang dùng (chỉ đọc), đọc từ
    ``config/business_profile.md`` đã bỏ ý «[CẦN XÁC NHẬN]» (``load_rules``). File của dự án."""
    st.markdown("#### 🏢 Thông tin nền cho mọi bài")
    st.caption(
        "AI dùng phần này khi viết mọi bài, để bài đúng doanh nghiệp, đúng khách. Muốn sửa: mở "
        "file config/business_profile.md bằng Notepad (lưu UTF-8), rồi tải lại trang."
    )
    try:
        profile = load_rules().business_profile
    except AIError as exc:
        show("warning", exc)
        return
    if not profile.strip():
        show("info", "Chưa có hồ sơ doanh nghiệp.")
        return
    sections = [line[3:].strip() for line in profile.splitlines() if line.startswith("## ")]
    if sections:
        st.markdown("\n".join(f"- {plain(name)}" for name in sections))
    with st.expander("Xem đủ nội dung AI đang dùng"):
        st.text(profile)


# ================================================================ trang

ui.page_header(
    "Kế hoạch",
    "Đưa kế hoạch của bạn vào — phần mềm đọc, đề xuất thay đổi, bạn duyệt rồi mới cập nhật.",
)
if "plan_flash" in S:
    show(*S.pop("plan_flash"))

client, problem = sheets_client()
if problem:
    show("error", problem)
listing = plan_listing(client)
base = listing.plan if listing is not None else None

source, brief = st.columns([3, 2], gap="large")
with source, st.container(border=True):
    st.markdown("#### 📥 Cung cấp kế hoạch")
    file_tab, paste_tab, sheet_tab = st.tabs(SOURCE_TABS, key="plan_source", on_change="rerun")
    with file_tab:
        # Giá trị trả về (không đọc qua session_state) để test giả được ``st.file_uploader``.
        chosen_file = st.file_uploader(
            "File kế hoạch (CSV, TSV, TXT, MD; tối đa 1 MB)",
            type=[suffix.lstrip(".") for suffix in parse.ALLOWED_SUFFIXES],
            key="plan_file",
        )
        st.caption(
            "Bảng có cột «Từ khóa chính» thì phần mềm tự đọc; chữ tự do thì AI đọc. File Excel, "
            "Word, PDF: mở file, chép vùng ô hoặc đoạn chữ rồi dán ở tab «Dán nội dung»."
        )
    with paste_tab:
        st.text_area(
            "Dán kế hoạch hoặc ghi chú định hướng",
            key="plan_paste",
            height=150,
            max_chars=model.MAX_PASTE_CHARS,
            placeholder=PASTE_PLACEHOLDER,
        )
    with sheet_tab:
        st.text_input(
            "Link Google Sheets",
            key="plan_link",
            placeholder="https://docs.google.com/spreadsheets/d/…",
        )
        st.caption(
            "Link Sheet kế hoạch chính: tải lại. Link Sheet khác (đã chia sẻ cho tài khoản dịch "
            "vụ, có trang tính «KeHoach»): đọc một lần rồi đề xuất ghi vào Sheet chính. Phần mềm "
            "chỉ lấy mã Sheet trong link, không mở link."
        )
    if st.button(
        "🧠 Đọc kế hoạch và đề xuất cập nhật", key="plan-read", type="primary"
    ) and read_source(base, chosen_file):
        st.rerun()

with brief, st.container(border=True):
    business_box()

if "plan_ai" in S and "plan_base" in S:
    ai_box()
if "plan_proposals" in S and "plan_base" in S:
    proposals_box()
if "plan_result" in S:
    result_box()

plan_list(listing, client)
