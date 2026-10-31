r"""Soi Lỗi T-099 (rút gọn): client WordPress hẹn giờ, đăng ngay, đọc trạng thái bài.

Kiểm độc lập (không dùng ``FakeWordPress`` hay hàm dựng site của Thợ Máy): website giả ``_WpSite``
giữ **trạng thái bài như WordPress thật** (tạo nháp, đọc, đổi trạng thái), có đồng hồ máy chủ riêng
(header ``Date``) và làm đúng luật ``wp_insert_post``: bài ``future`` có giờ chưa tới 60 giây sau
giờ máy chủ (kể cả giờ đã qua) thành ``publish`` ngay. Mỗi ca kiểm cả **trạng thái bài trên site**
trước và sau, không chỉ câu báo.

1. Chỉ nháp do chính client tạo, đúng mã, mới được hẹn giờ/đăng: bài người khác, bài đã đăng, đã
   hẹn, chờ duyệt, riêng tư, trong thùng rác, bài bị xóa, mã lạ, mã quá lớn → không lệnh ghi nào.
2. Không gửi lại khi không chắc: mất mạng, hết giờ, 3xx, 5xx, trả lời lạ, trả lời đúng mà thiếu
   trường → đúng một lệnh chuyển, lần gọi sau không gửi gì.
3. Giờ hẹn: múi giờ, giờ đã qua, quá gần, quá xa, lệch đồng hồ, header ``Date`` lạ, giờ mùa hè,
   dạng ``date_gmt``.
4. Không đường nào khác đổi ``status``/gửi ``date_gmt``: thử gọi thẳng ``_request`` với dấu giả,
   khuôn sai.
5. ``post_statuses`` chỉ đọc; ``ConnectionInfo`` múi giờ site lạ.

Không gọi website thật (bộ chặn mạng của ``tests/conftest.py`` bật suốt).
"""

from __future__ import annotations

import io
import json
import threading
from datetime import UTC, date, datetime, time, timedelta, timezone
from email.utils import format_datetime
from urllib.parse import parse_qs, urlsplit
from zoneinfo import ZoneInfo

import pytest
import requests
from requests.adapters import BaseAdapter
from requests.structures import CaseInsensitiveDict

import seo_app.wordpress.client as wp
from seo_app.publish import schedule
from seo_app.wordpress.client import (
    MAX_ID,
    ReleaseError,
    WordPressClient,
    WordPressError,
)

BASE = "https://example.com"
API = "/wp-json/wp/v2"
SERVER_NOW = datetime(2026, 11, 2, 1, 0, 0, tzinfo=UTC)  # Thứ Hai 02/11/2026 08:00 giờ VN
VN = ZoneInfo("Asia/Ho_Chi_Minh")
MAT_KHAU_GIA = "abcd efgh ijkl mnop"  # Application Password giả
MOI = "MOI-T099 <b>evil</b> https://evil.example"


MODIFIED = "2026-11-01T23:50:00"  # T-115: ``modified_gmt`` giả (Chỉ Huy duyệt 31/10)


def http_date(when: datetime) -> str:
    return format_datetime(when.astimezone(UTC), usegmt=True)


class _WpSite(BaseAdapter):
    """WordPress giả có trạng thái: bài, đồng hồ máy chủ, luật ``future`` sát giờ thành
    ``publish``. ``inject``: (phương thức, đường) → câu trả lời/ngoại lệ thay cho hành vi thường."""

    def __init__(self) -> None:
        super().__init__()
        self.posts: dict[int, dict] = {}
        self.server_now = SERVER_NOW
        self.date_header: str | None = None  # None: theo server_now; "": không gửi header
        self.inject: dict[tuple[str, str], object] = {}
        self.requests: list[requests.PreparedRequest] = []
        self.next_id = 42

    # ------------------------------------------------------------------ hành vi WordPress
    def _answer(self, request: requests.PreparedRequest):
        parts = urlsplit(request.url)
        path = parts.path
        if (request.method, path) in self.inject:
            answer = self.inject[(request.method, path)]
            return answer(request) if callable(answer) else answer
        if request.method == "POST" and path == f"{API}/posts":
            post_id, self.next_id = self.next_id, self.next_id + 1
            self.posts[post_id] = {"status": "draft", "date_gmt": "", "author": "app"}
            return 201, {"id": post_id, "status": "draft", "title": {"raw": "Bài"},
                         "modified_gmt": MODIFIED}  # T-115
        if path.startswith(f"{API}/posts/"):
            post_id = int(path.rsplit("/", 1)[1])
            post = self.posts.get(post_id)
            if post is None:
                return 404, {"code": "rest_post_invalid_id", "message": MOI}
            if request.method == "GET":
                return 200, {"id": post_id, "status": post["status"],
                             "modified_gmt": MODIFIED}  # T-115
            sent = json.loads(request.body)
            if "status" in sent:
                post["status"] = sent["status"]
            if "date_gmt" in sent:
                post["date_gmt"] = sent["date_gmt"]
            if post["status"] == "future":  # wp_insert_post: giờ < 60 giây sau giờ máy chủ
                when = datetime.fromisoformat(post["date_gmt"]).replace(tzinfo=UTC)
                if when - self.server_now < timedelta(seconds=60):
                    post["status"] = "publish"
            if post["status"] == "publish" and not post["date_gmt"]:
                post["date_gmt"] = self.server_now.strftime("%Y-%m-%dT%H:%M:%S")
            return 200, {"id": post_id, "status": post["status"], "date_gmt": post["date_gmt"],
                         "link": f"{BASE}/?p={post_id}"}
        if request.method == "GET" and path == f"{API}/posts":
            asked = {int(x) for x in parse_qs(parts.query)["include"][0].split(",")}
            return 200, [{"id": i, "status": p["status"], "date_gmt": p["date_gmt"] or
                          "2026-11-01T00:00:00", "modified_gmt": "2026-11-01T00:00:00",
                          "link": f"{BASE}/?p={i}"} for i, p in self.posts.items() if i in asked]
        return 404, {"code": "rest_no_route", "message": MOI}

    def send(self, request, **kwargs):
        self.requests.append(request)
        answer = self._answer(request)
        if isinstance(answer, BaseException):
            raise answer
        status, body, *rest = answer
        headers = dict(rest[0]) if rest else {}
        if self.date_header is None:
            headers.setdefault("Date", http_date(self.server_now))
        elif self.date_header:
            headers.setdefault("Date", self.date_header)
        response = requests.Response()
        response.status_code = status
        response._content = body if isinstance(body, bytes) else json.dumps(body).encode()
        response.headers = CaseInsensitiveDict(
            {"Content-Type": "application/json; charset=UTF-8", **headers})
        response.encoding = "utf-8"
        response.url = request.url
        response.request = request
        return response

    def close(self) -> None:
        pass

    # ------------------------------------------------------------------ tiện ích
    def writes(self) -> list[tuple[str, str]]:
        return [(r.method, urlsplit(r.url).path) for r in self.requests if r.method != "GET"]


@pytest.fixture(autouse=True)
def local_clock(monkeypatch):
    monkeypatch.setattr(wp, "_utc_now", lambda: SERVER_NOW)


@pytest.fixture
def site() -> _WpSite:
    return _WpSite()


def new_client(site: _WpSite) -> WordPressClient:
    session = requests.Session()
    session.mount("https://", site)
    session.mount("http://", site)
    return WordPressClient(BASE, "lam", MAT_KHAU_GIA, session=session, write_seo=True)


@pytest.fixture
def client(site) -> WordPressClient:
    return new_client(site)


def draft(client: WordPressClient) -> int:
    return client.create_draft("Cổng inox", "<p>Nội dung</p>").id


def vn(day: int, hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 11, day, hour, minute, tzinfo=VN)


# ================================================================ 1. chạy đúng, trạng thái thật
def test_hen_gio_doi_trang_thai_dung_va_chi_mot_lenh_chuyen(site, client):
    post_id = draft(client)
    result = client.release_draft(post_id, mode="future", when_utc=vn(3, 8))
    assert site.posts[post_id] == {"status": "future", "date_gmt": "2026-11-03T01:00:00",
                                   "author": "app"}
    assert (result.status, result.date_gmt) == ("future", "2026-11-03T01:00:00")
    release = [r for r in site.requests if r.method == "POST" and r.url.endswith(
        f"{post_id}?_fields=id%2Cstatus%2Cdate_gmt%2Clink")]
    assert len(release) == 1 and json.loads(release[0].body) == {
        "status": "future", "date_gmt": "2026-11-03T01:00:00"}
    check = [r for r in site.requests if r.method == "GET"]
    assert len(check) == 1 and parse_qs(urlsplit(check[0].url).query) == {
        "context": ["edit"], "_fields": ["id,status,modified_gmt"]}  # T-115
    assert site.requests.index(check[0]) == len(site.requests) - 2  # kiểm ngay trước lệnh


def test_dang_ngay_doi_trang_thai_dung(site, client):
    post_id = draft(client)
    result = client.release_draft(post_id, mode="publish")
    assert site.posts[post_id]["status"] == "publish" and result.status == "publish"
    assert json.loads(site.requests[-1].body) == {"status": "publish"}


def test_sau_khi_chuyen_moi_lenh_ghi_vao_bai_deu_bi_chan(site, client):
    post_id = draft(client)
    client.release_draft(post_id, mode="future", when_utc=vn(3, 8))
    before = len(site.requests)
    for call in (
        lambda: client.release_draft(post_id, mode="publish"),
        lambda: client.release_draft(post_id, mode="future", when_utc=vn(4, 8)),
        lambda: client.set_featured_image(post_id, 7),
        lambda: client.set_seo_meta(post_id, title="Cổng inox đẹp"),
    ):
        with pytest.raises(WordPressError):
            call()
    assert len(site.requests) == before
    assert site.posts[post_id]["status"] == "future"


# ================================================================ 2. chỉ nháp của chính client
@pytest.mark.parametrize(
    "post_id", [True, "42", 42.0, 0, -42, MAX_ID + 1, 2**64, None, [42], 43],
    ids=["bool", "chu", "so-thuc", "0", "am", "max+1", "2^64", "null", "danh-sach", "ma-khac"],
)
def test_ma_khong_phai_bai_cua_client_khong_gui_gi(site, client, post_id):
    draft(client)  # bài 42 của client
    site.posts[43] = {"status": "draft", "date_gmt": "", "author": "nguoi-khac"}
    before = len(site.requests)
    with pytest.raises(ReleaseError) as error:
        client.release_draft(post_id, mode="publish")
    assert len(site.requests) == before
    assert not error.value.unsure and not error.value.went_public
    assert site.posts[43]["status"] == "draft"


def test_bai_cua_client_khac_khong_chuyen_duoc(site):
    first = new_client(site)
    post_id = draft(first)
    second = new_client(site)
    with pytest.raises(ReleaseError):
        second.release_draft(post_id, mode="publish")
    assert site.posts[post_id]["status"] == "draft"


@pytest.mark.parametrize("status", ["publish", "future", "pending", "private", "trash", "Draft",
                                    "draft ", "auto-draft", "inherit"])
def test_bai_khong_con_la_nhap_tren_site_khong_gui_lenh_chuyen(site, client, status):
    post_id = draft(client)
    site.posts[post_id]["status"] = status  # ai đó đổi trong trang quản trị
    with pytest.raises(ReleaseError) as error:
        client.release_draft(post_id, mode="publish")
    assert site.writes() == [("POST", f"{API}/posts")]  # chỉ lệnh tạo nháp lúc đầu
    assert site.posts[post_id]["status"] == status
    assert not error.value.unsure
    before = len(site.requests)
    with pytest.raises(ReleaseError):  # đã bỏ khỏi danh sách bài của client: không hỏi lại
        client.release_draft(post_id, mode="publish")
    assert len(site.requests) == before


@pytest.mark.parametrize(
    "mode, when",
    [("Publish", None), ("draft", None), ("private", None), ("pending", None), (None, None),
     (b"publish", None), ("future ", None), ("publish", None), ("future", None)],
    ids=["Publish", "draft", "private", "pending", "null", "bytes", "future-cach",
         "publish-kem-gio", "future-thieu-gio"],
)
def test_hinh_thuc_sai_khong_gui_gi(site, client, mode, when):
    post_id = draft(client)
    if mode == "publish":
        when = vn(3, 8)
    before = len(site.requests)
    with pytest.raises(ReleaseError) as error:
        client.release_draft(post_id, mode=mode, when_utc=when)
    assert len(site.requests) == before
    assert not error.value.unsure and post_id in client._created_post_ids
    assert site.posts[post_id]["status"] == "draft"


CHECK_FAILURES = {
    "500": (500, {"code": "x", "message": MOI}),
    "404": (404, {"code": "rest_post_invalid_id", "message": MOI}),
    "301": (301, b"", {"Location": "https://evil.example/"}),
    "mat-mang": requests.exceptions.ConnectionError(MOI),
    "het-gio": requests.exceptions.ReadTimeout(MOI),
    "khong-json": (200, MOI.encode()),
}


@pytest.mark.parametrize("answer", CHECK_FAILURES.values(), ids=CHECK_FAILURES)
def test_kiem_nhap_loi_thi_khong_gui_lenh_chuyen_va_thu_lai_duoc(site, client, answer):
    """Lệnh kiểm nháp (chỉ đọc) lỗi: chắc chắn chưa chuyển, không gửi lệnh ghi; bài vẫn của client
    nên lần sau (site đã ổn) hẹn giờ được, đúng một lệnh chuyển."""
    post_id = draft(client)
    site.inject[("GET", f"{API}/posts/{post_id}")] = answer
    with pytest.raises(ReleaseError) as error:
        client.release_draft(post_id, mode="future", when_utc=vn(3, 8))
    assert not error.value.unsure and not error.value.went_public
    assert "vẫn là nháp" in str(error.value) and MOI not in str(error.value)
    assert site.writes() == [("POST", f"{API}/posts")]
    del site.inject[("GET", f"{API}/posts/{post_id}")]
    client.release_draft(post_id, mode="future", when_utc=vn(3, 8))
    assert site.posts[post_id]["status"] == "future"
    assert site.writes() == [("POST", f"{API}/posts"), ("POST", f"{API}/posts/{post_id}")]


def test_bai_bi_xoa_khong_gui_lenh_chuyen(site, client):
    post_id = draft(client)
    del site.posts[post_id]
    with pytest.raises(ReleaseError) as error:
        client.release_draft(post_id, mode="publish")
    assert site.writes() == [("POST", f"{API}/posts")]
    assert MOI not in str(error.value) and BASE not in str(error.value)


@pytest.mark.parametrize(
    "check",
    [{"id": 43, "status": "draft"}, {"id": "42", "status": "draft"},
     {"id": True, "status": "draft"}, {"status": "draft"}, {"id": 42},
     [{"id": 42, "status": "draft"}], "draft", None],
    ids=["ma-khac", "ma-chu", "ma-bool", "thieu-ma", "thieu-trang-thai", "danh-sach", "chu",
         "null"],
)
def test_cau_tra_loi_kiem_nhap_la_khong_gui_lenh_chuyen(site, client, check):
    post_id = draft(client)
    site.inject[("GET", f"{API}/posts/{post_id}")] = (200, check)
    with pytest.raises(ReleaseError):
        client.release_draft(post_id, mode="publish")
    assert site.writes() == [("POST", f"{API}/posts")]
    assert site.posts[post_id]["status"] == "draft"


# ================================================================ 3. không gửi lại khi không chắc
UNSURE_ANSWERS = {
    "mat-mang": requests.exceptions.ConnectionError(MOI),
    "het-gio": requests.exceptions.ReadTimeout(MOI),
    "301-location": (301, b"", {"Location": "https://evil.example/x"}),
    "302-khong-location": (302, b""),
    "500": (500, {"code": "x", "message": MOI}),
    "502-html": (502, MOI.encode()),
    "503": (503, b""),
    "200-khong-json": (200, MOI.encode()),
    "200-danh-sach": (200, []),
    "200-thieu-trang-thai": (200, {"id": 42}),
    "200-thieu-ma": (200, {"status": "future", "date_gmt": "2026-11-03T01:00:00"}),
    "200-ma-khac": (200, {"id": 43, "status": "future", "date_gmt": "2026-11-03T01:00:00"}),
    "200-ma-chu": (200, {"id": "42", "status": "future", "date_gmt": "2026-11-03T01:00:00"}),
    "200-van-nhap": (200, {"id": 42, "status": "draft"}),
    "200-cho-duyet": (200, {"id": 42, "status": "pending"}),
    "200-thieu-gio": (200, {"id": 42, "status": "future"}),
    "200-gio-khac": (200, {"id": 42, "status": "future", "date_gmt": "2026-11-03T01:00:01"}),
    "200-gio-co-Z": (200, {"id": 42, "status": "future", "date_gmt": "2026-11-03T01:00:00Z"}),
}


@pytest.mark.parametrize("answer", UNSURE_ANSWERS.values(), ids=UNSURE_ANSWERS)
def test_hen_gio_khong_chac_thi_bao_co_the_da_va_khong_gui_lai(site, client, answer):
    post_id = draft(client)
    assert post_id == 42
    site.inject[("POST", f"{API}/posts/{post_id}")] = answer
    with pytest.raises(ReleaseError) as error:
        client.release_draft(post_id, mode="future", when_utc=vn(3, 8))
    message = str(error.value)
    assert error.value.unsure and not error.value.went_public
    assert "có thể đã" in message or "khác giờ đã chọn" in message
    for piece in ("MOI-T099", "evil", BASE):
        assert piece not in message
    before = len(site.requests)
    with pytest.raises(ReleaseError):
        client.release_draft(post_id, mode="future", when_utc=vn(3, 8))
    assert len(site.requests) == before  # không tự gửi lại, kể cả khi gọi lại
    assert [w for w in site.writes() if w[1] == f"{API}/posts/{post_id}"] == [
        ("POST", f"{API}/posts/{post_id}")]


@pytest.mark.parametrize(
    "answer",
    [UNSURE_ANSWERS[k] for k in ("mat-mang", "het-gio", "302-khong-location", "500",
                                 "200-khong-json", "200-van-nhap", "200-thieu-trang-thai")],
)
def test_dang_ngay_khong_chac_thi_bao_co_the_da(site, client, answer):
    post_id = draft(client)
    site.inject[("POST", f"{API}/posts/{post_id}")] = answer
    with pytest.raises(ReleaseError) as error:
        client.release_draft(post_id, mode="publish")
    assert error.value.unsure and "có thể đã hiện công khai" in str(error.value)


@pytest.mark.parametrize("status", [400, 401, 403, 404, 409, 429])
def test_tu_choi_4xx_thi_bao_van_la_nhap(site, client, status):
    post_id = draft(client)
    site.inject[("POST", f"{API}/posts/{post_id}")] = (status, {"code": "x", "message": MOI})
    with pytest.raises(ReleaseError) as error:
        client.release_draft(post_id, mode="publish")
    assert not error.value.unsure and "vẫn là nháp" in str(error.value)
    assert MOI not in str(error.value)


def test_site_dang_ngay_khi_hen_gio_sat_gio_bao_khan(site, client):
    """Site đồng hồ chạy nhanh hơn sau lúc kiểm: luật WordPress đổi ``future`` sát giờ thành
    ``publish``. App báo khẩn, không gửi thêm lệnh nào vào bài."""
    post_id = draft(client)

    def late_clock(request):
        site.server_now = SERVER_NOW + timedelta(days=1, minutes=1)  # đã quá giờ hẹn
        site.inject.pop(("POST", f"{API}/posts/{post_id}"))
        return site._answer(request)

    site.inject[("POST", f"{API}/posts/{post_id}")] = late_clock
    with pytest.raises(ReleaseError) as error:
        client.release_draft(post_id, mode="future", when_utc=vn(3, 8))
    assert error.value.went_public and not error.value.unsure
    assert "KHẨN" in str(error.value)
    assert site.posts[post_id]["status"] == "publish"
    assert sum(1 for w in site.writes() if w == ("POST", f"{API}/posts/{post_id}")) == 1


# ================================================================ 4. giờ hẹn
@pytest.mark.parametrize(
    "when, ok",
    [
        (SERVER_NOW - timedelta(seconds=1), False),
        (SERVER_NOW, False),
        (SERVER_NOW + timedelta(minutes=9, seconds=59, microseconds=999_999), False),
        (SERVER_NOW + timedelta(minutes=10), True),
        (SERVER_NOW + timedelta(minutes=10, microseconds=500_000), True),
        (SERVER_NOW + timedelta(days=365), True),
        (SERVER_NOW + timedelta(days=365, microseconds=500_000), True),  # gửi đúng 365 ngày
        (SERVER_NOW + timedelta(days=365, seconds=1), False),
        (SERVER_NOW + timedelta(days=4000), False),
    ],
    ids=["da-qua", "bang-bay-gio", "9p59.999", "10-phut", "10p-le-giay", "365-ngay",
         "365-ngay-le-giay", "365-ngay-1-giay", "11-nam"],
)
def test_khoang_gio_hen_theo_gio_may_chu(site, client, when, ok):
    post_id = draft(client)
    if ok:
        client.release_draft(post_id, mode="future", when_utc=when)
        assert site.posts[post_id]["status"] == "future"
        assert site.posts[post_id]["date_gmt"] == when.strftime("%Y-%m-%dT%H:%M:%S")
    else:
        with pytest.raises(ReleaseError):
            client.release_draft(post_id, mode="future", when_utc=when)
        assert site.posts[post_id]["status"] == "draft"
        assert site.writes() == [("POST", f"{API}/posts")]


@pytest.mark.parametrize(
    "when",
    [datetime(2026, 11, 3, 8, 0), date(2026, 11, 3), "2026-11-03T01:00:00", 1793667600,
     datetime.max.replace(tzinfo=timezone(timedelta(hours=-5)))],
    ids=["khong-mui-gio", "chi-ngay", "chu", "so", "tran-nam-9999"],
)
def test_gio_hen_sai_dang_khong_gui_gi(site, client, when):
    post_id = draft(client)
    before = len(site.requests)
    with pytest.raises(ReleaseError):
        client.release_draft(post_id, mode="future", when_utc=when)
    assert len(site.requests) == before
    assert post_id in client._created_post_ids  # chưa hỏi site: bài vẫn của client


def test_mui_gio_bat_ky_doi_dung_sang_utc(site, client):
    post_id = draft(client)
    plus_2h30 = timezone(timedelta(hours=2, minutes=30))
    when = datetime(2026, 11, 3, 3, 30, 59, 900_000, tzinfo=plus_2h30)
    client.release_draft(post_id, mode="future", when_utc=when)
    assert site.posts[post_id]["date_gmt"] == "2026-11-03T01:00:59"  # đổi UTC, bỏ phần lẻ giây


@pytest.mark.parametrize(
    "header, ok",
    [
        ("", False),
        ("khong phai ngay", False),
        ("Mon, 02 Nov 2026 01:00:00 -0000", False),
        ("Mon Nov  2 01:00:00 2026", False),
        ("Mon, 02 Nov 2026 23:59:60 GMT", False),
        ("Mon, 02 Nov 2026 01:00:00 GMT\tx", False),
        ("Mon, 02 Nov 2026 08:00:00 +0700", True),
        ("Monday, 02-Nov-26 01:00:00 GMT", True),
        ("Mon, 02 Nov 26 01:00:00 GMT", True),
        ("Mon, 02 Nov 2026 01:00:00 UT", True),
        ("Mon, 02 Nov 2026 01:03:00 GMT", False),
        ("Mon, 02 Nov 2026 00:57:00 GMT", False),
        ("Mon, 02 Nov 2026 01:01:59 GMT", True),
    ],
    ids=["thieu", "rac", "-0000", "asctime", "giay-60", "tab", "+0700", "rfc850", "nam-2-so",
         "UT", "lech+3p", "lech-3p", "lech+1p59"],
)
def test_header_date_cua_lenh_kiem_nhap(site, client, header, ok):
    post_id = draft(client)
    site.date_header = header
    if ok:
        client.release_draft(post_id, mode="publish")
        assert site.posts[post_id]["status"] == "publish"
    else:
        with pytest.raises(ReleaseError) as error:
            client.release_draft(post_id, mode="publish")
        assert site.posts[post_id]["status"] == "draft"
        assert not error.value.unsure
        assert site.writes() == [("POST", f"{API}/posts")]


@pytest.mark.parametrize("skew", [timedelta(minutes=3), -timedelta(minutes=3),
                                  timedelta(days=400)])
def test_dong_ho_may_lech_thi_chan(site, client, monkeypatch, skew):
    post_id = draft(client)
    monkeypatch.setattr(wp, "_utc_now", lambda: SERVER_NOW + skew)
    with pytest.raises(ReleaseError):
        client.release_draft(post_id, mode="future", when_utc=vn(3, 8))
    assert site.posts[post_id]["status"] == "draft"


def test_gio_mua_he_va_nhan(site):
    berlin = "Europe/Berlin"
    with pytest.raises(schedule.ScheduleError):  # 02:30 không có (nhảy 02:00 → 03:00)
        schedule.local_to_utc(date(2026, 3, 29), time(2, 30), berlin)
    with pytest.raises(schedule.ScheduleError):  # 02:30 có hai lần (03:00 → 02:00)
        schedule.local_to_utc(date(2026, 10, 25), time(2, 30), berlin)
    summer = schedule.local_to_utc(date(2026, 7, 1), time(8, 0), berlin)
    assert schedule.date_gmt_text(summer) == "2026-07-01T06:00:00"
    winter = schedule.local_to_utc(date(2026, 12, 1), time(8, 0), berlin)
    assert schedule.date_gmt_text(winter) == "2026-12-01T07:00:00"
    vn_time = schedule.local_to_utc(date(2026, 11, 3), time(8, 0, 45))
    assert schedule.date_gmt_text(vn_time) == "2026-11-03T01:00:00"
    assert schedule.schedule_label(vn_time) == "Thứ Ba, 03/11/2026 lúc 08:00 (giờ Việt Nam)"
    with pytest.raises(schedule.ScheduleError):
        schedule.local_to_utc(datetime(2026, 11, 3), time(8, 0))  # datetime không phải date
    with pytest.raises(schedule.ScheduleError):
        schedule.local_to_utc(date(2026, 11, 3), time(8, 0, tzinfo=UTC))


# ================================================================ 5. không đường nào khác
FIELDS = {"_fields": "id,status,date_gmt,link"}
FORGED = {
    "khong-dau-publish": ({"json": {"status": "publish"}, "params": FIELDS}, None),
    "khong-dau-date-gmt": ({"json": {"date_gmt": "2026-11-03T01:00:00"}, "params": FIELDS}, None),
    "khong-dau-date": ({"json": {"date": "2026-11-03T08:00:00"}, "params": FIELDS}, None),
    "dau-gia-object": ({"json": {"status": "publish"}, "params": FIELDS}, object()),
    "dau-gia-true": ({"json": {"status": "publish"}, "params": FIELDS}, True),
    "dau-gia-chu": ({"json": {"status": "publish"}, "params": FIELDS}, "_RELEASE"),
    "dau-that-them-khoa": ({"json": {"status": "publish", "content": "x"}, "params": FIELDS},
                           wp._RELEASE),
    "dau-that-date": ({"json": {"status": "future", "date": "2026-11-03T08:00:00"},
                       "params": FIELDS}, wp._RELEASE),
    "dau-that-private": ({"json": {"status": "private"}, "params": FIELDS}, wp._RELEASE),
    "dau-that-pending": ({"json": {"status": "pending"}, "params": FIELDS}, wp._RELEASE),
    "dau-that-trash": ({"json": {"status": "trash"}, "params": FIELDS}, wp._RELEASE),
    "dau-that-future-thieu-gio": ({"json": {"status": "future"}, "params": FIELDS}, wp._RELEASE),
    "dau-that-gio-Z": ({"json": {"status": "future", "date_gmt": "2026-11-03T01:00:00Z"},
                        "params": FIELDS}, wp._RELEASE),
    "dau-that-gio-mui": ({"json": {"status": "future", "date_gmt": "2026-11-03T08:00:00+07:00"},
                          "params": FIELDS}, wp._RELEASE),
    "dau-that-gio-so-la": ({"json": {"status": "future", "date_gmt": "２０２６-11-03T01:00:00"},
                            "params": FIELDS}, wp._RELEASE),
    "dau-that-fields-khac": ({"json": {"status": "publish"},
                              "params": {"_fields": "id,status,content"}}, wp._RELEASE),
    "dau-that-them-tham-so": ({"json": {"status": "publish"},
                               "params": {**FIELDS, "force": "true"}}, wp._RELEASE),
    "dau-that-them-header": ({"json": {"status": "publish"}, "params": FIELDS,
                              "headers": {"Content-Type": "image/jpeg"}}, wp._RELEASE),
    "dau-that-status-bytes": ({"json": {"status": b"publish"}, "params": FIELDS}, wp._RELEASE),
}


@pytest.mark.parametrize("options, marker", FORGED.values(), ids=FORGED)
def test_moi_cach_goi_thang_lenh_ghi_trang_thai_deu_bi_chan(site, client, options, marker):
    post_id = draft(client)
    before = len(site.requests)
    kwargs = dict(options)
    if marker is not None:
        kwargs["release"] = marker
    with pytest.raises(WordPressError):
        client._request("POST", f"/wp/v2/posts/{post_id}", **kwargs)
    assert len(site.requests) == before
    assert site.posts[post_id]["status"] == "draft"


@pytest.mark.parametrize(
    "method, path",
    [("POST", "/wp/v2/posts"), ("POST", "/wp/v2/pages/42"), ("POST", "/wp/v2/media/42"),
     ("PUT", "/wp/v2/posts/42"), ("PATCH", "/wp/v2/posts/42"), ("POST", "/wp/v2/posts/42/")],
)
def test_dau_that_tren_duong_khac_bi_chan(site, client, method, path):
    draft(client)
    before = len(site.requests)
    with pytest.raises(WordPressError):
        client._request(method, path, json={"status": "publish"}, params=FIELDS,
                        release=wp._RELEASE)
    assert len(site.requests) == before


@pytest.mark.parametrize(
    "path, body",
    [("/wp/v2/posts/42", b"status=publish"),
     ("/wp/v2/posts/42", b"status=future&date_gmt=2026-11-03T01:00:00"),
     ("/wp/v2/posts/42", b"id=7&featured_media=1"),
     ("/wp/v2/posts", b"status=publish&title=x"),
     (wp.SITESEO_ABILITY_RUN_PATH, b"name=ability-khac")],
    ids=["publish", "future", "id-bai-khac", "tao-bai-publish", "ability-khac"],
)
def test_sl_t099_1_than_data_khong_qua_duoc_lop_chan(site, client, path, body):
    """``_is_plain_request`` chỉ xét khóa của ``json=``; ``data=`` (bytes) được ở **mọi** đường và
    ``requests`` không gắn ``Content-Type`` cho bytes. Hôm nay WordPress không đọc thân đó với POST
    (``$_POST`` của PHP rỗng khi thiếu Content-Type dạng form; ``_method``, header đổi phương thức
    đã bị chặn) nên chưa thành lỗ thật, nhưng lời hứa «chỉ lệnh mang dấu ``_RELEASE`` gửi được
    ``status`` khác nháp, ``date_gmt``» (LC-T094-22) dựa vào điều đó chứ không vào lớp chặn. Nên
    chỉ cho ``data`` ở ``POST /wp/v2/media`` kèm ``Content-Type`` loại ảnh."""
    draft(client)
    before = len(site.requests)
    with pytest.raises(WordPressError):
        client._request("POST", path, data=body)
    assert len(site.requests) == before


def test_tao_nhap_va_anh_dai_dien_khong_mang_trang_thai_khac(site, client):
    post_id = draft(client)
    created = json.loads(site.requests[0].body)
    assert created["status"] == "draft" and "date_gmt" not in created and "date" not in created
    site.inject[("POST", f"{API}/posts/{post_id}")] = (
        200, {"id": post_id, "status": "draft", "featured_media": 7})
    client.set_featured_image(post_id, 7)
    assert json.loads(site.requests[-1].body) == {"featured_media": 7}


# ================================================================ 6. post_statuses chỉ đọc
def test_post_statuses_chi_doc_va_khong_them_bai_cua_client(site, client):
    for i in range(250):
        site.posts[1000 + i] = {"status": "future" if i % 2 else "publish", "date_gmt": "",
                                "author": "x"}
    states = client.post_statuses(range(1000, 1250))
    assert len(states) == 250
    gets = [r for r in site.requests if r.method == "GET"]
    assert len(gets) == 3 and site.writes() == []
    for request in gets:
        query = parse_qs(urlsplit(request.url).query)
        assert len(query["include"][0].split(",")) <= 100
        assert query["status"] == ["draft,future,publish,pending,private"]
        assert query["context"] == ["edit"] and "content" not in query["_fields"][0]
    assert client._created_post_ids == set()
    with pytest.raises(ReleaseError):
        client.release_draft(1000, mode="publish")


@pytest.mark.parametrize(
    "ids",
    [[True], ["1"], [1.0], [0], [-1], [MAX_ID + 1], list(range(1, 1002)), "1,2", {1: 2}, 5],
    ids=["bool", "chu", "so-thuc", "0", "am", "max+1", "1001-ma", "chuoi", "dict", "so"],
)
def test_post_statuses_ma_sai_khong_hoi(site, client, ids):
    with pytest.raises(WordPressError):
        client.post_statuses(ids)
    assert site.requests == []


@pytest.mark.parametrize(
    "params",
    [{"include": "1, 2"}, {"include": "01"}, {"include": "1;2"}, {"include": "-1"},
     {"include": ",".join(str(i) for i in range(1, 102))}, {"include": "１"},
     {"status": "trash"}, {"status": "any"}, {"context": "view"}, {"include": 5}],
)
def test_tham_so_doc_trang_thai_sai_gia_tri_bi_chan(site, client, params):
    with pytest.raises(WordPressError):
        client._request("GET", "/wp/v2/posts", params=params)
    assert site.requests == []


# ================================================================ 7. múi giờ của website
@pytest.mark.parametrize(
    "zone, offset, expect_zone, expect_offset",
    [
        ("Asia/Ho_Chi_Minh", "7", "Asia/Ho_Chi_Minh", 7.0),
        ("", 5.5, "", 5.5),
        ("Etc/GMT+7", -7, "Etc/GMT+7", -7.0),
        ("<b>x</b>", "+7", "", None),
        ("A" * 70, 15, "", None),
        (["Asia/Ho_Chi_Minh"], True, "", None),
        ("Asia/Hồ_Chí_Minh", "7.255", "", None),
        (None, "1e2", "", None),
    ],
)
def test_mui_gio_website_duoc_kiem(site, client, zone, offset, expect_zone, expect_offset):
    site.inject[("GET", "/wp-json/")] = (200, {
        "name": "Site", "home": BASE, "namespaces": ["wp/v2"],
        "timezone_string": zone, "gmt_offset": offset})
    site.inject[("GET", f"{API}/users/me")] = (200, {"name": "Lâm", "capabilities": {}})
    info = client.check_connection()
    assert (info.timezone_string, info.gmt_offset) == (expect_zone, expect_offset)
    warning = info.timezone_warning()
    assert (warning == "") is (expect_offset == 7.0)
    for piece in ("<b>", "AAAA", "Hồ_Chí"):
        assert piece not in warning


# ================================================================ Lượt 2 (2026-10-30)
# SL-T099-1 (thân byte chỉ ở lệnh tải ảnh) và LC-T099-1 (giành mã bài một bước) của Thợ Máy lượt 2.

BODY_ROUTES = [
    ("POST", "/wp/v2/posts/42"), ("POST", "/wp/v2/posts"), ("POST", "/wp/v2/media/9"),
    ("POST", wp.SITESEO_ABILITY_RUN_PATH), ("GET", "/wp/v2/posts/42"), ("GET", "/wp/v2/posts"),
    ("GET", "/wp/v2/users/me"), ("GET", "/"),
]
BODIES = {
    "bytes": {"data": b"status=publish"},
    "bytes-rong": {"data": b""},
    "bytearray": {"data": bytearray(b"status=publish")},
    "memoryview": {"data": memoryview(b"status=publish")},
    "str": {"data": "status=publish"},
    "form-dict": {"data": {"status": "publish"}},
    "form-list": {"data": [("status", "publish")]},
    "file-like": {"data": io.BytesIO(b"status=publish")},
    "files": {"files": {"file": ("a.jpg", b"\xff\xd8\xff", "image/jpeg")}},
    "bytes-kem-loai-anh": {"data": b"status=publish", "headers": {"Content-Type": "image/jpeg"}},
    "bytes-kem-form": {"data": b"status=publish",
                       "headers": {"Content-Type": "application/x-www-form-urlencoded"}},
}


@pytest.mark.parametrize("method, path", BODY_ROUTES)
@pytest.mark.parametrize("options", BODIES.values(), ids=BODIES)
def test_luot2_than_lenh_khong_phai_json_bi_chan_o_moi_duong_khac_tai_anh(
    site, client, method, path, options
):
    draft(client)
    before = len(site.requests)
    with pytest.raises(WordPressError):
        client._request(method, path, **options)
    assert len(site.requests) == before
    assert site.posts[42]["status"] == "draft"


JPEG = b"\xff\xd8\xff\xe0 anh gia \xff\xd9"
MEDIA_ODD = {
    "khong-header": {"data": JPEG},
    "chi-ten-file": {"data": JPEG,
                     "headers": {"Content-Disposition": 'attachment; filename="a.jpg"'}},
    "loai-chu": {"data": JPEG, "headers": {"Content-Type": "text/plain"}},
    "loai-form": {"data": JPEG, "headers": {"Content-Type": "application/x-www-form-urlencoded"}},
    "loai-multipart": {"data": JPEG,
                       "headers": {"Content-Type": "multipart/form-data; boundary=x"}},
    "loai-co-tham-so": {"data": JPEG, "headers": {"Content-Type": "image/jpeg; charset=utf-8"}},
    "loai-svg": {"data": JPEG, "headers": {"Content-Type": "image/svg+xml"}},
    "hai-loai": {"data": JPEG,
                 "headers": {"Content-Type": "image/jpeg", "content-type": "image/png"}},
    "kem-json": {"data": JPEG, "json": {"title": "x"}, "headers": {"Content-Type": "image/jpeg"}},
    "kem-json-rong": {"data": JPEG, "json": {}, "headers": {"Content-Type": "image/jpeg"}},
    "chu-thay-byte": {"data": "anh", "headers": {"Content-Type": "image/jpeg"}},
    "bytearray": {"data": bytearray(JPEG), "headers": {"Content-Type": "image/jpeg"}},
}


@pytest.mark.parametrize("options", MEDIA_ODD.values(), ids=MEDIA_ODD)
def test_luot2_lenh_tai_anh_sai_khuon_bi_chan(site, client, options):
    with pytest.raises(WordPressError):
        client._request("POST", "/wp/v2/media", **options)
    assert site.requests == []


def _media_site(site: _WpSite) -> None:
    site.inject[("POST", f"{API}/media")] = (
        201, {"id": 9, "source_url": f"{BASE}/wp-content/uploads/anh.jpg", "alt_text": ""})
    site.inject[("POST", f"{API}/media/9")] = (
        200, {"id": 9, "source_url": f"{BASE}/wp-content/uploads/anh.jpg", "alt_text": "Cổng"})


@pytest.mark.parametrize("suffix", sorted(wp.IMAGE_TYPES))
def test_luot2_tai_anh_moi_loai_van_gui_nguyen_byte(site, client, suffix):
    """Không chặn oan: ``upload_media`` mọi loại ảnh vẫn gửi đúng byte, đúng một ``Content-Type``
    loại ảnh, rồi ghi đè alt (lệnh JSON)."""
    _media_site(site)
    media = client.upload_media(JPEG, f"Cổng sắt{suffix}", alt_text="Cổng")
    assert media.id == 9
    upload, describe = site.requests
    assert urlsplit(upload.url).path == f"{API}/media" and upload.body == JPEG
    assert upload.headers["Content-Type"] == wp.IMAGE_TYPES[suffix]
    assert urlsplit(describe.url).path == f"{API}/media/9"
    assert json.loads(describe.body)["alt_text"] == "Cổng"


def test_luot2_gui_nhap_kem_anh_that_van_chay(site, client):
    """Không chặn oan đường «Gửi nháp» của Soạn bài: ảnh WebP qua ``make_web_image`` lên được,
    bài nháp có ảnh đại diện."""
    from PIL import Image

    from seo_app.images.process import make_web_image

    buffer = io.BytesIO()
    Image.new("RGB", (64, 48), (120, 90, 60)).save(buffer, "JPEG")
    web = make_web_image(buffer.getvalue())
    _media_site(site)
    result = client.create_draft_with_images(
        "Sửa cổng inox", ["<p>Cổng sau khi sửa.</p>", wp.DraftImage(web, alt="Cổng inox")])
    upload = next(r for r in site.requests if urlsplit(r.url).path == f"{API}/media")
    assert upload.body == web.data and upload.headers["Content-Type"] == "image/webp"
    assert result.post.status == "draft" and [image.id for image in result.images] == [9]


# ---------------------------------------------------------------- LC-T099-1: nhiều luồng
def _hold_check(site: _WpSite, post_id: int, answer=None):
    """Lệnh kiểm nháp của luồng đầu tiên dừng lại tới khi ``go`` được bật."""
    inside, go = threading.Event(), threading.Event()

    def handler(request):
        inside.set()
        assert go.wait(10)
        if answer is not None:
            return answer
        return 200, {"id": post_id, "status": site.posts[post_id]["status"],
                     "modified_gmt": MODIFIED}  # T-115

    site.inject[("GET", f"{API}/posts/{post_id}")] = handler
    return inside, go


def _run(results: dict, client: WordPressClient, name: str, post_id: int, mode: str, when):
    try:
        results[name] = client.release_draft(post_id, mode=mode, when_utc=when)
    except ReleaseError as exc:
        results[name] = exc


def _releases(site: _WpSite, post_id: int) -> int:
    return site.writes().count(("POST", f"{API}/posts/{post_id}"))


def test_luot2_ba_luong_chung_mot_client_chi_mot_lenh_chuyen(site, client):
    post_id = draft(client)
    inside, go = _hold_check(site, post_id)
    results: dict = {}
    first = threading.Thread(target=_run, args=(results, client, "A", post_id, "future", vn(3, 8)))
    first.start()
    assert inside.wait(10)  # A đã giành bài, đang chờ lệnh kiểm nháp
    others = [threading.Thread(target=_run, args=(results, client, name, post_id, mode, when))
              for name, mode, when in (("B", "publish", None), ("C", "future", vn(4, 8)))]
    for thread in others:
        thread.start()
    for thread in others:
        thread.join(10)
    gets = [r for r in site.requests if r.method == "GET"]
    assert len(gets) == 1  # B, C bị từ chối ngay, không hỏi website
    for name in "BC":
        assert isinstance(results[name], ReleaseError) and not results[name].unsure
        assert "Chưa gửi gì" in str(results[name])
    go.set()
    first.join(10)
    assert results["A"].status == "future" and results["A"].date_gmt == "2026-11-03T01:00:00"
    assert _releases(site, post_id) == 1
    assert site.posts[post_id] == {"status": "future", "date_gmt": "2026-11-03T01:00:00",
                                   "author": "app"}


@pytest.mark.parametrize(
    "answer, when, gives_back",
    [((500, {"code": "x", "message": MOI}), vn(3, 8), True),
     (requests.exceptions.ConnectionError(MOI), vn(3, 8), True),
     (None, SERVER_NOW + timedelta(minutes=5), True),  # giờ quá gần
     ((200, {"id": 42, "status": "publish"}), vn(3, 8), False)],  # ai đó vừa đăng
    ids=["kiem-500", "kiem-mat-mang", "gio-qua-gan", "khong-con-nhap"],
)
def test_luot2_luong_dau_bi_chan_thi_luong_sau_moi_duoc_chuyen(site, client, answer, when,
                                                              gives_back):
    post_id = draft(client)
    inside, go = _hold_check(site, post_id, answer)
    results: dict = {}
    first = threading.Thread(target=_run, args=(results, client, "A", post_id, "future", when))
    first.start()
    assert inside.wait(10)
    _run(results, client, "B", post_id, "publish", None)  # trong lúc A giữ bài: từ chối
    assert isinstance(results["B"], ReleaseError) and _releases(site, post_id) == 0
    go.set()
    first.join(10)
    assert isinstance(results["A"], ReleaseError) and not results["A"].unsure
    assert (post_id in client._created_post_ids) is gives_back
    del site.inject[("GET", f"{API}/posts/{post_id}")]
    before = len(site.requests)
    _run(results, client, "C", post_id, "publish", None)
    if gives_back:
        assert results["C"].status == "publish" and _releases(site, post_id) == 1
    else:
        assert isinstance(results["C"], ReleaseError) and len(site.requests) == before
        assert _releases(site, post_id) == 0


def _together(barrier, results, client, name, post_id, mode, when):
    barrier.wait(10)
    _run(results, client, name, post_id, mode, when)


def test_luot2_ba_luong_xuat_phat_cung_luc_lap_lai_luon_mot_lenh_chuyen():
    for _round in range(25):
        site = _WpSite()
        client = new_client(site)
        post_id = draft(client)
        barrier = threading.Barrier(3)
        results: dict = {}
        threads = [
            threading.Thread(target=_together,
                             args=(barrier, results, client, name, post_id, mode, when))
            for name, mode, when in
            (("A", "future", vn(3, 8)), ("B", "publish", None), ("C", "future", vn(4, 8)))
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(10)
        done = [name for name, value in results.items() if not isinstance(value, ReleaseError)]
        assert len(done) == 1 and _releases(site, post_id) == 1
        assert all("Chưa gửi gì" in str(results[name]) for name in "ABC" if name not in done)


# ---------------------------------------------------------------- LC-T099-1: trả hay giữ mã
GIVE_BACK = {  # bị chặn trước lệnh chuyển: mã trở lại, bài vẫn là nháp của client
    "hinh-thuc-sai": {"mode": "Publish"},
    "dang-ngay-kem-gio": {"mode": "publish", "when": vn(3, 8)},
    "gio-khong-mui-gio": {"when": datetime(2026, 11, 3, 8, 0)},
    "header-phien-doi-phuong-thuc": {"session_header": True},
    "kiem-mat-mang": {"check": requests.exceptions.ConnectionError(MOI)},
    "kiem-het-gio": {"check": requests.exceptions.ReadTimeout(MOI)},
    "kiem-301": {"check": (301, b"", {"Location": "https://evil.example/"})},
    "kiem-401": {"check": (401, {"code": "x", "message": MOI})},
    "kiem-404": {"check": (404, {"code": "rest_post_invalid_id", "message": MOI})},
    "kiem-500": {"check": (500, {"code": "x", "message": MOI})},
    "kiem-503": {"check": (503, b"")},
    "kiem-khong-json": {"check": (200, MOI.encode())},
    "thieu-date": {"date_header": ""},
    "date-rac": {"date_header": "khong phai ngay"},
    "dong-ho-lech": {"skew": timedelta(minutes=3)},
    "gio-da-qua": {"when": SERVER_NOW - timedelta(minutes=1)},
    "gio-qua-gan": {"when": SERVER_NOW + timedelta(minutes=9)},
    "gio-qua-xa": {"when": SERVER_NOW + timedelta(days=366)},
    "dong-ho-may-hong": {"clock_error": True},
}


@pytest.mark.parametrize("case", GIVE_BACK.values(), ids=GIVE_BACK)
def test_luot2_bi_chan_truoc_lenh_chuyen_thi_tra_ma_va_thu_lai_duoc(site, client, monkeypatch,
                                                                    case):
    post_id = draft(client)
    if case.get("session_header"):
        client._session.headers["X-HTTP-Method-Override"] = "PUT"
    if "check" in case:
        site.inject[("GET", f"{API}/posts/{post_id}")] = case["check"]
    if "date_header" in case:
        site.date_header = case["date_header"]
    if "skew" in case:
        monkeypatch.setattr(wp, "_utc_now", lambda: SERVER_NOW + case["skew"])
    if case.get("clock_error"):
        def broken():
            raise RuntimeError("đồng hồ hỏng")
        monkeypatch.setattr(wp, "_utc_now", broken)
    mode = case.get("mode", "future")
    when = case.get("when", vn(3, 8) if mode == "future" else None)
    with pytest.raises((ReleaseError, RuntimeError)) as error:
        client.release_draft(post_id, mode=mode, when_utc=when)
    if isinstance(error.value, ReleaseError):
        assert not error.value.unsure and not error.value.went_public
        assert MOI not in str(error.value)
    assert post_id in client._created_post_ids  # mã trở lại
    assert _releases(site, post_id) == 0 and site.posts[post_id]["status"] == "draft"
    # Site ổn trở lại: chính client đó chuyển được, đúng một lệnh chuyển.
    client._session.headers.pop("X-HTTP-Method-Override", None)
    site.inject.pop(("GET", f"{API}/posts/{post_id}"), None)
    site.date_header = None
    monkeypatch.setattr(wp, "_utc_now", lambda: SERVER_NOW)
    client.release_draft(post_id, mode="future", when_utc=vn(3, 8))
    assert _releases(site, post_id) == 1 and site.posts[post_id]["status"] == "future"


KEEP = {  # đã biết bài không còn nháp, hoặc đã gửi lệnh chuyển: mã không bao giờ trở lại
    "site-bao-da-dang": {"check": (200, {"id": 42, "status": "publish"})},
    "site-bao-thung-rac": {"check": (200, {"id": 42, "status": "trash"})},
    "kiem-tra-loi-la": {"check": (200, [{"id": 42, "status": "draft"}])},
    "chuyen-thanh-cong": {},
    "chuyen-mat-mang": {"release": requests.exceptions.ConnectionError(MOI)},
    "chuyen-het-gio": {"release": requests.exceptions.ReadTimeout(MOI)},
    "chuyen-301": {"release": (301, b"", {"Location": "https://evil.example/"})},
    "chuyen-302-khong-location": {"release": (302, b"")},
    "chuyen-500": {"release": (500, {"code": "x", "message": MOI})},
    "chuyen-503": {"release": (503, b"")},
    "chuyen-tra-loi-la": {"release": (200, [])},
    "chuyen-thieu-truong": {"release": (200, {"id": 42})},
    "chuyen-tu-choi-400": {"release": (400, {"code": "rest_invalid_param", "message": MOI})},
    "chuyen-tu-choi-403": {"release": (403, {"code": "rest_cannot_publish", "message": MOI})},
}


@pytest.mark.parametrize("case", KEEP.values(), ids=KEEP)
def test_luot2_khong_con_nhap_hay_da_gui_lenh_chuyen_thi_giu_ma(site, client, case):
    post_id = draft(client)
    if "check" in case:
        site.inject[("GET", f"{API}/posts/{post_id}")] = case["check"]
    if "release" in case:
        site.inject[("POST", f"{API}/posts/{post_id}")] = case["release"]
    try:
        client.release_draft(post_id, mode="future", when_utc=vn(3, 8))
    except ReleaseError as exc:
        assert MOI not in str(exc)
    assert post_id not in client._created_post_ids
    sent = _releases(site, post_id)
    assert sent == (0 if "check" in case else 1)
    before = len(site.requests)
    for call in (lambda: client.release_draft(post_id, mode="publish"),
                 lambda: client.release_draft(post_id, mode="future", when_utc=vn(4, 8)),
                 lambda: client.set_featured_image(post_id, 7),
                 lambda: client.set_seo_meta(post_id, title="Cổng inox")):
        with pytest.raises(WordPressError):
            call()
    assert len(site.requests) == before and _releases(site, post_id) == sent
