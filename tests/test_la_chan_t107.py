"""Lá Chắn T-107: HEIC giải mã một luồng (LC-T093-3) và phép kiểm lưới trước khi giải mã.

Thử thêm các biến thể gần của SL-T107-2 (báo cáo ``docs/team/reports/T-107-la-chan.md``). Lỗi tìm
được đánh dấu ``xfail(strict=True)``: sửa xong thì test tự báo XPASS để gỡ dấu. Ảnh dựng ngay
trong test: ô HEVC lấy từ bộ mã hóa đi kèm pillow-heif, phần khung HEIF (``iinf``, ``iloc``,
``iref``, ``iprp``) tự ghi. Không gọi mạng.

- **LC-T107-1** (Trung bình): giới hạn 80 triệu điểm ảnh và phép kiểm lưới chỉ xét **ảnh chính**.
  Ảnh phụ alpha (``auxC`` alpha, tham chiếu ``auxl``) được libheif giải mã cùng ảnh chính mà không
  qua phép kiểm nào: file 3 kB, ảnh chính 512 × 512, alpha là lưới 31 × 31 ô 512 cùng trỏ một mục
  → giải mã 252 triệu điểm ảnh, thêm khoảng 330 MB, app **nhận** ảnh; ô 1024 thì cam kết tới
  khoảng 1,5 GB. Đúng dạng SL-T107-2, chỉ dời lưới sang ảnh phụ.
- **LC-T107-2** (Trung bình): libheif 1.23.6 còn các lỗi «làm treo CPU» đã công bố, vá ở 1.23.7
  (GHSA-48p4-gj45-w9v6, GHSA-2g6j-vhr6-6wrj, GHSA-7qm8-hj35-269r, GHSA-hhg3-fxg7-3gxw,
  GHSA-74mj-m37q-h3q9). Phép kiểm lưới của T-107 không chặn được các dạng gần: lưới lồng lưới,
  lưới mà mỗi ô là một ảnh chồng (``iovl``) của ảnh lớn. Hết khi app không giải mã HEIC bằng
  libheif < 1.23.7 (nâng pillow-heif, hay tạm tắt HEIF).
"""

from __future__ import annotations

import io
import struct

import pillow_heif
import pytest
import test_images_process as tp
from PIL import Image
from pillow_heif import options as heif_options

from seo_app.images import process

_REGISTRIES = ("OPEN", "MIME", "SAVE", "SAVE_ALL", "EXTENSION")
_OPTIONS = ("DECODE_THREADS", "THUMBNAILS", "DEPTH_IMAGES", "AUX_IMAGES", "DISABLE_SECURITY_LIMITS")
MAKERS = [process.open_image, process.make_preview, process.make_web_image, process.make_ai_image]
MAKER_IDS = ["open_image", "make_preview", "make_web_image", "make_ai_image"]
ALPHA_URN = b"urn:mpeg:hevc:2015:auxid:1\0"


@pytest.fixture(autouse=True)
def _heif_state_restored(monkeypatch):
    Image.init()
    monkeypatch.setattr(Image, "ID", list(Image.ID))
    for name in _REGISTRIES:
        monkeypatch.setattr(Image, name, dict(getattr(Image, name)))
    for name in _OPTIONS:
        monkeypatch.setattr(heif_options, name, getattr(heif_options, name))


# ----- dựng file HEIF tối thiểu ------------------------------------------------------------------


def _box(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I4s", 8 + len(payload), kind) + payload


def _full(kind: bytes, payload: bytes, *, version: int = 0, flags: int = 0) -> bytes:
    return _box(kind, struct.pack(">I", (version << 24) | flags) + payload)


def _children(data: bytes, start: int, end: int) -> dict[bytes, tuple[int, int]]:
    found, i = {}, start
    while i < end:
        size, kind = struct.unpack_from(">I4s", data, i)
        found.setdefault(kind, (i, size))
        i += size
    return found


def _coded_tile(edge: int) -> tuple[bytes, bytes]:
    """Một ô HEVC ``edge`` × ``edge`` của bộ mã hóa: (hộp ``hvcC``, dữ liệu ô trong ``mdat``)."""
    buffer = io.BytesIO()
    pillow_heif.from_pillow(tp._anh_bon_mau((edge, edge))).save(buffer, quality=60)
    g = buffer.getvalue()
    top = _children(g, 0, len(g))
    meta_at, meta_size = top[b"meta"]
    meta = _children(g, meta_at + 12, meta_at + meta_size)
    iinf_at, _ = meta[b"iinf"]
    assert struct.unpack_from(">H", g, iinf_at + 12)[0] == 1  # một mục: mdat chỉ chứa ô này
    iprp_at, iprp_size = meta[b"iprp"]
    ipco_at, ipco_size = _children(g, iprp_at + 8, iprp_at + iprp_size)[b"ipco"]
    hvcc_at, hvcc_size = _children(g, ipco_at + 8, ipco_at + ipco_size)[b"hvcC"]
    mdat_at, mdat_size = top[b"mdat"]
    return g[hvcc_at : hvcc_at + hvcc_size], g[mdat_at + 8 : mdat_at + mdat_size]


def _heif(items: list[tuple], primary: int, refs: list[tuple[bytes, int, list[int]]]) -> bytes:
    """``items``: (mã, loại, dữ liệu, ẩn?, [(hộp thuộc tính, bắt buộc?)]); dữ liệu nằm trong
    ``mdat``. ``refs``: (loại tham chiếu, từ mục, [tới mục])."""
    props: list[bytes] = []
    entries = b""
    for item_id, _kind, _data, _hidden, links in items:
        indexes = []
        for prop, essential in links:
            if prop not in props:
                props.append(prop)
            indexes.append((0x80 if essential else 0) | (props.index(prop) + 1))
        entries += struct.pack(">HB", item_id, len(indexes)) + bytes(indexes)
    ipma = _full(b"ipma", struct.pack(">I", len(items)) + entries)
    iprp = _box(b"iprp", _box(b"ipco", b"".join(props)) + ipma)
    infes = b"".join(
        _full(b"infe", struct.pack(">HH", i, 0) + kind + b"\0", version=2, flags=int(hidden))
        for i, kind, _data, hidden, _links in items
    )
    iinf = _full(b"iinf", struct.pack(">H", len(items)) + infes)
    links = b""
    for kind, src, dst in refs:
        links += _box(kind, struct.pack(">HH", src, len(dst)) + struct.pack(f">{len(dst)}H", *dst))
    iref = _full(b"iref", links)
    hdlr = _full(b"hdlr", b"\0" * 4 + b"pict" + b"\0" * 13)
    head = hdlr + _full(b"pitm", struct.pack(">H", primary))
    chunks = list(dict.fromkeys(data for _i, _k, data, _h, _l in items))

    def iloc(offsets: dict[bytes, int]) -> bytes:
        body = bytes([0x44, 0]) + struct.pack(">H", len(items))
        for item_id, _kind, data, _hidden, _links in items:
            body += struct.pack(">HHHHII", item_id, 0, 0, 1, offsets.get(data, 0), len(data))
        return _full(b"iloc", body, version=1)

    ftyp = _box(b"ftyp", b"heic" + b"\0" * 4 + b"mif1heic")
    start = len(ftyp) + 12 + len(head) + len(iloc({})) + len(iinf) + len(iref) + len(iprp) + 8
    offsets = {}
    for chunk in chunks:
        offsets[chunk] = start
        start += len(chunk)
    meta = _full(b"meta", head + iloc(offsets) + iinf + iref + iprp)
    return ftyp + meta + _box(b"mdat", b"".join(chunks))


def _ispe(width: int, height: int) -> bytes:
    return _full(b"ispe", struct.pack(">II", width, height))


def _grid(columns: int, rows: int, width: int, height: int) -> bytes:
    return bytes([0, 0, rows - 1, columns - 1]) + struct.pack(">HH", width, height)


@pytest.fixture(scope="module")
def tile_512():
    return _coded_tile(512)


@pytest.fixture(scope="module")
def big_alpha_heic(tile_512):
    """Ảnh chính 512 × 512; alpha là lưới 4 × 4 ô 512 cùng trỏ một mục (2048 × 2048, gấp 16 lần
    ảnh chính). Dạng đo trên máy dùng lưới 31 × 31 (252 MP); ở đây nhỏ cho test chạy nhanh."""
    hvcc, data = tile_512
    tile = (hvcc, True), (_ispe(512, 512), False)
    alpha = (_ispe(2048, 2048), False), (_full(b"auxC", ALPHA_URN), False)
    items = [
        (1, b"hvc1", data, False, list(tile)),
        (2, b"grid", _grid(4, 4, 2048, 2048), False, list(alpha)),
        (3, b"hvc1", data, True, list(tile)),
    ]
    return _heif(items, 1, [(b"dimg", 2, [3] * 16), (b"auxl", 2, [1])])


def test_big_alpha_fixture_is_valid_heic(big_alpha_heic):
    """Tiền đề: file dựng là HEIC hợp lệ với libheif (ảnh chính RGBA 512 × 512, giải mã được), để
    ca xfail dưới đây hỏng vì app giải mã ảnh phụ, không phải vì file hỏng."""
    heif = pillow_heif.open_heif(io.BytesIO(big_alpha_heic))
    assert heif.size == (512, 512)
    assert heif.has_alpha
    assert len(heif.data) == 512 * 512 * 4


@pytest.mark.xfail(
    strict=True,
    reason="LC-T107-1: ảnh phụ alpha (lưới) không qua giới hạn điểm ảnh, libheif giải mã hết",
)
@pytest.mark.parametrize("make", MAKERS, ids=MAKER_IDS)
def test_lc_t107_1_big_alpha_rejected_before_decode(big_alpha_heic, make, monkeypatch):
    """Mong đợi: ảnh HEIC có ảnh phụ alpha lớn hơn ảnh chính (lưới ô trỏ lặp) bị từ chối **trước
    khi giải mã** (``load`` không được gọi), câu báo cố định; như lưới ở ảnh chính (SL-T107-2).
    Thực tế: Pillow báo 512 × 512 RGBA lúc mở, mọi phép kiểm qua, libheif giải mã cả lưới alpha
    rồi thu về 512 × 512, app nhận ảnh."""
    loads: list[tuple[int, int]] = []
    real_load = pillow_heif.HeifImageFile.load

    def counting_load(self):
        loads.append(self.size)
        return real_load(self)

    monkeypatch.setattr(pillow_heif.HeifImageFile, "load", counting_load)
    with pytest.raises(process.ImageProcessError):
        make(big_alpha_heic)
    assert loads == []


@pytest.mark.xfail(
    strict=True,
    reason="LC-T107-2: libheif 1.23.6 còn lỗi làm treo CPU đã công bố (GHSA-48p4…), vá ở 1.23.7",
)
def test_lc_t107_2_heic_not_decoded_by_libheif_with_known_cpu_advisories():
    """Mong đợi: đăng ký HEIF như app (``_register_heif``) thì app không nhận HEIF, hoặc libheif
    mang theo từ 1.23.7. Thực tế: HEIF bật, libheif 1.23.6. Giải mã một luồng (LC-T093-3) và phép
    kiểm lưới của T-107 không chặn được lưới lồng lưới hay lưới ô ảnh chồng (đo ở báo cáo)."""
    process._register_heif()
    libheif = tuple(int(part) for part in pillow_heif.libheif_info()["libheif"].split(".")[:3])
    heif_on = "HEIF" in process.ALLOWED_FORMATS and Image.OPEN.get("HEIF") is not None
    assert not heif_on or libheif >= (1, 23, 7)
