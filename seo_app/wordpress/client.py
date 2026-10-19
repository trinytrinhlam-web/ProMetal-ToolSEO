"""Client WordPress REST API, xác thực bằng Application Password.

Chỉ làm những việc an toàn: đọc thông tin, tạo bài NHÁP, tải ảnh, đặt ảnh đại diện cho bài
nháp vừa tạo. Chỉ nói chuyện qua https.
Không có hàm nào đăng bài công khai. Mật khẩu không bao giờ xuất hiện trong thông báo lỗi.
"""

from __future__ import annotations

import html
import html.entities
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import requests

from seo_app.config import Settings
from seo_app.sanitize import sanitize_html, strip_tags
from seo_app.text import slugify

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
_MODIFIED_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
_SLUG_PATTERN = re.compile(r"[A-Za-z0-9%._~-]+")
_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f-\x9f]")
_LINK_UNSAFE = frozenset("\"'<>`")  # không được có trần trong link lấy từ site
_TOTAL_PAGES_PATTERN = re.compile(r"[0-9]+")
_PAGE_OUT_OF_RANGE = "rest_post_invalid_page_number"  # WordPress: xin trang quá số trang

# ---------------------------------------------------------------- đường REST được phép gọi
# Danh sách CỐ ĐỊNH (T-042, điều kiện Lá Chắn T-037): ``_request`` so khớp toàn chuỗi cặp
# (phương thức, đường) với danh sách này và từ chối mọi đường khác TRƯỚC KHI gửi. Site có những
# đường nhạy cảm (``/code-snippets/v1`` chạy mã PHP, ``/prometal/v1/deploy-files``,
# ``/prometal/v1/purge``): không bao giờ được gọi. Muốn thêm đường phải sửa ở đây và qua Lá Chắn.
_ID = r"[1-9][0-9]{0,18}"  # mã bài/ảnh: số nguyên dương, chỉ chữ số ASCII
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
    ("POST", rf"/wp/v2/posts/{_ID}"),  # ảnh đại diện, meta SEO dự phòng (chỉ bài app tạo)
    ("POST", r"/wp/v2/media"),
    ("POST", rf"/wp/v2/media/{_ID}"),
    ("GET", re.escape(SITESEO_ABILITY_PATH)),  # dò Abilities của SiteSEO đã bật chưa
    ("POST", re.escape(SITESEO_ABILITY_RUN_PATH)),  # ghi SEO (chỉ bài app tạo)
)
_ALLOWED_ROUTES = tuple((method, re.compile(pattern)) for method, pattern in ALLOWED_ROUTES)
# Chặn thêm (phòng khi ai đó nới biểu thức ở trên): đi ngược thư mục, mã hóa "%", "//", "\",
# và các namespace nhạy cảm của site. So trên chữ thường.
_FORBIDDEN_IN_PATH = ("..", "%", "//", "\\", "code-snippets", "prometal")


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
_SEO_WRITTEN_NO_KEYWORD = (
    "Đã ghi tiêu đề, mô tả SEO vào bài nháp. Từ khóa chính chưa ghi được bằng đường dự phòng: "
    "chép tay vào hộp SiteSEO."
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
        if type(self.id) is not int or self.id <= 0:
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
            raise WordPressError(
                f"Địa chỉ website '{base_url}' không hợp lệ. Ví dụ đúng: https://example.com"
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
                "dấu ?, #, %, @, đoạn /wp-json hay /.. ). Sửa trong file .env."
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

        Nội dung và đoạn trích luôn qua bộ lọc HTML (security.md 2.3); tiêu đề bỏ mọi thẻ.
        """
        title = strip_tags(title).strip()
        if not title:
            raise WordPressError("Tiêu đề bài viết không được để trống.")
        payload: dict[str, Any] = {
            "status": "draft",
            "title": title,
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
        data = self._json(self._request("POST", "/wp/v2/posts", json=payload))
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
                    params={"context": "edit", "_fields": "id,status,meta"},
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
        return SeoWriteResult(True, "abilities", tuple(fields), message=_SEO_WRITTEN)

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
                self._request("POST", f"/wp/v2/posts/{post_id}", json={"meta": send})
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
            self._request("POST", f"/wp/v2/posts/{post_id}", json={"featured_media": media_id})
        )
        if not _is_own_draft_answer(data, post_id):
            # SL-T042-11: câu trả lời nói về bài khác, hay bài không còn nháp: bất thường.
            raise WordPressError(_IMAGE_ODD_ANSWER)
        return self._post_from(data)

    def upload_media(
        self,
        data: bytes,
        filename: str,
        *,
        alt_text: str = "",
        title: str = "",
        caption: str = "",
    ) -> Media:
        """Tải ảnh lên thư viện Media. Tên file được chuyển thành không dấu."""
        suffix = Path(filename).suffix.lower()
        content_type = IMAGE_TYPES.get(suffix)
        if content_type is None:
            allowed = ", ".join(sorted(IMAGE_TYPES))
            raise WordPressError(f"File '{filename}' không phải ảnh được hỗ trợ ({allowed}).")
        if not data:
            raise WordPressError(f"File '{filename}' rỗng.")
        safe_name = f"{slugify(Path(filename).stem) or 'anh'}{suffix}"

        response = self._request(
            "POST",
            "/wp/v2/media",
            data=data,
            headers={
                "Content-Type": content_type,
                "Content-Disposition": f'attachment; filename="{safe_name}"',
            },
        )
        media = self._json(response)
        # SL-T042-4, LC-T044-1: chỉ nhận id là số nguyên dương thật (``True``, ``"7"``, ``7.9``
        # không được thành ảnh 1 hay ảnh 7 của người khác).
        media_id = _positive_id(media.get("id") if isinstance(media, dict) else None)
        if media_id is None:
            raise WordPressError(_BAD_DATA.format(what="ảnh vừa tải lên"))

        extra = {
            key: value
            for key, value in {"alt_text": alt_text, "title": title, "caption": caption}.items()
            if value
        }
        if extra:
            updated = self._json(self._request("POST", f"/wp/v2/media/{media_id}", json=extra))
            if isinstance(updated, dict):
                media = updated

        source_url = media.get("source_url")
        saved_alt = media.get("alt_text")
        return Media(
            id=media_id,
            source_url=source_url if isinstance(source_url, str) else "",
            alt_text=saved_alt if isinstance(saved_alt, str) else alt_text,
        )

    def upload_media_file(self, path: Path, **kwargs: Any) -> Media:
        return self.upload_media(path.read_bytes(), path.name, **kwargs)

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
        if not is_allowed_route(method, path):
            # Từ chối TRƯỚC KHI gửi: không có request nào đi ra (T-042). Câu cố định, không
            # chép đường bị từ chối.
            raise WordPressError(
                "Phần mềm chặn một lệnh gọi WordPress không có trong danh sách được phép. "
                "Không có gì được gửi lên website."
            )
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
                f"Không kết nối được tới {self.base_url}. Kiểm tra mạng và WORDPRESS_URL."
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
                "WordPress trả lời bằng một lệnh chuyển hướng sang địa chỉ khác; phần mềm không "
                "đi theo. Kiểm tra WORDPRESS_URL trong .env có đúng địa chỉ website không (có "
                "hay không có www, có https).",
                status_code=response.status_code,
            )
        if response.status_code >= 400:
            raise self._error_from(response)
        return response

    @staticmethod
    def _json(response: requests.Response) -> Any:
        try:
            return response.json()
        except ValueError as exc:
            raise WordPressError(
                "WordPress không trả về dữ liệu JSON (có thể là trang HTML). Thường do sai "
                "WORDPRESS_URL, hoặc plugin bảo mật / tường lửa đang chặn REST API."
            ) from exc

    def _error_from(self, response: requests.Response) -> WordPressError:
        status = response.status_code
        try:
            body = response.json()
        except ValueError:
            body = {}
        if not isinstance(body, dict):
            body = {}
        code = str(body.get("code", ""))
        wp_message = _plain(str(body.get("message", "")))
        detail = f" (WordPress: {wp_message})" if wp_message else ""

        if status == 401:
            message = (
                "WordPress từ chối đăng nhập. Kiểm tra WORDPRESS_USERNAME và "
                "WORDPRESS_APP_PASSWORD trong .env (phải là Application Password, không phải "
                "mật khẩu đăng nhập thường). Nếu đã đúng, có thể hosting đang chặn header "
                "Authorization hoặc plugin bảo mật tắt Application Passwords."
            )
        elif status == 403:
            message = (
                "Tài khoản WordPress không đủ quyền làm việc này, hoặc plugin bảo mật đang "
                "chặn REST API."
            )
        elif status == 404:
            if code == "rest_no_route" or not body:
                message = (
                    f"Không tìm thấy REST API tại {self.base_url}/wp-json. Kiểm tra "
                    "WORDPRESS_URL, và trong WordPress vào Cài đặt → Đường dẫn tĩnh, bấm Lưu "
                    "một lần."
                )
            else:
                message = "Không tìm thấy dữ liệu trên WordPress (có thể đã bị xóa)."
        elif status == 413:
            message = "File quá lớn so với giới hạn tải lên của máy chủ WordPress."
        elif status >= 500:
            message = f"Máy chủ WordPress đang gặp lỗi (mã {status}). Thử lại sau."
        else:
            message = f"WordPress báo lỗi (mã {status})."
        return WordPressError(message + detail, status_code=status, code=code)


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
            id=raw.get("id"),  # type: ignore[arg-type]  # PublishedItem tự kiểm kiểu
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
    ``%%`` (biến SiteSEO), ký tự điều khiển, quá dài. Xét cả chữ gốc, chữ đã chuẩn hóa và dạng
    NFKC (``＜``, ``％％`` toàn khổ).
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
    if _CONTROL_CHARS.search(value):
        raise WordPressError(f"{label} có ký tự điều khiển. Gõ lại chữ thường.")
    if len(value) > limit:
        raise WordPressError(f"{label} quá dài (tối đa {limit} ký tự).")
    return value


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
_SITE_PATH = re.compile(r"(?:/[A-Za-z0-9_~-][A-Za-z0-9._~-]*)*")
_SITE_PATH_FORBIDDEN = ("wp-json", "code-snippets", "prometal", "wp-admin")


def _is_plain_site_url(base_url: str) -> bool:
    """``https://tên-máy[:cổng][/thư-mục]``: không tên/mật khẩu, không ``?``, ``#``, ``%``,
    không đoạn ``.``/``..``, không ``wp-json``, ``code-snippets``, ``prometal`` (SL-T042-3)."""
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
    lowered = parts.path.lower()
    if any(word in lowered for word in _SITE_PATH_FORBIDDEN):
        return False
    # SL-T042-10: thư mục con không được là file PHP (``/xmlrpc.php``, ``/run.php``…): lệnh
    # gọi sẽ chạy file đó thay vì REST API. Không chừa cả ``index.php``: website dùng đường
    # dẫn tĩnh (``/wp-json/`` chạy được, T-033), không cần kiểu ``/index.php/wp-json/``.
    return not any(ext in lowered for ext in (".php", ".phtml", ".phar"))


def _positive_id(value: object) -> int | None:
    """``value`` nếu là số nguyên dương thật (``int``, không phải ``bool``, chữ, số thực)."""
    return value if type(value) is int and value > 0 else None


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
    """Câu trả lời 200 của ability ghi SEO có xác nhận rõ là đã ghi không (SL-T042-6).

    Khuôn SiteSEO 1.4.2 (``update_post_seo_data`` trong ``main/abilitiesregister.php``):
    ``{"updated": true, "post": {"title", "description", "focus_keyphrase", ...}}``; lỗi là
    ``WP_Error`` (``invalid_post``, ``forbidden``). Nhận thêm ``{"success": true}``. Đúng
    ``True`` (bool) mới tính; ``"false"``, ``0``, ``[]``, ``"ok"``, ``null``, thân lỗi
    WordPress (``code``) đều là chưa ghi. Có ``post`` thì giá trị đã lưu phải đúng chữ đã gửi.
    """
    if not isinstance(data, dict) or "code" in data:
        return False
    if data.get("updated") is False or data.get("success") is False:
        return False  # SL-T042-8: một khóa nói rõ "chưa ghi" thì không tin khóa kia
    if data.get("updated") is not True and data.get("success") is not True:
        return False
    snapshot = data.get("post")
    if snapshot is None:
        return True
    if not isinstance(snapshot, dict):
        return False
    return all(snapshot.get(_ABILITY_FIELDS[name]) == value for name, value in fields.items())


def _plain(text: object) -> str:
    """Bỏ thẻ HTML và giải mã ký tự (&amp; -> &) trong chuỗi WordPress trả về.

    Không phải chữ (site trả số, ``null``, danh sách…, LC-T044-1): số nguyên/thực thành chữ,
    còn lại là chuỗi rỗng. Không bao giờ ném lỗi.
    """
    if isinstance(text, bool) or not isinstance(text, str | int | float):
        return ""
    return html.unescape(re.sub(r"<[^>]+>", "", str(text))).strip()
