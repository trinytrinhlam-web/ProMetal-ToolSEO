"""Test của Lá Chắn T-079: lỗi còn lại sau bản vá đọc ảnh qua chính mục đã mở (``folders.py``).

- LC-T079-2: ``_checked_file`` kiểm loại file, cỡ trên ``lstat`` đi theo chuỗi đường dẫn và báo lỗi
  TRƯỚC lớp kiểm trên mục đã mở (``_open_image``, ``_opened_stat``). Khi một tầng giữa vừa bị tráo
  thành liên kết đúng lúc ``lstat`` mục cuối (như SL-T063-2, -3), ``lstat`` đi xuyên ra file NGOÀI
  thư mục ảnh và câu báo nói về file đó: "Ảnh quá lớn (2,0 MB)…", "File ảnh rỗng (0 byte).", "Đây
  không phải là file ảnh.". Mọi hệ điều hành (Linux thắng đua được thật). Ở đây giả đúng một bước:
  ``lstat`` của ``x/bi-mat.jpg`` trả số liệu của file ngoài gốc, mọi bước khác thấy ổ thật.
- LC-T079-1 (= SL-T079-1) ở đường xem thư mục: ``_scan_held`` (Windows, có từ T-048) cũng so đường
  dẫn thật của thư mục đang giữ bằng ``_path_key`` (NFC + ``casefold``), nên thư mục "anh em" của
  gốc tên trông y hệt (dạng NFD) qua phép so; ép kẻ tấn công thắng thì danh sách có tên, cỡ file
  ngoài thư mục ảnh. Các ca đọc, ``stat`` của SL-T079-1 nằm ở ``tests/test_soi_loi_t079.py``.

Lỗi đánh dấu ``xfail(strict=True)`` kèm mã LC-T079-x (xem ``docs/team/reports/T-079-la-chan.md``).
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
DECOY = b"\xff\xd8 moi"
REF = "x/bi-mat.jpg"
MAX_BYTES = 1024 * 1024


def write(path: Path, data: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def assert_no_abs_path(text: str, *paths: Path) -> None:
    for path in paths:
        for form in {str(path), str(path.resolve()), path.as_posix(), path.resolve().as_posix()}:
            assert form not in text, f"lộ đường dẫn tuyệt đối: {form!r}"


# ----- LC-T079-2: câu báo nói về file ngoài thư mục ảnh ---------------------------------------


def _outside_entry(path: Path, kind: str) -> None:
    if kind == "qua-co":
        write(path, b"\xff\xd8" + b"0" * (2 * MAX_BYTES))
    elif kind == "rong":
        write(path, b"")
    elif kind == "thu-muc":
        path.mkdir(parents=True)
    else:
        write(path, b"\xff\xd8 SECRET-NGOAI-GOC, dai hon anh moi")


OUTSIDE_KINDS = [
    pytest.param("qua-co", "MB", id="ngoai-qua-co"),
    pytest.param("rong", "rỗng", id="ngoai-rong"),
    pytest.param("thu-muc", "không phải là file ảnh", id="ngoai-la-thu-muc"),
    pytest.param("thuong", "MB", id="doi-chung-ngoai-co-thuong"),
]


@pytest.mark.parametrize("call", ["read_image_bytes", "stat_image"])
@pytest.mark.parametrize(("kind", "revealing"), OUTSIDE_KINDS)
def test_lc_t079_2_message_does_not_describe_outside_file(
    tmp_path, monkeypatch, call, kind, revealing
):
    """Kẻ tráo thắng đúng lúc ``lstat`` mục cuối (tầng ``x`` là liên kết ra ngoài lúc đó, là thư mục
    thật ở mọi bước khác). Mong đợi: báo lỗi gọn kiểu "vừa bị thay đổi" (mục đã mở khác mục vừa
    kiểm), không nói gì về file ngoài thư mục ảnh (cỡ, rỗng, không phải file). Ca đối chứng: file
    ngoài cỡ thường thì bản T-079 đã báo "vừa bị thay đổi"."""
    root = tmp_path / "anh"
    write(root / REF, DECOY)
    outside = tmp_path / "ngoai" / "bi-mat.jpg"
    _outside_entry(outside, kind)
    lib = ImageLibrary([root], max_file_bytes=MAX_BYTES)
    assert lib.read_image_bytes(ImageRef(0, REF)) == DECOY  # chưa bị tấn công

    image = os.path.normcase(str(root.resolve() / "x" / "bi-mat.jpg"))
    real_lstat = os.lstat

    def lstat_through_swapped_folder(path, *args, **kwargs):
        try:
            hit = os.path.normcase(os.fsdecode(path)) == image
        except TypeError:  # fd
            hit = False
        return real_lstat(outside if hit else path, *args, **kwargs)

    monkeypatch.setattr("seo_app.images.folders.os.lstat", lstat_through_swapped_folder)
    with pytest.raises(ImageFolderError) as info:
        getattr(lib, call)(ImageRef(0, REF))
    message = str(info.value)
    assert_no_abs_path(message, tmp_path)
    assert revealing not in message, f"câu báo nói về file ngoài thư mục ảnh: {message!r}"


# ----- LC-T079-1 ở đường xem thư mục (Windows) ------------------------------------------------

ROOT_NFC = unicodedata.normalize("NFC", "Ảnh công trình")


class _Listed:
    """Thay cho iterator của ``os.scandir`` (đã đọc hết trong lúc ``x`` còn là junction)."""

    def __init__(self, entries: list[os.DirEntry]) -> None:
        self._entries = iter(entries)

    def __enter__(self) -> _Listed:
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def __iter__(self) -> _Listed:
        return self

    def __next__(self) -> os.DirEntry:
        return next(self._entries)


@windows_only
@pytest.mark.parametrize(
    "sibling_name",
    [
        pytest.param(None, id="doi-chung-ngoai-goc-thuong"),
        pytest.param(unicodedata.normalize("NFD", ROOT_NFC), id="anh-em-nfd"),
    ],
)
def test_lc_t079_1_listing_through_lookalike_sibling_gives_no_outside_names(
    tmp_path, monkeypatch, sibling_name
):
    """Kẻ tráo thắng từ lúc app mở giữ thư mục ``x/y`` tới hết lúc đọc danh sách: ``x`` là junction
    trỏ vào ``x`` của thư mục đích. Đích ngoài gốc tên thường: đường dẫn thật của thư mục đang giữ
    khác ``gốc/x/y``, bản hiện tại đã chặn (đối chứng). Đích là thư mục anh em tên NFD của gốc:
    phép so ``_path_key`` coi là một. Mong đợi: báo lỗi gọn, hoặc danh sách không có tên file ngoài
    thư mục ảnh."""
    import _winapi

    parent = tmp_path / "cha"
    root = parent / ROOT_NFC
    write(root / "x" / "y" / "moi.jpg", DECOY)
    target = (parent / sibling_name if sibling_name else tmp_path / "ngoai") / "x"
    write(target / "y" / "chi-ngoai.jpg", b"\xff\xd8 SECRET-NGOAI-GOC")
    lib = ImageLibrary([root])
    assert [e.name for e in lib.list_folder(0, "x/y").images] == ["moi.jpg"]

    x, park = root.resolve() / "x", tmp_path / "cat-tam"
    held = os.path.normcase(str(x / "y"))
    swapped: list[bool] = []
    real_win_open, real_scandir = folders._win_open, os.scandir

    def swap_out() -> None:
        if swapped:
            os.rmdir(x)
            os.rename(park, x)
            swapped.clear()

    def win_open(path, *args, **kwargs):
        if os.path.normcase(str(path)) == held and not swapped:
            os.rename(x, park)
            _winapi.CreateJunction(str(target), str(x))
            swapped.append(True)
        return real_win_open(path, *args, **kwargs)

    def scandir(path):
        if swapped and not isinstance(path, int) and os.path.normcase(str(path)) == held:
            with real_scandir(path) as entries:
                listed = list(entries)
            swap_out()
            return _Listed(listed)
        return real_scandir(path)

    monkeypatch.setattr(folders, "_win_open", win_open)
    monkeypatch.setattr("seo_app.images.folders.os.scandir", scandir)
    try:
        listing = lib.list_folder(0, "x/y")
    except ImageFolderError as exc:
        assert_no_abs_path(str(exc), tmp_path)
    else:
        names = [e.name for e in listing.images]
        assert "chi-ngoai.jpg" not in names, "liệt kê được file ngoài thư mục ảnh"
    finally:
        swap_out()
    assert not x.is_junction()
