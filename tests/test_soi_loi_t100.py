"""Soi Lỗi T-100 (rút gọn): đồng bộ kế hoạch với Google Sheets, cache, nối nháp với dòng kế hoạch,
cảnh báo giá trong chữ AI (G2 / LC-T103-1), danh tính file khóa theo đường thật (SL-T097-5).

Kiểm độc lập với test của Thợ Máy: Sheet giả có trạng thái (``fake_plan_sheet``) đi qua đúng
``SheetsClient`` thật; cache, kho nháp là file SQLite thật trong thư mục tạm. Không gọi Google,
WordPress hay AI thật (bộ chặn mạng của ``tests/conftest.py`` vẫn bật).

Lỗi tìm ra (``xfail(strict=True)``; sửa xong thì gỡ dấu):

- **SL-T100-1** (Thấp): số nhà viết tắt tên đường kiểu Google Maps («45 Đ. Số 7», «123 Đ.Nguyễn Văn
  Linh») hay kiệt ở Đà Nẵng («12 K. Lê Duẩn») bị coi là giá: «Đ.», «K.» sau số khớp đơn vị tiền
  «đ», «k» của ``mentions_price``. Đề xuất AI có địa chỉ công trình bị cảnh báo giá oan và không
  được tick sẵn.
- **SL-T100-2** (Thấp): số đếm có «nghìn», «ngàn», «triệu» («hơn 2 nghìn công trình», «1 nghìn
  lượt tìm mỗi tháng», «3 triệu lượt xem») bị coi là giá: cảnh báo oan, không tick sẵn.
- **SL-T100-3** (Thấp): ghi chú dài hơn 900 ký tự dò giá theo từng khúc 900 ký tự: chỗ cắt khúc
  làm mất phần chữ loại trừ. Từ khóa chính «cửa sắt giá rẻ» vắt qua đầu khúc thành «rẻ», «giá rẻ»
  không còn nằm trong từ khóa; «2 đồng hồ» vắt qua cuối khúc thành «2 đồng». Cùng chữ đó trong
  ghi chú ngắn thì không cảnh báo.
"""

from __future__ import annotations

import json
import os
import sqlite3
import stat
from contextlib import closing
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
import requests
from fake_google import SHEET_ID, FakeGoogle, key_info, make_session, new_private_key
from fake_plan_sheet import HEADER, FakePlanSheet
from test_drafts_images import read_row, real_image, snapshot_with, write_row

from seo_app.content.models import PlanSuggestion, PlanSuggestions
from seo_app.google import service_account
from seo_app.google.service_account import ServiceAccountError, load_service_account
from seo_app.google.sheets import SheetsClient, SheetsError
from seo_app.plan import model, sync
from seo_app.plan.model import PlanRow
from seo_app.plan.propose import WARN_PRICE, Action, Proposal, compare_rows, from_ai
from seo_app.storage.drafts import DraftSnapshot, DraftStore, SendState, new_draft_id
from seo_app.storage.plan_cache import PlanCacheStore

TZ = model.TIMEZONE
NOW = datetime(2026, 10, 29, 9, 30, tzinfo=TZ)
TODAY = NOW.date()
MOI = "MOI-SLT100-KHONG-DUOC-CHEP"
COL = {name: position for position, (name, _) in enumerate(model.SHEET_COLUMNS)}
WINDOWS = pytest.mark.skipif(os.name != "nt", reason="junction chỉ có trên Windows")


def serial(day: date) -> int:
    return (day - date(1899, 12, 30)).days


def row(key="", keyword="", **fields):
    cells = [""] * len(HEADER)
    cells[COL["key"]], cells[COL["keyword"]] = key, keyword
    for name, value in fields.items():
        cells[COL[name]] = value
    return cells


def base_rows():
    return [
        HEADER,
        row("B-001", "sửa cửa cuốn", priority="Cao", status="Chưa viết",
            planned_date=serial(date(2026, 11, 20))),
        row("B-002", "cổng inox 304", priority="Thấp", status="Đang viết"),
        row("B-003", "lan can kính", status="Đã đăng", wp_post_id=77),
    ]  # fmt: skip


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


@pytest.fixture
def sheet(fake):
    return FakePlanSheet(fake, base_rows())


def read(client):
    return sync.read_sheet(client, now=NOW)


def update(base: sync.SheetPlan, key: str, **changes) -> Proposal:
    before = base.find(key).plan
    after = PlanRow.model_validate({**before.model_dump(), **changes})
    return Proposal(Action.UPDATE, key, after, before, "lý do")


def additions(base: sync.SheetPlan, *keywords: str) -> tuple[Proposal, ...]:
    incoming = [PlanRow(keyword=keyword) for keyword in keywords]
    return compare_rows(base.plan_rows(), incoming, today=TODAY).items


def fail_nth(monkeypatch, client, sheet, method: str, name: str, nth: int, result) -> None:
    """Lệnh ``method`` thứ ``nth`` của client: Google làm xong rồi câu trả lời hỏng (``result``)."""
    real = getattr(client, method)
    calls = []

    def wrapped(*args, **kwargs):
        calls.append(1)
        if len(calls) == nth:
            sheet.fail(name, result, apply=True)
        return real(*args, **kwargs)

    monkeypatch.setattr(client, method, wrapped)


def rows_with(client, key: str) -> tuple[int, ...]:
    return read(client).key_rows.get(key, ())


# ===================================================== 1. «unsure» không bao giờ thêm dòng trùng


def test_unsure_second_append_is_confirmed_and_reapply_adds_only_the_rest(
    monkeypatch, sheet, client
):
    """Ba dòng mới; lệnh thêm thứ hai đứt mạng sau khi Google đã thêm. Lần đầu: dòng 1, 2 đã ghi
    (dòng 2 xác nhận bằng đọc lại), dòng 3 chưa gửi. Bấm lại với đúng bản đã xem: dòng 1, 2 là
    xung đột «đã có», chỉ dòng 3 được thêm. Mỗi Mã bài đúng một dòng."""
    base = read(client)
    first, second, third = additions(base, "cửa kéo đài loan", "cổng xếp inox", "lan can sắt")
    assert [p.after.key for p in (first, second, third)] == ["B-004", "B-005", "B-006"]
    error = requests.exceptions.ConnectionError("đứt")
    fail_nth(monkeypatch, client, sheet, "append_row", "append", 2, error)
    result = sync.apply_proposals(client, base, [first, second, third], now=NOW)
    assert result.written == (first, second) and result.not_written == (third,)
    assert result.unsure == () and result.error
    again = sync.apply_proposals(client, base, [first, second, third], now=NOW)
    assert [c.proposal for c in again.conflicts] == [first, second]
    assert again.written == (third,)
    assert len(sheet.appends) == 3
    for key in ("B-004", "B-005", "B-006"):
        assert len(rows_with(client, key)) == 1


def test_server_error_after_append_is_unsure_and_checked(sheet, client):
    """Mã 503 sau khi Google đã thêm dòng: lệnh ghi coi là «chưa rõ» (không phải «chưa ghi»), đọc
    lại thấy Mã bài nên báo đã ghi; câu báo không chép lời máy chủ."""
    base = read(client)
    (proposal,) = additions(base, "cửa kéo đài loan")
    sheet.fail("append", (503, {"error": {"message": MOI}}), apply=True)
    result = sync.apply_proposals(client, base, [proposal], now=NOW)
    assert result.written == (proposal,) and not result.not_written
    assert MOI not in result.message and "503" in result.message
    again = sync.apply_proposals(client, base, [proposal], now=NOW)
    assert again.conflicts and len(sheet.appends) == 1


def test_unsure_append_then_reload_and_propose_again_adds_nothing(sheet, client):
    """Theo đúng lời báo: lệnh thêm không rõ kết quả (đọc lại cũng lỗi) → «Tải lại» → so lại cùng
    file kế hoạch với bản mới: không còn đề xuất «Thêm» nào, không có dòng trùng."""
    base = read(client)
    (proposal,) = additions(base, "cửa kéo đài loan")
    sheet.fail("append", requests.exceptions.ReadTimeout("hết giờ"), apply=True)
    real_read = client.read_plan_values
    calls = []

    def read_then_fail():
        calls.append(1)
        if len(calls) == 2:  # lần đọc lại ngay sau lệnh thêm lỗi
            raise SheetsError("mất mạng")
        return real_read()

    client.read_plan_values = read_then_fail
    result = sync.apply_proposals(client, base, [proposal], now=NOW)
    assert result.unsure == (proposal,) and "Tải lại" in result.message
    reloaded = read(client)  # «Tải lại»
    again = compare_rows(reloaded.plan_rows(), [PlanRow(keyword="cửa kéo đài loan")], today=TODAY)
    assert all(p.action is not Action.ADD for p in again.items)
    assert rows_with(client, "B-004") == (5,) and len(sheet.appends) == 1


def test_ai_added_row_unsure_then_reapply_is_not_duplicated(monkeypatch, sheet, client):
    """Đường AI («them»): Mã bài do code cấp; lệnh thêm đứt sau khi Google đã thêm, đọc lại cũng
    lỗi (chưa rõ); bấm áp dụng lại với bản cũ: xung đột «đã có», không thêm lần hai."""
    base = read(client)
    answer = PlanSuggestions(
        items=[
            PlanSuggestion.model_validate(
                {name: "" for name in PlanSuggestion.model_fields}
                | {"action": "them", "keyword": "cửa cuốn kêu to", "reason": "Khách hỏi nhiều."}
            )
        ]
    )
    (proposal,) = from_ai(answer, base.plan_rows(), today=TODAY).items
    assert proposal.action is Action.ADD and proposal.after.key == "B-004"
    sheet.fail("append", requests.exceptions.ConnectionError("đứt"), apply=True)
    real_read = client.read_plan_values
    calls = []

    def read_then_fail():
        calls.append(1)
        if len(calls) == 2:
            raise SheetsError("mất mạng")
        return real_read()

    monkeypatch.setattr(client, "read_plan_values", read_then_fail)
    assert sync.apply_proposals(client, base, [proposal], now=NOW).unsure == (proposal,)
    again = sync.apply_proposals(client, base, [proposal], now=NOW)
    assert again.conflicts and not again.written and len(sheet.appends) == 1
    assert rows_with(client, "B-004") == (5,)


# ============================================== 2. bảng tính và máy cùng đổi (xung đột)


def test_unsure_update_then_other_machine_edits_same_cell_is_a_conflict(sheet, client):
    """Lệnh ghi ô không rõ kết quả (đã ghi), rồi máy khác sửa đúng ô đó: bấm lại thì là xung đột,
    ô của máy kia giữ nguyên, không có lệnh ghi thứ hai."""
    base = read(client)
    proposal = update(base, "B-001", priority="Thấp")
    sheet.fail("update", requests.exceptions.ConnectionError("đứt"), apply=True)
    assert sync.apply_proposals(client, base, [proposal], now=NOW).unsure == (proposal,)
    sheet.set(2, COL["priority"], "Trung bình")  # máy khác
    again = sync.apply_proposals(client, base, [proposal], now=NOW)
    (conflict,) = again.conflicts
    assert conflict.fields == ("priority",) and conflict.now.priority == "Trung bình"
    assert sheet.cell(2, COL["priority"]) == "Trung bình" and len(sheet.updates) == 1


def test_other_machine_already_wrote_the_same_value(sheet, client):
    """Máy khác ghi đúng giá trị đề xuất: tính là đã ghi, không gửi lệnh ghi nào."""
    base = read(client)
    sheet.set(2, COL["priority"], "Thấp")
    result = sync.apply_proposals(client, base, [update(base, "B-001", priority="Thấp")], now=NOW)
    assert len(result.written) == 1 and not result.conflicts and sheet.updates == []


def test_columns_moved_between_view_and_apply_are_written_by_name(sheet, client):
    """Giữa lúc xem và lúc áp dụng, người dùng kéo đổi chỗ cột «Ưu tiên» với «Ghi chú của thợ» và
    chèn một cột riêng ở đầu: ô được ghi theo **tên cột** của bản vừa đọc; ghi chú, cột riêng giữ
    nguyên; dòng mới thêm để trống cột riêng."""
    base = read(client)
    for line in sheet.grid:
        line[COL["priority"]], line[COL["notes"]] = line[COL["notes"]], line[COL["priority"]]
        line.insert(0, "Cột riêng" if line is sheet.grid[0] else "riêng")
    sheet.set(2, 1 + COL["priority"], "ghi chú cũ")  # ô ghi chú (nay ở chỗ cột «Ưu tiên» cũ)
    base_notes = base.find("B-001").plan.notes
    assert base_notes == ""
    result = sync.apply_proposals(client, base, [update(base, "B-001", priority="Thấp")], now=NOW)
    assert len(result.written) == 1 and not result.conflicts
    fresh = read(client)
    assert fresh.find("B-001").plan.priority == "Thấp"
    assert fresh.find("B-001").plan.notes == "ghi chú cũ"
    assert sheet.cell(2, 0) == "riêng" and sheet.cell(2, 1 + COL["notes"]) == "Thấp"
    (added,) = additions(base, "cửa kéo đài loan")
    assert sync.apply_proposals(client, base, [added], now=NOW).written == (added,)
    assert sheet.cell(5, 0) == "" and read(client).find("B-004").plan.keyword == "cửa kéo đài loan"


def test_conflict_message_never_copies_cell_text(sheet, client):
    base = read(client)
    sheet.set(2, COL["notes"], MOI)  # máy khác sửa ghi chú
    result = sync.apply_proposals(client, base, [update(base, "B-001", notes="ghi chú mới")],
                                  now=NOW)  # fmt: skip
    (conflict,) = result.conflicts
    assert conflict.now.notes == MOI  # bản «bây giờ» để hiện trong bảng
    assert MOI not in result.message and MOI not in conflict.reason and MOI not in conflict.label
    assert sheet.cell(2, COL["notes"]) == MOI


def test_stale_cached_plan_never_overwrites_a_newer_cell(tmp_path, sheet, client):
    """Người dùng duyệt trên bản lưu (cache còn mới); sau lúc lưu, máy khác đổi ô: áp dụng thì là
    xung đột (bản lưu là «bản gốc»), Sheet giữ ô của máy kia."""
    store = PlanCacheStore(path=tmp_path / "plan_cache.sqlite")
    assert sync.get_plan(store, SHEET_ID, client, now=NOW).plan.from_cache is False
    sheet.set(2, COL["priority"], "Thấp")  # máy khác, sau lúc lưu
    cached = sync.get_plan(store, SHEET_ID, client, now=NOW + timedelta(minutes=1)).plan
    assert cached.from_cache and cached.find("B-001").plan.priority == "Cao"
    result = sync.apply_proposals(client, cached, [update(cached, "B-001", priority="Trung bình")],
                                  now=NOW)  # fmt: skip
    (conflict,) = result.conflicts
    assert conflict.now.priority == "Thấp" and sheet.updates == []


def test_tampered_cache_cannot_steer_a_write_to_another_row(tmp_path, sheet, client):
    """Cache bị sửa tay (mã băm tính lại cho khớp): dòng B-001 trong cache mang từ khóa khác Sheet.
    Đề xuất dựng trên cache đó không ghi được gì (ô Từ khóa khác bản gốc)."""
    store = PlanCacheStore(path=tmp_path / "plan_cache.sqlite")
    values = [list(r) for r in base_rows()]
    values[1][COL["keyword"]] = "từ khóa giả trong cache"
    store.save(SHEET_ID, values, NOW)
    cached = sync.get_plan(store, SHEET_ID, client, now=NOW).plan
    assert cached.from_cache and cached.find("B-001").plan.keyword == "từ khóa giả trong cache"
    result = sync.apply_proposals(client, cached, [update(cached, "B-001", priority="Thấp")],
                                  now=NOW)  # fmt: skip
    (conflict,) = result.conflicts
    assert "keyword" in conflict.fields and sheet.updates == []


# ===================================================================== 3. luôn RAW, chữ an toàn


def _query(request) -> dict[str, list[str]]:
    return parse_qs(urlsplit(request.url).query)


def test_every_write_is_raw_and_append_inserts_rows(fake, sheet, client, tmp_path):
    """Mọi lệnh ghi đi qua client thật: ghi ô, thêm dòng, ghi trạng thái, chuẩn bị trang tính.
    Không lệnh nào mang ``USER_ENTERED``; lệnh thêm dòng là ``RAW`` + ``INSERT_ROWS``."""
    base = read(client)
    (added,) = additions(base, '=HYPERLINK("http://x")')
    changed = update(
        base, "B-001", notes="+84 909 000 000", title_hint="-giảm giá", priority="Thấp"
    )
    result = sync.apply_proposals(client, base, [changed, added], now=NOW)
    assert len(result.written) == 2
    ref = sync.plan_ref(sync.open_row(client, "B-002", now=NOW), SHEET_ID, now=NOW)
    write = sync.status_write(ref, model.STATUS_DRAFT_SENT, wp_post_id=501, now=NOW)
    assert sync.write_status(client, write, now=NOW).outcome is sync.WriteOutcome.WRITTEN
    sync.prepare_sheet(client)
    writes = [r for r in fake.sheets_requests() if r.method == "POST"]
    assert writes
    for request in writes:
        assert "USER_ENTERED" not in (request.url + (request.body or b"").decode("utf-8"))
    value_writes = [r for r in writes if "values:batchUpdate" in r.url]
    assert value_writes and all(json.loads(r.body)["valueInputOption"] == "RAW"
                                for r in value_writes)  # fmt: skip
    (append,) = [r for r in writes if r.url.split("?")[0].endswith(":append")]
    assert _query(append)["valueInputOption"] == ["RAW"]
    assert _query(append)["insertDataOption"] == ["INSERT_ROWS"]
    # chữ dạng công thức được thêm dấu cách đầu, ở mọi cột chữ
    assert sheet.cell(2, COL["notes"]) == " +84 909 000 000"
    assert sheet.cell(2, COL["title_hint"]) == " -giảm giá"
    assert sheet.cell(5, COL["keyword"]) == ' =HYPERLINK("http://x")'


@pytest.mark.parametrize("start", ["\t", "\r", "  ", chr(0x00A0), chr(0x200B), chr(0xFEFF)])
def test_blank_or_hidden_start_before_formula_is_still_defused(start):
    """Ký tự trắng, vô hình đứng trước «=»: bộ làm sạch bỏ trước, rồi chữ vẫn được thêm dấu cách."""
    assert sync.safe_text(model.clean_text(f"{start}=1+1")) == " =1+1"
    assert sync.to_cell("notes", PlanRow(keyword="cửa sắt", notes=f"{start}@x").notes) == " @x"


def test_formula_like_cells_round_trip_without_false_conflicts(sheet, client):
    """Ô app ghi có dấu cách đầu (chữ dạng công thức); đọc lại rồi đề xuất tiếp trên dòng đó không
    sinh xung đột giả, và lần ghi không rõ kết quả được nhận là đã ghi."""
    base = read(client)
    first = sync.apply_proposals(client, base, [update(base, "B-002", notes="=1+1 ghi tay")],
                                 now=NOW)  # fmt: skip
    assert len(first.written) == 1
    fresh = read(client)
    assert fresh.find("B-002").plan.notes == "=1+1 ghi tay"
    proposal = update(fresh, "B-002", notes="@thợ Hùng: đo lại")
    sheet.fail("update", requests.exceptions.ConnectionError("đứt"), apply=True)
    assert sync.apply_proposals(client, fresh, [proposal], now=NOW).unsure == (proposal,)
    again = sync.apply_proposals(client, fresh, [proposal], now=NOW)
    assert again.written == (proposal,) and not again.conflicts
    assert sheet.cell(3, COL["notes"]) == " @thợ Hùng: đo lại"


# ================================================= 4. ghi trạng thái sau khi gửi, thử lại


def test_unsure_status_write_that_landed_is_finished_on_retry(tmp_path, sheet, client):
    """LC-T094-30: lệnh ghi trạng thái đứt sau khi Google đã ghi; việc còn nợ ở kho nháp; lần thử
    lại đọc Sheet, thấy đã đúng thì bỏ việc, không ghi lần hai."""
    store = DraftStore(path=tmp_path / "drafts.sqlite")
    draft_id = new_draft_id()
    ref = sync.plan_ref(sync.open_row(client, "B-001", now=NOW), SHEET_ID, now=NOW)
    write = sync.status_write(ref, model.STATUS_DRAFT_SENT, wp_post_id=501, now=NOW)
    sheet.fail("update", requests.exceptions.ConnectionError("đứt"), apply=True)
    first = sync.record_status(client, store, draft_id, write, now=NOW)
    assert first.outcome is sync.WriteOutcome.UNSURE and store.load_plan_write(draft_id) == write
    (item,) = sync.retry_pending(client, store, SHEET_ID, now=NOW)
    assert item.result.outcome is sync.WriteOutcome.ALREADY
    assert store.load_plan_write(draft_id) is None and len(sheet.updates) == 1
    assert sheet.cell(2, COL["status"]) == model.STATUS_DRAFT_SENT
    assert sheet.cell(2, COL["wp_post_id"]) == 501


@pytest.mark.parametrize(
    ("status", "post", "outcome"),
    [
        ("Đã đăng", 501, sync.WriteOutcome.LATER),  # máy khác đã đi tiếp: không lùi
        ("Đã gửi nháp", 999, sync.WriteOutcome.CONFLICT),  # bài khác đã gắn vào dòng
        ("Bỏ", "", sync.WriteOutcome.CONFLICT),  # người dùng đã bỏ dòng
        ("chữ lạ", "", sync.WriteOutcome.CONFLICT),
    ],
)
def test_retry_checks_the_row_again_and_drops_the_write(tmp_path, sheet, client, status, post,
                                                        outcome):  # fmt: skip
    store = DraftStore(path=tmp_path / "drafts.sqlite")
    draft_id = new_draft_id()
    ref = sync.plan_ref(sync.open_row(client, "B-001", now=NOW), SHEET_ID, now=NOW)
    write = sync.status_write(ref, model.STATUS_DRAFT_SENT, wp_post_id=501, now=NOW)
    assert sync.record_status(None, store, draft_id, write, now=NOW).finished is False  # mất mạng
    sheet.set(2, COL["status"], status)
    sheet.set(2, COL["wp_post_id"], post)
    (item,) = sync.retry_pending(client, store, SHEET_ID, now=NOW)
    assert item.result.outcome is outcome
    assert store.load_plan_write(draft_id) is None and sheet.updates == []
    assert sheet.cell(2, COL["status"]) == status


@pytest.mark.parametrize("typed", ["đã gửi nháp ", "Da gui nhap", "ĐÃ GỬI NHÁP"])
def test_status_typed_differently_counts_as_already_written(sheet, client, typed):
    ref = sync.plan_ref(sync.open_row(client, "B-001", now=NOW), SHEET_ID, now=NOW)
    write = sync.status_write(ref, model.STATUS_DRAFT_SENT, wp_post_id=501, now=NOW)
    sheet.set(2, COL["status"], typed)
    sheet.set(2, COL["wp_post_id"], "501")
    assert sync.write_status(client, write, now=NOW).outcome is sync.WriteOutcome.ALREADY
    assert sheet.updates == []


def test_open_row_with_empty_status_gives_a_valid_plan_ref(fake, client):
    """Dòng mới gõ tay, ô Trạng thái trống (thường gặp nhất): «Viết bài» dựng được ``plan_ref``."""
    FakePlanSheet(fake, [HEADER, row("B-009", "cửa sắt bị kẹt")])
    ref = sync.plan_ref(sync.open_row(client, "B-009", now=NOW), SHEET_ID, now=NOW)
    assert ref.status == model.STATUS_NEW and ref.wp_post_id is None


# ============================================================ 5. cache hỏng, cũ, bị khóa


def _seed_cache(store: PlanCacheStore) -> None:
    store.save(SHEET_ID, [list(r) for r in base_rows()], NOW - timedelta(hours=1))


def test_locked_cache_shows_the_sheet_and_keeps_the_file(tmp_path, sheet, client):
    """Chương trình khác giữ khóa ghi độc quyền file cache: trang vẫn có kế hoạch vừa đọc, kèm câu
    báo «đang bận»; file không bị xóa; nhả khóa thì lần sau ghi lại được."""
    store = PlanCacheStore(path=tmp_path / "plan_cache.sqlite")
    _seed_cache(store)
    holder = sqlite3.connect(store.path, isolation_level=None)
    try:
        holder.execute("BEGIN EXCLUSIVE")
        listing = sync.get_plan(store, SHEET_ID, client, now=NOW)
        assert listing.plan is not None and not listing.plan.from_cache
        assert "bận" in listing.notice and store.path.exists() and store.reset_count == 0
    finally:
        holder.execute("ROLLBACK")
        holder.close()
    after = sync.get_plan(store, SHEET_ID, client, refresh=True, now=NOW)
    assert after.notice == "" and store.load(SHEET_ID).fetched_at == NOW


def test_cache_damaged_inside_the_file_is_dropped(tmp_path, sheet, client):
    """File cache hỏng ở giữa (trang dữ liệu bị ghi đè): bỏ cache, đọc lại Sheet, trang không
    lỗi."""
    store = PlanCacheStore(path=tmp_path / "plan_cache.sqlite")
    values = [list(r) for r in base_rows()] + [row(f"B-{n:03d}", f"từ khóa {n}", notes="x" * 300)
                                               for n in range(4, 60)]  # fmt: skip
    store.save(SHEET_ID, values, NOW)
    data = bytearray(store.path.read_bytes())
    assert len(data) > 4 * 4096
    data[2 * 4096 : 3 * 4096] = b"\xa5" * 4096
    store.path.write_bytes(bytes(data))
    assert store.load(SHEET_ID) is None and store.reset_count == 1
    listing = sync.get_plan(store, SHEET_ID, client, now=NOW)
    assert listing.plan is not None and not listing.plan.from_cache and listing.notice == ""


@pytest.mark.skipif(os.name != "nt", reason="thuộc tính chỉ đọc kiểu Windows")
def test_read_only_cache_file_still_shows_the_sheet(tmp_path, sheet, client):
    store = PlanCacheStore(path=tmp_path / "plan_cache.sqlite")
    _seed_cache(store)
    store.path.chmod(stat.S_IREAD)
    try:
        listing = sync.get_plan(store, SHEET_ID, client, refresh=True, now=NOW)
        assert listing.plan is not None and not listing.plan.from_cache and listing.notice
        assert MOI not in listing.notice
    finally:
        store.path.chmod(stat.S_IREAD | stat.S_IWRITE)


def test_cache_path_taken_by_a_folder_still_shows_the_sheet(tmp_path, sheet, client):
    store = PlanCacheStore(path=tmp_path / "plan_cache.sqlite")
    store.path.mkdir()
    listing = sync.get_plan(store, SHEET_ID, client, now=NOW)
    assert listing.plan is not None and not listing.plan.from_cache and listing.notice
    assert store.path.is_dir()  # không xóa thứ không phải file của app


def test_old_cache_and_google_down_shows_saved_copy_with_vietnam_time(tmp_path, sheet, client):
    store = PlanCacheStore(path=tmp_path / "plan_cache.sqlite")
    store.save(SHEET_ID, [list(r) for r in base_rows()], datetime(2026, 10, 29, 1, 5, tzinfo=TZ))
    sheet.fail("read", (500, {"error": {"message": MOI}}))
    listing = sync.get_plan(store, SHEET_ID, client, now=NOW)
    assert listing.plan.from_cache and "01:05 29/10/2026" in listing.notice
    assert MOI not in listing.notice


# ===================================================== 6. kho nháp: luồng gửi T-086, T-089


def test_send_claim_on_a_row_written_by_the_old_app_still_works(tmp_path):
    """Nháp gửi bằng app trước T-100 (dòng trạng thái gửi 3 trường): bấm gửi lại bằng app mới, so
    rồi đặt «đang gửi» (T-089) vẫn qua; tab thứ hai cầm bản cũ thì không qua."""
    store = DraftStore(path=tmp_path / "drafts.sqlite")
    snap = store.save(DraftSnapshot())
    old = {"pending": False, "post_id": 501, "updated_at": "2026-10-26T10:00:00+07:00"}
    with closing(sqlite3.connect(store.path)) as conn, conn:
        conn.execute("INSERT INTO send_states (id, data) VALUES (?, ?)", (snap.id, json.dumps(old)))
    seen = store.load_send_state(snap.id)
    claim = SendState.now(pending=True, post_id=501)
    assert store.save_send_state(snap.id, claim, expected=(seen, False))
    other_tab = SendState.now(pending=True, post_id=501)
    assert not store.save_send_state(snap.id, other_tab, expected=(seen, False))
    assert store.load_send_state(snap.id) == claim


def test_v2_draft_keeps_approved_image_hash_after_upgrade(tmp_path):
    """Nháp khuôn 2 có băm ảnh đã duyệt (T-089, ``approved_sha256``): mở bằng app mới vẫn giữ băm,
    lưu lại lên khuôn 3 vẫn có băm (không bắt duyệt lại ảnh oan, không mất chốt chặn ảnh bị
    thay)."""
    store = DraftStore(path=tmp_path / "drafts.sqlite")
    digest = "ab" * 32
    saved = store.save(snapshot_with(real_image(approved_sha256=digest)))
    data = json.loads(read_row(store, saved.id))
    data["schema_version"] = 2
    data.pop("plan")
    write_row(store, saved.id, data)
    loaded = store.load(saved.id)
    assert loaded.dropped_images == 0 and loaded.parts[1].chosen_image.approved_sha256 == digest
    store.save(loaded)
    stored = json.loads(read_row(store, saved.id))
    assert stored["schema_version"] == 3
    assert stored["parts"][1]["chosen_image"]["approved_sha256"] == digest


def test_autosave_keeps_plan_link_and_send_state(tmp_path):
    """Nháp mở từ dòng kế hoạch: tự lưu nhiều lần không mất ``plan``, không đụng trạng thái gửi;
    ``find_plan_draft`` vẫn tìm ra đúng nháp đó."""
    store = DraftStore(path=tmp_path / "drafts.sqlite")
    sheet_id_hash = "a" * 64
    ref = {"key": "B-007", "sheet_hash": sheet_id_hash, "status": "Chưa viết", "opened_at": NOW}
    snap = store.save(DraftSnapshot(keyword="cửa sắt bị kẹt", plan=ref))
    sent = SendState.now(pending=False, post_id=812)
    store.save_send_state(snap.id, sent)
    for step in range(3):
        snap = store.save(snap.model_copy(update={"step": step}))
    loaded = store.load(snap.id)
    assert loaded.plan.key == "B-007" and store.load_send_state(snap.id) == sent
    assert store.find_plan_draft("B-007", sheet_id_hash) == snap.id
    assert store.find_plan_draft("B-007", "b" * 64) is None


# =================================================================== 7. G2: cảnh báo giá


def _suggestion(**fields) -> PlanSuggestion:
    fields.setdefault("reason", "Ghi chú yêu cầu.")
    return PlanSuggestion.model_validate(
        {name: "" for name in PlanSuggestion.model_fields} | fields
    )


def _price_warned(notes: str, keyword: str = "bản lề cổng sắt bị xệ", field: str = "notes"):
    current = (PlanRow(key="B-001", keyword=keyword),)
    answer = PlanSuggestions(items=[_suggestion(action="cap_nhat", key="B-001", **{field: notes})])
    (proposal,) = from_ai(answer, current, today=TODAY).items
    return WARN_PRICE in proposal.warnings, proposal.preselected


ORDINARY = [
    "Công trình làm năm 2026 ở Thủ Đức",
    "Khách lắp từ 2019, nay bản lề xệ",
    "Bảo hành 2 năm, bảo trì 6 tháng",
    "Cửa 3200 mm x 2400 mm, khung hộp 40x80 dày 1,4 ly",
    "Cổng cao 2m4, rộng 3,5 m",
    "Tôn dày 1.2mm, nặng 100 kg",
    "Motor 500 W, 220 V",
    "Cửa 2 cánh, 4 bản lề, 2 đôi then",
    "Nghiêng 5 độ, lệch 2 cm",
    "Inox 304, thép hộp 30x60, 3 trụ",
    "Nhà số 12 hẻm 45 Lê Văn Sỹ",
    "Công trình ở 12/3 Lê Lợi, quận 1",
    "Địa chỉ 88 đường 3/2, quận 10",
    "Thợ tới lúc 8h sáng, làm từ thứ 2 đến thứ 7",
    "Liên quan bài B-012 đã có; ảnh ở thư mục CT012",
    "Đồng bộ màu với cổng, 2 đồng hồ điện ở trụ",
    "Tỷ lệ cửa 2 cánh lệch, xu hướng cổng 2026",
]


@pytest.mark.parametrize("notes", ORDINARY)
def test_ordinary_numbers_are_not_a_price(notes):
    assert _price_warned(notes) == (False, True)


@pytest.mark.parametrize(
    ("field", "text"),
    [
        ("notes", "Thay motor 1tr5"),
        ("notes", "Bộ tay nắm 500 nghìn đồng"),
        ("notes", "Giá chỉ từ 99$"),
        ("title_hint", "Bảng giá sửa cổng sắt 2026"),
        ("secondary", "sửa cửa giá rẻ"),
        ("title_hint", "Sửa bản lề trọn gói"),
    ],
)
def test_price_forms_warn_in_every_ai_text_field(field, text):
    assert _price_warned(text, field=field) == (True, False)


def test_keyword_with_price_word_is_not_a_price_when_ai_changes_it():
    """AI đổi từ khóa chính sang từ khóa có chữ «giá»: chính từ khóa không bị coi là nói giá."""
    current = (PlanRow(key="B-001", keyword="bản lề cổng sắt bị xệ"),)
    answer = PlanSuggestions(
        items=[_suggestion(action="cap_nhat", key="B-001", keyword="bảng giá cửa cuốn")]
    )
    (proposal,) = from_ai(answer, current, today=TODAY).items
    assert WARN_PRICE not in proposal.warnings


@pytest.mark.xfail(
    strict=True,
    reason="SL-T100-1: số nhà viết tắt tên đường «Đ.», kiệt «K.» khớp đơn vị tiền «đ», «k»",
)
@pytest.mark.parametrize(
    "notes",
    [
        "Công trình ở 45 Đ. Số 7, Bình Tân",
        "Khách ở 123 Đ.Nguyễn Văn Linh, quận 7",
        "Nhà khách ở kiệt 12 K. Lê Duẩn, Đà Nẵng",
    ],
)
def test_sl_t100_1_abbreviated_street_after_house_number_is_not_a_price(notes):
    assert _price_warned(notes) == (False, True)


@pytest.mark.xfail(
    strict=True,
    reason="SL-T100-2: số đếm có «nghìn», «ngàn», «triệu» (công trình, lượt tìm) bị coi là giá",
)
@pytest.mark.parametrize(
    "notes",
    [
        "Xưởng đã làm hơn 2 nghìn công trình",
        "Từ khóa có khoảng 1 nghìn lượt tìm mỗi tháng",
        "Hơn 5 ngàn khách đã gọi hỏi bản lề",
        "Video hướng dẫn có 3 triệu lượt xem",
    ],
)
def test_sl_t100_2_counts_with_thousand_or_million_are_not_a_price(notes):
    assert _price_warned(notes) == (False, True)


FILLER = "Cửa sắt lâu năm bị rỉ ở chân, thợ cạo rỉ rồi sơn lại hai lớp. "


def _long_note(insert: str, at: int, length: int = 2000) -> str:
    text = (FILLER * 60)[:at] + insert + " " + FILLER * 60
    return text[:length]


def test_long_notes_place_the_same_text_far_from_window_edges_without_warning():
    """Đối chứng cho SL-T100-3: cùng chữ, nằm xa chỗ cắt khúc, không cảnh báo."""
    assert _price_warned(_long_note("cửa sắt giá rẻ", 300), keyword="cửa sắt giá rẻ") == (
        False, True
    )  # fmt: skip
    assert _price_warned(_long_note("2 đồng hồ điện ở trụ", 300)) == (False, True)


@pytest.mark.xfail(
    strict=True,
    reason="SL-T100-3: dò giá theo khúc 900 ký tự, chỗ cắt khúc làm mất phần loại trừ (từ khóa, "
    "«đồng hồ») nên ghi chú dài bị cảnh báo giá oan",
)
@pytest.mark.parametrize(
    ("insert", "at", "keyword"),
    [
        ("cửa sắt giá rẻ", 692, "cửa sắt giá rẻ"),  # từ khóa vắt qua đầu khúc thứ hai (700)
        ("cửa sắt giá rẻ", 1092, "cửa sắt giá rẻ"),  # vắt qua đầu khúc cuối (1100)
        ("2 đồng hồ điện ở trụ", 893, "bản lề cổng sắt bị xệ"),  # «2 đồng | hồ» ở cuối khúc đầu
    ],
)
def test_sl_t100_3_long_notes_cut_at_window_edges_are_not_a_price(insert, at, keyword):
    assert _price_warned(_long_note(insert, at), keyword=keyword) == (False, True)


# =========================================== 8. SL-T097-5: danh tính file khóa theo đường thật


def _key_file(folder: Path, private_key) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "du-an-thu-0123abcd.json"
    path.write_text(json.dumps(key_info(private_key)), encoding="utf-8")
    return path


def test_dots_that_lead_back_into_the_project_are_still_refused(tmp_path, private_key):
    project = tmp_path / "du-an"
    key = _key_file(project / "bi-mat", private_key)
    typed = os.sep.join([str(tmp_path), "ngoai", "..", "du-an", "bi-mat", key.name])
    (tmp_path / "ngoai").mkdir()
    with pytest.raises(ServiceAccountError):
        load_service_account(typed, project_root=project)
    assert service_account._inside_by_identity(Path(typed), project)


@WINDOWS
def test_junction_outside_pointing_into_the_project_is_refused(tmp_path, private_key):
    import _winapi

    project = tmp_path / "du-an"
    key = _key_file(project / "bi-mat", private_key)
    link = tmp_path / "ngoai-tro-vao"
    _winapi.CreateJunction(str(project), str(link))
    with pytest.raises(ServiceAccountError):
        load_service_account(link / "bi-mat" / key.name, project_root=project)


@WINDOWS
def test_junction_inside_the_project_pointing_out_is_still_refused(tmp_path, private_key):
    """Đường gõ nằm trong thư mục dự án (qua junction trỏ ra ngoài): vẫn chặn như trước T-100
    (phép so chuỗi theo đường gõ), dù file thật ở ngoài."""
    import _winapi

    project = tmp_path / "du-an"
    project.mkdir()
    outside = tmp_path / "ngoai"
    key = _key_file(outside, private_key)
    _winapi.CreateJunction(str(outside), str(project / "lien-ket"))
    with pytest.raises(ServiceAccountError):
        load_service_account(project / "lien-ket" / key.name, project_root=project)
    assert load_service_account(key, project_root=project).file_name == key.name
