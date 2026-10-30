"""T-109 (Thợ Máy): đưa trạng thái bài trên website về Google Sheets (``seo_app.plan.website``).

``check_website`` thuần (không mạng); ``apply_website_changes`` ghi qua đúng đường T-100 trên Sheet
giả có trạng thái (``FakePlanSheet`` gắn ``FakeGoogle``, đi qua ``SheetsClient`` thật: đường cố
định, ``RAW``). Không gọi Google, WordPress thật (LC-T094-1); khóa RSA sinh lúc chạy test.
"""

from __future__ import annotations

import dataclasses
import json
import os
from datetime import UTC, datetime, timedelta

import pytest
import requests
from fake_google import SHEET_ID, FakeGoogle, key_info, make_session, new_private_key
from fake_plan_sheet import HEADER, FakePlanSheet
from test_plan_sync import COL, MOI, row

from seo_app.google.service_account import load_service_account
from seo_app.google.sheets import SheetsClient, SheetsError
from seo_app.plan import model, sync, website
from seo_app.plan.website import WebChangeKind as Kind
from seo_app.plan.website import WebNoticeKind as Notice
from seo_app.storage.drafts import DraftPlanRef
from seo_app.storage.plan_cache import sheet_hash
from seo_app.wordpress.client import PostState

TZ = model.TIMEZONE
NOW = datetime(2026, 11, 3, 9, 30, tzinfo=TZ)  # 02:30 UTC
NOV3_08 = "2026-11-03T01:00:00"  # 08:00 giờ Việt Nam
NOV5_09 = "2026-11-05T02:00:00"  # 09:00 giờ Việt Nam
APP_COLUMNS = {COL["status"], COL["published_at"], COL["updated_at"]}


@pytest.fixture(scope="module")
def private_key():
    return new_private_key()


@pytest.fixture
def fake():
    return FakeGoogle()


@pytest.fixture
def client(fake, tmp_path, private_key):
    """``SheetsClient`` thật nối Google giả (như ``tests/test_plan_sync.py``)."""
    folder = tmp_path / "bi-mat"
    folder.mkdir()
    path = folder / "du-an-thu-0123abcd.json"
    path.write_text(json.dumps(key_info(private_key)), encoding="utf-8")
    if os.name != "nt":
        path.chmod(0o600)
    project = tmp_path / "du-an"
    project.mkdir()
    account = load_service_account(path, project_root=project)
    return SheetsClient(SHEET_ID, account, session=make_session(fake), sleep=lambda _s: None)


def vn(text: str) -> datetime:
    return datetime.fromisoformat(text).replace(tzinfo=UTC).astimezone(TZ)


def state(post: int, status: str, date_gmt: str = "") -> PostState:
    return PostState(id=post, status=status, date_gmt=date_gmt)


def rows(*lines):
    return [HEADER, *lines]


def check(client, states, asked=None, *, now=NOW):
    plan = sync.read_sheet(client, now=now)
    asked = sorted({r.plan.wp_post_id for r in plan.rows if r.plan.wp_post_id}) if asked is None \
        else asked  # fmt: skip
    return website.check_website(plan, states, asked, sheet_id=SHEET_ID, now=now)


def apply(client, result, updates=None, *, now=NOW):
    return website.apply_website_changes(client, result, updates, sheet_id=SHEET_ID, now=now)


def only(result, kind):
    found = [n for n in result.notices if n.kind is kind]
    assert len(found) == 1, result.notices
    return found[0]


def no_cell_text(*texts):
    for text in texts:
        assert MOI not in text


# ================================================================== kiểm (thuần, không ghi)


def test_scheduled_post_now_published(fake, client):
    sheet = FakePlanSheet(fake, rows(
        row("B-010", "sửa cửa cuốn", status="Đã hẹn giờ", wp_post_id=101,
            published_at="2026-11-03 08:00+07:00", notes=MOI),
    ))  # fmt: skip
    result = check(client, {101: state(101, "publish", NOV3_08)})
    (update,) = result.updates
    assert update.kind is Kind.PUBLISHED and update.fields == ("status",)
    assert (update.status_before, update.status_after) == ("Đã hẹn giờ", "Đã đăng")
    assert update.published_after == vn(NOV3_08) and update.row_number == 2
    assert update.reason == "Bài #101 đã đăng trên website lúc 03/11/2026 08:00."
    assert result.notices == () and result.sheet_hash == sheet_hash(SHEET_ID)
    assert sheet.updates == []  # kiểm không ghi gì

    outcome = apply(client, result)
    assert outcome.written == (update,) and outcome.message.startswith("Đã cập nhật 1 dòng")
    assert sorted(sheet.written_cells()) == [
        (2, COL["status"], "Đã đăng"),
        (2, COL["updated_at"], "2026-11-03 09:30+07:00"),
    ]
    assert sheet.update_options == [{"valueInputOption": "RAW", "includeValuesInResponse": False}]
    assert sheet.appends == []
    no_cell_text(update.reason, outcome.message)


def test_scheduled_in_wordpress_admin_is_picked_up(fake, client):
    """Chủ dự án tự hẹn giờ trong trang quản trị (câu hỏi 5A): «Đã gửi nháp» → «Đã hẹn giờ»."""
    sheet = FakePlanSheet(fake, rows(row("B-011", "cổng inox", status="Đã gửi nháp",
                                         wp_post_id=102)))  # fmt: skip
    result = check(client, {102: state(102, "future", NOV5_09)})
    (update,) = result.updates
    assert update.kind is Kind.SCHEDULED and update.fields == ("status", "published_at")
    assert update.reason == "Bài #102 đang hẹn giờ trên website lúc 05/11/2026 09:00."
    assert result.notices == ()  # chưa tới giờ: không «Lỡ lịch»
    apply(client, result)
    assert sorted(sheet.written_cells()) == [
        (2, COL["status"], "Đã hẹn giờ"),
        (2, COL["published_at"], "2026-11-05 09:00+07:00"),
        (2, COL["updated_at"], "2026-11-03 09:30+07:00"),
    ]


@pytest.mark.parametrize("web_status", ["draft", "pending"])
def test_unsent_row_with_draft_on_website_moves_to_draft_sent(fake, client, web_status):
    FakePlanSheet(fake, rows(row("B-012", "lan can", status="Đang viết", wp_post_id=103)))
    (update,) = check(client, {103: state(103, web_status)}).updates
    assert update.kind is Kind.DRAFT and update.status_after == "Đã gửi nháp"
    assert update.fields == ("status",)


def test_rescheduled_in_admin_only_changes_date(fake, client):
    FakePlanSheet(fake, rows(row("B-013", "cửa kính", status="Đã hẹn giờ", wp_post_id=104,
                                 published_at="2026-11-04 08:00+07:00")))  # fmt: skip
    (update,) = check(client, {104: state(104, "future", NOV5_09)}).updates
    assert update.kind is Kind.DATE and update.fields == ("published_at",)
    assert update.reason == (
        "Giờ đăng của bài #104 trên website là 05/11/2026 09:00, khác ô «Ngày đăng thực tế»."
    )


def test_nothing_to_do_when_sheet_matches(fake, client):
    FakePlanSheet(fake, rows(
        row("B-014", "cửa sắt", status="Đã đăng", wp_post_id=105,
            published_at="2026-11-03 08:00+07:00"),
        row("B-015", "cửa nhôm", status="Đã gửi nháp", wp_post_id=106),
    ))  # fmt: skip
    result = check(client, {105: state(105, "publish", NOV3_08), 106: state(106, "draft")})
    assert result.updates == () and result.notices == ()


@pytest.mark.parametrize(
    ("minutes", "late"), [(14, False), (15, False), (16, True), (60 * 24, True)]
)
def test_missed_schedule_after_15_minutes(fake, client, minutes, late):
    due = NOW - timedelta(minutes=minutes)
    due_gmt = due.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S")
    shown = due.isoformat(sep=" ", timespec="minutes")
    FakePlanSheet(fake, rows(row("B-020", "sửa cổng", status="Đã hẹn giờ", wp_post_id=110,
                                 published_at=shown)))  # fmt: skip
    result = check(client, {110: state(110, "future", due_gmt)})
    assert result.updates == ()  # «Lỡ lịch» chỉ là nhãn, không ghi Sheet
    assert bool(result.late) is late
    if late:
        notice = only(result, Notice.LATE)
        assert notice.message.startswith("Lỡ lịch: bài #110 (dòng B-020) hẹn giờ lúc ")
        assert "cron" in notice.message and notice.key == "B-020" and notice.wp_post_id == 110


def test_missed_schedule_still_moves_draft_row_forward(fake, client):
    FakePlanSheet(fake, rows(row("B-021", "sửa cổng", status="Đã gửi nháp", wp_post_id=111)))
    result = check(client, {111: state(111, "future", NOV3_08)})  # 08:00, giờ là 09:30
    assert [u.kind for u in result.updates] == [Kind.SCHEDULED]
    assert only(result, Notice.LATE).wp_post_id == 111


@pytest.mark.parametrize("asked", [[120], [120, 121]])
def test_deleted_trashed_or_no_permission_only_warns(fake, client, asked):
    """Bài đã xóa, trong thùng rác, hay tài khoản không còn quyền xem: ``post_statuses`` không trả
    mục đó. Chỉ cảnh báo, không tự sửa Sheet (thiết kế 1.7)."""
    sheet = FakePlanSheet(fake, rows(row("B-030", "cửa cuốn", status="Đã đăng", wp_post_id=120)))
    result = check(client, {}, asked)
    assert result.updates == ()
    notice = only(result, Notice.MISSING)
    assert notice.message.startswith("Không thấy bài #120 (dòng B-030) trên website")
    assert "không còn quyền xem" in notice.message
    assert apply(client, result).written == () and sheet.updates == []


@pytest.mark.parametrize(
    ("status", "web_status", "kind"),
    [
        ("Đã hẹn giờ", "draft", Notice.BACK_TO_DRAFT),
        ("Đã đăng", "draft", Notice.BACK_TO_DRAFT),
        ("Đã đăng", "pending", Notice.BACK_TO_DRAFT),
        ("Đã đăng", "future", Notice.AHEAD),
        ("Đã đăng", "private", Notice.PRIVATE),
        ("Đã gửi nháp", "private", Notice.PRIVATE),
        ("Bỏ", "publish", Notice.DROPPED),
        ("Bỏ", "draft", Notice.DROPPED),
    ],
)
def test_never_goes_back_only_warns(fake, client, status, web_status, kind):
    FakePlanSheet(fake, rows(row("B-031", "cửa cuốn", status=status, wp_post_id=121)))
    result = check(client, {121: state(121, web_status, NOV5_09)})
    assert result.updates == ()
    notice = only(result, kind)
    assert "#121" in notice.message and "B-031" in notice.message
    assert notice.message.endswith("Phần mềm không tự sửa Google Sheet.")


@pytest.mark.parametrize(
    "bad",
    [
        state(130, "trash"),
        state(130, "auto-draft"),
        state(130, "inherit"),
        state(130, "PUBLISH"),
        PostState(id=131, status="publish"),  # mục mang mã khác
        PostState(id=True, status="publish"),  # type: ignore[arg-type]
        "publish",
        None,
    ],
)
def test_odd_website_entries_count_as_not_found(fake, client, bad):
    FakePlanSheet(fake, rows(row("B-040", "cửa cuốn", status="Đã hẹn giờ", wp_post_id=130)))
    result = check(client, {130: bad})
    assert result.updates == ()
    assert only(result, Notice.MISSING).wp_post_id == 130


@pytest.mark.parametrize(
    "date_gmt", ["2026-13-01T00:00:00", "0000-00-00T00:00:00", "2050-01-01T00:00:00",
                 "2026-11-05T02:00:00Z", "2026-11-05 02:00:00", "x" * 5000],
)  # fmt: skip
def test_odd_website_date_changes_status_but_not_date(fake, client, date_gmt):
    FakePlanSheet(fake, rows(row("B-041", "cửa cuốn", status="Đã gửi nháp", wp_post_id=131)))
    result = check(client, {131: state(131, "future", date_gmt)})
    (update,) = result.updates
    assert update.kind is Kind.SCHEDULED and update.fields == ("status",)
    assert update.reason == "Bài #131 đang hẹn giờ trên website."
    assert only(result, Notice.ODD_DATE).wp_post_id == 131
    assert not result.late


def test_states_and_asked_from_outside_are_untrusted(fake, client):
    FakePlanSheet(fake, rows(row("B-042", "cửa cuốn", status="Đã hẹn giờ", wp_post_id=132)))
    states = {132: state(132, "publish", NOV3_08), 999: state(999, "publish")}
    # Mã hỏi sai kiểu (chữ, bool, số âm, quá lớn) bị bỏ: 132 coi như chưa hỏi.
    assert check(client, states, ["132", True, -132, 2**63]).updates == ()
    # Bài website trả thêm mà không có dòng nào nối: không đề xuất gì.
    (update,) = check(client, states, [132, 999]).updates
    assert update.wp_post_id == 132


@pytest.mark.parametrize("cell", ["abc", "0", "-5", "2147483648", "12.5", MOI, "=HYPERLINK(1)"])
def test_odd_post_id_on_sheet_is_not_linked(fake, client, cell):
    """Mã lạ trong cột «Mã bài WordPress»: dòng không nối được, không đề xuất gì cho dòng đó."""
    FakePlanSheet(fake, rows(row("B-043", "cửa cuốn", status="Đã hẹn giờ", wp_post_id=cell)))
    result = check(client, {133: state(133, "publish")}, [133])
    assert result.updates == () and result.notices == ()


def test_one_post_on_many_rows_is_not_written(fake, client):
    FakePlanSheet(fake, rows(
        row("B-050", "cửa cuốn", status="Đã hẹn giờ", wp_post_id=140),
        row("B-051", "cửa kéo", status="Đã hẹn giờ", wp_post_id=140),
        row("B-052", "cửa sắt", status="Đã hẹn giờ", wp_post_id=141),
    ))  # fmt: skip
    result = check(client, {140: state(140, "publish"), 141: state(141, "publish")})
    assert [u.key for u in result.updates] == ["B-052"]
    notice = only(result, Notice.SHARED_POST)
    assert notice.message.startswith("Mã bài WordPress 140 có ở nhiều dòng")


def test_post_shared_with_a_hidden_duplicate_row_is_not_written(fake, client):
    """Bài nối cả dòng trùng Mã bài (``plan.rows`` chỉ giữ dòng đầu): vẫn đếm là nhiều dòng."""
    FakePlanSheet(fake, rows(
        row("B-053", "cửa cuốn", status="Đã hẹn giờ", wp_post_id=142),
        row("B-054", "cửa kéo", status="Đã hẹn giờ", wp_post_id=143),
        row("B-054", "cửa kéo 2", status="Đã hẹn giờ", wp_post_id=142),
    ))  # fmt: skip
    result = check(client, {142: state(142, "publish"), 143: state(143, "publish")})
    assert result.updates == ()
    kinds = sorted(n.kind for n in result.notices)
    assert kinds == sorted([Notice.SHARED_POST, Notice.DUPLICATE_KEY])


def test_row_without_key_is_not_written(fake, client):
    FakePlanSheet(fake, rows(row("", "cửa cuốn", status="Đã hẹn giờ", wp_post_id=150)))
    result = check(client, {150: state(150, "publish")})
    assert result.updates == ()
    assert only(result, Notice.NO_KEY).message.startswith("Dòng 2 có Mã bài WordPress 150")


def test_messages_never_copy_sheet_text(fake, client):
    FakePlanSheet(fake, rows(
        row("B-060", MOI, status="Đã hẹn giờ", wp_post_id=160, notes=MOI, title_hint=MOI),
        row("B-061", MOI, status="Bỏ", wp_post_id=161, notes=MOI),
        row("B-062", MOI, status="Đã đăng", wp_post_id=162, notes=MOI),
    ))  # fmt: skip
    result = check(client, {160: state(160, "publish", NOV3_08), 161: state(161, "publish")},
                   [160, 161, 162])  # fmt: skip
    texts = [u.reason for u in result.updates] + [n.message for n in result.notices]
    assert len(texts) == 3
    no_cell_text(*texts)
    for update in result.updates:  # cũ/mới là nhãn chuẩn, giờ do app dựng: không chữ ô Sheet
        assert update.status_before in model.STATUSES and update.status_after in model.STATUSES


def test_check_needs_sheet_id_and_aware_time(fake, client):
    FakePlanSheet(fake, rows(row("B-063", "cửa cuốn", status="Đã hẹn giờ", wp_post_id=163)))
    plan = sync.read_sheet(client, now=NOW)
    with pytest.raises(ValueError):
        website.check_website(plan, {}, [163], sheet_id="", now=NOW)
    with pytest.raises(ValueError):
        website.check_website(plan, {}, [163], sheet_id=SHEET_ID, now=datetime(2026, 11, 3))


# ======================================================== ghi: Sheet đổi giữa chừng


@pytest.fixture
def two_rows(fake):
    return FakePlanSheet(fake, rows(
        row("B-070", "cửa cuốn", status="Đã hẹn giờ", wp_post_id=170,
            published_at="2026-11-03 08:00+07:00"),
        row("B-071", "cổng inox", status="Đã gửi nháp", wp_post_id=171),
    ))  # fmt: skip


def two_states():
    return {170: state(170, "publish", NOV3_08), 171: state(171, "future", NOV5_09)}


@pytest.mark.parametrize(
    ("column", "value", "fields"),
    [
        ("status", "Đang viết", "«Trạng thái»"),
        ("status", "Bỏ", "«Trạng thái»"),
        ("status", MOI, "«Trạng thái»"),
        ("wp_post_id", 999, "«Mã bài WordPress»"),
        ("wp_post_id", "", "«Mã bài WordPress»"),
        ("published_at", "2026-11-04 08:00+07:00", "«Ngày đăng thực tế»"),
        ("published_at", MOI, "«Ngày đăng thực tế»"),
    ],
)
def test_row_changed_elsewhere_is_not_written(client, two_rows, column, value, fields):
    result = check(client, two_states())
    two_rows.set(2, COL[column], value)  # máy khác / chủ dự án vừa sửa B-070
    outcome = apply(client, result)
    (conflict,) = outcome.conflicts
    assert conflict.update.key == "B-070"
    assert conflict.reason == f"Dòng vừa bị sửa ở nơi khác ({fields}) nên chưa ghi."
    assert [u.key for u in outcome.written] == ["B-071"]
    assert {(r, c) for r, c, _ in two_rows.written_cells()} <= {(3, c) for c in APP_COLUMNS}
    no_cell_text(outcome.message)


def test_sheet_already_has_new_status(client, two_rows):
    result = check(client, two_states())
    two_rows.set(2, COL["status"], "Đã đăng")  # máy khác vừa cập nhật
    outcome = apply(client, result)
    assert [u.key for u in outcome.already] == ["B-070"]
    assert {r for r, _, _ in two_rows.written_cells()} == {3}


@pytest.mark.parametrize("change", ["deleted", "renamed", "duplicated"])
def test_row_gone_or_duplicated_is_not_written(client, two_rows, change):
    result = check(client, two_states())
    if change == "deleted":
        del two_rows.grid[1]
    elif change == "renamed":
        two_rows.set(2, COL["key"], "B-099")
    else:
        two_rows.grid.append(list(two_rows.grid[1]))
    outcome = apply(client, result)
    assert [c.update.key for c in outcome.conflicts] == ["B-070"]
    assert all(r != 2 for r, _, _ in two_rows.written_cells()) or change == "deleted"
    assert two_rows.appends == []


def test_other_sheet_connected_writes_nothing(fake, client, two_rows):
    result = check(client, two_states())
    reads = two_rows.reads
    with pytest.raises(sync.SheetPlanError) as info:
        website.apply_website_changes(client, result, sheet_id="Q" * 44, now=NOW)
    assert "Google Sheet đang kết nối khác" in str(info.value)
    other = website.WebCheck(result.updates, result.notices, sheet_hash("Q" * 44), NOW)
    with pytest.raises(sync.SheetPlanError):
        apply(client, other)
    assert two_rows.reads == reads and two_rows.updates == []


def test_updates_must_come_from_the_check(client, two_rows):
    result = check(client, two_states())
    forged = website.WebUpdate(Kind.PUBLISHED, "B-071", 171, 3, "Đã gửi nháp", "Đã đăng",
                               None, None, "x")  # fmt: skip
    for bad in ([forged], [result.updates[0], result.updates[0]]):
        with pytest.raises(ValueError):
            apply(client, result, bad)
    assert two_rows.updates == []


def test_only_chosen_updates_are_written(client, two_rows):
    result = check(client, two_states())
    chosen = [u for u in result.updates if u.key == "B-071"]
    outcome = apply(client, result, chosen)
    assert outcome.written == tuple(chosen)
    assert {r for r, _, _ in two_rows.written_cells()} == {3}
    assert apply(client, result, []).message == "Không có thay đổi nào để ghi."


def test_unsure_write_is_not_retried(client, two_rows):
    result = check(client, two_states())
    two_rows.fail("update", requests.exceptions.ConnectionError("đứt"), apply=True)
    outcome = apply(client, result)
    assert len(outcome.unsure) == 2 and outcome.written == ()
    assert len(two_rows.updates) == 1  # một lệnh, không tự ghi lại
    assert "chưa rõ đã ghi chưa" in outcome.message
    # Lần sau: kiểm lại, Sheet đã đúng (Google đã ghi) nên không còn gì để ghi.
    assert check(client, two_states()).updates == ()


def test_failed_write_keeps_nothing_written(client, two_rows):
    result = check(client, two_states())
    two_rows.fail("update", (403, {"error": {"message": MOI}}))
    outcome = apply(client, result)
    assert len(outcome.not_written) == 2 and outcome.error
    no_cell_text(outcome.message)
    assert two_rows.cell(2, COL["status"]) == "Đã hẹn giờ"


def test_read_error_writes_nothing(client, two_rows):
    result = check(client, two_states())
    two_rows.fail("read", (503, {"error": {"message": MOI}}))
    with pytest.raises(SheetsError) as info:
        apply(client, result)
    assert MOI not in str(info.value) and two_rows.updates == []


def test_missing_columns_write_nothing(fake, client):
    header = [name for name in HEADER if name != "Mã bài WordPress"]
    sheet = FakePlanSheet(fake, rows(row("B-080", "cửa cuốn", status="Đã hẹn giờ",
                                         wp_post_id=180)))  # fmt: skip
    result = check(client, {180: state(180, "publish")})
    sheet.grid[0] = header + [""]  # cột bị đổi tên giữa chừng
    with pytest.raises(sync.SheetPlanError) as info:
        apply(client, result)
    assert "«Mã bài WordPress»" in str(info.value) and sheet.updates == []


def test_many_rows_are_written_in_batches_and_stop_after_error(fake, client, monkeypatch):
    monkeypatch.setattr(website, "MAX_UPDATES", 4)  # 2 ô mỗi dòng: 2 dòng mỗi lệnh
    lines = [row(f"B-{100 + n:03d}", f"cửa số {n}", status="Đã hẹn giờ", wp_post_id=300 + n)
             for n in range(6)]  # fmt: skip
    sheet = FakePlanSheet(fake, rows(*lines))
    result = check(client, {300 + n: state(300 + n, "publish") for n in range(6)})
    assert len(result.updates) == 6
    sheet.fail("update", (403, {}))
    outcome = apply(client, result)
    assert len(sheet.updates) == 0 and len(outcome.not_written) == 6  # lệnh đầu hỏng: dừng
    outcome = apply(client, result)
    assert len(outcome.written) == 6 and len(sheet.updates) == 3


def test_written_values_are_app_text_never_formulas(client, two_rows):
    apply(client, check(client, two_states()))
    for _row, column, value in two_rows.written_cells():
        assert column in APP_COLUMNS
        assert isinstance(value, str) and not value.startswith(("=", "+", "-", "@"))


# ======================================================== lượt 2 (SL-T109-1 → -3, G3 → G6)

ZWSP = "\N{ZERO WIDTH SPACE}"


@pytest.mark.parametrize("lead", [" " * 40, ZWSP * 40, " " * 1500], ids=["40-cach", "40-vo-hinh",
                                                                          "1500-cach"])  # fmt: skip
def test_sync_reads_key_post_and_status_cells_like_the_table_reader(fake, client, lead):
    """Gốc SL-T109-1, -2: ``sync._key_of``, ``_post_id_of``, ``_status_of`` đọc ô như bộ đọc bảng
    (làm sạch cả ô, tối đa 2.000 ký tự), không cắt 30 / 100 ký tự trước khi làm sạch."""
    FakePlanSheet(fake, rows(row(lead + "B-090", "cửa cuốn", status=lead + "Đã hẹn giờ",
                                 wp_post_id=lead + "190")))  # fmt: skip
    plan = sync.read_sheet(client, now=NOW)
    (sheet_row,) = plan.rows
    assert sheet_row.plan.key == "B-090" and plan.key_rows == {"B-090": (2,)}
    assert sync._post_id_of(sheet_row.cells[COL["wp_post_id"]]) == sheet_row.plan.wp_post_id == 190
    assert sync._status_of(sheet_row.cells[COL["status"]]) == sheet_row.plan.status == "Đã hẹn giờ"
    (update,) = check(client, {190: state(190, "publish", NOV3_08)}).updates
    assert update.status_before == "Đã hẹn giờ"


def test_t100_status_write_finds_row_with_leading_blanks(fake, client):
    """Nơi gọi khác của ``_key_of`` (T-100 ``write_status``): dòng bảng hiện là B-091 nay ghi được
    (trước: «Không còn thấy dòng»)."""
    sheet = FakePlanSheet(fake, rows(row(" " * 40 + "B-091", "cửa cuốn", status="Đang viết")))
    ref = DraftPlanRef(key="B-091", sheet_hash=sheet_hash(SHEET_ID), status="Đang viết",
                            wp_post_id=None, opened_at=NOW)  # fmt: skip
    write = sync.status_write(ref, model.STATUS_DRAFT_SENT, wp_post_id=191, now=NOW)
    assert sync.write_status(client, write, now=NOW).outcome is sync.WriteOutcome.WRITTEN
    assert sheet.cell(2, COL["status"]) == "Đã gửi nháp"


def test_row_reader_and_key_rows_disagree_is_not_proposed_nor_written(fake, client, monkeypatch):
    """Phòng khi hai cách đọc lại lệch nhau: lúc kiểm, Mã bài không ứng đúng dòng bộ đọc nhận thì
    chỉ cảnh báo; lúc ghi, dòng tìm được phải đúng là dòng bộ đọc nhận (như ``open_row``)."""
    FakePlanSheet(fake, rows(row("B-092", "cửa cuốn", status="Đã hẹn giờ", wp_post_id=192)))
    plan = sync.read_sheet(client, now=NOW)
    skewed = dataclasses.replace(plan, key_rows={"B-092": (3,)})
    result = website.check_website(skewed, {192: state(192, "publish")}, [192],
                                   sheet_id=SHEET_ID, now=NOW)  # fmt: skip
    assert result.updates == () and only(result, Notice.UNSURE_ROW).key == "B-092"

    good = check(client, {192: state(192, "publish")})
    real_read = website.read_sheet

    def read_skewed(*args, **kwargs):
        fresh = real_read(*args, **kwargs)
        moved = dataclasses.replace(fresh.rows[0], number=5)
        return dataclasses.replace(fresh, rows=(moved,))

    monkeypatch.setattr(website, "read_sheet", read_skewed)
    (conflict,) = apply(client, good).conflicts
    assert conflict.reason == "Mã bài B-092 có ở nhiều dòng trên Google Sheet nên chưa ghi."


@pytest.mark.parametrize(
    ("status", "published_at", "field"),
    [("Xong rồi", "", "Trạng thái"), ("Đã hẹn giờ", "hôm qua", "Ngày đăng thực tế"),
     (MOI, "", "Trạng thái")],
)  # fmt: skip
def test_unreadable_status_or_date_cell_only_warns(fake, client, status, published_at, field):
    """SL-T109-3: ô gõ chữ không đọc được thì không đề xuất (ghi đè chữ người dùng gõ không an
    toàn), cảnh báo nêu đúng ô cần sửa, không chép chữ trong ô."""
    sheet = FakePlanSheet(fake, rows(row("B-093", "cửa cuốn", status=status, wp_post_id=193,
                                         published_at=published_at)))  # fmt: skip
    result = check(client, {193: state(193, "publish", NOV3_08)})
    assert result.updates == ()
    notice = only(result, Notice.ODD_CELL)
    assert notice.message.startswith(f"Ô «{field}» của dòng B-093 trên Google Sheet không đọc được")
    no_cell_text(notice.message)
    assert apply(client, result).message == "Không có thay đổi nào để ghi." and sheet.updates == []


def test_dropped_row_whose_post_is_gone_is_quiet(fake, client):
    """G3: dòng «Bỏ» mà bài đã xóa hay vào thùng rác: không cảnh báo «Không thấy bài» mỗi lần."""
    FakePlanSheet(fake, rows(row("B-094", "cửa cuốn", status="Bỏ", wp_post_id=194)))
    assert check(client, {}, [194]).notices == ()


@pytest.mark.parametrize(
    ("minutes", "stale"), [(0, False), (5, False), (6, True), (60, True), (-2, True)]
)
def test_old_check_is_refused_before_reading(client, two_rows, minutes, stale):
    """G4: lần kiểm cũ hơn 5 phút (hay giờ máy lùi) thì không ghi: website có thể đã đổi."""
    result = check(client, two_states())
    reads = two_rows.reads
    later = NOW + timedelta(minutes=minutes)
    if stale:
        with pytest.raises(sync.SheetPlanError) as info:
            apply(client, result, now=later)
        assert str(info.value) == website.MSG_STALE
        assert two_rows.reads == reads and two_rows.updates == []
    else:
        assert len(apply(client, result, now=later).written) == 2


@pytest.mark.parametrize("missing", ["Trạng thái", "Mã bài WordPress", "Mã bài"])
def test_missing_column_is_reported_when_checking(fake, client, missing):
    """G5: thiếu cột thì báo ngay lúc kiểm, không đề xuất «Chưa viết → …» rồi mới báo lúc ghi."""
    header = ["Cột lạ" if name == missing else name for name in HEADER]
    FakePlanSheet(fake, [header, row("B-095", "cửa cuốn", status="Đã hẹn giờ", wp_post_id=195)])
    with pytest.raises(sync.SheetPlanError) as info:
        check(client, {195: state(195, "publish")}, [195])
    assert f"«{missing}»" in str(info.value)


@pytest.mark.parametrize(
    ("written", "date_change"),
    [("2026-11-03 08:01+07:00", False), ("2026-11-03 07:58+07:00", False),
     ("2026-11-03 08:03+07:00", True), ("2026-11-03 07:57+07:00", True)],
)  # fmt: skip
def test_publish_time_within_two_minutes_is_the_same(fake, client, written, date_change):
    """G6: «Đăng ngay» ghi giờ máy lúc nhận trả lời; lệch website tới 2 phút không đề xuất sửa."""
    FakePlanSheet(fake, rows(
        row("B-096", "cửa cuốn", status="Đã đăng", wp_post_id=196, published_at=written),
        row("B-097", "cửa kéo", status="Đã hẹn giờ", wp_post_id=197, published_at=written),
    ))  # fmt: skip
    states = {196: state(196, "publish", NOV3_08), 197: state(197, "publish", NOV3_08)}
    result = check(client, states)
    by_key = {u.key: u for u in result.updates}
    assert ("B-096" in by_key) is date_change
    moved = by_key["B-097"]  # đổi trạng thái; ngày chỉ đổi khi lệch quá 2 phút
    assert moved.fields == (("status", "published_at") if date_change else ("status",))
