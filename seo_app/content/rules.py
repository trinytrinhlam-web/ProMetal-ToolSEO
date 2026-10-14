"""Quy tắc nội dung (``config/content.toml``), hồ sơ doanh nghiệp và các kiểm tra không cần AI."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

from seo_app.config import PROJECT_ROOT

CONTENT_CONFIG_FILE = PROJECT_ROOT / "config" / "content.toml"
BUSINESS_PROFILE_FILE = PROJECT_ROOT / "config" / "business_profile.md"
# Dòng mang nhãn này trong hồ sơ doanh nghiệp chưa được chủ dự án xác nhận: AI không được dùng.
UNCONFIRMED_TAG = "[CẦN XÁC NHẬN"

# Chỗ AI để trống vì thiếu dữ liệu thật, ví dụ: [cần bổ sung: giá cổng 4 m của xưởng]
MISSING_PATTERN = re.compile(r"\[cần bổ sung:[^\]]*\]", re.IGNORECASE)
_SENTENCE_END = re.compile(r"(?<=[.!?…])\s+|\n+")


@dataclass(frozen=True)
class ContentRules:
    business_profile: str
    address: str
    tone: str
    banned: tuple[str, ...]
    checklist: tuple[str, ...]


def confirmed_profile(text: str) -> str:
    """Hồ sơ doanh nghiệp đã bỏ các dòng còn nhãn [CẦN XÁC NHẬN] và phần chú thích đầu file."""
    lines = [
        line
        for line in text.splitlines()
        if UNCONFIRMED_TAG not in line.upper() and not line.startswith(">")
    ]
    return "\n".join(lines).strip()


def load_rules(
    path: Path = CONTENT_CONFIG_FILE, profile_path: Path = BUSINESS_PROFILE_FILE
) -> ContentRules:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    voice = data.get("voice", {})
    profile = (
        confirmed_profile(profile_path.read_text(encoding="utf-8"))
        if profile_path.is_file()
        else ""
    )
    return ContentRules(
        business_profile=profile,
        address=str(voice.get("address", "")),
        tone=str(voice.get("tone", "")),
        banned=tuple(str(p) for p in voice.get("banned", [])),
        checklist=tuple(str(c) for c in data.get("review", {}).get("checklist", [])),
    )


def sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_END.split(text) if s.strip()]


def find_banned(text: str, banned: tuple[str, ...] | list[str]) -> list[tuple[str, str]]:
    """Các câu chứa cụm từ cấm: [(câu, cụm từ)]. Không phân biệt hoa thường."""
    found = []
    for sentence in sentences(text):
        lower = sentence.lower()
        for phrase in banned:
            if phrase.lower() in lower:
                found.append((sentence, phrase))
                break
    return found


def find_missing(text: str) -> list[str]:
    """Các chỗ «[cần bổ sung: …]» còn trong bài."""
    return MISSING_PATTERN.findall(text)
