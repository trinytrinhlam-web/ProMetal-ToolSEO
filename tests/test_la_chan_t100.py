"""Lá Chắn T-100 (rút gọn): đồng bộ kế hoạch với Google Sheets, cache, nối nháp, G2.

Lỗi tìm ra (``xfail(strict=True)``; sửa xong thì gỡ dấu):

- **LC-T100-1** (Thấp): Sheet đã có 1.000 dòng kế hoạch (vùng đọc ``A1:Z1001`` đầy). Google chỉ
  trả 1.001 dòng đầu, app không báo gì. Dòng «Thêm» được Google thêm sau dòng cuối (dòng 1.002),
  **ngoài vùng đọc**: đọc lại không thấy, đề xuất lại đúng bài đó thì thêm lần nữa với cùng Mã
  bài; lệnh thêm «chưa rõ» (Google đã thêm) bị báo «chưa ghi» vì đọc lại không thấy, bấm lại thành
  dòng trùng. Test với Sheet giả cắt lệnh đọc đúng như Google (Sheet giả của test hiện có trả mọi
  dòng nên không thấy lỗi này). Cách sửa gợi ý: vùng đọc đầy (Google trả đủ ``MAX_ROWS`` dòng) thì
  có câu báo cố định («phần mềm chỉ đọc 1.000 dòng đầu») và không thêm dòng mới (``Conflict``);
  ``_key_present`` khi vùng đầy trả «chưa rõ», không trả «chưa có».
- **LC-T100-2** (Thấp; cách sửa LC-T103-1 chưa đủ): cảnh báo giá trong chữ AI (``WARN_PRICE``,
  dò bằng ``mentions_price``) bỏ lọt cách viết giá thường gặp: «giá / đơn giá / báo giá / chi phí
  / phí» rồi số tiền không có đơn vị («Giá thay motor 1.200.000», «Chi phí 800.000 một lần»), và
  «VNĐ», «VND» đứng **trước** số. Các đề xuất đó vẫn được tick sẵn. Cách sửa gợi ý: dò thêm số có
  dấu chấm nghìn đi sau các chữ đó (trong vài từ) hay đi sau «VNĐ/VND»; không cảnh báo số đếm
  («10.000 lượt tìm mỗi tháng», test canh dưới). Sửa ``_PRICE`` của ``seo_app/onpage/meta.py``
  (dùng chung với bước SEO) thì chạy test mọi nơi gọi.
- **LC-T100-3** (Thấp): ``record_status`` (lần ghi đầu ngay sau khi gửi bài) ghi trạng thái vào
  Sheet **đang kết nối** mà không so mã băm Sheet của nháp (``write.sheet_hash``), trong khi
  ``retry_pending`` có so. Nháp mở từ Sheet bản sao (thử thật, LC-T094-44) rồi đổi
  ``GOOGLE_SHEET_ID`` về Sheet thật, gửi nháp đó: «Đã gửi nháp» và Mã bài WordPress ghi vào dòng
  cùng Mã bài của **Sheet khác**. Cách sửa gợi ý: so ``write.sheet_hash`` với mã băm Sheet của
  client (client cho biết mã Sheet, hay ``record_status`` nhận ``sheet_id`` như ``retry_pending``);
  khác thì giữ việc còn nợ, không ghi.

Test canh (không xfail): số đếm có dấu chấm nghìn không bị coi là giá.

Không gọi Google thật: Google giả gắn vào ``requests.Session`` (bộ chặn mạng của
``tests/conftest.py`` vẫn bật); khóa RSA sinh lúc chạy.
"""

from __future__ import annotations

import inspect
import json
import os
from datetime import UTC, date, datetime

import pytest
import requests
from fake_google import SHEET_ID, FakeGoogle, key_info, make_session, new_private_key
from fake_plan_sheet import HEADER, FakePlanSheet

from seo_app.content.models import PlanSuggestion, PlanSuggestions
from seo_app.google.service_account import load_service_account
from seo_app.google.sheets import MAX_ROWS, SheetsClient
from seo_app.plan import model, propose, sync
from seo_app.plan.model import PlanRow
from seo_app.plan.propose import compare_rows
from seo_app.storage.drafts import DraftPlanRef, DraftStore, new_draft_id
from seo_app.storage.plan_cache import sheet_hash

NOW = datetime(2026, 10, 29, 1, 0, tzinfo=UTC)
TODAY = date(2026, 10, 29)
COL = {name: position for position, (name, _) in enumerate(model.SHEET_COLUMNS)}
NEW_KEYWORD = "cửa kéo bị kẹt ray"


class GoogleLikeSheet(FakePlanSheet):
    """Như Google thật: lệnh đọc vùng ``A1:Z1001`` chỉ trả tối đa 1.001 dòng đầu."""

    def _read(self, request):
        answer = super()._read(request)
        answer["values"] = answer["values"][:MAX_ROWS]
        return answer


def row(key="", keyword="", **fields):
    cells = [""] * len(HEADER)
    cells[COL["key"]], cells[COL["keyword"]] = key, keyword
    for name, value in fields.items():
        cells[COL[name]] = value
    return cells


@pytest.fixture(scope="module")
def private_key():
    return new_private_key()


@pytest.fixture
def fake():
    return FakeGoogle()


@pytest.fixture
def client(fake, tmp_path, private_key):
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


@pytest.fixture
def full_sheet(fake):
    rows = [HEADER] + [row(f"B-{i:03d}", f"cửa sắt mẫu số {i}") for i in range(1, MAX_ROWS)]
    return GoogleLikeSheet(fake, rows)


def rows_with(sheet: FakePlanSheet, keyword: str) -> list[int]:
    return [n for n, cells in enumerate(sheet.grid, start=1)
            if len(cells) > COL["keyword"] and cells[COL["keyword"]] == keyword]  # fmt: skip


def add_new_article(client) -> sync.ApplyResult:
    base = sync.read_sheet(client, now=NOW)
    proposals = compare_rows(base.plan_rows(), [PlanRow(keyword=NEW_KEYWORD)]).items
    return sync.apply_proposals(client, base, list(proposals), now=NOW)


# ------------------------------------------------------------------------------- LC-T100-1


@pytest.mark.xfail(strict=True, reason="LC-T100-1: Sheet đầy 1.000 dòng mà app không báo")
def test_lc_t100_1_full_sheet_is_reported(full_sheet, client):
    plan = sync.read_sheet(client, now=NOW)
    assert len(plan.rows) == MAX_ROWS - 1
    assert plan.warnings


@pytest.mark.xfail(
    strict=True, reason="LC-T100-1: dòng thêm ngoài vùng đọc, đề xuất lại thêm trùng"
)
def test_lc_t100_1_full_sheet_never_gets_the_same_article_twice(full_sheet, client):
    add_new_article(client)
    add_new_article(client)  # người dùng dán lại kế hoạch: app phải thấy bài đã có (hay không thêm)
    assert len(rows_with(full_sheet, NEW_KEYWORD)) <= 1


@pytest.mark.xfail(strict=True, reason="LC-T100-1: thêm «chưa rõ» trên Sheet đầy bị báo «chưa ghi»")
def test_lc_t100_1_unsure_append_on_full_sheet_is_not_reported_as_not_written(full_sheet, client):
    full_sheet.fail("append", requests.exceptions.ConnectionError("đứt"), apply=True)
    result = add_new_article(client)
    assert not result.not_written  # Google đã thêm: không được báo «chưa ghi» (bấm lại là trùng)
    add_new_article(client)
    assert len(rows_with(full_sheet, NEW_KEYWORD)) <= 1


# ------------------------------------------------------------------------------- LC-T100-2


def ai_notes(text: str) -> propose.Proposal:
    fields = {name: "" for name in PlanSuggestion.model_fields}
    item = PlanSuggestion.model_validate(
        fields | {"action": "them", "keyword": NEW_KEYWORD, "notes": text, "reason": "Ghi chú."}
    )
    current = [PlanRow(key="B-001", keyword="bản lề cổng sắt bị xệ")]
    (proposal,) = propose.from_ai(PlanSuggestions(items=[item]), current, today=TODAY).items
    return proposal


MISSED_PRICES = [
    "Giá thay motor 1.200.000",
    "Giá: 500.000",
    "Đơn giá 1.200.000/m2",
    "Báo giá 2.500.000 cho cửa 3m",
    "Chi phí 800.000 một lần",
    "Phí khảo sát 200.000",
    "VNĐ 500.000",
    "VND 1.500.000",
]


@pytest.mark.xfail(strict=True, reason="LC-T100-2: cách viết giá thường gặp chưa được cảnh báo")
@pytest.mark.parametrize("text", MISSED_PRICES)
def test_lc_t100_2_common_price_writing_in_ai_notes_is_warned(text):
    proposal = ai_notes(text)
    assert propose.WARN_PRICE in proposal.warnings
    assert not proposal.preselected


@pytest.mark.parametrize(
    "text",
    ["Từ khóa có khoảng 10.000 lượt tìm mỗi tháng", "Xưởng làm từ năm 2009, có 3 thợ chính"],
)
def test_counts_with_thousand_dots_are_not_prices(text):
    """Cách sửa LC-T100-2 không được coi số đếm là giá (như SL-T100-2)."""
    assert propose.WARN_PRICE not in ai_notes(text).warnings


# ------------------------------------------------------------------------------- LC-T100-3


def call(func, *args, **kwargs):
    """Gọi ``func``; cách sửa LC-T100-3 thêm tham số ``sheet_id`` (như ``retry_pending``) thì
    truyền mã Sheet đang kết nối."""
    if "sheet_id" in inspect.signature(func).parameters:
        kwargs["sheet_id"] = SHEET_ID
    return func(*args, **kwargs)


@pytest.mark.xfail(strict=True, reason="LC-T100-3: ghi trạng thái vào Sheet khác Sheet của nháp")
def test_lc_t100_3_status_is_never_written_into_another_sheet(fake, client, tmp_path):
    sheet = FakePlanSheet(fake, [HEADER, row("B-001", "sửa cửa cuốn", status="Chưa viết")])
    store = DraftStore(path=tmp_path / "drafts.sqlite")
    draft_id = new_draft_id()
    copy_hash = sheet_hash("1" * 44)  # nháp mở từ Sheet bản sao (mã khác Sheet đang kết nối)
    assert copy_hash != sheet_hash(SHEET_ID)
    ref = DraftPlanRef(key="B-001", sheet_hash=copy_hash, status="Chưa viết", opened_at=NOW)
    write = sync.status_write(ref, model.STATUS_DRAFT_SENT, wp_post_id=501, now=NOW)
    result = call(sync.record_status, client, store, draft_id, write, now=NOW)
    assert sheet.updates == []
    assert result.outcome is not sync.WriteOutcome.WRITTEN
    assert store.load_plan_write(draft_id) == write  # việc giữ lại cho đúng Sheet của nó
