"""Soi Lỗi T-109 (rút gọn): đưa trạng thái bài trên website về Google Sheets.

Kiểm độc lập với test của Thợ Máy, cùng bộ giả (``FakePlanSheet`` gắn ``FakeGoogle``, đi qua
``SheetsClient`` thật: đường cố định, ``RAW``). Không gọi Google, WordPress thật.

Trọng tâm: dữ liệu website và Sheet chưa tin cậy (ô gõ khác dạng, chữ dài, mồi trong ô); trạng thái
chỉ đi tới; «Lỡ lịch» đúng biên 15 phút ở mọi múi giờ; ghi khi Sheet đổi giữa chừng (chèn, xếp lại,
đổi cột, hai tab, lỗi giữa lô); ăn khớp với việc ghi trạng thái sau khi gửi của T-100 / T-102.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
import requests
import test_t109_website_status as base
from fake_google import SHEET_ID
from fake_plan_sheet import HEADER, FakePlanSheet
from test_plan_sync import COL, row

from seo_app.plan import model, sync, website
from seo_app.plan.website import WebChangeKind as Kind
from seo_app.plan.website import WebNoticeKind as Notice
from seo_app.storage.plan_cache import sheet_hash
from seo_app.wordpress.client import PostState

private_key = base.private_key
fake = base.fake
client = base.client
state, rows, check, apply = base.state, base.rows, base.check, base.apply
NOW, NOV3_08, NOV5_09 = base.NOW, base.NOV3_08, base.NOV5_09
APP_COLUMNS = base.APP_COLUMNS
ORDER = (
    model.STATUS_NEW,
    model.STATUS_WRITING,
    model.STATUS_DRAFT_SENT,
    model.STATUS_SCHEDULED,
    model.STATUS_PUBLISHED,
)
FORMULA_START = ("=", "+", "-", "@", "\t", "\r")
RLO = chr(0x202E)
ZWSP = chr(0x200B)
BAIT = f"{RLO}=IMPORTXML(1)[x](javascript:1)<b>MOI"


def texts_of(result) -> list[str]:
    return [u.reason for u in result.updates] + [n.message for n in result.notices]


def assert_no_bait(*texts: str) -> None:
    for text in texts:
        for piece in ("MOI", RLO, "IMPORTXML", "javascript", "<b>", ZWSP):
            assert piece not in text, text


# ====================================================================== lỗi mới (xfail)


def test_key_with_leading_blanks_never_writes_a_duplicate_row(fake, client):
    """Mã bài B-070 ở hai dòng: dòng 2 gõ sau 30 dấu cách, dòng 3 gõ thường. Bộ đọc nhận dòng 2 là
    B-070 và bỏ dòng 3 («Mã bài trùng»), nhưng ``key_rows`` (cắt 30 ký tự **trước** khi làm sạch)
    chỉ thấy dòng 3: kiểm đề xuất cho dòng 2, ghi lại vào dòng 3. Mã bài trùng thì không ghi
    (LC-T094-28, thiết kế 2.5)."""
    blanks = " " * 30
    sheet = FakePlanSheet(fake, rows(
        row(blanks + "B-070", "cửa cuốn", status="Đã hẹn giờ", wp_post_id=blanks + "170"),
        row("B-070", "cửa kéo", status="Đã hẹn giờ", wp_post_id=170),
    ))  # fmt: skip
    plan = sync.read_sheet(client, now=NOW)
    assert any("Mã bài trùng" in warning for warning in plan.warnings)  # bộ đọc thấy trùng
    apply(client, check(client, {170: state(170, "publish", NOV3_08)}))
    assert sheet.updates == []


@pytest.mark.parametrize("lead", [" " * 30, ZWSP * 30], ids=["dau-cach", "vo-hinh"])
def test_post_on_two_rows_is_never_proposed_whatever_the_blanks(fake, client, lead):
    """Bộ đọc nối cả hai dòng với bài 170 (ô dòng 3 có 30 ký tự trắng hay vô hình ở đầu), nhưng
    ``_post_counts`` đọc ô bằng ``_post_id_of`` (cắt 30 ký tự trước khi làm sạch) nên chỉ đếm một
    dòng: cả hai dòng được đề xuất, ghi được dòng 2. Một bài nối nhiều dòng: chỉ cảnh báo."""
    FakePlanSheet(fake, rows(
        row("B-001", "cửa cuốn", status="Đã hẹn giờ", wp_post_id=170),
        row("B-002", "cửa kéo", status="Đã hẹn giờ", wp_post_id=lead + "170"),
    ))  # fmt: skip
    plan = sync.read_sheet(client, now=NOW)
    assert [r.plan.wp_post_id for r in plan.rows] == [170, 170]  # bộ đọc nối cả hai dòng
    result = check(client, {170: state(170, "publish", NOV3_08)})
    assert result.updates == ()


@pytest.mark.parametrize(
    ("status", "published_at"),
    [("Xong rồi", ""), ("Đã hẹn giờ", "hôm qua"), ("Đã đăng", "hôm qua")],
)
def test_what_check_proposes_is_writable_while_sheet_is_unchanged(
    fake, client, status, published_at
):
    """Bộ đọc coi ô không đọc được là trống («Chưa viết», không ngày) nên kiểm đề xuất; lúc ghi ô
    đó là «đã khác» nên luôn từ chối với lý do «Dòng vừa bị sửa ở nơi khác», lần kiểm sau đề xuất
    lại y hệt. Sheet không đổi giữa lúc kiểm và lúc ghi thì không được có xung đột."""
    FakePlanSheet(fake, rows(row("B-001", "cửa cuốn", status=status, wp_post_id=170,
                                 published_at=published_at)))  # fmt: skip
    result = check(client, {170: state(170, "publish", NOV3_08)})
    outcome = apply(client, result)
    assert outcome.conflicts == ()


# ========================================= gần lỗi mới: các dạng gõ khác mà hai bộ đọc khớp nhau


@pytest.mark.parametrize("other", ["b-70", "B-0070", " " * 20 + "B-070", ZWSP + "B-070"])
def test_key_typed_differently_on_two_rows_is_a_duplicate(fake, client, other):
    sheet = FakePlanSheet(fake, rows(
        row("B-070", "cửa cuốn", status="Đã hẹn giờ", wp_post_id=170),
        row(other, "cửa kéo", status="Đã hẹn giờ", wp_post_id=171),
    ))  # fmt: skip
    result = check(client, {170: state(170, "publish"), 171: state(171, "publish")})
    assert result.updates == ()
    assert [n.kind for n in result.notices] == [Notice.DUPLICATE_KEY]
    apply(client, result)
    assert sheet.updates == []


@pytest.mark.parametrize("other", ["0170", " 170 ", 170.0, ZWSP + "170", "１７０"])
def test_post_typed_differently_on_two_rows_is_shared(fake, client, other):
    FakePlanSheet(fake, rows(
        row("B-001", "cửa cuốn", status="Đã hẹn giờ", wp_post_id=170),
        row("B-002", "cửa kéo", status="Đã hẹn giờ", wp_post_id=other),
    ))  # fmt: skip
    result = check(client, {170: state(170, "publish")})
    assert result.updates == ()
    assert [n.kind for n in result.notices] == [Notice.SHARED_POST]


@pytest.mark.parametrize(
    ("status", "published_at"),
    [
        ("da dang bai", ""),
        ("ĐÃ HẸN GIỜ", ""),
        ("Đã hẹn giờ", "03/11/2026 08:00"),
        ("Đã hẹn giờ", 46329.333333333336),  # ô ngày giờ của Sheets: 03/11/2026 08:00
        ("Đã đăng", "2026-11-03T01:00:00Z"),
        ("Đã gửi nháp", ""),
    ],
)
def test_readable_cells_in_other_forms_are_written(fake, client, status, published_at):
    sheet = FakePlanSheet(fake, rows(row("B-001", "cửa cuốn", status=status, wp_post_id=170,
                                         published_at=published_at)))  # fmt: skip
    result = check(client, {170: state(170, "publish", NOV3_08)})
    outcome = apply(client, result)
    assert outcome.conflicts == () and outcome.unsure == () and outcome.not_written == ()
    assert check(client, {170: state(170, "publish", NOV3_08)}).updates == ()
    assert sheet.cell(2, COL["status"]) in (status, "Đã đăng")


# ============================================================ 1. dữ liệu website chưa tin cậy


class Sly(str):
    """Chuỗi giả dạng (lớp con của ``str``): không được coi là trạng thái thật."""


def test_odd_website_values_never_crash_late_or_leak(fake, client):
    odd = {
        401: state(401, "future", "２０２６-１１-０５T０２:００:００"),
        402: state(402, "future", "2026-11-03T01:00:0" + chr(0xD800)),
        403: state(403, "future", "2026-02-29T00:00:00"),
        404: state(404, "publish", "2026-12-31T23:59:60"),
        405: state(405, "future", "0000-00-00T00:00:00"),
        406: state(406, "future", "9" * 100_000),
        407: PostState(id=407, status="future", date_gmt=None),  # type: ignore[arg-type]
        408: state(408, "publish" + RLO),
        409: PostState(id=409, status=Sly("publish")),
        410: PostState(id="410", status="publish"),  # type: ignore[arg-type]
    }
    lines = [row(f"B-{post}", f"cửa số {post}", status="Đã gửi nháp", wp_post_id=post)
             for post in odd]  # fmt: skip
    FakePlanSheet(fake, rows(*lines))
    started = time.perf_counter()
    result = check(client, odd)
    assert time.perf_counter() - started < 2
    assert not result.late
    assert all(update.published_after is None for update in result.updates)
    assert sorted(u.wp_post_id for u in result.updates) == [401, 402, 403, 404, 405, 406, 407]
    notices = {(n.kind, n.wp_post_id) for n in result.notices}
    odd_dates = {post for kind, post in notices if kind is Notice.ODD_DATE}
    # T-109 lượt 2 (Chỉ Huy duyệt 31/10 00:45, R5): bài 407 (hẹn giờ, website không trả giờ)
    # nay cũng có cảnh báo «giờ lạ» (trước: range(401, 407), không có 407).
    assert odd_dates == set(range(401, 408))
    assert {post for kind, post in notices if kind is Notice.MISSING} == {408, 409, 410}
    assert_no_bait(*texts_of(result))


@pytest.mark.parametrize(
    ("date_gmt", "shown"),
    [("2035-12-31T16:59:59", "31/12/2035 23:59"), ("2019-12-31T17:00:00", "01/01/2020 00:00")],
)
def test_year_edges_follow_vietnam_time_and_read_back(fake, client, date_gmt, shown):
    sheet = FakePlanSheet(fake, rows(row("B-001", "cửa cuốn", status="Đã gửi nháp",
                                         wp_post_id=170)))  # fmt: skip
    result = check(client, {170: state(170, "publish", date_gmt)})
    (update,) = result.updates
    assert update.fields == ("status", "published_at") and shown in update.reason
    apply(client, result)
    assert sheet.cell(2, COL["published_at"]).startswith(shown[6:10])  # năm giờ Việt Nam
    again = check(client, {170: state(170, "publish", date_gmt)})
    assert again.updates == () and again.notices == ()


@pytest.mark.parametrize("date_gmt", ["2035-12-31T17:00:00", "2019-12-31T16:59:59"])
def test_year_edges_outside_the_plan_years_are_odd(fake, client, date_gmt):
    FakePlanSheet(fake, rows(row("B-001", "cửa cuốn", status="Đã gửi nháp", wp_post_id=170)))
    result = check(client, {170: state(170, "publish", date_gmt)})
    (update,) = result.updates
    assert update.fields == ("status",) and update.published_after is None
    assert [n.kind for n in result.notices] == [Notice.ODD_DATE]


# ============================================================== 1. dữ liệu Sheet chưa tin cậy


def test_messages_never_copy_hostile_cells(fake, client):
    statuses = ["Đã hẹn giờ", "Bỏ", "Đã đăng", "Đã gửi nháp", "Đang viết", "Đã đăng", "Đã hẹn giờ"]
    lines = [row(f"b-{n + 1}", f"{BAIT} cửa {n}", status=status, wp_post_id=200 + n,
                 secondary=BAIT, title_hint=BAIT, notes=BAIT, intent=BAIT, slug=BAIT)
             for n, status in enumerate(statuses)]  # fmt: skip
    lines += [
        row("", f"{BAIT} x", status="Đã hẹn giờ", wp_post_id=300),
        row("B-050", f"{BAIT} y", status="Đã hẹn giờ", wp_post_id=301, notes=BAIT),
        row("b-0050", f"{BAIT} z", status="Đã hẹn giờ", wp_post_id=302, notes=BAIT),
        row("B-060", f"{BAIT} y", status="Đã hẹn giờ", wp_post_id=303, notes=BAIT),
        row("B-061", f"{BAIT} y", status="Đã hẹn giờ", wp_post_id=303, notes=BAIT),
        row("B-062", "x" * 5000, status="Đã hẹn giờ", wp_post_id=304, notes="y" * 50_000),
        row("B-063", f"{BAIT} m", status="Đã đăng", wp_post_id=305, notes=BAIT),
    ]
    sheet = FakePlanSheet(fake, rows(*lines))
    states = {
        200: state(200, "publish", NOV3_08), 201: state(201, "draft"),
        202: state(202, "future", NOV3_08), 203: state(203, "private"),
        204: state(204, "pending"), 205: state(205, "draft"),
        206: state(206, "future", "2026-13-01T00:00:00"),
        **{post: state(post, "publish") for post in (300, 301, 302, 303, 304)},
    }  # fmt: skip
    result = check(client, states, [*range(200, 208), *range(300, 306)])
    kinds = {n.kind for n in result.notices}
    assert {Notice.DROPPED, Notice.AHEAD, Notice.LATE, Notice.PRIVATE, Notice.BACK_TO_DRAFT,
            Notice.ODD_DATE, Notice.NO_KEY, Notice.DUPLICATE_KEY, Notice.SHARED_POST,
            Notice.MISSING} <= kinds  # fmt: skip
    assert_no_bait(*texts_of(result))
    for update in result.updates:  # Mã bài trong câu là mã đã chuẩn hóa, không phải chữ ô
        assert update.key.startswith("B-0") and update.key in update.label
    sheet.set(2, COL["status"], BAIT)  # B-001 (có đề xuất) vừa bị sửa ô Trạng thái
    outcome = apply(client, result)
    assert outcome.conflicts and outcome.written
    assert_no_bait(outcome.message, *(c.reason for c in outcome.conflicts))


def test_key_typed_differently_between_check_and_write(fake, client):
    sheet = FakePlanSheet(fake, rows(
        row("b-70", "cửa cuốn", status="Đã hẹn giờ", wp_post_id=170),
        row("KV-0012", "cửa kéo", status="Đã gửi nháp", wp_post_id=171),
    ))  # fmt: skip
    states = {170: state(170, "publish", NOV3_08), 171: state(171, "future", NOV5_09)}
    result = check(client, states)
    assert [u.key for u in result.updates] == ["B-070", "KV-012"]
    sheet.set(2, COL["key"], " B-070 ")
    sheet.set(3, COL["key"], "kv-12")
    outcome = apply(client, result)
    assert len(outcome.written) == 2
    assert {r for r, _, _ in sheet.written_cells()} == {2, 3}
    assert (sheet.cell(2, COL["key"]), sheet.cell(3, COL["key"])) == (" B-070 ", "kv-12")


# ============================================================ 2. chỉ đi tới, «Lỡ lịch»


def test_status_only_moves_forward_for_every_pair(fake, client):
    """6 trạng thái Sheet × 5 trạng thái website, có và không có «Ngày đăng thực tế»: không đề xuất
    lùi, không đề xuất cho dòng «Bỏ» hay bài riêng tư; ghi rồi kiểm lại thì không còn đề xuất; chỉ
    3 ô app được ghi, giá trị không thể thành công thức; không thêm, không xóa dòng."""
    webs = ("draft", "pending", "future", "publish", "private")
    lines, states, before = [], {}, {}
    for number, (status, web) in enumerate(
        ((s, w) for s in model.STATUSES for w in webs for _ in range(2)), start=1
    ):
        key, post = f"B-{number:03d}", 500 + number
        shown = "2026-11-04 08:00+07:00" if number % 2 else ""
        lines.append(row(key, f"cửa số {number}", status=status, wp_post_id=post,
                         published_at=shown, notes="ghi chú"))  # fmt: skip
        states[post] = state(post, web, NOV5_09 if web in ("future", "publish") else "")
        before[key] = status
    sheet = FakePlanSheet(fake, rows(*lines))
    result = check(client, states)
    assert result.updates
    for update in result.updates:
        assert update.status_before != model.STATUS_DROPPED
        assert states[update.wp_post_id].status != "private"
        assert ORDER.index(update.status_after) >= ORDER.index(update.status_before)
        assert (update.kind is Kind.DATE) is (update.status_after == update.status_before)
    apply(client, result)
    assert check(client, states).updates == ()
    assert sheet.appends == [] and len(sheet.grid) == len(lines) + 1
    for _row, column, value in sheet.written_cells():
        assert column in APP_COLUMNS
        assert isinstance(value, str) and value and not value.startswith(FORMULA_START)
    for line in sheet.grid[1:]:
        old, new = before[line[COL["key"]]], line[COL["status"]]
        if old == model.STATUS_DROPPED:
            assert new == old
        else:
            assert ORDER.index(new) >= ORDER.index(old)
        assert line[COL["notes"]] == "ghi chú"


def test_older_check_applied_after_newer_never_moves_back(fake, client):
    sheet = FakePlanSheet(fake, rows(row("B-001", "cửa cuốn", status="Đã gửi nháp",
                                         wp_post_id=170)))  # fmt: skip
    older = check(client, {170: state(170, "future", NOV5_09)})  # → «Đã hẹn giờ»
    newer = check(client, {170: state(170, "publish", NOV5_09)})  # → «Đã đăng»
    assert len(apply(client, newer).written) == 1
    outcome = apply(client, older)
    assert [c.update.key for c in outcome.conflicts] == ["B-001"]
    assert sheet.cell(2, COL["status"]) == "Đã đăng" and len(sheet.updates) == 1


@pytest.mark.parametrize(
    ("after", "late"),
    [
        (timedelta(minutes=14, seconds=59), False),
        (timedelta(minutes=15), False),
        (timedelta(minutes=15, microseconds=1), True),
        (timedelta(minutes=15, seconds=1), True),
        (-timedelta(minutes=30), False),
    ],
)
@pytest.mark.parametrize("zone", ["Asia/Ho_Chi_Minh", "UTC", "America/New_York"])
def test_late_boundary_to_the_microsecond_in_any_timezone(fake, client, after, late, zone):
    """«Lỡ lịch» khi quá giờ hẹn **hơn** 15 phút, tính trên giờ tuyệt đối (múi giờ của ``now``
    không đổi kết quả); giờ trong câu báo là giờ Việt Nam."""
    due = datetime(2026, 11, 3, 2, 0, tzinfo=UTC)
    FakePlanSheet(fake, rows(row("B-001", "cửa cuốn", status="Đã hẹn giờ", wp_post_id=170,
                                 published_at="2026-11-03 09:00+07:00")))  # fmt: skip
    now = (due + after).astimezone(ZoneInfo(zone))
    result = check(client, {170: state(170, "future", "2026-11-03T02:00:00")}, now=now)
    assert result.updates == () and bool(result.late) is late
    if late:
        assert "hẹn giờ lúc 03/11/2026 09:00 đã quá giờ" in result.late[0].message


# ================================================================ 3. ghi khi Sheet đổi giữa chừng


def test_rows_inserted_and_sorted_before_writing(fake, client):
    sheet = FakePlanSheet(fake, rows(
        row("B-001", "cửa cuốn", status="Đã hẹn giờ", wp_post_id=170),
        row("B-002", "cửa kéo", status="Đã gửi nháp", wp_post_id=171),
        row("B-003", "cửa sắt", status="Đang viết", wp_post_id=172),
    ))  # fmt: skip
    states = {
        170: state(170, "publish", NOV3_08),
        171: state(171, "future", NOV5_09),
        172: state(172, "draft"),
    }
    result = check(client, states)
    body = sheet.grid[1:]
    sheet.grid[1:] = [row("B-009", "mới chèn", status="Chưa viết"), *reversed(body)]
    outcome = apply(client, result)
    assert len(outcome.written) == 3 and sheet.appends == []
    final = {line[COL["key"]]: line for line in sheet.grid[1:]}
    assert final["B-001"][COL["status"]] == "Đã đăng"
    assert final["B-002"][COL["status"]] == "Đã hẹn giờ"
    assert final["B-002"][COL["published_at"]] == "2026-11-05 09:00+07:00"
    assert final["B-003"][COL["status"]] == "Đã gửi nháp"
    assert final["B-009"][COL["status"]] == "Chưa viết"
    assert 2 not in {r for r, _, _ in sheet.written_cells()}  # dòng mới chèn không bị chạm


def test_columns_moved_before_writing(fake, client):
    """Chủ dự án đổi chỗ cột «Trạng thái» và «Ghi chú của thợ» sau lúc kiểm: ghi theo tên cột của
    bản đọc lại, ô ghi chú không bị đè."""
    sheet = FakePlanSheet(fake, rows(row("B-001", "cửa cuốn", status="Đã hẹn giờ", wp_post_id=170,
                                         notes="ghi chú")))  # fmt: skip
    result = check(client, {170: state(170, "publish", NOV3_08)})
    for line in sheet.grid:
        line[COL["status"]], line[COL["notes"]] = line[COL["notes"]], line[COL["status"]]
    outcome = apply(client, result)
    assert len(outcome.written) == 1
    assert sheet.cell(2, COL["notes"]) == "Đã đăng"  # cột «Trạng thái» giờ ở chỗ cũ của ghi chú
    assert sheet.cell(2, COL["status"]) == "ghi chú"
    assert sheet.cell(1, COL["notes"]) == "Trạng thái"


def two_rows(fake):
    return FakePlanSheet(fake, rows(
        row("B-001", "cửa cuốn", status="Đã hẹn giờ", wp_post_id=170),
        row("B-002", "cổng inox", status="Đã gửi nháp", wp_post_id=171),
    ))  # fmt: skip


TWO_STATES = {170: state(170, "publish", NOV3_08), 171: state(171, "future", NOV5_09)}


def test_two_tabs_apply_the_same_check_once(fake, client):
    sheet = two_rows(fake)
    result = check(client, TWO_STATES)
    first, second = apply(client, result), apply(client, result)
    assert len(first.written) == 2 and second.written == () and len(second.already) == 2
    assert len(sheet.updates) == 1 and second.message == "2 dòng đã đúng sẵn."


def test_two_tabs_reading_before_either_writes_write_the_same_cells(fake, client, monkeypatch):
    """Khe hở thiết kế 2.5: tab sau đọc trước khi tab đầu ghi. Cùng một lần kiểm thì hai lệnh ghi
    đúng các giá trị đó (không lệch, không lùi, không chạm cột khác)."""
    sheet = two_rows(fake)
    result = check(client, TWO_STATES)
    snapshot = client.read_plan_values()  # tab sau đã đọc
    apply(client, result)
    first = [list(line) for line in sheet.grid]
    monkeypatch.setattr(client, "read_plan_values", lambda: snapshot)
    assert len(apply(client, result).written) == 2
    assert sheet.grid == first and len(sheet.updates) == 2
    assert {column for _, column, _ in sheet.written_cells()} <= APP_COLUMNS


def test_error_in_the_second_batch_stops_the_rest(fake, client, monkeypatch):
    monkeypatch.setattr(website, "MAX_UPDATES", 2)  # 2 ô mỗi dòng: một dòng mỗi lệnh
    lines = [row(f"B-{100 + n:03d}", f"cửa số {n}", status="Đã hẹn giờ", wp_post_id=300 + n)
             for n in range(4)]  # fmt: skip
    sheet = FakePlanSheet(fake, rows(*lines))
    states = {300 + n: state(300 + n, "publish") for n in range(4)}
    result = check(client, states)
    real, calls = client.update_cells, []

    def second_breaks(cells):
        calls.append(len(cells))
        if len(calls) == 2:  # mất mạng ở lệnh thứ hai, Google chưa ghi
            sheet.fail("update", requests.exceptions.ConnectionError("đứt"))
        return real(cells)

    monkeypatch.setattr(client, "update_cells", second_breaks)
    outcome = apply(client, result)
    assert calls == [2, 2] and len(sheet.updates) == 1
    assert [u.key for u in outcome.written] == ["B-100"]
    assert [u.key for u in outcome.unsure] == ["B-101"]
    assert [u.key for u in outcome.not_written] == ["B-102", "B-103"]
    assert "chưa rõ đã ghi chưa" in outcome.message and "2 dòng chưa ghi." in outcome.message
    assert [u.key for u in check(client, states).updates] == ["B-101", "B-102", "B-103"]


# ====================================================== 4. ăn khớp với T-100 (T-102 gửi bài)


def test_pending_send_write_after_website_write_never_goes_back(fake, client):
    """Bài gửi lại từ app với giờ hẹn mới (việc ghi Sheet còn nợ) trong lúc «Cập nhật trạng thái từ
    website» ghi giờ cũ: việc còn nợ thấy dòng đã «Đã hẹn giờ» nên ``ALREADY`` (không lùi, không
    ghi thêm); lần kiểm sau đề xuất sửa «Ngày đăng thực tế» theo website."""
    sheet = FakePlanSheet(fake, rows(row("B-001", "cửa cuốn", status="Đã gửi nháp",
                                         wp_post_id=170)))  # fmt: skip
    result = check(client, {170: state(170, "future", NOV5_09)})
    ref = sync.plan_ref(sync.read_sheet(client, now=NOW).find("B-001"), SHEET_ID, now=NOW)
    later = datetime(2026, 11, 6, 2, 0, tzinfo=UTC)
    write = sync.status_write(ref, model.STATUS_SCHEDULED, wp_post_id=170, published_at=later,
                              now=NOW)  # fmt: skip
    assert result.sheet_hash == ref.sheet_hash == sheet_hash(SHEET_ID)
    assert len(apply(client, result).written) == 1
    done = sync.write_status(client, write, sheet_id=SHEET_ID, now=NOW)
    assert done.outcome is sync.WriteOutcome.ALREADY and len(sheet.updates) == 1
    (update,) = check(client, {170: state(170, "future", "2026-11-06T02:00:00")}).updates
    assert update.kind is Kind.DATE and update.published_after == later


def test_stale_website_check_after_send_write_is_a_conflict(fake, client):
    """Ngược lại: app ghi trạng thái sau khi gửi trước, rồi mới áp dụng lần kiểm website cũ: xung
    đột, không đè giờ app vừa ghi; sau đó «Đang viết» (mở lại bài) là bước trước nên không đổi."""
    sheet = FakePlanSheet(fake, rows(row("B-001", "cửa cuốn", status="Đã gửi nháp",
                                         wp_post_id=170)))  # fmt: skip
    result = check(client, {170: state(170, "future", NOV5_09)})
    ref = sync.plan_ref(sync.read_sheet(client, now=NOW).find("B-001"), SHEET_ID, now=NOW)
    later = datetime(2026, 11, 6, 2, 0, tzinfo=UTC)
    write = sync.status_write(ref, model.STATUS_SCHEDULED, wp_post_id=170, published_at=later,
                              now=NOW)  # fmt: skip
    assert sync.write_status(client, write, sheet_id=SHEET_ID, now=NOW).outcome is (
        sync.WriteOutcome.WRITTEN
    )
    outcome = apply(client, result)
    assert [c.update.key for c in outcome.conflicts] == ["B-001"]
    assert sheet.cell(2, COL["published_at"]) == "2026-11-06 09:00+07:00"
    fresh = sync.plan_ref(sync.read_sheet(client, now=NOW).find("B-001"), SHEET_ID, now=NOW)
    writing = sync.status_write(fresh, model.STATUS_WRITING, now=NOW)
    assert sync.write_status(client, writing, sheet_id=SHEET_ID, now=NOW).outcome is (
        sync.WriteOutcome.LATER
    )
    assert sheet.cell(2, COL["status"]) == "Đã hẹn giờ" and HEADER[COL["status"]] == "Trạng thái"
