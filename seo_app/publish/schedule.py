"""Giờ hẹn đăng bài (T-099; thiết kế T-094 mục 3.1, 3.4; Lá Chắn LC-T094-24, -27).

Logic thuần, không gọi mạng:

- ``local_to_utc``: ngày + giờ người dùng chọn theo múi giờ của app (``settings.timezone_name``,
  mặc định ``Asia/Ho_Chi_Minh``, đã kiểm ở ``load_settings``) → giờ UTC có múi giờ.
- ``date_gmt_text``: giờ UTC → chuỗi ``date_gmt`` gửi WordPress (``YYYY-MM-DDTHH:MM:SS``, không
  đuôi múi giờ). Client (``release_draft``) và bộ dựng bài (mã băm xác nhận) dùng cùng hàm này.
- ``schedule_label``: «Thứ Ba, 03/11/2026 lúc 08:00 (giờ Việt Nam)», tính từ giờ người dùng chọn,
  không từ đồng hồ máy.
- ``parse_server_date``: header ``Date`` của câu trả lời WordPress → giờ máy chủ (UTC).
- ``release_time_problem``: lớp chặn cuối của client ngay trước lệnh hẹn giờ/đăng (giờ máy chủ,
  lệch đồng hồ, khoảng hẹn giờ). ``check_schedule``: cùng quy tắc cho màn hình chọn giờ.

Vì sao chặn hẹn giờ quá gần: WordPress (``wp_insert_post``) đổi bài ``future`` có giờ chưa tới 60
giây sau giờ máy chủ, kể cả giờ đã qua, thành ``publish`` **ngay**. Biên 10 phút theo giờ máy chủ,
kiểm lại ngay trước lệnh (tải ảnh có thể mất vài phút), để không bao giờ chạm ngưỡng đó.
"""

from __future__ import annotations

import email.utils
from collections.abc import Iterable
from datetime import UTC, date, datetime, time, timedelta
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from seo_app.config import DEFAULT_TIMEZONE

if TYPE_CHECKING:  # nhập muộn trong ``check_schedule``: onpage kéo theo lớp nội dung, client
    from seo_app.onpage.links import Notice

MIN_LEAD = timedelta(minutes=10)  # hẹn giờ ít nhất 10 phút sau giờ máy chủ
MAX_AHEAD = timedelta(days=365)  # quá một năm: thường là gõ nhầm năm
MAX_CLOCK_SKEW = timedelta(minutes=2)  # đồng hồ máy lệch giờ website hơn mức này thì chặn
MAX_DATE_HEADER_CHARS = 64  # header ``Date`` chuẩn dài 29 ký tự

WEEKDAYS = ("Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật")

MSG_NO_SERVER_TIME = (
    "Không đọc được giờ của website (header Date thiếu hoặc sai dạng), nên không kiểm được giờ "
    "hẹn. Chưa hẹn giờ, chưa đăng: bài vẫn là nháp."
)
MSG_CLOCK_SKEW = (
    "Đồng hồ máy tính lệch giờ website hơn 2 phút. Chỉnh lại ngày giờ của máy (bật tự đặt giờ) "
    "rồi thử lại. Chưa hẹn giờ, chưa đăng: bài vẫn là nháp."
)
MSG_PAST = "Giờ hẹn đã qua. Chọn giờ khác. Chưa hẹn giờ: bài vẫn là nháp."
MSG_TOO_SOON = (
    "Giờ hẹn phải cách bây giờ ít nhất 10 phút (gần hơn thì WordPress đăng ngay). Chọn giờ muộn "
    "hơn. Chưa hẹn giờ: bài vẫn là nháp."
)
MSG_TOO_FAR = "Giờ hẹn xa hơn một năm, có thể gõ nhầm năm. Chọn lại. Chưa hẹn giờ: bài vẫn là nháp."
MSG_SAME_TIME = "Đã có bài khác hẹn đăng đúng giờ này. Nên cách nhau vài giờ."


class ScheduleError(ValueError):
    """Đầu vào sai dạng (không phải ngày, giờ; giờ không có múi giờ; giờ không có ở múi giờ đó).
    ``str(err)`` là câu tiếng Việt cố định."""


def local_to_utc(day: date, at: time, timezone_name: str = DEFAULT_TIMEZONE) -> datetime:
    """Ngày ``day`` lúc ``at`` theo múi giờ ``timezone_name`` → giờ UTC (có múi giờ, giây 0).

    ``at`` chỉ lấy giờ, phút (bỏ giây). Giờ không có thật ở múi giờ đó (giờ bị nhảy khi đổi giờ
    mùa hè; Việt Nam không đổi giờ nên không gặp) hay giờ lặp hai lần: ``ScheduleError``.
    """
    if type(day) is not date or type(at) is not time or at.tzinfo is not None:
        raise ScheduleError("Ngày hoặc giờ hẹn sai dạng.")
    zone = ZoneInfo(timezone_name)
    wall = datetime(day.year, day.month, day.day, at.hour, at.minute)
    local = wall.replace(tzinfo=zone)
    utc = local.astimezone(UTC)
    # Giờ nhảy qua (khoảng trống khi đổi giờ): đổi về lại thì ra giờ khác. Xét trước giờ lặp, vì
    # trong khoảng trống ``fold=0`` và ``fold=1`` cũng có độ lệch khác nhau (PEP 495).
    if utc.astimezone(zone).replace(tzinfo=None) != wall:
        raise ScheduleError("Giờ này không có ở múi giờ đã chọn (lúc đổi giờ). Chọn giờ khác.")
    if local.utcoffset() != wall.replace(tzinfo=zone, fold=1).utcoffset():
        raise ScheduleError("Giờ này lặp hai lần ở múi giờ đã chọn (lúc đổi giờ). Chọn giờ khác.")
    return utc


def _aware(value: object) -> datetime:
    """``value`` là ``datetime`` có múi giờ (không nhận lớp con, không nhận giờ không múi giờ)."""
    if type(value) is not datetime or value.utcoffset() is None:
        raise ScheduleError("Giờ hẹn phải có múi giờ rõ ràng.")
    return value


def _utc(value: object) -> datetime:
    """``value`` (có múi giờ) đổi sang UTC, bỏ phần lẻ của giây: đúng giờ ``date_gmt`` sẽ gửi."""
    try:
        return _aware(value).astimezone(UTC).replace(microsecond=0)
    except OverflowError:  # năm 1 hay 9999 ở múi giờ khác: ra ngoài khoảng của ``datetime``
        raise ScheduleError("Giờ hẹn sai dạng.") from None


def date_gmt_text(when_utc: datetime) -> str:
    """Chuỗi ``date_gmt`` gửi WordPress: giờ UTC dạng ``YYYY-MM-DDTHH:MM:SS`` (bỏ phần lẻ của
    giây, không đuôi múi giờ). ``when_utc`` phải có múi giờ (múi nào cũng được, đổi sang UTC)."""
    when = _utc(when_utc)
    if when.year < 1000:  # không đủ 4 chữ số năm
        raise ScheduleError("Giờ hẹn sai dạng.")
    return (
        f"{when.year:04d}-{when.month:02d}-{when.day:02d}"
        f"T{when.hour:02d}:{when.minute:02d}:{when.second:02d}"
    )


def schedule_label(when_utc: datetime, timezone_name: str = DEFAULT_TIMEZONE) -> str:
    """Nhãn giờ hẹn: «Thứ Ba, 03/11/2026 lúc 08:00 (giờ Việt Nam)».

    Tính từ giờ người dùng đã chọn (``when_utc``, đổi về ``timezone_name``), không từ đồng hồ
    máy (LC-T094-27). Múi giờ khác ``Asia/Ho_Chi_Minh`` thì ghi tên múi giờ.
    """
    try:
        local = _utc(when_utc).astimezone(ZoneInfo(timezone_name))
    except OverflowError:
        raise ScheduleError("Giờ hẹn sai dạng.") from None
    zone = "giờ Việt Nam" if timezone_name == DEFAULT_TIMEZONE else f"giờ {timezone_name}"
    return f"{WEEKDAYS[local.weekday()]}, {local:%d/%m/%Y} lúc {local:%H:%M} ({zone})"


def parse_server_date(value: object) -> datetime | None:
    """Header ``Date`` (``Tue, 03 Nov 2026 01:00:00 GMT``) → giờ máy chủ UTC; ``None`` khi thiếu,
    không phải chữ, quá dài, có ký tự lạ hay không đọc được. Không bao giờ ném lỗi.

    Không đoán: chuỗi không có múi giờ (``-0000``) cũng là ``None``. Người gọi phải **chặn** khi
    ``None``, không lấy đồng hồ máy thay (LC-T094-24).
    """
    if not isinstance(value, str) or not value.isascii() or len(value) > MAX_DATE_HEADER_CHARS:
        return None
    if not value.isprintable():
        return None
    try:
        parsed = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError, OverflowError):
        return None
    if parsed is None or parsed.utcoffset() is None:
        return None
    try:
        return parsed.astimezone(UTC)
    except (ValueError, OverflowError):
        return None


def release_time_problem(
    mode: str, when_utc: datetime | None, *, server_now: datetime | None, local_now: datetime
) -> str:
    """Lớp chặn giờ ngay trước lệnh hẹn giờ/đăng của client. ``""``: được gửi; còn lại là câu
    chặn cố định (không gửi gì).

    - ``server_now``: giờ máy chủ đọc từ header ``Date`` của câu trả lời ngay trước lệnh; ``None``
      (thiếu, sai dạng) → chặn.
    - ``local_now``: đồng hồ máy (UTC); lệch giờ máy chủ quá ``MAX_CLOCK_SKEW`` → chặn.
    - ``mode == "future"``: ``when_utc`` có múi giờ, ≥ giờ máy chủ + ``MIN_LEAD`` và ≤ giờ máy chủ
      + ``MAX_AHEAD`` (so trên giờ đã bỏ phần lẻ của giây, đúng giờ sẽ gửi).
    """
    if mode not in ("future", "publish"):
        raise ScheduleError("Hình thức gửi phải là hẹn giờ hoặc đăng ngay.")
    if server_now is None or type(server_now) is not datetime or server_now.utcoffset() is None:
        return MSG_NO_SERVER_TIME
    if abs(_aware(local_now) - server_now) > MAX_CLOCK_SKEW:
        return MSG_CLOCK_SKEW
    if mode == "publish":
        return ""
    return _gap_problem(_utc(when_utc), server_now)


def _gap_problem(when: datetime, now: datetime) -> str:
    gap = when - now  # trừ hai giờ có múi giờ: không tràn như ``now + MAX_AHEAD``
    if gap <= timedelta(0):
        return MSG_PAST
    if gap < MIN_LEAD:
        return MSG_TOO_SOON
    if gap > MAX_AHEAD:
        return MSG_TOO_FAR
    return ""


def check_schedule(
    when_utc: datetime, *, now_utc: datetime, scheduled: Iterable[datetime] = ()
) -> list[Notice]:
    """Kiểm giờ hẹn cho màn hình chọn giờ (thiết kế T-094 mục 3.4): đã qua, chưa tới 10 phút,
    quá một năm → Chặn; trùng phút với bài khác đã hẹn (``scheduled``, từ bước đồng bộ) →
    Cảnh báo. ``now_utc`` là đồng hồ máy: client còn kiểm lại theo giờ máy chủ ngay trước lệnh.
    """
    from seo_app.onpage.links import Notice
    from seo_app.onpage.meta import Level

    when = _utc(when_utc)
    problems: list[Notice] = []
    gap = _gap_problem(when, _aware(now_utc))
    if gap:
        problems.append(Notice(Level.BLOCK, gap))
    minute = when.replace(second=0)
    for other in scheduled:
        if type(other) is not datetime or other.utcoffset() is None:
            continue
        if (other - minute).total_seconds() // 60 == 0:
            problems.append(Notice(Level.WARN, MSG_SAME_TIME))
            break
    return problems
