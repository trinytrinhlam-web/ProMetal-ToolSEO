"""T-100: kho nháp gắn với kế hoạch (khuôn 3), ``SendState`` mở rộng, việc ghi Sheet còn nợ.

Điều kiện Lá Chắn LC-T094-30: ``DraftSnapshot.plan``, ``SendState`` mở rộng, tăng phiên bản cấu
trúc, nháp cũ vẫn mở; giữ so-rồi-đặt của T-089; việc ghi Sheet còn nợ lưu trong ``drafts.sqlite``.
Không gọi Google, WordPress.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError
from test_drafts_images import read_row, real_image, snapshot_with, write_row

from seo_app.plan import model
from seo_app.storage.drafts import (
    MAX_PLAN_WRITE_BYTES,
    MAX_PLAN_WRITES,
    SCHEMA_VERSION,
    DraftError,
    DraftPlanRef,
    DraftSnapshot,
    DraftStore,
    PlanStatusWrite,
    SendState,
    new_draft_id,
)
from seo_app.storage.plan_cache import sheet_hash

NOW = datetime(2026, 10, 29, 9, 30, tzinfo=model.TIMEZONE)
HASH = sheet_hash("1AbCdEfGhIjKlMnOpQrStUvWxYz0123456789_-xyz")


@pytest.fixture
def store(tmp_path) -> DraftStore:
    return DraftStore(path=tmp_path / "drafts.sqlite")


def ref(**changes) -> DraftPlanRef:
    data = {"key": "B-001", "sheet_hash": HASH, "status": "Chưa viết", "opened_at": NOW}
    return DraftPlanRef(**{**data, **changes})


def write(**changes) -> PlanStatusWrite:
    data = {
        "key": "B-001",
        "sheet_hash": HASH,
        "status": model.STATUS_DRAFT_SENT,
        "wp_post_id": 501,
        "expect_status": "Đang viết",
        "created_at": NOW,
    }
    return PlanStatusWrite(**{**data, **changes})


# ======================================================================== khuôn nháp


def test_schema_3_round_trip_with_plan_and_images(store):
    snap = snapshot_with(real_image()).model_copy(update={"plan": ref()})
    saved = store.save(snap)
    loaded = store.load(saved.id)
    assert SCHEMA_VERSION == 3 and loaded.schema_version == 3
    assert loaded.plan == ref() and loaded.parts[1].chosen_image == real_image()
    assert json.loads(read_row(store, saved.id))["plan"]["key"] == "B-001"


def test_v2_draft_keeps_its_image_and_has_no_plan(store):
    """Nháp khuôn 2 như ``main`` trước T-100 lưu (có ảnh, không có ``plan``): mở được, ảnh giữ
    nguyên, không ảnh nào tính là hỏng; lưu lại thành khuôn 3."""
    saved = store.save(snapshot_with(real_image()))
    data = json.loads(read_row(store, saved.id))
    data["schema_version"] = 2
    del data["plan"]
    write_row(store, saved.id, data)
    loaded = store.load(saved.id)
    assert loaded.plan is None and loaded.dropped_images == 0
    assert loaded.parts[1].chosen_image == real_image()
    store.save(loaded)
    assert json.loads(read_row(store, saved.id))["schema_version"] == 3


def _kept(old: object, new: object) -> bool:
    """Mọi khóa, giá trị của ``old`` còn nguyên trong ``new`` (``new`` được có thêm khóa mới)."""
    if isinstance(old, dict):
        return isinstance(new, dict) and all(k in new and _kept(v, new[k]) for k, v in old.items())
    if isinstance(old, list):
        return isinstance(new, list) and len(old) == len(new) and all(map(_kept, old, new))
    return old == new


@pytest.mark.parametrize("version", [1, 2])
def test_old_draft_on_users_machine_opens_and_resaves_as_v3(tmp_path, version):
    """Chỉ Huy duyệt A 28/10, điều kiện 3: file nháp tạo trước T-100 (chưa có bảng ``plan_writes``),
    nháp khuôn 1 hay 2 (khuôn 2 có ảnh đã chọn) đã gửi nháp (có trạng thái gửi): mở được, giữ ảnh,
    giữ trạng thái gửi; lưu lại thì lên khuôn 3 mà mọi trường cũ còn nguyên."""
    path = tmp_path / "drafts.sqlite"
    store = DraftStore(path=path)
    image = real_image() if version == 2 else None
    saved = store.save(snapshot_with(image))
    sent = SendState(pending=False, post_id=501, updated_at="2026-10-26T10:00:00+07:00")
    store.save_send_state(saved.id, sent)
    data = json.loads(read_row(store, saved.id))
    data["schema_version"] = version
    del data["plan"]
    if version == 1:  # khuôn 1: chưa có ảnh đã chọn, chưa có phần SEO
        del data["seo"]
        for part in data["parts"]:
            part.pop("chosen_image")
    write_row(store, saved.id, data)
    with closing(sqlite3.connect(path)) as conn, conn:
        conn.execute("DROP TABLE plan_writes")

    store = DraftStore(path=path)  # app mới mở lại file cũ
    loaded = store.load(saved.id)
    assert store.recovered_from is None and loaded.dropped_images == 0 and loaded.plan is None
    assert loaded.parts[1].chosen_image == image
    assert store.load_send_state(saved.id) == sent
    store.save(loaded)
    stored = json.loads(read_row(store, saved.id))
    assert stored["schema_version"] == 3
    old = {key: value for key, value in data.items() if key not in ("schema_version", "saved_at")}
    assert _kept(old, stored)
    assert store.load_send_state(saved.id) == sent
    assert store.load(saved.id).parts[1].chosen_image == image


def test_v1_draft_still_drops_only_image_data(store):
    saved = store.save(snapshot_with(real_image()))
    data = json.loads(read_row(store, saved.id))
    data["schema_version"] = 1
    del data["plan"]
    write_row(store, saved.id, data)
    loaded = store.load(saved.id)
    assert loaded.dropped_images == 1 and loaded.parts[1].chosen_image is None


@pytest.mark.parametrize(
    "plan",
    [
        {"key": "b-1", "sheet_hash": HASH, "status": "Chưa viết", "opened_at": NOW.isoformat()},
        {"key": "B-001", "sheet_hash": "1AbCdEf", "status": "Chưa viết",
         "opened_at": NOW.isoformat()},
        {"key": "B-001", "sheet_hash": HASH, "status": "Xong", "opened_at": NOW.isoformat()},
        {"key": "B-001", "sheet_hash": HASH, "status": "Chưa viết",
         "opened_at": "2026-10-29T09:30:00"},
        {"key": "B-001", "sheet_hash": HASH, "status": "Chưa viết", "opened_at": NOW.isoformat(),
         "wp_post_id": "5"},
        {"key": "B-001", "sheet_hash": HASH, "status": "Chưa viết", "opened_at": NOW.isoformat(),
         "link": "https://evil.example"},
        "B-001",
    ],
)  # fmt: skip
def test_broken_plan_in_file_is_dropped_and_draft_opens(store, plan):
    saved = store.save(snapshot_with(real_image()))
    data = json.loads(read_row(store, saved.id))
    data["plan"] = plan
    write_row(store, saved.id, data)
    loaded = store.load(saved.id)
    assert loaded.plan is None and loaded.keyword == "sửa cổng inox"
    assert loaded.parts[1].chosen_image == real_image()


def test_plan_ref_built_in_code_must_be_valid():
    with pytest.raises(ValidationError):
        DraftSnapshot(plan={"key": "B-001", "sheet_hash": HASH, "status": "x", "opened_at": NOW})
    with pytest.raises(ValidationError):
        ref(key="B-0001")  # không phải dạng chuẩn


def test_unknown_newer_version_is_rejected(store):
    saved = store.save(DraftSnapshot(keyword="a"))
    data = json.loads(read_row(store, saved.id))
    data["schema_version"] = 4
    write_row(store, saved.id, data)
    with pytest.raises(DraftError):
        store.load(saved.id)


# ======================================================================== SendState mở rộng


def test_old_send_state_row_reads_with_defaults(store):
    snap = store.save(DraftSnapshot())
    old = {"pending": False, "post_id": 501, "updated_at": "2026-10-26T10:00:00+07:00"}
    with closing(sqlite3.connect(store.path)) as conn, conn:
        conn.execute("INSERT INTO send_states (id, data) VALUES (?, ?)", (snap.id, json.dumps(old)))
    state = store.load_send_state(snap.id)
    assert (state.mode, state.scheduled_for, state.released, state.release_unknown) == (
        "draft", None, False, False
    )  # fmt: skip


def test_new_send_state_fields_round_trip(store):
    snap = store.save(DraftSnapshot())
    when = datetime(2026, 11, 3, 1, 0, tzinfo=UTC)
    state = SendState.now(pending=False, post_id=501, mode="future", scheduled_for=when,
                          released=True)  # fmt: skip
    store.save_send_state(snap.id, state)
    assert store.load_send_state(snap.id) == state


@pytest.mark.parametrize(
    "fields",
    [
        {"mode": "future"},  # thiếu giờ hẹn
        {"mode": "draft", "scheduled_for": "2026-11-03T08:00:00+07:00"},
        {"mode": "publish", "scheduled_for": "2026-11-03T08:00:00+07:00"},
        {"mode": "draft", "released": True, "post_id": 5},
        {"mode": "publish", "released": True},  # không có mã bài
        {"mode": "publish", "released": True, "release_unknown": True, "post_id": 5},
        {"mode": "PUBLISH"},
        {"mode": 1},
        {"released": "true"},
        {"mode": "future", "scheduled_for": "2026-11-03T08:00:00"},  # thiếu múi giờ
    ],
)
def test_inconsistent_send_state_in_file_is_an_error(store, fields):
    snap = store.save(DraftSnapshot())
    data = {"pending": False, "updated_at": "2026-10-26T10:00:00+07:00", **fields}
    with closing(sqlite3.connect(store.path)) as conn, conn:
        conn.execute(
            "INSERT INTO send_states (id, data) VALUES (?, ?)", (snap.id, json.dumps(data))
        )
    with pytest.raises(DraftError):
        store.load_send_state(snap.id)


def test_compare_and_set_sees_new_fields(store):
    """So rồi đặt của T-089 vẫn so cả trường mới: tab khác vừa ghi «đã hẹn giờ» thì lần ghi đang
    cầm bản «nháp» không qua."""
    snap = store.save(DraftSnapshot())
    seen = SendState.now(pending=False, post_id=501)
    store.save_send_state(snap.id, seen)
    other = seen.model_copy(update={"mode": "publish", "released": True})
    store.save_send_state(snap.id, other)
    claim = SendState.now(pending=True, post_id=501)
    assert not store.save_send_state(snap.id, claim, expected=(seen, False))
    assert store.save_send_state(snap.id, claim, expected=(other, False))


# ======================================================================== việc ghi Sheet còn nợ


def test_plan_write_round_trip_list_and_delete(store):
    first, second = new_draft_id(), new_draft_id()
    assert store.load_plan_write(first) is None
    store.save_plan_write(first, write())
    store.save_plan_write(second, write(key="B-002"))
    assert store.load_plan_write(first) == write()
    assert [(draft_id, item.key) for draft_id, item in store.list_plan_writes()] == [
        (first, "B-001"), (second, "B-002")
    ]  # fmt: skip
    store.save_plan_write(first, None)
    assert [item.key for _, item in store.list_plan_writes()] == ["B-002"]


def test_plan_write_compare_and_delete(store):
    draft_id = new_draft_id()
    old, newer = write(), write(status=model.STATUS_SCHEDULED, published_at=NOW)
    store.save_plan_write(draft_id, newer)
    assert not store.save_plan_write(draft_id, None, expected=old)
    assert store.load_plan_write(draft_id) == newer
    assert store.save_plan_write(draft_id, None, expected=newer)
    assert store.load_plan_write(draft_id) is None


def test_deleting_or_pruning_a_draft_keeps_its_pending_write(tmp_path):
    store = DraftStore(path=tmp_path / "drafts.sqlite", max_drafts=2)
    snap = store.save(DraftSnapshot(keyword="đã gửi"))
    store.save_plan_write(snap.id, write())
    store.delete(snap.id)
    for _ in range(3):
        store.save(DraftSnapshot(keyword="nháp khác"))
    assert store.load_plan_write(snap.id) == write()


@pytest.mark.parametrize(
    "data",
    [
        "không phải json",
        json.dumps({"key": "B-001"}),
        json.dumps({**json.loads(write().model_dump_json()), "status": "Bỏ"}),
        json.dumps({**json.loads(write().model_dump_json()), "wp_post_id": "501"}),
        json.dumps({**json.loads(write().model_dump_json()), "extra": "x"}),
        "x" * (MAX_PLAN_WRITE_BYTES + 1),
    ],
)
def test_broken_plan_write_is_an_error_and_skipped_in_list(store, data):
    good, bad = new_draft_id(), new_draft_id()
    store.save_plan_write(good, write())
    store.save_plan_write(bad, write())
    with closing(sqlite3.connect(store.path)) as conn, conn:
        conn.execute("UPDATE plan_writes SET data = ? WHERE id = ?", (data, bad))
    with pytest.raises(DraftError):
        store.load_plan_write(bad)
    assert [draft_id for draft_id, _ in store.list_plan_writes()] == [good]
    assert not store.save_plan_write(bad, None, expected=write())  # hỏng: không xóa mù


def test_plan_writes_are_capped(store):
    ids = [new_draft_id() for _ in range(MAX_PLAN_WRITES + 3)]
    for draft_id in ids:
        store.save_plan_write(draft_id, write())
    kept = [draft_id for draft_id, _ in store.list_plan_writes()]
    assert len(kept) == MAX_PLAN_WRITES and kept[-1] == ids[-1]


@pytest.mark.parametrize(
    "fields",
    [
        {"status": model.STATUS_WRITING},  # «Đang viết» không có mã bài WordPress
        {"wp_post_id": None},  # gửi xong phải có mã bài
        {"status": model.STATUS_DROPPED},
        {"status": model.STATUS_NEW},
        {"expect_status": "Xong"},
        {"created_at": datetime(2026, 10, 29, 9, 30)},
        {"key": "B-1"},
    ],
)
def test_plan_write_shape_is_strict(fields):
    with pytest.raises(ValidationError):
        write(**fields)


def test_old_draft_file_gets_plan_writes_table(tmp_path):
    path = tmp_path / "drafts.sqlite"
    snap = DraftStore(path=path).save(DraftSnapshot(keyword="nháp cũ"))
    with closing(sqlite3.connect(path)) as conn, conn:
        conn.execute("DROP TABLE plan_writes")
    store = DraftStore(path=path)
    assert store.load(snap.id).keyword == "nháp cũ" and store.recovered_from is None
    store.save_plan_write(snap.id, write())
    assert store.load_plan_write(snap.id) == write()


# ======================================================================== tìm nháp theo dòng


def test_find_plan_draft_returns_newest_matching_draft(store):
    older = store.save(DraftSnapshot(keyword="a", plan=ref()))
    newer = store.save(DraftSnapshot(keyword="b", plan=ref()))
    store.save(DraftSnapshot(keyword="c", plan=ref(key="B-002")))
    assert store.find_plan_draft("B-001", HASH) == newer.id
    store.delete(newer.id)
    assert store.find_plan_draft("B-001", HASH) == older.id
    assert store.find_plan_draft("B-001", sheet_hash("khac")) is None
    assert store.find_plan_draft("B-003", HASH) is None


def test_find_plan_draft_ignores_text_that_looks_like_a_plan(store):
    text = f'"key":"B-001" "sheet_hash":"{HASH}"'
    store.save(DraftSnapshot(keyword="a", material={"Ghi chú": text}))
    assert store.find_plan_draft("B-001", HASH) is None


def test_find_plan_draft_skips_draft_with_broken_plan(store):
    saved = store.save(DraftSnapshot(keyword="a", plan=ref()))
    data = json.loads(read_row(store, saved.id))
    data["plan"]["status"] = "Xong"
    write_row(store, saved.id, data)
    assert store.find_plan_draft("B-001", HASH) is None
