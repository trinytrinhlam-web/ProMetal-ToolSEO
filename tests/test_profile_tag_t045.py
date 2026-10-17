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
