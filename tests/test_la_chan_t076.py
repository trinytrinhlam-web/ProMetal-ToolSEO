"""Lá Chắn T-076 (rút gọn): ổ trả lại đúng chữ đã gõ khi ``resolve`` (Google Drive for Desktop).

Trên Windows, T-076 lấy tên trên ổ từ đường đã ``resolve`` (``folders._NAMES_FROM_RESOLVE``). Đo
thật trên máy Windows của chủ dự án (script nháp, chỉ đọc): ổ Google Drive for Desktop (G:, H:, I:,
báo "FAT32") trả lại **đúng chữ đã gõ**: ``H:/my drive`` ra ``H:\\my drive`` dù trên ổ là
``My Drive``; 4/4 thư mục người dùng tạo gõ đảo hoa thường cũng vậy. Danh sách thư mục
(``os.scandir``) và ``FindFirstFileW`` thì cho tên trên ổ. Nên trên ổ Drive, ``stat_image`` và
``list_folder`` vẫn trả ``ImageRef`` theo chữ đã gõ, và LC-T055-1 quay lại: nháp ghi
``…/congai/cong.png``, trên ổ là
``CongAI`` (ảnh AI) thì ra **ảnh thật** CT012, alt không có «Minh họa» vẫn "đã duyệt", khi
``scanned`` quét theo thư mục ghi trong nháp, hay khi danh sách thư mục cha bị cắt (cách sửa
LC-T055-3 giữ tên ``stat_image`` trả). Ghi là LC-T076-1 (``docs/team/reports/T-076-la-chan.md``),
đánh dấu ``xfail(strict=True)``: sửa xong thì test tự báo XPASS để gỡ dấu.

Ổ Drive được giả lập trên ổ NTFS của test: ``Path.resolve`` trả lại đúng chữ đã gõ (như đã đo),
danh sách thư mục vẫn là của ổ thật. Chỉ chạy trên Windows: Mac/Linux lấy tên bằng cách xem thư
mục cha, không dùng ``resolve``. Đối chứng (đang qua): ổ NTFS thật thì mọi luồng ra ảnh AI; trên ổ
giả lập, luồng có lớp phòng thứ hai xem hết danh sách cũng ra ảnh AI. Không gọi mạng, không đụng
ổ Drive thật.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from seo_app.content import OutlineItem
from seo_app.images.alt import AI_ALT_PREFIX
from seo_app.images.folders import ImageLibrary, ImageRef
from seo_app.images.tags import SOURCE_AI, SOURCE_REAL, tags_for_image
from seo_app.storage.drafts import DraftImage, DraftPart, DraftSnapshot, check_draft_images

pytestmark = pytest.mark.skipif(
    os.name != "nt", reason="chỉ cách lấy tên của Windows dùng resolve; Mac/Linux xem thư mục cha"
)

PROJECT = "CT012 - Cổng inox - Tân Phú"
DISK = f"{PROJECT}/CongAI/cong.png"
DRAFT = f"{PROJECT}/congai/cong.png"


def typed_resolve(self: Path, strict: bool = False) -> Path:
    """Như ``resolve`` của ổ Google Drive for Desktop trên Windows: trả lại đúng chữ đã gõ."""
    if strict:
        os.lstat(self)  # không có thì FileNotFoundError, như resolve thật
    return Path(os.path.abspath(self))


@pytest.fixture
def root(tmp_path: Path) -> Path:
    root = tmp_path / "Drive"
    (root / DISK).parent.mkdir(parents=True)
    (root / DISK).write_bytes(b"\x89PNG anh AI")
    for number in range(10):  # thư mục công trình đông: "A00".."A09" xếp trước "CongAI"
        (root / PROJECT / f"A{number:02d}").mkdir()
    if not (root / DRAFT).exists():
        pytest.skip("ổ phân biệt hoa thường: 'congai' là thư mục khác")
    return root


def draft_snapshot() -> DraftSnapshot:
    image = DraftImage(
        source=SOURCE_REAL,
        root_index=0,
        rel_path=DRAFT,
        category="Cổng inox",
        alt="Bản lề cổng inox bị gỉ trước khi sửa",
        alt_approved=True,
        caption="Bản lề gỉ sau 3 năm mưa nắng",
    )
    return DraftSnapshot(
        step=2,
        keyword="sửa cổng inox",
        outline_title="Sửa cổng inox",
        outline=[OutlineItem(heading="Mục 1", points=["bản lề"], image="ảnh")],
        article_title="Sửa cổng inox",
        parts=[
            DraftPart(heading="Mở bài", versions=["Mở bài."]),
            DraftPart(heading="Mục 1", versions=["Thân."], image="ảnh", chosen_image=image),
        ],
    )


def assert_ai(checked) -> None:
    assert checked.tags.is_ai, (checked.ref, checked.tags)
    assert (checked.tags.project_code, checked.tags.area) == ("", "")
    assert checked.image.alt.startswith(f"{AI_ALT_PREFIX} ") and not checked.image.alt_approved


def test_precondition_names_differ_only_by_case():
    assert tags_for_image(ImageRef(0, DISK)).tags.is_ai
    assert not tags_for_image(ImageRef(0, DRAFT)).tags.is_ai


def test_fake_drive_resolve_keeps_typed_case(root, monkeypatch):
    """Giả lập đúng điều đã đo: ``resolve`` trả chữ đã gõ, danh sách thư mục cho tên trên ổ."""
    monkeypatch.setattr(Path, "resolve", typed_resolve)
    assert (root / DRAFT).resolve(strict=True).parent.name == "congai"
    assert "CongAI" in os.listdir(root / PROJECT)


# ----- đối chứng: đang qua -------------------------------------------------------------------


def test_ntfs_every_flow_is_ai(root):
    lib, crowded = ImageLibrary([root]), ImageLibrary([root], max_entries=3)
    assert crowded.list_folder(0, PROJECT, page_size=1).truncated
    snap = draft_snapshot()
    by_draft = lib.list_folder(0, f"{PROJECT}/congai")
    assert lib.stat_image(ImageRef(0, DRAFT)).ref == ImageRef(0, DISK)
    assert by_draft.rel_dir == f"{PROJECT}/CongAI"
    assert_ai(check_draft_images(snap, lib)[1])
    assert_ai(check_draft_images(snap, lib, scanned=by_draft.images)[1])
    assert_ai(check_draft_images(snap, crowded)[1])


def test_fake_drive_full_listing_still_catches_case_variant(root, monkeypatch):
    """Ổ giả lập, không ``scanned``, danh sách thư mục cha xem hết: lớp phòng thứ hai bắt được."""
    monkeypatch.setattr(Path, "resolve", typed_resolve)
    lib = ImageLibrary([root])
    assert_ai(check_draft_images(draft_snapshot(), lib)[1])
    from_root = lib.list_folder(0, f"{PROJECT}/CongAI").images
    assert_ai(check_draft_images(draft_snapshot(), lib, scanned=from_root)[1])


# ----- LC-T076-1: đang hỏng trên ổ giả lập --------------------------------------------------


def test_lc_t076_1_stat_image_returns_disk_name(root, monkeypatch):
    monkeypatch.setattr(Path, "resolve", typed_resolve)
    assert ImageLibrary([root]).stat_image(ImageRef(0, DRAFT)).ref == ImageRef(0, DISK)


def test_lc_t076_1_list_folder_returns_disk_names(root, monkeypatch):
    monkeypatch.setattr(Path, "resolve", typed_resolve)
    listing = ImageLibrary([root]).list_folder(0, f"{PROJECT}/congai")
    assert listing.rel_dir == f"{PROJECT}/CongAI"
    assert [entry.ref for entry in listing.images] == [ImageRef(0, DISK)]


def test_lc_t076_1_scanned_by_draft_folder_stays_ai(root, monkeypatch):
    """LC-T055-1 (thử 1, 4 của Lá Chắn T-055) trên ổ Drive: "mở thư mục chứa ảnh" theo đường dẫn
    ghi trong nháp rồi truyền ``scanned``."""
    monkeypatch.setattr(Path, "resolve", typed_resolve)
    lib = ImageLibrary([root])
    scanned = lib.list_folder(0, f"{PROJECT}/congai").images
    assert_ai(check_draft_images(draft_snapshot(), lib, scanned=scanned)[1])


@pytest.mark.parametrize("scan", ["khong-quet", "quet-tu-goc"])
def test_lc_t076_1_cut_parent_listing_stays_ai(root, monkeypatch, scan):
    """Thư mục công trình đông nên danh sách bị cắt: lớp phòng thứ hai giữ tên ``stat_image`` trả
    (LC-T055-3), mà trên ổ Drive đó là chữ trong nháp. Trên ``main`` (T-055) cùng ca: không dùng
    được (không quét) hay ảnh AI (quét từ gốc)."""
    monkeypatch.setattr(Path, "resolve", typed_resolve)
    crowded = ImageLibrary([root], max_entries=3)
    assert crowded.list_folder(0, PROJECT, page_size=1).truncated
    scanned = ()
    if scan == "quet-tu-goc":
        scanned = ImageLibrary([root]).list_folder(0, f"{PROJECT}/CongAI").images
    checked = check_draft_images(draft_snapshot(), crowded, scanned=scanned)[1]
    assert_ai(checked)


def test_lc_t076_1_image_picked_again_from_draft_folder_is_ai(root, monkeypatch):
    monkeypatch.setattr(Path, "resolve", typed_resolve)
    (entry,) = ImageLibrary([root]).list_folder(0, f"{PROJECT}/congai").images
    picked = DraftImage.from_library(entry, tags_for_image(entry.ref).tags, alt="Cổng inox")
    assert picked.source == SOURCE_AI
