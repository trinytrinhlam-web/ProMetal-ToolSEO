"""Soi Lỗi · T-059 bước 7: thử phá phần siết client WordPress theo kết quả thử thật 2026-10-27.

Kiểm độc lập (không dùng lại bản WordPress giả lập hay khuôn trả lời của Thợ Máy):

1. ``_ability_confirms``: khuôn trả lời thật của SiteSEO 1.4.2 (ghi chú phiếu 27/10:
   ``{"updated": true, "post": {title, description, canonical_url: null, focus_keyphrase,
   seo_score, robots{5 cờ}, social{6 null}}}``) được nhận; mọi khuôn lạ (thiếu ``post``, ``post``
   sai kiểu, chữ khác một ký tự, ``success``, ``updated`` dạng chuỗi/số…) là chưa ghi.
   SiteSEO 1.4.2 (``update_post_seo_data``, đọc mã ở kho plugin wordpress.org 2026-10-28) lưu
   ``sanitize_text_field($value)`` rồi trả ``post`` đọc lại từ meta: site giả ở đây làm sạch y
   như vậy.
2. Ảnh trong bài: ``figure_html`` ghi sẵn ``srcset="<file đầy đủ> 1x"``. Bản Python riêng của
   ``wp_filter_content_tags`` (``wp-includes/media.php`` trunk, đọc 2026-10-28): mã ảnh lấy từ lớp
   ``wp-image-N``; chỉ thêm ``srcset``/``sizes`` khi thẻ **chưa có** `` srcset=``; cần từ 2 ứng
   viên. ``<figure>``, alt, chú thích, chặn shortcode, ``sanitize_html`` giữ thuộc tính.

Chỉ site giả (``FakeWordPress``), không gọi WordPress thật hay mạng thật. Test
``xfail(strict=True)`` là lỗi tìm được (SL-T059-n trong ``docs/team/reports/T-059-soi-loi.md``):
sửa xong thì test thành XPASS và báo hỏng, khi đó chỉ cần xóa dòng ``@pytest.mark.xfail``.
"""

import html
import json
import re
import unicodedata
from html.parser import HTMLParser
from urllib.parse import urlsplit

import pytest
import test_wordpress_images as wi
from fake_wordpress import BASE_URL, make_session

from seo_app.images import html as image_html
from seo_app.images.process import make_web_image
from seo_app.sanitize import sanitize_html
from seo_app.wordpress import WordPressClient, WordPressError
from seo_app.wordpress.client import DraftImage, _ability_confirms

PASSWORD = "Pw7r Nd3k Lq8s Zx5m"
POSTS = "/wp-json/wp/v2/posts"
POST_42 = f"{POSTS}/42"
ABILITY = "/wp-json/wp-abilities/v1/abilities/siteseo-posts/seo-data-update"
RUN = f"{ABILITY}/run"
UPLOADS = f"{BASE_URL}/wp-content/uploads/2026/10/"
FULL = f"{UPLOADS}cong-sat-tan-binh.webp"

TITLE = "Sửa cửa sắt tại nhà Tân Bình | Pro-Metal"
DESC = "Thợ tới trong 2 giờ, báo giá trước khi làm, bảo hành 12 tháng."
KEYWORD = "sửa cửa sắt"
SENT = {"title": TITLE, "description": DESC, "focus_keyword": KEYWORD}


def body(request):
    return json.loads(request.body) if request.body else None


def path(request):
    return urlsplit(request.url).path


# ================================================================ 1. _ability_confirms

def real_post(**changes):
    """``post`` đúng khuôn ghi chú 27/10 (thứ tự, kiểu như site thật)."""
    post = {
        "title": TITLE,
        "description": DESC,
        "canonical_url": None,
        "focus_keyphrase": KEYWORD,
        "seo_score": None,
        "robots": {"noindex": False, "nofollow": False, "noimageindex": False,
                   "noarchive": False, "nosnippet": False},
        "social": {"og_title": None, "og_description": None, "og_image": None,
                   "twitter_title": None, "twitter_description": None, "twitter_image": None},
    }
    post.update(changes)
    return post


ACCEPTED = {
    "khuon-that": {"updated": True, "post": real_post()},
    "diem-seo-la-so": {"updated": True, "post": real_post(seo_score=72)},
    "them-khoa-message": {"updated": True, "post": real_post(), "message": "ok"},
    "success-true-di-kem": {"updated": True, "post": real_post(), "success": True},
}
REJECTED = {
    "thieu-post": {"updated": True},
    "post-null": {"updated": True, "post": None},
    "post-danh-sach": {"updated": True, "post": [real_post()]},
    "post-chuoi": {"updated": True, "post": "ok"},
    "post-rong": {"updated": True, "post": {}},
    "chi-success": {"success": True},
    "success-false": {"updated": True, "post": real_post(), "success": False},
    "success-0": {"updated": True, "post": real_post(), "success": 0},
    "success-chuoi": {"updated": True, "post": real_post(), "success": "true"},
    "success-null": {"updated": True, "post": real_post(), "success": None},
    "co-code": {"updated": True, "post": real_post(), "code": "rest_x"},
    "code-null": {"updated": True, "post": real_post(), "code": None},
    "updated-chuoi": {"updated": "true", "post": real_post()},
    "updated-1": {"updated": 1, "post": real_post()},
    "updated-1.0": {"updated": 1.0, "post": real_post()},
    "updated-null": {"updated": None, "post": real_post()},
    "updated-false": {"updated": False, "post": real_post()},
    "updated-danh-sach": {"updated": [True], "post": real_post()},
    "thieu-updated": {"post": real_post()},
    "boc-trong-data": {"data": {"updated": True, "post": real_post()}},
    "tieu-de-them-cach": {"updated": True, "post": real_post(title=TITLE + " ")},
    "tieu-de-hoa": {"updated": True, "post": real_post(title=TITLE.upper())},
    "tieu-de-nfd": {"updated": True, "post": real_post(title=unicodedata.normalize("NFD", TITLE))},
    "tieu-de-ky-tu-vo-hinh": {"updated": True, "post": real_post(title=TITLE.replace(" ", " ​", 1))},
    "tieu-de-khac-mot-ky-tu": {"updated": True, "post": real_post(title=TITLE[:-1] + "I")},
    "tieu-de-danh-sach": {"updated": True, "post": real_post(title=[TITLE])},
    "tieu-de-dict": {"updated": True, "post": real_post(title={"raw": TITLE})},
    "mo-ta-khac": {"updated": True, "post": real_post(description=DESC[:-1])},
    "tu-khoa-null": {"updated": True, "post": real_post(focus_keyphrase=None)},
    "tu-khoa-sai-ten-khoa": {
        "updated": True,
        "post": {**{k: v for k, v in real_post().items() if k != "focus_keyphrase"},
                 "focus_keyword": KEYWORD},
    },
    "danh-sach": [{"updated": True, "post": real_post()}],
    "chuoi": "updated",
    "null": None,
    "true": True,
}


@pytest.mark.parametrize("name", ACCEPTED)
def test_khuon_that_va_khoa_la_vo_hai_duoc_nhan(name):
    assert _ability_confirms(ACCEPTED[name], SENT) is True


@pytest.mark.parametrize("name", REJECTED)
def test_khuon_la_la_chua_ghi(name):
    assert _ability_confirms(REJECTED[name], SENT) is False


def test_chi_so_truong_da_gui():
    """App chỉ gửi tiêu đề thì chỉ so tiêu đề; mô tả, từ khóa đang có trên site không ảnh hưởng."""
    data = {"updated": True, "post": real_post(description="Mô tả cũ", focus_keyphrase="")}
    assert _ability_confirms(data, {"title": TITLE}) is True
    assert _ability_confirms(data, {"description": DESC}) is False


def php_sanitize_text_field(text):
    """``sanitize_text_field`` của WordPress (``_sanitize_text_fields``), phần chạy với chữ một
    dòng app gửi: «<» thì ``wp_pre_kses_less_than`` (đoạn «<…» không có «>» thành ``esc_html``)
    rồi ``strip_tags``; gộp khoảng trắng ASCII; bỏ mọi «%» + 2 ký tự hex."""
    if "<" in text:
        text = re.sub(
            r"<[^>]*?((?=<)|>|$)",
            lambda m: m.group(0) if ">" in m.group(0) else html.escape(m.group(0)),
            text,
        )
        out, in_tag = [], False
        for i, ch in enumerate(text):
            nxt = text[i + 1 : i + 2]
            if in_tag:
                in_tag = ch != ">"
            elif ch == "<" and not (nxt and nxt in " \t\n\r\v\f"):
                in_tag = True
            else:
                out.append(ch)
        text = "".join(out)
    text = re.sub(r"[\r\n\t ]+", " ", text).strip()
    found = False
    while match := re.search(r"%[a-fA-F0-9]{2}", text):
        text, found = text.replace(match.group(0), ""), True
    return re.sub(" +", " ", text).strip() if found else text


def php_stripslashes(text):
    """``stripslashes`` của PHP (``wp_unslash``): «\\x» thành «x», «\\\\» thành «\\», «\\0»
    thành NUL, «\\» cuối chuỗi bị bỏ."""
    out, i = [], 0
    while i < len(text):
        if text[i] == "\\":
            i += 1
            if i < len(text):
                out.append("\0" if text[i] == "0" else text[i])
        else:
            out.append(text[i])
        i += 1
    return "".join(out)


def siteseo_1_4_2(request):
    """``update_post_seo_data`` của SiteSEO 1.4.2: ``update_post_meta(…, sanitize_text_field($v))``
    (``update_metadata`` của WordPress còn ``wp_unslash`` giá trị), trả ``updated`` và ``post``
    đọc lại sau khi lưu."""
    sent = (body(request) or {}).get("input", {})
    post = real_post(title="", description="", focus_keyphrase="")
    for name in ("title", "description", "focus_keyphrase"):
        if name in sent:
            post[name] = php_stripslashes(php_sanitize_text_field(sent[name]))
    return {"updated": True, "post": post}


@pytest.fixture
def seo_client(fake_wp):
    fake_wp.on("POST", POSTS, (201, {"id": 42, "status": "draft"}, {}))
    fake_wp.on("GET", POST_42, {"id": 42, "status": "draft", "meta": {}})
    fake_wp.on("GET", ABILITY, {"name": "siteseo-posts/seo-data-update"})
    fake_wp.on("POST", RUN, siteseo_1_4_2)
    client = WordPressClient(BASE_URL, "lam", PASSWORD, session=make_session(fake_wp),
                             write_seo=True)
    client.create_draft("Cổng inox", "<p>Nội dung</p>")
    return client


@pytest.mark.parametrize(
    "title",
    ["Sửa cửa sắt tại nhà | Pro-Metal", "So sánh cửa sắt & cửa nhôm", "Cửa sắt 100% thép",
     "Cửa < 2m và cổng > 3m", "Sơn tĩnh điện > sơn dầu?", 'Lắp cổng "inox" chuẩn'],
)
def test_chu_siteseo_luu_nguyen_thi_bao_da_ghi(fake_wp, seo_client, title):
    """Không chặn oan: chữ ``sanitize_text_field`` để nguyên thì app báo đã ghi."""
    assert php_sanitize_text_field(title) == title
    result = seo_client.set_seo_meta(42, title=title, description=DESC, focus_keyword=KEYWORD)
    assert result.written, result.message


def test_ban_python_cua_sanitize_text_field_dung_cho_ca_da_biet():
    assert php_sanitize_text_field("Giá < 5 triệu") == "Giá &lt; 5 triệu"
    assert php_sanitize_text_field("Cửa < 2m và cổng > 3m") == "Cửa < 2m và cổng > 3m"
    assert php_sanitize_text_field("Tăng 10%BE độ bền") == "Tăng 10 độ bền"
    assert php_sanitize_text_field("Giảm 10% tiền công") == "Giảm 10% tiền công"
    assert php_stripslashes("Giá 5\\% thôi") == "Giá 5% thôi"
    assert php_stripslashes("C:\\\\x") == "C:\\x"


@pytest.mark.xfail(
    strict=True,
    reason="SL-T059-1: chữ SEO hợp lệ mà SiteSEO 1.4.2 lưu khác đi (sanitize_text_field: «< » "
    "thành «&lt; », «%» + 2 ký tự hex bị bỏ; wp_unslash bỏ «\\»): website đã ghi nhưng app báo "
    "«không thành công»",
)
@pytest.mark.parametrize(
    "field,text",
    [
        ("title", "Cổng inox < 5 triệu, giảm 10% tiền công | Pro-Metal"),
        ("title", "Cửa sắt giá < 2 triệu"),
        ("description", "Cổng xếp < 3 triệu, lắp trong ngày tại Tân Bình."),
        ("title", "Tăng 10%BE độ bền cho cổng sắt"),
        ("title", "Giảm giá 5\\% cho cổng sắt"),
    ],
)
def test_sl_t059_1_chu_siteseo_lam_sach_van_bao_dung(fake_wp, seo_client, field, text):
    result = seo_client.set_seo_meta(42, **{field: text})
    runs = [r for r in fake_wp.requests if path(r) == RUN]
    if runs:  # app đã gửi, SiteSEO đã lưu (bản đã làm sạch): phải báo đã ghi
        assert result.written, result.message


# ================================================================ 2. srcset ảnh trong bài

IMG_TAG = re.compile(r"<(img|iframe)\s[^>]+>")
WP_SIZES = (("medium", 300), ("medium_large", 768), ("thumb800", 800), ("thumbnail", 150))


def attachment_meta(file_name, width=1600, height=1200):
    """``_wp_attachment_metadata`` như WordPress tạo cho ảnh 1600 px (các cỡ nhỏ mất EXIF/GPS)."""
    stem, ext = file_name.rsplit(".", 1)
    sizes = {}
    for size_name, w in WP_SIZES:
        h = 150 if size_name == "thumbnail" else round(height * w / width)
        sizes[size_name] = {"file": f"{stem}-{w}x{h}.{ext}", "width": w, "height": h}
    return {"width": width, "height": height, "file": f"2026/10/{file_name}", "sizes": sizes}


def wp_srcset_for(src, width, height, meta):
    """``wp_calculate_image_srcset``: cỡ cùng tỷ lệ (±1 px) với ảnh đang in, ≤ 2048 px, ảnh của
    ``src`` phải có trong danh sách, cần từ 2 ứng viên."""
    base = src.rsplit("/", 1)[0] + "/"
    candidates = [(meta["file"].rsplit("/", 1)[1], meta["width"], meta["height"])]
    candidates += [(s["file"], s["width"], s["height"]) for s in meta["sizes"].values()]
    sources = []
    for file_name, w, h in candidates:
        if w > 2048 or abs(round(w * height / width) - h) > 1:
            continue
        sources.append((base + file_name, w))
    if not any(url == src for url, _w in sources) or len(sources) < 2:
        return None
    return ", ".join(f"{url} {w}w" for url, w in sources)


def wp_filter_content_tags(content, attachments):
    """Phần ``srcset``/``sizes`` của ``wp_filter_content_tags``: mã ảnh từ ``wp-image-N`` (không
    phân biệt hoa thường); thẻ đã có `` srcset=`` thì để nguyên."""

    def one(match):
        tag = match.group(0)
        if match.group(1) != "img":
            return tag
        found = re.search(r"wp-image-([0-9]+)", tag, re.I)
        attachment_id = int(found.group(1)) if found else 0
        if attachment_id <= 0 or " srcset=" in tag or attachment_id not in attachments:
            return tag
        src = re.search(r'src="([^"]+)"', tag)
        width = re.search(r' width="([0-9]+)"', tag)
        height = re.search(r' height="([0-9]+)"', tag)
        if not (src and width and height):
            return tag
        srcset = wp_srcset_for(src.group(1).split("?")[0], int(width.group(1)),
                               int(height.group(1)), attachments[attachment_id])
        if not srcset:
            return tag
        sizes = f"(max-width: {width.group(1)}px) 100vw, {width.group(1)}px"
        attr = f' srcset="{html.escape(srcset)}" sizes="{html.escape(sizes)}"'
        return re.sub(r"<img ([^>]+?)[/ ]*>", lambda m: f"<img {m.group(1)}{attr} />", tag)

    return IMG_TAG.sub(one, content)


class _Page(HTMLParser):
    """Thẻ, thuộc tính, chữ trình duyệt thấy (đã giải mã ký tự)."""

    def __init__(self, content):
        super().__init__(convert_charrefs=True)
        self.tags, self.imgs, self.text = [], [], []
        self.feed(content)
        self.close()

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, [name for name, _v in attrs]))
        if tag == "img":
            self.imgs.append(dict(attrs))

    def handle_data(self, data):
        self.text.append(data)


def figure(src=FULL, alt="Cổng sắt Tân Bình sau khi sơn", caption="Sau khi sơn lại"):
    return image_html.figure_html(src=src, alt=alt, width=1600, height=1200, caption=caption)


def old_figure(src=FULL, alt="Cổng sắt Tân Bình sau khi sơn"):
    """Thẻ như trước T-059 (không ``srcset``): để chứng minh bản giả lập bắt đúng lỗi 27/10."""
    return (f'<figure class="wp-block-image"><img src="{src}" alt="{alt}" width="1600" '
            'height="1200"></figure>')


SITE_CLASS = {
    "lop-dau-the": lambda c: c.replace("<img ", '<img class="wp-image-951" ', 1),
    "lop-cuoi-the": lambda c: c.replace('height="1200">', 'height="1200" class="wp-image-951">'),
    "lop-kem-lop-khac": lambda c: c.replace(
        "<img ", '<img class="alignnone size-full wp-image-951" ', 1),
    "lop-chu-hoa": lambda c: c.replace("<img ", '<img class="WP-IMAGE-951" ', 1),
    "tu-dong-the": lambda c: c.replace("<img ", '<img class="wp-image-951" ', 1).replace(
        'height="1200">', 'height="1200" />'),
    "them-loading": lambda c: c.replace(
        "<img ", '<img loading="lazy" decoding="async" class="wp-image-951" ', 1),
    "nhay-don-srcset": lambda c: c.replace("<img ", '<img class="wp-image-951" ', 1).replace(
        f'srcset="{FULL} 1x"', f"srcset='{FULL} 1x'"),
}
ATTACHMENTS = {951: attachment_meta("cong-sat-tan-binh.webp")}


def test_ban_gia_lap_tai_hien_loi_27_10_o_the_cu():
    page = _Page(wp_filter_content_tags(SITE_CLASS["lop-dau-the"](old_figure()), ATTACHMENTS))
    srcset = page.imgs[0]["srcset"]
    assert "-300x225.webp 300w" in srcset and "-800x600.webp 800w" in srcset
    assert page.imgs[0]["sizes"]


@pytest.mark.parametrize("change", SITE_CLASS)
def test_wordpress_khong_them_ban_thu_nho_vao_the_moi(change):
    content = SITE_CLASS[change](figure())
    shown = _Page(wp_filter_content_tags(content, ATTACHMENTS))
    assert wp_filter_content_tags(content, ATTACHMENTS) == content
    assert shown.imgs[0]["srcset"] == f"{FULL} 1x" and "sizes" not in shown.imgs[0]


def test_nhieu_anh_trong_bai_deu_giu_file_day_du(fake_wp, wp_client):
    """Gửi nháp 3 ảnh qua site giả rồi để WordPress giả lập (đã gắn lớp đúng mã từng ảnh) xử lý
    nội dung: mọi ảnh vẫn chỉ có file đầy đủ."""
    site = wi.Site(fake_wp)
    images = [
        DraftImage(make_web_image(wi._jpeg((320, 240), color=(10 * i, 80, 40))), alt=f"Ảnh {i}",
                   caption=f"Chú thích {i}")
        for i in range(1, 4)
    ]
    wp_client.create_draft_with_images("Sửa cổng", ["<p>Mở</p>", *images, "<p>Kết</p>"])
    content = wi.sent_content(fake_wp)
    attachments = {}
    for media_id, file_name in site.files.items():
        content = content.replace(f'src="{site.source_url(media_id)}"',
                                  f'class="wp-image-{media_id}" src="{site.source_url(media_id)}"')
        attachments[media_id] = attachment_meta(file_name, 320, 240)
    shown = _Page(wp_filter_content_tags(content, attachments))
    assert len(shown.imgs) == 3
    for img in shown.imgs:
        assert img["srcset"] == f"{img['src']} 1x" and "sizes" not in img


ALTS_CAPTIONS = [
    ("Cổng sắt «Tân Bình» 2 cánh", "Sau khi sơn — bền 10 năm"),
    ('Cửa "kéo" Đài Loan', "Giá < 5 triệu & tặng ổ khóa"),
    ("[caption]thu[/caption]", "[code_snippet id=1] [[embed]]"),
    ("Cổng ​inox​", "Chú​ thích"),
    ("</figcaption><script>alert(1)</script>", "<img src=x onerror=alert(1)>"),
    ("Mái tôn 😀 xanh", ""),
]


@pytest.mark.parametrize(("alt", "caption"), ALTS_CAPTIONS)
def test_figure_khong_vo_alt_chu_thich_chan_shortcode(alt, caption):
    out = figure(alt=alt, caption=caption)
    page = _Page(out)
    expected_tags = [("figure", ["class"]), ("img", ["src", "alt", "srcset", "width", "height"])]
    if image_html.plain_image_text(caption):
        expected_tags.append(("figcaption", []))
    assert page.tags == expected_tags
    img = page.imgs[0]
    assert img["src"] == FULL and img["srcset"] == f"{FULL} 1x"
    assert img["alt"] == image_html.plain_image_text(alt)
    assert "".join(page.text) == image_html.plain_image_text(caption)
    assert "[" not in out and "]" not in out  # chặn shortcode: không còn ngoặc vuông trần
    assert sanitize_html(out) == out  # bộ lọc giữ nguyên mọi thuộc tính


@pytest.mark.parametrize(
    "src",
    [f"{UPLOADS}cong[1].webp", f"{UPLOADS}cong.webp?ver=2&size=full", f"{UPLOADS}c%C3%B4ng.webp",
     f"{UPLOADS}cong%2Cinox.webp"],
)
def test_dia_chi_la_van_dung_o_ca_src_va_srcset(src):
    out = figure(src=src)
    img = _Page(out).imgs[0]
    assert img["src"] == src and img["srcset"] == f"{src} 1x"
    assert "[" not in out and "]" not in out and sanitize_html(out) == out


@pytest.mark.parametrize(
    "src",
    [f"{UPLOADS}cong,inox.webp", f"{UPLOADS}cong inox.webp", f"{UPLOADS}cong.webp 2x",
     "javascript:alert(1)", f"{UPLOADS}cong.webp\t2x"],
)
def test_dia_chi_tach_duoc_thanh_ung_vien_khac_bi_tu_choi(src):
    with pytest.raises(image_html.ImageHtmlError):
        figure(src=src)


def test_gui_nhap_kem_anh_loi_bo_loc_bo_srcset_thi_khong_gui(fake_wp, wp_client, monkeypatch):
    """Chốt cuối: bộ lọc mà bỏ ``srcset`` thì không gửi ảnh (không để WordPress chọn cỡ nhỏ)."""
    wi.Site(fake_wp)
    original = image_html.sanitize_html
    monkeypatch.setattr(image_html, "sanitize_html",
                        lambda text: re.sub(r' srcset="[^"]*"', "", original(text)))
    image = DraftImage(make_web_image(wi._jpeg()), alt="Cổng sắt")
    with pytest.raises(WordPressError):
        wp_client.create_draft_with_images("Sửa cổng", ["<p>x</p>", image])
    assert not [r for r in fake_wp.requests if r.method == "POST" and path(r) == POSTS]
