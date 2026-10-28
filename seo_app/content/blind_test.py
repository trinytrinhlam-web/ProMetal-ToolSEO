"""Thử mù mô hình AI (T-019): cùng một đề gửi cho 2-3 mô hình, hiện bài dưới nhãn A/B/C.

Kết quả trả về thành HAI phần riêng:

- ``BlindEntry`` (nhãn + bài): hiện ngay để người dùng chấm. Không chứa tên hãng, tên mô hình
  hay câu lỗi gốc (câu lỗi của lớp AI có ghi tên mô hình).
- ``BlindReveal`` (nhãn → hãng, mô hình, câu lỗi): chỉ hiện sau khi người dùng chấm xong.

Không có hãng mặc định (CLAUDE.md, chốt 2026-10-15): người dùng tự chọn ứng viên.
"""

from __future__ import annotations

import random
import re
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, Field

from seo_app.ai import AIError, TaskConfig, load_ai_config, make_provider
from seo_app.ai.base import EFFORTS, TokenLimitError
from seo_app.ai.registry import AI_CONFIG_FILE, IMAGE_TASK, PROVIDERS
from seo_app.config import Settings
from seo_app.content import prompts
from seo_app.content.rules import ContentRules
from seo_app.sanitize import clean_ai_text

MIN_CANDIDATES = 2
MAX_CANDIDATES = 3
LABELS = ("A", "B", "C")
# Mỗi ứng viên chỉ viết mở bài + một mục ngắn: giới hạn độ dài trả về để thử không tốn nhiều.
BLIND_MAX_TOKENS = 2000
TASK_NAME = "blind_test"
MAX_KEYWORD_CHARS = 200
MAX_NOTE_CHARS = 1000
MAX_MODEL_CHARS = 100

# Câu hiện trong phần bài (trước khi chấm) khi một ứng viên lỗi. Câu lỗi thật nằm ở phần
# hiện tên, vì câu lỗi của lớp AI có ghi tên hãng và mô hình.
HIDDEN_ERROR = (
    "Ứng viên này gặp lỗi nên chưa có bài. Câu báo lỗi (có tên hãng, tên mô hình) hiện sau khi "
    "bấm hiện tên mô hình."
)
UNEXPECTED_ERROR = "Gặp lỗi không mong đợi khi gọi AI. Thử lại sau ít phút."
# Bài bị cắt vì chạm giới hạn token: giới hạn của thử mù cố định trong code (BLIND_MAX_TOKENS),
# không đọc từ config/ai.toml, nên câu của lớp AI ("tăng max_tokens của việc …") không làm được.
# Mô hình suy nghĩ kỹ tính cả phần suy nghĩ vào giới hạn này, nên hạ effort là cách sửa thật.
TOKEN_LIMIT_ERROR = (
    f"Bài thử dài quá giới hạn {BLIND_MAX_TOKENS} token của phần thử mù (mô hình suy nghĩ càng kỹ "
    "càng dùng nhiều phần giới hạn này). Chọn effort thấp hơn (low hoặc medium) cho ứng viên này "
    "rồi chạy lại."
)
# Không có "[", "]", "(", ")": chữ che chạy SAU ``clean_ai_text`` nên không được ghép thành link.
MASK = "«đã ẩn tên mô hình»"
# Tên mô hình dùng để che: phải có chữ cái, và có chữ số ("o3", "gpt-5.1") hoặc là tên dài có
# "-"/"." ("gemini-flash-latest"). Tên gõ nhầm kiểu "c", "10", "co", "cho", "khi" sẽ che mất chữ
# thường ("Cửa", "của", "cho", "10 năm") trong bài của mọi ứng viên (Soi Lỗi SL-T019-2), nên bị
# từ chối ngay ở ``validate_request`` (xem ``_maskable``). Tên thật của cả 3 hãng đều qua luật này.

# Ký tự được phép trong tên mô hình: đủ cho tên thật của cả 3 hãng ("models/gemini-2.5-pro",
# "ft:gpt-4o-mini:org::abc123", "claude-opus-4@20250514"), không có ký tự Markdown/HTML.
_MODEL_CHARS = re.compile(r"[A-Za-z0-9._:/@-]+")

# Ranh giới trước tên: không đứng sau chữ/số hay "-" (để "o3" không ăn vào giữa từ), nhưng
# ĐƯỢC đứng sau "_" vì Markdown viết nghiêng/đậm bằng gạch dưới (``_Claude_``, ``__Gemini__``;
# Soi Lỗi SL-T019-1). Phía sau che cả đuôi tự thêm ("gpt-5.1-mini", "Claude's") nhưng không ăn
# "_" cuối, để Markdown vẫn đóng đúng.
_BEFORE = r"(?<![^\W_]|-)"
_TAIL = r"(?:[\w.-]*[^\W_])?"
# Tên hãng, công ty, dòng mô hình AI của 3 hãng: bài về cửa sắt không cần tới, nên AI tự xưng
# tên thì che để không lộ ứng viên trước khi chấm. "Google" đứng riêng
# không che (bài hay nói "tìm trên Google"); "Google Gemini", "Google DeepMind"… che cả cụm.
_VENDOR_NAMES = (
    r"google\s+(?:gemini|deepmind|bard|gemma|ai\s+studio)",
    "claude", "anthropic", "opus", "sonnet", "haiku", "fable",
    "openai", "chatgpt", "gpt", "dall-e", "dalle", "sora", "codex",
    "gemini", "gemma", "bard", "deepmind", r"palm[\s-]?2",
)  # fmt: skip
# Số phiên bản / biến thể đứng liền sau tên đã che ("Opus 5.5", "GPT 6.1", "Gemini 3 Pro"): che
# luôn, vì người quen số phiên bản đoán được hãng (Soi Lỗi SL-T019-3). Chỉ xét ngay sau tên
# (cách bằng dấu cách, không qua dòng mới), nên số liệu đứng riêng trong bài ("dày 5.5 mm")
# không bị đụng.
# Mỗi phần có thể kèm đuôi nối bằng gạch ("Flash-Lite", "5.5-preview", "Pro-002"; Soi Lỗi
# SL-T034-1).
_VERSION = (
    r"(?:[^\S\n]+(?:v?\d+(?:[.,]\d+)*(?:[a-z]\b)?|pro|flash|ultra|mini|nano|lite|turbo|max"
    r"|plus|preview|thinking|exp|latest)(?:-[^\W_]+(?:\.\d+)*)*(?![\w.-]*[^\W_]))*"
)
_VENDOR_WORDS = re.compile(
    _BEFORE + "(?:" + "|".join(_VENDOR_NAMES) + ")" + _TAIL + _VERSION, re.IGNORECASE
)

TASK_LABELS = {
    "research": "Nghiên cứu, phân tích đối thủ",
    "outline": "Lập dàn ý",
    "write": "Viết bài",
    "rewrite": "Viết lại từng phần",
    "review": "Kiểm tra văn phong",
    "meta": "Gợi ý meta",
    "links": "Gợi ý liên kết nội bộ",
    "plan": "Đề xuất thay đổi kế hoạch",
    "alt": "Viết alt ảnh",
    "image": "Tạo ảnh AI",
}


class BlindSample(BaseModel):
    """Khuôn AI trả về khi thử mù."""

    intro: str = Field(description="Mở bài 2-4 câu, Markdown")
    heading: str = Field(description="Tiêu đề mục ngắn (H2), một dòng")
    body: str = Field(description="Nội dung mục ngắn, Markdown, không lặp lại tiêu đề")


@dataclass(frozen=True)
class Candidate:
    """Một mô hình dự thi. ``provider``: anthropic | openai | gemini."""

    provider: str
    model: str
    effort: str = "medium"


@dataclass(frozen=True)
class BlindEntry:
    """Bài của một ứng viên, chỉ có nhãn. An toàn để hiện trước khi chấm.

    Chữ đã qua ``clean_ai_text`` nhưng vẫn là chữ AI: hiện bằng ``st.markdown`` / ``st.text``,
    không bao giờ với ``unsafe_allow_html``.
    """

    label: str
    intro: str = ""
    heading: str = ""
    body: str = ""
    error: str | None = None  # câu cố định ``HIDDEN_ERROR`` nếu ứng viên lỗi

    @property
    def ok(self) -> bool:
        return self.error is None


@dataclass(frozen=True)
class BlindReveal:
    """Nhãn → mô hình. Chỉ hiện sau khi người dùng chấm xong."""

    label: str
    provider: str
    provider_label: str
    model: str
    effort: str
    error: str | None = None  # câu lỗi tiếng Việt của ``AIError`` (đã che khóa ở lớp AI)


@dataclass(frozen=True)
class ProviderStatus:
    provider: str
    label: str
    has_key: bool  # chỉ đúng/sai, không bao giờ mang khóa


@dataclass(frozen=True)
class TaskModel:
    """Một dòng bảng việc–mô hình đọc từ ``config/ai.toml``."""

    task: str
    task_label: str
    provider: str
    provider_label: str
    model: str
    effort: str


# ------------------------------------------------------------------ hàm phụ cho giao diện


def provider_status(settings: Settings) -> list[ProviderStatus]:
    """Các hãng và đã khai báo khóa hay chưa (chỉ đúng/sai)."""
    keys = {
        "anthropic": settings.anthropic_api_key,
        "openai": settings.openai_api_key,
        "gemini": settings.gemini_api_key,
    }
    return [
        ProviderStatus(provider=pid, label=label, has_key=bool(keys.get(pid)))
        for pid, (label, _key_name) in PROVIDERS.items()
    ]


def available_providers(settings: Settings) -> list[str]:
    """Mã các hãng đã có khóa (để giao diện chỉ cho chọn trong số này)."""
    return [p.provider for p in provider_status(settings) if p.has_key]


def task_models(path: Path = AI_CONFIG_FILE) -> list[TaskModel]:
    """Bảng việc–mô hình từ ``config/ai.toml``. File sai thì báo ``AIError`` (tiếng Việt)."""
    return [
        TaskModel(
            task=name,
            task_label=TASK_LABELS.get(name, name),
            provider=task.provider,
            provider_label=PROVIDERS[task.provider][0],
            model=task.model,
            effort=task.effort,
        )
        for name, task in load_ai_config(path).items()
    ]


def model_suggestions(rows: Sequence[TaskModel]) -> dict[str, list[str]]:
    """Tên mô hình gợi ý theo hãng, lấy từ bảng việc–mô hình (không trùng, giữ thứ tự).

    Bỏ mô hình của việc tạo ảnh (T-062): mô hình đó không viết bài, thử mù chỉ thử viết bài."""
    out: dict[str, list[str]] = {pid: [] for pid in PROVIDERS}
    for row in rows:
        if row.task == IMAGE_TASK:
            continue
        if row.model not in out[row.provider]:
            out[row.provider].append(row.model)
    return out


def estimate_calls(candidates: Sequence[Candidate]) -> int:
    """Số lần gọi AI (mỗi lần tốn tiền) khi chạy thử mù: mỗi ứng viên một lần."""
    return len(candidates)


# ------------------------------------------------------------------ chạy thử mù


def _one_line(text: str) -> str:
    return " ".join(text.split())


def validate_request(
    keyword: str, note: str, candidates: Sequence[Candidate]
) -> tuple[str, str, list[Candidate]]:
    """Kiểm tra đầu vào trước khi gọi AI. Sai thì báo ``AIError`` (tiếng Việt), chưa tốn tiền."""
    keyword = _one_line(keyword)
    note = note.strip()
    if not keyword:
        raise AIError("Nhập từ khóa để thử.")
    if len(keyword) > MAX_KEYWORD_CHARS:
        raise AIError(f"Từ khóa dài quá {MAX_KEYWORD_CHARS} ký tự.")
    if len(note) > MAX_NOTE_CHARS:
        raise AIError(f"Ghi chú dài quá {MAX_NOTE_CHARS} ký tự.")
    if not MIN_CANDIDATES <= len(candidates) <= MAX_CANDIDATES:
        raise AIError(f"Chọn từ {MIN_CANDIDATES} đến {MAX_CANDIDATES} mô hình để so sánh.")
    clean: list[Candidate] = []
    for i, c in enumerate(candidates, start=1):
        provider = c.provider.strip().lower()
        model = c.model.strip()
        effort = c.effort.strip().lower()
        if provider not in PROVIDERS:
            raise AIError(f"Ứng viên {i}: chưa chọn hãng AI.")
        if not model or len(model) > MAX_MODEL_CHARS or any(ch.isspace() for ch in model):
            raise AIError(f"Ứng viên {i}: tên mô hình trống hoặc viết sai (không có dấu cách).")
        if not _MODEL_CHARS.fullmatch(model):
            # Tên mô hình hiện lại trong câu lỗi (Markdown): chặn ký tự có thể thành link hay định
            # dạng, như "[a1](https://x.y)" (Lá Chắn LC-T019-1).
            raise AIError(
                f"Ứng viên {i}: tên mô hình chỉ gồm chữ không dấu, số và các dấu . _ : / @ -, "
                "ví dụ claude-opus-5-5, gpt-6.1, gemini-3-pro."
            )
        if not _maskable(model):
            raise AIError(
                f"Ứng viên {i}: tên mô hình «{model}» quá ngắn hoặc gõ nhầm. Ghi đúng tên đầy đủ, "
                "ví dụ claude-opus-5-5, gpt-6.1, gemini-3-pro."
            )
        if effort not in EFFORTS:
            raise AIError(f"Ứng viên {i}: effort phải là một trong {', '.join(EFFORTS)}.")
        clean.append(Candidate(provider=provider, model=model, effort=effort))
    return keyword, note, clean


def _maskable(model: str) -> bool:
    """Tên mô hình đủ rõ để che an toàn, không trùng chữ thường của bài.

    Có chữ cái, và: có chữ số ("o3", "4o", "gpt-5.1"), hoặc dài từ 5 ký tự và có "-" / "."
    ("gemini-flash-latest"). Từ trơn như "cho", "khi", "gpt" bị coi là gõ nhầm.
    """
    has_letter = any(ch.isalpha() for ch in model)
    has_digit = any(ch.isdigit() for ch in model)
    has_sep = "-" in model or "." in model
    return has_letter and (has_digit or (len(model) >= 5 and has_sep))


def _mask_names(text: str, models: Sequence[str]) -> str:
    # Chỉ che tên đủ rõ (``_maskable``): tên gõ nhầm quá ngắn không được che chữ thường của bài.
    names = {m for m in models if _maskable(m)}
    for model in sorted(names, key=len, reverse=True):
        text = re.sub(
            _BEFORE + re.escape(model) + _TAIL + _VERSION, MASK, text, flags=re.IGNORECASE
        )
    return _VENDOR_WORDS.sub(MASK, text)


def _call(candidate: Candidate, settings: Settings, system: str, prompt: str) -> BlindSample | str:
    """Gọi một ứng viên. Trả về bài, hoặc câu lỗi tiếng Việt (không bao giờ chép lỗi thô)."""
    task = TaskConfig(
        name=TASK_NAME,
        provider=candidate.provider,
        model=candidate.model,
        effort=candidate.effort,
        web_search=False,
        max_tokens=BLIND_MAX_TOKENS,
    )
    try:
        provider = make_provider(candidate.provider, settings)
        return provider.generate(task, system=system, prompt=prompt, schema=BlindSample)
    except TokenLimitError:
        # Câu của lớp AI bảo sửa mục «blind_test» trong config/ai.toml, mà mục đó không có.
        return TOKEN_LIMIT_ERROR
    except AIError as exc:
        return str(exc)
    except Exception:  # noqa: BLE001 - một ứng viên hỏng không được làm hỏng cả lượt thử
        return UNEXPECTED_ERROR


def run_blind_test(
    keyword: str,
    note: str,
    candidates: Sequence[Candidate],
    settings: Settings,
    rules: ContentRules,
    *,
    rng: random.Random | None = None,
) -> tuple[list[BlindEntry], dict[str, BlindReveal]]:
    """Chạy thử mù. Trả về (bài theo nhãn A/B/C, nhãn → mô hình).

    - Mọi ứng viên nhận cùng system prompt và cùng lời dặn; không tìm web, tối đa
      ``BLIND_MAX_TOKENS``.
    - Thứ tự bị xáo ngẫu nhiên trước khi gắn nhãn.
    - Ứng viên lỗi vẫn có nhãn; các ứng viên khác vẫn có bài.
    - Đầu vào sai thì báo ``AIError`` trước khi gọi AI.
    """
    keyword, note, clean = validate_request(keyword, note, candidates)
    system = prompts.system_prompt(rules)
    prompt = prompts.blind_test_prompt(keyword, note)

    order = list(clean)
    (rng or random.SystemRandom()).shuffle(order)

    # Gọi song song: cả lượt thử chỉ chờ bằng ứng viên chậm nhất.
    with ThreadPoolExecutor(max_workers=len(order)) as pool:
        results = list(pool.map(lambda c: _call(c, settings, system, prompt), order))

    models = [c.model for c in clean]
    entries: list[BlindEntry] = []
    reveal: dict[str, BlindReveal] = {}
    for label, candidate, result in zip(LABELS[: len(order)], order, results, strict=True):
        error = result if isinstance(result, str) else None
        if error is None:
            entries.append(
                BlindEntry(
                    label=label,
                    intro=_mask_names(clean_ai_text(result.intro), models),
                    heading=_mask_names(_one_line(clean_ai_text(result.heading)), models),
                    body=_mask_names(clean_ai_text(result.body), models),
                )
            )
        else:
            entries.append(BlindEntry(label=label, error=HIDDEN_ERROR))
        reveal[label] = BlindReveal(
            label=label,
            provider=candidate.provider,
            provider_label=PROVIDERS[candidate.provider][0],
            model=candidate.model,
            effort=candidate.effort,
            error=error,
        )
    return entries, reveal
