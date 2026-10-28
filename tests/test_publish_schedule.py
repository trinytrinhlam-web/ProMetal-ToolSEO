"""T-099: giờ hẹn đăng bài (``seo_app/publish/schedule.py``; thiết kế T-094 mục 3.1, 3.4).

- Giờ Việt Nam người dùng chọn → UTC → chuỗi ``date_gmt`` đúng dạng WordPress.
- Nhãn «Thứ Ba, 03/11/2026 lúc 08:00 (giờ Việt Nam)» tính từ giờ đã chọn (LC-T094-27).
- Header ``Date`` của website: đọc chặt, không đoán (LC-T094-24).
- Kiểm giờ: đã qua, chưa tới 10 phút, quá một năm → Chặn; trùng giờ bài khác → Cảnh báo; lệch
  đồng hồ máy quá 2 phút, không có giờ máy chủ → Chặn.

Logic thuần, không gọi mạng.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta, timezone

import pytest

from seo_app.onpage.links import Notice
from seo_app.onpage.meta import Level
from seo_app.publish import render
from seo_app.publish.schedule import (
    MAX_AHEAD,
    MAX_CLOCK_SKEW,
    MIN_LEAD,
    MSG_CLOCK_SKEW,
    MSG_NO_SERVER_TIME,
    MSG_PAST,
    MSG_SAME_TIME,
    MSG_TOO_FAR,
    MSG_TOO_SOON,
    WEEKDAYS,
    ScheduleError,
    check_schedule,
    date_gmt_text,
    local_to_utc,
    parse_server_date,
    release_time_problem,
    schedule_label,
)

NOW = datetime(2026, 11, 2, 1, 0, tzinfo=UTC)
VIETNAM = timezone(timedelta(hours=7))


class _Moment(datetime):
    """Lớp con của ``datetime`` (kiểu thư viện khác trả): không được nhận."""


# ====================================================================== giờ Việt Nam → UTC


def test_8_gio_sang_viet_nam_la_1_gio_utc():
    when = local_to_utc(date(2026, 11, 3), time(8, 0))
    assert when == datetime(2026, 11, 3, 1, 0, tzinfo=UTC)
    assert when.tzinfo is UTC


def test_bo_giay_cua_gio_chon():
    assert local_to_utc(date(2026, 11, 3), time(8, 0, 59, 999)) == datetime(
        2026, 11, 3, 1, 0, tzinfo=UTC
    )


def test_qua_nua_dem_viet_nam_lui_ngay_utc():
    assert local_to_utc(date(2026, 1, 1), time(3, 30)) == datetime(2025, 12, 31, 20, 30, tzinfo=UTC)


@pytest.mark.parametrize(
    ("day", "at"),
    [
        (datetime(2026, 11, 3, 8, 0), time(8, 0)),  # datetime là lớp con của date
        ("2026-11-03", time(8, 0)),
        (date(2026, 11, 3), "08:00"),
        (date(2026, 11, 3), time(8, 0, tzinfo=UTC)),
        (date(2026, 11, 3), None),
    ],
)
def test_ngay_gio_sai_kieu_bi_tu_choi(day, at):
    with pytest.raises(ScheduleError):
        local_to_utc(day, at)


def test_mui_gio_co_doi_gio_mua_he_tu_choi_gio_khong_co_va_gio_lap():
    with pytest.raises(ScheduleError, match="không có"):
        local_to_utc(date(2026, 3, 8), time(2, 30), "America/New_York")
    with pytest.raises(ScheduleError, match="lặp hai lần"):
        local_to_utc(date(2026, 11, 1), time(1, 30), "America/New_York")
    assert local_to_utc(date(2026, 7, 1), time(8, 0), "America/New_York") == datetime(
        2026, 7, 1, 12, 0, tzinfo=UTC
    )


# ====================================================================== date_gmt


def test_date_gmt_dung_dang_wordpress():
    assert date_gmt_text(datetime(2026, 11, 3, 1, 0, tzinfo=UTC)) == "2026-11-03T01:00:00"


def test_date_gmt_doi_mui_gio_va_bo_phan_le_cua_giay():
    when = datetime(2026, 11, 3, 8, 0, 5, 999_999, tzinfo=VIETNAM)
    assert date_gmt_text(when) == "2026-11-03T01:00:05"


def test_date_gmt_khop_khuon_cua_bo_dung_bai():
    """Bộ dựng T-096 tính mã băm xác nhận trên đúng chuỗi ``date_gmt`` sẽ gửi."""
    stamp = date_gmt_text(local_to_utc(date(2026, 11, 3), time(8, 0)))
    assert render._DATE_GMT.fullmatch(stamp)


@pytest.mark.parametrize(
    "value",
    [
        datetime(2026, 11, 3, 1, 0),  # không múi giờ
        date(2026, 11, 3),
        "2026-11-03T01:00:00",
        1793667600,
        None,
        _Moment(2026, 11, 3, 1, 0, tzinfo=UTC),
        datetime(999, 12, 31, 23, 0, tzinfo=UTC),
        datetime(1, 1, 1, 0, 0, tzinfo=VIETNAM),  # đổi sang UTC thì tràn
        datetime(9999, 12, 31, 23, 0, tzinfo=timezone(-timedelta(hours=7))),
    ],
)
def test_date_gmt_tu_choi_gio_sai(value):
    with pytest.raises(ScheduleError):
        date_gmt_text(value)


# ====================================================================== nhãn


def test_nhan_thu_ngay_gio_viet_nam():
    when = datetime(2026, 11, 3, 1, 0, tzinfo=UTC)
    assert schedule_label(when) == "Thứ Ba, 03/11/2026 lúc 08:00 (giờ Việt Nam)"


def test_nhan_chu_nhat_va_qua_nua_dem():
    when = datetime(2026, 11, 7, 17, 30, tzinfo=UTC)  # 00:30 Chủ Nhật 08/11 giờ Việt Nam
    assert schedule_label(when) == "Chủ Nhật, 08/11/2026 lúc 00:30 (giờ Việt Nam)"


def test_nhan_du_7_thu():
    labels = [
        schedule_label(datetime(2026, 11, 2 + offset, 1, 0, tzinfo=UTC)).split(",")[0]
        for offset in range(7)
    ]
    assert labels == list(WEEKDAYS)


def test_nhan_mui_gio_khac_ghi_ten_mui_gio():
    when = datetime(2026, 11, 3, 1, 0, tzinfo=UTC)
    assert schedule_label(when, "UTC") == "Thứ Ba, 03/11/2026 lúc 01:00 (giờ UTC)"


def test_module_khong_doc_dong_ho_may():
    """Nhãn, giờ hẹn chỉ từ giờ đã chọn và giờ người gọi đưa vào (LC-T094-27): cả module không
    gọi ``now``, ``today``, ``utcnow``, ``time.time``."""
    import ast
    import inspect

    import seo_app.publish.schedule as module

    tree = ast.parse(inspect.getsource(module))
    called = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert not called & {"now", "today", "utcnow", "time", "monotonic"}


def test_nhan_tu_choi_gio_khong_mui_gio():
    with pytest.raises(ScheduleError):
        schedule_label(datetime(2026, 11, 3, 8, 0))


# ====================================================================== header Date


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Mon, 02 Nov 2026 01:00:00 GMT", NOW),
        ("Mon, 02 Nov 2026 08:00:00 +0700", NOW),
        ("Mon, 02 Nov 2026 01:00:00 UTC", NOW),
    ],
)
def test_doc_header_date(value, expected):
    parsed = parse_server_date(value)
    assert parsed == expected and parsed.tzinfo is UTC


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        "garbage",
        "Mon, 32 Nov 2026 01:00:00 GMT",
        "Mon, 02 Nov 2026 25:00:00 GMT",
        "Mon, 02 Nov 2026 01:00:00 -0000",  # RFC 2822: không rõ múi giờ
        "Mon, 02 Nov 2026 01:00:00",
        "Mon, 02 Nov 2026 01:00:00 GMT\r\nX-Evil: 1",
        "Mon, 02 Nov 2026 01:00:00 GMT" + " " * 40,
        "Th\N{LATIN SMALL LETTER U WITH HORN} 2, 02/11/2026",
        b"Mon, 02 Nov 2026 01:00:00 GMT",
        1793581200,
        ["Mon, 02 Nov 2026 01:00:00 GMT"],
    ],
)
def test_header_date_sai_thi_none(value):
    assert parse_server_date(value) is None


# ====================================================================== lớp chặn của client


def problem(mode="future", when=NOW + timedelta(days=1), server=NOW, local=NOW):
    return release_time_problem(mode, when, server_now=server, local_now=local)


def test_gio_hop_le_khong_chan():
    assert problem() == ""
    assert problem("publish", None) == ""


@pytest.mark.parametrize("mode", ["future", "publish"])
def test_khong_co_gio_may_chu_thi_chan(mode):
    assert problem(mode, None if mode == "publish" else NOW + timedelta(days=1), None) == (
        MSG_NO_SERVER_TIME
    )
    assert problem(mode, NOW + timedelta(days=1), datetime(2026, 11, 2, 1, 0)) == (
        MSG_NO_SERVER_TIME
    )
    assert problem(mode, NOW + timedelta(days=1), "Mon, 02 Nov 2026 01:00:00 GMT") == (
        MSG_NO_SERVER_TIME
    )


@pytest.mark.parametrize(
    ("skew", "expected"),
    [
        (MAX_CLOCK_SKEW, ""),
        (-MAX_CLOCK_SKEW, ""),
        (MAX_CLOCK_SKEW + timedelta(seconds=1), MSG_CLOCK_SKEW),
        (-MAX_CLOCK_SKEW - timedelta(seconds=1), MSG_CLOCK_SKEW),
        (timedelta(days=-3650), MSG_CLOCK_SKEW),
    ],
)
@pytest.mark.parametrize("mode", ["future", "publish"])
def test_lech_dong_ho_qua_2_phut_thi_chan(skew, expected, mode):
    when = NOW + timedelta(days=1) if mode == "future" else None
    assert problem(mode, when, local=NOW + skew) == expected


@pytest.mark.parametrize(
    ("gap", "expected"),
    [
        (-timedelta(days=1), MSG_PAST),
        (timedelta(0), MSG_PAST),
        (timedelta(microseconds=900_000), MSG_PAST),  # bỏ phần lẻ của giây: đúng bằng bây giờ
        (MIN_LEAD - timedelta(seconds=1), MSG_TOO_SOON),
        (MIN_LEAD - timedelta(microseconds=1), MSG_TOO_SOON),
        (MIN_LEAD, ""),
        (MAX_AHEAD, ""),
        (MAX_AHEAD + timedelta(seconds=1), MSG_TOO_FAR),
        (timedelta(days=400), MSG_TOO_FAR),
    ],
)
def test_khoang_hen_gio_tinh_theo_gio_may_chu(gap, expected):
    assert problem(when=NOW + gap) == expected


def test_server_nam_9999_khong_tran():
    far = datetime(9999, 12, 31, 23, 0, tzinfo=UTC)
    assert problem(when=far, server=far, local=far) == MSG_PAST


@pytest.mark.parametrize("when", [datetime(2026, 11, 3, 1, 0), None, "2026-11-03T01:00:00"])
def test_hen_gio_khong_mui_gio_thi_loi(when):
    with pytest.raises(ScheduleError):
        problem(when=when)


@pytest.mark.parametrize("mode", ["draft", "Future", "", None])
def test_hinh_thuc_la_thi_loi(mode):
    with pytest.raises(ScheduleError):
        problem(mode)


# ====================================================================== màn hình chọn giờ


def test_check_schedule_hop_le_khong_bao_gi():
    assert check_schedule(NOW + timedelta(days=1), now_utc=NOW) == []


@pytest.mark.parametrize(
    ("gap", "message"),
    [
        (-timedelta(hours=1), MSG_PAST),
        (timedelta(minutes=5), MSG_TOO_SOON),
        (timedelta(days=366), MSG_TOO_FAR),
    ],
)
def test_check_schedule_chan(gap, message):
    assert check_schedule(NOW + gap, now_utc=NOW) == [Notice(Level.BLOCK, message)]


def test_check_schedule_canh_bao_trung_phut_voi_bai_khac():
    when = datetime(2026, 11, 3, 1, 0, tzinfo=UTC)
    same = [datetime(2026, 11, 3, 8, 0, 30, tzinfo=VIETNAM)]
    assert check_schedule(when, now_utc=NOW, scheduled=same) == [Notice(Level.WARN, MSG_SAME_TIME)]
    other = [datetime(2026, 11, 3, 1, 1, tzinfo=UTC), datetime(2026, 11, 3, 0, 59, 59, tzinfo=UTC)]
    assert check_schedule(when, now_utc=NOW, scheduled=other) == []


def test_check_schedule_bo_gio_khong_mui_gio_trong_danh_sach_bai_khac():
    when = datetime(2026, 11, 3, 1, 0, tzinfo=UTC)
    scheduled = [datetime(2026, 11, 3, 1, 0), "2026-11-03T01:00:00", None]
    assert check_schedule(when, now_utc=NOW, scheduled=scheduled) == []


def test_check_schedule_vua_chan_vua_canh_bao():
    when = NOW + timedelta(minutes=5)
    notices = check_schedule(when, now_utc=NOW, scheduled=[when])
    assert [n.level for n in notices] == [Level.BLOCK, Level.WARN]


def test_check_schedule_gio_sai_thi_loi():
    with pytest.raises(ScheduleError):
        check_schedule(datetime(2026, 11, 3, 1, 0), now_utc=NOW)
    with pytest.raises(ScheduleError):
        check_schedule(NOW, now_utc=datetime(2026, 11, 2, 1, 0))
