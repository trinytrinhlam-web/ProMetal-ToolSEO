"""Client WordPress REST API, xác thực bằng Application Password.

Chỉ làm những việc an toàn: đọc thông tin, tạo bài NHÁP, tải ảnh, đặt ảnh đại diện cho bài
nháp vừa tạo. Chỉ nói chuyện qua https.
Không có hàm nào đăng bài công khai. Mật khẩu không bao giờ xuất hiện trong thông báo lỗi.
"""

from __future__ import annotations

import html
import re
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
            if _CONTROL_CHARS.search(value):
                raise ValueError(f"{name} có ký tự điều khiển")
        if self.slug and not _SLUG_PATTERN.fullmatch(self.slug):
            raise ValueError("slug có ký tự lạ")
        if self.modified_gmt and not _MODIFIED_PATTERN.fullmatch(self.modified_gmt):
            raise ValueError("modified_gmt sai dạng")
        if not self.link:
            raise ValueError("thiếu link")


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
    ) -> None:
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
        if not username or not app_password:
            raise WordPressError("Thiếu tên đăng nhập hoặc Application Password của WordPress.")
        self.base_url = base_url
        self.timeout = timeout
        self._session = session or requests.Session()
        # WordPress bỏ qua dấu cách trong Application Password, nên xóa cho gọn.
        self._session.auth = (username, app_password.replace(" ", ""))
        self._session.headers.update({"Accept": "application/json", "User-Agent": "SEO-App/0.1"})
        # Bài do chính client này tạo: chỉ những bài này mới được sửa (ảnh đại diện), để không
        # bao giờ đụng tới bài đã có trên website (R3).
        self._created_post_ids: set[int] = set()

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
        """Kiểm tra REST API và quyền của tài khoản. Lỗi thì ném WordPressError."""
        root = self._json(self._request("GET", "/"))
        if not isinstance(root, dict) or "wp/v2" not in root.get("namespaces", []):
            raise WordPressError(
                "Website trả lời nhưng không có REST API của WordPress (wp/v2). "
                "Kiểm tra WORDPRESS_URL, hoặc plugin bảo mật có đang tắt REST API không."
            )
        me = self._json(self._request("GET", "/wp/v2/users/me", params={"context": "edit"}))
        capabilities = me.get("capabilities") or {}
        return ConnectionInfo(
            site_name=_plain(root.get("name", "")),
            site_url=root.get("home") or root.get("url") or self.base_url,
            user_name=_plain(me.get("name", "")),
            roles=tuple(me.get("roles") or ()),
            can_edit_posts=bool(capabilities.get("edit_posts")),
            can_publish_posts=bool(capabilities.get("publish_posts")),
            can_upload_files=bool(capabilities.get("upload_files")),
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
        return [
            Term(
                id=int(item["id"]),
                name=_plain(item.get("name", "")),
                slug=item.get("slug", ""),
                count=int(item.get("count", 0)),
                parent=int(item.get("parent", 0) or 0),
            )
            for item in self._get_all_pages(path, params)
        ]

    def list_published(self) -> list[PublishedItem]:
        """Mọi bài và trang ĐÃ ĐĂNG (``publish``) trên site, kèm meta SiteSEO nếu site mở.

        Chỉ đọc (``GET``), đúng hai đường cố định ``/wp/v2/posts`` và ``/wp/v2/pages``. Dữ liệu
        trả về là chưa tin cậy nên được lọc lại phía app (T-037, T-033 mục 4.1):
        - chỉ giữ mục có ``status == "publish"`` (bỏ ``future``, ``draft``, ``private``…);
        - ``link`` phải là ``https://`` và đúng tên máy (và cổng) của ``WORDPRESS_URL``;
        - tiêu đề và meta bỏ thẻ, gộp khoảng trắng, cắt theo giới hạn độ dài;
        - mục sai khuôn (thiếu id, link lạ…) bị bỏ, không làm hỏng cả danh sách.
        Meta SiteSEO không có trong kết quả thì để rỗng.
        """
        params = {
            "status": "publish",
            "per_page": PER_PAGE,
            "orderby": "id",
            "order": "asc",
            "_fields": _PUBLISHED_FIELDS,
        }
        items: list[PublishedItem] = []
        seen: set[tuple[str, int]] = set()
        for kind, path in (("post", "/wp/v2/posts"), ("page", "/wp/v2/pages")):
            for raw in self._get_all_pages(path, params):
                item = _published_from(raw, kind, self.base_url)
                if item is None or (item.type, item.id) in seen:
                    continue
                seen.add((item.type, item.id))
                items.append(item)
        return items

    def _get_all_pages(self, path: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        page = 1
        while page <= MAX_PAGES:
            response = self._request("GET", path, params={**params, "page": page})
            data = self._json(response)
            if not isinstance(data, list):
                raise WordPressError("WordPress trả về dữ liệu không đúng dạng danh sách.")
            items.extend(data)
            try:
                total_pages = int(response.headers.get("X-WP-TotalPages", "1"))
            except ValueError:
                total_pages = 1
            if page >= total_pages or not data:
                break
            page += 1
        return items

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
        self._created_post_ids.add(post.id)
        return post

    def set_featured_image(self, post_id: int, media_id: int) -> Post:
        """Đặt ảnh đại diện, CHỈ cho bài nháp mà client này vừa tạo bằng ``create_draft``.

        Bài đã có sẵn trên website không bao giờ bị sửa (R3, security.md 2.2).
        """
        if post_id not in self._created_post_ids:
            raise WordPressError(
                "Chỉ được đặt ảnh đại diện cho bài nháp app vừa tạo, không sửa bài đã có trên "
                "website."
            )
        data = self._json(
            self._request("POST", f"/wp/v2/posts/{post_id}", json={"featured_media": media_id})
        )
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
        media_id = int(media["id"])

        extra = {
            key: value
            for key, value in {"alt_text": alt_text, "title": title, "caption": caption}.items()
            if value
        }
        if extra:
            media = self._json(self._request("POST", f"/wp/v2/media/{media_id}", json=extra))

        return Media(
            id=media_id,
            source_url=media.get("source_url", ""),
            alt_text=media.get("alt_text", alt_text),
        )

    def upload_media_file(self, path: Path, **kwargs: Any) -> Media:
        return self.upload_media(path.read_bytes(), path.name, **kwargs)

    # ------------------------------------------------------------- nội bộ

    def edit_link(self, post_id: int) -> str:
        return f"{self.base_url}/wp-admin/post.php?post={post_id}&action=edit"

    def _post_from(self, data: dict[str, Any]) -> Post:
        title = data.get("title")
        if isinstance(title, dict):
            title = title.get("raw") or title.get("rendered") or ""
        post_id = int(data["id"])
        return Post(
            id=post_id,
            status=data.get("status", ""),
            title=_plain(title or ""),
            link=data.get("link", ""),
            edit_link=self.edit_link(post_id),
            featured_media=int(data.get("featured_media") or 0),
        )

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        url = f"{self.base_url}/wp-json{path}"
        try:
            response = self._session.request(method, url, timeout=self.timeout, **kwargs)
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


def is_site_link(link: object, base_url: str) -> bool:
    """``link`` là địa chỉ ``https://`` trên đúng tên máy (và cổng) của ``base_url``.

    Từ chối: ``http://``, tên máy khác (kể cả tên miền con), có tên/mật khẩu trong địa chỉ,
    khoảng trắng hoặc ký tự điều khiển, cổng sai dạng, quá dài.
    """
    if not isinstance(link, str) or not link or len(link) > MAX_LINK_CHARS:
        return False
    if _CONTROL_CHARS.search(link) or any(ch.isspace() for ch in link) or "\\" in link:
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
    return " ".join(text.split())[:limit].rstrip()


def _plain(text: str) -> str:
    """Bỏ thẻ HTML và giải mã ký tự (&amp; -> &) trong chuỗi WordPress trả về."""
    return html.unescape(re.sub(r"<[^>]+>", "", text)).strip()
