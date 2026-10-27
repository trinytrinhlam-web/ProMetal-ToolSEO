"""Lá Chắn T-040: test của LC-T040-1 (Thấp). Đã sửa ở T-041 (Thợ Máy), dấu ``xfail`` đã gỡ; test
giữ lại để canh.

Lời dặn meta mới (T-040) cho AI giữ nguyên từ khóa có chữ về giá («giá sửa cửa sắt»), «phần chữ
còn lại vẫn không có con số, mức giá hay chữ nào về giá». Bộ kiểm (``mentions_price``, có từ
T-036) bỏ từ khóa ra khỏi câu rồi mới dò giá, nên chỗ nói giá **vắt qua mép** từ khóa (từ khóa
kết thúc bằng «giá», «chi phí» hay chữ số, AI viết tiếp «tốt», «thấp», «triệu») mất theo từ
khóa và gợi ý được nhận. Giá đầy đủ nằm ngoài từ khóa thì vẫn bị bắt (test canh ở cuối file).
Sửa ở T-041 (Thợ Máy, ``seo_app/onpage/meta.py``).

Không gọi AI, không gọi mạng: chỉ gọi bộ kiểm và dựng lời dặn.
"""

import pytest

from seo_app.content import prompts
from seo_app.content.models import Section
from seo_app.content.rules import load_rules
from seo_app.onpage.meta import accept_ai_title, mentions_price

BANNED = load_rules().banned

# (từ khóa, title AI gợi ý): chỗ nói giá dùng chung một chữ với cuối từ khóa.
EDGE_PRICE = [
    ("làm cổng sắt báo giá", "Làm cổng sắt báo giá tốt: cần chuẩn bị những gì?"),
    ("làm cổng sắt báo giá", "Làm cổng sắt báo giá hợp lý: cần chuẩn bị những gì?"),
    ("sửa cửa cuốn chi phí", "Sửa cửa cuốn chi phí thấp: khi nào nên thay mô tơ?"),
    ("sửa cua quận 1", "Sửa cua quận 1 triệu: thợ đến tận nơi kiểm tra cửa"),
]
# Giá đầy đủ nằm ngoài từ khóa: hôm nay đã bị bỏ, phải giữ như vậy.
OUTSIDE_PRICE = [
    ("giá sửa cửa sắt", "Giá sửa cửa sắt rẻ: những gì quyết định số tiền bạn trả"),
    ("giá sửa cửa sắt", "Giá sửa cửa sắt từ 200.000đ: những gì quyết định"),
    ("sửa cua quận 1", "Sửa cua quận 1 chỉ 500k: thợ đến tận nơi kiểm tra cửa"),
    ("bảng giá cửa kéo", "Bảng giá cửa kéo trọn gói: chọn loại nào cho nhà phố"),
]
# Chỉ có chữ giá của chính từ khóa: đúng như lời dặn hứa, phải được nhận.
KEYWORD_ONLY = [
    ("giá sửa cửa sắt", "Giá sửa cửa sắt: phụ thuộc vào những gì?"),
    ("cửa sắt giá bao nhiêu", "Cửa sắt giá bao nhiêu: phụ thuộc vào những gì?"),
    ("chi phí sửa cửa cuốn", "Chi phí sửa cửa cuốn: phụ thuộc vào những gì?"),
]


@pytest.mark.parametrize(("keyword", "title"), EDGE_PRICE)
def test_lc1_price_across_keyword_edge_is_dropped(keyword, title):
    assert mentions_price(title, keyword)
    assert accept_ai_title(title, keyword, BANNED) is None


@pytest.mark.parametrize(("keyword", "title"), OUTSIDE_PRICE)
def test_price_outside_keyword_is_dropped(keyword, title):
    """Canh: câu ngoại lệ không nới bộ kiểm với giá nằm hẳn ngoài từ khóa."""
    assert mentions_price(title, keyword)
    assert accept_ai_title(title, keyword, BANNED) is None


@pytest.mark.parametrize(("keyword", "title"), KEYWORD_ONLY)
def test_price_word_inside_keyword_is_kept(keyword, title):
    """Canh: sửa LC-T040-1 không được bỏ oan gợi ý chỉ có chữ giá của chính từ khóa."""
    assert not mentions_price(title, keyword)
    assert accept_ai_title(title, keyword, BANNED) is not None


@pytest.mark.parametrize("which", ["both", "title", "description"])
def test_keyword_price_exception_always_keeps_the_limit(which):
    """Canh: câu ngoại lệ luôn kèm giới hạn «phần chữ còn lại» (không thành giấy phép nói giá)."""
    text = prompts.meta_prompt("giá sửa cửa sắt", "T", [Section(heading="H", body="B")], which)
    rule = text.split("Quy tắc cho mọi meta:", 1)[1]
    assert rule.count("vẫn giữ nguyên văn từ khóa") == 1
    after = rule.split("vẫn giữ nguyên văn từ khóa", 1)[1].split("\n- ", 1)[0]
    assert "phần chữ còn lại vẫn không có con số, mức giá hay chữ nào về giá" in " ".join(
        after.split()
    )
