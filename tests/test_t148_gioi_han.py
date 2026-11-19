"""T-148 (Thợ Máy): ``seo_app/ai/limits.py`` — mục ``[auto]``, ngày giờ Thái Bình Dương, giãn nhịp.

- ``[auto]`` chịu lỗi: thiếu mục, thiếu khóa thì mặc định (6 giây; 0 lần/ngày = chưa biết). Sai
  dạng (``bool``, chữ, ngoài khoảng 1–120 giây, 0–100.000 lần) thì câu tiếng Việt chỉ nêu
  ``config/ai.toml`` và ``[auto]``, không đường dẫn đầy đủ.
- ``pacific_day`` qua hai mốc đổi giờ của Mỹ năm 2026 (8/3 và 1/11); ``reset_at_vn`` là 15:00 giờ
  Việt Nam mùa đông, 14:00 mùa hè.
- ``seconds_to_wait`` là hàm thuần (không ``sleep``); ``daily_limit_reached`` không chặn khi trần 0.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import pytest

from seo_app.ai.base import AIError
from seo_app.ai.limits import (
    DEFAULT_MIN_SECONDS,
    DEFAULT_REQUESTS_PER_DAY,
    MIN_SECONDS_RANGE,
    PACIFIC,
    REQUESTS_PER_DAY_RANGE,
    VIETNAM,
    AutoLimits,
    daily_limit_reached,
    load_auto_limits,
    pacific_day,
    reset_at_vn,
    seconds_to_wait,
)

TASKS = '[tasks.write]\nprovider = "gemini"\nmodel = "gemini-3.8-flash"\n'


def toml(tmp_path, body: str):
    path = tmp_path / "ai.toml"
    path.write_text(TASKS + body, encoding="utf-8")
    return path


def utc(*args) -> datetime:
    return datetime(*args, tzinfo=UTC)


def vn(*args) -> datetime:
    return datetime(*args, tzinfo=VIETNAM)


# ============================================================================== mục [auto]


def test_defaults_match_t144_keys():
    assert (DEFAULT_MIN_SECONDS, DEFAULT_REQUESTS_PER_DAY) == (6, 0)
    assert AutoLimits() == AutoLimits(min_seconds_between_calls=6, gemini_requests_per_day=0)


@pytest.mark.parametrize(
    "body",
    ["", "[auto]\n", "[auto]\nkhoa_la = 1\n", '[other]\nmin_seconds_between_calls = "x"\n'],
    ids=["khong-muc", "muc-rong", "khoa-la", "muc-khac"],
)
def test_missing_section_or_keys_give_defaults(tmp_path, body):
    assert load_auto_limits(toml(tmp_path, body)) == AutoLimits(6, 0)


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        ("[auto]\nmin_seconds_between_calls = 12\n", AutoLimits(12, 0)),
        ("[auto]\ngemini_requests_per_day = 250\n", AutoLimits(6, 250)),
        ("[auto]\nmin_seconds_between_calls = 1\ngemini_requests_per_day = 0\n", AutoLimits(1, 0)),
        ("[auto]\nmin_seconds_between_calls = 120\ngemini_requests_per_day = 100000\n",
         AutoLimits(120, 100_000)),
        ("[auto]\nmin_seconds_between_calls = 6.5\n", AutoLimits(6.5, 0)),
    ],
    ids=["giay-12", "ngay-250", "nho-nhat", "lon-nhat", "giay-le"],
)  # fmt: skip
def test_valid_values_are_read(tmp_path, body, expected):
    limits = load_auto_limits(toml(tmp_path, body))
    assert limits == expected
    assert isinstance(limits.min_seconds_between_calls, float)
    assert isinstance(limits.gemini_requests_per_day, int)


SECONDS_BAD = ["true", "false", '"6"', "0", "0.5", "121", "-6", "nan", "inf", "[6]"]
PER_DAY_BAD = ["true", '"250"', "-1", "100001", "2.5", "nan", "[1]"]


@pytest.mark.parametrize("value", SECONDS_BAD, ids=lambda v: f"giay-{v}")
def test_bad_seconds_give_clear_error(tmp_path, value):
    path = toml(tmp_path, f"[auto]\nmin_seconds_between_calls = {value}\n")
    with pytest.raises(AIError) as info:
        load_auto_limits(path)
    message = str(info.value)
    assert "config/ai.toml" in message and "[auto]" in message
    assert "min_seconds_between_calls" in message and f"{MIN_SECONDS_RANGE[0]} tới" in message
    assert str(tmp_path) not in message and str(tmp_path.name) not in message


@pytest.mark.parametrize("value", PER_DAY_BAD, ids=lambda v: f"ngay-{v}")
def test_bad_requests_per_day_give_clear_error(tmp_path, value):
    path = toml(tmp_path, f"[auto]\ngemini_requests_per_day = {value}\n")
    with pytest.raises(AIError) as info:
        load_auto_limits(path)
    message = str(info.value)
    assert "config/ai.toml" in message and "[auto]" in message
    assert "gemini_requests_per_day" in message and f"{REQUESTS_PER_DAY_RANGE[1]}" in message
    assert str(tmp_path) not in message


@pytest.mark.parametrize("body", ['auto = "6"\n', "auto = 6\n", "auto = [1, 2]\n"])
def test_auto_that_is_not_a_section_gives_clear_error(tmp_path, body):
    # Khóa trần phải đứng trước mọi mục [..] mới là khóa của gốc file.
    path = tmp_path / "ai.toml"
    path.write_text(body + TASKS, encoding="utf-8")
    with pytest.raises(AIError, match=r"config/ai\.toml: mục \[auto\] viết sai dạng"):
        load_auto_limits(path)


def test_file_problems_name_only_config_ai_toml(tmp_path):
    missing = tmp_path / "khong-co" / "ai.toml"
    with pytest.raises(AIError) as info:
        load_auto_limits(missing)
    assert str(info.value) == "Không thấy file cấu hình AI: config/ai.toml."
    broken = toml(tmp_path, "[auto\n")
    with pytest.raises(AIError, match="viết sai cú pháp") as info:
        load_auto_limits(broken)
    assert str(tmp_path) not in str(info.value)
    latin = tmp_path / "latin.toml"
    latin.write_bytes(b"# Ghi ch\xfa (Notepad l\xfau sai m\xe3)\n[auto]\n")  # byte lẻ, không UTF-8
    with pytest.raises(AIError, match="UTF-8"):
        load_auto_limits(latin)


def test_utf8_bom_is_accepted(tmp_path):
    path = tmp_path / "ai.toml"
    path.write_bytes(b"\xef\xbb\xbf" + b"[auto]\nmin_seconds_between_calls = 9\n")
    assert load_auto_limits(path) == AutoLimits(9, 0)


def test_committed_config_loads_within_ranges():
    # T-144 thêm [auto] sau: test không ghim giá trị, chỉ đòi đọc được và nằm trong khoảng.
    limits = load_auto_limits()
    assert MIN_SECONDS_RANGE[0] <= limits.min_seconds_between_calls <= MIN_SECONDS_RANGE[1]
    assert REQUESTS_PER_DAY_RANGE[0] <= limits.gemini_requests_per_day <= REQUESTS_PER_DAY_RANGE[1]


# ===================================================== ngày theo giờ Thái Bình Dương (2026)


def test_2026_us_clock_changes_are_where_the_test_expects():
    # Tiền đề: Mỹ đổi sang giờ mùa hè 8/3/2026 lúc 2:00 sáng (10:00 UTC), về giờ mùa đông
    # 1/11/2026 lúc 2:00 sáng (9:00 UTC). zoneinfo của máy phải biết điều này.
    def offset(moment):
        return moment.astimezone(PACIFIC).utcoffset()

    assert offset(utc(2026, 3, 8, 9, 59)) == timedelta(hours=-8)
    assert offset(utc(2026, 3, 8, 10, 0)) == timedelta(hours=-7)
    assert offset(utc(2026, 11, 1, 8, 59)) == timedelta(hours=-7)
    assert offset(utc(2026, 11, 1, 9, 0)) == timedelta(hours=-8)


@pytest.mark.parametrize(
    ("now", "day"),
    [
        # Mốc 8/3/2026 (bắt đầu giờ mùa hè): nửa đêm 7→8/3 còn là giờ mùa đông (08:00 UTC),
        # nửa đêm 8→9/3 đã là giờ mùa hè (07:00 UTC).
        (utc(2026, 3, 8, 7, 59, 59), date(2026, 3, 7)),
        (utc(2026, 3, 8, 8, 0), date(2026, 3, 8)),
        (utc(2026, 3, 8, 10, 30), date(2026, 3, 8)),
        (utc(2026, 3, 9, 6, 59, 59), date(2026, 3, 8)),
        (utc(2026, 3, 9, 7, 0), date(2026, 3, 9)),
        # Mốc 1/11/2026 (hết giờ mùa hè): nửa đêm 31/10→1/11 là giờ mùa hè (07:00 UTC),
        # nửa đêm 1→2/11 đã là giờ mùa đông (08:00 UTC); giờ 1:30 sáng có hai lần.
        (utc(2026, 11, 1, 6, 59, 59), date(2026, 10, 31)),
        (utc(2026, 11, 1, 7, 0), date(2026, 11, 1)),
        (utc(2026, 11, 1, 8, 30), date(2026, 11, 1)),
        (utc(2026, 11, 1, 9, 30), date(2026, 11, 1)),
        (utc(2026, 11, 2, 7, 59, 59), date(2026, 11, 1)),
        (utc(2026, 11, 2, 8, 0), date(2026, 11, 2)),
        # Giờ Việt Nam: mùa đông của Mỹ, ngày mới bắt đầu lúc 15:00.
        (vn(2026, 11, 19, 14, 59, 59), date(2026, 11, 18)),
        (vn(2026, 11, 19, 15, 0), date(2026, 11, 19)),
        (vn(2026, 7, 1, 13, 59, 59), date(2026, 6, 30)),
        (vn(2026, 7, 1, 14, 0), date(2026, 7, 1)),
    ],
    ids=["3-7-cuoi", "3-8-dau", "3-8-sau-doi", "3-8-cuoi", "3-9-dau", "10-31-cuoi", "11-1-dau",
         "11-1-gio-lap-1", "11-1-gio-lap-2", "11-1-cuoi", "11-2-dau", "vn-dong-truoc",
         "vn-dong-15h", "vn-he-truoc", "vn-he-14h"],
)  # fmt: skip
def test_pacific_day_across_2026_clock_changes(now, day):
    assert pacific_day(now) == day


def test_pacific_day_needs_timezone():
    with pytest.raises(ValueError):
        pacific_day(datetime(2026, 11, 19, 10, 0))
    with pytest.raises(ValueError):
        reset_at_vn(datetime(2026, 11, 19, 10, 0))


@pytest.mark.parametrize(
    ("now", "reset"),
    [
        (vn(2026, 11, 19, 10, 0), vn(2026, 11, 19, 15, 0)),
        (vn(2026, 11, 19, 15, 0), vn(2026, 11, 20, 15, 0)),
        (vn(2026, 7, 1, 10, 0), vn(2026, 7, 1, 14, 0)),
        (vn(2026, 3, 8, 12, 0), vn(2026, 3, 8, 15, 0)),  # trước mốc: lần đặt lại cuối của mùa đông
        (vn(2026, 3, 8, 16, 0), vn(2026, 3, 9, 14, 0)),  # sau mốc: lần đầu của mùa hè
        (vn(2026, 11, 1, 12, 0), vn(2026, 11, 1, 14, 0)),  # lần cuối của mùa hè
        (vn(2026, 11, 1, 15, 0), vn(2026, 11, 2, 15, 0)),  # lần đầu của mùa đông
        (utc(2026, 11, 19, 7, 59), vn(2026, 11, 19, 15, 0)),
    ],
    ids=["dong-sang", "dong-dung-15h", "he", "3-8-truoc", "3-8-sau", "11-1-truoc", "11-1-sau",
         "tu-utc"],
)  # fmt: skip
def test_reset_at_vn(now, reset):
    result = reset_at_vn(now)
    assert result == reset and result.tzinfo == VIETNAM
    assert result > now and result - now <= timedelta(hours=25)


# ================================================================= giãn nhịp, trần mỗi ngày


@pytest.mark.parametrize(
    ("last_call", "now", "min_seconds", "wait"),
    [
        (None, 50.0, 6, 0.0),
        (100.0, 103.0, 6, 3.0),
        (100.0, 106.0, 6, 0.0),
        (100.0, 200.0, 6, 0.0),
        (100.0, 100.0, 12, 12.0),
        (100.0, 101.5, 6.5, 5.0),
        (100.0, 90.0, 6, 6.0),  # giờ chạy ngược: chờ đủ một nhịp, không hơn
    ],
    ids=["chua-goi", "con-3", "vua-du", "lau-roi", "vua-goi", "giay-le", "gio-nguoc"],
)
def test_seconds_to_wait(last_call, now, min_seconds, wait):
    assert seconds_to_wait(last_call, now, min_seconds) == pytest.approx(wait)


@pytest.mark.parametrize(
    ("used", "limit", "reached"),
    [(0, 0, False), (10_000, 0, False), (19, 20, False), (20, 20, True), (25, 20, True)],
    ids=["tran-0", "tran-0-dung-nhieu", "con-1", "cham-tran", "qua-tran"],
)
def test_daily_limit_reached(used, limit, reached):
    assert daily_limit_reached(used, AutoLimits(6, limit)) is reached
