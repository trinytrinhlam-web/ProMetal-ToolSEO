"""Phần chung của mọi hãng AI: cấu hình theo việc, lỗi, và giao diện provider."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

EFFORTS = ("low", "medium", "high", "xhigh", "max")


# Chuỗi trông giống khóa/mật khẩu:
# - khóa Anthropic/OpenAI (sk-…), Google (AIza…), kể cả khi dính sau "_" (x_sk-…);
# - token sau "Bearer"/"Basic" (có hoặc không có dấu ":");
# - giá trị sau "x-api-key", "api_key", "authorization", "password", "token" kèm ":" hoặc "=":
#   che tới hết dòng (hoặc tới dấu nháy đóng), vì mật khẩu có thể chứa dấu cách.
_SECRET_LIKE = re.compile(
    r"(?<![A-Za-z0-9])(?:sk-[A-Za-z0-9_\-]{8,}|AIza[0-9A-Za-z_\-]{16,})"
    r"|(?:(?<=bearer)|(?<=basic))[ \t]*:?[ \t]+[A-Za-z0-9._~+/=\-]{6,}"
    r"|(?:(?<=x-api-key)|(?<=api[_-]key)|(?<=authorization)|(?<=password)|(?<=token))"
    r"[\"']?[ \t]*[:=][ \t]*[\"']?[^\n\"']{4,}",
    re.IGNORECASE,
)


def redact_secrets(text: str) -> str:
    """Che các chuỗi giống khóa trong thông báo lỗi lấy từ máy chủ/thư viện (security.md 2.1)."""
    return _SECRET_LIKE.sub("[đã ẩn]", text)


class AIError(RuntimeError):
    """Lỗi khi gọi AI. Thông điệp viết bằng tiếng Việt để hiện thẳng cho người dùng."""


@dataclass(frozen=True)
class TaskConfig:
    """Mô hình dùng cho một việc (đọc từ ``config/ai.toml``)."""

    name: str
    provider: str
    model: str
    effort: str = "medium"
    web_search: bool = False
    max_tokens: int = 16000


class AIProvider(Protocol):
    """Một hãng AI. Mỗi lần gọi trả về dữ liệu đúng khuôn ``schema`` (đã kiểm tra)."""

    def generate(self, task: TaskConfig, *, system: str, prompt: str, schema: type[T]) -> T: ...
