"""Test thêm của Soi Lỗi T-117: các kho khác cũng ghi vào ``data/`` khi ``data/`` là liên kết.

T-117 sửa LC-T116-1 cho cache ảnh xem trước và kho thẻ ảnh. Ba kho khác cùng ghi vào ``data/``
chưa có lớp kiểm này (Thợ Máy đã nêu ở «Đề xuất 1» của báo cáo T-117):

- SL-T117-1 (Thấp, có từ trước, cùng loại LC-T116-1): ``data/`` là junction (Windows) hay symlink
  (Mac/Linux) trỏ ra ngoài thư mục dự án thì kho nháp bài viết (``drafts.sqlite``), cache kế hoạch
  (``plan_cache.sqlite``) và danh sách bài đã đăng (``site_index.sqlite``) tạo, ghi file SQLite ở
  nơi liên kết trỏ tới. Kho nháp ``_prepare`` không kiểm liên kết ở tầng nào; hai kho sau chỉ xét
  ``self.path.is_symlink()`` ở chính file (không bắt junction, không xét thư mục cha).

Mong đợi (không ràng cách sửa): không file nào xuất hiện ở nơi liên kết trỏ tới; kho được phép báo
lỗi riêng của nó. Liên kết thật: junction trên Windows (không cần quyền quản trị), symlink trên
Mac/Linux. Lỗi đánh dấu ``xfail(strict=True)`` kèm mã SL-T117-x.
"""

from __future__ import annotations

import contextlib
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from seo_app.storage.drafts import DraftError, DraftSnapshot, DraftStore, new_draft_id
from seo_app.storage.plan_cache import PlanCacheError, PlanCacheStore
from seo_app.storage.site_index import SiteIndex, SiteIndexError, SiteIndexStore

NOW = datetime(2026, 11, 2, 13, 30, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh"))


def link_dir(link: Path, target: Path) -> None:
    if os.name == "nt":
        import _winapi

        _winapi.CreateJunction(str(target), str(link))
    else:
        os.symlink(target, link, target_is_directory=True)


@pytest.fixture
def linked_data(tmp_path: Path):
    """``du-an/data`` là liên kết tới ``ngoai-du-an``. Trả (thư mục data, thư mục ngoài)."""
    project = tmp_path / "du-an"
    outside = tmp_path / "ngoai-du-an"
    project.mkdir()
    outside.mkdir()
    link_dir(project / "data", outside)
    yield project / "data", outside
    with contextlib.suppress(OSError):
        os.rmdir(project / "data")  # gỡ chính liên kết, không đụng thư mục đích


def _written(outside: Path) -> list[str]:
    return sorted(p.name for p in outside.rglob("*") if p.is_file())


def _drafts(data: Path) -> None:
    DraftStore(path=data / "drafts.sqlite").save(DraftSnapshot(id=new_draft_id(), keyword="cổng"))


def _plan_cache(data: Path) -> None:
    PlanCacheStore(path=data / "plan_cache.sqlite").save("1" * 44, [["Mã", "Từ khóa"]], NOW)


def _site_index(data: Path) -> None:
    SiteIndexStore(path=data / "site_index.sqlite").save(
        SiteIndex(site="https://vi-du.test", fetched_at=NOW, items=())
    )


def test_preview_cache_check_error_means_no_cache(tmp_path, monkeypatch):
    """Bổ sung test (thử đột biến D7): ``lstat`` của ``data`` lỗi lạ (không phải «không có», ví
    dụ bị từ chối quyền) thì không kiểm được liên kết: cache không đọc, không ghi (đóng an toàn),
    ảnh xem trước vẫn được dựng. Trước đây không test nào ghim nhánh ``except OSError`` của
    ``PreviewCache._no_link``."""
    import io

    from PIL import Image

    from seo_app.images import process
    from seo_app.images.folders import ImageLibrary, ImageRef

    project = tmp_path / "du-an"
    (project / "data" / "image_previews").mkdir(parents=True)
    (project / ".gitignore").write_text("data/\n", encoding="utf-8")
    monkeypatch.setattr(process, "PROJECT_ROOT", project)
    images = tmp_path / "anh"
    images.mkdir()
    buffer = io.BytesIO()
    Image.new("RGB", (40, 30), (90, 120, 150)).save(buffer, "JPEG")
    (images / "cong.jpg").write_bytes(buffer.getvalue())
    cache = process.PreviewCache(project / "data" / "image_previews")
    assert cache.enabled
    real_lstat = os.lstat
    blocked = os.path.normcase(str(project / "data"))

    def lstat(path, *args, **kwargs):
        if os.path.normcase(os.fspath(path)) == blocked:
            raise PermissionError(13, "Permission denied")
        return real_lstat(path, *args, **kwargs)

    monkeypatch.setattr(os, "lstat", lstat)
    preview = cache.get(ImageLibrary([images]), ImageRef(0, "cong.jpg"))
    assert preview[:2] == bytes([0xFF, 0xD8])
    assert list((project / "data" / "image_previews").iterdir()) == []


@pytest.mark.xfail(
    strict=True,
    reason=(
        "SL-T117-1 (soi-loi, có từ trước, cùng loại LC-T116-1): data/ là liên kết thì kho nháp, "
        "cache kế hoạch, danh sách bài đã đăng ghi file SQLite ra nơi liên kết trỏ tới (ngoài dự "
        "án); chưa dùng dir_has_link như cache ảnh, kho thẻ (T-117 Đề xuất 1)"
    ),
)
@pytest.mark.parametrize(
    ("write", "errors"),
    [
        (_drafts, (DraftError,)),
        (_plan_cache, (PlanCacheError,)),
        (_site_index, (SiteIndexError,)),
    ],
    ids=["kho-nhap", "cache-ke-hoach", "danh-sach-bai-da-dang"],
)
def test_sl_t117_1_other_data_stores_never_write_through_link(linked_data, write, errors):
    data, outside = linked_data
    with contextlib.suppress(*errors):
        write(data)
    assert _written(outside) == [], "kho đã ghi file xuyên liên kết ra ngoài thư mục dự án"
