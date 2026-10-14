"""Kho nháp bài đang soạn (T-016). Mọi test dùng thư mục tạm, không đụng ``data/`` thật."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from seo_app.content import OutlineItem, Research, Review
from seo_app.storage import (
    DEFAULT_DRAFTS_FILE,
    MAX_DRAFTS,
    DraftError,
    DraftPart,
    DraftSnapshot,
    DraftStore,
    new_draft_id,
)
from seo_app.storage import drafts as drafts_module


@pytest.fixture
def store(tmp_path: Path) -> DraftStore:
    return DraftStore(path=tmp_path / "data" / "drafts.sqlite")


def full_snapshot(**overrides) -> DraftSnapshot:
    data = dict(
        step=2,
        keyword="so sánh inox 201 và 304",
        material={
            "Kinh nghiệm của xưởng": "Khách gần biển ở Hội An làm cổng 201, 1–2 năm đã gỉ mối hàn.",
            "Số liệu của bạn": "",
            "Câu hỏi khách hay hỏi": "Inox 304 có bị gỉ không?",
        },
        research=Research(
            intent=["Chủ nhà muốn biết nên chọn loại nào cho cổng"],
            article_type="so sánh có bảng",
            competitors=[],
            new_angles=["Chi phí thật sau 5 năm"],
            questions=["Làm sao biết thợ dùng đúng 304?"],
        ),
        research_keyword="so sánh inox 201 và 304",
        outline_title="Inox 201 và 304: chọn loại nào cho cổng nhà [gần biển]",
        outline=[
            OutlineItem(heading="Khác nhau ở đâu?", points=["thành phần", "giá"], image=""),
            OutlineItem(heading="Ở gần biển", points=[], image="ảnh mối hàn bị gỉ"),
        ],
        article_title="Inox 201 và 304: chọn loại nào cho cổng nhà",
        parts=[
            DraftPart(heading="Mở bài", versions=["Bản một.", "Bản hai ngắn hơn."], current=1),
            DraftPart(
                heading="Khác nhau ở đâu?",
                versions=["Giá [cần bổ sung: giá 1 m²]: chênh khoảng…"],
                image="",
            ),
            DraftPart(
                heading="Ở gần biển",
                versions=["A", "B", "C"],
                current=0,
                image="ảnh mối hàn bị gỉ",
            ),
        ],
        review=Review.model_validate(
            {
                "scores": {
                    "friendly": 80,
                    "natural": 75,
                    "readable": 90,
                    "specific": 70,
                    "seo": 85,
                },
                "flags": [
                    {"section": 0, "sentence": "Bản hai.", "reason": "máy móc", "replacement": ""}
                ],
                "summary": "Ổn, cần thêm ví dụ.",
            }
        ),
        auto_fixed=3,
        ignored_flags={"Câu b.", "Câu a."},
    )
    data.update(overrides)
    return DraftSnapshot(**data)


# ----------------------------------------------------------------- lưu / đọc


def test_default_file_is_inside_ignored_data_folder():
    assert DEFAULT_DRAFTS_FILE.parent.name == "data"
    assert DEFAULT_DRAFTS_FILE.name == "drafts.sqlite"


def test_save_and_load_round_trip_keeps_everything(store):
    snap = full_snapshot()
    saved = store.save(snap)
    loaded = store.load(saved.id)

    assert loaded == saved
    assert loaded.saved_at is not None and loaded.saved_at.utcoffset() is not None
    assert loaded.saved_at.utcoffset().total_seconds() == 7 * 3600  # Asia/Ho_Chi_Minh
    assert loaded.material["Kinh nghiệm của xưởng"].startswith("Khách gần biển ở Hội An")
    assert [p.versions for p in loaded.parts] == [
        ["Bản một.", "Bản hai ngắn hơn."],
        ["Giá [cần bổ sung: giá 1 m²]: chênh khoảng…"],
        ["A", "B", "C"],
    ]
    assert [p.current for p in loaded.parts] == [1, 0, 0]
    assert loaded.parts[0].text == "Bản hai ngắn hơn."
    assert loaded.ignored_flags == ["Câu a.", "Câu b."]
    assert loaded.review == snap.review
    assert loaded.research == snap.research
    assert loaded.outline_title == "Inox 201 và 304: chọn loại nào cho cổng nhà [gần biển]"


def test_save_overwrites_same_id(store):
    first = store.save(full_snapshot(keyword="cửa sắt"))
    second = store.save(first.model_copy(update={"keyword": "cửa inox", "step": 3}))
    assert second.id == first.id
    listing = store.list_drafts()
    assert len(listing.drafts) == 1
    loaded = store.load(first.id)
    assert loaded.keyword == "cửa inox" and loaded.step == 3


def test_empty_snapshot_round_trip(store):
    saved = store.save(DraftSnapshot())
    assert store.load(saved.id) == saved
    assert saved.title == "Bài chưa đặt tên"


def test_load_missing_draft(store):
    with pytest.raises(DraftError, match="Không tìm thấy"):
        store.load(new_draft_id())


@pytest.mark.parametrize("bad", ["", "abc", "../../etc/passwd", "' OR 1=1 --", "A" * 32, 5])
def test_bad_ids_are_rejected(store, bad):
    with pytest.raises(DraftError, match="Mã nháp không hợp lệ"):
        store.load(bad)
    with pytest.raises(DraftError, match="Mã nháp không hợp lệ"):
        store.delete(bad)


def test_text_with_sql_and_quotes_is_stored_verbatim(store):
    nasty = '\'); DROP TABLE drafts; -- "x" 😀'
    saved = store.save(full_snapshot(keyword=nasty, article_title=nasty))
    assert store.load(saved.id).keyword == nasty
    assert store.list_drafts().drafts[0].title == nasty


def test_versions_cannot_carry_markdown_links(store):
    """File bị sửa tay chèn link vào thân bài: đọc ra vẫn bị escape (không thành link)."""
    saved = store.save(DraftSnapshot(parts=[DraftPart(heading="a", versions=["x"])]))
    with sqlite3.connect(store.path) as conn:
        data = json.loads(conn.execute("SELECT data FROM drafts").fetchone()[0])
        data["parts"][0]["versions"] = ["Bấm [vào đây](https://evil.example)"]
        conn.execute("UPDATE drafts SET data = ?", (json.dumps(data, ensure_ascii=False),))
    conn.close()
    text = store.load(saved.id).parts[0].text
    assert "](" not in text.replace("]\\(", "")


# ------------------------------------------------------------ liệt kê / xóa


def test_list_newest_first_with_title_keyword_time(store, monkeypatch):
    times = iter(datetime.fromisoformat(f"2026-10-14T0{h}:00:00+07:00") for h in (1, 2, 3))

    class FakeDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return next(times)

    monkeypatch.setattr(drafts_module, "datetime", FakeDatetime)
    a = store.save(DraftSnapshot(keyword="cửa cuốn"))
    b = store.save(DraftSnapshot(keyword="cổng inox", outline_title="Cổng inox đẹp"))
    c = store.save(DraftSnapshot(keyword="khóa cửa", article_title="Chọn khóa cửa"))

    listing = store.list_drafts()
    assert listing.skipped == 0
    assert [d.id for d in listing.drafts] == [c.id, b.id, a.id]
    assert [d.title for d in listing.drafts] == ["Chọn khóa cửa", "Cổng inox đẹp", "cửa cuốn"]
    assert [d.keyword for d in listing.drafts] == ["khóa cửa", "cổng inox", "cửa cuốn"]
    assert listing.drafts[0].saved_at.hour == 3
    assert store.list_drafts(limit=1).drafts[0].id == c.id


def test_delete(store):
    a = store.save(DraftSnapshot(keyword="a"))
    b = store.save(DraftSnapshot(keyword="b"))
    assert store.delete(a.id) is True
    assert store.delete(a.id) is False
    assert [d.id for d in store.list_drafts().drafts] == [b.id]
    with pytest.raises(DraftError):
        store.load(a.id)


def test_keeps_at_most_30_drafts_dropping_oldest(store):
    ids = [store.save(DraftSnapshot(keyword=f"từ khóa {i}")).id for i in range(MAX_DRAFTS + 5)]
    listing = store.list_drafts(limit=100)
    assert len(listing.drafts) == MAX_DRAFTS
    assert {d.id for d in listing.drafts} == set(ids[-MAX_DRAFTS:])
    with pytest.raises(DraftError, match="Không tìm thấy"):
        store.load(ids[0])
    with sqlite3.connect(store.path) as conn:
        assert conn.execute("SELECT count(*) FROM drafts").fetchone()[0] == MAX_DRAFTS
    conn.close()


def test_resaving_old_draft_moves_it_to_top_and_protects_it(tmp_path):
    store = DraftStore(path=tmp_path / "d.sqlite", max_drafts=3)
    first = store.save(DraftSnapshot(keyword="đầu"))
    store.save(DraftSnapshot(keyword="hai"))
    store.save(DraftSnapshot(keyword="ba"))
    store.save(first)  # sửa tiếp bài cũ nhất
    store.save(DraftSnapshot(keyword="bốn"))
    kws = [d.keyword for d in store.list_drafts().drafts]
    assert kws == ["bốn", "đầu", "ba"]


# ------------------------------------------------------ dữ liệu xấu / file hỏng


def test_corrupt_file_is_moved_aside_and_store_keeps_working(tmp_path):
    path = tmp_path / "drafts.sqlite"
    path.write_bytes(b"day khong phai file sqlite " * 100)
    store = DraftStore(path=path)

    assert store.list_drafts().drafts == []
    assert store.recovered_from is not None
    assert store.recovered_from.exists()
    assert store.recovered_from.read_bytes().startswith(b"day khong phai")
    saved = store.save(DraftSnapshot(keyword="mới"))
    assert store.load(saved.id).keyword == "mới"


def test_sqlite_with_wrong_drafts_table_is_moved_aside(tmp_path):
    path = tmp_path / "drafts.sqlite"
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE drafts (x TEXT)")
    conn.close()
    store = DraftStore(path=path)
    store.save(DraftSnapshot())
    assert store.recovered_from is not None


def test_healthy_file_is_not_moved(store):
    store.save(DraftSnapshot())
    again = DraftStore(path=store.path)
    assert len(again.list_drafts().drafts) == 1
    assert again.recovered_from is None


def _put_raw(store: DraftStore, draft_id: str, data, saved_at="2026-10-14T08:00:00+07:00"):
    store.list_drafts()  # tạo bảng
    with sqlite3.connect(store.path) as conn:
        conn.execute(
            "INSERT INTO drafts VALUES (?, ?, ?, ?, ?, ?)",
            (draft_id, "t", "k", saved_at, 1.0, data),
        )
    conn.close()


@pytest.mark.parametrize(
    "data",
    [
        "không phải json",
        "{}",  # thiếu gì cũng có mặc định, nhưng id không khớp
        json.dumps({"step": 99}),
        json.dumps({"api_key": "sk-ant-giả"}),  # trường lạ bị chặn
        json.dumps({"parts": [{"heading": "a", "versions": ["x"], "current": 5}]}),
        json.dumps({"parts": [{"heading": "a", "versions": []}]}),
        json.dumps({"schema_version": 999}),
        json.dumps({"saved_at": "2026-10-14T08:00:00"}),  # thiếu múi giờ
        b"\xff\xfe\x00",
    ],
)
def test_wrong_shape_draft_gives_friendly_error(store, data):
    draft_id = new_draft_id()
    if isinstance(data, str) and data.startswith("{") and data != "{}":
        obj = json.loads(data)
        obj.setdefault("id", draft_id)
        data = json.dumps(obj)
    _put_raw(store, draft_id, data)
    with pytest.raises(DraftError, match="bị hỏng|quá lớn") as info:
        store.load(draft_id)
    assert "sk-ant" not in str(info.value)  # không chép dữ liệu ra thông báo


def test_bad_rows_are_skipped_in_listing(store):
    good = store.save(DraftSnapshot(keyword="tốt"))
    _put_raw(store, "khong-phai-ma", "{}")
    _put_raw(store, new_draft_id(), "{}", saved_at="không phải ngày")
    _put_raw(store, new_draft_id(), "{}", saved_at="2026-10-14T08:00:00")  # thiếu múi giờ
    listing = store.list_drafts()
    assert [d.id for d in listing.drafts] == [good.id]
    assert listing.skipped == 3


def test_too_large_draft_is_not_saved(tmp_path):
    store = DraftStore(path=tmp_path / "d.sqlite", max_bytes=10_000)
    big = DraftSnapshot(parts=[DraftPart(heading="a", versions=["chữ " * 5000])])
    with pytest.raises(DraftError, match="quá lớn"):
        store.save(big)
    assert store.list_drafts().drafts == []


def test_too_large_draft_in_file_is_not_loaded(tmp_path):
    store = DraftStore(path=tmp_path / "d.sqlite", max_bytes=10_000)
    draft_id = new_draft_id()
    _put_raw(store, draft_id, json.dumps({"id": draft_id, "keyword": "x" * 20_000}))
    with pytest.raises(DraftError, match="quá lớn"):
        store.load(draft_id)


def test_save_revalidates_fields_changed_without_validation(store):
    snap = DraftSnapshot().model_copy(update={"step": 42})
    with pytest.raises(DraftError, match="sai khuôn"):
        store.save(snap)


def test_snapshot_rejects_unknown_fields_and_bad_parts():
    with pytest.raises(ValidationError):
        DraftSnapshot(password="bí mật")
    with pytest.raises(ValidationError):
        DraftPart(heading="a", versions=["x"], current=1)
    with pytest.raises(ValidationError):
        DraftSnapshot(id="khong-hop-le")


def test_unwritable_location_gives_friendly_error(tmp_path):
    blocker = tmp_path / "file-thuong"
    blocker.write_text("x", encoding="utf-8")
    store = DraftStore(path=blocker / "drafts.sqlite")  # thư mục cha là một file
    with pytest.raises(DraftError, match="file nháp"):
        store.save(DraftSnapshot())


def test_storage_module_does_not_use_pickle_or_string_sql():
    source = Path(drafts_module.__file__).read_text(encoding="utf-8")
    assert "import pickle" not in source and "pickle." not in source
    assert "execute(f" not in source and ".format(" not in source


# ------------------------------------------- T-021: lọc lại chữ AI khi đọc nháp


EVIL = (
    "Xem [bấm đây](https://evil.example/x) ![](https://track.example/p.gif) "
    "<img src=x onerror=alert(1)><script>alert(1)</script>"
)


def _live_link(text: str) -> bool:
    from seo_app.sanitize import escape_link_syntax

    return escape_link_syntax(text) != text


def _assert_disarmed(text: str, where: str) -> None:
    assert not _live_link(text), f"{where}: còn link Markdown"
    low = text.lower()
    assert "<script" not in low and "onerror" not in low and "<img" not in low, where


def _plant_everywhere(store: DraftStore) -> str:
    saved = store.save(full_snapshot())
    with sqlite3.connect(store.path) as conn:
        data = json.loads(conn.execute("SELECT data FROM drafts").fetchone()[0])
        r = data["research"]
        r["intent"] = [EVIL]
        r["article_type"] = EVIL
        r["new_angles"] = [EVIL]
        r["questions"] = [EVIL]
        r["competitors"] = [
            {"title": EVIL, "url": "javascript:alert(1)", "covers": EVIL, "missing": EVIL}
        ]
        data["review"]["summary"] = EVIL
        data["review"]["flags"][0].update(reason=EVIL, replacement=EVIL)
        data["outline_title"] = EVIL
        data["outline"][0].update(heading=EVIL, points=[EVIL], image=EVIL)
        data["article_title"] = EVIL
        data["parts"][0].update(heading=EVIL, versions=[EVIL, EVIL], image=EVIL)
        conn.execute("UPDATE drafts SET data = ?", (json.dumps(data, ensure_ascii=False),))
    conn.close()
    return saved.id


def test_loaded_ai_text_is_cleaned_in_every_field(store):
    """Lá Chắn T-016-020 #1: mọi trường chữ AI đọc từ file đều qua lại clean_*."""
    snap = store.load(_plant_everywhere(store))
    r, rv = snap.research, snap.review
    escaped_fields = {
        "research.intent": r.intent[0],
        "research.article_type": r.article_type,
        "research.new_angles": r.new_angles[0],
        "research.questions": r.questions[0],
        "research.covers": r.competitors[0].covers,
        "research.missing": r.competitors[0].missing,
        "review.summary": rv.summary,
        "review.reason": rv.flags[0].reason,
        "review.replacement": rv.flags[0].replacement,
        "outline.points": snap.outline[0].points[0],
        "outline.image": snap.outline[0].image,
        "article_title": snap.article_title,
        "parts.heading": snap.parts[0].heading,
        "parts.image": snap.parts[0].image,
        "parts.versions[0]": snap.parts[0].versions[0],
        "parts.versions[1]": snap.parts[0].versions[1],
    }
    for where, text in escaped_fields.items():
        _assert_disarmed(text, where)
    # Tên bài đối thủ chỉ bỏ thẻ (giao diện hiện qua markdown_link); địa chỉ lạ bị bỏ.
    assert "<script" not in r.competitors[0].title.lower()
    assert r.competitors[0].url == ""
    # Dàn ý lưu ở dạng ô sửa (chưa escape): link đã bị gỡ hẳn, không chỉ escape.
    for where, text in {
        "outline_title": snap.outline_title,
        "outline.heading": snap.outline[0].heading,
    }.items():
        assert "evil.example" not in text and "track.example" not in text, where
        assert "<script" not in text.lower(), where


def test_clean_draft_is_unchanged_by_many_save_load_cycles(store):
    """Bản đúng (đã sạch như khi AI vừa trả về) không đổi gì sau 5 vòng lưu/mở."""
    from seo_app.sanitize import escape_link_syntax

    snap = full_snapshot(
        outline_title="Cửa [A] (dày 1mm): chọn sao?",
        parts=[
            DraftPart(
                heading="Giá [cần bổ sung: giá 1 m²]",
                versions=[
                    escape_link_syntax("Đoạn có `code` và [chữ](ngoặc) — thật."),
                    "Dòng 1\n\n- ý a\n- ý b",
                ],
                current=1,
                image="ảnh mối hàn",
            )
        ],
    )
    first = store.load(store.save(snap).id)
    current = first
    for _ in range(5):
        current = store.load(store.save(current).id)
    assert current.model_dump(exclude={"saved_at"}) == first.model_dump(exclude={"saved_at"})
    assert first.model_dump(exclude={"saved_at"}) == store.save(snap).model_dump(
        exclude={"saved_at"}
    )


def test_loaded_research_keyword_is_cleaned(store):
    """Lá Chắn T-016-020 #4: research_keyword hiện trong st.warning nên phải được lọc lại."""
    saved = store.save(full_snapshot())
    with sqlite3.connect(store.path) as conn:
        data = json.loads(conn.execute("SELECT data FROM drafts").fetchone()[0])
        data["research_keyword"] = EVIL + "\r\ndòng hai"
        conn.execute("UPDATE drafts SET data = ?", (json.dumps(data, ensure_ascii=False),))
    conn.close()
    loaded = store.load(saved.id)
    _assert_disarmed(loaded.research_keyword, "research_keyword")
    assert "\n" not in loaded.research_keyword and "\r" not in loaded.research_keyword
    # Từ khóa bình thường giữ nguyên, để cảnh báo «kết quả của từ khóa khác» không hiện oan.
    assert store.load(store.save(full_snapshot()).id).research_keyword == "so sánh inox 201 và 304"


def test_loaded_keyword_is_one_line(store):
    """Soi Lỗi R9-1: từ khóa trong nháp bị cài dòng trống được gộp về một dòng khi mở."""
    saved = store.save(full_snapshot())
    with sqlite3.connect(store.path) as conn:
        data = json.loads(conn.execute("SELECT data FROM drafts").fetchone()[0])
        data["keyword"] = "cửa\r\n\r\n[bấm](https://evil.example)\t  sắt\x0b x"
        conn.execute("UPDATE drafts SET data = ?", (json.dumps(data, ensure_ascii=False),))
    conn.close()
    assert store.load(saved.id).keyword == "cửa [bấm](https://evil.example) sắt x"
    assert store.load(store.save(full_snapshot()).id).keyword == "so sánh inox 201 và 304"
