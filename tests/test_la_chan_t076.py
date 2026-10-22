"""Lá Chắn T-076 (rút gọn): ổ trả lại đúng chữ đã gõ khi ``resolve`` (Google Drive for Desktop).

Lượt 1, Windows lấy tên trên ổ từ đường đã ``resolve``. Đo thật trên máy Windows của chủ dự án
(script nháp, chỉ đọc): ổ Google Drive for Desktop (G:, H:, I:, báo "FAT32") trả lại **đúng chữ đã
gõ**: ``H:/my drive`` ra ``H:\\my drive`` dù trên ổ là ``My Drive``; 4/4 thư mục người dùng tạo gõ
đảo hoa thường cũng vậy. Danh sách thư mục (``os.scandir``) và ``FindFirstFileW`` thì cho tên trên
ổ. Nên trên ổ Drive, ``stat_image`` và ``list_folder`` trả ``ImageRef`` theo chữ đã gõ, và
LC-T055-1 quay lại: nháp ghi ``…/congai/cong.png``, trên ổ là ``CongAI`` (ảnh AI) thì ra **ảnh
thật** CT012, alt không có «Minh họa» vẫn "đã duyệt", khi ``scanned`` quét theo thư mục ghi trong
nháp, hay khi danh sách thư mục cha bị cắt (cách sửa LC-T055-3 giữ tên ``stat_image`` trả). Ghi là
LC-T076-1 (``docs/team/reports/T-076-la-chan.md``). Lượt 2 (Thợ Máy) hỏi tên ở thư mục cha bằng
``FindFirstFileW`` từng tầng: 6 ca LC-T076-1 qua, đã gỡ ``xfail``.

LC-T076-3 (= SL-T076-2, lượt 2): lớp phòng thứ hai của nháp vẫn có thể nhận bản sao ở tên của danh
sách thư mục. Danh sách được nhớ cho cả một lần kiểm nháp, nên trên thư mục phân biệt hoa thường
chỉ cần **một** lần đổi tên giữa hai ảnh của nháp. Đánh dấu ``xfail(strict=True)``: sửa xong thì
test tự báo XPASS để gỡ dấu.

Ổ Drive được giả lập trên ổ NTFS của test: ``Path.resolve`` trả lại đúng chữ đã gõ (như đã đo),
danh sách thư mục vẫn là của ổ thật. Chỉ chạy trên Windows: Mac/Linux lấy tên bằng cách xem thư
mục cha, không dùng ``resolve``; thư mục phân biệt hoa thường bật bằng ``fsutil`` (có sẵn trên
Windows) cho thư mục tạm của test. Đối chứng (đang qua): ổ NTFS thật thì mọi luồng ra ảnh AI; trên
ổ giả lập, luồng có lớp phòng thứ hai xem hết danh sách cũng ra ảnh AI. Không gọi mạng, không đụng
ổ Drive thật.
"""

from __future__ import annotations

import contextlib
import os
import shutil
import subprocess
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


# ----- LC-T076-1: hỏng trên ổ giả lập ở lượt 1, qua từ lượt 2 -------------------------------


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


# ----- LC-T076-3 (= SL-T076-2): danh sách thư mục nhớ cho cả nháp, một lần đổi tên -----------


def real_image(rel_path: str) -> DraftImage:
    return DraftImage(
        source=SOURCE_REAL,
        root_index=0,
        rel_path=rel_path,
        category="Cổng inox",
        alt="Bản lề cổng inox bị gỉ trước khi sửa",
        alt_approved=True,
        caption="Bản lề gỉ sau 3 năm mưa nắng",
    )


def snapshot_of(*images: DraftImage) -> DraftSnapshot:
    parts = [DraftPart(heading="Mở bài", versions=["Mở bài."])]
    for number, image in enumerate(images, start=1):
        parts.append(
            DraftPart(heading=f"Mục {number}", versions=["Thân."], image="ảnh", chosen_image=image)
        )
    return DraftSnapshot(
        step=2,
        keyword="sửa cổng inox",
        outline_title="Sửa cổng inox",
        outline=[OutlineItem(heading="Mục 1", points=["bản lề"], image="ảnh")],
        article_title="Sửa cổng inox",
        parts=parts,
    )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "LC-T076-3 = SL-T076-2: lớp phòng thứ hai nhận bản sao ở tên của danh sách thư mục (đã nhớ "
        "từ ảnh trước của nháp) khi hỏi lại tên cũ ra kết quả cũ"
    ),
)
def test_lc_t076_3_cached_listing_and_one_rename_on_case_sensitive_folder(tmp_path, monkeypatch):
    """Thư mục công trình **phân biệt** hoa thường có ``congai/cong.png`` là bản sao y hệt (cùng cỡ,
    cùng giờ sửa) của ảnh AI ở ``X/cong.png``. Nháp 2 ảnh: ảnh 1 ở ``truoc/`` làm danh sách thư mục
    công trình được đọc và nhớ; ngay sau đó ``X`` đổi tên thành ``CongAI`` (một lần, không đổi lại).
    Ảnh 2 nháp ghi ``CongAI/cong.png`` (nguồn "that", alt đã duyệt). Mong đợi: không dùng được, hoặc
    đúng file đã chọn và là ảnh AI; không bao giờ là bản sao ở ``congai``."""
    root = tmp_path / "anh"
    project = root / PROJECT
    project.mkdir(parents=True)
    fsutil = shutil.which("fsutil")
    if fsutil:
        with contextlib.suppress(OSError, subprocess.TimeoutExpired):
            subprocess.run(
                [fsutil, "file", "setCaseSensitiveInfo", str(project), "enable"],
                capture_output=True,
                timeout=30,
                check=False,
            )
    (project / "Thu").mkdir()
    sensitive = not (project / "thu").exists()
    (project / "Thu").rmdir()
    if not sensitive:
        pytest.skip("không bật được phân biệt hoa thường cho thư mục tạm")
    (project / "truoc").mkdir()
    (project / "truoc" / "IMG_0001.jpg").write_bytes(b"\xff\xd8 anh that")
    (project / "X").mkdir()
    (project / "X" / "cong.png").write_bytes(b"\x89PNG anh AI")
    (project / "congai").mkdir()
    shutil.copy2(project / "X" / "cong.png", project / "congai" / "cong.png")  # giữ giờ sửa
    assert tags_for_image(ImageRef(0, f"{PROJECT}/CongAI/cong.png")).tags.is_ai
    assert not tags_for_image(ImageRef(0, f"{PROJECT}/congai/cong.png")).tags.is_ai
    original_list = ImageLibrary.list_folder
    renamed: list[bool] = []

    def list_folder(self, root_index, rel_dir="", **kwargs):
        listing = original_list(self, root_index, rel_dir, **kwargs)
        if rel_dir == PROJECT and not renamed:
            os.rename(project / "X", project / "CongAI")
            renamed.append(True)
        return listing

    monkeypatch.setattr(ImageLibrary, "list_folder", list_folder)
    snapshot = snapshot_of(
        real_image(f"{PROJECT}/truoc/IMG_0001.jpg"), real_image(f"{PROJECT}/CongAI/cong.png")
    )
    checked = check_draft_images(snapshot, ImageLibrary([root]))[2]
    monkeypatch.undo()
    if not renamed:
        return  # không còn xem danh sách thư mục công trình: không có danh sách cũ để nhận bản sao
    if checked.available:
        chosen = os.stat(project / "CongAI" / "cong.png")
        assert os.stat(root / checked.ref.rel_path).st_ino == chosen.st_ino  # không phải bản sao
        assert_ai(checked)
