r"""Lá Chắn T-097 (đầy đủ): client Google Sheets và file khóa tài khoản dịch vụ.

Lỗi tìm ra (``xfail(strict=True)``; sửa xong thì gỡ dấu):

- **LC-T097-1** (Thấp): câu trả lời chuyển hướng (3xx **có** ``Location``) của
  ``sheets.googleapis.com`` hay máy chủ mã bị ``requests`` đọc **hết** thân (kể cả giải nén gzip)
  trước khi client kịp kiểm cỡ, nên giới hạn 2 MB (Sheets) và 64 KB (xin mã) không áp dụng.
  ``Session.send`` gọi ``resolve_redirects`` (đọc ``resp.content``) cả khi
  ``allow_redirects=False``; phiên ``max_redirects = 0`` chỉ làm nó ném ``TooManyRedirects`` sau
  khi đã đọc. Đo bằng script: thân gzip 100 KB thành 100 MB, bộ nhớ đỉnh khoảng 200 MB.
  Không lệnh nào đi tới địa chỉ chuyển hướng (đã đúng).
- **SL-T097-3, dạng Lá Chắn thêm** (Thấp, Windows): ngoài ``\\?\<ổ>:\…`` Soi Lỗi đã nêu, đường
  dẫn ``\\?\Volume{…}\…`` và ``\\?\GLOBALROOT\??\<ổ>:\…`` trỏ vào thư mục dự án hay thư mục ảnh
  cũng được nhận. Cách sửa phải so **danh tính thư mục** (``(st_dev, st_ino)``,
  ``os.path.samefile``); chỉ bỏ tiền tố ``\\?\`` thì hai dạng này vẫn lọt.

Không gọi Google thật: Google giả gắn vào ``requests.Session`` (bộ chặn mạng của
``tests/conftest.py`` vẫn bật); khóa RSA sinh lúc chạy (LC-T094-17).
"""

from __future__ import annotations

import ctypes
import io
import json
import os
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import quote, urlsplit

import pytest
import requests
from fake_google import (
    SHEET_ID,
    SHEETS,
    TOKEN_URL,
    FakeGoogle,
    key_info,
    make_session,
    new_private_key,
)
from requests.structures import CaseInsensitiveDict

from seo_app.google import sheets
from seo_app.google.service_account import ServiceAccountError, load_service_account
from seo_app.google.sheets import SheetsClient, SheetsError

BIG = 8 * 1024 * 1024
LOCATION = {"Location": "https://evil.example/noi-khac"}
INFO_URL = SHEETS + SHEET_ID
APPEND_URL = SHEETS + SHEET_ID + "/values/" + quote(sheets.APPEND_RANGE, safe="") + ":append"


@pytest.fixture(scope="module")
def key_text() -> str:
    return json.dumps(key_info(new_private_key()))


@pytest.fixture
def dirs(tmp_path):
    folders = SimpleNamespace(
        project=tmp_path / "du-an", images=tmp_path / "anh", outside=tmp_path / "bi-mat"
    )
    for folder in vars(folders).values():
        folder.mkdir()
    return folders


def _load(path, dirs):
    return load_service_account(path, project_root=dirs.project, image_folders=[dirs.images])


@pytest.fixture
def account(dirs, key_text):
    path = dirs.outside / "khoa.json"
    path.write_text(key_text, encoding="utf-8")
    return _load(path, dirs)


# ================================================================ LC-T097-1


class _CountingBody(io.BytesIO):
    """Thân câu trả lời đếm số byte đã bị đọc."""

    def __init__(self, data: bytes) -> None:
        super().__init__(data)
        self.read_bytes = 0

    def read(self, size: int | None = -1) -> bytes:
        chunk = super().read(size)
        self.read_bytes += len(chunk)
        return chunk


class _Google(FakeGoogle):
    """Google giả: địa chỉ đăng ký bằng ``big`` trả thân lớn có đếm byte đã đọc."""

    def __init__(self) -> None:
        super().__init__()
        self.big: dict[tuple[str, str], tuple[int, dict[str, str]]] = {}
        self.bodies: list[_CountingBody] = []

    def send(self, request: requests.PreparedRequest, **kwargs) -> requests.Response:
        parts = urlsplit(request.url)
        key = (request.method, f"{parts.scheme}://{parts.netloc}{parts.path}")
        if key not in self.big:
            return super().send(request, **kwargs)
        self.calls.append((request, kwargs))
        status, headers = self.big[key]
        body = _CountingBody(b"x" * BIG)
        self.bodies.append(body)
        response = requests.Response()
        response.status_code = status
        response.raw = body
        response.headers = CaseInsensitiveDict({"Content-Type": "application/json", **headers})
        response.url = request.url
        response.request = request
        return response


def _client(fake: FakeGoogle, account) -> SheetsClient:
    return SheetsClient(SHEET_ID, account, session=make_session(fake), sleep=lambda _s: None)


def _went_elsewhere(fake: FakeGoogle) -> list[str]:
    return [r.url for r in fake.requests if "evil.example" in r.url]


_LC1 = pytest.mark.xfail(
    strict=True,
    reason="LC-T097-1: requests đọc hết thân câu trả lời 3xx có Location (resolve_redirects đọc "
    "resp.content cả khi allow_redirects=False) trước khi client kiểm cỡ; giới hạn 2 MB / 64 KB "
    "không áp dụng",
)


@_LC1
@pytest.mark.parametrize("status", [301, 302, 303, 307, 308])
def test_lc_t097_1_chuyen_huong_sheets_khong_doc_qua_gioi_han(account, status):
    fake = _Google()
    fake.big[("GET", INFO_URL)] = (status, LOCATION)
    with pytest.raises(SheetsError, match="chuyển hướng"):
        _client(fake, account).get_info()
    assert not _went_elsewhere(fake)
    assert fake.bodies[0].read_bytes <= sheets.MAX_RESPONSE_BYTES


@_LC1
def test_lc_t097_1_lenh_ghi_chuyen_huong_khong_doc_qua_gioi_han_va_la_khong_chac(account):
    fake = _Google()
    fake.big[("POST", APPEND_URL)] = (307, LOCATION)
    with pytest.raises(SheetsError, match="chuyển hướng") as error:
        _client(fake, account).append_row(["B-001", "=IMPORTXML(1)"])
    assert error.value.unsure is True
    assert not _went_elsewhere(fake)
    assert fake.bodies[0].read_bytes <= sheets.MAX_RESPONSE_BYTES


@_LC1
def test_lc_t097_1_lenh_xin_ma_chuyen_huong_khong_doc_qua_64_kb(account):
    fake = _Google()
    fake.big[("POST", TOKEN_URL)] = (302, LOCATION)
    with pytest.raises(SheetsError):
        _client(fake, account).get_info()
    assert not _went_elsewhere(fake)
    assert not fake.sheets_requests()
    assert fake.bodies[0].read_bytes <= sheets.MAX_TOKEN_RESPONSE_BYTES


def test_lc_t097_1_doi_chung_tra_loi_200_lon_chi_doc_toi_gioi_han(account):
    fake = _Google()
    fake.big[("GET", INFO_URL)] = (200, {})
    with pytest.raises(SheetsError, match="lớn bất thường"):
        _client(fake, account).get_info()
    assert fake.bodies[0].read_bytes <= sheets.MAX_RESPONSE_BYTES + 64 * 1024


def test_lc_t097_1_doi_chung_xin_ma_200_lon_chi_doc_toi_64_kb(account):
    fake = _Google()
    fake.big[("POST", TOKEN_URL)] = (200, {})
    with pytest.raises(SheetsError):
        _client(fake, account).get_info()
    assert not fake.sheets_requests()
    assert fake.bodies[0].read_bytes <= sheets.MAX_TOKEN_RESPONSE_BYTES + 64 * 1024


@pytest.mark.parametrize("status", [302, 307])
def test_lc_t097_1_doi_chung_3xx_khong_location_khong_doc_than(account, status):
    fake = _Google()
    fake.big[("GET", INFO_URL)] = (status, {})
    with pytest.raises(SheetsError, match="chuyển hướng"):
        _client(fake, account).get_info()
    assert fake.bodies[0].read_bytes == 0


# ================================================================ SL-T097-3, dạng Lá Chắn thêm

_WINDOWS_ONLY = pytest.mark.skipif(os.name != "nt", reason="dạng đường dẫn chỉ có trên Windows")
_SL3_MORE = pytest.mark.xfail(
    strict=True,
    reason="SL-T097-3 (Lá Chắn thêm dạng): _is_within so chuỗi; \\\\?\\Volume{…}\\ và "
    "\\\\?\\GLOBALROOT\\??\\ trỏ vào dự án/thư mục ảnh vẫn được nhận; phải so danh tính thư mục, "
    "không chỉ bỏ tiền tố",
)


def _volume_form(path: Path) -> str | None:
    r"""``\\?\Volume{…}\<phần sau gốc ổ>`` của ``path`` (None nếu Windows không trả được)."""
    kernel32 = ctypes.windll.kernel32
    mount = ctypes.create_unicode_buffer(1024)
    if not kernel32.GetVolumePathNameW(str(path), mount, 1024):
        return None
    guid = ctypes.create_unicode_buffer(1024)
    if not kernel32.GetVolumeNameForVolumeMountPointW(mount.value, guid, 1024):
        return None
    return guid.value + str(path)[len(mount.value) :]


def _typed(form: str, path: Path) -> str:
    if form == "volume":
        typed = _volume_form(path)
        if typed is None:
            pytest.skip("Windows không trả mã ổ (Volume GUID) cho thư mục tạm")
        return typed
    return "\\\\?\\GLOBALROOT\\??\\" + str(path)


@_WINDOWS_ONLY
@_SL3_MORE
@pytest.mark.parametrize("form", ["volume", "globalroot"])
@pytest.mark.parametrize("where", ["dự án", "thư mục ảnh"])
def test_sl_t097_3_dang_volume_va_globalroot_vao_du_an_hay_thu_muc_anh_bi_tu_choi(
    dirs, key_text, form, where
):
    inside = (dirs.project if where == "dự án" else dirs.images) / "khoa.json"
    inside.write_text(key_text, encoding="utf-8")
    with pytest.raises(ServiceAccountError, match="thư mục phần mềm|thư mục ảnh"):
        _load(_typed(form, inside), dirs)


@_WINDOWS_ONLY
@pytest.mark.parametrize("form", ["volume", "globalroot"])
def test_sl_t097_3_doi_chung_file_ngoai_hai_thu_muc_van_nhan_o_moi_dang(dirs, key_text, form):
    """Không chặn oan: file khóa thật sự nằm ngoài dự án và thư mục ảnh, gõ dạng nào cũng nhận."""
    outside = dirs.outside / "khoa.json"
    outside.write_text(key_text, encoding="utf-8")
    assert _load(_typed(form, outside), dirs).file_name == "khoa.json"


@_WINDOWS_ONLY
@pytest.mark.parametrize("where", ["dự án", "thư mục ảnh"])
def test_sl_t097_3_doi_chung_dang_cham_va_ten_ngan_bi_tu_choi(dirs, key_text, where):
    inside = (dirs.project if where == "dự án" else dirs.images) / "khoa.json"
    inside.write_text(key_text, encoding="utf-8")
    variants = [str(inside), "\\\\.\\" + str(inside)]
    volume = _volume_form(inside)
    if volume is not None:
        variants.append("\\\\.\\" + volume[4:])
    short = ctypes.create_unicode_buffer(1024)
    if ctypes.windll.kernel32.GetShortPathNameW(str(inside), short, 1024) and (
        short.value.lower() != str(inside).lower()
    ):
        variants.append(short.value)
    for variant in variants:
        with pytest.raises(ServiceAccountError, match="thư mục phần mềm|thư mục ảnh"):
            _load(variant, dirs)
