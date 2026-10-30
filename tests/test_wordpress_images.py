"""T-054: gửi nháp kèm ảnh: tải ảnh lên thư viện Media, chèn ``<figure>``, tạo nháp, ảnh đại diện.

Chỉ dùng site giả (``FakeWordPress``), không gọi WordPress thật. Ảnh là ảnh giả tạo trong bộ nhớ
(không commit ảnh thật), tọa độ GPS là tọa độ giả. Trọng tâm (Lá Chắn T-046 số 7, 8; T-049 điều
kiện 4; T-050 điều kiện 4):
- byte gửi lên đúng ``WebImage.data`` và còn GPS đúng giá trị (quyết định 5A);
- tên file chỉ từ ``naming.image_file_name`` (thẻ đã chuẩn hóa, alt đã duyệt);
- alt/chú thích gỡ ký tự rộng 0 và escape Markdown rồi mới escape HTML; ``<figure>`` do code dựng,
  qua ``sanitize_html``; không lớp ``wp-image-N``, ``srcset`` chỉ có file đầy đủ (T-059: không để
  WordPress chọn cỡ nhỏ mất GPS);
- chỉ tạo nháp, ảnh đại diện chỉ cho bài nháp vừa tạo (``_own_draft``), mọi đường trong
  ``ALLOWED_ROUTES``; không bao giờ ``publish``/``future``;
- lỗi giữa chừng: liệt kê ảnh đã lên thư viện, không xóa gì; kiểm sai thì chưa gửi gì.

T-071 (dọn lỗi Thấp sau Lá Chắn T-054): lỗi ở lệnh tạo nháp báo bài nháp có thể đã có
(LC-T054-2); alt, chú thích ảnh AI không còn "\\" (LC-T054-3); thẻ chỉ từ ``ImageTags``
(LC-T054-4); tải ảnh phải ``201``, mã ảnh trùng thì dừng (LC-T054-5); chốt cuối của
``figure_html`` chỉ đọc thẻ ``<img>`` (LC-T054-6).
"""

import html
import io
import json
import re
from fractions import Fraction
from html.parser import HTMLParser
from types import SimpleNamespace
from urllib.parse import urlsplit

import pytest
import requests
from fake_wordpress import BASE_URL
from PIL import ExifTags, Image
from PIL.TiffImagePlugin import IFDRational
from pillow_heif import options as heif_options

from seo_app.images import html as image_html
from seo_app.images.alt import AltSuggestion, clean_suggestion
from seo_app.images.process import WebImage, make_web_image
from seo_app.images.tags import SOURCE_AI, ImageTags, TagError
from seo_app.sanitize import AUTOLINK_BREAK, clean_ai_text, escape_shortcodes, sanitize_html
from seo_app.wordpress import WordPressError, is_allowed_route
from seo_app.wordpress.client import (
    DraftImage,
    DraftImagesError,
    DraftWithImages,
    UploadedImage,
)

_PILLOW_REGISTRIES = ("ID", "OPEN", "MIME", "SAVE", "SAVE_ALL", "EXTENSION")
_HEIF_OPTIONS = ("THUMBNAILS", "DEPTH_IMAGES", "AUX_IMAGES", "DISABLE_SECURITY_LIMITS")


@pytest.fixture(autouse=True)
def _pillow_state_restored():
    """Trả nguyên bảng định dạng của Pillow và tùy chọn pillow-heif sau mỗi test (như
    ``tests/test_images_process.py``): ``make_web_image`` đăng ký HEIF khi mở ảnh."""
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
LAT = (R(10, 1), R(46, 1), R(3456, 100))  # 10°46'34,56" N (giả)
LON = (R(106, 1), R(41, 1), R(1234, 100))  # 106°41'12,34" E (giả)
GPS_EXPECTED = {
    1: "N",
    2: (Fraction(10), Fraction(46), Fraction(3456, 100)),
    3: "E",
    4: (Fraction(106), Fraction(41), Fraction(1234, 100)),
}
POST = "/wp-json/wp/v2/posts"
POST_42 = POST + "/42"
MEDIA = "/wp-json/wp/v2/media"
UPLOADS = f"{BASE_URL}/wp-content/uploads/2026/10/"
FIRST_MEDIA_ID = 101


def _jpeg(size=(320, 240), *, gps=True, color=(200, 80, 40)):
    exif = Image.Exif()
    exif[ExifTags.Base.Make] = "Apple"
    exif[ExifTags.Base.Model] = "iPhone 15"
    exif[ExifTags.Base.DateTime] = "2026:10:01 10:15:20"
    if gps:
        g = exif.get_ifd(ExifTags.IFD.GPSInfo)
        g[0] = b"\x02\x02\x00\x00"
        g[1], g[2], g[3], g[4] = "N", LAT, "E", LON
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, "JPEG", exif=exif.tobytes(), quality=90)
    return buffer.getvalue()


@pytest.fixture(scope="module")
def web():
    """Ảnh đăng web thật của module xử lý ảnh (T-049): WebP 1600 px tối đa, còn GPS."""
    image = make_web_image(_jpeg())
    assert image.gps is not None
    return image


@pytest.fixture(scope="module")
def web_no_gps():
    return make_web_image(_jpeg((200, 300), gps=False, color=(30, 120, 200)))


def _value(value):
    if isinstance(value, IFDRational):
        return Fraction(value.numerator, value.denominator)
    if isinstance(value, tuple):
        return tuple(_value(v) for v in value)
    return value


def _gps_read_back(data):
    """GPS đọc độc lập bằng Pillow từ byte website nhận được, theo giá trị."""
    image = Image.open(io.BytesIO(data))
    image.load()
    gps = image.getexif().get_ifd(ExifTags.IFD.GPSInfo)
    return {tag: _value(v) for tag, v in gps.items()}


def _browser_tags(content):
    """(thẻ, tên các thuộc tính) như trình duyệt đọc được (bộ đọc HTML của thư viện chuẩn)."""
    tags = []

    class Reader(HTMLParser):
        def handle_starttag(self, tag, attrs):
            tags.append((tag, [name for name, _ in attrs]))

    Reader().feed(content)
    return tags


def body(request):
    return json.loads(request.body) if request.body else None


def path(request):
    return urlsplit(request.url).path


def media_uploads(fake_wp):
    return [r for r in fake_wp.requests if r.method == "POST" and path(r) == MEDIA]


def json_writes(fake_wp):
    return [r for r in fake_wp.requests if r.method == "POST" and path(r) != MEDIA]


def walk(value):
    yield value
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk(item)


class Site:
    """Site giả: thư viện Media cấp mã từ 101, bài nháp 42; ghi lại tên file nhận được."""

    def __init__(self, fake_wp, *, status="draft", source_host=BASE_URL):
        self.fake_wp = fake_wp
        self.next_id = FIRST_MEDIA_ID
        self.files: dict[int, str] = {}
        self.source_host = source_host
        self.status = status
        fake_wp.on("POST", MEDIA, self.create_media)
        for media_id in range(FIRST_MEDIA_ID, FIRST_MEDIA_ID + 20):
            fake_wp.on("POST", f"{MEDIA}/{media_id}", self.update_media)
        fake_wp.on("POST", POST, (201, {"id": 42, "status": "draft", "title": {"raw": "T"}}, {}))
        fake_wp.on("GET", POST_42, lambda _r: {"id": 42, "status": self.status, "meta": {}})
        fake_wp.on("POST", POST_42, self.update_post)

    def source_url(self, media_id):
        host = self.source_host
        return f"{host}/wp-content/uploads/2026/10/{self.files[media_id]}"

    def create_media(self, request):
        disposition = request.headers["Content-Disposition"]
        name = re.fullmatch(r'attachment; filename="([^"]+)"', disposition).group(1)
        media_id = self.next_id
        self.next_id += 1
        self.files[media_id] = name
        answer = {
            "id": media_id, "source_url": self.source_url(media_id), "mime_type": "x", "post": None
        }
        return (201, answer, {})

    def update_media(self, request):
        media_id = int(path(request).rsplit("/", 1)[1])
        return {"id": media_id, "source_url": self.source_url(media_id), **body(request)}

    def update_post(self, request):
        return {"id": 42, "status": "draft", **body(request)}


@pytest.fixture
def site(fake_wp):
    return Site(fake_wp)


def send(client, parts, title="Sửa cổng inox Tân Phú", **kwargs):
    return client.create_draft_with_images(title, parts, **kwargs)


def sent_content(fake_wp):
    creates = [r for r in fake_wp.requests if r.method == "POST" and path(r) == POST]
    assert len(creates) == 1
    return body(creates[0])["content"]


# ----- yêu cầu 2: byte gửi lên đúng WebImage.data, còn GPS ------------------------------------


def test_byte_gui_len_dung_webimage_data_va_con_gps(fake_wp, wp_client, site, web):
    image = DraftImage(
        web, alt="Cổng inox 2 cánh sau khi sơn lại", tags=ImageTags(category="Cổng inox")
    )
    result = send(wp_client, ["<p>Mở bài</p>", image])

    uploads = media_uploads(fake_wp)
    assert len(uploads) == 1
    sent = uploads[0].body
    assert type(sent) is bytes
    assert sent == web.data  # không sửa, không nén lại byte nào
    assert uploads[0].headers["Content-Type"] == "image/webp"
    gps = _gps_read_back(sent)
    for tag, expected in GPS_EXPECTED.items():
        assert gps[tag] == expected  # GPS tới website đúng từng giá trị (quyết định 5A)
    assert result.images[0].id == FIRST_MEDIA_ID


def test_anh_khong_gps_van_gui_nguyen_byte(fake_wp, wp_client, site, web_no_gps):
    send(wp_client, [DraftImage(web_no_gps, alt="Cửa cuốn khe thoáng màu ghi")])
    assert media_uploads(fake_wp)[0].body == web_no_gps.data
    assert _gps_read_back(web_no_gps.data) == {}


def test_anh_dung_trong_bai_la_file_day_du_va_khong_co_wp_image(fake_wp, wp_client, site, web):
    send(wp_client, [DraftImage(web, alt="Cổng inox", tags=ImageTags(category="Cổng inox"))])
    content = sent_content(fake_wp)
    # src là file đầy đủ vừa tải (không phải cỡ nhỏ -300x200…); không lớp wp-image-N, không
    # sizes; srcset chỉ có chính file đầy đủ (T-059): WordPress không tự thêm cỡ nhỏ đã mất GPS
    # (quyết định 5A).
    assert f'src="{UPLOADS}cong-inox.webp"' in content
    assert "wp-image-" not in content
    assert f'srcset="{UPLOADS}cong-inox.webp 1x"' in content
    assert content.count("srcset=") == 1 and "sizes" not in content
    assert f'width="{web.width}" height="{web.height}"' in content
    classes = re.findall(r'class="([^"]*)"', content)
    assert classes == ["wp-block-image"]


# ----- yêu cầu 2: tên file chỉ từ naming.image_file_name ---------------------------------------


def _file_names(fake_wp):
    names = []
    for request in media_uploads(fake_wp):
        disposition = request.headers["Content-Disposition"]
        names.append(re.fullmatch(r'attachment; filename="([^"]+)"', disposition).group(1))
    return names


CT012_TAGS = ImageTags(project_code="CT012", category="Cổng inox", area="Tân Phú")


def test_ten_file_theo_the_da_chuan_hoa_va_tranh_trung(fake_wp, wp_client, site, web):
    first = DraftImage(web, alt="Cổng inox", tags=CT012_TAGS)
    second = DraftImage(web, alt="Cổng inox gần", tags=CT012_TAGS)
    result = send(wp_client, [first, "<p>giữa</p>", second])
    assert _file_names(fake_wp) == [
        "cong-inox-tan-phu-ct012.webp",
        "cong-inox-tan-phu-ct012-2.webp",
    ]
    assert [image.file_name for image in result.images] == _file_names(fake_wp)


def test_thieu_the_thi_ten_file_tu_alt_da_duyet_da_go_ky_tu_ngat(fake_wp, wp_client, site, web):
    alt = clean_ai_text("Bản lề cổng sắt bị gỉ www.example.vn")
    assert AUTOLINK_BREAK in alt
    send(wp_client, [DraftImage(web, alt=alt)])
    assert _file_names(fake_wp) == ["ban-le-cong-sat-bi-gi-www-example-vn.webp"]


def test_the_nhap_tay_duoc_chuan_hoa_vao_ten_file(fake_wp, wp_client, site, web):
    tags = ImageTags.from_input(project_code="ct 12", category="cổng INOX", area="q7")
    send(wp_client, [DraftImage(web, alt="Cổng inox", tags=tags)])
    assert _file_names(fake_wp) == ["cong-inox-quan-7-ct12.webp"]


def test_draft_image_khong_co_cho_cho_ten_file_goc_hay_thu_muc():
    # Không có trường nào nhận đường dẫn, tên thư mục, tên file gốc hay thẻ chữ tự do (Lá Chắn
    # T-049 N8, LC-T054-4): thẻ chỉ qua ``tags`` (``ImageTags``).
    fields = set(DraftImage.__dataclass_fields__)
    assert fields == {"image", "alt", "caption", "tags", "featured"}
    assert DraftImage(b"x", alt="a").tags == ImageTags()  # mặc định: ảnh thật, chưa có thẻ


def test_anh_ai_co_tien_to_ten_file_va_tieu_de_khong_ma_cong_trinh(fake_wp, wp_client, site, web):
    with pytest.raises(TagError):  # ảnh AI không mang được mã công trình (T-052)
        ImageTags(source=SOURCE_AI, project_code="CT012", category="Cổng inox")
    image = DraftImage(
        web,
        alt="Minh họa cổng inox 2 cánh",
        caption="Ảnh minh họa (AI): cổng inox",
        tags=ImageTags.for_ai_image("Cổng inox"),
    )
    send(wp_client, [image])
    assert _file_names(fake_wp) == ["minh-hoa-ai-cong-inox.webp"]
    update = next(r for r in json_writes(fake_wp) if path(r) == f"{MEDIA}/{FIRST_MEDIA_ID}")
    # T-061: "[", "]" ra mã ký tự (WordPress vẫn hiện «[AI] …», shortcode không chạy được).
    assert body(update)["title"] == "&#91;AI&#93; Minh họa cổng inox 2 cánh"


# ----- yêu cầu 3: alt/chú thích: gỡ ký tự ngắt, escape Markdown, rồi escape HTML -------------


def test_alt_chu_thich_go_ky_tu_ngat_va_escape_markdown_roi_escape_html(
    fake_wp, wp_client, site, web
):
    alt = clean_ai_text('Cổng "Pro" [mẫu](x) www.prometal.vn <b>sơn</b> a@b.vn & 5 < 6')
    caption = clean_ai_text("[Lưu ý](chữ có cách): cổng <script>x</script> www.a.vn")
    assert AUTOLINK_BREAK in alt and "\\(" in caption
    send(wp_client, [DraftImage(web, alt=alt, caption=caption)])

    content = sent_content(fake_wp)
    assert AUTOLINK_BREAK not in content and "\\" not in content
    assert 'alt="Cổng &quot;Pro&quot; mẫu www.prometal.vn sơn a@b.vn &amp; 5 &lt; 6"' in content
    # T-061: "[", "]" ra mã ký tự; người đọc vẫn thấy «[Lưu ý](chữ có cách)».
    assert "<figcaption>&#91;Lưu ý&#93;(chữ có cách): cổng www.a.vn</figcaption>" in content
    assert "<script" not in content and "<b>" not in content

    update = body(next(r for r in json_writes(fake_wp) if path(r) == f"{MEDIA}/{FIRST_MEDIA_ID}"))
    # alt_text qua REST: chữ thường đã gỡ ký tự ngắt (WordPress tự escape khi in ra).
    assert update["alt_text"] == 'Cổng "Pro" mẫu www.prometal.vn sơn a@b.vn & 5 < 6'
    # Tiêu đề, chú thích media: WordPress hiện như HTML nên đã escape.
    assert update["title"] == "Cổng &quot;Pro&quot; mẫu www.prometal.vn sơn a@b.vn &amp; 5 &lt; 6"
    assert update["caption"] == "&#91;Lưu ý&#93;(chữ có cách): cổng www.a.vn"
    for value in walk(update):
        assert AUTOLINK_BREAK not in str(value)


def test_chu_nguoi_dung_go_the_html_bi_escape_khong_thanh_the(fake_wp, wp_client, site, web):
    alt = '"><img src=x onerror=alert(1)>'
    caption = "</figcaption><script>alert(1)</script><a href='javascript:x'>bấm</a>"
    send(wp_client, [DraftImage(web, alt=alt, caption=caption)])
    content = sent_content(fake_wp)
    # Trình duyệt chỉ thấy đúng 3 thẻ do code dựng, img chỉ có 5 thuộc tính do code đặt
    # (srcset: T-059).
    assert _browser_tags(content) == [
        ("figure", ["class"]),
        ("img", ["src", "alt", "srcset", "width", "height"]),
        ("figcaption", []),
    ]
    assert 'alt="&quot;&gt;&lt;img src=x onerror=alert(1)&gt;"' in content
    assert "<script" not in content and "<a " not in content


def test_ky_tu_vo_hinh_khac_bi_bo(fake_wp, wp_client, site, web):
    alt = "Cổng\u202e inox\u200b\u00ad 2\x07 cánh\n\nmới"
    send(wp_client, [DraftImage(web, alt=alt)])
    assert 'alt="Cổng inox 2 cánh mới"' in sent_content(fake_wp)


# ----- figure_html (seo_app/images/html.py) --------------------------------------------------


SRC = f"{UPLOADS}cong-inox.webp"


def test_figure_html_dung_khuon_va_on_dinh_qua_bo_loc():
    out = image_html.figure_html(src=SRC, alt="Cổng inox", width=1600, height=1200, caption="Sau")
    assert out == (
        f'<figure class="wp-block-image"><img src="{SRC}" alt="Cổng inox" srcset="{SRC} 1x" '
        'width="1600" height="1200"><figcaption>Sau</figcaption></figure>'
    )
    assert sanitize_html(out) == out


def test_figure_html_khong_chu_thich_thi_khong_figcaption():
    out = image_html.figure_html(src=SRC, alt="Cổng", width=10, height=10, caption=" \u200b ")
    assert "figcaption" not in out


@pytest.mark.parametrize("alt", ["", "   ", "\u200b", AUTOLINK_BREAK * 3, None, 5])
def test_figure_html_alt_rong_bi_tu_choi(alt):
    with pytest.raises(image_html.ImageHtmlError):
        image_html.figure_html(src=SRC, alt=alt, width=10, height=10)


@pytest.mark.parametrize(
    "src",
    [
        "http://example.com/a.webp",
        "javascript:alert(1)",
        "data:image/webp;base64,AAAA",
        "//evil.com/a.webp",
        'https://example.com/a.webp" onerror="x',
        "https://example.com/a b.webp",
        "https://example.com/a.webp'x",
        "https://example.com/<a>.webp",
        "https://example.com/a\\b.webp",
        "https://example.com/a\n.webp",
        "https://" + "a" * 2000,
        "",
        None,
        b"https://example.com/a.webp",
    ],
)
def test_figure_html_dia_chi_la_bi_tu_choi(src):
    with pytest.raises(image_html.ImageHtmlError):
        image_html.figure_html(src=src, alt="Cổng", width=10, height=10)


@pytest.mark.parametrize(
    ("width", "height"), [(0, 10), (10, -1), (True, 10), (10.0, 10), ("10", 10), (10, 10_001)]
)
def test_figure_html_kich_thuoc_la_bi_tu_choi(width, height):
    with pytest.raises(image_html.ImageHtmlError):
        image_html.figure_html(src=SRC, alt="Cổng", width=width, height=height)


def test_plain_image_text_go_dung_thu_tu():
    raw = clean_ai_text("Xem [mẫu](https://x.vn) tại www.prometal.vn, email a@b.vn")
    assert image_html.plain_image_text(raw) == "Xem mẫu tại www.prometal.vn, email a@b.vn"
    assert image_html.plain_image_text("[a]\\(b) [c]\\[d]") == "[a](b) [c][d]"
    assert image_html.plain_image_text(None) == ""


# ----- yêu cầu 4: chỉ nháp, ảnh đại diện cho nháp vừa tạo, đường cố định ---------------------


def test_thu_tu_lenh_va_moi_duong_trong_danh_sach(fake_wp, wp_client, site, web, web_no_gps):
    first = DraftImage(web, alt="Cổng inox", tags=ImageTags(category="Cổng inox"))
    second = DraftImage(
        web_no_gps, alt="Cửa cuốn", tags=ImageTags(category="Cửa cuốn"), featured=True
    )
    result = send(wp_client, ["<h2>Phần 1</h2>", first, "<p>x</p>", second])

    calls = [(r.method, path(r)) for r in fake_wp.requests]
    assert calls == [
        ("POST", MEDIA),
        ("POST", f"{MEDIA}/101"),
        ("POST", MEDIA),
        ("POST", f"{MEDIA}/102"),
        ("POST", POST),
        ("POST", f"{MEDIA}/101"),  # T-110 (Chỉ Huy duyệt 30/10): gắn từng ảnh vào bài nháp
        ("POST", f"{MEDIA}/102"),
        ("GET", POST_42),
        ("POST", POST_42),
    ]
    for method, route in calls:
        assert is_allowed_route(method, route.removeprefix("/wp-json"))
    assert body(fake_wp.requests[-1]) == {"featured_media": 102}
    assert isinstance(result, DraftWithImages)
    assert result.featured_media == 102 and result.message == ""
    assert result.post.id == 42
    assert [image.source_url for image in result.images] == [
        f"{UPLOADS}cong-inox.webp",
        f"{UPLOADS}cua-cuon.webp",
    ]
    assert all(isinstance(image, UploadedImage) for image in result.images)


def test_khong_bao_gio_publish_future_va_chi_gui_truong_can_thiet(fake_wp, wp_client, site, web):
    image = DraftImage(web, alt="Cổng inox", caption="Sau khi sơn")
    send(wp_client, ["<p>Bài</p>", image], categories=[3], tags=(7,), excerpt="Tóm tắt")
    for request in json_writes(fake_wp):
        data = body(request)
        values = [str(v).lower() for v in walk(data)]
        assert "publish" not in values and "future" not in values
        if path(request) == POST:
            assert data["status"] == "draft"
        else:
            assert "status" not in data
        if path(request).startswith(MEDIA) and data == {"post": 42}:
            continue  # T-110 (Chỉ Huy duyệt 30/10): lệnh gắn ảnh vào bài nháp
        if path(request).startswith(MEDIA):
            assert set(data) <= {"alt_text", "title", "caption"}
        if path(request) == POST_42:
            assert data == {"featured_media": FIRST_MEDIA_ID}
    assert not [r for r in fake_wp.requests if r.method not in ("GET", "POST")]


def test_anh_dau_tien_la_anh_dai_dien_khi_khong_chon(fake_wp, wp_client, site, web, web_no_gps):
    result = send(wp_client, [DraftImage(web, alt="A"), DraftImage(web_no_gps, alt="B")])
    assert result.featured_media == FIRST_MEDIA_ID


def test_bai_khong_con_nhap_thi_khong_dat_anh_dai_dien(fake_wp, wp_client, web):
    site = Site(fake_wp, status="publish")
    result = send(wp_client, [DraftImage(web, alt="Cổng")])
    assert site.status == "publish"
    assert result.featured_media is None
    assert "chưa đặt được ảnh đại diện" in result.message
    assert result.post.id == 42 and len(result.images) == 1
    assert ("POST", POST_42) not in [(r.method, path(r)) for r in fake_wp.requests]


def test_khong_co_anh_thi_chi_tao_nhap(fake_wp, wp_client, site):
    result = send(wp_client, ["<p>Chỉ chữ</p>"])
    assert [(r.method, path(r)) for r in fake_wp.requests] == [("POST", POST)]
    assert result.images == () and result.featured_media is None


def test_cung_mot_anh_hai_lan_chi_tai_mot_lan(fake_wp, wp_client, site, web):
    image = DraftImage(web, alt="Cổng inox")
    result = send(wp_client, [image, "<p>x</p>", image])
    assert len(media_uploads(fake_wp)) == 1
    assert len(result.images) == 1
    assert sent_content(fake_wp).count("<figure") == 2


def test_noi_dung_ca_bai_van_qua_bo_loc(fake_wp, wp_client, site, web):
    send(wp_client, ['<p onclick="x()">A</p><script>alert(1)</script>', DraftImage(web, alt="C")])
    content = sent_content(fake_wp)
    assert "<script" not in content and "onclick" not in content


# ----- yêu cầu 1: kiểm trước khi gửi (chưa gửi gì) ------------------------------------------


def _not_web_image():
    return WebImage(data=_jpeg(), width=320, height=240, gps=None)


# Thẻ chữ tự do (tên thư mục, tên khách, địa chỉ) mà ``ImageTags`` không bao giờ nhận.
_FREE_TEXT_TAGS = {
    "source": "that",
    "project_code": "Nhà anh Tuấn 12 Lê Lợi",
    "category": r"C:\Users\An\Ảnh\CT012 - Nhà anh Tuấn",
    "area": "12 Lê Lợi",
    "phase": "",
}


class _SubTags(ImageTags):
    """Lớp con của ``ImageTags``: client chỉ nhận đúng lớp ``ImageTags``."""


def _tampered_tags(field="area"):
    """``ImageTags`` hợp lệ lúc tạo, rồi bị sửa thẳng (bỏ qua bước kiểm của lớp đóng băng)."""
    tags = ImageTags(category="Cổng inox")
    object.__setattr__(tags, field, _FREE_TEXT_TAGS[field])
    return tags


def _bad_cases(web):
    return {
        "alt rỗng": [DraftImage(web, alt="")],
        "alt chỉ ký tự ngắt": [DraftImage(web, alt=AUTOLINK_BREAK + " \u200b")],
        "alt quá dài": [DraftImage(web, alt="a" * 501)],
        "chú thích quá dài": [DraftImage(web, alt="a", caption="b" * 1001)],
        "byte trần": [DraftImage(b"RIFF", alt="a")],
        "WebImage chứa JPEG": [DraftImage(_not_web_image(), alt="a")],
        "WebImage rỗng": [DraftImage(WebImage(b"", 10, 10, None), alt="a")],
        "WebImage bytearray": [DraftImage(WebImage(bytearray(web.data), 10, 10, None), alt="a")],
        "WebImage cỡ sai": [DraftImage(WebImage(web.data, 0, 10, None), alt="a")],
        "WebImage mime sai": [
            DraftImage(WebImage(web.data, 10, 10, None, mime="image/x"), alt="a")
        ],
        "hai ảnh đại diện": [
            DraftImage(web, alt="a", featured=True),
            DraftImage(web, alt="b", featured=True),
        ],
        "phần lạ": ["<p>x</p>", 5],
        "dict": [{"image": web, "alt": "a"}],
        "thẻ là chữ": [DraftImage(web, alt="a", tags="Cổng inox")],
        "thẻ là dict": [DraftImage(web, alt="a", tags={"category": "Cổng inox"})],
        "thẻ giả dạng": [DraftImage(web, alt="a", tags=SimpleNamespace(**_FREE_TEXT_TAGS))],
        "thẻ lớp con": [DraftImage(web, alt="a", tags=_SubTags(category="Cổng inox"))],
        "thẻ bị sửa sau khi tạo": [DraftImage(web, alt="a", tags=_tampered_tags())],
        "featured lạ": [DraftImage(web, alt="a", featured="yes")],
    }


@pytest.mark.parametrize(
    "case",
    [
        "alt rỗng",
        "alt chỉ ký tự ngắt",
        "alt quá dài",
        "chú thích quá dài",
        "byte trần",
        "WebImage chứa JPEG",
        "WebImage rỗng",
        "WebImage bytearray",
        "WebImage cỡ sai",
        "WebImage mime sai",
        "hai ảnh đại diện",
        "phần lạ",
        "dict",
        "thẻ là chữ",
        "thẻ là dict",
        "thẻ giả dạng",
        "thẻ lớp con",
        "thẻ bị sửa sau khi tạo",
        "featured lạ",
    ],
)
def test_kiem_sai_thi_chua_gui_gi(fake_wp, wp_client, site, web, case):
    # Ảnh hợp lệ đứng trước ảnh lỗi cũng không được tải lên: kiểm hết rồi mới gửi.
    parts = [DraftImage(web, alt="Ảnh tốt"), *_bad_cases(web)[case]]
    with pytest.raises(WordPressError) as error:
        send(wp_client, parts)
    assert not isinstance(error.value, DraftImagesError)
    assert fake_wp.requests == []


@pytest.mark.parametrize(
    ("title", "kwargs"),
    [
        ("", {}),
        ("<b></b> ", {}),
        (None, {}),
        ("T", {"categories": [0]}),
        ("T", {"categories": "3"}),
        ("T", {"tags": [True]}),
        ("T", {"tags": [1.5]}),
        ("T", {"excerpt": None}),
        ("T", {"slug": 5}),
    ],
)
def test_tieu_de_chuyen_muc_sai_thi_chua_gui_gi(fake_wp, wp_client, site, web, title, kwargs):
    with pytest.raises(WordPressError):
        send(wp_client, [DraftImage(web, alt="a")], title=title, **kwargs)
    assert fake_wp.requests == []


@pytest.mark.parametrize("parts", ["<p>chuỗi</p>", b"bytes", None, 5, iter([])])
def test_noi_dung_khong_phai_danh_sach_thi_chua_gui_gi(fake_wp, wp_client, site, parts):
    with pytest.raises(WordPressError):
        send(wp_client, parts)
    assert fake_wp.requests == []


def test_dung_html_va_draft_image_khong_goi_mang(fake_wp, web):
    image = DraftImage(web, alt="Cổng")
    image_html.figure_html(src=SRC, alt=image.alt, width=web.width, height=web.height)
    assert fake_wp.requests == []


# ----- W2: lỗi giữa chừng: liệt kê ảnh đã tải, không xóa ------------------------------------


def _no_delete(fake_wp):
    assert {r.method for r in fake_wp.requests} <= {"GET", "POST"}


def test_anh_thu_hai_loi_may_chu_liet_ke_anh_dau_khong_tao_bai(
    fake_wp, wp_client, site, web, web_no_gps
):
    calls = {"n": 0}

    def flaky(request):
        calls["n"] += 1
        if calls["n"] == 2:
            return (500, {"code": "x", "message": "lỗi"}, {})
        return site.create_media(request)

    fake_wp.on("POST", MEDIA, flaky)
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, [DraftImage(web, alt="A"), DraftImage(web_no_gps, alt="B")])
    err = error.value
    assert [image.id for image in err.uploaded] == [FIRST_MEDIA_ID]
    assert err.uploaded[0].source_url == f"{UPLOADS}a.webp"
    assert err.uploaded[0].edit_link == f"{BASE_URL}/wp-admin/post.php?post=101&action=edit"
    assert err.maybe_uploaded is True  # lỗi máy chủ: ảnh thứ hai có thể đã lên
    message = str(err)
    assert "1 ảnh lên thư viện Media" in message and "không xóa" in message
    assert "có thể vẫn đã lên" in message
    assert ("POST", POST) not in [(r.method, path(r)) for r in fake_wp.requests]
    _no_delete(fake_wp)


def test_anh_bi_tu_choi_4xx_thi_khong_bao_co_the_da_len(fake_wp, wp_client, site, web):
    fake_wp.on("POST", MEDIA, (413, {"code": "too_big", "message": "x"}, {}))
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, [DraftImage(web, alt="A")])
    assert error.value.uploaded == ()
    assert error.value.maybe_uploaded is False
    assert "Chưa có ảnh nào lên thư viện Media" in str(error.value)
    _no_delete(fake_wp)


def test_tai_len_khong_tra_ma_anh_thi_bao_co_the_da_len(fake_wp, wp_client, site, web):
    fake_wp.on("POST", MEDIA, (201, {"id": "101", "source_url": SRC}, {}))
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, [DraftImage(web, alt="A")])
    assert error.value.uploaded == () and error.value.maybe_uploaded is True
    assert "Chưa có ảnh nào" not in str(error.value)


def test_ghi_alt_loi_van_liet_ke_anh_da_tai(fake_wp, wp_client, site, web):
    fake_wp.on("POST", f"{MEDIA}/{FIRST_MEDIA_ID}", (500, {"code": "x", "message": "y"}, {}))
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, [DraftImage(web, alt="A")])
    assert [image.id for image in error.value.uploaded] == [FIRST_MEDIA_ID]
    assert error.value.uploaded[0].source_url == ""
    assert error.value.maybe_uploaded is False
    assert ("POST", POST) not in [(r.method, path(r)) for r in fake_wp.requests]
    _no_delete(fake_wp)


def test_ghi_alt_tra_loi_anh_khac_thi_dung(fake_wp, wp_client, site, web):
    fake_wp.on("POST", f"{MEDIA}/{FIRST_MEDIA_ID}", {"id": 7, "source_url": SRC})
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, [DraftImage(web, alt="A")])
    assert "không khớp" in str(error.value)
    assert [image.id for image in error.value.uploaded] == [FIRST_MEDIA_ID]


@pytest.mark.parametrize(
    "host",
    ["https://cdn.evil.com", "http://example.com", "https://example.com.evil.com", "javascript:"],
)
def test_dia_chi_anh_ngoai_website_thi_dung(fake_wp, wp_client, web, host):
    Site(fake_wp, source_host=host)
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, [DraftImage(web, alt="A")])
    assert "không phải https trên đúng website" in str(error.value)
    assert [image.id for image in error.value.uploaded] == [FIRST_MEDIA_ID]
    assert ("POST", POST) not in [(r.method, path(r)) for r in fake_wp.requests]


def test_tao_nhap_loi_liet_ke_moi_anh_da_tai(fake_wp, wp_client, site, web, web_no_gps):
    fake_wp.on("POST", POST, (500, {"code": "x", "message": "y"}, {}))
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, [DraftImage(web, alt="A"), DraftImage(web_no_gps, alt="B")])
    assert [image.id for image in error.value.uploaded] == [101, 102]
    assert "2 ảnh lên thư viện Media" in str(error.value)
    _no_delete(fake_wp)


def test_loi_la_van_liet_ke_anh_da_tai(fake_wp, wp_client, site, web, monkeypatch):
    def boom(*_args, **_kwargs):
        raise RuntimeError("bất ngờ /home/site")

    monkeypatch.setattr(wp_client, "create_draft", boom)
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, [DraftImage(web, alt="A")])
    assert [image.id for image in error.value.uploaded] == [FIRST_MEDIA_ID]
    assert "RuntimeError" in str(error.value) and "/home/site" not in str(error.value)


def test_client_khong_co_ham_xoa():
    from seo_app.wordpress.client import WordPressClient

    names = [name.lower() for name in dir(WordPressClient)]
    assert not [name for name in names if "delete" in name or "remove" in name or "xoa" in name]


# ----- T-071 yêu cầu 1 (LC-T054-2): lỗi ở lệnh tạo nháp, bài nháp có thể đã có ---------------

MAYBE_DRAFT = "Bài nháp có thể vẫn đã được tạo"
KHOA_GIA = "abcd efgh ijkl"  # khóa giả của fixture ``wp_client``


@pytest.mark.parametrize(
    "answer",
    [
        requests.exceptions.ReadTimeout("hết giờ"),
        requests.exceptions.ConnectionError("mất mạng"),
        (500, {"code": "x", "message": "y"}, {}),
        (502, b"<html>Bad Gateway</html>", {}),
        (301, {}, {"Location": f"{BASE_URL}/khac"}),
        (201, {"id": "42", "status": "draft"}, {}),
        (201, [], {}),
        (200, b"<html></html>", {}),
    ],
)
def test_t071_loi_khong_ro_o_lenh_tao_nhap_bao_bai_nhap_co_the_da_co(
    fake_wp, wp_client, site, web, answer
):
    fake_wp.on("POST", POST, answer)
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, [DraftImage(web, alt="Cổng")])
    err = error.value
    assert err.maybe_draft is True and err.maybe_uploaded is False
    assert [image.id for image in err.uploaded] == [FIRST_MEDIA_ID]
    message = str(err)
    assert MAYBE_DRAFT in message and "Bài viết → Nháp" in message
    assert "Chưa tạo bài nháp" not in message
    # Câu "nháp có thể đã có" đứng trước danh sách ảnh đã lên thư viện.
    assert message.index(MAYBE_DRAFT) < message.index("1 ảnh lên thư viện Media")
    assert [(r.method, path(r)) for r in fake_wp.requests][-1] == ("POST", POST)
    for secret in (KHOA_GIA, KHOA_GIA.replace(" ", "")):
        assert secret not in message
    _no_delete(fake_wp)


@pytest.mark.parametrize("code", [400, 401, 403, 404, 409, 413, 429])
def test_t071_lenh_tao_nhap_bi_tu_choi_4xx_thi_bao_chua_tao(fake_wp, wp_client, site, web, code):
    fake_wp.on("POST", POST, (code, {"code": "loi_gia", "message": "lỗi giả"}, {}))
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, [DraftImage(web, alt="Cổng")])
    err = error.value
    assert err.maybe_draft is False and err.status_code == code
    assert "Chưa tạo bài nháp" in str(err) and MAYBE_DRAFT not in str(err)
    assert [image.id for image in err.uploaded] == [FIRST_MEDIA_ID]


@pytest.mark.parametrize(
    ("route", "answer"),
    [
        (MEDIA, (500, {"code": "x", "message": "y"}, {})),
        (MEDIA, requests.exceptions.ReadTimeout("hết giờ")),
        (f"{MEDIA}/{FIRST_MEDIA_ID}", (502, {"code": "x", "message": "y"}, {})),
        (f"{MEDIA}/{FIRST_MEDIA_ID}", requests.exceptions.ConnectionError("mất mạng")),
    ],
)
def test_t071_loi_truoc_lenh_tao_nhap_khong_bao_nhap_co_the_da_co(
    fake_wp, wp_client, site, web, route, answer
):
    fake_wp.on("POST", route, answer)
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, [DraftImage(web, alt="Cổng")])
    assert error.value.maybe_draft is False and MAYBE_DRAFT not in str(error.value)
    assert ("POST", POST) not in [(r.method, path(r)) for r in fake_wp.requests]


def test_t071_loi_la_o_lenh_tao_nhap_khong_khang_dinh_chua_tao(
    fake_wp, wp_client, site, web, monkeypatch
):
    def boom(*_args, **_kwargs):
        raise RuntimeError("bất ngờ")

    monkeypatch.setattr(wp_client, "create_draft", boom)
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, [DraftImage(web, alt="A")])
    assert error.value.maybe_draft is True
    assert MAYBE_DRAFT in str(error.value) and "Chưa tạo bài nháp" not in str(error.value)


def test_t071_loi_la_truoc_lenh_tao_nhap_van_bao_chua_tao(
    fake_wp, wp_client, site, web, monkeypatch
):
    def boom(*_args, **_kwargs):
        raise RuntimeError("bất ngờ")

    monkeypatch.setattr(wp_client, "_describe_draft_media", boom)
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, [DraftImage(web, alt="A")])
    err = error.value
    assert err.maybe_draft is False and "Chưa tạo bài nháp" in str(err)
    assert [image.id for image in err.uploaded] == [FIRST_MEDIA_ID]
    assert ("POST", POST) not in [(r.method, path(r)) for r in fake_wp.requests]
    assert DraftImagesError("x").maybe_draft is False  # mặc định: không nói "có thể đã có"


# ----- T-071 yêu cầu 2 (LC-T054-3): alt, chú thích ảnh AI mở đầu «[…]:» không còn "\" ------


def test_t071_plain_image_text_go_dau_gach_cheo_cua_nhan_giua_dong():
    plain = image_html.plain_image_text
    assert plain(r"Minh họa [Trước khi sửa]\: cổng") == "Minh họa [Trước khi sửa]: cổng"
    assert plain(r"chữ [x]\: y [z]\: w") == "chữ [x]: y [z]: w"
    assert plain(r"[a]\(b) [c]\[d] e [f]\: g") == "[a](b) [c][d] e [f]: g"
    # "]" đã escape (đứng sau số lẻ dấu "\") không đóng nhãn nào: giữ nguyên.
    assert plain(r"a \]\: b") == r"a \]\: b"
    assert plain(r"a \\]\: b") == r"a \\]: b"
    for text in (r"Minh họa [x]\: y", r"a \]\: b", r"]\:]\:"):
        assert plain(plain(text)) == plain(text)  # chạy lại không đổi


def _img_alt_and_captions(content):
    """(alt của các ``<img>``, chữ các ``<figcaption>``) như trình duyệt đọc (đã giải mã)."""
    alts, captions, inside = [], [], []

    class Reader(HTMLParser):
        def handle_starttag(self, tag, attrs):
            if tag == "img":
                alts.append(dict(attrs)["alt"])
            if tag == "figcaption":
                inside.append("")

        def handle_data(self, data):
            if inside:
                inside[-1] += data

        def handle_endtag(self, tag):
            if tag == "figcaption":
                captions.append(inside.pop())

    Reader(convert_charrefs=True).feed(content)
    return alts, captions


@pytest.mark.parametrize(
    ("alt", "caption"),
    [
        ("[Trước khi sửa]: cổng sắt gỉ sét", "[Lưu ý]: sơn lại cổng"),
        ("[Cổng]: [Bản lề]: gỉ", "[Ghi chú]: hai lớp sơn"),
    ],
)
def test_t071_anh_ai_chu_mo_dau_ngoac_vuong_khong_con_dau_gach_cheo(
    fake_wp, wp_client, site, web, alt, caption
):
    suggestion = clean_suggestion(AltSuggestion(alt=alt, caption=caption), ai_generated=True)
    assert "\\" in suggestion.alt and "\\" in suggestion.caption  # tiền đề: còn escape Markdown
    image = DraftImage(
        web, alt=suggestion.alt, caption=suggestion.caption, tags=ImageTags(source=SOURCE_AI)
    )
    send(wp_client, [image])
    want_alt, want_caption = f"Minh họa {alt}", f"Ảnh minh họa (AI): {caption}"

    content = sent_content(fake_wp)
    assert "\\" not in content
    assert _img_alt_and_captions(content) == ([want_alt], [want_caption])
    assert "[" not in content and "]" not in content  # T-061: shortcode vẫn bị vô hiệu
    update = body(next(r for r in json_writes(fake_wp) if path(r) == f"{MEDIA}/{FIRST_MEDIA_ID}"))
    assert update["alt_text"] == escape_shortcodes(want_alt)
    assert update["title"] == escape_shortcodes(html.escape(f"[AI] {want_alt}", quote=True))
    assert update["caption"] == escape_shortcodes(html.escape(want_caption, quote=True))
    for value in update.values():
        assert "\\" not in value and "[" not in value and "]" not in value


def test_t071_nguoi_dung_go_them_chu_truoc_nhan_khong_con_dau_gach_cheo(
    fake_wp, wp_client, site, web
):
    edited = "Cổng mới, " + clean_ai_text("[Lưu ý]: sơn 2 lớp")
    assert edited == r"Cổng mới, [Lưu ý]\: sơn 2 lớp"
    send(wp_client, [DraftImage(web, alt=edited, caption=edited)])
    content = sent_content(fake_wp)
    assert "\\" not in content
    assert _img_alt_and_captions(content) == (
        ["Cổng mới, [Lưu ý]: sơn 2 lớp"],
        ["Cổng mới, [Lưu ý]: sơn 2 lớp"],
    )


def test_t071_go_dau_gach_cheo_khong_mo_lai_shortcode(fake_wp, wp_client, site, web):
    suggestion = clean_suggestion(
        AltSuggestion(alt="[code_snippet id=1]: cổng sắt", caption="Cổng sắt"), ai_generated=True
    )
    assert suggestion.alt == r"Minh họa [code_snippet id=1]\: cổng sắt"
    send(wp_client, [DraftImage(web, alt=suggestion.alt, tags=ImageTags(source=SOURCE_AI))])
    content = sent_content(fake_wp)
    assert "[code_snippet" not in content and "\\" not in content
    assert 'alt="Minh họa &#91;code_snippet id=1&#93;: cổng sắt"' in content
    update = body(next(r for r in json_writes(fake_wp) if path(r) == f"{MEDIA}/{FIRST_MEDIA_ID}"))
    assert update["alt_text"] == "Minh họa &#91;code_snippet id=1&#93;: cổng sắt"


# ----- T-071 yêu cầu 3 (LC-T054-5): tải ảnh phải 201, mã ảnh trùng thì dừng -----------------


@pytest.mark.parametrize("code", [200, 202, 204])
def test_t071_tai_anh_khong_phai_201_thi_dung_khong_ghi_alt(fake_wp, wp_client, site, web, code):
    fake_wp.on("POST", MEDIA, (code, {"id": 7, "source_url": f"{UPLOADS}cu.webp"}, {}))
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, [DraftImage(web, alt="Cổng")])
    err = error.value
    assert err.uploaded == () and err.maybe_uploaded is True and err.maybe_draft is False
    assert "201" in str(err) and "có thể vẫn đã lên" in str(err)
    # Không ghi alt cho ảnh 7 (có thể là ảnh có sẵn trên website), không tạo nháp.
    assert [(r.method, path(r)) for r in fake_wp.requests] == [("POST", MEDIA)]


def test_t071_anh_thu_hai_khong_phai_201_liet_ke_anh_dau(
    fake_wp, wp_client, site, web, web_no_gps
):
    calls = {"n": 0}

    def answer(request):
        calls["n"] += 1
        if calls["n"] == 2:
            return {"id": 7, "source_url": f"{UPLOADS}cu.webp"}  # 200: có thể là ảnh có sẵn
        return site.create_media(request)

    fake_wp.on("POST", MEDIA, answer)
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, [DraftImage(web, alt="A"), DraftImage(web_no_gps, alt="B")])
    err = error.value
    assert [image.id for image in err.uploaded] == [FIRST_MEDIA_ID]
    assert err.maybe_uploaded is True
    assert ("POST", f"{MEDIA}/7") not in [(r.method, path(r)) for r in fake_wp.requests]
    assert ("POST", POST) not in [(r.method, path(r)) for r in fake_wp.requests]


def test_t071_website_tra_cung_ma_anh_thi_dung_khong_ghi_de_alt(fake_wp, wp_client, site, web):
    def same_id(request):
        site.create_media(request)
        return (201, {"id": FIRST_MEDIA_ID, "source_url": site.source_url(FIRST_MEDIA_ID)}, {})

    fake_wp.on("POST", MEDIA, same_id)
    # Hai ảnh khác đối tượng, cùng byte (plugin gộp ảnh trùng byte có thể trả lại mã cũ).
    first, second = DraftImage(web, alt="Ảnh một"), DraftImage(web, alt="Ảnh hai")
    with pytest.raises(DraftImagesError) as error:
        send(wp_client, [first, second])
    err = error.value
    assert [image.id for image in err.uploaded] == [FIRST_MEDIA_ID]
    assert err.maybe_uploaded is True and err.maybe_draft is False
    assert "cùng một mã ảnh" in str(err) and "chưa tạo bài nháp" in str(err)
    writes = [r for r in json_writes(fake_wp) if path(r) == f"{MEDIA}/{FIRST_MEDIA_ID}"]
    assert [body(r)["alt_text"] for r in writes] == ["Ảnh một"]  # alt ảnh 101 không bị đè
    assert ("POST", POST) not in [(r.method, path(r)) for r in fake_wp.requests]
    _no_delete(fake_wp)


# ----- T-071 yêu cầu 4 (LC-T054-6): chốt cuối của figure_html chỉ đọc thẻ <img> ------------

CAPTION_LIKE_IMG = f'chữ src="{SRC}" alt=y'


def test_t071_chu_thich_giong_thuoc_tinh_anh_van_dung_binh_thuong():
    out = image_html.figure_html(
        src=SRC, alt="Cổng", width=10, height=10, caption=CAPTION_LIKE_IMG
    )
    assert out.count("<img ") == 1
    assert f"<figcaption>{CAPTION_LIKE_IMG}</figcaption>" in out


@pytest.mark.parametrize(
    "broken",
    [
        lambda out: re.sub(r'<img src="[^"]*"', "<img", out),  # bộ lọc bỏ src của ảnh
        lambda out: re.sub(r' alt="[^"]*"( srcset)', r"\1", out),  # bộ lọc bỏ alt của ảnh
        lambda out: re.sub(r' srcset="[^"]*"', "", out, count=1),  # bỏ srcset (T-059)
        lambda out: out.replace("<img ", "<span ", 1),  # bộ lọc bỏ hẳn thẻ ảnh
        lambda out: out.replace("</figure>", f'<img src="{SRC}" alt="x"></figure>'),  # hai ảnh
    ],
)
def test_t071_bo_loc_lam_hong_the_anh_thi_bao_loi_du_chu_thich_co(monkeypatch, broken):
    real = image_html.sanitize_html
    monkeypatch.setattr(image_html, "sanitize_html", lambda text: broken(real(text)))
    with pytest.raises(image_html.ImageHtmlError):
        image_html.figure_html(src=SRC, alt="Cổng", width=10, height=10, caption=CAPTION_LIKE_IMG)


# ----- T-071 yêu cầu 5 (LC-T054-4): thẻ chỉ từ ImageTags ------------------------------------


@pytest.mark.parametrize("field", ["project_code", "category", "area"])
def test_t071_chu_tu_do_khong_thanh_the_duoc(field):
    with pytest.raises(TagError):
        ImageTags(**{field: _FREE_TEXT_TAGS[field]})


@pytest.mark.parametrize("field", ["project_code", "category", "area"])
def test_t071_the_bi_sua_sau_khi_tao_bi_chan_truoc_khi_gui(fake_wp, wp_client, site, web, field):
    # Thay test cũ "mã công trình sai mẫu không vào tên file": nay chữ tự do không tới được
    # bước đặt tên file, kể cả khi ``ImageTags`` bị sửa sau khi tạo (chưa gửi gì).
    with pytest.raises(WordPressError) as error:
        send(wp_client, [DraftImage(web, alt="Cổng", tags=_tampered_tags(field))])
    assert str(error.value) == "Thẻ của ảnh thứ 1 không hợp lệ. Chưa gửi gì lên website."
    assert fake_wp.requests == []


def test_t071_anh_ai_lay_tu_the_nguon_anh(fake_wp, wp_client, site, web):
    send(wp_client, [DraftImage(web, alt="Cổng inox", tags=ImageTags(source=SOURCE_AI))])
    assert _file_names(fake_wp) == ["minh-hoa-ai-cong-inox.webp"]
    update = next(r for r in json_writes(fake_wp) if path(r) == f"{MEDIA}/{FIRST_MEDIA_ID}")
    assert body(update)["title"] == "&#91;AI&#93; Cổng inox"


def test_t071_anh_that_khong_co_tien_to_ai(fake_wp, wp_client, site, web):
    send(wp_client, [DraftImage(web, alt="Cổng inox", tags=CT012_TAGS)])
    assert _file_names(fake_wp) == ["cong-inox-tan-phu-ct012.webp"]
    update = next(r for r in json_writes(fake_wp) if path(r) == f"{MEDIA}/{FIRST_MEDIA_ID}")
    assert body(update)["title"] == "Cổng inox"
