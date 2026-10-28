"""Client Google Sheets REST v4 cho kế hoạch (T-097; thiết kế T-094 mục 2.3).

An toàn (điều kiện Lá Chắn LC-T094-2, -12, -13, -15):

- **Danh sách lệnh cố định** (như ``ALLOWED_ROUTES`` của client WordPress), kiểm **trước khi
  gửi** ở một chỗ (``_check_call``), bất kể ai gọi: đúng phương thức, đúng đường (mã Sheet,
  vùng ô dựng từ hằng ``PLAN_TAB`` và **chỉ số** cột), đúng từng tham số, đúng khuôn thân JSON.
  Ghi ô chỉ nhận ``valueInputOption = RAW`` (chữ bắt đầu bằng ``=`` không thành công thức).
  ``:batchUpdate`` chỉ nhận 4 loại yêu cầu của thiết kế (``addSheet``, ``updateSheetProperties``
  cố định dòng tiêu đề, ``repeatCell`` định dạng số/ngày, ``setDataValidation`` danh sách chọn)
  và chỉ trên đúng tab «KeHoach» vừa đọc bằng ``get_info``; không bao giờ xóa tab, dòng, vùng.
- Chỉ ``https://sheets.googleapis.com`` và máy chủ mã ``https://oauth2.googleapis.com/token``.
  Lệnh xin mã của ``google-auth`` đi qua ``_TokenRequest`` của module này (thư viện mặc định đợi
  tới 120 giây và đi theo chuyển hướng): giờ chờ 30 giây, không theo chuyển hướng, câu trả lời
  ≤ 64 KB. Không dùng ``before_request``/``AuthorizedSession`` (bản 2.62.0 tự mở luồng nền gọi
  thêm ``iamcredentials.googleapis.com``): chỉ ``refresh`` rồi tự gắn header ``Bearer``.
- Mọi lệnh: giờ chờ ≤ 30 giây, ``allow_redirects=False`` (phiên ``max_redirects = 0``), câu trả
  lời 3xx đóng ngay, không đọc thân (móc ``_refuse_redirect``, LC-T097-1), đọc câu trả lời theo
  luồng, quá 2 MB thì bỏ. Lỗi 429: lệnh đọc thử lại tối đa 3 lần (1, 2, 4 giây
  cộng ngẫu nhiên), lệnh ghi ô thử lại 1 lần, lệnh thêm dòng và ``:batchUpdate`` **không bao
  giờ** tự thử lại.
- Câu lỗi cố định theo mã HTTP: không chép lời máy chủ Google, mã Sheet, chữ trong ô.
  ``SheetsError.unsure``: lệnh ghi có thể đã chạy trên Google dù báo lỗi (hết giờ, mất mạng,
  5xx, trả lời hỏng); nơi gọi phải đọc lại trước khi làm lại.
- Mã Sheet coi như nửa bí mật (Sheet lỡ bật «bất kỳ ai có link» thì mã là chìa khóa):
  ``repr`` chỉ hiện 4 ký tự cuối (``mask_sheet_id``); mã chỉ tách từ link đúng dạng
  (``sheet_id_from_link``), không bao giờ mở link người dùng dán.

Client tạo mới cho **mỗi** thao tác (``from_settings`` kiểm lại file khóa mỗi lần, LC-T094-11);
không giữ qua các lần bấm (không ``st.cache_resource``). Dữ liệu đọc từ Sheet là **chưa tin
cậy**: client chỉ kiểm khuôn (≤ 1.001 dòng, ≤ 26 cột, ô là chữ/số/đúng-sai); nơi dùng phải qua
``PlanRow`` (T-098, T-100).
"""

from __future__ import annotations

import json
import math
import random
import re
import time
import unicodedata
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote, urlsplit

import requests
from google.auth import exceptions as google_exceptions
from google.auth import transport as google_transport

from seo_app.env_file import SHEET_ID_PATTERN
from seo_app.google.service_account import TOKEN_URI, ServiceAccount

SHEETS_URL = "https://sheets.googleapis.com"
SPREADSHEETS_URL = f"{SHEETS_URL}/v4/spreadsheets/"
PLAN_TAB = "KeHoach"
MAX_COLUMNS = 26  # A…Z
MAX_ROWS = 1001  # dòng tiêu đề + 1.000 dòng kế hoạch
MAX_CELL_CHARS = 2000
MAX_UPDATES = 200
MAX_STRUCTURE_REQUESTS = 50
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
MAX_TOKEN_RESPONSE_BYTES = 64 * 1024
DEFAULT_TIMEOUT = 30
READ_RETRIES = 3
UPDATE_RETRIES = 1
_RETRY_DELAYS = (1.0, 2.0, 4.0)

INFO_FIELDS = "properties(title,locale,timeZone),sheets.properties(sheetId,title)"
READ_RANGE = f"'{PLAN_TAB}'!A1:Z{MAX_ROWS}"
APPEND_RANGE = f"'{PLAN_TAB}'!A1:Z1"

CellValue = str | int | float | bool

# ---------------------------------------------------------------- danh sách lệnh cố định
_ID = r"[A-Za-z0-9_-]{25,100}"
_READ_PARAMS = {
    "valueRenderOption": "UNFORMATTED_VALUE",
    "dateTimeRenderOption": "SERIAL_NUMBER",
    "majorDimension": "ROWS",
}
_APPEND_PARAMS = {
    "valueInputOption": "RAW",
    "insertDataOption": "INSERT_ROWS",
    "includeValuesInResponse": "false",
}
# (tên lệnh, phương thức, đường sau /v4/spreadsheets/, tham số đúng từng giá trị, số lần thử lại
# khi gặp 429, là lệnh ghi)
_ROUTES: tuple[tuple[str, str, re.Pattern[str], dict[str, str], int, bool], ...] = (
    ("info", "GET", re.compile(rf"({_ID})"), {"fields": INFO_FIELDS}, READ_RETRIES, False),
    (
        "read",
        "GET",
        re.compile(rf"({_ID})/values/{re.escape(quote(READ_RANGE, safe=''))}"),
        _READ_PARAMS,
        READ_RETRIES,
        False,
    ),
    ("update", "POST", re.compile(rf"({_ID})/values:batchUpdate"), {}, UPDATE_RETRIES, True),
    (
        "append",
        "POST",
        re.compile(rf"({_ID})/values/{re.escape(quote(APPEND_RANGE, safe=''))}:append"),
        _APPEND_PARAMS,
        0,
        True,
    ),
    ("structure", "POST", re.compile(rf"({_ID}):batchUpdate"), {}, 0, True),
)
# Vùng một ô do code dựng: tab cố định, cột A…Z, dòng 1…MAX_ROWS.
_CELL_RANGE = re.compile(rf"'{PLAN_TAB}'!([A-Z])([1-9][0-9]{{0,3}})")
_UPDATED_RANGE = re.compile(
    rf"(?:'{PLAN_TAB}'|{PLAN_TAB})!A([1-9][0-9]{{0,6}})(?::[A-Z]{{1,2}}[0-9]{{1,7}})?"
)
# Mã truy cập Google ("ya29.…"): chữ, số và vài dấu, không khoảng trắng hay xuống dòng.
_TOKEN = re.compile(r"[A-Za-z0-9._~+/=-]{1,4096}")
_SAFE_INT = 2**53

# ---------------------------------------------------------------- câu báo cố định
_MSG_BAD_ID = (
    "Mã Google Sheet chưa khai báo hoặc sai dạng. Dán lại link Google Sheet kế hoạch ở trang "
    "Cài đặt."
)
_MSG_BAD_LINK = (
    "Link chưa đúng dạng link Google Sheet (https://docs.google.com/spreadsheets/d/…). Mở Sheet "
    "trên trình duyệt, chép đường link ở thanh địa chỉ rồi dán lại."
)
_MSG_BLOCKED = (
    "Lệnh gọi Google Sheets này không nằm trong danh sách được phép, phần mềm không gửi."
)
_MSG_NO_INFO = "Phải đọc thông tin Google Sheet (kiểm tra kết nối) ngay trước khi sửa cấu trúc."
_MSG_BAD_VALUE = (
    "Dữ liệu định ghi lên Google Sheet không đúng dạng (ô phải là chữ ≤ "
    f"{MAX_CELL_CHARS} ký tự, số hoặc đúng/sai), phần mềm không gửi."
)
_MSG_AUTH = (
    "Không lấy được mã truy cập Google cho tài khoản dịch vụ. Kiểm tra file khóa còn hiệu lực "
    "(chưa bị xóa trong Google Cloud) rồi thử lại."
)
_MSG_AUTH_GRANT = (
    "Google từ chối khóa của tài khoản dịch vụ: khóa đã bị xóa hay vô hiệu trong Google Cloud, "
    "hoặc đồng hồ máy tính đang sai giờ. Kiểm tra giờ máy, hoặc tạo khóa mới."
)
_MSG_AUTH_NETWORK = (
    "Không kết nối được tới máy chủ xác thực của Google. Kiểm tra mạng Internet rồi thử lại."
)
_MSG_TIMEOUT = "Google Sheets không trả lời sau {timeout:g} giây. Thử lại sau."
_MSG_CONNECTION = "Không kết nối được tới Google Sheets. Kiểm tra mạng Internet rồi thử lại."
_MSG_SSL = "Lỗi chứng chỉ bảo mật (SSL) khi kết nối Google. Kiểm tra giờ máy và mạng."
_MSG_NETWORK = "Lỗi mạng khi gọi Google Sheets ({kind}). Thử lại sau."
_MSG_REDIRECT = (
    "Google trả lời bằng một lệnh chuyển hướng (mã {code}); phần mềm không đi theo. Thử lại sau."
)
_MSG_TOO_BIG = (
    f"Câu trả lời của Google lớn bất thường (quá {MAX_RESPONSE_BYTES // (1024 * 1024)} MB), "
    "phần mềm bỏ qua. Kiểm tra trang tính «KeHoach» có quá nhiều dữ liệu không."
)
_MSG_BAD_DATA = "Google Sheets trả về dữ liệu không đúng dạng (mã {code}). Thử lại sau."
_MSG_BY_STATUS = {
    400: "Google Sheets báo yêu cầu không hợp lệ (mã 400).",
    401: (
        "Google không nhận mã truy cập (mã 401). Thử lại; nếu vẫn lỗi, kiểm tra file khóa tài "
        "khoản dịch vụ."
    ),
    403: (
        "Tài khoản dịch vụ chưa có quyền mở Google Sheet này (mã 403). Hãy chia sẻ Sheet cho "
        "email của tài khoản dịch vụ với quyền «Người chỉnh sửa», và kiểm tra đã bật Google "
        "Sheets API trong Google Cloud."
    ),
    404: "Không tìm thấy Google Sheet (mã 404). Kiểm tra lại link Sheet ở trang Cài đặt.",
    429: "Google đang giới hạn số lần gọi (mã 429). Đợi một phút rồi thử lại.",
}
_MSG_SERVER = "Máy chủ Google Sheets đang lỗi (mã {code}). Thử lại sau ít phút."
_MSG_REJECTED = "Google Sheets từ chối yêu cầu (mã {code})."


class SheetsError(Exception):
    """Lỗi khi làm việc với Google Sheets. ``str(err)`` là câu tiếng Việt cố định.

    ``unsure``: lệnh **ghi** có thể đã chạy trên Google dù báo lỗi; đọc lại trước khi làm lại.
    """

    def __init__(
        self, message: str, *, status_code: int | None = None, unsure: bool = False
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.unsure = unsure


@dataclass(frozen=True)
class SheetTab:
    sheet_id: int
    title: str  # đã bỏ ký tự điều khiển, ký tự vô hình; nơi hiện vẫn phải escape


@dataclass(frozen=True)
class SpreadsheetInfo:
    title: str  # tên Sheet (đã bỏ ký tự lạ), để hiện thay cho mã Sheet
    locale: str
    time_zone: str
    tabs: tuple[SheetTab, ...]
    plan_tab: SheetTab | None  # tab tên đúng «KeHoach» (so nguyên văn), chưa có thì None


@dataclass(frozen=True)
class CellUpdate:
    """Một ô sẽ ghi: ``row`` đếm từ 1 (dòng 1 là tiêu đề), ``column`` là chỉ số từ 0 (A = 0)."""

    row: int
    column: int
    value: CellValue


def column_letter(index: int) -> str:
    """Chỉ số cột (0…25) → chữ cột (A…Z)."""
    if type(index) is not int or not 0 <= index < MAX_COLUMNS:
        raise SheetsError(_MSG_BAD_VALUE)
    return chr(ord("A") + index)


def mask_sheet_id(sheet_id: str) -> str:
    """Mã Sheet để hiện hay ghi chú: chỉ 4 ký tự cuối (LC-T094-15)."""
    return f"…{sheet_id[-4:]}" if isinstance(sheet_id, str) and sheet_id else "…"


_LINK_PATH = re.compile(rf"/spreadsheets(?:/u/[0-9]{{1,2}})?/d/({_ID})(?:/[^\s]*)?")


def sheet_id_from_link(text: object) -> str:
    """Mã Google Sheet từ link người dùng dán (hoặc chính mã). **Không** mở link.

    Chỉ nhận ``https://docs.google.com/spreadsheets/d/<mã>/…`` (kể cả ``/u/1/d/…``,
    ``?gid=…#gid=…``): tên máy đúng chữ ``docs.google.com``, không ``@``, không cổng, không
    ``\\``, chỉ ký tự ASCII nhìn thấy. Dán thẳng mã (đúng ``SHEET_ID_PATTERN``) cũng được.
    """
    if not isinstance(text, str):
        raise SheetsError(_MSG_BAD_LINK)
    value = text.strip()
    if SHEET_ID_PATTERN.fullmatch(value):
        return value
    if (
        not value.isascii()
        or any(ch.isspace() or ord(ch) < 32 or ord(ch) == 127 for ch in value)
        or "\\" in value
        or "@" in value
    ):
        raise SheetsError(_MSG_BAD_LINK)
    try:
        parts = urlsplit(value)
    except ValueError:
        raise SheetsError(_MSG_BAD_LINK) from None
    match = _LINK_PATH.fullmatch(parts.path)
    if parts.scheme != "https" or parts.netloc != "docs.google.com" or match is None:
        raise SheetsError(_MSG_BAD_LINK)
    return match.group(1)


# ---------------------------------------------------------------- lớp chuyển của google-auth
class _NoAuth(requests.auth.AuthBase):
    """Không gắn gì (và để ``requests`` không lấy mật khẩu trong ``.netrc``)."""

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        return request


class _Bearer(requests.auth.AuthBase):
    def __init__(self, token: str) -> None:
        self._token = token

    def __repr__(self) -> str:
        return "_Bearer(***)"

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        request.headers["Authorization"] = f"Bearer {self._token}"
        return request


class _TooLarge(Exception):
    pass


class _Redirected(Exception):
    """Câu trả lời 3xx: đã đóng, **chưa đọc** thân (LC-T097-1)."""

    def __init__(self, status: int) -> None:
        super().__init__(status)
        self.status = status


def _refuse_redirect(response: requests.Response, *_args: Any, **_kwargs: Any) -> requests.Response:
    """Móc ``response`` của ``requests``, gắn vào mọi lệnh (Sheets và xin mã): chạy ngay khi có mã
    trả lời, **trước** ``Session.resolve_redirects`` (hàm này đọc và giải nén hết thân câu trả lời
    3xx cả khi ``allow_redirects=False``, rồi mới ném ``TooManyRedirects``; LC-T097-1). Gặp 3xx
    (có hay không có ``Location``) thì đóng câu trả lời, không đọc thân, ném ``_Redirected``."""
    if 300 <= response.status_code < 400:
        response.close()
        raise _Redirected(response.status_code)
    return response


def _read_limited(response: requests.Response, limit: int) -> bytes:
    """Đọc thân câu trả lời theo luồng; quá ``limit`` byte (sau giải nén) thì ``_TooLarge``."""
    declared = response.headers.get("Content-Length", "")
    if declared.strip().isdigit() and int(declared) > limit:
        raise _TooLarge
    parts: list[bytes] = []
    total = 0
    for chunk in response.iter_content(chunk_size=64 * 1024):
        total += len(chunk)
        if total > limit:
            raise _TooLarge
        parts.append(chunk)
    return b"".join(parts)


def _close_and_status(exc: requests.RequestException) -> int | None:
    """Mã HTTP của câu trả lời gắn với lỗi ``requests`` (nếu có), đóng câu trả lời đó."""
    response = getattr(exc, "response", None)
    if response is None:
        return None
    response.close()
    status = response.status_code
    return status if type(status) is int else None


class _TokenResponse(google_transport.Response):
    def __init__(self, status: int, headers: Mapping[str, str], data: bytes) -> None:
        self._status = status
        self._headers = dict(headers)
        self._data = data

    @property
    def status(self) -> int:
        return self._status

    @property
    def headers(self) -> Mapping[str, str]:
        return self._headers

    @property
    def data(self) -> bytes:
        return self._data


class _TokenRequest(google_transport.Request):
    """Lệnh xin mã truy cập của ``google-auth`` đi qua đây: chỉ ``POST TOKEN_URI``, giờ chờ cố
    định, không theo chuyển hướng, câu trả lời ≤ 64 KB, lỗi mạng thành câu cố định."""

    def __init__(self, session: requests.Session, timeout: float) -> None:
        self._session = session
        self._timeout = timeout

    def __call__(
        self,
        url: str,
        method: str = "GET",
        body: Any = None,
        headers: Mapping[str, str] | None = None,
        timeout: Any = None,
        **kwargs: Any,
    ) -> _TokenResponse:
        if url != TOKEN_URI or method != "POST" or kwargs:
            raise google_exceptions.TransportError("blocked")
        try:
            response = self._session.request(
                "POST",
                TOKEN_URI,
                data=body,
                headers=dict(headers or {}),
                timeout=self._timeout,  # bỏ qua giờ chờ thư viện đưa (mặc định 120 giây)
                allow_redirects=False,
                stream=True,
                auth=_NoAuth(),
                hooks={"response": [_refuse_redirect]},
            )
        except _Redirected as exc:
            # Máy chủ mã trả 3xx: không đọc thân, không đi theo; google-auth thấy mã khác 200.
            return _TokenResponse(exc.status, {}, b"")
        except requests.exceptions.TooManyRedirects as exc:
            # Máy chủ mã trả 3xx: không đi theo; google-auth thấy mã khác 200 và báo lỗi xin mã.
            return _TokenResponse(_close_and_status(exc) or 302, {}, b"")
        except (requests.RequestException, OSError):
            raise google_exceptions.TransportError("network") from None
        try:
            data = _read_limited(response, MAX_TOKEN_RESPONSE_BYTES)
        except (_TooLarge, requests.RequestException, OSError):
            raise google_exceptions.TransportError("response") from None
        finally:
            response.close()
        return _TokenResponse(response.status_code, response.headers, data)


# ---------------------------------------------------------------- kiểm khuôn dữ liệu
def _is_cell_value(value: object) -> bool:
    if isinstance(value, bool):
        return True
    if isinstance(value, int):
        return -_SAFE_INT <= value <= _SAFE_INT
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, str):
        return len(value) <= MAX_CELL_CHARS and "\x00" not in value
    return False


def _keys(value: object, required: set[str], optional: set[str] = frozenset()) -> bool:
    return isinstance(value, dict) and required <= value.keys() <= required | optional


def _small_int(value: object, low: int, high: int) -> bool:
    return type(value) is int and low <= value <= high


def _valid_update_body(body: object) -> bool:
    if not _keys(body, {"valueInputOption", "includeValuesInResponse", "data"}):
        return False
    data = body["data"]
    if (
        body["valueInputOption"] != "RAW"
        or body["includeValuesInResponse"] is not False
        or not isinstance(data, list)
        or not 1 <= len(data) <= MAX_UPDATES
    ):
        return False
    for item in data:
        if not _keys(item, {"range", "majorDimension", "values"}):
            return False
        cell = _CELL_RANGE.fullmatch(item["range"]) if isinstance(item["range"], str) else None
        values = item["values"]
        if (
            cell is None
            or int(cell.group(2)) > MAX_ROWS
            or item["majorDimension"] != "ROWS"
            or not (isinstance(values, list) and len(values) == 1)
            or not (isinstance(values[0], list) and len(values[0]) == 1)
            or not _is_cell_value(values[0][0])
        ):
            return False
    return True


def _valid_append_body(body: object) -> bool:
    if not _keys(body, {"majorDimension", "values"}) or body["majorDimension"] != "ROWS":
        return False
    values = body["values"]
    return (
        isinstance(values, list)
        and len(values) == 1
        and isinstance(values[0], list)
        and 1 <= len(values[0]) <= MAX_COLUMNS
        and all(_is_cell_value(cell) for cell in values[0])
    )


def _valid_grid_range(value: object, sheet_id: int) -> bool:
    optional = {"startRowIndex", "endRowIndex", "startColumnIndex", "endColumnIndex"}
    if not _keys(value, {"sheetId"}, optional) or value["sheetId"] != sheet_id:
        return False
    if type(value["sheetId"]) is not int:
        return False
    limits = {
        "startRowIndex": MAX_ROWS,
        "endRowIndex": MAX_ROWS,
        "startColumnIndex": MAX_COLUMNS,
        "endColumnIndex": MAX_COLUMNS,
    }
    if not all(_small_int(value[key], 0, limits[key]) for key in optional & value.keys()):
        return False
    for start, end in (("startRowIndex", "endRowIndex"), ("startColumnIndex", "endColumnIndex")):
        if start in value and end in value and value[start] >= value[end]:
            return False
    return True


_NUMBER_FORMAT_TYPES = frozenset({"TEXT", "NUMBER", "DATE", "TIME", "DATE_TIME"})
_FORMULA_START = ("=", "+", "-", "@")


def _valid_structure_request(request: object, plan_sheet_id: int | None) -> bool:
    """Một yêu cầu ``:batchUpdate``: đúng 1 trong 4 loại của thiết kế, đúng tab «KeHoach»."""
    if not isinstance(request, dict) or len(request) != 1:
        return False
    kind, body = next(iter(request.items()))
    if kind == "addSheet":
        # Chỉ tạo tab «KeHoach» khi lần đọc gần nhất chưa thấy tab đó.
        if plan_sheet_id is not None or not _keys(body, {"properties"}):
            return False
        props = body["properties"]
        if not _keys(props, {"title"}, {"gridProperties"}) or props["title"] != PLAN_TAB:
            return False
        grid = props.get("gridProperties", {})
        return _keys(grid, set(), {"rowCount", "columnCount", "frozenRowCount"}) and all(
            _small_int(grid[key], 0, MAX_ROWS) for key in grid
        )
    if plan_sheet_id is None:
        return False
    if kind == "updateSheetProperties":
        # Chỉ cố định dòng tiêu đề; không đổi tên, không ẩn, không dời tab.
        if not _keys(body, {"properties", "fields"}) or body["fields"] != (
            "gridProperties.frozenRowCount"
        ):
            return False
        props = body["properties"]
        return (
            _keys(props, {"sheetId", "gridProperties"})
            and type(props["sheetId"]) is int
            and props["sheetId"] == plan_sheet_id
            and _keys(props["gridProperties"], {"frozenRowCount"})
            and _small_int(props["gridProperties"]["frozenRowCount"], 0, 10)
        )
    if kind == "repeatCell":
        # Chỉ định dạng số/ngày; không bao giờ ghi giá trị ô (userEnteredValue) qua đường này.
        if not _keys(body, {"range", "cell", "fields"}) or body["fields"] != (
            "userEnteredFormat.numberFormat"
        ):
            return False
        cell = body["cell"]
        if not (_keys(cell, {"userEnteredFormat"}) and _keys(
            cell["userEnteredFormat"], {"numberFormat"}
        )):
            return False
        number_format = cell["userEnteredFormat"]["numberFormat"]
        return (
            _keys(number_format, {"type"}, {"pattern"})
            and number_format["type"] in _NUMBER_FORMAT_TYPES
            and (
                "pattern" not in number_format
                or (
                    isinstance(number_format["pattern"], str)
                    and 1 <= len(number_format["pattern"]) <= 40
                    and number_format["pattern"].isascii()
                    and not number_format["pattern"].startswith(_FORMULA_START)
                )
            )
            and _valid_grid_range(body["range"], plan_sheet_id)
        )
    if kind == "setDataValidation":
        # Chỉ danh sách chọn cố định (ONE_OF_LIST); không công thức, không lấy từ vùng khác.
        if not _keys(body, {"range", "rule"}) or not _valid_grid_range(
            body["range"], plan_sheet_id
        ):
            return False
        rule = body["rule"]
        if not _keys(rule, {"condition"}, {"strict", "showCustomUi"}):
            return False
        if any(type(rule[key]) is not bool for key in ("strict", "showCustomUi") if key in rule):
            return False
        condition = rule["condition"]
        if not _keys(condition, {"type", "values"}) or condition["type"] != "ONE_OF_LIST":
            return False
        values = condition["values"]
        return (
            isinstance(values, list)
            and 1 <= len(values) <= 50
            and all(
                _keys(item, {"userEnteredValue"})
                and isinstance(item["userEnteredValue"], str)
                and 1 <= len(item["userEnteredValue"]) <= 100
                and not item["userEnteredValue"].startswith(_FORMULA_START)
                for item in values
            )
        )
    return False


def _clean_text(value: object, limit: int = 200) -> str:
    """Chữ từ Google (tên Sheet, tên tab) để hiện: bỏ ký tự điều khiển, vô hình, đổi hướng chữ."""
    if not isinstance(value, str):
        return ""
    kept = "".join(
        ch
        for ch in unicodedata.normalize("NFC", value)
        if unicodedata.category(ch) not in ("Cc", "Cf", "Cs", "Co", "Cn")
    )
    return " ".join(kept.split())[:limit]


# ---------------------------------------------------------------- client
class SheetsClient:
    """Đọc/ghi Google Sheet kế hoạch bằng tài khoản dịch vụ (``ServiceAccount`` đã kiểm)."""

    def __init__(
        self,
        spreadsheet_id: str,
        account: ServiceAccount,
        *,
        session: requests.Session | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if not isinstance(spreadsheet_id, str) or not SHEET_ID_PATTERN.fullmatch(spreadsheet_id):
            raise SheetsError(_MSG_BAD_ID)
        if not isinstance(account, ServiceAccount):
            raise SheetsError(_MSG_AUTH)
        self._id = spreadsheet_id
        self._account = account
        self._session = session if session is not None else requests.Session()
        # Không theo chuyển hướng ở cả lệnh Sheets lẫn lệnh xin mã (LC-T094-13).
        self._session.max_redirects = 0
        self.timeout = min(float(timeout), DEFAULT_TIMEOUT) if timeout > 0 else DEFAULT_TIMEOUT
        self._sleep = sleep
        self._token_request = _TokenRequest(self._session, self.timeout)
        self._info_read = False
        self._plan_sheet_id: int | None = None

    @classmethod
    def from_settings(
        cls, settings: Any = None, *, session: requests.Session | None = None
    ) -> SheetsClient:
        """Client từ ``.env``: kiểm mã Sheet rồi kiểm lại file khóa (mỗi lần gọi).

        Ném ``SheetsError`` (mã Sheet) hoặc ``ServiceAccountError`` (file khóa).
        """
        from seo_app import config
        from seo_app.google.service_account import load_service_account

        if settings is None:
            settings = config.load_settings()
        sheet_id = getattr(settings, "google_sheet_id", "")
        # ``load_settings`` (config.py) chưa kiểm dạng mã: kiểm ở đây, trước mọi lệnh gọi.
        if not isinstance(sheet_id, str) or not SHEET_ID_PATTERN.fullmatch(sheet_id):
            raise SheetsError(_MSG_BAD_ID)
        account = load_service_account(
            settings.google_service_account_file, image_folders=settings.image_folders
        )
        return cls(sheet_id, account, session=session)

    def __repr__(self) -> str:
        return f"SheetsClient(sheet={mask_sheet_id(self._id)!r})"

    @property
    def account_email(self) -> str:
        """Email tài khoản dịch vụ (để chủ dự án chia sẻ Sheet; chỉ hiện ở trang Cài đặt)."""
        return self._account.email

    @property
    def account_warnings(self) -> tuple[str, ...]:
        return self._account.warnings

    # ------------------------------------------------------------- lệnh công khai
    def get_info(self) -> SpreadsheetInfo:
        """Tên Sheet, vùng, múi giờ và các tab; ghi nhớ mã tab «KeHoach» cho ``batch_update``."""
        data = self._send("GET", self._id, params={"fields": INFO_FIELDS})
        props = data.get("properties")
        sheets = data.get("sheets", [])
        if not isinstance(props, dict) or not isinstance(sheets, list) or len(sheets) > 200:
            raise SheetsError(_MSG_BAD_DATA.format(code=200))
        tabs: list[SheetTab] = []
        plan: list[SheetTab] = []
        for item in sheets:
            tab_props = item.get("properties") if isinstance(item, dict) else None
            if not isinstance(tab_props, dict):
                raise SheetsError(_MSG_BAD_DATA.format(code=200))
            sheet_id, title = tab_props.get("sheetId", 0), tab_props.get("title")
            if not _small_int(sheet_id, 0, 2**31 - 1) or not isinstance(title, str):
                raise SheetsError(_MSG_BAD_DATA.format(code=200))
            tab = SheetTab(sheet_id, _clean_text(title))
            tabs.append(tab)
            if title == PLAN_TAB:  # so nguyên văn: tab tên gần giống không phải tab kế hoạch
                plan.append(tab)
        if len(plan) > 1:
            raise SheetsError(_MSG_BAD_DATA.format(code=200))
        self._plan_sheet_id = plan[0].sheet_id if plan else None
        self._info_read = True
        return SpreadsheetInfo(
            title=_clean_text(props.get("title")),
            locale=_clean_text(props.get("locale"), 20),
            time_zone=_clean_text(props.get("timeZone"), 60),
            tabs=tuple(tabs),
            plan_tab=plan[0] if plan else None,
        )

    def read_plan_values(self) -> tuple[tuple[CellValue, ...], ...]:
        """Cả tab «KeHoach» (A1:Z1001) trong một lệnh: ô là chữ, số (ngày là số ngày của Sheets),
        đúng/sai. Dòng trống ở giữa là bộ rỗng. Chưa tin cậy: nơi dùng phải qua ``PlanRow``."""
        data = self._send(
            "GET", f"{self._id}/values/{quote(READ_RANGE, safe='')}", params=dict(_READ_PARAMS)
        )
        values = data.get("values", [])
        if data.get("majorDimension", "ROWS") != "ROWS" or not isinstance(values, list):
            raise SheetsError(_MSG_BAD_DATA.format(code=200))
        if len(values) > MAX_ROWS:
            raise SheetsError(_MSG_BAD_DATA.format(code=200))
        rows: list[tuple[CellValue, ...]] = []
        for row in values:
            if not isinstance(row, list) or len(row) > MAX_COLUMNS:
                raise SheetsError(_MSG_BAD_DATA.format(code=200))
            if not all(_is_read_value(cell) for cell in row):
                raise SheetsError(_MSG_BAD_DATA.format(code=200))
            rows.append(tuple(row))
        return tuple(rows)

    def update_cells(self, updates: Sequence[CellUpdate]) -> int | None:
        """Ghi đúng các ô ``updates`` trong **một** lệnh (Google áp dụng trọn hoặc không), luôn
        ``RAW``. Trả số ô Google báo đã ghi (hoặc ``None`` nếu câu trả lời không có số)."""
        items = list(updates) if isinstance(updates, Sequence) else []
        if not items or len(items) > MAX_UPDATES or not all(
            isinstance(item, CellUpdate) for item in items
        ):
            raise SheetsError(_MSG_BAD_VALUE)
        data = []
        for item in items:
            if type(item.row) is not int or not 1 <= item.row <= MAX_ROWS:
                raise SheetsError(_MSG_BAD_VALUE)
            cell = f"'{PLAN_TAB}'!{column_letter(item.column)}{item.row}"
            data.append({"range": cell, "majorDimension": "ROWS", "values": [[item.value]]})
        body = {"valueInputOption": "RAW", "includeValuesInResponse": False, "data": data}
        answer = self._send("POST", f"{self._id}/values:batchUpdate", body=body)
        total = answer.get("totalUpdatedCells")
        return total if _small_int(total, 0, MAX_UPDATES) else None

    def append_row(self, values: Sequence[CellValue]) -> int | None:
        """Thêm một dòng cuối tab «KeHoach» (``RAW``, ``INSERT_ROWS``). **Không bao giờ** tự thử
        lại (lặp lại là thêm trùng). Trả số dòng Google báo đã thêm, không đọc được thì ``None``."""
        row = list(values) if isinstance(values, Sequence) and not isinstance(values, str) else []
        if not 1 <= len(row) <= MAX_COLUMNS:
            raise SheetsError(_MSG_BAD_VALUE)
        answer = self._send(
            "POST",
            f"{self._id}/values/{quote(APPEND_RANGE, safe='')}:append",
            params=dict(_APPEND_PARAMS),
            body={"majorDimension": "ROWS", "values": [row]},
        )
        updates = answer.get("updates")
        updated = updates.get("updatedRange") if isinstance(updates, dict) else None
        match = _UPDATED_RANGE.fullmatch(updated) if isinstance(updated, str) else None
        return int(match.group(1)) if match else None

    def batch_update(self, requests_: Sequence[Mapping[str, Any]]) -> tuple[dict[str, Any], ...]:
        """Sửa cấu trúc tab «KeHoach» (chỉ nút «Chuẩn bị trang tính», T-100). Phải ``get_info``
        ngay trước; sau lệnh này phải ``get_info`` lại mới gọi tiếp được."""
        is_list = isinstance(requests_, Sequence) and not isinstance(requests_, str | bytes)
        items = list(requests_) if is_list else []
        try:
            answer = self._send("POST", f"{self._id}:batchUpdate", body={"requests": items})
        finally:
            # Cấu trúc có thể đã đổi (tab mới, mã tab mới): bắt đọc lại.
            self._info_read = False
        replies = answer.get("replies", [])
        if not isinstance(replies, list) or not all(isinstance(item, dict) for item in replies):
            raise SheetsError(_MSG_BAD_DATA.format(code=200), unsure=True)
        return tuple(replies)

    # ------------------------------------------------------------- nội bộ
    def _check_call(
        self, method: str, path: str, params: Mapping[str, str], body: object
    ) -> tuple[int, bool]:
        """Lệnh có trong danh sách cố định không (kiểm TRƯỚC KHI gửi, LC-T094-13). Trả (số lần
        thử lại khi 429, là lệnh ghi); không có thì ``SheetsError`` câu cố định."""
        for name, route_method, pattern, route_params, retries, writes in _ROUTES:
            match = pattern.fullmatch(path)
            if method != route_method or match is None:
                continue
            if match.group(1) != self._id or dict(params) != route_params:
                break
            if name in ("info", "read"):
                valid = body is None
            elif name == "update":
                valid = _valid_update_body(body)
            elif name == "append":
                valid = _valid_append_body(body)
            else:
                requests_ = body.get("requests") if _keys(body, {"requests"}) else None
                if not self._info_read:
                    raise SheetsError(_MSG_NO_INFO)
                valid = (
                    isinstance(requests_, list)
                    and 1 <= len(requests_) <= MAX_STRUCTURE_REQUESTS
                    and all(
                        _valid_structure_request(item, self._plan_sheet_id) for item in requests_
                    )
                )
            if valid:
                return retries, writes
            break
        raise SheetsError(_MSG_BLOCKED)

    def _access_token(self) -> str:
        """Mã truy cập (chỉ trong bộ nhớ). Hết hạn thì xin lại qua ``_TokenRequest``."""
        credentials = self._account.credentials
        if not credentials.valid:
            try:
                credentials.refresh(self._token_request)
            except google_exceptions.RefreshError as exc:
                raise SheetsError(_refresh_message(exc)) from None
            except google_exceptions.TransportError:
                raise SheetsError(_MSG_AUTH_NETWORK) from None
            except (
                google_exceptions.GoogleAuthError,
                ValueError,
                TypeError,
                KeyError,
                # google-auth 2.62.0: ``_parse_expiry`` ném OverflowError với ``expires_in`` quá
                # lớn; ``json.loads`` thân lồng sâu ném RecursionError (SL-T097-1). Không bắt
                # ``Exception``: lỗi của bộ chặn mạng trong test phải lọt ra được.
                OverflowError,
                RecursionError,
            ):
                raise SheetsError(_MSG_AUTH) from None
        token = credentials.token
        if not isinstance(token, str) or not _TOKEN.fullmatch(token):
            raise SheetsError(_MSG_AUTH)
        return token

    def _send(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, str] | None = None,
        body: object = None,
    ) -> dict[str, Any]:
        params = dict(params or {})
        retries, writes = self._check_call(method, path, params, body)
        token = self._access_token()
        for attempt in range(retries + 1):
            status, data = self._call(method, path, params, body, token, writes)
            if status == 429 and attempt < retries:
                delay = _RETRY_DELAYS[min(attempt, len(_RETRY_DELAYS) - 1)]
                self._sleep(delay + random.uniform(0, 0.5))
                continue
            return self._answer(status, data, writes)
        raise AssertionError("unreachable")  # pragma: no cover

    def _call(
        self,
        method: str,
        path: str,
        params: dict[str, str],
        body: object,
        token: str,
        writes: bool,
    ) -> tuple[int, bytes]:
        try:
            response = self._session.request(
                method,
                SPREADSHEETS_URL + path,
                params=params or None,
                json=body,
                headers={"Accept": "application/json"},
                timeout=self.timeout,
                allow_redirects=False,
                stream=True,
                auth=_Bearer(token),
                hooks={"response": [_refuse_redirect]},
            )
        except _Redirected as exc:
            # 3xx (có hay không có Location): không đọc thân, không đi theo. Lệnh ghi có thể đã
            # chạy trên Google: ``unsure`` theo loại lệnh (SL-T097-2).
            raise SheetsError(
                _MSG_REDIRECT.format(code=exc.status), status_code=exc.status, unsure=writes
            ) from None
        except requests.exceptions.TooManyRedirects as exc:
            # Phiên có max_redirects = 0: requests ném lỗi này cho mọi câu trả lời 3xx (kể cả khi
            # không đi theo). Không có lệnh nào được gửi tới địa chỉ mới.
            code = _close_and_status(exc)
            raise SheetsError(
                _MSG_REDIRECT.format(code=code or "3xx"), status_code=code, unsure=writes
            ) from None
        except requests.exceptions.SSLError:
            raise SheetsError(_MSG_SSL, unsure=writes) from None
        except requests.exceptions.Timeout:
            raise SheetsError(_MSG_TIMEOUT.format(timeout=self.timeout), unsure=writes) from None
        except requests.exceptions.ConnectionError:
            raise SheetsError(_MSG_CONNECTION, unsure=writes) from None
        except (requests.RequestException, OSError) as exc:
            raise SheetsError(_MSG_NETWORK.format(kind=type(exc).__name__), unsure=writes) from None
        status = response.status_code
        try:
            if 300 <= status < 400:  # phòng thêm (móc đã chặn mọi 3xx trước khi tới đây)
                raise SheetsError(
                    _MSG_REDIRECT.format(code=status), status_code=status, unsure=writes
                )
            return status, _read_limited(response, MAX_RESPONSE_BYTES)
        except _TooLarge:
            raise SheetsError(_MSG_TOO_BIG, status_code=status, unsure=writes) from None
        except (requests.RequestException, OSError):
            raise SheetsError(_MSG_CONNECTION, status_code=status, unsure=writes) from None
        finally:
            response.close()

    @staticmethod
    def _answer(status: int, data: bytes, writes: bool) -> dict[str, Any]:
        if status >= 500:
            raise SheetsError(_MSG_SERVER.format(code=status), status_code=status, unsure=writes)
        if status >= 400:
            message = _MSG_BY_STATUS.get(status, _MSG_REJECTED.format(code=status))
            raise SheetsError(message, status_code=status)
        if status != 200:
            raise SheetsError(_MSG_BAD_DATA.format(code=status), status_code=status, unsure=writes)
        try:
            answer = json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, ValueError, RecursionError):
            raise SheetsError(
                _MSG_BAD_DATA.format(code=status), status_code=status, unsure=writes
            ) from None
        if not isinstance(answer, dict):
            raise SheetsError(_MSG_BAD_DATA.format(code=status), status_code=status, unsure=writes)
        return answer


def _is_read_value(value: object) -> bool:
    if isinstance(value, bool | str):
        return True
    if isinstance(value, int):
        return -_SAFE_INT <= value <= _SAFE_INT
    return isinstance(value, float) and math.isfinite(value)


def _refresh_message(exc: Exception) -> str:
    """Câu cố định cho lỗi xin mã: chỉ đọc mã lỗi OAuth dạng ASCII, không chép mô tả."""
    details = exc.args[1] if len(exc.args) > 1 else None
    code = details.get("error") if isinstance(details, dict) else None
    if code == "invalid_grant":
        return _MSG_AUTH_GRANT
    if any(isinstance(arg, google_exceptions.TransportError) for arg in exc.args):
        return _MSG_AUTH_NETWORK
    return _MSG_AUTH
