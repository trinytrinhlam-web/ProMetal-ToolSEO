"""Lá Chắn T-116, nhóm 1 (đọc ảnh từ thư mục, xử lý ảnh, HEIC): lỗi mới tìm thấy khi kiểm lại bằng
Fable 5.1 (``docs/team/reports/T-116-la-chan-nhom-1.md``).

Mỗi lỗi được đánh dấu ``xfail(strict=True)``: sửa xong thì test tự báo XPASS để gỡ dấu. Không gọi
mạng, không đụng ``data/`` thật của dự án (mọi thứ nằm trong ``tmp_path``).

LC-T116-1 (Thấp): hai chỗ app ghi file trong ``data/`` không kiểm liên kết ở **tầng thư mục**:

- ``PreviewCache`` (``seo_app/images/process.py``): ``_cache_dir_is_ignored`` ``resolve`` thư mục
  cache; thư mục ``data/`` (hay ``data/image_previews``) là junction/symlink trỏ ra ngoài dự án thì
  ``resolve`` ra ngoài gốc dự án → hàm trả ``True`` («git không thấy») → cache **bật** và ảnh xem
  trước được ghi vào nơi liên kết trỏ tới.
- ``ImageTagStore`` (``seo_app/storage/image_tags.py``): ``_remove_links`` chỉ gỡ liên kết ở đúng
  tên file ``image_tags.sqlite`` và file nhật ký; thư mục cha ``data/`` là liên kết thì file SQLite
  được tạo và ghi bên trong nơi liên kết trỏ tới.

Muốn đặt được liên kết đó phải ghi được vào thư mục dự án trên máy người dùng (cùng lớp với các
dòng «phải chiếm máy trước» trong sổ rủi ro), nên mức Thấp. Cách sửa gợi ý: một hàm dùng chung
``lstat`` từng tầng từ gốc dự án xuống tới ``data/…`` và từ chối symlink/junction (như
``_is_link``), dùng cho cả hai module; hoặc đòi ``data.resolve() == PROJECT_ROOT / "data"`` đúng
từng chữ trước khi ghi.
"""

from __future__ import annotations

import contextlib
import io
import os
from pathlib import Path

import pytest
from PIL import Image

from seo_app.images import process
from seo_app.images.folders import ImageLibrary, ImageRef
from seo_app.images.process import PreviewCache
from seo_app.images.tags import SOURCE_AI, ImageTags
from seo_app.storage.image_tags import ImageTagStore, ImageTagStoreError


def _link_dir(link: Path, target: Path) -> None:
    """Liên kết thư mục không cần quyền quản trị: junction trên Windows, symlink trên Mac/Linux."""
    if os.name == "nt":
        import _winapi

        _winapi.CreateJunction(str(target), str(link))
    else:
        os.symlink(target, link, target_is_directory=True)


@pytest.fixture
def linked_project(tmp_path: Path, monkeypatch) -> tuple[Path, Path]:
    """Thư mục dự án giả có ``.gitignore`` chặn ``data/`` như thật, nhưng ``data`` là liên kết trỏ
    ra một thư mục ngoài dự án. Trả (gốc dự án, thư mục ngoài)."""
    project = tmp_path / "du-an"
    project.mkdir()
    (project / ".gitignore").write_text("data/\n", encoding="utf-8")
    outside = tmp_path / "ngoai-du-an"
    outside.mkdir()
    _link_dir(project / "data", outside)
    monkeypatch.setattr(process, "PROJECT_ROOT", project)
    return project, outside


@pytest.fixture
def image_root(tmp_path: Path) -> Path:
    root = tmp_path / "anh"
    root.mkdir()
    buffer = io.BytesIO()
    Image.new("RGB", (40, 30), (90, 120, 150)).save(buffer, "JPEG")
    (root / "cong.jpg").write_bytes(buffer.getvalue())
    return root


@pytest.mark.xfail(
    strict=True,
    reason="LC-T116-1: thư mục data/ là junction thì PreviewCache vẫn bật và ghi ảnh xem trước "
    "vào nơi liên kết trỏ tới",
)
def test_lc_t116_1_preview_cache_khong_ghi_xuyen_lien_ket(linked_project, image_root) -> None:
    """Mong đợi: ``data/`` là liên kết thì cache không bật (hoặc không ghi gì qua liên kết); ảnh
    xem trước vẫn được dựng và trả về. Thực tế: ``enabled`` là ``True`` và file ``<băm>.jpg`` xuất
    hiện trong thư mục ngoài dự án."""
    project, outside = linked_project
    cache = PreviewCache(project / "data" / "image_previews")
    library = ImageLibrary([image_root])
    preview = cache.get(library, ImageRef(0, "cong.jpg"))
    assert preview[:2] == b"\xff\xd8"  # ảnh xem trước vẫn phải có
    written = [p for p in outside.rglob("*") if p.is_file()]
    assert not written, "cache ảnh xem trước đã ghi xuyên liên kết ra ngoài thư mục dự án"


@pytest.mark.xfail(
    strict=True,
    reason="LC-T116-1: thư mục data/ là junction thì ImageTagStore tạo và ghi file SQLite vào nơi "
    "liên kết trỏ tới",
)
def test_lc_t116_1_kho_the_khong_ghi_xuyen_lien_ket(linked_project) -> None:
    """Mong đợi: ``data/`` là liên kết thì kho thẻ từ chối (``ImageTagStoreError``) hoặc không tạo
    file qua liên kết. Thực tế: ``image_tags.sqlite`` được tạo trong thư mục ngoài dự án."""
    project, outside = linked_project
    store = ImageTagStore(project / "data" / "image_tags.sqlite")
    with contextlib.suppress(ImageTagStoreError):
        store.set(ImageRef(0, "cong.jpg"), ImageTags(source=SOURCE_AI))
    assert not (outside / "image_tags.sqlite").exists(), (
        "kho thẻ sửa tay đã được tạo xuyên liên kết ra ngoài thư mục dự án"
    )
