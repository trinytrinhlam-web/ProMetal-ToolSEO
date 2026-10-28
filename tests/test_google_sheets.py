"""T-097: client Google Sheets, tách mã từ link, ghi ``GOOGLE_SHEET_ID`` vào ``.env``.

Điều kiện Lá Chắn: LC-T094-1 (không gọi Google thật), -2 (câu báo cố định), -12 (không lộ khóa,
mã truy cập), -13 (đường cố định, ``RAW``, ``:batchUpdate`` 4 loại, không chuyển hướng, giờ chờ,
≤ 2 MB, thử lại), -14 (chỉ file khóa đã kiểm), -15 (link, mã Sheet, ``.env``).
Google giả: ``tests/fake_google.py``; khóa RSA sinh lúc chạy test.
"""

from __future__ import annotations

import json
import os
from urllib.parse import parse_qs, quote, urlsplit

import google.auth.transport.requests
import pytest
import requests
from conftest import RealNetworkBlocked
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from fake_google import (
    ACCESS_TOKEN,
    EMAIL,
    SHEET_ID,
    SHEETS,
    TOKEN_URL,
    FakeGoogle,
    form,
    json_body,
    jwt_claims,
    key_info,
    make_session,
    new_private_key,
)

from seo_app import config, env_file
from seo_app.google import sheets
from seo_app.google.service_account import SHEETS_SCOPE, ServiceAccountError, load_service_account
from seo_app.google.sheets import (
    CellUpdate,
    SheetsClient,
    SheetsError,
    mask_sheet_id,
    sheet_id_from_link,
)

MOI = "LOI-MAY-CHU-GOOGLE-KHONG-DUOC-CHEP"
INFO_URL = SHEETS + SHEET_ID
READ_URL = f"{SHEETS}{SHEET_ID}/values/{quote(sheets.READ_RANGE, safe='')}"
UPDATE_URL = f"{SHEETS}{SHEET_ID}/values:batchUpdate"
APPEND_URL = f"{SHEETS}{SHEET_ID}/values/{quote(sheets.APPEND_RANGE, safe='')}:append"
STRUCTURE_URL = f"{SHEETS}{SHEET_ID}:batchUpdate"
PLAN_ID = 777


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
    return load_service_account(key_file, project_root=project)


@pytest.fixture
def fake():
    return FakeGoogle()


@pytest.fixture
def sleeps():
    return []


@pytest.fixture
def client(fake, account, sleeps):
    return SheetsClient(SHEET_ID, account, session=make_session(fake), sleep=sleeps.append)


def info_answer(*tabs):
    return {
        "properties": {"title": "Kế hoạch SEO", "locale": "vi_VN", "timeZone": "Asia/Saigon"},
        "sheets": [{"properties": {"sheetId": sid, "title": title}} for sid, title in tabs],
    }


def with_plan(fake, client):
    fake.on("GET", INFO_URL, info_answer((0, "Trang tính1"), (PLAN_ID, "KeHoach")))
    client.get_info()


def assert_no_secret(error):
    text = str(error.value)
    assert MOI not in text and SHEET_ID not in text and ACCESS_TOKEN not in text
    assert EMAIL not in text


# ================================================================ link và mã Sheet (LC-T094-15)


@pytest.mark.parametrize(
    "link",
    [
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit",
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit?gid=0#gid=0",
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}",
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/",
        f"https://docs.google.com/spreadsheets/u/1/d/{SHEET_ID}/edit#gid=123",
        f"  https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit?usp=sharing  ",
        SHEET_ID,
        f" {SHEET_ID}\n",
    ],
)
def test_tach_ma_tu_link_dung_dang(link):
    assert sheet_id_from_link(link) == SHEET_ID


@pytest.mark.parametrize(
    "link",
    [
        f"https://docs.google.com.evil.example/spreadsheets/d/{SHEET_ID}/edit",
        f"https://evil.example/docs.google.com/spreadsheets/d/{SHEET_ID}/edit",
        f"https://x@docs.google.com/spreadsheets/d/{SHEET_ID}/edit",
        f"https://docs.google.com@evil.example/spreadsheets/d/{SHEET_ID}/edit",
        f"https://docs.google.com:443/spreadsheets/d/{SHEET_ID}/edit",
        f"https://docs.google.com:8443/spreadsheets/d/{SHEET_ID}/edit",
        f"http://docs.google.com/spreadsheets/d/{SHEET_ID}/edit",
        f"https://DOCS.GOOGLE.COM/spreadsheets/d/{SHEET_ID}/edit",
        f"https://docs.google.com\\@evil.example/spreadsheets/d/{SHEET_ID}/edit",
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}\\edit",
        f"https://docs.google.com/document/d/{SHEET_ID}/edit",
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}%0aWORDPRESS_URL=x/edit",
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}\nGOOGLE_X=1",
        f"https://docs.goog\u0430le.com/spreadsheets/d/{SHEET_ID}/edit",  # chữ «а» Kirin
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID[:20]}/edit",  # mã quá ngắn
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}=/edit",
        f'https://docs.google.com/spreadsheets/d/{SHEET_ID}"/edit',
        f"javascript:alert('{SHEET_ID}')",
        f"//docs.google.com/spreadsheets/d/{SHEET_ID}/edit",
        f"docs.google.com/spreadsheets/d/{SHEET_ID}/edit",
        SHEET_ID + "#",
        SHEET_ID + " x",
        "",
        None,
        123,
    ],
)
def test_link_sai_dang_bi_tu_choi(link):
    with pytest.raises(SheetsError, match="link Google Sheet") as error:
        sheet_id_from_link(link)
    assert SHEET_ID not in str(error.value)


def test_che_ma_sheet():
    assert mask_sheet_id(SHEET_ID) == "…" + SHEET_ID[-4:]
    assert SHEET_ID[:-4] not in mask_sheet_id(SHEET_ID)
    assert mask_sheet_id("") == "…"


# ================================================================ ghi GOOGLE_SHEET_ID vào .env


ENV_TEXT = (
    "# cấu hình\n"
    "WORDPRESS_URL=https://example.com\n"
    "GOOGLE_SERVICE_ACCOUNT_FILE=C:/bi-mat/khoa.json\n"
    "GOOGLE_SHEET_ID=\n"
    "ANTHROPIC_API_KEY=sk-gia\n"
)


@pytest.fixture
def env_path(tmp_path):
    path = tmp_path / ".env"
    path.write_text(ENV_TEXT, encoding="utf-8", newline="")
    return path


def test_ghi_ma_sheet_giu_nguyen_dong_khac(env_path):
    env_file.set_google_sheet_id(f"  {SHEET_ID} ", env_path)
    text = env_path.read_text(encoding="utf-8")
    assert text == ENV_TEXT.replace("GOOGLE_SHEET_ID=\n", f"GOOGLE_SHEET_ID={SHEET_ID}\n")
    settings = config.load_settings(env_path, environ={})
    assert settings.google_sheet_id == SHEET_ID
    assert settings.wordpress_url == "https://example.com"
    if os.name != "nt":
        assert env_path.stat().st_mode & 0o777 == 0o600


def test_ghi_ma_sheet_khi_chua_co_dong(tmp_path):
    path = tmp_path / ".env"
    path.write_text("WORDPRESS_URL=https://example.com\n", encoding="utf-8")
    env_file.set_google_sheet_id(SHEET_ID, path)
    assert path.read_text(encoding="utf-8").splitlines() == [
        "WORDPRESS_URL=https://example.com",
        f"GOOGLE_SHEET_ID={SHEET_ID}",
    ]


def test_xoa_ma_sheet(env_path):
    env_file.set_google_sheet_id(SHEET_ID, env_path)
    env_file.clear_google_sheet_id(env_path)
    assert env_path.read_text(encoding="utf-8") == ENV_TEXT


@pytest.mark.parametrize(
    "value",
    [
        SHEET_ID + "\nWORDPRESS_URL=https://evil.example",
        SHEET_ID + "\rWORDPRESS_URL=https://evil.example",
        SHEET_ID + "=",
        SHEET_ID + '"',
        "'" + SHEET_ID + "'",
        SHEET_ID + " #ghi-chu",
        SHEET_ID + "$HOME",
        SHEET_ID + "\x00",
        SHEET_ID[:24],
        "a" * 101,
        SHEET_ID[:-1] + "ạ",
        SHEET_ID[:-1] + "\u200b",
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit",  # link: phải tách mã trước
        "",
        "   ",
        None,
        123,
    ],
)
def test_ma_sheet_sai_khong_ghi_gi(env_path, value):
    with pytest.raises(env_file.EnvFileError) as error:
        env_file.set_google_sheet_id(value, env_path)
    assert env_path.read_text(encoding="utf-8") == ENV_TEXT
    assert SHEET_ID[:20] not in str(error.value) and "evil" not in str(error.value)


def test_khong_ghi_duoc_bien_google_bang_ham_khoa_ai(env_path):
    for name in ("GOOGLE_SHEET_ID", "GOOGLE_SERVICE_ACCOUNT_FILE"):
        with pytest.raises(env_file.EnvFileError, match="Chỉ được ghi"):
            env_file.set_api_key(name, SHEET_ID, env_path)
    assert env_path.read_text(encoding="utf-8") == ENV_TEXT
    assert not [name for name in dir(env_file) if "service_account" in name.lower()]


def test_bo_kiem_ma_sheet_chat_hon_khoa_ai():
    """Giá trị khóa AI nhận được (``/ : + . ~``) vẫn bị bộ kiểm mã Sheet từ chối."""
    for suffix in ("/x", ":x", "+", ".x", "~"):
        value = SHEET_ID + suffix
        assert env_file.validate_key_value(value) == value
        with pytest.raises(env_file.EnvFileError):
            env_file.validate_sheet_id(value)


# ================================================================ from_settings


def test_from_settings_kiem_ma_sheet_truoc_moi_lenh(monkeypatch, key_file, fake):
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_FILE", str(key_file))
    for bad in ("", "ngan", SHEET_ID + "\x7f", SHEET_ID + "/../x"):
        monkeypatch.setenv("GOOGLE_SHEET_ID", bad)
        with pytest.raises(SheetsError, match="Mã Google Sheet") as error:
            SheetsClient.from_settings(session=make_session(fake))
        assert "ngan" not in str(error.value)
    assert fake.requests == []


def test_from_settings_kiem_lai_file_khoa_moi_lan(monkeypatch, key_file, fake):
    monkeypatch.setenv("GOOGLE_SHEET_ID", SHEET_ID)
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_FILE", str(key_file))
    client = SheetsClient.from_settings(session=make_session(fake))
    assert client.account_email == EMAIL
    key_file.write_text('{"type": "authorized_user"}', encoding="utf-8")  # file đổi sau đó
    with pytest.raises(ServiceAccountError):
        SheetsClient.from_settings(session=make_session(fake))
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_FILE", "")
    with pytest.raises(ServiceAccountError, match="Chưa khai báo"):
        SheetsClient.from_settings(session=make_session(fake))
    assert fake.requests == []


def test_from_settings_tu_choi_file_khoa_trong_thu_muc_anh(monkeypatch, key_file, fake):
    monkeypatch.setenv("GOOGLE_SHEET_ID", SHEET_ID)
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_FILE", str(key_file))
    monkeypatch.setenv("IMAGE_FOLDERS", str(key_file.parent))
    with pytest.raises(ServiceAccountError, match="thư mục ảnh"):
        SheetsClient.from_settings(session=make_session(fake))


def test_tao_client_sai_doi_so(account, fake):
    with pytest.raises(SheetsError):
        SheetsClient("sai", account, session=make_session(fake))
    with pytest.raises(SheetsError):
        SheetsClient(SHEET_ID, object(), session=make_session(fake))


# ================================================================ xin mã truy cập


def test_lenh_xin_ma_dung_chuan_va_ky_bang_khoa_trong_file(fake, client, private_key):
    fake.on("GET", INFO_URL, info_answer((PLAN_ID, "KeHoach")))
    client.get_info()
    (token_call,) = [(r, kw) for r, kw in fake.calls if r.url == TOKEN_URL]
    request, options = token_call
    assert request.method == "POST"
    assert "Authorization" not in request.headers  # không gửi kèm gì khác
    assert options["timeout"] <= 30
    body = form(request)
    assert body["grant_type"] == "urn:ietf:params:oauth:grant-type:jwt-bearer"
    header_b64, payload_b64, signature_b64 = body["assertion"].split(".")
    claims = jwt_claims(body["assertion"])
    assert claims["iss"] == EMAIL and claims["aud"] == TOKEN_URL
    assert claims["scope"] == SHEETS_SCOPE and "sub" not in claims
    import base64

    signature = base64.urlsafe_b64decode(signature_b64 + "=" * (-len(signature_b64) % 4))
    private_key.public_key().verify(
        signature,
        f"{header_b64}.{payload_b64}".encode(),
        padding.PKCS1v15(),
        hashes.SHA256(),
    )


def test_ma_truy_cap_dung_lai_trong_mot_client(fake, client):
    fake.on("GET", INFO_URL, info_answer((PLAN_ID, "KeHoach")))
    fake.on("GET", READ_URL, {"values": [["Mã bài"]]})
    client.get_info()
    client.read_plan_values()
    assert len(fake.token_requests()) == 1
    for request in fake.sheets_requests():
        assert request.headers["Authorization"] == f"Bearer {ACCESS_TOKEN}"


def test_chi_goi_dung_hai_may_chu_google(fake, client):
    """Không ``before_request``: không có lệnh tra «regional access boundary» tới
    ``iamcredentials.googleapis.com`` hay máy chủ nào khác."""
    fake.on("GET", INFO_URL, info_answer((PLAN_ID, "KeHoach")))
    client.get_info()
    hosts = {urlsplit(r.url).netloc for r in fake.requests}
    assert hosts == {"oauth2.googleapis.com", "sheets.googleapis.com"}


def test_repr_khong_lo_ma_truy_cap_ma_sheet_email(fake, client):
    fake.on("GET", INFO_URL, info_answer((PLAN_ID, "KeHoach")))
    client.get_info()
    shown = repr(client) + str(client) + repr(sheets._Bearer(ACCESS_TOKEN))
    assert ACCESS_TOKEN not in shown and SHEET_ID not in shown and EMAIL not in shown
    assert SHEET_ID[-4:] in repr(client)


@pytest.mark.parametrize(
    "answer",
    [
        (400, {"error": "invalid_grant", "error_description": MOI}, {}),
        (401, {"error": "invalid_client", "error_description": MOI}, {}),
        (200, {"token_type": "Bearer", "error_description": MOI}, {}),  # thiếu mã
        (200, b"<html>" + MOI.encode() + b"</html>", {}),
        (200, {"access_token": "ya29.ma\nX-Chen: 1", "expires_in": 3600}, {}),
        (302, {"x": MOI}, {"Location": "https://evil.example/token"}),
        (200, {"access_token": "x" * 70_000, "expires_in": 3600}, {}),  # > 64 KB
        requests.exceptions.ConnectTimeout(MOI),
        requests.exceptions.ConnectionError(MOI),
    ],
)
def test_loi_xin_ma_thanh_cau_co_dinh(fake, client, answer):
    fake.on("POST", TOKEN_URL, lambda _r: answer)
    fake.on("GET", INFO_URL, info_answer((PLAN_ID, "KeHoach")))
    with pytest.raises(SheetsError) as error:
        client.get_info()
    assert_no_secret(error)
    assert error.value.__cause__ is None
    assert fake.sheets_requests() == []  # không có mã thì không gọi Sheets
    redirects = [r for r in fake.requests if "evil.example" in r.url]
    assert redirects == []


def test_invalid_grant_co_cau_rieng(fake, client):
    fake.on("POST", TOKEN_URL, (400, {"error": "invalid_grant", "error_description": MOI}, {}))
    with pytest.raises(SheetsError, match="đồng hồ máy tính") as error:
        client.get_info()
    assert_no_secret(error)


def test_lop_chuyen_xin_ma_chi_nhan_dung_dia_chi(fake, account):
    transport = sheets._TokenRequest(make_session(fake), 30)
    import google.auth.exceptions

    for url, method in (("https://evil.example/token", "POST"), (TOKEN_URL, "GET")):
        with pytest.raises(google.auth.exceptions.TransportError):
            transport(url, method=method, body=b"x")
    with pytest.raises(google.auth.exceptions.TransportError):
        transport(TOKEN_URL, method="POST", body=b"x", verify=False)
    assert fake.requests == []


def test_lop_chuyen_bo_qua_gio_cho_120_giay_cua_thu_vien(fake):
    transport = sheets._TokenRequest(make_session(fake), 30)
    transport(TOKEN_URL, method="POST", body=b"grant_type=x", timeout=120)
    ((_request, options),) = fake.calls
    assert options["timeout"] == 30


# ================================================================ get_info


def test_get_info_doc_ten_va_tab_ke_hoach(fake, client):
    fake.on("GET", INFO_URL, info_answer((0, "Trang tính1"), (PLAN_ID, "KeHoach")))
    info = client.get_info()
    assert info.title == "Kế hoạch SEO" and info.time_zone == "Asia/Saigon"
    assert info.plan_tab == sheets.SheetTab(PLAN_ID, "KeHoach")
    (request,) = fake.sheets_requests()
    assert parse_qs(urlsplit(request.url).query) == {"fields": [sheets.INFO_FIELDS]}


@pytest.mark.parametrize("title", ["KeHoach ", "kehoach", "KeHoạch", "KeHoach\u200b", "Ke Hoach"])
def test_tab_ten_gan_giong_khong_phai_tab_ke_hoach(fake, client, title):
    fake.on("GET", INFO_URL, info_answer((5, title)))
    assert client.get_info().plan_tab is None


def test_ten_sheet_bo_ky_tu_dieu_khien_va_doi_huong(fake, client):
    answer = info_answer((PLAN_ID, "KeHoach"))
    answer["properties"]["title"] = "Kế\u202ehoạch\u200b\x07 SEO\n[x](javascript:1)"
    fake.on("GET", INFO_URL, answer)
    title = client.get_info().title
    assert "\u202e" not in title and "\u200b" not in title and "\x07" not in title
    assert "\n" not in title


@pytest.mark.parametrize(
    "answer",
    [
        [],
        {"sheets": []},
        {"properties": {}, "sheets": "x"},
        {"properties": {}, "sheets": [{"properties": {"sheetId": "1", "title": "A"}}]},
        {"properties": {}, "sheets": [{"properties": {"sheetId": True, "title": "A"}}]},
        {"properties": {}, "sheets": [{"properties": {"sheetId": 1, "title": 5}}]},
        {"properties": {}, "sheets": [{"properties": {"sheetId": 1, "title": "KeHoach"}},
                                      {"properties": {"sheetId": 2, "title": "KeHoach"}}]},
    ],
)
def test_get_info_khuon_la_bao_loi(fake, client, answer):
    fake.on("GET", INFO_URL, answer)
    with pytest.raises(SheetsError, match="không đúng dạng"):
        client.get_info()


# ================================================================ read_plan_values


def test_doc_ke_hoach_mot_lenh_dung_tham_so(fake, client):
    fake.on("GET", READ_URL, {"range": "KeHoach!A1:Z1001", "majorDimension": "ROWS",
                              "values": [["Mã bài", "Từ khóa chính"], [], ["B01", 46000.0, True]]})
    rows = client.read_plan_values()
    assert rows == (("Mã bài", "Từ khóa chính"), (), ("B01", 46000.0, True))
    (request,) = fake.sheets_requests()
    assert request.method == "GET"
    query = {name: values[0] for name, values in parse_qs(urlsplit(request.url).query).items()}
    assert query == {
        "valueRenderOption": "UNFORMATTED_VALUE",
        "dateTimeRenderOption": "SERIAL_NUMBER",
        "majorDimension": "ROWS",
    }
    assert urlsplit(request.url).path == urlsplit(READ_URL).path


@pytest.mark.parametrize(
    "values",
    [
        [["a"] * 27],  # quá 26 cột
        [["a"]] * 1002,  # quá 1.001 dòng
        [[{"formula": "=1"}]],
        [[["lồng"]]],
        [[None]],
        "abc",
        [["a"], "b"],
    ],
)
def test_doc_khuon_la_bao_loi(fake, client, values):
    fake.on("GET", READ_URL, {"values": values})
    with pytest.raises(SheetsError, match="không đúng dạng"):
        client.read_plan_values()


def test_doc_429_thu_lai_3_lan_roi_bao_loi(fake, client, sleeps):
    fake.on("GET", READ_URL, (429, {"error": {"message": MOI}}, {}))
    with pytest.raises(SheetsError, match="giới hạn số lần gọi") as error:
        client.read_plan_values()
    assert_no_secret(error)
    assert len(fake.sheets_requests()) == 4
    assert len(sleeps) == 3
    assert [round(s) for s in sleeps] == [1, 2, 4] or all(1 <= s <= 4.5 for s in sleeps)
    assert sleeps == sorted(sleeps)


def test_doc_429_mot_lan_roi_thanh_cong(fake, client, sleeps):
    answers = iter([(429, {}, {}), {"values": [["Mã bài"]]}])
    fake.on("GET", READ_URL, lambda _r: next(answers))
    assert client.read_plan_values() == (("Mã bài",),)
    assert len(sleeps) == 1 and 1 <= sleeps[0] <= 1.5


# ================================================================ update_cells (RAW)


def test_ghi_o_luon_raw_vung_tu_chi_so_cot(fake, client):
    fake.on("POST", UPDATE_URL, {"totalUpdatedCells": 2})
    result = client.update_cells(
        [CellUpdate(5, 8, "Đã gửi nháp"), CellUpdate(5, 15, "=IMPORTXML(\"https://x\")")]
    )
    assert result == 2
    (request,) = fake.sheets_requests()
    assert urlsplit(request.url).query == ""
    assert json_body(request) == {
        "valueInputOption": "RAW",
        "includeValuesInResponse": False,
        "data": [
            {"range": "'KeHoach'!I5", "majorDimension": "ROWS", "values": [["Đã gửi nháp"]]},
            {"range": "'KeHoach'!P5", "majorDimension": "ROWS",
             "values": [['=IMPORTXML("https://x")']]},
        ],
    }


@pytest.mark.parametrize(
    "updates",
    [
        [],
        [CellUpdate(0, 0, "x")],
        [CellUpdate(1002, 0, "x")],
        [CellUpdate(1, 26, "x")],
        [CellUpdate(1, -1, "x")],
        [CellUpdate(True, 0, "x")],
        [CellUpdate(1, 0, None)],
        [CellUpdate(1, 0, {"x": 1})],
        [CellUpdate(1, 0, float("nan"))],
        [CellUpdate(1, 0, "x" * 2001)],
        [CellUpdate(1, 0, "x")] * 201,
        [("1", "A", "x")],
        "abc",
    ],
)
def test_ghi_o_du_lieu_sai_khong_gui(fake, client, updates):
    with pytest.raises(SheetsError):
        client.update_cells(updates)
    assert fake.requests == []  # kiểm trước, kể cả lệnh xin mã


def test_ghi_o_429_thu_lai_dung_1_lan(fake, client, sleeps):
    fake.on("POST", UPDATE_URL, (429, {}, {}))
    with pytest.raises(SheetsError, match="429"):
        client.update_cells([CellUpdate(2, 0, "x")])
    assert len(fake.sheets_requests()) == 2 and len(sleeps) == 1


@pytest.mark.parametrize(
    ("answer", "unsure"),
    [
        ((500, {"error": {"message": MOI}}, {}), True),
        ((503, b"<html>" + MOI.encode(), {}), True),
        (requests.exceptions.ReadTimeout(MOI), True),
        (requests.exceptions.ConnectionError(MOI), True),
        ((200, b"khong-phai-json " + MOI.encode(), {}), True),
        ((403, {"error": {"message": MOI}}, {}), False),
        ((404, {"error": {"message": MOI}}, {}), False),
        ((400, {"error": {"message": MOI}}, {}), False),
    ],
)
def test_ghi_o_loi_co_cau_co_dinh_va_co_unsure(fake, client, answer, unsure):
    fake.on("POST", UPDATE_URL, lambda _r: answer)
    with pytest.raises(SheetsError) as error:
        client.update_cells([CellUpdate(2, 0, "x")])
    assert_no_secret(error)
    assert error.value.unsure is unsure
    assert error.value.__cause__ is None


def test_cau_bao_403_huong_dan_chia_se(fake, client):
    fake.on("POST", UPDATE_URL, (403, {"error": {"message": MOI}}, {}))
    with pytest.raises(SheetsError, match="chia sẻ Sheet cho") as error:
        client.update_cells([CellUpdate(2, 0, "x")])
    assert error.value.status_code == 403


# ================================================================ append_row


def test_them_dong_raw_insert_rows_tra_so_dong(fake, client):
    fake.on("POST", APPEND_URL, {"updates": {"updatedRange": "KeHoach!A12:C12"}})
    assert client.append_row(["B09", "cửa cuốn", 46000]) == 12
    (request,) = fake.sheets_requests()
    query = {name: values[0] for name, values in parse_qs(urlsplit(request.url).query).items()}
    assert query == {"valueInputOption": "RAW", "insertDataOption": "INSERT_ROWS",
                     "includeValuesInResponse": "false"}
    assert json_body(request) == {"majorDimension": "ROWS", "values": [["B09", "cửa cuốn", 46000]]}


@pytest.mark.parametrize(
    "answer",
    [(429, {}, {}), (500, {}, {}), requests.exceptions.ReadTimeout("x")],
)
def test_them_dong_khong_bao_gio_tu_thu_lai(fake, client, sleeps, answer):
    fake.on("POST", APPEND_URL, lambda _r: answer)
    with pytest.raises(SheetsError) as error:
        client.append_row(["B09"])
    assert len(fake.sheets_requests()) == 1 and sleeps == []
    assert error.value.unsure is (answer != (429, {}, {}))


@pytest.mark.parametrize("values", [[], ["a"] * 27, "abc", [None], [["x"]], [float("inf")]])
def test_them_dong_du_lieu_sai_khong_gui(fake, client, values):
    with pytest.raises(SheetsError):
        client.append_row(values)
    assert fake.requests == []


@pytest.mark.parametrize("updated", ["Khac!A12:C12", "KeHoach!B12:C12", 12, None])
def test_them_dong_tra_loi_la_thi_khong_doan_so_dong(fake, client, updated):
    fake.on("POST", APPEND_URL, {"updates": {"updatedRange": updated}})
    assert client.append_row(["B09"]) is None


# ================================================================ batch_update (4 loại, đúng tab)


def grid(sheet_id=PLAN_ID, **extra):
    return {"sheetId": sheet_id, **extra}


ALLOWED_STRUCTURE = [
    {"updateSheetProperties": {"properties": {"sheetId": PLAN_ID,
                                              "gridProperties": {"frozenRowCount": 1}},
                               "fields": "gridProperties.frozenRowCount"}},
    {"repeatCell": {"range": grid(startRowIndex=1, startColumnIndex=6, endColumnIndex=7),
                    "cell": {"userEnteredFormat": {"numberFormat": {"type": "DATE",
                                                                    "pattern": "dd/mm/yyyy"}}},
                    "fields": "userEnteredFormat.numberFormat"}},
    {"setDataValidation": {"range": grid(startRowIndex=1, startColumnIndex=8,
                                         endColumnIndex=9),
                           "rule": {"condition": {"type": "ONE_OF_LIST", "values": [
                               {"userEnteredValue": "Chưa viết"},
                               {"userEnteredValue": "Đã gửi nháp"}]},
                               "strict": True, "showCustomUi": True}}},
]


def test_sua_cau_truc_dung_4_loai_tren_tab_ke_hoach(fake, client):
    with_plan(fake, client)
    fake.on("POST", STRUCTURE_URL, {"replies": [{}, {}, {}]})
    assert client.batch_update(ALLOWED_STRUCTURE) == ({}, {}, {})
    request = fake.sheets_requests()[-1]
    assert json_body(request) == {"requests": ALLOWED_STRUCTURE}


def test_tao_tab_ke_hoach_khi_chua_co(fake, client):
    fake.on("GET", INFO_URL, info_answer((0, "Trang tính1")))
    client.get_info()
    fake.on("POST", STRUCTURE_URL, {"replies": [{"addSheet": {"properties": {"sheetId": 9}}}]})
    add = {"addSheet": {"properties": {"title": "KeHoach",
                                       "gridProperties": {"frozenRowCount": 1}}}}
    client.batch_update([add])
    # Sau khi sửa cấu trúc phải đọc lại mới sửa tiếp được.
    with pytest.raises(SheetsError, match="ngay trước khi sửa cấu trúc"):
        client.batch_update(ALLOWED_STRUCTURE[:1])


def test_sua_cau_truc_phai_doc_thong_tin_truoc(fake, client):
    with pytest.raises(SheetsError, match="ngay trước khi sửa cấu trúc"):
        client.batch_update(ALLOWED_STRUCTURE)
    assert fake.requests == []


FORBIDDEN_STRUCTURE = [
    {"deleteSheet": {"sheetId": PLAN_ID}},
    {"deleteDimension": {"range": {"sheetId": PLAN_ID, "dimension": "ROWS", "startIndex": 1,
                                   "endIndex": 5}}},
    {"deleteRange": {"range": grid(), "shiftDimension": "ROWS"}},
    {"updateSpreadsheetProperties": {"properties": {"title": "x"}, "fields": "title"}},
    {"duplicateSheet": {"sourceSheetId": PLAN_ID}},
    {"addProtectedRange": {"protectedRange": {"range": grid()}}},
    {"updateCells": {"range": grid(), "rows": [], "fields": "*"}},
    {"appendCells": {"sheetId": PLAN_ID, "rows": [], "fields": "*"}},
    # updateSheetProperties chỉ được cố định dòng tiêu đề:
    {"updateSheetProperties": {"properties": {"sheetId": PLAN_ID, "title": "Khac"},
                               "fields": "title"}},
    {"updateSheetProperties": {"properties": {"sheetId": PLAN_ID,
                                              "gridProperties": {"frozenRowCount": 1}},
                               "fields": "*"}},
    {"updateSheetProperties": {"properties": {"sheetId": 0,
                                              "gridProperties": {"frozenRowCount": 1}},
                               "fields": "gridProperties.frozenRowCount"}},
    # repeatCell không được ghi giá trị ô (đường vòng qua RAW):
    {"repeatCell": {"range": grid(),
                    "cell": {"userEnteredValue": {"formulaValue": "=IMPORTXML(\"x\",\"y\")"}},
                    "fields": "userEnteredValue"}},
    {"repeatCell": {"range": grid(),
                    "cell": {"userEnteredFormat": {"numberFormat": {"type": "DATE"}},
                             "userEnteredValue": {"stringValue": "x"}},
                    "fields": "userEnteredFormat.numberFormat"}},
    {"repeatCell": {"range": grid(0), "cell": {"userEnteredFormat": {
        "numberFormat": {"type": "DATE"}}}, "fields": "userEnteredFormat.numberFormat"}},
    {"repeatCell": {"range": grid(), "cell": {"userEnteredFormat": {
        "numberFormat": {"type": "DATE", "pattern": "=1"}}},
        "fields": "userEnteredFormat.numberFormat"}},
    # setDataValidation chỉ danh sách chữ cố định:
    {"setDataValidation": {"range": grid(), "rule": {"condition": {
        "type": "ONE_OF_RANGE", "values": [{"userEnteredValue": "=Khac!A1:A9"}]}}}},
    {"setDataValidation": {"range": grid(), "rule": {"condition": {
        "type": "CUSTOM_FORMULA", "values": [{"userEnteredValue": "=IMPORTXML(1)"}]}}}},
    {"setDataValidation": {"range": grid(), "rule": {"condition": {
        "type": "ONE_OF_LIST", "values": [{"userEnteredValue": "=IMPORTXML(1)"}]}}}},
    {"setDataValidation": {"range": grid(1), "rule": {"condition": {
        "type": "ONE_OF_LIST", "values": [{"userEnteredValue": "A"}]}}}},
    # addSheet khi tab đã có, hay tên khác:
    {"addSheet": {"properties": {"title": "KeHoach"}}},
    {"addSheet": {"properties": {"title": "Khac"}}},
    # vùng sai:
    {"repeatCell": {"range": grid(startRowIndex=5, endRowIndex=2), "cell": {"userEnteredFormat": {
        "numberFormat": {"type": "DATE"}}}, "fields": "userEnteredFormat.numberFormat"}},
    {"repeatCell": {"range": grid(startColumnIndex=0, endColumnIndex=99), "cell": {
        "userEnteredFormat": {"numberFormat": {"type": "DATE"}}},
        "fields": "userEnteredFormat.numberFormat"}},
    {"repeatCell": {"range": {"sheetId": PLAN_ID, "dimension": "x"}, "cell": {
        "userEnteredFormat": {"numberFormat": {"type": "DATE"}}},
        "fields": "userEnteredFormat.numberFormat"}},
    {"updateSheetProperties": ALLOWED_STRUCTURE[0]["updateSheetProperties"],
     "deleteSheet": {"sheetId": PLAN_ID}},  # hai loại trong một yêu cầu
    "deleteSheet",
]


@pytest.mark.parametrize("request_", FORBIDDEN_STRUCTURE)
def test_yeu_cau_cau_truc_ngoai_danh_sach_khong_gui(fake, client, request_):
    with_plan(fake, client)
    before = len(fake.requests)
    with pytest.raises(SheetsError, match="không nằm trong danh sách"):
        client.batch_update([*ALLOWED_STRUCTURE[:1], request_])
    assert len(fake.requests) == before


def test_qua_nhieu_yeu_cau_cau_truc(fake, client):
    with_plan(fake, client)
    with pytest.raises(SheetsError, match="không nằm trong danh sách"):
        client.batch_update(ALLOWED_STRUCTURE[:1] * 51)
    with pytest.raises(SheetsError):
        client.batch_update([])


def test_sua_cau_truc_khong_tu_thu_lai(fake, client, sleeps):
    with_plan(fake, client)
    fake.on("POST", STRUCTURE_URL, (429, {}, {}))
    with pytest.raises(SheetsError):
        client.batch_update(ALLOWED_STRUCTURE[:1])
    assert len([r for r in fake.sheets_requests() if r.url == STRUCTURE_URL]) == 1
    assert sleeps == []


# ================================================================ lớp kiểm chung (_send)


@pytest.mark.parametrize(
    ("method", "path", "params", "body"),
    [
        # USER_ENTERED ở lớp kiểm, không chỉ ở nơi gọi:
        ("POST", f"{SHEET_ID}/values:batchUpdate", {}, {
            "valueInputOption": "USER_ENTERED", "includeValuesInResponse": False,
            "data": [{"range": "'KeHoach'!A2", "majorDimension": "ROWS", "values": [["=1"]]}]}),
        ("POST", f"{SHEET_ID}/values/{quote(sheets.APPEND_RANGE, safe='')}:append",
         {**sheets._APPEND_PARAMS, "valueInputOption": "USER_ENTERED"},
         {"majorDimension": "ROWS", "values": [["=1"]]}),
        # Vùng ô không dựng từ hằng tab:
        ("POST", f"{SHEET_ID}/values:batchUpdate", {}, {
            "valueInputOption": "RAW", "includeValuesInResponse": False,
            "data": [{"range": "'Khac'!A2", "majorDimension": "ROWS", "values": [["x"]]}]}),
        ("POST", f"{SHEET_ID}/values:batchUpdate", {}, {
            "valueInputOption": "RAW", "includeValuesInResponse": False,
            "data": [{"range": "'KeHoach'!A1:Z9", "majorDimension": "ROWS",
                      "values": [["x"]]}]}),
        ("GET", f"{SHEET_ID}/values/{quote('Khac!A1:Z9', safe='')}", sheets._READ_PARAMS, None),
        # Đường, phương thức, tham số lạ:
        ("GET", f"{SHEET_ID}/values:batchGet", {}, None),
        ("POST", f"{SHEET_ID}/values:batchClear", {}, {"ranges": ["'KeHoach'!A1:Z9"]}),
        ("POST", f"{SHEET_ID}/values/{quote(sheets.READ_RANGE, safe='')}:clear", {}, {}),
        ("DELETE", SHEET_ID, {}, None),
        ("PUT", f"{SHEET_ID}/values/{quote(sheets.APPEND_RANGE, safe='')}", {}, None),
        ("GET", SHEET_ID, {"fields": "*"}, None),
        ("GET", SHEET_ID, {"fields": sheets.INFO_FIELDS, "includeGridData": "true"}, None),
        ("GET", SHEET_ID, {}, None),
        ("GET", f"{SHEET_ID}/values/{quote(sheets.READ_RANGE, safe='')}",
         {**sheets._READ_PARAMS, "valueRenderOption": "FORMULA"}, None),
        ("GET", "1ZzZzZzZzZzZzZzZzZzZzZzZzZz", {"fields": sheets.INFO_FIELDS}, None),  # Sheet khác
        ("GET", f"{SHEET_ID}/../{SHEET_ID}", {"fields": sheets.INFO_FIELDS}, None),
        ("GET", f"{SHEET_ID}?fields=*", {"fields": sheets.INFO_FIELDS}, None),
        ("POST", f"{SHEET_ID}/values:batchUpdate", {"key": "x"}, {}),
    ],
)
def test_lop_kiem_chan_truoc_khi_gui(fake, client, method, path, params, body):
    with pytest.raises(SheetsError, match="không nằm trong danh sách"):
        client._send(method, path, params=params, body=body)
    assert fake.requests == []


def test_moi_lenh_co_gio_cho_va_khong_theo_chuyen_huong(fake, client):
    fake.on("GET", INFO_URL, info_answer((PLAN_ID, "KeHoach")))
    fake.on("GET", READ_URL, {"values": []})
    fake.on("POST", UPDATE_URL, {"totalUpdatedCells": 1})
    fake.on("POST", APPEND_URL, {"updates": {"updatedRange": "KeHoach!A3:A3"}})
    session = client._session
    sent: list[dict] = []
    original = session.request

    def spy(method, url, **kwargs):  # ghi lại đúng tùy chọn mỗi lệnh truyền cho requests
        sent.append({"url": url, **kwargs})
        return original(method, url, **kwargs)

    session.request = spy  # lớp chuyển xin mã dùng chung phiên này
    client.get_info()
    client.read_plan_values()
    client.update_cells([CellUpdate(2, 0, "x")])
    client.append_row(["x"])
    assert len(sent) == len(fake.calls) == 5  # 1 lệnh xin mã + 4 lệnh Sheets
    assert sent[0]["url"] == TOKEN_URL
    for options in sent:
        assert 0 < options["timeout"] <= 30
        assert options["allow_redirects"] is False and options["stream"] is True
        assert isinstance(options["auth"], sheets._NoAuth | sheets._Bearer)  # không lấy .netrc
    assert session.max_redirects == 0


def test_chuyen_huong_cua_sheets_khong_di_theo(fake, client):
    fake.on("GET", INFO_URL, (302, b"", {"Location": "https://evil.example/x"}))
    with pytest.raises(SheetsError, match="chuyển hướng") as error:
        client.get_info()
    assert "evil" not in str(error.value)
    assert all("evil" not in r.url for r in fake.requests)


@pytest.mark.parametrize("declared", [True, False])
def test_cau_tra_loi_qua_2_mb_bi_bo(fake, client, declared):
    big = json.dumps({"values": [["x" * 1000]] * 3000}).encode()  # ~3 MB
    headers = {"Content-Length": str(len(big))} if declared else {}
    fake.on("GET", READ_URL, (200, big, headers))
    with pytest.raises(SheetsError, match="lớn bất thường"):
        client.read_plan_values()


def test_json_long_qua_sau_khong_lam_sap(fake, client):
    fake.on("GET", READ_URL, (200, b"[" * 100_000 + b"]" * 100_000, {}))
    with pytest.raises(SheetsError, match="không đúng dạng"):
        client.read_plan_values()


# ================================================================ bộ chặn mạng (LC-T094-1)


def test_bo_chan_mang_chan_ca_client_sheets_khong_co_site_gia(account):
    client = SheetsClient(SHEET_ID, account)  # phiên requests thật, không gắn Google giả
    with pytest.raises(RealNetworkBlocked):
        client.get_info()


def test_bo_chan_mang_chan_ca_lop_chuyen_mac_dinh_cua_google_auth(account):
    """Nếu ai đó lỡ dùng lớp chuyển của thư viện (đường đợi 120 giây), test vẫn không ra mạng."""
    with pytest.raises((RealNetworkBlocked, Exception)) as error:
        account.credentials.refresh(google.auth.transport.requests.Request())
    chain, current = [], error.value
    while current is not None:
        chain.append(current)
        current = current.__cause__ or current.__context__
    assert any(isinstance(item, RealNetworkBlocked) for item in chain)
