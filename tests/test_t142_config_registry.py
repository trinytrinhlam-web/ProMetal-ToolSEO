"""T-142: cấu hình Cloudflare (``registry.py``, ``config.py``, ``.env.example``; LC-T140-2, -3).

Hãng ``cloudflare`` chỉ cho việc ``image`` và không nằm trong ``PROVIDERS`` (thử mù, «Kiểm tra
khóa» chỉ duyệt hãng viết bài). Thiếu khóa Cloudflare không làm trang Soạn bài đòi khóa (T-062).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import seo_app.ai.registry as ai_registry
from seo_app.ai import cloudflare_images as cf
from seo_app.ai.base import AIError
from seo_app.ai.registry import (
    IMAGE_ONLY_PROVIDERS,
    IMAGE_PROVIDERS,
    IMAGE_TASK,
    PROVIDERS,
    WRITING_TASKS,
    AIRouter,
    load_ai_config,
    make_provider,
    provider_label,
)
from seo_app.config import ENV_VARS, Settings, load_settings
from seo_app.content import blind_test
from tests.fake_cloudflare import ACCOUNT, MA_GIA

KHOA_GIA = "sk-ant-khoa-gia-t142-khong-duoc-hien"
ROOT = Path(__file__).resolve().parents[1]
IMAGE_BLOCK = f'\n[tasks.image]\nprovider = "cloudflare"\nmodel = "{cf.FLUX_SCHNELL}"\nsteps = 4\n'


def _toml(tmp_path, body: str) -> Path:
    path = tmp_path / "ai.toml"
    path.write_text(body, encoding="utf-8")
    return path


def _real_with_cloudflare(tmp_path) -> Path:
    """Bản sao ``config/ai.toml`` thật, thêm một khối ``[tasks.image]`` Cloudflare đang bật."""
    text = ai_registry.AI_CONFIG_FILE.read_text(encoding="utf-8")
    return _toml(tmp_path, text + IMAGE_BLOCK)


# ------------------------------------------------------------------ registry


def test_cloudflare_is_an_image_only_provider_not_a_writing_one():
    assert set(PROVIDERS) == {"anthropic", "openai", "gemini"}
    assert "cloudflare" in IMAGE_PROVIDERS
    assert IMAGE_ONLY_PROVIDERS["cloudflare"] == ("Cloudflare Workers AI", "CLOUDFLARE_API_TOKEN")
    assert provider_label("cloudflare") == "Cloudflare Workers AI"
    assert provider_label("gemini") == PROVIDERS["gemini"][0]
    assert provider_label("la") == "la"


def test_cloudflare_image_block_loads(tmp_path):
    tasks = load_ai_config(_real_with_cloudflare(tmp_path))
    assert tasks[IMAGE_TASK].provider == "cloudflare"
    assert tasks[IMAGE_TASK].model == cf.FLUX_SCHNELL


@pytest.mark.parametrize("task", ["write", "alt", "meta", "research"])
def test_cloudflare_for_any_other_task_is_refused(tmp_path, task):
    path = _toml(tmp_path, f'[tasks.{task}]\nprovider = "cloudflare"\nmodel = "x"\n')
    with pytest.raises(AIError) as info:
        load_ai_config(path)
    assert str(info.value) == (
        f"Việc «{task}»: Cloudflare Workers AI chỉ dùng để tạo ảnh (mục [tasks.image])."
    )


def test_unknown_provider_message_is_unchanged(tmp_path):
    path = _toml(tmp_path, '[tasks.write]\nprovider = "hang-la"\nmodel = "x"\n')
    with pytest.raises(AIError, match="không biết hãng AI «hang-la»"):
        load_ai_config(path)


def test_claude_for_images_is_still_refused(tmp_path):
    path = _toml(tmp_path, '[tasks.image]\nprovider = "anthropic"\nmodel = "claude-x"\n')
    with pytest.raises(AIError, match="Claude không tạo được ảnh"):
        load_ai_config(path)


@pytest.mark.parametrize("steps", [1, 4, 8])
def test_steps_in_range_are_accepted(tmp_path, steps):
    body = f'[tasks.image]\nprovider = "cloudflare"\nmodel = "{cf.FLUX_SCHNELL}"\nsteps = {steps}\n'
    load_ai_config(_toml(tmp_path, body))
    assert cf.load_image_task(tmp_path / "ai.toml").steps == steps


@pytest.mark.parametrize(
    "steps", ["0", "9", "-1", "true", "false", '"4"', "4.5", "[4]"],
    ids=["0", "9", "am", "t", "f", "chu", "thuc", "mang"],
)  # fmt: skip
def test_odd_steps_are_refused_when_loading(tmp_path, steps):
    body = f'[tasks.image]\nprovider = "cloudflare"\nmodel = "{cf.FLUX_SCHNELL}"\nsteps = {steps}\n'
    with pytest.raises(AIError) as info:
        load_ai_config(_toml(tmp_path, body))
    assert str(info.value) == "Việc «image»: steps phải là số nguyên từ 1 đến 8, ví dụ 4."


def test_make_provider_refuses_cloudflare_cleanly():
    with pytest.raises(AIError) as info:
        make_provider("cloudflare", Settings(cloudflare_api_token=MA_GIA))
    assert str(info.value) == "Cloudflare Workers AI chỉ dùng để tạo ảnh minh họa."
    assert MA_GIA not in str(info.value)


def test_router_never_asks_for_cloudflare_when_writing(tmp_path):
    tasks = load_ai_config(_real_with_cloudflare(tmp_path))
    router = AIRouter(tasks, Settings(anthropic_api_key=KHOA_GIA))  # không khóa Cloudflare
    for name in (*WRITING_TASKS, "meta", "alt"):
        router.get(name)
    with pytest.raises(AIError, match="chỉ dùng để tạo ảnh"):
        router.get(IMAGE_TASK)


def test_blind_test_table_shows_cloudflare_row_and_skips_it_in_suggestions(tmp_path):
    rows = blind_test.task_models(_real_with_cloudflare(tmp_path))
    image = next(row for row in rows if row.task == IMAGE_TASK)
    assert image.provider_label == "Cloudflare Workers AI"
    suggestions = blind_test.model_suggestions(rows)
    assert "cloudflare" not in suggestions
    assert cf.FLUX_SCHNELL not in [m for models in suggestions.values() for m in models]
    statuses = blind_test.provider_status(Settings(cloudflare_api_token=MA_GIA))
    assert [s.provider for s in statuses] == list(PROVIDERS)


# ------------------------------------------------------------------ .env, Settings


def test_settings_read_cloudflare_values_and_hide_them():
    settings = load_settings(
        None, environ={"CLOUDFLARE_ACCOUNT_ID": ACCOUNT, "CLOUDFLARE_API_TOKEN": MA_GIA}
    )
    assert settings.cloudflare_account_id == ACCOUNT
    assert settings.cloudflare_api_token == MA_GIA
    assert MA_GIA not in repr(settings)
    assert ACCOUNT not in repr(settings)
    assert {"CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_API_TOKEN"} <= set(ENV_VARS)


def test_odd_account_value_does_not_break_settings():
    settings = load_settings(None, environ={"CLOUDFLARE_ACCOUNT_ID": "SAI DANG ../"})
    assert settings.cloudflare_account_id == "SAI DANG ../"  # kiểm lúc tạo client, không ở đây
    with pytest.raises(cf.CloudflareImageError):
        cf.CloudflareImageClient.from_settings(
            load_settings(
                None,
                environ={"CLOUDFLARE_ACCOUNT_ID": "SAI DANG ../", "CLOUDFLARE_API_TOKEN": MA_GIA},
            )
        )


@pytest.mark.parametrize("name", ["CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_API_TOKEN"])
def test_env_example_explains_each_cloudflare_variable(name):
    lines = (ROOT / ".env.example").read_text(encoding="utf-8").splitlines()
    index = lines.index(f"{name}=")  # không có giá trị
    assert lines[index - 1].startswith("# ")  # có chú thích ngay trên
    text = "\n".join(lines)
    assert "Workers AI Read" in text
    assert "My Profile" in text
    assert re.search(r"Workers Free", text)


# ------------------------------------------------------------------ trang (AppTest)


def test_write_page_does_not_ask_for_cloudflare_key(project_root, tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setenv("ANTHROPIC_API_KEY", KHOA_GIA)
    monkeypatch.setattr(
        ai_registry.load_ai_config, "__defaults__", (_real_with_cloudflare(tmp_path),)
    )
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.session_state["authenticated"] = True
    at.switch_page("views/write.py").run()
    assert not at.exception
    shown = [w.value for w in at.warning] + [e.value for e in at.error]
    assert not [text for text in shown if "CLOUDFLARE" in text or "Cloudflare" in text]
    at.text_input(key="keyword").input("sửa cửa cuốn bị kẹt").run()
    analyze = next(b for b in at.button if b.label == "🔎 Phân tích từ khóa")
    assert not analyze.disabled


def test_settings_page_lists_the_cloudflare_image_task(project_root, tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setenv("ANTHROPIC_API_KEY", KHOA_GIA)
    path = _real_with_cloudflare(tmp_path)
    monkeypatch.setattr(ai_registry.load_ai_config, "__defaults__", (path,))
    monkeypatch.setattr(blind_test.task_models, "__defaults__", (path,))
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.session_state["authenticated"] = True
    at.switch_page("views/settings.py").run()
    assert not at.exception
    tables = [frame.value.to_string() for frame in at.dataframe]
    assert any("Cloudflare Workers AI" in table for table in tables)
