"""Nhịp gọi AI của lượt chạy tự động (T-148, thiết kế T-141 2.4, 6.3, 6.5).

- Đọc mục ``[auto]`` của ``config/ai.toml``, chịu lỗi: thiếu mục, thiếu khóa thì dùng mặc định
  (giãn nhịp 6 giây; trần lần gọi Gemini mỗi ngày 0 = chưa biết, không chặn). Giá trị sai dạng
  thì báo câu tiếng Việt chỉ nêu ``config/ai.toml`` và ``[auto]``.
- Ngày theo giờ Thái Bình Dương (``America/Los_Angeles``): Google đặt lại hạn mức số lần gọi mỗi
  ngày lúc nửa đêm giờ đó, tức 15:00 giờ Việt Nam mùa đông, 14:00 mùa hè của Mỹ.
- Hàm thuần tính số giây phải chờ trước lần gọi sau (không tự ``sleep``).

Không dùng ``streamlit`` (LC-T141-9): gọi được từ luồng nền của lượt chạy.
"""

from __future__ import annotations

import math
import tomllib
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from seo_app.ai.base import AIError
from seo_app.ai.registry import AI_CONFIG_FILE

PACIFIC = ZoneInfo("America/Los_Angeles")
VIETNAM = ZoneInfo("Asia/Ho_Chi_Minh")

SECTION = "auto"
# Tên khóa đúng như T-144 ghi vào config/ai.toml.
MIN_SECONDS_KEY = "min_seconds_between_calls"
REQUESTS_PER_DAY_KEY = "gemini_requests_per_day"
DEFAULT_MIN_SECONDS = 6
DEFAULT_REQUESTS_PER_DAY = 0  # 0 = chưa biết hạn mức: không chặn, chỉ đếm
MIN_SECONDS_RANGE = (1, 120)
REQUESTS_PER_DAY_RANGE = (0, 100_000)


@dataclass(frozen=True)
class AutoLimits:
    """Giới hạn đọc từ ``[auto]``: giây tối thiểu giữa hai lần gọi Gemini, trần lần gọi mỗi ngày
    (0 = chưa biết)."""

    min_seconds_between_calls: float = DEFAULT_MIN_SECONDS
    gemini_requests_per_day: int = DEFAULT_REQUESTS_PER_DAY


def load_auto_limits(path: Path = AI_CONFIG_FILE) -> AutoLimits:
    """Đọc mục ``[auto]``. Thiếu mục, thiếu khóa: mặc định. Sai dạng: ``AIError`` tiếng Việt."""
    try:
        # "utf-8-sig": nhận cả file UTF-8 có BOM (Notepad đời cũ), như load_ai_config.
        data = tomllib.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise AIError("Không thấy file cấu hình AI: config/ai.toml.") from exc
    except UnicodeDecodeError as exc:
        raise AIError(
            "File config/ai.toml không lưu ở dạng UTF-8. Mở lại bằng Notepad, chọn Lưu thành "
            "(Save As) → Mã hóa (Encoding): UTF-8, rồi lưu."
        ) from exc
    except OSError as exc:
        raise AIError("Không đọc được file config/ai.toml.") from exc
    except tomllib.TOMLDecodeError as exc:
        raise AIError(f"File config/ai.toml viết sai cú pháp: {exc}") from exc

    section = data.get(SECTION, {})
    if not isinstance(section, dict):
        raise AIError(
            "config/ai.toml: mục [auto] viết sai dạng. Ghi một dòng [auto], dưới đó mỗi thông số "
            "một dòng, ví dụ min_seconds_between_calls = 6."
        )
    seconds = _seconds(section.get(MIN_SECONDS_KEY, DEFAULT_MIN_SECONDS))
    per_day = _requests_per_day(section.get(REQUESTS_PER_DAY_KEY, DEFAULT_REQUESTS_PER_DAY))
    return AutoLimits(min_seconds_between_calls=seconds, gemini_requests_per_day=per_day)


def _seconds(value: object) -> float:
    low, high = MIN_SECONDS_RANGE
    # bool là một loại int trong Python: true/false không phải số giây.
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or not low <= value <= high
    ):
        raise AIError(
            f"config/ai.toml, mục [auto]: {MIN_SECONDS_KEY} phải là số giây từ {low} tới "
            f"{high}, ví dụ {MIN_SECONDS_KEY} = {DEFAULT_MIN_SECONDS} (không để trong ngoặc kép)."
        )
    return float(value)


def _requests_per_day(value: object) -> int:
    low, high = REQUESTS_PER_DAY_RANGE
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise AIError(
            f"config/ai.toml, mục [auto]: {REQUESTS_PER_DAY_KEY} phải là số nguyên từ {low} tới "
            f"{high} (0 là chưa biết hạn mức, không chặn), không để trong ngoặc kép."
        )
    return value


# ------------------------------------------------------------------ ngày theo giờ Google đặt lại


def _aware(now: datetime) -> datetime:
    if now.tzinfo is None or now.utcoffset() is None:
        # Giờ không kèm múi giờ thì không biết là ngày nào ở Mỹ (CLAUDE.md: lưu giờ kèm múi giờ).
        raise ValueError("now phải là giờ có múi giờ")
    return now


def pacific_day(now: datetime) -> date:
    """Ngày theo giờ Thái Bình Dương (đúng giờ mùa hè của Mỹ): khóa ngày của sổ đếm lần gọi
    Gemini, vì Google đặt lại số lần gọi mỗi ngày lúc nửa đêm giờ này."""
    return _aware(now).astimezone(PACIFIC).date()


def reset_at_vn(now: datetime) -> datetime:
    """Giờ Việt Nam của lần đặt lại hạn mức kế tiếp (nửa đêm giờ Thái Bình Dương sau ``now``):
    15:00 khi Mỹ theo giờ mùa đông, 14:00 khi theo giờ mùa hè. Để hiện cho người dùng."""
    next_day = pacific_day(now) + timedelta(days=1)
    # Nửa đêm ở Los Angeles luôn có và chỉ có một lần (đổi giờ lúc 2 giờ sáng).
    return datetime.combine(next_day, time(0), tzinfo=PACIFIC).astimezone(VIETNAM)


# ------------------------------------------------------------------------------- giãn nhịp


def seconds_to_wait(last_call: float | None, now: float, min_seconds: float) -> float:
    """Số giây còn phải chờ trước lần gọi sau, để hai lần gọi cách nhau ít nhất ``min_seconds``.

    ``last_call``, ``now``: giờ theo ``time.monotonic()`` (không lùi khi đổi giờ máy);
    ``last_call`` ``None`` (chưa gọi lần nào): không phải chờ. Hàm thuần, không tự ``sleep``.
    """
    if last_call is None:
        return 0.0
    elapsed = now - last_call
    # Giờ chạy ngược (không nên có với monotonic): chờ đủ một nhịp, không chờ quá.
    return max(0.0, min(float(min_seconds), min_seconds - elapsed))


def daily_limit_reached(used_today: int, limits: AutoLimits) -> bool:
    """Số lần gọi Gemini hôm nay (theo sổ đếm của máy) đã chạm trần ghi ở ``[auto]`` chưa. Trần 0
    (chưa biết) thì không bao giờ chặn."""
    limit = limits.gemini_requests_per_day
    return limit > 0 and used_today >= limit
