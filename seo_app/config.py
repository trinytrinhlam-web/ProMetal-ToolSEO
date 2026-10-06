"""Đọc cấu hình từ file ``.env`` ở thư mục gốc dự án và biến môi trường.

Biến môi trường của hệ điều hành được ưu tiên hơn giá trị trong ``.env``.
Các giá trị bí mật (khóa API, mật khẩu) được ẩn khỏi ``repr`` để không lỡ in ra log.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dotenv import dotenv_values

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ENV_FILE = PROJECT_ROOT / ".env"
DEFAULT_TIMEZONE = "Asia/Ho_Chi_Minh"

# Tên tất cả biến mà app đọc. .env.example phải có đủ các tên này (có test kiểm tra).
ENV_VARS = (
    "APP_PASSWORD_HASH",
    "APP_TIMEZONE",
    "WORDPRESS_URL",
    "WORDPRESS_USERNAME",
    "WORDPRESS_APP_PASSWORD",
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_SERVICE_ACCOUNT_FILE",
    "GOOGLE_SHEET_ID",
    "GSC_SITE_URL",
    "IMAGE_FOLDERS",
)


class ConfigError(ValueError):
    """Cấu hình sai (ví dụ múi giờ không tồn tại)."""


@dataclass(frozen=True)
class Settings:
    password_hash: str = field(default="", repr=False)
    timezone_name: str = DEFAULT_TIMEZONE

    wordpress_url: str = ""
    wordpress_username: str = ""
    wordpress_app_password: str = field(default="", repr=False)

    anthropic_api_key: str = field(default="", repr=False)
    openai_api_key: str = field(default="", repr=False)
    gemini_api_key: str = field(default="", repr=False)

    google_service_account_file: Path | None = None
    google_sheet_id: str = ""
    gsc_site_url: str = ""

    image_folders: tuple[Path, ...] = ()

    @property
    def timezone(self) -> ZoneInfo:
        return ZoneInfo(self.timezone_name)

    def now(self) -> datetime:
        """Thời điểm hiện tại, kèm múi giờ đã cấu hình."""
        return datetime.now(self.timezone)

    def status(self) -> dict[str, bool]:
        """Mục nào đã khai báo (chỉ trả về đúng/sai, không bao giờ trả về giá trị)."""
        return {
            "Mật khẩu đăng nhập": bool(self.password_hash),
            "WordPress": bool(
                self.wordpress_url and self.wordpress_username and self.wordpress_app_password
            ),
            "Anthropic (Claude)": bool(self.anthropic_api_key),
            "OpenAI": bool(self.openai_api_key),
            "Google Gemini": bool(self.gemini_api_key),
            "Google service account": bool(self.google_service_account_file),
            "Google Sheets": bool(self.google_sheet_id),
            "Search Console": bool(self.gsc_site_url),
            "Thư mục ảnh": bool(self.image_folders),
        }


def load_settings(
    env_file: Path | None = DEFAULT_ENV_FILE,
    environ: Mapping[str, str] | None = None,
) -> Settings:
    """Tạo ``Settings`` từ ``.env`` (nếu có) và biến môi trường.

    ``env_file=None`` bỏ qua file; ``environ`` mặc định là ``os.environ``.
    """
    values: dict[str, str] = {}
    if env_file is not None and env_file.is_file():
        file_values = dotenv_values(env_file, encoding="utf-8")
        values.update({k: v for k, v in file_values.items() if v is not None})
    env = os.environ if environ is None else environ
    values.update({name: env[name] for name in ENV_VARS if name in env})

    def get(name: str) -> str:
        return values.get(name, "").strip()

    timezone_name = get("APP_TIMEZONE") or DEFAULT_TIMEZONE
    try:
        ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ConfigError(
            f"Múi giờ APP_TIMEZONE='{timezone_name}' không hợp lệ. Ví dụ đúng: {DEFAULT_TIMEZONE}"
        ) from exc

    service_account = get("GOOGLE_SERVICE_ACCOUNT_FILE")

    return Settings(
        password_hash=get("APP_PASSWORD_HASH"),
        timezone_name=timezone_name,
        wordpress_url=get("WORDPRESS_URL").rstrip("/"),
        wordpress_username=get("WORDPRESS_USERNAME"),
        wordpress_app_password=get("WORDPRESS_APP_PASSWORD"),
        anthropic_api_key=get("ANTHROPIC_API_KEY"),
        openai_api_key=get("OPENAI_API_KEY"),
        gemini_api_key=get("GEMINI_API_KEY"),
        google_service_account_file=Path(service_account).expanduser() if service_account else None,
        google_sheet_id=get("GOOGLE_SHEET_ID"),
        gsc_site_url=get("GSC_SITE_URL"),
        image_folders=_parse_folders(get("IMAGE_FOLDERS")),
    )


def _parse_folders(raw: str) -> tuple[Path, ...]:
    """Danh sách thư mục ngăn cách bằng dấu chấm phẩy ``;``."""
    return tuple(Path(part.strip()).expanduser() for part in raw.split(";") if part.strip())
