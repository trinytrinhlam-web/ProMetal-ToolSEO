"""T-098: đọc kế hoạch từ file CSV/TSV/TXT/MD và chữ dán (thiết kế T-094 mục 1.2; LC-T094-18).

Không gọi mạng, không gọi AI.
"""

from datetime import UTC, date, datetime

import pytest

from seo_app.plan import model, parse
from seo_app.plan.parse import PlanSourceError, read_file, read_paste
from seo_app.storage.site_index import SiteIndex
from seo_app.wordpress.client import PublishedItem

SITE = "https://suachuacuasat.com"
INDEX = SiteIndex(
    site=SITE,
    fetched_at=datetime(2026, 10, 28, tzinfo=UTC),
    items=(
        PublishedItem(id=12, type="page", slug="sua-cua-cuon", link=f"{SITE}/sua-cua-cuon/",
                      title="Sửa cửa cuốn"),
        PublishedItem(id=30, type="post", slug="cua-sat-bi-xe", link=f"{SITE}/cua-sat-bi-xe/",
                      title="Cửa sắt bị xệ: nguyên nhân"),
    ),
)  # fmt: skip
MARK = "MOI_CHU_TRONG_O"  # chữ mồi: không được xuất hiện trong câu báo

HEADER = "Mã bài,Từ khóa chính,Ý định,Ưu tiên,Ngày dự kiến,Trạng thái,Slug,Ghi chú của thợ"


def csv_bytes(*lines: str, header: str = HEADER, bom: bool = True) -> bytes:
    text = "\n".join([header, *lines]) + "\n"
    return text.encode("utf-8-sig" if bom else "utf-8")


def all_warnings(result) -> str:
    return " ".join(result.warnings)


# ------------------------------------------------------------------------------ CSV


def test_csv_reads_columns_by_name_with_bom():
    data = csv_bytes(
        "B-001,sửa cửa cuốn quận 7,Mua hàng,Cao,20/11/2026,Chưa viết,Sửa cửa cuốn Q7,"
        '"Ray hay mòn\nKhách hay hỏi giá"',
        ",cửa sắt bị xệ,tim hieu,high,2026-12-01,,,",
    )
    result = read_file(data, "ke-hoach.csv")
    assert result.is_table and result.skipped == 0 and not result.warnings
    first, second = result.rows
    assert first.key == "B-001" and first.keyword == "sửa cửa cuốn quận 7"
    assert first.intent == "Mua hàng" and first.priority == "Cao"
    assert first.planned_date == date(2026, 11, 20) and first.status == "Chưa viết"
    assert first.slug == "sua-cua-cuon-q7"
    assert first.notes == "Ray hay mòn\nKhách hay hỏi giá"
    assert second.key == "" and second.intent == "Tìm hiểu" and second.priority == "Cao"


def test_csv_column_order_synonyms_and_unknown_columns():
    data = csv_bytes(
        "Q7,sửa cửa cuốn,8h30,20/11/2026,Local",
        header="Quận,Từ khóa,Giờ đăng,Ngày,Độ khó",
    )
    (row,) = read_file(data, "a.csv").rows
    assert row.keyword == "sửa cửa cuốn" and row.planned_time == "08:30"
    assert row.planned_date == date(2026, 11, 20)


@pytest.mark.parametrize("delimiter", [";", "\t"])
def test_csv_semicolon_or_tab_delimiter(delimiter):
    header = delimiter.join(["Từ khóa chính", "Ưu tiên"])
    data = csv_bytes(delimiter.join(["cổng inox 304", "Thấp"]), header=header, bom=False)
    (row,) = read_file(data, "A.CSV").rows
    assert (row.keyword, row.priority) == ("cổng inox 304", "Thấp")


def test_tsv_file():
    data = "Từ khóa chính\tNgày dự kiến\nlan can cầu thang\t46346\n".encode()
    (row,) = read_file(data, "kh.tsv").rows
    assert row.planned_date == date(2026, 11, 20)


def test_date_time_in_one_cell_and_time_column_wins():
    data = csv_bytes(
        "cổng inox,20/11/2026 08:30,",
        "lan can sắt,21/11/2026 08:30,14:00",
        header="Từ khóa chính,Ngày giờ đăng,Giờ đăng",
    )
    first, second = read_file(data, "a.csv").rows
    assert (first.planned_date, first.planned_time) == (date(2026, 11, 20), "08:30")
    assert second.planned_time == "14:00"


def test_bad_cells_are_left_empty_and_reported_by_row_without_cell_text():
    data = csv_bytes(
        f"B-1,cửa cuốn,{MARK},Rất {MARK},11/25/2026,{MARK},,",
        f"X{MARK},cửa sắt,,,15/10,,,",
    )
    result = read_file(data, "a.csv")
    first, second = result.rows
    assert first.intent == first.priority == "" and first.planned_date is None
    assert first.status == model.STATUS_NEW
    assert second.key == "" and second.planned_date is None
    text = all_warnings(result)
    assert "«Ý định»" in text and "«Ưu tiên»" in text and "«Ngày dự kiến»" in text
    assert "«Mã bài»" in text and "dòng 2" in text and "dòng 3" in text
    assert MARK not in text


def test_rows_without_keyword_or_with_bad_keyword_are_skipped():
    data = csv_bytes(
        "B-1,,Mua hàng,,,,,",
        f"B-2,{'a' * 121},,,,,,",
        "B-3,x,,,,,,",
        "B-4,cửa cuốn,,,,,,",
    )
    result = read_file(data, "a.csv")
    assert [row.key for row in result.rows] == ["B-4"]
    assert result.skipped == 3
    assert "không có từ khóa chính" in all_warnings(result)


def test_duplicate_key_skips_later_row():
    data = csv_bytes("B-1,cửa cuốn,,,,,,", "b-1,cửa sắt,,,,,,")
    result = read_file(data, "a.csv")
    assert [row.keyword for row in result.rows] == ["cửa cuốn"]
    assert result.skipped == 1 and "Mã bài trùng" in all_warnings(result)


def test_duplicate_header_reads_first_column_only():
    data = csv_bytes("cửa cuốn,cửa sắt", header="Từ khóa chính,Từ khóa")
    result = read_file(data, "a.csv")
    assert result.rows[0].keyword == "cửa cuốn"
    assert "chỉ đọc cột đầu tiên" in all_warnings(result)


def test_control_bidi_and_invisible_characters_are_removed():
    data = csv_bytes("B-1,cửa\u202e cuốn\u0000\u200b,Mua\u2066 hàng,Cao,,,,ghi\u202d chú")
    (row,) = read_file(data, "a.csv").rows
    assert (row.keyword, row.intent, row.notes) == ("cửa cuốn", "Mua hàng", "ghi chú")


def test_csv_without_keyword_column_is_free_text():
    data = "Tháng,Số bài\nT10,20\n".encode()
    result = read_file(data, "a.csv")
    assert not result.is_table and result.free_text == "Tháng,Số bài\nT10,20"


# ------------------------------------------------------------------- trang dịch vụ đích


def test_target_link_on_site_becomes_post_id_never_an_address():
    data = csv_bytes(
        f"cửa cuốn,{SITE}/sua-cua-cuon/",
        f"cửa sắt,{SITE}/cua-sat-bi-xe",
        "lan can,30",
        header="Từ khóa chính,Trang dịch vụ đích",
    )
    rows = read_file(data, "a.csv", index=INDEX).rows
    assert [row.target_id for row in rows] == [12, 30, 30]
    assert all("http" not in row.model_dump_json() for row in rows)


@pytest.mark.parametrize(
    "target",
    [
        "https://evil.example/sua-cua-cuon/",
        "http://suachuacuasat.com/sua-cua-cuon/",
        "https://user@suachuacuasat.com/sua-cua-cuon/",
        "https://suachuacuasat.com.evil.example/sua-cua-cuon/",
        f"{SITE}/bai-chua-dang/",
        "99",
        "javascript:alert(1)",
    ],
)
def test_target_outside_published_list_is_dropped(target):
    data = csv_bytes(f"cửa cuốn,{target}", header="Từ khóa chính,Trang dịch vụ đích")
    result = read_file(data, "a.csv", index=INDEX)
    assert result.rows[0].target_id is None
    assert "Trang dịch vụ đích" in all_warnings(result)


def test_target_without_site_index_is_dropped():
    data = csv_bytes(f"cửa cuốn,{SITE}/sua-cua-cuon/", header="Từ khóa chính,Trang dịch vụ đích")
    assert read_file(data, "a.csv").rows[0].target_id is None


def test_app_columns_are_read_for_sheet_rows():
    data = csv_bytes(
        "B-1,cửa cuốn,Đã hẹn giờ,321,20/11/2026 08:00,2026-11-19T10:00:00+07:00",
        header="Mã bài,Từ khóa chính,Trạng thái,Mã bài WordPress,Ngày đăng thực tế,Cập nhật lúc",
    )
    (row,) = read_file(data, "a.csv").rows
    assert row.wp_post_id == 321 and row.status == "Đã hẹn giờ"
    assert row.published_at.utcoffset().total_seconds() == 7 * 3600
    assert row.updated_at.isoformat() == "2026-11-19T10:00:00+07:00"


# ------------------------------------------------------------------------- giới hạn


def test_file_size_checked_in_bytes_before_decoding():
    # File quá 1 MB mà còn không phải UTF-8: phải báo «lớn quá» (kiểm trước khi giải mã).
    data = b"\xff" * (model.MAX_FILE_BYTES + 1)
    with pytest.raises(PlanSourceError) as raised:
        read_file(data, "a.csv")
    assert str(raised.value) == parse.FILE_TOO_BIG


def test_two_megabyte_file_rejected():
    data = csv_bytes(*(["cửa cuốn quận 7"] * 120_000), header="Từ khóa chính")
    assert len(data) > 2_000_000
    with pytest.raises(PlanSourceError, match="lớn quá"):
        read_file(data, "a.csv")


def test_one_thousand_rows_ok_one_more_rejected():
    rows = [f"cửa cuốn {i}" for i in range(model.MAX_ROWS)]
    assert len(read_file(csv_bytes(*rows, header="Từ khóa chính"), "a.csv").rows) == 1000
    with pytest.raises(PlanSourceError) as raised:
        read_file(csv_bytes(*rows, "thêm một", header="Từ khóa chính"), "a.csv")
    assert str(raised.value) == parse.TOO_MANY_ROWS


def test_too_many_columns_rejected_but_trailing_empty_cells_ignored():
    header = ",".join(["Từ khóa chính", *(f"c{i}" for i in range(25))])
    assert read_file(csv_bytes("cửa cuốn" + "," * 40, header=header), "a.csv").rows
    wide = header + ",c26"
    with pytest.raises(PlanSourceError) as raised:
        read_file(csv_bytes("cửa cuốn", header=wide), "a.csv")
    assert str(raised.value) == parse.TOO_MANY_COLUMNS


def test_long_cell_is_cut_and_reported():
    data = csv_bytes(f"cửa cuốn,{'x' * 5000}", header="Từ khóa chính,Ghi chú của thợ")
    result = read_file(data, "a.csv")
    assert len(result.rows[0].notes) == model.MAX_CELL_CHARS
    assert "dài quá 2,000 ký tự" in all_warnings(result)


def test_huge_cell_beyond_csv_limit_is_a_fixed_error():
    data = csv_bytes(f'cửa cuốn,"{"x" * 200_000}"', header="Từ khóa chính,Ghi chú")
    with pytest.raises(PlanSourceError) as raised:
        read_file(data, "a.csv")
    assert str(raised.value) == parse.BAD_TABLE


@pytest.mark.parametrize(
    "data",
    [
        "Từ khóa chính\ncửa sắt\n".encode("cp1258", errors="replace").replace(b"?", b"\xe0"),
        "Từ khóa chính\ncửa sắt\n".encode("utf-16"),
        b"Tu khoa\n\xc3\x28\n",
    ],
)
def test_only_utf8_no_guessing(data):
    with pytest.raises(PlanSourceError) as raised:
        read_file(data, "a.csv")
    assert str(raised.value) == parse.FILE_BAD_ENCODING


@pytest.mark.parametrize("name", ["a.xlsx", "a.xls", "a.docx", "a.pdf", "a.exe", "a", "a.csv.exe"])
def test_only_text_extensions(name):
    with pytest.raises(PlanSourceError) as raised:
        read_file(b"Tu khoa\ncua\n", name)
    assert str(raised.value) == parse.FILE_BAD_TYPE


def test_empty_inputs():
    for data in (b"", b"\n\n  \n", "\ufeff".encode()):
        with pytest.raises(PlanSourceError):
            read_file(data, "a.csv")
    with pytest.raises(PlanSourceError):
        read_paste("   \n ")


def test_free_text_file_over_paste_limit_rejected():
    data = ("Ghi chú định hướng. " * 1_200).encode()
    assert len(data.decode()) > model.MAX_PASTE_CHARS
    with pytest.raises(PlanSourceError) as raised:
        read_file(data, "ghi-chu.txt")
    assert str(raised.value) == parse.TEXT_TOO_LONG


# ------------------------------------------------------------------------- chữ dán


def test_paste_from_excel_is_a_table():
    text = (
        "Từ khóa chính\tƯu tiên\tNgày dự kiến\r\ncửa cuốn\tCao\t20/11/2026\r\ncửa sắt\tThấp\t\r\n"
    )
    result = read_paste(text)
    assert [row.keyword for row in result.rows] == ["cửa cuốn", "cửa sắt"]


def test_paste_markdown_table_like_owner_plan():
    text = (
        "## Tháng 1\n"
        "| Quận | Từ khóa chính | Search Intent | Độ khó |\n"
        "|------|---------------|---------------|--------|\n"
        "| Q1 | sửa cua quận 1 | Local service | Cao |\n"
        "| Q3 | sửa cua quận 3 | Local service | Cao |\n"
    )
    result = read_paste(text)
    assert [row.keyword for row in result.rows] == ["sửa cua quận 1", "sửa cua quận 3"]
    assert all(row.intent == "" for row in result.rows)
    assert "«Ý định»" in all_warnings(result) and parse.OUTSIDE_TABLE not in result.warnings


def test_paste_markdown_table_with_prose_reports_prose_not_read():
    text = "Ưu tiên quận 7 trước.\n\n| Từ khóa |\n|---|\n| cửa cuốn quận 7 |\n"
    result = read_paste(text)
    assert result.rows[0].keyword == "cửa cuốn quận 7"
    assert parse.OUTSIDE_TABLE in result.warnings


def test_paste_free_text_goes_to_ai():
    text = 'Tháng 10–11: tập trung cổng inox.\n- Đẩy "lan can" lên ưu tiên cao\u202e\n'
    result = read_paste(text)
    assert not result.is_table and not result.rows
    assert result.free_text == 'Tháng 10–11: tập trung cổng inox.\n- Đẩy "lan can" lên ưu tiên cao'


def test_paste_tab_text_without_keyword_column_is_free_text():
    result = read_paste("Tháng\tSố bài\nT10\t20\nT11\t20\n")
    assert not result.is_table


def test_paste_limit():
    read_paste("a" * model.MAX_PASTE_CHARS)
    with pytest.raises(PlanSourceError) as raised:
        read_paste("a" * (model.MAX_PASTE_CHARS + 1))
    assert str(raised.value) == parse.PASTE_TOO_LONG


def test_warnings_are_grouped_and_capped():
    rows = [f"cửa cuốn {i},{MARK}" for i in range(40)]
    result = read_file(csv_bytes(*rows, header="Từ khóa chính,Ưu tiên"), "a.csv")
    (warning,) = result.warnings
    assert "40 dòng" in warning and "dòng 2, 3, 4, 5, 6, …" in warning
    assert MARK not in warning
