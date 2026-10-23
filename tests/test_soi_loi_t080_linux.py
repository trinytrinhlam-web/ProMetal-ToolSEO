"""Test thêm của Soi Lỗi T-080 (cloud Linux): câu báo khi đường dẫn bị tráo lúc ``resolve``.

T-080 sửa LC-T079-3 (SL-T079-L-1): ``resolve(strict=True)`` gặp lỗi vì một tầng vừa bị tráo thì
báo "vừa bị thay đổi". Lượt tráo thật trên cloud (báo cáo
``docs/team/reports/T-080-soi-loi-linux.md``) còn thấy một ca cùng loại, có từ trước T-079:
``resolve`` **không lỗi** mà đi trọn qua tầng vừa bị tráo thành symlink, rồi bước so kết quả báo
"nằm ngoài thư mục ảnh" (symlink ra ngoài) hay "tên ngắn hoặc tên khác của cùng một mục" (symlink
tới thư mục khác trong gốc) thay vì "vừa bị thay đổi". An toàn (không đọc gì, không lộ gì), chỉ sai
nghĩa câu báo.

Lỗi tìm được đánh dấu ``xfail(strict=True)`` kèm mã SL-T080-L-x. Mọi test dùng thư mục tạm, ảnh
giả, không gọi mạng.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from seo_app.images.folders import ImageFolderError, ImageLibrary, ImageRef

IS_WINDOWS = os.name == "nt"
posix_only = pytest.mark.skipif(IS_WINDOWS, reason="symlink thật, Mac/Linux")
SECRET = b"\xff\xd8 SECRET-NGOAI-GOC, dai hon anh moi"
DECOY = b"\xff\xd8 moi"
OTHER = b"\xff\xd8 anh khac trong goc"
CALLS = ["read_image_bytes", "stat_image", "list_folder"]
TARGETS = ["ngoai-goc", "trong-goc"]


def write(path: Path, data: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def assert_safe_error(exc: ImageFolderError, base: Path) -> None:
    text = str(exc)
    assert text
    for form in {str(base), str(base.resolve()), "ngoai", "SECRET"}:
        assert form not in text, f"câu lỗi lộ {form!r}"
    assert exc.__cause__ is None
    assert exc.__context__ is None or exc.__suppress_context__


def swapped_during_resolve(tmp_path: Path, monkeypatch, target: str, call: str):
    """``x`` là thư mục thật lúc vòng ``lstat`` của ``_resolve_inside`` xem, thành symlink (ra ngoài
    gốc, hay tới ``y`` trong gốc) đúng lúc ``resolve`` chạy, rồi trở lại thư mục thật ngay sau đó.
    Như ca 8a (ra ngoài) và 8f (trong gốc) của lượt tráo thật. Trả lời gọi app sẽ gặp tráo."""
    root = tmp_path / "anh"
    write(root / "x" / "bi-mat.jpg", DECOY)
    write(root / "y" / "bi-mat.jpg", OTHER)
    outside = tmp_path / "ngoai"
    write(outside / "bi-mat.jpg", SECRET)
    link_to = outside if target == "ngoai-goc" else root / "y"
    park = tmp_path / "cat-tam"
    x = root / "x"
    real_realpath = os.path.realpath

    def racing_realpath(path, *args, **kwargs):
        if os.path.basename(os.fsdecode(path)) not in ("bi-mat.jpg", "x"):
            return real_realpath(path, *args, **kwargs)
        x.rename(park)
        x.symlink_to(link_to, target_is_directory=True)
        try:
            return real_realpath(path, *args, **kwargs)
        finally:
            x.unlink()
            park.rename(x)

    lib = ImageLibrary([root])
    target_call = (
        (lambda: lib.list_folder(0, "x"))
        if call == "list_folder"
        else (lambda: getattr(lib, call)(ImageRef(0, "x/bi-mat.jpg")))
    )
    target_call()  # chưa bị tấn công
    monkeypatch.setattr(os.path, "realpath", racing_realpath)
    return target_call, x


@posix_only
@pytest.mark.parametrize("target", TARGETS)
@pytest.mark.parametrize("call", CALLS)
def test_swap_during_resolve_is_refused_safely(tmp_path, monkeypatch, target, call):
    """Đối chứng (qua): tráo đúng lúc ``resolve`` thì app từ chối, câu báo không lộ đường dẫn, không
    đọc được nội dung hay số liệu của mục ngoài ``x``; sau đó ``x`` vẫn là thư mục thật."""
    target_call, x = swapped_during_resolve(tmp_path, monkeypatch, target, call)
    with pytest.raises(ImageFolderError) as info:
        target_call()
    assert_safe_error(info.value, tmp_path)
    assert x.is_dir() and not x.is_symlink()


@posix_only
@pytest.mark.xfail(
    strict=True,
    reason="SL-T080-L-1 (soi-loi): resolve(strict=True) đi trọn qua tầng vừa bị tráo thành symlink "
    "(vòng lstat trước đó vừa thấy thư mục thật), _resolve_inside báo 'Đường dẫn nằm ngoài thư mục "
    "ảnh được phép.' hay 'Đường dẫn ảnh không hợp lệ (tên ngắn hoặc tên khác của cùng một mục).' "
    "thay vì 'vừa bị thay đổi'. Có từ trước T-079; an toàn, chỉ sai nghĩa câu báo",
)
@pytest.mark.parametrize("target", TARGETS)
@pytest.mark.parametrize("call", CALLS)
def test_sl_t080_l_1_swap_during_resolve_is_reported_as_changed(
    tmp_path, monkeypatch, target, call
):
    """Lượt tráo thật trên cloud (bản T-080): ca 8a, 8c, 8d, 8e báo "nằm ngoài thư mục ảnh" hàng
    trăm nghìn lần, ca 8f báo "tên ngắn hoặc tên khác" khoảng 90.000 lần (bản trước T-080 cũng
    vậy). Trên Mac/Linux, sau vòng ``lstat`` không thấy liên kết nào, ``resolve`` ra chỗ khác
    ``gốc/parts`` chỉ có thể vì đường dẫn vừa bị tráo (tên ngắn 8.3 chỉ có trên Windows): người
    dùng nên được bảo "hãy thử lại", không phải "đường dẫn không hợp lệ" hay "nằm ngoài thư mục
    ảnh"."""
    target_call, _x = swapped_during_resolve(tmp_path, monkeypatch, target, call)
    with pytest.raises(ImageFolderError) as info:
        target_call()
    assert "thay đổi" in str(info.value)
