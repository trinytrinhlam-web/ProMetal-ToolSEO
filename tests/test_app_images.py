"""Trang Soạn bài: chỗ cần ảnh thật và gửi nháp kèm ảnh (T-056, G3-10).

Mỗi test gắn với một điều kiện trong mục "Ghi chú của Chỉ Huy" của phiếu
``docs/team/tickets/T-056-giao-dien-cho-can-anh.md`` (bảng "điều kiện → test" trong
``docs/team/reports/T-056-hoa-si.md``). AI giả (``fake_ai``), WordPress giả (``FakeWordPress``),
ảnh do Pillow tạo trong thư mục tạm; không gọi mạng, không dùng ảnh thật, không đụng
``data/`` thật (kho nháp, kho thẻ ảnh, cache ảnh xem trước đều trỏ sang thư mục tạm).
"""

from __future__ import annotations

import dataclasses
import hashlib
import html
import io
import json
import os
import re
import sqlite3
import threading
import time
from contextlib import closing, contextmanager
from pathlib import Path
from urllib.parse import urlsplit

import pytest
import streamlit as st
import test_app_pages as pages
from fake_ai import ALT, RESEARCH, FakeProvider
from fake_wordpress import BASE_URL, make_session
from PIL import ExifTags, Image
from PIL.TiffImagePlugin import IFDRational
from streamlit.runtime.scriptrunner_utils.exceptions import StopException
from streamlit.testing.v1 import AppTest

import seo_app.ai as ai_module
import seo_app.images.alt as alt_module
import seo_app.storage.drafts as drafts
import seo_app.storage.image_tags as image_tags
from seo_app.ai import AIError
from seo_app.ai import registry as ai_registry
from seo_app.content import OutlineItem
from seo_app.content.rules import load_alt_rules, load_image_settings
from seo_app.images import process as image_process
from seo_app.images.alt import AI_ALT_PREFIX
from seo_app.images.folders import ImageLibrary, ImageRef
from seo_app.images.tags import SOURCE_AI, SOURCE_REAL, ImageTags
from seo_app.storage import DraftPart, DraftSnapshot, DraftStore
from seo_app.storage.drafts import DraftImage
from seo_app.storage.image_tags import ImageTagStore, ImageTagStoreError
from seo_app.text import escape_markdown
from seo_app.wordpress.client import DraftImagesError, WordPressClient

env = pages.env  # mật khẩu thử, không có khóa AI thật
fake_ai = pages.fake_ai
button = pages.button

PROJECT = "CT012 - Cổng inox - Tân Phú"
REAL_FILE = f"{PROJECT}/truoc/IMG_0001.jpg"
MEDIA = "/wp-json/wp/v2/media"
POSTS = "/wp-json/wp/v2/posts"
POST_ID = 501
UPLOADS = f"{BASE_URL}/wp-content/uploads/2026/10/"
IS_WINDOWS = os.name == "nt"


# ----------------------------------------------------------------------------- ảnh giả


def jpeg(size=(320, 240), color=(200, 80, 40), *, gps: bool = False) -> bytes:
    """JPEG do Pillow tạo; ``gps``: kèm vị trí GPS giả (16.0544 N, 108.2022 E)."""
    params: dict[str, object] = {"quality": 90}
    if gps:
        exif = Image.Exif()
        exif[ExifTags.Base.Make] = "Apple"
        exif[ExifTags.Base.Model] = "iPhone 15"
        gps_ifd = exif.get_ifd(ExifTags.IFD.GPSInfo)
        gps_ifd[0] = b"\x02\x02\x00\x00"
        gps_ifd[1] = "N"
        gps_ifd[2] = (IFDRational(16, 1), IFDRational(3, 1), IFDRational(1584, 100))
        gps_ifd[3] = "E"
        gps_ifd[4] = (IFDRational(108, 1), IFDRational(12, 1), IFDRational(792, 100))
        params["exif"] = exif.tobytes()
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, "JPEG", **params)
    return buffer.getvalue()


def write(path: Path, data: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


@pytest.fixture(autouse=True)
def previews(monkeypatch, tmp_path_factory):
    """Cache ảnh xem trước trong thư mục tạm (không ghi vào ``data/image_previews`` thật)."""
    folder = tmp_path_factory.mktemp("anh-xem-truoc")
    monkeypatch.setattr(image_process, "PREVIEW_CACHE_DIR", folder)
    return folder


@pytest.fixture
def root(tmp_path, monkeypatch) -> Path:
    """Thư mục ảnh: một công trình, ảnh "trước" có GPS, ảnh "sau" không có GPS."""
    root = tmp_path / "Anh cong trinh"
    write(root / REAL_FILE, jpeg(gps=True))
    write(root / PROJECT / "sau" / "IMG_0002.jpg", jpeg(color=(30, 120, 200)))
    monkeypatch.setenv("IMAGE_FOLDERS", str(root))
    return root


# ----------------------------------------------------------------------------- trang


def store() -> DraftStore:
    return DraftStore(drafts.DEFAULT_DRAFTS_FILE)


def tag_store() -> ImageTagStore:
    return ImageTagStore(image_tags.DEFAULT_IMAGE_TAGS_FILE)


def article(chosen: DraftImage | None = None, **changes) -> DraftSnapshot:
    """Bài ở bước Viết & kiểm tra: mở bài và một mục có chỗ cần ảnh."""
    data = dict(
        step=2,
        keyword="sửa cổng inox",
        research=RESEARCH,
        research_keyword="sửa cổng inox",
        outline_title="Sửa cổng inox Tân Phú",
        outline=[OutlineItem(heading="Bản lề cổng", points=["gỉ"], image="Bản lề gỉ")],
        article_title="Sửa cổng inox Tân Phú",
        parts=[
            DraftPart(heading="Mở bài", versions=["Cổng inox ở Tân Phú bị xệ cánh."]),
            DraftPart(
                heading="Bản lề cổng",
                versions=["Bản lề gỉ thì thay cả cặp."],
                image="Ảnh bản lề gỉ trước khi sửa",
                chosen_image=chosen,
            ),
        ],
    )
    data.update(changes)
    return DraftSnapshot(**data)


def open_article(project_root, snap: DraftSnapshot | None = None) -> tuple[AppTest, int]:
    """Mở trang Soạn bài, mở nháp ``snap`` (mặc định ``article()``); trả (trang, mã chỗ cần ảnh)."""
    snap = snap or article()
    store().save(snap)
    at = pages.open_page(project_root, "write.py")
    button(at, "Mở", key=f"open-{snap.id}").click().run()
    assert not at.exception, at.exception
    pid = next(p for p in at.session_state["part_ids"] if at.session_state[f"img-{p}"])
    return at, pid


def run_ok(at: AppTest) -> AppTest:
    assert not at.exception, at.exception
    return at


def by_key(at: AppTest, key: str):
    return next(b for b in at.button if b.key == key)


def browse(at: AppTest, pid: int) -> AppTest:
    """Bấm «Chọn ảnh từ thư mục» (hay «Chọn ảnh khác» khi đã có ảnh)."""
    return run_ok(by_key(at, f"browse-{pid}").click().run())


def listing(at: AppTest):
    place = at.session_state["_browse"]
    return at.session_state["_scans"][(place["root"], place["dir"], place["page"])]


def sub_box(at: AppTest):
    """Ô «Thư mục con» (khóa đổi mỗi lần sang thư mục khác)."""
    return next(box for box in at.selectbox if box.label.startswith("Thư mục con"))


def open_sub(at: AppTest, name: str) -> AppTest:
    target = next(sub.rel_path for sub in listing(at).subfolders if sub.name == name)
    return run_ok(sub_box(at).select(target).run())


def choose(at: AppTest, name: str) -> AppTest:
    index = next(i for i, entry in enumerate(listing(at).images) if entry.name == name)
    return run_ok(button(at, "Chọn", key=f"choose-{index}").click().run())


def choose_real(at: AppTest, pid: int) -> AppTest:
    browse(at, pid)
    open_sub(at, PROJECT)
    open_sub(at, "truoc")
    return choose(at, "IMG_0001.jpg")


def write_alt(at: AppTest, pid: int) -> AppTest:
    return run_ok(button(at, "✨ AI viết alt", key=f"altai-{pid}").click().run())


def approve(at: AppTest, pid: int) -> AppTest:
    return run_ok(at.checkbox(key=f"altok-{pid}").check().run())


def texts(at: AppTest) -> list[str]:
    """Mọi chữ đang hiện trên trang (Markdown, chú thích, cảnh báo, ô nhập, lựa chọn…)."""
    found: list[str] = []
    for kind in ("markdown", "caption", "text", "warning", "info", "error", "success", "code"):
        found += [str(element.value) for element in getattr(at, kind)]
    for widget in [*at.text_input, *at.text_area]:
        found.append(str(widget.value))
    for box in at.selectbox:
        found += [str(option) for option in box.options]
    found += [str(b.label) for b in at.button]
    return found


def saved_image(at: AppTest) -> DraftImage | None:
    return store().load(at.session_state["draft_id"]).parts[1].chosen_image


# ======================================================== luồng chính: chọn ảnh, alt, duyệt


def test_spot_is_real_picker_and_nothing_scanned_until_opened(project_root, root, monkeypatch):
    """Chỗ cần ảnh không còn là bản demo; chưa bấm mở thư mục thì không quét (LC-T048)."""
    scans = []
    original = ImageLibrary.list_folder
    monkeypatch.setattr(
        ImageLibrary,
        "list_folder",
        lambda self, *a, **k: scans.append(a) or original(self, *a, **k),
    )
    at, pid = open_article(project_root)
    page = "\n".join(texts(at))
    assert "📷 Chỗ cần ảnh" in page
    assert "Giai đoạn 3" not in page
    assert any(b.key == f"browse-{pid}" for b in at.button)
    assert scans == []
    browse(at, pid)
    assert len(scans) == 1  # mở thư mục gốc


def test_choose_image_write_alt_approve_and_save(project_root, root, fake_ai):
    at, pid = open_article(project_root)
    choose_real(at, pid)
    checked = at.session_state[f"pick-{pid}"]
    assert checked.ref == ImageRef(0, REAL_FILE)
    assert checked.tags.source == SOURCE_REAL and checked.tags.project_code == "CT012"
    assert at.session_state[f"kind-{pid}"] == "Ảnh thật"
    assert "_browse" not in at.session_state  # chọn xong thì đóng khung chọn ảnh
    page = "\n".join(texts(at))
    assert "📷 Ảnh thật" in page
    assert "Mã CT012 · Cổng inox · Tân Phú · Trước khi làm" in page.replace("\\", "")
    assert "📍 Ảnh có vị trí GPS" in page

    write_alt(at, pid)
    assert at.session_state[f"alt-{pid}"] == ALT.alt
    assert at.session_state[f"cap-{pid}"] == ALT.caption
    assert at.session_state[f"altok-{pid}"] is False  # gợi ý AI phải được duyệt
    ((task, images),) = fake_ai.image_calls
    assert task == "alt" and images[0].mime == "image/jpeg"

    approve(at, pid)
    saved = saved_image(at)
    assert (saved.root_index, saved.rel_path, saved.source) == (0, REAL_FILE, SOURCE_REAL)
    assert saved.alt == ALT.alt and saved.alt_approved is True
    assert saved.category == "Cổng inox"


def test_ai_kind_prompt_view_edit_and_saved(project_root, root):
    """Ảnh AI: prompt xem (khung có nút sao chép), sửa được, nháp nhớ prompt (CLAUDE.md). Tạo
    ảnh trong app đang hoãn nên nút tạo ảnh bị khóa, không gọi AI."""
    at, pid = open_article(project_root)
    at.session_state[f"kind-{pid}"] = "Ảnh AI"
    run_ok(at.run())
    assert [c.value for c in at.code] == ["Ảnh bản lề gỉ trước khi sửa"]
    assert by_key(at, f"gen-{pid}").disabled
    run_ok(at.text_area(key=f"prompt-{pid}").input("Bản lề inox gỉ, ảnh chụp gần").run())
    assert [c.value for c in at.code] == ["Bản lề inox gỉ, ảnh chụp gần"]
    saved = saved_image(at)
    assert (saved.source, saved.root_index, saved.prompt) == (
        SOURCE_AI,
        None,
        "Bản lề inox gỉ, ảnh chụp gần",
    )
    # Mở lại nháp: vẫn là ảnh AI, prompt còn nguyên.
    again, pid2 = open_article(project_root, store().load(at.session_state["draft_id"]))
    assert again.session_state[f"kind-{pid2}"] == "Ảnh AI"
    assert [c.value for c in again.code] == ["Bản lề inox gỉ, ảnh chụp gần"]


def test_switching_pages_keeps_inputs_and_draft(project_root, root, fake_ai):
    """Sang trang khác ở menu rồi quay lại: Streamlit xóa giá trị các ô nhập của trang Soạn bài.
    Trang lấy lại từ bản sao, nên không mất alt đã duyệt, từ khóa, bước đang làm, và lần tự lưu
    sau không ghi đè nháp bằng ô trống (phát hiện khi làm T-056)."""
    at, pid = open_article(project_root)
    choose_real(at, pid)
    write_alt(at, pid)
    approve(at, pid)
    run_ok(at.switch_page("views/home.py").run())
    run_ok(at.switch_page("views/write.py").run())
    assert at.session_state["step"] == 2
    assert at.session_state["keyword"] == "sửa cổng inox"
    assert at.session_state[f"alt-{pid}"] == ALT.alt
    assert at.session_state[f"altok-{pid}"] is True
    saved = store().load(at.session_state["draft_id"])
    assert saved.keyword == "sửa cổng inox"
    assert saved.parts[1].chosen_image.alt == ALT.alt
    assert saved.parts[1].chosen_image.alt_approved is True


# ============================================== quét thư mục: khi nào, trong luồng nào, giữ lại


def spy_scans(monkeypatch) -> list[tuple[str, tuple]]:
    calls: list[tuple[str, tuple]] = []
    original = ImageLibrary.list_folder

    def spy(self, *args, **kwargs):
        calls.append((threading.current_thread().name, args))
        return original(self, *args, **kwargs)

    monkeypatch.setattr(ImageLibrary, "list_folder", spy)
    return calls


def test_scan_in_own_thread_kept_in_session_rescan_on_request(project_root, root, monkeypatch):
    """Quét trong luồng riêng; kết quả giữ trong phiên, chuyển trang rồi quay lại không quét lại;
    chỉ «Quét lại» mới quét lại (Soi Lỗi T-048, Lá Chắn T-048)."""
    calls = spy_scans(monkeypatch)
    at, pid = open_article(project_root)
    browse(at, pid)
    open_sub(at, PROJECT)
    assert [args[:2] for _name, args in calls] == [(0, ""), (0, PROJECT)]
    assert all(name.startswith("quet-anh") for name, _args in calls)
    run_ok(at.run())
    run_ok(at.switch_page("views/home.py").run())
    run_ok(at.switch_page("views/write.py").run())
    assert len(calls) == 2
    assert at.session_state["_browse"]["dir"] == PROJECT
    run_ok(by_key(at, "browse-up").click().run())
    assert len(calls) == 2  # thư mục gốc đã quét trong phiên này
    run_ok(by_key(at, "browse-rescan").click().run())
    assert [args[:2] for _name, args in calls[2:]] == [(0, "")]


def test_subfolder_box_is_fresh_after_moving(project_root, root):
    """Sang thư mục khác thì ô «Thư mục con» là ô mới, trống: trình duyệt không giữ lựa chọn của
    thư mục trước (lựa chọn đó không có trong danh sách mới; lỗi thấy khi mở app thật)."""
    at, pid = open_article(project_root)
    browse(at, pid)
    first = sub_box(at).key
    open_sub(at, PROJECT)
    box = sub_box(at)
    assert box.key != first and box.value is None
    assert box.options == ["\u2068sau\u2069", "\u2068truoc\u2069"]


def test_unpick_clears_image_and_alt(project_root, root, fake_ai):
    """«Bỏ ảnh»: bỏ ảnh và alt; bản sao ô nhập không đưa alt cũ trở lại; nháp không còn ảnh."""
    at, pid = open_article(project_root)
    choose_real(at, pid)
    write_alt(at, pid)
    approve(at, pid)
    run_ok(by_key(at, f"unpick-{pid}").click().run())
    run_ok(at.run())
    assert f"pick-{pid}" not in at.session_state
    assert at.session_state.get(f"alt-{pid}", "") == ""
    assert saved_image(at) is None
    browse(at, pid)
    choose(at, "IMG_0001.jpg")
    assert at.session_state[f"alt-{pid}"] == "" and at.session_state[f"altok-{pid}"] is False


def test_slow_drive_does_not_hold_the_page(project_root, root, monkeypatch):
    """Ổ chậm (Google Drive): trang không chờ mãi, báo đang quét; lần quét chạy tiếp ở nền."""
    release = threading.Event()
    original = ImageLibrary.list_folder

    def slow(self, *args, **kwargs):
        release.wait(90)
        return original(self, *args, **kwargs)

    monkeypatch.setattr(ImageLibrary, "list_folder", slow)
    at, pid = open_article(project_root)
    try:
        started = time.monotonic()
        by_key(at, f"browse-{pid}").click().run(timeout=90)
        assert not at.exception, at.exception
        assert time.monotonic() - started < 60
        assert any("đang quét thư mục này ở nền" in i.value for i in at.info)
    finally:
        release.set()
    run_ok(by_key(at, "scan-wait").click().run(timeout=90))
    assert [sub.name for sub in listing(at).subfolders] == [PROJECT]


# ======================================================== tên lấy từ máy, đường dẫn, lối tắt

WEIRD = "[bấm](evil.example) _đậm_ \u200bẩn \u05d0\u05d1"
WEIRD_FILE = "anh\u200b_[x](y).jpg"


def test_names_from_disk_escaped_isolated_never_html(project_root, root):
    """Tên thư mục, tên file là dữ liệu chưa tin cậy: không thành link hay định dạng, ký tự vô
    hình hiện thành «�», cả tên cô lập hướng chữ; không bao giờ vào HTML (LC-T048-4 b, U1)."""
    write(root / WEIRD / WEIRD_FILE, jpeg())
    at, pid = open_article(project_root)
    browse(at, pid)
    assert "\u2068[bấm](evil.example) _đậm_ \ufffdẩn \u05d0\u05d1\u2069" in (sub_box(at).options)
    open_sub(at, WEIRD)
    choose(at, WEIRD_FILE)
    assert not any("\u200b" in text for text in texts(at))
    markdown = [m.value for m in [*at.markdown, *at.caption, *at.warning]]
    assert not any("](evil.example)" in v or "[x](y)" in v for v in markdown)
    assert any(escape_markdown("\u2068anh\ufffd_[x](y).jpg\u2069") in v for v in markdown)
    assert any(
        escape_markdown(f"\u2068{WEIRD}\u2069".replace("\u200b", "\ufffd")) in v for v in markdown
    )
    for element in [*at.markdown, *at.caption]:
        if element.proto.allow_html:
            assert "evil" not in element.value and "[x]" not in element.value


def test_no_absolute_path_on_the_page(project_root, root, fake_ai):
    """Không hiện đường dẫn tuyệt đối (yêu cầu 3, U2); không dùng ``ImageLibrary._folders``."""
    at, pid = open_article(project_root)
    choose_real(at, pid)
    write_alt(at, pid)
    browse(at, pid)
    shown = "\n".join(texts(at))
    for secret in {str(root), str(root.parent), root.as_posix(), str(Path.home())}:
        assert secret not in shown
    assert "Anh cong trinh" in shown  # chỉ tên thư mục gốc
    source = (project_root / "app" / "views" / "write.py").read_text(encoding="utf-8")
    # Chỉ được nhắc tới trong lời giải thích «không dùng ``ImageLibrary._folders``».
    assert not re.search(r"(?<!ImageLibrary)\._folders", source)


def make_link(link: Path, target: Path) -> None:
    """Lối tắt tới thư mục: junction trên Windows (không cần quyền quản trị), symlink nơi khác."""
    if IS_WINDOWS:
        import _winapi

        _winapi.CreateJunction(str(target), str(link))
    else:
        link.symlink_to(target, target_is_directory=True)


def test_root_through_link_is_reported_without_path(project_root, tmp_path, monkeypatch):
    """Thư mục gốc đi qua lối tắt thì báo, không hiện đường dẫn (ghi nhận Lá Chắn T-048)."""
    direct = tmp_path / "Anh that"
    write(direct / "a.jpg", jpeg())
    target = tmp_path / "noi khac" / "Anh tro toi"
    write(target / "b.jpg", jpeg())
    link = tmp_path / "Anh qua loi tat"
    make_link(link, target)
    monkeypatch.setenv("IMAGE_FOLDERS", f"{direct};{link}")
    at, pid = open_article(project_root)
    browse(at, pid)
    assert not any("lối tắt" in w.value for w in at.warning)
    run_ok(at.selectbox(key="_browse_root").select(1).run())
    assert any("đi qua lối tắt" in w.value for w in at.warning)
    assert [entry.name for entry in listing(at).images] == ["b.jpg"]
    shown = "\n".join(texts(at))
    assert str(target) not in shown and str(tmp_path) not in shown


# ======================================================================== ảnh xem trước


def test_st_image_only_gets_preview_cache_bytes(project_root, root, monkeypatch, fake_ai):
    """``st.image`` chỉ nhận byte của ``PreviewCache.get`` (LC-T058-2, Lá Chắn T-049 điều kiện 3):
    không đường dẫn, không byte gốc, không ảnh Pillow."""
    made: list[bytes] = []
    original_get = image_process.PreviewCache.get

    def get(self, library, ref):
        data = original_get(self, library, ref)
        made.append(data)
        return data

    monkeypatch.setattr(image_process.PreviewCache, "get", get)
    shown: list[object] = []
    original_image = st.image

    def image(data, *args, **kwargs):
        shown.append(data)
        return original_image(data, *args, **kwargs)

    monkeypatch.setattr(st, "image", image)
    at, pid = open_article(project_root)
    shown.clear()  # bỏ logo của trang đăng nhập (file cố định của app)
    choose_real(at, pid)
    write_alt(at, pid)
    originals = {path.read_bytes() for path in root.rglob("*.jpg")}
    assert shown
    for data in shown:
        assert type(data) is bytes
        assert data in made and data not in originals
        with Image.open(io.BytesIO(data)) as preview:
            assert preview.format == "JPEG" and max(preview.size) <= 320


def test_preview_errors_are_vietnamese_without_trace(project_root, root, monkeypatch):
    """Lỗi đọc ảnh hiện câu tiếng Việt của module ảnh; lỗi lạ hiện câu cố định, không dấu vết lỗi,
    không chữ của lỗi gốc (Lá Chắn T-049 điều kiện 3)."""
    write(root / PROJECT / "truoc" / "IMG_0003.jpg", b"day khong phai anh <?php echo 1; ?>")
    at, pid = open_article(project_root)
    browse(at, pid)
    open_sub(at, PROJECT)
    open_sub(at, "truoc")
    names = [entry.name for entry in listing(at).images]
    assert by_key(at, f"choose-{names.index('IMG_0003.jpg')}").disabled
    assert not by_key(at, f"choose-{names.index('IMG_0001.jpg')}").disabled
    message = (
        "File này không phải ảnh JPEG, PNG, WebP hoặc HEIC đọc được (có thể bị đổi đuôi hoặc hỏng)."
    )
    assert escape_markdown(message) in [c.value for c in at.caption]

    def broken(self, library, ref):
        raise RuntimeError(r"C:\Users\bi-mat\anh.jpg")

    monkeypatch.setattr(image_process.PreviewCache, "get", broken)
    run_ok(at.run())
    shown = "\n".join(texts(at))
    assert "bi-mat" not in shown
    assert escape_markdown("Không xử lý được ảnh này. Hãy thử ảnh khác.") in shown


def test_gps_text_notice_and_image_settings(project_root, root, monkeypatch):
    """«Ảnh không có vị trí GPS» khi không có GPS; hiện ``WebImage.notice`` khi có (Lá Chắn T-049,
    T-067); ``make_web_image`` nhận cấu hình ``load_image_settings()`` (Lá Chắn T-062)."""
    at, pid = open_article(project_root)
    browse(at, pid)
    open_sub(at, PROJECT)
    open_sub(at, "sau")
    choose(at, "IMG_0002.jpg")
    assert "Ảnh không có vị trí GPS." in [c.value for c in at.caption]

    seen: list[dict] = []
    original = image_process.make_web_image
    notice = "Thông tin GPS của ảnh gốc bị hỏng nên ảnh nén không có vị trí GPS."

    def with_notice(data, **kwargs):
        seen.append(kwargs)
        return dataclasses.replace(original(data, **kwargs), notice=notice)

    monkeypatch.setattr(image_process, "make_web_image", with_notice)
    at.session_state["_web_info"] = {}
    run_ok(at.run())
    assert any(escape_markdown(notice) in c.value for c in at.caption)
    settings = load_image_settings()
    assert seen == [{"max_edge_px": settings.max_edge_px, "webp_quality": settings.webp_quality}]


# ========================================================================= alt bằng AI


def test_alt_only_on_click_for_chosen_image_with_ai_copy(project_root, root, monkeypatch, fake_ai):
    """AI chỉ viết alt khi bấm, cho đúng ảnh đã chọn; ảnh gửi AI là byte của ``make_ai_image``
    (Lá Chắn T-050 a, Soi Lỗi T-066); ``ai_generated`` theo thẻ, ``rules=load_alt_rules()``,
    router ``prepare=("alt",)`` (Lá Chắn T-062)."""
    made, calls, prepared = [], [], []
    original_make = image_process.make_ai_image

    def make(data, **kwargs):
        result = original_make(data, **kwargs)
        made.append(result)
        return result

    monkeypatch.setattr(image_process, "make_ai_image", make)
    original_suggest = alt_module.suggest_alt

    def suggest(ai, image, **kwargs):
        calls.append((image, kwargs))
        return original_suggest(ai, image, **kwargs)

    monkeypatch.setattr(alt_module, "suggest_alt", suggest)
    original_router = ai_module.AIRouter

    def router(*args, **kwargs):
        prepared.append(kwargs.get("prepare"))
        return original_router(*args, **kwargs)

    monkeypatch.setattr(ai_module, "AIRouter", router)
    at, pid = open_article(project_root)
    choose_real(at, pid)  # duyệt thư mục (2 ảnh) rồi chọn: chưa gửi ảnh nào cho AI
    assert (made, calls, fake_ai.image_calls) == ([], [], [])
    write_alt(at, pid)
    ((image, kwargs),) = calls
    (ai_copy,) = made
    assert image.data == ai_copy.data and image.mime == "image/jpeg"
    assert fake_ai.image_calls[0][1][0].data == ai_copy.data
    assert kwargs["ai_generated"] is False
    assert kwargs["tags"] == {
        "Hạng mục": "Cổng inox",
        "Khu vực": "Tân Phú",
        "Giai đoạn": "Trước khi làm",
    }
    assert kwargs["rules"] == load_alt_rules()
    assert ("alt",) in prepared


def test_alt_ai_errors_shown_as_message(project_root, root, monkeypatch):
    """Lỗi AI hiện đúng câu ``AIError`` bằng ``st.error``, không ``st.exception`` (Lá Chắn T-050
    c, T-062): không có khóa AI, rồi hãng AI báo lỗi."""
    at, pid = open_article(project_root)
    choose_real(at, pid)
    write_alt(at, pid)
    assert any(escape_markdown("ANTHROPIC_API_KEY") in e.value for e in at.error)
    assert not at.exception

    class Failing(FakeProvider):
        def generate(self, task, **kwargs):
            raise AIError("Hãng AI đang quá tải. Thử lại sau ít phút.")

    monkeypatch.setattr(ai_registry, "make_provider", lambda name, settings: Failing())
    write_alt(at, pid)
    # Hiện qua escape_markdown như mọi câu lỗi khác (T-086, Ghi nhận 3 của Lá Chắn T-056).
    assert escape_markdown("Hãng AI đang quá tải. Thử lại sau ít phút.") in [
        e.value for e in at.error
    ]
    assert at.session_state[f"alt-{pid}"] == ""


def test_alt_needs_approval_and_phone_numbers_warn(project_root, root, fake_ai):
    """Alt, chú thích sửa được trong ô; sửa thì phải duyệt lại; dãy số giống số điện thoại thì
    nhắc (Lá Chắn T-050 b, d)."""
    at, pid = open_article(project_root)
    choose_real(at, pid)
    assert at.checkbox(key=f"altok-{pid}").disabled  # chưa có alt thì chưa duyệt được
    write_alt(at, pid)
    approve(at, pid)
    run_ok(at.text_input(key=f"alt-{pid}").input("Cổng nhà anh Tư, gọi 0909 123 456").run())
    assert at.session_state[f"altok-{pid}"] is False
    assert any("số điện thoại" in w.value for w in at.warning)
    run_ok(at.text_input(key=f"alt-{pid}").input("Cổng inox 2 cánh cao 2,4 m").run())
    assert not any("số điện thoại" in w.value for w in at.warning)
    run_ok(at.text_input(key=f"cap-{pid}").input("Liên hệ 028.3812.3456").run())
    assert any("số điện thoại" in w.value for w in at.warning)


# ================================================================= ảnh thật / ảnh AI, thẻ


def test_ai_root_folder_makes_every_image_ai(project_root, tmp_path, monkeypatch, fake_ai):
    """Thư mục gốc tên có dấu hiệu AI: mọi ảnh trong đó là ảnh AI, kèm lý do; alt «Minh họa»
    (Lá Chắn T-052 c, T-070 g, h)."""
    ai_root = tmp_path / "Ảnh AI"
    write(ai_root / REAL_FILE, jpeg())
    monkeypatch.setenv("IMAGE_FOLDERS", str(ai_root))
    at, pid = open_article(project_root)
    choose_real(at, pid)
    tags = at.session_state[f"pick-{pid}"].tags
    assert tags.is_ai and (tags.project_code, tags.area, tags.phase) == ("", "", "")
    shown = "\n".join(texts(at))
    assert "🤖 Ảnh AI" in shown and "tên thư mục ảnh gốc có chữ AI" in shown
    assert not any(b.key == f"markai-{pid}" for b in at.button)
    write_alt(at, pid)
    assert at.session_state[f"alt-{pid}"].startswith(f"{AI_ALT_PREFIX} ")


def test_root_link_to_ai_folder_counts_as_ai(project_root, tmp_path, monkeypatch, fake_ai):
    """Gốc khai báo tên thường nhưng là lối tắt tới thư mục tên AI: xét cả tên sau ``resolve()``
    (Lá Chắn T-070 g)."""
    target = tmp_path / "Ảnh AI tạo"
    write(target / "cong.jpg", jpeg())
    link = tmp_path / "Anh chung"
    make_link(link, target)
    monkeypatch.setenv("IMAGE_FOLDERS", str(link))
    at, pid = open_article(project_root)
    browse(at, pid)
    choose(at, "cong.jpg")
    assert at.session_state[f"pick-{pid}"].tags.is_ai


def test_mark_ai_saves_manual_tag_and_rewrites_alt(project_root, root, fake_ai):
    """Một bấm đổi sang ảnh AI (``ImageTagStore.set(source="ai")``); alt, chú thích thêm «Minh
    họa» và phải duyệt lại; AI viết alt như ảnh AI; nháp nhớ ảnh AI (Lá Chắn T-052 b)."""
    at, pid = open_article(project_root)
    choose_real(at, pid)
    write_alt(at, pid)
    approve(at, pid)
    run_ok(by_key(at, f"markai-{pid}").click().run())
    tags = at.session_state[f"pick-{pid}"].tags
    assert tags.is_ai and tags.category == "Cổng inox"
    assert (tags.project_code, tags.area, tags.phase) == ("", "", "")
    assert tag_store().get(ImageRef(0, REAL_FILE)).tags.source == SOURCE_AI
    assert at.session_state[f"alt-{pid}"].startswith(f"{AI_ALT_PREFIX} ")
    assert at.session_state[f"altok-{pid}"] is False
    assert at.session_state[f"kind-{pid}"] == "Ảnh AI"
    assert "ảnh đã được đánh dấu là ảnh AI" in "\n".join(texts(at))
    run_ok(by_key(at, f"altai-{pid}").click().run())
    assert (
        at.session_state[f"alt-{pid}"]
        == f"{AI_ALT_PREFIX} cổng inox 304 hai cánh màu bạc vừa lắp xong trước nhà phố"
    )
    assert saved_image(at).source == SOURCE_AI


def test_mark_ai_store_failure_still_ai_in_session(project_root, root, monkeypatch, fake_ai):
    """Lưu thẻ hỏng (file bận): trong phiên vẫn là ảnh AI, hiện câu lỗi; không viết alt như ảnh
    thật (Lá Chắn T-074 j)."""

    def busy(self, ref, tags):
        raise ImageTagStoreError("File lưu thẻ ảnh đang bận, thử lại sau.")

    monkeypatch.setattr(ImageTagStore, "set", busy)
    at, pid = open_article(project_root)
    choose_real(at, pid)
    run_ok(by_key(at, f"markai-{pid}").click().run())
    assert any("Chưa lưu được dấu «ảnh AI»" in w.value for w in at.warning)
    assert at.session_state[f"pick-{pid}"].tags.is_ai
    assert tag_store().get(ImageRef(0, REAL_FILE)) is None
    write_alt(at, pid)
    assert at.session_state[f"alt-{pid}"].startswith(f"{AI_ALT_PREFIX} ")
    # Chọn lại đúng ảnh đó trong phiên: vẫn là ảnh AI.
    browse(at, pid)
    choose(at, "IMG_0001.jpg")
    assert at.session_state[f"pick-{pid}"].tags.is_ai


def test_broken_tag_file_reported_by_name_only(project_root, root):
    """File thẻ sửa tay hỏng được cất sang một bên: chỉ hiện tên file (Lá Chắn T-052 d)."""
    path = image_tags.DEFAULT_IMAGE_TAGS_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"day khong phai SQLite " * 50)
    at, pid = open_article(project_root)
    browse(at, pid)
    open_sub(at, PROJECT)
    open_sub(at, "truoc")  # trang ảnh: đọc thẻ (resolve_many) lần đầu
    found = [w.value for w in at.warning if "File lưu thẻ ảnh sửa tay bị hỏng" in w.value]
    (moved,) = path.parent.glob("image_tags.hong-*")
    assert len(found) == 1 and escape_markdown(moved.name) in found[0]
    assert str(path.parent) not in found[0]


def test_unmatched_folder_words_only_counted(project_root, tmp_path, monkeypatch):
    """Phần tên thư mục không khớp danh sách chỉ hiện dạng số, không vào dòng thẻ (Lá Chắn T-052
    e)."""
    folder = "CT012 - Nhà anh Tuấn - Tân Phú"
    write(tmp_path / "Anh" / folder / "IMG_1.jpg", jpeg())
    monkeypatch.setenv("IMAGE_FOLDERS", str(tmp_path / "Anh"))
    at, pid = open_article(project_root)
    browse(at, pid)
    open_sub(at, folder)
    choose(at, "IMG_1.jpg")
    captions = [c.value for c in at.caption]
    tag_line = next(c for c in captions if c.startswith("Thẻ:"))
    assert "Tuấn" not in tag_line and "Tân Phú" in tag_line
    assert "1 phần tên thư mục không khớp danh sách thẻ nên bị bỏ qua." in captions


def test_tags_read_per_page_at_most_200(project_root, tmp_path, monkeypatch):
    """Thẻ đọc bằng ``resolve_many`` theo từng trang (≤ 200 ảnh), không cho cả lần quét
    (SL-T074-1); trang không đọc thẻ bằng ``get``/``get_many`` (Lá Chắn T-052 a)."""
    folder = "CT001 - Cổng sắt - Quận 7"
    for number in range(15):
        write(tmp_path / "Anh" / folder / f"IMG_{number:02d}.jpg", jpeg(size=(40, 30)))
    monkeypatch.setenv("IMAGE_FOLDERS", str(tmp_path / "Anh"))
    sizes: list[int] = []
    original = ImageTagStore.resolve_many

    def spy(self, refs):
        refs = list(refs)
        sizes.append(len(refs))
        return original(self, refs)

    monkeypatch.setattr(ImageTagStore, "resolve_many", spy)
    at, pid = open_article(project_root)
    browse(at, pid)
    open_sub(at, folder)
    assert sizes[-1] == 12 and listing(at).total_images == 15
    run_ok(by_key(at, "page-next").click().run())
    assert sizes[-1] == 3
    assert max(sizes) <= 200
    source = (project_root / "app" / "views" / "write.py").read_text(encoding="utf-8")
    assert ".get_many(" not in source and "store().get(" not in source


# ============================================================================ mở nháp (T-055)


def test_open_draft_uses_checked_image_not_draft_fields(project_root, root):
    """Ảnh của nháp được kiểm lại khi mở (``check_draft_images``); hiện, duyệt theo kết quả kiểm
    (thẻ theo thư mục thật), không theo trường trong nháp (Lá Chắn T-055 b). Nháp mang băm của
    file lúc duyệt (T-089; nháp không có băm thì phải duyệt lại: ``test_t089_send_draft.py``)."""
    chosen = DraftImage(
        source=SOURCE_REAL,
        root_index=0,
        rel_path=REAL_FILE,
        category="Cổng sắt",  # nháp ghi khác thư mục thật
        alt="Bản lề cổng gỉ",
        alt_approved=True,
        caption="Bản lề gỉ sau 3 năm",
        approved_sha256=hashlib.sha256((root / REAL_FILE).read_bytes()).hexdigest(),
    )
    at, pid = open_article(project_root, article(chosen))
    checked = at.session_state[f"pick-{pid}"]
    assert checked.available and checked.ref == ImageRef(0, REAL_FILE)
    assert (checked.tags.category, checked.tags.project_code) == ("Cổng inox", "CT012")
    assert at.session_state[f"alt-{pid}"] == "Bản lề cổng gỉ"
    assert at.session_state[f"altok-{pid}"] is True
    assert "Mã CT012 · Cổng inox · Tân Phú · Trước khi làm" in "\n".join(texts(at)).replace(
        "\\", ""
    )


@pytest.mark.parametrize(
    ("root_index", "rel_path", "expected"),
    [
        (0, f"{PROJECT}/truoc/DA_XOA.jpg", "Không tìm thấy ảnh"),
        (7, REAL_FILE, "Không có thư mục ảnh với số thứ tự này"),
    ],
)
def test_open_draft_unusable_image_shows_checked_message(
    project_root, root, root_index, rel_path, expected
):
    """Ảnh của nháp không dùng được trên máy này: hiện ``checked.message``, không cho duyệt alt."""
    chosen = DraftImage(
        source=SOURCE_REAL,
        root_index=root_index,
        rel_path=rel_path,
        alt="Bản lề",
        alt_approved=True,
    )
    at, pid = open_article(project_root, article(chosen))
    checked = at.session_state[f"pick-{pid}"]
    assert not checked.available and expected in checked.message
    assert escape_markdown(checked.message) in [w.value for w in at.warning]
    assert not any(box.key == f"alt-{pid}" for box in at.text_input)
    to_publish(at)
    assert any("Ảnh ở mục" in w.value for w in at.warning)
    assert button(at, "📤 Gửi nháp").disabled


def test_open_draft_in_ai_root_is_ai(project_root, tmp_path, monkeypatch):
    """Mở nháp: kiểm ảnh kèm ``ai_roots`` (Lá Chắn T-055 d). Nháp ghi ảnh thật, alt đã duyệt,
    nhưng thư mục gốc là thư mục ảnh AI: ra ảnh AI, alt thêm «Minh họa», phải duyệt lại."""
    ai_root = tmp_path / "Ảnh AI"
    write(ai_root / REAL_FILE, jpeg())
    monkeypatch.setenv("IMAGE_FOLDERS", str(ai_root))
    chosen = DraftImage(
        source=SOURCE_REAL,
        root_index=0,
        rel_path=REAL_FILE,
        alt="Cổng inox hai cánh",
        alt_approved=True,
    )
    at, pid = open_article(project_root, article(chosen))
    checked = at.session_state[f"pick-{pid}"]
    assert checked.available and checked.tags.is_ai
    assert (checked.tags.project_code, checked.tags.area) == ("", "")
    assert at.session_state[f"alt-{pid}"] == f"{AI_ALT_PREFIX} cổng inox hai cánh"
    assert at.session_state[f"altok-{pid}"] is False
    assert at.session_state[f"kind-{pid}"] == "Ảnh AI"


def test_broken_image_in_draft_dropped_and_reported(project_root, root):
    """Ảnh trong nháp bị sửa tay sai khuôn: bỏ ảnh đó, báo số ảnh bỏ, phần chữ giữ nguyên
    (``snapshot.dropped_images``, Lá Chắn T-055 b)."""
    snap = article(DraftImage(source=SOURCE_REAL, root_index=0, rel_path=REAL_FILE, alt="Bản lề"))
    store().save(snap)
    with closing(sqlite3.connect(drafts.DEFAULT_DRAFTS_FILE)) as conn:
        (data,) = conn.execute("SELECT data FROM drafts WHERE id = ?", (snap.id,)).fetchone()
        data = json.loads(data)
        data["parts"][1]["chosen_image"]["rel_path"] = "../ngoai/anh.jpg"
        conn.execute(
            "UPDATE drafts SET data = ? WHERE id = ?",
            (json.dumps(data, ensure_ascii=False), snap.id),
        )
        conn.commit()
    at = pages.open_page(project_root, "write.py")
    run_ok(button(at, "Mở", key=f"open-{snap.id}").click().run())
    assert any("1 ảnh đã chọn trong nháp bị hỏng nên đã bỏ" in w.value for w in at.warning)
    pid = at.session_state["part_ids"][1]
    assert f"pick-{pid}" not in at.session_state
    assert at.session_state[f"texts-{pid}"] == ["Bản lề gỉ thì thay cả cặp."]


# ---- 2a (Lá Chắn T-055, giữ bắt buộc test theo Lá Chắn T-076): nháp ghi thư mục chữ thường

AI_DISK = f"{PROJECT}/CongAI/cong.png"
AI_DRAFT = f"{PROJECT}/congai/cong.png"


def typed_resolve(self: Path, strict: bool = False) -> Path:
    """Như ``resolve`` của ổ Google Drive for Desktop trên Windows: trả lại đúng chữ đã gõ
    (giống ``tests/test_la_chan_t076.py``)."""
    if strict:
        os.lstat(self)
    return Path(os.path.abspath(self))


@pytest.fixture
def drive(tmp_path, monkeypatch) -> Path:
    """Ảnh AI ở ``CongAI`` (tách chữ hoa mới nhận ra "AI"); thư mục công trình đông (A00…A09
    xếp trước ``CongAI``) để ca danh sách bị cắt không thấy ``CongAI``."""
    root = tmp_path / "Drive"
    png = io.BytesIO()
    Image.new("RGB", (64, 48), (90, 200, 90)).save(png, "PNG")
    write(root / AI_DISK, png.getvalue())
    for number in range(10):
        (root / PROJECT / f"A{number:02d}").mkdir()
    if not (root / AI_DRAFT).exists():
        pytest.skip("ổ phân biệt hoa thường: 'congai' là thư mục khác")
    monkeypatch.setenv("IMAGE_FOLDERS", str(root))
    return root


def assert_ai_tags(at: AppTest, pid: int) -> None:
    tags = at.session_state[f"pick-{pid}"].tags
    assert tags.is_ai, tags
    assert (tags.project_code, tags.area, tags.phase) == ("", "", "")


@pytest.mark.parametrize("how", ["image_folder", "draft_path"])
@pytest.mark.parametrize("crowded", [False, True], ids=["full", "cut"])
@pytest.mark.parametrize("disk", ["ntfs", "typed_resolve"])
def test_2a_lowercase_folder_in_draft_stays_ai(
    project_root, drive, monkeypatch, fake_ai, how, crowded, disk
):
    """Nháp ghi ``…/congai/cong.png``, trên ổ là ``CongAI``: mở nháp, mở thư mục (bằng nút «Mở thư
    mục chứa ảnh», hay theo đúng đường dẫn ghi trong nháp), chọn lại ảnh → ảnh AI, alt «Minh họa».
    Chạy trên ổ thường, ổ giả "resolve trả chữ đã gõ" (Google Drive for Desktop), và khi danh sách
    thư mục cha bị cắt (Lá Chắn T-055 2a, T-076)."""
    if disk == "typed_resolve":
        if not IS_WINDOWS:
            pytest.skip("chỉ cách lấy tên của Windows dùng resolve; Mac/Linux xem thư mục cha")
        monkeypatch.setattr(Path, "resolve", typed_resolve)
    if crowded:

        def small(cls, settings, **kwargs):
            return cls(settings.image_folders, max_entries=3)

        monkeypatch.setattr(ImageLibrary, "from_settings", classmethod(small))
    chosen = DraftImage(
        source=SOURCE_REAL,
        root_index=0,
        rel_path=AI_DRAFT,
        category="Cổng inox",
        alt="Bản lề cổng inox bị gỉ trước khi sửa",
        alt_approved=True,
        caption="Bản lề gỉ sau 3 năm mưa nắng",
    )
    at, pid = open_article(project_root, article(chosen))
    assert_ai_tags(at, pid)  # mở nháp
    assert at.session_state[f"alt-{pid}"].startswith(f"{AI_ALT_PREFIX} ")
    assert at.session_state[f"altok-{pid}"] is False

    if how == "image_folder":
        run_ok(by_key(at, f"openfolder-{pid}").click().run())
    else:  # mở theo đúng chữ ghi trong nháp
        at.session_state["_browse"] = {
            "pid": pid,
            "root": 0,
            "dir": "",
            "page": 1,
            "walk": AI_DRAFT.split("/")[:-1],
        }
        run_ok(at.run())
    if crowded:
        assert at.session_state["_scans"][(0, PROJECT, 1)].truncated
    assert listing(at).rel_dir == f"{PROJECT}/CongAI"
    choose(at, "cong.png")
    assert_ai_tags(at, pid)
    write_alt(at, pid)
    assert at.session_state[f"alt-{pid}"].startswith(f"{AI_ALT_PREFIX} ")
    approve(at, pid)
    saved = saved_image(at)
    assert (saved.source, saved.rel_path) == (SOURCE_AI, AI_DISK)


# =================================================================== gửi nháp kèm ảnh


def path_of(request) -> str:
    return urlsplit(request.url).path


def body_of(request):
    return json.loads(request.body) if request.body else None


class Site:
    """WordPress giả cho «Gửi nháp» kèm ảnh: nhận ảnh (201), ghi alt, tạo nháp, đặt ảnh đại diện."""

    def __init__(self, fake) -> None:
        self.fake = fake
        self.post_status = "draft"
        self.next_id = 900
        self.names: dict[int, str] = {}
        fake.on("POST", MEDIA, self.create_media)
        for media_id in range(900, 920):
            fake.on("POST", f"{MEDIA}/{media_id}", self.update_media)
        fake.on("POST", POSTS, self.create_post)
        fake.on("GET", f"{POSTS}/{POST_ID}", lambda _r: {"id": POST_ID, "status": "draft"})
        fake.on(
            "POST", f"{POSTS}/{POST_ID}", lambda r: {"id": POST_ID, "status": "draft", **body_of(r)}
        )

    def create_media(self, request):
        disposition = request.headers["Content-Disposition"]
        name = re.fullmatch(r'attachment; filename="([^"]+)"', disposition).group(1)
        media_id, self.next_id = self.next_id, self.next_id + 1
        self.names[media_id] = name
        return (201, {"id": media_id, "source_url": f"{UPLOADS}{name}"}, {})

    def update_media(self, request):
        media_id = int(path_of(request).rsplit("/", 1)[1])
        return {
            "id": media_id,
            "source_url": f"{UPLOADS}{self.names[media_id]}",
            **body_of(request),
        }

    def create_post(self, _request):
        return (201, {"id": POST_ID, "status": self.post_status, "title": {"raw": "T"}}, {})

    def uploads(self) -> list:
        return [r for r in self.fake.requests if (r.method, path_of(r)) == ("POST", MEDIA)]

    def file_names(self) -> list[str]:
        return [self.names[media_id] for media_id in sorted(self.names)]

    def media_writes(self) -> list[dict]:
        return [
            body_of(r)
            for r in self.fake.requests
            if r.method == "POST" and path_of(r).startswith(f"{MEDIA}/")
        ]

    def posts(self) -> list[dict]:
        return [body_of(r) for r in self.fake.requests if (r.method, path_of(r)) == ("POST", POSTS)]


@pytest.fixture
def site(monkeypatch, fake_wp) -> Site:
    """Trang dựng ``WordPressClient`` thật nối vào WordPress giả (không gọi mạng)."""

    def from_settings(cls, settings, **kwargs):
        return cls(BASE_URL, "lam", "abcd efgh ijkl", session=make_session(fake_wp))

    monkeypatch.setattr(WordPressClient, "from_settings", classmethod(from_settings))
    return Site(fake_wp)


@dataclasses.dataclass
class SendSpy:
    calls: list = dataclasses.field(default_factory=list)
    errors: list = dataclasses.field(default_factory=list)


@pytest.fixture
def sent(monkeypatch) -> SendSpy:
    spy = SendSpy()
    original = WordPressClient.create_draft_with_images

    def create(self, title, parts, **kwargs):
        spy.calls.append((title, list(parts)))
        try:
            return original(self, title, parts, **kwargs)
        except Exception as exc:
            spy.errors.append(exc)
            raise

    monkeypatch.setattr(WordPressClient, "create_draft_with_images", create)
    return spy


def ready_image(project_root, snap: DraftSnapshot | None = None) -> tuple[AppTest, int]:
    at, pid = open_article(project_root, snap)
    choose_real(at, pid)
    write_alt(at, pid)
    approve(at, pid)
    return at, pid


def to_publish(at: AppTest) -> AppTest:
    at.session_state["step"] = 4
    return run_ok(at.run())


def send(at: AppTest) -> AppTest:
    return run_ok(button(at, "📤 Gửi nháp").click().run())


def flatten(node):
    """Phần tử trên trang theo đúng thứ tự hiện."""
    children = getattr(node, "children", None)
    if children:
        for child in children.values():
            yield from flatten(child)
    else:
        yield node


def test_send_draft_with_real_image(project_root, root, fake_ai, site, sent):
    """Chỉ gửi khi bấm; cảnh báo ảnh (có GPS) công khai ngay trước nút; ``DraftImage`` mang thẻ
    ``ImageTags`` đã kiểm của chính ảnh đó; ảnh lên còn GPS; bài là nháp (Lá Chắn T-054 4a, 4b,
    T-071 3a).

    T-102 (R5, Chỉ Huy B duyệt 30/10 18:45): nội dung là các khối của bộ dựng T-096 (mỗi phần một
    khối, LC-T094-36), ảnh ngay sau khối của phần mình; giữ các kiểm về ảnh: alt, chú thích đã
    làm sạch trong ``<figure>``, ``srcset`` chỉ file đầy đủ (T-059), «[» «]» vô hiệu (T-061),
    không còn chỗ giữ chỗ ``{{…}}``."""
    at, pid = ready_image(project_root)
    first = at.session_state["part_ids"][0]
    at.session_state[f"texts-{first}"] = ["Cổng inox ở Tân Phú bị xệ cánh [gallery]."]
    at.session_state[f"ver-{first}"] = 0
    to_publish(at)
    assert site.fake.requests == [] and sent.calls == []
    elements = list(flatten(at.main))
    index = next(i for i, e in enumerate(elements) if getattr(e, "label", "") == "📤 Gửi nháp")
    assert "xem được công khai" in elements[index - 1].value  # cảnh báo nằm ngay trước nút
    send(at)
    ((title, parts),) = sent.calls
    assert title == "Sửa cổng inox Tân Phú"
    assert parts[:2] == [
        "<p>Cổng inox ở Tân Phú bị xệ cánh &#91;gallery&#93;.</p>",
        "<h2>Bản lề cổng</h2>\n<p>Bản lề gỉ thì thay cả cặp.</p>",
    ]
    (image,) = parts[2:]
    assert type(image.tags) is ImageTags
    assert image.tags == at.session_state[f"pick-{pid}"].tags
    assert image.tags.source == SOURCE_REAL and image.tags.project_code == "CT012"
    assert (image.alt, image.caption) == (ALT.alt, ALT.caption)
    assert site.file_names() == ["cong-inox-tan-phu-ct012.webp"]
    (upload,) = site.uploads()
    with Image.open(io.BytesIO(upload.body)) as web:
        assert web.format == "WEBP"
        assert web.getexif().get_ifd(ExifTags.IFD.GPSInfo)  # GPS lên website (quyết định 5A)
    (media,) = site.media_writes()
    assert media["alt_text"] == ALT.alt and not html.unescape(media["title"]).startswith("[AI]")
    (post,) = site.posts()
    content = post["content"]
    assert post["status"] == "draft" and content.count("<figure") == 1
    assert content.index("<h2>Bản lề cổng</h2>") < content.index("<figure")  # ảnh đúng chỗ
    assert f'srcset="{UPLOADS}cong-inox-tan-phu-ct012.webp 1x"' in content  # T-059
    assert f'alt="{html.escape(ALT.alt)}"' in content
    assert f"<figcaption>{html.escape(ALT.caption)}</figcaption>" in content
    assert "&#91;gallery&#93;" in content and "[" not in content and "]" not in content  # T-061
    assert "{{" not in content and "}}" not in content
    assert any("Đã tạo bài nháp trên WordPress" in s.value for s in at.success)
    assert button(at, "📤 Gửi nháp").disabled  # gửi lại phải xác nhận tạo thêm bài nháp mới
    run_ok(at.checkbox(key="_wp_again").check().run())
    assert not button(at, "📤 Gửi nháp").disabled


def test_send_ai_image_named_and_titled_as_ai(project_root, tmp_path, monkeypatch, fake_ai, site):
    """Ảnh AI lên website với tên ``minh-hoa-ai-…``, tiêu đề media ``[AI] …``, alt «Minh họa»
    (Lá Chắn T-071 điều kiện 3a)."""
    ai_root = tmp_path / "Ảnh AI"
    write(ai_root / "cong.jpg", jpeg())
    monkeypatch.setenv("IMAGE_FOLDERS", str(ai_root))
    at, pid = open_article(project_root)
    browse(at, pid)
    choose(at, "cong.jpg")
    write_alt(at, pid)
    approve(at, pid)
    to_publish(at)
    send(at)
    (name,) = site.file_names()
    assert name.startswith("minh-hoa-ai-")
    (media,) = site.media_writes()
    assert html.unescape(media["title"]).startswith("[AI] ")
    assert media["alt_text"].startswith(f"{AI_ALT_PREFIX} ")


@pytest.mark.parametrize("step", ["create", "upload"])
def test_send_errors_shown_in_full_and_maybe_draft_locks_resend(
    project_root, root, fake_ai, site, sent, step
):
    """Lỗi gửi: hiện đủ ``str(exc)`` (escape), liệt kê ảnh đã lên thư viện, ``maybe_uploaded``;
    ``maybe_draft`` thì nhắc kiểm Bài viết → Nháp và khóa nút tới khi người dùng xác nhận, không
    tự gửi lại (Lá Chắn T-054 4c, T-071 3b)."""
    route = POSTS if step == "create" else MEDIA
    site.fake.on("POST", route, lambda _r: (502, {"code": "x", "message": "Bad gateway"}, {}))
    at, pid = ready_image(project_root)
    to_publish(at)
    send(at)
    (error,) = sent.errors
    assert isinstance(error, DraftImagesError)
    assert escape_markdown(str(error)) in [e.value for e in at.error]
    if step == "create":
        assert error.maybe_draft and error.uploaded
        listed = "\n".join(t.value for t in at.text)
        assert error.uploaded[0].file_name in listed and error.uploaded[0].source_url in listed
        assert any("bài nháp có thể đã có trên website" in e.value for e in at.error)
        assert button(at, "📤 Gửi nháp").disabled
        count = len(site.fake.requests)
        run_ok(at.run())
        assert len(site.fake.requests) == count  # không tự gửi lại
        run_ok(at.checkbox(key="_wp_checked").check().run())
        assert not button(at, "📤 Gửi nháp").disabled
    else:
        assert error.maybe_uploaded and not error.maybe_draft
        assert any("có thể vẫn đã lên thư viện Media" in w.value for w in at.warning)
        assert not button(at, "📤 Gửi nháp").disabled


@pytest.mark.parametrize("saved", [True, False], ids=["luu-the-duoc", "luu-the-hong"])
def test_marked_ai_image_sent_as_ai(project_root, root, monkeypatch, fake_ai, site, sent, saved):
    """Ảnh đánh dấu bằng «Đây là ảnh AI» (kể cả khi lưu thẻ hỏng) lên website như ảnh AI: thẻ
    ``source="ai"``, tên ``minh-hoa-ai-…``, tiêu đề ``[AI] …`` (Lá Chắn T-052 b, T-074 j)."""
    if not saved:

        def busy(self, ref, tags):
            raise ImageTagStoreError("File lưu thẻ ảnh đang bận, thử lại sau.")

        monkeypatch.setattr(ImageTagStore, "set", busy)
    at, pid = open_article(project_root)
    choose_real(at, pid)
    run_ok(by_key(at, f"markai-{pid}").click().run())
    write_alt(at, pid)
    approve(at, pid)
    to_publish(at)
    send(at)
    ((_title, parts),) = sent.calls
    (image,) = [part for part in parts if not isinstance(part, str)]
    assert image.tags.source == SOURCE_AI and not image.tags.project_code
    (name,) = site.file_names()
    assert name.startswith("minh-hoa-ai-") and "ct012" not in name
    (media,) = site.media_writes()
    assert html.unescape(media["title"]).startswith("[AI] ")


def test_post_not_draft_is_flagged(project_root, root, fake_ai, site):
    """Website trả bài không ở trạng thái nháp (app không xin): báo rõ (Soi Lỗi T-054 G9)."""
    site.post_status = "publish"
    at, pid = ready_image(project_root)
    to_publish(at)
    send(at)
    assert any("không phải nháp" in e.value for e in at.error)


def test_shortcode_like_segments_listed_before_send(project_root, root, fake_ai, site):
    """Trước nút «Gửi nháp», liệt kê mọi đoạn dạng shortcode trong tiêu đề, nội dung, alt, chú
    thích, kèm lời nhắc (Lá Chắn T-061, LC-T061-4)."""
    snap = article(
        parts=[
            DraftPart(heading="Mở bài", versions=["Xem [code_snippet id=3] nhé."]),
            DraftPart(heading="Bản lề [embed]", versions=["Thân bài."], image="Ảnh bản lề"),
        ]
    )
    at, pid = open_article(project_root, snap)
    choose_real(at, pid)
    run_ok(
        at.text_input(key=f"alt-{pid}").input("Bản lề [caption]gỉ[/caption] trước khi sửa").run()
    )
    approve(at, pid)
    to_publish(at)
    warning = next(w.value for w in at.warning if "đoạn dạng shortcode" in w.value)
    reminder = "WordPress sẽ chạy đoạn này nếu bạn sửa và lưu bài trong trang quản trị; nên xóa"
    assert reminder in warning
    for segment in ("[code_snippet id=3]", "[embed]", "[caption]", "[/caption]"):
        assert escape_markdown(segment) in warning
    assert escape_markdown("Alt ảnh ở mục «Bản lề [embed]»") in warning
    assert site.fake.requests == []


def test_no_shortcode_warning_for_plain_article(project_root, root, fake_ai, site):
    at, pid = ready_image(project_root)
    to_publish(at)
    assert not any("đoạn dạng shortcode" in w.value for w in at.warning)


def test_same_image_in_two_spots_uploaded_once(project_root, root, fake_ai, site):
    """Một ảnh đặt ở hai chỗ, cùng alt: chỉ tải một lần (Soi Lỗi T-054 G10); chọn ảnh đại diện."""
    snap = article(
        parts=[
            DraftPart(heading="Mở bài", versions=["Mở bài."]),
            DraftPart(heading="Bản lề", versions=["Phần một."], image="Ảnh một"),
            DraftPart(heading="Cánh cổng", versions=["Phần hai."], image="Ảnh hai"),
        ]
    )
    at, first = open_article(project_root, snap)
    second = at.session_state["part_ids"][2]
    choose_real(at, first)
    browse(at, second)  # mở lại đúng thư mục vừa xem
    choose(at, "IMG_0001.jpg")
    for pid in (first, second):
        write_alt(at, pid)
        approve(at, pid)
    to_publish(at)
    run_ok(at.selectbox(key="_featured").select(second).run())
    send(at)
    assert len(site.uploads()) == 1
    (post,) = site.posts()
    assert post["content"].count("<figure") == 2


def test_image_checked_again_right_before_upload(project_root, root, fake_ai, site, monkeypatch):
    """Ngay trước khi tải, kiểm lại ảnh (``check_chosen_image``, LC-T055-2): ảnh vừa thành ảnh AI
    (thẻ sửa ở tab khác) thì dừng, chưa gửi gì, alt thêm «Minh họa» và phải duyệt lại."""
    calls = []
    original = drafts.check_chosen_image

    def check(image, *args, **kwargs):
        calls.append(image)
        return original(image, *args, **kwargs)

    monkeypatch.setattr(drafts, "check_chosen_image", check)
    at, pid = ready_image(project_root)
    to_publish(at)
    before = len(calls)
    tag_store().set(ImageRef(0, REAL_FILE), ImageTags(source=SOURCE_AI, category="Cổng inox"))
    send(at)
    assert len(calls) == before + 1 and calls[-1].rel_path == REAL_FILE
    assert site.fake.requests == []
    assert any("vừa thay đổi" in m.value for m in at.markdown)
    assert at.session_state[f"pick-{pid}"].tags.is_ai
    assert at.session_state[f"alt-{pid}"].startswith(f"{AI_ALT_PREFIX} ")
    assert button(at, "📤 Gửi nháp").disabled  # alt đổi: phải duyệt lại


def test_deleted_image_stops_send(project_root, root, fake_ai, site):
    at, pid = ready_image(project_root)
    to_publish(at)
    (root / REAL_FILE).unlink()
    send(at)
    assert site.fake.requests == []
    assert any("Chưa gửi gì lên website" in e.value for e in at.error)
    assert any("Không tìm thấy ảnh" in m.value for m in at.markdown)


# ================================== lượt 2: gửi bị ngắt, bấm đúp, file bị thay, ổ chậm (Soi Lỗi)

SEND_LABEL = "📤 Gửi nháp"
INTERRUPTED = "Lần gửi trước bị ngắt giữa chừng"


def counts(site: Site) -> tuple[int, int]:
    return len(site.posts()), len(site.uploads())


def click_send_once_more(monkeypatch) -> None:
    """Lần chạy kế tiếp nhận thêm một cú bấm «Gửi nháp» (cú thứ hai của bấm đúp): Streamlit vẫn
    báo nút đã bấm dù lần vẽ mới là khóa (cú bấm gửi từ lần vẽ trước)."""
    original = st.button
    pending = [True]  # đúng một lần

    def second_click(label, *args, **kwargs):
        clicked = original(label, *args, **kwargs)
        if label == SEND_LABEL and pending:
            pending.pop()
            return True
        return clicked

    monkeypatch.setattr(st, "button", second_click)


def stop_when_leaving_send_spinner(monkeypatch) -> None:
    """Như người dùng bấm nút khác lúc đang gửi: Streamlit dừng lần chạy ở lệnh ``st.*`` kế tiếp,
    tức lúc thoát vòng quay «Đang gửi bài nháp…»."""
    original = st.spinner

    @contextmanager
    def spinner(text="", *args, **kwargs):
        with original(text, *args, **kwargs):
            yield
        if text.startswith("Đang gửi bài nháp"):
            raise StopException()

    monkeypatch.setattr(st, "spinner", spinner)


def test_double_click_does_not_send_twice(project_root, root, fake_ai, site, monkeypatch):
    """Bấm đúp «Gửi nháp»: cú bấm thứ hai tới khi lần chạy trước đã gửi xong. Không gửi lần hai
    (SL-T056-1)."""
    at, _pid = ready_image(project_root)
    to_publish(at)
    send(at)
    assert counts(site) == (1, 1)
    click_send_once_more(monkeypatch)
    run_ok(at.run())
    assert counts(site) == (1, 1)
    assert any("Đã tạo bài nháp trên WordPress" in s.value for s in at.success)
    assert button(at, SEND_LABEL).disabled


def test_stop_when_leaving_spinner_keeps_result(project_root, root, fake_ai, site, monkeypatch):
    """Bấm nút khác lúc đang gửi: lần chạy dừng lúc thoát vòng quay. Kết quả đã ghi trước đó: lần
    chạy sau hiện kết quả, khóa nút; cú bấm thứ hai không gửi lại (SL-T056-1)."""
    stop_when_leaving_send_spinner(monkeypatch)
    at, _pid = ready_image(project_root)
    to_publish(at)
    send(at)
    assert counts(site) == (1, 1)
    click_send_once_more(monkeypatch)
    run_ok(at.run())
    assert counts(site) == (1, 1)
    assert any("Đã tạo bài nháp trên WordPress" in s.value for s in at.success)
    assert button(at, SEND_LABEL).disabled
    assert "_wp_sending" not in at.session_state


def test_confirmation_untick_even_if_run_stops(project_root, root, fake_ai, site, monkeypatch):
    """Đã tick «Tôi đã kiểm tra…» sau một lần lỗi, gửi lại, lại lỗi đúng lúc tạo nháp và lần chạy
    bị dừng lúc thoát vòng quay: lần sau ô xác nhận đã bỏ tick, nút khóa; cú bấm thứ hai không gửi
    lần ba (SL-T056-1)."""
    site.fake.on("POST", POSTS, lambda _r: (502, {"code": "x", "message": "Bad gateway"}, {}))
    at, _pid = ready_image(project_root)
    to_publish(at)
    send(at)
    run_ok(at.checkbox(key="_wp_checked").check().run())
    stop_when_leaving_send_spinner(monkeypatch)
    send(at)
    attempts = len(site.posts())
    assert attempts == 2
    click_send_once_more(monkeypatch)
    run_ok(at.run())
    assert len(site.posts()) == attempts
    assert at.checkbox(key="_wp_checked").value is False
    assert button(at, SEND_LABEL).disabled


def test_stop_during_image_upload_locks_resend(project_root, root, fake_ai, site):
    """Lần chạy dừng ngay trong lúc tải ảnh (lỗi giữa chừng, lệnh tải chưa trả lời): không biết ảnh,
    bài đã lên chưa. Lần chạy sau nhắc kiểm trang quản trị, khóa nút tới khi người dùng xác nhận;
    không tự gửi lại (SL-T056-1)."""
    original = site.create_media

    def stopped(request):
        original(request)
        raise StopException()

    site.fake.on("POST", MEDIA, stopped)
    at, _pid = ready_image(project_root)
    to_publish(at)
    send(at)
    assert counts(site) == (0, 1)
    run_ok(at.run())
    errors = [e.value for e in at.error]
    assert any(INTERRUPTED in e for e in errors)
    assert any("bài nháp có thể đã có" in e for e in errors)
    assert button(at, SEND_LABEL).disabled
    requests = len(site.fake.requests)
    run_ok(at.run())
    assert len(site.fake.requests) == requests
    run_ok(at.checkbox(key="_wp_checked").check().run())
    assert not button(at, SEND_LABEL).disabled


def test_leftover_sending_mark_locks_send(project_root, root, fake_ai, site):
    """Dấu «đang gửi» còn mà chưa có kết quả (lần chạy trước dừng giữa lúc gửi): coi như gửi dở,
    nhắc và khóa nút (SL-T056-1)."""
    at, _pid = ready_image(project_root)
    to_publish(at)
    at.session_state["_wp_sending"] = True
    run_ok(at.run())
    assert any(INTERRUPTED in e.value for e in at.error)
    assert button(at, SEND_LABEL).disabled
    assert site.fake.requests == []


def test_replaced_file_needs_new_look_and_approval(project_root, root, fake_ai, site):
    """File bị thay bằng ảnh khác cùng tên sau khi duyệt alt (SL-T056-2): dừng, chưa gửi gì; khung
    ảnh chuyển sang file mới (xem trước, GPS của file mới), bỏ «Đã duyệt»; duyệt lại rồi mới gửi,
    và gửi đúng file mới."""
    at, pid = open_article(project_root)
    browse(at, pid)
    open_sub(at, PROJECT)
    open_sub(at, "sau")
    choose(at, "IMG_0002.jpg")
    write_alt(at, pid)
    approve(at, pid)
    to_publish(at)
    before = at.session_state[f"pick-{pid}"].entry
    write(root / PROJECT / "sau" / "IMG_0002.jpg", jpeg((640, 480), (10, 10, 10), gps=True))
    send(at)
    assert site.fake.requests == []
    assert at.session_state[f"altok-{pid}"] is False
    assert at.session_state[f"pick-{pid}"].entry.size != before.size
    assert button(at, SEND_LABEL).disabled
    at.session_state["step"] = 2
    run_ok(at.run())
    assert any(c.value.startswith("📍 Ảnh có vị trí GPS") for c in at.caption)
    approve(at, pid)
    to_publish(at)
    send(at)
    (upload,) = site.uploads()
    with Image.open(io.BytesIO(upload.body)) as web:
        assert web.size == (640, 480) and web.getexif().get_ifd(ExifTags.IFD.GPSInfo)


def test_recheck_on_slow_drive_does_not_hold_page(project_root, root, fake_ai, monkeypatch):
    """Kiểm lại ảnh trước khi AI viết alt chạy trong luồng quét (có thể xem thư mục từng tầng):
    ổ chậm quá 15 giây thì trang báo, không gọi AI (SL-T056-7)."""
    at, pid = open_article(project_root)
    choose_real(at, pid)
    release = threading.Event()
    original = drafts.check_chosen_image

    def slow(*args, **kwargs):
        release.wait(90)
        return original(*args, **kwargs)

    monkeypatch.setattr(drafts, "check_chosen_image", slow)
    try:
        started = time.monotonic()
        by_key(at, f"altai-{pid}").click().run(timeout=90)
        assert not at.exception, at.exception
        assert time.monotonic() - started < 60
        assert any("Ổ đĩa đang chậm" in e.value for e in at.error)
        assert fake_ai.image_calls == []
    finally:
        release.set()


def test_dates_and_sizes_are_not_phone_numbers(project_root, root, fake_ai):
    """Mẫu số điện thoại rộng hơn (SL-T056-4) nhưng ngày tháng, năm, kích thước không bị nhắc."""
    at, pid = open_article(project_root)
    choose_real(at, pid)
    for alt in ("Cổng sửa ngày 12/10/2026", "Mùa mưa 2024–2025 cổng bị gỉ", "Cổng 1600 x 1200 cm"):
        run_ok(at.text_input(key=f"alt-{pid}").input(alt).run())
        assert not any("số điện thoại" in w.value for w in at.warning), alt


def test_shortcode_from_body_into_image_caption_listed(project_root, root, fake_ai, site):
    """«[» mở ở thân mục, «]» ở chú thích ảnh của mục đó: trên website là một chuỗi nội dung, nên
    vẫn liệt kê (SL-T056-3)."""
    snap = article(
        parts=[
            DraftPart(heading="Mở bài", versions=["Mở bài."]),
            DraftPart(heading="Bản lề cổng", versions=["Mã nhúng [code_snippet id=3"], image="Ảnh"),
        ]
    )
    at, pid = open_article(project_root, snap)
    choose_real(at, pid)
    write_alt(at, pid)
    run_ok(at.text_input(key=f"cap-{pid}").input("Bản lề gỉ, xem bảng giá]").run())
    approve(at, pid)
    to_publish(at)
    warning = next(w.value for w in at.warning if "đoạn dạng shortcode" in w.value)
    assert escape_markdown("Nội dung, vắt qua nhiều mục") in warning
    assert escape_markdown("[code_snippet id=3") in warning
