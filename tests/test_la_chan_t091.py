"""Lá Chắn T-091 (rút gọn, W2, W3): dạng lọt thêm của SL-T091-1.

- **SL-T091-1, dạng Lá Chắn thêm** (Thấp): ngoài ``charset`` khác UTF-8 Soi Lỗi đã nêu, website
  **không khai** bảng mã (không có ``Content-Type``, hay kiểu không phải ``application/json`` như
  ``application/octet-stream``, ``application/problem+json``) mà trả JSON UTF-16, UTF-32 (có hay
  không có BOM) thì ``requests`` tự đoán bảng mã (``guess_json_utf``, RFC 4627) rồi giải mã
  đúng; byte không có chuỗi ASCII ``\\ud8`` nên ``_json`` không đi qua dữ liệu, surrogate lẻ lọt
  ra. Cách sửa phải bịt cả dạng này (ví dụ luôn gọi ``_without_lone_surrogates``); chỉ dò trên
  ``response.text`` thì chưa chắc (``text`` đoán bảng mã theo cách khác ``json()``).

Không gọi mạng: dựng thẳng ``requests.Response`` với ``encoding`` đặt như ``HTTPAdapter`` của
``requests`` (``get_encoding_from_headers``).
"""

from __future__ import annotations

import json

import pytest
import requests
from requests.structures import CaseInsensitiveDict
from requests.utils import get_encoding_from_headers

from seo_app.wordpress import WordPressError
from seo_app.wordpress.client import WordPressClient

SURROGATE = chr(0xD800)
ROOT = {"name": "Site " + SURROGATE, "home": "https://example.com", "namespaces": ["wp/v2"]}


def _response(body: bytes, headers: dict[str, str]) -> requests.Response:
    response = requests.Response()
    response.status_code = 200
    response._content = body
    response.headers = CaseInsensitiveDict(headers)
    response.encoding = get_encoding_from_headers(response.headers)  # như HTTPAdapter
    return response


def _no_surrogate(text: str) -> bool:
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


@pytest.mark.parametrize(
    "encoding", ["utf-16-le", "utf-16-be", "utf-32-le", "utf-32-be", "utf-16", "utf-32"]
)
@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"Content-Type": "application/octet-stream"},
        {"Content-Type": "application/problem+json"},
    ],
    ids=["khong-content-type", "octet-stream", "problem-json"],
)
def test_sl_t091_1_khong_khai_bang_ma_van_khong_lot_surrogate(encoding, headers):
    data = WordPressClient._json(_response(json.dumps(ROOT).encode(encoding), headers))
    assert _no_surrogate(data["name"])


@pytest.mark.parametrize(
    "headers",
    [{}, {"Content-Type": "application/json"}, {"Content-Type": "application/json; charset=UTF-8"}],
    ids=["khong-content-type", "json", "json-utf8"],
)
def test_sl_t091_1_doi_chung_utf8_khong_khai_hay_co_khai_deu_sach(headers):
    data = WordPressClient._json(_response(json.dumps(ROOT).encode(), headers))
    assert data["name"] == "Site " + chr(0xFFFD)


@pytest.mark.parametrize("encoding", ["utf-16-le", "utf-16", "utf-32"])
def test_sl_t091_1_doi_chung_khai_json_khong_charset_la_cau_co_dinh(encoding):
    """Khai ``application/json`` (không ``charset``): requests giải mã theo UTF-8 nên JSON UTF-16,
    UTF-32 hỏng; client báo câu cố định (không lọt surrogate, không lỗi lạ)."""
    response = _response(json.dumps(ROOT).encode(encoding), {"Content-Type": "application/json"})
    with pytest.raises(WordPressError, match="không trả về dữ liệu JSON đọc được"):
        WordPressClient._json(response)
