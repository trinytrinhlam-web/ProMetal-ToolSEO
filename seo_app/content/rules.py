"""Quy tắc nội dung (``config/content.toml``), hồ sơ doanh nghiệp và các kiểm tra không cần AI."""

from __future__ import annotations

import re
import tomllib
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from seo_app.ai.base import AIError
from seo_app.config import PROJECT_ROOT

CONTENT_CONFIG_FILE = PROJECT_ROOT / "config" / "content.toml"
BUSINESS_PROFILE_FILE = PROJECT_ROOT / "config" / "business_profile.md"
# Ý mang nhãn «[CẦN XÁC NHẬN» (có hay không có lý do phía sau) trong hồ sơ doanh nghiệp chưa
# được chủ dự án xác nhận: AI không được thấy. So trên chữ đã chuẩn hóa NFC và viết hoa; chịu
# được dấu cách thừa, tab, dấu cách không ngắt.
_UNCONFIRMED_PATTERN = re.compile(r"\[\s*CẦN\s+XÁC\s+NHẬN")
# Gạch đầu dòng: «- », «* », «+ », «1. », «1) ».
_BULLET = re.compile(r"(?:[-*+]|\d+[.)])(?:\s|$)")

# Chỗ AI để trống vì thiếu dữ liệu thật, ví dụ: [cần bổ sung: giá cổng 4 m của xưởng]
MISSING_PATTERN = re.compile(r"\[cần bổ sung:[^\]]*\]", re.IGNORECASE)
_SENTENCE_END = re.compile(r"(?<=[.!?…])\s+|\n+")


class ContentRulesError(AIError):
    """``config/content.toml`` hoặc hồ sơ doanh nghiệp đọc không được / viết sai dạng.

    Là một loại ``AIError`` để trang Soạn bài báo lỗi tiếng Việt và khóa các bước AI, thay vì
    hiện lỗi Python.
    """


@dataclass(frozen=True)
class ContentRules:
    business_profile: str
    address: str
    tone: str
    banned: tuple[str, ...]
    checklist: tuple[str, ...]


def confirmed_profile(text: str) -> str:
    """Hồ sơ doanh nghiệp đã bỏ các ý còn nhãn [CẦN XÁC NHẬN] và mọi dòng ghi chú ``>``.

    Lọc theo **khối**, không theo từng dòng, để một ý viết trên nhiều dòng không lọt nửa nào:

    - Gạch đầu dòng (``- …``, ``* …``, ``1. …``) không thụt lề mở một khối; các dòng sau nó
      cho tới dòng trống, tiêu đề hoặc gạch đầu dòng không thụt lề kế tiếp đều thuộc khối đó
      (dòng thụt vào, gạch đầu dòng lồng nhau, cả dòng quên thụt lề khi gõ Notepad).
    - Đoạn văn thường: khối là cả đoạn, ngăn bằng dòng trống.
    - Tiêu đề ``#`` (không thụt lề) luôn đứng riêng một khối.

    Khối có nhãn ở bất kỳ dòng nào thì bỏ cả khối. Dòng ghi chú (ký tự đầu tiên không phải
    khoảng trắng là ``>``) luôn bị bỏ và không cắt khối. Các dòng giữ lại y nguyên như trong
    file.
    """
    kept: list[str] = []
    block: list[str] = []
    block_unconfirmed = False

    def close_block() -> None:
        nonlocal block_unconfirmed
        if not block_unconfirmed:
            kept.extend(block)
        block.clear()
        block_unconfirmed = False

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(">"):
            continue
        if not stripped:
            close_block()
            kept.append(line)
            continue
        indented = line[0].isspace()
        if not indented and (stripped.startswith("#") or _BULLET.match(stripped)):
            close_block()
        block.append(line)
        block_unconfirmed = block_unconfirmed or _is_unconfirmed(line)
        if not indented and stripped.startswith("#"):
            close_block()
    close_block()
    return "\n".join(kept).strip()


def _is_unconfirmed(line: str) -> bool:
    return bool(_UNCONFIRMED_PATTERN.search(unicodedata.normalize("NFC", line).upper()))


def _read_text(path: Path) -> str:
    try:
        # "utf-8-sig": nhận cả file UTF-8 có BOM (Notepad đời cũ lưu kiểu này).
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ContentRulesError(
            f"File config/{path.name} không lưu ở dạng UTF-8. Mở lại bằng Notepad, chọn "
            "Lưu thành (Save As) → Mã hóa (Encoding): UTF-8, rồi lưu."
        ) from exc
    except OSError as exc:
        raise ContentRulesError(f"Không đọc được file config/{path.name}.") from exc


def _table(data: dict, key: str, path: Path) -> dict:
    value = data.get(key, {})
    if not isinstance(value, dict):
        raise ContentRulesError(
            f"File config/{path.name}: «{key}» phải là một mục [{key}], không phải một giá trị."
        )
    return value


def _text(table: dict, key: str, path: Path) -> str:
    value = table.get(key, "")
    if not isinstance(value, str):
        raise ContentRulesError(f"File config/{path.name}: «{key}» phải là chữ trong ngoặc kép.")
    return value


def _text_list(table: dict, key: str, path: Path) -> tuple[str, ...]:
    value = table.get(key, [])
    if isinstance(value, str):
        # Viết nhầm một chuỗi thay vì danh sách: coi là danh sách một dòng, không tách từng chữ.
        value = [value]
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise ContentRulesError(
            f'File config/{path.name}: «{key}» phải là danh sách chữ, ví dụ ["dòng 1", "dòng 2"].'
        )
    return tuple(v for v in value if v.strip())


def load_rules(
    path: Path = CONTENT_CONFIG_FILE, profile_path: Path = BUSINESS_PROFILE_FILE
) -> ContentRules:
    """Đọc quy tắc nội dung. File sai bảng mã hoặc sai dạng thì báo ``ContentRulesError``."""
    try:
        data = tomllib.loads(_read_text(path))
    except tomllib.TOMLDecodeError as exc:
        raise ContentRulesError(f"File config/{path.name} viết sai cú pháp: {exc}") from exc
    voice = _table(data, "voice", path)
    review = _table(data, "review", path)
    profile = confirmed_profile(_read_text(profile_path)) if profile_path.is_file() else ""
    return ContentRules(
        business_profile=profile,
        address=_text(voice, "address", path),
        tone=_text(voice, "tone", path),
        banned=_text_list(voice, "banned", path),
        checklist=_text_list(review, "checklist", path),
    )


def sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_END.split(text) if s.strip()]


def find_banned(text: str, banned: tuple[str, ...] | list[str]) -> list[tuple[str, str]]:
    """Các câu chứa cụm từ cấm: [(câu, cụm từ)]. Không phân biệt hoa thường.

    So khớp sau khi chuẩn hóa Unicode (NFC; chữ Việt dán từ máy Mac hay ở dạng tổ hợp NFD) và
    gộp mọi khoảng trắng (dấu cách không ngắt, nhiều dấu cách) thành một dấu cách. Cụm từ phải
    đứng trọn từ: «Tóm lại» không khớp «Tóm lạii». Câu trả về giữ nguyên như trong bài.
    """
    patterns = [(phrase, _phrase_pattern(phrase)) for phrase in banned if phrase.strip()]
    found = []
    for sentence in sentences(text):
        normalized = _normalize(sentence)
        for phrase, pattern in patterns:
            if pattern.search(normalized):
                found.append((sentence, phrase))
                break
    return found


def _normalize(text: str) -> str:
    return " ".join(unicodedata.normalize("NFC", text).lower().split())


def _phrase_pattern(phrase: str) -> re.Pattern[str]:
    """Cụm từ đứng trọn từ: không dính chữ cái/chữ số ngay trước hoặc ngay sau.

    Chỉ đòi ranh giới ở đầu (cuối) cụm khi cụm bắt đầu (kết thúc) bằng chữ cái/chữ số: cụm
    «Nhìn chung,» vẫn khớp «Nhìn chung,cửa…» (thiếu dấu cách sau dấu phẩy, Soi Lỗi R3-5).
    """
    normalized = _normalize(phrase)
    before = r"(?<!\w)" if re.match(r"\w", normalized) else ""
    after = r"(?!\w)" if re.search(r"\w$", normalized) else ""
    return re.compile(before + re.escape(normalized) + after)


def find_missing(text: str) -> list[str]:
    """Các chỗ «[cần bổ sung: …]» còn trong bài."""
    return MISSING_PATTERN.findall(text)
