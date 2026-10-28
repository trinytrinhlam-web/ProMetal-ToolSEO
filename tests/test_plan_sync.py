"""T-100: đồng bộ kế hoạch với Google Sheets (``seo_app.plan.sync``).

Điều kiện Lá Chắn: LC-T094-1 (Sheet giả trên ``FakeGoogle``, không gọi Google thật), -2 (câu báo
cố định, không chép chữ ô Sheet), -28 (chỉ cột app được ghi, so từng ô với bản gốc, Mã bài trùng
không ghi, không xóa dòng, ``RAW``, chữ dạng công thức có dấu cách đầu, giờ có ``+07:00``), -29
(luôn đọc lại Sheet trước khi ghi, trước khi mở Soạn bài), -30 (việc còn nợ chỉ ghi Sheet), -31
(«Chuẩn bị trang tính»). Khóa RSA sinh lúc chạy test.
"""

from __future__ import annotations

import ast
import json
import os
from datetime import UTC, date, datetime

import pytest
import requests
from fake_google import SHEET_ID, FakeGoogle, key_info, make_session, new_private_key
from fake_plan_sheet import HEADER, NEW_TAB_ID, PLAN_ID, FakePlanSheet

from seo_app.google.service_account import load_service_account
from seo_app.google.sheets import SheetsClient, SheetsError
from seo_app.plan import model, sync
from seo_app.plan.model import PlanRow
from seo_app.plan.propose import Action, Proposal, compare_rows
from seo_app.storage.drafts import DraftPlanRef, DraftStore, new_draft_id
from seo_app.storage.plan_cache import PlanCacheStore, sheet_hash
from seo_app.storage.site_index import SiteIndex
from seo_app.wordpress.client import PublishedItem

TZ = model.TIMEZONE
NOW = datetime(2026, 10, 29, 9, 30, tzinfo=TZ)
TODAY = NOW.date()
SITE = "https://suachuacuasat.com"
INDEX = SiteIndex(
    site=SITE,
    fetched_at=datetime(2026, 10, 29, tzinfo=UTC),
    items=(PublishedItem(id=12, type="page", slug="sua-cua-cuon", link=f"{SITE}/sua-cua-cuon/",
                         title="Sửa cửa cuốn"),),
)  # fmt: skip
MOI = "CHU-TRONG-O-KHONG-DUOC-CHEP"
COL = {name: position for position, (name, _) in enumerate(model.SHEET_COLUMNS)}


def serial(day: date) -> int:
    return (day - date(1899, 12, 30)).days


def row(key="", keyword="", **fields):
    """Một dòng Sheet theo đúng thứ tự cột của ``HEADER``."""
    cells = [""] * len(HEADER)
    cells[COL["key"]], cells[COL["keyword"]] = key, keyword
    for name, value in fields.items():
        cells[COL[name]] = value
    return cells


@pytest.fixture(scope="module")
def private_key():
    return new_private_key()


@pytest.fixture
def account(tmp_path, private_key):
    folder = tmp_path / "bi-mat"
    folder.mkdir()
    path = folder / "du-an-thu-0123abcd.json"
    path.write_text(json.dumps(key_info(private_key)), encoding="utf-8")
    if os.name != "nt":
        path.chmod(0o600)
    project = tmp_path / "du-an"
    project.mkdir()
    return load_service_account(path, project_root=project)


@pytest.fixture
def fake():
    return FakeGoogle()


@pytest.fixture
def client(fake, account):
    return SheetsClient(SHEET_ID, account, session=make_session(fake), sleep=lambda _s: None)


def base_rows():
    return [
        HEADER,
        row("B-001", "sửa cửa cuốn", priority="Cao", planned_date=serial(date(2026, 11, 20)),
            status="Chưa viết"),
        row("B-002", "cổng inox 304", priority="Thấp", status="Đang viết"),
        row("B-003", "lan can kính", status="Đã đăng", wp_post_id=77),
    ]  # fmt: skip


@pytest.fixture
def sheet(fake):
    return FakePlanSheet(fake, base_rows())


def read(client, **kwargs):
    return sync.read_sheet(client, now=NOW, **kwargs)


def update(base: sync.SheetPlan, key: str, **changes) -> Proposal:
    before = base.find(key).plan
    after = PlanRow.model_validate({**before.model_dump(), **changes})
    return Proposal(Action.UPDATE, key, after, before, "lý do")


# ======================================================================== đọc


def test_reads_columns_by_name_in_any_order_and_skips_blank_rows(fake, client):
    header = ["Ghi chú riêng", "Từ khóa chính", "Giờ đăng", "Mã bài", "Ngày dự kiến"]
    first = ["x", "sửa cửa cuốn", 0.375, "b-7", serial(date(2026, 11, 20))]
    last = ["y", "cổng xếp", "08:00", "B-8", ""]
    FakePlanSheet(fake, [header, first, [], ["", "", "", "", ""], last])
    plan = read(client)
    assert [(r.number, r.plan.key, r.plan.keyword) for r in plan.rows] == [
        (2, "B-007", "sửa cửa cuốn"),
        (5, "B-008", "cổng xếp"),
    ]
    first = plan.rows[0].plan
    assert (first.planned_date, first.planned_time) == (date(2026, 11, 20), "09:00")
    assert plan.columns == {"keyword": 1, "planned_time": 2, "key": 3, "planned_date": 4}
    assert "status" in plan.missing and plan.skipped == 0


def test_app_columns_round_trip(fake, client):
    stamp = "2026-11-20 08:00+07:00"
    FakePlanSheet(fake, [HEADER, row("B-001", "sửa cửa cuốn", status="Đã hẹn giờ", wp_post_id=91,
                                     published_at=stamp, updated_at=stamp)])  # fmt: skip
    (only,) = read(client).rows
    assert only.plan.wp_post_id == 91 and only.plan.status == model.STATUS_SCHEDULED
    assert only.plan.published_at == datetime(2026, 11, 20, 8, 0, tzinfo=TZ)


def test_duplicate_keys_keep_first_row_and_warn_without_cell_text(fake, client):
    FakePlanSheet(fake, [HEADER, row("B-001", "sửa cửa cuốn"), row("B-1", MOI),
                         row("", "", notes=MOI)])  # fmt: skip
    plan = read(client)
    assert [r.plan.keyword for r in plan.rows] == ["sửa cửa cuốn"]
    assert plan.key_rows == {"B-001": (2, 3)} and plan.duplicate_keys == {"B-001"}
    text = " ".join(plan.warnings)
    assert "B-001" in text and MOI not in text


def test_sheet_without_keyword_column_has_no_rows(fake, client):
    FakePlanSheet(fake, [["Mục", "Nội dung"], ["a", "b"]])
    plan = read(client)
    assert plan.rows == () and sync.MSG_NO_KEYWORD_COLUMN in plan.warnings


def test_dirty_cells_go_through_plan_row(fake, client):
    rlo = chr(0x202E)
    FakePlanSheet(fake, [HEADER, row("B-001", f"sửa{rlo} cửa «cuốn»", notes="<b>đậm</b>",
                                     target_id=f"{SITE}/sua-cua-cuon/")])  # fmt: skip
    (only,) = read(client, index=INDEX).rows
    assert only.plan.keyword == "sửa cửa ‹cuốn›" and only.plan.target_id == 12


# ======================================================================== cache, get_plan


@pytest.fixture
def cache(tmp_path):
    return PlanCacheStore(path=tmp_path / "plan_cache.sqlite")


def test_get_plan_uses_fresh_cache_without_calling_google(sheet, client, cache):
    first = sync.get_plan(cache, SHEET_ID, client, now=NOW)
    assert not first.plan.from_cache and sheet.reads == 1
    again = sync.get_plan(cache, SHEET_ID, client, now=NOW)
    assert again.plan.from_cache and sheet.reads == 1
    assert again.plan.plan_rows() == first.plan.plan_rows()


def test_get_plan_reloads_stale_or_on_refresh(sheet, client, cache):
    sync.get_plan(cache, SHEET_ID, client, now=NOW)
    sync.get_plan(cache, SHEET_ID, client, now=NOW, refresh=True)
    later = NOW.replace(minute=40)
    listing = sync.get_plan(cache, SHEET_ID, client, now=later)
    assert sheet.reads == 3 and not listing.plan.from_cache


def test_get_plan_shows_cached_copy_when_google_fails(sheet, client, cache):
    sync.get_plan(cache, SHEET_ID, client, now=NOW)
    sheet.fail("read", (503, {"error": {"message": MOI}}))
    listing = sync.get_plan(cache, SHEET_ID, client, now=NOW, refresh=True)
    assert listing.plan.from_cache and "09:30 29/10/2026" in listing.notice
    assert MOI not in listing.notice
    offline = sync.get_plan(cache, SHEET_ID, None, now=NOW, refresh=True)
    assert offline.plan.from_cache and sync.MSG_NOT_CONNECTED in offline.notice


def test_get_plan_without_cache_or_client(cache):
    listing = sync.get_plan(cache, SHEET_ID, None, now=NOW)
    assert listing.plan is None and listing.notice == sync.MSG_NOT_CONNECTED


def test_cache_of_another_sheet_is_not_used(sheet, client, cache):
    sync.get_plan(cache, SHEET_ID, client, now=NOW)
    other = "Z" * 44
    assert cache.load(other) is None
    assert sync.get_plan(cache, other, None, now=NOW).plan is None


# ======================================================================== áp dụng đề xuất


def test_update_writes_only_changed_cells_raw_with_time(sheet, client):
    base = read(client)
    proposal = update(base, "B-001", planned_date=date(2026, 11, 25), notes="=IMPORTXML(A1)")
    result = sync.apply_proposals(client, base, [proposal], now=NOW)
    assert result.written == (proposal,) and not result.conflicts
    assert sheet.update_options == [{"valueInputOption": "RAW", "includeValuesInResponse": False}]
    assert sorted(sheet.written_cells()) == [
        (2, COL["planned_date"], serial(date(2026, 11, 25))),
        (2, COL["notes"], " =IMPORTXML(A1)"),
        (2, COL["updated_at"], "2026-10-29 09:30+07:00"),
    ]
    again = read(client).find("B-001").plan
    assert again.planned_date == date(2026, 11, 25) and again.notes == "=IMPORTXML(A1)"


def test_cell_changed_elsewhere_is_not_written(sheet, client):
    base = read(client)
    sheet.set(2, COL["planned_date"], serial(date(2026, 12, 1)))  # máy kia vừa sửa
    proposal = update(base, "B-001", planned_date=date(2026, 11, 25))
    result = sync.apply_proposals(client, base, [proposal], now=NOW)
    (conflict,) = result.conflicts
    assert conflict.fields == ("planned_date",) and result.written == ()
    assert conflict.now.planned_date == date(2026, 12, 1) and sheet.updates == []
    assert "B-001 (Ngày dự kiến)" in result.message


def test_two_machines_editing_different_columns_do_not_block(sheet, client):
    base = read(client)
    sheet.set(2, COL["notes"], "ghi chú từ máy kia")
    result = sync.apply_proposals(client, base, [update(base, "B-001", priority="Thấp")], now=NOW)
    assert len(result.written) == 1 and sheet.cell(2, COL["notes"]) == "ghi chú từ máy kia"
    assert sheet.cell(2, COL["priority"]) == "Thấp"


def test_row_found_by_key_after_sorting(sheet, client):
    base = read(client)
    sheet.grid[1], sheet.grid[3] = sheet.grid[3], sheet.grid[1]  # sắp xếp lại trên Sheet
    sync.apply_proposals(client, base, [update(base, "B-001", priority="Thấp")], now=NOW)
    assert sheet.cell(4, COL["priority"]) == "Thấp" and sheet.cell(2, COL["key"]) == "B-003"


def test_keyword_changed_elsewhere_blocks_the_row(sheet, client):
    base = read(client)
    sheet.set(2, COL["keyword"], "sửa cửa cuốn đài loan")
    result = sync.apply_proposals(client, base, [update(base, "B-001", priority="Thấp")], now=NOW)
    assert result.conflicts[0].fields == ("keyword",) and sheet.updates == []


@pytest.mark.parametrize("change", ["duplicate", "deleted", "renamed"])
def test_duplicate_or_missing_key_is_not_written(sheet, client, change):
    base = read(client)
    if change == "duplicate":
        sheet.grid.append(row("B-001", "bài khác"))
    elif change == "deleted":
        del sheet.grid[1]
    else:
        sheet.set(2, COL["key"], "B-099")
    result = sync.apply_proposals(client, base, [update(base, "B-001", priority="Thấp")], now=NOW)
    assert result.conflicts and sheet.updates == []


def test_drop_only_sets_status_and_never_deletes_rows(sheet, client):
    base = read(client)
    before = base.find("B-002").plan
    after = PlanRow.model_validate({**before.model_dump(), "status": model.STATUS_DROPPED})
    rows_before = len(sheet.grid)
    drop = Proposal(Action.DROP, "B-002", after, before, "x")
    sync.apply_proposals(client, base, [drop], now=NOW)
    assert len(sheet.grid) == rows_before
    assert {(r, c) for r, c, _ in sheet.written_cells()} == {
        (3, COL["status"]), (3, COL["updated_at"])
    }  # fmt: skip
    assert sheet.cell(3, COL["status"]) == model.STATUS_DROPPED


def test_foreign_columns_are_never_written(fake, client):
    header = ["Mã bài", "Người phụ trách", "Từ khóa chính", "Ưu tiên", "Cột riêng"]
    sheet = FakePlanSheet(fake, [header, ["B-001", "anh Tư", "sửa cửa cuốn", "Cao", "=SUM(1)"]])
    base = read(client)
    result = sync.apply_proposals(client, base, [update(base, "B-001", priority="Thấp")], now=NOW)
    assert result.written and {c for _, c, _ in sheet.written_cells()} == {3}
    assert sheet.grid[1][1] == "anh Tư" and sheet.grid[1][4] == "=SUM(1)"


def test_missing_column_for_a_change_is_a_conflict(fake, client):
    sheet = FakePlanSheet(fake, [["Mã bài", "Từ khóa chính"], ["B-001", "sửa cửa cuốn"]])
    base = read(client)
    result = sync.apply_proposals(client, base, [update(base, "B-001", priority="Thấp")], now=NOW)
    (conflict,) = result.conflicts
    assert conflict.fields == ("priority",) and "«Ưu tiên»" in conflict.reason
    assert sheet.updates == []


def test_keyless_row_gets_its_new_key(fake, client):
    sheet = FakePlanSheet(fake, [HEADER, row("B-004", "cổng"), row("", "sửa cửa cuốn")])
    base = read(client)
    incoming = [PlanRow(keyword="Sửa cửa cuốn", priority="Cao")]
    (proposal,) = compare_rows(base.plan_rows(), incoming, today=TODAY).items
    assert proposal.after.key == "B-005"
    result = sync.apply_proposals(client, base, [proposal], now=NOW)
    assert result.written and sheet.cell(3, COL["key"]) == "B-005"
    assert sheet.cell(3, COL["priority"]) == "Cao"


def test_add_appends_row_by_column_name(sheet, client):
    base = read(client)
    incoming = [PlanRow(keyword="cửa kéo đài loan", planned_date="30/11/2026", notes="+84 gọi")]
    (proposal,) = compare_rows(base.plan_rows(), incoming, today=TODAY).items
    result = sync.apply_proposals(client, base, [proposal], now=NOW)
    assert result.written == (proposal,) and len(sheet.appends) == 1
    added = read(client).find("B-004")
    assert added.number == 5 and added.plan.keyword == "cửa kéo đài loan"
    assert sheet.cell(5, COL["notes"]) == " +84 gọi"  # chữ dạng công thức: dấu cách đầu
    assert sheet.cell(5, COL["planned_date"]) == serial(date(2026, 11, 30))
    assert sheet.cell(5, COL["updated_at"]) == "2026-10-29 09:30+07:00"


def test_add_with_key_already_on_sheet_is_not_appended(sheet, client):
    base = read(client)
    incoming = [PlanRow(keyword="cửa kéo đài loan")]
    (proposal,) = compare_rows(base.plan_rows(), incoming, today=TODAY).items
    sheet.grid.append(row("B-004", "máy kia vừa thêm"))
    result = sync.apply_proposals(client, base, [proposal], now=NOW)
    assert result.conflicts and sheet.appends == []


def test_unsure_append_is_checked_and_never_duplicated(sheet, client):
    base = read(client)
    (proposal,) = compare_rows(base.plan_rows(), [PlanRow(keyword="cửa kéo")], today=TODAY).items
    sheet.fail("append", requests.exceptions.ConnectionError("đứt"), apply=True)
    result = sync.apply_proposals(client, base, [proposal], now=NOW)
    assert result.written == (proposal,) and result.unsure == () and result.error
    again = sync.apply_proposals(client, base, [proposal], now=NOW)  # bấm lại
    assert again.conflicts and len(sheet.appends) == 1
    assert read(client).key_rows["B-004"] == (5,)


def test_unsure_append_that_did_not_happen_is_reported_not_written(sheet, client):
    base = read(client)
    (proposal,) = compare_rows(base.plan_rows(), [PlanRow(keyword="cửa kéo")], today=TODAY).items
    sheet.fail("append", requests.exceptions.ConnectionError("đứt"))
    result = sync.apply_proposals(client, base, [proposal], now=NOW)
    assert result.not_written == (proposal,) and "B-004" not in read(client).key_rows


def test_unsure_append_and_failed_reread_stays_unsure(sheet, client):
    base = read(client)
    (proposal,) = compare_rows(base.plan_rows(), [PlanRow(keyword="cửa kéo")], today=TODAY).items
    sheet.fail("append", requests.exceptions.ConnectionError("đứt"), apply=True)
    real_read = client.read_plan_values
    calls = []

    def read_once_then_fail():
        calls.append(1)
        if len(calls) > 1:
            raise SheetsError("mất mạng", unsure=False)
        return real_read()

    client.read_plan_values = read_once_then_fail
    result = sync.apply_proposals(client, base, [proposal], now=NOW)
    assert result.unsure == (proposal,) and "Tải lại" in result.message


def test_unsure_update_then_apply_again_counts_as_written(sheet, client):
    base = read(client)
    proposal = update(base, "B-001", priority="Thấp")
    sheet.fail("update", requests.exceptions.ConnectionError("đứt"), apply=True)
    first = sync.apply_proposals(client, base, [proposal], now=NOW)
    assert first.unsure == (proposal,)
    again = sync.apply_proposals(client, base, [proposal], now=NOW)
    assert again.written == (proposal,) and not again.conflicts and len(sheet.updates) == 1


def test_rejected_update_stops_and_appends_are_not_sent(sheet, client):
    base = read(client)
    changed = update(base, "B-001", priority="Thấp")
    (added,) = compare_rows(base.plan_rows(), [PlanRow(keyword="cửa kéo")], today=TODAY).items
    sheet.fail("update", (403, {"error": {"message": MOI}}))
    result = sync.apply_proposals(client, base, [changed, added], now=NOW)
    assert result.not_written == (changed, added) and sheet.appends == []
    assert MOI not in result.message and "403" in result.message


def test_many_changes_are_split_into_batches_of_at_most_200_cells(fake, client):
    rows = [HEADER] + [row(f"B-{n:03d}", f"từ khóa số {n}") for n in range(1, 61)]
    sheet = FakePlanSheet(fake, rows)
    base = read(client)
    proposals = [
        update(base, f"B-{n:03d}", priority="Cao", intent="Mua hàng", kind="Dịch vụ", notes="x")
        for n in range(1, 61)
    ]
    result = sync.apply_proposals(client, base, proposals, now=NOW)
    assert len(result.written) == 60 and all(len(data) <= 200 for data in sheet.updates)
    assert len(sheet.updates) == 2  # 60 × 5 ô = 300 ô


def test_reading_again_fails_before_anything_is_written(sheet, client):
    base = read(client)
    sheet.fail("read", (500, {}))
    with pytest.raises(SheetsError):
        sync.apply_proposals(client, base, [update(base, "B-001", priority="Thấp")], now=NOW)
    assert sheet.updates == []


def test_proposal_for_a_row_not_in_base_is_a_conflict(sheet, client):
    base = read(client)
    stranger = PlanRow(key="B-050", keyword="không có")
    after = stranger.model_copy(update={"priority": "Cao"})
    result = sync.apply_proposals(
        client, base, [Proposal(Action.UPDATE, "B-050", after, stranger, "x")], now=NOW
    )
    assert result.conflicts[0].reason == sync.CONFLICT_UNKNOWN_ROW


def test_target_written_as_site_link(sheet, client):
    base = read(client, index=INDEX)
    sync.apply_proposals(client, base, [update(base, "B-002", target_id=12)], index=INDEX, now=NOW)
    assert sheet.cell(3, COL["target_id"]) == f"{SITE}/sua-cua-cuon/"
    assert read(client, index=INDEX).find("B-002").plan.target_id == 12


# ======================================================================== ghi trạng thái


def ref(key="B-001", status="Chưa viết", post=None):
    return DraftPlanRef(key=key, sheet_hash=sheet_hash(SHEET_ID), status=status, wp_post_id=post,
                        opened_at=NOW)  # fmt: skip


def test_status_after_sending_writes_four_cells(sheet, client):
    when = datetime(2026, 11, 3, 1, 0, tzinfo=UTC)
    write = sync.status_write(ref(), model.STATUS_SCHEDULED, wp_post_id=501, published_at=when,
                              now=NOW)  # fmt: skip
    result = sync.write_status(client, write, now=NOW)
    assert result.outcome is sync.WriteOutcome.WRITTEN
    assert sorted(sheet.written_cells()) == [
        (2, COL["status"], model.STATUS_SCHEDULED),
        (2, COL["wp_post_id"], 501),
        (2, COL["published_at"], "2026-11-03 08:00+07:00"),
        (2, COL["updated_at"], "2026-10-29 09:30+07:00"),
    ]


def test_status_already_written_is_not_written_again(sheet, client):
    sheet.set(2, COL["status"], model.STATUS_DRAFT_SENT)
    sheet.set(2, COL["wp_post_id"], 501)
    write = sync.status_write(ref(), model.STATUS_DRAFT_SENT, wp_post_id=501, now=NOW)
    assert sync.write_status(client, write, now=NOW).outcome is sync.WriteOutcome.ALREADY
    assert sheet.updates == []


def test_status_never_goes_back(sheet, client):
    write = sync.status_write(ref("B-003", "Đã đăng", 77), model.STATUS_DRAFT_SENT,
                              wp_post_id=77, now=NOW)  # fmt: skip
    assert sync.write_status(client, write, now=NOW).outcome is sync.WriteOutcome.LATER
    sheet.set(2, COL["status"], model.STATUS_PUBLISHED)
    sheet.set(2, COL["wp_post_id"], 501)
    later = sync.status_write(ref(), model.STATUS_DRAFT_SENT, wp_post_id=502, now=NOW)
    assert sync.write_status(client, later, now=NOW).outcome is sync.WriteOutcome.LATER
    assert sheet.updates == []


@pytest.mark.parametrize(
    "change",
    ["dropped", "other-post", "bad-status", "duplicate", "missing", "no-status-column"],
)
def test_status_conflicts_are_not_written(sheet, client, change):
    if change == "dropped":
        sheet.set(2, COL["status"], model.STATUS_DROPPED)
    elif change == "other-post":
        sheet.set(2, COL["wp_post_id"], 999)
    elif change == "bad-status":
        sheet.set(2, COL["status"], MOI)
    elif change == "duplicate":
        sheet.grid.append(row("B-001", "trùng"))
    elif change == "missing":
        del sheet.grid[1]
    else:
        sheet.grid[0][COL["status"]] = "Cột khác"
    write = sync.status_write(ref(), model.STATUS_DRAFT_SENT, wp_post_id=501, now=NOW)
    result = sync.write_status(client, write, now=NOW)
    assert result.outcome is sync.WriteOutcome.CONFLICT and sheet.updates == []
    assert result.finished and MOI not in result.message


def test_resend_replaces_post_id_seen_when_opened(sheet, client):
    sheet.set(2, COL["status"], model.STATUS_DRAFT_SENT)
    sheet.set(2, COL["wp_post_id"], 501)
    write = sync.status_write(ref(status="Đã gửi nháp", post=501), model.STATUS_DRAFT_SENT,
                              wp_post_id=502, now=NOW)  # fmt: skip
    assert sync.write_status(client, write, now=NOW).outcome is sync.WriteOutcome.WRITTEN
    assert sheet.cell(2, COL["wp_post_id"]) == 502


def test_status_errors_keep_the_pending_write(sheet, client):
    write = sync.status_write(ref(), model.STATUS_DRAFT_SENT, wp_post_id=501, now=NOW)
    sheet.fail("read", (503, {"error": {"message": MOI}}))
    failed = sync.write_status(client, write, now=NOW)
    assert failed.outcome is sync.WriteOutcome.FAILED and not failed.finished
    sheet.fail("update", requests.exceptions.Timeout("chậm"), apply=True)
    unsure = sync.write_status(client, write, now=NOW)
    assert unsure.outcome is sync.WriteOutcome.UNSURE and MOI not in unsure.message
    assert sync.write_status(client, write, now=NOW).outcome is sync.WriteOutcome.ALREADY


def test_writing_status_from_a_new_row(sheet, client):
    write = sync.status_write(ref(), model.STATUS_WRITING, now=NOW)
    assert sync.write_status(client, write, now=NOW).outcome is sync.WriteOutcome.WRITTEN
    assert sheet.cell(2, COL["status"]) == model.STATUS_WRITING
    on_writing = sync.status_write(ref("B-002", "Đang viết"), model.STATUS_WRITING, now=NOW)
    assert sync.write_status(client, on_writing, now=NOW).outcome is sync.WriteOutcome.ALREADY


def test_time_written_is_vietnam_time_even_from_utc_clock(sheet, client):
    utc_now = datetime(2026, 10, 29, 2, 30, tzinfo=UTC)
    write = sync.status_write(ref(), model.STATUS_WRITING, now=utc_now)
    sync.write_status(client, write, now=utc_now)
    assert sheet.cell(2, COL["updated_at"]) == "2026-10-29 09:30+07:00"


# ======================================================================== việc còn nợ


@pytest.fixture
def store(tmp_path):
    return DraftStore(path=tmp_path / "drafts.sqlite")


def test_record_status_keeps_write_until_sheet_has_it(sheet, client, store):
    draft_id = new_draft_id()
    write = sync.status_write(ref(), model.STATUS_DRAFT_SENT, wp_post_id=501, now=NOW)
    sheet.fail("read", (503, {}))
    first = sync.record_status(client, store, draft_id, write, now=NOW)
    assert not first.finished and store.load_plan_write(draft_id) == write
    (item,) = sync.retry_pending(client, store, SHEET_ID, now=NOW)
    assert item.result.outcome is sync.WriteOutcome.WRITTEN and item.key == "B-001"
    assert store.load_plan_write(draft_id) is None
    assert sheet.cell(2, COL["wp_post_id"]) == 501


def test_record_status_without_google_only_saves(store):
    draft_id = new_draft_id()
    write = sync.status_write(ref(), model.STATUS_DRAFT_SENT, wp_post_id=501, now=NOW)
    result = sync.record_status(None, store, draft_id, write, now=NOW)
    assert not result.finished and store.load_plan_write(draft_id) == write


def test_retry_skips_other_sheet_and_stops_on_error(sheet, client, store):
    other = sync.status_write(ref(), model.STATUS_DRAFT_SENT, wp_post_id=501, now=NOW)
    other = other.model_copy(update={"sheet_hash": sheet_hash("Q" * 44)})
    first, second = new_draft_id(), new_draft_id()
    store.save_plan_write(new_draft_id(), other)
    store.save_plan_write(first, sync.status_write(ref(), model.STATUS_DRAFT_SENT, wp_post_id=501,
                                                   now=NOW))  # fmt: skip
    store.save_plan_write(second, sync.status_write(ref("B-002", "Đang viết"),
                                                    model.STATUS_DRAFT_SENT, wp_post_id=502,
                                                    now=NOW))  # fmt: skip
    sheet.fail("read", (503, {}))
    items = sync.retry_pending(client, store, SHEET_ID, now=NOW)
    assert len(items) == 1 and not items[0].result.finished  # dừng ngay khi Google lỗi
    assert len(store.list_plan_writes()) == 3
    items = sync.retry_pending(client, store, SHEET_ID, now=NOW)
    assert [item.result.outcome for item in items] == [sync.WriteOutcome.WRITTEN] * 2
    assert [write.sheet_hash for _, write in store.list_plan_writes()] == [sheet_hash("Q" * 44)]


def test_retry_does_not_remove_a_newer_write_from_another_tab(sheet, client, store, monkeypatch):
    draft_id = new_draft_id()
    old = sync.status_write(ref(), model.STATUS_DRAFT_SENT, wp_post_id=501, now=NOW)
    newer = sync.status_write(ref(), model.STATUS_SCHEDULED, wp_post_id=501,
                              published_at=NOW, now=NOW)  # fmt: skip
    store.save_plan_write(draft_id, old)
    real_write = sync.write_status

    def write_then_other_tab(client_, write, *, now=None):
        result = real_write(client_, write, now=now)
        store.save_plan_write(draft_id, newer)  # tab khác ghi việc mới trong lúc này
        return result

    monkeypatch.setattr(sync, "write_status", write_then_other_tab)
    sync.retry_pending(client, store, SHEET_ID, now=NOW)
    assert store.load_plan_write(draft_id) == newer


def test_sync_module_never_talks_to_wordpress():
    with open(sync.__file__, encoding="utf-8") as handle:
        tree = ast.parse(handle.read())
    modules = [
        node.module if isinstance(node, ast.ImportFrom) else alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import | ast.ImportFrom)
        for alias in node.names
    ]
    assert modules and not [name for name in modules if name and "wordpress" in name]


# ======================================================================== mở Soạn bài từ dòng


def test_open_row_reads_the_sheet_again(sheet, client):
    read(client)
    sheet.set(2, COL["notes"], "ghi chú mới")
    reads = sheet.reads
    found = sync.open_row(client, "B-001", now=NOW)
    assert sheet.reads == reads + 1 and found.plan.notes == "ghi chú mới"
    reference = sync.plan_ref(found, SHEET_ID, now=NOW)
    assert (reference.key, reference.status, reference.wp_post_id) == ("B-001", "Chưa viết", None)
    assert reference.sheet_hash == sheet_hash(SHEET_ID)
    assert SHEET_ID not in reference.model_dump_json()


@pytest.mark.parametrize("change", ["missing", "duplicate", "unreadable"])
def test_open_row_refuses_missing_duplicate_or_unreadable(sheet, client, change):
    if change == "missing":
        del sheet.grid[1]
    elif change == "duplicate":
        sheet.grid.append(row("B-001", "trùng"))
    else:
        sheet.set(2, COL["keyword"], "")
    with pytest.raises(sync.SheetPlanError):
        sync.open_row(client, "B-001", now=NOW)


# ======================================================================== chuẩn bị trang tính


KINDS = {"addSheet", "updateSheetProperties", "repeatCell", "setDataValidation"}


def request_kinds(sheet):
    return [next(iter(item)) for batch in sheet.structure for item in batch]


def test_prepare_creates_tab_and_header(fake, client):
    sheet = FakePlanSheet(fake, [], tabs=[(0, "Trang tính1"), (5, "Kehoach"), (6, "KeHoach ")])
    result = sync.prepare_sheet(client)
    assert result.created_tab and result.added == tuple(name for name, _ in model.SHEET_COLUMNS)
    assert sheet.grid[0] == HEADER
    assert set(request_kinds(sheet)) <= KINDS and request_kinds(sheet)[0] == "addSheet"
    targets = {
        item[kind].get("range", item[kind].get("properties", {})).get("sheetId")
        for batch in sheet.structure[1:]
        for item in batch
        for kind in item
    }
    assert targets == {NEW_TAB_ID}  # tab tên gần giống không bị đụng
    validations = [item["setDataValidation"] for item in sheet.structure[1]
                   if "setDataValidation" in item]  # fmt: skip
    status = next(v for v in validations if v["range"]["startColumnIndex"] == COL["status"])
    values = [value["userEnteredValue"] for value in status["rule"]["condition"]["values"]]
    assert values == list(model.STATUSES)


def test_prepare_reports_missing_columns_without_writing(fake, client):
    header = ["Mã bài", "Từ khóa chính", "Cột riêng"]
    sheet = FakePlanSheet(fake, [header, ["B-001", "sửa cửa cuốn", "x"]])
    result = sync.prepare_sheet(client)
    assert not result.created_tab and result.added == () and "status" in result.missing
    assert sheet.updates == [] and sheet.grid[0] == header
    assert "Thêm cột còn thiếu" in result.message


def test_prepare_adds_missing_columns_at_the_end(fake, client):
    header = ["Mã bài", "", "Từ khóa chính", "Cột riêng"]
    sheet = FakePlanSheet(fake, [header, ["B-001", "", "sửa cửa cuốn", "x"]])
    result = sync.prepare_sheet(client, add_missing=True)
    assert sheet.grid[0][:4] == header and len(result.added) == 14
    assert sheet.grid[0][4] == "Từ khóa phụ, ý cần có" and sheet.grid[0][17] == "Cập nhật lúc"
    assert sheet.grid[1] == ["B-001", "", "sửa cửa cuốn", "x"]
    plan = read(client)
    assert plan.missing == () and plan.find("B-001").plan.keyword == "sửa cửa cuốn"


def test_prepare_refuses_when_no_room_left(fake, client):
    header = ["Mã bài", "Từ khóa chính"] + [f"Cột {n}" for n in range(20)]
    sheet = FakePlanSheet(fake, [header])
    with pytest.raises(sync.SheetPlanError):
        sync.prepare_sheet(client, add_missing=True)
    assert sheet.updates == []


def test_prepare_formats_only_the_plan_tab(sheet, client):
    sync.prepare_sheet(client)
    (batch,) = sheet.structure
    assert {next(iter(item)) for item in batch} == KINDS - {"addSheet"}
    for item in batch:
        body = next(iter(item.values()))
        target = body.get("range", body.get("properties"))
        assert target["sheetId"] == PLAN_ID


# ======================================================================== chuyển giá trị


@pytest.mark.parametrize("start", ["=", "+", "-", "@", "\t", "\r"])
def test_safe_text_defuses_formula_start(start):
    assert sync.safe_text(f"{start}HYPERLINK(1)") == f" {start}HYPERLINK(1)"
    long = start + "x" * 1999
    assert not sync.safe_text(long).startswith(start) and len(sync.safe_text(long)) <= 2000
    assert sync.safe_text("sửa = cửa") == "sửa = cửa"


def test_to_cell_values():
    assert sync.to_cell("planned_date", date(2026, 11, 20)) == serial(date(2026, 11, 20))
    assert sync.to_cell("wp_post_id", 77) == 77
    assert sync.to_cell("target_id", 12, INDEX) == f"{SITE}/sua-cua-cuon/"
    assert sync.to_cell("target_id", 99, INDEX) == 99
    moment = datetime(2026, 11, 20, 1, 0, tzinfo=UTC)
    assert sync.to_cell("published_at", moment) == "2026-11-20 08:00+07:00"
    with pytest.raises(ValueError):
        sync.to_cell("published_at", datetime(2026, 11, 20, 8, 0))
