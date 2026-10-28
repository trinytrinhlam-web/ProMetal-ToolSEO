"""T-098: khuôn một dòng kế hoạch (``PlanRow``) và bộ làm sạch chung (LC-T094-18, -21).

Không gọi mạng, không gọi AI.
"""

from datetime import UTC, date, datetime, timedelta

import pytest
from pydantic import ValidationError

from seo_app.onpage.links import ArticleKind
from seo_app.plan import model
from seo_app.plan.model import PlanRow

# Ký tự điều khiển, vô hình, đảo hướng chữ, surrogate lẻ, ký tự riêng, chưa gán.
ODD = "\u0000\u0007\u001b\u007f\u0085\u200b\u200d\u2060\ufeff\u202a\u202b\u202c\u202d\u202e"
ODD += "\u2066\u2067\u2068\u2069\u00ad\ue000\U000e0001\u034f\ufe0f"


@pytest.mark.parametrize("multiline", [False, True])
def test_clean_text_removes_control_invisible_and_bidi_characters(multiline):
    text = model.clean_text(f" Cửa{ODD} cuốn\u202e\u2066 Q7 ", multiline=multiline)
    assert text == "Cửa cuốn Q7"
    assert not any(ch in text for ch in ODD)


def test_clean_text_is_nfc_and_collapses_spaces():
    text = model.clean_text("Của  \t sắt 　x")
    assert text == "Của sắt x"


def test_clean_text_multiline_keeps_line_breaks_and_one_blank_line():
    text = model.clean_text("  Ray  mòn \r\n\r\n\n\rKhách hay hỏi \n", multiline=True)
    assert text == "Ray mòn\n\nKhách hay hỏi"


def test_clean_text_non_string_is_empty():
    assert model.clean_text(None) == model.clean_text(12) == ""


def test_plan_row_cleans_every_text_field():
    row = PlanRow(
        keyword=f"cửa cuốn\u202e{ODD} «quận 7»",
        secondary=f"ray{ODD} lá cửa",
        title_hint="Sửa\u200b cửa",
        notes=f"Ray mòn{ODD}\n\nKhách hỏi giá",
    )
    assert row.keyword == "cửa cuốn ‹quận 7›"
    assert row.secondary == "ray lá cửa"
    assert row.title_hint == "Sửa cửa"
    assert row.notes == "Ray mòn\n\nKhách hỏi giá"


def test_plan_row_is_strict_extra_fields_and_frozen():
    with pytest.raises(ValidationError):
        PlanRow(keyword="cửa cuốn", url="https://evil.example")
    row = PlanRow(keyword="cửa cuốn")
    with pytest.raises(ValidationError):
        row.keyword = "khác"  # type: ignore[misc]


@pytest.mark.parametrize("keyword", ["", " ", "x", "\u200b\u200bx", "a" * 121, None, 123])
def test_plan_row_rejects_bad_keyword(keyword):
    with pytest.raises(ValidationError):
        PlanRow(keyword=keyword)


@pytest.mark.parametrize(
    ("field", "limit"),
    [("secondary", model.SECONDARY_MAX), ("title_hint", model.TITLE_MAX), ("notes", 2000)],
)
def test_plan_row_rejects_too_long_text_instead_of_cutting(field, limit):
    PlanRow(keyword="cửa cuốn", **{field: "a" * limit})
    with pytest.raises(ValidationError):
        PlanRow(keyword="cửa cuốn", **{field: "a" * (limit + 1)})


@pytest.mark.parametrize(
    ("raw", "expected"), [("b-1", "B-1"), (" kv-00012 ", "KV-00012"), ("", ""), ("B-024", "B-024")]
)
def test_key_format(raw, expected):
    assert PlanRow(key=raw, keyword="cửa cuốn").key == expected


@pytest.mark.parametrize("raw", ["B001", "ABCD-1", "B-123456", "B-1\nC-2", "B-1;", "Б-1"])
def test_key_rejects_other_formats(raw):
    with pytest.raises(ValidationError):
        PlanRow(key=raw, keyword="cửa cuốn")


@pytest.mark.parametrize(
    ("field", "raw", "expected"),
    [
        ("intent", "tim hieu", "Tìm hiểu"),
        ("intent", "SO SÁNH TRƯỚC KHI MUA", "So sánh trước khi mua"),
        ("intent", "transactional", "Mua hàng"),
        ("kind", "service page", "Dịch vụ"),
        ("kind", "Khu vực", "Khu vực"),
        ("priority", "high", "Cao"),
        ("priority", "trung binh", "Trung bình"),
        ("status", "", "Chưa viết"),
        ("status", "Đã đăng", "Đã đăng"),
        ("status", "huy", "Bỏ"),
    ],
)
def test_labels_accept_variants(field, raw, expected):
    assert getattr(PlanRow(keyword="cửa cuốn", **{field: raw}), field) == expected


@pytest.mark.parametrize(
    ("field", "raw"),
    [("intent", "Local service"), ("kind", "Landing"), ("priority", "Rất cao"), ("status", "Sẵn")],
)
def test_labels_reject_unknown(field, raw):
    with pytest.raises(ValidationError):
        PlanRow(keyword="cửa cuốn", **{field: raw})


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("20/11/2026", date(2026, 11, 20)),
        ("5/1/2027", date(2027, 1, 5)),
        ("20-11-2026", date(2026, 11, 20)),
        ("20.11.2026", date(2026, 11, 20)),
        ("2026-11-20", date(2026, 11, 20)),
        ("46346", date(2026, 11, 20)),  # số ngày kiểu Google Sheets
        (46346, date(2026, 11, 20)),
        (46346.0, date(2026, 11, 20)),
        (date(2026, 11, 20), date(2026, 11, 20)),
        ("", None),
        (None, None),
    ],
)
def test_dates(raw, expected):
    assert model.parse_plan_date(raw) == expected


@pytest.mark.parametrize(
    "raw",
    [
        "11/25/2026",  # kiểu Mỹ mm/dd: không nhận
        "31/02/2026",
        "15/10",  # thiếu năm
        "2019-12-31",
        "01/01/2036",
        "1000",  # số ngày nhỏ: năm 1902
        "99999",
        True,
        46346.5,
        datetime(2026, 11, 20, 8, 0),
        "20/11/2026 08:00",
        "ngày mai",
    ],
)
def test_dates_rejected(raw):
    with pytest.raises(ValueError):
        model.parse_plan_date(raw)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("8:00", "08:00"), ("08:30", "08:30"), ("8h", "08:00"), ("8h30", "08:30"), ("8 giờ", "08:00")],
)
def test_times(raw, expected):
    assert model.parse_plan_time(raw) == expected


@pytest.mark.parametrize("raw", ["25:00", "8:61", "sáng", "8", "08:00:00"])
def test_times_rejected(raw):
    with pytest.raises(ValueError):
        model.parse_plan_time(raw)


def test_datetimes_always_have_timezone():
    vn = model.parse_plan_datetime("20/11/2026 08:00")
    assert vn.tzinfo is not None and vn.utcoffset() == timedelta(hours=7)
    iso = model.parse_plan_datetime("2026-11-20T01:00:00+00:00")
    assert iso == vn
    naive = model.parse_plan_datetime("2026-11-20T08:00:00")
    assert naive == vn
    assert model.parse_plan_datetime(datetime(2026, 11, 20, 1, tzinfo=UTC)) == vn
    with pytest.raises(ValueError):
        model.parse_plan_datetime("2040-01-01T00:00:00+07:00")
    row = PlanRow(keyword="cửa cuốn", updated_at="20/11/2026 08:00")
    assert row.updated_at.utcoffset() == timedelta(hours=7)


@pytest.mark.parametrize("field", ["target_id", "wp_post_id"])
def test_post_ids_are_strict_positive_ints(field):
    assert getattr(PlanRow(keyword="cửa cuốn", **{field: 12}), field) == 12
    for bad in (0, -1, "12", True, 12.0, model.MAX_POST_ID + 1):
        with pytest.raises(ValidationError):
            PlanRow(keyword="cửa cuốn", **{field: bad})


def test_slug_must_be_plain_and_make_slug_converts():
    assert PlanRow(keyword="cửa cuốn", slug="sua-cua-cuon").slug == "sua-cua-cuon"
    for bad in ("Sửa cửa", "sua_cua", "/sua-cua/", "sua--cua", "https://x.vn/a"):
        with pytest.raises(ValidationError):
            PlanRow(keyword="cửa cuốn", slug=bad)
    assert model.make_slug("Sửa cửa cuốn Q7!") == "sua-cua-cuon-q7"


def test_round_trip_through_json_keeps_row():
    row = PlanRow(
        key="B-001",
        keyword="sửa cửa cuốn quận 7",
        planned_date="20/11/2026",
        planned_time="8h",
        status="Đã hẹn giờ",
        wp_post_id=12,
        published_at="20/11/2026 08:00",
    )
    assert PlanRow.model_validate_json(row.model_dump_json()) == row


def test_next_key():
    assert model.next_key([]) == "B-001"
    assert model.next_key(["B-001", "B-024", "KV-99", "x"]) == "B-025"
    assert model.next_key(["B-1000"]) == "B-1001"
    with pytest.raises(ValueError):
        model.next_key(["B-99999"])


def test_article_kind_mapping():
    assert model.article_kind("Dịch vụ") is ArticleKind.SERVICE
    assert model.article_kind("Hướng dẫn") is ArticleKind.GUIDE
    assert model.article_kind("Khu vực") is ArticleKind.AREA
    assert model.article_kind("Cập nhật bài cũ") is None
    assert model.article_kind("") is None


def test_sheet_columns_match_plan_row_fields():
    assert [name for name, _ in model.SHEET_COLUMNS] == list(PlanRow.model_fields)
    assert model.SHEET_TAB == "KeHoach"


# ------------------------------------------------- dữ liệu cá nhân của khách (A3, LC-T094-21)


@pytest.mark.parametrize(
    ("text", "phones", "emails"),
    [
        ("Gọi anh Ba 0909 123 456 khi tới", 1, 0),
        ("Số +84 909 123 456 hay 84909123456", 2, 0),
        ("Bàn: 028.3812.3456", 1, 0),
        ("Gửi a.b@khach.vn hoặc x+y@mail.com.vn", 0, 2),
        ("0909\u200b123\u200b456", 1, 0),  # ký tự vô hình chen giữa không che được số
        ("Ngày 20/11/2026, cổng 2024 x 3000", 0, 0),
        ("Cửa rộng 3200 mm, cao 2400", 0, 0),
    ],
)
def test_personal_info_counts(text, phones, emails):
    assert model.personal_info(text) == (phones, emails)


def test_mask_personal_info():
    masked = model.mask_personal_info("Anh Ba 0909.123.456, mail ba@khach.vn.\nNhà 12 Lê Lợi")
    assert masked == f"Anh Ba {model.MASK}, mail {model.MASK}.\nNhà 12 Lê Lợi"
    assert model.personal_info(masked) == (0, 0)
