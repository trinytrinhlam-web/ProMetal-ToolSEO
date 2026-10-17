"""T-045: bộ lọc hồ sơ, 3 lỗi Thấp theo dõi sau T-043 (LC-T043-1, SL-T043-1, SL-T043-2).
Chỉ gọi ``confirmed_profile`` trên chuỗi, không gọi mạng."""

import pytest

from seo_app.content.rules import confirmed_profile
from tests.timing import assert_scales_linearly

# --- LC-T043-1: ý đã có nhãn, dòng nối thụt lề «  ## … [CẦN» không được tách ý ra -------------


@pytest.mark.parametrize("indent", [" ", "  ", "\t", "　"])
@pytest.mark.parametrize("half", ["[CẦN", "[CẦN XÁC", "(chưa", "[**CẦN", "["])
def test_lc_t043_1_tagged_item_keeps_indented_half_heading(indent, half):
    # Ca Lá Chắn: trước T-043 cả ý bị giấu, sau T-043 dòng «## …» và dòng sau nó tới AI.
    text = f"- giá [CẦN XÁC NHẬN]\n{indent}## ghi chú {half}\n{indent}BIMAT\n- ok"
    assert confirmed_profile(text) == "- ok"


def test_lc_t043_1_tag_split_over_earlier_lines():
    # Nhãn của ý nằm vắt hai dòng phía trước dòng tiêu đề thụt lề.
    text = "- giá [CẦN XÁC\n  NHẬN] lý do\n  ## ghi chú [CẦN\n  BIMAT\n- ok"
    assert confirmed_profile(text) == "- ok"


def test_lc_t043_1_paragraph_block_with_tag():
    # Đoạn văn thường (không gạch đầu dòng) có nhãn cũng là một khối.
    text = "Giá cổng [CẦN XÁC NHẬN]\n  ## ghi chú [CẦN\n  BIMAT\n\n- ok"
    assert confirmed_profile(text) == "- ok"


def test_lc_t043_1_several_indented_half_headings_in_tagged_item():
    text = (
        "- giá [CẦN XÁC NHẬN]\n  ## a [CẦN\n  BIMAT 1\n  ## b [CHƯA\n  BIMAT 2\n- ok\n## 8\n- B"
    )
    assert confirmed_profile(text) == "- ok\n## 8\n- B"


def test_lc_t043_1_untagged_item_still_split_like_t043():
    # Ý trước không có nhãn: giữ cách của SL-T032-5 (tiêu đề thụt lề có nửa nhãn chờ dòng kế,
    # ý trước được giữ).
    text = "- trước\n  ## 7 [CẦN XÁC\nNHẬN]\n- bí mật\n## 8\n- ok"
    assert confirmed_profile(text) == "- trước\n## 8\n- ok"


def test_lc_t043_1_untagged_item_half_heading_not_joined_kept():
    text = "- trước\n  ## 9 Giá [\n- ok\n## 10"
    assert confirmed_profile(text) == text


def test_lc_t043_1_tagged_item_then_indented_half_heading_completed():
    # Dòng tiêu đề thụt lề nối vào ý có nhãn; dòng kế hoàn thành nhãn của nó cũng nằm trong ý.
    text = "- giá [CẦN XÁC NHẬN]\n  ## 7 [CẦN XÁC\n  NHẬN]\n  BIMAT\n- ok"
    assert confirmed_profile(text) == "- ok"


def test_lc_t043_1_linear_on_long_tagged_item():
    # Ý có nhãn rất dài xen nhiều dòng «  ## … [CẦN»: kết quả «có nhãn» được nhớ, không dò lại
    # cả khối ở mỗi dòng.
    assert_scales_linearly(
        confirmed_profile,
        lambda k: "- x [CAN XAC NHAN]\n" + "  y\n  ## b [CAN\n" * 2500 * k,
        label="LC-T043-1",
    )


# --- SL-T043-2: nửa sau của nhãn nằm trên dòng trông như tiêu đề («## NHẬN]») -----------------


@pytest.mark.parametrize(
    ("first", "rest"),
    [
        ("## 7 [CẦN XÁC", "## NHẬN]"),
        ("## 7 [CẦN", "## XÁC NHẬN]"),
        ("## 7 [CẦN XÁC", "# NHẬN]"),  # cấp cao hơn cũng không kết thúc mục
        ("## 7 (chưa", "## xác nhận)"),
        ("## 7 [**CẦN XÁC", "## NHẬN**]"),
    ],
)
def test_sl_t043_2_rest_of_tag_on_heading_line_hides_section(first, rest):
    text = f"## 6\n- A\n{first}\n{rest}\n- BIMAT\n### 7.1\n- BIMAT 2\n## 8\n- B"
    assert confirmed_profile(text) == "## 6\n- A\n## 8\n- B"


def test_sl_t043_2_with_blank_lines_between_halves():
    text = "## 7 [CẦN XÁC\n\n## NHẬN]\n- BIMAT\n## 8\n- B"
    assert confirmed_profile(text) == "## 8\n- B"


def test_sl_t043_2_indented_half_heading_then_heading_rest():
    text = "- trước\n  ## 7 [CẦN XÁC\n## NHẬN]\n- BIMAT\n## 8\n- B"
    assert confirmed_profile(text) == "- trước\n## 8\n- B"


def test_sl_t043_2_next_heading_not_part_of_tag_still_kept():
    # Dòng kế là tiêu đề thường, không ghép thành nhãn: giữ cả hai tiêu đề như cũ.
    text = "## 7 [CẦN\n## 8\n- B"
    assert confirmed_profile(text) == text


# --- SL-T043-1: nhãn có từ 5 ký tự lạ trở lên ---------------------------------------------------

FIVE_PLUS_TAGS = [
    "[*****CẦN XÁC NHẬN]",
    "[❗❗❗ **CẦN XÁC NHẬN**]",
    "[🇻🇳🇻🇳🇻🇳 **CẦN XÁC NHẬN**]",
    "[⚠️👨‍👩‍👧‍👦 CẦN XÁC NHẬN]",
    "[CẦN ** ⚠️ ** XÁC ~~**~~ NHẬN]",
    "[" + "*" * 200 + "CẦN XÁC NHẬN]",
    "[CẦN" + " -" * 100 + " XÁC NHẬN]",
    "(«««« chưa ···· xác ···· nhận »»»»)",
    "[[[[CẦN XÁC NHẬN]]]]",
    "[(**CẦN XÁC NHẬN**)]",
    "[CẦN (XÁC NHẬN]",  # ngoặc mở giữa nhãn: vẫn nhận như T-043
    "[CẦN [** XÁC ** NHẬN]",
]


@pytest.mark.parametrize("tag", FIVE_PLUS_TAGS)
def test_sl_t043_1_many_symbols_inside_tag_hidden(tag):
    text = f"- công khai\n- bí mật {tag} lý do\n- ok"
    assert confirmed_profile(text) == "- công khai\n- ok"


@pytest.mark.parametrize(
    ("half", "rest"),
    [
        ("[❗❗❗ **CẦN", "XÁC NHẬN**]"),
        ("[" + "*" * 200 + "CẦN XÁC", "NHẬN]"),
        ("[" + "[(" * 300 + "**CHƯA", "XÁC NHẬN]"),
        ("[CẦN" + " ⚠️" * 100, "XÁC NHẬN]"),
        ("[CẦN (", "XÁC NHẬN]"),
        ("[🇻🇳🇻🇳🇻🇳", "CẦN XÁC NHẬN]"),
    ],
)
def test_sl_t043_1_heading_half_tag_with_many_symbols(half, rest):
    # Nửa nhãn dài hơn cửa sổ 64 ký tự trước khi thu dải ký tự lạ vẫn được nhận.
    text = f"## 6\n- A\n## 7 {half}\n{rest}\n- bí mật\n## 8\n- ok"
    assert confirmed_profile(text) == "## 6\n- A\n## 8\n- ok"


@pytest.mark.parametrize(
    "line",
    [
        "- khách cần xác nhận lịch trước khi thợ tới",
        "- [*] cần xác nhận lịch",
        "- [ ] cần xác nhận lịch",
        "- [] cần xác nhận lịch",
        "- (*) cần xác nhận lịch",
        "- (xem bảng) cần xác nhận",
        "- [1] cần xác nhận lịch",
        "- [CẦN XÁC 1 NHẬN]",
        "- [CẦN] xác nhận",
        "- (cần) xác nhận lịch",
        "- [CẦN *** ] XÁC NHẬN",
        "- [ghi chú ***** cần xác nhận]",
    ],
)
def test_sl_t043_1_plain_sentences_still_kept(line):
    assert confirmed_profile(line) == line


@pytest.mark.parametrize(
    "make",
    [
        lambda k: "- " + "[" * 50000 * k,
        lambda k: "- " + "(" * 50000 * k + "CAN XAC",
        lambda k: "- [" + "*" * 50000 * k + "CAN",
        lambda k: "- [CAN" + "*" * 50000 * k + "XAC",
        lambda k: "- [CAN" + "[" * 50000 * k,
        lambda k: "- [CAN XAC" + "(" * 50000 * k,
        lambda k: "- " + "[CAN[" * 10000 * k,
        lambda k: "- " + "[CAN*XAC*" * 6000 * k,
        lambda k: "- " + "[*(*" * 12000 * k,
        lambda k: "## " + "[ * ( " * 8000 * k + "\n- ok",
        lambda k: "## 7 [CAN" + "*" * 50000 * k + "\nXAC NHAN]\n- x",
        lambda k: ("## 7 [" + "*" * 100 + "CAN\nXAC NHAN]\n- x\n## 8\n") * 100 * k,
    ],
    ids=[
        "brackets",
        "parens-then-words",
        "stars-after-bracket",
        "stars-between-words",
        "brackets-between-words",
        "parens-after-xac",
        "repeated-can-bracket",
        "repeated-starred-words",
        "mixed-brackets-stars",
        "heading-mixed",
        "heading-long-half",
        "many-long-half-headings",
    ],
)
def test_sl_t043_1_unbounded_symbols_still_linear(make):
    assert_scales_linearly(confirmed_profile, make, label="SL-T043-1")
