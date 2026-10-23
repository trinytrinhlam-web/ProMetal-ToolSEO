"""Trang Soạn bài: chỗ cần ảnh thật và gửi nháp kèm ảnh (T-056, G3-10).

Mỗi test gắn với một điều kiện trong mục "Ghi chú của Chỉ Huy" của phiếu
``docs/team/tickets/T-056-giao-dien-cho-can-anh.md`` (bảng "điều kiện → test" trong
``docs/team/reports/T-056-hoa-si.md``). AI giả (``fake_ai``), WordPress giả (``FakeWordPress``),
ảnh do Pillow tạo trong thư mục tạm; không gọi mạng, không dùng ảnh thật, không đụng
``data/`` thật (kho nháp, kho thẻ ảnh, cache ảnh xem trước đều trỏ sang thư mục tạm).
"""

from __future__ import annotations

import io
import os
from pathlib import Path

import pytest
import test_app_pages as pages
from fake_ai import ALT, RESEARCH
from fake_wordpress import BASE_URL
from PIL import ExifTags, Image
from PIL.TiffImagePlugin import IFDRational
from streamlit.testing.v1 import AppTest

import seo_app.storage.drafts as drafts
import seo_app.storage.image_tags as image_tags
from seo_app.content import OutlineItem
from seo_app.images import process as image_process
from seo_app.images.folders import ImageLibrary, ImageRef
from seo_app.images.tags import SOURCE_REAL
from seo_app.storage import DraftPart, DraftSnapshot, DraftStore
from seo_app.storage.drafts import DraftImage
from seo_app.storage.image_tags import ImageTagStore

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


def browse(at: AppTest, pid: int) -> AppTest:
    return run_ok(button(at, "📁 Chọn ảnh từ thư mục", key=f"browse-{pid}").click().run())


def listing(at: AppTest):
    place = at.session_state["_browse"]
    return at.session_state["_scans"][(place["root"], place["dir"], place["page"])]


def open_sub(at: AppTest, name: str) -> AppTest:
    target = next(sub.rel_path for sub in listing(at).subfolders if sub.name == name)
    return run_ok(at.selectbox(key="_browse_sub").select(target).run())


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
