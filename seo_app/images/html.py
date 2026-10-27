"""Dựng HTML ``<figure>`` cho ảnh trong bài nháp WordPress (phiếu T-054, thiết kế T-046 mục 6).

HTML ảnh **do code dựng**, không lấy từ AI hay người dùng (góp ý Lá Chắn T-046 số 7):

- Alt và chú thích là chữ (AI gợi ý, người dùng đã duyệt). Trước khi ghi vào HTML (điều kiện 4
  của Lá Chắn T-050): ``unbreak_autolinks`` gỡ ký tự rộng 0 mà ``clean_ai_text`` chèn vào địa
  chỉ trần, "www.", email (T-031); ``unescape_link_syntax`` gỡ dấu "\\" mà ``clean_ai_text``
  thêm trước ``(``, ``[``, ``:`` (``]\\(``…), và "\\" của ``]\\:`` ở mọi chỗ trong dòng (tiền tố
  «Minh họa» ghép sau bước escape, T-071); rồi bỏ ký tự vô hình còn lại, gộp một dòng
  (``plain_image_text``). Chữ này mới ``html.escape(…, quote=True)`` khi ghép vào HTML.
- ``src`` chỉ nhận địa chỉ ``https://`` an toàn (``is_safe_url``), không có dấu nháy hay ký tự
  lạ. Client WordPress còn kiểm địa chỉ nằm trên đúng website (``is_site_link``).
- Kết quả đi qua ``sanitize_html`` lần cuối; thẻ ``<img>`` thiếu ``src`` hay ``alt`` sau khi lọc
  thì báo lỗi. Bộ lọc đổi mọi "[" và "]" (cả trong ``alt``) thành "&#91;", "&#93;" (T-061):
  shortcode WordPress trong alt, chú thích không chạy được, kể cả khi ký tự vô hình vừa được gỡ
  ở trên.

Lớp CSS: chỉ ``wp-block-image`` trên ``<figure>`` (kiểu dáng ảnh của WordPress). **Không** gắn
``wp-image-<mã>`` vào ``<img>``: có lớp này WordPress tự thêm ``srcset`` (các cỡ nhỏ do WordPress
tạo, đã bị bỏ EXIF), điện thoại sẽ tải bản không còn GPS. Quyết định 5A: ảnh trong bài dùng file
đầy đủ 1600 px để GPS tới người xem và Google.

``srcset`` chỉ một ứng viên là chính file đầy đủ (T-059 bước 7): thử thật 2026-10-27, bài gửi
không có ``wp-image-<mã>`` mà trang vẫn in ``<img class="wp-image-951" srcset="…800w, …768w,
…300w">`` (một thứ phía website gắn lớp đó; WordPress lõi chỉ lấy mã ảnh từ lớp này), nên điện
thoại tải bản thu nhỏ đã mất GPS. ``wp_filter_content_tags`` (``wp-includes/media.php``) chỉ gọi
``wp_img_tag_add_srcset_and_sizes_attr`` khi thẻ **chưa có** `` srcset=``: thẻ có sẵn
``srcset="<file đầy đủ> 1x"`` thì WordPress để nguyên, dù thẻ có lớp ``wp-image-<mã>`` hay không;
trình duyệt chỉ có một lựa chọn là file đầy đủ. Không ghi ``sizes`` (chỉ có ý nghĩa với ứng viên
"w"), không ghi ``loading`` (WordPress tự thêm ``loading``/``fetchpriority`` theo vị trí ảnh).
Giới hạn: tài khoản không có quyền ``unfiltered_html`` thì kses của WordPress bỏ ``srcset`` khi
lưu (Biên tập viên trên site đơn có quyền này); và lớp đó vẫn bị gắn thì WordPress lại tự thêm.
"""

from __future__ import annotations

import html
import re

from seo_app.onpage.meta import normalize_meta
from seo_app.sanitize import (
    escape_shortcodes,
    is_safe_url,
    sanitize_html,
    unbreak_autolinks,
    unescape_link_syntax,
)

FIGURE_CLASS = "wp-block-image"
MAX_SRC_CHARS = 2000
MAX_IMAGE_EDGE = 10_000  # cạnh ảnh (px) ghi vào width/height; ảnh đăng web chỉ tới 1600 px

# Ký tự điều khiển (C0, DEL, C1): thành dấu cách trước khi gộp khoảng trắng.
_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f-\x9f]")
# Địa chỉ ảnh: không khoảng trắng, ký tự điều khiển, dấu nháy, ``<``, ``>``, dấu huyền, ``\``,
# dấu phẩy (``srcset`` tách ứng viên bằng dấu phẩy; WordPress bỏ dấu phẩy khỏi tên file tải lên).
_SRC_UNSAFE = re.compile(r"[\s\x00-\x1f\x7f-\x9f\"'<>`\\,]")
# Mô tả của ứng viên duy nhất trong ``srcset``: file đầy đủ cho mọi màn hình.
_SRCSET_DESCRIPTOR = "1x"
# "\" giữa "]" (không bị escape: đứng sau một số chẵn dấu "\") và ":" (SL-T054-1, LC-T054-3).
# ``escape_link_syntax`` chỉ thêm dấu này khi "[" mở nhãn đứng đầu dòng, và
# ``unescape_link_syntax`` cũng chỉ gỡ khi "[" còn ở đầu dòng. ``clean_suggestion`` ghép tiền tố
# «Minh họa», «Ảnh minh họa (AI):» SAU khi escape (người dùng gõ thêm chữ phía trước cũng vậy),
# nên "[" ra giữa dòng và dấu "\" còn lại. Alt, chú thích gửi WordPress không phải Markdown: gỡ ở
# mọi chỗ trong dòng.
_LABEL_COLON_ESCAPE = re.compile(r"(?<!\\)((?:\\\\)*)\]\\:")
# Thẻ ``<img …>`` trong kết quả của bộ lọc: giá trị thuộc tính đã escape (không có ">" trần), chữ
# chú thích có "<" thành "&lt;", nên thẻ kết thúc ở dấu ">" đầu tiên.
_IMG_TAG = re.compile(r"<img\s[^>]*>")

_MSG_NO_ALT = "Ảnh chưa có alt (mô tả ảnh). Viết hoặc duyệt alt rồi gửi lại."
_MSG_BAD_SRC = "Địa chỉ ảnh không hợp lệ (phải là https:// trên website, không có ký tự lạ)."
_MSG_BAD_SIZE = "Kích thước ảnh không hợp lệ."


class ImageHtmlError(ValueError):
    """Không dựng được HTML ảnh. ``str(err)`` là câu tiếng Việt cố định (không chép dữ liệu)."""


def plain_image_text(text: object) -> str:
    """Alt hay chú thích ở dạng chữ thường, sẵn sàng để escape vào HTML hay gửi qua REST.

    Thứ tự (điều kiện 4 của Lá Chắn T-050): gỡ ký tự ngắt rộng 0 (``unbreak_autolinks``), gỡ
    escape link Markdown (``unescape_link_syntax``, rồi "\\" của ``]\\:`` ở giữa dòng: T-071),
    rồi chuẩn hóa như meta (``normalize_meta``: NFC, bỏ mọi ký tự vô hình còn lại, gộp mọi
    khoảng trắng thành một dấu cách). Ký tự điều khiển thành dấu cách. **Chưa** escape HTML
    (không đụng tới "[", "]": ``sanitize_html``, ``escape_shortcodes`` vô hiệu shortcode sau
    bước này, T-061). Không phải chữ thì là chuỗi rỗng.
    """
    if not isinstance(text, str):
        return ""
    text = unescape_link_syntax(unbreak_autolinks(text))
    text = _LABEL_COLON_ESCAPE.sub(r"\1]:", text)
    return normalize_meta(_CONTROL_CHARS.sub(" ", text))


def _check_src(src: object) -> str:
    if (
        not isinstance(src, str)
        or not src.startswith("https://")
        or len(src) > MAX_SRC_CHARS
        or _SRC_UNSAFE.search(src)
        or not is_safe_url(src)
    ):
        raise ImageHtmlError(_MSG_BAD_SRC)
    return src


def _check_edge(value: object) -> int:
    if type(value) is not int or not 0 < value <= MAX_IMAGE_EDGE:
        raise ImageHtmlError(_MSG_BAD_SIZE)
    return value


def figure_html(*, src: str, alt: str, width: int, height: int, caption: str = "") -> str:
    """``<figure class="wp-block-image"><img …><figcaption>…</figcaption></figure>``.

    ``<img src alt srcset width height>``: ``srcset`` chỉ có ``src`` (``1x``) để WordPress không
    tự thêm các cỡ nhỏ đã mất GPS (T-059, xem đầu module).
    ``alt``, ``caption``: chữ người dùng đã duyệt (có thể còn ký tự ngắt rộng 0, escape Markdown
    của ``clean_ai_text``); hàm tự làm sạch bằng ``plain_image_text`` rồi escape. Chú thích rỗng
    thì không có ``<figcaption>``. ``width``, ``height``: cỡ thật của file ảnh (``WebImage``).
    Báo ``ImageHtmlError`` khi alt rỗng, địa chỉ hay kích thước không hợp lệ.
    """
    src = _check_src(src)
    alt_text = plain_image_text(alt)
    if not alt_text:
        raise ImageHtmlError(_MSG_NO_ALT)
    caption_text = plain_image_text(caption)
    width, height = _check_edge(width), _check_edge(height)
    src_escaped = html.escape(src, quote=True)
    img = (
        f'<img src="{src_escaped}" alt="{html.escape(alt_text, quote=True)}" '
        f'srcset="{src_escaped} {_SRCSET_DESCRIPTOR}" width="{width}" height="{height}">'
    )
    figcaption = (
        f"<figcaption>{html.escape(caption_text, quote=True)}</figcaption>" if caption_text else ""
    )
    cleaned = sanitize_html(f'<figure class="{FIGURE_CLASS}">{img}{figcaption}</figure>')
    # Bộ lọc là chốt cuối: nó mà bỏ src, alt hay srcset (địa chỉ lạ lọt qua bước kiểm ở trên)
    # thì dừng, không gửi một ảnh hỏng (hay ảnh để WordPress tự chọn cỡ nhỏ mất GPS) vào bài. So
    # với ``src`` đúng dạng bộ lọc in ra ("[" thành "&#91;"). Chỉ tìm trong thẻ ``<img>``, không
    # trong chữ chú thích (LC-T054-6): chú thích ``src="https://…" alt=x`` không được làm chốt
    # này tưởng ảnh vẫn còn ``src``.
    src_attr = escape_shortcodes(src_escaped)
    img_tags = _IMG_TAG.findall(cleaned)
    if (
        len(img_tags) != 1
        or f' src="{src_attr}"' not in img_tags[0]
        or f' srcset="{src_attr} {_SRCSET_DESCRIPTOR}"' not in img_tags[0]
        or " alt=" not in img_tags[0]
    ):
        raise ImageHtmlError(_MSG_BAD_SRC)
    return cleaned
