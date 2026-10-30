"""Client WordPress REST API, xác thực bằng Application Password.

Chỉ làm những việc an toàn: đọc thông tin, tạo bài NHÁP, tải ảnh, đặt ảnh đại diện cho bài
nháp vừa tạo. Chỉ nói chuyện qua https.
Đúng một hàm, ``release_draft`` (T-099), chuyển bài nháp chính client này vừa tạo sang hẹn giờ
(``future``) hay đăng (``publish``); không hàm nào khác gửi được trạng thái khác ``draft``. Mật khẩu
không bao giờ xuất hiện trong thông báo lỗi.
"""

from __future__ import annotations

import html
import html.entities
import re
import unicodedata
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from itertools import islice
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

import requests

from seo_app.config import DEFAULT_TIMEZONE, Settings
from seo_app.sanitize import escape_shortcodes, sanitize_html, strip_tags
from seo_app.text import slugify

if TYPE_CHECKING:
    from seo_app.images.process import WebImage
    from seo_app.images.tags import ImageTags

DEFAULT_TIMEOUT = 30
PER_PAGE = 100
MAX_PAGES = 50  # chặn vòng lặp vô hạn nếu máy chủ trả số trang sai

# Giới hạn độ dài cho dữ liệu đọc từ site (chưa tin cậy) trong ``list_published`` (T-037).
MAX_TITLE_CHARS = 300
MAX_META_CHARS = 500
MAX_SLUG_CHARS = 200
MAX_LINK_CHARS = 2000
PUBLISHED_TYPES = ("post", "page")
# Khóa meta SiteSEO site đã mở trong REST (T-033 mục 1.3).
SITESEO_TITLE_KEY = "_siteseo_titles_title"
SITESEO_DESC_KEY = "_siteseo_titles_desc"
_PUBLISHED_FIELDS = "id,type,status,slug,link,title,modified_gmt,meta"
# ``_fields`` cố định cho lệnh ghi (T-061, Lá Chắn T-054): câu trả lời chỉ có trường app đọc.
# Không hỏi ``content``, ``excerpt`` (bài) hay ``description``, ``caption`` (ảnh): WordPress dựng
# các trường đó bằng ``the_content``/``the_excerpt``, tức chạy shortcode ngay trong lệnh của app
# (``description`` của ảnh còn chèn ``<img alt="…">`` qua ``prepend_attachment``).
_POST_FIELDS = "id,status,title,link,featured_media"
_POST_META_FIELDS = "id,status,meta"
_MEDIA_FIELDS = "id,source_url,alt_text"
_MODIFIED_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
_SLUG_PATTERN = re.compile(r"[A-Za-z0-9%._~-]+")
_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f-\x9f]")
_LINK_UNSAFE = frozenset("\"'<>`")  # không được có trần trong link lấy từ site
_TOTAL_PAGES_PATTERN = re.compile(r"[0-9]+")
_PAGE_OUT_OF_RANGE = "rest_post_invalid_page_number"  # WordPress: xin trang quá số trang
_ERROR_CODE = re.compile(r"[A-Za-z0-9_-]{1,100}")  # ``code`` lỗi WordPress (rest_no_route…)

# ---------------------------------------------------------------- đường REST được phép gọi
# Danh sách CỐ ĐỊNH (T-042, điều kiện Lá Chắn T-037): ``_request`` so khớp toàn chuỗi cặp
# (phương thức, đường) với danh sách này và từ chối mọi đường khác TRƯỚC KHI gửi. Site có những
# đường nhạy cảm (``/code-snippets/v1`` chạy mã PHP, ``/prometal/v1/deploy-files``,
# ``/prometal/v1/purge``): không bao giờ được gọi. Muốn thêm đường phải sửa ở đây và qua Lá Chắn.
_ID = r"[1-9][0-9]{0,18}"  # mã bài/ảnh: số nguyên dương, chỉ chữ số ASCII
MAX_ID = 2**63 - 1  # mã bài/ảnh website trả lớn hơn là dữ liệu hỏng (``_positive_id``, T-091)
# Ability ghi SEO của SiteSEO (T-033 mục 1.4), mở qua Abilities API của WordPress 6.9.
SITESEO_ABILITY = "siteseo-posts/seo-data-update"
SITESEO_ABILITY_PATH = f"/wp-abilities/v1/abilities/{SITESEO_ABILITY}"
SITESEO_ABILITY_RUN_PATH = f"{SITESEO_ABILITY_PATH}/run"
ALLOWED_ROUTES: tuple[tuple[str, str], ...] = (
    ("GET", r"/"),  # kiểm tra REST API (check_connection)
    ("GET", r"/wp/v2/users/me"),  # quyền của tài khoản
    ("GET", r"/wp/v2/categories"),
    ("GET", r"/wp/v2/tags"),
    ("GET", r"/wp/v2/posts"),  # danh sách bài đã đăng (list_published)
    ("GET", r"/wp/v2/pages"),
    ("GET", rf"/wp/v2/posts/{_ID}"),  # kiểm bài còn là nháp trước khi ghi SEO
    ("POST", r"/wp/v2/posts"),  # tạo nháp (create_draft)
    # ảnh đại diện, meta SEO dự phòng, hẹn giờ/đăng (``release_draft``): chỉ bài app vừa tạo
    ("POST", rf"/wp/v2/posts/{_ID}"),
    ("POST", r"/wp/v2/media"),
    ("POST", rf"/wp/v2/media/{_ID}"),
    ("GET", re.escape(SITESEO_ABILITY_PATH)),  # dò Abilities của SiteSEO đã bật chưa
    ("POST", re.escape(SITESEO_ABILITY_RUN_PATH)),  # ghi SEO (chỉ bài app tạo)
)
_ALLOWED_ROUTES = tuple((method, re.compile(pattern)) for method, pattern in ALLOWED_ROUTES)
# Chặn thêm (phòng khi ai đó nới biểu thức ở trên): đi ngược thư mục, mã hóa "%", "//", "\",
# và các namespace nhạy cảm của site. So trên chữ thường.
_FORBIDDEN_IN_PATH = ("..", "%", "//", "\\", "code-snippets", "prometal")

# Tham số ``params`` được phép theo từng đường (LC-T042-1), khóa là đúng cặp trong
# ``ALLOWED_ROUTES``: khóa khác bị từ chối TRƯỚC KHI gửi. WordPress đọc ``?rest_route=`` (đổi
# đường), ``?_method=`` hay header ``X-HTTP-Method-Override`` (đổi phương thức), ``_envelope``,
# ``_jsonp`` ở MỌI đường, kể cả ``/wp/v2/posts``. Thêm đường mới phải thêm ở đây (thiếu thì lỗi
# ngay khi nạp module).
_LIST_PARAMS = frozenset({"per_page", "page", "orderby", "order", "_fields"})
ALLOWED_PARAMS: dict[tuple[str, str], frozenset[str]] = {
    ("GET", r"/"): frozenset(),
    ("GET", r"/wp/v2/users/me"): frozenset({"context"}),
    ("GET", r"/wp/v2/categories"): _LIST_PARAMS | {"hide_empty"},
    ("GET", r"/wp/v2/tags"): _LIST_PARAMS | {"hide_empty"},
    # ``include``, ``context``: chỉ cho ``post_statuses`` (T-099), giá trị kiểm ở ``_PARAM_VALUES``
    ("GET", r"/wp/v2/posts"): _LIST_PARAMS | {"status", "include", "context"},
    ("GET", r"/wp/v2/pages"): _LIST_PARAMS | {"status"},
    ("GET", rf"/wp/v2/posts/{_ID}"): frozenset({"context", "_fields"}),
    ("POST", r"/wp/v2/posts"): frozenset({"_fields"}),
    ("POST", rf"/wp/v2/posts/{_ID}"): frozenset({"_fields"}),
    ("POST", r"/wp/v2/media"): frozenset({"_fields"}),
    ("POST", rf"/wp/v2/media/{_ID}"): frozenset({"_fields"}),
    ("GET", re.escape(SITESEO_ABILITY_PATH)): frozenset(),
    ("POST", re.escape(SITESEO_ABILITY_RUN_PATH)): frozenset(),
}
_ROUTE_PARAMS = tuple(
    (method, re.compile(pattern), ALLOWED_PARAMS[(method, pattern)])
    for method, pattern in ALLOWED_ROUTES
)
# Chặn thêm (phòng khi ai đó nới danh sách trên): tên tham số chứa các chữ này (so trên chữ
# thường, mọi ký tự không phải chữ, số thành "_", vì PHP đổi "." và dấu cách trong tên thành "_").
_FORBIDDEN_PARAMS = ("rest_route", "_method", "_envelope", "_jsonp")
# ``_fields`` (LC-T060-2) không được hỏi trường WordPress dựng bằng ``the_content``/``the_excerpt``
# (``content``, ``excerpt`` của bài; ``description``, ``caption`` của ảnh: chạy shortcode ngay
# trong lệnh của app, Lá Chắn T-054, T-061) hay phần nhúng thêm (``_embedded``, ``_links``).
_RENDERED_FIELDS = frozenset(
    {"content", "excerpt", "description", "caption", "_embedded", "_links"}
)
# Ký tự ``trim()`` của PHP cắt ở hai đầu (mặc định " \t\n\r\0\x0B", có NUL): WordPress cắt từng
# tên trường của ``_fields`` như vậy trước khi so (SL-T085-1).
_PHP_TRIM = " \t\n\r\0\x0b"

# Khóa thân JSON cấp trên cùng được phép theo từng đường (LC-T060-1), cùng kiểu
# ``ALLOWED_PARAMS`` (thiếu đường thì lỗi ngay khi nạp module). WordPress đọc tham số theo thứ
# tự JSON → form → truy vấn → đường (``WP_REST_Request::get_parameter_order``): ``id`` (bài,
# ảnh) hay ``name`` (Abilities ``/run``) trong thân JSON thắng giá trị trên đường, nên lệnh đi
# đúng đường đã duyệt mà sửa bài, ảnh khác hay chạy ability khác. Cũng vì thứ tự đó, đừng thêm
# ``_fields``, ``context`` vào đây: giá trị trong thân JSON sẽ vòng qua bước kiểm ở ``params``.
ALLOWED_JSON_KEYS: dict[tuple[str, str], frozenset[str]] = {
    ("GET", r"/"): frozenset(),
    ("GET", r"/wp/v2/users/me"): frozenset(),
    ("GET", r"/wp/v2/categories"): frozenset(),
    ("GET", r"/wp/v2/tags"): frozenset(),
    ("GET", r"/wp/v2/posts"): frozenset(),
    ("GET", r"/wp/v2/pages"): frozenset(),
    ("GET", rf"/wp/v2/posts/{_ID}"): frozenset(),
    ("POST", r"/wp/v2/posts"): frozenset(  # create_draft
        {"status", "title", "content", "excerpt", "slug", "categories", "tags", "featured_media"}
    ),
    ("POST", rf"/wp/v2/posts/{_ID}"): frozenset({"featured_media", "meta"}),
    ("POST", r"/wp/v2/media"): frozenset(),  # thân là byte ảnh (``data``)
    ("POST", rf"/wp/v2/media/{_ID}"): frozenset({"alt_text", "title", "caption"}),
    ("GET", re.escape(SITESEO_ABILITY_PATH)): frozenset(),
    ("POST", re.escape(SITESEO_ABILITY_RUN_PATH)): frozenset({"input"}),
}
_ROUTE_JSON_KEYS = tuple(
    (method, re.compile(pattern), ALLOWED_JSON_KEYS[(method, pattern)])
    for method, pattern in ALLOWED_ROUTES
)
# Không bao giờ nhận (phòng khi ai đó nới danh sách trên), so trên chữ thường. ``date`` là giờ
# theo múi giờ của site: không lệnh nào gửi (thiết kế T-094 mục 3.1: chỉ ``date_gmt``). ``status``
# có mặt thì chỉ được là ``"draft"``; ``date_gmt`` không được có. Riêng lệnh mang dấu ``_RELEASE``
# của ``release_draft`` (T-099) theo khuôn riêng ``_is_release_request``.
_FORBIDDEN_JSON_KEYS = frozenset({"id", "name", "date"})
_RELEASE_ONLY_JSON_KEYS = frozenset({"date_gmt"})
# ``_request`` chỉ nhận các tùy chọn client tự dùng: không ``files`` (thân ``multipart`` thành
# ``$_POST``, WordPress đọc ``rest_route`` từ đó), không ``verify``, ``auth``, ``cookies``…
_REQUEST_OPTIONS = frozenset({"params", "json", "data", "headers"})
# Header riêng của lệnh chỉ có loại file và tên file khi tải ảnh (``_post_media``).
_REQUEST_HEADERS = frozenset({"content-type", "content-disposition"})
_ROUTE_BLOCKED = (
    "Phần mềm chặn một lệnh gọi WordPress không có trong danh sách được phép. Không có gì được "
    "gửi lên website."
)

# ---------------------------------------------------------------- hẹn giờ, đăng (T-099)
# Dấu riêng của ``release_draft`` (LC-T094-22, thiết kế T-094 mục 3.3): ``_request`` gỡ nó khỏi
# tùy chọn trước khi gửi (không tới ``requests``), ``_is_plain_request`` so bằng ``is``. Chỉ lệnh
# mang dấu này mới gửi được ``status`` khác ``"draft"`` và khóa ``date_gmt``, và chỉ đúng khuôn
# ``_is_release_request``. Test đọc mã nguồn: tên này chỉ có ở đây, ``release_draft`` và
# ``_is_plain_request``.
_RELEASE = object()
RELEASE_MODES = ("future", "publish")
_RELEASE_PATH = re.compile(rf"/wp/v2/posts/{_ID}")
_RELEASE_FIELDS = "id,status,date_gmt,link"  # câu trả lời lệnh chuyển: không nội dung bài
_RELEASE_CHECK_FIELDS = "id,status"  # hỏi lại còn nháp ngay trước lệnh chuyển
_DATE_GMT_PATTERN = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}")
# Đọc trạng thái bài (``post_statuses``, LC-T094-26): chỉ đọc, giá trị tham số là hằng.
POST_STATUS_FILTER = "draft,future,publish,pending,private"
POST_STATUSES = frozenset(POST_STATUS_FILTER.split(","))
_STATUS_FIELDS = "id,status,date_gmt,modified_gmt,link"
MAX_STATUS_IDS = 100  # mỗi lệnh ``include`` tối đa 100 mã (đúng ``per_page`` tối đa)
MAX_STATUS_LOOKUP = 1000  # ``post_statuses`` nhận tối đa chừng này mã (≤ 10 lệnh)
_ID_LIST = re.compile(rf"{_ID}(?:,{_ID}){{0,{MAX_STATUS_IDS - 1}}}")


def is_allowed_route(method: object, path: object) -> bool:
    """``(method, path)`` có trong ``ALLOWED_ROUTES`` (so khớp toàn chuỗi, phân biệt hoa thường).

    ``path`` là phần sau ``/wp-json``, không có ``?`` hay ``#`` (tham số đi qua ``params``).
    """
    if not isinstance(method, str) or not isinstance(path, str):
        return False
    lowered = path.lower()
    if any(part in lowered for part in _FORBIDDEN_IN_PATH):
        return False
    return any(
        method == allowed_method and pattern.fullmatch(path)
        for allowed_method, pattern in _ALLOWED_ROUTES
    )


def _is_plain_request(
    method: str, path: str, options: dict[str, Any], session: object, *, release: object = None
) -> bool:
    """Tham số, header, thân lệnh chỉ là loại client tự viết (LC-T042-1), xét TRƯỚC KHI gửi.

    - tùy chọn chỉ ``params``, ``json`` (``dict``), ``data`` (``bytes``), ``headers``; ``data``
      chỉ ở lệnh tải ảnh (``_is_image_upload``, SL-T099-1);
    - khóa ``params`` thuộc ``ALLOWED_PARAMS`` của đúng đường, giá trị là chữ hay số nguyên;
      không bao giờ có ``rest_route``, ``_method``, ``_envelope``, ``_jsonp``; ``_fields`` không
      rỗng, không hỏi trường trong ``_RENDERED_FIELDS`` (LC-T060-2);
    - giá trị ``include``, ``status``, ``context`` của ``GET /wp/v2/posts`` đúng dạng
      ``_PARAM_VALUES`` (LC-T094-26);
    - khóa thân JSON cấp trên cùng thuộc ``ALLOWED_JSON_KEYS`` của đúng đường, không bao giờ có
      ``id``, ``name``, ``date``, ``date_gmt``; có ``status`` thì chỉ ``"draft"`` (LC-T060-1);
    - ``release`` đúng là dấu ``_RELEASE`` (so bằng ``is``): lệnh phải đúng khuôn
      ``_is_release_request`` (hẹn giờ/đăng, LC-T094-22) thay cho luật thân JSON ở trên; ``release``
      là thứ khác (kể cả bản chép của dấu): từ chối;
    - header chỉ ``Content-Type`` (loại ảnh trong ``IMAGE_TYPES``) và ``Content-Disposition``;
      không header nào (kể cả của ``session``) có chữ "method" (``X-HTTP-Method-Override``…);
    - ``session`` không có ``params`` hay ``Content-Type`` riêng (``requests`` gộp vào mọi lệnh).
    """
    released = release is _RELEASE
    if release is not None and not released:
        return False
    if released and not _is_release_request(method, path, options):
        return False
    if not set(options) <= _REQUEST_OPTIONS:
        return False
    allowed = next(
        (names for m, pattern, names in _ROUTE_PARAMS if m == method and pattern.fullmatch(path)),
        None,
    )
    json_keys = next(
        (keys for m, pattern, keys in _ROUTE_JSON_KEYS if m == method and pattern.fullmatch(path)),
        None,
    )
    params, headers = options.get("params"), options.get("headers")
    data, payload = options.get("data"), options.get("json")
    if allowed is None or json_keys is None or getattr(session, "params", None):
        return False
    if not (data is None or type(data) is bytes) or not (payload is None or type(payload) is dict):
        return False
    if data is not None and not _is_image_upload(method, path, headers, payload):
        return False
    if payload is not None and not released:
        for key in payload:
            if type(key) is not str or key not in json_keys:
                return False
            if key.lower() in _FORBIDDEN_JSON_KEYS | _RELEASE_ONLY_JSON_KEYS:
                return False
        status = payload.get("status", "draft")
        if type(status) is not str or status != "draft":
            return False
    if params is not None:
        if type(params) is not dict:
            return False
        for key, value in params.items():
            if type(key) is not str or key not in allowed or type(value) not in (str, int):
                return False
            folded = re.sub(r"[^a-z0-9]", "_", key.lower())
            if any(name in folded for name in _FORBIDDEN_PARAMS):
                return False
            if "fields" in folded and _asks_rendered_fields(value):
                return False
            check = _PARAM_VALUES.get((method, path, key))
            if check is not None and not check(value):
                return False
    if headers is not None:
        if type(headers) is not dict:
            return False
        for name, value in headers.items():
            if type(name) is not str or name.lower() not in _REQUEST_HEADERS:
                return False
            if type(value) is not str:
                return False
            if name.lower() == "content-type" and value not in IMAGE_TYPES.values():
                return False
    session_headers = getattr(session, "headers", None) or {}
    if any(str(name).lower() == "content-type" for name in session_headers):
        return False
    return not any("method" in str(name).lower() for name in [*session_headers, *(headers or {})])


def _is_image_upload(method: str, path: str, headers: object, payload: object) -> bool:
    """Thân byte (``data``) chỉ được ở lệnh tải ảnh (SL-T099-1): đúng ``POST /wp/v2/media``,
    không kèm ``json``, có đúng một header ``Content-Type`` thuộc ``IMAGE_TYPES``.

    ``requests`` không gắn ``Content-Type`` cho byte; WordPress lõi hôm nay không đọc thân thiếu
    ``Content-Type`` với ``POST`` (PHP chỉ điền ``$_POST`` cho thân dạng form), nhưng lời hứa «chỉ
    lệnh có dấu ``_RELEASE`` gửi được ``status`` khác nháp» phải nằm ở lớp chặn này, không dựa vào
    cách website đọc thân: thân byte ở đường khác (``status=publish``, ``id=7``…) bị từ chối.
    """
    if method != "POST" or path != "/wp/v2/media" or payload is not None:
        return False
    if type(headers) is not dict:
        return False
    types = [
        value
        for name, value in headers.items()
        if type(name) is str and name.lower() == "content-type"
    ]
    return len(types) == 1 and type(types[0]) is str and types[0] in IMAGE_TYPES.values()


def _is_release_request(method: str, path: str, options: dict[str, Any]) -> bool:
    """Khuôn duy nhất của lệnh hẹn giờ/đăng (LC-T094-22, thiết kế T-094 mục 3.3):
    ``POST /wp/v2/posts/<mã>``, chỉ ``json`` và ``params``; ``params`` đúng
    ``{"_fields": _RELEASE_FIELDS}``; thân **đúng** ``{"status": "future", "date_gmt":
    "YYYY-MM-DDTHH:MM:SS"}`` hoặc ``{"status": "publish"}`` (``str`` thật, đúng chữ). Không
    ``date``, không nội dung, tiêu đề, không khóa nào khác."""
    if method != "POST" or not _RELEASE_PATH.fullmatch(path):
        return False
    if set(options) != {"json", "params"}:
        return False
    params, payload = options["params"], options["json"]
    if type(params) is not dict or list(params) != ["_fields"]:
        return False
    if type(params["_fields"]) is not str or params["_fields"] != _RELEASE_FIELDS:
        return False
    if type(payload) is not dict or any(type(key) is not str for key in payload):
        return False
    status = payload.get("status")
    if type(status) is not str:
        return False
    if status == "publish":
        return list(payload) == ["status"]
    if status != "future" or sorted(payload) != ["date_gmt", "status"]:
        return False
    stamp = payload["date_gmt"]
    return type(stamp) is str and stamp.isascii() and bool(_DATE_GMT_PATTERN.fullmatch(stamp))


def _is_id_list(value: object) -> bool:
    """``include`` của ``post_statuses``: 1–100 số nguyên dương (chữ số ASCII, không số 0 đầu),
    nối bằng dấu phẩy, không dấu cách (LC-T094-26)."""
    return type(value) is str and value.isascii() and bool(_ID_LIST.fullmatch(value))


# Giá trị tham số kiểm thêm theo (phương thức, đường đúng chữ, tên) (LC-T094-26): T-085 chỉ kiểm
# kiểu. ``GET /wp/v2/posts`` dùng cho cả ``list_published`` (``status=publish``) lẫn
# ``post_statuses`` (``include``, ``context=edit``, ``status`` hằng).
_PARAM_VALUES: dict[tuple[str, str, str], Any] = {
    ("GET", "/wp/v2/posts", "include"): _is_id_list,
    ("GET", "/wp/v2/posts", "status"): lambda value: value in ("publish", POST_STATUS_FILTER),
    ("GET", "/wp/v2/posts", "context"): lambda value: value == "edit",
}


def _asks_rendered_fields(value: str | int) -> bool:
    """Giá trị ``_fields`` rỗng hay hỏi trường trong ``_RENDERED_FIELDS`` (LC-T060-2).

    Tách như ``wp_parse_list`` của WordPress (dấu phẩy, khoảng trắng), rồi cắt hai đầu mỗi phần
    như ``trim()`` của PHP mà ``get_fields_for_response`` chạy sau đó (``_PHP_TRIM``, có cả NUL:
    "\\x00content" vẫn là ``content``, SL-T085-1); tên trường là phần trước dấu chấm
    (``content.rendered`` là ``content``, cũng cắt hai đầu), so trên chữ thường. ``_fields`` rỗng
    (``""``, ``","``, chỉ NUL) thì WordPress trả MỌI trường, kể cả ``content``, nên cũng bị chặn.
    """
    names = []
    for part in re.split(r"[\s,]+", str(value)):
        part = part.strip(_PHP_TRIM)
        if part:
            names.append(part.split(".", 1)[0].strip(_PHP_TRIM).lower())
    return not names or any(name in _RENDERED_FIELDS for name in names)


# ---------------------------------------------------------------- ghi SEO (T-042)
MAX_SEO_TITLE_CHARS = 200
MAX_SEO_DESC_CHARS = 500
MAX_SEO_KEYWORD_CHARS = 200
SEO_FIELDS = ("title", "description", "focus_keyword")
# Tên trường trong ``input`` của ability (SiteSEO 1.4.2, ``abilitiesregister.php:261-316``).
# Chỉ 3 trường này; không bao giờ gửi canonical, robots (bài mới để SiteSEO tự đặt).
_ABILITY_FIELDS = {
    "title": "title",
    "description": "description",
    "focus_keyword": "focus_keyphrase",
}
# Đường dự phòng chỉ có 2 khóa meta site đã mở (T-033 mục 1.3); không có từ khóa chính.
_META_FIELDS = {"title": SITESEO_TITLE_KEY, "description": SITESEO_DESC_KEY}
# Mã ký tự HTML dạng số thiếu dấu ";" (trình duyệt vẫn giải mã "&#37" thành "%").
_NUMERIC_REF = re.compile(r"&#(?:[0-9]|x[0-9a-f])", re.IGNORECASE)
# Tên thực thể HTML cũ trình duyệt vẫn giải mã khi THIẾU ";" (``&lt``, ``&amp``, ``&copy``…;
# SL-T042-2). Phân biệt hoa thường như HTML (``&LT`` có, ``&Lt`` không). "R&D", "AT&T" vẫn qua.
_LEGACY_ENTITY = re.compile(
    "&(?:"
    + "|".join(
        re.escape(name)
        for name in sorted(
            (n for n in html.entities.html5 if not n.endswith(";")), key=len, reverse=True
        )
    )
    + ")"
)
# Mở đầu shortcode WordPress (T-061, LC-T042-3): "[" (có thể thêm một "[" hay "/") ngay trước
# ký tự ``do_shortcode`` nhận làm tên (mọi ký tự trừ ``<>&/[]=``, khoảng trắng, ký tự điều khiển;
# ``wp-includes/shortcodes.php``). Chữ SEO không dùng được "&#91;" (mọi mã ký tự HTML bị chặn),
# nên chặn hẳn; "[ 2026 ]" (dấu cách sau "[") hay "[" không có "]" phía sau thì không phải.
_SHORTCODE_OPEN = re.compile(r"\[[\[/]?[^<>&/\[\]=\x00-\x20]")
# "<" mà ký tự ngay sau KHÔNG phải khoảng trắng ASCII (hoặc "<" ở cuối chữ): ``strip_tags`` của
# PHP mở thẻ ở đó (``isspace`` của C: " \t\n\r\v\f"; không dùng ``str.isspace`` của Python, vốn
# nhận cả U+00A0, U+3000). LC-T061-2.
_TAG_LIKE_OPEN = re.compile(r"<(?![ \t\n\r\v\f])")

_SEO_NOT_OWN = (
    "Chỉ được ghi SEO cho bài nháp app vừa tạo trong lần làm việc này, không sửa bài đã có "
    "trên website."
)
_SEO_NOT_DRAFT = (
    "Bài này không còn là bản nháp trên website (có thể đã được đăng hoặc bị xóa). Phần mềm "
    "không sửa bài đã đăng (không ghi SEO, không đổi ảnh đại diện); nếu cần, sửa tay trong "
    "trang quản trị WordPress."
)
_IMAGE_ODD_ANSWER = (
    "WordPress trả lời lệnh đặt ảnh đại diện không khớp với bài nháp vừa tạo (bài khác, hoặc "
    "bài không còn là nháp). Hãy mở bài trong trang quản trị WordPress để kiểm tra."
)
_IMAGE_CHECK_FAILED = (
    "Không kiểm được bài nháp trên WordPress trước khi đặt ảnh đại diện{code}. Chưa ghi gì; "
    "thử lại sau."
)
# Dữ liệu WordPress trả về sai kiểu (LC-T044-1): câu cố định, không chép dữ liệu.
_BAD_DATA = (
    "WordPress trả về dữ liệu {what} không đúng dạng. Thử lại sau; nếu vẫn lỗi, có thể một "
    "plugin trên website đang làm sai câu trả lời của REST API."
)
_SEO_CHECK_FAILED = (
    "Không kiểm được bài nháp trên WordPress trước khi ghi SEO{code}. Chưa ghi gì; bài nháp "
    "vẫn còn. Thử lại sau, hoặc chép tay tiêu đề, mô tả SEO vào hộp SiteSEO của bài nháp."
)
_SEO_EMPTY = "Chưa có tiêu đề, mô tả hay từ khóa chính SEO nào để ghi."
_SEO_DISABLED = (
    "Chưa bật ghi SEO lên website: hãy chép tiêu đề, mô tả SEO vào hộp SiteSEO của bài nháp."
)
_SEO_UNAVAILABLE = (
    "Website chưa cho phần mềm ghi SEO (SiteSEO chưa bật Abilities). Bài nháp đã tạo; hãy chép "
    "tiêu đề, mô tả SEO vào hộp SiteSEO của bài nháp."
)
_SEO_ERROR = (
    "Ghi SEO lên website không thành công{code}. Bài nháp vẫn còn; hãy chép tay tiêu đề, mô tả "
    "SEO vào hộp SiteSEO của bài nháp, hoặc thử lại sau."
)
_SEO_WRITTEN = "Đã ghi SEO vào hộp SiteSEO của bài nháp."
_SEO_WRITTEN_CHANGED = (
    "Đã ghi SEO vào hộp SiteSEO của bài nháp, nhưng SiteSEO tự bỏ vài ký tự khi lưu (ví dụ «%» "
    "liền hai chữ/số như «10%BE», hay dấu «\\»). Mở hộp SiteSEO của bài nháp để xem lại chữ đã lưu."
)
_SEO_WRITTEN_NO_KEYWORD = (
    "Đã ghi tiêu đề, mô tả SEO vào bài nháp. Từ khóa chính chưa ghi được bằng đường dự phòng: "
    "chép tay vào hộp SiteSEO."
)

# ---------------------------------------------------------------- gửi nháp kèm ảnh (T-054)
# Alt/chú thích dài hơn thì báo lỗi trước khi tải (alt AI gợi ý mặc định ≤ 125, chú thích ≤ 200).
MAX_IMAGE_ALT_CHARS = 500
MAX_IMAGE_CAPTION_CHARS = 1000
AI_MEDIA_TITLE_PREFIX = "[AI] "  # tiêu đề media của ảnh AI (thiết kế T-046 mục 4)
_WEBP_TYPE = "image/webp"

_DRAFT_EMPTY_TITLE = "Tiêu đề bài viết không được để trống."
_DRAFT_BAD_PART = (
    "Nội dung bài chỉ được gồm các đoạn HTML (chữ) và ảnh đã duyệt. Chưa gửi gì lên website."
)
_DRAFT_TWO_FEATURED = "Chỉ được chọn một ảnh đại diện. Chưa gửi gì lên website."
_IMAGE_NOT_WEB = (
    "Ảnh thứ {n} chưa qua bước xử lý ảnh của phần mềm (cần file WebP do phần mềm tạo). Chưa gửi "
    "gì lên website."
)
_IMAGE_NO_ALT = "Ảnh thứ {n} chưa có alt (mô tả ảnh). Viết hoặc duyệt alt rồi gửi lại."
_IMAGE_TEXT_TOO_LONG = (
    "Alt hoặc chú thích của ảnh thứ {n} quá dài (alt tối đa {alt} ký tự, chú thích tối đa "
    "{caption} ký tự). Rút gọn rồi gửi lại."
)
_IMAGE_BAD_TAGS = "Thẻ của ảnh thứ {n} không hợp lệ. Chưa gửi gì lên website."
_MEDIA_ODD_ANSWER = (
    "WordPress trả lời lệnh ghi alt cho ảnh vừa tải lên không khớp với ảnh đó. Chưa tạo bài nháp."
)
_MEDIA_BAD_URL = (
    "WordPress trả về địa chỉ ảnh không phải https trên đúng website. Chưa tạo bài nháp."
)
_MEDIA_NOT_CREATED = (
    "WordPress không xác nhận đã tạo ảnh mới trong thư viện Media (cần mã 201 Created). Chưa ghi "
    "alt cho ảnh này, chưa tạo bài nháp."
)
_MEDIA_SAME_ID = (
    "WordPress trả cùng một mã ảnh cho hai ảnh khác nhau trong lần gửi này (có thể là một ảnh đã "
    "có trên website). Phần mềm không ghi alt đè lên ảnh đó, chưa tạo bài nháp."
)
# ``upload_media``: lệnh tải lỗi mà không phải lời từ chối 4xx rõ ràng (5xx, hết giờ, mất kết nối,
# ``201`` hỏng thân…): ảnh có thể đã lên (SL-T085-3).
_MEDIA_MAYBE_UPLOADED = (
    " Ảnh có thể đã lên thư viện Media của website: kiểm Media → Thư viện trong trang quản trị "
    "WordPress trước khi tải lại (tải lại sẽ thêm một ảnh nữa)."
)
_MEDIA_UPLOAD_UNEXPECTED = "Tải ảnh lên WordPress gặp lỗi không mong đợi ({kind})."
# ``upload_media``: ảnh đã lên (201) mà không xác nhận được lệnh ghi đè ba ô (LC-T060-3, SL-T060-1).
_MEDIA_NOT_DESCRIBED = (
    "Ảnh đã lên thư viện Media của website (mã ảnh {media_id}) nhưng phần mềm không xác nhận được "
    "đã ghi alt, tiêu đề, chú thích cho ảnh đó{code}, nên ảnh có thể đang mang chữ WordPress tự "
    "lấy từ file. Vào Media → Thư viện trong trang quản trị WordPress, mở ảnh mã {media_id} để "
    "kiểm, sửa hoặc xóa trước khi tải lại (tải lại sẽ thêm một ảnh nữa). Chưa tạo bài nháp."
)
_DRAFT_IMAGES_LEFT = (
    " Đã có {count} ảnh lên thư viện Media trước khi lỗi (danh sách bên dưới). Phần mềm không xóa "
    "ảnh: ảnh vẫn xem được công khai qua đường dẫn; nếu không dùng, hãy tự xóa trong trang quản "
    "trị WordPress (Media → Thư viện)."
)
_DRAFT_IMAGES_NONE = " Chưa có ảnh nào lên thư viện Media."
_DRAFT_IMAGE_MAYBE = (
    " Ảnh đang tải lúc lỗi có thể vẫn đã lên thư viện Media: kiểm tra Media → Thư viện trong "
    "trang quản trị."
)
# Lỗi ở chính lệnh tạo nháp mà không phải lời từ chối 4xx rõ ràng (LC-T054-2, SL-T054-3).
_DRAFT_MAYBE_CREATED = (
    " Bài nháp có thể vẫn đã được tạo dù có lỗi: trước khi gửi lại, mở trang quản trị WordPress, "
    "kiểm tra Bài viết → Nháp (và Media → Thư viện) để không tạo thêm một bài nháp trùng và tải "
    "lại ảnh lần nữa."
)
_DRAFT_NOT_CREATED = " Chưa tạo bài nháp."
_DRAFT_UNEXPECTED = "Gửi nháp kèm ảnh gặp lỗi không mong đợi ({kind})."
_FEATURED_NOT_SET = (
    "Đã tạo bài nháp kèm ảnh nhưng chưa đặt được ảnh đại diện. {reason} Có thể đặt tay trong "
    "trang quản trị WordPress."
)

# Câu báo hẹn giờ/đăng (T-099): cố định, không chép lời máy chủ, không chép WORDPRESS_URL. Mã bài
# là số đã kiểm. «Chưa gửi gì», «vẫn là nháp» chỉ dùng khi chắc chắn chưa có lệnh chuyển nào chạy.
_RELEASE_NOT_OWN = (
    "Chỉ hẹn giờ hay đăng được bài nháp phần mềm vừa tạo trong chính lần gửi này. Bài đã có trên "
    "website thì hẹn giờ, đăng trong trang quản trị WordPress. Chưa gửi gì lên website."
)
_RELEASE_BAD_MODE = "Hình thức gửi phải là hẹn giờ hoặc đăng ngay. Chưa gửi gì lên website."
_RELEASE_BAD_TIME = (
    "Giờ hẹn phải có ngày, giờ và múi giờ rõ ràng. Chưa hẹn giờ: bài vẫn là nháp trên website."
)
_RELEASE_NOW_WITH_TIME = (
    "Đăng ngay thì không kèm giờ hẹn. Chưa đăng: bài vẫn là nháp trên website."
)
_RELEASE_CHECK_FAILED = (
    "Không kiểm được bài nháp trên website ngay trước khi hẹn giờ/đăng{code}. Chưa hẹn giờ, chưa "
    "đăng: bài vẫn là nháp."
)
_RELEASE_NOT_DRAFT = (
    "Bài không còn là nháp trên website (có thể ai đó đã đăng, hẹn giờ, chuyển hay xóa bài trong "
    "trang quản trị). Phần mềm không gửi lệnh nào vào bài này nữa; mở trang quản trị WordPress để "
    "xem."
)
_RELEASE_STILL_DRAFT = " Chưa hẹn giờ, chưa đăng: bài vẫn là nháp trên website."
_RELEASE_UNSURE = (
    "Không biết chắc lệnh {action} đã chạy trên website chưa{code}. Bài (mã {post_id}) có thể đã "
    "{done}. Mở trang quản trị WordPress kiểm tra bài này trước khi làm gì tiếp; phần mềm không "
    "tự gửi lại."
)
_RELEASE_ODD_ANSWER = (
    "Website trả lời lệnh {action} không đúng như mong đợi. Bài (mã {post_id}) có thể đã {done} "
    "hoặc vẫn là nháp. Mở trang quản trị WordPress kiểm tra bài này; phần mềm không tự gửi lại."
)
_RELEASE_WRONG_TIME = (
    "Website báo bài (mã {post_id}) đã hẹn giờ nhưng giờ hẹn khác giờ đã chọn. Mở trang quản trị "
    "WordPress kiểm tra và sửa giờ hẹn; phần mềm không gửi thêm lệnh nào vào bài này."
)
# Hẹn giờ mà website đăng ngay (security.md mục 7, «Lỡ đăng bài»).
_RELEASE_WENT_PUBLIC = (
    "KHẨN: website báo bài (mã {post_id}) đã ĐĂNG CÔNG KHAI NGAY, không phải hẹn giờ. Nếu chưa "
    "muốn đăng: vào trang quản trị WordPress → Bài viết, mở bài này, chuyển về «Bản nháp» rồi bấm "
    "Cập nhật, và báo chủ dự án. Phần mềm không gửi thêm lệnh nào vào bài này."
)
_RELEASE_WORDS = {  # hình thức → (tên lệnh, điều có thể đã xảy ra)
    "future": ("hẹn giờ", "được hẹn giờ"),
    "publish": ("đăng", "hiện công khai"),
}
_STATUS_BAD_IDS = (
    "Danh sách mã bài cần xem trạng thái không hợp lệ (phải là số nguyên dương, tối đa "
    f"{MAX_STATUS_LOOKUP} mã). Chưa hỏi website."
)


IMAGE_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".avif": "image/avif",
}


class WordPressError(Exception):
    """Lỗi khi làm việc với WordPress. ``str(err)`` là thông báo tiếng Việt cho người dùng."""

    def __init__(self, message: str, *, status_code: int | None = None, code: str = "") -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code


@dataclass(frozen=True)
class ConnectionInfo:
    site_name: str
    site_url: str
    user_name: str
    roles: tuple[str, ...]
    can_edit_posts: bool
    can_publish_posts: bool
    can_upload_files: bool
    # SiteSEO có cho phần mềm ghi SEO qua Abilities không (T-042): True ghi được; False chưa
    # bật (hoặc tài khoản không đủ quyền); None không dò được (lỗi mạng, máy chủ).
    siteseo_writable: bool | None = None
    # Vai trò của tài khoản có quyền ``unfiltered_html`` không (T-091). Không có thì WordPress lọc
    # bài khi lưu (kses) và bỏ ``srcset`` app ghi sẵn cho ảnh: điện thoại tải bản thu nhỏ đã mất
    # GPS (T-059). Có (Biên tập viên trên site đơn) vẫn có thể bị tắt bằng
    # ``DISALLOW_UNFILTERED_HTML`` hay khi site là multisite: REST không cho biết điều đó.
    can_unfiltered_html: bool = False
    # Múi giờ của website (T-099, đọc ở ``GET /wp-json/``): dữ liệu website, đã kiểm dạng
    # (``_site_timezone``, ``_site_offset``; lạ thì rỗng / ``None``). Chỉ dùng cho
    # ``timezone_warning`` (LC-T094-27): bài hẹn giờ gửi ``date_gmt`` (giờ tuyệt đối), múi giờ của
    # site chỉ đổi giờ hiện trong trang quản trị.
    timezone_string: str = ""
    gmt_offset: float | None = None

    def timezone_warning(self, timezone_name: str = DEFAULT_TIMEZONE) -> str:
        """Câu Cảnh báo khi trang quản trị WordPress sẽ hiện giờ hẹn khác giờ của phần mềm
        (``timezone_name``, mặc định giờ Việt Nam); chuỗi rỗng khi cùng giờ. Câu cố định, chỉ
        chèn độ lệch đã kiểm là số (không chép chữ website trả)."""
        app = "giờ Việt Nam" if timezone_name == DEFAULT_TIMEZONE else f"giờ {timezone_name}"
        if self.gmt_offset is None:
            return (
                "Không đọc được múi giờ của website. Kiểm trong WordPress → Cài đặt → Tổng quan → "
                f"Múi giờ (nên chọn «Hồ Chí Minh»). Bài hẹn giờ vẫn lên đúng {app} đã chọn."
            )
        offset = ZoneInfo(timezone_name).utcoffset(datetime.now(UTC))
        if offset is not None and round(self.gmt_offset * 60) * 60 == offset.total_seconds():
            return ""
        return (
            f"Múi giờ của website là {_format_offset(self.gmt_offset)}, khác {app}: trang quản trị "
            f"WordPress sẽ hiện giờ hẹn khác, nhưng bài vẫn lên đúng {app} đã chọn. Nên đặt "
            "WordPress → Cài đặt → Tổng quan → Múi giờ là «Hồ Chí Minh»."
        )

    @property
    def unfiltered_html_status(self) -> str:
        """Câu cảnh báo cho trang Kết nối WordPress khi tài khoản thiếu ``unfiltered_html``;
        chuỗi rỗng khi có quyền."""
        if self.can_unfiltered_html:
            return ""
        return (
            "Tài khoản WordPress này không có quyền đăng HTML không lọc (unfiltered_html): khi lưu "
            "bài, WordPress bỏ phần giữ ảnh 1600 px, nên điện thoại có thể tải bản thu nhỏ đã mất "
            "vị trí GPS. Nhờ người quản trị website dùng vai trò Biên tập viên cho tài khoản này."
        )

    @property
    def siteseo_status(self) -> str:
        """Một dòng tiếng Việt cho giao diện: "SiteSEO: ghi được / chưa bật"."""
        if self.siteseo_writable is True:
            return "SiteSEO: ghi được"
        if self.siteseo_writable is False:
            return (
                "SiteSEO: chưa bật (bật Abilities trong SiteSEO để phần mềm ghi tiêu đề, mô tả, "
                "từ khóa chính vào bài nháp)"
            )
        return "SiteSEO: chưa dò được (thử kiểm tra kết nối lại sau)"


@dataclass(frozen=True)
class SeoWriteResult:
    """Kết quả ``set_seo_meta``. Không ghi được thì app quay về chép tay, không chặn tạo nháp.

    ``reason``: ``""`` (đã ghi), ``"disabled"`` (tùy chọn ghi SEO đang tắt), ``"unavailable"``
    (site chưa cho ghi: im lặng quay về chép tay), ``"error"`` (máy chủ báo lỗi khi ghi).
    ``message`` là câu tiếng Việt cố định, không chép thông điệp của máy chủ.
    """

    written: bool
    route: str = ""  # "abilities" (đường chính) | "meta" (dự phòng qua wp/v2/posts) | ""
    fields: tuple[str, ...] = ()  # trường đã ghi: "title", "description", "focus_keyword"
    reason: str = ""
    message: str = ""
    status_code: int | None = None


@dataclass(frozen=True)
class Released:
    """Kết quả ``release_draft``: website xác nhận đúng trạng thái đã chọn (T-099).

    ``status``: ``"future"`` (đã hẹn giờ) hoặc ``"publish"`` (đã đăng công khai). ``date_gmt``:
    giờ UTC dạng ``YYYY-MM-DDTHH:MM:SS``; với ``future`` là đúng chuỗi đã gửi (website trả khác
    thì không có kết quả này mà là ``ReleaseError``), với ``publish`` là giờ đăng website trả (rỗng
    nếu sai dạng). ``link``: địa chỉ bài, ``https://`` trên đúng website, rỗng nếu lạ (chưa escape:
    giao diện hiện chữ thuần, không bấm được).
    """

    post_id: int
    status: str
    date_gmt: str
    link: str
    edit_link: str


class ReleaseError(WordPressError):
    """Hẹn giờ/đăng (``release_draft``) không xong. ``str(err)`` là câu tiếng Việt cố định.

    - ``unsure``: lệnh chuyển đã gửi mà không biết chắc kết quả (hết giờ, mất mạng, chuyển hướng,
      5xx, câu trả lời sai dạng, sai trạng thái, sai giờ): bài **có thể đã** hẹn giờ/đăng.
      Giao diện khóa gửi lại, hướng dẫn kiểm trang quản trị; không tự gửi lại (LC-T094-25).
    - ``went_public``: người dùng chọn hẹn giờ mà website báo bài đã **đăng công khai** (câu báo
      khẩn, cách chuyển về nháp).
    - Cả hai tắt: bài chắc chắn chưa chuyển (bị chặn trước khi gửi, hay website từ chối 4xx).
    - ``post_id``, ``edit_link``: bài liên quan (0, rỗng khi lỗi trước khi biết bài).
    """

    def __init__(
        self,
        message: str,
        *,
        unsure: bool = False,
        went_public: bool = False,
        post_id: int = 0,
        edit_link: str = "",
        status_code: int | None = None,
        code: str = "",
    ) -> None:
        super().__init__(message, status_code=status_code, code=code)
        self.unsure = unsure
        self.went_public = went_public
        self.post_id = post_id
        self.edit_link = edit_link


@dataclass(frozen=True)
class PostState:
    """Trạng thái một bài trên website (``post_statuses``, chỉ đọc, T-099). Dữ liệu website đã
    kiểm dạng: ``status`` thuộc ``POST_STATUSES``; ``date_gmt``, ``modified_gmt`` dạng
    ``YYYY-MM-DDTHH:MM:SS`` (UTC) hay rỗng; ``link`` ``https://`` trên đúng website hay rỗng."""

    id: int
    status: str
    date_gmt: str = ""
    modified_gmt: str = ""
    link: str = ""


@dataclass(frozen=True)
class Term:
    """Chuyên mục hoặc thẻ."""

    id: int
    name: str
    slug: str
    count: int
    parent: int = 0


@dataclass(frozen=True)
class Post:
    id: int
    status: str
    title: str
    link: str
    edit_link: str
    featured_media: int = 0


@dataclass(frozen=True)
class PublishedItem:
    """Một bài hoặc trang ĐÃ ĐĂNG trên site (đọc từ REST hoặc từ cache).

    Tự kiểm khuôn khi tạo: dữ liệu từ site và từ file cache đều là chưa tin cậy. Sai khuôn thì
    ``ValueError``. Chữ ở dạng thuần (không thẻ, đã giải mã ``&amp;``) nhưng **chưa escape**:
    nơi hiện lên giao diện hoặc ghép vào HTML phải tự ``html.escape``.
    """

    id: int
    type: str  # "post" hoặc "page"
    slug: str
    link: str
    title: str
    meta_title: str = ""  # trống: site chưa đặt (SiteSEO dùng mẫu theo tiêu đề bài)
    meta_desc: str = ""
    modified_gmt: str = ""  # "YYYY-MM-DDTHH:MM:SS" giờ UTC như WordPress trả; trống nếu thiếu

    def __post_init__(self) -> None:
        if _positive_id(self.id) is None:  # số nguyên 1 … MAX_ID (SL-T091-2)
            raise ValueError("id phải là số nguyên dương")
        if self.type not in PUBLISHED_TYPES:
            raise ValueError("loại phải là post hoặc page")
        limits = {
            "slug": MAX_SLUG_CHARS,
            "link": MAX_LINK_CHARS,
            "title": MAX_TITLE_CHARS,
            "meta_title": MAX_META_CHARS,
            "meta_desc": MAX_META_CHARS,
            "modified_gmt": 19,
        }
        for name, limit in limits.items():
            value = getattr(self, name)
            if not isinstance(value, str) or len(value) > limit:
                raise ValueError(f"{name} sai kiểu hoặc quá dài")
            if _CONTROL_CHARS.search(value) or _has_invisible(value):
                raise ValueError(f"{name} có ký tự điều khiển hoặc ký tự vô hình")
        if self.slug and not _SLUG_PATTERN.fullmatch(self.slug):
            raise ValueError("slug có ký tự lạ")
        if self.modified_gmt and not _MODIFIED_PATTERN.fullmatch(self.modified_gmt):
            raise ValueError("modified_gmt sai dạng")
        if not self.link:
            raise ValueError("thiếu link")


class PublishedList(list[PublishedItem]):
    """Kết quả ``list_published``: một ``list`` bình thường, thêm cờ ``truncated``.

    ``truncated`` đúng khi site báo nhiều trang kết quả hơn ``MAX_PAGES`` nên danh sách chưa
    đủ (SL-T037-2). Khi đó đừng kết luận "link hỏng" chỉ vì link không có trong danh sách.
    """

    truncated: bool = False


@dataclass(frozen=True)
class Media:
    id: int
    source_url: str
    alt_text: str = ""


def _no_tags() -> ImageTags:
    """Thẻ mặc định của ``DraftImage``: ảnh thật, chưa có thẻ nào. Nhập muộn như module ảnh."""
    from seo_app.images.tags import ImageTags

    return ImageTags()


@dataclass(frozen=True)
class DraftImage:
    """Một ảnh người dùng đã chọn và duyệt, để ``create_draft_with_images`` tải lên (T-054).

    - ``image``: ``WebImage`` do ``make_web_image`` tạo (T-049). Byte ``image.data`` được gửi
      **nguyên vẹn** (không sửa, không nén lại) để GPS tới web (quyết định 5A, Lá Chắn T-049
      điều kiện 4).
    - ``alt``, ``caption``: chữ người dùng đã duyệt. Có thể còn ký tự ngắt rộng 0 và escape
      Markdown của ``clean_ai_text``: client tự gỡ (``plain_image_text``) trước khi dùng.
    - ``tags``: thẻ của ảnh, **chỉ** nhận ``ImageTags`` (T-052): mã công trình, hạng mục, khu vực
      đều thuộc danh sách cố định, không phải chữ tự do (LC-T054-4). Chỉ dùng để đặt tên file
      qua ``naming.image_file_name``, nên tên file công khai không mang tên thư mục, tên file gốc
      hay tên khách (Lá Chắn T-049 điều kiện 4). Client kiểm đúng lớp và chạy lại bước kiểm của
      ``ImageTags`` trước khi dùng. ``tags.source == "ai"``: ảnh AI (tên file ``minh-hoa-ai-…``,
      tiêu đề media ``[AI] …``). Mặc định: ảnh thật, chưa có thẻ.
    - ``featured``: làm ảnh đại diện. Không ảnh nào được đánh dấu thì lấy ảnh đầu tiên trong bài.
    """

    image: WebImage
    alt: str
    caption: str = ""
    tags: ImageTags = field(default_factory=_no_tags)
    featured: bool = False


@dataclass(frozen=True)
class UploadedImage:
    """Ảnh đã lên thư viện Media (xem được công khai qua ``source_url``, kể cả khi bài là nháp).

    ``source_url`` rỗng khi lỗi xảy ra ngay sau lúc tải lên (chưa đọc được địa chỉ).
    """

    id: int
    file_name: str
    source_url: str
    edit_link: str


@dataclass(frozen=True)
class DraftWithImages:
    """Kết quả ``create_draft_with_images``.

    ``featured_media``: mã ảnh đại diện đã đặt; ``None`` khi chưa đặt được (``message`` nói vì
    sao) hoặc bài không có ảnh. Bài nháp và ảnh vẫn còn trên website trong mọi trường hợp.
    """

    post: Post
    images: tuple[UploadedImage, ...]
    featured_media: int | None = None
    message: str = ""


class DraftImagesError(WordPressError):
    """Gửi nháp kèm ảnh lỗi giữa chừng: ở bước tải ảnh, ghi alt (chưa gửi lệnh tạo nháp), hoặc ở
    chính lệnh tạo nháp (W2, góp ý Lá Chắn T-046 số 8). Không phải lỗi đặt ảnh đại diện: lúc đó
    bài nháp đã có, hàm trả kết quả kèm ``message``.

    ``uploaded``: ảnh ĐÃ lên thư viện Media trước khi lỗi. Phần mềm không xóa ảnh nào (không có
    hàm xóa); giao diện liệt kê ``uploaded`` để người dùng tự xử lý. ``maybe_uploaded``: ảnh đang
    tải lúc lỗi có thể đã lên mà website không trả mã (lỗi mạng, máy chủ, câu trả lời sai dạng).
    ``maybe_draft``: lỗi ở lệnh tạo nháp mà không phải lời từ chối 4xx rõ ràng (hết giờ, mất
    mạng, 5xx, chuyển hướng, câu trả lời 2xx sai dạng): bài nháp **có thể đã có** trên website,
    người dùng kiểm Bài viết → Nháp trước khi gửi lại (LC-T054-2, SL-T054-3). ``maybe_draft``
    tắt thì chưa có bài nháp nào được tạo.
    """

    def __init__(
        self,
        message: str,
        *,
        uploaded: Sequence[UploadedImage] = (),
        maybe_uploaded: bool = False,
        maybe_draft: bool = False,
        status_code: int | None = None,
        code: str = "",
    ) -> None:
        super().__init__(message, status_code=status_code, code=code)
        self.uploaded = tuple(uploaded)
        self.maybe_uploaded = maybe_uploaded
        self.maybe_draft = maybe_draft


@dataclass(frozen=True)
class _PlannedImage:
    """Một ảnh đã kiểm xong, sẵn sàng tải lên (chưa gửi gì)."""

    source: DraftImage
    file_name: str
    alt: str  # chữ thường đã gỡ ký tự ngắt, escape Markdown (alt_text gửi REST)
    caption: str  # chữ thường; escape HTML khi gửi
    ai_generated: bool  # thẻ đã kiểm lại có ``source == "ai"``


class WordPressClient:
    def __init__(
        self,
        base_url: str,
        username: str,
        app_password: str,
        *,
        session: requests.Session | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        write_seo: bool = False,
    ) -> None:
        """``write_seo``: cho ``set_seo_meta`` ghi SEO lên site. **Mặc định tắt** (T-042):
        khi tắt, ``set_seo_meta`` không gửi gì và trả kết quả "chép tay"."""
        base_url = base_url.strip().rstrip("/")
        if not re.match(r"^https?://[^/\s]+", base_url, re.IGNORECASE):
            # LC-T042-4: không chép lại địa chỉ (có thể là "htps://tên:mật-khẩu@site").
            raise WordPressError(
                "Địa chỉ website trong WORDPRESS_URL không hợp lệ. Sửa trong file .env, ví dụ "
                "đúng: https://example.com"
            )
        if not base_url.lower().startswith("https://"):
            # Qua http, Application Password đi trên mạng không mã hóa (security.md 2.7).
            raise WordPressError(
                "WORDPRESS_URL phải bắt đầu bằng https:// để mật khẩu không bị gửi qua mạng "
                "dưới dạng không mã hóa. Sửa trong file .env, ví dụ: https://example.com"
            )
        if not _is_plain_site_url(base_url):
            # SL-T042-3: base_url có ?, #, %, .., wp-json… làm đường thật khác đường đã kiểm.
            raise WordPressError(
                "WORDPRESS_URL chỉ được là địa chỉ website, ví dụ https://example.com (không có "
                "dấu ?, #, %, @, đoạn /wp-json, /.. hay tên file kiểu .php, .cgi). Sửa trong file "
                ".env."
            )
        if not username or not app_password:
            raise WordPressError("Thiếu tên đăng nhập hoặc Application Password của WordPress.")
        self.base_url = base_url
        self.timeout = timeout
        self._session = session or requests.Session()
        # WordPress bỏ qua dấu cách trong Application Password, nên xóa cho gọn.
        self._session.auth = (username, app_password.replace(" ", ""))
        self._session.headers.update({"Accept": "application/json", "User-Agent": "SEO-App/0.1"})
        # Bài do chính client này tạo: chỉ những bài này mới được sửa (ảnh đại diện, meta SEO),
        # để không bao giờ đụng tới bài đã có trên website (R3).
        self._created_post_ids: set[int] = set()
        self.write_seo = write_seo is True
        # Kết quả dò Abilities của SiteSEO (None: chưa dò hoặc dò lỗi, sẽ dò lại).
        self._siteseo_ok: bool | None = None

    @classmethod
    def from_settings(cls, settings: Settings, **kwargs: Any) -> WordPressClient:
        if not (
            settings.wordpress_url
            and settings.wordpress_username
            and settings.wordpress_app_password
        ):
            raise WordPressError(
                "Chưa khai báo WordPress. Điền WORDPRESS_URL, WORDPRESS_USERNAME và "
                "WORDPRESS_APP_PASSWORD trong file .env."
            )
        return cls(
            settings.wordpress_url,
            settings.wordpress_username,
            settings.wordpress_app_password,
            **kwargs,
        )

    def __repr__(self) -> str:
        return f"WordPressClient(base_url={self.base_url!r})"

    @property
    def uses_https(self) -> bool:
        """Luôn đúng: client từ chối địa chỉ không phải https ngay khi tạo."""
        return self.base_url.lower().startswith("https://")

    # ------------------------------------------------------------------ đọc

    def check_connection(self) -> ConnectionInfo:
        """Kiểm tra REST API, quyền của tài khoản, và SiteSEO có cho ghi SEO không.

        Lỗi kết nối/đăng nhập thì ném WordPressError. Dò SiteSEO chỉ đọc (``GET``) và không bao
        giờ làm hỏng kết quả kiểm tra: dò lỗi thì ``siteseo_writable`` là ``None``.
        """
        root = self._json(self._request("GET", "/"))
        namespaces = root.get("namespaces") if isinstance(root, dict) else None
        if not isinstance(namespaces, list) or "wp/v2" not in namespaces:
            raise WordPressError(
                "Website trả lời nhưng không có REST API của WordPress (wp/v2). "
                "Kiểm tra WORDPRESS_URL, hoặc plugin bảo mật có đang tắt REST API không."
            )
        siteseo = self._siteseo_abilities()
        me = self._json(self._request("GET", "/wp/v2/users/me", params={"context": "edit"}))
        if not isinstance(me, dict):  # LC-T044-1: dữ liệu sai kiểu thì báo lỗi, không vỡ trang
            raise WordPressError(_BAD_DATA.format(what="tài khoản"))
        capabilities = me.get("capabilities")
        if not isinstance(capabilities, dict):
            capabilities = {}
        roles = me.get("roles")
        site_url = next(
            (v for v in (root.get("home"), root.get("url")) if isinstance(v, str) and v),
            self.base_url,
        )
        return ConnectionInfo(
            site_name=_plain(root.get("name", "")),
            site_url=site_url,
            user_name=_plain(me.get("name", "")),
            roles=tuple(r for r in roles if isinstance(r, str)) if isinstance(roles, list) else (),
            can_edit_posts=capabilities.get("edit_posts") is True,
            can_publish_posts=capabilities.get("publish_posts") is True,
            can_upload_files=capabilities.get("upload_files") is True,
            siteseo_writable=siteseo,
            can_unfiltered_html=capabilities.get("unfiltered_html") is True,
            timezone_string=_site_timezone(root.get("timezone_string")),
            gmt_offset=_site_offset(root.get("gmt_offset")),
        )

    def list_categories(self) -> list[Term]:
        return self._list_terms("/wp/v2/categories")

    def list_tags(self) -> list[Term]:
        return self._list_terms("/wp/v2/tags")

    def _list_terms(self, path: str) -> list[Term]:
        params = {
            "per_page": PER_PAGE,
            "orderby": "name",
            "order": "asc",
            "hide_empty": "false",
            "_fields": "id,name,slug,count,parent",
        }
        terms: list[Term] = []
        for item in self._get_all_pages(path, params):
            # LC-T044-1: mục sai kiểu (không phải dict, id lạ) bị bỏ, không làm vỡ cả danh sách.
            if not isinstance(item, dict) or type(item.get("id")) is not int or item["id"] < 0:
                continue
            slug = item.get("slug")
            terms.append(
                Term(
                    id=item["id"],
                    name=_plain(item.get("name", "")),
                    slug=slug if isinstance(slug, str) else "",
                    count=_non_negative(item.get("count")),
                    parent=_non_negative(item.get("parent")),
                )
            )
        return terms

    def list_published(self) -> PublishedList:
        """Mọi bài và trang ĐÃ ĐĂNG (``publish``) trên site, kèm meta SiteSEO nếu site mở.

        Chỉ đọc (``GET``), đúng hai đường cố định ``/wp/v2/posts`` và ``/wp/v2/pages``. Dữ liệu
        trả về là chưa tin cậy nên được lọc lại phía app (T-037, T-033 mục 4.1):
        - chỉ giữ mục có ``status == "publish"`` (bỏ ``future``, ``draft``, ``private``…);
        - ``link`` phải là ``https://`` và đúng tên máy (và cổng) của ``WORDPRESS_URL``;
        - tiêu đề và meta bỏ thẻ, gộp khoảng trắng, cắt theo giới hạn độ dài;
        - mục sai khuôn (thiếu id, link lạ…) bị bỏ, không làm hỏng cả danh sách.
        Meta SiteSEO không có trong kết quả thì để rỗng. Site có quá ``MAX_PAGES`` trang kết
        quả thì phần thừa không được đọc và ``truncated`` của kết quả là ``True``.
        """
        params = {
            "status": "publish",
            "per_page": PER_PAGE,
            "orderby": "id",
            "order": "asc",
            "_fields": _PUBLISHED_FIELDS,
        }
        items = PublishedList()
        seen: set[tuple[str, int]] = set()
        for kind, path in (("post", "/wp/v2/posts"), ("page", "/wp/v2/pages")):
            raws, truncated = self._get_pages_checked(path, params)
            items.truncated = items.truncated or truncated
            for raw in raws:
                item = _published_from(raw, kind, self.base_url)
                if item is None or (item.type, item.id) in seen:
                    continue
                seen.add((item.type, item.id))
                items.append(item)
        return items

    def _get_pages_checked(
        self, path: str, params: dict[str, Any]
    ) -> tuple[list[dict[str, Any]], bool]:
        """Đọc mọi trang kết quả (tối đa ``MAX_PAGES``), kèm cờ "còn trang chưa đọc".

        - Header ``X-WP-TotalPages`` đọc được (số nguyên ≥ 1): đọc đúng số trang đó.
        - Header thiếu hoặc sai (proxy/plugin bỏ header, SL-T037-3): trang trả đủ ``PER_PAGE``
          mục thì đọc tiếp, dừng ở trang thiếu mục, trang rỗng, hoặc khi WordPress báo "quá số
          trang" (``rest_post_invalid_page_number``).
        - Máy chủ bỏ qua tham số ``page`` (bộ đệm trang, CDN: trả lại y hệt trang trước, **kể
          cả khi header đúng**, SL-T042-1) thì dừng và coi là chưa đủ.
        - Tới ``MAX_PAGES`` mà vẫn còn trang: cờ là ``True`` (danh sách chưa đủ).
        """
        items: list[dict[str, Any]] = []
        previous: list[Any] | None = None
        previous_total: int | None = None
        page = 1
        while True:
            try:
                response = self._request("GET", path, params={**params, "page": page})
            except WordPressError as exc:
                if (
                    page > 1
                    and previous_total is None
                    and exc.status_code == 400
                    and exc.code == _PAGE_OUT_OF_RANGE
                ):
                    return items, False  # header thiếu và trang trước vừa đủ PER_PAGE mục
                raise
            data = self._json(response)
            if not isinstance(data, list):
                raise WordPressError("WordPress trả về dữ liệu không đúng dạng danh sách.")
            total_pages = _total_pages(response.headers.get("X-WP-TotalPages"))
            if data and data == previous:
                return items, True  # máy chủ không phân trang: không biết còn bao nhiêu
            items.extend(data)
            if not data:
                return items, False
            if total_pages is None:
                if len(data) < PER_PAGE:
                    return items, False
            elif page >= total_pages:
                return items, False
            if page >= MAX_PAGES:
                return items, True
            previous, previous_total = data, total_pages
            page += 1

    def _get_all_pages(self, path: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        """Như ``_get_pages_checked`` nhưng bỏ cờ (chuyên mục, thẻ)."""
        return self._get_pages_checked(path, params)[0]

    # ------------------------------------------------------------------ ghi

    def create_draft(
        self,
        title: str,
        content: str,
        *,
        categories: list[int] | tuple[int, ...] = (),
        tags: list[int] | tuple[int, ...] = (),
        excerpt: str = "",
        slug: str = "",
        featured_media: int | None = None,
    ) -> Post:
        """Tạo bài ở trạng thái NHÁP (draft). Không bao giờ đăng công khai.

        Nội dung và đoạn trích luôn qua bộ lọc HTML (security.md 2.3); tiêu đề bỏ mọi thẻ. Không
        còn "[" trần ở cả ba (T-061): WordPress không chạy được shortcode, kể cả trong câu trả lời
        của chính lệnh này (``_fields`` cố định, không có ``content``).
        """
        title = strip_tags(title).strip()
        if not title:
            raise WordPressError("Tiêu đề bài viết không được để trống.")
        payload: dict[str, Any] = {
            "status": "draft",
            "title": escape_shortcodes(title),
            "content": sanitize_html(content),
        }
        if categories:
            payload["categories"] = list(categories)
        if tags:
            payload["tags"] = list(tags)
        if excerpt:
            payload["excerpt"] = sanitize_html(excerpt)
        if slug:
            payload["slug"] = slug
        if featured_media:
            payload["featured_media"] = featured_media
        data = self._json(
            self._request("POST", "/wp/v2/posts", json=payload, params={"_fields": _POST_FIELDS})
        )
        post = self._post_from(data)
        if post.status == "draft":  # chỉ ghi nhận bài site xác nhận là nháp (R3, T-042)
            self._created_post_ids.add(post.id)
        return post

    def set_seo_meta(
        self,
        post_id: int,
        *,
        title: str = "",
        description: str = "",
        focus_keyword: str = "",
    ) -> SeoWriteResult:
        """Ghi tiêu đề, mô tả, từ khóa chính SEO vào SiteSEO của bài NHÁP app vừa tạo (T-042).

        An toàn (Lá Chắn soát kỹ nhất):
        - **chỉ** bài trong ``_created_post_ids`` (do ``create_draft`` của client này tạo), và
          site phải xác nhận bài **còn là nháp** ngay trước khi ghi; bài đã đăng thì từ chối;
        - chỉ gửi trường có chữ, **không bao giờ gửi ``null``** (với SiteSEO, ``null`` là xóa);
          không gửi ``status``, canonical, robots;
        - chữ có thẻ HTML, mã ký tự HTML (``&#37;``, ``&lt;``…) hay ``%%`` bị chặn trước khi gửi;
        - chỉ đi qua đường trong ``ALLOWED_ROUTES``; câu lỗi cố định, không chép lời máy chủ.

        Đường ghi: Abilities của SiteSEO (chính); không có thì meta qua ``wp/v2/posts`` (dự
        phòng, chỉ tiêu đề và mô tả). Tùy chọn ``write_seo`` tắt, hoặc site chưa cho ghi: trả
        ``SeoWriteResult(written=False)`` để app quay về chép tay, không ném lỗi.
        Ném ``WordPressError`` khi: bài không do app tạo, bài không còn là nháp, chữ không hợp
        lệ, hoặc không kiểm được bài trên site.
        """
        if type(post_id) is not int or post_id not in self._created_post_ids:
            raise WordPressError(_SEO_NOT_OWN)
        if not self.write_seo:
            return SeoWriteResult(False, reason="disabled", message=_SEO_DISABLED)
        values = {
            "title": _seo_text("Tiêu đề SEO", title, MAX_SEO_TITLE_CHARS),
            "description": _seo_text("Mô tả SEO", description, MAX_SEO_DESC_CHARS),
            "focus_keyword": _seo_text("Từ khóa chính", focus_keyword, MAX_SEO_KEYWORD_CHARS),
        }
        fields = {name: value for name, value in values.items() if value}
        if not fields:
            raise WordPressError(_SEO_EMPTY)
        # Dò đường TRƯỚC, kiểm còn nháp NGAY TRƯỚC lệnh ghi: khe "kiểm rồi ghi" ngắn nhất.
        abilities = self._siteseo_abilities()
        draft = self._own_draft(post_id)
        if abilities:
            return self._seo_via_abilities(post_id, fields)
        return self._seo_via_meta(post_id, fields, draft)

    def _own_draft(self, post_id: int, *, failed: str = "") -> dict[str, Any]:
        """Hỏi site bài ``post_id`` còn là nháp không (chỉ đọc). Không phải nháp: từ chối.

        ``failed``: câu báo khi không hỏi được (mặc định câu của ghi SEO).
        """
        try:
            data = self._json(
                self._request(
                    "GET",
                    f"/wp/v2/posts/{post_id}",
                    params={"context": "edit", "_fields": _POST_META_FIELDS},
                )
            )
        except WordPressError as exc:
            code = f" (mã {exc.status_code})" if exc.status_code else ""
            raise WordPressError(
                (failed or _SEO_CHECK_FAILED).format(code=code), status_code=exc.status_code
            ) from None
        if not _is_own_draft_answer(data, post_id):
            # Bài đã bị đăng/xóa ngoài app: thôi coi là "bài app được sửa" (cả ảnh đại diện).
            self._created_post_ids.discard(post_id)
            raise WordPressError(_SEO_NOT_DRAFT)
        return data

    def _siteseo_abilities(self) -> bool | None:
        """Abilities của SiteSEO đã bật và tài khoản gọi được chưa (chỉ ``GET``, có nhớ kết quả).

        ``True``: có ability ghi SEO; ``False``: chưa bật / không đủ quyền (400, 401, 403, 404);
        ``None``: không dò được (lỗi mạng, máy chủ); lần sau dò lại.
        """
        if self._siteseo_ok is not None:
            return self._siteseo_ok
        try:
            data = self._json(self._request("GET", SITESEO_ABILITY_PATH))
        except WordPressError as exc:
            if exc.status_code in (400, 401, 403, 404):
                self._siteseo_ok = False
                return False
            return None
        self._siteseo_ok = isinstance(data, dict) and data.get("name") == SITESEO_ABILITY
        return self._siteseo_ok

    def _seo_via_abilities(self, post_id: int, fields: dict[str, str]) -> SeoWriteResult:
        payload = {
            "input": {
                "postId": post_id,
                **{_ABILITY_FIELDS[name]: value for name, value in fields.items()},
            }
        }
        try:
            data = self._json(self._request("POST", SITESEO_ABILITY_RUN_PATH, json=payload))
        except WordPressError as exc:
            return _seo_error("abilities", exc.status_code)
        if not _ability_confirms(data, fields):
            return _seo_error("abilities", None)
        message = _SEO_WRITTEN_CHANGED if _siteseo_lost_text(data, fields) else _SEO_WRITTEN
        return SeoWriteResult(True, "abilities", tuple(fields), message=message)

    def _seo_via_meta(
        self, post_id: int, fields: dict[str, str], draft: dict[str, Any]
    ) -> SeoWriteResult:
        """Đường dự phòng: ghi 2 khóa meta site đã mở trong REST (chỉ tiêu đề, mô tả)."""
        meta = draft.get("meta")
        send = {_META_FIELDS[name]: value for name, value in fields.items() if name in _META_FIELDS}
        if not isinstance(meta, dict) or not all(key in meta for key in _META_FIELDS.values()):
            return SeoWriteResult(False, reason="unavailable", message=_SEO_UNAVAILABLE)
        if not send:  # chỉ có từ khóa chính: đường này không ghi được
            return SeoWriteResult(False, reason="unavailable", message=_SEO_UNAVAILABLE)
        try:
            data = self._json(
                self._request(
                    "POST",
                    f"/wp/v2/posts/{post_id}",
                    json={"meta": send},
                    params={"_fields": _POST_META_FIELDS},
                )
            )
        except WordPressError as exc:
            if exc.status_code in (400, 401, 403):  # site không cho ghi khóa meta này
                return SeoWriteResult(
                    False, "meta", reason="unavailable", message=_SEO_UNAVAILABLE
                )
            return _seo_error("meta", exc.status_code)
        if not _is_own_draft_answer(data, post_id):
            # Câu trả lời của lệnh ghi nói về bài khác, hay bài không còn nháp: bất thường.
            return _seo_error("meta", None)
        saved = data.get("meta")
        if not isinstance(saved, dict) or any(saved.get(k) != v for k, v in send.items()):
            # Máy chủ trả 200 nhưng không lưu (đoạn code mở khóa meta không cho ghi).
            return SeoWriteResult(False, "meta", reason="unavailable", message=_SEO_UNAVAILABLE)
        written = tuple(name for name in fields if name in _META_FIELDS)
        message = _SEO_WRITTEN if len(written) == len(fields) else _SEO_WRITTEN_NO_KEYWORD
        return SeoWriteResult(True, "meta", written, message=message)

    def set_featured_image(self, post_id: int, media_id: int) -> Post:
        """Đặt ảnh đại diện, CHỈ cho bài nháp mà client này vừa tạo bằng ``create_draft``.

        Bài đã có sẵn trên website không bao giờ bị sửa (R3, security.md 2.2). Như
        ``set_seo_meta``, hỏi lại site bài còn là nháp ngay trước khi ghi (SL-T042-5).
        """
        if type(post_id) is not int or post_id not in self._created_post_ids:
            raise WordPressError(
                "Chỉ được đặt ảnh đại diện cho bài nháp app vừa tạo, không sửa bài đã có trên "
                "website."
            )
        if _positive_id(media_id) is None:
            raise WordPressError("Mã ảnh đại diện không hợp lệ.")
        self._own_draft(post_id, failed=_IMAGE_CHECK_FAILED)
        data = self._json(
            self._request(
                "POST",
                f"/wp/v2/posts/{post_id}",
                json={"featured_media": media_id},
                params={"_fields": _POST_FIELDS},
            )
        )
        if not _is_own_draft_answer(data, post_id):
            # SL-T042-11: câu trả lời nói về bài khác, hay bài không còn nháp: bất thường.
            raise WordPressError(_IMAGE_ODD_ANSWER)
        return self._post_from(data)

    # ------------------------------------------------------- hẹn giờ, đăng (T-099)

    def release_draft(
        self, post_id: int, *, mode: str, when_utc: datetime | None = None
    ) -> Released:
        """Chuyển bài NHÁP client này vừa tạo sang hẹn giờ (``mode="future"``, giờ ``when_utc``)
        hoặc đăng công khai ngay (``mode="publish"``). Đường **duy nhất** tới ``future``/``publish``
        (thiết kế T-094 mục 3.3; Lá Chắn LC-T094-22 → -25, soát kỹ nhất).

        Chỉ gọi từ bước Xuất bản, sau màn hình xác nhận (mã băm) và sau khi tải ảnh, tạo nháp, ảnh
        đại diện, ghi SEO đã xong trong **cùng** lần bấm (T-102). Thứ tự:

        1. **Giành bài một bước** (LC-T099-1): ``post_id`` phải thuộc ``_created_post_ids`` của
           **chính đối tượng client này** (client tạo mới mỗi lần bấm: bài tạo ở lần gửi khác, mã
           bài đọc từ Sheet hay ``post_statuses`` không bao giờ vào được), và được **bỏ khỏi tập
           ngay trong bước kiểm** (``set.remove``): hai luồng dùng chung client cùng gọi cho một
           bài thì chỉ một luồng đi tiếp, luồng kia bị từ chối, 0 request. Bị chặn ở bước 1–2
           (chưa gửi lệnh chuyển) thì trả mã lại: bài vẫn là nháp của client.
        2. Kiểm trước khi gửi gì (sai thì ``ReleaseError``, 0 request): ``mode`` đúng chữ; Đăng
           ngay không kèm giờ; Hẹn giờ thì ``when_utc`` là ``datetime`` có múi giờ. Rồi hỏi lại
           website bài **còn là nháp** (``GET``, chỉ đọc); không còn: từ chối, **không** trả mã.
           Giờ máy chủ lấy từ header ``Date`` của **chính** câu trả lời này (thiếu, sai dạng →
           chặn; không lấy đồng hồ máy thay); đồng hồ máy lệch quá 2 phút → chặn; giờ hẹn ≥ giờ
           máy chủ + 10 phút, ≤ 365 ngày (``release_time_problem``).
        3. Gửi **một** lệnh ``POST /wp/v2/posts/<mã>`` thân đúng ``{"status": "future",
           "date_gmt": "YYYY-MM-DDTHH:MM:SS"}`` hoặc ``{"status": "publish"}``, mang dấu
           ``_RELEASE`` (``_is_release_request``). Từ đây mã bài không bao giờ được trả lại: không
           lệnh nào của client sửa tiếp bài này, kể cả khi lỗi.
        4. Kiểm câu trả lời: đúng mã bài, đúng trạng thái; hẹn giờ thì ``date_gmt`` trả về đúng
           chuỗi đã gửi. Hẹn giờ mà website đăng ngay: ``ReleaseError(went_public=True)`` câu báo
           khẩn. Từ chối 4xx: bài vẫn là nháp. Lỗi không rõ (hết giờ, mất mạng, 3xx, 5xx, câu trả
           lời sai): ``ReleaseError(unsure=True)``. Không bao giờ tự gửi lại, không gửi lệnh nào
           khác vào bài.
        """
        # Nhập muộn như ``_seo_text``: module giờ hẹn thuộc gói publish, client không cần lúc nạp.
        from seo_app.publish.schedule import ScheduleError, date_gmt_text, release_time_problem

        if type(post_id) is not int:
            raise ReleaseError(_RELEASE_NOT_OWN)
        try:
            # Kiểm và bỏ mã trong MỘT lệnh (LC-T099-1): không có khe giữa «kiểm» và «bỏ» để luồng
            # khác dùng chung client chen vào.
            self._created_post_ids.remove(post_id)
        except KeyError:
            raise ReleaseError(_RELEASE_NOT_OWN) from None
        give_back = True  # chưa gửi lệnh chuyển: bị chặn thì trả mã lại cho client
        try:
            if type(mode) is not str or mode not in RELEASE_MODES:
                raise ReleaseError(_RELEASE_BAD_MODE)
            fail = {"post_id": post_id, "edit_link": self.edit_link(post_id)}
            stamp = ""
            if mode == "publish" and when_utc is not None:
                raise ReleaseError(_RELEASE_NOW_WITH_TIME, **fail)
            if mode == "future":
                try:
                    stamp = date_gmt_text(when_utc)  # type: ignore[arg-type]
                except ScheduleError:
                    raise ReleaseError(_RELEASE_BAD_TIME, **fail) from None
            payload = {"status": "future", "date_gmt": stamp} if stamp else {"status": "publish"}
            path = f"/wp/v2/posts/{post_id}"
            options = {"json": payload, "params": {"_fields": _RELEASE_FIELDS}}
            if not is_allowed_route("POST", path) or not _is_plain_request(
                "POST", path, options, self._session, release=_RELEASE
            ):
                raise ReleaseError(_ROUTE_BLOCKED, **fail)  # chưa gửi gì, kể cả lệnh kiểm nháp

            still_draft, server_now = self._release_check(post_id, fail)
            if not still_draft:
                # Bài đã bị đăng, hẹn giờ, chuyển hay xóa ngoài app: không trả mã (thôi coi là
                # bài app được sửa, cả ảnh đại diện, SEO).
                give_back = False
                raise ReleaseError(_RELEASE_NOT_DRAFT, **fail)
            try:
                problem = release_time_problem(
                    mode, when_utc, server_now=server_now, local_now=_utc_now()
                )
            except ScheduleError:
                problem = _RELEASE_BAD_TIME
            if problem:
                raise ReleaseError(problem, **fail)
            give_back = False  # sắp gửi lệnh chuyển: mã bài không bao giờ trả lại nữa
        finally:
            if give_back:
                self._created_post_ids.add(post_id)

        action, done = _RELEASE_WORDS[mode]
        try:
            data = self._json(self._request("POST", path, **options, release=_RELEASE))
        except WordPressError as exc:
            status = exc.status_code
            if status is not None and 400 <= status < 500:
                # Lời từ chối rõ ràng (thiếu quyền ``publish_posts``, giờ sai…): chưa chuyển.
                raise ReleaseError(
                    str(exc).rstrip() + _RELEASE_STILL_DRAFT,
                    status_code=status,
                    code=exc.code,
                    **fail,
                ) from None
            code = f" (mã {status})" if status else ""
            raise ReleaseError(
                _RELEASE_UNSURE.format(action=action, code=code, post_id=post_id, done=done),
                unsure=True,
                status_code=status,
                code=exc.code,
                **fail,
            ) from None
        except Exception as exc:  # lỗi lạ giữa lúc gửi: lệnh có thể đã chạy
            raise ReleaseError(
                _RELEASE_UNSURE.format(action=action, code="", post_id=post_id, done=done),
                unsure=True,
                **fail,
            ) from exc
        return self._released_from(data, post_id, mode, stamp, fail)

    def _release_check(
        self, post_id: int, fail: dict[str, Any]
    ) -> tuple[bool, datetime | None]:
        """Bước 2 của ``release_draft``: hỏi website bài còn là nháp (chỉ đọc). Trả (còn nháp
        không, giờ máy chủ đọc từ header ``Date`` của chính câu trả lời này; ``None`` khi thiếu,
        sai dạng). Không hỏi được: ``ReleaseError``. Không đụng ``_created_post_ids``: người gọi
        đã giành mã bài và tự quyết trả lại hay không."""
        from seo_app.publish.schedule import parse_server_date

        try:
            response = self._request(
                "GET",
                f"/wp/v2/posts/{post_id}",
                params={"context": "edit", "_fields": _RELEASE_CHECK_FIELDS},
            )
            data = self._json(response)
        except WordPressError as exc:
            code = f" (mã {exc.status_code})" if exc.status_code else ""
            raise ReleaseError(
                _RELEASE_CHECK_FAILED.format(code=code), status_code=exc.status_code, **fail
            ) from None
        except Exception as exc:  # lỗi lạ ở lệnh đọc: lệnh chuyển chưa gửi, bài vẫn là nháp
            raise ReleaseError(_RELEASE_CHECK_FAILED.format(code=""), **fail) from exc
        if not _is_own_draft_answer(data, post_id):
            return False, None
        return True, parse_server_date(response.headers.get("Date"))

    def _released_from(
        self, data: object, post_id: int, mode: str, stamp: str, fail: dict[str, Any]
    ) -> Released:
        """Bước 4 của ``release_draft``: kiểm câu trả lời của lệnh chuyển (LC-T094-25)."""
        action, done = _RELEASE_WORDS[mode]
        odd = ReleaseError(
            _RELEASE_ODD_ANSWER.format(action=action, post_id=post_id, done=done),
            unsure=True,
            **fail,
        )
        if not isinstance(data, dict) or _positive_id(data.get("id")) != post_id:
            raise odd
        status = data.get("status")
        if type(status) is not str:
            raise odd
        if mode == "future" and status == "publish":
            raise ReleaseError(
                _RELEASE_WENT_PUBLIC.format(post_id=post_id), went_public=True, **fail
            )
        if status != mode:
            raise odd
        date_gmt = data.get("date_gmt")
        if mode == "future" and (type(date_gmt) is not str or date_gmt != stamp):
            raise ReleaseError(_RELEASE_WRONG_TIME.format(post_id=post_id), unsure=True, **fail)
        link = data.get("link")
        return Released(
            post_id=post_id,
            status=status,
            date_gmt=stamp or (date_gmt if _is_date_gmt(date_gmt) else ""),
            link=link if is_site_link(link, self.base_url) else "",
            edit_link=self.edit_link(post_id),
        )

    def post_statuses(self, post_ids: Iterable[int]) -> dict[int, PostState]:
        """Trạng thái hiện tại của các bài ``post_ids`` trên website: **chỉ đọc** (T-099; thiết kế
        T-094 mục 1.7, 3.3; LC-T094-26). Dùng cho bước «Cập nhật trạng thái từ website».

        - ``post_ids``: số nguyên dương thật (không ``bool``, chữ, số thực), tối đa
          ``MAX_STATUS_LOOKUP`` mã; sai thì ``WordPressError``, chưa hỏi website. Mã bài thường
          đọc từ Google Sheets (chưa tin cậy): kết quả chỉ để ghi ô trạng thái, **không** làm
          mã nào thành «bài app được sửa» (``_created_post_ids`` không đổi).
        - Mỗi lệnh ``GET /wp/v2/posts`` hỏi tối đa ``MAX_STATUS_IDS`` mã (``include``), ``status``
          và ``_fields`` là hằng (không ``content``, ``excerpt``), ``context=edit``.
        - Kết quả: mã → ``PostState``. Chỉ giữ mục đúng mã đã hỏi, trạng thái thuộc
          ``POST_STATUSES``; mục sai khuôn bị bỏ. Bài không có trong kết quả: đã xóa, vào thùng
          rác hay tài khoản không xem được.
        """
        if isinstance(post_ids, str | bytes | dict) or not isinstance(post_ids, Iterable):
            raise WordPressError(_STATUS_BAD_IDS)
        ids = list(islice(post_ids, MAX_STATUS_LOOKUP + 1))
        if len(ids) > MAX_STATUS_LOOKUP or any(_positive_id(value) is None for value in ids):
            raise WordPressError(_STATUS_BAD_IDS)
        wanted = sorted(set(ids))
        states: dict[int, PostState] = {}
        for start in range(0, len(wanted), MAX_STATUS_IDS):
            chunk = wanted[start : start + MAX_STATUS_IDS]
            data = self._json(
                self._request(
                    "GET",
                    "/wp/v2/posts",
                    params={
                        "include": ",".join(str(value) for value in chunk),
                        "status": POST_STATUS_FILTER,
                        "context": "edit",
                        "per_page": MAX_STATUS_IDS,
                        "_fields": _STATUS_FIELDS,
                    },
                )
            )
            if not isinstance(data, list):
                raise WordPressError("WordPress trả về dữ liệu không đúng dạng danh sách.")
            asked = set(chunk)
            for raw in data:
                state = self._state_from(raw, asked)
                if state is not None and state.id not in states:
                    states[state.id] = state
        return states

    def _state_from(self, raw: object, asked: set[int]) -> PostState | None:
        """Một mục của ``post_statuses`` → ``PostState``; ``None`` nếu sai khuôn hay không phải
        mã đã hỏi (website trả thêm bài khác: bỏ)."""
        if not isinstance(raw, dict):
            return None
        post_id = _positive_id(raw.get("id"))
        status = raw.get("status")
        if post_id is None or post_id not in asked:
            return None
        if type(status) is not str or status not in POST_STATUSES:
            return None
        date_gmt, modified, link = raw.get("date_gmt"), raw.get("modified_gmt"), raw.get("link")
        return PostState(
            id=post_id,
            status=status,
            date_gmt=date_gmt if _is_date_gmt(date_gmt) else "",
            modified_gmt=modified if _is_date_gmt(modified) else "",
            link=link if is_site_link(link, self.base_url) else "",
        )

    def upload_media(
        self,
        data: bytes,
        filename: str,
        *,
        alt_text: str = "",
        title: str = "",
        caption: str = "",
    ) -> Media:
        """Tải ảnh lên thư viện Media. Tên file được chuyển thành không dấu.

        - Website phải trả ``201 Created`` (LC-T071-1): mã khác có thể là ảnh **đã có** (plugin
          trả lại ảnh trùng), ghi alt vào đó là sửa ảnh có sẵn (R3). Khi đó báo lỗi, không ghi gì.
        - Sau khi tải, **luôn** ghi đè cả ba ô alt, tiêu đề, chú thích (LC-T061-3): ô trống cũng
          gửi chuỗi rỗng, tiêu đề trống thì lấy tên file đã làm sạch (như WordPress tự đặt). Nếu
          không, WordPress lấy ba ô từ chữ nằm trong file người dùng chọn (EXIF, IPTC, XMP).
        - Cả ba không còn "[" trần (``escape_shortcodes``, T-061): WordPress chèn alt vào
          ``<img>`` khi dựng nội dung trang ảnh (``prepend_attachment``) rồi chạy shortcode.
        - Lệnh tải lỗi mà không phải lời từ chối 4xx rõ ràng (hết giờ, mất kết nối, 3xx, 5xx, câu
          trả lời hỏng kể cả ``201``, lỗi lạ): câu báo thêm ``_MEDIA_MAYBE_UPLOADED`` (ảnh có thể
          đã lên thư viện Media, kiểm Media → Thư viện trước khi tải lại; SL-T085-3).
        - Ảnh đã lên mà lệnh ghi đè hỏng (kể cả lỗi lạ, LC-T085-1), hay câu trả lời không nói
          đúng mã ảnh vừa tạo: báo câu cố định ``_MEDIA_NOT_DESCRIBED`` (ảnh đang ở thư viện
          Media, mã ảnh, vào Media → Thư viện kiểm hoặc xóa), không dùng địa chỉ, alt của ảnh
          khác (LC-T060-3, SL-T060-1).
        """
        suffix = Path(filename).suffix.lower()
        content_type = IMAGE_TYPES.get(suffix)
        if content_type is None:
            allowed = ", ".join(sorted(IMAGE_TYPES))
            raise WordPressError(f"File '{filename}' không phải ảnh được hỗ trợ ({allowed}).")
        if not data:
            raise WordPressError(f"File '{filename}' rỗng.")
        stem = slugify(Path(filename).stem) or "anh"
        safe_name = f"{stem}{suffix}"
        # Kiểm TRƯỚC khi tải: ảnh đã lên mà không ghi đè được thì chữ trong file ở lại website.
        fields = {"alt_text": alt_text or "", "title": title or stem, "caption": caption or ""}
        if not all(isinstance(value, str) for value in fields.values()):
            raise WordPressError(
                "Alt, tiêu đề, chú thích của ảnh phải là chữ. Chưa gửi gì lên website."
            )

        try:
            media_id, _ = self._post_media(data, safe_name, content_type, new_only=True)
        except WordPressError as exc:
            status = exc.status_code
            if status is not None and 400 <= status < 500:
                raise  # lời từ chối 4xx rõ ràng: ảnh chưa lên
            # Hết giờ, mất kết nối, 3xx, 5xx, câu trả lời hỏng (kể cả 201): lệnh có thể đã chạy
            # xong trên website (SL-T085-3, như ``maybe_uploaded`` của gửi nháp kèm ảnh).
            raise WordPressError(
                str(exc).rstrip() + _MEDIA_MAYBE_UPLOADED, status_code=status, code=exc.code
            ) from None
        except Exception as exc:
            raise WordPressError(
                _MEDIA_UPLOAD_UNEXPECTED.format(kind=type(exc).__name__) + _MEDIA_MAYBE_UPLOADED
            ) from exc

        # Từ đây ảnh đã ở thư viện Media: lỗi nào cũng phải nói rõ điều đó (mã ảnh đã kiểm),
        # kể cả lỗi lạ (LC-T085-1).
        try:
            updated = self._json(
                self._request(
                    "POST",
                    f"/wp/v2/media/{media_id}",
                    json={key: escape_shortcodes(value) for key, value in fields.items()},
                    params={"_fields": _MEDIA_FIELDS},
                )
            )
        except WordPressError as exc:
            code = f" (mã {exc.status_code})" if exc.status_code else ""
            raise WordPressError(
                _MEDIA_NOT_DESCRIBED.format(media_id=media_id, code=code),
                status_code=exc.status_code,
                code=exc.code,
            ) from None
        except Exception as exc:
            raise WordPressError(_MEDIA_NOT_DESCRIBED.format(media_id=media_id, code="")) from exc
        if not isinstance(updated, dict) or _positive_id(updated.get("id")) != media_id:
            raise WordPressError(_MEDIA_NOT_DESCRIBED.format(media_id=media_id, code=""))

        source_url = updated.get("source_url")
        saved_alt = updated.get("alt_text")
        return Media(
            id=media_id,
            source_url=source_url if isinstance(source_url, str) else "",
            alt_text=saved_alt if isinstance(saved_alt, str) else fields["alt_text"],
        )

    def upload_media_file(self, path: Path, **kwargs: Any) -> Media:
        return self.upload_media(path.read_bytes(), path.name, **kwargs)

    def _post_media(
        self, data: bytes, file_name: str, content_type: str, *, new_only: bool = False
    ) -> tuple[int, dict[str, Any]]:
        """Gửi đúng ``data`` (không sửa byte nào) lên thư viện Media; trả (mã ảnh, câu trả lời).

        ``file_name`` phải là tên đã làm sạch (chữ thường không dấu, ``-``, đuôi ảnh).
        ``new_only``: chỉ nhận câu trả lời ``201 Created`` (website xác nhận vừa tạo mục mới;
        WordPress lõi luôn trả 201). Mã khác có thể là mục đã có sẵn trên website (plugin trả lại
        ảnh trùng byte): ghi alt cho mã đó là sửa ảnh có sẵn (R3, LC-T054-5).
        """
        response = self._request(
            "POST",
            "/wp/v2/media",
            data=data,
            headers={
                "Content-Type": content_type,
                "Content-Disposition": f'attachment; filename="{file_name}"',
            },
            params={"_fields": _MEDIA_FIELDS},
        )
        if new_only and response.status_code != 201:
            raise WordPressError(_MEDIA_NOT_CREATED)
        media = self._json(response)
        # SL-T042-4, LC-T044-1: chỉ nhận id là số nguyên dương thật (``True``, ``"7"``, ``7.9``
        # không được thành ảnh 1 hay ảnh 7 của người khác).
        media_id = _positive_id(media.get("id") if isinstance(media, dict) else None)
        if media_id is None:
            raise WordPressError(_BAD_DATA.format(what="ảnh vừa tải lên"))
        return media_id, media

    # ------------------------------------------------------- gửi nháp kèm ảnh (T-054)

    def create_draft_with_images(
        self,
        title: str,
        parts: Sequence[str | DraftImage],
        *,
        categories: list[int] | tuple[int, ...] = (),
        tags: list[int] | tuple[int, ...] = (),
        excerpt: str = "",
        slug: str = "",
    ) -> DraftWithImages:
        """Gửi nháp kèm ảnh: tải ảnh lên thư viện Media, chèn ``<figure>``, tạo bài NHÁP, đặt
        ảnh đại diện (T-054, thiết kế T-046 mục 6).

        **Chỉ gọi khi người dùng bấm «Gửi nháp»**: ảnh xem được công khai qua đường dẫn ngay khi
        tải lên, kể cả khi bài vẫn là nháp (ảnh thật còn GPS, quyết định 5A). Không hàm nào khác
        tải ảnh của bài.

        ``parts``: nội dung bài theo thứ tự. Chuỗi là HTML do code dựng (cả bài vẫn qua
        ``sanitize_html`` trong ``create_draft``); ``DraftImage`` được thay bằng ``<figure>`` của
        ảnh đó. Cùng một đối tượng ``DraftImage`` xuất hiện nhiều lần thì chỉ tải một lần.

        Thứ tự, đều qua ``ALLOWED_ROUTES``:
        1. Kiểm mọi thứ **trước khi gửi**: tiêu đề, từng ảnh (đúng ``WebImage`` WebP, alt không
           rỗng, thẻ là ``ImageTags`` hợp lệ), tối đa một ảnh đại diện. Sai thì
           ``WordPressError``, chưa có request nào.
        2. Từng ảnh: ``POST /wp/v2/media`` với đúng ``image.data``; website phải trả
           ``201 Created`` với mã ảnh chưa gặp trong lần gửi này (LC-T054-5); rồi
           ``POST /wp/v2/media/<mã>`` ghi alt, tiêu đề, chú thích cho đúng mã đó. Tên file chỉ từ
           ``naming.image_file_name`` (thẻ ``ImageTags``, alt đã duyệt). Địa chỉ ảnh phải là
           ``https://`` trên đúng website (``is_site_link``).
        3. ``create_draft``: bài luôn ``draft``; không bao giờ sửa bài có sẵn.
        4. ``set_featured_image``: chỉ bài nháp vừa tạo, hỏi lại site bài còn nháp (``_own_draft``).
           Lỗi ở bước này không làm mất bài: trả kết quả kèm ``message``.

        Lỗi ở bước 2–3: ``DraftImagesError`` liệt kê ảnh đã lên thư viện (``uploaded``). Phần
        mềm **không xóa** ảnh nào (W2). Lỗi ở chính lệnh tạo nháp mà không phải lời từ chối 4xx
        rõ ràng: ``maybe_draft``, câu báo nói bài nháp có thể đã có (LC-T054-2).
        """
        from seo_app.images.html import ImageHtmlError, figure_html

        if not isinstance(title, str) or not strip_tags(title).strip():
            raise WordPressError(_DRAFT_EMPTY_TITLE)
        if isinstance(parts, str | bytes) or not isinstance(parts, Sequence):
            raise WordPressError(_DRAFT_BAD_PART)
        items = tuple(parts)  # chốt một lần: kiểm và dựng nội dung trên cùng một danh sách
        if not (_is_term_ids(categories) and _is_term_ids(tags)):
            raise WordPressError(_DRAFT_BAD_PART)
        if not isinstance(excerpt, str) or not isinstance(slug, str):
            raise WordPressError(_DRAFT_BAD_PART)
        planned, featured = self._plan_draft_images(items)

        uploaded: list[UploadedImage] = []
        sent: dict[int, UploadedImage] = {}  # id(DraftImage) → ảnh đã tải
        uploading = False  # đang ở lệnh POST /wp/v2/media (ảnh có thể đã lên mà chưa có mã)
        creating = False  # đã tới lệnh tạo nháp (bài có thể đã có dù lệnh báo lỗi)
        try:
            for item in planned:
                uploading = True
                media_id, created = self._post_media(
                    item.source.image.data, item.file_name, _WEBP_TYPE, new_only=True
                )
                if any(image.id == media_id for image in uploaded):
                    # LC-T054-5: một mã cho hai lần tải. Không ghi alt (đè alt ảnh trước, hay ảnh
                    # có sẵn trên website); ảnh vừa gửi có thể đã lên với mã khác.
                    raise WordPressError(_MEDIA_SAME_ID)
                uploading = False
                uploaded.append(
                    UploadedImage(media_id, item.file_name, "", self.edit_link(media_id))
                )
                source_url = self._describe_draft_media(media_id, item, created)
                uploaded[-1] = replace(uploaded[-1], source_url=source_url)
                sent[id(item.source)] = uploaded[-1]
            content = [
                part
                if isinstance(part, str)
                else figure_html(
                    src=sent[id(part)].source_url,
                    alt=part.alt,
                    caption=part.caption,
                    width=part.image.width,
                    height=part.image.height,
                )
                for part in items
            ]
            creating = True
            post = self.create_draft(
                title,
                "\n".join(content),
                categories=categories,
                tags=tags,
                excerpt=excerpt,
                slug=slug,
            )
        except (WordPressError, ImageHtmlError) as exc:
            status = exc.status_code if isinstance(exc, WordPressError) else None
            # Chỉ lời từ chối 4xx là rõ ràng "website không làm". Hết giờ, mất mạng, 5xx, chuyển
            # hướng, câu trả lời sai dạng: lệnh có thể đã chạy xong trên website.
            unsure = status is None or not 400 <= status < 500
            reason = str(exc)
            if creating and not unsure:
                reason = reason.rstrip() + _DRAFT_NOT_CREATED
            raise _draft_images_error(
                reason,
                uploaded,
                maybe_uploaded=uploading and unsure,
                maybe_draft=creating and unsure,
                status=status,
            ) from None
        except Exception as exc:
            # Lỗi lạ (không nên có): vẫn phải báo ảnh nào đã công khai trên website (W2), và
            # không khẳng định "chưa tạo bài nháp" khi lỗi xảy ra ở lệnh tạo nháp.
            reason = _DRAFT_UNEXPECTED.format(kind=type(exc).__name__)
            raise _draft_images_error(
                reason if creating else reason + _DRAFT_NOT_CREATED,
                uploaded,
                maybe_uploaded=uploading,
                maybe_draft=creating,
                status=None,
            ) from exc

        if featured is None:
            return DraftWithImages(post, tuple(uploaded))
        featured_id = sent[id(featured)].id
        try:
            self.set_featured_image(post.id, featured_id)
        except WordPressError as exc:
            return DraftWithImages(
                post, tuple(uploaded), message=_FEATURED_NOT_SET.format(reason=str(exc))
            )
        return DraftWithImages(post, tuple(uploaded), featured_media=featured_id)

    def _plan_draft_images(
        self, parts: tuple[object, ...]
    ) -> tuple[list[_PlannedImage], DraftImage | None]:
        """Kiểm nội dung và ảnh, đặt tên file. Không gửi gì. Trả (ảnh theo thứ tự, ảnh đại diện)."""
        from seo_app.images.html import plain_image_text
        from seo_app.images.naming import image_file_name
        from seo_app.images.tags import ImageTags

        planned: list[_PlannedImage] = []
        seen: set[int] = set()
        names: list[str] = []
        for part in parts:
            if isinstance(part, str):
                continue
            if not isinstance(part, DraftImage):
                raise WordPressError(_DRAFT_BAD_PART)
            if id(part) in seen:
                continue
            seen.add(id(part))
            number = len(planned) + 1
            _check_web_image(part.image, number)
            # Thẻ chỉ từ ``ImageTags`` (LC-T054-4): đúng lớp (không nhận lớp con, chữ, dict), rồi
            # dựng lại để chạy lại bước kiểm danh sách cố định (``replace`` gọi
            # ``__post_init__``), phòng đối tượng bị sửa sau khi tạo (``object.__setattr__``).
            if type(part.tags) is not ImageTags or type(part.featured) is not bool:
                raise WordPressError(_IMAGE_BAD_TAGS.format(n=number))
            try:
                tags = replace(part.tags)
            except (TypeError, ValueError):  # ``TagError`` là ``ValueError``
                raise WordPressError(_IMAGE_BAD_TAGS.format(n=number)) from None
            alt, caption = plain_image_text(part.alt), plain_image_text(part.caption)
            if not alt:
                raise WordPressError(_IMAGE_NO_ALT.format(n=number))
            if len(alt) > MAX_IMAGE_ALT_CHARS or len(caption) > MAX_IMAGE_CAPTION_CHARS:
                raise WordPressError(
                    _IMAGE_TEXT_TOO_LONG.format(
                        n=number, alt=MAX_IMAGE_ALT_CHARS, caption=MAX_IMAGE_CAPTION_CHARS
                    )
                )
            # Tên file chỉ từ thẻ đã chuẩn hóa và alt đã duyệt (Lá Chắn T-049 điều kiện 4).
            file_name = image_file_name(
                category=tags.category,
                area=tags.area,
                project_code=tags.project_code,
                alt=alt,
                ai_generated=tags.is_ai,
                taken=names,
            )
            names.append(file_name)
            planned.append(_PlannedImage(part, file_name, alt, caption, tags.is_ai))
        chosen = [item.source for item in planned if item.source.featured]
        if len(chosen) > 1:
            raise WordPressError(_DRAFT_TWO_FEATURED)
        featured = chosen[0] if chosen else (planned[0].source if planned else None)
        return planned, featured

    def _describe_draft_media(
        self, media_id: int, item: _PlannedImage, created: dict[str, Any]
    ) -> str:
        """Ghi alt, tiêu đề, chú thích cho ảnh ``media_id`` vừa tải; trả địa chỉ file đầy đủ.

        ``alt_text`` là chữ thường (WordPress tự escape khi in ra); tiêu đề và chú thích được
        WordPress hiện như HTML nên phải ``html.escape``. Không gửi ``status``, ``post``.
        Cả ba không còn "[" trần (``escape_shortcodes``, T-061), làm SAU khi ``plain_image_text``
        đã gỡ ký tự vô hình: WordPress chèn ``alt_text`` vào ``<img>`` của nội dung trang ảnh
        (``prepend_attachment``, cả trong câu trả lời REST có ``description``) rồi chạy shortcode.
        """
        title = f"{AI_MEDIA_TITLE_PREFIX}{item.alt}" if item.ai_generated else item.alt
        payload = {
            "alt_text": escape_shortcodes(item.alt),
            "title": escape_shortcodes(html.escape(title, quote=True)),
        }
        if item.caption:
            payload["caption"] = escape_shortcodes(html.escape(item.caption, quote=True))
        updated = self._json(
            self._request(
                "POST", f"/wp/v2/media/{media_id}", json=payload, params={"_fields": _MEDIA_FIELDS}
            )
        )
        if not isinstance(updated, dict) or _positive_id(updated.get("id")) != media_id:
            raise WordPressError(_MEDIA_ODD_ANSWER)
        # File đầy đủ (không phải cỡ nhỏ WordPress tự tạo): địa chỉ lúc tải lên, rồi tới câu
        # trả lời lệnh ghi alt. Phải là https trên đúng website.
        for answer in (created, updated):
            source_url = answer.get("source_url")
            if is_site_link(source_url, self.base_url):
                return source_url
        raise WordPressError(_MEDIA_BAD_URL)

    # ------------------------------------------------------------- nội bộ

    def edit_link(self, post_id: int) -> str:
        return f"{self.base_url}/wp-admin/post.php?post={post_id}&action=edit"

    def _post_from(self, data: object) -> Post:
        """Câu trả lời về một bài -> ``Post``. Sai kiểu (LC-T044-1, SL-T042-4) thì
        ``WordPressError`` câu cố định: không bao giờ đoán id (``int(True)`` là bài 1)."""
        post_id = _positive_id(data.get("id")) if isinstance(data, dict) else None
        if post_id is None:
            raise WordPressError(_BAD_DATA.format(what="bài viết"))
        title = data.get("title")
        if isinstance(title, dict):
            title = title.get("raw") or title.get("rendered") or ""
        status, link = data.get("status"), data.get("link")
        return Post(
            id=post_id,
            status=status if isinstance(status, str) else "",
            title=_plain(title or ""),
            link=link if isinstance(link, str) else "",
            edit_link=self.edit_link(post_id),
            featured_media=_non_negative(data.get("featured_media")),
        )

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        # Dấu hẹn giờ/đăng (chỉ ``release_draft`` có): gỡ khỏi tùy chọn, không tới ``requests``.
        release = kwargs.pop("release", None)
        if not is_allowed_route(method, path) or not _is_plain_request(
            method, path, kwargs, self._session, release=release
        ):
            # Từ chối TRƯỚC KHI gửi: không có request nào đi ra (T-042, LC-T042-1). Câu cố định,
            # không chép đường, tham số hay header bị từ chối.
            raise WordPressError(_ROUTE_BLOCKED)
        url = f"{self.base_url}/wp-json{path}"
        try:
            # Không đi theo chuyển hướng: máy chủ không được đưa lệnh gọi sang đường khác ngoài
            # danh sách (ví dụ chuyển POST sang bài khác hay sang /code-snippets).
            response = self._session.request(
                method, url, timeout=self.timeout, allow_redirects=False, **kwargs
            )
        except requests.exceptions.SSLError as exc:
            raise WordPressError(
                "Lỗi chứng chỉ bảo mật (SSL) của website. Kiểm tra website có mở được bằng "
                "https trên trình duyệt không."
            ) from exc
        except requests.exceptions.Timeout as exc:
            raise WordPressError(
                f"WordPress phản hồi quá lâu (hơn {self.timeout:g} giây). Thử lại sau."
            ) from exc
        except requests.exceptions.ConnectionError as exc:
            raise WordPressError(
                "Không kết nối được tới website trong WORDPRESS_URL. Kiểm tra mạng và "
                "WORDPRESS_URL."
            ) from exc
        except requests.exceptions.RequestException as exc:
            # Lỗi mạng khác (địa chỉ sai dạng, chuyển hướng vòng…): chỉ nêu tên lỗi, không chép
            # thông điệp thô (có thể chứa URL, header).
            raise WordPressError(
                f"Lỗi mạng khi gọi WordPress ({type(exc).__name__}). Kiểm tra WORDPRESS_URL "
                "rồi thử lại."
            ) from exc
        if 300 <= response.status_code < 400:
            raise WordPressError(
                f"WordPress trả lời bằng một lệnh chuyển hướng sang địa chỉ khác (mã "
                f"{response.status_code}); phần mềm không đi theo. Kiểm tra WORDPRESS_URL trong "
                ".env có đúng địa chỉ website không (có hay không có www, có https).",
                status_code=response.status_code,
            )
        if response.status_code >= 400:
            raise self._error_from(response)
        return response

    @staticmethod
    def _json(response: requests.Response) -> Any:
        """Đọc JSON của câu trả lời. Mọi lỗi lúc giải mã (không phải JSON, chữ hỏng, JSON lồng
        quá sâu làm ``RecursionError``…, SL-T085-2) thành câu cố định kèm mã HTTP.

        Mọi chữ website trả (tên site, tên tài khoản, vai trò, tiêu đề bài, tên chuyên mục, địa
        chỉ ảnh…) đi qua đây: ký tự surrogate lẻ được thay ở đây, một chỗ cho cả client
        (``_without_lone_surrogates``, SL-T088-1). Lọc **luôn**, trên dữ liệu đã giải mã: website
        khai hay ``requests`` tự đoán bảng mã khác UTF-8 (UTF-16, UTF-32, UTF-7, cp500…) thì
        surrogate không hiện ra thành mã thoát ``\\uD8..`` trong byte (SL-T091-1)."""
        try:
            return _without_lone_surrogates(response.json())
        except Exception as exc:  # chỉ bọc bước giải mã: lỗi nào cũng là "không đọc được"
            raise WordPressError(
                f"WordPress không trả về dữ liệu JSON đọc được (mã {response.status_code}; có "
                "thể là trang HTML hay dữ liệu hỏng). Thường do sai WORDPRESS_URL, hoặc plugin "
                "bảo mật / tường lửa đang chặn REST API."
            ) from exc

    @staticmethod
    def _error_from(response: requests.Response) -> WordPressError:
        """Câu lỗi CỐ ĐỊNH theo mã HTTP (LC-T042-4): không chép ``message`` của máy chủ (máy chủ
        hay plugin đặt được câu tùy ý lên màn hình) và không chép ``WORDPRESS_URL``. ``code`` của
        WordPress chỉ giữ trong ``WordPressError.code`` (dạng ASCII, để code phân biệt lỗi)."""
        status = response.status_code
        try:
            body = response.json()
        except Exception:  # thân lỗi không đọc được (kể cả lồng quá sâu, LC-T085-1): bỏ qua
            body = {}
        if not isinstance(body, dict):
            body = {}
        raw_code = body.get("code")
        code = raw_code if isinstance(raw_code, str) and _ERROR_CODE.fullmatch(raw_code) else ""

        if status == 401:
            message = (
                "WordPress từ chối đăng nhập (mã 401). Kiểm tra WORDPRESS_USERNAME và "
                "WORDPRESS_APP_PASSWORD trong .env (phải là Application Password, không phải "
                "mật khẩu đăng nhập thường). Nếu đã đúng, có thể hosting đang chặn header "
                "Authorization hoặc plugin bảo mật tắt Application Passwords."
            )
        elif status == 403:
            message = (
                "Tài khoản WordPress không đủ quyền làm việc này, hoặc plugin bảo mật đang "
                "chặn REST API (mã 403)."
            )
        elif status == 404:
            if code == "rest_no_route" or not body:
                message = (
                    "Không tìm thấy REST API của WordPress (đường /wp-json) ở địa chỉ trong "
                    "WORDPRESS_URL (mã 404). Kiểm tra WORDPRESS_URL, và trong WordPress vào Cài "
                    "đặt → Đường dẫn tĩnh, bấm Lưu một lần."
                )
            else:
                message = "Không tìm thấy dữ liệu trên WordPress, có thể đã bị xóa (mã 404)."
        elif status == 413:
            message = "File quá lớn so với giới hạn tải lên của máy chủ WordPress (mã 413)."
        elif status >= 500:
            message = f"Máy chủ WordPress đang gặp lỗi (mã {status}). Thử lại sau."
        else:
            message = f"WordPress báo lỗi (mã {status})."
        return WordPressError(message, status_code=status, code=code)


def _total_pages(value: object) -> int | None:
    """Giá trị header ``X-WP-TotalPages``; ``None`` nếu thiếu, sai dạng hoặc nhỏ hơn 1."""
    if not isinstance(value, str) or not _TOTAL_PAGES_PATTERN.fullmatch(value.strip()):
        return None
    digits = value.strip().lstrip("0")
    if len(digits) > 9:  # số rất lớn: chắc chắn hơn MAX_PAGES (không đổi chuỗi dài ra số)
        return 10**9
    return int(digits) if digits else None  # "0", "000": coi như thiếu


def is_site_link(link: object, base_url: str) -> bool:
    """``link`` là địa chỉ ``https://`` trên đúng tên máy (và cổng) của ``base_url``.

    Từ chối: ``http://``, tên máy khác (kể cả tên miền con), có tên/mật khẩu trong địa chỉ,
    khoảng trắng hoặc ký tự điều khiển, dấu ``" ' < > ` `` để trần, ký tự vô hình (loại Cf),
    cổng sai dạng, quá dài.
    """
    if not isinstance(link, str) or not link or len(link) > MAX_LINK_CHARS:
        return False
    if _CONTROL_CHARS.search(link) or any(ch.isspace() for ch in link) or "\\" in link:
        return False
    # LC-T037-1 (a): WordPress chuẩn luôn mã hóa % các dấu này trong permalink; còn để trần
    # thì link có thể thoát khỏi thuộc tính href khi phiếu sau ghép vào HTML.
    if any(ch in _LINK_UNSAFE for ch in link) or _has_invisible(link):
        return False
    try:
        got, want = urlsplit(link), urlsplit(base_url)
        got_port, want_port = got.port, want.port
    except ValueError:
        return False
    if got.scheme.lower() != "https" or want.scheme.lower() != "https":
        return False
    if got.username is not None or got.password is not None:
        return False
    if not got.hostname or got.hostname != (want.hostname or ""):
        return False
    return (got_port or 443) == (want_port or 443)


def _published_from(raw: object, kind: str, base_url: str) -> PublishedItem | None:
    """Một mục REST -> ``PublishedItem``; ``None`` nếu không phải bài đã đăng hợp lệ."""
    if not isinstance(raw, dict) or raw.get("status") != "publish":
        return None
    link = raw.get("link")
    if not is_site_link(link, base_url):
        return None
    meta = raw.get("meta")
    if not isinstance(meta, dict):
        meta = {}
    slug = raw.get("slug")
    modified = raw.get("modified_gmt")
    try:
        return PublishedItem(
            # Mã quá MAX_ID như mã sai khuôn: PublishedItem từ chối, mục bị bỏ (SL-T091-2).
            id=_positive_id(raw.get("id")),  # type: ignore[arg-type]
            type=kind,
            slug=slug if _matches(_SLUG_PATTERN, slug, MAX_SLUG_CHARS) else "",
            link=link,  # type: ignore[arg-type]
            title=_clean_text(_rendered(raw.get("title")), MAX_TITLE_CHARS),
            meta_title=_clean_text(meta.get(SITESEO_TITLE_KEY), MAX_META_CHARS),
            meta_desc=_clean_text(meta.get(SITESEO_DESC_KEY), MAX_META_CHARS),
            modified_gmt=modified if _matches(_MODIFIED_PATTERN, modified, 19) else "",
        )
    except ValueError:
        return None


def _matches(pattern: re.Pattern[str], value: object, limit: int) -> bool:
    return isinstance(value, str) and len(value) <= limit and bool(pattern.fullmatch(value))


def _rendered(value: object) -> object:
    """Tiêu đề WordPress dạng ``{"rendered": "…"}`` hoặc chuỗi."""
    if isinstance(value, dict):
        return value.get("rendered")
    return value


def _clean_text(value: object, limit: int) -> str:
    """Chữ một dòng từ site: bỏ thẻ, giải mã, bỏ ký tự điều khiển, gộp khoảng trắng, cắt."""
    if isinstance(value, list):  # meta đăng ký kiểu mảng: lấy phần tử đầu
        value = value[0] if value else ""
    if not isinstance(value, str):
        return ""
    text = _CONTROL_CHARS.sub(" ", _plain(value[: limit * 20]))
    text = _drop_invisible(text)  # LC-T037-1 (b), SL-T042-7
    return " ".join(text.split())[:limit].rstrip()


def _seo_text(label: str, raw: object, limit: int) -> str:
    """Chữ SEO sẽ gửi lên SiteSEO: chuẩn hóa như ``normalize_meta``; rỗng nghĩa là không gửi.

    Chặn (ném ``WordPressError``, câu cố định không chép chữ người dùng): không phải chữ, thẻ
    HTML, mã ký tự HTML (LC-T036-3: ``&#37;``, ``&lt;script&gt;``, cả ``&#37`` thiếu ``;``),
    ``%%`` (biến SiteSEO), dạng shortcode WordPress (T-061: ``[tên]``, ``[[tên]]``, ``[/tên]``),
    «<» liền ký tự không phải khoảng trắng ASCII (LC-T061-2: ``<>``, ``<1>``, «<» cuối chữ),
    ký tự điều khiển, quá dài. Xét cả chữ gốc, chữ đã chuẩn hóa (đã gỡ ký tự vô hình, đúng chữ
    sẽ gửi) và dạng NFKC (``＜``, ``％％``, ``［`` toàn khổ).
    """
    # Nhập muộn: seo_app.onpage kéo theo lớp nội dung/AI, không cần khi chỉ dùng client.
    from seo_app.onpage.meta import _ENTITY, has_html, normalize_meta

    if raw is None:
        return ""
    if not isinstance(raw, str):
        raise WordPressError(f"{label} phải là chữ.")
    value = normalize_meta(raw)
    if not value:
        return ""
    folded = unicodedata.normalize("NFKC", value)
    if has_html(raw) or has_html(value) or has_html(folded):
        raise WordPressError(f"{label} có thẻ HTML (dấu < ngay trước chữ). Bỏ thẻ đi rồi gửi lại.")
    patterns = (_ENTITY, _NUMERIC_REF, _LEGACY_ENTITY)
    if any(pattern.search(text) for pattern in patterns for text in (raw, value, folded)):
        raise WordPressError(
            f"{label} có mã ký tự HTML (dạng &…;). Gõ thẳng ký tự (ví dụ «%» thay cho «&#37;») "
            "rồi gửi lại."
        )
    if "%%" in folded:
        raise WordPressError(f"{label} có «%%»: plugin SiteSEO hiểu đó là biến. Bỏ «%%» đi.")
    if any(_has_shortcode(text) for text in (raw, value, folded)):
        raise WordPressError(
            f"{label} có chữ dạng shortcode WordPress («[» liền chữ, có «]» phía sau), website "
            "có thể chạy như lệnh. Bỏ dấu ngoặc vuông hoặc dùng ngoặc tròn rồi gửi lại."
        )
    if any(_TAG_LIKE_OPEN.search(text) for text in (raw, value, folded)):
        # LC-T061-2: ``strip_tags`` của PHP (``sanitize_text_field``) bỏ cả cụm "<…>" như "<>",
        # "<1>", "<=>", nên "[<>code_snippet id=1]" thành shortcode liền mạch trên website.
        raise WordPressError(
            f"{label} có dấu «<» liền ký tự khác: website có thể coi là thẻ HTML và bỏ đi. Thêm "
            "dấu cách sau «<» hoặc bỏ dấu «<» rồi gửi lại."
        )
    # Xét trên chữ gốc: từ T-041 ``normalize_meta`` bỏ hẳn ký tự điều khiển (LC-T036-1), chữ đã
    # chuẩn hóa không còn để thấy. Khoảng trắng loại điều khiển (tab, xuống dòng) vẫn được gộp.
    if any(_CONTROL_CHARS.match(ch) and not ch.isspace() for ch in raw):
        raise WordPressError(f"{label} có ký tự điều khiển. Gõ lại chữ thường.")
    if len(value) > limit:
        raise WordPressError(f"{label} quá dài (tối đa {limit} ký tự).")
    return value


def _has_shortcode(text: str) -> bool:
    """Có dạng shortcode WordPress: "[" mở đầu tên (``_SHORTCODE_OPEN``) và "]" phía sau.

    Một lượt, tuyến tính: "[" mở đầu tiên không có "]" phía sau thì các "[" sau nó cũng không.
    """
    match = _SHORTCODE_OPEN.search(text)
    return match is not None and text.find("]", match.end()) >= 0


def _seo_error(route: str, status_code: int | None) -> SeoWriteResult:
    code = f" (mã {status_code})" if status_code else ""
    return SeoWriteResult(
        False,
        route,
        reason="error",
        message=_SEO_ERROR.format(code=code),
        status_code=status_code,
    )


def _ignorable_not_cf() -> re.Pattern[str]:
    """Ký tự "mặc định bỏ qua" không thuộc loại Cf (U+3164, U+FE0F…), dùng chung với
    ``normalize_meta``. Nhập muộn: ``seo_app.content`` kéo theo lớp AI."""
    from seo_app.content.rules import IGNORABLE_NOT_CF

    return IGNORABLE_NOT_CF


def _has_invisible(text: str) -> bool:
    """Có ký tự vô hình: loại Cf (U+200B rộng 0, U+202E đảo chiều, BOM, gạch nối mềm…) hoặc
    ký tự mặc định bỏ qua khác (U+3164 trắng Hangul, U+FE0F, U+034F…; SL-T042-7)."""
    return any(unicodedata.category(ch) == "Cf" for ch in text) or bool(
        _ignorable_not_cf().search(text)
    )


def _drop_invisible(text: str) -> str:
    """Bỏ mọi ký tự vô hình (như ``_has_invisible``)."""
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Cf")
    return _ignorable_not_cf().sub("", text)


_SITE_HOST = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?(?::[0-9]{1,5})?")
# Mỗi đoạn thư mục KHÔNG có dấu "." (LC-T042-5): đoạn có đuôi có thể là file chạy được trên máy
# chủ (``.php``, ``.pht``, ``.phtml``, ``.cgi``, ``.shtml``, ``.asp``, ``.aspx``, ``.jsp``,
# ``.py``…), lệnh gọi thành ``POST …/x.pht/wp-json/…`` chạy file đó thay vì REST API (PATH_INFO).
# Thư mục cài WordPress gần như không bao giờ có dấu chấm trong tên.
_SITE_PATH = re.compile(r"(?:/[A-Za-z0-9_~-]+)*")
_SITE_PATH_FORBIDDEN = ("wp-json", "code-snippets", "prometal", "wp-admin")


def _is_plain_site_url(base_url: str) -> bool:
    """``https://tên-máy[:cổng][/thư-mục]``: không tên/mật khẩu, không ``?``, ``#``, ``%``,
    không dấu ``.`` trong thư mục (``.``/``..``, file ``.php``, ``.cgi``…), không ``wp-json``,
    ``code-snippets``, ``prometal`` (SL-T042-3, LC-T042-5)."""
    # SL-T042-9: xét chuỗi GỐC trước ``urlsplit`` (hàm này âm thầm bỏ tab, xuống dòng).
    if any(ch.isspace() or _CONTROL_CHARS.match(ch) for ch in base_url):
        return False
    try:
        parts = urlsplit(base_url)
    except ValueError:
        return False
    if parts.scheme.lower() != "https" or "?" in base_url or "#" in base_url:
        return False
    if parts.query or parts.fragment or not _SITE_HOST.fullmatch(parts.netloc):
        return False
    if not _SITE_PATH.fullmatch(parts.path):
        return False
    # SL-T042-10, LC-T042-5: thư mục con không được là file (``_SITE_PATH`` không nhận dấu ".").
    # Không chừa cả ``index.php``: website dùng đường dẫn tĩnh (``/wp-json/`` chạy được, T-033),
    # không cần kiểu ``/index.php/wp-json/``.
    lowered = parts.path.lower()
    return not any(word in lowered for word in _SITE_PATH_FORBIDDEN)


def _check_web_image(image: object, number: int) -> None:
    """Ảnh thứ ``number`` phải là ``WebImage`` do ``make_web_image`` tạo: byte WebP đúng khuôn,
    chỉ có các chunk ảnh đăng web được phép (ảnh, độ trong suốt, hồ sơ màu, EXIF), cỡ hợp lệ.
    Không sửa byte nào: chỉ đọc để kiểm (Lá Chắn T-049 điều kiện 4)."""
    # Nhập muộn: module ảnh kéo theo Pillow, không cần khi chỉ dùng client.
    from seo_app.images.html import MAX_IMAGE_EDGE
    from seo_app.images.process import _WEBP_ALLOWED_CHUNKS, WebImage, webp_chunks

    error = WordPressError(_IMAGE_NOT_WEB.format(n=number))
    if not isinstance(image, WebImage) or image.mime != _WEBP_TYPE:
        raise error
    data = image.data
    if type(data) is not bytes or not data:
        raise error
    try:
        chunks = webp_chunks(data)
    except ValueError:
        raise error from None
    if not chunks or not set(chunks) <= _WEBP_ALLOWED_CHUNKS:
        raise error
    for edge in (image.width, image.height):
        if type(edge) is not int or not 0 < edge <= MAX_IMAGE_EDGE:
            raise error


def _is_term_ids(value: object) -> bool:
    """Danh sách mã chuyên mục/thẻ: list hay tuple các số nguyên dương thật."""
    return isinstance(value, list | tuple) and all(_positive_id(v) is not None for v in value)


def _draft_images_error(
    message: str,
    uploaded: Sequence[UploadedImage],
    *,
    maybe_uploaded: bool,
    maybe_draft: bool,
    status: int | None,
) -> DraftImagesError:
    """Câu báo lỗi gửi nháp kèm ảnh: lý do, bài nháp có thể đã có (lỗi ở lệnh tạo nháp), rồi
    ảnh đã lên thư viện (không xóa, W2)."""
    tail = _DRAFT_MAYBE_CREATED if maybe_draft else ""
    if uploaded:
        tail += _DRAFT_IMAGES_LEFT.format(count=len(uploaded))
    elif not maybe_uploaded:
        tail += _DRAFT_IMAGES_NONE
    if maybe_uploaded:
        tail += _DRAFT_IMAGE_MAYBE
    return DraftImagesError(
        message.rstrip() + tail,
        uploaded=uploaded,
        maybe_uploaded=maybe_uploaded,
        maybe_draft=maybe_draft,
        status_code=status,
    )


def _utc_now() -> datetime:
    """Đồng hồ máy (UTC), để so lệch với giờ website trong ``release_draft`` (test thay hàm này)."""
    return datetime.now(UTC)


def _is_date_gmt(value: object) -> bool:
    """Giờ UTC website trả dạng ``YYYY-MM-DDTHH:MM:SS`` (chữ số ASCII)."""
    return type(value) is str and value.isascii() and bool(_DATE_GMT_PATTERN.fullmatch(value))


# Tên múi giờ WordPress trả (``timezone_string``: tên IANA như ``Asia/Ho_Chi_Minh``, hay rỗng khi
# site đặt độ lệch tay).
_SITE_TIMEZONE = re.compile(r"[A-Za-z][A-Za-z0-9_+/-]{0,63}")
_SITE_OFFSET = re.compile(r"-?[0-9]{1,2}(?:\.[0-9]{1,2})?")


def _site_timezone(value: object) -> str:
    """``timezone_string`` của site: tên múi giờ dạng IANA đã kiểm, còn lại rỗng."""
    return value if isinstance(value, str) and _SITE_TIMEZONE.fullmatch(value) else ""


def _site_offset(value: object) -> float | None:
    """``gmt_offset`` của site (giờ, có thể lẻ: 5.5, 5.75; WordPress trả số hay chữ số) trong
    khoảng −12 … +14; còn lại ``None``."""
    if isinstance(value, str):
        if not value.isascii() or not _SITE_OFFSET.fullmatch(value):
            return None
        value = float(value)
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    hours = float(value)
    return hours if -12 <= hours <= 14 else None


def _format_offset(hours: float) -> str:
    """Độ lệch giờ đã kiểm → «UTC+7», «UTC+5:30», «UTC−3:30»."""
    minutes = round(hours * 60)
    sign = "+" if minutes >= 0 else "−"
    whole, rest = divmod(abs(minutes), 60)
    return f"UTC{sign}{whole}" + (f":{rest:02d}" if rest else "")


def _positive_id(value: object) -> int | None:
    """``value`` nếu là số nguyên dương thật (``int``, không phải ``bool``, chữ, số thực) và không
    quá ``MAX_ID`` (mã bài, ảnh WordPress là BIGINT không dấu, nhưng SQLite và PHP 64 bit chỉ tới
    2⁶³−1; lớn hơn là dữ liệu hỏng: như mã sai khuôn, T-091)."""
    return value if type(value) is int and 0 < value <= MAX_ID else None


# Ký tự surrogate lẻ (U+D800–U+DFFF): JSON hợp lệ («\\ud800») nhưng không mã hóa UTF-8 được, làm
# vỡ trang Streamlit, lưu SQLite lỗi (SL-T088-1). Thay bằng «�» (bỏ hẳn thì có thể ghép chữ, địa
# chỉ ảnh thành một chữ, một file khác).
_LONE_SURROGATE = re.compile(f"[{chr(0xD800)}-{chr(0xDFFF)}]")
_REPLACEMENT = "\N{REPLACEMENT CHARACTER}"


def _without_lone_surrogates(data: Any) -> Any:
    """``data`` (JSON đã đọc) với mọi surrogate lẻ trong chữ, kể cả tên khóa, thay bằng «�».
    Đi bằng ngăn xếp (không đệ quy): JSON lồng sâu không làm tràn."""
    if isinstance(data, str):
        return _LONE_SURROGATE.sub(_REPLACEMENT, data)
    stack = [data] if isinstance(data, list | dict) else []
    while stack:
        node = stack.pop()
        if isinstance(node, list):
            for index, item in enumerate(node):
                if isinstance(item, str):
                    node[index] = _LONE_SURROGATE.sub(_REPLACEMENT, item)
                elif isinstance(item, list | dict):
                    stack.append(item)
            continue
        items = list(node.items())
        node.clear()
        for key, value in items:
            if isinstance(value, str):
                value = _LONE_SURROGATE.sub(_REPLACEMENT, value)
            elif isinstance(value, list | dict):
                stack.append(value)
            node[_LONE_SURROGATE.sub(_REPLACEMENT, key) if isinstance(key, str) else key] = value
    return data


def _non_negative(value: object) -> int:
    """Số đếm / mã cha từ site: số nguyên ≥ 0 thật, còn lại là 0 (LC-T044-1)."""
    return value if type(value) is int and value >= 0 else 0


def _is_own_draft_answer(data: object, post_id: int) -> bool:
    """Câu trả lời của site nói đúng bài ``post_id`` và bài đó đang là nháp (đúng chữ)."""
    return (
        isinstance(data, dict)
        and type(data.get("id")) is int
        and data["id"] == post_id
        and data.get("status") == "draft"
    )


def _ability_confirms(data: object, fields: dict[str, str]) -> bool:
    """Câu trả lời 200 của ability ghi SEO có xác nhận rõ là đã ghi không (SL-T042-6, T-059).

    Chỉ nhận đúng khuôn SiteSEO 1.4.2 (``update_post_seo_data`` trong
    ``main/abilitiesregister.php``), đã thấy trên site thật ngày 2026-10-27 (T-059):
    ``{"updated": true, "post": {"title", "description", "canonical_url", "focus_keyphrase",
    "seo_score", "robots", "social"}}``; lỗi là ``WP_Error`` (``invalid_post``, ``forbidden``).

    - ``updated`` phải đúng ``True`` (bool); ``"true"``, ``1``, ``null``, thiếu khóa: chưa ghi.
      Khuôn ``{"success": true}`` **không** còn được nhận (site thật không trả khóa này).
    - ``post`` **bắt buộc** và là dict: đó là phần SiteSEO đọc lại sau khi lưu, chỉ nó cho biết
      website lưu đúng chữ đã gửi (SiteSEO làm sạch chữ, ví dụ ``<`` thành ``&lt;``, thì giá trị
      khác). Thiếu ``post`` là câu trả lời không phải của SiteSEO 1.4.2 (ability khác, lớp đệm,
      plugin chen giữa): không xác nhận được, coi là chưa ghi (Lá Chắn T-042, việc 10).
    - Mỗi trường đã gửi phải có trong ``post`` với giá trị **đúng từng chữ**, hoặc đúng từng chữ
      với bản SiteSEO lưu khi nhận chữ đó (``_siteseo_saved_form``, SL-T059-1: «< » thành
      ``&lt; ``, «%» liền hai chữ/số hex bị cắt, «\\» bị bỏ). Bản đó tính trên máy, nên máy chủ
      không làm app tin một chữ tùy ý.
    - Thân lỗi WordPress (có ``code``), hay ``success`` khác ``True`` (SL-T042-8: một khóa nói rõ
      "chưa ghi" thì không tin khóa kia): chưa ghi.

    Sai bất kỳ điều nào thì app báo "không thành công" (người dùng chép tay vào hộp SiteSEO):
    chiều an toàn, không bao giờ báo "đã ghi" khi chưa chắc.
    """
    if not isinstance(data, dict) or "code" in data:
        return False
    if data.get("updated") is not True or data.get("success", True) is not True:
        return False
    snapshot = data.get("post")
    if not fields or not isinstance(snapshot, dict):
        return False
    for name, value in fields.items():
        saved = snapshot.get(_ABILITY_FIELDS[name])
        if saved != value and (saved is None or saved != _siteseo_saved_form(value)):
            return False
    return True


def _siteseo_lost_text(data: dict[str, Any], fields: dict[str, str]) -> bool:
    """Sau ``_ability_confirms``: SiteSEO có bỏ mất ký tự nào không (khác chữ đã gửi cả khi đổi
    mã ký tự HTML về chữ, ví dụ «10%BE» thành «10»). «< » thành ``&lt; `` thì hiện y như cũ."""
    snapshot = data["post"]
    return any(
        html.unescape(snapshot[_ABILITY_FIELDS[name]]) != value for name, value in fields.items()
    )


# ``sanitize_text_field`` của WordPress (``_sanitize_text_fields``), phần chạy với chữ SEO app
# gửi (một dòng, ``_seo_text`` đã chặn thẻ, mã ký tự HTML, «<» liền ký tự khác, ký tự điều khiển).
# ``wp_pre_kses_less_than``: đoạn từ «<» tới «<» kế tiếp, «>» hay hết chữ; không có «>» thì
# ``esc_html`` (``&``, ``<``, ``"``, ``'`` thành ``&amp;``, ``&lt;``, ``&quot;``, ``&#039;``).
_LESS_THAN_RUN = re.compile(r"<[^>]*?((?=<)|>|$)")
_PERCENT_HEX = re.compile(r"%[a-f0-9]{2}", re.IGNORECASE)
_ESC_HTML = str.maketrans({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"})


def _siteseo_saved_form(text: str) -> str | None:
    """Chữ SiteSEO 1.4.2 lưu khi nhận ``text``: ``update_post_meta(…, sanitize_text_field(text))``
    (``update_metadata`` còn ``wp_unslash``), đọc mã ở kho plugin wordpress.org (Soi Lỗi T-059).

    ``None`` khi không đoán chắc được (có đoạn «< … >»: ``strip_tags`` của PHP có thể bỏ; «<»
    không có khoảng trắng ngay sau): khi đó chỉ nhận chữ khớp từng chữ.
    """
    if "<" in text:
        runs = [match.group(0) for match in _LESS_THAN_RUN.finditer(text)]
        if any(run.endswith(">") or run[1:2] not in (" ", "\t") for run in runs):
            return None
        text = _LESS_THAN_RUN.sub(lambda match: match.group(0).translate(_ESC_HTML), text)
    text = re.sub(r"[\r\n\t ]+", " ", text).strip()
    found = False
    while match := _PERCENT_HEX.search(text):
        text, found = text.replace(match.group(0), ""), True
    if found:
        text = re.sub(" +", " ", text).strip()
    return _php_stripslashes(text)


def _php_stripslashes(text: str) -> str:
    """``stripslashes`` của PHP: «\\x» thành «x», «\\0» thành NUL, «\\» cuối chữ bị bỏ."""
    out: list[str] = []
    chars = iter(text)
    for char in chars:
        if char != "\\":
            out.append(char)
            continue
        following = next(chars, None)
        if following is not None:
            out.append("\x00" if following == "0" else following)
    return "".join(out)


def _plain(text: object) -> str:
    """Bỏ thẻ HTML và giải mã ký tự (&amp; -> &) trong chuỗi WordPress trả về.

    Không phải chữ (site trả số, ``null``, danh sách…, LC-T044-1): số nguyên/thực thành chữ,
    còn lại là chuỗi rỗng. Không bao giờ ném lỗi.
    """
    if isinstance(text, bool) or not isinstance(text, str | int | float):
        return ""
    return html.unescape(re.sub(r"<[^>]+>", "", str(text))).strip()
