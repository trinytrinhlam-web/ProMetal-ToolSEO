"""Test thêm của Soi Lỗi T-080 (phần Windows): so đường dẫn thật từng chữ, câu báo khi bị tráo.

T-080 dọn LC-T079-1 (Windows so đường dẫn thật của handle từng chữ, không gộp hoa thường hay dạng
Unicode), LC-T079-2 (câu báo cỡ, loại tả mục lấy lại trong thư mục ảnh), LC-T079-3 (lỗi ``resolve``
khi bị tráo là "vừa bị thay đổi"). File này thêm:

- Không chặn oan: tên có dấu dạng NFC và NFD, tên dài, chữ hoa thường lẫn lộn, ``ref`` và gốc gõ
  khác hoa thường vẫn đọc, kiểm, xem được.
- Ép kẻ tráo "luôn thắng" khi ``ref`` gõ khác hoa thường (đọc ảnh Windows đi nhánh hỏi lại tên
  trên ổ, commit ``62a16f5``), cả lúc hỏi tên (``FindFirstFileW``): không đọc, không trả cỡ, không
  tả file ngoài thư mục ảnh.
- SL-T080-1: Windows, thư mục ảnh vừa bị dời đi giữa lúc kiểm và lúc mở handle hỏi thuộc tính thì
  báo "không có quyền hoặc ổ đĩa vừa bị ngắt" (``_opened_stat``).
- SL-T080-2: Windows, xem thư mục khi không giữ được thư mục (lỗi 32 lúc chương trình khác đang đổi
  tên nó) mà thư mục vừa bị dời đi thì báo "không có quyền hoặc ổ đĩa vừa bị ngắt"
  (``_read_entries``).
- SL-T080-L-1 phần Windows (lỗi của lượt Linux, ``tests/test_soi_loi_t080_linux.py``): tráo đúng
  lúc ``resolve`` thì báo "nằm ngoài thư mục ảnh" hay "tên ngắn hoặc tên khác", không "vừa bị thay
  đổi".

Lỗi tìm được đánh dấu ``xfail(strict=True)`` kèm mã (xem ``docs/team/reports/T-080-soi-loi.md``).
Mọi test dùng thư mục tạm, ảnh giả, không gọi mạng.
"""

from __future__ import annotations

import os
import unicodedata
from pathlib import Path

import pytest

from seo_app.images import folders
from seo_app.images.folders import ImageFolderError, ImageLibrary, ImageRef

IS_WINDOWS = os.name == "nt"
windows_only = pytest.mark.skipif(not IS_WINDOWS, reason="junction, handle: thử trên Windows")
SECRET = b"\xff\xd8 SECRET-NGOAI-GOC, dai hon anh moi"
DECOY = b"\xff\xd8 moi"
OTHER = b"\xff\xd8 anh khac trong goc"
CALLS = ["read_image_bytes", "stat_image", "list_folder"]
OUTSIDE_WORDS = ("MB", "rỗng", "không phải là file ảnh")


def write(path: Path, data: bytes = b"\xff\xd8\xff anh gia") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def assert_no_abs_path(text: str, *paths: Path) -> None:
    for path in paths:
        for form in {str(path), str(path.resolve()), path.as_posix(), path.resolve().as_posix()}:
            assert form not in text, f"lộ đường dẫn tuyệt đối: {form!r}"


def raises_safely(func, *paths: Path) -> ImageFolderError:
    """Gọi ``func``, bắt buộc ``ImageFolderError`` có câu không chứa đường dẫn tuyệt đối."""
    with pytest.raises(ImageFolderError) as info:
        func()
    exc = info.value
    assert str(exc)
    assert_no_abs_path(str(exc), *paths)
    assert "SECRET" not in str(exc)
    assert exc.__cause__ is None
    assert exc.__context__ is None or exc.__suppress_context__
    return exc


def basename(path) -> str:
    try:
        return os.path.basename(os.fsdecode(path)).casefold()
    except TypeError:  # fd, không phải đường dẫn
        return ""


def case_insensitive(folder: Path) -> bool:
    probe = folder / "Thu-Hoa-Thuong"
    probe.mkdir()
    try:
        return (folder / "thu-hoa-thuong").exists()
    finally:
        probe.rmdir()


def call_on(lib: ImageLibrary, call: str, rel: str):
    if call == "list_folder":
        return lib.list_folder(0, rel.rsplit("/", 1)[0])
    return getattr(lib, call)(ImageRef(0, rel))


# ----- Không chặn oan -------------------------------------------------------------------------

NFC_DIR = unicodedata.normalize("NFC", "Cổng sắt Tân Phú")
NFD_DIR = unicodedata.normalize("NFD", "Cửa kéo Thủ Đức")
LONG_DIR = "Công trình " + "rất dài " * 7 + "cuối"
NORMAL_IMAGES = {
    f"{NFC_DIR}/Ảnh trước.jpg": b"\xff\xd8 nfc",
    f"{NFD_DIR}/" + unicodedata.normalize("NFD", "ảnh sau ĐẸP.JPG"): b"\xff\xd8 nfd",
    f"{LONG_DIR}/" + "Hình hàn khung " * 3 + "xong.png": b"\x89PNG dai",
    "CongAI Mixed-Case/Sub DIR/IMG_0001.JPG": b"\xff\xd8 hoa thuong",
}


@pytest.mark.parametrize(
    "root_typed",
    [
        "dung",
        pytest.param("chu-thuong", marks=windows_only),
        pytest.param("chu-hoa", marks=windows_only),
    ],
)
def test_normal_folders_are_read_listed_and_checked(tmp_path, root_typed):
    """So đường dẫn thật từng chữ không chặn oan: tên có dấu dạng NFC lẫn NFD, tên dài, chữ hoa
    thường lẫn lộn, gốc gõ khác hoa thường (Windows) đều đọc, kiểm, xem được; ``ref`` lấy từ danh
    sách đọc lại đúng nội dung."""
    root = tmp_path / unicodedata.normalize("NFD", "Ảnh công trình")
    for rel, data in NORMAL_IMAGES.items():
        write(root.joinpath(*rel.split("/")), data)
    typed = {"dung": str(root), "chu-thuong": str(root).lower(), "chu-hoa": str(root).upper()}
    lib = ImageLibrary([typed[root_typed]])
    listing = lib.list_folder(0, "", recursive=True, max_depth=3)
    assert sorted(entry.ref.rel_path for entry in listing.images) == sorted(NORMAL_IMAGES)
    assert listing.skipped == folders.SkipCounts()
    for entry in listing.images:
        data = NORMAL_IMAGES[entry.ref.rel_path]
        assert lib.read_image_bytes(entry.ref) == data
        checked = lib.stat_image(entry.ref)
        assert (checked.ref, checked.size) == (entry.ref, len(data))
        folder = entry.ref.rel_path.rsplit("/", 1)[0]
        assert entry.ref in [image.ref for image in lib.list_folder(0, folder).images]


def test_ref_typed_in_other_case_reads_by_disk_names(tmp_path):
    """``ref`` gõ khác hoa thường (ổ không phân biệt hoa thường): đọc đúng nội dung, ``stat_image``
    và ``list_folder`` trả tên trên ổ."""
    root = tmp_path / "anh"
    for rel, data in NORMAL_IMAGES.items():
        write(root.joinpath(*rel.split("/")), data)
    if not case_insensitive(root):
        pytest.skip("ổ phân biệt hoa thường")
    lib = ImageLibrary([root])
    for rel, data in NORMAL_IMAGES.items():
        for typed in {rel.upper(), rel.lower()}:
            assert lib.read_image_bytes(ImageRef(0, typed)) == data
            assert lib.stat_image(ImageRef(0, typed)).ref == ImageRef(0, rel)
            folder = typed.rsplit("/", 1)[0]
            assert [e.ref for e in lib.list_folder(0, folder).images] == [ImageRef(0, rel)]


# ----- Ép thắng khi ``ref`` gõ khác hoa thường (Windows) ----------------------------------------

ROOT_NFC = unicodedata.normalize("NFC", "Ảnh kho sân")
TWINS = {
    "ngoai-goc-thuong": None,
    "anh-em-nfd": unicodedata.normalize("NFD", ROOT_NFC),
    "anh-em-dau-kelvin": ROOT_NFC.replace("k", "K"),
}


@windows_only
@pytest.mark.parametrize("payload", ["bi-mat", "qua-co"])
@pytest.mark.parametrize("call", ["read_image_bytes", "stat_image"])
@pytest.mark.parametrize("twin", TWINS.values(), ids=TWINS.keys())
def test_forced_swap_with_ref_typed_in_other_case_never_describes_outside(
    tmp_path, monkeypatch, twin, call, payload
):
    """``ref`` gõ CHỮ HOA nên đọc ảnh Windows hỏi lại tên trên ổ rồi mới mở (``62a16f5``). Kẻ tráo
    luôn thắng: ``x`` là junction trỏ vào ``x`` của đích mỗi khi app ``lstat``, mở, mở handle hỏi
    thuộc tính **hay hỏi tên trên ổ** (``_win_listed_name``) mục ảnh. Đích ngoài gốc tên thường,
    hay thư mục anh em tên trông y hệt (NFD, dấu Kelvin). Không đọc được nội dung, không trả cỡ,
    câu báo không tả file ngoài (quá cỡ). Bản ``main`` 417efea: đích anh em lọt nội dung, cỡ;
    đích quá cỡ báo "Ảnh quá lớn (2,0 MB)"."""
    import _winapi

    base = tmp_path / "cha"
    root = base / ROOT_NFC
    write(root / "x" / "bi-mat.jpg", DECOY)
    target = (base / twin if twin else tmp_path / "ngoai") / "x"
    write(target / "bi-mat.jpg", SECRET if payload == "bi-mat" else b"x" * (2 * 1024 * 1024))
    if twin is not None:
        assert len(os.listdir(base)) == 2, "ổ coi hai tên là một"
    if not case_insensitive(root):
        pytest.skip("thư mục tạm phân biệt hoa thường")
    lib = ImageLibrary([root], max_file_bytes=1024 * 1024)
    ref = ImageRef(0, "X/BI-MAT.JPG")
    assert lib.read_image_bytes(ref) == DECOY  # chưa bị tráo: dùng được

    x, park = root / "x", tmp_path / "cat-tam"

    def swapped(real):
        def wrapped(path, *args, **kwargs):
            if basename(path) != "bi-mat.jpg":
                return real(path, *args, **kwargs)
            x.rename(park)
            _winapi.CreateJunction(str(target), str(x))
            try:
                return real(path, *args, **kwargs)
            finally:
                os.rmdir(x)
                park.rename(x)

        return wrapped

    with monkeypatch.context() as patch:
        patch.setattr(folders.os, "lstat", swapped(os.lstat))
        patch.setattr(folders.os, "open", swapped(os.open))
        patch.setattr(folders, "_win_open", swapped(folders._win_open))
        patch.setattr(folders, "_win_listed_name", swapped(folders._win_listed_name))
        try:
            result = getattr(lib, call)(ref)
        except ImageFolderError as exc:
            assert_no_abs_path(str(exc), tmp_path)
            assert not any(word in str(exc) for word in OUTSIDE_WORDS), f"tả file ngoài: {exc}"
        else:
            if call == "read_image_bytes":
                assert result == DECOY, "đọc được file ngoài thư mục ảnh"
            else:
                assert result.size == len(DECOY), "trả cỡ file ngoài thư mục ảnh"
    assert not x.is_junction() and (x / "bi-mat.jpg").read_bytes() == DECOY


@windows_only
@pytest.mark.parametrize("call", ["read_image_bytes", "stat_image"])
def test_kelvin_sibling_seen_by_lstat_and_resolve_is_not_opened(tmp_path, monkeypatch, call):
    """Đường lọt thật trên ``main`` 417efea (tráo thật: lọt nội dung 39/2.783 vòng): ``x`` là
    junction tới ``x`` của thư mục anh em tên dấu Kelvin đúng lúc ``lstat`` mục ảnh và lúc
    ``resolve``, thư mục thật lúc mở. ``is_relative_to`` (so chữ thường) và khóa tên (``casefold``)
    coi tên anh em là gốc, nên ``resolve`` trả đường dẫn trong thư mục anh em; bản cũ mở thẳng
    đường dẫn đó (không cần thắng lúc mở). T-080 không mở theo đường dẫn ``resolve`` trả: đọc ra
    ảnh mồi hoặc báo lỗi, không bao giờ ra nội dung, cỡ file ngoài."""
    import _winapi

    base = tmp_path / "cha"
    root = base / ROOT_NFC
    write(root / "x" / "bi-mat.jpg", DECOY)
    target = base / TWINS["anh-em-dau-kelvin"] / "x"
    write(target / "bi-mat.jpg", SECRET)
    assert len(os.listdir(base)) == 2, "ổ coi hai tên là một"
    lib = ImageLibrary([root])
    x, park = root / "x", tmp_path / "cat-tam"

    def swapped(real):
        def wrapped(path, *args, **kwargs):
            if basename(path) != "bi-mat.jpg":
                return real(path, *args, **kwargs)
            x.rename(park)
            _winapi.CreateJunction(str(target), str(x))
            try:
                return real(path, *args, **kwargs)
            finally:
                os.rmdir(x)
                park.rename(x)

        return wrapped

    with monkeypatch.context() as patch:
        patch.setattr(folders.os, "lstat", swapped(os.lstat))
        patch.setattr(Path, "resolve", swapped(Path.resolve))
        try:
            result = getattr(lib, call)(ImageRef(0, "x/bi-mat.jpg"))
        except ImageFolderError as exc:
            assert_no_abs_path(str(exc), tmp_path)
        else:
            assert (result if call == "read_image_bytes" else result.size) in (DECOY, len(DECOY))
    assert not x.is_junction() and (x / "bi-mat.jpg").read_bytes() == DECOY


# ----- SL-T080-1: handle hỏi thuộc tính mở hỏng vì thư mục vừa bị dời đi (Windows) --------------


@windows_only
@pytest.mark.parametrize(
    ("call", "size"),
    [
        pytest.param("stat_image", 8, id="stat-anh-thuong"),
        pytest.param("stat_image", 2048, id="stat-anh-qua-co"),
        pytest.param("read_image_bytes", 2048, id="doc-anh-qua-co"),
    ],
)
def test_sl_t080_1_folder_moved_before_attribute_handle_is_not_permission_error(
    tmp_path, monkeypatch, call, size
):
    """``x`` bị chương trình khác dời đi ngay lúc app mở handle hỏi thuộc tính của ảnh (sau khi đã
    kiểm đường đi và tên trên ổ), rồi trả lại. Ổ báo lỗi 3 (không thấy đường dẫn): ảnh vừa bị thay
    đổi hay không tìm thấy, không phải "không có quyền". Ảnh quá cỡ (đi đường lấy lại mục để báo,
    LC-T079-2) cũng vậy. Bản Mac/Linux của bước này báo "Không tìm thấy"."""
    root = tmp_path / "anh"
    write(root / "x" / "a.jpg", b"x" * size)
    x, park = root / "x", tmp_path / "cat-tam"
    real_win_open = folders._win_open

    def win_open(path, access):
        if basename(path) != "a.jpg" or access != folders._FILE_READ_ATTRIBUTES:
            return real_win_open(path, access)
        x.rename(park)
        try:
            return real_win_open(path, access)
        finally:
            park.rename(x)

    monkeypatch.setattr(folders, "_win_open", win_open)
    lib = ImageLibrary([root], max_file_bytes=1024)
    exc = raises_safely(lambda: getattr(lib, call)(ImageRef(0, "x/a.jpg")), tmp_path)
    assert "không có quyền" not in str(exc)
    assert "thay đổi" in str(exc) or "Không tìm thấy" in str(exc)


# ----- SL-T080-2: xem thư mục không giữ được, thư mục vừa bị dời đi (Windows) --------------------


@windows_only
def test_sl_t080_2_folder_moved_before_listing_is_not_permission_error(tmp_path, monkeypatch):
    """App không giữ được ``x`` (như lỗi 32 đo được khi chương trình khác đang đổi tên ``x``), nên
    kiểm đường đi rồi đọc danh sách theo tên; ``x`` bị dời đi đúng lúc đó. Mong đợi "vừa bị thay
    đổi" hay "không tìm thấy", không phải "không có quyền"."""
    root = tmp_path / "anh"
    write(root / "x" / "a.jpg")
    lib = ImageLibrary([root])
    x, park = root / "x", tmp_path / "cat-tam"
    held = os.path.normcase(str(x.resolve()))
    real_win_open, real_scandir = folders._win_open, os.scandir

    def win_open(path, access):
        if os.path.normcase(str(path)) == held:
            return None  # không giữ được thư mục (lỗi 32)
        return real_win_open(path, access)

    def scandir(path):
        if isinstance(path, int) or os.path.normcase(str(path)) != held:
            return real_scandir(path)
        x.rename(park)
        try:
            return real_scandir(path)
        finally:
            park.rename(x)

    monkeypatch.setattr(folders, "_win_open", win_open)
    monkeypatch.setattr(folders.os, "scandir", scandir)
    exc = raises_safely(lambda: lib.list_folder(0, "x"), tmp_path)
    assert "không có quyền" not in str(exc)
    assert "thay đổi" in str(exc) or "Không tìm thấy" in str(exc)


# ----- SL-T080-L-1 phần Windows: tráo đúng lúc ``resolve`` -------------------------------------

TARGETS = ["ngoai-goc", "trong-goc"]


def swapped_during_resolve(tmp_path: Path, monkeypatch, target: str, call: str):
    """``x`` là thư mục thật lúc vòng ``lstat`` của ``_resolve_inside`` xem, thành junction (ra
    ngoài gốc, hay tới ``y`` trong gốc) đúng lúc ``resolve`` chạy, rồi trở lại thư mục thật. Trả
    lời gọi app sẽ gặp tráo."""
    import _winapi

    root = tmp_path / "anh"
    write(root / "x" / "bi-mat.jpg", DECOY)
    write(root / "y" / "bi-mat.jpg", OTHER)
    outside = tmp_path / "ngoai"
    write(outside / "bi-mat.jpg", SECRET)
    link_to = outside if target == "ngoai-goc" else root / "y"
    x, park = root / "x", tmp_path / "cat-tam"
    real_resolve = Path.resolve

    def racing_resolve(self, strict=False):
        if self.name not in ("bi-mat.jpg", "x"):
            return real_resolve(self, strict=strict)
        x.rename(park)
        _winapi.CreateJunction(str(link_to), str(x))
        try:
            return real_resolve(self, strict=strict)
        finally:
            os.rmdir(x)
            park.rename(x)

    lib = ImageLibrary([root])
    call_on(lib, call, "x/bi-mat.jpg")  # chưa bị tấn công
    monkeypatch.setattr(Path, "resolve", racing_resolve)
    return (lambda: call_on(lib, call, "x/bi-mat.jpg")), x


@windows_only
@pytest.mark.parametrize("target", TARGETS)
@pytest.mark.parametrize("call", CALLS)
def test_swap_during_resolve_is_refused_safely_on_windows(tmp_path, monkeypatch, target, call):
    """Đối chứng (qua): tráo đúng lúc ``resolve`` thì app từ chối, câu báo không lộ đường dẫn, không
    đọc được nội dung hay số liệu của mục ngoài ``x``; sau đó ``x`` vẫn là thư mục thật."""
    with monkeypatch.context() as patch:
        target_call, x = swapped_during_resolve(tmp_path, patch, target, call)
        raises_safely(target_call, tmp_path)
    assert not x.is_junction() and (x / "bi-mat.jpg").read_bytes() == DECOY


@windows_only
@pytest.mark.parametrize("target", TARGETS)
@pytest.mark.parametrize("call", CALLS)
def test_sl_t080_l_1_windows_swap_during_resolve_is_reported_as_changed(
    tmp_path, monkeypatch, target, call
):
    """Tráo thật trên Windows (báo cáo ``T-080-soi-loi.md``) cũng ra hai câu này. Vòng ``lstat``
    vừa thấy mọi tầng không phải liên kết, nên ``resolve`` ra ngoài gốc hay ra mục khác (định danh
    khác ``lstat``) chỉ có thể vì đường dẫn vừa bị tráo: người dùng nên được bảo "hãy thử lại"."""
    target_call, _x = swapped_during_resolve(tmp_path, monkeypatch, target, call)
    exc = raises_safely(target_call, tmp_path)
    assert "thay đổi" in str(exc)
