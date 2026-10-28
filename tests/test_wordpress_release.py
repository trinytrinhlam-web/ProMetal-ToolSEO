"""T-099: client WordPress hẹn giờ, đăng ngay, đọc trạng thái bài (thiết kế T-094 mục 3.3).

Đối chiếu điều kiện Lá Chắn T-094:

- LC-T094-22: ``release_draft`` là đường duy nhất gửi ``status`` khác ``"draft"`` và ``date_gmt``;
  dấu ``_RELEASE`` so bằng ``is``, gỡ khỏi tùy chọn trước ``requests``; ``date`` không bao giờ
  được gửi; test đọc mã nguồn.
- LC-T094-23: chỉ bài chính đối tượng client này vừa tạo, site xác nhận còn nháp ngay trước lệnh;
  bỏ mã bài sau khi chuyển.
- LC-T094-24: giờ máy chủ từ header ``Date`` của câu trả lời ngay trước lệnh; lệch đồng hồ, giờ
  hẹn quá gần, quá xa, không múi giờ → 0 lệnh chuyển.
- LC-T094-25: kiểm câu trả lời; hẹn giờ thành đăng ngay → câu báo khẩn; lỗi không rõ → «có thể
  đã», không tự gửi lại.
- LC-T094-26: ``post_statuses`` chỉ đọc; giá trị ``include``, ``status``, ``context`` kiểm trước
  khi gửi.
- LC-T094-27: múi giờ website trong ``ConnectionInfo`` kiểm dạng, chỉ để Cảnh báo.
- LC-T094-1, -2: chỉ site giả (``FakeWordPress``); câu báo cố định, không chép lời máy chủ.
"""

from __future__ import annotations

import ast
import json
import re
from datetime import UTC, date, datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path
from urllib.parse import urlsplit

import pytest
import requests
from fake_wordpress import BASE_URL, FakeWordPress, make_session, query

from seo_app.config import PROJECT_ROOT
from seo_app.publish import schedule
from seo_app.wordpress import WordPressClient, WordPressError
from seo_app.wordpress import client as client_module
from seo_app.wordpress.client import (
    _RELEASE,
    _RELEASE_FIELDS,
    _ROUTE_BLOCKED,
    _STATUS_FIELDS,
    MAX_STATUS_IDS,
    MAX_STATUS_LOOKUP,
    POST_STATUS_FILTER,
    ConnectionInfo,
    PostState,
    Released,
    ReleaseError,
)

POSTS = "/wp-json/wp/v2/posts"
POST_42 = POSTS + "/42"
NOW = datetime(2026, 11, 2, 1, 0, tzinfo=UTC)  # giờ máy chủ (và đồng hồ máy) trong test
TOMORROW = NOW + timedelta(days=1)
STAMP = "2026-11-03T01:00:00"
BAIT = "MỒI-máy-chủ <b>evil</b>"
LINK = f"{BASE_URL}/sua-cua-sat/"


def http_date(when: datetime) -> str:
    return format_datetime(when, usegmt=True)


@pytest.fixture(autouse=True)
def fixed_clock(monkeypatch):
    """Đồng hồ máy cố định ở ``NOW`` (test riêng đổi qua ``set_clock``)."""
    monkeypatch.setattr(client_module, "_utc_now", lambda: NOW)


def set_clock(monkeypatch, when: datetime) -> None:
    monkeypatch.setattr(client_module, "_utc_now", lambda: when)


@pytest.fixture
def fake() -> FakeWordPress:
    return FakeWordPress()


@pytest.fixture
def client(fake) -> WordPressClient:
    return WordPressClient(BASE_URL, "lam", "abcd efgh ijkl", session=make_session(fake))


def body(request: requests.PreparedRequest) -> object:
    return json.loads(request.body)


def paths(fake: FakeWordPress) -> list[tuple[str, str]]:
    return [(r.method, urlsplit(r.url).path) for r in fake.requests]


def own_draft(client: WordPressClient, fake: FakeWordPress, post_id: int = 42) -> int:
    """Client tạo bài nháp ``post_id`` (site giả xác nhận ``draft``), rồi xóa sổ request."""
    fake.on("POST", POSTS, {"id": post_id, "status": "draft", "title": {"raw": "Bài"}})
    post = client.create_draft("Bài", "<p>Nội dung</p>")
    assert post.id == post_id
    fake.requests.clear()
    return post_id


def site(
    fake: FakeWordPress,
    *,
    check: object = None,
    check_status: int = 200,
    date_header: str | None = None,
    answer: object = None,
    post_id: int = 42,
) -> None:
    """Site giả: ``GET`` bài (kiểm nháp, kèm header ``Date``) và ``POST`` chuyển trạng thái.

    ``answer`` mặc định: trả lại đúng trạng thái, giờ đã gửi (site làm đúng)."""
    path = f"{POSTS}/{post_id}"
    if date_header is None:
        headers = {"Date": http_date(NOW)}
    else:  # "" là không có header ``Date``
        headers = {"Date": date_header} if date_header else {}
    fake.on(
        "GET",
        path,
        lambda r: (check_status, check if check is not None else {"id": post_id, "status": "draft"},
                   headers),
    )

    def released(request):
        if answer is not None:
            return answer(request) if callable(answer) else answer
        sent = body(request)
        return {"id": post_id, "link": LINK, "date_gmt": sent.get("date_gmt", STAMP), **sent}

    fake.on("POST", path, released)


# ====================================================================== chạy đúng


def test_hen_gio_gui_dung_mot_lenh_kiem_va_mot_lenh_chuyen(client, fake):
    own_draft(client, fake)
    site(fake)
    result = client.release_draft(42, mode="future", when_utc=TOMORROW)
    assert result == Released(42, "future", STAMP, LINK, client.edit_link(42))
    check, release = fake.requests
    assert (check.method, urlsplit(check.url).path) == ("GET", POST_42)
    assert query(check) == {"context": ["edit"], "_fields": ["id,status"]}
    assert (release.method, urlsplit(release.url).path) == ("POST", POST_42)
    assert query(release) == {"_fields": [_RELEASE_FIELDS]}
    assert body(release) == {"status": "future", "date_gmt": STAMP}


def test_dang_ngay_chi_gui_status_publish_khong_ngay(client, fake):
    own_draft(client, fake)
    site(fake, answer={"id": 42, "status": "publish", "date_gmt": "2026-11-02T01:00:05",
                       "link": LINK})
    result = client.release_draft(42, mode="publish")
    assert result == Released(42, "publish", "2026-11-02T01:00:05", LINK, client.edit_link(42))
    assert body(fake.requests[-1]) == {"status": "publish"}


def test_gio_co_mui_gio_khac_doi_sang_utc_va_bo_phan_le_cua_giay(client, fake):
    own_draft(client, fake)
    site(fake)
    vietnam = timezone(timedelta(hours=7))
    when = datetime(2026, 11, 3, 8, 0, 0, 700_000, tzinfo=vietnam)
    client.release_draft(42, mode="future", when_utc=when)
    assert body(fake.requests[-1]) == {"status": "future", "date_gmt": STAMP}


def test_gio_tu_schedule_gui_dung_chuoi_date_gmt(client, fake):
    """Giờ người dùng chọn (08:00 giờ Việt Nam) → đúng chuỗi ``date_gmt`` ``schedule`` tính."""
    own_draft(client, fake)
    site(fake)
    when = schedule.local_to_utc(date(2026, 11, 3), datetime(2026, 1, 1, 8, 0).time())
    client.release_draft(42, mode="future", when_utc=when)
    assert body(fake.requests[-1])["date_gmt"] == schedule.date_gmt_text(when) == STAMP


def test_link_la_trong_ket_qua_thi_bo(client, fake):
    own_draft(client, fake)
    site(fake, answer={"id": 42, "status": "future", "date_gmt": STAMP,
                       "link": "https://evil.example/x"})
    assert client.release_draft(42, mode="future", when_utc=TOMORROW).link == ""


def test_dau_rieng_khong_toi_requests(client, fake, monkeypatch):
    own_draft(client, fake)
    site(fake)
    seen: list[set[str]] = []
    original = client._session.request

    def spy(method, url, **kwargs):
        seen.append(set(kwargs))
        return original(method, url, **kwargs)

    monkeypatch.setattr(client._session, "request", spy)
    client.release_draft(42, mode="future", when_utc=TOMORROW)
    assert seen and all("release" not in names for names in seen)


def test_sau_khi_chuyen_khong_lenh_nao_sua_tiep_bai(client, fake):
    own_draft(client, fake)
    site(fake)
    client.release_draft(42, mode="future", when_utc=TOMORROW)
    fake.requests.clear()
    with pytest.raises(ReleaseError):
        client.release_draft(42, mode="publish")
    with pytest.raises(WordPressError):
        client.set_featured_image(42, 7)
    with pytest.raises(WordPressError):
        client.set_seo_meta(42, title="Tiêu đề")
    assert fake.requests == []


# ====================================================================== LC-T094-22: đúng một đường

DATE = "2026-12-01T01:00:00"


@pytest.mark.parametrize(
    ("path", "payload"),
    [
        ("/wp/v2/posts", {"title": "Bài", "status": "publish"}),
        ("/wp/v2/posts", {"title": "Bài", "status": "future", "date_gmt": DATE}),
        ("/wp/v2/posts", {"title": "Bài", "status": "draft", "date_gmt": DATE}),
        ("/wp/v2/posts", {"title": "Bài", "date": DATE}),
        ("/wp/v2/posts", {"title": "Bài", "DATE_GMT": DATE}),
        ("/wp/v2/posts/42", {"status": "publish"}),
        ("/wp/v2/posts/42", {"status": "future", "date_gmt": DATE}),
        ("/wp/v2/posts/42", {"featured_media": 7, "date_gmt": DATE}),
        ("/wp/v2/posts/42", {"featured_media": 7, "status": "publish"}),
        ("/wp/v2/posts/42", {"meta": {}, "date": DATE}),
        ("/wp/v2/media/9", {"alt_text": "A", "status": "publish"}),
        ("/wp/v2/media/9", {"alt_text": "A", "date_gmt": DATE}),
    ],
)
def test_khong_dau_rieng_thi_khong_gui_duoc_trang_thai_hay_ngay(client, fake, path, payload):
    with pytest.raises(WordPressError, match=re.escape(_ROUTE_BLOCKED)):
        client._request("POST", path, json=payload, params={"_fields": "id,status"})
    assert fake.requests == []


def test_noi_danh_sach_khoa_van_khong_gui_duoc_date_gmt_hay_status_khac(client, fake, monkeypatch):
    """Phòng khi ai đó thêm ``status``, ``date_gmt``, ``date`` vào ``ALLOWED_JSON_KEYS``."""
    loosened = tuple(
        (method, pattern, keys | {"status", "date_gmt", "date"})
        for method, pattern, keys in client_module._ROUTE_JSON_KEYS
    )
    monkeypatch.setattr(client_module, "_ROUTE_JSON_KEYS", loosened)
    for payload in ({"status": "publish"}, {"date_gmt": DATE}, {"date": DATE}):
        with pytest.raises(WordPressError, match=re.escape(_ROUTE_BLOCKED)):
            client._request("POST", "/wp/v2/posts/42", json=payload)
    assert fake.requests == []


RELEASE_OK = {"json": {"status": "publish"}, "params": {"_fields": _RELEASE_FIELDS}}


def _with(**changes):
    options = {"json": dict(RELEASE_OK["json"]), "params": dict(RELEASE_OK["params"])}
    options.update(changes)
    return options


@pytest.mark.parametrize(
    ("method", "path", "options"),
    [
        pytest.param("POST", "/wp/v2/posts", RELEASE_OK, id="duong-tao-bai"),
        pytest.param("POST", "/wp/v2/media/9", RELEASE_OK, id="duong-anh"),
        pytest.param("GET", "/wp/v2/posts/42", RELEASE_OK, id="phuong-thuc-get"),
        pytest.param("POST", "/wp/v2/posts/42", _with(json={"status": "publish", "title": "x"}),
                     id="them-tieu-de"),
        pytest.param("POST", "/wp/v2/posts/42", _with(json={"status": "publish", "content": "x"}),
                     id="them-noi-dung"),
        pytest.param("POST", "/wp/v2/posts/42",
                     _with(json={"status": "publish", "date_gmt": DATE}), id="dang-ngay-kem-gio"),
        pytest.param("POST", "/wp/v2/posts/42", _with(json={"status": "future", "date": DATE}),
                     id="date-thay-date-gmt"),
        pytest.param("POST", "/wp/v2/posts/42",
                     _with(json={"status": "future", "date_gmt": DATE, "date": DATE}),
                     id="ca-date"),
        pytest.param("POST", "/wp/v2/posts/42", _with(json={"status": "future"}),
                     id="hen-gio-thieu-gio"),
        pytest.param("POST", "/wp/v2/posts/42",
                     _with(json={"status": "future", "date_gmt": "2026-12-01 01:00:00"}),
                     id="gio-sai-dang"),
        pytest.param("POST", "/wp/v2/posts/42",
                     _with(json={"status": "future", "date_gmt": DATE + "Z"}), id="gio-co-duoi"),
        pytest.param("POST", "/wp/v2/posts/42",
                     _with(json={"status": "future", "date_gmt": "２０２６-12-01T01:00:00"}),
                     id="chu-so-toan-kho"),
        pytest.param("POST", "/wp/v2/posts/42",
                     _with(json={"status": "future", "date_gmt": 1764550800}), id="gio-la-so"),
        pytest.param("POST", "/wp/v2/posts/42", _with(json={"status": "Publish"}), id="hoa"),
        pytest.param("POST", "/wp/v2/posts/42", _with(json={"status": "private"}), id="private"),
        pytest.param("POST", "/wp/v2/posts/42", _with(json={"status": "pending"}), id="pending"),
        pytest.param("POST", "/wp/v2/posts/42", _with(json={"status": "draft"}), id="draft"),
        pytest.param("POST", "/wp/v2/posts/42", _with(json={"status": ["publish"]}), id="mang"),
        pytest.param("POST", "/wp/v2/posts/42", _with(json={}), id="than-rong"),
        pytest.param("POST", "/wp/v2/posts/42", _with(json=[("status", "publish")]), id="list"),
        pytest.param("POST", "/wp/v2/posts/42", _with(params={"_fields": "id,status,content"}),
                     id="fields-noi-dung"),
        pytest.param("POST", "/wp/v2/posts/42", _with(params={"_fields": "id"}), id="fields-khac"),
        pytest.param("POST", "/wp/v2/posts/42",
                     _with(params={"_fields": _RELEASE_FIELDS, "context": "edit"}),
                     id="them-tham-so"),
        pytest.param("POST", "/wp/v2/posts/42", {"json": {"status": "publish"}}, id="thieu-params"),
        pytest.param("POST", "/wp/v2/posts/42", _with(data=b"x"), id="them-data"),
        pytest.param("POST", "/wp/v2/posts/42", _with(headers={"Content-Type": "image/webp"}),
                     id="them-header"),
    ],
)
def test_co_dau_rieng_ma_sai_khuon_thi_chan(client, fake, method, path, options):
    with pytest.raises(WordPressError, match=re.escape(_ROUTE_BLOCKED)):
        client._request(method, path, **options, release=_RELEASE)
    assert fake.requests == []


@pytest.mark.parametrize("marker", [object(), True, "release", 1, client_module.RELEASE_MODES])
def test_dau_gia_bi_chan(client, fake, marker):
    with pytest.raises(WordPressError, match=re.escape(_ROUTE_BLOCKED)):
        client._request("POST", "/wp/v2/posts/42", **RELEASE_OK, release=marker)
    assert fake.requests == []


def test_dau_rieng_dung_khuon_thi_qua_lop_kiem(client, fake):
    """Đối chứng cho hai test trên: đúng khuôn và đúng dấu thì lệnh đi (ở mức ``_request``)."""
    fake.on("POST", POST_42, {"id": 42, "status": "publish"})
    client._request("POST", "/wp/v2/posts/42", **RELEASE_OK, release=_RELEASE)
    future = {"json": {"status": "future", "date_gmt": DATE}, "params": RELEASE_OK["params"]}
    client._request("POST", "/wp/v2/posts/42", **future, release=_RELEASE)
    assert [body(r) for r in fake.requests] == [{"status": "publish"}, future["json"]]


def test_session_co_header_doi_phuong_thuc_thi_chan_ca_lenh_kiem(client, fake):
    own_draft(client, fake)
    site(fake)
    client._session.headers["X-HTTP-Method-Override"] = "DELETE"
    with pytest.raises(ReleaseError, match=re.escape(_ROUTE_BLOCKED)):
        client.release_draft(42, mode="publish")
    assert fake.requests == []


def _functions_using(tree: ast.AST, name: str) -> set[str]:
    """Tên hàm trong cùng (hay ``<module>``) có dùng tên ``name`` (biến ``name`` hay thuộc tính
    ``.name``)."""
    found: set[str] = set()

    def walk(node: ast.AST, scope: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef):
                walk(child, child.name)
                continue
            if (isinstance(child, ast.Name) and child.id == name) or (
                isinstance(child, ast.Attribute) and child.attr == name
            ):
                found.add(scope)
            walk(child, scope)

    walk(tree, "<module>")
    return found


CLIENT_SOURCE = PROJECT_ROOT / "seo_app" / "wordpress" / "client.py"


def _python_files() -> list[Path]:
    return [
        path
        for folder in ("seo_app", "app")
        for path in (PROJECT_ROOT / folder).rglob("*.py")
    ]


def test_dau_rieng_chi_o_dinh_nghia_release_draft_va_lop_kiem():
    tree = ast.parse(CLIENT_SOURCE.read_text(encoding="utf-8"))
    assert _functions_using(tree, "_RELEASE") == {"<module>", "release_draft", "_is_plain_request"}
    module_level = [
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "_RELEASE" for t in node.targets)
    ]
    assert len(module_level) == 1  # chỉ một chỗ định nghĩa
    others = [
        path
        for path in _python_files()
        if path != CLIENT_SOURCE and re.search(r"\b_RELEASE\b", path.read_text(encoding="utf-8"))
    ]
    assert others == []


def test_release_draft_chi_duoc_goi_tu_mot_ham_buoc_xuat_ban():
    """Hiện chưa ai gọi (T-102 sẽ gọi từ đúng một hàm của ``app/views/write.py``)."""
    callers = {
        (path.relative_to(PROJECT_ROOT).as_posix(), scope)
        for path in _python_files()
        if path != CLIENT_SOURCE
        for scope in _functions_using(
            ast.parse(path.read_text(encoding="utf-8")), "release_draft"
        )
    }
    assert len(callers) <= 1
    assert all(file == "app/views/write.py" and scope != "<module>" for file, scope in callers)


def test_trong_client_chi_release_draft_gui_lenh_co_dau():
    """Không hàm nào khác của client truyền ``release=`` vào ``_request``."""
    tree = ast.parse(CLIENT_SOURCE.read_text(encoding="utf-8"))
    senders = set()
    for function in ast.walk(tree):
        if not isinstance(function, ast.FunctionDef):
            continue
        for node in ast.walk(function):
            if isinstance(node, ast.Call) and any(k.arg == "release" for k in node.keywords):
                senders.add(function.name)
    assert senders == {"release_draft", "_request"}


def test_tao_nhap_van_chi_draft(client, fake):
    fake.on("POST", POSTS, {"id": 42, "status": "draft"})
    client.create_draft("Bài", "<p>x</p>")
    assert body(fake.requests[0])["status"] == "draft"


# ====================================================================== LC-T094-23: chỉ bài vừa tạo


@pytest.mark.parametrize("post_id", [42, True, "42", 42.0, None, -42])
def test_bai_khong_do_client_tao_thi_tu_choi_khong_request(client, fake, post_id):
    site(fake)
    with pytest.raises(ReleaseError) as caught:
        client.release_draft(post_id, mode="publish")
    assert not caught.value.unsure and not caught.value.went_public
    assert fake.requests == []


def test_client_cua_luot_khac_khong_chuyen_duoc(client, fake):
    own_draft(client, fake)
    other = WordPressClient(BASE_URL, "lam", "abcd efgh ijkl", session=make_session(fake))
    site(fake)
    with pytest.raises(ReleaseError, match="vừa tạo trong chính lần gửi này"):
        other.release_draft(42, mode="future", when_utc=TOMORROW)
    assert fake.requests == []


def test_ma_bai_tu_post_statuses_khong_thanh_bai_duoc_sua(client, fake):
    fake.on("GET", POSTS, [{"id": 42, "status": "draft"}])
    assert client.post_statuses([42])[42].status == "draft"
    fake.requests.clear()
    site(fake)
    with pytest.raises(ReleaseError):
        client.release_draft(42, mode="publish")
    assert fake.requests == []


@pytest.mark.parametrize(
    "check",
    [
        {"id": 42, "status": "publish"},
        {"id": 42, "status": "future"},
        {"id": 42, "status": "pending"},
        {"id": 42, "status": "private"},
        {"id": 42, "status": "trash"},
        {"id": 42, "status": "Draft"},
        {"id": 43, "status": "draft"},
        {"id": "42", "status": "draft"},
        [{"id": 42, "status": "draft"}],
    ],
)
def test_site_bao_khong_con_la_nhap_thi_khong_gui_lenh_chuyen(client, fake, check):
    own_draft(client, fake)
    site(fake, check=check)
    with pytest.raises(ReleaseError, match="không còn là nháp") as caught:
        client.release_draft(42, mode="publish")
    assert not caught.value.unsure
    assert paths(fake) == [("GET", POST_42)]
    fake.requests.clear()
    with pytest.raises(WordPressError):
        client.set_featured_image(42, 7)  # không còn là «bài app được sửa»
    assert fake.requests == []


@pytest.mark.parametrize("status", [401, 403, 404, 500, 503])
def test_khong_kiem_duoc_nhap_thi_khong_gui_lenh_chuyen(client, fake, status):
    own_draft(client, fake)
    site(fake, check={"code": "x", "message": BAIT}, check_status=status)
    with pytest.raises(ReleaseError, match="Không kiểm được bài nháp") as caught:
        client.release_draft(42, mode="future", when_utc=TOMORROW)
    assert BAIT not in str(caught.value) and not caught.value.unsure
    assert caught.value.status_code == status
    assert paths(fake) == [("GET", POST_42)]


def test_loi_la_luc_kiem_nhap_thi_khong_gui_lenh_chuyen(client, fake, monkeypatch):
    own_draft(client, fake)
    site(fake)

    def boom(method, url, **kwargs):
        raise RuntimeError(BAIT)

    monkeypatch.setattr(client._session, "request", boom)
    with pytest.raises(ReleaseError, match="vẫn là nháp") as caught:
        client.release_draft(42, mode="publish")
    assert not caught.value.unsure and BAIT not in str(caught.value)
    assert 42 in client._created_post_ids  # chưa gửi lệnh chuyển


def test_mat_mang_luc_kiem_nhap_thi_khong_gui_lenh_chuyen(client, fake):
    own_draft(client, fake)
    fake.on("GET", POST_42, requests.exceptions.ConnectTimeout("x"))
    with pytest.raises(ReleaseError, match="vẫn là nháp"):
        client.release_draft(42, mode="publish")
    assert paths(fake) == [("GET", POST_42)]


# ====================================================================== LC-T094-24: giờ


@pytest.mark.parametrize("when", [TOMORROW.replace(tzinfo=None), date(2026, 11, 3), STAMP, 0,
                                  None])
def test_gio_hen_khong_mui_gio_hay_sai_kieu_thi_khong_request(client, fake, when):
    own_draft(client, fake)
    site(fake)
    with pytest.raises(ReleaseError, match="múi giờ rõ ràng"):
        client.release_draft(42, mode="future", when_utc=when)
    assert fake.requests == []


def test_dang_ngay_kem_gio_thi_khong_request(client, fake):
    own_draft(client, fake)
    site(fake)
    with pytest.raises(ReleaseError, match="không kèm giờ hẹn"):
        client.release_draft(42, mode="publish", when_utc=TOMORROW)
    assert fake.requests == []


@pytest.mark.parametrize("mode", ["draft", "Future", "pending", "private", "", None, 1])
def test_hinh_thuc_la_thi_khong_request(client, fake, mode):
    own_draft(client, fake)
    site(fake)
    with pytest.raises(ReleaseError, match="hẹn giờ hoặc đăng ngay"):
        client.release_draft(42, mode=mode, when_utc=TOMORROW)
    assert fake.requests == []


@pytest.mark.parametrize(
    "date_header",
    [
        "",  # không có header
        "garbage",
        "Tue, 99 Nov 2026 01:00:00 GMT",
        "Mon, 02 Nov 2026 01:00:00 -0000",  # không rõ múi giờ
        "Mon, 02 Nov 2026 01:00:00 GMT" + " " * 60,  # quá dài
        "Th\N{LATIN SMALL LETTER U WITH HORN}, 02 Nov 2026 01:00:00 GMT",
    ],
)
@pytest.mark.parametrize("mode", ["future", "publish"])
def test_khong_doc_duoc_gio_may_chu_thi_chan(client, fake, date_header, mode):
    own_draft(client, fake)
    site(fake, date_header=date_header)
    with pytest.raises(ReleaseError, match="Không đọc được giờ của website") as caught:
        client.release_draft(42, mode=mode, when_utc=TOMORROW if mode == "future" else None)
    assert not caught.value.unsure
    assert paths(fake) == [("GET", POST_42)]


@pytest.mark.parametrize("skew", [timedelta(minutes=3), -timedelta(minutes=3),
                                  timedelta(minutes=2, seconds=1), timedelta(days=400)])
@pytest.mark.parametrize("mode", ["future", "publish"])
def test_dong_ho_may_lech_qua_2_phut_thi_chan(client, fake, monkeypatch, skew, mode):
    own_draft(client, fake)
    site(fake)
    set_clock(monkeypatch, NOW + skew)
    with pytest.raises(ReleaseError, match="Đồng hồ máy tính lệch"):
        client.release_draft(42, mode=mode, when_utc=TOMORROW if mode == "future" else None)
    assert paths(fake) == [("GET", POST_42)]


@pytest.mark.parametrize(
    ("when", "message"),
    [
        (NOW - timedelta(days=1), "đã qua"),
        (NOW, "đã qua"),
        (NOW + timedelta(minutes=9, seconds=59), "ít nhất 10 phút"),
        (NOW + timedelta(minutes=9, seconds=59, microseconds=999_999), "ít nhất 10 phút"),
        (NOW + timedelta(days=365, seconds=1), "xa hơn một năm"),
        (NOW + timedelta(days=400), "xa hơn một năm"),
    ],
)
def test_gio_hen_qua_gan_hay_qua_xa_theo_gio_may_chu_thi_chan(client, fake, when, message):
    own_draft(client, fake)
    site(fake)
    with pytest.raises(ReleaseError, match=message):
        client.release_draft(42, mode="future", when_utc=when)
    assert paths(fake) == [("GET", POST_42)]


@pytest.mark.parametrize("gap", [timedelta(minutes=10), timedelta(days=365)])
def test_bien_10_phut_va_365_ngay_duoc_gui(client, fake, gap):
    own_draft(client, fake)
    site(fake, answer=lambda r: {"id": 42, "status": "future", **body(r)})
    client.release_draft(42, mode="future", when_utc=NOW + gap)
    assert paths(fake)[-1] == ("POST", POST_42)


def test_moc_10_phut_tinh_theo_gio_may_chu_khong_theo_dong_ho_may(client, fake, monkeypatch):
    """Đồng hồ máy nhanh 90 giây (trong mức 2 phút): giờ hẹn = giờ máy chủ + 10 phút vẫn được;
    giờ máy chủ chậm hơn giờ hẹn 9 phút 59 giây thì chặn dù đồng hồ máy nói đã đủ."""
    own_draft(client, fake)
    site(fake, answer=lambda r: {"id": 42, "status": "future", **body(r)})
    set_clock(monkeypatch, NOW + timedelta(seconds=90))
    client.release_draft(42, mode="future", when_utc=NOW + timedelta(minutes=10))
    own_draft(client, fake, 43)
    site(fake, post_id=43, date_header=http_date(NOW + timedelta(seconds=1)))
    set_clock(monkeypatch, NOW - timedelta(seconds=60))
    with pytest.raises(ReleaseError, match="ít nhất 10 phút"):
        client.release_draft(43, mode="future", when_utc=NOW + timedelta(minutes=10))
    assert paths(fake) == [("GET", f"{POSTS}/43")]


def test_gio_may_chu_lay_tu_chinh_cau_tra_loi_kiem_nhap(client, fake):
    """Câu trả lời tạo bài có ``Date`` đúng nhưng câu trả lời kiểm nháp ngay trước lệnh không có:
    vẫn chặn (không dùng giờ của lệnh trước)."""
    fake.on("POST", POSTS, lambda r: (201, {"id": 42, "status": "draft"},
                                      {"Date": http_date(NOW)}))
    client.create_draft("Bài", "<p>x</p>")
    fake.requests.clear()
    site(fake, date_header="")
    with pytest.raises(ReleaseError, match="Không đọc được giờ"):
        client.release_draft(42, mode="publish")
    assert paths(fake) == [("GET", POST_42)]


def test_bi_chan_vi_gio_thi_bai_van_la_cua_client(client, fake):
    """Chặn trước khi gửi lệnh chuyển: chưa gì thay đổi, client vẫn coi là bài nháp của mình."""
    own_draft(client, fake)
    site(fake)
    with pytest.raises(ReleaseError):
        client.release_draft(42, mode="future", when_utc=NOW + timedelta(minutes=5))
    assert 42 in client._created_post_ids


# ====================================================================== LC-T094-25: câu trả lời


def test_hen_gio_ma_site_dang_ngay_thi_bao_khan_va_dung(client, fake):
    own_draft(client, fake)
    site(fake, answer={"id": 42, "status": "publish", "date_gmt": STAMP, "link": LINK})
    with pytest.raises(ReleaseError, match="KHẨN") as caught:
        client.release_draft(42, mode="future", when_utc=TOMORROW)
    error = caught.value
    assert error.went_public and not error.unsure
    assert error.post_id == 42 and error.edit_link == client.edit_link(42)
    assert "Bản nháp" in str(error)
    assert paths(fake) == [("GET", POST_42), ("POST", POST_42)]  # không gửi thêm gì
    assert 42 not in client._created_post_ids


@pytest.mark.parametrize(
    ("mode", "answer", "message"),
    [
        ("future", {"id": 42, "status": "future", "date_gmt": "2026-11-03T02:00:00"},
         "giờ hẹn khác"),
        ("future", {"id": 42, "status": "future"}, "giờ hẹn khác"),
        ("future", {"id": 42, "status": "future", "date_gmt": None}, "giờ hẹn khác"),
        ("future", {"id": 42, "status": "draft", "date_gmt": STAMP}, "không đúng như mong đợi"),
        ("future", {"id": 42, "status": "pending", "date_gmt": STAMP}, "không đúng như mong đợi"),
        ("future", {"id": 43, "status": "future", "date_gmt": STAMP}, "không đúng như mong đợi"),
        ("future", {"id": "42", "status": "future", "date_gmt": STAMP},
         "không đúng như mong đợi"),
        ("publish", {"id": 42, "status": "future", "date_gmt": STAMP}, "không đúng như mong đợi"),
        ("publish", {"id": 42, "status": "private"}, "không đúng như mong đợi"),
        ("publish", {"id": 42, "status": ["publish"]}, "không đúng như mong đợi"),
        ("publish", {"id": 42}, "không đúng như mong đợi"),
        ("publish", [{"id": 42, "status": "publish"}], "không đúng như mong đợi"),
        ("publish", "publish", "không đúng như mong đợi"),
        ("publish", (200, b"<html>ok</html>", {}), "Không biết chắc"),
    ],
)
def test_cau_tra_loi_sai_thi_co_the_da_chuyen_khong_gui_lai(client, fake, mode, answer, message):
    own_draft(client, fake)
    site(fake, answer=answer)
    with pytest.raises(ReleaseError, match=message) as caught:
        client.release_draft(42, mode=mode, when_utc=TOMORROW if mode == "future" else None)
    assert caught.value.unsure and not caught.value.went_public
    assert paths(fake) == [("GET", POST_42), ("POST", POST_42)]
    assert 42 not in client._created_post_ids


@pytest.mark.parametrize("status", [400, 401, 403, 404, 409, 429])
def test_tu_choi_4xx_thi_bai_van_la_nhap(client, fake, status):
    own_draft(client, fake)
    site(fake, answer=(status, {"code": "rest_cannot_publish", "message": BAIT}, {}))
    with pytest.raises(ReleaseError, match="bài vẫn là nháp trên website") as caught:
        client.release_draft(42, mode="publish")
    error = caught.value
    assert not error.unsure and not error.went_public and error.status_code == status
    assert BAIT not in str(error) and BASE_URL not in str(error)
    assert paths(fake) == [("GET", POST_42), ("POST", POST_42)]


@pytest.mark.parametrize(
    "answer",
    [
        (500, {"code": "x", "message": BAIT}, {}),
        (502, b"<html>Bad gateway</html>", {}),
        (301, {"message": BAIT}, {"Location": "https://evil.example/"}),
        requests.exceptions.ReadTimeout("hết giờ " + BAIT),
        requests.exceptions.ConnectionError("mất mạng " + BAIT),
        requests.exceptions.ChunkedEncodingError("đứt " + BAIT),
    ],
)
@pytest.mark.parametrize("mode", ["future", "publish"])
def test_loi_khong_ro_thi_co_the_da_chuyen_khong_tu_gui_lai(client, fake, answer, mode):
    own_draft(client, fake)
    site(fake, answer=answer)  # ngoại lệ ``requests``: site giả ném ra như lỗi mạng
    with pytest.raises(ReleaseError, match="có thể đã") as caught:
        client.release_draft(42, mode=mode, when_utc=TOMORROW if mode == "future" else None)
    error = caught.value
    assert error.unsure and not error.went_public
    assert "không tự gửi lại" in str(error)
    assert BAIT not in str(error) and BASE_URL not in str(error)
    assert paths(fake) == [("GET", POST_42), ("POST", POST_42)]
    fake.requests.clear()
    with pytest.raises(ReleaseError):  # gọi lại: không gửi gì
        client.release_draft(42, mode=mode, when_utc=TOMORROW if mode == "future" else None)
    assert fake.requests == []


def test_loi_la_khi_gui_thi_co_the_da_chuyen(client, fake, monkeypatch):
    own_draft(client, fake)
    site(fake)
    original = client._session.request

    def boom(method, url, **kwargs):
        if method == "POST":
            raise RuntimeError(BAIT)
        return original(method, url, **kwargs)

    monkeypatch.setattr(client._session, "request", boom)
    with pytest.raises(ReleaseError, match="có thể đã") as caught:
        client.release_draft(42, mode="publish")
    assert caught.value.unsure and BAIT not in str(caught.value)


# ====================================================================== LC-T094-26: post_statuses


def test_post_statuses_mot_lenh_chi_doc_tham_so_hang(client, fake):
    fake.on("GET", POSTS, [
        {"id": 1, "status": "publish", "date_gmt": "2026-10-01T01:00:00",
         "modified_gmt": "2026-10-02T01:00:00", "link": f"{BASE_URL}/a/"},
        {"id": 2, "status": "future", "date_gmt": STAMP, "modified_gmt": STAMP,
         "link": f"{BASE_URL}/?p=2"},
        {"id": 3, "status": "draft", "date_gmt": None, "modified_gmt": "x", "link": "javascript:x"},
    ])
    states = client.post_statuses([3, 1, 2, 2])
    (request,) = fake.requests
    assert (request.method, urlsplit(request.url).path) == ("GET", POSTS)
    assert query(request) == {
        "include": ["1,2,3"],
        "status": [POST_STATUS_FILTER],
        "context": ["edit"],
        "per_page": [str(MAX_STATUS_IDS)],
        "_fields": [_STATUS_FIELDS],
    }
    assert "content" not in _STATUS_FIELDS and "excerpt" not in _STATUS_FIELDS
    assert states == {
        1: PostState(1, "publish", "2026-10-01T01:00:00", "2026-10-02T01:00:00", f"{BASE_URL}/a/"),
        2: PostState(2, "future", STAMP, STAMP, f"{BASE_URL}/?p=2"),
        3: PostState(3, "draft", "", "", ""),
    }
    assert client._created_post_ids == set()


def test_post_statuses_bo_muc_la(client, fake):
    fake.on("GET", POSTS, [
        {"id": 5, "status": "publish"},  # không hỏi
        {"id": 1, "status": "trash"},
        {"id": 2, "status": "inherit"},
        {"id": True, "status": "publish"},
        {"id": "3", "status": "publish"},
        {"id": 4, "status": None},
        "x",
        {"id": 6, "status": "publish", "date_gmt": "２０２６-10-01T01:00:00"},
        {"id": 6, "status": "draft"},  # trùng: giữ mục đầu
    ])
    states = client.post_statuses([1, 2, 3, 4, 6])
    assert states == {6: PostState(6, "publish")}


def test_post_statuses_chia_lenh_moi_lenh_toi_da_100_ma(client, fake):
    fake.on("GET", POSTS, [])
    client.post_statuses(range(1, 251))
    includes = [query(r)["include"][0].split(",") for r in fake.requests]
    assert [len(chunk) for chunk in includes] == [100, 100, 50]


def test_post_statuses_rong_thi_khong_hoi(client, fake):
    assert client.post_statuses([]) == {}
    assert fake.requests == []


@pytest.mark.parametrize(
    "ids",
    [
        ["1"],
        [0],
        [-1],
        [True],
        [1.0],
        [2**63],
        [1, None],
        "1,2",
        b"12",
        None,
        5,
        {1: 1},
        range(1, MAX_STATUS_LOOKUP + 2),
    ],
)
def test_post_statuses_ma_sai_thi_khong_hoi(client, fake, ids):
    with pytest.raises(WordPressError, match="Chưa hỏi website"):
        client.post_statuses(ids)
    assert fake.requests == []


def test_post_statuses_tra_khong_phai_danh_sach_thi_bao_loi(client, fake):
    fake.on("GET", POSTS, {"id": 1, "status": "publish"})
    with pytest.raises(WordPressError, match="không đúng dạng danh sách"):
        client.post_statuses([1])


def test_post_statuses_loi_may_chu_cau_co_dinh(client, fake):
    fake.on("GET", POSTS, (500, {"code": "x", "message": BAIT}, {}))
    with pytest.raises(WordPressError) as caught:
        client.post_statuses([1])
    assert BAIT not in str(caught.value)


@pytest.mark.parametrize(
    "params",
    [
        {"include": "1,a"},
        {"include": "-1"},
        {"include": "1,2;3"},
        {"include": "1, 2"},
        {"include": " 1"},
        {"include": "01"},
        {"include": "0"},
        {"include": ""},
        {"include": "1,"},
        {"include": "１"},
        {"include": 5},
        {"include": ",".join(["7"] * (MAX_STATUS_IDS + 1))},
        {"include": "1", "status": "any"},
        {"include": "1", "status": "draft"},
        {"include": "1", "status": "publish,trash"},
        {"include": "1", "status": POST_STATUS_FILTER + ",trash"},
        {"include": "1", "context": "view"},
        {"include": "1", "context": "embed"},
        {"include": "1", "_fields": "id,content"},
        {"include": "1", "_fields": "id,excerpt.rendered"},
    ],
)
def test_tham_so_doc_trang_thai_sai_gia_tri_thi_chan(client, fake, params):
    with pytest.raises(WordPressError, match=re.escape(_ROUTE_BLOCKED)):
        client._request("GET", "/wp/v2/posts", params=params)
    assert fake.requests == []


@pytest.mark.parametrize("path", ["/wp/v2/pages", "/wp/v2/posts/42", "/wp/v2/categories"])
def test_include_chi_cho_get_posts(client, fake, path):
    with pytest.raises(WordPressError, match=re.escape(_ROUTE_BLOCKED)):
        client._request("GET", path, params={"include": "1"})
    assert fake.requests == []


def test_include_dung_100_ma_duoc_gui_va_list_published_van_chay(client, fake):
    fake.on("GET", POSTS, [])
    fake.on("GET", "/wp-json/wp/v2/pages", [])
    client._request("GET", "/wp/v2/posts", params={"include": ",".join(["7"] * MAX_STATUS_IDS)})
    client.list_published()
    assert len(fake.requests) == 3


# ====================================================================== LC-T094-27: múi giờ site


def connect(fake: FakeWordPress, client: WordPressClient, **root: object) -> ConnectionInfo:
    fake.on("GET", "/wp-json/", {"name": "Site", "namespaces": ["wp/v2"], **root})
    fake.on("GET", "/wp-json/wp/v2/users/me", {"name": "Lâm", "roles": ["editor"],
                                               "capabilities": {"publish_posts": True}})
    return client.check_connection()


def test_mui_gio_ho_chi_minh_khong_canh_bao(client, fake):
    info = connect(fake, client, timezone_string="Asia/Ho_Chi_Minh", gmt_offset=7)
    assert (info.timezone_string, info.gmt_offset) == ("Asia/Ho_Chi_Minh", 7.0)
    assert info.timezone_warning() == ""


def test_do_lech_dang_chu_cung_doc_duoc(client, fake):
    info = connect(fake, client, timezone_string="", gmt_offset="7")
    assert info.gmt_offset == 7.0 and info.timezone_warning() == ""


@pytest.mark.parametrize(
    ("offset", "shown"),
    [(0, "UTC+0"), ("5.5", "UTC+5:30"), (-3.5, "UTC−3:30"), (8, "UTC+8")],
)
def test_mui_gio_khac_thi_canh_bao_chi_chen_so(client, fake, offset, shown):
    info = connect(fake, client, timezone_string="Evil/Zone_Name", gmt_offset=offset)
    warning = info.timezone_warning()
    assert shown in warning and "khác giờ Việt Nam" in warning
    assert "Evil" not in warning


@pytest.mark.parametrize(
    ("zone", "offset"),
    [
        ("<script>", "abc"),
        ("a" * 100, True),
        (5, 99),
        (None, None),
        (["Asia/Ho_Chi_Minh"], [7]),
        ("Asia/Ho_Chi_Minh\n", "7; DROP"),
        ("Asia/Hồ", float("nan")),
        ("", "1e1"),
        ("", "７"),
    ],
)
def test_mui_gio_la_thi_bo_va_canh_bao_khong_doc_duoc(client, fake, zone, offset):
    info = connect(fake, client, timezone_string=zone, gmt_offset=offset)
    assert info.timezone_string == "" and info.gmt_offset is None
    assert "Không đọc được múi giờ" in info.timezone_warning()


def test_mui_gio_cua_phan_mem_khac_viet_nam(client, fake):
    info = connect(fake, client, timezone_string="UTC", gmt_offset=0)
    assert info.timezone_warning("UTC") == ""
    assert "khác giờ Asia/Tokyo" in info.timezone_warning("Asia/Tokyo")


def test_site_khong_tra_mui_gio(client, fake):
    info = connect(fake, client)
    assert info.timezone_string == "" and info.gmt_offset is None


def test_connection_info_cu_van_tao_duoc_khong_can_mui_gio():
    info = ConnectionInfo("Site", BASE_URL, "Lâm", ("editor",), True, True, True)
    assert info.gmt_offset is None and info.timezone_string == ""
