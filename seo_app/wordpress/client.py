"""Client WordPress REST API, xác thực bằng Application Password.

Chỉ làm những việc an toàn: đọc thông tin, tạo bài NHÁP, tải ảnh, đặt ảnh đại diện.
Không có hàm nào đăng bài công khai. Mật khẩu không bao giờ xuất hiện trong thông báo lỗi.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

from seo_app.config import Settings
from seo_app.text import slugify

DEFAULT_TIMEOUT = 30
PER_PAGE = 100
MAX_PAGES = 50  # chặn vòng lặp vô hạn nếu máy chủ trả số trang sai

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
        if not re.match(r"^https?://[^/\s]+", base_url):
            raise WordPressError(
                f"Địa chỉ website '{base_url}' không hợp lệ. Ví dụ đúng: https://example.com"
            )
        if not username or not app_password:
            raise WordPressError("Thiếu tên đăng nhập hoặc Application Password của WordPress.")
        self.base_url = base_url
        self.timeout = timeout
        self._session = session or requests.Session()
        # WordPress bỏ qua dấu cách trong Application Password, nên xóa cho gọn.
        self._session.auth = (username, app_password.replace(" ", ""))
        self._session.headers.update({"Accept": "application/json", "User-Agent": "SEO-App/0.1"})

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
        return self.base_url.startswith("https://")

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
        """Tạo bài ở trạng thái NHÁP (draft). Không bao giờ đăng công khai."""
        if not title.strip():
            raise WordPressError("Tiêu đề bài viết không được để trống.")
        payload: dict[str, Any] = {
            "status": "draft",
            "title": title.strip(),
            "content": content,
        }
        if categories:
            payload["categories"] = list(categories)
        if tags:
            payload["tags"] = list(tags)
        if excerpt:
            payload["excerpt"] = excerpt
        if slug:
            payload["slug"] = slug
        if featured_media:
            payload["featured_media"] = featured_media
        data = self._json(self._request("POST", "/wp/v2/posts", json=payload))
        return self._post_from(data)

    def set_featured_image(self, post_id: int, media_id: int) -> Post:
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


def _plain(text: str) -> str:
    """Bỏ thẻ HTML và giải mã ký tự (&amp; -> &) trong chuỗi WordPress trả về."""
    return html.unescape(re.sub(r"<[^>]+>", "", text)).strip()
