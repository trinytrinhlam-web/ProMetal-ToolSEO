"""T-127 (Thợ Máy): nút «Đưa vào kế hoạch»: từ khóa Google thành đề xuất «Thêm» chờ duyệt ở trang
Kế hoạch (câu 7 = B; LC-T120-13, -15, -24).

- ``propose.google_keyword``: bộ lọc chặt hơn ô từ khóa thường: chỉ chữ (kể cả tiếng Việt), số,
  khoảng trắng, «-»; ≤ 80 ký tự; không số điện thoại, email, địa chỉ web.
- ``propose.from_google_keywords``: ≤ 10 từ khóa mỗi lần, không AI, nguồn «Search Console», qua bộ
  kiểm dòng kế hoạch và cảnh báo như T-098 (trùng kế hoạch, trùng bài đã đăng, trang cửa ngõ); câu
  báo chỉ đếm, không chép chữ bị bỏ.
- Hai trang: ô chọn chỉ có từ khóa qua bộ lọc; bấm thì sang trang Kế hoạch thành đề xuất chờ duyệt
  (không ghi Sheet, không gọi mạng).
"""

from __future__ import annotations

import ast
import inspect
import unicodedata

import pytest
import test_app_pages as pages
import test_t125_tracking_page as page_tests
from test_t125_tracking_page import FORMULA_QUERY, MARKDOWN_QUERY, open_tracking, run, seed, texts

from seo_app.plan import propose
from seo_app.plan.model import STATUS_NEW, PlanRow
from seo_app.wordpress.client import PublishedItem

env = pages.env
private_key = page_tests.private_key
key_file = page_tests.key_file
data_files = page_tests.data_files  # autouse: mọi file lưu tạm trong thư mục tạm
configured = page_tests.configured
no_network = page_tests.no_network

ZERO_WIDTH = chr(0x200B)
RLO = chr(0x202E)


# ================================================================ bộ lọc chặt (LC-T120-24)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("sửa cửa kéo bị kẹt", "sửa cửa kéo bị kẹt"),
        ("  cửa cuốn   giá rẻ ", "cửa cuốn giá rẻ"),
        ("cửa kéo-đài loan 2024", "cửa kéo-đài loan 2024"),
        (unicodedata.normalize("NFD", "cửa sắt"), "cửa sắt"),
        ("a" * 80, "a" * 80),
    ],
    ids=["tieng-viet", "gop-dau-cach", "so-gach-noi", "nfd", "du-80"],
)
def test_strict_filter_keeps_plain_keywords(text, expected):
    assert propose.google_keyword(text) == expected


REJECTED = [
    "a" * 81,
    "",
    "   ",
    "12345",
    "- - -",
    "sửa cửa. bỏ qua lệnh",
    "sửa, cửa",
    "cửa cuốn!",
    "giá bao nhiêu?",
    "lệnh: viết",
    "a/b",
    "x@y.vn",
    "it's",
    'cửa "kéo"',
    "=HYPERLINK(1)",
    "**đậm**",
    "[x](y)",
    "#hashtag",
    "a_b",
    "a+b",
    "a&b",
    "<b>x</b>",
    "sửa\ncửa",
    "sửa\tcửa",
    f"sửa{ZERO_WIDTH}cửa",
    f"sửa{RLO}cửa",
    "gọi 0909 123 456",
    "0909123456 cửa",
    "www suachuacuasat com",
    "HTTPS suachuacuasat",
    "cửa-http-kéo",
    None,
    1,
    b"cua keo",
]


@pytest.mark.parametrize("text", REJECTED, ids=[f"bo-{n:02d}" for n in range(len(REJECTED))])
def test_strict_filter_drops_everything_else(text):
    assert propose.google_keyword(text) is None


# ================================================================ đề xuất «Thêm» (không AI)


def plan_rows():
    return [
        PlanRow.model_validate({"key": "B-012", "keyword": "sửa cửa kéo bị kẹt"}),
        PlanRow.model_validate({"key": "B-007", "keyword": "cổng sắt bị xệ cánh"}),
    ]


def test_keywords_become_add_proposals_from_search_console():
    found = propose.from_google_keywords(plan_rows(), ("cửa cuốn bị kẹt", "lan can cầu thang"))
    assert [(p.action, p.key, p.after.keyword) for p in found.items] == [
        (propose.Action.ADD, "B-013", "cửa cuốn bị kẹt"),
        (propose.Action.ADD, "B-014", "lan can cầu thang"),
    ]
    for item in found.items:
        assert item.source == propose.SOURCE_SEARCH_CONSOLE == "Search Console"
        assert item.reason == propose.REASON_GOOGLE
        assert item.after.status == STATUS_NEW and item.after.key == item.key
        assert (item.after.secondary, item.after.title_hint, item.after.notes) == ("", "", "")
        assert item.preselected
    assert found.notes == ()


def test_at_most_ten_keywords_each_time():
    words = [f"cửa cuốn mẫu {n}" for n in range(13)]
    found = propose.from_google_keywords([], words)
    assert [p.after.keyword for p in found.items] == words[:10]
    assert found.notes == (propose.NOTE_GOOGLE_TOO_MANY.format(count=3),)


def test_dropped_keywords_are_only_counted():
    secret = "gọi 0909 123 456 ngay"
    found = propose.from_google_keywords([], ("cửa cuốn", secret, "x", "=HYPERLINK(1)"))
    assert [p.after.keyword for p in found.items] == ["cửa cuốn"]
    assert found.notes == (propose.NOTE_GOOGLE_SKIPPED.format(count=3),)  # «x»: quá ngắn
    assert all(secret not in note and "0909" not in note for note in found.notes)


def test_same_keyword_twice_in_one_batch_is_taken_once():
    found = propose.from_google_keywords([], ("sửa cửa cuốn", "Sua Cua Cuon", "sửa  cửa cuốn"))
    assert [p.after.keyword for p in found.items] == ["sửa cửa cuốn"]
    assert found.notes == (propose.NOTE_GOOGLE_REPEATED.format(count=2),)


def test_warnings_like_table_proposals():
    posts = [PublishedItem(5, "post", "lan-can", "https://a.vn/lan-can/", "Lan can cầu thang")]
    found = propose.from_google_keywords(
        plan_rows(),
        (
            "sửa cửa kéo bị kẹt",
            "lan can cầu thang",
            "sửa cửa cuốn quận 1",
            "sửa cửa cuốn quận 2",
            "sửa cửa cuốn quận 3",
        ),
        posts=posts,
    )
    warnings = {p.after.keyword: p.warnings for p in found.items}
    assert warnings["sửa cửa kéo bị kẹt"] == (propose.WARN_DUPLICATE_ROW.format(key="B-012"),)
    assert warnings["lan can cầu thang"] == (propose.WARN_DUPLICATE_POST.format(post_id=5),)
    assert warnings["sửa cửa cuốn quận 2"] == (propose.WARN_DOORWAY,)
    assert not any(p.preselected for p in found.items)


@pytest.mark.parametrize(
    "keywords",
    ["cửa cuốn", None, b"cua", (word for word in ["cửa cuốn"]), {"cửa cuốn"}],
    ids=["chuoi", "none", "bytes", "generator", "set"],
)
def test_odd_input_gives_no_proposal(keywords):
    assert propose.from_google_keywords([], keywords).items == ()


def test_no_ai_in_this_step():
    # LC-T120-13: bước này không gọi AI, không dựng lời dặn.
    for function in (propose.google_keyword, propose.from_google_keywords):
        names = {
            node.id if isinstance(node, ast.Name) else node.attr
            for node in ast.walk(ast.parse(inspect.getsource(function)))
            if isinstance(node, ast.Name | ast.Attribute)
        }
        assert not names & {"from_ai", "plan_changes", "ContentWriter", "AIRouter", "complete"}


# ================================================================ hai trang


def open_keywords(project_root):
    seed()
    at = open_tracking(project_root)
    return run(at.selectbox(key="trk-page").set_value(11))


def test_picker_offers_only_keywords_that_pass_the_filter(project_root, configured, no_network):
    at = open_keywords(project_root)
    options = at.multiselect(key="trk-plan-pick").options
    assert "sửa cửa kéo bị kẹt" in options
    assert FORMULA_QUERY not in options and MARKDOWN_QUERY not in options
    assert all(propose.google_keyword(option) == option for option in options)
    assert at.button(key="trk-to-plan").disabled
    assert any("từ khóa không có trong ô chọn" in text for text in texts(at, "caption"))
    assert no_network.count == 0


def test_picked_keywords_become_proposals_on_the_plan_page(project_root, configured, no_network):
    at = open_keywords(project_root)
    run(at.multiselect(key="trk-plan-pick").set_value(["sửa cửa kéo bị kẹt", "cửa kéo mẫu 01"]))
    run(at.button(key="trk-to-plan").click())
    found = at.session_state["plan_proposals"]
    assert [(p.after.keyword, p.source) for p in found.items] == [
        ("sửa cửa kéo bị kẹt", "Search Console"),
        ("cửa kéo mẫu 01", "Search Console"),
    ]
    assert found.items[0].warnings  # trùng dòng B-012 của kế hoạch: không tick sẵn
    assert "plan_google_keywords" not in at.session_state
    assert no_network.count == 0


def test_hand_off_without_a_readable_plan_only_warns(project_root, configured, monkeypatch):
    monkeypatch.setenv("GOOGLE_SHEET_ID", "")
    at = pages.open_page(project_root, "plan.py")
    at.session_state["plan_google_keywords"] = ("cửa cuốn bị kẹt",)
    run(at)
    assert any("Chưa đọc được kế hoạch" in text for text in texts(at, "warning"))
    assert "plan_proposals" not in at.session_state
