"""Đọc ``config/ai.toml`` và tạo provider cho từng việc."""

from __future__ import annotations

import tomllib
from pathlib import Path

from seo_app.ai.base import EFFORTS, AIError, AIProvider, TaskConfig
from seo_app.config import PROJECT_ROOT, Settings

AI_CONFIG_FILE = PROJECT_ROOT / "config" / "ai.toml"

# Tên hãng trong config -> (tên hiển thị, tên biến khóa API trong .env)
PROVIDERS = {
    "anthropic": ("Anthropic (Claude)", "ANTHROPIC_API_KEY"),
    "openai": ("OpenAI", "OPENAI_API_KEY"),
    "gemini": ("Google Gemini", "GEMINI_API_KEY"),
}
SUPPORTED = {"anthropic"}


def load_ai_config(path: Path = AI_CONFIG_FILE) -> dict[str, TaskConfig]:
    """Mô hình cho từng việc. Báo ``AIError`` (tiếng Việt) nếu file viết sai."""
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AIError(f"Không thấy file cấu hình AI: {path}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise AIError(f"File {path.name} viết sai cú pháp: {exc}") from exc

    tasks: dict[str, TaskConfig] = {}
    for name, raw in data.get("tasks", {}).items():
        provider = str(raw.get("provider", "")).strip().lower()
        if provider not in PROVIDERS:
            raise AIError(f"Việc «{name}»: không biết hãng AI «{provider}».")
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
            web_search=bool(raw.get("web_search", False)),
            max_tokens=int(raw.get("max_tokens", 16000)),
        )
    return tasks


def make_provider(provider: str, settings: Settings) -> AIProvider:
    """Tạo provider của một hãng. Báo ``AIError`` nếu chưa hỗ trợ hoặc thiếu khóa API."""
    label, key_name = PROVIDERS[provider]
    if provider not in SUPPORTED:
        raise AIError(f'{label} chưa được hỗ trợ. Tạm thời đổi provider = "anthropic".')
    if provider == "anthropic":
        if not settings.anthropic_api_key:
            raise AIError(f"Chưa có {key_name} trong file .env.")
        from seo_app.ai.anthropic_provider import AnthropicProvider

        return AnthropicProvider(settings.anthropic_api_key)
    raise AIError(f"{label} chưa được hỗ trợ.")  # pragma: no cover


class AIRouter:
    """Chọn đúng provider + cấu hình cho từng việc (nghiên cứu, viết, rà soát…)."""

    def __init__(self, tasks: dict[str, TaskConfig], settings: Settings) -> None:
        self.tasks = tasks
        self._providers: dict[str, AIProvider] = {}
        for task in tasks.values():
            if task.provider not in self._providers:
                self._providers[task.provider] = make_provider(task.provider, settings)

    def get(self, task_name: str) -> tuple[AIProvider, TaskConfig]:
        if task_name not in self.tasks:
            raise AIError(f"config/ai.toml thiếu mục [tasks.{task_name}].")
        task = self.tasks[task_name]
        return self._providers[task.provider], task
