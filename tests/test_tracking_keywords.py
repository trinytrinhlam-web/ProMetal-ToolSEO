"""T-123 (Thợ Máy): từ khóa của một bài (``seo_app.tracking.keywords``; thiết kế T-120 mục 1.7).

Gộp cách gõ có dấu, không dấu bằng ``fold_key``; từ khóa chính; từ khóa mới; từ khóa là chữ người
lạ gõ: làm sạch lại, cắt 200 ký tự, chỉ là chữ thuần (LC-T120-11).
"""

from __future__ import annotations

import math
import unicodedata
from datetime import date

import pytest
from test_tracking_model import SITE, Query, query_row

from seo_app.tracking.keywords import (
    DEFAULT_ROWS,
    HIDDEN_QUERIES_NOTE,
    MAX_QUERY_CHARS,
    has_keyword,
    keyword_key,
    keyword_table,
    page_queries,
    query_text,
)
from seo_app.tracking.match import page_key
from seo_app.tracking.model import KeywordTable, PageStats
from seo_app.tracking.periods import Period, last_days, previous_period

E = date(2026, 10, 31)
NOW = last_days(E, 28)
BEFORE = previous_period(NOW)


def test_variants_with_and_without_accents_are_grouped():
    rows = [
        query_row(NOW, "/a/", "sửa cửa sắt", 5, 50, 4.0),
        query_row(NOW, "/a/", "sua cua sat", 3, 70, 6.0),
        query_row(NOW, "/a/", "Sửa  cửa sắt", 1, 10, 2.0),  # hai dấu cách: làm sạch thành một
        query_row(NOW, "/a/", "Sửa cửa sắt", 1, 5, 2.0),  # cùng chữ sau khi làm sạch: cộng vào
        query_row(NOW, "/a/", "cửa cuốn", 2, 20, 3.0),
    ]
    table = keyword_table(rows)
    first, second = table.groups
    assert first.key == "sua cua sat"
    assert first.current == PageStats(10, 135, 200.0 + 420.0 + 20.0 + 10.0)
    assert first.current.position == pytest.approx(650.0 / 135)  # trung bình theo lượt hiển thị
    assert first.text == "sua cua sat"  # cách gõ nhiều lượt hiển thị nhất
    assert [(v.text, v.stats.impressions) for v in first.variants] == [
        ("sua cua sat", 70),
        ("sửa cửa sắt", 50),
        ("Sửa cửa sắt", 15),
    ]
    assert second.text == "cửa cuốn" and len(second.variants) == 1
    assert table.skipped == 0 and not table.has_previous
    assert not first.is_new and first.previous is None and first.rank_gain is None


def test_sorted_by_clicks_then_impressions():
    rows = [
        query_row(NOW, "/a/", "b", 1, 100),
        query_row(NOW, "/a/", "a", 1, 200),
        query_row(NOW, "/a/", "c", 5, 10),
    ]
    assert [group.text for group in keyword_table(rows).groups] == ["c", "a", "b"]
    assert DEFAULT_ROWS == 50
    assert "Google ẩn từ khóa hiếm" in HIDDEN_QUERIES_NOTE


def test_main_keyword_and_new_keywords():
    current = [
        query_row(NOW, "/a/", "sua cua sat", 3, 30, 5.0),
        query_row(NOW, "/a/", "cửa sắt giá rẻ", 1, 20, 8.0),
    ]
    previous = [query_row(BEFORE, "/a/", "Sửa cửa sắt", 1, 40, 9.0)]
    table = keyword_table(current, previous, main_keyword="Sửa cửa sắt")
    main, other = table.groups
    assert main.is_main and not main.is_new
    assert main.previous == PageStats(1, 40, 360.0)
    assert main.rank_gain == pytest.approx(4.0)  # 9 → 5: lên 4 bậc
    assert not other.is_main and other.is_new and other.previous is None
    assert table.has_previous
    assert has_keyword(table, "sửa cửa sắt") is True
    assert has_keyword(table, "SUA-CUA-SAT") is True
    assert has_keyword(table, "cửa cuốn") is False
    assert has_keyword(table, "门窗") is None  # không có chữ Latin, chữ số để so


def test_previous_not_fetched_means_no_new_flag():
    table = keyword_table([query_row(NOW, "/a/", "cửa cuốn", 1, 10)], None)
    assert not table.groups[0].is_new and not table.has_previous


def test_non_latin_queries_are_not_merged():
    rows = [query_row(NOW, "/a/", "门窗", 1, 10), query_row(NOW, "/a/", "ドア", 1, 10)]
    table = keyword_table(rows, main_keyword="门窗")
    assert sorted(group.text for group in table.groups) == ["ドア", "门窗"]
    assert {keyword_key("门窗"), keyword_key("ドア")} == {"=门窗", "=ドア"}
    assert not any(group.is_main for group in table.groups)  # fold_key rỗng: không gắn «chính»


@pytest.mark.parametrize(
    "bad",
    [
        Query(
            NOW.start,
            NOW.end,
            SITE + "/a/",
            "\N{ZERO WIDTH SPACE}\N{RIGHT-TO-LEFT OVERRIDE}\N{LEFT-TO-RIGHT ISOLATE}",
            1,
            10,
            10.0,
        ),  # toàn ký tự vô hình
        Query(NOW.start, NOW.end, SITE + "/a/", "   ", 1, 10, 10.0),
        Query(NOW.start, NOW.end, SITE + "/a/", "x" * 2049, 1, 10, 10.0),
        Query(NOW.start, NOW.end, SITE + "/a/", None, 1, 10, 10.0),
        Query(NOW.start, NOW.end, SITE + "/a/", "a", True, 10, 10.0),
        Query(NOW.start, NOW.end, SITE + "/a/", "a", 1, 10, math.nan),
        Query(NOW.start, NOW.end, SITE + "/a/", "a", 11, 10, 10.0),
        Query(NOW.start, NOW.end, SITE + "/a/", "a", 0, 10, 0.0),
    ],
)
def test_bad_query_rows_are_skipped(bad):
    table = keyword_table([bad, query_row(NOW, "/a/", "b", 1, 10)])
    assert [group.text for group in table.groups] == ["b"]
    assert table.skipped == 1


def test_query_text_cleans_and_cuts():
    hostile = (
        "c\N{RIGHT-TO-LEFT OVERRIDE}ửa\N{ZERO WIDTH SPACE} <b>sắt</b>\n[link](https://evil.example)"
    )
    text = query_text(hostile)
    assert text == "cửa <b>sắt</b> [link](https://evil.example)"  # chữ thuần: giao diện tự escape
    assert not any(unicodedata.category(ch) in ("Cc", "Cf") for ch in text)
    assert len(query_text("đ" * 2048)) == MAX_QUERY_CHARS
    assert query_text("x" * 2049) == ""
    assert query_text(42) == ""


def test_page_queries_filter_page_and_range():
    other_period = Period(date(2026, 9, 1), date(2026, 9, 28))
    rows = [
        query_row(NOW, "/a/", "q1", 1, 10),
        query_row(NOW, "/a/#muc-2", "q2", 1, 10),  # cùng trang (chỉ khác «#…»)
        query_row(NOW, "/a", "q3", 1, 10),  # cùng trang (thiếu «/» cuối)
        query_row(NOW, "/b/", "q4", 1, 10),  # trang khác
        query_row(other_period, "/a/", "q5", 1, 10),  # khoảng khác
        Query(NOW.start, NOW.end, "https://www.staging-m.suachuacuasat.com/a/", "q6", 1, 10, 10.0),
        Query(NOW.start, NOW.end, None, "q7", 1, 10, 10.0),
    ]
    found = page_queries(rows, site=SITE, key=page_key(SITE + "/a/", SITE), period=NOW)
    assert [row.query for row in found] == ["q1", "q2", "q3"]


def test_empty_table():
    assert keyword_table([]) == KeywordTable((), 0, False)
