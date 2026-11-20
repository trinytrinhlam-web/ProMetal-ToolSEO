"""Soi Lỗi T-142: client Cloudflare Workers AI, ảnh AI sạch, kho ``data/ai_images``.

Cloudflare giả (``tests/fake_cloudflare.py``), không gọi mạng thật. Kho ảnh AI chỉ ở thư mục tạm.

- Mã tài khoản, mã truy cập không lọt ra câu lỗi, ``repr``, ``args`` hay dấu vết lỗi (traceback),
  với mọi mã HTTP và mọi kiểu thân trả lời (lỗi JSON, ``messages``, trang HTML); cả lệnh kiểm
  token.
- Mỗi lần lỗi chỉ một lệnh tới Cloudflare (không tự thử lại), cả 429, 3036, 3040, 408, hết giờ.
- Ảnh «bẩn» đi trọn đường client → ``wrap_generated``: JPEG, PNG, WebP có EXIF + GPS, ICC, XMP,
  chú thích, khối riêng, dữ liệu dính sau cuối file: ảnh ra không còn dấu nhận nào, qua
  ``_check_webp``. Lớp kiểm cuối (``web.gps``, ``_check_webp``) tự bắt được WebP bẩn.
- Ảnh AI: alt «Minh họa…», chú thích «Ảnh minh họa (AI)…», tên ``minh-hoa-ai-…``, không thẻ công
  trình, khu vực.
- Kho: tầng ``data/ai_images`` là lối tắt, hay một «file» trong kho là lối tắt: không đọc, không
  ghi, không xóa gì ở ngoài.
- ``cloudflare`` bị từ chối ở mọi việc khác ``image``; không trang nào hiện mã Cloudflare; thử mù
  không có Cloudflare.
- Lỗi chưa sửa (``xfail(strict=True)``): SL-T142-1 (2 ca test ghim cấu hình Claude, hỏng khi gộp
  T-138), SL-T142-2 (ảnh Cloudflare hỏng báo câu của ảnh trong thư mục).
"""

from __future__ import annotations

import base64
import hashlib
import io
import os
import random
import struct
import sys
import traceback
import zlib
from pathlib import Path

import pytest
import requests
import test_app_pages as pages
from PIL import Image, ImageCms, PngImagePlugin
from test_settings_images import page_strings

import seo_app.ai.registry as ai_registry
from seo_app.ai import cloudflare_images as cf
from seo_app.ai.base import AIError, _check_webp
from seo_app.ai.registry import load_ai_config, make_provider
from seo_app.config import Settings
from seo_app.content import blind_test
from seo_app.images import generated as gen
from seo_app.images import process
from seo_app.images.alt import AltSuggestion, clean_suggestion
from seo_app.images.data_dir import MSG_DATA_DIR_LINK
from seo_app.images.process import ImageProcessError
from tests.fake_cloudflare import (
    ACCOUNT,
    MA_GIA,
    RUN_URL,
    VERIFY_URL,
    FakeCloudflare,
    make_session,
    ok_image,
    token_status,
)

env = pages.env  # mật khẩu thử cho trang (fixture tự chạy của test_app_pages)

MARK = b"SOILOIT142DAUNHAN"
KINDS = {"busy", "rate", "quota_day", "network", "timeout", "auth", "bad_request", "shape"}
IMAGE_BLOCK = f'\n[tasks.image]\nprovider = "cloudflare"\nmodel = "{cf.FLUX_SCHNELL}"\nsteps = 4\n'


def _client(fake: FakeCloudflare) -> cf.CloudflareImageClient:
    return cf.CloudflareImageClient(ACCOUNT, MA_GIA, session=make_session(fake))


def _all_text(exc: BaseException) -> str:
    """Mọi chữ một lỗi có thể mang ra ngoài: câu, ``repr``, ``args``, dấu vết lỗi đầy đủ."""
    return "\n".join(
        [str(exc), repr(exc), repr(exc.args), "".join(traceback.format_exception(exc))]
    )


def _no_secret(exc: BaseException) -> None:
    text = _all_text(exc)
    assert ACCOUNT not in text
    assert MA_GIA not in text
    assert "bia.example" not in text


# ====================================================== mã truy cập không lọt ra ngoài


SECRET = f"tai khoan {ACCOUNT} ma {MA_GIA} https://bia.example/{ACCOUNT}"
STATUSES = [200, 400, 401, 403, 404, 408, 429, 500, 503]
SHAPES = {
    "errors": {"success": False, "errors": [{"code": 5004, "message": SECRET}], "result": None},
    "messages": {
        "success": False,
        "errors": [],
        "messages": [{"code": 1, "message": SECRET}],
        "result": {"note": SECRET},
    },
    "html": f"<html><body>{SECRET}</body></html>".encode(),
}


@pytest.mark.parametrize("shape", list(SHAPES), ids=list(SHAPES))
@pytest.mark.parametrize("status", STATUSES, ids=[str(s) for s in STATUSES])
def test_loi_may_chu_co_ma_truy_cap_khong_lot_ra(status, shape):
    headers = {"Content-Type": "text/html"} if shape == "html" else {}
    for method, url, call in (
        ("POST", RUN_URL, lambda client: client.generate("a rusty gate hinge")),
        ("GET", VERIFY_URL, lambda client: client.verify_token()),
    ):
        fake = FakeCloudflare()
        fake.on(method, url, (status, SHAPES[shape], headers))
        with pytest.raises(cf.CloudflareImageError) as info:
            call(_client(fake))
        assert info.value.kind in KINDS
        _no_secret(info.value)
        assert len(fake.calls) == 1


ERRORS = [
    requests.exceptions.ConnectionError,
    requests.exceptions.ReadTimeout,
    requests.exceptions.SSLError,
    requests.exceptions.ChunkedEncodingError,
    requests.exceptions.ContentDecodingError,
    requests.exceptions.InvalidURL,
    requests.exceptions.RequestException,
    OSError,
    ValueError,
]


@pytest.mark.parametrize("error", ERRORS, ids=[e.__name__ for e in ERRORS])
def test_loi_requests_khong_de_url_trong_dau_vet_loi(error):
    fake = FakeCloudflare()
    fake.on("POST", RUN_URL, lambda request: error(f"loi {request.url} {MA_GIA} {SECRET}"))
    with pytest.raises(cf.CloudflareImageError) as info:
        _client(fake).generate("a rusty gate hinge")
    assert info.value.kind in {"network", "timeout"}
    _no_secret(info.value)


def test_loi_dung_client_khong_chep_gia_tri():
    for account, token in ((ACCOUNT.upper(), MA_GIA), (ACCOUNT, f"{MA_GIA} {SECRET}")):
        with pytest.raises(cf.CloudflareImageError) as info:
            cf.CloudflareImageClient(account, token)
        assert info.value.kind == "auth"
        text = _all_text(info.value)
        assert ACCOUNT.upper() not in text and MA_GIA not in text


ONCE = {
    "503": (503, b"", {}),
    "429": (429, {"success": False, "errors": [{"code": 0}]}, {}),
    "3040": (429, {"success": False, "errors": [{"code": 3040}]}, {}),
    "3036": (429, {"success": False, "errors": [{"code": 3036}]}, {}),
    "408": (408, b"", {}),
    "het-gio": requests.exceptions.ReadTimeout("het gio"),
    "mat-mang": requests.exceptions.ConnectionError("mat mang"),
    "anh-sai": (200, {"success": True, "result": {"image": "@@@@"}}, {}),
}


@pytest.mark.parametrize("answer", list(ONCE.values()), ids=list(ONCE))
def test_moi_lan_loi_chi_mot_lenh_toi_cloudflare(answer):
    fake = FakeCloudflare()
    fake.on("POST", RUN_URL, answer)
    with pytest.raises(cf.CloudflareImageError):
        _client(fake).generate("a rusty gate hinge")
    assert len(fake.calls) == 1


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"], ids=["nan", "inf", "-inf"])
def test_bo_doc_json_tu_choi_nan_ca_khi_phan_con_lai_dung_khuon(constant):
    # Ca «nan» của Thợ Máy đặt NaN vào ``success`` nên bị chặn ở bước sau dù bộ đọc nhận NaN
    # (đột biến bỏ ``parse_constant`` sống). Ở đây câu trả lời đúng khuôn, chỉ thêm một trường NaN:
    # bộ đọc chặt phải từ chối cả câu trả lời (LC-T140-4).
    image = base64.b64encode(b"anh gia").decode()
    body = '{"success": true, "result": {"image": "' + image + '", "x": ' + constant + "}}"
    fake = FakeCloudflare()
    fake.on("POST", RUN_URL, (200, body.encode(), {}))
    with pytest.raises(cf.CloudflareImageError) as info:
        _client(fake).generate("a rusty gate hinge")
    assert info.value.kind == "shape"


def test_kiem_token_doc_than_tra_loi_co_gioi_han():
    fake = FakeCloudflare()
    big = token_status("active")
    big["result"]["dem"] = "x" * (cf.MAX_VERIFY_RESPONSE_BYTES + 1)
    fake.on("GET", VERIFY_URL, big)
    with pytest.raises(cf.CloudflareImageError) as info:
        _client(fake).verify_token()
    assert str(info.value) == cf.MSG_TOO_BIG


# ====================================================== ảnh bẩn → WebP sạch, cả đường


def _noise(size=(320, 320)) -> Image.Image:
    rnd = random.Random(142)
    image = Image.new("RGB", size)
    image.putdata([tuple(rnd.randrange(256) for _ in range(3)) for _ in range(size[0] * size[1])])
    return image


def _exif_gps() -> bytes:
    exif = Image.Exif()
    exif[0x010E] = MARK.decode()  # ImageDescription
    exif.get_ifd(0x8825).update({1: "N", 2: (10.0, 45.0, 0.0), 3: "E", 4: (106.0, 40.0, 0.0)})
    return exif.tobytes()


def _icc() -> bytes:
    return ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()


def _chunk(kind: bytes, body: bytes) -> bytes:
    return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))


def _png_dirty() -> bytes:
    info = PngImagePlugin.PngInfo()
    info.add_text("Comment", MARK.decode())
    info.add_text("Note", MARK.decode(), zip=True)
    info.add_itxt("XML:com.adobe.xmp", MARK.decode())
    buffer = io.BytesIO()
    _noise().save(buffer, "PNG", pnginfo=info, exif=_exif_gps(), icc_profile=_icc())
    data = buffer.getvalue()
    end = data.rindex(b"IEND") - 4
    return data[:end] + _chunk(b"prVt", MARK) + data[end:] + MARK  # khối riêng + đuôi dính


def _jpeg_dirty() -> bytes:
    buffer = io.BytesIO()
    _noise().save(buffer, "JPEG", exif=_exif_gps(), icc_profile=_icc(), comment=MARK)
    data = buffer.getvalue()
    xmp = b"http://ns.adobe.com/xap/1.0/\x00" + MARK
    irb = b"Photoshop 3.0\x00" + MARK
    app1 = b"\xff\xe1" + struct.pack(">H", len(xmp) + 2) + xmp
    app13 = b"\xff\xed" + struct.pack(">H", len(irb) + 2) + irb
    return data[:2] + app1 + app13 + data[2:] + MARK


def _webp_dirty() -> bytes:
    buffer = io.BytesIO()
    _noise().save(buffer, "WEBP", exif=_exif_gps(), xmp=MARK, icc_profile=_icc(), quality=90)
    data = bytearray(buffer.getvalue())
    data += b"ZZZZ" + struct.pack("<I", len(MARK)) + MARK + (b"\x00" if len(MARK) % 2 else b"")
    data[4:8] = struct.pack("<I", len(data) - 8)
    return bytes(data) + MARK


DIRTY = {"png": _png_dirty, "jpeg": _jpeg_dirty, "webp": _webp_dirty}


@pytest.mark.parametrize("kind", list(DIRTY), ids=list(DIRTY))
def test_anh_ban_qua_ca_duong_ra_webp_khong_con_dau_nhan(kind):
    source = DIRTY[kind]()
    assert MARK in source
    fake = FakeCloudflare()
    fake.on("POST", RUN_URL, ok_image(source))
    image = _client(fake).generate("a rusty gate hinge")
    assert image.data == source  # client chỉ giải base64; dựng lại ở generated
    wrapped = gen.wrap_generated(image.data, category="cổng inox")
    assert MARK not in wrapped.data
    assert _check_webp(wrapped.data) is None
    assert wrapped.web.gps is None
    with Image.open(io.BytesIO(wrapped.data)) as out:
        assert out.format == "WEBP"
        assert not {"exif", "icc_profile", "xmp", "XML:com.adobe.xmp"} & set(out.info)
    assert wrapped.sha256 == hashlib.sha256(wrapped.data).hexdigest()


def _dirty_web(_data: bytes, **kwargs) -> process.WebImage:
    """``make_web_image`` hỏng giả: trả WebP còn GPS (đi qua đường ảnh thật, giữ GPS)."""
    buffer = io.BytesIO()
    _noise().save(buffer, "JPEG", exif=_exif_gps())
    return process.make_web_image(buffer.getvalue(), **kwargs)


def _dirty_web_no_gps(_data: bytes, **kwargs) -> process.WebImage:
    """``make_web_image`` hỏng giả: WebP có khối EXIF nhưng báo ``gps=None``."""
    buffer = io.BytesIO()
    _noise().save(buffer, "WEBP", exif=b"Exif\x00\x00" + MARK)
    return process.WebImage(data=buffer.getvalue(), width=320, height=320, gps=None)


@pytest.mark.parametrize("fake_web", [_dirty_web, _dirty_web_no_gps], ids=["gps", "exif"])
def test_lop_kiem_cuoi_bat_webp_ban(monkeypatch, fake_web):
    monkeypatch.setattr(gen, "make_web_image", fake_web)
    buffer = io.BytesIO()
    _noise().save(buffer, "PNG")
    with pytest.raises(ImageProcessError) as info:
        gen.make_generated_web_image(buffer.getvalue())
    assert str(info.value) == gen.MSG_NOT_CLEAN


def test_anh_ai_luon_minh_hoa_ten_minh_hoa_ai_khong_the_cong_trinh():
    buffer = io.BytesIO()
    _noise().save(buffer, "PNG")
    wrapped = gen.wrap_generated(buffer.getvalue(), category="CT012 - Cổng inox - Tân Phú")
    assert wrapped.tags.is_ai
    assert not (wrapped.tags.project_code or wrapped.tags.area or wrapped.tags.phase)
    suggestion = clean_suggestion(
        AltSuggestion(alt="Cổng sắt sơn tĩnh điện màu xám", caption="Cổng vừa lắp xong"),
        ai_generated=wrapped.tags.is_ai,
    )
    assert suggestion.alt.startswith("Minh họa")
    assert suggestion.caption.startswith("Ảnh minh họa (AI)")
    name = gen.generated_file_name(wrapped.tags, alt=suggestion.alt)
    assert name.startswith("minh-hoa-ai-") and name.endswith(".webp")


# ====================================================== kho data/ai_images: lối tắt


def _make_link(link: Path, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    if sys.platform == "win32":
        import _winapi

        _winapi.CreateJunction(str(target), str(link))
    else:
        os.symlink(target, link, target_is_directory=True)


@pytest.fixture
def webp() -> bytes:
    buffer = io.BytesIO()
    _noise((300, 300)).save(buffer, "PNG")
    return gen.make_generated_web_image(buffer.getvalue()).data


def test_tang_ai_images_la_loi_tat_khong_doc_ghi_xoa(tmp_path, webp):
    outside = tmp_path / "ngoai"
    (tmp_path / "data").mkdir()
    _make_link(tmp_path / "data" / "ai_images", outside)
    sha = hashlib.sha256(webp).hexdigest()
    (outside / f"{sha}.webp").write_bytes(webp)
    old = os.stat(outside / f"{sha}.webp").st_mtime - 30 * 24 * 60 * 60
    os.utime(outside / f"{sha}.webp", (old, old))
    store = gen.AIImageStore(tmp_path / "data" / "ai_images")
    for action in (lambda: store.save(webp), lambda: store.load(sha)):
        with pytest.raises(gen.AIImageStoreError) as info:
            action()
        assert str(info.value) == MSG_DATA_DIR_LINK
    assert store.cleanup([]) == 0
    assert sorted(p.name for p in outside.iterdir()) == [f"{sha}.webp"]


def test_file_trong_kho_la_loi_tat_khong_bi_theo(tmp_path, webp, monkeypatch):
    folder = tmp_path / "data" / "ai_images"
    folder.mkdir(parents=True)
    outside = tmp_path / "ngoai"
    sha = hashlib.sha256(webp).hexdigest()
    _make_link(folder / f"{sha}.webp", outside)
    (outside / "giu-lai.txt").write_text("khong duoc xoa", encoding="utf-8")
    store = gen.AIImageStore(folder)
    with pytest.raises(gen.AIImageStoreError):
        store.load(sha)
    with pytest.raises(gen.AIImageStoreError):
        store.save(webp)
    monkeypatch.setattr(gen, "MAX_FILES", 0)  # ép dọn mọi thứ
    store.cleanup([])
    assert (outside / "giu-lai.txt").read_text(encoding="utf-8") == "khong duoc xoa"


# ====================================================== registry, trang


TASKS = ["research", "outline", "write", "rewrite", "review", "meta", "links", "plan", "alt", "moi"]


@pytest.mark.parametrize("task", TASKS, ids=TASKS)
@pytest.mark.parametrize("spelling", ["cloudflare", "CloudFlare"], ids=["thuong", "hoa"])
def test_cloudflare_chi_dung_cho_viec_anh(tmp_path, task, spelling):
    path = tmp_path / "ai.toml"
    body = f'[tasks.{task}]\nprovider = "{spelling}"\nmodel = "{cf.FLUX_SCHNELL}"\n'
    path.write_text(body, encoding="utf-8")
    with pytest.raises(AIError, match="chỉ dùng để tạo ảnh"):
        load_ai_config(path)


@pytest.mark.parametrize("provider", ["cloudflare", "anthropic", "openai", "gemini"])
def test_make_provider_khong_bao_gio_keyerror(provider):
    with pytest.raises(AIError):
        make_provider(provider, Settings())  # không khóa nào: luôn AIError, không KeyError


def _cloudflare_toml(tmp_path) -> Path:
    path = tmp_path / "ai.toml"
    path.write_text(ai_registry.AI_CONFIG_FILE.read_text(encoding="utf-8") + IMAGE_BLOCK, "utf-8")
    return path


@pytest.mark.parametrize("view", pages.VIEWS, ids=[v.removesuffix(".py") for v in pages.VIEWS])
def test_khong_trang_nao_hien_ma_cloudflare(project_root, tmp_path, monkeypatch, view):
    monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", ACCOUNT)
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", MA_GIA)
    path = _cloudflare_toml(tmp_path)
    monkeypatch.setattr(ai_registry.load_ai_config, "__defaults__", (path,))
    monkeypatch.setattr(blind_test.task_models, "__defaults__", (path,))
    at = pages.open_page(project_root, view)
    shown = page_strings(at)
    assert ACCOUNT not in shown
    assert MA_GIA not in shown


def test_thu_mu_khong_co_cloudflare(project_root, tmp_path, monkeypatch):
    for name in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"):
        monkeypatch.setenv(name, f"khoa-gia-{name.lower()}")
    monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", ACCOUNT)
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", MA_GIA)
    path = _cloudflare_toml(tmp_path)
    monkeypatch.setattr(ai_registry.load_ai_config, "__defaults__", (path,))
    monkeypatch.setattr(blind_test.task_models, "__defaults__", (path,))
    at = pages.open_page(project_root, "settings.py")
    options = at.selectbox(key="blind-cand-0-provider").options
    assert len(options) == len(ai_registry.PROVIDERS) == 3
    assert not [option for option in options if "cloudflare" in str(option).lower()]
    statuses = blind_test.provider_status(Settings(cloudflare_api_token=MA_GIA))
    assert [status.provider for status in statuses] == list(ai_registry.PROVIDERS)


# ====================================================== lỗi chưa sửa (xfail strict)


def _png_header(width: int, height: int) -> bytes:
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) + _chunk(b"IEND", b"")


def _gif() -> bytes:
    buffer = io.BytesIO()
    _noise((300, 300)).save(buffer, "GIF")
    return buffer.getvalue()


BROKEN = {
    "hong": b"\x89PNG\r\n\x1a\n" + b"rac" * 200,
    "gif": _gif(),
    "heic": b"\x00\x00\x00\x18ftypheic\x00\x00\x00\x00mif1heic" + b"\x00" * 64,
    "81-trieu": _png_header(9000, 9000),
}
PHOTO_HINTS = ("Google Drive", "đổi đuôi", "iPhone", "thu nhỏ ảnh")


@pytest.mark.parametrize("data", list(BROKEN.values()), ids=list(BROKEN))
def test_anh_cloudflare_hong_bao_cau_cua_anh_ai(data):
    with pytest.raises(ImageProcessError) as info:
        gen.make_generated_web_image(data)
    text = str(info.value)
    assert not [hint for hint in PHOTO_HINTS if hint in text], text


def _committed_on_gemini(folder: Path) -> Path:
    """``config/ai.toml`` như sau khi gộp T-138: mọi việc viết dùng Gemini Flash (chỉ đổi hai dòng
    ``provider``, ``model`` đang bật; giữ nguyên phần còn lại)."""
    rows = []
    for row in ai_registry.AI_CONFIG_FILE.read_text(encoding="utf-8").split("\n"):
        if row.startswith("provider = "):
            row = 'provider = "gemini"'
        elif row.startswith("model = "):
            row = 'model = "gemini-3.8-flash"'
        rows.append(row)
    folder.mkdir()
    path = folder / "ai.toml"
    path.write_text("\n".join(rows), encoding="utf-8")
    return path


GOP_T138 = (
    "SL-T142-1: ca test của T-142 chỉ đặt khóa Claude trên cấu hình đã commit; gộp T-138 hỏng"
)


def test_ca_router_t142_van_qua_khi_cau_hinh_la_gemini(tmp_path, monkeypatch):
    import test_t142_config_registry as t142

    monkeypatch.setattr(ai_registry, "AI_CONFIG_FILE", _committed_on_gemini(tmp_path / "goc"))
    t142.test_router_never_asks_for_cloudflare_when_writing(tmp_path)


def test_ca_trang_t142_van_qua_khi_cau_hinh_la_gemini(project_root, tmp_path, monkeypatch):
    import test_t142_config_registry as t142

    monkeypatch.setattr(ai_registry, "AI_CONFIG_FILE", _committed_on_gemini(tmp_path / "goc"))
    t142.test_write_page_does_not_ask_for_cloudflare_key(project_root, tmp_path, monkeypatch)
