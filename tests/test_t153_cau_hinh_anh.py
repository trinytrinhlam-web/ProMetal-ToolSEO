"""T-153: chữ cấu hình cho prompt ảnh chi tiết (mục ``[image_prompt]`` của config/content.toml),
việc ``[tasks.image_prompt]`` và khối ``[tasks.image]`` Cloudflare đang tắt trong config/ai.toml.

Không gọi AI, Cloudflare: chỉ đọc file cấu hình. Bộ kiểm prompt dưới đây là bản thử theo LC-T140-9
(mã thật ở T-145); ví dụ tốt phải qua, ví dụ xấu phải trượt. Báo cáo:
``docs/team/reports/T-153-ngoi-but.md``.
"""

from __future__ import annotations

import re
import tomllib
import unicodedata

import pytest

from seo_app.ai import registry as ai_registry
from seo_app.ai.base import AIError
from seo_app.content.blind_test import TASK_LABELS
from seo_app.content.rules import CONTENT_CONFIG_FILE
from seo_app.images.tags import AREAS
from seo_app.onpage.meta import has_link
from seo_app.plan.model import personal_info

# Từ «vẽ chữ» bị cấm trong prompt (LC-T140-9), so cả từ, không phân biệt hoa thường.
BANNED = ("text", "caption", "watermark", "logo", "banner", "label", "lettering", "typography",
          "phone", "website", "address", "brand")  # fmt: skip
# Trần của thiết kế T-141 1.10 / phiếu T-145: phần AI viết ≤ 600 ký tự; tóm tắt ≤ 140; từng trường.
AI_PART_MAX, SUMMARY_MAX = 600, 140
FIELD_CAPS = {"Vật chính": 80, "Cỡ, chất liệu, màu": 60, "Tình trạng hư": 80, "Chi tiết phụ": 40,
              "Bối cảnh": 60, "Màu chủ đạo": 30, "Dòng tóm tắt": 140}  # fmt: skip
IMAGE_LINES = ('[tasks.image]', 'provider = "cloudflare"',
               'model = "@cf/black-forest-labs/flux-1-schnell"', "steps = 4")  # fmt: skip


def _fold(text: str) -> str:
    text = text.replace("đ", "d").replace("Đ", "D")
    text = "".join(c for c in unicodedata.normalize("NFD", text) if not unicodedata.combining(c))
    return " ".join(re.sub(r"[^0-9a-z]+", " ", text.casefold()).split())


AREA_KEYS = tuple(key for key in (_fold(area) for area in AREAS) if key)


def prompt_problems(text: str) -> list[str]:
    """Bản thử của bộ kiểm LC-T140-9 trên chữ prompt tiếng Anh."""
    found = []
    if any(ch in text for ch in ("\n", "\r", chr(0x2028), chr(0x2029))):
        found.append("nhiều dòng")
    if not text.isprintable() or any(unicodedata.category(c) == "Cf" for c in text):
        found.append("ký tự không in được")
    if re.search(r"\d", text):
        found.append("chữ số")
    if has_link(text) or personal_info(text) != (0, 0):
        found.append("link, email, số điện thoại")
    folded = f" {_fold(text)} "
    if any(name in folded for name in (" pro metal ", "prometal", "suachuacuasat")):
        found.append("tên doanh nghiệp, tên miền")
    found += [f"khu vực {key}" for key in AREA_KEYS if f" {key} " in folded]
    words = set(re.findall(r"[a-z]+", text.casefold()))
    found += [f"từ cấm {word}" for word in BANNED if word in words]
    return found


def _image_prompt() -> dict:
    return tomllib.loads(CONTENT_CONFIG_FILE.read_text(encoding="utf-8"))["image_prompt"]


def _examples() -> list[dict]:
    return _image_prompt()["examples"]


def _ai_text() -> str:
    return ai_registry.AI_CONFIG_FILE.read_text(encoding="utf-8")


# =========================================================== [image_prompt] (content.toml)


def test_image_prompt_section_shape():
    section = _image_prompt()
    assert set(section) == {"rules", "examples"}
    assert section["rules"] and all(isinstance(r, str) and r.strip() for r in section["rules"])
    assert len(section["examples"]) >= 2
    for example in section["examples"]:
        assert set(example) == {"mo_ta", "tot", "tom_tat", "xau", "vi_sao"}
        assert all(isinstance(v, str) and v.strip() for v in example.values())


@pytest.mark.parametrize("index", range(3), ids=["vi-du-1", "vi-du-2", "vi-du-3"])
def test_good_example_passes_prompt_checks(index):
    """Yêu cầu 8: phần AI viết của ví dụ tốt qua bộ kiểm LC-T140-9 và trong ngân sách; phần mã
    gắn thêm (kiểu ảnh, mệnh đề, đuôi) ≤ 300 ký tự nên cả prompt ≤ 900. Tóm tắt ≤ 140, không link,
    không số điện thoại."""
    example = _examples()[index]
    assert prompt_problems(example["tot"]) == []
    assert len(example["tot"]) <= AI_PART_MAX
    summary = example["tom_tat"]
    assert len(summary) <= SUMMARY_MAX and "\n" not in summary
    assert not has_link(summary) and personal_info(summary) == (0, 0)


@pytest.mark.parametrize("index", range(3), ids=["vi-du-1", "vi-du-2", "vi-du-3"])
def test_bad_example_breaks_a_rule_and_is_labelled(index):
    """C4 của T-051: bản xấu có nhãn «Không nên viết» kèm lý do; bản xấu thật sự sai luật (bộ kiểm
    bắt, hay viết phủ định gợi mô hình vẽ chữ)."""
    example = _examples()[index]
    assert example["vi_sao"].startswith("Không nên viết:")
    negated = re.search(r"\bno (text|logo|watermark)\b", example["xau"], re.IGNORECASE)
    assert prompt_problems(example["xau"]) or negated


def test_rule_limits_are_under_the_code_caps():
    """Số «dưới N ký tự» trong luật nhỏ hơn trần mã của trường đó: AI đếm không chính xác."""
    rules = _image_prompt()["rules"]
    for field, cap in FIELD_CAPS.items():
        rule = next(r for r in rules if field in r)
        limit = int(re.search(r"dưới (\d+) ký tự", rule).group(1))
        assert limit < cap, (field, limit, cap)


def test_rules_and_examples_have_no_real_contact():
    text = "\n".join([*_image_prompt()["rules"], *(v for e in _examples() for v in e.values())])
    squeezed = re.sub(r"[\s.\-()]", "", text)
    assert re.findall(r"(?:\+?84|0)\d{8,10}", squeezed) == []
    assert "suachuacuasat" not in text.casefold()


def test_image_prompt_section_sits_before_plan_and_meta_notes():
    """Đặt trước khối «LƯU Ý (T-103» của ``[plan]`` và trước ``[meta]``: test T-040, T-041, T-103
    cắt file theo các khối đó."""
    text = CONTENT_CONFIG_FILE.read_text(encoding="utf-8")
    start = text.index("\n[image_prompt]\n")
    assert text.index("[[alt.examples]]") < start < text.index("# LƯU Ý (T-103")
    above = text[:start].rsplit("\n\n", 1)[1].casefold()
    assert "nguyên văn" in above and "hãng ai" in above and "bịa" in above


# =========================================================== config/ai.toml


def test_image_prompt_task_is_on_with_gemini_flash():
    """Yêu cầu 9: việc mới đang bật, như các việc khác (Gemini Flash), effort thấp, max_tokens
    khoảng 8.000 (LC-T141-19); có nhãn tiếng Việt (bất biến SL-T051-3)."""
    task = ai_registry.load_ai_config()["image_prompt"]
    assert (task.provider, task.model, task.effort, task.max_tokens, task.web_search) == (
        "gemini",
        "gemini-3.8-flash",
        "low",
        8000,
        False,
    )
    assert TASK_LABELS["image_prompt"]


def _image_start(rows: list[str]) -> int:
    return next(i for i, row in enumerate(rows) if row.lstrip("# ").startswith("[tasks.image]"))


def _image_block(text: str) -> list[str]:
    rows = text.split("\n")
    start = _image_start(rows)
    return rows[start : start + len(IMAGE_LINES)]


def test_image_block_is_cloudflare_and_still_off():
    """Yêu cầu 9, LC-T140-17: khối Cloudflare để dấu #, ghi «chỉ bật sau lần gọi thử»; bỏ các dòng
    Gemini «CHƯA XÁC MINH»; chú thích nêu đúng 4 dòng phải xóa dấu #."""
    text = _ai_text()
    block = _image_block(text)
    assert all(row.startswith("# ") for row in block)
    assert [row.lstrip("# ").split("  #")[0].rstrip() for row in block] == list(IMAGE_LINES)
    parsed = tomllib.loads("\n".join(row.lstrip("# ") for row in block))
    assert parsed == {"tasks": {"image": {"provider": "cloudflare",
                                          "model": "@cf/black-forest-labs/flux-1-schnell",
                                          "steps": 4}}}  # fmt: skip
    flat = " ".join(line.lstrip("#").strip() for line in text.splitlines())
    assert "CHỈ BẬT SAU LẦN GỌI THỬ CÙNG CHỦ DỰ ÁN" in flat
    assert "dấu # ở 4 dòng [tasks.image], provider, model, steps" in flat
    assert "CHƯA XÁC MINH" not in text and "gemini-nano" not in text
    assert "image" not in ai_registry.load_ai_config()


def test_enabled_cloudflare_block_loads_once_the_provider_exists(tmp_path):
    """Bỏ dấu # theo chú thích: khi lớp AI đã có hãng «cloudflare» (T-142) thì đọc được đúng khối;
    trước đó báo câu tiếng Việt, không sập."""
    rows = _ai_text().split("\n")
    start = _image_start(rows)
    for i in range(start, start + len(IMAGE_LINES)):
        rows[i] = rows[i].lstrip("# ")
    path = tmp_path / "ai.toml"
    path.write_text("\n".join(rows), encoding="utf-8")
    if "cloudflare" in ai_registry.PROVIDERS:
        image = ai_registry.load_ai_config(path)["image"]
        assert image.provider == "cloudflare"
        assert image.model == "@cf/black-forest-labs/flux-1-schnell"
    else:
        with pytest.raises(AIError, match="không biết hãng AI «cloudflare»"):
            ai_registry.load_ai_config(path)
