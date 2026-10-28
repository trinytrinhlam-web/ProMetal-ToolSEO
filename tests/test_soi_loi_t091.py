r"""Soi Lỗi T-091 (rút gọn): dọn client WordPress sau T-059.

Kiểm độc lập (website giả riêng ``_RawSite`` cho câu trả lời theo từng byte và bảng mã; bản Python
riêng của ``sanitize_text_field`` + ``wp_unslash`` dựng lại từ mã WordPress lõi; không dùng lại
hàm hay bảng kỳ vọng của Thợ Máy):

1. Ký tự surrogate lẻ ở mọi chữ client lấy từ website (tên site, địa chỉ site, tài khoản, vai
   trò, chuyên mục, thẻ, bài đã đăng, bài nháp vừa tạo, ảnh vừa tải, khóa JSON) được thay bằng
   «�»; cặp đúng (emoji) và chữ «\ud800» gõ thật giữ nguyên.
2. ``MAX_ID`` (2⁶³−1): biên nhận / biên chặn ở mã bài, mã ảnh, ảnh đại diện, chuyên mục gửi đi.
3. SL-T059-1: SiteSEO giả lưu đúng ``wp_unslash(sanitize_text_field(chữ))``: app báo đã ghi; báo
   «SiteSEO tự bỏ vài ký tự» đúng khi chữ trên site khác chữ đã gửi; câu trả lời khác cách SiteSEO
   lưu vẫn là chưa ghi.
4. ``unfiltered_html``: có / không / giá trị lạ; câu cảnh báo cố định.
5. Soát R5: ca cũ đổi ở ``tests/test_wordpress_t085.py`` bỏ mất phần kiểm «không chép lời máy chủ,
   địa chỉ site» (SL-T091-3): ca dưới đây kiểm lại phần đó.

Lỗi tìm ra (``xfail(strict=True)``; sửa xong thì gỡ dấu):

- **SL-T091-1** (Thấp): surrogate lẻ lọt ``_json`` khi website khai bảng mã khác UTF-8
  (``charset=utf-16``, ``utf-32``, ``utf-7``, ``cp500``): bộ lọc chỉ dò mã thoát ``\uD8..`` trên
  **byte** câu trả lời, còn ``response.json()`` giải mã theo ``charset``.
- **SL-T091-2** (Thấp): mã bài đã đăng lớn hơn ``MAX_ID`` lọt ``list_published`` (``PublishedItem``
  chỉ chặn ≤ 0) nên ``site_listing`` / ``SiteIndexStore.refresh`` ném ``OverflowError`` của SQLite
  (không phải ``SiteIndexError``): bước SEO của trang Soạn bài lỗi trang.
"""

from __future__ import annotations

import html
import io
import json
import random
import re
from urllib.parse import urlsplit

import pytest
import requests
import urllib3
from fake_wordpress import BASE_URL, FakeWordPress, make_session
from requests.adapters import BaseAdapter
from requests.structures import CaseInsensitiveDict

from seo_app.storage.site_index import SiteIndexStore, site_listing
from seo_app.wordpress import WordPressClient, WordPressError
from seo_app.wordpress.client import (
    _SEO_WRITTEN,
    _SEO_WRITTEN_CHANGED,
    MAX_ID,
    ConnectionInfo,
    _positive_id,
    _seo_text,
)

SUR = chr(0xD800)
LOW = chr(0xDC00)
FFFD = "\N{REPLACEMENT CHARACTER}"
SMILE = "\N{GRINNING FACE}"
BS = chr(92)
MAT_KHAU_GIA = "abcd efgh ijkl mnop"  # Application Password giả
API = "/wp-json"
ROOT = f"{API}/"
ME = f"{API}/wp/v2/users/me"
ABILITY = f"{API}/wp-abilities/v1/abilities/siteseo-posts/seo-data-update"
RUN = f"{ABILITY}/run"
POSTS = f"{API}/wp/v2/posts"
PAGES = f"{API}/wp/v2/pages"
MEDIA = f"{API}/wp/v2/media"
CATEGORIES = f"{API}/wp/v2/categories"
TAGS = f"{API}/wp/v2/tags"
UPLOADS = f"{BASE_URL}/wp-content/uploads/2026/10/"
JPEG = bytes.fromhex("ffd8ffe000104a46494600010100000100010000ffd9")


def has_surrogate(text: str) -> bool:
    return any(0xD800 <= ord(ch) <= 0xDFFF for ch in text)


def strings(value) -> list[str]:
    """Mọi chữ (và tên khóa) trong một giá trị lồng nhau, kể cả trường của dataclass."""
    out: list[str] = []
    stack = [value]
    while stack:
        item = stack.pop()
        if isinstance(item, str):
            out.append(item)
        elif isinstance(item, dict):
            stack.extend(item.keys())
            stack.extend(item.values())
        elif isinstance(item, list | tuple | set):
            stack.extend(item)
        elif hasattr(item, "__dataclass_fields__"):
            stack.extend(getattr(item, name) for name in item.__dataclass_fields__)
    return out


def assert_clean(value) -> None:
    for text in strings(value):
        assert not has_surrogate(text), repr(text)
        text.encode("utf-8")  # trang Streamlit, SQLite đều cần mã hóa được


# ---------------------------------------------------------------- website giả theo từng byte
class _RawSite(BaseAdapter):
    """Website giả của Soi Lỗi: trả đúng byte và header đã cho; ``encoding`` lấy từ header như
    ``requests`` thật (``get_encoding_from_headers``)."""

    def __init__(self, routes: dict) -> None:
        super().__init__()
        self.routes = routes
        self.requests: list[requests.PreparedRequest] = []

    def send(self, request, **kwargs):
        self.requests.append(request)
        path = urlsplit(request.url).path
        answer = self.routes.get((request.method, path), (404, b'{"code":"rest_no_route"}', {}))
        if callable(answer):
            answer = answer(request)
        status, body, headers = answer
        headers = {"Content-Type": "application/json; charset=UTF-8", **headers}
        raw = urllib3.HTTPResponse(
            body=io.BytesIO(body), status=status, headers=headers, preload_content=False
        )
        response = requests.Response()
        response.status_code = status
        response.raw = raw
        response.headers = CaseInsensitiveDict(headers)
        response.encoding = requests.utils.get_encoding_from_headers(response.headers)
        response.url = request.url
        response.request = request
        return response

    def close(self) -> None:
        pass


def raw_client(routes: dict, **kwargs) -> tuple[WordPressClient, _RawSite]:
    site = _RawSite(routes)
    session = requests.Session()
    session.mount("https://", site)
    session.mount("http://", site)
    return WordPressClient(BASE_URL, "lam", MAT_KHAU_GIA, session=session, **kwargs), site


def js(value) -> bytes:
    """JSON như PHP ``wp_json_encode``: ký tự ngoài ASCII thành mã thoát ``\\uXXXX`` (surrogate lẻ
    thành đúng một mã thoát lẻ)."""
    return json.dumps(value).encode("ascii")


def connection_routes(root: dict, me: dict) -> dict:
    return {
        ("GET", ROOT): (200, js(root), {}),
        ("GET", ME): (200, js(me), {}),
        ("GET", ABILITY): (404, js({"code": "rest_no_route"}), {}),
    }


def good_root(**changes) -> dict:
    return {"name": "Pro-Metal", "home": BASE_URL, "namespaces": ["wp/v2"], **changes}


def good_me(**changes) -> dict:
    return {"name": "Lâm", "roles": ["editor"],
            "capabilities": {"edit_posts": True, "unfiltered_html": True}, **changes}


# ================================================================ 1. surrogate lẻ
@pytest.mark.parametrize(
    "root, me",
    [
        (good_root(name="Site " + SUR), good_me()),
        (good_root(name=LOW + "Site"), good_me()),
        (good_root(name="Site" + chr(0xDFFF)), good_me()),
        (good_root(name="Đảo " + chr(0xDE00) + chr(0xD83D)), good_me()),  # cặp ngược
        (good_root(home=BASE_URL + "/" + SUR), good_me()),
        (good_root(), good_me(name="Lâm " + SUR)),
        (good_root(), good_me(roles=["editor" + SUR, "x"])),
    ],
    ids=["ten-site", "dau-chu", "cuoi-chu", "cap-nguoc", "dia-chi", "tai-khoan", "vai-tro"],
)
def test_kiem_tra_ket_noi_khong_lot_surrogate(root, me):
    client, _site = raw_client(connection_routes(root, me))
    info = client.check_connection()
    assert_clean(info)
    assert FFFD in " ".join(strings(info))  # thay, không bỏ


def test_surrogate_trong_ten_khoa_json_khong_lam_hong_ket_qua():
    me = good_me(capabilities={"unfiltered_html" + SUR: True, "edit" + LOW: True})
    client, _site = raw_client(connection_routes(good_root(), me))
    info = client.check_connection()
    assert_clean(info)
    assert info.can_unfiltered_html is False and info.can_edit_posts is False


def test_json_doc_ve_khong_con_surrogate_o_ten_khoa_moi_tang():
    """``_json`` (chỗ dùng chung của mọi chữ website): tên khóa ở mọi tầng cũng được thay."""
    data = {"a" + SUR: [{"b" + LOW: {"c" + SUR + LOW[::-1]: ["d" + SUR]}}], "ok": SMILE}
    response = requests.Response()
    response.status_code = 200
    response._content = js(data)
    response.encoding = "utf-8"
    parsed = WordPressClient._json(response)
    assert_clean(parsed)
    assert parsed["ok"] == SMILE and ("a" + FFFD) in parsed


def test_surrogate_thay_bang_ky_tu_thay_the_khong_bi_bo():
    client, _site = raw_client(connection_routes(good_root(name="Cổng" + SUR + "inox"), good_me()))
    assert client.check_connection().site_name == "Cổng" + FFFD + "inox"


def test_cap_dung_va_chu_go_that_giu_nguyen():
    literal = BS + "ud800"  # người dùng gõ đúng 6 ký tự này làm tên site
    client, _site = raw_client(connection_routes(good_root(name=f"{SMILE} {literal}"), good_me()))
    assert client.check_connection().site_name == f"{SMILE} {literal}"


def test_byte_utf8_hong_cua_surrogate_thanh_ky_tu_thay_the():
    """Byte CESU-8 của U+D800 (không phải UTF-8 hợp lệ): requests đọc thay bằng «�»."""
    body = b'{"name": "A' + bytes.fromhex("eda080") + b'B", "home": "https://example.com", ' \
        b'"namespaces": ["wp/v2"]}'
    routes = connection_routes(good_root(), good_me())
    routes[("GET", ROOT)] = (200, body, {})
    client, _site = raw_client(routes)
    assert_clean(client.check_connection())


def list_routes(path: str, items: list) -> dict:
    return {("GET", path): (200, js(items), {"X-WP-TotalPages": "1"})}


@pytest.mark.parametrize("path", [CATEGORIES, TAGS])
def test_chuyen_muc_the_khong_lot_surrogate(path):
    item = {"id": 5, "name": "Cửa " + SUR, "slug": "cua-" + SUR, "count": 1, "parent": 0}
    client, _site = raw_client(list_routes(path, [item]))
    terms = client.list_categories() if path == CATEGORIES else client.list_tags()
    assert len(terms) == 1
    assert_clean(terms)
    assert FFFD in terms[0].name


def test_bai_da_dang_khong_lot_surrogate_va_luu_tam_duoc(tmp_path):
    post = {"id": 7, "status": "publish", "link": f"{BASE_URL}/cong-inox/", "slug": "cong-inox",
            "title": {"rendered": "Cổng " + SUR}, "modified_gmt": "2026-10-01T00:00:00",
            "meta": {"_siteseo_titles_title": "T " + LOW, "_siteseo_titles_desc": SUR}}
    routes = {**list_routes(POSTS, [post]), **list_routes(PAGES, [])}
    client, _site = raw_client(routes)
    items = client.list_published()
    assert_clean(list(items))
    listing = site_listing(SiteIndexStore(tmp_path / "site_index.sqlite"), client, refresh=True)
    assert listing.index is not None and listing.notice == ""
    assert_clean(list(listing.index.items))


def test_bai_nhap_vua_tao_khong_lot_surrogate():
    answer = {"id": 42, "status": "draft", "title": {"raw": "Cổng " + SUR},
              "link": f"{BASE_URL}/?p=42" + LOW}
    client, _site = raw_client({("POST", POSTS): (201, js(answer), {})})
    post = client.create_draft("Cổng inox", "<p>Nội dung</p>")
    assert_clean(post)
    assert post.title == "Cổng " + FFFD


def test_anh_vua_tai_khong_lot_surrogate_va_khong_ghep_thanh_file_khac():
    created = {"id": 9, "source_url": f"{UPLOADS}a{SUR}.webp"}
    described = {"id": 9, "source_url": f"{UPLOADS}a{SUR}.webp", "alt_text": "Cổng " + SUR}
    client, _site = raw_client({
        ("POST", MEDIA): (201, js(created), {}),
        ("POST", f"{MEDIA}/9"): (200, js(described), {}),
    })
    media = client.upload_media(JPEG, "cong.jpg", alt_text="Cổng")
    assert_clean(media)
    assert media.source_url == f"{UPLOADS}a{FFFD}.webp"  # không thành «a.webp» của ảnh khác


def test_loi_wordpress_co_surrogate_van_la_cau_co_dinh():
    error = {"code": "rest_cannot" + SUR, "message": "Lỗi " + SUR, "data": {"status": 403}}
    client, _site = raw_client({("GET", ROOT): (403, js(error), {})})
    with pytest.raises(WordPressError) as caught:
        client.check_connection()
    assert not has_surrogate(str(caught.value)) and not has_surrogate(caught.value.code)


_SL1 = pytest.mark.xfail(
    strict=True,
    reason="SL-T091-1: _json chỉ đi qua dữ liệu khi BYTE câu trả lời có mã thoát \\uD8..; "
    "response.json() giải mã theo charset của website (utf-16, utf-32, utf-7, cp500 không có "
    "byte đó) nên surrogate lẻ lọt ra như trước T-091",
)


@_SL1
@pytest.mark.parametrize("charset", ["utf-16", "utf-16-le", "utf-32", "utf-7", "cp500"])
def test_sl_t091_1_bang_ma_khac_utf8_van_khong_lot_surrogate(charset):
    text = json.dumps(good_root(name="Site " + SUR))  # chữ ASCII có mã thoát lẻ
    routes = connection_routes(good_root(), good_me())
    routes[("GET", ROOT)] = (
        200, text.encode(charset), {"Content-Type": f"application/json; charset={charset}"}
    )
    client, _site = raw_client(routes)
    assert_clean(client.check_connection())


def test_bang_ma_khac_utf8_khong_co_surrogate_van_doc_dung():
    """Đối chứng cho SL-T091-1: cùng câu trả lời utf-16 nhưng chữ thường thì đọc đúng."""
    text = json.dumps(good_root(name="Cửa sắt " + SMILE))
    routes = connection_routes(good_root(), good_me())
    routes[("GET", ROOT)] = (
        200, text.encode("utf-16"), {"Content-Type": "application/json; charset=utf-16"}
    )
    client, _site = raw_client(routes)
    assert client.check_connection().site_name == "Cửa sắt " + SMILE


# ================================================================ 2. MAX_ID
@pytest.mark.parametrize(
    "value, expected",
    [(1, 1), (MAX_ID, MAX_ID), (MAX_ID + 1, None), (2**64, None), (10**30, None), (0, None),
     (-1, None), (True, None), (1.0, None), ("5", None), (None, None)],
)
def test_positive_id_bien(value, expected):
    assert _positive_id(value) == expected


def wp_fake() -> tuple[WordPressClient, FakeWordPress]:
    fake = FakeWordPress()
    session = make_session(fake)
    client = WordPressClient(BASE_URL, "lam", MAT_KHAU_GIA, session=session, write_seo=True)
    return client, fake


def paths(fake) -> list[tuple[str, str]]:
    return [(r.method, urlsplit(r.url).path) for r in fake.requests]


def test_ma_bai_bang_bien_duoc_nhan_va_dat_anh_dai_dien_duoc():
    client, fake = wp_fake()
    fake.on("POST", POSTS, (201, {"id": MAX_ID, "status": "draft", "title": {"raw": "T"}}, {}))
    post = client.create_draft("Cổng", "<p>x</p>")
    assert post.id == MAX_ID
    fake.on("GET", f"{POSTS}/{MAX_ID}", {"id": MAX_ID, "status": "draft"})
    fake.on("POST", f"{POSTS}/{MAX_ID}",
            {"id": MAX_ID, "status": "draft", "featured_media": MAX_ID})
    client.set_featured_image(MAX_ID, MAX_ID)
    assert ("POST", f"{POSTS}/{MAX_ID}") in paths(fake)


@pytest.mark.parametrize("post_id", [MAX_ID + 1, 2**64, 10**25])
def test_ma_bai_qua_bien_la_sai_khuon_khong_goi_tiep(post_id):
    client, fake = wp_fake()
    fake.on("POST", POSTS, (201, {"id": post_id, "status": "draft", "title": {"raw": "T"}}, {}))
    with pytest.raises(WordPressError) as caught:
        client.create_draft("Cổng", "<p>x</p>")
    assert str(post_id) not in str(caught.value)
    assert paths(fake) == [("POST", POSTS)]
    with pytest.raises(WordPressError):
        client.set_seo_meta(post_id, title="Cổng inox")  # không phải bài app đã ghi nhận
    assert paths(fake) == [("POST", POSTS)]


@pytest.mark.parametrize("media_id", [MAX_ID + 1, 2**64])
def test_anh_dai_dien_ma_qua_bien_bi_chan_truoc_khi_gui(media_id):
    client, fake = wp_fake()
    fake.on("POST", POSTS, (201, {"id": 42, "status": "draft", "title": {"raw": "T"}}, {}))
    client.create_draft("Cổng", "<p>x</p>")
    before = len(fake.requests)
    with pytest.raises(WordPressError):
        client.set_featured_image(42, media_id)
    assert len(fake.requests) == before


@pytest.mark.parametrize(
    "categories, sent",
    [([MAX_ID], True), ([MAX_ID + 1], False), ([5, 2**64], False), ([0], False)],
)
def test_chuyen_muc_gui_di_theo_bien(categories, sent):
    """Đường «Gửi nháp» của trang Soạn bài (``create_draft_with_images``, ``_is_term_ids``).
    ``create_draft`` gọi thẳng (trang Kết nối WordPress) không kiểm mã chuyên mục: Ghi nhận."""
    client, fake = wp_fake()
    fake.on("POST", POSTS, (201, {"id": 42, "status": "draft", "title": {"raw": "T"}}, {}))
    if sent:
        client.create_draft_with_images("Cổng", ["<p>x</p>"], categories=categories)
        assert json.loads(fake.requests[0].body)["categories"] == categories
    else:
        with pytest.raises(WordPressError):
            client.create_draft_with_images("Cổng", ["<p>x</p>"], categories=categories)
        assert fake.requests == []


@pytest.mark.parametrize("media_id", [MAX_ID + 1, 10**20])
def test_anh_ma_qua_bien_chi_mot_lenh_va_cau_bao_khong_chep_gi(media_id):
    """SL-T091-3 (soát R5): ``test_wordpress_t085.py`` đổi ca này và bỏ mất phần kiểm «không chép
    lời máy chủ, địa chỉ site» của ``assert_says_in_media_library``; kiểm lại ở đây."""
    client, fake = wp_fake()
    server_text = "Gọi 0909 123 456 https://evil.example/x <b>quản trị</b>"
    fake.on("POST", MEDIA, (201, {"id": media_id, "source_url": f"{UPLOADS}anh-khac.jpg",
                                  "title": {"raw": server_text}}, {}))
    with pytest.raises(WordPressError) as caught:
        client.upload_media(JPEG, "cong.jpg", alt_text="Cổng")
    message = str(caught.value)
    assert paths(fake) == [("POST", MEDIA)]
    assert "có thể đã lên thư viện Media" in message and "Media → Thư viện" in message
    for piece in (str(media_id), "0909", "evil", "quản trị</b>", "example.com", "anh-khac"):
        assert piece not in message, piece


def test_anh_ma_bang_bien_ghi_de_dung_anh():
    client, fake = wp_fake()
    fake.on("POST", MEDIA, (201, {"id": MAX_ID, "source_url": f"{UPLOADS}cong.jpg"}, {}))
    fake.on("POST", f"{MEDIA}/{MAX_ID}",
            {"id": MAX_ID, "source_url": f"{UPLOADS}cong.jpg", "alt_text": "Cổng"})
    media = client.upload_media(JPEG, "cong.jpg", alt_text="Cổng")
    assert media.id == MAX_ID
    assert paths(fake) == [("POST", MEDIA), ("POST", f"{MEDIA}/{MAX_ID}")]


def published(post_id: int) -> dict:
    return {"id": post_id, "status": "publish", "link": f"{BASE_URL}/bai-{post_id % 97}/",
            "slug": f"bai-{post_id % 97}", "title": {"rendered": "Bài"},
            "modified_gmt": "2026-10-01T00:00:00"}


def test_bai_da_dang_ma_bang_bien_luu_tam_duoc(tmp_path):
    routes = {**list_routes(POSTS, [published(MAX_ID)]), **list_routes(PAGES, [])}
    client, _site = raw_client(routes)
    listing = site_listing(SiteIndexStore(tmp_path / "s.sqlite"), client, refresh=True)
    assert listing.index is not None
    assert [item.id for item in listing.index.items] == [MAX_ID]


@pytest.mark.xfail(
    strict=True,
    reason="SL-T091-2: _published_from/PublishedItem chỉ chặn mã ≤ 0, không có MAX_ID; "
    "SiteIndexStore.save ném OverflowError (SQLite INTEGER) mà site_listing chỉ bắt "
    "WordPressError, SiteIndexError",
)
@pytest.mark.parametrize("post_id", [MAX_ID + 1, 2**64, 10**30])
def test_sl_t091_2_bai_da_dang_ma_qua_bien_bi_bo_khong_vo_luu_tam(tmp_path, post_id):
    routes = {**list_routes(POSTS, [published(post_id), published(8)]), **list_routes(PAGES, [])}
    client, _site = raw_client(routes)
    listing = site_listing(SiteIndexStore(tmp_path / "s.sqlite"), client, refresh=True)
    assert listing.index is not None
    assert [item.id for item in listing.index.items] == [8]


# ================================================================ 3. SL-T059-1: bản lưu SiteSEO
_ESC_HTML = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"}


def php_trim(text: str) -> str:
    return text.strip(" \t\n\r\0\x0b")


def php_strip_tags(text: str) -> str:
    """``strip_tags`` của PHP, phần cần cho chữ một dòng: «<» theo sau là khoảng trắng là chữ
    thường; «<» khác mở thẻ tới «>» (hay hết chữ) và bị bỏ."""
    out, in_tag = [], False
    for index, char in enumerate(text):
        if in_tag:
            in_tag = char != ">"
        elif char == "<" and not text[index + 1 : index + 2].isspace():
            in_tag = True
        else:
            out.append(char)
    return "".join(out)


def wp_sanitize_text_field(text: str) -> str:
    """``_sanitize_text_fields($str, false)`` của WordPress (``formatting.php``)."""
    filtered = text
    if "<" in filtered:
        # wp_pre_kses_less_than: đoạn «<…» không có «>» thì esc_html (ENT_QUOTES, «'» → &#039;).
        filtered = re.sub(
            r"<[^>]*?((?=<)|>|$)",
            lambda m: m.group(0) if ">" in m.group(0)
            else "".join(_ESC_HTML.get(ch, ch) for ch in m.group(0)),
            filtered,
        )
        filtered = re.sub(r"<(script|style)[^>]*?>.*?</\1>", "", filtered, flags=re.S | re.I)
        filtered = php_trim(php_strip_tags(filtered))  # wp_strip_all_tags
        filtered = filtered.replace("<\n", "&lt;\n")
    filtered = php_trim(re.sub(r"[\r\n\t ]+", " ", filtered))
    found = False
    while match := re.search(r"%[a-f0-9]{2}", filtered, re.I):
        filtered, found = filtered.replace(match.group(0), ""), True
    if found:
        filtered = php_trim(re.sub(" +", " ", filtered))
    return filtered


def wp_unslash(text: str) -> str:
    out, chars = [], iter(text)
    for char in chars:
        if char == BS:
            nxt = next(chars, None)
            if nxt is not None:
                out.append(chr(0) if nxt == "0" else nxt)
        else:
            out.append(char)
    return "".join(out)


def siteseo_stored(text: str) -> str:
    """SiteSEO 1.4.2: ``update_post_meta(…, sanitize_text_field($v))``; ``update_metadata`` còn
    ``wp_unslash``."""
    return wp_unslash(wp_sanitize_text_field(text))


SEO_KEYS = {"title": "title", "description": "description", "focus_keyword": "focus_keyphrase"}


def siteseo_site(store=siteseo_stored):
    """Bài nháp 42 do client tạo; SiteSEO giả lưu theo ``store`` và trả ``post`` đọc lại."""
    client, fake = wp_fake()
    fake.on("POST", POSTS, (201, {"id": 42, "status": "draft", "title": {"raw": "T"}}, {}))
    fake.on("GET", f"{POSTS}/42", {"id": 42, "status": "draft", "meta": {}})
    fake.on("GET", ABILITY, {"name": "siteseo-posts/seo-data-update"})

    def run(request):
        sent = json.loads(request.body)["input"]
        post = {key: "" for key in ("title", "description", "focus_keyphrase")}
        post.update({key: store(sent[key]) for key in post if key in sent})
        post.update(canonical_url=None, seo_score=None)
        return {"updated": True, "post": post}

    fake.on("POST", RUN, run)
    client.create_draft("Cổng inox", "<p>Nội dung</p>")
    return client, fake


CURATED = [
    "Giá < 5 triệu | Pro-Metal",
    "Cửa < 2m và cổng > 3m",
    "5 > 3 < 4 tầng",
    "Giảm 50%BE tiền công",
    "Giảm 50% tiền công",
    "Đường dẫn C:" + BS + "cua-sat",
    "Nhà < 3 tầng 'giá rẻ' \"chuẩn\"",
    "A < B & C < D",
    "R&D cửa sắt < 10%AB",
    BS + "0 lỗi",
    "Cửa sắt " + BS + "< 5 triệu",
    "Thợ < 2 giờ có mặt " + BS,
    "So sánh inox 201 < 304 < 430",
    "%41%42 cửa",
    "Giảm 100%4 tiền công",
    "Giá < 5 triệu, cổng < 3m > 2m",
]


@pytest.mark.parametrize("text", CURATED)
def test_siteseo_luu_kieu_nao_app_cung_bao_dung(text):
    try:
        sent = _seo_text("Tiêu đề SEO", text, 90)
    except WordPressError:
        pytest.skip("chữ bị app chặn trước khi gửi")
    client, _fake = siteseo_site()
    result = client.set_seo_meta(42, title=text)
    stored = siteseo_stored(sent)
    uncertain = any(run.endswith(">") for run in re.findall(r"<[^>]*?(?:(?=<)|>|$)", sent))
    if stored == sent or not uncertain:
        assert result.written, (sent, stored, result.message)
        expected = _SEO_WRITTEN if html.unescape(stored) == sent else _SEO_WRITTEN_CHANGED
        assert result.message == expected
    else:  # có đoạn «< … >» mà SiteSEO đổi chữ: app không đoán, báo chưa ghi (hướng an toàn)
        assert not result.written


def test_siteseo_luu_nhieu_chu_ngau_nhien():
    """300 chữ ngẫu nhiên (hạt giống cố định) từ bảng ký tự dễ bị SiteSEO đổi: mọi chữ app cho
    gửi, SiteSEO lưu đúng cách của nó, thì app báo đã ghi (trừ ca «< … >» không đoán), câu báo
    «tự bỏ ký tự» đúng khi và chỉ khi chữ trên site khác chữ đã gửi."""
    alphabet = ["<", " ", "%", "B", "E", "4", "1", BS, "'", '"', "&", "R", "D", ">", "a", "ơ",
                "0", "f", "C"]
    rng = random.Random(91)
    checked = uncertain_count = 0
    client, _fake = siteseo_site()
    for _ in range(300):
        text = "Cửa " + "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 14)))
        try:
            sent = _seo_text("Tiêu đề SEO", text, 90)
        except WordPressError:
            continue
        stored = siteseo_stored(sent)
        if not stored:
            continue  # SiteSEO lưu rỗng: app không gửi lại chữ rỗng
        result = client.set_seo_meta(42, title=text)
        runs = re.findall(r"<[^>]*?(?:(?=<)|>|$)", sent)
        if stored != sent and any(run.endswith(">") for run in runs):
            assert not result.written, (sent, stored)
            uncertain_count += 1
            continue
        assert result.written, (sent, stored, result.message)
        changed = html.unescape(stored) != sent
        assert result.message == (_SEO_WRITTEN_CHANGED if changed else _SEO_WRITTEN), (sent, stored)
        checked += 1
    assert checked >= 100


@pytest.mark.parametrize(
    "text, server",
    [
        ("Giá < 5 triệu", "Giá &amp;lt; 5 triệu"),
        ("Giá < 5 triệu", "Giá &#60; 5 triệu"),
        ("Giá < 5 triệu", "Giá 5 triệu"),
        ("Giá < 5 triệu", "Giá &lt; 5 triệu "),
        ("Giá < 5 triệu", "Giá &lt; 5 triệu (đã sửa)"),
        ("Giảm 50%BE", "Giảm 5"),
        ("Giảm 50%BE", "Giảm 50%"),
        ("A" + BS + "B", "A/B"),
        ("R&D < 10", "R&amp;D &lt; 10"),
        ("Nhà < 3 'rẻ'", "Nhà &lt; 3 &#x27;rẻ&#x27;"),
        ("Cửa sắt", "Cửa sắt "),
        ("Cửa sắt", ""),
        ("Cửa < 2m và cổng > 3m", "Cửa &lt; 2m và cổng &gt; 3m"),
    ],
)
def test_tra_loi_khac_cach_siteseo_luu_van_la_chua_ghi(text, server):
    client, _fake = siteseo_site(store=lambda _sent: server)
    assert not client.set_seo_meta(42, title=text).written


@pytest.mark.parametrize("field", ["description", "focus_keyword"])
def test_mo_ta_tu_khoa_cung_theo_ban_luu(field):
    client, _fake = siteseo_site()
    result = client.set_seo_meta(42, **{field: "Giá < 5 triệu, giảm 10%BE"})
    assert result.written and result.message == _SEO_WRITTEN_CHANGED


@pytest.mark.parametrize("title, written", [("Cửa sắt tại nhà", True), ("Giá < 5 triệu", False)])
def test_duong_du_phong_meta_van_so_tung_chu(title, written):
    """Phạm vi: chỉ đường Abilities so theo bản lưu SiteSEO; đường meta dự phòng (site chưa bật
    Abilities) giữ so khớp từng chữ như trước (ca đối chứng: chữ không đổi thì ghi được)."""
    client, fake = wp_fake()
    fake.on("POST", POSTS, (201, {"id": 42, "status": "draft", "title": {"raw": "T"}}, {}))
    keys = {"_siteseo_titles_title": "", "_siteseo_titles_desc": ""}
    fake.on("GET", f"{POSTS}/42", {"id": 42, "status": "draft", "meta": keys})
    fake.on("GET", ABILITY, (404, {"code": "rest_no_route"}, {}))

    def meta_answer(request):
        meta = json.loads(request.body)["meta"]
        stored = {**keys, **{key: siteseo_stored(value) for key, value in meta.items()}}
        return {"id": 42, "status": "draft", "meta": stored}

    fake.on("POST", f"{POSTS}/42", meta_answer)
    client.create_draft("Cổng inox", "<p>x</p>")
    result = client.set_seo_meta(42, title=title)
    assert result.written is written
    assert ("POST", f"{POSTS}/42") in paths(fake)  # đường meta thật sự chạy


# ================================================================ 4. unfiltered_html
@pytest.mark.parametrize(
    "capabilities, expected",
    [
        ({"unfiltered_html": True, "edit_posts": True}, True),
        ({"unfiltered_html": False, "edit_posts": True}, False),
        ({"edit_posts": True}, False),
        ({"unfiltered_html": 1}, False),
        ({"unfiltered_html": "true"}, False),
        ({"unfiltered_html": [True]}, False),
        ({"unfiltered_html": None}, False),
        (["unfiltered_html"], False),
        (None, False),
        ("unfiltered_html", False),
    ],
    ids=["co", "false", "thieu", "so-1", "chu-true", "danh-sach", "null", "caps-la-danh-sach",
         "caps-null", "caps-la-chu"],
)
def test_quyen_unfiltered_html(capabilities, expected):
    me = good_me(capabilities=capabilities, name="Lâm MOI-T091")
    client, site = raw_client(connection_routes(good_root(name="Site MOI-T091"), me))
    info = client.check_connection()
    assert info.can_unfiltered_html is expected
    if expected:
        assert info.unfiltered_html_status == ""
    else:
        status = info.unfiltered_html_status
        assert "unfiltered_html" in status and "MOI-T091" not in status
    assert {r.method for r in site.requests} == {"GET"}  # vẫn chỉ đọc


def test_quyen_unfiltered_html_khong_doi_cac_quyen_khac():
    caps = {"unfiltered_html": True, "edit_posts": False, "publish_posts": True,
            "upload_files": False}
    client, _site = raw_client(connection_routes(good_root(), good_me(capabilities=caps)))
    info = client.check_connection()
    assert (info.can_edit_posts, info.can_publish_posts, info.can_upload_files) == (
        False, True, False)


def test_connection_info_tao_kieu_cu_van_duoc():
    info = ConnectionInfo("Site", BASE_URL, "Lâm", ("editor",), True, True, True)
    assert info.can_unfiltered_html is False and info.siteseo_writable is None
    assert info.unfiltered_html_status  # mặc định là chưa biết có quyền: có câu nhắc
