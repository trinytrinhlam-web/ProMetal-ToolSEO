"""Soạn bài: 5 bước. Bước 1–3 do AI làm thật; chỗ cần ảnh (Giai đoạn 3, T-056) là thật; bước 4
(SEO) còn là bản demo; bước 5 (Xuất bản): «Nháp» gửi thật lên WordPress kèm ảnh, «Hẹn giờ» và
«Đăng ngay» còn là bản demo (Giai đoạn 5).

Bài đang soạn nằm trong session_state:
- ``research``: kết quả nghiên cứu từ khóa (``Research``)
- dàn ý: ``outline_ids`` + ``h-<id>`` (tiêu đề mục), ``pts-<id>`` (ý chính), ``img-<id>`` (ảnh)
- bài viết: ``part_ids`` + ``heading-<id>``, ``texts-<id>`` (các phiên bản), ``ver-<id>``
- ``review``: lần rà soát gần nhất (``Review``)
- ``draft_id``: mã nháp đang mở; trang tự lưu nháp vào ``seo_app.storage`` sau mỗi lần chạy
- chỗ cần ảnh của phần ``<id>``: ``kind-<id>`` (Ảnh thật / Ảnh AI), ``pick-<id>`` (ảnh đã chọn,
  ``CheckedImage`` đã kiểm trên máy), ``alt-<id>``, ``cap-<id>`` (chú thích), ``altok-<id>`` (đã
  duyệt alt), ``prompt-<id>`` (prompt ảnh AI), ``imgmsg-<id>`` (câu báo riêng của chỗ đó)

Ảnh (điều kiện Lá Chắn T-048 → T-076, xem ``docs/team/tickets/T-056-giao-dien-cho-can-anh.md``):
- Tên file, tên thư mục lấy từ máy là dữ liệu chưa tin cậy: hiện qua ``shown_name`` (cô lập hướng
  chữ, ký tự vô hình hiện thành «�») và ``escape_markdown``; không bao giờ qua
  ``unsafe_allow_html``. Không hiện đường dẫn tuyệt đối: chỉ tên thư mục gốc
  (``ImageLibrary.roots()``) và đường dẫn tương đối. Không dùng ``ImageLibrary._folders``.
- Chỉ quét thư mục khi người dùng mở thư mục hay bấm quét lại; quét trong luồng riêng; kết quả giữ
  trong phiên (``_scans``). Đi từ thư mục gốc xuống qua ``SubFolder.rel_path`` của chính các lần
  quét (LC-T055-1).
- ``st.image`` chỉ nhận byte của ``PreviewCache.get`` (ảnh xem trước JPEG do app tạo; LC-T058-2,
  Lá Chắn T-049).
- Thẻ lấy bằng ``ImageTagStore.resolve``/``resolve_many`` (theo trang, ≤ 200 ảnh); nguồn ảnh theo
  hướng an toàn: thư mục gốc có dấu hiệu AI, tên thư mục/tên file có dấu hiệu AI, thẻ sửa tay hay
  nháp nói AI thì là ảnh AI. Nút «Đây là ảnh AI» lưu thẻ sửa tay; lưu hỏng thì trong phiên vẫn coi
  là ảnh AI (``_ai_marked``).
- AI chỉ viết alt khi người dùng bấm, cho đúng ảnh đã chọn, với byte của ``make_ai_image``.
- Ảnh chỉ lên WordPress khi bấm «Gửi nháp»; ngay trước đó kiểm lại ảnh (``check_chosen_image``)
  và so băm SHA-256 byte sắp tải với bản đã xem và duyệt (``altsha-<id>``, T-086).

Gửi nháp (T-086): trạng thái gửi ghi vào kho nháp (``SendState``) trước khi gửi và ngay khi có kết
quả, nên mở bài khác rồi mở lại, tải lại trang vẫn khóa nút. Trong phiên: ``_wp_sending`` (đối
tượng giữ kết quả, sửa tại chỗ), ``_wp_result``, ``_wp_sent``, ``_wp_maybe_draft``. Mọi lần
đọc/ghi ``st.session_state`` và mọi lệnh ``st.*`` là chỗ Streamlit có thể dừng lần chạy (người dùng
bấm gì đó): ghi khóa trước, bỏ dấu sau (LC-T056-1). Lần chạy mới bắt đầu ngay, song song với lần
đang gửi (``runner.fastReruns``): ``finish_send`` đợi lần gửi xong rồi mới đọc kết quả.
"""

import dataclasses
import hashlib
import html
import re
import threading
import tomllib
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlsplit

import streamlit as st

from seo_app import demo, ui
from seo_app.ai import AIError, AIRouter, load_ai_config
from seo_app.ai.base import ImageInput
from seo_app.config import load_settings
from seo_app.content import ContentWriter, Outline, OutlineItem, Research, Section, load_rules
from seo_app.content.models import SCORE_LABELS
from seo_app.content.rules import (
    find_missing,
    load_alt_rules,
    load_image_settings,
    load_meta_rules,
)
from seo_app.content.workflow import apply_flag
from seo_app.images import process as image_process
from seo_app.images.alt import suggest_alt
from seo_app.images.folders import FolderListing, ImageEntry, ImageFolderError, ImageLibrary
from seo_app.images.html import plain_image_text
from seo_app.images.process import ImageProcessError, PreviewCache, make_ai_image, make_web_image
from seo_app.images.tags import (
    FIELD_LABELS,
    PHASE_LABELS,
    SOURCE_AI,
    ImageTags,
    TagError,
    is_ai_name,
    tags_for_image,
)
from seo_app.onpage import links as onpage_links
from seo_app.onpage import meta as onpage_meta
from seo_app.onpage.schema import build_article_faq
from seo_app.sanitize import escape_link_syntax, unbreak_autolinks, unescape_link_syntax
from seo_app.storage import DraftError, DraftPart, DraftSnapshot, DraftStore, new_draft_id
from seo_app.storage import drafts as draft_storage
from seo_app.storage import image_tags as tag_storage
from seo_app.storage import site_index as site_storage
from seo_app.storage.drafts import (
    CheckedImage,
    DraftImage,
    DraftLink,
    DraftMetaVersions,
    DraftSeo,
    SendState,
    check_chosen_image,
    check_draft_images,
)
from seo_app.storage.image_tags import ImageTagStore, ImageTagStoreError
from seo_app.text import escape_markdown, markdown_link, paragraphs_to_html
from seo_app.wordpress.client import DraftImage as WordPressImage
from seo_app.wordpress.client import DraftImagesError, WordPressClient, WordPressError
from seo_app.wordpress.shortcodes import find_shortcodes

S = st.session_state
REWRITE_STYLES = ["Ngắn hơn", "Thân thiện hơn", "Thêm ví dụ", "Bớt thuật ngữ", "Trang trọng hơn"]
MATERIAL = {
    "Kinh nghiệm của xưởng": "ví dụ: khách gần biển làm cổng 201, 1–2 năm đã gỉ mối hàn",
    "Số liệu của bạn": "ví dụ: chênh lệch giá thật từ báo giá của xưởng",
    "Câu hỏi khách hay hỏi": "ví dụ: Inox 304 có bị gỉ không? Làm sao biết thợ dùng đúng 304?",
}
IMAGE_PREFIXES = ("kind-", "pick-", "prompt-", "alt-", "cap-", "altok-", "altsha-", "imgmsg-")
COMPOSE_PREFIXES = (
    "h-",
    "pts-",
    "img-",
    "heading-",
    "texts-",
    "ver-",
    "editing-",
    "manual-",
    "seo_",  # bước SEO (T-041): các bản meta, slug, liên kết nội bộ, schema, công tắc ghi SEO
    *IMAGE_PREFIXES,
)
# Khóa của cả bài (không theo phần) bị xóa cùng bài: cửa sổ chọn ảnh, kết quả gửi nháp, bản sao
# ô nhập.
COMPOSE_KEYS = (
    "_browse",
    "_featured",
    "_wp_result",
    "_wp_sent",
    "_wp_maybe_draft",
    "_wp_sending",
    "_kept",
)
# Ô nhập chỉ hiện ở một bước. Streamlit tự xóa giá trị của ô không được vẽ, nên mỗi lần chạy
# gán lại để chuyển bước không mất từ khóa, chất liệu thật, tiêu đề mục, alt ảnh, ảnh đại diện (và
# nháp không lưu thiếu). Sang trang khác rồi quay lại thì trang này không chạy nên không gán lại
# được: lấy lại từ bản sao ``_kept`` (``remember_inputs``).
KEEP_PREFIXES = ("real-", "h-", "kind-", "prompt-", "alt-", "cap-", "altok-")
KEEP_KEYS = ("keyword", "outline_title", "step", "_featured", "seo_slug", "seo_use_faq")
DRAFT_FLAGS = ("draft_id", "_draft_saved_json", "_draft_saved_at", "_draft_baseline")

# Chỗ cần ảnh (T-056). Nhãn của segmented_control cố định giữa các lần chạy.
REAL, AI_KIND = "Ảnh thật", "Ảnh AI"
IMAGE_KINDS = [REAL, AI_KIND]
BROWSE_PAGE_SIZE = 12  # ảnh mỗi trang khi chọn ảnh: mỗi ảnh một ảnh xem trước
BROWSE_COLUMNS = 4
SCAN_WAIT_SECONDS = 15  # chờ một lần quét lâu nhất (ImageLibrary tự dừng quét sau 10 giây)
MAX_SCANS_KEPT = 40  # số trang thư mục đã quét giữ trong phiên
MAX_SHOWN_SHORTCODE = 80  # ký tự tối đa của một đoạn dạng shortcode khi liệt kê
# Giống số điện thoại (điều kiện Lá Chắn T-050 3d; SL-T056-4): tổng đài 1800/1900 kèm từ 4 chữ số,
# hoặc dãy từ 9 chữ số trở lên; chữ số có thể ngăn bằng dấu cách, chấm, ngoặc, gạch nối, gạch ngang
# dài, gạch chéo, gạch dưới. Ngày tháng (12/10/2026: 8 chữ số) không bị nhắc. Chỉ để nhắc, không
# chặn.
_PHONE_SEP = r"[\s.()\-–—/_]*"
PHONE_LIKE = re.compile(
    rf"\b1[89]00{_PHONE_SEP}\d(?:{_PHONE_SEP}\d){{3,}}|\d(?:{_PHONE_SEP}\d){{8,}}"
)
# Ký tự không nhìn thấy hoặc làm tên trông khác thật: hiện thành «�» (Soi Lỗi T-048).
_HIDDEN_IN_NAME = frozenset({"Cc", "Cf", "Cs", "Co", "Cn", "Zl", "Zp"})
MSG_IMAGE_FAILED = "Không xử lý được ảnh này. Hãy thử ảnh khác."
MSG_SCAN_FAILED = "Không xem được thư mục này. Bấm quét lại hoặc chọn thư mục khác."
MSG_ALT_FAILED = "AI chưa viết được alt cho ảnh này. Bấm thử lại hoặc tự gõ alt."
MSG_SEND_UNEXPECTED = (
    "Gửi nháp gặp lỗi không mong đợi. Bài nháp và ảnh có thể đã lên website: mở trang quản trị "
    "WordPress, kiểm tra Bài viết → Nháp và Media → Thư viện trước khi gửi lại."
)
MSG_SEND_INTERRUPTED = (
    "Lần gửi trước bị ngắt giữa chừng (có thể do bấm nút khác hoặc bấm đúp trong lúc đang gửi), "
    "app không biết kết quả. Bài nháp và ảnh có thể đã lên website: mở trang quản trị WordPress, "
    "kiểm tra Bài viết → Nháp và Media → Thư viện trước khi gửi lại."
)
MSG_SLOW_CHECK = (
    "Ổ đĩa đang chậm (Google Drive?) nên chưa kiểm lại được ảnh. Đợi vài giây rồi bấm lại."
)
MSG_CHECK_FAILED = "Chưa kiểm lại được ảnh này. Bấm lại, hoặc chọn lại ảnh từ thư mục."
SEND_WAIT_SECONDS = 60  # lần chạy mới đợi lần gửi đang chạy song song lâu nhất (``finish_send``)
MSG_WAIT_SEND = "Lần gửi nháp vừa bấm vẫn đang chạy, đợi gửi xong rồi mới hiện kết quả…"
MSG_STILL_SENDING = (
    "Lần gửi nháp trước vẫn đang chạy (website chậm?). Đợi thêm rồi bấm lại hoặc tải lại trang; "
    "trước khi gửi lại, mở trang quản trị WordPress kiểm tra Bài viết → Nháp và Media → Thư viện."
)
MSG_FILE_REPLACED = (
    "nội dung file khác bản bạn đã xem và duyệt (file vừa bị thay bằng ảnh khác cùng tên). Xem "
    "lại ảnh, alt rồi duyệt lại ở bước Viết & kiểm tra"
)
GPS_PUBLIC_WARNING = (
    "📍 Ảnh (kể cả vị trí GPS còn trong ảnh) **xem được công khai** qua đường dẫn ngay khi tải "
    "lên, kể cả khi bài vẫn là nháp. Phần mềm không tự xóa ảnh đã tải lên."
)


# ------------------------------------------------------------------ trạng thái


def init_state() -> None:
    # Trước mọi việc khác (kể cả mở nháp khác): lần chạy trước dừng khi đang gửi bài đang mở.
    finish_send()
    if "_start_keyword" in S:  # bấm «Viết bài mới» ở trang Bài viết
        clear_compose()  # bài mới: xóa cả chất liệu thật của bài cũ (bài cũ vẫn còn trong nháp)
        forget_draft()  # lần tự lưu sau tạo nháp mới, không ghi đè nháp đang mở
        S.keyword = S.pop("_start_keyword")
    if "_open_draft" in S:  # bấm «Mở» ở khung Bài đang soạn dở (phải chạy trước khi vẽ ô nhập)
        open_draft(S.pop("_open_draft"))
    for key, value in S.get("_kept", {}).items():  # vừa quay lại từ trang khác
        S.setdefault(key, value)
    for key in [k for k in S if is_kept(k)]:
        S[key] = S[key]
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
    if "_goto" in S:  # đổi bước sau khi AI chạy xong (phải đặt trước khi vẽ thanh bước)
        S.step = S.pop("_goto")


def is_kept(key: object) -> bool:
    return key in KEEP_KEYS or str(key).startswith(KEEP_PREFIXES)


def remember_inputs() -> None:
    """Cuối mỗi lần chạy: bản sao các ô nhập của bài vào khóa thường (không phải ô nhập).

    Sang trang khác ở menu trên cùng, Streamlit xóa giá trị các ô nhập của trang này; không có bản
    sao thì quay lại sẽ thấy từ khóa, chất liệu thật, alt trống, và lần tự lưu sau ghi đè nháp
    bằng ô trống."""
    S._kept = {key: S[key] for key in S if is_kept(key)}


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
            *COMPOSE_KEYS,
        }:
            del S[key]
    S.step = 0


def clear_compose() -> None:
    """Xóa trắng bài đang soạn, kể cả từ khóa và chất liệu thật (reset_compose giữ hai thứ này)."""
    reset_compose()
    for key in [k for k in S if str(k).startswith("real-")]:
        del S[key]
    S.keyword = ""


def forget_draft() -> None:
    for key in DRAFT_FLAGS:
        S.pop(key, None)


def new_id() -> int:
    S.next_id = S.get("next_id", 0) + 1
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


# ----------------------------------------------------------------------- nháp


@st.cache_resource(show_spinner=False)
def _store_at(path: str) -> DraftStore:
    return DraftStore(Path(path))


def draft_store() -> DraftStore:
    # Đọc đường dẫn lúc chạy (không lúc import) để test trỏ được kho sang thư mục tạm.
    return _store_at(str(draft_storage.DEFAULT_DRAFTS_FILE))


def snapshot() -> DraftSnapshot:
    """Bài đang soạn trong session → nháp. Giữ nguyên chữ như trong session (xem T-016)."""
    return DraftSnapshot(
        id=S.setdefault("draft_id", new_draft_id()),
        step=S.step,
        keyword=S.keyword,
        material={label: text for label, text in material().items() if text},
        research=S.research,
        research_keyword=S.research_keyword,
        outline_title=S.outline_title,
        outline=[
            OutlineItem(heading=S[f"h-{u}"], points=list(S[f"pts-{u}"]), image=S[f"img-{u}"])
            for u in S.outline_ids
        ],
        article_title=S.article_title,
        parts=[
            DraftPart(
                heading=S[f"heading-{p}"],
                versions=list(S[f"texts-{p}"]),
                current=S[f"ver-{p}"],
                image=S.get(f"img-{p}", ""),
                chosen_image=slot_draft_image(p),
            )
            for p in S.part_ids
        ],
        review=S.review,
        auto_fixed=S.auto_fixed,
        ignored_flags=S.ignored_flags,
        seo=seo_snapshot(),
    )


def open_draft(draft_id: str) -> None:
    """Nháp → session. Gọi trong init_state, trước khi vẽ ô nhập nào."""
    try:
        snap = draft_store().load(draft_id)
    except DraftError as exc:
        S._draft_error = str(exc)
        return
    clear_compose()
    forget_draft()
    S.draft_id = snap.id
    S.keyword = snap.keyword
    for label, text in snap.material.items():
        if label in MATERIAL:  # chỉ nhận nhãn đang có trên trang
            S[f"real-{label}"] = text
    S.research = snap.research
    S.research_keyword = snap.research_keyword
    # Không dùng set_outline: dàn ý trong nháp đã ở dạng ô sửa (chưa escape), không unescape nữa.
    S.outline_title = snap.outline_title
    S.outline_ids = []
    for item in snap.outline:
        uid = new_id()
        S[f"h-{uid}"] = item.heading
        S[f"pts-{uid}"] = list(item.points)
        S[f"img-{uid}"] = item.image
        S.outline_ids.append(uid)
    S.article_title = snap.article_title
    S.part_ids = []
    for part in snap.parts:
        pid = new_id()
        S[f"heading-{pid}"] = part.heading
        S[f"texts-{pid}"] = list(part.versions)
        S[f"ver-{pid}"] = part.current
        S[f"img-{pid}"] = part.image
        S.part_ids.append(pid)
    restore_images(snap)
    restore_seo(snap.seo)
    S.review = snap.review
    S.auto_fixed = snap.auto_fixed
    S.ignored_flags = set(snap.ignored_flags)
    S.step = snap.step
    S._draft_saved_at = snap.saved_at
    S._draft_baseline = True  # lần chạy này chỉ ghi nhận, không lưu lại (giờ lưu giữ nguyên)
    st.toast("Đã mở bài đang soạn dở", icon="📂")


def restore_images(snap: DraftSnapshot) -> None:
    """Ảnh đã chọn trong nháp → các chỗ cần ảnh (điều kiện Lá Chắn T-055).

    Nháp là dữ liệu chưa tin cậy: kiểm lại mọi ảnh trên máy **một lần** khi mở
    (``check_draft_images``, kèm ``ai_roots``), rồi chỉ dùng kết quả kiểm (``checked.image``,
    ``checked.tags``, ``checked.ref``), không dùng trường trong nháp vừa mở. Không truyền
    ``scanned``: lúc mở nháp chưa có lần quét nào từ thư mục gốc (LC-T055-1).
    """
    if snap.dropped_images:
        S._images_notice = (
            f"{snap.dropped_images} ảnh đã chọn trong nháp bị hỏng nên đã bỏ; phần chữ của bài "
            "vẫn giữ. Hãy chọn lại ảnh cho các chỗ đó."
        )
    if not any(part.chosen_image is not None for part in snap.parts):
        return
    library = image_library()
    with st.spinner("Đang kiểm lại ảnh đã chọn trong nháp…"):
        checked = check_draft_images(
            snap, library, tag_store=tag_store(), ai_roots=ai_root_indexes(library)
        )
    for index, item in checked.items():
        pid = S.part_ids[index]
        S[f"kind-{pid}"] = AI_KIND if item.is_ai or item.is_generated else REAL
        if item.image.prompt:
            S[f"prompt-{pid}"] = item.image.prompt
        set_pick(pid, item)  # ảnh không dùng được: khung ảnh hiện ``item.message``


def ask_open(draft_id: str) -> None:
    S._open_draft = draft_id


def delete_draft(draft_id: str) -> None:
    try:
        draft_store().delete(draft_id)
    except DraftError as exc:
        S._draft_error = str(exc)
        return
    if S.get("draft_id") == draft_id:
        # Xóa đúng bài đang mở: xóa trắng trang, nếu không lần tự lưu sau sẽ tạo lại nháp.
        clear_compose()
        forget_draft()
    st.toast("Đã xóa nháp", icon="🗑️")


def autosave(slot) -> None:
    """Cuối mỗi lần chạy: bài khác bản đã lưu thì lưu. Không bao giờ làm sập trang."""
    if "draft_id" not in S and not (keyword() or S.research is not None):
        return  # trang còn trống, chưa có gì để lưu
    try:
        snap = snapshot()
        current = snap.model_dump_json(exclude={"saved_at"})
        if S.pop("_draft_baseline", False):
            S._draft_saved_json = current
        elif current != S.get("_draft_saved_json"):
            saved = draft_store().save(snap)
            S._draft_saved_json = current
            S._draft_saved_at = saved.saved_at
    except (DraftError, ValueError, KeyError) as exc:  # ValidationError là một dạng ValueError
        message = str(exc) if isinstance(exc, DraftError) else "dữ liệu bài chưa đầy đủ."
        slot.caption(f"⚠️ Chưa lưu được nháp: {message}")
        return
    if S.get("_draft_saved_at") is not None:
        slot.caption(f"💾 Đã lưu lúc {S._draft_saved_at.strftime('%H:%M')}")


def format_saved(summary_time) -> str:
    return summary_time.strftime("%H:%M · %d/%m/%Y")


def drafts_panel() -> None:
    """Khung «Bài đang soạn dở» ở bước Chuẩn bị. Chữ từ nháp chỉ hiện bằng st.text."""
    try:
        listing = draft_store().list_drafts()
    except DraftError as exc:
        st.warning(str(exc))
        return
    if not listing.drafts and not listing.skipped:
        return
    current = S.get("draft_id")
    others = [d for d in listing.drafts if d.id != current]
    with st.expander(
        f"📂 Bài đang soạn dở ({len(listing.drafts)})",
        expanded=not keyword() and S.research is None and bool(others),
    ):
        if listing.skipped:
            st.caption(f"Có {listing.skipped} nháp bị hỏng nên không hiện.")
        for d in listing.drafts:
            with st.container(border=True):
                info, open_col, del_col = st.columns([6, 1.2, 1.2], vertical_alignment="center")
                info.text(d.title)
                meta = f"Lưu lúc {format_saved(d.saved_at)}"
                if d.keyword.strip() and d.keyword.strip() != d.title:
                    meta = f"Từ khóa: {d.keyword.strip()} · {meta}"
                info.text(meta)
                if d.id == current:
                    open_col.button("Đang mở", key=f"open-{d.id}", disabled=True, width="stretch")
                else:
                    open_col.button(
                        "Mở",
                        key=f"open-{d.id}",
                        on_click=ask_open,
                        args=(d.id,),
                        width="stretch",
                    )
                with del_col.popover("🗑️ Xóa", width="stretch"):
                    st.markdown("Xóa hẳn nháp này? Không lấy lại được.")
                    st.button(
                        "Xóa hẳn",
                        key=f"del-{d.id}",
                        type="primary",
                        on_click=delete_draft,
                        args=(d.id,),
                        width="stretch",
                    )


# ------------------------------------------------------------------------ ảnh


@st.cache_resource(show_spinner=False)
def _tag_store_at(path: str) -> ImageTagStore:
    return ImageTagStore(Path(path))


def tag_store() -> ImageTagStore:
    # Đọc đường dẫn lúc chạy (không lúc import) để test trỏ được kho thẻ sang thư mục tạm.
    return _tag_store_at(str(tag_storage.DEFAULT_IMAGE_TAGS_FILE))


@st.cache_resource(show_spinner=False)
def _preview_cache_at(path: str) -> PreviewCache:
    return PreviewCache(Path(path))


def preview_cache() -> PreviewCache:
    # Thư mục cache luôn là của app, người dùng không đặt được (điều kiện Lá Chắn T-049).
    return _preview_cache_at(str(image_process.PREVIEW_CACHE_DIR))


@st.cache_resource(show_spinner=False)
def _scan_pool() -> ThreadPoolExecutor:
    """Quét thư mục trong luồng riêng: ổ Google Drive chậm không giữ trang quá lâu (Thợ Máy T-048
    điểm 7). Quét quá ``SCAN_WAIT_SECONDS`` thì trang báo "đang quét", lần quét chạy tiếp ở nền."""
    return ThreadPoolExecutor(max_workers=2, thread_name_prefix="quet-anh")


def image_library() -> ImageLibrary:
    return ImageLibrary.from_settings(load_settings())


def _resolved_name(folder: Path) -> str:
    try:
        return folder.expanduser().resolve(strict=True).name
    except (OSError, RuntimeError):
        return ""


def _through_link(folder: Path) -> bool:
    """Đường dẫn thư mục gốc có tầng nào là lối tắt (symlink, junction) không."""
    try:
        folder = folder.expanduser()
        return any(part.is_symlink() or part.is_junction() for part in (folder, *folder.parents))
    except (OSError, RuntimeError, ValueError):
        return False


def root_notes(library: ImageLibrary) -> dict[int, tuple[bool, bool]]:
    """``{số thứ tự thư mục gốc: (mọi ảnh trong đó là ảnh AI, đi qua lối tắt)}``.

    - Ảnh AI (điều kiện Lá Chắn T-052 c, T-070 g): ``is_ai_name`` với ``RootInfo.label`` (tên lấy
      từ ``Path``) **và** với tên thư mục gốc sau ``resolve()`` (gốc là lối tắt thì tên thật có
      thể khác); một trong hai đúng là đủ.
    - Lối tắt: ghi nhận của Lá Chắn T-048 (gốc trên USB có thể là junction trỏ vào thư mục khác).

    Đường dẫn khai báo chỉ dùng để tính hai giá trị đúng/sai này, không hiện ra giao diện.
    """
    folders = load_settings().image_folders
    notes = {}
    for root in library.roots():
        folder = folders[root.index] if root.index < len(folders) else None
        resolved = _resolved_name(folder) if folder is not None else ""
        ai = is_ai_name(root.label) or bool(resolved and is_ai_name(resolved))
        notes[root.index] = (ai, folder is not None and _through_link(folder))
    return notes


def ai_root_indexes(library: ImageLibrary) -> frozenset[int]:
    return frozenset(index for index, (ai, _link) in root_notes(library).items() if ai)


def shown_name(name: str) -> str:
    """Tên file, tên thư mục lấy từ máy (dữ liệu chưa tin cậy) để hiện (Soi Lỗi T-048, LC-T048-4 b).

    Ký tự vô hình, điều khiển (rộng 0, đảo hướng, ngắt dòng…) hiện thành «�» để tên không trông khác
    thật; cả tên nằm trong cặp cô lập hướng chữ (U+2068 … U+2069) để chữ viết từ phải sang trái
    không đảo thứ tự chữ xung quanh. Chưa escape Markdown: hiện bằng Markdown thì qua ``name_md``.
    """
    visible = "".join(
        "\ufffd" if unicodedata.category(ch) in _HIDDEN_IN_NAME else ch for ch in name
    )
    return f"\u2068{visible}\u2069"


def name_md(name: str) -> str:
    return escape_markdown(shown_name(name))


def place_md(root_label: str, rel_dir: str) -> str:
    """«Thư mục gốc › a › b»: chỉ tên thư mục gốc và đường dẫn tương đối, không đường dẫn máy."""
    return " › ".join(name_md(part) for part in [root_label, *rel_dir.split("/")] if part)


def root_label(library: ImageLibrary, index: int) -> str:
    for root in library.roots():
        if root.index == index:
            return root.label
    return f"Thư mục ảnh {index + 1}"


def tags_md(tags: ImageTags) -> str:
    """Thẻ để hiện. Mọi giá trị thuộc danh sách cố định của ``ImageTags`` (không phải chữ tên thư
    mục), vẫn escape cho chắc."""
    items = [
        f"Mã {tags.project_code}" if tags.project_code else "",
        tags.category,
        tags.area,
        PHASE_LABELS.get(tags.phase, ""),
    ]
    return escape_markdown(" · ".join(item for item in items if item))


def _name_key(name: str) -> str:
    return unicodedata.normalize("NFC", name).casefold()


def note_tag_store(store: ImageTagStore) -> None:
    """File thẻ sửa tay hỏng đã được cất sang một bên: báo một lần, chỉ tên file (điều kiện d)."""
    if store.recovered_from is not None and not S.get("_tags_recovered_noted"):
        S._tags_recovered_noted = True
        st.warning(
            "File lưu thẻ ảnh sửa tay bị hỏng nên đã được cất sang một bên "
            f"(tên «{escape_markdown(store.recovered_from.name)}», cùng thư mục). Các dấu «ảnh AI» "
            "đã gắn tay trước đó không còn: xem lại ảnh trước khi gửi."
        )


# ----- một chỗ cần ảnh -----------------------------------------------------------------------


def set_pick(pid: int, checked: CheckedImage) -> None:
    """Ảnh đã chọn của chỗ ``pid`` và chữ đi kèm, theo đúng kết quả kiểm (``checked.image``)."""
    if checked.ref is None:
        S.pop(f"pick-{pid}", None)
    else:
        S[f"pick-{pid}"] = checked
    S[f"alt-{pid}"] = checked.image.alt
    S[f"cap-{pid}"] = checked.image.caption
    S[f"altok-{pid}"] = checked.image.alt_approved
    # Băm của bản đã duyệt gắn lại ở lần vẽ khung ảnh tới (``alt_editor``), theo ảnh mới này.
    S.pop(f"altsha-{pid}", None)


def ai_tags(tags: ImageTags) -> ImageTags:
    """Thẻ ảnh AI: chỉ giữ hạng mục (ảnh AI không mang mã công trình, khu vực, trước/sau)."""
    return ImageTags(source=SOURCE_AI, category=tags.category)


def slot_tags(checked: CheckedImage) -> ImageTags:
    """Thẻ dùng cho ảnh đã chọn. Ảnh đã đánh dấu là ảnh AI trong phiên (kể cả khi lưu thẻ hỏng)
    luôn là ảnh AI (điều kiện Lá Chắn T-074 j)."""
    if not checked.tags.is_ai and checked.ref in S.get("_ai_marked", ()):
        return ai_tags(checked.tags)
    return checked.tags


def slot_texts(pid: int) -> dict[str, object]:
    return {
        "alt": S.get(f"alt-{pid}", ""),
        "alt_approved": bool(S.get(f"altok-{pid}", False)),
        "caption": S.get(f"cap-{pid}", ""),
        "prompt": S.get(f"prompt-{pid}", ""),
    }


def slot_draft_image(pid: int) -> DraftImage | None:
    """Chỗ cần ảnh → ``DraftImage`` để lưu nháp (theo ``checked.ref``, thẻ đã kiểm; T-055)."""
    checked: CheckedImage | None = S.get(f"pick-{pid}")
    if checked is not None:
        return DraftImage.from_library(checked.ref, slot_tags(checked), **slot_texts(pid))
    if S.get(f"kind-{pid}") == AI_KIND and S.get(f"img-{pid}"):
        return DraftImage(source=SOURCE_AI, **slot_texts(pid))  # ảnh AI chưa có file: nhớ prompt
    return None


def scanned_entries() -> list[ImageEntry]:
    """Ảnh của các lần quét trong phiên (đi từ thư mục gốc xuống, LC-T055-1): ``scanned`` hợp lệ."""
    return [
        entry
        for listing in S.get("_scans", {}).values()
        if isinstance(listing, FolderListing)
        for entry in listing.images
    ]


def check_in_pool(image: DraftImage, library: ImageLibrary) -> CheckedImage | str:
    """``check_chosen_image`` chạy trong luồng quét, chờ tối đa ``SCAN_WAIT_SECONDS``. Chưa kiểm
    xong thì trả câu báo thay cho kết quả: quá giờ (``MSG_SLOW_CHECK``, lần kiểm vẫn chạy tiếp ở
    nền), lỗi lạ (``MSG_CHECK_FAILED``: câu cố định, không để Streamlit in dấu vết lỗi có đường dẫn
    máy; Ghi nhận 2 của Lá Chắn T-056).

    Ảnh chưa có trong lần quét nào của phiên (ảnh mở từ nháp) được đối chiếu tên thư mục bằng cách
    xem danh sách thư mục từng tầng (lớp phòng thứ hai của T-055): không làm việc đó trong luồng của
    trang, để ổ Google Drive chậm không giữ trang (Soi Lỗi T-048, SL-T056-7). ``scanned`` vẫn chỉ
    là ảnh của các lần quét (LC-T055-1)."""
    future = _scan_pool().submit(
        check_chosen_image,
        image,
        library,
        tag_store=tag_store(),
        scanned=scanned_entries(),
        ai_roots=ai_root_indexes(library),
    )
    try:
        return future.result(timeout=SCAN_WAIT_SECONDS)
    except TimeoutError:
        return MSG_SLOW_CHECK
    except Exception:
        return MSG_CHECK_FAILED


def recheck(
    library: ImageLibrary, pid: int, checked: CheckedImage
) -> tuple[CheckedImage | str, DraftImage]:
    """Kiểm lại ảnh đã chọn ngay trước khi dùng (LC-T055-2): cùng ``checked.ref``, thẻ hiện tại,
    chữ đang có trong ô. Trả (kết quả kiểm, ảnh đã đưa vào kiểm); kết quả là chữ: chưa kiểm xong,
    đó là câu báo (``check_in_pool``)."""
    image = DraftImage.from_library(checked.ref, slot_tags(checked), **slot_texts(pid))
    return check_in_pool(image, library), image


def file_changed(fresh: CheckedImage, checked: CheckedImage) -> bool:
    """File ảnh khác lần chọn, xem trước, duyệt alt (cỡ, giờ sửa, định danh trên ổ): ví dụ bị thay
    bằng ảnh khác cùng tên (Drive đồng bộ bản mới, chép đè; SL-T056-2)."""
    old, new = checked.entry, fresh.entry
    if old is None or new is None:
        return old is not new
    return (old.size, old.modified, old.file_id) != (new.size, new.modified, new.file_id)


def changed(fresh: CheckedImage, image: DraftImage, checked: CheckedImage) -> bool:
    """Lần kiểm lại cho ảnh khác (tên, thư mục, file bị thay cùng tên), hay ảnh vừa thành ảnh AI
    (alt thêm tiền tố)."""
    return (
        fresh.ref != checked.ref
        or file_changed(fresh, checked)
        or fresh.tags.is_ai != (image.source == SOURCE_AI)
        or (fresh.image.alt, fresh.image.caption) != (image.alt, image.caption)
    )


def slot_problem(pid: int) -> str | None:
    """``None``: chưa chọn ảnh; ``""``: sẵn sàng gửi; còn lại: vì sao chưa gửi được."""
    checked: CheckedImage | None = S.get(f"pick-{pid}")
    if checked is None:
        return None
    if not checked.available:
        return checked.message or "ảnh không còn dùng được trên máy này"
    texts = DraftImage(**slot_texts(pid))  # lọc như lúc lưu, lúc gửi
    if not texts.alt:
        return "chưa có alt (mô tả ảnh)"
    if not texts.alt_approved:
        return "alt và chú thích chưa duyệt"
    return ""


def preview_bytes(library: ImageLibrary, ref) -> tuple[bytes | None, str]:
    """Ảnh xem trước (JPEG do app tạo) cho ``st.image``. Không bao giờ trả byte gốc, ảnh Pillow
    hay đường dẫn (LC-T058-2; Lá Chắn T-049 điều kiện 3).

    Ảnh bị thay tại chỗ (cùng cỡ, cùng giờ sửa: ``PreviewCache`` vẫn giữ ảnh xem trước của bản cũ;
    Ghi nhận 1 của Lá Chắn T-056) thì dựng ảnh xem trước từ file hiện tại bằng ``make_preview``."""
    try:
        if ref in S.get("_replaced", ()):
            return image_process.make_preview(library.read_image_bytes(ref)), ""
        return preview_cache().get(library, ref), ""
    except (ImageFolderError, ImageProcessError) as exc:
        return None, str(exc)
    except Exception:  # lỗi lạ: câu cố định, không để Streamlit in dấu vết lỗi
        return None, MSG_IMAGE_FAILED


def content_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def web_info(
    library: ImageLibrary, checked: CheckedImage
) -> tuple[bool | None, str, str, str | None]:
    """(có vị trí GPS, câu báo của ``WebImage.notice``, lỗi, băm SHA-256 nội dung file) của bản
    đăng web. Nén thử một lần cho mỗi phiên bản file; giữ trong phiên (chỉ giữ kết quả, không giữ
    ảnh). Băm là của đúng byte đã đọc để ra dòng GPS đang hiện: lúc duyệt alt, lần duyệt gắn với
    băm này (``alt_editor``), lúc gửi so lại (T-086, SL-T056-10)."""
    entry = checked.entry
    key = (checked.ref, entry.size, entry.modified)
    cache = S.setdefault("_web_info", {})
    if key not in cache:
        digest = None
        try:
            settings = load_image_settings()
            with st.spinner("Đang kiểm ảnh (nén thử WebP, đọc vị trí GPS)…"):
                data = library.read_image_bytes(checked.ref)
                digest = content_hash(data)
                web = make_web_image(
                    data, max_edge_px=settings.max_edge_px, webp_quality=settings.webp_quality
                )
        except (ImageFolderError, ImageProcessError, AIError) as exc:  # ContentRulesError: AIError
            cache[key] = (None, "", str(exc), digest)
        except Exception:
            cache[key] = (None, "", MSG_IMAGE_FAILED, digest)
        else:
            cache[key] = (web.has_gps, web.notice, "", digest)
    return cache[key]


def alt_limits() -> tuple[int, int]:
    try:
        rules = load_alt_rules()
    except AIError:  # ContentRulesError: lỗi hiện ở nút AI viết alt
        return 125, 200
    return rules.max_chars, rules.caption_max_chars


def ai_reason(checked: CheckedImage, ai_roots: frozenset[int]) -> str:
    """Vì sao ảnh là ảnh AI (điều kiện Lá Chắn T-070 h): người dùng không đổi lại được trong app."""
    if checked.ref.root_index in ai_roots:
        why = "tên thư mục ảnh gốc có chữ AI hoặc tên công cụ tạo ảnh"
    elif tags_for_image(checked.ref).tags.is_ai:
        why = "tên thư mục hoặc tên file có chữ AI hoặc tên công cụ tạo ảnh"
    else:
        why = "ảnh đã được đánh dấu là ảnh AI (trong nháp hoặc trên máy này)"
    return f"Vì sao là ảnh AI: {why}. App không đổi lại thành ảnh thật được."


def unapprove(pid: int) -> None:
    S[f"altok-{pid}"] = False


def unpick(pid: int) -> None:
    for prefix in ("pick-", "alt-", "cap-", "altok-", "altsha-", "imgmsg-"):
        S.pop(f"{prefix}{pid}", None)
        S.get("_kept", {}).pop(f"{prefix}{pid}", None)  # bản sao không đưa alt cũ trở lại


def mark_ai(pid: int) -> None:
    """Nút «Đây là ảnh AI» (điều kiện Lá Chắn T-052 b, T-074 j): lưu thẻ sửa tay
    ``source="ai"``. Lưu hỏng (file đang bận, hỏng) thì trong phiên vẫn coi là ảnh AI (hướng an
    toàn) và báo lỗi; không bao giờ viết alt hay gửi nháp như ảnh thật vì lần lưu hỏng.

    Thẻ theo ảnh, không theo chỗ: mọi chỗ cần ảnh dùng cùng ảnh này đều thành ảnh AI ngay (alt,
    chú thích thêm «Minh họa», phải duyệt lại; SL-T056-6)."""
    checked: CheckedImage | None = S.get(f"pick-{pid}")
    if checked is None or slot_tags(checked).is_ai:
        return
    ref = checked.ref
    S.setdefault("_ai_marked", set()).add(ref)  # từ đây ``slot_tags`` của ảnh này là ảnh AI
    error = ""
    try:
        tag_store().set(ref, ai_tags(checked.tags))
    except (ImageTagStoreError, TagError) as exc:
        error = (
            f"Chưa lưu được dấu «ảnh AI» trên máy này: {exc} Trong lần làm việc này app vẫn coi "
            "ảnh là ảnh AI."
        )
    library = image_library()
    for spot in S.part_ids:
        current: CheckedImage | None = S.get(f"pick-{spot}")
        if current is None or current.ref != ref:
            continue
        S.pop(f"imgmsg-{spot}", None)
        fresh, _image = recheck(library, spot, current)
        if isinstance(fresh, str):  # chưa kiểm xong: vẫn là ảnh AI trong phiên, alt kiểm sau
            S[f"pick-{spot}"] = dataclasses.replace(current, tags=ai_tags(current.tags))
            S[f"altok-{spot}"] = False
            S[f"imgmsg-{spot}"] = fresh
        else:
            set_pick(spot, fresh)  # alt, chú thích thêm tiền tố «Minh họa», phải duyệt lại
            if file_changed(fresh, current):
                S[f"altok-{spot}"] = False
        S[f"kind-{spot}"] = AI_KIND
    if error:
        S[f"imgmsg-{pid}"] = error


def choose_image(pid: int, entry: ImageEntry, scanned: tuple[ImageEntry, ...]) -> None:
    """Chọn một ảnh của lần quét (``ImageEntry`` từ ``list_folder``, khóa theo tên trên ổ): thẻ lấy
    bằng ``resolve``, rồi kiểm như ảnh của nháp (``check_chosen_image`` kèm ``ai_roots``)."""
    library, store = image_library(), tag_store()
    try:
        tags = store.resolve(entry.ref).tags
        if entry.ref in S.get("_ai_marked", ()):
            tags = ai_tags(tags)
        image = DraftImage.from_library(entry, tags, prompt=S.get(f"prompt-{pid}", ""))
        checked = check_chosen_image(
            image, library, tag_store=store, scanned=scanned, ai_roots=ai_root_indexes(library)
        )
    except Exception:  # lỗi lạ: câu cố định, không dấu vết lỗi (Ghi nhận 2 của Lá Chắn T-056)
        S[f"imgmsg-{pid}"] = MSG_CHECK_FAILED
        return
    set_pick(pid, checked)  # ảnh mới: alt, chú thích để trống, chưa duyệt
    S[f"kind-{pid}"] = AI_KIND if checked.is_ai else REAL
    S.pop(f"imgmsg-{pid}", None)
    close_browser()
    st.toast("Đã chọn ảnh", icon="🖼️")


def ai_write_alt(library: ImageLibrary, pid: int, checked: CheckedImage) -> str:
    """AI gợi ý alt, chú thích cho đúng ảnh đã chọn, chỉ khi người dùng bấm (điều kiện Lá Chắn
    T-050 a, T-062; Soi Lỗi T-066): byte gửi AI là của ``make_ai_image``; ``ai_generated`` theo thẻ
    (sau bước «Đây là ảnh AI»), không theo AI. Gọi trước khi vẽ ô alt. Trả câu lỗi, rỗng nếu xong.
    """
    fresh, _image = recheck(library, pid, checked)
    if isinstance(fresh, str):  # ổ chậm, lỗi lạ: câu báo
        return fresh
    if not fresh.available:
        set_pick(pid, fresh)
        return fresh.message
    try:
        rules = load_alt_rules()
        router = AIRouter(load_ai_config(), load_settings(), prepare=("alt",))
        ai_image = make_ai_image(library.read_image_bytes(fresh.ref))
        with st.spinner("AI đang xem ảnh và viết alt…", show_time=True):
            suggestion = suggest_alt(
                router,
                ImageInput(data=ai_image.data, mime=ai_image.mime),
                tags=fresh.tags.reference(),
                keyword=keyword(),
                ai_generated=fresh.tags.is_ai,
                rules=rules,
            )
    except AIError as exc:  # kể cả ContentRulesError: đúng câu tiếng Việt, không st.exception
        return str(exc)
    except (ImageFolderError, ImageProcessError) as exc:
        return str(exc)
    except Exception:
        return MSG_ALT_FAILED
    set_pick(pid, fresh)
    S[f"alt-{pid}"] = suggestion.alt
    S[f"cap-{pid}"] = suggestion.caption
    S[f"altok-{pid}"] = False  # gợi ý của AI phải được người dùng đọc và duyệt
    return ""


def image_slot(pid: int) -> None:
    S.setdefault(f"kind-{pid}", REAL)
    checked: CheckedImage | None = S.get(f"pick-{pid}")
    library = image_library()
    with st.container(border=True, key=f"imgbox-{pid}"):
        st.markdown(f"**📷 Chỗ cần ảnh** — {S[f'img-{pid}']}")
        st.segmented_control(
            "Loại ảnh",
            IMAGE_KINDS,
            key=f"kind-{pid}",
            required=True,
            label_visibility="collapsed",
        )
        preview, detail = st.columns([1, 2], gap="medium")
        with preview:
            slot_preview(library, pid, checked)
        with detail:
            if S[f"kind-{pid}"] == AI_KIND:
                ai_prompt_panel(pid)
            if S.get(f"imgmsg-{pid}"):
                st.warning(escape_markdown(S[f"imgmsg-{pid}"]))
            if checked is None:
                empty_slot(library, pid)
            else:
                chosen_panel(library, pid, checked)
        if S.get("_browse", {}).get("pid") == pid:
            folder_browser(library, pid)


def slot_preview(library: ImageLibrary, pid: int, checked: CheckedImage | None) -> None:
    if checked is not None and checked.available:
        data, error = preview_bytes(library, checked.ref)
        if data is not None:
            st.image(data, alt="Ảnh xem trước của ảnh đã chọn", width="stretch")
            return
        st.caption(f"⚠️ {escape_markdown(error)}")
    if checked is not None:
        icon, text = "⚠️", "Ảnh không dùng được"
    elif S[f"kind-{pid}"] == AI_KIND:
        icon, text = "✨", "Ảnh AI sẽ hiện ở đây"
    else:
        icon, text = "🖼️", "Chưa chọn ảnh"
    # HTML cố định do code viết (U1): không có chữ nào lấy từ máy, AI hay người dùng.
    st.markdown(f'<div class="img-ph">{icon}<br>{text}</div>', unsafe_allow_html=True)


def ai_prompt_panel(pid: int) -> None:
    """Ảnh AI: prompt xem, sửa, sao chép được. Tạo ảnh ngay trong app đang hoãn (T-053, chủ dự án
    chốt 2026-10-20): người dùng tạo ảnh ở công cụ khác rồi chọn từ thư mục ảnh AI."""
    S.setdefault(f"prompt-{pid}", S[f"img-{pid}"])
    st.caption("Prompt tạo ảnh — bấm biểu tượng ở góc khung để sao chép.")
    st.code(S[f"prompt-{pid}"] or " ", language=None, wrap_lines=True)
    later = "Tạo ảnh ngay trong app đang tạm hoãn (chủ dự án chốt 2026-10-20)."
    row = st.container(horizontal=True, gap="small")
    row.button("🎨 Tạo ảnh", key=f"gen-{pid}", disabled=True, help=later)
    row.button("🔄 Prompt khác", key=f"rp-{pid}", disabled=True, help=later)
    with row.popover("✏️ Sửa prompt"):
        st.text_area(
            "Prompt", key=f"prompt-{pid}", height=150, max_chars=draft_storage.MAX_PROMPT_CHARS
        )
    st.caption(
        "Dùng prompt này tạo ảnh ở Gemini (hoặc công cụ khác), lưu ảnh vào thư mục có chữ «AI» "
        "trong tên (ví dụ «Ảnh AI»), rồi chọn ảnh từ thư mục: app coi đó là ảnh AI."
    )


def empty_slot(library: ImageLibrary, pid: int) -> None:
    if len(library) == 0:
        st.info(
            "Chưa khai báo thư mục ảnh: điền IMAGE_FOLDERS trong file .env (xem README), rồi mở "
            "lại app."
        )
        return
    st.caption("Chưa chọn ảnh cho chỗ này.")
    st.button("📁 Chọn ảnh từ thư mục", key=f"browse-{pid}", on_click=open_browser, args=(pid,))


def chosen_panel(library: ImageLibrary, pid: int, checked: CheckedImage) -> None:
    ref = checked.ref
    st.markdown(f"**{name_md(ref.name)}**")
    st.caption(
        f"Thư mục: {place_md(root_label(library, ref.root_index), '/'.join(ref.parts[:-1]))}"
    )
    # Ảnh thật / Ảnh AI hiện rõ trước khi viết alt (điều kiện Lá Chắn T-052 b).
    if slot_tags(checked).is_ai:  # kể cả ảnh vừa đánh dấu ở chỗ khác trong phiên (SL-T056-6)
        st.markdown(":violet-badge[🤖 Ảnh AI]")
        st.caption(ai_reason(checked, ai_root_indexes(library)))
    else:
        st.markdown(":green-badge[📷 Ảnh thật]")
        if S[f"kind-{pid}"] == AI_KIND:
            st.caption(
                "Ảnh đang chọn được coi là ảnh thật. Nếu ảnh do AI tạo, bấm «Đây là ảnh AI»."
            )
        st.button(
            "🤖 Đây là ảnh AI",
            key=f"markai-{pid}",
            on_click=mark_ai,
            args=(pid,),
            help=(
                "Ảnh do AI tạo, không phải ảnh chụp công trình: alt mở đầu «Minh họa», tên file "
                "«minh-hoa-ai-…». Không đổi lại thành ảnh thật trong app được."
            ),
        )
    found = tags_md(slot_tags(checked))
    st.caption(f"Thẻ: {found}" if found else "Chưa có thẻ (tên thư mục chưa theo quy ước).")
    auto = tags_for_image(ref)
    if auto.unmatched:  # chỉ hiện số, không hiện chữ tên thư mục (điều kiện Lá Chắn T-052 e)
        st.caption(f"{auto.unmatched} phần tên thư mục không khớp danh sách thẻ nên bị bỏ qua.")
    if auto.conflicts:
        names = ", ".join(FIELD_LABELS.get(name, name) for name in auto.conflicts)
        st.caption(f"Để trống vì tên thư mục ghi hai giá trị khác nhau: {escape_markdown(names)}.")
    if checked.tag_error:
        st.caption(f"⚠️ {escape_markdown(checked.tag_error)}")
    if not checked.available:
        st.warning(escape_markdown(checked.message or "Ảnh không còn dùng được trên máy này."))
    else:
        gps, notice, error, digest = web_info(library, checked)
        if error:
            st.warning(escape_markdown(error))
        elif gps:
            st.caption("📍 Ảnh có vị trí GPS: vị trí này lên website cùng ảnh.")
        else:
            st.caption("Ảnh không có vị trí GPS.")
        if notice:
            st.caption(f"⚠️ {escape_markdown(notice)}")
        alt_editor(library, pid, checked, digest)
    actions = st.container(horizontal=True, gap="small")
    actions.button(
        "📂 Mở thư mục chứa ảnh", key=f"openfolder-{pid}", on_click=open_image_folder, args=(pid,)
    )
    actions.button("🔁 Chọn ảnh khác", key=f"browse-{pid}", on_click=open_browser, args=(pid,))
    actions.button("✖ Bỏ ảnh", key=f"unpick-{pid}", on_click=unpick, args=(pid,))


def alt_editor(library: ImageLibrary, pid: int, checked: CheckedImage, digest: str | None) -> None:
    """Alt, chú thích trong ô nhập để người dùng sửa và duyệt (điều kiện Lá Chắn T-050 b). Nút AI
    nằm dưới ô nhưng chạy trước khi vẽ ô (gán giá trị mới cho ô chỉ được trước khi ô được vẽ).

    Lần duyệt gắn với băm nội dung của bản ảnh đang hiện (``digest`` của ``web_info``):
    ``altsha-<id>``. Lúc gửi, byte sắp tải phải cùng băm (T-086, SL-T056-10)."""
    inputs = st.container()
    row = st.container()
    write_col, ok_col = row.columns([1, 1.4], vertical_alignment="center")
    has_alt = bool(S.get(f"alt-{pid}", "").strip())
    if write_col.button(
        "🔄 AI viết lại alt" if has_alt else "✨ AI viết alt",
        key=f"altai-{pid}",
        width="stretch",
    ):
        error = ai_write_alt(library, pid, checked)
        if error:
            row.error(escape_markdown(error))
    alt_max, caption_max = alt_limits()
    with inputs:
        st.text_input(
            "Alt (mô tả ảnh cho Google và người khiếm thị)",
            key=f"alt-{pid}",
            on_change=unapprove,
            args=(pid,),
        )
        alt = S.get(f"alt-{pid}", "")
        st.caption(
            f"{len(alt)}/{alt_max} ký tự"
            + (" · dài quá, nên rút gọn" if len(alt) > alt_max else "")
        )
        st.text_input(
            "Chú thích dưới ảnh (không bắt buộc)",
            key=f"cap-{pid}",
            on_change=unapprove,
            args=(pid,),
        )
        caption = S.get(f"cap-{pid}", "")
        if len(caption) > caption_max:
            st.caption(f"Chú thích {len(caption)} ký tự, nên dưới {caption_max}.")
        if slot_tags(checked).is_ai:
            st.caption(
                "Ảnh AI: alt mở đầu «Minh họa», chú thích mở đầu «Ảnh minh họa (AI)». Thiếu thì "
                "app tự thêm trước khi gửi và nhờ bạn duyệt lại."
            )
    if not alt.strip():
        S[f"altok-{pid}"] = False
    ok_col.checkbox(
        "✅ Đã duyệt",
        key=f"altok-{pid}",
        disabled=not alt.strip(),
        help=(
            "Bạn đã đọc alt và chú thích: đúng với ảnh, không có tên, số điện thoại, địa chỉ của "
            "khách. Sửa chữ thì phải duyệt lại."
        ),
    )
    if not S.get(f"altok-{pid}"):
        S.pop(f"altsha-{pid}", None)
    elif digest and f"altsha-{pid}" not in S:
        S[f"altsha-{pid}"] = digest  # bản ảnh đang hiện (xem trước, dòng GPS) là bản được duyệt
    if PHONE_LIKE.search(alt) or PHONE_LIKE.search(caption):
        row.warning(
            "Alt hoặc chú thích có dãy số giống số điện thoại. Đừng để số điện thoại, số nhà, "
            "biển số xe lên website."
        )


# ----- chọn ảnh từ thư mục -------------------------------------------------------------------


def moved() -> None:
    """Đã sang thư mục khác: ô «Thư mục con» lấy khóa mới (``sub_key``), nên trình duyệt vẽ ô
    trống, không giữ lựa chọn của thư mục trước (lựa chọn đó không có trong danh sách mới)."""
    S._browse_nav = S.get("_browse_nav", 0) + 1


def sub_key() -> str:
    return f"_browse_sub_{S.get('_browse_nav', 0)}"


def open_browser(pid: int) -> None:
    last = S.get("_last_place", {"root": 0, "dir": ""})
    S._browse = {"pid": pid, "root": last["root"], "dir": last["dir"], "page": 1}
    moved()


def open_image_folder(pid: int) -> None:
    """Mở thư mục chứa ảnh đã chọn: đi từ thư mục gốc xuống (``walk_to_folder``, LC-T055-1)."""
    checked: CheckedImage | None = S.get(f"pick-{pid}")
    if checked is None:
        return
    ref = checked.ref
    S._browse = {
        "pid": pid,
        "root": ref.root_index,
        "dir": "",
        "page": 1,
        "walk": list(ref.parts[:-1]),
    }
    moved()


def close_browser() -> None:
    S.pop("_browse", None)
    moved()


def go_to(rel_dir: str) -> None:
    S._browse.update(dir=rel_dir, page=1)
    moved()


def go_root() -> None:
    S._browse.update(root=S["_browse_root"], dir="", page=1)
    moved()


def go_sub(key: str) -> None:
    target = S.get(key)
    if target:
        go_to(target)


def go_page(delta: int) -> None:
    S._browse["page"] = max(1, S._browse["page"] + delta)


def rescan() -> None:
    place = (S._browse["root"], S._browse["dir"])
    S._scans = {key: value for key, value in S.get("_scans", {}).items() if key[:2] != place}


def folder_listing(
    library: ImageLibrary, root: int, rel_dir: str, page: int
) -> FolderListing | str | None:
    """Một trang của thư mục: quét trong luồng riêng, giữ kết quả trong phiên. Chỉ được gọi khi
    người dùng mở thư mục hay bấm quét lại. ``None``: ổ chậm, lần quét còn chạy ở nền; chữ: lỗi."""
    key = (root, rel_dir, page)
    scans = S.setdefault("_scans", {})
    if key in scans:
        return scans[key]
    pending = S.get("_scan_pending")
    if pending is not None and pending[0] == key:
        future = pending[1]
    else:
        future = _scan_pool().submit(
            library.list_folder, root, rel_dir, page=page, page_size=BROWSE_PAGE_SIZE
        )
    try:
        with st.spinner("Đang xem thư mục…"):
            result = future.result(timeout=SCAN_WAIT_SECONDS)
    except TimeoutError:
        S._scan_pending = (key, future)
        return None
    except ImageFolderError as exc:
        result = str(exc)
    except Exception:
        result = MSG_SCAN_FAILED
    if S.get("_scan_pending", (None,))[0] == key:  # chỉ bỏ lần chờ của chính thư mục này
        S.pop("_scan_pending")
    while len(scans) >= MAX_SCANS_KEPT:
        scans.pop(next(iter(scans)))
    scans[key] = result
    if isinstance(result, FolderListing) and result.rel_dir != rel_dir:
        scans[(root, result.rel_dir, page)] = result  # tên trên ổ (T-076)
    return result


def walk_to_folder(library: ImageLibrary, browse: dict) -> None:
    """«Mở thư mục chứa ảnh»: đi từ thư mục gốc xuống qua ``SubFolder.rel_path`` của chính các lần
    quét (LC-T055-1): tên trùng hẳn trước; trùng không phân biệt hoa thường chỉ khi có đúng một và
    danh sách không bị cắt. Danh sách bị cắt (thư mục hơn 5.000 mục, quét quá giờ) mà chưa thấy thì
    mở thẳng phần còn lại: ``list_folder`` trả tên trên ổ (T-076), ảnh chọn ở đó vẫn qua
    ``check_chosen_image`` như mọi ảnh."""
    names = browse.pop("walk")
    root, current = browse["root"], ""
    for index, name in enumerate(names):
        listing = folder_listing(library, root, current, 1)
        if not isinstance(listing, FolderListing):
            break
        current = listing.rel_dir
        found = next((sub for sub in listing.subfolders if sub.name == name), None)
        if found is None and not listing.truncated:
            same = [sub for sub in listing.subfolders if _name_key(sub.name) == _name_key(name)]
            found = same[0] if len(same) == 1 else None
        if found is None:
            if listing.truncated:
                target = folder_listing(
                    library, root, "/".join([current, *names[index:]]).strip("/"), 1
                )
                if isinstance(target, FolderListing):
                    current = target.rel_dir
            break
        current = found.rel_path
    browse.update(dir=current, page=1)


def skipped_text(listing: FolderListing) -> str:
    labels = {
        "links": "lối tắt",
        "hidden": "mục ẩn",
        "bad_names": "tên có ký tự lạ",
        "other_files": "file không phải ảnh",
        "empty": "file rỗng",
        "too_large": "ảnh quá lớn",
        "unreadable": "mục không đọc được",
        "too_deep": "thư mục quá sâu",
    }
    skipped = listing.skipped
    parts = [
        f"{getattr(skipped, name)} {label}"
        for name, label in labels.items()
        if getattr(skipped, name)
    ]
    return f"Bỏ qua: {', '.join(parts)}." if parts else ""


def folder_browser(library: ImageLibrary, pid: int) -> None:
    browse = S._browse
    with st.container(border=True, key="imgbrowser"):
        head, close = st.columns([5, 1], vertical_alignment="center")
        head.markdown("**📁 Chọn ảnh từ thư mục**")
        close.button("✖ Đóng", key="browse-close", on_click=close_browser, width="stretch")
        roots = library.roots()
        if not roots:
            st.info("Chưa khai báo thư mục ảnh: điền IMAGE_FOLDERS trong file .env (xem README).")
            return
        if not 0 <= browse["root"] < len(roots):
            browse.update(root=0, dir="", page=1)
        notes = root_notes(library)
        S["_browse_root"] = browse["root"]
        st.selectbox(
            "Thư mục ảnh",
            [root.index for root in roots],
            format_func=lambda i: (
                shown_name(roots[i].label)
                + ("" if roots[i].available else " (không thấy trên máy này)")
            ),
            key="_browse_root",
            on_change=go_root,
        )
        root = roots[browse["root"]]
        ai_root, via_link = notes.get(root.index, (False, False))
        if via_link:
            st.warning(
                "Thư mục ảnh này đi qua lối tắt (symlink/junction): app đọc thư mục mà lối tắt trỏ "
                "tới. Hãy chắc đó đúng là thư mục ảnh bạn muốn (khai báo thẳng ổ đĩa, ví dụ E:/, "
                "thì không bị)."
            )
        if not root.available:
            st.warning(escape_markdown(root.message))
            return
        if ai_root:
            st.caption(
                "🤖 Mọi ảnh trong thư mục gốc này là ảnh AI (tên thư mục có chữ AI hoặc tên công "
                "cụ tạo ảnh)."
            )
        if "walk" in browse:
            walk_to_folder(library, browse)
        listing = folder_listing(library, root.index, browse["dir"], browse["page"])
        if listing is None:
            st.info(
                "Ổ đĩa đang chậm (Google Drive?): app vẫn đang quét thư mục này ở nền. Đợi vài "
                "giây rồi bấm «Xem kết quả»."
            )
            st.button("🔄 Xem kết quả", key="scan-wait")
            return
        nav = st.container(horizontal=True, gap="small", vertical_alignment="center")
        if browse["dir"]:
            parent = browse["dir"].rpartition("/")[0]
            nav.button("⬆ Lên một cấp", key="browse-up", on_click=go_to, args=(parent,))
        nav.button("🔄 Quét lại", key="browse-rescan", on_click=rescan)
        if isinstance(listing, str):
            st.warning(escape_markdown(listing))
            return
        browse.update(dir=listing.rel_dir, page=listing.page)
        S._last_place = {"root": root.index, "dir": listing.rel_dir}
        st.caption(f"Đang xem: {place_md(root.label, listing.rel_dir)}")
        if listing.notice:
            st.warning(escape_markdown(listing.notice))
        if skipped_text(listing):
            st.caption(skipped_text(listing))
        if listing.subfolders:
            names = {sub.rel_path: shown_name(sub.name) for sub in listing.subfolders}
            st.selectbox(
                f"Thư mục con ({len(names)})",
                list(names),
                format_func=names.get,
                index=None,
                placeholder="Chọn một thư mục con để mở…",
                key=sub_key(),
                on_change=go_sub,
                args=(sub_key(),),
            )
        if not listing.images:
            st.caption("Thư mục này không có ảnh dùng được (ảnh có thể nằm trong thư mục con).")
            return
        image_grid(library, pid, listing, ai_root)
        if listing.page_count > 1:
            back, info, forward = st.columns([1, 2, 1], vertical_alignment="center")
            back.button(
                "← Trang trước",
                key="page-prev",
                on_click=go_page,
                args=(-1,),
                disabled=not listing.has_previous_page,
                width="stretch",
            )
            info.caption(f"Trang {listing.page}/{listing.page_count} · {listing.total_images} ảnh")
            forward.button(
                "Trang sau →",
                key="page-next",
                on_click=go_page,
                args=(1,),
                disabled=not listing.has_next_page,
                width="stretch",
            )


def image_grid(library: ImageLibrary, pid: int, listing: FolderListing, ai_root: bool) -> None:
    """Một trang ảnh: ảnh xem trước, tên (đã cô lập hướng chữ, escape), dấu ảnh AI, nút Chọn.
    Thẻ đọc bằng ``resolve_many`` cho đúng trang này (tối đa ``BROWSE_PAGE_SIZE`` ≤ 200 ảnh,
    SL-T074-1). Không gợi ý alt cho ảnh nào ở đây (ảnh chưa chọn không rời máy, A3)."""
    store = tag_store()
    resolved = store.resolve_many([entry.ref for entry in listing.images])
    note_tag_store(store)
    marked = S.get("_ai_marked", set())
    columns = st.columns(BROWSE_COLUMNS)
    with st.spinner("Đang tạo ảnh xem trước…"):
        for i, entry in enumerate(listing.images):
            with columns[i % BROWSE_COLUMNS]:
                data, error = preview_bytes(library, entry.ref)
                if data is not None:
                    st.image(data, alt=f"Ảnh xem trước số {i + 1}", width="stretch")
                else:
                    st.markdown('<div class="img-ph">⚠️</div>', unsafe_allow_html=True)  # cố định
                    st.caption(escape_markdown(error))
                st.caption(name_md(entry.name))
                if resolved[entry.ref].tags.is_ai or ai_root or entry.ref in marked:
                    st.markdown(":violet-badge[🤖 Ảnh AI]")
                st.button(
                    "Chọn",
                    key=f"choose-{i}",
                    on_click=choose_image,
                    args=(pid, entry, listing.images),
                    disabled=data is None,
                    width="stretch",
                )


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
    drafts_panel()
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


def quote_ai_text(text: str) -> str:
    """Hiện chữ AI dạng trích dẫn Markdown mà không tạo được link.

    Câu AI chỉ ra là một đoạn con của bài, có thể bắt đầu giữa dòng (vd. "[nhãn]: …"); thêm
    "> " đưa nó về đầu dòng nên phải escape lại cú pháp link SAU khi thêm "> " (Soi Lỗi R4-1).
    Mỗi dòng của câu nhiều dòng đều nằm trong trích dẫn. Chỉ dùng để hiển thị: khi Áp dụng /
    Bỏ qua vẫn dùng câu gốc để khớp với bài.
    """
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return escape_link_syntax("\n".join(f"> {line}" if line else ">" for line in lines))


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
            st.markdown(quote_ai_text(sentence))
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


# ----- bước SEO (T-041) -----------------------------------------------------------------------
#
# Logic ở ``seo_app/onpage`` (Thợ Máy); ở đây chỉ nối giao diện. Chữ lấy từ website (tiêu đề bài
# đã đăng trong câu báo kiểm trùng, cột «Trỏ tới bài») và chữ AI chỉ hiện bằng chữ thuần
# (``escape_markdown``, ô bảng, ``st.code``), không bao giờ qua ``unsafe_allow_html`` (U1; điều kiện
# Lá Chắn T-036 số 5, T-037, T-039 2c). Schema FAQ chỉ hiện bằng ``st.code`` (Lá Chắn T-038 đk 3).

SEO_LABELS = {"title": "Meta title", "description": "Meta description"}
LEVEL_BADGES = {
    onpage_meta.Level.GOOD: ("green", "Nên"),
    onpage_meta.Level.WARN: ("orange", "Cảnh báo"),
    onpage_meta.Level.BLOCK: ("red", "Chặn"),
}
# ``select_candidates`` luôn báo câu này khi bài hướng dẫn chưa có phiếu giao bài; app chưa nhập
# phiếu giao bài nên chủ dự án không làm gì được với câu này: không hiện (góp ý G4 Soi Lỗi T-041).
NO_ORDER_NOTICE = "Bài hướng dẫn chưa có trang dịch vụ đích (ghi trong phiếu giao bài)."
COPY_LABELS = ("Tiêu đề SEO", "Mô tả SEO", "Đường dẫn (slug)")
MSG_SEO_RECHECK = "Kiểm lại ngay sau khi ghi SEO:"
MSG_SEO_WILL_SKIP = "Sẽ không ghi {fields}: ở bước SEO đang báo «Chặn» (xem lý do ở đó)."
MSG_SEO_SKIPPED = (
    "Không ghi {fields}: ở bước SEO đang báo «Chặn». Sửa ở bước SEO rồi chép tay vào hộp SiteSEO."
)
MSG_SEO_UNEXPECTED = (
    "Ghi SEO lên website gặp lỗi không mong đợi. Mở bài nháp trong WordPress kiểm hộp SiteSEO, "
    "hoặc chép tay tiêu đề, mô tả ở bước SEO."
)


@st.cache_resource(show_spinner=False)
def _site_store_at(path: str) -> site_storage.SiteIndexStore:
    return site_storage.SiteIndexStore(Path(path))


def site_store() -> site_storage.SiteIndexStore:
    # Đọc đường dẫn lúc chạy (không lúc import) để test trỏ được file cache sang thư mục tạm.
    return _site_store_at(str(site_storage.DEFAULT_SITE_INDEX_FILE))


def ask_reload_listing() -> None:
    S._reload_listing = True


def published_listing() -> site_storage.SiteListing:
    """Danh sách bài đã đăng (kiểm trùng, liên kết nội bộ), giữ trong phiên. Lần đầu và khi bấm
    «Tải lại danh sách bài» thì hỏi kho cache / website. Chưa kết nối WordPress hay tải lỗi: câu báo
    nhẹ, các phần khác của bước SEO vẫn dùng được."""
    refresh = bool(S.pop("_reload_listing", False))
    if refresh or "_site_listing" not in S:
        client, _problem = wordpress_client()
        with st.spinner("Đang tải danh sách bài đã đăng trên website…"):
            S._site_listing = site_storage.site_listing(site_store(), client, refresh=refresh)
    return S._site_listing


def brand_suffix() -> str | None:
    """Đuôi thương hiệu trong mục ``[meta]`` của config/content.toml; mục sai thì đuôi mặc định
    (lỗi hiện ở nút AI gợi ý meta, như ``alt_limits``)."""
    try:
        return load_meta_rules().brand_suffix
    except AIError:  # ContentRulesError
        return None


def meta_versions(field: str) -> list[str]:
    return S.get(f"seo_{field}_versions", [])


def meta_index(field: str) -> int:
    return S.get(f"seo_{field}_ver", 0)


def meta_text(field: str) -> str:
    """Bản đang dùng của ô meta (title chưa gắn đuôi thương hiệu)."""
    versions = meta_versions(field)
    index = meta_index(field)
    return versions[index] if 0 <= index < len(versions) else ""


def set_meta_versions(field: str, versions: list[str], current: int) -> None:
    """Các bản của một ô meta, qua ``DraftMetaVersions`` như lúc lưu nháp (chuẩn hóa chữ, tối đa
    20 bản, không bao giờ bỏ bản đang dùng), rồi đưa bản đang dùng vào ô sửa. Gọi trước khi vẽ ô."""
    kept = DraftMetaVersions(versions=versions, current=current)
    S[f"seo_{field}_versions"] = kept.versions
    S[f"seo_{field}_ver"] = kept.current
    S[f"seo_{field}"] = kept.text


def add_meta_versions(field: str, texts: list[str]) -> None:
    """Thêm bản mới (gợi ý AI, chữ người dùng sửa), dùng bản mới đầu tiên; bản cũ để quay lại."""
    versions = meta_versions(field)
    set_meta_versions(field, [*versions, *texts], len(versions))


def meta_edited(field: str) -> None:
    """Người dùng sửa ô meta: chữ sửa thành một bản mới (vẫn quay lại được bản trước)."""
    text = S.get(f"seo_{field}", "")
    if text != meta_text(field):
        add_meta_versions(field, [text])


def meta_step(field: str, delta: int) -> None:
    """↶ / ↷: về bản trước, tới bản sau."""
    versions = meta_versions(field)
    if versions:
        index = min(max(meta_index(field) + delta, 0), len(versions) - 1)
        set_meta_versions(field, versions, index)


def suggest_meta(writer: ContentWriter, which: str) -> None:
    """AI gợi ý meta (``which``: "title", "description" hay "both"; viết lại riêng một ô thì ô kia
    giữ nguyên). Gợi ý đã qua bộ kiểm của ``ContentWriter.meta``; gợi ý đạt thành các bản mới."""
    suffix = brand_suffix()
    result = ai_call(
        "AI đang gợi ý meta…",
        writer.meta,
        keyword(),
        S.article_title,
        current_parts(),
        which,
        current_title=meta_text("title"),
        current_description=meta_text("description"),
    )
    if result is None:
        return
    if result.titles:  # đã gắn đuôi khi còn chỗ: ô sửa giữ title chưa gắn đuôi
        add_meta_versions("title", [onpage_meta.strip_brand(t, suffix) for t in result.titles])
    if result.descriptions:
        add_meta_versions("description", list(result.descriptions))
    st.rerun()  # nút ↶ ↷, số bản đã vẽ theo trạng thái cũ


def check_lines(*checks: onpage_meta.FieldCheck, length: int | None = None) -> None:
    """Huy hiệu mức chung (Nên / Cảnh báo / Chặn, kèm số ký tự nếu có) và từng câu báo. Câu báo
    kiểm trùng có tên bài lấy từ website: chữ thuần qua ``escape_markdown`` (LC-T036 số 5)."""
    color, name = LEVEL_BADGES[onpage_meta.worst(check.level for check in checks)]
    count = "" if length is None else f" · {length} ký tự"
    st.markdown(f":{color}-badge[{name}{count}]")
    for check in checks:
        for message in check.messages:
            st.caption(escape_markdown(message))


def meta_field(
    writer: ContentWriter | None, field: str, posts: list, suffix: str | None
) -> onpage_meta.FieldCheck:
    """Một ô meta: ô sửa, 🔄 AI viết lại riêng ô này, ↶ ↷ bản trước/sau, đếm ký tự theo chữ sẽ lên
    Google (title tính cả đuôi thương hiệu), kiểm trùng với bài đã đăng. Trả kết quả kiểm."""
    label = SEO_LABELS[field]
    count = len(meta_versions(field))
    box, tools = st.columns([5, 2], vertical_alignment="bottom")
    with tools, st.container(horizontal=True, gap="small"):  # nút vẽ trước ô (đổi được chữ ô)
        rewrite = st.button(
            "🔄", key=f"seo-ai-{field}", disabled=writer is None, help=f"AI viết lại {label}"
        )
        st.button(
            "↶",
            key=f"seo-undo-{field}",
            on_click=meta_step,
            args=(field, -1),
            help="Về bản trước",
            disabled=meta_index(field) == 0,
        )
        st.button(
            "↷",
            key=f"seo-redo-{field}",
            on_click=meta_step,
            args=(field, 1),
            help="Tới bản sau",
            disabled=meta_index(field) >= count - 1,
        )
    if rewrite and writer is not None:
        suggest_meta(writer, field)
    S.setdefault(f"seo_{field}", meta_text(field))
    widget = box.text_input if field == "title" else box.text_area
    options = {} if field == "title" else {"height": 90}
    widget(
        label,
        key=f"seo_{field}",
        on_change=meta_edited,
        args=(field,),
        max_chars=draft_storage.MAX_SEO_TEXT_CHARS,
        **options,
    )
    if len(meta_versions(field)) > 1:
        st.caption(f"Bản {meta_index(field) + 1}/{len(meta_versions(field))}")
    if field == "title":
        check = onpage_meta.check_title(meta_text(field), suffix)
        duplicate = onpage_meta.check_title_duplicates(check.value, posts)
    else:
        check = onpage_meta.check_description(meta_text(field))
        duplicate = onpage_meta.check_description_duplicates(check.value, posts)
    check_lines(check, duplicate, length=check.length)
    return check


def slug_edited() -> None:
    """Slug người dùng gõ: chỉ đổi về dạng không dấu (``make_slug(given=…)``), không cắt từ."""
    raw = S.get("seo_slug", "")
    S.seo_slug = onpage_meta.make_slug("", given=raw) if raw.strip() else ""


def suggest_slug() -> None:
    S.seo_slug = onpage_meta.make_slug(keyword() or sent_title())


def slug_field(posts: list) -> str:
    box, tools = st.columns([5, 2], vertical_alignment="bottom")
    tools.button("🔄", key="seo-slug-suggest", on_click=suggest_slug, help="Gợi ý lại từ từ khóa")
    S.setdefault("seo_slug", onpage_meta.make_slug(keyword() or sent_title()))
    box.text_input(
        "Đường dẫn (slug)",
        key="seo_slug",
        on_change=slug_edited,
        max_chars=draft_storage.MAX_SEO_TEXT_CHARS,
    )
    slug = S.seo_slug
    check_lines(onpage_meta.check_slug(slug), onpage_meta.check_slug_duplicates(slug, posts))
    return slug


def site_host() -> str:
    """Tên miền để xem trước kiểu Google (chỉ để hiện; chưa khai báo WordPress thì chữ mẫu)."""
    return urlsplit(load_settings().wordpress_url).netloc or "website-cua-ban.vn"


def final_seo(posts: list, suffix: str | None) -> list[tuple[str, str | None, str]]:
    """Chữ SEO cuối cùng từng trường (tiêu đề đã gắn đuôi, mô tả, slug), chung cho «Chép sang
    SiteSEO» và «Ghi SEO lên website»: (tên, chữ, lý do). Chữ là ``None`` khi trường bị Chặn: sai
    dạng (``siteseo_copy``) hay trùng hệt bài đã đăng (kiểm trùng cũng ra mức «Chặn»)."""
    slug = S.get("seo_slug", "")
    copy = onpage_meta.siteseo_copy(
        meta_text("title"), meta_text("description"), slug, suffix=suffix
    )
    title, description, _slug = copy.checks
    duplicates = (
        onpage_meta.check_title_duplicates(title.value, posts),
        onpage_meta.check_description_duplicates(description.value, posts),
        onpage_meta.check_slug_duplicates(slug, posts),
    )
    values = (copy.title, copy.description, copy.slug)
    fields: list[tuple[str, str | None, str]] = []
    for label, value, check, duplicate in zip(
        COPY_LABELS, values, copy.checks, duplicates, strict=True
    ):
        if value is None:
            fields.append((label, None, " ".join(check.messages)))
        elif duplicate.level is onpage_meta.Level.BLOCK:
            fields.append((label, None, " ".join(duplicate.messages)))
        else:
            fields.append((label, value, ""))
    return fields


def siteseo_panel(posts: list, suffix: str | None) -> None:
    """Chữ cuối cùng để chép, dán tay vào hộp SiteSEO (khi chưa bật «Ghi SEO lên website»).
    Trường bị Chặn không cho chép, hiện câu báo (có thể có tên bài trên website: chữ thuần)."""
    st.markdown("**Chép sang SiteSEO**")
    st.caption(
        "Bấm biểu tượng ở góc từng khung để chép, rồi dán vào hộp SiteSEO của bài nháp. Muốn phần "
        "mềm tự ghi: bật «Ghi SEO lên website» ở bước Xuất bản."
    )
    for label, value, reason in final_seo(posts, suffix):
        if value is None:
            st.caption(f"{label}: chưa chép được. {escape_markdown(reason)}")
        else:
            st.caption(label)
            st.code(value, language=None, wrap_lines=True)


def links_panel(writer: ContentWriter | None, listing: site_storage.SiteListing) -> None:
    """Liên kết nội bộ: AI gợi ý chỗ đặt link tới bài đã đăng (bài đích do code chọn), bảng «Dùng /
    Cụm từ trong bài / Trỏ tới bài». Không gắn link nào ở đây: link chỉ chèn lúc dựng bài gửi đi
    (``apply_links``, Giai đoạn 5). Không hiện địa chỉ bài."""
    st.markdown("**Liên kết nội bộ** — gợi ý từ các bài đã có trên website")
    candidates = None
    if listing.index is not None:
        candidates = onpage_links.select_candidates(
            listing.index,
            kind=onpage_links.ArticleKind.GUIDE,
            title=sent_title(),
            keyword=keyword(),
        )
        for notice in candidates.notices:
            if notice.message != NO_ORDER_NOTICE:
                st.caption(f"⚠️ {escape_markdown(notice.message)}")
    row = st.container(horizontal=True, gap="small")
    if row.button(
        "✨ AI gợi ý liên kết",
        key="seo-links-ai",
        disabled=writer is None or candidates is None or not candidates.items,
    ):
        review = ai_call(
            "AI đang tìm chỗ đặt liên kết…",
            writer.internal_links,
            S.article_title,
            current_parts(),
            candidates,
        )
        if review is not None:
            S.seo_links = [DraftLink.from_link(link, use=True) for link in review.links]
            S.seo_link_notes = list(review.rejected)
            S.seo_links_nav = S.get("seo_links_nav", 0) + 1  # bảng mới: bỏ lựa chọn cũ
    row.button("🔄 Tải lại danh sách bài", key="seo-reload", on_click=ask_reload_listing)
    if candidates is not None and not candidates.items:
        st.caption("Chưa có bài đã đăng nào cùng chủ đề để đặt liên kết.")
    for note in S.get("seo_link_notes", []):  # câu cố định, không chép chữ AI
        st.caption(escape_markdown(note))
    links: list[DraftLink] = S.get("seo_links", [])
    if not links:  # nói đúng lý do khi nút đang mờ (góp ý 4 của báo cáo Họa Sĩ)
        if writer is None:
            st.caption(
                "Chưa có liên kết nội bộ nào. Nút «AI gợi ý liên kết» đang tắt vì AI chưa dùng "
                "được (xem cảnh báo ở đầu trang)."
            )
        elif candidates is None:
            st.caption(
                "Chưa có liên kết nội bộ nào. Nút «AI gợi ý liên kết» cần danh sách bài đã đăng "
                "trên website (xem dòng báo ở đầu bước SEO)."
            )
        elif candidates.items:
            st.caption("Chưa có liên kết nội bộ nào: bấm «AI gợi ý liên kết».")
        return
    titles = {item.id: item.title for item in listing.index.items} if listing.index else {}
    rows = [
        {
            "Dùng": link.use,
            "Cụm từ trong bài": link.anchor,
            "Trỏ tới bài": titles.get(link.post_id) or f"bài #{link.post_id}",
        }
        for link in links
    ]
    edited = st.data_editor(
        rows,
        hide_index=True,
        disabled=["Cụm từ trong bài", "Trỏ tới bài"],
        key=f"seo_links_table_{S.get('seo_links_nav', 0)}",
    )
    if hasattr(edited, "to_dict"):
        edited = edited.to_dict("records")
    S.seo_links = [
        link if link.use == bool(row["Dùng"]) else link.model_copy(update={"use": not link.use})
        for link, row in zip(links, edited, strict=True)
    ]


def faq_panel() -> None:
    """Schema FAQ dựng từ mục Hỏi đáp của bài: chỉ hiện bằng ``st.code`` (Lá Chắn T-038 đk 3); câu
    báo là chữ cố định (không chép chữ của bài)."""
    with st.expander("Schema (dữ liệu có cấu trúc cho Google)"):
        result = build_article_faq(current_parts())
        for issue in result.issues:
            st.caption(f"⚠️ {escape_markdown(issue.message)}")
        if result.json_ld:
            st.checkbox("Dùng schema Hỏi đáp (FAQ) này cho bài", key="seo_use_faq")
            st.code(result.json_ld, language="json")


def step_seo(writer: ContentWriter | None) -> None:
    listing = published_listing()
    posts = onpage_meta.site_posts(listing.index)
    suffix = brand_suffix()
    if listing.notice:
        st.caption(f"ℹ️ {escape_markdown(listing.notice)}")
    left, right = st.columns([3, 2], gap="large")
    with left:
        empty = not meta_versions("title") and not meta_versions("description")
        if empty and st.button(
            "✨ AI gợi ý tiêu đề và mô tả SEO",
            key="seo-ai-both",
            type="primary",
            disabled=writer is None,
        ):
            suggest_meta(writer, "both")
        title = meta_field(writer, "title", posts, suffix)
        meta_field(writer, "description", posts, suffix)
        slug = slug_field(posts)
    with right:
        st.markdown("**Xem trước trên Google**")
        st.markdown(  # ``serp_preview`` escape mọi chữ (U1)
            ui.serp_preview(title.value, f"{site_host()} › {slug}", meta_text("description")),
            unsafe_allow_html=True,
        )
        siteseo_panel(posts, suffix)
    links_panel(writer, listing)
    faq_panel()
    st.divider()
    a, b = st.columns([1, 4])
    a.button("← Viết & kiểm tra", on_click=go, args=(2,))
    b.button("Tiếp: xuất bản →", type="primary", on_click=go, args=(4,))


def seo_snapshot() -> DraftSeo:
    """Lựa chọn ở bước SEO → nháp (tự lưu như bước 1–3)."""
    return DraftSeo(
        title=DraftMetaVersions(versions=meta_versions("title"), current=meta_index("title")),
        description=DraftMetaVersions(
            versions=meta_versions("description"), current=meta_index("description")
        ),
        slug=S.get("seo_slug", ""),
        links=list(S.get("seo_links", [])),
        use_faq=bool(S.get("seo_use_faq", False)),
    )


def restore_seo(seo: DraftSeo) -> None:
    """Nháp → bước SEO. Phần SEO hỏng trong file đã thành trống (``DraftSeo``); chữ vẫn được kiểm
    lại bằng ``seo_app.onpage`` mỗi lần hiện."""
    for field, versions in (("title", seo.title), ("description", seo.description)):
        if versions.versions:
            S[f"seo_{field}_versions"] = list(versions.versions)
            S[f"seo_{field}_ver"] = versions.current
    if seo.slug:
        S.seo_slug = seo.slug
    if seo.links:
        S.seo_links = list(seo.links)
    S.seo_use_faq = seo.use_faq


def seo_request() -> dict | None:
    """Chữ SEO sẽ ghi vào hộp SiteSEO sau khi tạo nháp (công tắc «Ghi SEO lên website» bật): đúng
    chữ của «Chép sang SiteSEO» (``final_seo``: title đã gắn đuôi bằng ``with_brand``; trường bị
    Chặn, kể cả vì trùng bài đã đăng, thì không ghi và ghi tên vào ``skipped``), kèm từ khóa chính.
    Lấy trước khi gửi (đọc ``st.session_state``)."""
    if not S.get("seo_write"):
        return None
    listing = published_listing()
    title, description, _slug = final_seo(onpage_meta.site_posts(listing.index), brand_suffix())
    return {
        "fields": {
            "title": title[1] or "",
            "description": description[1] or "",
            "focus_keyword": keyword(),
        },
        "skipped": [label for label, value, _reason in (title, description) if value is None],
    }


def seo_check() -> tuple[bool, str]:
    """Dòng SEO trong «Kiểm tra trước khi gửi» ở bước Xuất bản (thay dòng demo). Không tải danh
    sách bài ở đây (chỉ xem bước Xuất bản thì không gọi website): kiểm trùng theo danh sách đã tải
    ở bước SEO trong phiên, nếu có."""
    listing = S.get("_site_listing")
    posts = onpage_meta.site_posts(listing.index) if listing is not None else []
    fields = final_seo(posts, brand_suffix())
    missing = [label for label, value, _reason in fields if value is None]
    if missing:
        return False, f"SEO: {', '.join(missing)} chưa dùng được (xem bước SEO)"
    return True, "SEO: tiêu đề, mô tả, đường dẫn đã sẵn sàng"


def seo_toggle() -> None:
    """Công tắc «Ghi SEO lên website» ở bước Xuất bản, mặc định tắt (Lá Chắn T-042). Bật thì báo
    trước trường nào sẽ không ghi (đang bị Chặn ở bước SEO)."""
    st.toggle(
        "Ghi SEO lên website",
        key="seo_write",
        help=(
            "Bật: ngay sau khi tạo bài nháp, phần mềm ghi tiêu đề SEO, mô tả SEO, từ khóa chính "
            "(như ở bước SEO) vào hộp SiteSEO của chính bài nháp đó. Tắt: chép tay ở bước SEO."
        ),
    )
    request = seo_request()
    if request and request["skipped"]:
        st.caption(escape_markdown(MSG_SEO_WILL_SKIP.format(fields=", ".join(request["skipped"]))))


def write_seo(client: WordPressClient, holder: dict) -> None:
    """Ghi SEO vào hộp SiteSEO của bài nháp **vừa tạo bằng chính client này** (điều kiện Lá Chắn
    T-042: chỉ khi bật công tắc; không nạp mã bài nào vào client, không dùng mã bài ghi trong nháp
    (T-086 Ghi nhận 2); client không giữ trong ``st.cache_resource``). Chạy trong
    ``send_and_record``: không đọc/ghi ``st.session_state``. Ghi qua Abilities xong thì hỏi lại bài
    còn là nháp không (LC-T042-2). Kết quả là câu tiếng Việt cố định của client, hiện chữ thường."""
    request, result = holder.get("seo"), holder.get("result")
    if not request or not result or not result.get("ok"):
        return
    post_id = result["post_id"]
    try:
        seo = client.set_seo_meta(post_id, **request["fields"])
        message = seo.message
        if seo.written and seo.route == "abilities":
            try:
                # Hàm riêng của client: hỏi lại site bài còn là nháp (không có hàm công khai;
                # phiếu sửa client sau nên mở hàm này ra).
                client._own_draft(post_id)
            except WordPressError as exc:
                message = f"{message} {MSG_SEO_RECHECK} {exc}"
    except WordPressError as exc:
        message = str(exc)
    except Exception:  # lỗi lạ: bài nháp đã tạo và đã ghi vào nháp, chỉ báo phần SEO
        message = MSG_SEO_UNEXPECTED
    if request["skipped"]:
        message = f"{message} {MSG_SEO_SKIPPED.format(fields=', '.join(request['skipped']))}"
    result["seo"] = message


def sent_text(text: str) -> str:
    """Chữ trong session (đã escape link, có ký tự ngắt rộng 0 của T-031) → chữ gửi WordPress."""
    return unescape_link_syntax(unbreak_autolinks(text))


def sent_line(text: str) -> str:
    return " ".join(sent_text(text).split())


def sent_title() -> str:
    return sent_line(S.article_title or S.outline_title or keyword())


def image_spots() -> list[int]:
    return [pid for pid in S.part_ids if S.get(f"img-{pid}")]


def part_name(pid: int) -> str:
    return sent_line(S[f"heading-{pid}"])


def article_parts(uploads: dict[int, WordPressImage]) -> list[str | WordPressImage]:
    """Nội dung gửi WordPress theo thứ tự: tiêu đề mục (``<h2>``), đoạn văn, rồi ảnh của mục.

    Thân bài là Markdown; ở đây mỗi đoạn thành một ``<p>`` chữ thường (``paragraphs_to_html``
    escape mọi ký tự HTML; cả bài còn qua ``sanitize_html`` khi tạo nháp). Chuyển định dạng
    Markdown (đậm, gạch đầu dòng) sang HTML là việc của Giai đoạn 5.
    """
    parts: list[str | WordPressImage] = []
    for index, pid in enumerate(S.part_ids):
        if index > 0:
            parts.append(f"<h2>{html.escape(part_name(pid))}</h2>")
        body = paragraphs_to_html(sent_text(current_text(pid)))
        if body:
            parts.append(body)
        if pid in uploads:
            parts.append(uploads[pid])
    return parts


def shortcode_findings(ready: list[int]) -> list[tuple[str, str]]:
    """(chỗ, đoạn) dạng shortcode trong mọi chữ sẽ gửi (LC-T061-4): tiêu đề bài, tiêu đề mục, nội
    dung, alt và chú thích của ảnh sẽ gửi, đúng như chữ sẽ tới WordPress (đã gỡ ký tự ngắt, escape
    link). App không gửi đoạn trích nên không xét.

    Nội dung gửi WordPress là một chuỗi (``article_parts``): «[» mở ở mục này, «]» ở mục sau (hay ở
    alt, chú thích của ảnh) vẫn là shortcode. Nên xét thêm cả nội dung ghép theo đúng thứ tự gửi và
    liệt kê các đoạn chưa thấy khi xét từng phần (SL-T056-3)."""
    found: list[tuple[str, str]] = []

    def scan(where: str, text: str) -> None:
        found.extend((where, segment) for segment in find_shortcodes(text))

    scan("Tiêu đề bài", sent_title())
    content: list[str] = []  # chữ của nội dung, đúng thứ tự gửi (không có thẻ HTML)
    for index, pid in enumerate(S.part_ids):
        name = part_name(pid)
        body = sent_text(current_text(pid))
        if index > 0:
            scan(f"Tiêu đề mục «{name}»", name)
            content.append(name)
        scan(f"Nội dung mục «{name}»", body)
        content.append(body)
        if pid in ready:
            texts = DraftImage(**slot_texts(pid))  # lọc như lúc gửi
            alt, caption = plain_image_text(texts.alt), plain_image_text(texts.caption)
            scan(f"Alt ảnh ở mục «{name}»", alt)
            scan(f"Chú thích ảnh ở mục «{name}»", caption)
            content += [alt, caption]
    seen = {segment for _where, segment in found}
    for segment in find_shortcodes("\n".join(content)):
        if segment not in seen:
            found.append(("Nội dung, vắt qua nhiều mục", segment))
    return found


def wordpress_client(write_seo: bool = False) -> tuple[WordPressClient | None, str]:
    """Client mới mỗi lần gọi (không ``st.cache_resource``: điều kiện Lá Chắn T-042). ``write_seo``:
    công tắc «Ghi SEO lên website» (mặc định tắt)."""
    try:
        return WordPressClient.from_settings(load_settings(), write_seo=write_seo), ""
    except WordPressError as exc:
        return None, str(exc)


def send_draft(client: WordPressClient, ready: list[int], previous_post: int | None) -> None:
    """Gửi bài nháp kèm ảnh. **Chỉ chạy khi người dùng bấm «Gửi nháp»** (Lá Chắn T-054 4b).

    - Ngay trước khi tải, kiểm lại từng ảnh (``check_chosen_image``, LC-T055-2) và dùng đúng ảnh đã
      xem trước (cùng ``ref``). Ảnh không còn dùng được, đổi tên/thư mục, hay vừa thành ảnh AI
      (alt phải thêm «Minh họa», duyệt lại) thì dừng: chưa gửi gì.
    - Byte đọc để tải phải cùng băm SHA-256 với bản đã xem và duyệt (``altsha-<id>``); khác (file
      bị thay cùng tên, kể cả cùng cỡ và giờ sửa, kể cả sau lần kiểm lại ở trên) thì cũng dừng, bắt
      xem và duyệt lại (T-086, SL-T056-10, Ghi nhận 1 của Lá Chắn T-056).
    - ``DraftImage(web, alt, caption, tags=<thẻ đã kiểm của chính ảnh đó>, featured)`` (Lá Chắn
      T-071 điều kiện 3a): ảnh AI mang ``ImageTags(source="ai")``.
    - Một ảnh đặt ở hai chỗ, cùng alt và chú thích: dùng lại cùng một đối tượng (chỉ tải một lần).
    - Gửi bằng ``send_and_record`` (ghi «đang gửi» vào nháp, gửi, ghi kết quả vào đối tượng giữ kết
      quả và vào nháp, không có chỗ dừng nào ở giữa), rồi ``apply_send``. Lỗi hiện đủ
      (``send_result``); không rõ kết quả thì khóa nút tới khi người dùng xác nhận đã kiểm trang
      quản trị. Không bao giờ tự gửi lại.
    """
    library = image_library()
    try:
        settings = load_image_settings() if ready else None
    except AIError as exc:  # ContentRulesError: mục [images] của config/content.toml sai
        S._wp_result = {"ok": False, "message": f"{exc} Chưa gửi gì lên website."}
        return
    problems: list[str] = []
    fresh_by_pid: dict[int, CheckedImage] = {}
    with st.spinner("Đang kiểm lại ảnh…"):
        for pid in ready:
            checked: CheckedImage = S[f"pick-{pid}"]
            fresh, image = recheck(library, pid, checked)
            if isinstance(fresh, str):  # ổ chậm, lỗi lạ: câu báo
                problems.append(f"Ảnh ở mục «{part_name(pid)}»: {fresh}")
            elif not fresh.available:
                set_pick(pid, fresh)
                problems.append(f"Ảnh ở mục «{part_name(pid)}»: {fresh.message}")
            elif changed(fresh, image, checked):
                set_pick(pid, fresh)
                if file_changed(fresh, checked):
                    # File không còn là ảnh đã xem, đã duyệt alt (SL-T056-2): xem lại, duyệt lại.
                    S[f"altok-{pid}"] = False
                problems.append(
                    f"Ảnh ở mục «{part_name(pid)}» vừa thay đổi (tên, thư mục, file bị thay bằng "
                    "ảnh khác cùng tên, hay thành ảnh AI), hoặc alt, chú thích của ảnh AI vừa được "
                    "thêm «Minh họa». Xem lại ảnh, alt rồi duyệt ở bước Viết & kiểm tra."
                )
            else:
                fresh_by_pid[pid] = fresh
    featured = S.get("_featured")
    featured_ref = fresh_by_pid[featured].ref if featured in fresh_by_pid else None
    built: dict[tuple, WordPressImage] = {}
    digests: dict[tuple, str] = {}  # băm byte đã đọc để tải, theo ảnh của ``built``
    uploads: dict[int, WordPressImage] = {}
    with st.spinner("Đang nén ảnh WebP (giữ vị trí GPS)…"):
        for pid, fresh in fresh_by_pid.items():
            key = (fresh.ref, fresh.image.alt, fresh.image.caption)
            try:
                data = None
                if key not in built:
                    data = library.read_image_bytes(fresh.ref)
                    digests[key] = content_hash(data)
                approved = S.get(f"altsha-{pid}")
                if approved is not None and digests[key] != approved:
                    replaced_after_approval(library, pid, fresh)
                    problems.append(f"Ảnh ở mục «{part_name(pid)}»: {MSG_FILE_REPLACED}.")
                    continue
                if data is not None:
                    web = make_web_image(
                        data, max_edge_px=settings.max_edge_px, webp_quality=settings.webp_quality
                    )
                    is_featured = fresh.ref == featured_ref and not any(
                        item.featured for item in built.values()
                    )
                    built[key] = WordPressImage(
                        web,
                        alt=fresh.image.alt,
                        caption=fresh.image.caption,
                        tags=fresh.tags,
                        featured=is_featured,
                    )
            except (ImageFolderError, ImageProcessError) as exc:
                problems.append(f"Ảnh ở mục «{part_name(pid)}»: {exc}")
                continue
            except Exception:
                problems.append(f"Ảnh ở mục «{part_name(pid)}»: {MSG_IMAGE_FAILED}")
                continue
            uploads[pid] = built[key]
    if problems:
        S._wp_result = {"ok": False, "message": "Chưa gửi gì lên website.", "problems": problems}
        return
    # Mọi thứ cần lấy từ trang lấy **trước** khi đặt dấu «đang gửi»: từ lúc đặt dấu tới lúc kết quả
    # nằm trong ``holder`` không có lần đọc/ghi ``st.session_state`` hay lệnh ``st.*`` nào (chỗ
    # Streamlit dừng lần chạy khi người dùng bấm gì đó; SL-T056-9).
    title, parts = sent_title(), article_parts(uploads)
    draft = S.setdefault("draft_id", new_draft_id())
    holder = {"draft": draft, "result": None, "state": None, "done": threading.Event()}
    holder["seo"] = seo_request()  # T-041: chữ ghi SiteSEO sau khi tạo nháp (công tắc bật)
    store = draft_store()
    with st.spinner("Đang gửi bài nháp và ảnh lên WordPress…", show_time=True):
        S._wp_sending = holder  # chỗ dừng cuối cùng trước khi gửi: dừng ở đây thì chưa gửi gì
        try:
            send_and_record(client, store, holder, title, parts, previous_post)
        finally:
            holder["done"].set()  # cả khi lần chạy bị dừng ngay trong lúc gửi (``finish_send``)
    apply_send(holder, interrupted=False)


def replaced_after_approval(library: ImageLibrary, pid: int, fresh: CheckedImage) -> None:
    """Byte sắp tải khác bản đã xem và duyệt (file bị thay bằng ảnh khác cùng tên, có thể cùng cỡ,
    cùng giờ sửa, hay đúng lúc đang gửi). Như SL-T056-2: khung ảnh chuyển sang file mới (kiểm lại,
    tính lại dòng GPS, ảnh xem trước dựng từ chính file), bỏ «Đã duyệt»."""
    cache = S.get("_web_info", {})
    for key in [key for key in cache if key[0] == fresh.ref]:
        del cache[key]
    S.setdefault("_replaced", set()).add(fresh.ref)
    again, _image = recheck(library, pid, fresh)
    if isinstance(again, CheckedImage):
        set_pick(pid, again)
    S[f"altok-{pid}"] = False
    S.pop(f"altsha-{pid}", None)


def send_and_record(
    client: WordPressClient,
    store: DraftStore,
    holder: dict,
    title: str,
    parts: list[str | WordPressImage],
    previous_post: int | None,
) -> None:
    """Ghi «đang gửi» vào nháp, gửi, rồi ghi kết quả vào ``holder`` (đối tượng giữ kết quả, sửa
    tại chỗ) và vào nháp (T-086: SL-T056-9, -11).

    **Không đọc/ghi ``st.session_state``, không gọi ``st.*``**: đó là các chỗ Streamlit dừng lần
    chạy khi người dùng bấm gì đó. Nên từ lúc ghi «đang gửi» tới lúc kết quả nằm trong ``holder``
    và trong nháp, lần chạy không thể dừng giữa chừng; dừng ở đâu sau đó thì lần chạy sau vẫn có
    kết quả (``finish_send``). Chưa ghi được «đang gửi» thì không gửi: thiếu dấu đó, tải lại trang
    lúc đang gửi là mất khóa chống gửi trùng.
    """
    try:
        store.save_send_state(holder["draft"], SendState.now(pending=True, post_id=previous_post))
    except Exception as exc:
        reason = str(exc) if isinstance(exc, DraftError) else "lỗi không mong đợi"
        holder["result"] = {
            "ok": False,
            "message": (
                f"Chưa gửi gì lên website: chưa ghi được trạng thái gửi vào nháp ({reason}). "
                "Thử lại sau giây lát."
            ),
        }
        holder["state"] = (False, previous_post)
        return
    pending, post_id = True, previous_post
    try:
        result = client.create_draft_with_images(title, parts)
    except DraftImagesError as exc:
        holder["result"] = {
            "ok": False,
            "message": str(exc),
            "uploaded": [(i.file_name, i.source_url, i.edit_link) for i in exc.uploaded],
            "maybe_uploaded": exc.maybe_uploaded,
        }
        pending = exc.maybe_draft
    except WordPressError as exc:  # kiểm sai trước khi gửi: chưa có request nào
        holder["result"] = {"ok": False, "message": str(exc)}
        pending = False
    except Exception:  # lỗi lạ: không biết bài nháp đã lên chưa (vẫn «đang gửi»)
        holder["result"] = {"ok": False, "message": MSG_SEND_UNEXPECTED}
    else:
        holder["result"] = {
            "ok": True,
            "post_id": result.post.id,
            "status": result.post.status,
            "edit_link": result.post.edit_link,
            "uploaded": [(i.file_name, i.source_url, i.edit_link) for i in result.images],
            "message": result.message,
        }
        pending, post_id = False, result.post.id
    holder["state"] = (pending, post_id)
    record_outcome(store, holder)
    write_seo(client, holder)  # T-041: sau khi đã ghi «đã gửi» vào nháp


def record_outcome(store: DraftStore, holder: dict) -> None:
    """Kết quả gửi (``holder["state"]``: còn chưa rõ không, mã bài nháp gần nhất) → nháp. Không
    đọc/ghi ``st.session_state``. Ghi hỏng thì nháp vẫn giữ «đang gửi» (mở lại thì khóa, hướng an
    toàn) và trang báo cho người dùng (``note``)."""
    pending, post_id = holder["state"]
    state = SendState.now(pending=pending, post_id=post_id) if pending or post_id else None
    try:
        store.save_send_state(holder["draft"], state)
    except Exception as exc:
        holder["note"] = str(exc) if isinstance(exc, DraftError) else "lỗi không mong đợi"
    else:
        holder["saved"] = True
        holder.pop("note", None)


def apply_send(holder: dict, *, interrupted: bool) -> None:
    """Kết quả trong ``holder`` → trang. Thứ tự đơn điệu (LC-T056-1): khóa trước, kết quả sau, bỏ
    dấu ``_wp_sending`` sau cùng; dừng ở dòng nào thì dấu còn, lần chạy sau làm lại
    (``finish_send``).

    Lần gửi bị ngắt (``interrupted``): vẫn hiện kết quả đã có (SL-T056-9) nhưng giữ khóa «gửi dở»:
    gửi tiếp phải xác nhận đã kiểm trang quản trị (như SL-T056-1)."""
    result, state = holder.get("result"), holder.get("state")
    unsure = interrupted or state is None or state[0]
    sent = (result is not None and result["ok"]) or (state is not None and state[1] is not None)
    if unsure:
        S._wp_maybe_draft = True
    if sent:
        S._wp_sent = True
    if result is None:  # dừng ngay trong lúc gửi: không có kết quả nào
        S._wp_result = {"ok": False, "message": MSG_SEND_INTERRUPTED}
    else:
        S._wp_result = {**result, "interrupted": interrupted, "note": holder.get("note", "")}
    if not unsure:
        S.pop("_wp_maybe_draft", None)
    S.pop("_wp_sending", None)


def finish_send() -> None:
    """Lần chạy gửi nháp trước bị dừng (người dùng bấm nút khác, bấm đúp, đổi trang lúc đang gửi)
    trước khi kết quả lên trang: dấu ``_wp_sending`` còn. Gọi đầu ``init_state``.

    Thứ tự đơn điệu (LC-T056-1 a): dựng khóa «gửi dở» trước (đúng với mọi kết quả), rồi mới hiện
    kết quả có trong đối tượng giữ kết quả (SL-T056-9) và bỏ dấu sau cùng (``apply_send``).

    Streamlit mặc định chạy lần mới **ngay**, song song với lần đang gửi (``runner.fastReruns``:
    lần cũ chỉ dừng ở chỗ dừng kế tiếp, tức sau khi lệnh gửi xong). Nên lần gửi có thể vẫn đang
    chạy: đợi nó xong (``done``, tối đa ``SEND_WAIT_SECONDS``) rồi mới đọc kết quả; quá giờ thì giữ
    dấu, lần chạy sau đợi tiếp."""
    holder = S.get("_wp_sending")
    if holder is None:
        return
    S._wp_maybe_draft = True
    S._wp_result = {"ok": False, "message": MSG_SEND_INTERRUPTED}
    if not isinstance(holder, dict):  # dấu không kèm đối tượng giữ kết quả
        S.pop("_wp_sending", None)
        return
    done = holder.get("done")
    if done is not None and not done.is_set():
        # Ô thông báo thường (hiện ngay), không dùng st.spinner: vòng quay của Streamlit 1.65 là
        # phần tử tạm, trên trang chưa có phần tử nào thì không thấy (thử trên trình duyệt thật).
        waiting = st.empty()
        waiting.info(MSG_WAIT_SEND, icon="⏳")
        done.wait(SEND_WAIT_SECONDS)
        waiting.empty()
        if not done.is_set():
            S._wp_result = {"ok": False, "message": MSG_STILL_SENDING}
            return
    if holder.get("result") is not None and not holder.get("saved"):
        record_outcome(draft_store(), holder)  # lần trước chưa ghi được kết quả vào nháp: thử lại
    apply_send(holder, interrupted=True)


def saved_send_state() -> tuple[SendState | None, str]:
    """Trạng thái gửi ghi trong nháp đang mở (T-086): (trạng thái, câu lỗi khi không đọc được)."""
    draft_id = S.get("draft_id")
    if not draft_id:
        return None, ""
    try:
        return draft_store().load_send_state(draft_id), ""
    except DraftError as exc:
        return None, str(exc)


def unsure_message(saved: SendState | None, saved_error: str) -> str:
    """Khóa «gửi dở»: lần gửi trước có thể đã tạo bài nháp mà app không chắc."""
    if S.get("_wp_maybe_draft"):
        why = "Lần gửi trước bị lỗi hoặc bị ngắt đúng lúc gửi"
    elif saved_error:
        why = f"Không đọc được trạng thái gửi ghi trong nháp ({saved_error})"
    else:
        why = (
            f"Lần gửi trước (bắt đầu lúc {format_saved(saved.updated_at)}) chưa có kết quả: có thể "
            "vẫn đang gửi ở cửa sổ khác, hoặc đã bị ngắt (tải lại trang, đóng tab, mất mạng)"
        )
    return (
        f"{escape_markdown(why)}: **bài nháp có thể đã có trên website**. Mở trang quản trị "
        "WordPress, kiểm tra Bài viết → Nháp và Media → Thư viện trước khi gửi lại. App không tự "
        "gửi lại."
    )


def sent_message(saved: SendState | None) -> str:
    """Khóa «đã gửi»: gửi lại là thêm một bài nháp nữa."""
    if saved is not None and saved.post_id is not None:
        what = (
            f"Bài này đã gửi lên WordPress (bài nháp mã {saved.post_id}, lúc "
            f"{format_saved(saved.updated_at)})."
        )
    else:
        what = "Bài này đã gửi thành công."
    return (
        f"{escape_markdown(what)} Gửi lại sẽ tạo **thêm một bài nháp mới** và tải ảnh lên lần nữa."
    )


def send_result() -> None:
    """Kết quả lần gửi gần nhất. Mọi chữ từ WordPress hay câu lỗi hiện bằng ``escape_markdown`` hay
    ``st.text`` (Lá Chắn T-054 4c, T-071 3b), không ``unsafe_allow_html``."""
    result = S.get("_wp_result")
    if not result:
        return
    if result["ok"]:
        count = len(result["uploaded"])
        st.success(
            f"Đã tạo bài nháp trên WordPress (mã {result['post_id']})"
            + (f", kèm {count} ảnh." if count else ".")
        )
        if result["status"] != "draft":
            st.error(
                f"WordPress báo bài đang ở trạng thái «{escape_markdown(result['status'])}», "
                "không phải nháp. Mở trang quản trị WordPress kiểm tra ngay."
            )
        st.link_button("Mở bài nháp trong WordPress", result["edit_link"])
        if result["message"]:
            st.warning(escape_markdown(result["message"]))
    else:
        st.error(escape_markdown(result["message"]))
        for problem in result.get("problems", ()):
            st.markdown(f"- {escape_markdown(problem)}")
        if result.get("maybe_uploaded"):
            st.warning(
                "Ảnh đang tải lúc lỗi có thể vẫn đã lên thư viện Media: kiểm tra Media → Thư viện "
                "trong trang quản trị WordPress."
            )
    if result.get("interrupted"):
        st.caption(
            "Lần gửi này bị ngắt giữa chừng (bấm nút khác hoặc bấm đúp lúc đang gửi); trên đây là "
            "kết quả app đã nhận được từ website."
        )
    if result.get("note"):
        st.warning(
            f"Chưa ghi được kết quả gửi vào nháp ({escape_markdown(result['note'])}): mở lại nháp "
            "này sau sẽ thấy nhắc «chưa có kết quả», hãy kiểm trang quản trị trước khi gửi lại."
        )
    if result.get("seo"):  # T-041: kết quả ghi SEO, câu cố định của client
        st.info(escape_markdown(result["seo"]))
    if result.get("uploaded"):
        title = (
            "Ảnh đã lên thư viện Media"
            if result["ok"]
            else "Ảnh đã lên thư viện Media trước khi lỗi (xem được công khai, app không xóa)"
        )
        st.markdown(f"**{title}:**")
        st.text(
            "\n".join(
                f"• {name}\n  {url or '(chưa đọc được địa chỉ ảnh)'}\n  Sửa: {edit}"
                for name, url, edit in result["uploaded"]
            )
        )


def draft_panel() -> None:
    """«Nháp»: gửi bài nháp kèm ảnh lên WordPress (bài luôn là nháp)."""
    if S.get("_wp_reset_guards"):  # bỏ tick trước, bỏ cờ sau (LC-T056-1 b)
        S.pop("_wp_checked", None)
        S.pop("_wp_again", None)
        S.pop("_wp_reset_guards", None)
    client, problem = wordpress_client(write_seo=bool(S.get("seo_write")))
    saved, saved_error = saved_send_state()  # đọc mỗi lần vẽ: mở lại nháp, phiên mới vẫn khóa
    spots = image_spots()
    states = {pid: slot_problem(pid) for pid in spots}
    ready = [pid for pid, state in states.items() if state == ""]
    blocked = [(pid, state) for pid, state in states.items() if state]
    empty = [pid for pid, state in states.items() if state is None]
    if problem:
        st.warning(escape_markdown(problem))
    for pid, state in blocked:
        st.warning(
            f"Ảnh ở mục «{escape_markdown(part_name(pid))}»: {escape_markdown(state)}. Sửa ở "
            "bước Viết & kiểm tra."
        )
    if empty:
        st.caption(f"{len(empty)} chỗ cần ảnh chưa có ảnh: bài gửi đi không có ảnh ở các chỗ đó.")
    if len(ready) > 1:
        if S.get("_featured") not in ready:
            S.pop("_featured", None)
        labels = {pid: f"Ảnh ở mục «{part_name(pid)}»" for pid in ready}
        st.selectbox("Ảnh đại diện", ready, format_func=labels.get, key="_featured")
    findings = shortcode_findings(ready)
    if findings:
        lines = "\n".join(
            f"- {escape_markdown(where)}: {escape_markdown(shorten(segment))}"
            for where, segment in findings
        )
        st.warning(
            "**Có đoạn dạng shortcode** («[» liền chữ, có «]» phía sau). Lúc gửi, app đã vô hiệu "
            "nên đoạn này không chạy, nhưng **WordPress sẽ chạy đoạn này nếu bạn sửa và lưu bài "
            f"trong trang quản trị; nên xóa**:\n\n{lines}"
        )
    allowed = client is not None and not blocked and bool(S.part_ids)
    post_id = saved.post_id if saved is not None else None
    if S.get("_wp_maybe_draft") or saved_error or (saved is not None and saved.pending):
        st.error(unsure_message(saved, saved_error))
        checked = st.checkbox("Tôi đã kiểm tra trang quản trị, vẫn muốn gửi", key="_wp_checked")
        allowed = allowed and checked
    elif S.get("_wp_sent") or post_id is not None:
        st.info(sent_message(saved))
        if post_id is not None and client is not None and not S.get("_wp_result"):
            st.link_button("Mở bài nháp trong WordPress", client.edit_link(post_id))
        again = st.checkbox("Tạo thêm một bài nháp mới", key="_wp_again")
        allowed = allowed and again
    seo_toggle()  # T-041: «Ghi SEO lên website», mặc định tắt (Lá Chắn T-042)
    if ready:
        # Nhắc ngay trước nút (Lá Chắn T-046 số 8, T-054 4b).
        st.warning(GPS_PUBLIC_WARNING)
    clicked = st.button("📤 Gửi nháp", type="primary", disabled=not allowed, width="stretch")
    # Lần bấm thứ hai của một cú bấm đúp tới khi lần chạy trước đã gửi xong: Streamlit vẫn báo nút
    # đã bấm dù lúc này nút được vẽ là khóa. Nên xét lại điều kiện khóa ngay lúc bấm (SL-T056-1).
    if clicked and allowed:
        # Bỏ tick các ô xác nhận trước khi gửi (không phải sau): lần chạy bị dừng giữa chừng thì
        # lần sau vẫn phải xác nhận lại mới gửi tiếp được.
        S._wp_reset_guards = True
        send_draft(client, ready, post_id)
        st.rerun()
    send_result()


def shorten(text: str) -> str:
    return text if len(text) <= MAX_SHOWN_SHORTCODE else f"{text[: MAX_SHOWN_SHORTCODE - 1]}…"


def step_publish() -> None:
    flags = open_flags()
    missing = missing_spots()
    score = overall_score()
    spots = image_spots()
    ready = sum(1 for pid in spots if slot_problem(pid) == "")
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
            (
                ready == len(spots),
                f"Chỗ cần ảnh đã có ảnh, alt đã duyệt: {ready}/{len(spots)}",
            ),
            seo_check(),  # T-041
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
        if mode == "Nháp":
            draft_panel()
        else:
            demo_note("hẹn giờ và đăng ngay sẽ nối ở Giai đoạn 5.")
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
saved_note = st.empty()  # «Đã lưu lúc HH:MM», điền ở cuối trang sau khi tự lưu

store = None
try:
    store = draft_store()
    store.list_drafts(limit=0)  # lần đầu: kiểm file nháp (file hỏng được cất sang một bên)
except DraftError as exc:
    st.warning(str(exc))
if store is not None and store.recovered_from is not None and not S.get("_recovered_noted"):
    S._recovered_noted = True
    st.warning(
        "File nháp cũ bị hỏng nên đã được cất sang một bên "
        f"(tên «{store.recovered_from.name}», cùng thư mục). App bắt đầu file nháp mới."
    )
if "_draft_error" in S:
    st.error(S.pop("_draft_error"))
if "_images_notice" in S:
    st.warning(S.pop("_images_notice"))
note_tag_store(tag_store())

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
    step_seo(writer)
else:
    step_publish()

autosave(saved_note)
remember_inputs()
