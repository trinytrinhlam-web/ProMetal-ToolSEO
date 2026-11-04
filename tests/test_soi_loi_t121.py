"""Soi Lỗi T-121: client Google Search Console chỉ đọc (``seo_app/google/search_console.py``).

Ca thêm cho các trọng tâm Chỉ Huy giao: đường gọi và thân lệnh cố định, thuộc tính theo từng phần
tên miền (LC-T120-17), kiểm câu trả lời (``NaN``, số khổng lồ, ``bool``, JSON trùng khóa, tỉ lệ
dòng hỏng), lật trang ở 25.000 dòng, 429 thử lại một lần, lớp vận chuyển nhập từ ``sheets.py``
(LC-T120-18), ``load_service_account`` (hàm dùng chung). Phần lớn là ca **qua** lấp chỗ đột biến
code mà bộ test của Thợ Máy chưa bắt (báo cáo ``docs/team/reports/T-121-soi-loi.md``); lỗi mới có
``xfail(strict=True)`` mã ``SL-T121-n``.

Không gọi Google thật: ``tests/fake_google.py`` + bộ chặn mạng của ``tests/conftest.py``. Tham số
dài luôn có ``ids`` ngắn (Windows: tên ca quá dài làm pytest in cả ``os.environ``).
"""

from __future__ import annotations

import copy
import io
import json
import os
from collections import OrderedDict
from dataclasses import replace
from datetime import date, timedelta
from urllib.parse import quote

import pytest
import requests
from fake_google import (
    ACCESS_TOKEN,
    EMAIL,
    SC_SITES,
    SEARCH_CONSOLE,
    TOKEN_URL,
    FakeGoogle,
    form,
    jwt_claims,
    key_info,
    make_session,
    new_private_key,
)

from seo_app.config import Settings
from seo_app.google import search_console
from seo_app.google.search_console import (
    SHAPES,
    SearchConsoleClient,
    SearchConsoleError,
    covers_site,
    parse_property,
)
from seo_app.google.service_account import (
    SEARCH_CONSOLE_SCOPE,
    SHEETS_SCOPE,
    ServiceAccountError,
    load_service_account,
)

MOI = "LOI-MAY-CHU-GOOGLE-KHONG-DUOC-CHEP"
TODAY = date(2026, 11, 3)
DAY = "2026-10-30"
WORDPRESS = "https://suachuacuasat.com"
DOMAIN = "sc-domain:suachuacuasat.com"
PREFIX = "https://suachuacuasat.com/"
PAGE = PREFIX + "sua-cua-keo-bi-ket/"
QUERY_URL = SEARCH_CONSOLE + "sites/sc-domain%3Asuachuacuasat.com/searchAnalytics/query"
BAD_DATA = "không đúng dạng"


# ================================================================ dựng sẵn
@pytest.fixture(scope="module")
def private_key():
    return new_private_key()


@pytest.fixture
def key_file(tmp_path, private_key):
    folder = tmp_path / "bi-mat"
    folder.mkdir()
    path = folder / "du-an-thu-0123abcd.json"
    path.write_text(json.dumps(key_info(private_key)), encoding="utf-8")
    if os.name != "nt":
        path.chmod(0o600)
    return path


@pytest.fixture
def account(key_file, tmp_path):
    project = tmp_path / "du-an"
    project.mkdir()
    return load_service_account(key_file, scope=SEARCH_CONSOLE_SCOPE, project_root=project)


@pytest.fixture
def fake():
    return FakeGoogle()


@pytest.fixture
def sleeps():
    return []


def make_client(account, fake, prop=DOMAIN, **kwargs):
    options = {"session": make_session(fake), "today": lambda: TODAY, **kwargs}
    return SearchConsoleClient(account, WORDPRESS, parse_property(prop), **options)


@pytest.fixture
def client(account, fake, sleeps):
    return make_client(account, fake, sleep=sleeps.append)


def row(day=DAY, page=PAGE, *, clicks=1, impressions=10, position=3.5, **extra):
    return {
        "keys": [day, page],
        "clicks": clicks,
        "impressions": impressions,
        "ctr": 0.1,
        "position": position,
        **extra,
    }


def query_row(query, page=PAGE, **numbers):
    data = row(**numbers)
    data["keys"] = [page, query]
    return data


def answer(*rows, **extra):
    return {"rows": list(rows), "responseAggregationType": "byPage", **extra}


def good_rows(count=20):
    return [row(page=f"{PREFIX}bai-{i}/") for i in range(count)]


def sent_bodies(fake):
    return [json.loads(r.body) for r in fake.search_console_requests() if r.method == "POST"]


def assert_fixed(error, *forbidden):
    text = str(error.value)
    for item in (MOI, ACCESS_TOKEN, EMAIL, "suachuacuasat", *forbidden):
        assert item not in text
    assert error.value.__cause__ is None


# ================================================================ thuộc tính (LC-T120-17)
# Bảy ca phiếu ghi + biến thể: chữ giống chữ Latinh, dấu chấm Unicode mà IDNA coi là «.», mã %,
# IP, IPv6, tên/mật khẩu, ký tự điều khiển, tên miền con staging, tên miền cha, tên miền đảo.
PROPERTIES = {
    "evil-dinh-lien": ("sc-domain:evilsuachuacuasat.com", "không phải của website"),
    "evil-duoi": ("sc-domain:suachuacuasat.com.evil.com", "không phải của website"),
    "chu-hoa": ("sc-domain:SUACHUACUASAT.com", "sai dạng"),
    "cham-cuoi": ("sc-domain:suachuacuasat.com.", "sai dạng"),
    "ip": ("sc-domain:1.2.3.4", "sai dạng"),
    "cong-8443": ("https://suachuacuasat.com:8443/", "sai dạng"),
    "duong-con": ("https://suachuacuasat.com/blog/", "sai dạng"),
    "chu-kirin": ("sc-domain:suachuacuas" + chr(0x430) + "t.com", "sai dạng"),
    "cham-y-tuong": ("sc-domain:suachuacuasat" + chr(0x3002) + "com", "sai dạng"),
    "cham-toan-khoang": ("sc-domain:suachuacuasat" + chr(0xFF0E) + "com", "sai dạng"),
    "ma-phan-tram": ("https://suachuacuasat%2Ecom/", "sai dạng"),
    "tien-to-cham-cuoi": ("https://suachuacuasat.com./", "sai dạng"),
    "tien-to-hai-gach": ("https://suachuacuasat.com//", "sai dạng"),
    "tien-to-ip": ("https://127.0.0.1/", "sai dạng"),
    "tien-to-ipv6": ("https://[::1]/", "sai dạng"),
    "tien-to-ten-mat-khau": ("https://a:b@suachuacuasat.com/", "sai dạng"),
    "tien-to-tab": ("https://suachuacuasat.com\t/", "sai dạng"),
    "ten-mien-nul": ("sc-domain:suachuacuasat.com" + chr(0), "sai dạng"),
    "ten-mien-con-staging": ("sc-domain:staging-m.suachuacuasat.com", "không phải của website"),
    "tien-to-www": ("https://www.suachuacuasat.com/", "không phải của website"),
    "ten-mien-dao": ("sc-domain:com.suachuacuasat", "không phải của website"),
    "ten-mien-duoi-chung": ("sc-domain:cuasat.com", "không phải của website"),
    "ten-mien-cha-quoc-gia": ("sc-domain:com.vn", "không phải của website"),
}


@pytest.mark.parametrize("name", list(PROPERTIES))
def test_thuoc_tinh_phieu_va_bien_the_bi_tu_choi_truoc_khi_doc_file_khoa(tmp_path, fake, name):
    site_url, match = PROPERTIES[name]
    settings = Settings(
        wordpress_url=WORDPRESS,
        gsc_site_url=site_url,
        google_service_account_file=tmp_path / "khong-co.json",  # đọc file thì ra lỗi khác
    )
    with pytest.raises(SearchConsoleError, match=match) as error:
        SearchConsoleClient.from_settings(settings, session=make_session(fake))
    assert_fixed(error, "evil", "staging-m", "cuasat")
    assert fake.requests == []


@pytest.mark.parametrize(
    "name", [name for name, (_url, match) in PROPERTIES.items() if match != "sai dạng"]
)
def test_thuoc_tinh_dung_dang_nhung_khong_phu_website_client_tu_choi(account, fake, name):
    prop = parse_property(PROPERTIES[name][0])
    assert covers_site(prop, WORDPRESS) is False
    with pytest.raises(SearchConsoleError, match="không phải của website"):
        SearchConsoleClient(account, WORDPRESS, prop, session=make_session(fake))
    assert fake.requests == []


@pytest.mark.parametrize(
    ("wordpress", "covers"),
    [
        ("https://blog.suachuacuasat.com", True),  # tên miền con: thuộc tính tên miền phủ
        ("https://SuaChuaCuaSat.com/", True),
        ("https://suachuacuasat.com:443/", True),
        ("https://suachuacuasat.com.", False),  # dấu chấm cuối: WORDPRESS_URL không dùng được
        ("https://xsuachuacuasat.com", False),
        ("https://suachuacuasat.co", False),
    ],
    ids=["ten-mien-con", "chu-hoa", "cong-443", "cham-cuoi", "dinh-lien", "thieu-chu"],
)
def test_thuoc_tinh_ten_mien_phu_theo_ten_may_cua_wordpress(wordpress, covers):
    assert covers_site(parse_property(DOMAIN), wordpress) is covers


@pytest.mark.parametrize(
    "wordpress",
    ["https://SuaChuaCuaSat.com", "HTTPS://suachuacuasat.com/", "https://SUACHUACUASAT.COM:443"],
    ids=["ten-may-hoa", "giao-thuc-hoa", "hoa-cong-443"],
)
def test_wordpress_url_viet_hoa_van_nhan_dong_cua_google(account, fake, wordpress):
    """``WORDPRESS_URL`` viết hoa (``load_settings`` không hạ chữ; xem SL-T123-2 ở lõi T-123): bộ
    lọc gửi Google viết thường, dòng ``https://suachuacuasat.com/…`` của Google vẫn được nhận."""
    client = SearchConsoleClient(
        account, wordpress, parse_property(DOMAIN), session=make_session(fake), today=lambda: TODAY
    )
    fake.on("POST", QUERY_URL, answer(*good_rows(5)))
    result = client.fetch_day_page(date(2026, 10, 30), TODAY)
    assert result.dropped == 0 and len(result.rows) == 5
    (body,) = sent_bodies(fake)
    expression = body["dimensionFilterGroups"][0]["filters"][0]["expression"]
    assert expression == "^https://suachuacuasat\\.com/"


# ================================================================ «Tìm thuộc tính» (sites.list)
@pytest.mark.parametrize(
    "bad",
    [chr(10), chr(13), chr(0), chr(9), chr(0x7F), chr(0x200B), chr(0x202E), " "],
    ids=["xuong-dong", "ve-dau-dong", "nul", "tab", "del", "zero-width", "dao-chieu", "cach"],
)
def test_danh_sach_thuoc_tinh_bo_dia_chi_co_ky_tu_dieu_khien_hay_vo_hinh(fake, client, bad):
    """``siteUrl`` từ Google là chữ chưa tin cậy: ký tự điều khiển, vô hình, đảo chiều chữ hay
    khoảng trắng thì bỏ mục (đếm ``skipped``), không giữ lại để giao diện hiện."""
    entries = [
        {"siteUrl": DOMAIN, "permissionLevel": "siteRestrictedUser"},
        {"siteUrl": "https://khac.example/" + bad + "x/", "permissionLevel": "siteOwner"},
        {"siteUrl": "sc-domain:khac" + bad + ".example", "permissionLevel": "siteOwner"},
    ]
    fake.on("GET", SC_SITES, {"siteEntry": entries})
    result = client.list_sites()
    assert [entry.site_url for entry in result.entries] == [DOMAIN]
    assert result.skipped == 2


def test_danh_sach_thuoc_tinh_chu_dang_markdown_khong_chon_duoc(fake, client):
    """Chữ ASCII nhìn thấy được nhưng không đúng dạng thuộc tính (``[x](…)``, ``<b>``) vẫn được
    có thể được giữ để hiện «không dùng được»: khi đó không bao giờ ``usable``; nơi hiện phải hiện
    chữ thuần (T-124)."""
    odd = ["[bam-vao](https://evil.example/)", "<b>sc-domain:suachuacuasat.com</b>"]
    entries = [{"siteUrl": url, "permissionLevel": "siteOwner"} for url in odd]
    fake.on("GET", SC_SITES, {"siteEntry": entries})
    result = client.list_sites()
    assert len(result.entries) + result.skipped == 2  # giữ để hiện «không dùng được», hoặc bỏ
    for entry in result.entries:
        assert entry.kind == "" and entry.covers is False and entry.usable is False


def test_danh_sach_thuoc_tinh_429_thu_lai_mot_lan(fake, client, sleeps):
    answers = iter([(429, {"error": {"code": 429, "message": MOI}}, {}), {"siteEntry": []}])
    fake.on("GET", SC_SITES, lambda _r: next(answers))
    assert client.list_sites().entries == ()
    assert len(fake.search_console_requests()) == 2 and len(sleeps) == 1


def test_danh_sach_thuoc_tinh_429_hai_lan_bao_loi(fake, client, sleeps):
    fake.on("GET", SC_SITES, (429, {"error": {"code": 429, "message": MOI}}, {}))
    with pytest.raises(SearchConsoleError, match="15 phút") as error:
        client.list_sites()
    assert_fixed(error)
    assert len(fake.search_console_requests()) == 2 and len(sleeps) == 1


# ================================================================ thân lệnh dựng tay (LC-T120-2)
_DROP = object()


def _set(**changes):
    def change(body):
        for key, value in changes.items():
            if value is _DROP:
                body.pop(key)
            else:
                body[key] = value
        return body

    return change


def _filter(**changes):
    def change(body):
        body["dimensionFilterGroups"][0]["filters"][0].update(changes)
        return body

    return change


class _Text(str):
    """Lớp con của ``str`` nói dối khi so sánh, in ra: ``json`` vẫn gửi đúng nội dung thật."""

    def __eq__(self, other):
        return True

    __hash__ = str.__hash__

    def __str__(self):
        return "evil"


EXTRA_BAD_BODIES = {
    "startRow-True": _set(startRow=True),
    "rowLimit-True": _set(rowLimit=True),
    "type-WEB": _set(type="WEB"),
    "type-discover": _set(type="discover"),
    "type-news": _set(type="news"),
    "dataState-ALL": _set(dataState="ALL"),
    "aggregation-BYPAGE": _set(aggregationType="BYPAGE"),
    "dimensions-device": _set(dimensions=["date", "page", "device"]),
    "ngay-la-date": _set(startDate=date(2026, 10, 30)),
    "ngay-co-gio": _set(startDate="2026-10-30T00:00:00"),
    "ngay-khoang-trang": _set(startDate=" 2026-10-30"),
    "ngay-so-toan-khoang": _set(startDate="２０２６-10-30"),
    "loc-cham-khong-thoat": _filter(expression="^https://suachuacuasat.com/"),
    "loc-thieu-gach-cuoi": _filter(expression="^https://suachuacuasat\\.com"),
    "loc-khong-mo-dau": _filter(expression="https://suachuacuasat\\.com/"),
    "loc-excluding": _filter(operator="excludingRegex"),
    "loc-equals": _filter(operator="equals"),
    "loc-nan": _filter(expression=float("nan")),
    "loc-chu-noi-doi": _filter(expression=_Text("^https://evil\\.example/")),
    "khoa-so": lambda b: {**b, 0: "x"},
    "khoa-so-thay-khoa-chu": lambda b: {**{k: v for k, v in b.items() if k != "type"}, 1: "web"},
}


@pytest.mark.parametrize("name", list(EXTRA_BAD_BODIES))
def test_than_dung_tay_kieu_la_khong_gui(fake, client, name):
    good = client._body(SHAPES["day_page"], date(2026, 10, 30), TODAY, 0)
    body = EXTRA_BAD_BODIES[name](copy.deepcopy(good))
    with pytest.raises(SearchConsoleError, match="không nằm trong danh sách") as error:
        client._send("POST", QUERY_URL, body)
    assert_fixed(error)
    assert fake.requests == []


@pytest.mark.parametrize(
    "build",
    [
        lambda b: OrderedDict(reversed(list(b.items()))),
        lambda b: {**b, "dimensions": tuple(b["dimensions"])},
        lambda b: {key: _Text(v) if isinstance(v, str) else v for key, v in b.items()},
    ],
    ids=["ordered-dict-dao", "tuple", "lop-con-str"],
)
def test_than_khac_kieu_nhung_cung_noi_dung_gui_dung_nguyen_van(fake, client, build):
    """Kiểu khác (``OrderedDict`` đảo thứ tự, ``tuple``, lớp con ``str`` nói dối khi so) mà nội
    dung JSON y hệt khuôn thì được gửi, và cái **gửi đi** đúng y khuôn (không lọt nội dung khác)."""
    fake.on("POST", QUERY_URL, answer())
    good = client._body(SHAPES["day_page"], date(2026, 10, 30), TODAY, 0)
    client._send("POST", QUERY_URL, build(copy.deepcopy(good)))
    assert sent_bodies(fake) == [good]


@pytest.mark.parametrize(
    ("method", "url"),
    [
        ("get", SC_SITES),
        ("HEAD", SC_SITES),
        ("OPTIONS", SC_SITES),
        ("GET", SC_SITES + "/"),
        ("GET", "https://www.googleapis.com:443/webmasters/v3/sites"),
        ("GET", "https://WWW.googleapis.com/webmasters/v3/sites"),
        ("GET", "https://www.googleapis.com@evil.example/webmasters/v3/sites"),
        ("GET", "https://www.googleapis.com.evil.example/webmasters/v3/sites"),
        ("GET", SEARCH_CONSOLE + "sites/" + quote(DOMAIN, safe="")),
        ("GET", SEARCH_CONSOLE + "sites/" + quote(DOMAIN, safe="") + "/sitemaps"),
        ("POST", TOKEN_URL),
    ],
    ids=[
        "get-thuong",
        "head",
        "options",
        "gach-cuoi",
        "cong-443",
        "chu-hoa",
        "a-cong",
        "duoi-evil",
        "sites-get",
        "sitemaps",
        "token",
    ],
)
def test_lenh_sites_bien_the_khong_gui(fake, client, method, url):
    with pytest.raises(SearchConsoleError, match="không nằm trong danh sách") as error:
        client._send(method, url, None)
    assert_fixed(error, "evil")
    assert fake.requests == []


@pytest.mark.parametrize("method", ["PUT", "DELETE", "GET", "post"])
def test_lenh_query_phuong_thuc_khac_khong_gui(fake, client, method):
    body = client._body(SHAPES["day_page"], date(2026, 10, 30), TODAY, 0)
    with pytest.raises(SearchConsoleError, match="không nằm trong danh sách"):
        client._send(method, QUERY_URL, body)
    assert fake.requests == []


# ================================================================ đọc JSON (LC-T120-5)
def _raw_answer(*rows, swap=None):
    """Câu trả lời dạng byte; ``swap`` thay chuỗi đánh dấu bằng chữ JSON nguyên văn (``NaN``,
    ``1e400``…) mà ``json.dumps`` của Python không tự viết ra được."""
    text = json.dumps(answer(*rows))
    for marker, raw in (swap or {}).items():
        text = text.replace(json.dumps(marker), raw)
    return text.encode("utf-8")


NAN_PLACES = {
    "click-nan": ("clicks", "NaN"),
    "hien-thi-infinity": ("impressions", "Infinity"),
    "vi-tri-am-infinity": ("position", "-Infinity"),
    "ctr-nan": ("ctr", "NaN"),
    "truong-la-nan": ("la", "NaN"),
}


@pytest.mark.parametrize("name", list(NAN_PLACES))
def test_nan_mot_dong_giua_20_dong_dung_bo_ca_cau_tra_loi(fake, client, name):
    """LC-T120-5: chặn ``NaN``/``Infinity`` ngay ở bộ đọc JSON (``parse_constant``). Một dòng
    ``NaN`` giữa 20 dòng đúng (≈ 5%, dưới ngưỡng 10%) vẫn phải bỏ **cả** câu trả lời; chỉ bỏ dòng
    đó là bộ đọc JSON đã để ``NaN`` lọt qua."""
    field, raw = NAN_PLACES[name]
    bad = row(page=PREFIX + "nan/", **{field: "__SO__"})
    fake.on("POST", QUERY_URL, (200, _raw_answer(*good_rows(), bad, swap={"__SO__": raw}), {}))
    with pytest.raises(SearchConsoleError, match=BAD_DATA) as error:
        client.fetch_day_page(date(2026, 10, 30), TODAY)
    assert_fixed(error)


def test_nan_trong_metadata_bo_ca_cau_tra_loi(fake, client):
    data = answer(*good_rows(), metadata={"first_incomplete_date": "__SO__"})
    raw = json.dumps(data).replace('"__SO__"', "NaN").encode()
    fake.on("POST", QUERY_URL, (200, raw, {}))
    with pytest.raises(SearchConsoleError, match=BAD_DATA):
        client.fetch_day_page(date(2026, 10, 30), TODAY)


HUGE = {
    "click-10-mu-400": ("clicks", "1" + "0" * 400),
    "hien-thi-10-mu-400": ("impressions", "1" + "0" * 400),
    "vi-tri-10-mu-400": ("position", "1" + "0" * 400),
    "ctr-10-mu-400": ("ctr", "1" + "0" * 400),
    "vi-tri-am-10-mu-400": ("position", "-1" + "0" * 400),
    "click-1e400": ("clicks", "1e400"),
    "vi-tri-1e400": ("position", "1e400"),
    "ctr-am-1e400": ("ctr", "-1e400"),
}


@pytest.mark.parametrize("name", list(HUGE))
def test_so_khong_lo_chi_bo_dong_khong_sap(fake, client, name):
    """Số nguyên 401 chữ số (``float()`` của nó ném ``OverflowError``) và ``1e400`` (JSON đọc ra
    ``inf``, ``parse_constant`` không thấy): chỉ bỏ dòng đó, đếm, không sập."""
    field, raw = HUGE[name]
    bad = row(page=PREFIX + "khong-lo/", **{field: "__SO__"})
    fake.on("POST", QUERY_URL, (200, _raw_answer(*good_rows(), bad, swap={"__SO__": raw}), {}))
    result = client.fetch_day_page(date(2026, 10, 30), TODAY)
    assert result.dropped == 1 and len(result.rows) == 20


@pytest.mark.parametrize(
    "value", [-0.0, 0.0, 2.0, 1e-400], ids=["am-khong", "khong-thuc", "hai-thuc", "duoi-nho"]
)
def test_so_thuc_nguyen_doc_thanh_so_nguyen(fake, client, value):
    fake.on("POST", QUERY_URL, answer(row(clicks=value, impressions=2)))
    (shown,) = client.fetch_day_page(date(2026, 10, 30), TODAY).rows
    assert type(shown.clicks) is int and shown.clicks == int(value)


def test_trung_khoa_trong_metadata_bo_ca_cau_tra_loi(fake, client):
    raw = json.dumps(answer(*good_rows())).encode()[:-1] + (
        b', "metadata": {"first_incomplete_date": "2026-11-01", '
        b'"first_incomplete_date": "2026-10-30"}}'
    )
    fake.on("POST", QUERY_URL, (200, raw, {}))
    with pytest.raises(SearchConsoleError, match=BAD_DATA):
        client.fetch_day_page(date(2026, 10, 30), TODAY)


@pytest.mark.parametrize(
    "key",
    ["2026-10-30" + chr(10), "２０２６-10-30", "2026-1O-30", "+2026-10-30", "2026-10-30Z"],
    ids=["xuong-dong", "so-toan-khoang", "chu-o", "dau-cong", "chu-z"],
)
def test_ngay_la_trong_dong_bi_bo(fake, client, key):
    fake.on("POST", QUERY_URL, answer(*good_rows(), row(day=key, page=PREFIX + "ngay-la/")))
    result = client.fetch_day_page(date(2026, 10, 30), TODAY)
    assert result.dropped == 1 and len(result.rows) == 20


def test_phan_thang_dai_khong_cuu_dia_chi_qua_2000_ky_tu(fake, client):
    """Trang ≤ 2.000 ký tự tính trên chữ Google trả (thiết kế 2.4), trước khi bỏ ``#…``: phần
    ``#`` dài không làm địa chỉ quá dài lọt qua."""
    long_key = PAGE + "#" + "a" * 2000
    fake.on("POST", QUERY_URL, answer(*good_rows(), row(page=long_key)))
    result = client.fetch_day_page(date(2026, 10, 30), TODAY)
    assert result.dropped == 1 and PAGE not in {r.page for r in result.rows}


# ================================================================ lật trang (thiết kế 2.5)
def _page_bytes(count, *, query=False, tag="p"):
    if query:
        rows = [query_row(f"tu khoa {tag}{i}") for i in range(count)]
    else:
        rows = [row(page=f"{PREFIX}{tag}{i}/") for i in range(count)]
    return json.dumps(answer(*rows)).encode()


def test_lat_trang_q1_dung_tran_8_trang_200000_dong(fake, client):
    """Q1 trả đủ 25.000 dòng mọi trang: dừng ở trang thứ 8 (``startRow`` 175.000), báo «có thể
    thiếu dòng», không gửi lệnh thứ 9."""
    pages = iter([_page_bytes(25_000, tag=f"t{n}-") for n in range(8)])
    fake.on("POST", QUERY_URL, lambda _r: (200, next(pages), {}))
    result = client.fetch_day_page(date(2026, 10, 30), TODAY)
    assert [b["startRow"] for b in sent_bodies(fake)] == list(range(0, 200_000, 25_000))
    assert result.truncated is True and len(result.rows) == 200_000
    assert client.request_count == 8


def test_lat_trang_429_giua_chung_thu_lai_roi_lay_tiep(fake, client, sleeps):
    answers = iter(
        [
            (200, _page_bytes(5_000, query=True, tag="a"), {}),
            (429, {"error": {"code": 429, "message": MOI}}, {}),
            (200, _page_bytes(10, query=True, tag="b"), {}),
        ]
    )
    fake.on("POST", QUERY_URL, lambda _r: next(answers))
    result = client.fetch_page_query(TODAY - timedelta(days=27), TODAY)
    assert len(result.rows) == 5_010 and result.truncated is False
    assert [b["startRow"] for b in sent_bodies(fake)] == [0, 5_000, 5_000]
    assert len(sleeps) == 1


def test_metadata_trang_dau_khong_bi_trang_sau_xoa(fake, client):
    """Q1 đọc ``metadata`` ở trang đầu; trang sau không có ``metadata`` không xóa ngày đầu tiên còn
    số tạm đã biết (xóa thì T-124 coi 3 ngày cuối là tạm: an toàn nhưng thừa)."""
    first = json.loads(_page_bytes(25_000))
    first["metadata"] = {"first_incomplete_date": "2026-11-01"}
    answers = iter([(200, json.dumps(first).encode(), {}), (200, _page_bytes(10, tag="q"), {})])
    fake.on("POST", QUERY_URL, lambda _r: next(answers))
    result = client.fetch_day_page(date(2026, 10, 30), TODAY)
    assert (result.first_incomplete_date, result.metadata) == (date(2026, 11, 1), "ok")
    assert len(result.rows) == 25_010


def test_lat_trang_loi_o_trang_sau_khong_tra_nua_voi(fake, client):
    """Trang 2 lỗi: không trả kết quả nửa vời (T-124 giữ các đoạn đã ghi, đoạn này lấy lại)."""
    answers = iter(
        [(200, _page_bytes(5_000, query=True), {}), (500, {"error": {"message": MOI}}, {})]
    )
    fake.on("POST", QUERY_URL, lambda _r: next(answers))
    with pytest.raises(SearchConsoleError, match="đang lỗi") as error:
        client.fetch_page_query(TODAY - timedelta(days=27), TODAY)
    assert_fixed(error)


def test_trang_sau_nhieu_hon_row_limit_bo_ca(fake, client):
    answers = iter(
        [
            (200, _page_bytes(5_000, query=True, tag="a"), {}),
            (200, _page_bytes(5_001, query=True, tag="b"), {}),
        ]
    )
    fake.on("POST", QUERY_URL, lambda _r: next(answers))
    with pytest.raises(SearchConsoleError, match=BAD_DATA):
        client.fetch_page_query(TODAY - timedelta(days=27), TODAY)


# ================================================================ 429, 5xx, số lệnh (LC-T120-8)
@pytest.mark.parametrize("status", [500, 502, 503, 504])
def test_5xx_khong_thu_lai(fake, client, sleeps, status):
    fake.on("POST", QUERY_URL, (status, {"error": {"code": status, "message": MOI}}, {}))
    with pytest.raises(SearchConsoleError, match="đang lỗi") as error:
        client.fetch_days(TODAY - timedelta(days=9), TODAY)
    assert_fixed(error)
    assert len(fake.search_console_requests()) == 1 and sleeps == []


def test_429_khong_vuot_tran_so_lenh(fake, account, sleeps):
    client = make_client(account, fake, sleep=sleeps.append, max_requests=1)
    fake.on("POST", QUERY_URL, (429, {"error": {"code": 429, "message": MOI}}, {}))
    with pytest.raises(SearchConsoleError, match="Đã gửi đủ 1 lệnh"):
        client.fetch_days(TODAY - timedelta(days=9), TODAY)
    assert len(fake.search_console_requests()) == 1 == client.request_count


def test_429_retry_after_rat_lau_van_chi_cho_toi_da_2_5_giay(fake, client, sleeps):
    answers = iter([(429, {"error": {"code": 429}}, {"Retry-After": "86400"}), answer()])
    fake.on("POST", QUERY_URL, lambda _r: next(answers))
    client.fetch_days(TODAY - timedelta(days=9), TODAY)
    assert len(sleeps) == 1 and 2.0 <= sleeps[0] <= 2.5


# ================================================================ lớp vận chuyển (LC-T120-18)
class _Tripwire(io.RawIOBase):
    """Thân câu trả lời đếm số lần bị đọc (thân 3xx không được đọc)."""

    def __init__(self) -> None:
        super().__init__()
        self.reads = 0

    def readable(self) -> bool:
        return True

    def readinto(self, buffer) -> int:
        self.reads += 1
        return 0


@pytest.mark.parametrize("status", [301, 302, 303, 307, 308])
def test_query_chuyen_huong_khong_di_theo_khong_gui_lai_than(fake, client, status):
    """POST ``query`` gặp 3xx (307/308 giữ nguyên thân và phương thức khi đi theo): không đọc
    thân, không gửi lại tới ``Location``, không lộ mã truy cập ra máy khác."""
    fake.on("POST", QUERY_URL, (status, b"x" * 10, {"Location": "https://evil.example/q"}))
    trip = _Tripwire()
    original = fake.send

    def send(request, **kwargs):
        response = original(request, **kwargs)
        if 300 <= response.status_code < 400:
            response.raw = trip
        return response

    fake.send = send
    with pytest.raises(SearchConsoleError, match="chuyển hướng") as error:
        client.fetch_days(TODAY - timedelta(days=9), TODAY)
    assert_fixed(error, "evil")
    assert trip.reads == 0
    assert [r.url for r in fake.search_console_requests()] == [QUERY_URL]
    assert all("evil" not in r.url for r in fake.requests)


def test_netrc_that_khong_duoc_doc(fake, client, tmp_path, monkeypatch):
    """File ``.netrc`` thật (biến ``NETRC``) có mật khẩu cho cả hai máy chủ Google: không lệnh nào
    mang ``Authorization: Basic``; lệnh Search Console chỉ mang mã ``Bearer``."""
    netrc = tmp_path / "netrc"
    netrc.write_text(
        "machine www.googleapis.com login ten password mat-khau-netrc\n"
        "machine oauth2.googleapis.com login ten password mat-khau-netrc\n",
        encoding="utf-8",
    )
    if os.name != "nt":
        netrc.chmod(0o600)
    monkeypatch.setenv("NETRC", str(netrc))
    assert requests.utils.get_netrc_auth(SC_SITES) == ("ten", "mat-khau-netrc")  # đối chứng
    fake.on("GET", SC_SITES, {"siteEntry": []})
    fake.on("POST", QUERY_URL, answer())
    client.list_sites()
    client.fetch_days(TODAY - timedelta(days=9), TODAY)
    for request in fake.requests:
        assert not request.headers.get("Authorization", "").startswith("Basic")
    for request in fake.search_console_requests():
        assert request.headers["Authorization"] == f"Bearer {ACCESS_TOKEN}"


@pytest.mark.parametrize(
    ("timeout", "expected"),
    [(7, 7.0), (0.5, 0.5), (0, 30.0), (-5, 30.0), (float("nan"), 30.0), (float("inf"), 30.0)],
    ids=["7", "nua-giay", "khong", "am", "nan", "vo-cung"],
)
def test_gio_cho_truyen_dung_ca_lenh_xin_ma(fake, account, timeout, expected):
    client = make_client(account, fake, timeout=timeout)
    fake.on("GET", SC_SITES, {"siteEntry": []})
    client.list_sites()
    assert client.timeout == expected
    assert [kwargs["timeout"] for _request, kwargs in fake.calls] == [expected, expected]


@pytest.mark.parametrize(
    ("size", "ok"),
    [(256 * 1024, True), (256 * 1024 + 1, False)],
    ids=["dung-256-kb", "qua-1-byte"],
)
def test_gioi_han_256_kb_cua_sites_dung_bien(fake, client, size, ok):
    head = b'{"siteEntry": [], "pad": "'
    tail = b'"}'
    body = head + b"y" * (size - len(head) - len(tail)) + tail
    assert len(body) == size
    fake.on("GET", SC_SITES, (200, body, {}))
    if ok:
        assert client.list_sites().entries == ()
    else:
        with pytest.raises(SearchConsoleError, match="lớn bất thường"):
            client.list_sites()


def test_content_length_khai_lon_bo_truoc_khi_doc(fake, client):
    fake.on("GET", SC_SITES, (200, b'{"siteEntry": []}', {"Content-Length": str(10**12)}))
    with pytest.raises(SearchConsoleError, match="lớn bất thường"):
        client.list_sites()


# ================================================================ «Kiểm tra» (khuôn hosts)
def _host_row(page, impressions=1):
    return {"keys": [page], "clicks": 0, "impressions": impressions, "position": 4.0}


def test_kiem_tra_du_200_dong_bao_co_the_thieu(fake, client):
    rows = [_host_row(f"{PREFIX}p{i}/") for i in range(200)]
    fake.on("POST", QUERY_URL, answer(*rows))
    result = client.check_hosts(date(2026, 10, 7), TODAY)
    assert result.truncated is True and result.inside_impressions == 200


def test_kiem_tra_qua_10_phan_tram_dong_sai_bo_ca(fake, client):
    rows = [_host_row(f"{PREFIX}p{i}/") for i in range(17)]
    rows += [{**_host_row(PAGE), "impressions": True}] * 3  # 3/20 = 15%
    fake.on("POST", QUERY_URL, answer(*rows))
    with pytest.raises(SearchConsoleError, match=BAD_DATA):
        client.check_hosts(date(2026, 10, 7), TODAY)


def test_kiem_tra_dia_chi_qua_dai_bi_bo(fake, client):
    rows = [_host_row(f"{PREFIX}p{i}/") for i in range(20)]
    rows.append(_host_row("https://khac.example/" + "a" * 2000, 50))
    fake.on("POST", QUERY_URL, answer(*rows))
    result = client.check_hosts(date(2026, 10, 7), TODAY)
    assert result.dropped == 1 and result.outside_impressions == 0 and result.hosts == ()


def test_kiem_tra_ten_may_ngoai_website_chu_thuong_dung_dang(fake, client):
    rows = [_host_row(f"{PREFIX}p{i}/") for i in range(10)]
    rows += [
        _host_row("https://WWW.Khac.Example/a/", 4),
        _host_row("https://khac.example./b/", 3),  # dấu chấm cuối: đếm, không hiện tên
        _host_row("https://[::1]/c/", 2),
        _host_row("https://[::1/d/", 1),  # IPv6 hỏng: urlsplit ném ValueError
    ]
    fake.on("POST", QUERY_URL, answer(*rows))
    result = client.check_hosts(date(2026, 10, 7), TODAY)
    assert result.outside_impressions == 10
    assert result.hosts == (("www.khac.example", 4),)


# ================================================================ load_service_account (dùng chung)
class _Scope(str):
    pass


@pytest.mark.parametrize(
    "scope",
    [
        _Scope(SEARCH_CONSOLE_SCOPE),
        SEARCH_CONSOLE_SCOPE.replace("https", "http"),
        SEARCH_CONSOLE_SCOPE + "/",
        SEARCH_CONSOLE_SCOPE.replace(".readonly", ""),
        "webmasters.readonly",
        frozenset({SEARCH_CONSOLE_SCOPE}),
    ],
    ids=["lop-con-str", "http", "gach-cuoi", "doc-ghi", "ten-ngan", "frozenset"],
)
def test_pham_vi_bien_the_bi_tu_choi_truoc_khi_doc_file(tmp_path, scope):
    with pytest.raises(ServiceAccountError, match="Phạm vi quyền Google") as error:
        load_service_account(tmp_path / "khong-co.json", scope=scope)
    assert error.value.__cause__ is None


@pytest.mark.parametrize(
    "scopes",
    [
        [SEARCH_CONSOLE_SCOPE, SHEETS_SCOPE],
        [SEARCH_CONSOLE_SCOPE, "https://www.googleapis.com/auth/webmasters"],
        [SEARCH_CONSOLE_SCOPE, "https://www.googleapis.com/auth/cloud-platform"],
        [SEARCH_CONSOLE_SCOPE, SEARCH_CONSOLE_SCOPE],
    ],
    ids=["them-sheets", "them-doc-ghi", "them-cloud-platform", "lap-lai"],
)
def test_client_tu_choi_tai_khoan_co_them_pham_vi(account, fake, scopes):
    """LC-T120-16: đối tượng xác thực có **đúng một** phạm vi chỉ đọc. Có thêm phạm vi khác (kể
    cả có ``webmasters.readonly`` trong đó) thì client không nhận, không gửi lệnh nào."""
    wide = replace(account, credentials=account.credentials.with_scopes(scopes))
    with pytest.raises(SearchConsoleError, match="quyền chỉ đọc Search Console") as error:
        SearchConsoleClient(wide, WORDPRESS, parse_property(DOMAIN), session=make_session(fake))
    assert_fixed(error)
    assert fake.requests == []


def test_hai_tai_khoan_hai_ma_rieng(fake, key_file, tmp_path):
    """Tài khoản Sheets và tài khoản Search Console nạp từ cùng file khóa: lệnh xin mã của client
    Search Console ký đúng phạm vi chỉ đọc; tài khoản Sheets không bị đổi phạm vi theo."""
    project = tmp_path / "du-an-2"
    project.mkdir()
    sheets_account = load_service_account(key_file, project_root=project)
    sc_account = load_service_account(key_file, scope=SEARCH_CONSOLE_SCOPE, project_root=project)
    client = make_client(sc_account, fake)
    fake.on("GET", SC_SITES, {"siteEntry": []})
    client.list_sites()
    (token_request,) = fake.token_requests()
    assert jwt_claims(form(token_request)["assertion"])["scope"] == SEARCH_CONSOLE_SCOPE
    assert sheets_account.credentials.token is None
    assert list(sheets_account.credentials.scopes) != list(sc_account.credentials.scopes)


# ================================================================ lỗi mới (xfail strict)
@pytest.mark.xfail(
    strict=True,
    reason="SL-T121-1: dòng trùng nguyên văn (cùng khóa, kể cả #…) bị cộng dồn: trang lặp làm "
    "click/lượt hiển thị gấp bội mà không báo",
)
def test_sl_t121_1_dong_trung_nguyen_van_trong_mot_cau_tra_loi_khong_cong_don(fake, client):
    """Một (ngày, trang) chỉ có **một** dòng trong câu trả lời của Google. Dòng lặp lại nguyên văn
    là dữ liệu lạ: bỏ (đếm ``dropped``) hoặc bỏ cả câu trả lời đều được; cộng dồn thành 20 lượt
    hiển thị là sai số liệu."""
    rows = [*good_rows(), row(), row()]  # dòng PAGE lặp lại y hệt
    fake.on("POST", QUERY_URL, answer(*rows))
    try:
        result = client.fetch_day_page(date(2026, 10, 30), TODAY)
    except SearchConsoleError:
        return
    shown = {r.page: r for r in result.rows}
    assert shown[PAGE].impressions == 10 and shown[PAGE].clicks == 1


@pytest.mark.xfail(
    strict=True,
    reason="SL-T121-1: trang sau lặp lại trang trước (Google bỏ qua startRow, hay số liệu dịch "
    "giữa hai lệnh) thì số liệu bị cộng gấp đôi",
)
def test_sl_t121_1_trang_sau_lap_lai_trang_truoc_khong_cong_gap_doi(fake, client):
    page = _page_bytes(5_000, query=True)
    answers = iter([(200, page, {}), (200, page, {}), (200, _page_bytes(0, query=True), {})])
    fake.on("POST", QUERY_URL, lambda _r: next(answers))
    try:
        result = client.fetch_page_query(TODAY - timedelta(days=27), TODAY)
    except SearchConsoleError:
        return
    assert {r.impressions for r in result.rows} == {10}


# ================================================================ code: một chỗ gửi lệnh
def test_moi_lenh_toi_google_di_qua_send_hoac_lop_xin_ma():
    """Chỉ ``_call`` (sau ``_check_call`` trong ``_send``) gọi ``session.request``; không có chỗ
    gọi ``requests.get/post`` hay ``session.get/post`` khác trong module."""
    import ast
    from pathlib import Path

    tree = ast.parse(Path(search_console.__file__).read_text(encoding="utf-8"))
    callers = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for inner in ast.walk(node):
                if (
                    isinstance(inner, ast.Call)
                    and isinstance(inner.func, ast.Attribute)
                    and inner.func.attr
                    in {"request", "get", "post", "put", "delete", "patch", "head", "send"}
                    and "session" in ast.unparse(inner.func.value).lower()
                ):
                    callers.append(node.name)
            if node.name == "_send":
                lines = {
                    ast.unparse(c.func): c.lineno for c in ast.walk(node) if isinstance(c, ast.Call)
                }
                assert lines["self._check_call"] < lines["self._access_token"] < lines["self._call"]
    assert callers == ["_call"]
