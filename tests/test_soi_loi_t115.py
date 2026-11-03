"""Soi Lỗi T-115 (rút gọn): ``release_draft`` so ``modified_gmt`` ngay trước lệnh chuyển
(LC-T094-23); chặn luôn LC-T102-1 ở lớp client.

Kiểm độc lập. Website giả riêng ``_ModSite`` (adapter ``requests``) có đồng hồ riêng và nhớ từng
bài như WordPress: mọi lệnh ghi REST vào bài (tạo, ảnh đại diện, meta, chuyển) đi qua
``wp_update_post`` nên đặt ``modified_gmt`` = giờ lúc đó, **tính theo giây**; chỉ trả trường
``_fields`` xin (``rest_filter_response_fields``); ghi SEO qua Abilities của SiteSEO chỉ đổi meta
(``update_post_meta``: giờ sửa giữ nguyên) hoặc đổi giờ theo tùy chọn; có lối «sửa ngoài app»
(trang quản trị, plugin). Không dùng ``FakeWordPress``, site giả hay bảng kỳ vọng của Thợ Máy (trừ
ca giao diện cuối, mượn khung bước Xuất bản của ``test_t102_publish`` như file T-102 của Soi Lỗi).

1. Mọi đường tới ``future``/``publish`` qua phép so: hai hình thức; chỉ ``release_draft`` gửi lệnh
   mang dấu chuyển, phép so đứng trước lệnh đó.
2. Bị sửa ngoài app ở mọi chỗ (sau tạo, giữa các lệnh ghi, sau lệnh ghi cuối), ghi SEO qua meta
   hay Abilities: không chuyển, bài vẫn nháp, câu cố định, không trả mã; biên giây.
3. Giá trị lạ ở lệnh tạo, lệnh ghi, lệnh kiểm (múi giờ, rỗng, số, chuỗi dài, NaN…).
4. Abilities không trả ``modified_gmt``: giữ giá trị nhớ; Abilities đổi giờ sửa thì từ chối.
5. Lệnh ghi lỗi giữa chừng: «không biết»; từ chối 4xx rõ ràng ở meta: giữ.
6. Hai client, hai bài, hai tab.
7. Trang Soạn bài (công tắc bật trong test): bài bị sửa ngay trước lệnh chuyển thì không hẹn giờ.

Không gọi website thật (bộ chặn mạng của ``tests/conftest.py`` bật suốt).
"""

from __future__ import annotations

import ast
import json
from datetime import UTC, datetime, timedelta
from email.utils import format_datetime
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
import requests
import test_app_images as ui
import test_t102_publish as t102
from fake_wordpress import siteseo_seo_answer
from requests.adapters import BaseAdapter
from requests.structures import CaseInsensitiveDict

import seo_app.wordpress.client as wp
from seo_app.storage import site_index
from seo_app.wordpress.client import ReleaseError, WordPressClient, WordPressError

BASE = "https://example.com"
API = "/wp-json/wp/v2"
ABILITY = f"/wp-json{wp.SITESEO_ABILITY_PATH}"
MOI = "MOI-T115 <b>x</b> https://evil.example"
MAT_KHAU_GIA = "abcd efgh ijkl mnop"  # Application Password giả
T0 = datetime(2026, 11, 2, 1, 0, 0, tzinfo=UTC)
CLIENT_PY = Path(__file__).resolve().parents[1] / "seo_app" / "wordpress" / "client.py"
SEO = {"title": "Sửa cổng inox tại nhà", "description": "Thợ tới tận nơi, báo giá trước khi làm."}

# Khung bước Xuất bản (ca giao diện cuối), như ``test_soi_loi_t102.py``.
env = ui.env
previews = ui.previews
fake_ai = ui.fake_ai
root = ui.root
site = ui.site
live = t102.live


@pytest.fixture(autouse=True)
def site_cache(monkeypatch, tmp_path_factory):
    """Cache danh sách bài đã đăng trong thư mục tạm (không tạo ``data/site_index.sqlite``)."""
    path = tmp_path_factory.mktemp("danh-sach-bai") / "site_index.sqlite"
    monkeypatch.setattr(site_index, "DEFAULT_SITE_INDEX_FILE", path)
    return path


class _ModSite(BaseAdapter):
    """WordPress giả có đồng hồ riêng (``now``) và trạng thái từng bài. ``inject``: (phương thức,
    đường) → câu trả lời/ngoại lệ, hay hàm ``(request) -> câu trả lời | None`` (``None``: làm như
    thường). ``raw_modified``: loại lệnh → token JSON viết tay thay ``modified_gmt`` trong câu trả
    lời (``None``: bỏ khóa); loại lệnh: ``tao``, ``anh`` (ảnh đại diện), ``meta``, ``doc`` (đọc
    trước lệnh ghi), ``kiem`` (đọc ngay trước lệnh chuyển)."""

    def __init__(self) -> None:
        super().__init__()
        self.now = T0
        self.posts: dict[int, dict] = {}
        self.requests: list[requests.PreparedRequest] = []
        self.inject: dict[tuple[str, str], object] = {}
        self.raw_modified: dict[str, str | None] = {}
        self.next_post = 42
        self.abilities = False  # Abilities của SiteSEO chưa bật: ghi SEO qua meta dự phòng
        self.ability_bumps = False  # lệnh ghi SEO qua Abilities có đổi giờ sửa bài không

    def tick(self, seconds: float = 2) -> None:
        self.now += timedelta(seconds=seconds)

    def stamp(self) -> str:
        return self.now.strftime("%Y-%m-%dT%H:%M:%S")  # như ``post_modified_gmt``: tới giây

    def edit_outside(self, post_id: int = 42) -> None:
        """Ai đó lưu bài trong trang quản trị (``wp_update_post``): đổi nội dung và giờ sửa."""
        self.posts[post_id].update(content="<p>Bản người khác sửa</p>", modified=self.stamp())

    def view(self, post_id: int) -> dict:
        post = self.posts[post_id]
        return {
            "id": post_id, "status": post["status"], "title": {"raw": post["title"]},
            "link": f"{BASE}/?p={post_id}", "featured_media": post["featured_media"],
            "meta": dict(post["meta"]), "modified_gmt": post["modified"],
            "date_gmt": post["date_gmt"],
        }

    def _body(self, data: dict, kind: str, fields: list[str] | None) -> dict | bytes:
        data = data if fields is None else {k: v for k, v in data.items() if k in fields}
        if kind not in self.raw_modified or "modified_gmt" not in data:
            return data
        token = self.raw_modified[kind]
        text = json.dumps({k: v for k, v in data.items() if k != "modified_gmt"})
        if token is not None:
            text = text[:-1] + f', "modified_gmt": {token}}}'
        return text.encode()

    def _answer(self, request: requests.PreparedRequest):
        parts = urlsplit(request.url)
        path, query = parts.path, parse_qs(parts.query)
        hook = self.inject.get((request.method, path))
        if hook is not None:
            answer = hook(request) if callable(hook) else hook
            if answer is not None:
                return answer
        sent = json.loads(request.body) if request.body else {}
        fields = query["_fields"][0].split(",") if "_fields" in query else None
        if request.method == "POST" and path == f"{API}/posts":
            post_id, self.next_post = self.next_post, self.next_post + 1
            self.posts[post_id] = {
                "status": sent.get("status"), "title": sent.get("title"),
                "content": sent.get("content"), "featured_media": 0,
                "meta": dict.fromkeys(wp._META_FIELDS.values(), ""),
                "modified": self.stamp(), "date_gmt": None,
            }
            return 201, self._body(self.view(post_id), "tao", fields)
        if path.startswith(f"{API}/posts/"):
            post_id = int(path.rsplit("/", 1)[1])
            post = self.posts.get(post_id)
            if post is None:
                return 404, {"code": "rest_post_invalid_id", "message": MOI}
            if request.method == "GET":
                kind = "doc" if fields and "meta" in fields else "kiem"
                date = {"Date": format_datetime(self.now, usegmt=True)}
                return 200, self._body(self.view(post_id), kind, fields), date
            post["meta"].update(sent.get("meta", {}))
            for key in ("featured_media", "status", "date_gmt"):
                if key in sent:
                    post[key] = sent[key]
            post["modified"] = self.stamp()  # mọi lệnh ghi REST đi qua ``wp_update_post``
            kind = "anh" if "featured_media" in sent else "meta" if "meta" in sent else "chuyen"
            return 200, self._body(self.view(post_id), kind, fields)
        if request.method == "GET" and path == ABILITY:
            if self.abilities:
                return 200, {"name": wp.SITESEO_ABILITY}
            return 404, {"code": "rest_no_route", "message": MOI}
        if request.method == "POST" and path == f"{ABILITY}/run":
            post = self.posts[sent["input"]["postId"]]
            post["seo"] = dict(sent["input"])  # SiteSEO lưu khóa meta (``update_post_meta``)
            if self.ability_bumps:
                post["modified"] = self.stamp()
            return 200, siteseo_seo_answer(request)
        return 404, {"code": "rest_no_route", "message": MOI}

    def send(self, request, **kwargs):
        self.requests.append(request)
        answer = self._answer(request)
        if isinstance(answer, BaseException):
            raise answer
        status, body, *rest = answer
        response = requests.Response()
        response.status_code = status
        response._content = body if isinstance(body, bytes) else json.dumps(body).encode()
        response.headers = CaseInsensitiveDict(
            {"Content-Type": "application/json; charset=UTF-8", **(rest[0] if rest else {})})
        response.encoding = "utf-8"
        response.url = request.url
        response.request = request
        return response

    def close(self) -> None:
        pass

    def calls(self) -> list[tuple[str, str]]:
        return [(r.method, urlsplit(r.url).path) for r in self.requests]

    def releases(self) -> list[dict]:
        """Lệnh chuyển trạng thái đã gửi (``POST`` bài có mã, thân có ``status``)."""
        return [
            json.loads(r.body) for r in self.requests
            if r.method == "POST" and urlsplit(r.url).path.startswith(f"{API}/posts/")
            and "status" in json.loads(r.body)
        ]


def _client(wp_site: _ModSite, **kwargs) -> WordPressClient:
    session = requests.Session()
    session.mount("https://", wp_site)
    return WordPressClient(BASE, "lam", MAT_KHAU_GIA, session=session, **kwargs)


@pytest.fixture
def wp_site(monkeypatch) -> _ModSite:
    fake = _ModSite()
    monkeypatch.setattr(wp, "_utc_now", lambda: fake.now)  # đồng hồ máy = đồng hồ website
    return fake


@pytest.fixture
def client(wp_site) -> WordPressClient:
    return _client(wp_site, write_seo=True)


STEPS = ("sau-tao", "sau-anh", "sau-seo")
MODES = ("publish", "future")


def _prepare(client: WordPressClient, wp_site: _ModSite, edit_after: str = "") -> int:
    """Như bước Xuất bản (T-102): tạo nháp, ảnh đại diện, ghi SEO, mỗi bước cách 2 giây.
    ``edit_after``: ai đó sửa bài 1 giây sau bước đó."""
    post_id = client.create_draft("Sửa cổng inox", "<p>Nội dung</p>").id
    for step, action in (
        ("sau-tao", lambda: client.set_featured_image(post_id, 7)),
        ("sau-anh", lambda: client.set_seo_meta(post_id, **SEO)),
        ("sau-seo", lambda: None),
    ):
        if edit_after == step:
            wp_site.tick(1)
            wp_site.edit_outside(post_id)
        wp_site.tick()
        result = action()
        if step == "sau-anh":
            assert result.written, result.message
    return post_id


def _release(client: WordPressClient, wp_site: _ModSite, post_id: int, mode: str):
    when = wp_site.now + timedelta(days=1) if mode == "future" else None
    return client.release_draft(post_id, mode=mode, when_utc=when)


def _refused(client: WordPressClient, wp_site: _ModSite, post_id: int, mode: str) -> None:
    """Không chuyển: câu cố định, bài vẫn nháp, không lệnh chuyển, không trả mã (thử lại thì bị
    từ chối ngay, 0 lệnh)."""
    before = len(wp_site.releases())
    with pytest.raises(ReleaseError) as error:
        _release(client, wp_site, post_id, mode)
    assert str(error.value) == wp._RELEASE_CHANGED
    assert (error.value.unsure, error.value.went_public) == (False, False)
    assert len(wp_site.releases()) == before and wp_site.posts[post_id]["status"] == "draft"
    assert wp_site.calls()[-1] == ("GET", f"{API}/posts/{post_id}")  # lệnh cuối là lệnh kiểm
    sent = len(wp_site.requests)
    with pytest.raises(ReleaseError) as again:
        _release(client, wp_site, post_id, mode)
    assert str(again.value) == wp._RELEASE_NOT_OWN and len(wp_site.requests) == sent


# ====================================================================== 1. mọi đường qua phép so
@pytest.mark.parametrize("mode", MODES)
def test_khong_ai_sua_thi_chuyen_lenh_kiem_xin_modified_gmt(wp_site, client, mode):
    post_id = _prepare(client, wp_site)
    released = _release(client, wp_site, post_id, mode)
    assert released.status == mode and wp_site.posts[post_id]["status"] == mode
    check, release = wp_site.requests[-2:]
    assert (check.method, release.method) == ("GET", "POST")
    assert parse_qs(urlsplit(check.url).query)["_fields"] == ["id,status,modified_gmt"]
    assert len(wp_site.releases()) == 1


def test_chi_release_draft_gui_lenh_chuyen_va_phep_so_dung_truoc():
    tree = ast.parse(CLIENT_PY.read_text(encoding="utf-8"))

    def sends(node: ast.AST) -> list[ast.Call]:
        return [
            call for call in ast.walk(node)
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
            and call.func.attr == "_request" and any(k.arg == "release" for k in call.keywords)
        ]

    functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    assert {f.name for f in functions if sends(f)} == {"release_draft"}
    (release,) = [f for f in functions if f.name == "release_draft"]
    changed = [
        n.lineno for n in ast.walk(release)
        if isinstance(n, ast.Name) and n.id == "_RELEASE_CHANGED"
    ]
    assert changed and max(changed) < min(call.lineno for call in sends(release))


# ====================================================================== 2. bị sửa ngoài app
@pytest.mark.parametrize("abilities", [False, True], ids=["seo-meta", "seo-abilities"])
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("step", STEPS)
def test_bi_sua_ngoai_app_o_moi_cho_thi_khong_chuyen(wp_site, client, step, mode, abilities):
    wp_site.abilities = abilities
    post_id = _prepare(client, wp_site, edit_after=step)
    assert wp_site.posts[post_id]["content"] == "<p>Bản người khác sửa</p>"
    _refused(client, wp_site, post_id, mode)


def test_bien_giay_sua_sang_giay_moi_du_chi_cach_hai_phan_muoi_giay(wp_site, client):
    """``modified_gmt`` tính theo giây: lệnh ghi cuối của app lúc …:00.9, người khác sửa lúc
    …:01.1 (sang giây mới) thì bị bắt dù chỉ cách 0,2 giây."""
    wp_site.now = T0 + timedelta(seconds=0.9)
    post_id = client.create_draft("Sửa cổng inox", "<p>Nội dung</p>").id
    wp_site.tick(0.2)
    wp_site.edit_outside(post_id)
    wp_site.tick(5)
    _refused(client, wp_site, post_id, "publish")


def test_bien_giay_khong_ai_sua_thi_cach_bao_lau_van_chuyen(wp_site, client):
    post_id = client.create_draft("Sửa cổng inox", "<p>Nội dung</p>").id
    wp_site.tick(300 * 24 * 3600)  # để lâu (300 ngày) mà không ai sửa: giờ sửa vẫn khớp
    assert _release(client, wp_site, post_id, "future").status == "future"


# ====================================================================== 3. giá trị lạ
def _odd(stamp: str) -> dict[str, str | None]:
    full = stamp.translate({ord(d): ord(d) + 0xFEE0 for d in "0123456789"})  # chữ số toàn góc
    return {
        "mui-gio": json.dumps(stamp + "+07:00"), "z": json.dumps(stamp + "Z"),
        "phan-giay": json.dumps(stamp + ".000"), "dau-cach": json.dumps(stamp.replace("T", " ")),
        "t-thuong": json.dumps(stamp.replace("T", "t")), "toan-goc": json.dumps(full),
        "xuong-dong": json.dumps(stamp + "\n"), "cach-dau": json.dumps(" " + stamp),
        "dai": json.dumps(stamp * 1000), "rong": '""',
        "so-0-gio": json.dumps("0000-00-00T00:00:00"),
        "so": "0", "so-thuc": "1.5", "nan": "NaN", "inf": "Infinity", "null": "null",
        "true": "true", "mang": json.dumps([stamp]), "dict": json.dumps({"raw": stamp}),
        "thieu": None,
    }


ODD_IDS = list(_odd("2026-11-02T01:00:06"))


@pytest.mark.parametrize("name", ODD_IDS)
def test_gia_tri_la_o_lenh_kiem_thi_khong_chuyen(wp_site, client, name):
    """Lệnh kiểm trả đúng giờ đã nhớ nhưng viết khác dạng (múi giờ, phần giây, chữ số toàn
    góc…), hay giá trị lạ: không chuyển."""
    post_id = _prepare(client, wp_site)
    wp_site.raw_modified["kiem"] = _odd(wp_site.posts[post_id]["modified"])[name]
    _refused(client, wp_site, post_id, "publish")


@pytest.mark.parametrize("kind", ["tao", "anh", "meta"])
@pytest.mark.parametrize("name", ["thieu", "rong", "mui-gio", "so", "nan", "mang", "dai"])
def test_gia_tri_la_o_lenh_ghi_thi_khong_biet_khong_chuyen(wp_site, client, kind, name):
    """Lệnh ghi của app (tạo, ảnh đại diện, meta) trả giờ sửa lạ: «không biết», dù lệnh kiểm
    cuối trả đúng giờ của website."""
    wp_site.raw_modified[kind] = _odd("2026-11-02T01:00:00")[name]
    post_id = _prepare(client, wp_site)
    _refused(client, wp_site, post_id, "future")


def test_moi_lenh_cung_tra_mot_gia_tri_la_van_khong_chuyen(wp_site, client):
    for kind in ("tao", "anh", "meta", "doc", "kiem"):
        wp_site.raw_modified[kind] = '"x"'
    post_id = _prepare(client, wp_site)
    _refused(client, wp_site, post_id, "publish")


# ====================================================================== 4. Abilities
def test_abilities_khong_tra_gio_sua_giu_gia_tri_nho_thi_chuyen(wp_site, client):
    wp_site.abilities = True
    post_id = _prepare(client, wp_site)
    runs = [r for r in wp_site.requests if urlsplit(r.url).path == f"{ABILITY}/run"]
    assert len(runs) == 1 and wp_site.posts[post_id]["seo"]["title"] == SEO["title"]
    assert _release(client, wp_site, post_id, "publish").status == "publish"


def test_abilities_lam_doi_gio_sua_thi_khong_chuyen(wp_site, client):
    """Nếu SiteSEO đổi ``modified_gmt`` khi ghi (cần kiểm ở lần thử thật): hỏng theo hướng an
    toàn, không chuyển."""
    wp_site.abilities = wp_site.ability_bumps = True
    post_id = _prepare(client, wp_site)
    _refused(client, wp_site, post_id, "publish")


# ====================================================================== 5. lệnh ghi lỗi
def _when(key: str, answer):
    return lambda request: answer if key in json.loads(request.body or b"{}") else None


def _applied_then(key: str, wp_site: _ModSite, error: BaseException):
    """Lệnh ghi đã chạy xong trên website nhưng câu trả lời mất (hết giờ)."""

    def hook(request):
        if key not in json.loads(request.body or b"{}"):
            return None
        post = wp_site.posts[42]
        post.update(json.loads(request.body), modified=wp_site.stamp())
        raise error

    return hook


FEATURED_FAILURES = {
    "500": (500, {"code": "x", "message": MOI}),
    "503-rong": (503, b""),
    "400": (400, {"code": "rest_invalid_param", "message": MOI}),
    "403": (403, {"code": "rest_cannot_edit", "message": MOI}),
    "het-gio": requests.exceptions.ReadTimeout(MOI),
    "mat-mang": requests.exceptions.ConnectionError(MOI),
    "200-khong-json": (200, MOI.encode()),
    "loi-la": ValueError(MOI),
}


@pytest.mark.parametrize("answer", FEATURED_FAILURES.values(), ids=FEATURED_FAILURES)
def test_lenh_anh_dai_dien_loi_thi_khong_chuyen(wp_site, client, answer):
    """LC-T102-1 ở lớp client: đặt ảnh đại diện hỏng thì không đăng, kể cả khi website chưa
    đổi gì."""
    post_id = client.create_draft("Sửa cổng inox", "<p>Nội dung</p>").id
    wp_site.tick()
    wp_site.inject[("POST", f"{API}/posts/{post_id}")] = _when("featured_media", answer)
    with pytest.raises((WordPressError, ValueError)):
        client.set_featured_image(post_id, 7)
    wp_site.inject.clear()
    _refused(client, wp_site, post_id, "publish")


def test_lenh_anh_dai_dien_da_chay_nhung_mat_cau_tra_loi_thi_khong_chuyen(wp_site, client):
    post_id = client.create_draft("Sửa cổng inox", "<p>Nội dung</p>").id
    wp_site.tick()
    timeout = requests.exceptions.ReadTimeout(MOI)
    wp_site.inject[("POST", f"{API}/posts/{post_id}")] = _applied_then(
        "featured_media", wp_site, timeout
    )
    with pytest.raises(WordPressError):
        client.set_featured_image(post_id, 7)
    wp_site.inject.clear()
    assert wp_site.posts[post_id]["featured_media"] == 7
    _refused(client, wp_site, post_id, "publish")


META_FAILURES = {  # câu trả lời, có chặn lệnh chuyển không
    "500": ((500, {"code": "x", "message": MOI}), True),
    "502-html": ((502, MOI.encode()), True),
    "het-gio": (requests.exceptions.ReadTimeout(MOI), True),
    "200-khong-json": ((200, MOI.encode()), True),
    "400": ((400, {"code": "rest_invalid_param", "message": MOI}), False),
    "401": ((401, {"code": "rest_cannot_edit", "message": MOI}), False),
    "403": ((403, {"code": "rest_forbidden", "message": MOI}), False),
}


@pytest.mark.parametrize("answer, blocks", META_FAILURES.values(), ids=META_FAILURES)
def test_lenh_ghi_meta_loi(wp_site, client, answer, blocks):
    """Lỗi không rõ (5xx, hết giờ, trả lời hỏng): «không biết», không chuyển. Từ chối 4xx rõ
    ràng (site không cho ghi khóa meta): website không đổi gì, giữ giá trị nhớ, chuyển được."""
    post_id = client.create_draft("Sửa cổng inox", "<p>Nội dung</p>").id
    wp_site.tick()
    wp_site.inject[("POST", f"{API}/posts/{post_id}")] = _when("meta", answer)
    assert client.set_seo_meta(post_id, **SEO).written is False
    wp_site.inject.clear()
    wp_site.tick()
    if blocks:
        _refused(client, wp_site, post_id, "publish")
    else:
        assert _release(client, wp_site, post_id, "publish").status == "publish"


ODD_WRITE_ANSWERS = {  # câu trả lời lạ của lệnh ghi, vẫn mang đúng giờ sửa mới của bài 42
    "ma-chu": {"id": "42"},
    "ma-so-thuc": {"id": 42.0},
    "bai-khac": {"id": 43},
    "khong-con-nhap": {"status": "pending"},
    "thieu-trang-thai": {"status": None},
}


def _odd_write(wp_site: _ModSite, key: str, change: dict):
    """Lệnh ghi có khóa ``key`` chạy xong trên website (giờ sửa mới), câu trả lời lạ ``change``
    (``None``: bỏ khóa) nhưng mang đúng ``modified_gmt`` mới của bài."""

    def hook(request):
        sent = json.loads(request.body or b"{}")
        if key not in sent:
            return None
        post = wp_site.posts[42]
        post["meta"].update(sent.get("meta", {}))
        post["featured_media"] = sent.get("featured_media", post["featured_media"])
        post["modified"] = wp_site.stamp()
        answer = {**wp_site.view(42), **change}
        return 200, {k: v for k, v in answer.items() if v is not None}

    return hook


@pytest.mark.parametrize("change", ODD_WRITE_ANSWERS.values(), ids=ODD_WRITE_ANSWERS)
@pytest.mark.parametrize("key", ["featured_media", "meta"], ids=["anh-dai-dien", "meta"])
def test_sl_t115_1_lenh_ghi_tra_loi_la_thi_khong_biet_khong_chuyen(wp_site, client, key, change):
    post_id = client.create_draft("Sửa cổng inox", "<p>Nội dung</p>").id
    wp_site.tick()
    wp_site.inject[("POST", f"{API}/posts/{post_id}")] = _odd_write(wp_site, key, change)
    if key == "featured_media":
        with pytest.raises(WordPressError):  # app báo «chưa đặt được ảnh đại diện»
            client.set_featured_image(post_id, 7)
    else:
        assert client.set_seo_meta(post_id, **SEO).written is False  # app báo ghi SEO hỏng
    wp_site.inject.clear()
    wp_site.tick()
    _refused(client, wp_site, post_id, "publish")


def test_lenh_doc_truoc_khi_ghi_loi_thi_chua_ghi_gi_van_chuyen(wp_site, client):
    """Lệnh đọc bài trước lệnh ghi ảnh đại diện lỗi: lệnh ghi không gửi, website không đổi."""
    post_id = client.create_draft("Sửa cổng inox", "<p>Nội dung</p>").id
    wp_site.tick()
    wp_site.inject[("GET", f"{API}/posts/{post_id}")] = (500, {"code": "x", "message": MOI})
    with pytest.raises(WordPressError):
        client.set_featured_image(post_id, 7)
    wp_site.inject.clear()
    assert wp_site.posts[post_id]["featured_media"] == 0
    assert _release(client, wp_site, post_id, "publish").status == "publish"


# ====================================================================== 6. hai client, hai bài
def test_hai_client_moi_client_nho_rieng_bai_cua_minh(wp_site):
    a, b = _client(wp_site), _client(wp_site)
    first = a.create_draft("A", "<p>a</p>").id
    wp_site.tick()
    second = b.create_draft("B", "<p>b</p>").id
    wp_site.tick()
    wp_site.edit_outside(second)
    wp_site.tick()
    sent = len(wp_site.requests)
    with pytest.raises(ReleaseError) as other:
        b.release_draft(first, mode="publish")  # tab khác không chuyển được bài không phải của nó
    assert str(other.value) == wp._RELEASE_NOT_OWN and len(wp_site.requests) == sent
    assert a.release_draft(first, mode="publish").status == "publish"
    _refused(b, wp_site, second, "publish")


def test_tab_khac_khong_ghi_duoc_vao_bai_nen_khong_lam_hong_gia_tri_nho(wp_site):
    a, b = _client(wp_site, write_seo=True), _client(wp_site, write_seo=True)
    post_id = a.create_draft("A", "<p>a</p>").id
    wp_site.tick()
    sent = len(wp_site.requests)
    with pytest.raises(WordPressError):
        b.set_featured_image(post_id, 7)
    with pytest.raises(WordPressError):
        b.set_seo_meta(post_id, **SEO)
    assert len(wp_site.requests) == sent  # bị chặn trước khi gửi
    assert a.release_draft(post_id, mode="publish").status == "publish"


def test_mot_client_hai_bai_bai_bi_sua_khong_keo_bai_kia(wp_site, client):
    first = client.create_draft("A", "<p>a</p>").id
    wp_site.tick()
    second = client.create_draft("B", "<p>b</p>").id
    wp_site.tick()
    wp_site.edit_outside(second)
    wp_site.tick()
    _refused(client, wp_site, second, "publish")
    assert client.release_draft(first, mode="publish").status == "publish"


# ====================================================================== 7. trang Soạn bài
def test_trang_soan_bai_bai_bi_sua_ngay_truoc_lenh_chuyen_thi_khong_hen_gio(
    project_root, root, fake_ai, live
):
    """Công tắc bật trong test: tick xác nhận, gửi Hẹn giờ; ngay trước lệnh chuyển website báo
    giờ sửa khác (ai đó vừa lưu bài): không lệnh chuyển, câu cố định, nháp ghi «chưa hẹn giờ»."""

    def get_post(request):
        fields = parse_qs(urlsplit(request.url).query).get("_fields", [""])[0]
        modified = ui.MODIFIED if "meta" in fields else "2026-10-31T01:05:00"
        answer = {"id": ui.POST_ID, "status": "draft", "modified_gmt": modified}
        return (200, answer, {"Date": t102.http_date()})

    live.site.fake.on("GET", t102.POST, get_post)
    at, _pid = ui.ready_image(project_root)
    t102.to_mode(at, "Hẹn giờ")
    t102.confirm(at)
    ui.run_ok(t102.send_button(at).click().run())
    assert t102.release_bodies(live.site) == []
    shown = [x.value.replace("\\", "") for x in [*at.warning, *at.error]]
    assert any(wp._RELEASE_CHANGED in text for text in shown), shown
    saved = ui.store().load_send_state(at.session_state["draft_id"])
    assert (saved.released, saved.release_unknown, saved.post_id) == (False, False, ui.POST_ID)
