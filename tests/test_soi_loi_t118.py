"""Test thêm của Soi Lỗi T-118: tên mô hình dạng link «ngoặc nhọn» vẫn thành link trong st.error.

- SL-T118-1 (Thấp, có từ trước ở bộ làm sạch dùng chung ``escape_link_syntax`` T-031; còn sót của
  LC-T034-1): Markdown (CommonMark) coi ``<scheme:…>`` là link tự động. ``model_label`` (tức
  ``escape_link_syntax``) chỉ chèn ký tự rộng 0 vào ``://``, không gỡ dấu ``<``, nên:

  - ``<https:evil.example/x>`` (không có ``//``) qua nguyên vẹn; trình duyệt mở thành
    ``https://evil.example/x`` (thử trên trang Streamlit thật, Soi Lỗi T-118);
  - ``<https://…>``, ``<HTTPS://…>``, ``<ftp://…>``, ``<mailto:…>``, ``<http:\\…>`` vẫn hiện
    thành thẻ link (địa chỉ hỏng vì ký tự rộng 0, riêng ``mailto:`` vẫn mở trình gửi thư).

  Trái lời hứa của ``model_label``: «không bao giờ thành link». Tên mô hình người dùng gõ ở Thử mù
  (Cài đặt) và tên trong ``config/ai.toml`` đi vào câu báo ``st.error``. Bộ làm sạch này cũng dùng
  cho chữ AI hiện trên trang (T-031), nên chữ AI có ``<https:…>`` cũng thành link ở trang xem.

Lỗi đánh dấu ``xfail(strict=True)`` kèm mã SL-T118-x. Không gọi mạng, không gọi AI.
"""

from __future__ import annotations

import re

import pytest

from seo_app.ai.base import TaskConfig, bad_request_error, model_label

# CommonMark 0.31 «autolink»: «<» + scheme (2–32 ký tự) + «:» + mọi ký tự trừ điều khiển ASCII,
# dấu cách, «<», «>», rồi «>»; dấu «\» ngay trước «<» thì không còn là link.
AUTOLINK = re.compile(r"(?<!\\)<[A-Za-z][A-Za-z0-9+.\-]{1,31}:[^\x00-\x20<>]*>")

ANGLE_MODELS = (
    "<https:evil.example/khong-gach>",  # link hoạt động thật trên trang
    "<https://evil.example/goc>",
    "<HTTPS://evil.example/hoa>",
    "<ftp://evil.example/f>",
    "<mailto:ban@evil.example>",
    "<http:\\\\evil.example\\gach-nguoc>",
)


def test_autolink_pattern_matches_markdown():
    """Đối chứng cho mẫu dò: chữ chưa làm sạch thì là link tự động; chữ thường thì không."""
    assert all(AUTOLINK.search(model) for model in ANGLE_MODELS)
    assert not AUTOLINK.search("claude-opus-5-5")
    assert not AUTOLINK.search(r"\<https:evil.example>")


@pytest.mark.xfail(
    strict=True,
    reason=(
        "SL-T118-1 (soi-loi, có từ trước ở escape_link_syntax T-031): tên mô hình dạng "
        "<https:evil.example/x> qua model_label vẫn là link tự động của Markdown, st.error hiện "
        "thành link mở được https://evil.example/x"
    ),
)
@pytest.mark.parametrize("model", ANGLE_MODELS)
def test_sl_t118_1_angle_bracket_model_never_becomes_a_link(model):
    task = TaskConfig(name="write", provider="openai", model=model, effort="high")
    for text in (model_label(model), str(bad_request_error("OpenAI", task))):
        assert not AUTOLINK.search(text), text
