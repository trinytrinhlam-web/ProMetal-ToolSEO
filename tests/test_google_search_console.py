"""T-121: client Google Search Console chỉ đọc (``seo_app/google/search_console.py``).

Thiết kế T-120 mục 1.2, 2.1–2.8; điều kiện Lá Chắn LC-T120-1 → -8, -15 → -18:

- LC-T120-1, -16: phạm vi ``webmasters.readonly`` duy nhất, lấy từ hằng; không ủy quyền toàn miền.
- LC-T120-2, -7: hai lệnh cố định, thân đúng nguyên văn một trong 4 khuôn; không lệnh ghi.
- LC-T120-3, -18: từng lớp chặn của lớp vận chuyển dùng chung được nối đúng ở client mới.
- LC-T120-4: câu lỗi cố định, không chép lời Google, thuộc tính, đường dẫn trang, từ khóa.
- LC-T120-5: JSON không ``NaN``/trùng khóa, kiểm từng dòng, tỉ lệ dòng hỏng.
- LC-T120-6, -17: thuộc tính phủ website theo từng phần tên miền; staging bị từ chối.
- LC-T120-8: tối đa 20 lệnh mỗi client, thử lại 429 một lần, trần lật trang.

Google giả: ``tests/fake_google.py`` (bộ chặn mạng của ``tests/conftest.py`` vẫn bật); khóa RSA
sinh lúc chạy test.
"""

from __future__ import annotations

import ast
import copy
import io
import itertools
import json
import os
import unicodedata
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

import pytest
import requests
from conftest import RealNetworkBlocked
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
from seo_app.google import search_console, sheets
from seo_app.google.search_console import (
    MAX_REQUESTS,
    SHAPES,
    SearchConsoleClient,
    SearchConsoleError,
    covers_site,
    page_filter_expression,
    parse_property,
    site_prefix,
    today_pacific,
)
from seo_app.google.service_account import (
    ALLOWED_SCOPES,
    SEARCH_CONSOLE_SCOPE,
    SHEETS_SCOPE,
    ServiceAccountError,
    load_service_account,
)

MOI = "LOI-MAY-CHU-GOOGLE-KHONG-DUOC-CHEP"
TODAY = date(2026, 11, 3)
WORDPRESS = "https://suachuacuasat.com"
DOMAIN = "sc-domain:suachuacuasat.com"
PREFIX_PROPERTY = "https://suachuacuasat.com/"
PREFIX = "https://suachuacuasat.com/"
PAGE = PREFIX + "sua-cua-keo-bi-ket/"
QUERY_URL = SEARCH_CONSOLE + "sites/sc-domain%3Asuachuacuasat.com/searchAnalytics/query"
PREFIX_QUERY_URL = SEARCH_CONSOLE + "sites/https%3A%2F%2Fsuachuacuasat.com%2F/searchAnalytics/query"
FILTER = [
    {
        "groupType": "and",
        "filters": [
            {
                "dimension": "page",
                "operator": "includingRegex",
                "expression": "^https://suachuacuasat\\.com/",
            }
        ],
    }
]
ZERO_WIDTH = chr(0x200B)
RTL_OVERRIDE = chr(0x202E)


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
def project(tmp_path):
    folder = tmp_path / "du-an"
    folder.mkdir()
    return folder


@pytest.fixture
def account(key_file, project):
    return load_service_account(key_file, scope=SEARCH_CONSOLE_SCOPE, project_root=project)


@pytest.fixture
def fake():
    return FakeGoogle()


@pytest.fixture
def sleeps():
    return []


def make_client(account, fake, prop=DOMAIN, **kwargs):
    options = {"session": make_session(fake), "today": lambda: TODAY, **kwargs}
    site = parse_property(prop) if prop is not None else None
    return SearchConsoleClient(account, WORDPRESS, site, **options)


@pytest.fixture
def client(account, fake, sleeps):
    return make_client(account, fake, sleep=sleeps.append)


def row(day="2026-10-30", page=PAGE, *, clicks=1, impressions=10, position=3.5, **extra):
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


def sent_bodies(fake):
    return [json.loads(r.body) for r in fake.search_console_requests() if r.method == "POST"]


def assert_fixed(error, *forbidden):
    text = str(error.value)
    for item in (MOI, ACCESS_TOKEN, EMAIL, "suachuacuasat", *forbidden):
        assert item not in text
    assert error.value.__cause__ is None


# ================================================================ phạm vi (LC-T120-1, -16)


def test_tai_khoan_search_console_dung_mot_pham_vi_chi_doc(account):
    credentials = account.credentials
    assert list(credentials.scopes) == [SEARCH_CONSOLE_SCOPE]
    assert SEARCH_CONSOLE_SCOPE == "https://www.googleapis.com/auth/webmasters.readonly"
    assert credentials._subject is None  # không ủy quyền toàn miền
    assert credentials.token is None  # chưa xin mã


def test_mac_dinh_van_la_pham_vi_sheets(key_file, project):
    account = load_service_account(key_file, project_root=project)
    assert list(account.credentials.scopes) == [SHEETS_SCOPE]
    assert ALLOWED_SCOPES == (SHEETS_SCOPE, SEARCH_CONSOLE_SCOPE)


def test_moi_client_mot_doi_tuong_xac_thuc_rieng(key_file, project):
    sheets_account = load_service_account(key_file, project_root=project)
    sc_account = load_service_account(key_file, scope=SEARCH_CONSOLE_SCOPE, project_root=project)
    assert sheets_account.credentials is not sc_account.credentials
    assert list(sheets_account.credentials.scopes) == [SHEETS_SCOPE]
    assert list(sc_account.credentials.scopes) == [SEARCH_CONSOLE_SCOPE]


@pytest.mark.parametrize(
    "scope",
    [
        "https://www.googleapis.com/auth/webmasters",
        "https://www.googleapis.com/auth/cloud-platform",
        "https://www.googleapis.com/auth/drive",
        "",
        " ",
        SEARCH_CONSOLE_SCOPE + " ",
        SEARCH_CONSOLE_SCOPE.upper(),
        f"{SHEETS_SCOPE} {SEARCH_CONSOLE_SCOPE}",
        [SHEETS_SCOPE, SEARCH_CONSOLE_SCOPE],
        [SEARCH_CONSOLE_SCOPE],
        (SEARCH_CONSOLE_SCOPE,),
        SEARCH_CONSOLE_SCOPE.encode(),
        None,
    ],
)
def test_pham_vi_la_bi_tu_choi_truoc_khi_doc_file(tmp_path, scope):
    missing = tmp_path / "khong-co.json"  # nếu đọc file thì câu báo sẽ là «không tìm thấy»
    with pytest.raises(ServiceAccountError, match="Phạm vi quyền Google") as error:
        load_service_account(missing, scope=scope)
    assert error.value.__cause__ is None


def test_client_tu_choi_tai_khoan_pham_vi_sheets(key_file, project, fake):
    sheets_account = load_service_account(key_file, project_root=project)
    with pytest.raises(SearchConsoleError, match="quyền chỉ đọc Search Console"):
        SearchConsoleClient(sheets_account, WORDPRESS, session=make_session(fake))
    assert fake.requests == []


def test_client_tu_choi_tai_khoan_uy_quyen_toan_mien(account, fake):
    delegated = replace(account, credentials=account.credentials.with_subject("chu@example.com"))
    with pytest.raises(SearchConsoleError, match="quyền chỉ đọc Search Console"):
        SearchConsoleClient(delegated, WORDPRESS, session=make_session(fake))
    with pytest.raises(SearchConsoleError, match="quyền chỉ đọc Search Console"):
        SearchConsoleClient(object(), WORDPRESS, session=make_session(fake))


def test_lenh_xin_ma_ky_dung_pham_vi_search_console(fake, client):
    fake.on("GET", SC_SITES, {"siteEntry": []})
    client.list_sites()
    (token_request,) = fake.token_requests()
    claims = jwt_claims(form(token_request)["assertion"])
    assert claims["iss"] == EMAIL and claims["aud"] == TOKEN_URL
    assert claims["scope"] == SEARCH_CONSOLE_SCOPE
    assert "sub" not in claims


def test_code_search_console_khong_mao_danh_khong_lenh_ghi():
    """Đọc cây cú pháp: không ``with_subject``, ``with_scopes``, ``AuthorizedSession``,
    ``before_request``, ``*.auth.default``, lớp chuyển 120 giây của thư viện; không địa chỉ nào
    ngoài gốc Search Console; không phương thức ghi; phạm vi đọc-ghi không xuất hiện."""
    tree = ast.parse(Path(search_console.__file__).read_text(encoding="utf-8"))
    banned = {
        "with_subject",
        "with_scopes",
        "with_quota_project",
        "AuthorizedSession",
        "before_request",
        "compute_engine",
        "apply",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            assert node.attr not in banned, ast.unparse(node)
            if node.attr == "default":
                assert not ast.unparse(node.value).endswith("auth"), ast.unparse(node)
            if node.attr == "Request":
                assert "requests" not in ast.unparse(node.value), ast.unparse(node)
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("google"):
            names = {alias.name for alias in node.names}
            assert not names & {"default", "compute_engine", "AuthorizedSession"}, names
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            value = node.value
            assert value not in {"PUT", "DELETE", "PATCH"}, value
            assert value != "GOOGLE_APPLICATION_CREDENTIALS"
            assert not value.rstrip("/").endswith("/auth/webmasters"), value
            if value.startswith(("https://", "http://")):
                assert value in {"https://www.googleapis.com/webmasters/v3/", "https://"}, value
    assert search_console._ROUTES == (("sites", "GET"), ("query", "POST"))


# ================================================================ thuộc tính (LC-T120-6, -17)


@pytest.mark.parametrize(
    "value",
    [
        DOMAIN,
        PREFIX_PROPERTY,
        "sc-domain:www.suachuacuasat.com",
        "https://www.suachuacuasat.com/",
        "sc-domain:xn--sa-cha-ca-st-ipb.vn",
        "sc-domain:a-b.example",
    ],
)
def test_thuoc_tinh_dung_dang(value):
    prop = parse_property(value)
    assert prop.site_url == value
    assert prop.kind == ("domain" if value.startswith("sc-domain:") else "prefix")


@pytest.mark.parametrize(
    "value",
    [
        "sc-domain:SUACHUACUASAT.com",
        "sc-domain:suachuacuasat.com.",
        "sc-domain:1.2.3.4",
        "sc-domain:[::1]",
        "https://suachuacuasat.com:8443/",
        "https://suachuacuasat.com:443/",
        "https://suachuacuasat.com/blog/",
        "http://suachuacuasat.com/",
        "https://suachuacuasat.com",
        "HTTPS://suachuacuasat.com/",
        "https://user@suachuacuasat.com/",
        "https://suachuacuasat.com/?x=1",
        "https://suachuacuasat.com/#x",
        "https:///",
        "sc-domain:",
        "sc-domain:com",
        "sc-domain:-bad.com",
        "sc-domain:bad-.com",
        "sc-domain:suachuacuasat..com",
        "sc-domain:suachuacuasat.com/x",
        "sc-domain:suachuacuasat.com:443",
        "sc-domain:@suachuacuasat.com",
        "sc-domain:sua chua.com",
        "sc-domain:suachuacuasát.com",
        "sc-domain:suachuacuasat.com\n",
        " sc-domain:suachuacuasat.com",
        "domain:suachuacuasat.com",
        "sc-domain:" + "a" * 64 + ".com",
        "sc-domain:" + "a." * 130 + "com",
        "",
        None,
        123,
        b"sc-domain:suachuacuasat.com",
    ],
)
def test_thuoc_tinh_sai_dang_bi_tu_choi(value):
    with pytest.raises(SearchConsoleError, match="sai dạng") as error:
        parse_property(value)
    assert_fixed(error)


@pytest.mark.parametrize(
    ("value", "wordpress", "covers"),
    [
        (DOMAIN, WORDPRESS, True),
        (DOMAIN, "https://www.suachuacuasat.com", True),
        (DOMAIN, "https://suachuacuasat.com/blog", True),
        (PREFIX_PROPERTY, WORDPRESS, True),
        (PREFIX_PROPERTY, "https://suachuacuasat.com/blog", True),
        (PREFIX_PROPERTY, "https://www.suachuacuasat.com", False),
        ("https://www.suachuacuasat.com/", WORDPRESS, False),
        ("sc-domain:www.suachuacuasat.com", WORDPRESS, False),
        ("sc-domain:evilsuachuacuasat.com", WORDPRESS, False),
        (DOMAIN, "https://evilsuachuacuasat.com", False),  # endswith trần sẽ cho qua
        ("sc-domain:cuasat.com", WORDPRESS, False),  # «suachuacuasat.com».endswith("cuasat.com")
        ("sc-domain:suachuacuasat.com.evil.com", WORDPRESS, False),
        ("sc-domain:staging-m.suachuacuasat.com", WORDPRESS, False),
        ("https://www.staging-m.suachuacuasat.com/", WORDPRESS, False),
        (DOMAIN, "http://suachuacuasat.com", False),
        (DOMAIN, "https://suachuacuasat.com:8443", False),
        (DOMAIN, "", False),
    ],
)
def test_phu_website_theo_tung_phan_ten_mien(value, wordpress, covers):
    assert covers_site(parse_property(value), wordpress) is covers


@pytest.mark.parametrize(
    ("wordpress", "prefix", "expression"),
    [
        (WORDPRESS, PREFIX, r"^https://suachuacuasat\.com/"),
        (WORDPRESS + "/", PREFIX, r"^https://suachuacuasat\.com/"),
        ("https://SuaChuaCuaSat.com", PREFIX, r"^https://suachuacuasat\.com/"),
        ("https://suachuacuasat.com:443", PREFIX, r"^https://suachuacuasat\.com/"),
        ("https://example.com/blog", "https://example.com/blog/", r"^https://example\.com/blog/"),
        (
            "https://example.com/b.log/",
            "https://example.com/b.log/",
            r"^https://example\.com/b\.log/",
        ),
    ],
)
def test_tien_to_va_bieu_thuc_loc_dung_tu_wordpress_url(wordpress, prefix, expression):
    assert site_prefix(wordpress) == prefix
    assert page_filter_expression(prefix) == expression


@pytest.mark.parametrize(
    "wordpress",
    [
        "",
        None,
        "suachuacuasat.com",
        "http://suachuacuasat.com",
        "https://suachuacuasat.com:8443",
        "https://u:p@suachuacuasat.com",
        "https://suachuacuasat.com/?a=1",
        "https://suachuacuasat.com/#a",
        "https://suachuacuasát.com",
        "https://suachuacuasat.com/a b",
        "https://suachuacuasat.com/(x)",
        "https://1.2.3.4",
        "https://suachuacuasat.com\\x",
    ],
)
def test_wordpress_url_khong_dung_duoc_bi_tu_choi(wordpress):
    with pytest.raises(SearchConsoleError, match="WORDPRESS_URL") as error:
        site_prefix(wordpress)
    assert_fixed(error)


def test_from_settings_kiem_thuoc_tinh_va_file_khoa_moi_lan(key_file, fake):
    settings = Settings(
        wordpress_url=WORDPRESS, gsc_site_url=DOMAIN, google_service_account_file=key_file
    )
    client = SearchConsoleClient.from_settings(settings, session=make_session(fake))
    assert client.site.site_url == DOMAIN
    assert list(client._account.credentials.scopes) == [SEARCH_CONSOLE_SCOPE]
    assert client.account_email == EMAIL
    key_file.write_text("{}", encoding="utf-8")  # file khóa hỏng: lần sau phải báo
    with pytest.raises(ServiceAccountError):
        SearchConsoleClient.from_settings(settings, session=make_session(fake))
    assert fake.requests == []


@pytest.mark.parametrize(
    ("site_url", "match"),
    [
        ("https://www.staging-m.suachuacuasat.com/", "không phải của website"),
        ("sc-domain:evilsuachuacuasat.com", "không phải của website"),
        ("http://suachuacuasat.com/", "sai dạng"),
        ("", "chưa khai báo"),
    ],
)
def test_from_settings_tu_choi_thuoc_tinh_truoc_khi_doc_file_khoa(tmp_path, fake, site_url, match):
    settings = Settings(
        wordpress_url=WORDPRESS,
        gsc_site_url=site_url,
        google_service_account_file=tmp_path / "khong-co.json",  # đọc file thì sẽ ra lỗi khác
    )
    with pytest.raises(SearchConsoleError, match=match) as error:
        SearchConsoleClient.from_settings(settings, session=make_session(fake))
    assert_fixed(error, "staging-m", "evil")  # câu cố định chỉ nói «thuộc tính staging»
    assert fake.requests == []


def test_from_settings_chi_tim_thuoc_tinh_khong_doc_gsc_site_url(key_file, fake):
    settings = Settings(
        wordpress_url=WORDPRESS, gsc_site_url="http://sai/", google_service_account_file=key_file
    )
    client = SearchConsoleClient.from_settings(
        settings, session=make_session(fake), with_property=False
    )
    assert client.site is None
    with pytest.raises(SearchConsoleError, match="sai dạng"):
        client.fetch_days(TODAY - timedelta(days=9), TODAY)
    assert fake.requests == []


def test_client_kiem_lai_thuoc_tinh_truyen_vao(account, fake):
    fake_site = search_console.SiteProperty("sc-domain:evil.example", "domain", "suachuacuasat.com")
    with pytest.raises(SearchConsoleError, match="không phải của website"):
        SearchConsoleClient(account, WORDPRESS, fake_site, session=make_session(fake))
    with pytest.raises(SearchConsoleError, match="sai dạng"):
        SearchConsoleClient(account, WORDPRESS, DOMAIN, session=make_session(fake))


# ================================================================ lệnh, thân (LC-T120-2, -7)


@pytest.mark.parametrize(
    ("method", "shape", "start", "expected"),
    [
        (
            "fetch_day_page",
            "day_page",
            date(2026, 10, 4),
            {"dimensions": ["date", "page"], "dataState": "all", "rowLimit": 25_000},
        ),
        (
            "fetch_page_query",
            "page_query",
            date(2026, 8, 3),
            {"dimensions": ["page", "query"], "dataState": "final", "rowLimit": 5_000},
        ),
        (
            "fetch_days",
            "days",
            date(2026, 10, 7),
            {"dimensions": ["date"], "dataState": "final", "rowLimit": 200},
        ),
        (
            "check_hosts",
            "hosts",
            date(2026, 10, 7),
            {"dimensions": ["page"], "dataState": "final", "rowLimit": 200},
        ),
    ],
)
def test_than_gui_dung_nguyen_van_khuon(fake, client, method, shape, start, expected):
    fake.on("POST", QUERY_URL, answer())
    getattr(client, method)(start, TODAY)
    (request,) = fake.search_console_requests()
    assert request.url == QUERY_URL and request.method == "POST"
    assert request.headers["Authorization"] == f"Bearer {ACCESS_TOKEN}"
    body = json.loads(request.body)
    full = {
        "startDate": start.isoformat(),
        "endDate": TODAY.isoformat(),
        "type": "web",
        "aggregationType": "byPage",
        "startRow": 0,
        **expected,
    }
    if SHAPES[shape].filtered:
        full["dimensionFilterGroups"] = FILTER
    assert body == full


def test_dia_chi_lenh_ma_hoa_dung_thuoc_tinh(fake, account):
    for prop, url in ((DOMAIN, QUERY_URL), (PREFIX_PROPERTY, PREFIX_QUERY_URL)):
        fake.on("POST", url, answer())
        make_client(account, fake, prop).fetch_days(TODAY - timedelta(days=9), TODAY)
        assert fake.requests[-1].url == url


GOOD = object()  # chỗ đặt thân đúng khuôn (dựng trong test)


@pytest.mark.parametrize(
    ("method", "url", "body"),
    [
        ("GET", QUERY_URL, None),
        ("POST", SC_SITES, None),
        ("POST", SC_SITES, GOOD),
        ("GET", SC_SITES, {}),
        ("GET", SC_SITES + "?fields=siteEntry", None),
        ("PUT", SEARCH_CONSOLE + "sites/sc-domain%3Asuachuacuasat.com", None),
        ("DELETE", SEARCH_CONSOLE + "sites/sc-domain%3Asuachuacuasat.com", None),
        ("GET", SEARCH_CONSOLE + "sites/sc-domain%3Asuachuacuasat.com", None),
        ("GET", SEARCH_CONSOLE + "sites/sc-domain%3Asuachuacuasat.com/sitemaps", None),
        (
            "PUT",
            SEARCH_CONSOLE + "sites/sc-domain%3Asuachuacuasat.com/sitemaps/https%3A%2F%2Fx%2Fs.xml",
            None,
        ),
        (
            "POST",
            "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect",
            {"inspectionUrl": PAGE, "siteUrl": DOMAIN},
        ),
        ("POST", SEARCH_CONSOLE + "sites/sc-domain%3Aevil.example/searchAnalytics/query", GOOD),
        (
            "POST",
            SEARCH_CONSOLE + "sites/sc-domain%3asuachuacuasat.com/searchAnalytics/query",
            GOOD,
        ),
        ("POST", SEARCH_CONSOLE + "sites/sc-domain:suachuacuasat.com/searchAnalytics/query", GOOD),
        ("POST", QUERY_URL + "?fields=rows", GOOD),
        ("POST", QUERY_URL.replace("https://", "http://"), GOOD),
        ("POST", QUERY_URL.replace("www.googleapis.com", "searchconsole.googleapis.com"), GOOD),
        ("PATCH", QUERY_URL, GOOD),
    ],
)
def test_lenh_ngoai_danh_sach_khong_gui(fake, client, method, url, body):
    if body is GOOD:
        body = client._body(SHAPES["day_page"], date(2026, 10, 30), TODAY, 0)
    with pytest.raises(SearchConsoleError, match="không nằm trong danh sách") as error:
        client._send(method, url, body)
    assert_fixed(error)
    assert fake.requests == []


def _set(**changes):
    def change(body):
        for key, value in changes.items():
            if value is _DROP:
                body.pop(key)
            else:
                body[key] = value
        return body

    return change


_DROP = object()


def _filter(**changes):
    def change(body):
        body["dimensionFilterGroups"][0]["filters"][0].update(changes)
        return body

    return change


BAD_BODIES = {
    "khoa-la-searchType": _set(searchType="web"),
    "khoa-la-fields": _set(fields="rows"),
    "type-image": _set(type="image"),
    "type-thieu": _set(type=_DROP),
    "dataState-hourly": _set(dataState="hourly_all"),
    "dataState-final-sai-khuon": _set(dataState="final"),
    "aggregation-byProperty": _set(aggregationType="byProperty"),
    "aggregation-auto": _set(aggregationType="auto"),
    "rowLimit-25001": _set(rowLimit=25_001),
    "rowLimit-1000": _set(rowLimit=1000),
    "rowLimit-chu": _set(rowLimit="25000"),
    "rowLimit-so-thuc": _set(rowLimit=25_000.0),
    "startRow-False": _set(startRow=False),
    "startRow-am": _set(startRow=-25_000),
    "startRow-le": _set(startRow=1),
    "startRow-qua-tran": _set(startRow=200_000),
    "startRow-so-thuc": _set(startRow=0.0),
    "startRow-thieu": _set(startRow=_DROP),
    "dimensions-dao": _set(dimensions=["page", "date"]),
    "dimensions-them-query": _set(dimensions=["date", "page", "query"]),
    "dimensions-country": _set(dimensions=["country"]),
    "dimensions-tuple-chu": _set(dimensions="date,page"),
    "loc-khac": _filter(expression="^https://evil\\.example/"),
    "loc-rong": _filter(expression=".*"),
    "loc-contains": _filter(operator="contains"),
    "loc-query": _filter(dimension="query"),
    "loc-them-khoa": _filter(extra="x"),
    "loc-bo": _set(dimensionFilterGroups=_DROP),
    "loc-or": lambda b: {**b, "dimensionFilterGroups": [{**FILTER[0], "groupType": "or"}]},
    "loc-hai-nhom": lambda b: {**b, "dimensionFilterGroups": FILTER * 2},
    "ngay-nguoc": _set(startDate="2026-11-03", endDate="2026-10-30"),
    "ngay-tuong-lai": _set(endDate="2026-11-04"),
    "qua-31-ngay": _set(startDate="2026-10-01"),
    "qua-16-thang": _set(startDate="2025-06-01", endDate="2025-06-02"),
    "ngay-sai-dang": _set(startDate="2026-10-3"),
    "ngay-khong-co": _set(startDate="2026-02-30", endDate="2026-03-01"),
    "ngay-so": _set(startDate=20261030),
    "nan": _set(rowLimit=float("nan")),
    "khong-phai-dict": lambda b: [b],
    "chuoi": lambda b: json.dumps(b),
}


@pytest.mark.parametrize("name", list(BAD_BODIES))
def test_than_sai_khuon_khong_gui(fake, client, name):
    good = client._body(SHAPES["day_page"], date(2026, 10, 30), TODAY, 0)
    body = BAD_BODIES[name](copy.deepcopy(good))
    with pytest.raises(SearchConsoleError, match="không nằm trong danh sách"):
        client._send("POST", QUERY_URL, body)
    assert fake.requests == []


def test_than_dung_khuon_duoc_gui(fake, client):
    """Đối chứng cho ``test_than_sai_khuon_khong_gui``: chính thân gốc thì gửi được."""
    fake.on("POST", QUERY_URL, answer())
    good = client._body(SHAPES["day_page"], date(2026, 10, 30), TODAY, 0)
    client._send("POST", QUERY_URL, copy.deepcopy(good))
    assert sent_bodies(fake) == [good]


def test_chua_chon_thuoc_tinh_khong_goi_query(fake, account):
    client = make_client(account, fake, prop=None)
    for call in (
        client.fetch_day_page,
        client.fetch_page_query,
        client.fetch_days,
        client.check_hosts,
    ):
        with pytest.raises(SearchConsoleError, match="sai dạng"):
            call(TODAY - timedelta(days=9), TODAY)
    assert fake.requests == []


@pytest.mark.parametrize(
    ("start", "end"),
    [
        (date(2026, 11, 4), date(2026, 11, 4)),  # ở tương lai (theo giờ PT)
        (TODAY - timedelta(days=487), TODAY - timedelta(days=480)),  # cũ hơn 16 tháng
        (date(2026, 10, 3), TODAY),  # 32 ngày
        (TODAY, date(2026, 11, 1)),  # ngược
        (datetime(2026, 10, 30), TODAY),  # datetime không phải date
        ("2026-10-30", TODAY),
    ],
)
def test_khoang_ngay_sai_khong_gui(fake, client, start, end):
    with pytest.raises(SearchConsoleError, match="Khoảng ngày") as error:
        client.fetch_day_page(start, end)
    assert_fixed(error)
    assert fake.requests == []


def test_khoang_ngay_bien_van_gui(fake, client):
    fake.on("POST", QUERY_URL, answer())
    oldest = TODAY - timedelta(days=486)
    client.fetch_day_page(oldest, oldest + timedelta(days=30))  # đúng 16 tháng, đúng 31 ngày
    client.fetch_page_query(TODAY - timedelta(days=92), TODAY)  # đúng 93 ngày
    assert [b["startDate"] for b in sent_bodies(fake)] == [oldest.isoformat(), "2026-08-03"]


# ================================================================ lớp vận chuyển (LC-T120-3, -18)


def test_moi_lenh_co_gio_cho_khong_theo_chuyen_huong_khong_doc_netrc(fake, client):
    fake.on("GET", SC_SITES, {"siteEntry": []})
    fake.on("POST", QUERY_URL, answer())
    session = client._session
    sent: list[dict] = []
    original = session.request

    def spy(method, url, **kwargs):  # ghi lại đúng tùy chọn mỗi lệnh truyền cho requests
        sent.append({"method": method, "url": url, **kwargs})
        return original(method, url, **kwargs)

    session.request = spy  # lớp chuyển xin mã dùng chung phiên này
    client.list_sites()
    client.fetch_days(TODAY - timedelta(days=9), TODAY)
    assert [(s["method"], s["url"]) for s in sent] == [
        ("POST", TOKEN_URL),
        ("GET", SC_SITES),
        ("POST", QUERY_URL),
    ]
    for options in sent:
        assert 0 < options["timeout"] <= 30
        assert options["allow_redirects"] is False and options["stream"] is True
        assert isinstance(options["auth"], sheets._NoAuth | sheets._Bearer)
        assert sheets._refuse_redirect in options["hooks"]["response"]
    assert isinstance(sent[0]["auth"], sheets._NoAuth)  # lệnh xin mã không gắn gì
    assert session.max_redirects == 0
    assert isinstance(client._token_request, sheets._TokenRequest)
    assert search_console._TokenRequest is sheets._TokenRequest  # dùng chung, không chép


def test_netrc_khong_duoc_doc(fake, client, monkeypatch):
    def no_netrc(*_args, **_kwargs):
        raise AssertionError("requests đọc .netrc")

    monkeypatch.setattr(requests.sessions, "get_netrc_auth", no_netrc)
    fake.on("GET", SC_SITES, {"siteEntry": []})
    client.list_sites()
    (token_request,) = fake.token_requests()
    assert "Authorization" not in token_request.headers
    for request in fake.search_console_requests():
        assert request.headers["Authorization"] == f"Bearer {ACCESS_TOKEN}"


def test_gio_cho_toi_da_30_giay(fake, account):
    client = make_client(account, fake, timeout=120)
    assert client.timeout == 30
    fake.on("GET", SC_SITES, {"siteEntry": []})
    client.list_sites()
    assert [kwargs["timeout"] for _request, kwargs in fake.calls] == [30, 30]


def test_het_gio_thanh_cau_co_dinh(fake, client):
    fake.on("GET", SC_SITES, lambda _r: requests.exceptions.ReadTimeout(MOI))
    with pytest.raises(SearchConsoleError, match="30 giây") as error:
        client.list_sites()
    assert_fixed(error)


@pytest.mark.parametrize(
    ("exception", "match"),
    [
        (requests.exceptions.ConnectionError(MOI), "Không kết nối được"),
        (requests.exceptions.SSLError(MOI), "SSL"),
        (requests.exceptions.ChunkedEncodingError(MOI), "Lỗi mạng"),
        (requests.exceptions.InvalidURL(MOI), "Lỗi mạng"),
    ],
)
def test_loi_mang_thanh_cau_co_dinh(fake, client, exception, match):
    fake.on("POST", QUERY_URL, lambda _r: exception)
    with pytest.raises(SearchConsoleError, match=match) as error:
        client.fetch_days(TODAY - timedelta(days=9), TODAY)
    assert_fixed(error)


class _Tripwire(io.RawIOBase):
    """Thân câu trả lời đếm số lần bị đọc: thân 3xx không được đọc (như LC-T097-1)."""

    def __init__(self) -> None:
        super().__init__()
        self.reads = 0

    def readable(self) -> bool:
        return True

    def readinto(self, buffer) -> int:
        self.reads += 1
        return 0


@pytest.mark.parametrize("location", [True, False])
def test_chuyen_huong_khong_di_theo_khong_doc_than(fake, client, location):
    headers = {"Location": "https://evil.example/x"} if location else {}
    fake.on("GET", SC_SITES, (302, b"x" * 10, headers))
    trip = _Tripwire()
    original = fake.send

    def send(request, **kwargs):
        response = original(request, **kwargs)
        if response.status_code == 302:
            response.raw = trip
        return response

    fake.send = send
    with pytest.raises(SearchConsoleError, match="chuyển hướng") as error:
        client.list_sites()
    assert_fixed(error, "evil")
    assert trip.reads == 0
    assert all("evil" not in r.url for r in fake.requests)


@pytest.mark.parametrize("declared", [True, False])
def test_cau_tra_loi_query_qua_8_mb_bi_bo(fake, client, declared):
    big = b'{"rows": ["' + b"x" * (8 * 1024 * 1024 + 10) + b'"]}'
    headers = {"Content-Length": str(len(big))} if declared else {}
    fake.on("POST", QUERY_URL, (200, big, headers))
    with pytest.raises(SearchConsoleError, match="lớn bất thường") as error:
        client.fetch_days(TODAY - timedelta(days=9), TODAY)
    assert_fixed(error)


def test_gioi_han_co_theo_tung_lenh(fake, client):
    """Câu trả lời 300 KB: lệnh ``query`` (≤ 8 MB) nhận, lệnh ``sites`` (≤ 256 KB) bỏ."""
    pad = "y" * 300_000
    fake.on("POST", QUERY_URL, answer(pad=pad))
    assert client.fetch_days(TODAY - timedelta(days=9), TODAY).rows == ()
    fake.on("GET", SC_SITES, {"siteEntry": [], "pad": pad})
    with pytest.raises(SearchConsoleError, match="lớn bất thường"):
        client.list_sites()


def test_chi_goi_dung_hai_may_chu_google(fake, client):
    fake.on("GET", SC_SITES, {"siteEntry": []})
    fake.on("POST", QUERY_URL, answer())
    client.list_sites()
    client.fetch_days(TODAY - timedelta(days=9), TODAY)
    assert {urlsplit(r.url).netloc for r in fake.requests} == {
        "oauth2.googleapis.com",
        "www.googleapis.com",
    }


def test_ma_truy_cap_xin_mot_lan_cho_mot_client(fake, client):
    fake.on("GET", SC_SITES, {"siteEntry": []})
    fake.on("POST", QUERY_URL, answer())
    client.list_sites()
    client.fetch_days(TODAY - timedelta(days=9), TODAY)
    assert len(fake.token_requests()) == 1


def test_repr_khong_lo_ma_truy_cap_email(fake, client):
    fake.on("GET", SC_SITES, {"siteEntry": []})
    client.list_sites()
    shown = repr(client) + str(client) + repr(sheets._Bearer(ACCESS_TOKEN)) + repr(client._account)
    assert ACCESS_TOKEN not in shown and EMAIL not in shown


@pytest.mark.parametrize(
    "token_answer",
    [
        (400, {"error": "invalid_grant", "error_description": MOI}, {}),
        (401, {"error": "invalid_client", "error_description": MOI}, {}),
        (200, {"token_type": "Bearer", "error_description": MOI}, {}),
        (200, {"access_token": "ya29.ma\nX-Chen: 1", "expires_in": 3600}, {}),
        (302, {"x": MOI}, {"Location": "https://evil.example/token"}),
        requests.exceptions.ConnectTimeout(MOI),
    ],
)
def test_loi_xin_ma_thanh_cau_co_dinh(fake, client, token_answer):
    fake.on("POST", TOKEN_URL, lambda _r: token_answer)
    fake.on("GET", SC_SITES, {"siteEntry": []})
    with pytest.raises(SearchConsoleError) as error:
        client.list_sites()
    assert_fixed(error)
    assert fake.search_console_requests() == []  # không có mã thì không gọi Search Console
    assert all("evil" not in r.url for r in fake.requests)


def test_bo_chan_mang_chan_ca_client_khong_co_google_gia(account):
    client = SearchConsoleClient(account, WORDPRESS, parse_property(DOMAIN), today=lambda: TODAY)
    with pytest.raises(RealNetworkBlocked):
        client.list_sites()


# ================================================================ câu lỗi (LC-T120-4), 429, số lệnh


@pytest.mark.parametrize(
    ("status", "match"),
    [
        (400, "không hợp lệ"),
        (401, "mã truy cập"),
        (403, "chưa có quyền xem thuộc tính"),
        (404, "Không tìm thấy thuộc tính"),
        (418, "từ chối yêu cầu"),
        (429, "15 phút"),
        (500, "đang lỗi"),
        (503, "đang lỗi"),
        (204, "không đúng dạng"),
    ],
)
def test_loi_http_thanh_cau_co_dinh(fake, client, status, match):
    body = {
        "error": {
            "code": status,
            "message": f"{MOI} {PAGE} sửa cửa sắt {DOMAIN}",
            "errors": [{"reason": "forbidden", "message": MOI}],
        }
    }
    fake.on("POST", QUERY_URL, (status, body, {}))
    with pytest.raises(SearchConsoleError, match=match) as error:
        client.fetch_days(TODAY - timedelta(days=9), TODAY)
    assert_fixed(error, PAGE, "sửa cửa sắt", DOMAIN)
    assert error.value.status_code == status


@pytest.mark.parametrize(
    ("field", "reason"), [("errors", "accessNotConfigured"), ("details", "SERVICE_DISABLED")]
)
def test_403_api_chua_bat_co_cau_rieng(fake, client, field, reason):
    body = {"error": {"code": 403, "message": MOI, field: [{"reason": reason, "message": MOI}]}}
    fake.on("POST", QUERY_URL, (403, body, {}))
    with pytest.raises(SearchConsoleError, match="Chưa bật Google Search Console API") as error:
        client.fetch_days(TODAY - timedelta(days=9), TODAY)
    assert_fixed(error)


@pytest.mark.parametrize(
    "reason",
    ["accessNotConfigured" + ZERO_WIDTH, "ACCESSNOTCONFIGURED", "accessNotConfigured x", 123, None],
)
def test_ma_ly_do_la_khong_doi_cau(fake, client, reason):
    body = {"error": {"code": 403, "errors": [{"reason": reason}]}}
    fake.on("POST", QUERY_URL, (403, body, {}))
    with pytest.raises(SearchConsoleError, match="chưa có quyền xem thuộc tính"):
        client.fetch_days(TODAY - timedelta(days=9), TODAY)


def test_429_thu_lai_dung_mot_lan_roi_thanh_cong(fake, client, sleeps):
    answers = iter([(429, {"error": {"code": 429, "message": MOI}}, {}), answer()])
    fake.on("POST", QUERY_URL, lambda _r: next(answers))
    client.fetch_days(TODAY - timedelta(days=9), TODAY)
    assert len(fake.search_console_requests()) == 2
    assert len(sleeps) == 1 and 2.0 <= sleeps[0] <= 2.5


def test_429_hai_lan_thi_bao_loi(fake, client, sleeps):
    fake.on("POST", QUERY_URL, (429, {"error": {"code": 429, "message": MOI}}, {}))
    with pytest.raises(SearchConsoleError, match="15 phút") as error:
        client.fetch_days(TODAY - timedelta(days=9), TODAY)
    assert_fixed(error)
    assert len(fake.search_console_requests()) == 2  # đúng một lần thử lại
    assert len(sleeps) == 1


def distinct_query_pages(count=5_000):
    """Mỗi lần gọi trả một trang đầy, từ khóa không trùng trang trước (lượt 2: dòng lặp nguyên văn
    giữa hai trang bị bỏ, SL-T121-1, nên trang lặp y hệt không còn dùng để thử lật trang)."""
    pages = itertools.count()

    def handler(_request):
        number = next(pages)
        return answer(*[query_row(f"tu khoa {number}-{i}") for i in range(count)])

    return handler


def test_toi_da_so_lenh_moi_client(fake, account):
    fake.on("POST", QUERY_URL, distinct_query_pages())
    client = make_client(account, fake, max_requests=2)
    with pytest.raises(SearchConsoleError, match="Đã gửi đủ 2 lệnh") as error:
        client.fetch_page_query(TODAY - timedelta(days=27), TODAY)
    assert_fixed(error)
    assert len(fake.search_console_requests()) == 2 and client.request_count == 2
    assert make_client(account, fake).max_requests == MAX_REQUESTS == 20
    assert make_client(account, fake, max_requests=50).max_requests == 20
    assert make_client(account, fake, max_requests=True).max_requests == 20


# ================================================================ đọc JSON (LC-T120-5)


BAD_JSON = {
    "nan": b'{"rows": [{"keys": ["2026-10-30"], "clicks": NaN, "impressions": 1, "position": 1}]}',
    "infinity": b'{"rows": [{"keys": ["2026-10-30"], "clicks": 1, "impressions": Infinity, '
    b'"position": 1}]}',
    "am-infinity": b'{"rows": [{"keys": ["2026-10-30"], "clicks": 1, "impressions": 1, '
    b'"position": -Infinity}]}',
    "trung-khoa-ngoai": b'{"rows": [], "rows": []}',
    "trung-khoa-trong-dong": b'{"rows": [{"keys": ["2026-10-30"], "clicks": 1, "clicks": 2, '
    b'"impressions": 3, "position": 1}]}',
    "long-qua-sau": b"[" * 100_000 + b"]" * 100_000,
    "khong-phai-utf8": b"\xff\xfe{}",
    "danh-sach": b"[]",
    "chuoi": b'"rows"',
    "rong": b"",
    "cut-giua-chung": b'{"rows": [{"keys": ["2026-10-30"], "clicks": 1',
    "so-qua-nhieu-chu-so": b'{"rows": [{"keys": ["2026-10-30"], "clicks": 1' + b"0" * 5000 + b"}]}",
}


# Tên ca ngắn (``ids``): trên Windows, tên test dài quá 32.767 ký tự làm pytest hỏng lúc đặt biến
# PYTEST_CURRENT_TEST, và câu báo lỗi của pytest in cả os.environ (có thể có khóa thật của máy).
@pytest.mark.parametrize("raw", list(BAD_JSON.values()), ids=list(BAD_JSON))
def test_json_la_bi_bo_ca_cau_tra_loi(fake, client, raw):
    fake.on("POST", QUERY_URL, (200, raw, {}))
    with pytest.raises(SearchConsoleError, match="không đúng dạng") as error:
        client.fetch_days(TODAY - timedelta(days=9), TODAY)
    assert_fixed(error)


@pytest.mark.parametrize("aggregation", ["byProperty", "auto", "", 1, None])
def test_kieu_cong_don_la_bo_ca_cau_tra_loi(fake, client, aggregation):
    data = {"rows": [], "responseAggregationType": aggregation}
    fake.on("POST", QUERY_URL, data)
    if aggregation is None:  # «null» coi như không có trường
        assert client.fetch_days(TODAY - timedelta(days=9), TODAY).rows == ()
        return
    with pytest.raises(SearchConsoleError, match="không đúng dạng"):
        client.fetch_days(TODAY - timedelta(days=9), TODAY)


@pytest.mark.parametrize("rows", [{"a": 1}, "rows", [row(day="2026-10-30")] * 201])
def test_rows_sai_khuon_bo_ca_cau_tra_loi(fake, client, rows):
    fake.on("POST", QUERY_URL, {"rows": rows})
    with pytest.raises(SearchConsoleError, match="không đúng dạng"):
        client.fetch_days(TODAY - timedelta(days=9), TODAY)


@pytest.mark.parametrize("data", [{}, {"responseAggregationType": "byPage"}, {"rows": []}])
def test_khong_co_dong_la_khong_co_so_lieu(fake, client, data):
    fake.on("POST", QUERY_URL, data)
    result = client.fetch_day_page(TODAY - timedelta(days=9), TODAY)
    assert result.rows == () and result.dropped == 0 and result.truncated is False


# ================================================================ kiểm từng dòng (thiết kế 2.4)

D = "2026-10-30"
BAD_ROWS = {
    "click-bool": {"clicks": True},
    "hien-thi-bool": {"impressions": True},
    "vi-tri-bool": {"position": True},
    "vi-tri-0": {"position": 0},
    "vi-tri-duoi-1": {"position": 0.5},
    "vi-tri-qua-lon": {"position": 10_001},
    "vi-tri-chu": {"position": "3"},
    "click-lon-hon-hien-thi": {"clicks": 11, "impressions": 10},
    "hien-thi-0": {"clicks": 0, "impressions": 0},
    "click-am": {"clicks": -1},
    "click-le": {"clicks": 1.5},
    "hien-thi-qua-lon": {"impressions": 10**9 + 1},
    "so-nguyen-khong-lo": {"impressions": 10**30},
    "ctr-qua-1": {"ctr": 1.5},
    "ctr-chu": {"ctr": "0.1"},
    "thieu-click": {"clicks": _DROP},
    "thieu-vi-tri": {"position": _DROP},
    "keys-thieu": {"keys": [D]},
    "keys-thua": {"keys": [D, PAGE, "x"]},
    "keys-so": {"keys": [20261030, PAGE]},
    "keys-khong-phai-list": {"keys": f"{D},{PAGE}"},
    "ngay-ngoai-khoang": {"keys": ["2026-10-01", PAGE]},
    "ngay-sai-dang": {"keys": ["30/10/2026", PAGE]},
    "ngay-khong-co": {"keys": ["2026-02-30", PAGE]},
    "trang-staging": {"keys": [D, "https://www.staging-m.suachuacuasat.com/x/"]},
    "trang-www": {"keys": [D, "https://www.suachuacuasat.com/x/"]},
    "trang-http": {"keys": [D, "http://suachuacuasat.com/x/"]},
    "trang-ten-mien-gia": {"keys": [D, "https://suachuacuasat.com.evil.example/x/"]},
    "trang-mat-khau": {"keys": [D, "https://u:p@suachuacuasat.com/x/"]},
    "trang-cong": {"keys": [D, "https://suachuacuasat.com:8443/x/"]},
    "trang-dau-nhay": {"keys": [D, PREFIX + 'x"y/']},
    "trang-khoang-trang": {"keys": [D, PREFIX + "a b/"]},
    "trang-ky-tu-vo-hinh": {"keys": [D, PREFIX + "a" + ZERO_WIDTH + "b/"]},
    "trang-qua-dai": {"keys": [D, PREFIX + "a" * 2000]},
    "trang-khong-tien-to": {"keys": [D, "https://suachuacuasat.com"]},
}


@pytest.mark.parametrize("name", [*BAD_ROWS, "dong-khong-phai-dict"])
def test_dong_sai_bi_bo_va_dem(fake, client, name):
    good = [row(page=f"{PREFIX}bai-{i}/") for i in range(20)]
    if name == "dong-khong-phai-dict":
        bad = "x"
    else:
        bad = row()
        for key, value in BAD_ROWS[name].items():
            if value is _DROP:
                bad.pop(key)
            else:
                bad[key] = value
    fake.on("POST", QUERY_URL, answer(*good, bad))
    result = client.fetch_day_page(date(2026, 10, 30), TODAY)
    assert result.dropped == 1
    assert [r.page for r in result.rows] == [f"{PREFIX}bai-{i}/" for i in range(20)]


def test_dong_dung_doc_dung_so(fake, client):
    fake.on("POST", QUERY_URL, answer(row(clicks=3.0, impressions=40, position=7.25)))
    (shown,) = client.fetch_day_page(date(2026, 10, 30), TODAY).rows
    assert shown.day == date(2026, 10, 30) and shown.page == PAGE and shown.query is None
    assert (shown.clicks, shown.impressions, shown.position) == (3, 40, 7.25)
    assert type(shown.clicks) is int and shown.position_sum == pytest.approx(290)


def test_qua_10_phan_tram_dong_sai_bo_ca_cau_tra_loi(fake, client):
    good = [row(page=f"{PREFIX}bai-{i}/") for i in range(9)]
    bad = [{**row(), "position": 0}] * 2  # 2/11 ≈ 18%
    fake.on("POST", QUERY_URL, answer(*good, *bad))
    with pytest.raises(SearchConsoleError, match="không đúng dạng"):
        client.fetch_day_page(date(2026, 10, 30), TODAY)


def test_dung_10_phan_tram_dong_sai_van_nhan(fake, client):
    good = [row(page=f"{PREFIX}bai-{i}/") for i in range(9)]
    fake.on("POST", QUERY_URL, answer(*good, {**row(), "position": 0}))  # 1/10
    result = client.fetch_day_page(date(2026, 10, 30), TODAY)
    assert len(result.rows) == 9 and result.dropped == 1


def test_bo_phan_thang_va_cong_don(fake, client):
    fake.on(
        "POST",
        QUERY_URL,
        answer(
            row(page=PAGE, clicks=1, impressions=10, position=3.0),
            row(page=PAGE + "#cach-sua", clicks=2, impressions=30, position=5.0),
            row(day="2026-10-31", page=PAGE + "#cach-sua", clicks=0, impressions=5, position=8.0),
        ),
    )
    first, second = client.fetch_day_page(date(2026, 10, 30), TODAY).rows
    assert (first.day, first.page, first.clicks, first.impressions) == (
        date(2026, 10, 30),
        PAGE,
        3,
        40,
    )
    assert first.position == pytest.approx(4.5) and first.position_sum == pytest.approx(180)
    assert (second.day, second.page, second.impressions) == (date(2026, 10, 31), PAGE, 5)


def test_ma_phan_tram_hoa_thuong_giu_nguyen_cho_loi_chuan_hoa(fake, client):
    """Client không giải mã ``%``: hai cách viết cùng một trang về nguyên văn (T-123 chuẩn hóa)."""
    upper = PREFIX + "s%E1%BB%ADa-c%E1%BB%ADa/"
    lower = PREFIX + "s%e1%bb%ada-c%e1%bb%ada/"
    fake.on("POST", QUERY_URL, answer(row(page=upper), row(page=lower)))
    assert [r.page for r in client.fetch_day_page(date(2026, 10, 30), TODAY).rows] == [upper, lower]


def test_thuoc_tinh_ten_mien_bo_dong_staging_ca_khi_google_tra(fake, client):
    staging = "https://www.staging-m.suachuacuasat.com/bai/"
    rows = [row(page=f"{PREFIX}bai-{i}/") for i in range(10)] + [row(page=staging)]
    fake.on("POST", QUERY_URL, answer(*rows))
    result = client.fetch_day_page(date(2026, 10, 30), TODAY)
    assert staging not in {r.page for r in result.rows} and result.dropped == 1


def test_tu_khoa_lam_sach_va_cat(fake, client):
    nfd = unicodedata.normalize("NFD", "sửa")  # viết tách dấu: phải về NFC
    assert nfd != "sửa"
    rows = [query_row(f"q{i}") for i in range(30)] + [
        query_row(f"sửa  cửa{ZERO_WIDTH} sắt{RTL_OVERRIDE}\t"),
        query_row(nfd),
        query_row("a" * 300),
        query_row(ZERO_WIDTH * 3),  # rỗng sau làm sạch: bỏ
        query_row("x" * 2049),  # quá dài: bỏ
    ]
    fake.on("POST", QUERY_URL, answer(*rows))
    result = client.fetch_page_query(TODAY - timedelta(days=27), TODAY)
    queries = [r.query for r in result.rows]
    assert "sửa cửa sắt" in queries
    assert "sửa" in queries
    assert "a" * 200 in queries
    assert result.dropped == 2
    assert all(r.day is None and r.page == PAGE for r in result.rows)


@pytest.mark.parametrize(
    ("metadata", "first", "state"),
    [
        ({"first_incomplete_date": "2026-11-01"}, date(2026, 11, 1), "ok"),
        ({"firstIncompleteDate": "2026-11-01"}, date(2026, 11, 1), "ok"),
        (_DROP, None, "missing"),
        ({}, None, "missing"),
        ({"first_incomplete_hour": "2026-11-03T10:00:00-08:00"}, None, "missing"),
        ({"first_incomplete_date": "2026-13-01"}, None, "bad"),
        ({"first_incomplete_date": "2026-10-01"}, None, "bad"),  # ngoài khoảng đã hỏi
        ({"first_incomplete_date": 20261101}, None, "bad"),
        ("x", None, "bad"),
    ],
)
def test_ngay_dau_tien_con_so_tam(fake, client, metadata, first, state):
    data = answer(row())
    if metadata is not _DROP:
        data["metadata"] = metadata
    fake.on("POST", QUERY_URL, data)
    result = client.fetch_day_page(date(2026, 10, 30), TODAY)
    assert (result.first_incomplete_date, result.metadata) == (first, state)


def test_lat_trang_khi_du_25000_dong(fake, client):
    first = [row(day="2026-10-30", page=f"{PREFIX}p{i}/") for i in range(25_000)]
    second = [row(day="2026-10-31", page=f"{PREFIX}q{i}/") for i in range(10)]
    pages = iter([answer(*first), answer(*second)])
    fake.on("POST", QUERY_URL, lambda _r: next(pages))
    result = client.fetch_day_page(date(2026, 10, 30), TODAY)
    assert len(result.rows) == 25_010 and result.truncated is False
    assert [b["startRow"] for b in sent_bodies(fake)] == [0, 25_000]


def test_lat_trang_dung_khi_trang_sau_rong(fake, client):
    full = [row(day="2026-10-30", page=f"{PREFIX}p{i}/") for i in range(25_000)]
    pages = iter([answer(*full), answer()])
    fake.on("POST", QUERY_URL, lambda _r: next(pages))
    result = client.fetch_day_page(date(2026, 10, 30), TODAY)
    assert len(result.rows) == 25_000 and result.truncated is False
    assert len(sent_bodies(fake)) == 2


def test_tran_so_dong_thi_dung_va_bao_co_the_thieu(fake, client):
    # Lượt 2 (SL-T121-1, R5): mỗi trang dòng riêng. Bản lượt 1 cho 10 trang giống hệt nhau và ghim
    # đúng hành vi lỗi (dòng lặp cộng dồn thành 100 lượt hiển thị); trang lặp nay ở
    # test_trang_lap_lai_bo_ca_lan_lay.
    fake.on("POST", QUERY_URL, distinct_query_pages())
    result = client.fetch_page_query(TODAY - timedelta(days=27), TODAY)
    assert result.truncated is True
    assert [b["startRow"] for b in sent_bodies(fake)] == list(range(0, 50_000, 5_000))
    assert len(result.rows) == 50_000 and result.dropped == 0
    assert {r.impressions for r in result.rows} == {10}  # không dòng nào bị cộng gấp


# ================================================================ lượt 2: dòng lặp, surrogate, GN


def test_dong_lap_nguyen_van_bi_bo_va_dem(fake, client):
    rows = [row(page=f"{PREFIX}bai-{i}/") for i in range(20)] + [row(), row()]
    fake.on("POST", QUERY_URL, answer(*rows))
    result = client.fetch_day_page(date(2026, 10, 30), TODAY)
    shown = {r.page: r for r in result.rows}
    assert (shown[PAGE].clicks, shown[PAGE].impressions) == (1, 10)
    assert result.dropped == 1 and len(result.rows) == 21


def test_dong_lap_giua_hai_trang_bi_bo(fake, client):
    """Số liệu dịch giữa hai lệnh lật trang: dòng cuối trang 1 hiện lại ở đầu trang 2."""
    first = [query_row(f"a{i}") for i in range(5_000)]
    second = [query_row("a4999"), *[query_row(f"b{i}") for i in range(30)]]
    pages = iter([answer(*first), answer(*second)])
    fake.on("POST", QUERY_URL, lambda _r: next(pages))
    result = client.fetch_page_query(TODAY - timedelta(days=27), TODAY)
    assert len(result.rows) == 5_030 and result.dropped == 1
    assert {r.impressions for r in result.rows} == {10}


def test_trang_lap_lai_bo_ca_lan_lay(fake, client):
    fake.on("POST", QUERY_URL, answer(*[query_row(f"tu khoa {i}") for i in range(5_000)]))
    with pytest.raises(SearchConsoleError, match="lặp lại") as error:
        client.fetch_page_query(TODAY - timedelta(days=27), TODAY)
    assert_fixed(error)
    assert "không đúng dạng" in str(error.value) and "Thử lại sau" not in str(error.value)
    assert len(fake.search_console_requests()) == 2  # dừng ngay ở trang lặp, không lật tiếp


def test_dong_chi_khac_phan_thang_van_cong_don_khi_co_dong_lap(fake, client):
    """Dòng lặp nguyên văn bị bỏ; dòng khác nhau ở «#…» vẫn cộng dồn (thiết kế 1.4)."""
    rows = [row(page=f"{PREFIX}bai-{i}/") for i in range(20)] + [
        row(page=PAGE, clicks=1, impressions=10),
        row(page=PAGE + "#a", clicks=0, impressions=5),
        row(page=PAGE + "#a", clicks=0, impressions=5),  # lặp nguyên văn: bỏ
    ]
    fake.on("POST", QUERY_URL, answer(*rows))
    result = client.fetch_day_page(date(2026, 10, 30), TODAY)
    shown = {r.page: r for r in result.rows}
    assert (shown[PAGE].clicks, shown[PAGE].impressions) == (1, 15) and result.dropped == 1


def test_kiem_tra_bo_dong_lap(fake, client):
    def host_row(page, impressions):
        return {"keys": [page], "clicks": 0, "impressions": impressions, "position": 4.0}

    staging = "https://www.staging-m.suachuacuasat.com/x/"
    rows = [host_row(f"{PREFIX}p{i}/", 1) for i in range(20)] + [host_row(staging, 5)] * 2
    fake.on("POST", QUERY_URL, answer(*rows))
    result = client.check_hosts(date(2026, 10, 7), TODAY)
    assert (result.inside_impressions, result.outside_impressions) == (20, 5)
    assert result.hosts == (("www.staging-m.suachuacuasat.com", 5),) and result.dropped == 1


LONE = chr(0xD800)  # surrogate lẻ: JSON "\ud800" đọc ra chữ này, không mã hóa được UTF-8


@pytest.mark.parametrize(
    "page",
    [PREFIX + "a" + LONE + "/", PREFIX + LONE, PAGE + "#" + LONE],
    ids=["giua-duong-dan", "cuoi-duong-dan", "phan-thang"],
)
def test_dia_chi_co_surrogate_le_bi_bo(fake, client, page):
    rows = [row(page=f"{PREFIX}bai-{i}/") for i in range(20)] + [row(page=page)]
    fake.on("POST", QUERY_URL, answer(*rows))  # Google giả ghi JSON kiểu "\ud800"
    result = client.fetch_day_page(date(2026, 10, 30), TODAY)
    assert result.dropped == 1 and len(result.rows) == 20
    for shown in result.rows:
        shown.page.encode("utf-8")  # mọi địa chỉ trả về đều mã hóa được (cache, mã băm, giao diện)


def test_tu_khoa_co_surrogate_le_duoc_lam_sach(fake, client):
    rows = [query_row(f"q{i}") for i in range(20)] + [query_row("sửa" + LONE + " cửa")]
    fake.on("POST", QUERY_URL, answer(*rows))
    result = client.fetch_page_query(TODAY - timedelta(days=27), TODAY)
    assert "sửa cửa" in {r.query for r in result.rows} and result.dropped == 0


def test_kiem_tra_dia_chi_surrogate_khong_tinh_trong_website(fake, client):
    def host_row(page, impressions):
        return {"keys": [page], "clicks": 0, "impressions": impressions, "position": 4.0}

    rows = [host_row(f"{PREFIX}p{i}/", 1) for i in range(20)] + [host_row(PREFIX + LONE, 3)]
    fake.on("POST", QUERY_URL, answer(*rows))
    result = client.check_hosts(date(2026, 10, 7), TODAY)
    assert (result.inside_impressions, result.outside_impressions) == (20, 3)
    assert result.hosts == (("suachuacuasat.com", 3),)


@pytest.mark.parametrize(
    "reason", ["rateLimitExceeded", "userRateLimitExceeded", "dailyLimitExceeded", "quotaExceeded"]
)
def test_403_han_muc_bao_doi_15_phut(fake, client, sleeps, reason):
    body = {"error": {"code": 403, "message": MOI, "errors": [{"reason": reason, "message": MOI}]}}
    fake.on("POST", QUERY_URL, (403, body, {}))
    with pytest.raises(SearchConsoleError, match="15 phút") as error:
        client.fetch_days(TODAY - timedelta(days=9), TODAY)
    assert_fixed(error)
    assert error.value.status_code == 403
    assert len(fake.search_console_requests()) == 1 and sleeps == []  # 403 không tự thử lại


def test_than_long_qua_sau_bi_chan_bang_cau_co_dinh(fake, client):
    """GN-7 Soi Lỗi: thân lồng sâu không làm lọt ``RecursionError`` ở ``_known_body``."""
    body = client._body(SHAPES["day_page"], date(2026, 10, 30), TODAY, 0)
    nested: list = []
    cursor = nested
    for _ in range(100_000):
        cursor.append([])
        cursor = cursor[0]
    body["x"] = nested
    with pytest.raises(SearchConsoleError, match="không nằm trong danh sách"):
        client._send("POST", QUERY_URL, body)
    assert fake.requests == []


# ================================================================ «Kiểm tra», thuộc tính


def test_kiem_tra_dem_phan_ngoai_website(fake, client):
    def host_row(page, impressions):
        return {"keys": [page], "clicks": 0, "impressions": impressions, "position": 4.0}

    fake.on(
        "POST",
        QUERY_URL,
        answer(
            host_row(PAGE, 80),
            host_row(PREFIX, 10),
            host_row("https://www.staging-m.suachuacuasat.com/x/", 5),
            host_row("https://www.suachuacuasat.com/y/", 3),
            host_row("http://suachuacuasat.com/z/", 1),
            host_row("https://1.2.3.4/a/", 1),
            host_row("https://xn--bcher-kva.example/", 1),
        ),
    )
    result = client.check_hosts(date(2026, 10, 7), TODAY)
    assert (result.inside_impressions, result.outside_impressions) == (90, 11)
    assert result.hosts == (
        ("www.staging-m.suachuacuasat.com", 5),
        ("www.suachuacuasat.com", 3),
        ("suachuacuasat.com", 1),
    )
    assert result.dropped == 0 and result.truncated is False
    (body,) = sent_bodies(fake)
    assert "dimensionFilterGroups" not in body  # Q3 theo trang: không lọc (chỉ đếm)


def test_danh_sach_thuoc_tinh(fake, client):
    entries = [
        {"siteUrl": DOMAIN, "permissionLevel": "siteRestrictedUser"},
        {"siteUrl": PREFIX_PROPERTY, "permissionLevel": "siteFullUser"},
        {"siteUrl": "https://www.staging-m.suachuacuasat.com/", "permissionLevel": "siteOwner"},
        {"siteUrl": "http://suachuacuasat.com/", "permissionLevel": "siteRestrictedUser"},
        {"siteUrl": "https://suachuacuasat.com/blog/", "permissionLevel": "siteRestrictedUser"},
        {"siteUrl": "sc-domain:www.suachuacuasat.com", "permissionLevel": "siteUnverifiedUser"},
        {"siteUrl": "sc-domain:suachuacuasát.com", "permissionLevel": "siteOwner"},  # bỏ
        {"siteUrl": "sc-domain:x.example", "permissionLevel": "admin"},  # bỏ
        {"siteUrl": DOMAIN, "permissionLevel": "siteOwner"},  # trùng: bỏ
        {"siteUrl": "sc-domain:a b.example", "permissionLevel": "siteOwner"},  # bỏ
        {"siteUrl": "sc-domain:" + "a" * 400, "permissionLevel": "siteOwner"},  # bỏ
        {"permissionLevel": "siteOwner"},  # bỏ
        "x",  # bỏ
    ]
    fake.on("GET", SC_SITES, {"siteEntry": entries})
    result = client.list_sites()
    shown = [(e.site_url, e.kind, e.covers, e.usable) for e in result.entries]
    assert shown == [
        (DOMAIN, "domain", True, True),
        (PREFIX_PROPERTY, "prefix", True, True),
        ("https://www.staging-m.suachuacuasat.com/", "prefix", False, False),
        ("http://suachuacuasat.com/", "", False, False),
        ("https://suachuacuasat.com/blog/", "", False, False),
        ("sc-domain:www.suachuacuasat.com", "domain", False, False),
    ]
    assert result.skipped == 7


@pytest.mark.parametrize(
    "data", [{"siteEntry": "x"}, {"siteEntry": [{"siteUrl": DOMAIN}] * 201}, {"siteEntry": {}}]
)
def test_danh_sach_thuoc_tinh_sai_khuon(fake, client, data):
    fake.on("GET", SC_SITES, data)
    with pytest.raises(SearchConsoleError, match="không đúng dạng"):
        client.list_sites()


def test_danh_sach_thuoc_tinh_rong(fake, client):
    fake.on("GET", SC_SITES, {})
    assert client.list_sites().entries == ()


# ================================================================ ngày theo giờ Thái Bình Dương


@pytest.mark.parametrize(
    ("now", "expected"),
    [
        (datetime(2026, 11, 3, 7, 59, tzinfo=UTC), date(2026, 11, 2)),  # 23:59 PST
        (datetime(2026, 11, 3, 8, 0, tzinfo=UTC), date(2026, 11, 3)),  # 00:00 PST
        (datetime(2026, 7, 1, 6, 59, tzinfo=UTC), date(2026, 6, 30)),  # 23:59 PDT
        (datetime(2026, 7, 1, 7, 0, tzinfo=UTC), date(2026, 7, 1)),
        (datetime(2026, 3, 8, 9, 59, tzinfo=UTC), date(2026, 3, 8)),  # ngày đổi sang giờ hè
        (datetime(2026, 11, 1, 7, 30, tzinfo=UTC), date(2026, 11, 1)),  # ngày đổi về giờ đông
        (datetime(2026, 11, 3, 14, 59, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh")), date(2026, 11, 2)),
        (datetime(2026, 11, 3, 15, 0, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh")), date(2026, 11, 3)),
    ],
)
def test_hom_nay_theo_gio_thai_binh_duong(now, expected):
    assert today_pacific(now) == expected


def test_client_mac_dinh_dung_gio_thai_binh_duong(account, fake):
    client = SearchConsoleClient(account, WORDPRESS, session=make_session(fake))
    assert client._today is today_pacific
