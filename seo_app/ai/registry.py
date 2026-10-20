"""Đọc ``config/ai.toml`` và tạo provider cho từng việc."""

from __future__ import annotations

import tomllib
from collections.abc import Iterable
from pathlib import Path

from seo_app.ai.base import EFFORTS, SETUP_ERRORS, AIError, AIProvider, TaskConfig, library_error
from seo_app.config import PROJECT_ROOT, Settings

AI_CONFIG_FILE = PROJECT_ROOT / "config" / "ai.toml"

# Tên hãng trong config -> (tên hiển thị, tên biến khóa API trong .env)
PROVIDERS = {
    "anthropic": ("Anthropic (Claude)", "ANTHROPIC_API_KEY"),
    "openai": ("OpenAI", "OPENAI_API_KEY"),
    "gemini": ("Google Gemini", "GEMINI_API_KEY"),
}
SUPPORTED = {"anthropic", "openai", "gemini"}

# Việc tạo ảnh minh họa (T-053): Claude không tạo được ảnh (T-046 mục 4), chỉ OpenAI, Gemini.
IMAGE_TASK = "image"
IMAGE_PROVIDERS = ("gemini", "openai")

# Các việc của trang Soạn bài (``ContentWriter``: nghiên cứu → dàn ý → viết → rà soát → viết
# lại). ``AIRouter`` dựng sẵn provider cho các việc này lúc tạo, để trang Soạn bài báo thiếu khóa
# ngay khi mở và khóa các nút AI như trước. Mọi việc khác (meta, alt, image…) chỉ tạo provider
# khi được gọi lần đầu (T-062): bật [tasks.image] bằng Gemini không bắt người chỉ viết bài nhập
# khóa Gemini.
WRITING_TASKS = ("research", "outline", "write", "rewrite", "review")

# Việc mới thêm sau, có thể chưa có trong config/ai.toml của máy đang dùng (file do người dùng
# sửa, máy kia có thể chưa cập nhật): câu báo nói rõ việc đó là gì và ghi mẫu để chép vào.
# Mẫu theo quyết định 4A (2026-10-19: alt bằng Claude Sonnet).
TASK_EXAMPLES = {
    "alt": (
        "viết alt cho ảnh",
        'provider = "anthropic", model = "claude-sonnet-5-5", effort = "low", max_tokens = 2000',
    ),
}


def missing_task_message(task_name: str) -> str:
    """Câu báo thiếu mục ``[tasks.<task_name>]`` trong config/ai.toml (tiếng Việt, không sập)."""
    example = TASK_EXAMPLES.get(task_name)
    if example is None:
        return f"config/ai.toml thiếu mục [tasks.{task_name}]."
    label, sample = example
    return (
        f"config/ai.toml chưa có mục [tasks.{task_name}] (mô hình AI dùng để {label}). Mở file "
        f"config/ai.toml, thêm mục [tasks.{task_name}] với {sample} (mỗi thông số một dòng), "
        "lưu lại rồi tải lại trang."
    )


def load_ai_config(path: Path = AI_CONFIG_FILE) -> dict[str, TaskConfig]:
    """Mô hình cho từng việc. Báo ``AIError`` (tiếng Việt) nếu file viết sai."""
    try:
        # "utf-8-sig": nhận cả file UTF-8 có BOM (Notepad đời cũ lưu kiểu này).
        data = tomllib.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        # Chỉ tên file, không lộ đường dẫn đầy đủ trên máy (Lá Chắn LC-T019-2).
        raise AIError(f"Không thấy file cấu hình AI: config/{path.name}.") from exc
    except UnicodeDecodeError as exc:
        raise AIError(
            f"File config/{path.name} không lưu ở dạng UTF-8. Mở lại bằng Notepad, chọn "
            "Lưu thành (Save As) → Mã hóa (Encoding): UTF-8, rồi lưu."
        ) from exc
    except OSError as exc:
        raise AIError(f"Không đọc được file config/{path.name}.") from exc
    except tomllib.TOMLDecodeError as exc:
        raise AIError(f"File {path.name} viết sai cú pháp: {exc}") from exc

    raw_tasks = data.get("tasks", {})
    if not isinstance(raw_tasks, dict):
        raise AIError(f"File {path.name}: mục [tasks] viết sai dạng.")
    tasks: dict[str, TaskConfig] = {}
    for name, raw in raw_tasks.items():
        if not isinstance(raw, dict):
            raise AIError(
                f"File {path.name}: việc «{name}» phải là một mục [tasks.{name}] có provider, "
                "model…"
            )
        provider = str(raw.get("provider", "")).strip().lower()
        if provider not in PROVIDERS:
            raise AIError(f"Việc «{name}»: không biết hãng AI «{provider}».")
        if name == IMAGE_TASK and provider not in IMAGE_PROVIDERS:
            raise AIError(
                f"Việc «{name}»: Claude không tạo được ảnh. Trong mục [tasks.{name}] của "
                'config/ai.toml, ghi provider = "gemini" hoặc provider = "openai".'
            )
        effort = str(raw.get("effort", "medium")).strip().lower()
        if effort not in EFFORTS:
            raise AIError(f"Việc «{name}»: effort phải là một trong {', '.join(EFFORTS)}.")
        model = str(raw.get("model", "")).strip()
        if not model:
            raise AIError(f"Việc «{name}»: chưa ghi tên mô hình (model).")
        tasks[name] = TaskConfig(
            name=name,
            provider=provider,
            model=model,
            effort=effort,
            web_search=_bool_value(name, "web_search", raw.get("web_search", False)),
            max_tokens=_positive_int(name, "max_tokens", raw.get("max_tokens", 16000)),
        )
    return tasks


def _bool_value(task: str, key: str, value: object) -> bool:
    # Chỉ nhận true/false thật của TOML: "false" trong ngoặc kép là chữ, bool("false") lại là True.
    if not isinstance(value, bool):
        raise AIError(f"Việc «{task}»: {key} phải là true hoặc false (không để trong ngoặc kép).")
    return value


def _positive_int(task: str, key: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise AIError(f"Việc «{task}»: {key} phải là số nguyên dương, ví dụ 16000.")
    return value


def make_provider(provider: str, settings: Settings) -> AIProvider:
    """Tạo provider của một hãng. Báo ``AIError`` nếu chưa hỗ trợ hoặc thiếu khóa API."""
    label, key_name = PROVIDERS[provider]
    if provider not in SUPPORTED:
        raise AIError(f'{label} chưa được hỗ trợ. Tạm thời đổi provider = "anthropic".')
    api_key = {
        "anthropic": settings.anthropic_api_key,
        "openai": settings.openai_api_key,
        "gemini": settings.gemini_api_key,
    }[provider]
    if not api_key:
        raise AIError(f"Chưa có khóa {label} ({key_name}). Vào Cài đặt → 🔌 Kết nối để nhập khóa.")
    # Nhập thư viện của hãng khi cần, để app mở nhanh và hãng không dùng thì không phải tải.
    # Thư viện cài sai phiên bản (nâng ngoài uv.lock) thì báo tiếng Việt, không làm sập trang:
    # lúc nhập (thiếu module, thiếu hằng như types.ThinkingLevel) lẫn lúc tạo client (đổi tham
    # số; google-genai kiểm tham số bằng pydantic nên tham số lạ ra ValidationError).
    try:
        if provider == "anthropic":
            from seo_app.ai.anthropic_provider import AnthropicProvider as cls
        elif provider == "openai":
            from seo_app.ai.openai_provider import OpenAIProvider as cls
        else:
            from seo_app.ai.gemini_provider import GeminiProvider as cls
        return cls(api_key)
    except SETUP_ERRORS as exc:
        raise library_error(label) from exc


class AIRouter:
    """Chọn đúng provider + cấu hình cho từng việc (nghiên cứu, viết, rà soát…).

    Provider của mỗi hãng chỉ tạo một lần, khi một việc dùng hãng đó được gọi lần đầu (lười), nên
    thiếu khóa của một hãng chỉ báo ``AIError`` khi gọi đúng việc dùng hãng đó. Riêng các việc
    trong ``prepare`` (mặc định ``WRITING_TASKS``) được tạo ngay lúc dựng: thiếu khóa hay thư viện
    hỏng thì báo ở đây, trang Soạn bài khóa các nút AI. Trang chỉ dùng việc khác (ví dụ viết alt)
    truyền ``prepare=()`` hoặc đúng việc của trang, để không đòi khóa của các việc viết bài.
    """

    def __init__(
        self,
        tasks: dict[str, TaskConfig],
        settings: Settings,
        prepare: Iterable[str] = WRITING_TASKS,
    ) -> None:
        self.tasks = tasks
        self._settings = settings
        self._providers: dict[str, AIProvider] = {}
        for name in prepare:
            if name in tasks:
                self._provider(tasks[name])

    def _provider(self, task: TaskConfig) -> AIProvider:
        provider = self._providers.get(task.provider)
        if provider is None:
            # Lỗi (thiếu khóa, thư viện hỏng) không được nhớ: lần gọi sau thử tạo lại.
            provider = make_provider(task.provider, self._settings)
            self._providers[task.provider] = provider
        return provider

    def get(self, task_name: str) -> tuple[AIProvider, TaskConfig]:
        if task_name not in self.tasks:
            raise AIError(missing_task_message(task_name))
        task = self.tasks[task_name]
        return self._provider(task), task
