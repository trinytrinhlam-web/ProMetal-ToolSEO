"""Cấu hình AI mẫu cho test (T-138).

Chủ dự án đổi hãng AI theo từng lúc (2026-11-18: tạm Gemini Flash cho mọi việc, phiếu T-138), nên
test kiểm **điều bảo vệ**, không ghim hãng đang ghi trong ``config/ai.toml`` đã commit:

- ``configured_key_envs`` / ``set_configured_keys``: biến khóa của các hãng mà các việc (trừ tạo
  ảnh) đang dùng; trang Soạn bài chỉ được đòi đúng các khóa này.
- ``ai_text_on``: chữ ``config/ai.toml`` với mọi việc đang bật chuyển sang một hãng. Dùng làm bản
  mẫu trong ``tmp_path``, ví dụ «viết bài bằng Claude, tạo ảnh bằng Gemini» để thử khóa Gemini chỉ
  bị đòi khi gọi việc ảnh (điều bảo vệ của T-062), dù file đã commit đang dùng hãng nào.
- ``research_web_search_toml``: bản mẫu ``config/ai.toml`` với bước nghiên cứu bật hay tắt tìm web,
  để kiểm điều chỉ có khi bật (bài đối thủ hiện trên trang) dù file đã commit đang tắt.
"""

from __future__ import annotations

from pathlib import Path

from seo_app.ai import registry as ai_registry
from seo_app.ai.registry import IMAGE_TASK

ENV_KEYS = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
}
SAMPLE_MODELS = {
    "anthropic": "claude-opus-5-5",
    "openai": "gpt-5.1",
    "gemini": "gemini-3.8-flash",
}


def configured_providers(path: Path | None = None) -> set[str]:
    """Các hãng mà các việc (trừ tạo ảnh) trong cấu hình đang dùng. ``path`` ``None``: file mà
    ``load_ai_config`` đang đọc (kể cả khi test đã đổi giá trị mặc định của nó)."""
    load = ai_registry.load_ai_config
    tasks = load() if path is None else load(path)
    return {task.provider for name, task in tasks.items() if name != IMAGE_TASK}


def configured_key_envs(path: Path | None = None) -> set[str]:
    return {ENV_KEYS[provider] for provider in configured_providers(path)}


def set_configured_keys(monkeypatch, value: str, path: Path | None = None) -> set[str]:
    """Đặt khóa giả ``value`` cho đúng các hãng đang được cấu hình; trả tên các biến đã đặt."""
    names = configured_key_envs(path)
    for name in names:
        monkeypatch.setenv(name, value)
    return names


def ai_text_on(provider: str, text: str | None = None, model: str | None = None) -> str:
    """Chữ ``config/ai.toml`` (hay ``text``) với mọi dòng ``provider = …``, ``model = …`` đang bật
    (không có dấu # đầu dòng) đổi sang ``provider`` và ``model`` (mặc định ``SAMPLE_MODELS``). Khối
    ``[tasks.image]`` đang tắt giữ nguyên để test tự bật."""
    if text is None:
        text = ai_registry.AI_CONFIG_FILE.read_text(encoding="utf-8")
    model = model or SAMPLE_MODELS[provider]
    rows = []
    for row in text.split("\n"):
        if row.startswith("provider = "):
            row = f'provider = "{provider}"'
        elif row.startswith("model = "):
            row = f'model = "{model}"'
        rows.append(row)
    return "\n".join(rows)


def research_web_search_toml(tmp_path: Path, on: bool, text: str | None = None) -> Path:
    """Ghi ``tmp_path/ai.toml``: chữ ``config/ai.toml`` (hay ``text``) với khối
    ``[tasks.research]`` chỉ còn một dòng ``web_search`` bật (``on``) hay tắt; các việc khác giữ
    nguyên. Đọc lại để chắc giá trị đã ăn."""
    if text is None:
        text = ai_registry.AI_CONFIG_FILE.read_text(encoding="utf-8")
    rows = text.split("\n")
    head = next(i for i, row in enumerate(rows) if row.startswith("[tasks.research]"))
    end = next((i for i in range(head + 1, len(rows)) if rows[i].startswith("[")), len(rows))
    block = [row for row in rows[head + 1 : end] if not row.startswith("web_search = ")]
    rows[head + 1 : end] = [f"web_search = {'true' if on else 'false'}", *block]
    path = tmp_path / "ai.toml"
    path.write_text("\n".join(rows), encoding="utf-8")
    assert ai_registry.load_ai_config(path)["research"].web_search is on
    return path
