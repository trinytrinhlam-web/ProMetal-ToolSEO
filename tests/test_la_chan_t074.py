"""Lá Chắn T-074 (rút gọn): tên công cụ tạo ảnh AI một từ bị gõ tách đôi.

SL-T074-2 (Soi Lỗi) là kiểu viết hoa giữa chữ ở tên thư mục ("MidJourney"). Kiểu gõ tách bằng dấu
cách hay gạch nối ("Mid Journey", "Co-Pilot") cũng ra **ảnh thật**, ở cả tên thư mục, tên file và
thư mục gốc (``is_ai_name``), trên ``main`` (``da87dbf``) lẫn nhánh T-074; cách sửa một dòng của
Soi Lỗi (đọc thêm kiểu không tách chữ hoa) không gỡ được kiểu này. Ghi là LC-T074-1 (xem
``docs/team/reports/T-074-la-chan.md``), đánh dấu ``xfail(strict=True)``: sửa xong thì test tự báo
XPASS để gỡ dấu.

Đối chứng (đang qua): tên công cụ viết liền vẫn là ảnh AI; tên thư mục ảnh thật có các chữ gần
giống ("Cửa sổ ra ban công" gõ không dấu) vẫn là ảnh thật, để cách sửa không ghép bừa mọi cặp chữ
liền nhau. Chỉ xử lý chữ, không đọc ổ đĩa, không gọi mạng.
"""

from __future__ import annotations

import pytest

from seo_app.images.folders import ImageRef
from seo_app.images.tags import SOURCE_AI, ImageTags, is_ai_name, tags_for_image

BASE = "CT012 - Cổng inox - Quận 7/truoc"
REAL = ImageTags(project_code="CT012", category="Cổng inox", area="Quận 7", phase="truoc")
AI_ONLY = ImageTags(source=SOURCE_AI, category="Cổng inox")

# Midjourney, Firefly, Copilot, Seedream: tên ghép từ hai chữ tiếng Anh, hay bị gõ tách.
SPLIT_TOOL_NAMES = [
    "Mid Journey",
    "Mid-Journey",
    "Ảnh Mid Journey",
    "Fire Fly",
    "Adobe Fire Fly",
    "Co Pilot",
    "Co-Pilot",
    "See Dream",
]
_REASON = (
    "LC-T074-1: dấu hiệu tên công cụ một từ ('midjourney', 'firefly', 'copilot', 'seedream') "
    "chỉ khớp một chữ; gõ tách bằng dấu cách hay gạch nối thành hai chữ không khớp, ảnh AI giữ mã "
    "công trình, khu vực, trước/sau như ảnh thật"
)


@pytest.mark.xfail(strict=True, reason=_REASON)
@pytest.mark.parametrize("name", SPLIT_TOOL_NAMES)
def test_lc_t074_1_split_tool_name_in_folder_is_ai(name):
    assert tags_for_image(ImageRef(0, f"{BASE}/{name}/IMG_0001.jpg")).tags == AI_ONLY


@pytest.mark.xfail(strict=True, reason=_REASON)
@pytest.mark.parametrize("name", SPLIT_TOOL_NAMES)
def test_lc_t074_1_split_tool_name_in_file_name_is_ai(name):
    assert tags_for_image(ImageRef(0, f"{BASE}/{name} 0001.png")).tags == AI_ONLY


@pytest.mark.xfail(strict=True, reason=_REASON)
@pytest.mark.parametrize("name", ["Mid Journey", "Fire Fly", "Co-Pilot", "See Dream"])
def test_lc_t074_1_split_tool_name_as_root_folder_is_ai(name):
    assert is_ai_name(f"G:/My Drive/{name}") is True


@pytest.mark.parametrize("name", ["Midjourney", "Firefly", "Copilot", "Seedream"])
def test_tool_name_written_as_one_word_is_ai(name):
    assert tags_for_image(ImageRef(0, f"{BASE}/{name}/IMG_0001.jpg")).tags == AI_ONLY
    assert tags_for_image(ImageRef(0, f"{BASE}/{name} 0001.png")).tags == AI_ONLY
    assert is_ai_name(f"G:/My Drive/{name}") is True


@pytest.mark.parametrize(
    "name", ["Cua so ra ban cong", "Cửa sổ ra ban công", "Nha co Phuong", "Mai che san thuong"]
)
def test_real_folders_with_nearby_words_stay_real(name):
    tags = tags_for_image(ImageRef(0, f"{BASE}/{name}/IMG_0001.jpg")).tags
    assert not tags.is_ai
    assert (tags.project_code, tags.area, tags.phase) == (REAL.project_code, REAL.area, REAL.phase)
    assert is_ai_name(f"G:/My Drive/{name}") is False
