"""Soạn bài: 5 bước. Bước 1–3 do AI làm thật; bước 4 (SEO) và 5 (Xuất bản) còn là bản demo.

Bài đang soạn nằm trong session_state:
- ``research``: kết quả nghiên cứu từ khóa (``Research``)
- dàn ý: ``outline_ids`` + ``h-<id>`` (tiêu đề mục), ``pts-<id>`` (ý chính), ``img-<id>`` (ảnh)
- bài viết: ``part_ids`` + ``heading-<id>``, ``texts-<id>`` (các phiên bản), ``ver-<id>``
- ``review``: lần rà soát gần nhất (``Review``)
"""

import html
import tomllib

import streamlit as st

from seo_app import demo, ui
from seo_app.ai import AIError, AIRouter, load_ai_config
from seo_app.config import load_settings
from seo_app.content import ContentWriter, Outline, OutlineItem, Research, Section, load_rules
from seo_app.content.models import SCORE_LABELS
from seo_app.content.rules import find_missing
from seo_app.content.workflow import apply_flag
from seo_app.sanitize import escape_link_syntax, unescape_link_syntax
from seo_app.text import markdown_link, slugify

S = st.session_state
REWRITE_STYLES = ["Ngắn hơn", "Thân thiện hơn", "Thêm ví dụ", "Bớt thuật ngữ", "Trang trọng hơn"]
MATERIAL = {
    "Kinh nghiệm của xưởng": "ví dụ: khách gần biển làm cổng 201, 1–2 năm đã gỉ mối hàn",
    "Số liệu của bạn": "ví dụ: chênh lệch giá thật từ báo giá của xưởng",
    "Câu hỏi khách hay hỏi": "ví dụ: Inox 304 có bị gỉ không? Làm sao biết thợ dùng đúng 304?",
}
COMPOSE_PREFIXES = ("h-", "pts-", "img-", "heading-", "texts-", "ver-", "editing-", "manual-")


# ------------------------------------------------------------------ trạng thái


def init_state() -> None:
    if "_start_keyword" in S:  # bấm «Viết bài mới» ở trang Bài viết
        reset_compose()
        S.keyword = S.pop("_start_keyword")
    S.setdefault("step", 0)
    S.setdefault("keyword", "")
    S.setdefault("research", None)
    S.setdefault("research_keyword", "")
    S.setdefault("outline_title", "")
    S.setdefault("outline_ids", [])
    S.setdefault("next_id", 0)
    S.setdefault("article_title", "")
    S.setdefault("part_ids", [])
    S.setdefault("review", None)
    S.setdefault("auto_fixed", 0)
    S.setdefault("ignored_flags", set())
    S.setdefault("title_v", 0)
    S.setdefault("desc_v", 0)
    S.setdefault("meta_title", demo.META_TITLES[0])
    S.setdefault("meta_desc", demo.META_DESCRIPTIONS[0])
    if "_goto" in S:  # đổi bước sau khi AI chạy xong (phải đặt trước khi vẽ thanh bước)
        S.step = S.pop("_goto")


def reset_compose() -> None:
    for key in list(S.keys()):
        if key.startswith(COMPOSE_PREFIXES) or key in {
            "research",
            "research_keyword",
            "outline_title",
            "outline_ids",
            "article_title",
            "part_ids",
            "review",
            "auto_fixed",
            "ignored_flags",
        }:
            del S[key]
    S.step = 0


def new_id() -> int:
    S.next_id += 1
    return S.next_id


def keyword() -> str:
    return S.keyword.strip()


def material() -> dict[str, str]:
    return {label: S.get(f"real-{label}", "") for label in MATERIAL}


def current_text(pid: int) -> str:
    return S[f"texts-{pid}"][S[f"ver-{pid}"]]


def current_parts() -> list[Section]:
    return [Section(heading=S[f"heading-{pid}"], body=current_text(pid)) for pid in S.part_ids]


def current_outline() -> Outline:
    """Dàn ý theo các ô người dùng đã sửa; escape lại cú pháp link (ô sửa hiện bản chưa escape)."""
    items = [
        OutlineItem(
            heading=escape_link_syntax(S[f"h-{uid}"].strip()),
            points=S[f"pts-{uid}"],
            image=S[f"img-{uid}"],
        )
        for uid in S.outline_ids
        if S[f"h-{uid}"].strip()
    ]
    title = escape_link_syntax(S.outline_title.strip()) or keyword()
    return Outline(title=title, items=items)


def set_outline(outline: Outline) -> None:
    # Ô sửa hiện chữ thật, không có dấu "\" do escape_link_syntax thêm; current_outline escape lại.
    S.outline_title = unescape_link_syntax(outline.title)
    S.outline_ids = []
    for item in outline.items:
        uid = new_id()
        S[f"h-{uid}"] = unescape_link_syntax(item.heading)
        S[f"pts-{uid}"] = list(item.points)
        S[f"img-{uid}"] = item.image.strip()
        S.outline_ids.append(uid)


def set_article(title: str, parts: list[Section], outline: Outline) -> None:
    images = {item.heading: item.image.strip() for item in outline.items}
    S.article_title = title
    S.part_ids = []
    for part in parts:
        pid = new_id()
        S[f"heading-{pid}"] = part.heading
        S[f"texts-{pid}"] = [part.body]
        S[f"ver-{pid}"] = 0
        S[f"img-{pid}"] = images.get(part.heading, "")
        S.part_ids.append(pid)


def open_flags() -> list[tuple[int, str, str, str]]:
    """Gợi ý sửa còn hiệu lực: (id phần, câu, lý do, câu thay thế)."""
    if S.review is None:
        return []
    result = []
    for flag in S.review.flags:
        if flag.section >= len(S.part_ids) or flag.sentence in S.ignored_flags:
            continue
        pid = S.part_ids[flag.section]
        if flag.sentence in current_text(pid):
            result.append((pid, flag.sentence, flag.reason, flag.replacement))
    return result


def missing_spots() -> list[tuple[int, str]]:
    return [(pid, spot) for pid in S.part_ids for spot in find_missing(current_text(pid))]


def overall_score() -> int | None:
    if S.review is None:
        return None
    scores = S.review.scores.model_dump().values()
    return round(sum(scores) / len(scores))


# -------------------------------------------------------------------------- AI


def build_writer() -> ContentWriter:
    return ContentWriter(AIRouter(load_ai_config(), load_settings()), load_rules())


def ai_call(spinner: str, fn, *args, **kwargs):
    """Chạy một bước AI, hiện vòng quay; lỗi thì báo bằng tiếng Việt và trả về None."""
    try:
        with st.spinner(spinner, show_time=True):
            return fn(*args, **kwargs)
    except AIError as exc:
        st.error(str(exc))
        return None


def goto(step: int) -> None:
    S._goto = step
    st.rerun()


# -------------------------------------------------------------------- hành động


def go(step: int) -> None:
    S.step = step


def undo(pid: int) -> None:
    S[f"ver-{pid}"] = max(0, S[f"ver-{pid}"] - 1)


def redo(pid: int) -> None:
    S[f"ver-{pid}"] = min(len(S[f"texts-{pid}"]) - 1, S[f"ver-{pid}"] + 1)


def toggle_edit(pid: int) -> None:
    S[f"editing-{pid}"] = not S.get(f"editing-{pid}", False)


def save_manual(pid: int) -> None:
    # Ô sửa hiện bản chưa escape; lưu thì escape lại để chữ không thành link Markdown.
    S[f"texts-{pid}"][S[f"ver-{pid}"]] = escape_link_syntax(S[f"manual-{pid}"])
    S[f"editing-{pid}"] = False
    del S[f"manual-{pid}"]
    st.toast("Đã lưu phần bạn sửa", icon="✏️")


def apply_fix(pid: int, sentence: str, replacement: str) -> None:
    texts = S[f"texts-{pid}"]
    i = S[f"ver-{pid}"]
    texts[i] = apply_flag(texts[i], sentence, replacement)
    st.toast("Đã sửa câu", icon="✅")


def ignore_fix(sentence: str) -> None:
    S.ignored_flags = S.ignored_flags | {sentence}


def add_item() -> None:
    uid = new_id()
    S[f"h-{uid}"] = ""
    S[f"pts-{uid}"] = []
    S[f"img-{uid}"] = ""
    S.outline_ids = [*S.outline_ids, uid]


def remove_item(uid: int) -> None:
    S.outline_ids = [i for i in S.outline_ids if i != uid]


def move_item(uid: int, delta: int) -> None:
    ids = list(S.outline_ids)
    i = ids.index(uid)
    j = i + delta
    if 0 <= j < len(ids):
        ids[i], ids[j] = ids[j], ids[i]
        S.outline_ids = ids


def next_meta(kind: str) -> None:
    options = demo.META_TITLES if kind == "title" else demo.META_DESCRIPTIONS
    S[f"{kind}_v"] = (S[f"{kind}_v"] + 1) % len(options)
    S["meta_title" if kind == "title" else "meta_desc"] = options[S[f"{kind}_v"]]


def demo_toast(message: str) -> None:
    st.toast(f"Bản demo: {message}", icon="🧪")


def demo_note(text: str) -> None:
    st.caption(f":orange-badge[🧪 Bản demo] {text}")


# ------------------------------------------------------------------- các bước


def run_outline(writer: ContentWriter) -> None:
    outline = ai_call("AI đang lập dàn ý…", writer.outline, keyword(), S.research, material())
    if outline is not None:
        set_outline(outline)
        goto(1)


def step_prepare(writer: ContentWriter | None) -> None:
    kw_col, btn_col = st.columns([4, 1.4], vertical_alignment="bottom")
    kw_col.text_input("Từ khóa chính", key="keyword", placeholder="ví dụ: so sánh inox 201 và 304")
    research: Research | None = S.research
    label = "🔄 Phân tích lại" if research else "🔎 Phân tích từ khóa"
    if btn_col.button(
        label, type="primary", width="stretch", disabled=writer is None or not keyword()
    ):
        result = ai_call(
            "AI đang tìm và đọc các bài đứng đầu Google… (thường mất 1–2 phút)",
            writer.research,
            keyword(),
        )
        if result is not None:
            S.research = result
            S.research_keyword = keyword()
            st.rerun()

    if research is None:
        st.info(
            "Nhập từ khóa rồi bấm **Phân tích**: AI xác định người tìm muốn gì và đọc các "
            "bài đứng đầu Google để tìm chỗ họ còn thiếu."
        )
    else:
        if S.research_keyword != keyword():
            st.warning(
                f"Kết quả dưới đây là của từ khóa «{S.research_keyword}». "
                "Bấm Phân tích lại cho từ khóa mới."
            )
        left, right = st.columns(2, gap="medium")
        with left, st.container(border=True, height="stretch"):
            st.markdown("#### 🎯 Người tìm từ khóa này muốn gì?")
            for line in research.intent:
                st.markdown(f"- {line}")
            st.markdown(f"**Dạng bài hợp nhất:** {research.article_type}")
        with right, st.container(border=True, height="stretch"):
            st.markdown("#### 🔎 Các bài đứng đầu Google còn thiếu gì?")
            for c in research.competitors:
                title = markdown_link(c.title, c.url)
                st.markdown(f"**{title}**  \n:gray[Đã có: {c.covers}]  \n:gray[Thiếu: {c.missing}]")
        with st.container(border=True):
            st.markdown("#### ✨ Bài của mình phải có thêm")
            for angle in research.new_angles:
                st.markdown(f"- {angle}")
            if research.questions:
                st.markdown("**Người đọc hay hỏi thêm:** " + " · ".join(research.questions))

    with st.container(border=True):
        st.markdown("#### 🧱 Chất liệu thật — phần chỉ bạn có")
        st.caption(
            "AI không được bịa phần này. Ô nào để trống, bài sẽ đánh dấu chỗ cần bổ sung "
            "thay vì tự điền."
        )
        cols = st.columns(len(MATERIAL))
        for col, (label, hint) in zip(cols, MATERIAL.items(), strict=True):
            col.text_area(label, height=130, key=f"real-{label}", placeholder=hint)

    has_outline = bool(S.outline_ids)
    if st.button(
        "Tiếp: dàn ý →" if has_outline else "Tiếp: tạo dàn ý →",
        type="primary",
        disabled=writer is None or research is None,
    ):
        if has_outline:
            goto(1)
        run_outline(writer)


def step_outline(writer: ContentWriter | None) -> None:
    if S.research is None:
        st.info("Làm bước **Chuẩn bị** trước: nhập từ khóa và bấm Phân tích.")
        return
    if not S.outline_ids:
        st.info("Chưa có dàn ý.")
        if st.button("🧠 Tạo dàn ý", type="primary", disabled=writer is None):
            run_outline(writer)
        return

    st.caption("Duyệt dàn ý trước. AI chỉ viết toàn bài sau khi bạn bấm Duyệt.")
    st.text_input("Tiêu đề bài (H1)", key="outline_title")
    for n, uid in enumerate(S.outline_ids, start=1):
        with st.container(border=True):
            num, text, tag, up, down, rm = st.columns(
                [0.5, 7, 1.6, 0.6, 0.6, 0.6], vertical_alignment="center"
            )
            num.markdown(f"**{n}**")
            text.text_input("Mục", key=f"h-{uid}", label_visibility="collapsed")
            if S[f"img-{uid}"]:
                tag.markdown(":violet-badge[📷 cần ảnh]", help=S[f"img-{uid}"])
            up.button("↑", key=f"up-{uid}", on_click=move_item, args=(uid, -1), help="Lên")
            down.button("↓", key=f"dn-{uid}", on_click=move_item, args=(uid, 1), help="Xuống")
            rm.button("🗑️", key=f"rm-{uid}", on_click=remove_item, args=(uid,), help="Xóa mục")
            if S[f"pts-{uid}"]:
                st.caption(" · ".join(S[f"pts-{uid}"]))
    a, b, _ = st.columns([1.3, 1.6, 3])
    a.button("➕ Thêm mục", on_click=add_item, width="stretch")
    if b.button("🔄 Tạo lại cả dàn ý", width="stretch", disabled=writer is None):
        run_outline(writer)
    st.divider()
    if S.part_ids:
        st.caption("⚠️ Đã có bài viết. Duyệt lại dàn ý sẽ viết lại toàn bài, thay bài hiện tại.")
    left, right = st.columns([1, 4])
    left.button("← Chuẩn bị", on_click=go, args=(0,))
    if right.button("✅ Duyệt dàn ý, viết toàn bài →", type="primary", disabled=writer is None):
        outline = current_outline()
        if not outline.items:
            st.error("Dàn ý đang trống.")
            return
        result = ai_call(
            "AI đang viết toàn bài rồi tự rà soát theo checklist… (thường mất 2–4 phút)",
            writer.write_and_review,
            keyword(),
            S.research,
            material(),
            outline,
        )
        if result is not None:
            title, parts, review, fixed = result
            set_article(title, parts, outline)
            S.review = review
            S.auto_fixed = fixed
            S.ignored_flags = set()
            goto(2)


def image_slot(pid: int) -> None:
    with st.container(border=True):
        st.markdown(f"**📷 Chỗ cần ảnh** — {S[f'img-{pid}']}")
        demo_note("chọn ảnh thật từ thư mục hoặc tạo ảnh AI sẽ làm ở Giai đoạn 3.")


def section_card(writer: ContentWriter | None, index: int, pid: int, tone: list[str]) -> None:
    versions = len(S[f"texts-{pid}"])
    with st.container(border=True, key=f"sec-{pid}"):
        title, tools = st.columns([3, 2], vertical_alignment="center")
        label = "Đoạn mở đầu" if index == 0 else "Mục"
        title.markdown(
            f'<div class="sec-label">{label} · bản {S[f"ver-{pid}"] + 1}/{versions}</div>'
            f'<div class="sec-title">{html.escape(S[f"heading-{pid}"])}</div>',
            unsafe_allow_html=True,
        )
        with tools, st.container(horizontal=True, horizontal_alignment="right", gap="small"):
            with st.popover("🔄 Viết lại", disabled=writer is None):
                styles = st.pills(
                    "Viết lại theo kiểu",
                    REWRITE_STYLES,
                    selection_mode="multi",
                    key=f"style-{pid}",
                )
                note = st.text_input(
                    "Hoặc ghi yêu cầu",
                    key=f"note-{pid}",
                    placeholder="ví dụ: nhắc tới khách ở Hội An",
                )
                if st.button(
                    "Viết lại phần này", key=f"do-rw-{pid}", type="primary", width="stretch"
                ):
                    body = ai_call(
                        "AI đang viết lại…",
                        writer.rewrite_section,
                        keyword(),
                        S.article_title,
                        current_parts(),
                        index,
                        styles or [],
                        note or "",
                    )
                    if body:
                        S[f"texts-{pid}"] = [*S[f"texts-{pid}"], body]
                        S[f"ver-{pid}"] = len(S[f"texts-{pid}"]) - 1
                        st.rerun()
            st.button("✏️ Sửa", key=f"edit-{pid}", on_click=toggle_edit, args=(pid,))
            st.button(
                "↶",
                key=f"undo-{pid}",
                on_click=undo,
                args=(pid,),
                help="Về bản trước",
                disabled=S[f"ver-{pid}"] == 0,
            )
            if versions > 1:
                st.button(
                    "↷",
                    key=f"redo-{pid}",
                    on_click=redo,
                    args=(pid,),
                    help="Tới bản sau",
                    disabled=S[f"ver-{pid}"] == versions - 1,
                )

        if S.get(f"editing-{pid}"):
            st.text_area(
                "Sửa trực tiếp",
                unescape_link_syntax(current_text(pid)),
                height=220,
                key=f"manual-{pid}",
                label_visibility="collapsed",
            )
            st.button("Lưu", key=f"save-{pid}", on_click=save_manual, args=(pid,))
        else:
            text = current_text(pid)
            st.markdown(ui.highlight(text, tone, find_missing(text)), unsafe_allow_html=True)

        if S.get(f"img-{pid}"):
            image_slot(pid)


def quality_panel(writer: ContentWriter | None, flags: list[tuple[int, str, str, str]]) -> None:
    with st.container(border=True):
        st.markdown("#### 🔍 Văn phong")
        st.caption("AI đọc lại cả bài như một người đọc thật, theo checklist trong config/.")
        if S.review is not None:
            scores = {SCORE_LABELS[k]: v for k, v in S.review.scores.model_dump().items()}
            st.markdown(ui.score_panel(overall_score(), scores), unsafe_allow_html=True)
            if S.review.summary:
                st.caption(S.review.summary)
        if st.button("Kiểm tra lại toàn bài", width="stretch", disabled=writer is None):
            review = ai_call(
                "AI đang đọc lại toàn bài…",
                writer.review,
                keyword(),
                S.article_title,
                current_parts(),
            )
            if review is not None:
                S.review = review
                S.ignored_flags = set()
                st.rerun()
        if S.auto_fixed:
            st.caption(f"✅ AI đã tự sửa {S.auto_fixed} câu trước khi đưa bạn xem.")

    missing = missing_spots()
    st.markdown(f"**Cần xem lại ({len(flags) + len(missing)})**")
    for pid, sentence, reason, replacement in flags:
        with st.container(border=True):
            st.markdown(f":orange-badge[Nghe máy móc] :gray[{S[f'heading-{pid}']}]")
            st.markdown(f"> {sentence}")
            st.caption(reason)
            st.markdown(f"**Gợi ý:** {replacement}" if replacement else "**Gợi ý:** bỏ câu này.")
            a, b = st.columns(2)
            key = f"{pid}-{abs(hash(sentence))}"
            a.button(
                "Áp dụng",
                key=f"fix-{key}",
                type="primary",
                width="stretch",
                on_click=apply_fix,
                args=(pid, sentence, replacement),
            )
            b.button(
                "Bỏ qua",
                key=f"skip-{key}",
                width="stretch",
                on_click=ignore_fix,
                args=(sentence,),
            )
    for pid, spot in missing:
        with st.container(border=True):
            st.markdown(f":red-badge[Thiếu số liệu] :gray[{S[f'heading-{pid}']}]")
            st.caption(f"{spot} — điền số liệu thật bằng nút ✏️ Sửa. AI không tự điền.")
    if not flags and not missing:
        st.success("Không còn câu nào cần xem lại.")


def step_write(writer: ContentWriter | None) -> None:
    if not S.part_ids:
        st.info("Chưa có bài. Duyệt dàn ý ở bước **Dàn ý** để AI viết toàn bài.")
        return
    flags = open_flags()
    st.markdown(f"## {html.escape(S.article_title)}", unsafe_allow_html=True)
    article, panel = st.columns([2.3, 1], gap="large")
    with article:
        for index, pid in enumerate(S.part_ids):
            tone = [f[1] for f in flags if f[0] == pid]
            section_card(writer, index, pid, tone)
    with panel:
        quality_panel(writer, flags)
    st.divider()
    left, right = st.columns([1, 4])
    left.button("← Dàn ý", on_click=go, args=(1,))
    right.button("Tiếp: SEO →", type="primary", on_click=go, args=(3,))


def count_badge(n: int, low: int, high: int) -> str:
    color = "green" if low <= n <= high else "orange"
    return f":{color}-badge[{n} ký tự · nên {low}–{high}]"


def step_seo() -> None:
    demo_note("meta, schema và liên kết nội bộ thật sẽ làm ở Giai đoạn 4.")
    slug = slugify(keyword()) or demo.SLUG
    left, right = st.columns([3, 2], gap="large")
    with left:
        a, b = st.columns([6, 1], vertical_alignment="bottom")
        a.text_input("Meta title", key="meta_title")
        b.button("🔄", key="re-title", on_click=next_meta, args=("title",), help="Gợi ý khác")
        st.markdown(count_badge(len(S.meta_title), 50, 60))
        a, b = st.columns([6, 1], vertical_alignment="bottom")
        a.text_area("Meta description", key="meta_desc", height=90)
        b.button("🔄", key="re-desc", on_click=next_meta, args=("desc",), help="Gợi ý khác")
        st.markdown(count_badge(len(S.meta_desc), 120, 155))
        st.text_input("Đường dẫn (slug)", slug)
    with right:
        st.markdown("**Xem trước trên Google**")
        st.markdown(
            ui.serp_preview(S.meta_title, f"suachuacuasat.com › {slug}", S.meta_desc),
            unsafe_allow_html=True,
        )
    st.markdown("**Liên kết nội bộ** — gợi ý từ các bài đã có trên website")
    st.data_editor(
        demo.INTERNAL_LINKS, hide_index=True, disabled=["Cụm từ trong bài", "Trỏ tới bài"]
    )
    with st.expander("Schema (dữ liệu có cấu trúc cho Google)"):
        st.code(demo.SCHEMA, language="json")
    st.divider()
    a, b = st.columns([1, 4])
    a.button("← Viết & kiểm tra", on_click=go, args=(2,))
    b.button("Tiếp: xuất bản →", type="primary", on_click=go, args=(4,))


def step_publish() -> None:
    demo_note("gửi bài thật sang WordPress từ trang này sẽ nối ở Giai đoạn 5.")
    flags = open_flags()
    missing = missing_spots()
    score = overall_score()
    images = sum(1 for pid in S.part_ids if S.get(f"img-{pid}"))
    left, right = st.columns([1, 1], gap="large")
    with left, st.container(border=True):
        st.markdown("#### Kiểm tra trước khi gửi")
        checks = [
            (bool(S.part_ids), "Đã có bài viết" if S.part_ids else "Chưa có bài viết"),
            (
                score is not None and score >= 80,
                f"Điểm văn phong {score}/100" if score is not None else "Chưa chấm văn phong",
            ),
            (not flags, f"Câu cần xem lại còn: {len(flags)}"),
            (not missing, f"Chỗ thiếu số liệu thật còn: {len(missing)}"),
            (images == 0, f"Chỗ cần ảnh: {images} (chọn ảnh ở Giai đoạn 3)"),
            (True, "Meta title, description, slug"),
        ]
        for ok, text in checks:
            st.markdown(f"{'✅' if ok else '⚠️'} {text}")
    with right, st.container(border=True):
        st.markdown("#### Gửi sang WordPress")
        mode = st.segmented_control(
            "Hình thức",
            ["Nháp", "Hẹn giờ", "Đăng ngay"],
            default="Nháp",
            required=True,
        )
        if mode == "Hẹn giờ":
            a, b = st.columns(2)
            a.date_input("Ngày", format="DD/MM/YYYY")
            b.time_input("Giờ")
            st.caption("WordPress tự đăng đúng giờ — không cần mở app lúc đó.")
        st.pills("Chuyên mục", demo.CATEGORIES, selection_mode="multi", default=["Inox"])
        allowed = True
        if mode == "Đăng ngay":
            st.warning("Bài sẽ hiện công khai ngay trên website.")
            allowed = st.checkbox("Tôi đã đọc lại bài và đồng ý đăng ngay")
        if st.button(
            "📤 Gửi sang WordPress", type="primary", disabled=not allowed, width="stretch"
        ):
            demo_toast(f"gửi bài ({mode.lower()}) sang WordPress")
    st.button("← SEO", on_click=go, args=(3,))


# ----------------------------------------------------------------------- trang

init_state()
ui.page_header("Soạn bài", f"Từ khóa: {keyword()}" if keyword() else "Bắt đầu bằng một từ khóa")

writer: ContentWriter | None = None
try:
    writer = build_writer()
except AIError as exc:
    st.warning(f"{exc} Các bước dùng AI tạm khóa cho tới khi sửa xong.")
except tomllib.TOMLDecodeError as exc:
    st.warning(f"File config/content.toml viết sai cú pháp: {exc}")

st.segmented_control(
    "Bước",
    list(range(len(demo.STEPS))),
    key="step",
    required=True,
    format_func=lambda i: f"{i + 1} · {demo.STEPS[i]}",
    label_visibility="collapsed",
    width="stretch",
)

if S.step == 0:
    step_prepare(writer)
elif S.step == 1:
    step_outline(writer)
elif S.step == 2:
    step_write(writer)
elif S.step == 3:
    step_seo()
else:
    step_publish()
