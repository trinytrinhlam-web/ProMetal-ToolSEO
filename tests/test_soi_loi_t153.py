"""Soi Lỗi T-153 (rút gọn): chữ cấu hình cho prompt ảnh chi tiết.

- Mục ``[image_prompt]`` mới của ``config/content.toml`` không đổi kết quả các bộ đọc cũ.
- Việc mới ``[tasks.image_prompt]`` (đang bật) không bắt trang Soạn bài nhập thêm khóa.
- Lỗi mới: ``xfail(strict=True)`` mã ``SL-T153-n``.

Không gọi AI, Cloudflare: chỉ đọc file cấu hình.
"""

from __future__ import annotations

import re
import tomllib
from dataclasses import replace

import pytest
import test_t153_cau_hinh_anh as t153

from seo_app.ai import AIError, AIRouter
from seo_app.ai import registry as ai_registry
from seo_app.config import Settings
from seo_app.content.rules import (
    CONTENT_CONFIG_FILE,
    load_alt_rules,
    load_image_settings,
    load_meta_rules,
    load_rules,
)

WRITING_TASKS = ("research", "outline", "write", "rewrite", "review")
BLOCK_START = "# LƯU Ý: quy tắc (rules) và ví dụ ([[image_prompt.examples]]"
BLOCK_END = "# LƯU Ý (T-103"
POSITION = r"(?:Foreground|Midground|Background) (?:left|center|right): ([^.]+)\."


def _content_text() -> str:
    return CONTENT_CONFIG_FILE.read_text(encoding="utf-8")


def _image_prompt() -> dict:
    return tomllib.loads(_content_text())["image_prompt"]


# ====================================================================== [image_prompt]
def test_muc_image_prompt_khong_doi_ket_qua_cac_bo_doc_cu(tmp_path):
    """Bỏ hẳn khối ``[image_prompt]`` (kể cả ghi chú đầu khối) thì mọi bộ đọc cũ cho kết quả y
    hệt: mục mới không lọt vào lời dặn viết bài, alt, meta, cài đặt ảnh, giờ đăng mặc định."""
    text = _content_text()
    start, end = text.index(BLOCK_START), text.index(BLOCK_END)
    without = tmp_path / "content.toml"
    without.write_text(text[:start] + text[end:], encoding="utf-8")
    assert "image_prompt" not in tomllib.loads(without.read_text(encoding="utf-8"))
    assert load_rules(CONTENT_CONFIG_FILE) == load_rules(without)
    assert load_alt_rules(CONTENT_CONFIG_FILE) == load_alt_rules(without)
    assert load_meta_rules(CONTENT_CONFIG_FILE) == load_meta_rules(without)
    assert load_image_settings(CONTENT_CONFIG_FILE) == load_image_settings(without)
    plan = tomllib.loads(text)["plan"]
    assert plan == tomllib.loads(without.read_text(encoding="utf-8"))["plan"]


def _image_prompt_on(provider: str, model: str, text: str) -> str:
    """Chữ ai.toml với mục ``[tasks.image_prompt]`` đổi sang ``provider``, ``model``."""
    rows = text.split("\n")
    head = rows.index(next(r for r in rows if r.startswith("[tasks.image_prompt]")))
    end = next((i for i in range(head + 1, len(rows)) if rows[i].startswith("[")), len(rows))
    for i in range(head + 1, end):
        if rows[i].startswith("provider = "):
            rows[i] = f'provider = "{provider}"'
        elif rows[i].startswith("model = "):
            rows[i] = f'model = "{model}"'
    return "\n".join(rows)


def test_viec_image_prompt_khong_bat_nhap_khoa_khi_viet_bai_bang_hang_khac(tmp_path):
    """Chủ dự án quay lại Claude cho các việc viết (ghi chú T-138) mà việc ``image_prompt`` còn ở
    Gemini: trang Soạn bài (``AIRouter`` dựng sẵn 5 việc viết) không đòi khóa Gemini; chỉ khi gọi
    đúng việc ``image_prompt`` mới báo thiếu khóa, câu tiếng Việt."""
    text = ai_registry.AI_CONFIG_FILE.read_text(encoding="utf-8")
    rows = []
    for row in text.split("\n"):
        if row.startswith("provider = "):
            row = 'provider = "anthropic"'
        elif row.startswith("model = "):
            row = 'model = "claude-opus-5-5"'
        rows.append(row)
    path = tmp_path / "ai.toml"
    path.write_text(_image_prompt_on("gemini", "gemini-3.8-flash", "\n".join(rows)), "utf-8")
    tasks = ai_registry.load_ai_config(path)
    assert tasks["image_prompt"].provider == "gemini"
    assert {tasks[name].provider for name in WRITING_TASKS} == {"anthropic"}
    router = AIRouter(tasks, Settings(anthropic_api_key="khoa-gia-soi-loi-t153"))
    for name in WRITING_TASKS:
        router.get(name)
    with pytest.raises(AIError, match="Gemini"):
        router.get("image_prompt")


# ====================================================================== lỗi mới
@pytest.mark.xfail(
    strict=True,
    reason="SL-T153-1: luật «Màu chủ đạo… dưới 25 ký tự» kèm ví dụ 27 ký tự; màu của cả 3 ví dụ "
    "tốt 25–27 ký tự; chi tiết phụ của ví dụ 1 đúng 35 ký tự (luật «dưới 35»)",
)
def test_sl_t153_1_vi_du_theo_dung_muc_cua_luat():
    """Luật xin mỗi trường ngắn hơn trần mã (AI đếm ký tự không chính xác). Ví dụ trong chính luật
    và ví dụ tốt phải theo đúng mức «dưới N ký tự» đó, không thì AI học theo ví dụ vượt mức."""
    section = _image_prompt()
    color_rule = next(r for r in section["rules"] if r.startswith("Màu chủ đạo"))
    detail_rule = next(r for r in section["rules"] if r.startswith("Chi tiết phụ"))
    color_limit = int(re.search(r"dưới (\d+) ký tự", color_rule).group(1))
    detail_limit = int(re.search(r"dưới (\d+) ký tự", detail_rule).group(1))
    colors = re.findall(r"«([^»]+)»", color_rule)
    colors += [re.search(r"Colors: (.+)\.$", ex["tot"]).group(1) for ex in section["examples"]]
    details = [d for ex in section["examples"] for d in re.findall(POSITION, ex["tot"])]
    too_long = [c for c in colors if len(c) >= color_limit]
    too_long += [d for d in details if len(d) >= detail_limit]
    assert too_long == []


def _t142_style_loader(real_loader, folder):
    """Bộ đọc ``config/ai.toml`` theo hợp đồng của T-142 (đã qua Lá Chắn, chờ gộp): hãng
    «cloudflare» chỉ nhận ở ``[tasks.image]``, nằm trong ``IMAGE_ONLY_PROVIDERS``, **không** trong
    ``PROVIDERS``. Phần còn lại đọc bằng bộ đọc thật."""

    def load(path=ai_registry.AI_CONFIG_FILE):
        text = path.read_text(encoding="utf-8")
        image = tomllib.loads(text).get("tasks", {}).get("image", {})
        if image.get("provider") != "cloudflare":
            return real_loader(path)
        swapped = folder / "ai-swapped.toml"
        swapped.write_text(text.replace('provider = "cloudflare"', 'provider = "gemini"'), "utf-8")
        tasks = real_loader(swapped)
        tasks["image"] = replace(tasks["image"], provider="cloudflare")
        return tasks

    return load


@pytest.mark.xfail(
    strict=True,
    reason="SL-T153-2: test_enabled_cloudflare_block_loads_once_the_provider_exists rẽ nhánh theo "
    "PROVIDERS; T-142 thêm «cloudflare» vào IMAGE_ONLY_PROVIDERS nên gộp hai nhánh thì ca này hỏng",
)
def test_sl_t153_2_ca_bat_khoi_cloudflare_van_qua_khi_da_co_t142(tmp_path, monkeypatch):
    """Gộp thử thật ``team/T-153`` + ``team/T-142``: ca này hỏng «DID NOT RAISE AIError». Ở đây
    dựng lại đúng hợp đồng của T-142 (hãng chỉ tạo ảnh) rồi chạy ca của Ngòi Bút."""
    monkeypatch.setattr(
        ai_registry,
        "IMAGE_ONLY_PROVIDERS",
        {"cloudflare": ("Cloudflare Workers AI", "CLOUDFLARE_API_TOKEN")},
        raising=False,
    )
    monkeypatch.setattr(
        ai_registry, "IMAGE_PROVIDERS", (*ai_registry.IMAGE_PROVIDERS, "cloudflare")
    )
    loader = _t142_style_loader(ai_registry.load_ai_config, tmp_path)
    monkeypatch.setattr(ai_registry, "load_ai_config", loader)
    assert "cloudflare" not in ai_registry.PROVIDERS  # như T-142
    folder = tmp_path / "ca-ngoi-but"
    folder.mkdir()
    t153.test_enabled_cloudflare_block_loads_once_the_provider_exists(folder)
