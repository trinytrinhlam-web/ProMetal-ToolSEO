"""Soi Lỗi T-076: ``ImageRef`` theo tên trên ổ (``seo_app/images/folders.py``,
``seo_app/storage/drafts.py``).

Bổ sung cho test của Thợ Máy (``tests/test_images_folders.py`` mục "tên trên ổ (T-076)",
``tests/test_drafts_images.py`` các test LC-T055-x), tập trung vào:

- Ổ **thật** phân biệt hoa thường có cả ``CongAI`` lẫn ``congai``: Windows bật phân biệt hoa
  thường cho thư mục tạm (``fsutil file setCaseSensitiveInfo``, Windows 11 không cần quyền quản
  trị), Linux sẵn có; Mac APFS mặc định thì bỏ qua.
- Tên chỉ khác dấu tiếng Việt (``Tan Phu``/``Tân Phú``), chữ Đ hoa/thường, ba cách viết chữ "ệ"
  (dựng sẵn, NFD, hai dấu đảo thứ tự) trên ổ không gộp dạng Unicode (NTFS, ext4).
- Thư mục bị xóa, bị tráo thành liên kết giữa lúc kiểm đường đi và lúc lấy tên; kết quả quét cũ
  (quét trước khi đổi tên thư mục); ổ chậm khi kiểm nháp.
- Lớp chặn T-048 trên đường lấy tên mới: câu báo không lộ đường dẫn máy, không trả tên ngoài gốc.

Test thư mục ảnh chạy cả hai cách lấy tên (``name_source``): cách của hệ điều hành đang chạy và
cách của Mac/Linux (xem tên trong thư mục cha), như test của Thợ Máy.

Lỗi tìm được đánh dấu ``xfail(strict=True)`` kèm mã SL-T076-x (xem
``docs/team/reports/T-076-soi-loi.md``). Mọi test dùng thư mục tạm, ảnh giả, không gọi mạng.
"""

from __future__ import annotations

import contextlib
import os
import shutil
import subprocess
import unicodedata
from pathlib import Path

import pytest

from seo_app.images import folders
from seo_app.images.alt import AI_ALT_PREFIX, AI_CAPTION_PREFIX
from seo_app.images.folders import (
    ImageFolderError,
    ImageLibrary,
    ImageRef,
    _match_disk_name,
)
from seo_app.images.tags import SOURCE_REAL, tags_for_image
from seo_app.storage.drafts import DraftImage, check_chosen_image

IS_WINDOWS = os.name == "nt"

PROJECT = "CT012 - Cổng inox - Tân Phú"
AI_PATH = f"{PROJECT}/CongAI/cong.png"  # ảnh AI chỉ nhờ tách chữ hoa ("Cong AI", T-052)
LOWER_PATH = f"{PROJECT}/congai/cong.png"  # ảnh thật
AI_BYTES = b"\x89PNG anh AI"
REAL_BYTES = b"\x89PNG anh that, dai hon"
REAL_ALT = "Bản lề cổng inox bị gỉ trước khi sửa"


# ----- tiện ích ----------------------------------------------------------------------------


def write(path: Path, data: bytes = b"\xff\xd8\xff anh gia") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def assert_no_abs_path(text: str, *paths: Path) -> None:
    for path in paths:
        for form in {str(path), str(path.resolve()), path.as_posix(), path.resolve().as_posix()}:
            assert form not in text, f"lộ đường dẫn tuyệt đối: {form!r}"


def raises_safely(func, *paths: Path) -> ImageFolderError:
    """Gọi ``func``, bắt buộc ``ImageFolderError`` có câu không chứa đường dẫn tuyệt đối, không
    xích theo lỗi hệ điều hành (lỗi đó có đường dẫn đầy đủ)."""
    with pytest.raises(ImageFolderError) as info:
        func()
    exc = info.value
    assert str(exc)
    assert_no_abs_path(str(exc), *paths)
    assert exc.__cause__ is None
    assert exc.__context__ is None or exc.__suppress_context__
    return exc


def case_insensitive(folder: Path) -> bool:
    probe = folder / "Thu-Hoa-Thuong"
    probe.mkdir(parents=True)
    try:
        return (folder / "thu-hoa-thuong").exists()
    finally:
        probe.rmdir()


def real_image(rel_path: str) -> DraftImage:
    return DraftImage(
        source=SOURCE_REAL,
        root_index=0,
        rel_path=rel_path,
        category="Cổng inox",
        alt=REAL_ALT,
        alt_approved=True,
        caption="Bản lề gỉ sau 3 năm mưa nắng",
    )


def assert_ai_only_by_case(ai_path: str, other_case: str) -> None:
    """Điều kiện đầu: ``ai_path`` là ảnh AI chỉ nhờ chữ hoa, tên viết hoa thường khác thì không.
    Đổi cách nhận tên ảnh AI làm mất điều này thì test hỏng ở đây, không qua oan."""
    assert tags_for_image(ImageRef(0, ai_path)).tags.is_ai
    assert not tags_for_image(ImageRef(0, other_case)).tags.is_ai


def assert_ai_wording(result) -> None:
    assert result.is_ai
    assert (result.tags.project_code, result.tags.area, result.tags.phase) == ("", "", "")
    assert result.image.alt.startswith(f"{AI_ALT_PREFIX} ") and not result.image.alt_approved
    assert result.image.caption.startswith(AI_CAPTION_PREFIX)


@pytest.fixture(params=["he-dieu-hanh", "xem-thu-muc-cha"])
def name_source(request, monkeypatch) -> str:
    """Cả hai cách lấy tên trên ổ: của hệ điều hành đang chạy (Windows: từ ``resolve``), và của
    Mac/Linux (xem tên trong thư mục cha từng tầng)."""
    if request.param == "xem-thu-muc-cha":
        monkeypatch.setattr(folders, "_NAMES_FROM_RESOLVE", False)
    return request.param


@pytest.fixture
def case_sensitive_dir(tmp_path: Path) -> Path:
    """Thư mục trên ổ thật **phân biệt** hoa thường (thư mục con tạo sau thừa hưởng)."""
    folder = tmp_path / "phan-biet-hoa-thuong"
    folder.mkdir()
    fsutil = shutil.which("fsutil") if IS_WINDOWS else None
    if fsutil:
        with contextlib.suppress(OSError, subprocess.TimeoutExpired):
            subprocess.run(
                [fsutil, "file", "setCaseSensitiveInfo", str(folder), "enable"],
                capture_output=True,
                timeout=30,
                check=False,
            )
    if case_insensitive(folder):
        pytest.skip("ổ không phân biệt hoa thường (Mac APFS mặc định, Windows không bật được)")
    return folder


# ----- ổ thật phân biệt hoa thường: có cả "CongAI" lẫn "congai" ----------------------------


@pytest.fixture
def both_folders(case_sensitive_dir: Path) -> Path:
    assert_ai_only_by_case(AI_PATH, LOWER_PATH)
    root = case_sensitive_dir / "anh"
    write(root / AI_PATH, AI_BYTES)
    write(root / LOWER_PATH, REAL_BYTES)
    assert len(list((root / PROJECT).iterdir())) == 2
    return root


def test_case_sensitive_disk_each_name_is_its_own_folder(both_folders, name_source):
    """Ổ phân biệt hoa thường: ``CongAI`` và ``congai`` là hai thư mục; ``stat_image``,
    ``list_folder`` trả đúng thư mục đã gõ (trùng hẳn thắng), không lẫn sang thư mục kia; tên
    viết khác cả hai thì không tìm thấy."""
    lib = ImageLibrary([both_folders])
    for rel_path, data in ((AI_PATH, AI_BYTES), (LOWER_PATH, REAL_BYTES)):
        entry = lib.stat_image(ImageRef(0, rel_path))
        assert entry.ref == ImageRef(0, rel_path) and entry.size == len(data)
        assert lib.read_image_bytes(entry.ref) == data
        listing = lib.list_folder(0, rel_path.rsplit("/", 1)[0])
        assert listing.rel_dir == rel_path.rsplit("/", 1)[0]
        assert [(e.ref, e.size) for e in listing.images] == [(ImageRef(0, rel_path), len(data))]
    whole = lib.list_folder(0, PROJECT, recursive=True)
    assert sorted(sub.rel_path for sub in whole.subfolders) == [
        f"{PROJECT}/CongAI",
        f"{PROJECT}/congai",
    ]
    assert sorted((e.ref.rel_path, e.size) for e in whole.images) == [
        (AI_PATH, len(AI_BYTES)),
        (LOWER_PATH, len(REAL_BYTES)),
    ]
    for typed in (f"{PROJECT}/CONGAI/cong.png", f"{PROJECT}/Congai/cong.png"):
        raises_safely(lambda typed=typed: lib.stat_image(ImageRef(0, typed)), both_folders)


@pytest.mark.parametrize("max_entries", [5000, 1], ids=["xem-het", "danh-sach-bi-cat"])
def test_case_sensitive_disk_draft_keeps_the_named_folder(both_folders, name_source, max_entries):
    """Nháp ghi đúng một trong hai thư mục: ảnh trong ``CongAI`` là ảnh AI («Minh họa», bỏ "đã
    duyệt"), ảnh trong ``congai`` là ảnh thật CT012, mỗi ảnh đúng file của nó; cả khi danh sách
    thư mục cha bị cắt (LC-T055-2) và khi ``scanned`` là kết quả quét của thư mục kia."""
    lib = ImageLibrary([both_folders], max_entries=max_entries)
    for scanned in ((), lib.list_folder(0, f"{PROJECT}/congai").images):
        ai = check_chosen_image(real_image(AI_PATH), lib, scanned=scanned)
        assert ai.available, ai.message
        assert ai.ref == ai.entry.ref == ImageRef(0, AI_PATH) and ai.entry.size == len(AI_BYTES)
        assert_ai_wording(ai)
    for scanned in ((), lib.list_folder(0, f"{PROJECT}/CongAI").images):
        real = check_chosen_image(real_image(LOWER_PATH), lib, scanned=scanned)
        assert real.available, real.message
        assert real.ref == ImageRef(0, LOWER_PATH) and real.entry.size == len(REAL_BYTES)
        assert not real.is_ai and real.tags.project_code == "CT012"
        assert real.image.alt == REAL_ALT and real.image.alt_approved


# ----- yêu cầu 1 ở cả hai cách lấy tên ----------------------------------------------------


@pytest.mark.parametrize(
    "scan", ["khong-quet", "quet-theo-nhap", "quet-de-quy-theo-nhap", "ref-theo-nhap"]
)
def test_lc_t055_1_draft_case_variant_stays_ai_both_name_sources(tmp_path, name_source, scan):
    """LC-T055-1 (yêu cầu 1) ở **cả hai** cách lấy tên (test nháp của Thợ Máy chỉ chạy cách của
    hệ điều hành đang chạy): nháp ghi ``ct012 - cổng INOX - tân phú/congai/cong.png`` (khác hoa
    thường cả thư mục công trình), trên ổ là ``…/CongAI/…``: ảnh AI, «Minh họa», bỏ "đã duyệt",
    cả khi ``scanned`` là ``list_folder`` theo đường dẫn trong nháp (một tầng hay đệ quy)."""
    root = tmp_path / "anh"
    write(root / AI_PATH, AI_BYTES)
    write(root / PROJECT / "truoc" / "IMG_0001.jpg")
    if not case_insensitive(root):
        pytest.skip("ổ phân biệt hoa thường: 'congai' là thư mục khác, không trỏ tới 'CongAI'")
    typed = "ct012 - cổng INOX - tân phú/congai/cong.png"
    assert_ai_only_by_case(AI_PATH, typed)
    lib = ImageLibrary([root])
    scanned: tuple = ()
    if scan == "quet-theo-nhap":
        scanned = lib.list_folder(0, typed.rsplit("/", 1)[0]).images
        assert [entry.ref for entry in scanned] == [ImageRef(0, AI_PATH)]
    elif scan == "quet-de-quy-theo-nhap":
        scanned = lib.list_folder(0, typed.split("/", 1)[0], recursive=True).images
        assert sorted(entry.ref.rel_path for entry in scanned) == [
            AI_PATH,
            f"{PROJECT}/truoc/IMG_0001.jpg",
        ]
    elif scan == "ref-theo-nhap":
        scanned = (ImageRef(0, typed),)
    result = check_chosen_image(real_image(typed), lib, scanned=scanned)
    assert result.available, result.message
    assert result.ref == result.entry.ref == ImageRef(0, AI_PATH)
    assert_ai_wording(result)


# ----- tên chỉ khác dấu tiếng Việt, dạng Unicode ------------------------------------------


@pytest.mark.parametrize(
    ("plain", "marked"),
    [("Tan Phu", "Tân Phú"), ("Da Nang", "Đà Nẵng"), ("Cong so 1", "Cổng số 1")],
)
def test_names_differing_only_by_vietnamese_marks_never_mix(tmp_path, name_source, plain, marked):
    """Hai thư mục chỉ khác dấu là hai thư mục trên mọi ổ: gõ khác hoa thường thì ra đúng thư mục
    cùng dấu (tên trên ổ), không bao giờ sang thư mục kia."""
    root = tmp_path / "anh"
    write(root / plain / "a.jpg", b"\xff\xd8 khong dau")
    write(root / marked / "a.jpg", b"\xff\xd8 co dau, dai hon")
    lib = ImageLibrary([root])
    sizes = {plain: len(b"\xff\xd8 khong dau"), marked: len(b"\xff\xd8 co dau, dai hon")}
    for name in (plain, marked):
        entry = lib.stat_image(ImageRef(0, f"{name}/a.jpg"))
        assert entry.ref.rel_path == f"{name}/a.jpg" and entry.size == sizes[name]
    if not case_insensitive(root):
        return
    for name in (plain, marked):
        for typed in (name.upper(), name.lower(), name.swapcase()):
            entry = lib.stat_image(ImageRef(0, f"{typed}/a.jpg"))
            assert entry.ref.rel_path == f"{name}/a.jpg" and entry.size == sizes[name]
            assert lib.list_folder(0, typed).rel_dir == name


E_FORMS = {
    "dung-san": "Bệ cửa",
    "nfd": unicodedata.normalize("NFD", "Bệ cửa"),
    "dau-dao": "Bệ cửa",  # hai dấu của "ệ" đảo thứ tự: NFC vẫn là "ệ"
}


def test_three_spellings_of_the_same_vietnamese_letter(tmp_path, name_source):
    """Ổ không gộp dạng Unicode (NTFS, ext4) có ba thư mục "Bệ cửa" viết ba kiểu (cùng khóa NFC):
    gõ kiểu nào ra đúng thư mục kiểu đó (trùng hẳn thắng), ở thư mục ảnh lẫn ở nháp."""
    assert len(set(E_FORMS.values())) == 3
    assert len({unicodedata.normalize("NFC", name) for name in E_FORMS.values()}) == 1
    root = tmp_path / "anh"
    for number, name in enumerate(E_FORMS.values()):
        try:
            write(root / name / "a.jpg", b"\xff\xd8" + b"x" * number)
        except FileExistsError:
            pytest.skip("ổ gộp dạng Unicode (Mac): không có ba thư mục riêng")
    if len(list(root.iterdir())) != 3:
        pytest.skip("ổ gộp dạng Unicode (Mac): không có ba thư mục riêng")
    lib = ImageLibrary([root])
    for number, name in enumerate(E_FORMS.values()):
        ref = ImageRef(0, f"{name}/a.jpg")
        entry = lib.stat_image(ref)
        assert entry.ref == ref and entry.size == 2 + number
        assert lib.list_folder(0, name).rel_dir == name
        checked = check_chosen_image(real_image(ref.rel_path), lib)
        assert checked.available and checked.ref == ref and checked.entry.size == 2 + number
    # Kiểu thứ tư (ê dựng sẵn + dấu nặng): cùng khóa NFC nhưng không có trên ổ.
    fourth = "Bệ cửa"
    assert unicodedata.normalize("NFC", fourth) == E_FORMS["dung-san"]
    raises_safely(lambda: lib.stat_image(ImageRef(0, f"{fourth}/a.jpg")), tmp_path)


def test_match_disk_name_with_many_same_key_names():
    """Danh sách có nhiều tên cùng khóa (ba kiểu viết "ệ", hoa thường): trùng hẳn luôn thắng dù
    đứng sau; không trùng hẳn mà nhiều tên cùng khóa thì từ chối, không chọn bừa."""
    names = [*E_FORMS.values(), "BỆ CỬA"]
    for name in names:
        assert _match_disk_name(iter(names), name, lambda: False) == name
        assert _match_disk_name(iter(reversed(names)), name, lambda: False) == name
    exc = raises_safely(lambda: _match_disk_name(iter(names), "bệ cửa", lambda: False))
    assert "tên khác" in str(exc)
    assert _match_disk_name(iter(["Tan Phu", "Tân Phú"]), "tân phú", lambda: False) == "Tân Phú"
    assert _match_disk_name(iter(["Tân Phú", "Tan Phu"]), "TAN PHU", lambda: False) == "Tan Phu"


# ----- thay đổi giữa chừng ------------------------------------------------------------------


CALLS = {
    "stat_image": lambda lib, rel: lib.stat_image(ImageRef(0, f"{rel}/a.jpg")),
    "list_folder": lambda lib, rel: lib.list_folder(0, rel),
}


@pytest.mark.parametrize("call", list(CALLS))
@pytest.mark.parametrize("typed", ["Album", "ALBUM"], ids=["ten-dung", "khac-hoa-thuong"])
def test_folder_deleted_right_after_path_check(tmp_path, monkeypatch, name_source, call, typed):
    """Thư mục bị xóa ngay sau khi kiểm đường đi, trước khi lấy tên trên ổ: báo lỗi gọn (không
    sập, không lộ đường dẫn máy), không trả ``ImageRef`` nào."""
    root = tmp_path / "anh"
    write(root / "Album" / "a.jpg")
    if typed != "Album" and not case_insensitive(root):
        pytest.skip("ổ phân biệt hoa thường: 'ALBUM' không trỏ tới 'Album'")
    original = ImageLibrary._resolve_inside
    deleted: list[bool] = []

    def check_then_delete(self, root_path, parts):
        result = original(self, root_path, parts)
        if parts[:1] == (typed,) and not deleted:
            deleted.append(True)
            shutil.rmtree(root / "Album")
        return result

    monkeypatch.setattr(ImageLibrary, "_resolve_inside", check_then_delete)
    raises_safely(lambda: CALLS[call](ImageLibrary([root]), typed), tmp_path)
    assert deleted


def make_link(link: Path, target: Path) -> None:
    if IS_WINDOWS:
        import _winapi

        _winapi.CreateJunction(str(target), str(link))  # không cần quyền quản trị
    else:
        link.symlink_to(target, target_is_directory=True)


@pytest.mark.parametrize("call", list(CALLS))
@pytest.mark.parametrize("typed", ["album", "ALBUM"], ids=["ten-dung", "khac-hoa-thuong"])
def test_link_swapped_in_after_path_check(tmp_path, monkeypatch, name_source, call, typed):
    """Lớp chặn T-048 trên đường lấy tên mới: ngay sau khi kiểm đường đi, thư mục bị đổi tên đi và
    một junction (Windows) hay symlink tên đó trỏ ra ngoài gốc (có ``a.jpg`` cùng tên): báo lỗi,
    không trả tên hay số liệu của file ngoài gốc, câu báo không lộ đường dẫn."""
    root = tmp_path / "anh"
    write(root / "album" / "a.jpg", b"\xff\xd8 trong goc")
    outside = write(tmp_path / "ngoai" / "a.jpg", b"\xff\xd8 NGOAI GOC, dai hon").parent
    if typed != "album" and not case_insensitive(root):
        pytest.skip("ổ phân biệt hoa thường: 'ALBUM' không trỏ tới 'album'")
    original = ImageLibrary._resolve_inside
    swapped: list[bool] = []

    def check_then_swap(self, root_path, parts):
        result = original(self, root_path, parts)
        if parts[:1] == (typed,) and not swapped:
            swapped.append(True)
            os.rename(root / "album", root / "album-cu")
            make_link(root / "album", outside)
        return result

    monkeypatch.setattr(ImageLibrary, "_resolve_inside", check_then_swap)
    try:
        exc = raises_safely(lambda: CALLS[call](ImageLibrary([root]), typed), tmp_path)
    except OSError as error:  # Mac/Linux không cho tạo symlink ở đây
        pytest.skip(f"không tạo được liên kết: {error.strerror}")
    assert swapped
    assert "ngoai" not in str(exc).lower()


def test_folder_swapped_during_check_does_not_switch_to_another_file(tmp_path, monkeypatch):
    """Bổ sung SL-T055-4 trên ổ thật. Từ T-076 ``entry`` lấy theo lần kiểm lại, nên câu so cỡ của
    ``test_sl_t055_4_folder_swapped_during_check_on_real_disk`` (T-055) luôn đúng kể cả khi ảnh đã
    đổi sang file khác (thử đột biến bỏ phép so cỡ, giờ sửa: test đó vẫn qua). Ở đây so định danh
    file: ảnh dùng được thì phải đúng file đã chọn, với số liệu của chính nó."""
    root = tmp_path / "anh"
    chosen = write(root / "Congai" / "cong.png", b"\x89PNG anh da chon")
    write(root / "Khac" / "cong.png", b"\x89PNG mot anh khac han, dai hon")
    if not case_insensitive(root):
        pytest.skip("ổ phân biệt hoa thường: nháp 'congai' không trỏ tới 'Congai'")
    first = os.stat(chosen)
    original = ImageLibrary.list_folder
    swapped: list[bool] = []

    def swap_then_list(self, root_index, rel_dir="", **kwargs):
        if rel_dir == "" and not swapped:
            swapped.append(True)
            os.rename(root / "Congai", root / "Congai cu")
            os.rename(root / "Khac", root / "CongAI")
        return original(self, root_index, rel_dir, **kwargs)

    monkeypatch.setattr(ImageLibrary, "list_folder", swap_then_list)
    result = check_chosen_image(real_image("congai/cong.png"), ImageLibrary([root]))
    monkeypatch.undo()
    assert swapped
    if result.available:
        assert os.stat(root / result.ref.rel_path).st_ino == first.st_ino
        assert result.entry.size == first.st_size
    else:
        assert "mở lại từ thư mục ảnh gốc" in result.message
        assert_no_abs_path(result.message, tmp_path)


def test_stale_scan_from_before_folder_rename(tmp_path, name_source):
    """``scanned`` quét lúc thư mục còn tên ``Congai`` (ảnh thật), sau đó thư mục được đổi thành
    ``CongAI`` để đánh dấu ảnh AI: kết quả quét cũ không quyết thẻ, ảnh là ảnh AI theo tên mới."""
    root = tmp_path / "anh"
    old = f"{PROJECT}/Congai/cong.png"
    assert_ai_only_by_case(AI_PATH, old)
    write(root / old, AI_BYTES)
    lib = ImageLibrary([root])
    scanned = lib.list_folder(0, f"{PROJECT}/Congai").images
    assert [entry.ref.rel_path for entry in scanned] == [old]
    os.rename(root / PROJECT / "Congai", root / PROJECT / "CongAI")
    result = check_chosen_image(real_image(old), lib, scanned=scanned)
    if not case_insensitive(root):
        assert not result.available
        return
    assert result.available, result.message
    assert result.ref == result.entry.ref == ImageRef(0, AI_PATH)
    assert_ai_wording(result)


def test_slow_disk_while_checking_draft_is_unavailable_and_safe(tmp_path, monkeypatch):
    """Cách của Mac/Linux, ổ chậm (xem tên quá ``max_seconds``) khi kiểm nháp: ảnh không dùng
    được, câu báo "chậm" không có đường dẫn máy; không sập, nháp vẫn giữ lựa chọn."""
    monkeypatch.setattr(folders, "_NAMES_FROM_RESOLVE", False)
    root = tmp_path / "anh"
    for number in range(10):
        write(root / f"{number:04d}.jpg")
    write(root / AI_PATH, AI_BYTES)
    if not case_insensitive(root):
        pytest.skip("ổ phân biệt hoa thường: 'congai' không trỏ tới 'CongAI'")
    ticks = iter(range(100_000))
    lib = ImageLibrary([root], max_seconds=3, clock=lambda: float(next(ticks)))
    image = real_image(LOWER_PATH)
    result = check_chosen_image(image, lib)
    assert not result.available and result.entry is None
    assert "chậm" in result.message
    assert_no_abs_path(result.message, tmp_path)
    assert result.image.rel_path == image.rel_path


def test_deep_path_with_case_variants_gets_disk_names(tmp_path, name_source):
    """Thư mục sâu (20 tầng, gõ chữ thường ở mọi tầng): ra đúng tên trên ổ ở mọi tầng. Giữ đường
    dẫn dưới 260 ký tự cho máy Windows chưa bật đường dẫn dài."""
    root = tmp_path / "anh"
    disk = [f"Tầng{number:02d}" for number in range(20)]
    write(root.joinpath(*disk) / "Anh.JPG")
    if not case_insensitive(root):
        pytest.skip("ổ phân biệt hoa thường")
    typed = "/".join(name.lower() for name in disk) + "/anh.jpg"
    entry = ImageLibrary([root]).stat_image(ImageRef(0, typed))
    assert entry.ref.rel_path == "/".join(disk) + "/Anh.JPG"


# ===== Lỗi mới ===============================================================================


@pytest.mark.xfail(
    strict=True,
    reason="SL-T076-1: lớp phòng thứ hai nhận file khác khi cùng cỡ và giờ sửa (bản sao)",
)
def test_sl_t076_1_swapped_copy_with_same_size_and_time_is_not_used(tmp_path, monkeypatch):
    """SL-T076-1 (Thấp). Nháp (nguồn "that", alt đã duyệt) ghi ``…/CongAI/cong.png`` (ảnh AI nhờ
    tách chữ hoa). Giữa lúc ``stat_image`` và lúc lớp phòng thứ hai xem danh sách thư mục, thư mục
    ``CongAI`` bị đổi tên đi và thư mục ``Khac`` (có **bản sao** ``cong.png``: cùng nội dung, cùng
    giờ sửa, như khi chép bằng Explorer) được đổi thành ``Congai``. Lớp phòng thứ hai thấy đúng một
    tên trùng không phân biệt hoa thường (``Congai``), ``stat_image`` lại ở đó: cùng cỡ, cùng giờ
    sửa nên nhận. Mong đợi: không dùng được, hoặc đúng file đã kiểm và vẫn là ảnh AI. Thực tế: dùng
    được, ``ref`` là file ở ``Congai`` (file khác), **ảnh thật** CT012, alt không có «Minh họa» vẫn
    "đã duyệt" (trái điều kiện Lá Chắn T-052 số 3; T-076 việc 1: "không lẫn sang file khác")."""
    root = tmp_path / "anh"
    other_case = f"{PROJECT}/Congai/cong.png"
    assert_ai_only_by_case(AI_PATH, other_case)
    chosen = write(root / AI_PATH, AI_BYTES)
    copy = write(root / PROJECT / "Khac" / "cong.png", AI_BYTES)
    first = os.stat(chosen)
    os.utime(copy, ns=(first.st_atime_ns, first.st_mtime_ns))
    if not case_insensitive(root):
        pytest.skip("ổ phân biệt hoa thường: cần ổ tìm tên không phân biệt hoa thường")
    original = ImageLibrary.list_folder
    swapped: list[bool] = []

    def swap_then_list(self, root_index, rel_dir="", **kwargs):
        if rel_dir == PROJECT and not swapped:
            swapped.append(True)
            os.rename(root / PROJECT / "CongAI", root / PROJECT / "CongAI cu")
            os.rename(root / PROJECT / "Khac", root / PROJECT / "Congai")
        return original(self, root_index, rel_dir, **kwargs)

    monkeypatch.setattr(ImageLibrary, "list_folder", swap_then_list)
    result = check_chosen_image(real_image(AI_PATH), ImageLibrary([root]))
    monkeypatch.undo()
    assert swapped
    if result.available:
        assert os.stat(root / result.ref.rel_path).st_ino == first.st_ino  # đúng file đã chọn
    assert_ai_wording(result)
