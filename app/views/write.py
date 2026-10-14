"""Soạn bài (DEMO): 5 bước, mỗi phần do AI viết đều có nút viết lại.

Bản demo chạy trên dữ liệu mẫu (seo_app/demo.py): «viết lại» đổi sang phiên bản khác có sẵn,
«áp dụng» sửa câu ngay trong bài. Chưa gọi AI thật.
"""

import html

import streamlit as st

from seo_app import demo, ui

S = st.session_state
SECTION_BY_ID = {sec["id"]: sec for sec in demo.SECTIONS}
REWRITE_STYLES = ["Ngắn hơn", "Thân thiện hơn", "Thêm ví dụ", "Bớt thuật ngữ", "Trang trọng hơn"]


# ------------------------------------------------------------------ trạng thái


def init_state() -> None:
    S.setdefault("step", 2)  # mở sẵn ở bước «Viết & kiểm tra» cho dễ xem
    S.setdefault("intent_v", 0)
    S.setdefault("ignored_flags", set())
    S.setdefault("title_v", 0)
    S.setdefault("desc_v", 0)
    S.setdefault("meta_title", demo.META_TITLES[0])
    S.setdefault("meta_desc", demo.META_DESCRIPTIONS[0])
    for sec in demo.SECTIONS:
        S.setdefault(f"texts-{sec['id']}", list(sec["versions"]))
        S.setdefault(f"ver-{sec['id']}", 0)
    for i, item in enumerate(demo.OUTLINE):
        S.setdefault(f"h-{i}", item["heading"])
    for slot in demo.IMAGE_SLOTS:
        S.setdefault(f"kind-{slot['id']}", slot["kind"])
        S.setdefault(f"prompt-{slot['id']}", slot["prompt"])


def current_text(sid: str) -> str:
    return S[f"texts-{sid}"][S[f"ver-{sid}"]]


def open_tone_flags() -> list[tuple[str, str, str, str]]:
    return [
        flag
        for flag in demo.TONE_FLAGS
        if flag[1] in current_text(flag[0]) and flag[1] not in S.ignored_flags
    ]


def quality_scores() -> dict[str, int]:
    natural = demo.NATURAL_MAX - demo.NATURAL_PENALTY * len(open_tone_flags())
    base = dict(demo.QUALITY_BASE)
    return {
        "Thân thiện": base["Thân thiện"],
        "Tự nhiên, không máy móc": natural,
        "Dễ đọc": base["Dễ đọc"],
        "Cụ thể, có ích": base["Cụ thể, có ích"],
        "Chuẩn SEO": base["Chuẩn SEO"],
    }


def overall_score() -> int:
    scores = quality_scores()
    return round(sum(scores.values()) / len(scores))


# -------------------------------------------------------------------- hành động


def go(step: int) -> None:
    S.step = step


def rewrite(sid: str) -> None:
    S[f"ver-{sid}"] = (S[f"ver-{sid}"] + 1) % len(S[f"texts-{sid}"])
    styles = S.get(f"style-{sid}") or []
    note = S.get(f"note-{sid}", "").strip()
    wish = ", ".join([*styles, note] if note else styles)
    heading = SECTION_BY_ID[sid]["heading"]
    st.toast(f"Đã viết lại «{heading}»" + (f" — {wish}" if wish else ""), icon="🔄")


def undo(sid: str) -> None:
    S[f"ver-{sid}"] = (S[f"ver-{sid}"] - 1) % len(S[f"texts-{sid}"])


def toggle_edit(sid: str) -> None:
    S[f"editing-{sid}"] = not S.get(f"editing-{sid}", False)


def save_manual(sid: str) -> None:
    S[f"texts-{sid}"][S[f"ver-{sid}"]] = S[f"manual-{sid}"]
    S[f"editing-{sid}"] = False
    del S[f"manual-{sid}"]
    st.toast("Đã lưu phần bạn sửa", icon="✏️")


def apply_fix(sid: str, sentence: str, replacement: str) -> None:
    texts = S[f"texts-{sid}"]
    i = S[f"ver-{sid}"]
    if replacement:
        texts[i] = texts[i].replace(sentence, replacement)
    else:
        texts[i] = texts[i].replace(sentence + " ", "").replace(sentence, "")
    st.toast("Đã sửa câu", icon="✅")


def ignore_fix(sentence: str) -> None:
    S.ignored_flags = S.ignored_flags | {sentence}


def next_intent() -> None:
    S.intent_v = 1 - S.intent_v
    st.toast("Đã phân tích lại ý định tìm kiếm", icon="🔄")


def next_heading(i: int) -> None:
    item = demo.OUTLINE[i]
    S[f"h-{i}"] = item["alt"] if S[f"h-{i}"] == item["heading"] else item["heading"]


def next_meta(kind: str) -> None:
    options = demo.META_TITLES if kind == "title" else demo.META_DESCRIPTIONS
    S[f"{kind}_v"] = (S[f"{kind}_v"] + 1) % len(options)
    S["meta_title" if kind == "title" else "meta_desc"] = options[S[f"{kind}_v"]]


def demo_toast(message: str) -> None:
    st.toast(f"Bản demo: {message}", icon="🧪")


# ------------------------------------------------------------------- các bước


def step_prepare() -> None:
    left, right = st.columns(2, gap="medium")
    with left, st.container(border=True, height="stretch"):
        head, btn = st.columns([5, 1], vertical_alignment="center")
        head.markdown("#### 🎯 Người tìm từ khóa này muốn gì?")
        btn.button("🔄", key="re-intent", on_click=next_intent, help="Phân tích lại")
        for line in demo.INTENT if S.intent_v == 0 else demo.INTENT_ALT:
            st.markdown(f"- {line}")
    with right, st.container(border=True, height="stretch"):
        head, btn = st.columns([5, 1], vertical_alignment="center")
        head.markdown("#### 🔎 Các bài đứng đầu Google còn thiếu gì?")
        btn.button(
            "🔄",
            key="re-competitors",
            help="Nghiên cứu lại",
            on_click=demo_toast,
            args=("nghiên cứu lại đối thủ",),
        )
        for title, gap in demo.COMPETITOR_GAPS:
            st.markdown(f"**{title}**  \n:gray[Thiếu: {gap}]")

    with st.container(border=True):
        st.markdown("#### ✨ Bài của mình phải có thêm")
        for angle in demo.NEW_ANGLES:
            st.markdown(f"- {angle}")

    with st.container(border=True):
        st.markdown("#### 🧱 Chất liệu thật — phần chỉ bạn có")
        st.caption(
            "AI không được bịa phần này. Ô nào để trống, bài sẽ đánh dấu chỗ cần bổ sung "
            "thay vì tự điền."
        )
        cols = st.columns(3)
        for col, (label, value) in zip(cols, demo.REAL_MATERIAL.items(), strict=True):
            col.text_area(
                label,
                value,
                height=130,
                key=f"real-{label}",
                placeholder="ví dụ: chênh lệch giá thật từ báo giá của xưởng",
            )

    st.button("Tiếp: tạo dàn ý →", type="primary", on_click=go, args=(1,))


def step_outline() -> None:
    st.caption("Duyệt dàn ý trước. AI chỉ viết toàn bài sau khi bạn bấm Duyệt.")
    for i, item in enumerate(demo.OUTLINE):
        with st.container(border=True):
            num, text, tag, rw, rm = st.columns(
                [0.5, 7, 1.6, 0.7, 0.7], vertical_alignment="center"
            )
            num.markdown(f"**{i + 1}**")
            text.text_input("Mục", key=f"h-{i}", label_visibility="collapsed")
            if item["image"]:
                tag.markdown(":violet-badge[📷 cần ảnh]")
            rw.button(
                "🔄", key=f"rw-h-{i}", on_click=next_heading, args=(i,), help="Viết lại mục này"
            )
            rm.button("🗑️", key=f"rm-h-{i}", on_click=demo_toast, args=("xóa mục",), help="Xóa mục")
    a, b, _ = st.columns([1.3, 1.6, 3])
    a.button("➕ Thêm mục", on_click=demo_toast, args=("thêm mục",), width="stretch")
    b.button("🔄 Tạo lại cả dàn ý", on_click=demo_toast, args=("tạo lại dàn ý",), width="stretch")
    st.divider()
    left, right = st.columns([1, 4])
    left.button("← Chuẩn bị", on_click=go, args=(0,))
    right.button("✅ Duyệt dàn ý, viết toàn bài →", type="primary", on_click=go, args=(2,))


def image_slot(slot: dict) -> None:
    sid = slot["id"]
    with st.container(border=True, key=f"img-{sid}"):
        st.markdown(f"**📷 Chỗ cần ảnh** — {slot['purpose']}")
        kind = st.segmented_control(
            "Loại ảnh",
            ["Ảnh thật", "Ảnh AI"],
            key=f"kind-{sid}",
            required=True,
            label_visibility="collapsed",
        )
        preview, detail = st.columns([1, 2], gap="medium")
        if kind == "Ảnh thật":
            choice = detail.selectbox(
                "Ảnh trong thư mục",
                demo.FOLDER_IMAGES,
                index=demo.FOLDER_IMAGES.index(slot["file"]) if slot["file"] else 0,
                key=f"file-{sid}",
            )
            preview.markdown(
                f'<div class="img-ph">🖼️<br>{html.escape(choice)}</div>', unsafe_allow_html=True
            )
            detail.caption("Ảnh được nén WebP, đổi tên không dấu và xóa vị trí GPS khi tải lên.")
        else:
            preview.markdown(
                '<div class="img-ph">✨<br>Ảnh AI sẽ hiện ở đây</div>', unsafe_allow_html=True
            )
            with detail:
                st.caption(
                    "Prompt tạo ảnh (tiếng Anh cho mô hình hiểu tốt hơn) — bấm biểu "
                    "tượng ở góc khung để sao chép."
                )
                st.code(S[f"prompt-{sid}"], language=None, wrap_lines=True)
                a, b, c = st.columns(3)
                a.button(
                    "🎨 Tạo ảnh",
                    key=f"gen-{sid}",
                    type="primary",
                    width="stretch",
                    on_click=demo_toast,
                    args=("tạo ảnh bằng AI",),
                )
                b.button(
                    "🔄 Prompt khác",
                    key=f"rp-{sid}",
                    width="stretch",
                    on_click=demo_toast,
                    args=("viết prompt khác",),
                )
                with c.popover("✏️ Sửa", width="stretch"):
                    st.text_area("Prompt", key=f"prompt-{sid}", height=150)
        detail.text_input(
            "Alt (mô tả ảnh cho Google và người khiếm thị)", slot["alt"], key=f"alt-{sid}"
        )


def section_card(sec: dict, flags: list[tuple[str, str, str, str]]) -> None:
    sid = sec["id"]
    versions = len(S[f"texts-{sid}"])
    with st.container(border=True, key=f"sec-{sid}"):
        title, tools = st.columns([3, 2], vertical_alignment="center")
        label = "Đoạn mở đầu" if sid == "mo-bai" else "Mục"
        title.markdown(
            f'<div class="sec-label">{label} · bản {S[f"ver-{sid}"] + 1}/{versions}</div>'
            f'<div class="sec-title">{html.escape(sec["heading"])}</div>',
            unsafe_allow_html=True,
        )
        with tools, st.container(horizontal=True, horizontal_alignment="right", gap="small"):
            with st.popover("🔄 Viết lại"):
                st.pills(
                    "Viết lại theo kiểu",
                    REWRITE_STYLES,
                    selection_mode="multi",
                    key=f"style-{sid}",
                )
                st.text_input(
                    "Hoặc ghi yêu cầu",
                    key=f"note-{sid}",
                    placeholder="ví dụ: nhắc tới khách ở Hội An",
                )
                st.button(
                    "Viết lại phần này",
                    key=f"do-rw-{sid}",
                    type="primary",
                    width="stretch",
                    on_click=rewrite,
                    args=(sid,),
                )
            st.button("✏️ Sửa", key=f"edit-{sid}", on_click=toggle_edit, args=(sid,))
            st.button("↶", key=f"undo-{sid}", on_click=undo, args=(sid,), help="Về bản trước")

        if S.get(f"editing-{sid}"):
            st.text_area(
                "Sửa trực tiếp",
                current_text(sid),
                height=180,
                key=f"manual-{sid}",
                label_visibility="collapsed",
            )
            st.button("Lưu", key=f"save-{sid}", on_click=save_manual, args=(sid,))
        else:
            tone = [f[1] for f in flags if f[0] == sid]
            missing = ["[số liệu của xưởng]"] if sid == demo.MISSING_DATA[0] else []
            st.markdown(ui.highlight(current_text(sid), tone, missing), unsafe_allow_html=True)

        for slot in demo.IMAGE_SLOTS:
            if slot["section"] == sid:
                image_slot(slot)


def quality_panel(flags: list[tuple[str, str, str, str]]) -> None:
    with st.container(border=True):
        st.markdown("#### 🔍 Văn phong")
        st.caption("AI đọc lại cả bài như một người đọc thật: có thân thiện, tự nhiên không?")
        st.markdown(ui.score_panel(overall_score(), quality_scores()), unsafe_allow_html=True)
        st.button(
            "Kiểm tra lại toàn bài",
            width="stretch",
            on_click=demo_toast,
            args=("kiểm tra lại văn phong",),
        )

    st.markdown(f"**Cần xem lại ({len(flags) + 1})**")
    for sid, sentence, reason, replacement in flags:
        with st.container(border=True):
            st.markdown(f":orange-badge[Nghe máy móc] :gray[{SECTION_BY_ID[sid]['heading']}]")
            st.markdown(f"> {sentence}")
            st.caption(reason)
            st.markdown(f"**Gợi ý:** {replacement}" if replacement else "**Gợi ý:** bỏ câu này.")
            a, b = st.columns(2)
            a.button(
                "Áp dụng",
                key=f"fix-{sentence[:20]}",
                type="primary",
                width="stretch",
                on_click=apply_fix,
                args=(sid, sentence, replacement),
            )
            b.button(
                "Bỏ qua",
                key=f"skip-{sentence[:20]}",
                width="stretch",
                on_click=ignore_fix,
                args=(sentence,),
            )
    with st.container(border=True):
        sid, note = demo.MISSING_DATA
        st.markdown(f":red-badge[Thiếu số liệu] :gray[{SECTION_BY_ID[sid]['heading']}]")
        st.caption(note)
    if not flags:
        st.success("Không còn câu nào nghe máy móc.")


def step_write() -> None:
    flags = open_tone_flags()
    article, panel = st.columns([2.3, 1], gap="large")
    with article:
        for sec in demo.SECTIONS:
            section_card(sec, flags)
    with panel:
        quality_panel(flags)
    st.divider()
    left, right = st.columns([1, 4])
    left.button("← Dàn ý", on_click=go, args=(1,))
    right.button("Tiếp: SEO →", type="primary", on_click=go, args=(3,))


def count_badge(n: int, low: int, high: int) -> str:
    color = "green" if low <= n <= high else "orange"
    return f":{color}-badge[{n} ký tự · nên {low}–{high}]"


def step_seo() -> None:
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
        st.text_input("Đường dẫn (slug)", demo.SLUG)
    with right:
        st.markdown("**Xem trước trên Google**")
        st.markdown(
            ui.serp_preview(S.meta_title, f"prometal.vn › {demo.SLUG}", S.meta_desc),
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
    flags = open_tone_flags()
    score = overall_score()
    ready_images = sum(1 for s in demo.IMAGE_SLOTS if S[f"kind-{s['id']}"] == "Ảnh thật")
    left, right = st.columns([1, 1], gap="large")
    with left, st.container(border=True):
        st.markdown("#### Kiểm tra trước khi gửi")
        checks = [
            (score >= 80, f"Điểm văn phong {score}/100"),
            (not flags, f"Câu nghe máy móc còn lại: {len(flags)}"),
            (False, "Còn 1 chỗ thiếu số liệu thật (mục Chi phí)"),
            (
                ready_images == len(demo.IMAGE_SLOTS),
                f"Ảnh: {ready_images}/{len(demo.IMAGE_SLOTS)} đã có (ảnh AI chưa tạo)",
            ),
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
ui.page_header("Soạn bài", f"Từ khóa: {demo.KEYWORD}", demo=True)

st.segmented_control(
    "Bước",
    list(range(len(demo.STEPS))),
    key="step",
    required=True,
    format_func=lambda i: f"{i + 1} · {demo.STEPS[i]}",
    label_visibility="collapsed",
    width="stretch",
)

[step_prepare, step_outline, step_write, step_seo, step_publish][S.step]()
