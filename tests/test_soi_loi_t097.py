r"""Soi Lỗi T-097 (rút gọn): client Google Sheets và kiểm file khóa tài khoản dịch vụ.

Google giả **riêng** của Soi Lỗi (adapter ``_Google`` dưới đây, không dùng
``tests/fake_google.py``), thân trả lời là ``urllib3.HTTPResponse`` thật (đọc theo luồng, lỗi
giữa thân đi đúng đường của ``requests``). Khóa RSA sinh lúc chạy (LC-T094-17); file khóa, thư
mục dự án, thư mục ảnh và
``.env`` đều nằm trong thư mục tạm. Không gọi Google thật; bộ chặn mạng của ``tests/conftest.py``
vẫn bật (có test riêng: chặn được cả lớp chuyển của ``google-auth``).

Lỗi tìm ra (``xfail(strict=True)``; sửa xong thì gỡ dấu). Lượt 1: SL-T097-1 → -4, đã sửa ở lượt 2
(Thợ Máy gỡ dấu); lượt 2: SL-T097-5 (cuối file).

- **SL-T097-1** (Thấp): lệnh xin mã trả lời lạ (``expires_in`` quá lớn, JSON lồng sâu) làm
  ``OverflowError``/``RecursionError`` lọt khỏi ``SheetsClient``, không thành ``SheetsError`` câu
  cố định (LC-T094-2).
- **SL-T097-2** (Thấp): lệnh ghi gặp mã 3xx **không** có ``Location`` báo ``unsure=False``; cùng
  mã có ``Location`` thì ``unsure=True``. Nơi gọi (T-100) dựa vào ``unsure`` để biết có phải đọc
  lại trước khi làm lại (thêm dòng làm lại là thêm trùng).
- **SL-T097-3** (Thấp, Windows): phép so «trong thư mục dự án / thư mục ảnh» so chuỗi đường dẫn:
  dạng ``\\?\<ổ>:\…`` và ``\\localhost\<ổ>$\…`` trỏ vào đúng các thư mục đó vẫn được nhận
  (LC-T094-11: so đường dẫn thật).
- **SL-T097-4** (Thấp): Cảnh báo «thư mục đồng bộ» thiếu hai thư mục của Google Drive for Desktop
  nằm cạnh «My Drive» trên cùng ổ ảo: ``Shared drives``, ``Other computers``.
- **SL-T097-5** (Thấp, lượt 2): phép so danh tính thư mục (``_inside_by_identity``) đi ngược các
  thư mục cha **theo chữ** của đường gõ: đường có ``..`` đi ngang thư mục dự án / thư mục ảnh rồi
  ra ngoài bị từ chối oan («đang nằm trong thư mục phần mềm»).
"""

from __future__ import annotations

import base64
import io
import json
import logging
import os
import threading
import time
import unicodedata
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import parse_qs, quote, urlsplit

import google.auth.transport.requests
import google.auth.transport.urllib3
import pytest
import requests
import urllib3
from conftest import RealNetworkBlocked
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, padding, rsa
from requests.adapters import BaseAdapter
from requests.structures import CaseInsensitiveDict

from seo_app import config, env_file
from seo_app.google import service_account as sa
from seo_app.google import sheets
from seo_app.google.service_account import ServiceAccountError, load_service_account
from seo_app.google.sheets import CellUpdate, SheetsClient, SheetsError

# ---------------------------------------------------------------- hằng giả (không có thật)
SHEET = "1Sl097" + "x" * 30 + "_-Q9"  # 40 ký tự, đúng dạng mã Sheet
EMAIL = "soi-loi-t097@du-an-gia-097.iam.gserviceaccount.com"
OTHER_EMAIL = "tai-khoan-khac@du-an-khac.iam.gserviceaccount.com"
ACCESS = "ya29.ma-gia-sl097"
BAIT = "MOI-SL097-ZQX"
BAIT_BODY = json.dumps({"error": {"code": 0, "message": BAIT, "status": BAIT}}).encode()
TOKEN_URL = "https://oauth2.googleapis.com/token"
BASE = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET}"
INFO_URL = BASE
READ_URL = f"{BASE}/values/{quote(chr(39) + 'KeHoach' + chr(39) + '!A1:Z1001', safe='')}"
UPDATE_URL = f"{BASE}/values:batchUpdate"
APPEND_URL = f"{BASE}/values/{quote(chr(39) + 'KeHoach' + chr(39) + '!A1:Z1', safe='')}:append"
STRUCT_URL = f"{BASE}:batchUpdate"
PLAN_ID = 7
COMMAND_URL = {
    "info": ("GET", INFO_URL),
    "read": ("GET", READ_URL),
    "update": ("POST", UPDATE_URL),
    "append": ("POST", APPEND_URL),
    "structure": ("POST", STRUCT_URL),
}
COMMANDS = tuple(COMMAND_URL)
WRITES = ("update", "append", "structure")
FREEZE = {
    "updateSheetProperties": {
        "properties": {"sheetId": PLAN_ID, "gridProperties": {"frozenRowCount": 1}},
        "fields": "gridProperties.frozenRowCount",
    }
}
_PEM_HEAD = "-----BEGIN " + "PRIVATE KEY-----"  # ghép hai nửa: bộ quét bí mật không nhận nhầm
_PEM_TAIL = "-----END " + "PRIVATE KEY-----"
_DROP = object()


def info_answer(plan_id: int | None = PLAN_ID, title: str = "Kế hoạch SEO") -> dict:
    tabs = [{"properties": {"sheetId": 0, "title": "Trang tính1"}}]
    if plan_id is not None:
        tabs.append({"properties": {"sheetId": plan_id, "title": "KeHoach"}})
    return {
        "properties": {"title": title, "locale": "vi_VN", "timeZone": "Asia/Ho_Chi_Minh"},
        "sheets": tabs,
    }


class _Broken(io.RawIOBase):
    """Thân trả lời đứt giữa chừng: trả ``first`` rồi ném ``exc`` (urllib3 đổi thành lỗi của nó,
    ``requests`` đổi tiếp thành ``RequestException`` như khi chạy thật)."""

    def __init__(self, first: bytes, exc: BaseException) -> None:
        self._first, self._exc, self._sent = first, exc, False

    def readable(self) -> bool:
        return True

    def readinto(self, buffer) -> int:
        if not self._sent:
            self._sent = True
            buffer[: len(self._first)] = self._first
            return len(self._first)
        raise self._exc


class _Google(BaseAdapter):
    """Google giả của Soi Lỗi: tra theo (phương thức, địa chỉ không có ``?…``). Mỗi đường giữ một
    hàng câu trả lời: mỗi lần gọi lấy câu kế tiếp, còn một câu thì lặp mãi câu đó."""

    def __init__(self) -> None:
        super().__init__()
        self.routes: dict[tuple[str, str], list] = {}
        self.calls: list[tuple[requests.PreparedRequest, dict]] = []
        self.on("POST", TOKEN_URL, (200, {"access_token": ACCESS, "expires_in": 3599}))
        self.on("GET", INFO_URL, (200, info_answer()))

    def on(self, method: str, url: str, *answers) -> None:
        self.routes[(method, url)] = list(answers)

    def urls(self, url: str) -> list[requests.PreparedRequest]:
        return [r for r, _ in self.calls if urlsplit(r.url)._replace(query="").geturl() == url]

    def hosts(self) -> set[str]:
        return {urlsplit(r.url).netloc for r, _ in self.calls}

    def send(self, request: requests.PreparedRequest, **kwargs) -> requests.Response:
        self.calls.append((request, kwargs))
        parts = urlsplit(request.url)
        queue = self.routes.get((request.method, f"{parts.scheme}://{parts.netloc}{parts.path}"))
        answer = (404, {"error": {"code": 404}}) if not queue else queue[0]
        if queue and len(queue) > 1:
            queue.pop(0)
        if callable(answer):
            answer = answer()
        if isinstance(answer, BaseException):
            raise answer
        status, body, *rest = answer
        headers = dict(rest[0]) if rest else {}
        if not isinstance(body, io.RawIOBase):
            body = io.BytesIO(body if isinstance(body, bytes) else json.dumps(body).encode())
        raw = urllib3.HTTPResponse(
            body=body, status=status, headers=headers, preload_content=False,
            enforce_content_length=False,
        )
        response = requests.Response()
        response.status_code = status
        response.raw = raw
        response.headers = CaseInsensitiveDict(headers)
        response.url = request.url
        response.request = request
        return response

    def close(self) -> None:
        pass


# ---------------------------------------------------------------- dựng file khóa, client
@pytest.fixture(scope="module")
def rsa_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def _pem(key) -> str:
    return key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    ).decode("ascii")


@pytest.fixture(scope="module")
def rsa_pem(rsa_key) -> str:
    return _pem(rsa_key)


@pytest.fixture
def dirs(tmp_path):
    folders = SimpleNamespace(
        outside=tmp_path / "ngoai" / "bi-mat",
        project=tmp_path / "du-an",
        images=tmp_path / "anh-dong-bo",
    )
    for folder in vars(folders).values():
        folder.mkdir(parents=True)
    return folders


def key_dict(pem: str, **changes) -> dict:
    info = {
        "type": "service_account",
        "project_id": "du-an-gia-097",
        "private_key_id": "ab" * 20,
        "private_key": pem,
        "client_email": EMAIL,
        "client_id": "1" * 21,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": TOKEN_URL,
        "universe_domain": "googleapis.com",
    }
    info.update(changes)
    return {key: value for key, value in info.items() if value is not _DROP}


def write_key(folder: Path, pem: str, name: str = "du-an-gia-097-0a1b2c3d.json", **changes) -> Path:
    path = folder / name
    path.write_text(json.dumps(key_dict(pem, **changes)), encoding="utf-8")
    return path


def load(path, dirs, **kwargs):
    kwargs.setdefault("image_folders", (dirs.images,))
    return load_service_account(path, project_root=dirs.project, **kwargs)


class _Session(requests.Session):
    """Phiên ghi lại tùy chọn của từng lệnh (``allow_redirects`` không tới được adapter)."""

    def __init__(self) -> None:
        super().__init__()
        self.sent: list[dict] = []

    def request(self, method, url, *args, **kwargs):
        self.sent.append({"method": method, "url": url, **kwargs})
        return super().request(method, url, *args, **kwargs)


def make_client(fake: _Google, account, sleeps: list | None = None) -> SheetsClient:
    session = _Session()
    session.mount("https://", fake)
    session.mount("http://", fake)
    sleep = sleeps.append if sleeps is not None else (lambda _seconds: None)
    return SheetsClient(SHEET, account, session=session, sleep=sleep)


@pytest.fixture
def fake() -> _Google:
    return _Google()


@pytest.fixture
def account(dirs, rsa_pem):
    return load(write_key(dirs.outside, rsa_pem), dirs)


@pytest.fixture
def client(fake, account) -> SheetsClient:
    return make_client(fake, account)


def run(client: SheetsClient, command: str):
    if command == "info":
        return client.get_info()
    if command == "read":
        return client.read_plan_values()
    if command == "update":
        return client.update_cells([CellUpdate(2, 1, "=IMPORTXML(A1)")])
    if command == "append":
        return client.append_row(["SL-1", "=HYPERLINK(A1)"])
    client.get_info()
    return client.batch_update([FREEZE])


def assert_fixed(error: BaseException, *forbidden: str) -> None:
    """Câu báo cố định: không chép mồi, mã Sheet, mã truy cập, email; không nối lỗi gốc."""
    text = f"{error} {error!r}"
    for item in (BAIT, SHEET, ACCESS, EMAIL, _PEM_HEAD, *forbidden):
        assert item not in text
    assert error.__cause__ is None


# ================================================================ SL-T097-1 (xfail)
TOKEN_ODD_LEAKS = {
    "expires_in vô cực (1e400)": (200, b'{"access_token":"ya29.x","expires_in":1e400}'),
    "expires_in 300 tỷ giây": (200, b'{"access_token":"ya29.x","expires_in":300000000000}'),
    "expires_in dạng chữ 300 tỷ": (200, b'{"access_token":"ya29.x","expires_in":"300000000000"}'),
    "expires_in 1e20": (200, b'{"access_token":"ya29.x","expires_in":100000000000000000000}'),
    "200 JSON lồng sâu": (200, b"[" * 60_000),
    "400 JSON lồng sâu": (400, b"[" * 60_000),
}


@pytest.mark.parametrize("answer", TOKEN_ODD_LEAKS.values(), ids=TOKEN_ODD_LEAKS)
def test_sl_t097_1_lenh_xin_ma_tra_loi_la_thanh_cau_co_dinh(fake, client, answer):
    fake.on("POST", TOKEN_URL, answer)
    with pytest.raises(SheetsError) as error:
        client.get_info()
    assert_fixed(error.value)
    assert not fake.urls(INFO_URL)  # chưa có mã thì không gọi Sheets


TOKEN_ODD_OK = {
    "expires_in NaN": (200, b'{"access_token":"ya29.x","expires_in":NaN}'),
    "expires_in lồng": (200, b'{"access_token":"ya29.x","expires_in":[[1]]}'),
    "không phải UTF-8": (200, b"\xff\xfe{"),
    "JSON là mảng": (200, b"[1, 2]"),
    "JSON là chữ": (200, b'"ya29.x"'),
    "mã rỗng": (200, b'{"access_token":""}'),
    "mã có xuống dòng": (200, b'{"access_token":"ya29.x\\nX-Chen: 1"}'),
    "mã là số": (200, b'{"access_token":12345}'),
    "thiếu access_token": (200, b'{"expires_in":3599}'),
    "invalid_grant có mồi": (400, json.dumps({"error": "invalid_grant",
                                             "error_description": BAIT}).encode()),
    "lỗi khác có mồi": (400, json.dumps({"error": BAIT, "error_description": BAIT}).encode()),
    "302 có Location": (302, b"", {"Location": "https://evil.example/token"}),
    "quá 64 KB": (200, b" " * (64 * 1024 + 1)),
    "đứt giữa thân": lambda: (200, _Broken(b'{"acc', ConnectionResetError(BAIT))),
}


@pytest.mark.parametrize("answer", TOKEN_ODD_OK.values(), ids=TOKEN_ODD_OK)
def test_lenh_xin_ma_tra_loi_la_da_thanh_cau_co_dinh(fake, client, answer):
    fake.on("POST", TOKEN_URL, answer)
    with pytest.raises(SheetsError) as error:
        client.get_info()
    assert_fixed(error.value)
    assert fake.hosts() == {"oauth2.googleapis.com"}  # không gọi Sheets, không theo Location


def test_lenh_xin_ma_5xx_thu_lai_cua_thu_vien_roi_cau_co_dinh(fake, client, monkeypatch):
    """google-auth tự thử lại lệnh xin mã khi máy chủ mã báo 5xx/429 (3 lần): vẫn chỉ tới
    máy chủ mã, rồi câu cố định; không lệnh Sheets nào."""
    monkeypatch.setattr(time, "sleep", lambda _seconds: None)
    fake.on("POST", TOKEN_URL, (503, BAIT_BODY))
    with pytest.raises(SheetsError) as error:
        client.get_info()
    assert_fixed(error.value)
    assert len(fake.urls(TOKEN_URL)) == 3
    assert fake.hosts() == {"oauth2.googleapis.com"}


# ================================================================ SL-T097-2 (xfail)
@pytest.mark.parametrize(
    "command, status",
    [("update", 302), ("append", 302), ("append", 307), ("structure", 302)],
)
def test_sl_t097_2_ghi_gap_3xx_khong_location_van_la_khong_chac(fake, client, command, status):
    fake.on(*COMMAND_URL[command], (status, BAIT_BODY))
    with pytest.raises(SheetsError) as error:
        run(client, command)
    assert error.value.unsure is True


@pytest.mark.parametrize("command", COMMANDS)
def test_3xx_co_location_khong_di_theo_unsure_theo_loai_lenh(fake, client, command):
    fake.on(*COMMAND_URL[command], (308, BAIT_BODY, {"Location": "https://evil.example/x"}))
    with pytest.raises(SheetsError) as error:
        run(client, command)
    assert_fixed(error.value, "evil.example")
    assert error.value.unsure is (command in WRITES)
    assert "evil.example" not in fake.hosts()


@pytest.mark.parametrize("command", ["info", "read"])
def test_3xx_khong_location_o_lenh_doc_khong_bao_gio_unsure(fake, client, command):
    fake.on(*COMMAND_URL[command], (302, BAIT_BODY))
    with pytest.raises(SheetsError) as error:
        run(client, command)
    assert_fixed(error.value)
    assert error.value.unsure is False


# ================================================================ câu trả lời Sheets lạ
SHEETS_ODD = {
    # tên: (câu trả lời, lệnh ghi có thể đã chạy)
    "JSON mảng lồng sâu 2 MB": (lambda: (200, b"[" * (2 * 1024 * 1024 - 64)), True),
    "JSON object lồng sâu": (lambda: (200, b'{"a":' * 200_000 + b"1" + b"}" * 200_000), True),
    "số 5000 chữ số": (lambda: (200, b'{"values":[[' + b"9" * 5000 + b"]]}"), True),
    "thân rỗng": (lambda: (200, b""), True),
    "không phải JSON (có mồi)": (lambda: (200, f"<b>{BAIT}</b>".encode()), True),
    "JSON là mảng": (lambda: (200, b"[]"), True),
    "mã 201": (lambda: (201, {}), True),
    "mã 204": (lambda: (204, b""), True),
    "mã 500 có mồi": (lambda: (500, BAIT_BODY), True),
    "mã 503": (lambda: (503, b""), True),
    "mã 400 có mồi": (lambda: (400, BAIT_BODY), False),
    "mã 401 có mồi": (lambda: (401, BAIT_BODY), False),
    "mã 403 có mồi": (lambda: (403, BAIT_BODY), False),
    "mã 404 có mồi": (lambda: (404, BAIT_BODY), False),
    "3 MB không khai Content-Length": (lambda: (200, b" " * (3 * 1024 * 1024)), True),
    "khai Content-Length 3 MB": (
        lambda: (200, b"{}", {"Content-Length": str(3 * 1024 * 1024)}), True),
    "hết giờ đọc": (lambda: requests.exceptions.ReadTimeout(BAIT), True),
    "hết giờ nối": (lambda: requests.exceptions.ConnectTimeout(BAIT), True),
    "mất kết nối": (lambda: requests.exceptions.ConnectionError(BAIT), True),
    "lỗi SSL": (lambda: requests.exceptions.SSLError(BAIT), True),
    "đứt giữa thân": (lambda: (200, _Broken(b'{"val', ConnectionResetError(BAIT))), True),
    "hết giờ giữa thân": (lambda: (200, _Broken(b'{"val', TimeoutError(BAIT))), True),
}


@pytest.mark.parametrize("command", COMMANDS)
@pytest.mark.parametrize("answer, maybe_ran", SHEETS_ODD.values(), ids=SHEETS_ODD)
def test_cau_tra_loi_sheets_la_thanh_cau_co_dinh(fake, client, command, answer, maybe_ran):
    fake.on(*COMMAND_URL[command], answer)
    with pytest.raises(SheetsError) as error:
        run(client, command)
    assert_fixed(error.value)
    assert error.value.unsure is (maybe_ran and command in WRITES)
    assert len(fake.urls(COMMAND_URL[command][1])) == 1  # không tự thử lại


WRONG_SHAPES = {
    "info": [
        {"properties": [], "sheets": []},
        {"properties": {}, "sheets": {}},
        {"properties": {}, "sheets": [1]},
        {"properties": {}, "sheets": [{"properties": {"sheetId": "7", "title": "KeHoach"}}]},
        {"properties": {}, "sheets": [{"properties": {"sheetId": True, "title": "KeHoach"}}]},
        {"properties": {}, "sheets": [{"properties": {"sheetId": -1, "title": "KeHoach"}}]},
        {"properties": {}, "sheets": [{"properties": {"sheetId": 1, "title": ["KeHoach"]}}]},
        {"properties": {}, "sheets": [{"properties": {"sheetId": 1, "title": "KeHoach"}},
                                      {"properties": {"sheetId": 2, "title": "KeHoach"}}]},
        {"properties": {}, "sheets": [{"properties": {"sheetId": i, "title": str(i)}}
                                      for i in range(201)]},
    ],
    "read": [
        {"values": {"A1": "x"}},
        {"values": ["dòng"]},
        {"values": [[{"formulaValue": "=1"}]]},
        {"values": [["x"] * 27]},
        {"values": [["x"]] * 1002},
        {"values": [[2**60]]},
        {"values": [[None]]},
        {"majorDimension": "COLUMNS", "values": [["x"]]},
    ],
    "structure": [{"replies": {}}, {"replies": [1]}, {"replies": "x"}],
}


@pytest.mark.parametrize(
    "command, body",
    [(command, body) for command, bodies in WRONG_SHAPES.items() for body in bodies],
)
def test_json_dung_cu_phap_nhung_sai_khuon_bi_tu_choi(fake, client, command, body):
    fake.on(*COMMAND_URL[command], (200, body))
    with pytest.raises(SheetsError, match="không đúng dạng") as error:
        run(client, command)
    assert_fixed(error.value)
    assert error.value.unsure is (command in WRITES)


def test_o_doc_ve_la_vo_cuc_bi_tu_choi(fake, client):
    fake.on("GET", READ_URL, (200, b'{"values":[["x", Infinity, NaN]]}'))
    with pytest.raises(SheetsError, match="không đúng dạng"):
        client.read_plan_values()


# ================================================================ 429: thử lại đúng thiết kế
@pytest.mark.parametrize(
    "command, attempts",
    [("info", 4), ("read", 4), ("update", 2), ("append", 1), ("structure", 1)],
)
def test_429_thu_lai_dung_so_lan_va_gio_cho(fake, account, command, attempts):
    sleeps: list[float] = []
    client = make_client(fake, account, sleeps)
    fake.on(*COMMAND_URL[command], (429, BAIT_BODY))
    with pytest.raises(SheetsError) as error:
        run(client, command)
    assert_fixed(error.value)
    assert error.value.status_code == 429 and error.value.unsure is False
    assert len(fake.urls(COMMAND_URL[command][1])) == attempts
    assert len(sleeps) == attempts - 1
    for waited, base in zip(sleeps, (1.0, 2.0, 4.0), strict=False):
        assert base <= waited <= base + 0.5


@pytest.mark.parametrize("command", COMMANDS)
def test_429_roi_thanh_cong(fake, account, command):
    client = make_client(fake, account)
    good = {
        "info": info_answer(),
        "read": {"range": "KeHoach!A1:Z1001", "majorDimension": "ROWS", "values": [["Mã bài"]]},
        "update": {"totalUpdatedCells": 1},
        "append": {"updates": {"updatedRange": "KeHoach!A5:B5"}},
        "structure": {"replies": [{}]},
    }[command]
    fake.on(*COMMAND_URL[command], (429, BAIT_BODY), (200, good))
    if command in ("append", "structure"):  # thêm dòng, sửa cấu trúc: không bao giờ tự thử lại
        with pytest.raises(SheetsError, match="429"):
            run(client, command)
        assert len(fake.urls(COMMAND_URL[command][1])) == 1
    else:
        run(client, command)
        assert len(fake.urls(COMMAND_URL[command][1])) == 2


# ======================================================== RAW, đường cố định, không chặn oan
def test_luong_hop_le_day_du_khong_chan_oan_va_chi_ghi_raw(fake, account):
    """Chuẩn bị trang tính từ đầu → ghi 200 ô (tối đa) chữ dạng công thức → thêm dòng 26 cột →
    đọc lại: mọi lệnh hợp lệ đi qua, đúng 1 lần, đúng đường cố định, luôn RAW."""
    client = make_client(fake, account)
    fake.on("GET", INFO_URL, (200, info_answer(plan_id=None)), (200, info_answer(plan_id=9)))
    fake.on("POST", STRUCT_URL, (200, {"replies": [{"addSheet": {}}]}), (200, {"replies": []}))
    fake.on("POST", UPDATE_URL, (200, {"totalUpdatedCells": 200}))
    fake.on("POST", APPEND_URL, (200, {"updates": {"updatedRange": "KeHoach!A12:Z12"}}))
    fake.on("GET", READ_URL, (200, {"values": [["Mã bài", "Từ khóa chính"], [], ["SL-1", 3.5]]}))

    first = client.get_info()
    assert first.plan_tab is None
    client.batch_update([{"addSheet": {"properties": {"title": "KeHoach",
                                                      "gridProperties": {"frozenRowCount": 1}}}}])
    second = client.get_info()
    assert second.plan_tab is not None and second.plan_tab.sheet_id == 9
    rng = {"sheetId": 9, "startRowIndex": 1, "endRowIndex": 1001,
           "startColumnIndex": 6, "endColumnIndex": 7}
    client.batch_update([
        {"updateSheetProperties": {"properties": {"sheetId": 9,
                                                  "gridProperties": {"frozenRowCount": 1}},
                                   "fields": "gridProperties.frozenRowCount"}},
        {"repeatCell": {"range": rng, "fields": "userEnteredFormat.numberFormat",
                        "cell": {"userEnteredFormat": {"numberFormat": {
                            "type": "DATE", "pattern": "dd/mm/yyyy"}}}}},
        {"setDataValidation": {"range": {**rng, "startColumnIndex": 8, "endColumnIndex": 9},
                               "rule": {"condition": {"type": "ONE_OF_LIST", "values": [
                                   {"userEnteredValue": "Đang viết"},
                                   {"userEnteredValue": "Đã gửi nháp"}]},
                                   "strict": True, "showCustomUi": True}}},
    ])
    formulas = ["=IMPORTXML(\"https://evil.example\";A1)", "+1", "-1", "@x", "=1+1"]
    updates = [CellUpdate(row, column, formulas[(row + column) % len(formulas)])
               for row in range(2, 10) for column in range(25)]
    assert client.update_cells(updates) == 200
    assert client.append_row([f"=A{i}" for i in range(26)]) == 12
    assert client.read_plan_values() == (("Mã bài", "Từ khóa chính"), (), ("SL-1", 3.5))

    allowed = {("POST", TOKEN_URL), ("GET", INFO_URL), ("GET", READ_URL), ("POST", UPDATE_URL),
               ("POST", APPEND_URL), ("POST", STRUCT_URL)}
    for sent in client._session.sent:
        assert sent["allow_redirects"] is False and sent["stream"] is True
        assert 0 < sent["timeout"] <= 30
        assert sent["auth"] is not None  # luôn gắn auth riêng: requests không lấy .netrc
    assert len(client._session.sent) == len(fake.calls)
    for request, kwargs in fake.calls:
        url = urlsplit(request.url)._replace(query="").geturl()
        assert (request.method, url) in allowed
        assert kwargs["stream"] is True
        assert 0 < kwargs["timeout"] <= 30
        assert "USER_ENTERED" not in request.url
        assert b"USER_ENTERED" not in (request.body or b"")
        auth = request.headers.get("Authorization", "")
        if url == TOKEN_URL:
            assert auth == ""
        else:
            assert auth == f"Bearer {ACCESS}"
    (update,) = fake.urls(UPDATE_URL)
    assert json.loads(update.body)["valueInputOption"] == "RAW"
    (append,) = fake.urls(APPEND_URL)
    assert parse_qs(urlsplit(append.url).query) == {
        "valueInputOption": ["RAW"], "insertDataOption": ["INSERT_ROWS"],
        "includeValuesInResponse": ["false"]}
    assert len(fake.urls(TOKEN_URL)) == 1  # mã dùng lại trong cùng client
    assert client._session.max_redirects == 0


def _call(client: SheetsClient, method: str, path: str, params=None, body=None):
    return client._send(method, path, params=params, body=body)


GOOD_UPDATE = {"valueInputOption": "RAW", "includeValuesInResponse": False, "data": [
    {"range": "'KeHoach'!B2", "majorDimension": "ROWS", "values": [["x"]]}]}
GOOD_APPEND = {"majorDimension": "ROWS", "values": [["x"]]}
APPEND_PATH = f"{SHEET}/values/{quote(chr(39) + 'KeHoach' + chr(39) + '!A1:Z1', safe='')}:append"
READ_PATH = f"{SHEET}/values/{quote(chr(39) + 'KeHoach' + chr(39) + '!A1:Z1001', safe='')}"
APPEND_PARAMS = {"valueInputOption": "RAW", "insertDataOption": "INSERT_ROWS",
                 "includeValuesInResponse": "false"}
READ_PARAMS = {"valueRenderOption": "UNFORMATTED_VALUE", "dateTimeRenderOption": "SERIAL_NUMBER",
               "majorDimension": "ROWS"}


def _update(**changes):
    body = json.loads(json.dumps(GOOD_UPDATE))
    body["data"][0].update(changes.pop("item", {}))
    body.update(changes)
    return body


def _structure(request):
    return {"requests": [request]}


MUTATIONS = {
    "update USER_ENTERED": ("POST", f"{SHEET}/values:batchUpdate", None,
                            _update(valueInputOption="USER_ENTERED")),
    "update raw chữ thường": ("POST", f"{SHEET}/values:batchUpdate", None,
                              _update(valueInputOption="raw")),
    "update tham số USER_ENTERED": ("POST", f"{SHEET}/values:batchUpdate",
                                    {"valueInputOption": "USER_ENTERED"}, _update()),
    "update thêm khóa trả lời": ("POST", f"{SHEET}/values:batchUpdate", None,
                                 _update(responseValueRenderOption="FORMULA")),
    "update vùng 2 ô": ("POST", f"{SHEET}/values:batchUpdate", None,
                        _update(item={"range": "'KeHoach'!B2:C2"})),
    "update tab khác": ("POST", f"{SHEET}/values:batchUpdate", None,
                        _update(item={"range": "'Trang tính1'!B2"})),
    "update không nháy": ("POST", f"{SHEET}/values:batchUpdate", None,
                          _update(item={"range": "KeHoach!B2"})),
    "update dòng 1002": ("POST", f"{SHEET}/values:batchUpdate", None,
                         _update(item={"range": "'KeHoach'!B1002"})),
    "update cột AA": ("POST", f"{SHEET}/values:batchUpdate", None,
                      _update(item={"range": "'KeHoach'!AA2"})),
    "update 2 giá trị": ("POST", f"{SHEET}/values:batchUpdate", None,
                         _update(item={"values": [["x", "y"]]})),
    "update ô là object": ("POST", f"{SHEET}/values:batchUpdate", None,
                           _update(item={"values": [[{"formulaValue": "=1"}]]})),
    "update ô có NUL": ("POST", f"{SHEET}/values:batchUpdate", None,
                        _update(item={"values": [["a" + chr(0) + "b"]]})),
    "update PUT": ("PUT", f"{SHEET}/values:batchUpdate", None, _update()),
    "append USER_ENTERED": ("POST", APPEND_PATH,
                            {**APPEND_PARAMS, "valueInputOption": "USER_ENTERED"}, GOOD_APPEND),
    "append OVERWRITE": ("POST", APPEND_PATH,
                         {**APPEND_PARAMS, "insertDataOption": "OVERWRITE"}, GOOD_APPEND),
    "append thiếu tham số": ("POST", APPEND_PATH, {"valueInputOption": "RAW"}, GOOD_APPEND),
    "append 2 dòng": ("POST", APPEND_PATH, APPEND_PARAMS,
                      {"majorDimension": "ROWS", "values": [["x"], ["y"]]}),
    "append vùng tab khác": ("POST", APPEND_PATH.replace("KeHoach", "Khac"), APPEND_PARAMS,
                             GOOD_APPEND),
    "read FORMULA": ("GET", READ_PATH, {**READ_PARAMS, "valueRenderOption": "FORMULA"}, None),
    "read thêm fields": ("GET", READ_PATH, {**READ_PARAMS, "fields": "*"}, None),
    "info fields *": ("GET", SHEET, {"fields": "*"}, None),
    "info includeGridData": ("GET", SHEET, {"fields": sheets.INFO_FIELDS,
                                            "includeGridData": "true"}, None),
    "mã Sheet khác": ("GET", "2" + SHEET[1:], {"fields": sheets.INFO_FIELDS}, None),
    "chèn ? vào đường": ("GET", f"{SHEET}?alt=media", {"fields": sheets.INFO_FIELDS}, None),
    "đi ngược ..": ("GET", f"{SHEET}/../{SHEET}", {"fields": sheets.INFO_FIELDS}, None),
    "developerMetadata": ("POST", f"{SHEET}/developerMetadata:search", None, {}),
    "values:batchClear": ("POST", f"{SHEET}/values:batchClear", None,
                          {"ranges": ["'KeHoach'!A1:Z1001"]}),
    "findReplace": ("POST", f"{SHEET}:batchUpdate", None, _structure(
        {"findReplace": {"find": "a", "replacement": "=IMPORTXML(1)", "allSheets": True}})),
    "appendCells công thức": ("POST", f"{SHEET}:batchUpdate", None, _structure(
        {"appendCells": {"sheetId": PLAN_ID, "fields": "*", "rows": [{"values": [
            {"userEnteredValue": {"formulaValue": "=IMPORTXML(1)"}}]}]}})),
    "pasteData HTML": ("POST", f"{SHEET}:batchUpdate", None, _structure(
        {"pasteData": {"coordinate": {"sheetId": PLAN_ID}, "data": "<b>x</b>", "html": True}})),
    "sortRange": ("POST", f"{SHEET}:batchUpdate", None, _structure(
        {"sortRange": {"range": {"sheetId": PLAN_ID}, "sortSpecs": []}})),
    "autoFill": ("POST", f"{SHEET}:batchUpdate", None, _structure(
        {"autoFill": {"range": {"sheetId": PLAN_ID}}})),
    "cutPaste": ("POST", f"{SHEET}:batchUpdate", None, _structure(
        {"cutPaste": {"source": {"sheetId": PLAN_ID}, "destination": {"sheetId": 0}}})),
    "repeatCell ghi giá trị": ("POST", f"{SHEET}:batchUpdate", None, _structure(
        {"repeatCell": {"range": {"sheetId": PLAN_ID}, "fields": "userEnteredValue",
                        "cell": {"userEnteredValue": {"formulaValue": "=1"}}}})),
    "repeatCell fields *": ("POST", f"{SHEET}:batchUpdate", None, _structure(
        {"repeatCell": {"range": {"sheetId": PLAN_ID}, "fields": "*", "cell": {
            "userEnteredFormat": {"numberFormat": {"type": "DATE"}}}}})),
    "setDataValidation công thức": ("POST", f"{SHEET}:batchUpdate", None, _structure(
        {"setDataValidation": {"range": {"sheetId": PLAN_ID}, "rule": {"condition": {
            "type": "ONE_OF_LIST", "values": [{"userEnteredValue": "=IMPORTXML(1)"}]}}}})),
    "setDataValidation tab khác": ("POST", f"{SHEET}:batchUpdate", None, _structure(
        {"setDataValidation": {"range": {"sheetId": 0}, "rule": {"condition": {
            "type": "ONE_OF_LIST", "values": [{"userEnteredValue": "a"}]}}}})),
    "freeze sheetId là bool": ("POST", f"{SHEET}:batchUpdate", None, _structure(
        {"updateSheetProperties": {"properties": {"sheetId": True, "gridProperties": {
            "frozenRowCount": 1}}, "fields": "gridProperties.frozenRowCount"}})),
    "đổi tên tab": ("POST", f"{SHEET}:batchUpdate", None, _structure(
        {"updateSheetProperties": {"properties": {"sheetId": PLAN_ID, "title": "X"},
                                   "fields": "title"}})),
    "thêm khóa ngoài requests": ("POST", f"{SHEET}:batchUpdate", None,
                                 {"requests": [FREEZE], "includeSpreadsheetInResponse": True}),
}


@pytest.mark.parametrize("call", MUTATIONS.values(), ids=MUTATIONS)
def test_lenh_ngoai_danh_sach_khong_gui_gi(fake, client, call):
    client.get_info()  # có tab «KeHoach» mã 7 (để lệnh cấu trúc không bị chặn vì chưa đọc)
    before = len(fake.calls)
    method, path, params, body = call
    with pytest.raises(SheetsError, match="không nằm trong danh sách") as error:
        _call(client, method, path, params, body)
    assert_fixed(error.value)
    assert len(fake.calls) == before  # không lệnh nào, kể cả xin mã


# ================================================================ không lộ trong câu báo và log
def test_khong_lo_khoa_ma_email_trong_log_va_cau_bao(fake, dirs, rsa_pem, caplog):
    caplog.set_level(logging.DEBUG)
    key_path = write_key(dirs.outside, rsa_pem)
    client = make_client(fake, load(key_path, dirs))
    client.get_info()
    errors = []
    for answer in ((403, BAIT_BODY), requests.exceptions.ReadTimeout(BAIT), (500, BAIT_BODY)):
        fake.on("POST", UPDATE_URL, answer)
        with pytest.raises(SheetsError) as error:
            client.update_cells([CellUpdate(2, 0, BAIT)])
        errors.append(error.value)
    fresh = make_client(fake, load(key_path, dirs))
    fake.on("POST", TOKEN_URL, (400, json.dumps({"error": "invalid_grant",
                                                   "error_description": BAIT}).encode()))
    with pytest.raises(SheetsError) as error:
        fresh.get_info()
    errors.append(error.value)
    secrets = (SHEET, ACCESS, EMAIL, BAIT, rsa_pem.splitlines()[1], str(key_path))
    shown = [record.getMessage() for record in caplog.records]
    shown += [str(item) for item in errors] + [repr(item) for item in errors]
    shown += [repr(client), repr(fresh), repr(client._account), str(client._account)]
    for text in shown:
        for secret in secrets:
            assert secret not in text


# ================================================================ bộ chặn mạng chặn google-auth
def _chain(error: BaseException) -> list[BaseException]:
    items, current = [], error
    while current is not None and len(items) < 20:
        items.append(current)
        current = current.__cause__ or current.__context__
    return items


def test_bo_chan_mang_chan_lop_chuyen_requests_cua_google_auth():
    with pytest.raises(Exception) as error:  # noqa: B017 - lỗi gốc nằm trong chuỗi nguyên nhân
        google.auth.transport.requests.Request()(url=TOKEN_URL, method="POST", body=b"x")
    assert any(isinstance(item, RealNetworkBlocked) for item in _chain(error.value))


def test_bo_chan_mang_chan_lop_chuyen_urllib3_cua_google_auth():
    request = google.auth.transport.urllib3.Request(urllib3.PoolManager())
    with pytest.raises(Exception) as error:  # noqa: B017
        request(url=TOKEN_URL, method="POST", body=b"x")
    assert any(isinstance(item, RealNetworkBlocked) for item in _chain(error.value))


def test_bo_chan_mang_chan_authorized_session_va_luong_nen_cua_no(account, monkeypatch):
    """``AuthorizedSession`` (app không dùng) mở luồng nền tra «regional access boundary» tới
    ``iamcredentials.googleapis.com``: cả lệnh chính lẫn luồng nền đều bị bộ chặn mạng chặn
    (đếm tên máy đã thử tra qua hàm tra tên đã bị chặn của conftest)."""
    import socket
    from datetime import UTC, datetime, timedelta

    from google.auth.transport.requests import AuthorizedSession

    blocked = socket.getaddrinfo  # bản đã bị conftest chặn
    tried: list[str] = []

    def spy(host, *args, **kwargs):
        tried.append(host)
        return blocked(host, *args, **kwargs)

    monkeypatch.setattr(socket, "getaddrinfo", spy)
    credentials = account.credentials
    credentials.token = ACCESS
    # Còn hạn (google-auth so giờ UTC không múi giờ): không xin mã, đi thẳng tới luồng nền.
    credentials.expiry = datetime.now(UTC).replace(tzinfo=None) + timedelta(hours=1)
    session = AuthorizedSession(credentials)
    with pytest.raises(Exception) as error:  # noqa: B017
        session.get(INFO_URL, timeout=1)
    assert any(isinstance(item, RealNetworkBlocked) for item in _chain(error.value))
    workers = [t for t in threading.enumerate() if "Boundary" in type(t).__name__]
    for thread in workers:
        thread.join(timeout=10)
        assert not thread.is_alive()
    assert "sheets.googleapis.com" in tried
    assert "iamcredentials.googleapis.com" in tried  # luồng nền có thử, và đã bị chặn
    with pytest.raises(RealNetworkBlocked):
        blocked("iamcredentials.googleapis.com", 443)


# ================================================================ file khóa: nội dung lạ
BAD_CONTENT = {
    "JSON hỏng có mồi": (f'{{"type": "service_account", "x": "{BAIT}"', "không phải JSON"),
    "rỗng": ("", "không phải JSON"),
    "mảng": (json.dumps([BAIT]), "service_account"),
    "type là mảng": (json.dumps({"type": ["service_account"], "x": BAIT}), "service_account"),
    "type authorized_user": (json.dumps({"type": "authorized_user", "refresh_token": BAIT}),
                             "service_account"),
    "type external_account": (json.dumps({"type": "external_account",
                                          "credential_source": {"url": BAIT}}), "service_account"),
    "trùng khóa private_key": (
        '{"type":"service_account","private_key":"a","private_key":"' + BAIT + '"}',
        "không phải JSON"),
    "lồng sâu": ('{"type":"service_account","x":' + "[" * 30_000 + "]" * 30_000 + "}",
                 "không phải JSON"),
    "số 5000 chữ số": ('{"type":"service_account","x":' + "9" * 5000 + "}", "không phải JSON"),
}


@pytest.mark.parametrize("content, message", BAD_CONTENT.values(), ids=BAD_CONTENT)
def test_file_khoa_noi_dung_la_cau_co_dinh(dirs, content, message):
    path = dirs.outside / "khoa.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ServiceAccountError, match=message) as error:
        load(path, dirs)
    assert_fixed(error.value, str(path), "khoa.json")
    assert error.value.__context__ is None or error.value.__suppress_context__


@pytest.mark.parametrize(
    "changes, message",
    [
        ({"client_email": BAIT}, "client_email"),
        ({"client_email": "x@gmail.com"}, "client_email"),
        ({"client_email": EMAIL.upper()}, "client_email"),
        ({"client_email": _DROP}, "client_email"),
        ({"private_key": _DROP}, "private_key"),
        ({"private_key": f"{_PEM_HEAD}\n{BAIT}\n{_PEM_TAIL}\n"}, "private_key"),
        ({"private_key": "x" * 9000}, "private_key"),
        ({"private_key_id": f"{BAIT} !"}, "private_key"),
        ({"token_uri": f"https://{BAIT}.example/token"}, "token_uri"),
        ({"token_uri": TOKEN_URL + "/"}, "token_uri"),
        ({"token_uri": TOKEN_URL.upper()}, "token_uri"),
        ({"token_uri": _DROP}, "token_uri"),
        ({"universe_domain": f"{BAIT}.example"}, "universe_domain"),
    ],
)
def test_file_khoa_truong_sai_cau_co_dinh(dirs, rsa_pem, changes, message):
    path = write_key(dirs.outside, rsa_pem, **changes)
    with pytest.raises(ServiceAccountError, match=message) as error:
        load(path, dirs)
    assert_fixed(error.value, str(path))


@pytest.mark.parametrize(
    "make_key",
    [lambda: ec.generate_private_key(ec.SECP256R1()), ed25519.Ed25519PrivateKey.generate],
    ids=["EC P-256", "Ed25519"],
)
def test_khoa_khong_phai_rsa_khong_lam_lot_loi(fake, dirs, make_key):
    """Khóa EC/Ed25519 có dấu PEM đúng: nạp được (chưa ký), nhưng gọi thì ra câu cố định."""
    account = load(write_key(dirs.outside, _pem(make_key())), dirs)
    with pytest.raises(SheetsError) as error:
        make_client(fake, account).get_info()
    assert_fixed(error.value)
    assert fake.calls == []


def test_file_khoa_dung_64_kb_nhan_64_kb_cong_1_tu_choi(dirs, rsa_pem):
    path = write_key(dirs.outside, rsa_pem)
    text = path.read_text(encoding="utf-8")
    path.write_text(text + " " * (64 * 1024 - len(text.encode())), encoding="utf-8")
    assert path.stat().st_size == 64 * 1024
    assert load(path, dirs).email == EMAIL
    path.write_text(text + " " * (64 * 1024 + 1 - len(text.encode())), encoding="utf-8")
    with pytest.raises(ServiceAccountError, match="lớn bất thường"):
        load(path, dirs)


def test_file_khoa_utf16_va_bom(dirs, rsa_pem):
    path = write_key(dirs.outside, rsa_pem)
    text = path.read_text(encoding="utf-8")
    path.write_bytes(text.encode("utf-16"))
    with pytest.raises(ServiceAccountError, match="không phải JSON"):
        load(path, dirs)
    path.write_bytes(b"\xef\xbb\xbf" + text.encode("utf-8"))
    assert load(path, dirs).email == EMAIL


@pytest.mark.parametrize("bad", ["", "   ", "khoa.json", "C:khoa.json", "~", "a" + chr(0) + "b"])
def test_duong_dan_file_khoa_la_cau_co_dinh(dirs, bad):
    with pytest.raises(ServiceAccountError) as error:
        load(bad, dirs)
    assert_fixed(error.value)


def test_khong_dung_google_application_credentials_ma_dung_file_da_kiem(
    fake, dirs, rsa_pem, monkeypatch
):
    other_key = _pem(rsa.generate_private_key(public_exponent=65537, key_size=2048))
    other = write_key(dirs.outside, other_key, name="khac.json", client_email=OTHER_EMAIL)
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", str(other))
    client = make_client(fake, load(write_key(dirs.outside, rsa_pem), dirs))
    client.get_info()
    (token,) = fake.urls(TOKEN_URL)
    form = {name: values[0] for name, values in parse_qs(token.body.decode()).items()}
    header, payload, signature = form["assertion"].split(".")
    claims = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    assert claims["iss"] == EMAIL and "sub" not in claims
    assert claims["aud"] == TOKEN_URL
    assert claims["scope"] == "https://www.googleapis.com/auth/spreadsheets"
    public = serialization.load_pem_private_key(rsa_pem.encode(), None).public_key()
    public.verify(
        base64.urlsafe_b64decode(signature + "=" * (-len(signature) % 4)),
        f"{header}.{payload}".encode(),
        padding.PKCS1v15(),
        hashes.SHA256(),
    )


# ================================================================ file khóa: vị trí
@pytest.mark.parametrize(
    "where, message", [("du-an", "thư mục phần mềm"), ("anh-dong-bo", "thư mục ảnh")]
)
def test_cac_dang_duong_dan_khac_van_bi_bat(dirs, rsa_pem, where, message):
    """Đối chứng cho SL-T097-3: các dạng này đã bị bắt đúng (thư mục dự án và thư mục ảnh)."""
    inside = write_key(dirs.project if where == "du-an" else dirs.images, rsa_pem)
    variants = [str(inside), f"{dirs.outside}/../../{where}/{inside.name}"]
    if os.name == "nt":
        variants += [str(inside).upper(), str(inside).lower(), "\\\\.\\" + str(inside),
                     str(inside) + ".", str(inside) + " ", str(inside) + "::$DATA",
                     str(inside).replace("\\", "/")]
    for variant in variants:
        with pytest.raises(ServiceAccountError, match=message) as error:
            load(variant, dirs)
        assert_fixed(error.value, str(inside), inside.name)


_WINDOWS_ONLY = pytest.mark.skipif(os.name != "nt", reason="dạng đường dẫn chỉ có trên Windows")


def _admin_share(path: Path) -> str:
    text = str(path)
    return f"\\\\localhost\\{text[0]}${text[2:]}"


@_WINDOWS_ONLY
@pytest.mark.parametrize("where", ["dự án", "thư mục ảnh"])
def test_sl_t097_3_tien_to_thiet_bi_vao_du_an_hay_thu_muc_anh_bi_tu_choi(dirs, rsa_pem, where):
    folder = dirs.project if where == "dự án" else dirs.images
    inside = write_key(folder, rsa_pem)
    with pytest.raises(ServiceAccountError, match="thư mục phần mềm|thư mục ảnh"):
        load("\\\\?\\" + str(inside), dirs)


@_WINDOWS_ONLY
def test_sl_t097_3_thu_muc_anh_khai_tien_to_thiet_bi(dirs, rsa_pem):
    inside = write_key(dirs.images, rsa_pem)
    with pytest.raises(ServiceAccountError, match="thư mục ảnh"):
        load(inside, dirs, image_folders=("\\\\?\\" + str(dirs.images),))


@_WINDOWS_ONLY
def test_sl_t097_3_chia_se_quan_tri_localhost_vao_du_an(dirs, rsa_pem):
    inside = write_key(dirs.project, rsa_pem)
    shared = _admin_share(inside)
    if not os.path.exists(shared):
        pytest.skip("máy này không mở được chia sẻ quản trị \\\\localhost\\X$")
    with pytest.raises(ServiceAccountError, match="thư mục phần mềm"):
        load(shared, dirs)


@pytest.mark.parametrize(
    "parts",
    [("My Drive",), ("Google Drive", "bi-mat"), ("Drive của tôi",), ("GoogleDrive-ten",),
     ("OneDrive - Cong Ty",), ("Dropbox (Personal)",), ("iCloudDrive",),
     ("Mobile Documents", "com~apple~CloudDocs")],
)
def test_thu_muc_dong_bo_co_canh_bao(dirs, rsa_pem, parts):
    folder = dirs.outside.joinpath(*parts)
    folder.mkdir(parents=True)
    account = load(write_key(folder, rsa_pem), dirs)
    assert any("đồng bộ" in warning for warning in account.warnings)


@pytest.mark.parametrize("parts", [("Shared drives", "Nhom SEO"), ("Other computers", "May nha")])
def test_sl_t097_4_thu_muc_google_drive_khac_cung_canh_bao(dirs, rsa_pem, parts):
    folder = dirs.outside.joinpath(*parts)
    folder.mkdir(parents=True)
    account = load(write_key(folder, rsa_pem), dirs)
    assert any("đồng bộ" in warning for warning in account.warnings)


# ================================================================ GOOGLE_SHEET_ID và link Sheet
ID = "1AbCdEfGhIjKlMnOpQrStUvWxYz0123456789_-xyz"
GOOD_LINKS = [
    f"https://docs.google.com/spreadsheets/d/{ID}/edit#gid=0",
    f"https://docs.google.com/spreadsheets/d/{ID}/edit?usp=sharing",
    f"https://docs.google.com/spreadsheets/d/{ID}",
    f"https://docs.google.com/spreadsheets/d/{ID}/",
    f"https://docs.google.com/spreadsheets/u/0/d/{ID}/edit",
    f"https://docs.google.com/spreadsheets/u/1/d/{ID}/htmlview",
    f"https://docs.google.com/spreadsheets/d/{ID}/edit?gid=123#gid=123",
    f"https://docs.google.com/spreadsheets/d/{ID}/edit?usp=drive_link",
    f"https://docs.google.com/spreadsheets/d/{ID}/edit?usp=sharing&ouid=1&rtpof=true&sd=true",
    f"https://docs.google.com/spreadsheets/d/{ID}/edit#gid=0&range=A1",
    f"https://docs.google.com/spreadsheets/d/{ID}/edit?authuser=ten%40gmail.com",
    f"HTTPS://docs.google.com/spreadsheets/d/{ID}/edit",
    f"  https://docs.google.com/spreadsheets/d/{ID}/edit" + chr(10),
    ID,
    f"  {ID}" + chr(9),
]


@pytest.mark.parametrize("link", GOOD_LINKS)
def test_link_sheet_dung_dang_lay_dung_ma(link):
    assert sheets.sheet_id_from_link(link) == ID


BAD_LINKS = [
    f"https://docs.google.com.evil.example/spreadsheets/d/{ID}/edit",
    f"https://evil.example/spreadsheets/d/{ID}/edit#docs.google.com",
    f"https://x@docs.google.com/spreadsheets/d/{ID}/edit",
    f"https://docs.google.com:8443/spreadsheets/d/{ID}/edit",
    "https://docs.google.com\\@evil.example/spreadsheets/d/" + ID,
    f"http://docs.google.com/spreadsheets/d/{ID}/edit",
    f"https:/docs.google.com/spreadsheets/d/{ID}/edit",
    f"https://docs.google.com./spreadsheets/d/{ID}/edit",
    f"javascript:alert(1)//docs.google.com/spreadsheets/d/{ID}",
    f"https://docs.google.com/spreadsheets/d/e/2PACX-{'a' * 80}/pubhtml",
    f"https://docs.google.com/spreadsheets/d/{ID}" + chr(10) + "GOOGLE_SERVICE_ACCOUNT_FILE=C:/x",
    f"https://docs.google.com/spreadsheets/d/{ID}%0aX=1",
    f"https://docs.google.com/spreadsheets/d/{ID[:-1]}" + chr(0x0430),
    f"https://docs.google.com/spreadsheets/d/{ID}" + chr(0x200B) + "/edit",
    f"https://docs.google.com/spreadsheets/d/{ID}" + chr(9) + "/edit",
    f"https://docs.google.com/spreadsheets/d/{'A' * 101}/edit",
    f"https://docs.google.com/spreadsheets/d/{'A' * 24}/edit",
    None,
    b"https://docs.google.com/spreadsheets/d/" + ID.encode(),
]


@pytest.mark.parametrize("link", BAD_LINKS)
def test_link_sheet_doc_bi_tu_choi_cau_khong_chep_ma(link):
    with pytest.raises(SheetsError) as error:
        sheets.sheet_id_from_link(link)
    assert_fixed(error.value, ID, "evil.example")


_CRLF = chr(13) + chr(10)
ENV_ORIGINAL = chr(0xFEFF) + _CRLF.join(  # có BOM, xuống dòng kiểu Windows
    ["# đầu file", "WORDPRESS_URL=https://site.example", "GOOGLE_SHEET_ID=",
     "ANTHROPIC_API_KEY=khoa-gia", ""]
)
POISON = [
    ID + chr(10) + "WORDPRESS_URL=https://evil.example",
    ID + chr(13) + "X=1",
    ID + "=",
    "${WORDPRESS_APP_PASSWORD}" + "A" * 20,
    "$WORDPRESS_APP_PASSWORD" + "A" * 20,
    ID[:-1] + chr(34),
    ID[:-1] + chr(39),
    ID[:-1] + "#",
    ID[:-1] + chr(92),
    ID[:-1] + chr(96),
    ID[:10] + " " + ID[10:],
    ID[:10] + chr(0) + ID[10:],
    ID[:10] + chr(0x2028) + ID[10:],
    ID[:10] + chr(0x85) + ID[10:],
    ID[:-1] + chr(0xFF21),
    ID[:-1] + chr(0x0430),
    "A" * 24,
    "A" * 101,
    f"https://docs.google.com/spreadsheets/d/{ID}/edit",
    None,
]


@pytest.mark.parametrize("value", POISON)
def test_ma_sheet_doc_khong_ghi_gi_vao_env(tmp_path, value):
    env = tmp_path / ".env"
    env.write_bytes(ENV_ORIGINAL.encode("utf-8"))
    with pytest.raises(env_file.EnvFileError) as error:
        env_file.set_google_sheet_id(value, env)
    assert env.read_bytes() == ENV_ORIGINAL.encode("utf-8")
    for item in (ID[5:15], "WORDPRESS", "evil.example"):
        assert item not in str(error.value)


@pytest.mark.parametrize(
    "text",
    [
        "WORDPRESS_URL=https://site.example\n",
        "export GOOGLE_SHEET_ID=cu\nWORDPRESS_URL=https://site.example\n",
        "GOOGLE_SHEET_ID=a\nWORDPRESS_URL=https://site.example\nGOOGLE_SHEET_ID=b\n",
        'GOOGLE_SHEET_ID="a\nWORDPRESS_URL=https://evil.example"\n'
        "WORDPRESS_URL=https://site.example\n",
        "GOOGLE_SHEET_ID=${WORDPRESS_URL}\nWORDPRESS_URL=https://site.example\n",
        "WORDPRESS_URL=https://site.example",
    ],
    ids=["chưa có dòng", "export", "hai dòng", "nháy nhiều dòng", "chèn biến", "không xuống dòng"],
)
def test_ghi_ma_dung_vao_env_la_chi_doi_dong_cua_no(tmp_path, text):
    env = tmp_path / ".env"
    env.write_text(text, encoding="utf-8", newline="")
    env_file.set_google_sheet_id(ID, env)
    settings = config.load_settings(env, environ={})
    assert settings.google_sheet_id == ID
    assert settings.wordpress_url == "https://site.example"
    assert "evil.example" not in env.read_text(encoding="utf-8")


def test_sheets_client_tu_choi_ma_sheet_doc_trong_env(tmp_path, dirs, rsa_pem):
    """Mã sai sửa tay trong .env: client không dựng, không đọc file khóa, câu không chép mã."""
    key = write_key(dirs.outside, rsa_pem)
    env = tmp_path / "doc.env"
    for value in (ID + "/../x", "A" * 24, "A" * 101, ID + "#x", ID + ".evil"):
        env.write_text(
            f"GOOGLE_SHEET_ID={value}\nGOOGLE_SERVICE_ACCOUNT_FILE={key}\n", encoding="utf-8"
        )
        settings = config.load_settings(env, environ={})
        assert settings.google_sheet_id == value  # load_settings chưa kiểm (Rủi ro 1 của Thợ Máy)
        with pytest.raises(SheetsError, match="Mã Google Sheet") as error:
            SheetsClient.from_settings(settings)
        assert_fixed(error.value, value)


def test_service_account_khong_co_ham_ghi_duong_dan_file_khoa():
    names = [name for name in dir(env_file) if "service" in name.lower()]
    assert names == []
    assert "GOOGLE_SERVICE_ACCOUNT_FILE" not in env_file.ALLOWED_KEYS
    with pytest.raises(env_file.EnvFileError):
        env_file.set_api_key("GOOGLE_SERVICE_ACCOUNT_FILE", "C:/x/khoa.json")


def test_code_google_khong_dung_tai_khoan_ngam_dinh_hay_lop_chuyen_cua_thu_vien():
    """Đọc cây cú pháp (bỏ chữ trong docstring): không ``*.auth.default``, ``with_subject``,
    ``AuthorizedSession``, ``before_request``, ``compute_engine``, lớp chuyển 120 giây của thư
    viện, không đọc ``GOOGLE_APPLICATION_CREDENTIALS``."""
    import ast

    banned_attrs = {"with_subject", "AuthorizedSession", "before_request", "compute_engine",
                    "apply", "with_scopes", "with_quota_project"}
    for module in (sa, sheets):
        tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                assert node.attr not in banned_attrs, ast.unparse(node)
                if node.attr == "default":
                    assert not ast.unparse(node.value).endswith("auth"), ast.unparse(node)
                if node.attr == "Request":  # google.auth.transport.requests.Request (120 giây)
                    assert "requests" not in ast.unparse(node.value), ast.unparse(node)
            if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("google"):
                names = {alias.name for alias in node.names}
                assert not names & {"default", "compute_engine", "AuthorizedSession"}, names
            if isinstance(node, ast.Constant) and node.value == "GOOGLE_APPLICATION_CREDENTIALS":
                pytest.fail("đọc GOOGLE_APPLICATION_CREDENTIALS")


# ================================================================ Lượt 2 (2026-10-28)
_BS = chr(92)


class _Tripwire(io.RawIOBase):
    """Thân câu trả lời đếm số lần bị đọc (LC-T097-1: thân 3xx không được đọc). Lần đọc đầu trả
    1 byte, sau đó hết thân: code lỡ đọc thì test hỏng ngay, không treo."""

    def __init__(self) -> None:
        self.reads = 0

    def readable(self) -> bool:
        return True

    def readinto(self, buffer) -> int:
        self.reads += 1
        if self.reads > 1:
            return 0
        buffer[:1] = b"x"
        return 1


@pytest.mark.parametrize("command", COMMANDS)
@pytest.mark.parametrize("status", [301, 302, 304, 307, 308])
@pytest.mark.parametrize("location", [True, False], ids=["co-location", "khong-location"])
def test_luot2_3xx_khong_doc_than_khong_di_theo_unsure_theo_lenh(
    fake, client, command, status, location
):
    wire = _Tripwire()
    headers = {"Location": "https://evil.example/x", "Content-Encoding": "gzip"} if location else {}
    fake.on(*COMMAND_URL[command], (status, wire, headers))
    with pytest.raises(SheetsError, match="chuyển hướng") as error:
        run(client, command)
    assert_fixed(error.value, "evil.example")
    assert error.value.unsure is (command in WRITES)
    assert error.value.status_code == status
    assert wire.reads == 0
    assert "evil.example" not in fake.hosts()


@pytest.mark.parametrize("status", [302, 307, 308])
@pytest.mark.parametrize("location", [True, False], ids=["co-location", "khong-location"])
def test_luot2_lenh_xin_ma_3xx_khong_doc_than(fake, client, status, location):
    wire = _Tripwire()
    headers = {"Location": "https://evil.example/token"} if location else {}
    fake.on("POST", TOKEN_URL, (status, wire, headers))
    with pytest.raises(SheetsError) as error:
        client.get_info()
    assert_fixed(error.value, "evil.example")
    assert wire.reads == 0
    assert fake.hosts() == {"oauth2.googleapis.com"}


TOKEN_ODD_LUOT2 = {
    "expires_in -1e400": (200, b'{"access_token":"ya29.x","expires_in":-1e400}'),
    "expires_in chu 5000 so": (
        200, b'{"access_token":"ya29.x","expires_in":"' + b"9" * 5000 + b'"}'),
    "expires_in so 5000 chu so": (
        200, b'{"access_token":"ya29.x","expires_in":' + b"9" * 5000 + b"}"),
    "truong thua long sau": (
        200,
        b'{"access_token":"ya29.x","expires_in":3599,"x":' + b"[" * 30_000 + b"]" * 30_000 + b"}"),
    "400 error long 990": (400, b'{"error":' + b"[" * 990 + b"]" * 990 + b"}"),
    "400 khong error long 990": (400, b'{"x":' + b"[" * 990 + b"]" * 990 + b"}"),
    "500 long sau": (500, b"[" * 60_000),
}


@pytest.mark.parametrize("answer", TOKEN_ODD_LUOT2.values(), ids=TOKEN_ODD_LUOT2)
def test_luot2_lenh_xin_ma_tra_loi_la_them(fake, client, answer):
    fake.on("POST", TOKEN_URL, answer)
    with pytest.raises(SheetsError) as error:
        client.get_info()
    assert_fixed(error.value)
    assert not fake.urls(INFO_URL)


def _device_forms(path: Path) -> dict[str, str]:
    """Cách viết khác của cùng đường ``path`` trên Windows (ổ đĩa của thư mục tạm)."""
    import ctypes

    k32 = ctypes.windll.kernel32
    text = str(path)
    drive, rest = text[:2], text[3:]
    buffer = ctypes.create_unicode_buffer(1024)
    prefix = _BS * 2 + "?" + _BS
    forms = {
        "globalroot-dos": prefix + "GLOBALROOT" + _BS + "??" + _BS + text,
        "unc-localhost": prefix + "UNC" + _BS + "localhost" + _BS + drive[0] + "$" + _BS + rest,
    }
    if k32.GetVolumeNameForVolumeMountPointW(drive + _BS, buffer, 1024):
        forms["volume-guid"] = buffer.value + rest
    if k32.QueryDosDeviceW(drive, buffer, 1024):
        forms["globalroot-device"] = prefix + "GLOBALROOT" + buffer.value + _BS + rest
    return forms


_FORMS = ["volume-guid", "globalroot-device", "globalroot-dos", "unc-localhost"]


@_WINDOWS_ONLY
@pytest.mark.parametrize("where", ["du-an", "anh"])
@pytest.mark.parametrize("form", _FORMS)
def test_luot2_dang_duong_thiet_bi_vao_du_an_hay_anh_bi_tu_choi(dirs, rsa_pem, where, form):
    inside = write_key(dirs.project if where == "du-an" else dirs.images, rsa_pem)
    path = _device_forms(inside).get(form)
    if path is None or not os.path.exists(path):
        pytest.skip("máy này không mở được dạng đường dẫn này")
    with pytest.raises(ServiceAccountError, match="thư mục phần mềm|thư mục ảnh") as error:
        load(path, dirs)
    assert_fixed(error.value, str(inside), inside.name)


@_WINDOWS_ONLY
@pytest.mark.parametrize("form", _FORMS)
def test_luot2_thu_muc_anh_khai_dang_thiet_bi_van_bat(dirs, rsa_pem, form):
    inside = write_key(dirs.images, rsa_pem)
    declared = _device_forms(dirs.images).get(form)
    if declared is None or not os.path.exists(declared):
        pytest.skip("máy này không mở được dạng đường dẫn này")
    with pytest.raises(ServiceAccountError, match="thư mục ảnh"):
        load(inside, dirs, image_folders=(declared,))


@pytest.mark.parametrize(
    "parts, synced",
    [
        (("Bộ nhớ dùng chung", "Nhom"), True),
        (("Máy tính khác",), True),
        (("Drive dùng chung",), True),
        ((unicodedata.normalize("NFD", "Máy tính khác"),), True),
        (("SHARED DRIVES",), True),
        (("Other Computers", "May nha"), True),
        (("thu-muc-rieng",), False),
    ],
    ids=["bo-nho-dung-chung", "may-tinh-khac", "drive-dung-chung", "nfd", "chu-hoa",
         "other-computers", "thuong"],
)
def test_luot2_dau_hieu_thu_muc_dong_bo(dirs, rsa_pem, parts, synced):
    folder = dirs.outside.joinpath(*parts)
    folder.mkdir(parents=True)
    account = load(write_key(folder, rsa_pem), dirs)
    assert account.in_sync_folder is synced
    assert any("đồng bộ" in warning for warning in account.warnings) is synced


def test_luot2_khong_chan_oan_thu_muc_ten_giong_va_ngoai(dirs, rsa_pem, tmp_path):
    """Đối chứng cho SL-T097-5: thư mục tên bắt đầu giống dự án / thư mục ảnh vẫn được nhận."""
    for name in ("du-an-2", "anh-dong-bo-cu"):
        folder = tmp_path / name
        folder.mkdir()
        assert load(write_key(folder, rsa_pem), dirs).email == EMAIL


@pytest.mark.xfail(
    strict=True,
    reason="SL-T097-5: _inside_by_identity đi ngược các thư mục cha THEO CHỮ của đường gõ (không "
    "chuẩn hóa ..): «<dự án>/../ngoai/k.json» có một thư mục cha theo chữ là thư mục dự án nên bị "
    "coi là nằm trong dự án (trước lượt 2, phép so chuỗi sau normpath nhận đúng)",
)
@pytest.mark.parametrize("via", ["du-an", "anh", "du-an-con"])
def test_sl_t097_5_duong_co_cham_cham_di_ngang_roi_ra_ngoai_khong_bi_chan_oan(
    dirs, rsa_pem, via
):
    key = write_key(dirs.outside, rsa_pem)  # <tạm>/ngoai/bi-mat/<tên>.json, ngoài cả hai thư mục
    (dirs.project / "con").mkdir()
    base = {"du-an": dirs.project, "anh": dirs.images, "du-an-con": dirs.project / "con"}[via]
    ups = os.sep.join([".."] * (2 if via == "du-an-con" else 1))
    path = os.sep.join([str(base), ups, "ngoai", "bi-mat", key.name])
    assert Path(os.path.normpath(path)) == key  # đúng là file ở ngoài
    assert load(path, dirs).email == EMAIL
