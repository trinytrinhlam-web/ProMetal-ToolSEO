"""Soi Lỗi · T-054: thử phá «gửi nháp kèm ảnh» (``create_draft_with_images``, ``figure_html``).

Chỉ site giả (``FakeWordPress``), không gọi WordPress thật. Ảnh là ảnh giả tạo trong bộ nhớ (không
commit ảnh thật), GPS là tọa độ giả, tên khách là tên giả.

Test ``xfail(strict=True)`` là lỗi tìm được (SL-T054-1…3 trong
``docs/team/reports/T-054-soi-loi.md``): sửa xong thì test thành XPASS và báo hỏng, khi đó chỉ
cần xóa dòng ``@pytest.mark.xfail``. SL-T054-2 đã sửa ở T-061, SL-T054-1 và SL-T054-3 ở T-071
(đã gỡ ``xfail``).
"""

import base64
import html
import io
import json
import re
import unicodedata
from fractions import Fraction
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlsplit

import pytest
import requests
from fake_wordpress import BASE_URL
from PIL import ExifTags, Image
from PIL.TiffImagePlugin import IFDRational
from pillow_heif import options as heif_options

import seo_app.images.naming as naming
import seo_app.wordpress.client as client_module
from seo_app.images import html as image_html
from seo_app.images.alt import AltSuggestion, clean_suggestion
from seo_app.images.process import make_web_image
from seo_app.images.tags import SOURCE_AI, ImageTags, TagError
from seo_app.sanitize import AUTOLINK_BREAK, clean_ai_text, escape_shortcodes, sanitize_html
from seo_app.wordpress import WordPressError
from seo_app.wordpress.client import (
    MAX_ID,
    DraftImage,
    DraftImagesError,
    DraftWithImages,
    WordPressClient,
)

_PILLOW_REGISTRIES = ("ID", "OPEN", "MIME", "SAVE", "SAVE_ALL", "EXTENSION")
_HEIF_OPTIONS = ("THUMBNAILS", "DEPTH_IMAGES", "AUX_IMAGES", "DISABLE_SECURITY_LIMITS")


@pytest.fixture(autouse=True)
def _pillow_state_restored():
    """Trả nguyên bảng định dạng của Pillow và tùy chọn pillow-heif sau mỗi test (như
    ``tests/test_wordpress_images.py``): ``make_web_image`` đăng ký HEIF khi mở ảnh."""
    Image.init()
    saved = {name: getattr(Image, name).copy() for name in _PILLOW_REGISTRIES}
    options = {name: getattr(heif_options, name) for name in _HEIF_OPTIONS}
    yield
    for name, value in saved.items():
        current = getattr(Image, name)
        current.clear()
        if isinstance(current, dict):
            current.update(value)
        else:
            current.extend(value)
    for name, value in options.items():
        setattr(heif_options, name, value)


# ----- dữ liệu giả ---------------------------------------------------------------------------

R = IFDRational
POSTS = "/wp-json/wp/v2/posts"
MEDIA = "/wp-json/wp/v2/media"
UPLOADS = f"{BASE_URL}/wp-content/uploads/2026/10/"
FIRST_ID = 101
KHOA_GIA = "abcd efgh ijkl"  # khóa giả của fixture ``wp_client``
CUSTOMER = ("Tuấn", "Tuan", "Lê Lợi", "IMG_1234", "SN987654321", "CT012 - Nhà")


def _jpeg(size=(320, 240), *, gps=None, extra=None, exif_ifd=None, color=(200, 80, 40)):
    exif = Image.Exif()
    exif[ExifTags.Base.Make] = "Apple"
    exif[ExifTags.Base.Model] = "iPhone 15"
    for tag, value in (extra or {}).items():
        exif[tag] = value
    if exif_ifd:
        ifd = exif.get_ifd(ExifTags.IFD.Exif)
        ifd.update(exif_ifd)
    if gps:
        g = exif.get_ifd(ExifTags.IFD.GPSInfo)
        g.update(gps)
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, "JPEG", exif=exif.tobytes(), quality=85)
    return buffer.getvalue()


GPS_NE = {0: b"\x02\x02\x00\x00", 1: "N", 2: (R(10), R(46), R(3456, 100)), 3: "E",
          4: (R(106), R(41), R(1234, 100))}  # fmt: skip


@pytest.fixture(scope="module")
def web():
    image = make_web_image(_jpeg(gps=GPS_NE))
    assert image.gps is not None
    return image


@pytest.fixture(scope="module")
def web2():
    return make_web_image(_jpeg((200, 300), color=(30, 120, 200)))


def _value(value):
    if isinstance(value, IFDRational):
        return Fraction(value.numerator, value.denominator)
    if isinstance(value, tuple):
        return tuple(_value(v) for v in value)
    return value


def _gps(data):
    image = Image.open(io.BytesIO(data))
    image.load()
    return {tag: _value(v) for tag, v in image.getexif().get_ifd(ExifTags.IFD.GPSInfo).items()}


def path(request):
    return urlsplit(request.url).path


def body(request):
    return json.loads(request.body) if request.body else None


def uploads(fake_wp):
    return [r for r in fake_wp.requests if r.method == "POST" and path(r) == MEDIA]


def describes(fake_wp):
    return [r for r in fake_wp.requests if r.method == "POST" and path(r).startswith(MEDIA + "/")]


def creates(fake_wp):
    return [r for r in fake_wp.requests if r.method == "POST" and path(r) == POSTS]


def sent_content(fake_wp):
    sent = creates(fake_wp)
    assert len(sent) == 1
    return body(sent[0])["content"]


def file_names(fake_wp):
    names = []
    for request in uploads(fake_wp):
        disposition = request.headers["Content-Disposition"]
        names.append(re.fullmatch(r'attachment; filename="([^"]+)"', disposition).group(1))
    return names


class Site:
    """Site giả: Media cấp mã từ 101, bài nháp ``post_id`` (mặc định 42)."""

    def __init__(self, fake_wp, *, post_id=42, post_status="draft"):
        self.fake_wp = fake_wp
        self.next_id = FIRST_ID
        self.files = {}
        self.post_id = post_id
        self.post_status = post_status
        fake_wp.on("POST", MEDIA, self.create_media)
        for media_id in range(FIRST_ID, FIRST_ID + 30):
            fake_wp.on("POST", f"{MEDIA}/{media_id}", self.update_media)
        fake_wp.on("POST", POSTS, self.create_post)
        fake_wp.on("GET", f"{POSTS}/{post_id}", self.get_post)
        fake_wp.on("POST", f"{POSTS}/{post_id}", self.update_post)

    def source_url(self, media_id):
        return f"{UPLOADS}{self.files[media_id]}"

    def create_media(self, request):
        disposition = request.headers["Content-Disposition"]
        name = re.fullmatch(r'attachment; filename="([^"]+)"', disposition).group(1)
        media_id = self.next_id
        self.next_id += 1
        self.files[media_id] = name
        return (201, {"id": media_id, "source_url": self.source_url(media_id), "post": None}, {})

    def update_media(self, request):
        media_id = int(path(request).rsplit("/", 1)[1])
        return {"id": media_id, "source_url": self.source_url(media_id), **body(request)}

    def create_post(self, request):
        return (201, {"id": self.post_id, "status": self.post_status, "title": {"raw": "T"}}, {})

    def get_post(self, _request):
        return {"id": self.post_id, "status": self.post_status, "meta": {}}

    def update_post(self, request):
        return {"id": self.post_id, "status": self.post_status, **body(request)}


@pytest.fixture
def site(fake_wp):
    return Site(fake_wp)


def send(client, parts, title="Sửa cổng inox Tân Phú", **kwargs):
    return client.create_draft_with_images(title, parts, **kwargs)


class _Figures(HTMLParser):
    """Đọc nội dung như trình duyệt: thẻ, thuộc tính (đã giải mã), chữ trong ``<figcaption>``."""

    def __init__(self, content):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.imgs = []
        self.captions = []
        self._in_caption = False
        self.feed(content)
        self.close()

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, [name for name, _ in attrs]))
        if tag == "img":
            self.imgs.append(dict(attrs))
        elif tag == "figcaption":
            self._in_caption = True
            self.captions.append("")

    def handle_endtag(self, tag):
        if tag == "figcaption":
            self._in_caption = False

    def handle_data(self, data):
        if self._in_caption:
            self.captions[-1] += data


def _no_cf(text):
    return not [ch for ch in text if unicodedata.category(ch) == "Cf"]


# ===== Yêu cầu 2 · byte gửi lên đúng WebImage.data, GPS đúng giá trị ========================


def test_anh_lon_kieu_dien_thoai_gps_nam_tay_den_web_dung_tung_gia_tri(fake_wp, wp_client, site):
    gps = {
        0: b"\x02\x03\x00\x00",
        1: "S",
        2: (R(33), R(52), R(1234, 100)),
        3: "W",
        4: (R(151), R(12), R(5678, 100)),
        5: b"\x00",
        6: R(1234, 10),
    }
    original = _jpeg((4032, 3024), gps=gps)
    web = make_web_image(original)
    assert (web.width, web.height) == (1600, 1200)  # file đầy đủ 1600 px (5A)

    send(wp_client, ["<p>Mở bài</p>", DraftImage(web, alt="Cổng inox 4 cánh")])
    sent = uploads(fake_wp)[0].body
    assert type(sent) is bytes and sent == web.data
    assert Image.open(io.BytesIO(sent)).size == (1600, 1200)
    back = _gps(sent)
    assert back[1] == "S" and back[3] == "W"
    assert back[2] == (Fraction(33), Fraction(52), Fraction(1234, 100))
    assert back[4] == (Fraction(151), Fraction(12), Fraction(5678, 100))
    assert back[6] == Fraction(1234, 10)
    img = _Figures(sent_content(fake_wp)).imgs[0]
    assert (img["width"], img["height"]) == ("1600", "1200")  # cỡ thật của file vừa gửi


def test_byte_va_moi_lenh_gui_di_khong_co_ten_khach_ten_file_goc(fake_wp, wp_client, site):
    # Chữ có dấu ghi dạng byte UTF-8 (như điện thoại, Windows ghi); Pillow tự đổi chuỗi str sang
    # ASCII nên phải đưa byte vào.
    folder = r"D:\Anh\CT012 - Nhà anh Tuấn - 12 Lê Lợi\IMG_1234.JPG"
    original = _jpeg(
        gps=GPS_NE,
        extra={
            ExifTags.Base.ImageDescription: folder.encode("utf-8"),
            ExifTags.Base.Artist: "Nguyễn Văn Tuấn".encode(),
            ExifTags.Base.Copyright: "Tuấn Lê Lợi".encode(),
            0x9C9C: "Nhà anh Tuấn IMG_1234".encode("utf-16le") + b"\x00\x00",  # XPComment
        },
        exif_ifd={
            ExifTags.Base.BodySerialNumber: "SN987654321",
            ExifTags.Base.CameraOwnerName: "Tuấn Lê Lợi".encode(),
        },
    )
    assert b"SN987654321" in original and "Tuấn".encode() in original  # tiền đề: ảnh gốc có
    web = make_web_image(original)
    send(
        wp_client,
        [DraftImage(web, alt="Cổng inox", tags=ImageTags(category="Cổng inox", area="Tân Phú"))],
    )

    assert file_names(fake_wp) == ["cong-inox-tan-phu.webp"]
    for request in fake_wp.requests:
        if path(request) == MEDIA:
            raw = request.body
        else:  # JSON: so trên chữ đã giải mã (requests gửi \uXXXX cho chữ có dấu)
            raw = json.dumps(body(request), ensure_ascii=False).encode() if request.body else b""
        everything = raw + str(dict(request.headers)).encode() + request.url.encode()
        for word in CUSTOMER:
            for encoded in (word.encode("utf-8"), word.encode("utf-16le")):
                assert encoded not in everything, word
    assert _gps(uploads(fake_wp)[0].body)[2] == (Fraction(10), Fraction(46), Fraction(3456, 100))


def test_hai_draft_image_dung_chung_mot_webimage_gui_hai_lan_dung_byte(
    fake_wp, wp_client, site, web
):
    first, second = DraftImage(web, alt="Cổng trước"), DraftImage(web, alt="Cổng sau")
    result = send(wp_client, [first, "<p>giữa</p>", second])
    assert [r.body for r in uploads(fake_wp)] == [web.data, web.data]
    assert file_names(fake_wp) == ["cong-truoc.webp", "cong-sau.webp"]
    imgs = _Figures(sent_content(fake_wp)).imgs
    assert [(i["src"], i["alt"]) for i in imgs] == [
        (f"{UPLOADS}cong-truoc.webp", "Cổng trước"),
        (f"{UPLOADS}cong-sau.webp", "Cổng sau"),
    ]
    assert result.featured_media == FIRST_ID


# ===== Yêu cầu 2 · tên file chỉ từ naming.image_file_name ====================================


def test_ten_file_chi_lay_tu_image_file_name(fake_wp, wp_client, site, web, monkeypatch):
    calls = []
    real = naming.image_file_name

    def spy(**kwargs):
        kwargs["taken"] = list(kwargs.get("taken", ()))
        name = real(**kwargs)
        calls.append((kwargs, name))
        return name

    monkeypatch.setattr(naming, "image_file_name", spy)
    alt = clean_ai_text("Bản lề cổng www.prometal.vn")
    send(
        wp_client,
        [
            DraftImage(
                web,
                alt=alt,
                tags=ImageTags(category="Cổng inox", area="Tân Phú", project_code="CT012"),
            ),
            DraftImage(
                web, alt="Minh họa cổng", tags=ImageTags(source=SOURCE_AI, category="Cổng inox")
            ),
        ],
    )
    assert file_names(fake_wp) == [name for _, name in calls]
    for kwargs, _ in calls:
        assert set(kwargs) <= {"category", "area", "project_code", "alt", "ai_generated", "taken"}
        assert AUTOLINK_BREAK not in kwargs["alt"]  # alt đã duyệt, đã gỡ ký tự ngắt
    assert calls[1][0]["taken"] == [calls[0][1]]


@pytest.mark.parametrize(
    "category",
    [
        'x"; filename="shell.php',
        "a\r\nX-Evil: 1",
        "../../wp-config.php",
        r"C:\Users\An\Ảnh\CT012 - Nhà anh Tuấn\cong.php",
        "%2e%2e%2fshell.php",
        "<script>alert(1)</script>",
        "\u202egnp.php",
    ],
)
def test_ten_file_khong_the_chen_header_hay_doi_duoi(
    fake_wp, wp_client, site, web, category
):
    # T-071 (LC-T054-4): thẻ chỉ nhận ``ImageTags``, chuỗi độc không thành thẻ được, và thẻ
    # không phải ``ImageTags`` bị từ chối trước mọi request.
    with pytest.raises(TagError):
        ImageTags(category=category)
    with pytest.raises(WordPressError):
        send(wp_client, [DraftImage(web, alt="Cổng", tags=category)])
    assert fake_wp.requests == []
    # Chữ tự do còn vào tên file là alt (ảnh không có thẻ): chuỗi độc đi qua cùng
    # ``image_file_name`` như ``category`` trước đây.
    send(wp_client, [DraftImage(web, alt=category)])
    disposition = uploads(fake_wp)[0].headers["Content-Disposition"]
    assert re.fullmatch(r'attachment; filename="[a-z0-9-]+\.webp"', disposition)
    assert "\r" not in disposition and "\n" not in disposition


# ===== Yêu cầu 3 · alt/chú thích độc trong <figure>, REST alt_text ===========================

NASTY = {
    "thẻ html, nháy": '"><img src=x onerror=alert(1)> \'x\'',
    "đóng figure": "</figcaption></figure><script>alert(1)</script><p>",
    "javascript:": "<a href='javascript:alert(1)'>bấm</a> javascript:alert(1)",
    "mã ký tự": "Cổng &lt;b&gt; &amp;quot; &#34; &#x27; &#0; &",
    "chữ AI có link": clean_ai_text(
        'Cổng "Pro" [mẫu](javascript:alert(1)) www.prometal.vn a@b.vn https://evil.com/x'
    ),
    "escape markdown": clean_ai_text("[Lưu ý](chữ có cách) [a][b] cổng sắt"),
    "ký tự rộng 0": "C\u200bổng\u200c\u200d\ufeff\u2060 inox\u00ad",
    "hướng chữ": "Cổng\u202einox\u2066x\u2069\u200e\u200f\u061c\u202a\u202b\u202c\u202d",
    "điều khiển": "Cổng\x00 sắt\x1f\x7f\x85 mới\r\n\tđẹp",
    "comment, cdata": "<!-- x --> ]]> <![CDATA[x]]> <?php echo 1; ?>",
    "tổ hợp NFD": unicodedata.normalize("NFD", "Cổng inox Tân Phú"),
    "rất dài": "Cổng sắt " * 55,
}


@pytest.mark.parametrize("case", list(NASTY))
def test_alt_chu_thich_doc_chi_con_la_chu(fake_wp, wp_client, site, web, case):
    text = NASTY[case]
    plain = image_html.plain_image_text(text)
    assert plain and len(plain) <= client_module.MAX_IMAGE_ALT_CHARS
    send(wp_client, ["<p>Mở bài</p>", DraftImage(web, alt=text, caption=text)])

    content = sent_content(fake_wp)
    page = _Figures(content)
    # Trình duyệt chỉ thấy đúng các thẻ do code dựng, img chỉ 5 thuộc tính do code đặt
    # (srcset một ứng viên là file đầy đủ: T-059).
    assert page.tags == [
        ("p", []),
        ("figure", ["class"]),
        ("img", ["src", "alt", "srcset", "width", "height"]),
        ("figcaption", []),
    ]
    assert page.imgs[0]["alt"] == plain
    assert page.imgs[0]["src"] == f"{UPLOADS}{file_names(fake_wp)[0]}"
    assert page.captions == [plain]
    assert _no_cf(content) and "\x00" not in content
    assert sanitize_html(content) == content  # kết quả cuối đã qua bộ lọc, ổn định

    update = body(describes(fake_wp)[0])
    # Chữ thường đã gỡ ký tự rộng 0 (REST); T-061: "[", "]" ra "&#91;", "&#93;" (shortcode).
    assert update["alt_text"] == escape_shortcodes(plain)
    for field in ("title", "caption"):
        assert html.unescape(update[field]) == plain
        assert not set(update[field]) & set('<>"')
    for value in update.values():
        assert _no_cf(value) and AUTOLINK_BREAK not in value


def test_gioi_han_do_dai_tinh_tren_chu_da_lam_sach(fake_wp, wp_client, site, web):
    alt = "a" * client_module.MAX_IMAGE_ALT_CHARS + "\u200b" * 5000 + "\u202e" * 100
    caption = "b" * client_module.MAX_IMAGE_CAPTION_CHARS
    send(wp_client, [DraftImage(web, alt=alt, caption=caption)])
    update = body(describes(fake_wp)[0])
    assert update["alt_text"] == "a" * client_module.MAX_IMAGE_ALT_CHARS
    assert update["caption"] == caption


@pytest.mark.parametrize(
    ("alt", "caption"),
    [("a" * 501, ""), ("a", "b" * 1001), ("\u200b\u202e\u2066 \u00ad\ufeff", "")],
)
def test_alt_chu_thich_qua_dai_hay_rong_thi_chua_gui_gi(
    fake_wp, wp_client, site, web, alt, caption
):
    with pytest.raises(WordPressError):
        send(wp_client, [DraftImage(web, alt=alt, caption=caption)])
    assert fake_wp.requests == []


def test_tien_de_sl_t054_1_chu_ai_cho_anh_ai_con_dau_escape_markdown():
    """Tiền đề của SL-T054-1 (để xfail bên dưới không qua oan): ``clean_suggestion`` cho ảnh AI
    ghép tiền tố «Minh họa» trước chữ đã ``clean_ai_text``, nên «]\\:» không còn ở đầu dòng."""
    suggestion = clean_suggestion(
        AltSuggestion(alt="[Trước khi sửa]: cổng sắt gỉ sét", caption="[Lưu ý]: sơn lại cổng"),
        ai_generated=True,
    )
    assert suggestion.alt == "Minh họa [Trước khi sửa]\\: cổng sắt gỉ sét"
    assert suggestion.caption == "Ảnh minh họa (AI): [Lưu ý]\\: sơn lại cổng"


def test_anh_that_chu_ai_mo_dau_ngoac_vuong_khong_con_dau_gach_cheo(fake_wp, wp_client, site, web):
    suggestion = clean_suggestion(
        AltSuggestion(alt="[Trước khi sửa]: cổng sắt gỉ sét", caption="[Lưu ý]: sơn lại cổng")
    )
    assert "\\" in suggestion.alt  # chữ AI còn escape Markdown của clean_ai_text
    send(wp_client, [DraftImage(web, alt=suggestion.alt, caption=suggestion.caption)])
    assert "\\" not in sent_content(fake_wp)
    assert "\\" not in json.dumps(body(describes(fake_wp)[0]), ensure_ascii=False)


def test_sl_t054_1_anh_ai_chu_mo_dau_ngoac_vuong_con_dau_gach_cheo(fake_wp, wp_client, site, web):
    suggestion = clean_suggestion(
        AltSuggestion(alt="[Trước khi sửa]: cổng sắt gỉ sét", caption="[Lưu ý]: sơn lại cổng"),
        ai_generated=True,
    )
    image = DraftImage(
        web, alt=suggestion.alt, caption=suggestion.caption, tags=ImageTags(source=SOURCE_AI)
    )
    send(wp_client, [image])
    page = _Figures(sent_content(fake_wp))
    assert page.imgs[0]["alt"] == "Minh họa [Trước khi sửa]: cổng sắt gỉ sét"
    assert page.captions == ["Ảnh minh họa (AI): [Lưu ý]: sơn lại cổng"]
    update = body(describes(fake_wp)[0])
    # T-061: "[", "]" của alt_text ra "&#91;", "&#93;" (shortcode); lỗi kiểm ở đây vẫn là dấu "\".
    assert update["alt_text"] == escape_shortcodes("Minh họa [Trước khi sửa]: cổng sắt gỉ sét")
    assert "\\" not in update["caption"] and "\\" not in update["title"]


def _shortcode_reached(fake_wp):
    """Shortcode còn nguyên dạng (WordPress sẽ chạy) trong nội dung bài gửi đi."""
    return re.search(r"\[\s*/?\s*code_snippet", sent_content(fake_wp)) is not None


def test_sl_t054_2_shortcode_trong_chu_thich(fake_wp, wp_client, site, web):
    try:
        send(wp_client, [DraftImage(web, alt="Cổng", caption="[code_snippet id=1] sơn lại")])
    except WordPressError:
        assert creates(fake_wp) == []  # chặn trước khi tạo nháp cũng là đạt
        return
    assert not _shortcode_reached(fake_wp)


def test_sl_t054_2_shortcode_trong_alt(fake_wp, wp_client, site, web):
    try:
        send(wp_client, [DraftImage(web, alt="[code_snippet id=1] cổng")])
    except WordPressError:
        assert creates(fake_wp) == []
        return
    assert not _shortcode_reached(fake_wp)


# ===== Yêu cầu 1 · chỉ tải ảnh khi gọi gửi nháp =============================================


def test_chuan_bi_anh_khong_goi_mang_va_khong_qua_upload_media(
    fake_wp, wp_client, site, web, monkeypatch
):
    image = DraftImage(web, alt=clean_ai_text("Cổng www.prometal.vn"), caption="Sau khi sơn")
    image_html.figure_html(
        src=f"{UPLOADS}a.webp", alt=image.alt, caption=image.caption, width=10, height=10
    )
    planned, featured = wp_client._plan_draft_images((image, "<p>x</p>"))
    assert featured is image and len(planned) == 1
    assert fake_wp.requests == []  # dựng ảnh, HTML, kiểm trước: không gửi gì

    def no_upload(*_args, **_kwargs):
        raise AssertionError("gửi nháp kèm ảnh không được đi qua upload_media")

    monkeypatch.setattr(WordPressClient, "upload_media", no_upload)
    send(wp_client, [image])
    assert len(uploads(fake_wp)) == 1


def test_danh_sach_parts_bi_doi_trong_luc_gui_khong_anh_huong(fake_wp, wp_client, site, web, web2):
    parts = ["<p>a</p>", DraftImage(web, alt="Ảnh một")]

    def mutate(request):
        parts.append(DraftImage(web2, alt="Ảnh chen vào"))
        parts[0] = "<p>đã đổi</p>"
        return site.create_media(request)

    fake_wp.on("POST", MEDIA, mutate)
    result = send(wp_client, parts)
    assert len(uploads(fake_wp)) == 1 and len(result.images) == 1
    content = sent_content(fake_wp)
    assert content.startswith("<p>a</p>")
    assert "đã đổi" not in content and "chen vào" not in content


def test_mat_mang_o_anh_thu_muoi_liet_ke_du_chin_anh_khong_xoa(fake_wp, wp_client, site, web):
    images = [DraftImage(web, alt=f"Cổng số {n}") for n in range(1, 13)]
    count = {"n": 0}

    def flaky(request):
        count["n"] += 1
        if count["n"] == 10:
            return requests.exceptions.ConnectionError("mất mạng")
        return site.create_media(request)

    fake_wp.on("POST", MEDIA, flaky)
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, images)
    err = error.value
    assert [image.id for image in err.uploaded] == list(range(FIRST_ID, FIRST_ID + 9))
    assert all(image.source_url.startswith(UPLOADS) for image in err.uploaded)
    assert err.maybe_uploaded is True  # ảnh thứ 10 có thể đã lên
    assert "9 ảnh" in str(err) and "không xóa" in str(err)
    assert len(uploads(fake_wp)) == 10 and creates(fake_wp) == []
    assert {r.method for r in fake_wp.requests} == {"POST"}


# ===== Yêu cầu 4 · chỉ nháp, chỉ bài app tạo, đường REST cố định ============================


@pytest.mark.parametrize(
    "kwargs",
    [{"status": "publish"}, {"status": "future"}, {"featured_media": 7}, {"date": "2026-10-21"}],
)
def test_khong_co_cach_truyen_trang_thai_hay_ngay_dang(fake_wp, wp_client, site, web, kwargs):
    with pytest.raises(TypeError):
        send(wp_client, [DraftImage(web, alt="Cổng")], **kwargs)
    assert fake_wp.requests == []


def test_moi_lenh_deu_qua_danh_sach_duong_khong_tham_so_la(
    fake_wp, wp_client, site, web, web2, monkeypatch
):
    asked = []
    real = client_module.is_allowed_route

    def spy(method, route):
        allowed = real(method, route)
        asked.append((method, route, allowed))
        return allowed

    monkeypatch.setattr(client_module, "is_allowed_route", spy)
    parts = ["<p>a</p>", DraftImage(web, alt="A"), DraftImage(web2, alt="B", featured=True)]
    send(wp_client, parts, categories=[3], tags=[7], excerpt="Tóm tắt")
    sent = [(r.method, path(r).removeprefix("/wp-json")) for r in fake_wp.requests]
    assert [(method, route) for method, route, _ in asked] == sent
    assert all(allowed for *_, allowed in asked)
    for request in fake_wp.requests:
        assert request.method in ("GET", "POST")
        assert not [name for name in request.headers if "override" in name.lower()]
        query = parse_qs(urlsplit(request.url).query)
        if request.method == "GET":  # chỉ lệnh kiểm nháp của _own_draft (T-042)
            assert query == {"context": ["edit"], "_fields": ["id,status,meta"]}
        elif path(request).startswith(MEDIA + "/") and body(request) == {"post": 42}:
            # T-110 (Chỉ Huy duyệt 30/10): lệnh gắn ảnh vào bài nháp.
            assert query == {"_fields": ["id,post"]}
        elif path(request) == MEDIA:  # T-110 lượt 2 (Chỉ Huy duyệt 30/10 20:25): lệnh tải ảnh
            assert query == {"_fields": ["id,source_url,alt_text,post"]}
        elif path(request).startswith(MEDIA):  # T-061: ``_fields`` cố định, không ``description``
            assert query == {"_fields": ["id,source_url,alt_text"]}
        else:  # T-061: ``_fields`` cố định, không ``content``, ``excerpt``
            assert query == {"_fields": ["id,status,title,link,featured_media"]}


def test_duong_bi_go_khoi_danh_sach_thi_khong_gui(fake_wp, wp_client, site, web, monkeypatch):
    kept = tuple(
        (method, pattern)
        for method, pattern in client_module._ALLOWED_ROUTES
        if not (method == "POST" and pattern.pattern.startswith("/wp/v2/media/"))
    )
    monkeypatch.setattr(client_module, "_ALLOWED_ROUTES", kept)
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, [DraftImage(web, alt="Cổng")])
    assert [(r.method, path(r)) for r in fake_wp.requests] == [("POST", MEDIA)]
    assert [image.id for image in error.value.uploaded] == [FIRST_ID]
    assert "danh sách được phép" in str(error.value)


def test_anh_dai_dien_chi_ghi_vao_bai_nhap_vua_tao(fake_wp, wp_client, web, web2):
    Site(fake_wp, post_id=43)
    result = send(wp_client, [DraftImage(web, alt="A"), DraftImage(web2, alt="B", featured=True)])
    calls = [(r.method, path(r)) for r in fake_wp.requests if path(r).startswith(POSTS)]
    assert calls == [("POST", POSTS), ("GET", f"{POSTS}/43"), ("POST", f"{POSTS}/43")]
    assert body(fake_wp.requests[-1]) == {"featured_media": FIRST_ID + 1}
    assert body(creates(fake_wp)[0])["status"] == "draft"
    assert result.post.id == 43 and result.featured_media == FIRST_ID + 1


@pytest.mark.parametrize("status", ["publish", "future", "pending", "private", ""])
def test_site_tao_bai_khong_phai_nhap_thi_khong_ghi_them(fake_wp, wp_client, web, status):
    Site(fake_wp, post_status=status)
    result = send(wp_client, [DraftImage(web, alt="Cổng")])
    assert body(creates(fake_wp)[0])["status"] == "draft"
    assert fake_wp.requests[-1] is creates(fake_wp)[0]  # sau lệnh tạo không còn lệnh nào
    assert result.featured_media is None and "chưa đặt được ảnh đại diện" in result.message


# ===== WordPress giả trả lỗi 401/403/404/500 ở từng bước ====================================

STEPS = {
    "tải ảnh": ("POST", MEDIA),
    "ghi alt": ("POST", f"{MEDIA}/{FIRST_ID}"),
    "tạo nháp": ("POST", POSTS),
    "kiểm nháp": ("GET", f"{POSTS}/42"),
    "ảnh đại diện": ("POST", f"{POSTS}/42"),
}
AUTH = base64.b64encode(f"lam:{KHOA_GIA.replace(' ', '')}".encode()).decode()


@pytest.mark.parametrize("code", [401, 403, 404, 500])
@pytest.mark.parametrize("step", list(STEPS))
def test_loi_http_o_tung_buoc(fake_wp, wp_client, site, web, step, code):
    fake_wp.on(*STEPS[step], (code, {"code": "loi_gia", "message": "lỗi giả"}, {}))
    image = DraftImage(web, alt="Cổng")
    if step in ("kiểm nháp", "ảnh đại diện"):
        result = send(wp_client, [image])  # bài nháp và ảnh vẫn còn: không ném lỗi
        assert isinstance(result, DraftWithImages)
        assert result.featured_media is None and [i.id for i in result.images] == [FIRST_ID]
        assert "chưa đặt được ảnh đại diện" in result.message
        if step == "kiểm nháp":
            assert ("POST", f"{POSTS}/42") not in [(r.method, path(r)) for r in fake_wp.requests]
        text = result.message
    else:
        with pytest.raises(DraftImagesError) as error:
            send(wp_client, [image])
        err = error.value
        assert err.status_code == code
        assert [i.id for i in err.uploaded] == ([] if step == "tải ảnh" else [FIRST_ID])
        assert err.maybe_uploaded is (step == "tải ảnh" and code >= 500)
        if step != "tạo nháp":
            assert creates(fake_wp) == []
        text = str(err)
    assert {r.method for r in fake_wp.requests} <= {"GET", "POST"}  # không xóa gì (W2)
    for secret in (KHOA_GIA, KHOA_GIA.replace(" ", ""), AUTH):
        assert secret not in text


# ===== WordPress giả trả dữ liệu sai kiểu, mã lạ ============================================


@pytest.mark.parametrize(
    "answer",
    [
        (201, [], {}),
        (201, "ok", {}),
        (201, None, {}),
        (201, {"id": "101", "source_url": f"{UPLOADS}a.webp"}, {}),
        (201, {"id": 101.0}, {}),
        (201, {"id": True}, {}),
        (201, {"id": 0}, {}),
        (201, {"id": -101}, {}),
        (201, {"source_url": f"{UPLOADS}a.webp"}, {}),
        (200, "<html>Website bảo trì</html>".encode(), {}),
    ],
)
def test_tai_anh_tra_du_lieu_sai_kieu_thi_dung(fake_wp, wp_client, site, web, answer):
    fake_wp.on("POST", MEDIA, answer)
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, [DraftImage(web, alt="Cổng")])
    assert error.value.uploaded == () and error.value.maybe_uploaded is True
    assert [(r.method, path(r)) for r in fake_wp.requests] == [("POST", MEDIA)]


@pytest.mark.parametrize("huge", [10**19, 2**63], ids=["10^19", "2^63"])
def test_ma_anh_qua_lon_bi_danh_sach_duong_chan(fake_wp, wp_client, site, web, huge):
    """T-091 (Chỉ Huy duyệt phương án A 28/10): mã ảnh quá ``MAX_ID`` (2⁶³−1) như mã sai khuôn,
    giống ``test_tai_anh_tra_du_lieu_sai_kieu_thi_dung`` (trước: client nhận mã, liệt kê
    ``uploaded == [huge]``, lệnh ghi alt bị danh sách đường chặn). Giữ: chỉ một lệnh tải, không
    lệnh nào gọi tiếp với mã quá lớn, câu báo nói ảnh có thể đã lên thư viện Media."""
    fake_wp.on("POST", MEDIA, (201, {"id": huge, "source_url": f"{UPLOADS}a.webp"}, {}))
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, [DraftImage(web, alt="Cổng")])
    assert [(r.method, path(r)) for r in fake_wp.requests] == [("POST", MEDIA)]
    assert error.value.uploaded == () and error.value.maybe_uploaded is True
    assert "thư viện Media" in str(error.value) and str(huge) not in str(error.value)


def test_ma_anh_bang_gioi_han_van_nhan(fake_wp, wp_client, site, web):
    """Biên T-091: mã ảnh đúng ``MAX_ID`` (2⁶³−1) vẫn hợp lệ: ghi alt, tạo nháp bình thường."""
    site.next_id = MAX_ID
    fake_wp.on("POST", f"{MEDIA}/{MAX_ID}", site.update_media)
    result = send(wp_client, [DraftImage(web, alt="Cổng")])
    assert [image.id for image in result.images] == [MAX_ID]
    assert [(r.method, path(r)) for r in fake_wp.requests][:2] == [
        ("POST", MEDIA), ("POST", f"{MEDIA}/{MAX_ID}")
    ]


@pytest.mark.parametrize("answer", [[], None, "ok", {}, {"id": "101"}, {"id": 102}, {"id": True}])
def test_ghi_alt_tra_du_lieu_sai_thi_dung(fake_wp, wp_client, site, web, answer):
    fake_wp.on("POST", f"{MEDIA}/{FIRST_ID}", (200, answer, {}))
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, [DraftImage(web, alt="Cổng")])
    assert "không khớp" in str(error.value)
    assert [image.id for image in error.value.uploaded] == [FIRST_ID]
    assert error.value.maybe_uploaded is False and creates(fake_wp) == []


@pytest.mark.parametrize(
    "answer",
    [
        (201, [], {}),
        (201, {"id": "42", "status": "draft"}, {}),
        (201, {"status": "draft"}, {}),
        (200, b"<html></html>", {}),
    ],
)
def test_tao_nhap_tra_du_lieu_sai_van_liet_ke_anh(fake_wp, wp_client, site, web, answer):
    fake_wp.on("POST", POSTS, answer)
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, [DraftImage(web, alt="Cổng")])
    assert [image.id for image in error.value.uploaded] == [FIRST_ID]
    assert error.value.uploaded[0].source_url == f"{UPLOADS}cong.webp"
    assert [(r.method, path(r)) for r in fake_wp.requests][-1] == ("POST", POSTS)


@pytest.mark.parametrize(
    "answer",
    [
        (201, {"id": "42", "status": "draft"}, {}),
        requests.exceptions.ReadTimeout("hết giờ"),
        (502, {"code": "x", "message": "x"}, {}),
    ],
)
def test_sl_t054_3_loi_sau_lenh_tao_nhap_phai_bao_bai_nhap_co_the_da_co(
    fake_wp, wp_client, site, web, answer
):
    fake_wp.on("POST", POSTS, answer)
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, [DraftImage(web, alt="Cổng")])
    message = str(error.value)
    assert "Chưa tạo bài nháp" not in message
    assert re.search(r"nháp[^.]*có thể|có thể[^.]*nháp", message)


# ===== source_url WordPress trả về ==========================================================


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com:8443/wp-content/uploads/a.webp",
        "https://user@example.com/wp-content/uploads/a.webp",
        "https://example.com.evil.com/a.webp",
        "https://exаmple.com/a.webp",  # chữ «а» Kirin
        "https://example.com./a.webp",
        "https://evil.com/https://example.com/a.webp",
        "https:example.com/a.webp",
        "//example.com/a.webp",
        "/wp-content/uploads/a.webp",
        'https://example.com/a.webp"onerror="alert(1)',
        "https://example.com/a​.webp",
        "https://example.com/a.webp\n",
        "https://example.com/a\\b.webp",
        "ftp://example.com/a.webp",
        "data:image/webp;base64,AAAA",
        "https://example.com/" + "a" * 2000,
        5,
        None,
        {"raw": "https://example.com/a.webp"},
        ["https://example.com/a.webp"],
    ],
)
def test_source_url_ngoai_site_thi_dung_truoc_khi_tao_nhap(fake_wp, wp_client, site, web, url):
    fake_wp.on("POST", MEDIA, (201, {"id": FIRST_ID, "source_url": url, "post": None}, {}))
    fake_wp.on("POST", f"{MEDIA}/{FIRST_ID}", {"id": FIRST_ID, "source_url": url})
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, [DraftImage(web, alt="Cổng")])
    assert "không phải https trên đúng website" in str(error.value)
    assert [image.id for image in error.value.uploaded] == [FIRST_ID]
    assert creates(fake_wp) == []


@pytest.mark.parametrize(
    "url",
    [
        "https://EXAMPLE.com/wp-content/uploads/a.webp",
        "https://example.com:443/wp-content/uploads/a.webp",
        "https://example.com/wp-content/uploads/a%22b.webp?v=1&x=2#f",
    ],
)
def test_source_url_hop_le_dang_la_vao_src_nguyen_van(fake_wp, wp_client, site, web, url):
    fake_wp.on("POST", MEDIA, (201, {"id": FIRST_ID, "source_url": url, "post": None}, {}))
    fake_wp.on("POST", f"{MEDIA}/{FIRST_ID}", {"id": FIRST_ID, "source_url": url})
    send(wp_client, [DraftImage(web, alt="Cổng")])
    assert _Figures(sent_content(fake_wp)).imgs[0]["src"] == url


def test_source_url_https_chu_hoa_dung_lai_khong_tao_nhap(fake_wp, wp_client, site, web):
    # is_site_link nhận «HTTPS://» nhưng figure_html chỉ nhận «https://»: dừng an toàn, chỉ
    # muộn hơn (sau khi đã tải hết ảnh). Ghi nhận G4 trong báo cáo.
    url = "HTTPS://example.com/wp-content/uploads/a.webp"
    fake_wp.on("POST", MEDIA, (201, {"id": FIRST_ID, "source_url": url, "post": None}, {}))
    fake_wp.on("POST", f"{MEDIA}/{FIRST_ID}", {"id": FIRST_ID, "source_url": url})
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, [DraftImage(web, alt="Cổng")])
    assert "Địa chỉ ảnh không hợp lệ" in str(error.value)  # figure_html, không phải lỗi lạ
    assert creates(fake_wp) == [] and [i.id for i in error.value.uploaded] == [FIRST_ID]
