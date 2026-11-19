"""Ảnh minh họa AI do app tạo (T-142; thiết kế T-140 mục 2.6, 2.7; Lá Chắn LC-T140-5, -6, -13).

- ``make_generated_web_image``: byte ảnh Cloudflare trả về → WebP sạch.
  - Mở có kiểm (``process._open``: chỉ JPEG, PNG, WebP; giới hạn cỡ file, số điểm ảnh); ảnh tĩnh;
    cạnh 256–2048 px; từ chối ảnh gần một màu (bộ lọc an toàn chặn thì thường ra ảnh đen).
  - **Dựng lại từ điểm ảnh** (ảnh mới, không ``info``: không EXIF, XMP, ICC, chú thích, chunk chữ),
    rồi qua ``make_web_image`` (không phóng to, cạnh dài ≤ 1600 px).
  - Byte WebP ra phải qua bộ kiểm ``_check_webp`` của lớp AI (chỉ ``VP8``/``VP8L``/``VP8X``/
    ``ALPH``, không ``EXIF``/``XMP``/``ICCP``, không ảnh động): chỉ byte này được lưu, hiện, gửi.
    Byte gốc của Cloudflare không lưu, không gửi đi.
- ``wrap_generated``: kèm thẻ ảnh AI **do mã đặt** ngay lúc bọc (``ImageTags.for_ai_image``: chỉ
  hạng mục trong danh sách cố định; không mã công trình, khu vực, giai đoạn) và băm SHA-256.
  Tên file ``minh-hoa-ai-…`` (``generated_file_name``); alt «Minh họa…», chú thích «Ảnh minh họa
  (AI)…» do lớp alt và client WordPress bảo đảm như với mọi ảnh AI.
- ``AIImageStore``: kho ``data/ai_images/<sha256>.webp`` trên máy đang dùng.
  - Tên file là băm SHA-256 của chính byte WebP; ghi nguyên tử (file tạm rồi đổi tên); mỗi file
    ≤ 2 MB; thư mục phải nằm trong ``data/`` đã chặn ở ``.gitignore``.
  - ``dir_has_link`` trước mỗi lần đọc, ghi, xóa (T-117): ``data/`` hay thư mục con là lối tắt thì
    không đọc, không ghi.
  - Đọc lại phải khớp băm với tên file (và với nháp: nơi gọi truyền đúng băm của nháp), rồi kiểm
    ``_check_webp`` lại.
  - Dọn chỉ xóa tên đúng mẫu ``^[0-9a-f]{64}\\.webp$`` trong đúng thư mục, giữ file còn được nháp
    nhắc tới (kể cả ảnh trước trong ``history``); ngưỡng 14 ngày, 500 file, 500 MB.

Không nhập ``streamlit``: gọi được từ luồng nền (LC-T141-9). Câu lỗi tiếng Việt cố định, không có
đường dẫn trên máy.
"""

from __future__ import annotations

import hashlib
import io
import os
import re
import stat
import tempfile
import time
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from seo_app.ai.base import _check_webp
from seo_app.config import PROJECT_ROOT
from seo_app.images.data_dir import MSG_DATA_DIR_LINK, dir_has_link, is_link
from seo_app.images.naming import image_file_name
from seo_app.images.process import (
    WEB_MAX_EDGE_PX,
    WEB_WEBP_QUALITY,
    ImageProcessError,
    WebImage,
    _cache_dir_is_ignored,
    _open,
    make_web_image,
)
from seo_app.images.tags import ImageTags, TagError

AI_IMAGES_DIR = PROJECT_ROOT / "data" / "ai_images"
GENERATED_FORMATS = ("JPEG", "PNG", "WEBP")
MIN_GENERATED_EDGE = 256
MAX_GENERATED_EDGE = 2048
# Mọi kênh màu chênh nhau không quá chừng này (trên 255): coi là ảnh trống, gần như một màu.
BLANK_SPREAD = 8
MAX_STORED_BYTES = 2 * 1024 * 1024
KEEP_SECONDS = 14 * 24 * 60 * 60
MAX_FILES = 500
MAX_TOTAL_BYTES = 500 * 1024 * 1024
_STORED_NAME = re.compile(r"[0-9a-f]{64}\.webp")
_SHA256 = re.compile(r"[0-9a-f]{64}")

MSG_ANIMATED = "Ảnh Cloudflare trả về là ảnh động nên app không dùng. Tạo lại."
MSG_SIZE = (
    "Ảnh Cloudflare trả về có kích thước lạ ({width}×{height} điểm ảnh) nên app không dùng. "
    "Tạo lại."
)
MSG_BLANK = "Cloudflare trả về ảnh trống (prompt có thể bị chặn). Sửa prompt rồi tạo lại."
MSG_BROKEN = "Ảnh Cloudflare trả về bị hỏng, app không đọc được. Tạo lại."
MSG_NOT_CLEAN = "Ảnh WebP dựng lại vẫn chưa sạch (còn dữ liệu lạ) nên app không dùng. Tạo lại."
MSG_STORE_BAD = "Ảnh AI không đúng dạng để lưu vào máy."
MSG_STORE_NOT_IGNORED = (
    "Thư mục lưu ảnh AI không nằm trong thư mục data (đã chặn đưa lên GitHub) nên app không ghi."
)
MSG_STORE_WRITE = "Không lưu được ảnh AI vào máy ({kind}). Thử lại."
MSG_STORE_READ = "Không đọc được ảnh AI trên máy ({kind}). Bấm Tạo lại."
MSG_STORE_MISSING = "Ảnh AI không còn trên máy này. Bấm Tạo lại."
MSG_STORE_CHANGED = "Ảnh AI trên máy đã bị đổi (không khớp bản đã tạo). Bấm Tạo lại."


class AIImageStoreError(Exception):
    """Lỗi kho ảnh AI: câu tiếng Việt cố định, không đường dẫn."""


@dataclass(frozen=True)
class GeneratedWebImage:
    """Ảnh minh họa AI đã sạch, sẵn sàng lưu kho, hiện, gửi. ``tags``: thẻ ảnh AI do mã đặt."""

    web: WebImage
    sha256: str
    tags: ImageTags

    @property
    def data(self) -> bytes:
        return self.web.data


# ------------------------------------------------------------------ ảnh về → WebP sạch


def make_generated_web_image(
    data: bytes,
    *,
    max_edge_px: int = WEB_MAX_EDGE_PX,
    webp_quality: int = WEB_WEBP_QUALITY,
) -> WebImage:
    """Byte ảnh Cloudflare trả về → WebP sạch (LC-T140-5). Lỗi: ``ImageProcessError`` câu cố định.

    ``max_edge_px``, ``webp_quality``: từ ``load_image_settings()`` (điều kiện 6 của Lá Chắn T-049);
    mặc định như ảnh thật."""
    image = _open(data, formats=GENERATED_FORMATS)
    try:
        if getattr(image, "n_frames", 1) != 1 or getattr(image, "is_animated", False):
            raise ImageProcessError(MSG_ANIMATED)
        width, height = image.size
        if min(width, height) < MIN_GENERATED_EDGE or max(width, height) > MAX_GENERATED_EDGE:
            raise ImageProcessError(MSG_SIZE.format(width=width, height=height))
        try:
            rgb = image.convert("RGB")
        except (OSError, ValueError):
            raise ImageProcessError(MSG_BROKEN) from None
        try:
            if all(high - low <= BLANK_SPREAD for low, high in rgb.getextrema()):
                raise ImageProcessError(MSG_BLANK)
            # Ảnh mới dựng từ điểm ảnh: không mang ``info`` nào của ảnh gốc.
            clean = Image.frombytes("RGB", rgb.size, rgb.tobytes())
        finally:
            rgb.close()
    finally:
        image.close()
    buffer = io.BytesIO()
    try:
        clean.save(buffer, "PNG")
    except (OSError, ValueError):
        raise ImageProcessError(MSG_BROKEN) from None
    finally:
        clean.close()
    web = make_web_image(buffer.getvalue(), max_edge_px=max_edge_px, webp_quality=webp_quality)
    if web.gps is not None or _check_webp(web.data) is not None:
        raise ImageProcessError(MSG_NOT_CLEAN)
    return web


def ai_image_tags(category: str = "") -> ImageTags:
    """Thẻ ảnh AI do mã đặt (LC-T140-13): nguồn AI, chỉ hạng mục khớp danh sách cố định."""
    try:
        return ImageTags.for_ai_image(category)
    except TagError:
        return ImageTags.for_ai_image("")


def wrap_generated(
    data: bytes,
    *,
    category: str = "",
    max_edge_px: int = WEB_MAX_EDGE_PX,
    webp_quality: int = WEB_WEBP_QUALITY,
) -> GeneratedWebImage:
    """Ảnh Cloudflare trả về → ảnh minh họa AI sạch kèm thẻ ảnh AI và băm (ngay lúc bọc)."""
    web = make_generated_web_image(data, max_edge_px=max_edge_px, webp_quality=webp_quality)
    return GeneratedWebImage(
        web=web, sha256=hashlib.sha256(web.data).hexdigest(), tags=ai_image_tags(category)
    )


def generated_file_name(tags: ImageTags, *, alt: str = "", taken: Iterable[str] = ()) -> str:
    """Tên file của ảnh AI khi gửi WordPress: luôn ``minh-hoa-ai-…`` (``ai_generated=True``)."""
    return image_file_name(category=tags.category, alt=alt, ai_generated=True, taken=taken)


# ------------------------------------------------------------------ kho data/ai_images/


def _valid_sha(sha256: object) -> str:
    if not isinstance(sha256, str) or not _SHA256.fullmatch(sha256):
        raise AIImageStoreError(MSG_STORE_BAD)
    return sha256


class AIImageStore:
    """Kho ảnh minh họa AI đã tạo trên máy đang dùng (``data/ai_images/``). Không giữ trạng
    thái ngoài đường dẫn thư mục: tạo mới ở đâu cũng được, kể cả trong luồng nền."""

    def __init__(self, directory: Path | str = AI_IMAGES_DIR) -> None:
        self._dir = Path(directory)

    def __repr__(self) -> str:
        return "AIImageStore()"  # không in đường dẫn

    def _no_link(self) -> None:
        """Từ ngay dưới gốc dự án tới thư mục kho không tầng nào là lối tắt (T-117)."""
        try:
            linked = dir_has_link(self._dir, PROJECT_ROOT)
        except OSError as exc:
            raise AIImageStoreError(MSG_STORE_READ.format(kind=type(exc).__name__)) from None
        if linked:
            raise AIImageStoreError(MSG_DATA_DIR_LINK)

    def save(self, data: bytes) -> str:
        """Lưu byte WebP sạch, trả băm SHA-256 (cũng là tên file). Đã có đúng file thì giữ."""
        if (
            not isinstance(data, bytes)
            or not data
            or len(data) > MAX_STORED_BYTES
            or _check_webp(data) is not None
        ):
            raise AIImageStoreError(MSG_STORE_BAD)
        if not _cache_dir_is_ignored(self._dir):
            raise AIImageStoreError(MSG_STORE_NOT_IGNORED)
        sha256 = hashlib.sha256(data).hexdigest()
        path = self._dir / f"{sha256}.webp"
        self._no_link()
        try:
            self._dir.mkdir(parents=True, exist_ok=True)
            self._no_link()  # kiểm lại sau khi tạo thư mục
            if is_link(path):
                raise AIImageStoreError(MSG_DATA_DIR_LINK)
            if self._read_checked(path, sha256) is not None:
                return sha256
            fd, temp = tempfile.mkstemp(dir=self._dir, suffix=".tmp")
            try:
                with os.fdopen(fd, "wb") as handle:
                    handle.write(data)
                os.replace(temp, path)
            except BaseException:
                Path(temp).unlink(missing_ok=True)
                raise
        except AIImageStoreError:
            raise
        except OSError as exc:
            raise AIImageStoreError(MSG_STORE_WRITE.format(kind=type(exc).__name__)) from None
        return sha256

    def load(self, sha256: str) -> bytes:
        """Byte WebP của ảnh có băm ``sha256``: phải khớp băm và qua ``_check_webp`` (nơi gọi
        truyền đúng băm ghi trong nháp, nên ảnh cũng khớp nháp)."""
        sha256 = _valid_sha(sha256)
        path = self._dir / f"{sha256}.webp"
        self._no_link()
        try:
            if is_link(path):
                raise AIImageStoreError(MSG_DATA_DIR_LINK)
            data = self._read_checked(path, sha256)
        except AIImageStoreError:
            raise
        except OSError as exc:
            raise AIImageStoreError(MSG_STORE_READ.format(kind=type(exc).__name__)) from None
        if data is None:
            raise AIImageStoreError(MSG_STORE_MISSING)
        return data

    @staticmethod
    def _read_checked(path: Path, sha256: str) -> bytes | None:
        """Byte của file nếu có: ``None`` khi chưa có file; sai dạng, sai băm thì báo lỗi."""
        try:
            info = os.lstat(path)
        except FileNotFoundError:
            return None
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_STORED_BYTES:
            raise AIImageStoreError(MSG_STORE_CHANGED)
        with path.open("rb") as handle:
            data = handle.read(MAX_STORED_BYTES + 1)
        if (
            len(data) > MAX_STORED_BYTES
            or hashlib.sha256(data).hexdigest() != sha256
            or _check_webp(data) is not None
        ):
            raise AIImageStoreError(MSG_STORE_CHANGED)
        return data

    def cleanup(self, keep: Iterable[str], *, now: float | None = None) -> int:
        """Xóa ảnh không còn nháp nào nhắc tới: cũ hơn 14 ngày; rồi cả kho quá 500 file hay
        500 MB thì xóa thêm từ ảnh cũ nhất. Chỉ xóa tên đúng mẫu, file thường, trong đúng thư
        mục; ``keep``: băm còn được nháp nhắc tới (kể cả ``history``). Trả số file đã xóa; lỗi
        thì bỏ qua (dọn để sau), không bao giờ làm hỏng việc khác."""
        kept = {sha for sha in keep if isinstance(sha, str) and _SHA256.fullmatch(sha)}
        try:
            self._no_link()
        except AIImageStoreError:
            return 0
        moment = time.time() if now is None else now
        files: list[tuple[float, int, str]] = []
        try:
            with os.scandir(self._dir) as entries:
                for entry in entries:
                    if not _STORED_NAME.fullmatch(entry.name):
                        continue
                    try:
                        info = entry.stat(follow_symlinks=False)
                    except OSError:
                        continue
                    if stat.S_ISREG(info.st_mode) and not is_link(Path(entry.path)):
                        files.append((info.st_mtime, info.st_size, entry.name))
        except OSError:
            return 0
        files.sort()
        total_files = len(files)
        total_bytes = sum(size for _, size, _ in files)
        removed = 0
        left: list[tuple[float, int, str]] = []
        for modified, size, name in files:
            if name[:64] not in kept and moment - modified > KEEP_SECONDS and self._drop(name):
                removed += 1
                total_files -= 1
                total_bytes -= size
            else:
                left.append((modified, size, name))
        for _modified, size, name in left:
            if total_files <= MAX_FILES and total_bytes <= MAX_TOTAL_BYTES:
                break
            if name[:64] not in kept and self._drop(name):
                removed += 1
                total_files -= 1
                total_bytes -= size
        return removed

    def _drop(self, name: str) -> bool:
        try:
            self._no_link()
            path = self._dir / name
            if is_link(path):
                return False
            path.unlink()
        except (AIImageStoreError, OSError):
            return False
        return True
