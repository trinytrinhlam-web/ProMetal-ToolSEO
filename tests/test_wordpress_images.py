"""T-054: gửi nháp kèm ảnh: tải ảnh lên thư viện Media, chèn ``<figure>``, tạo nháp, ảnh đại diện.

Chỉ dùng site giả (``FakeWordPress``), không gọi WordPress thật. Ảnh là ảnh giả tạo trong bộ nhớ
(không commit ảnh thật), tọa độ GPS là tọa độ giả. Trọng tâm (Lá Chắn T-046 số 7, 8; T-049 điều
kiện 4; T-050 điều kiện 4):
- byte gửi lên đúng ``WebImage.data`` và còn GPS đúng giá trị (quyết định 5A);
- tên file chỉ từ ``naming.image_file_name`` (thẻ đã chuẩn hóa, alt đã duyệt);
- alt/chú thích gỡ ký tự rộng 0 và escape Markdown rồi mới escape HTML; ``<figure>`` do code dựng,
  qua ``sanitize_html``; không lớp ``wp-image-N`` (không để WordPress chọn cỡ nhỏ mất GPS);
- chỉ tạo nháp, ảnh đại diện chỉ cho bài nháp vừa tạo (``_own_draft``), mọi đường trong
  ``ALLOWED_ROUTES``; không bao giờ ``publish``/``future``;
- lỗi giữa chừng: liệt kê ảnh đã lên thư viện, không xóa gì; kiểm sai thì chưa gửi gì.
"""

import io
import json
import re
from fractions import Fraction
from html.parser import HTMLParser
from urllib.parse import urlsplit

import pytest
from fake_wordpress import BASE_URL
from PIL import ExifTags, Image
from PIL.TiffImagePlugin import IFDRational
from pillow_heif import options as heif_options

from seo_app.images import html as image_html
from seo_app.images.process import WebImage, make_web_image
from seo_app.sanitize import AUTOLINK_BREAK, clean_ai_text, sanitize_html
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
        answer = {"id": media_id, "source_url": self.source_url(media_id), "mime_type": "x"}
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
    image = DraftImage(web, alt="Cổng inox 2 cánh sau khi sơn lại", category="Cổng inox")
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
    send(wp_client, [DraftImage(web, alt="Cổng inox", category="Cổng inox")])
    content = sent_content(fake_wp)
    # src là file đầy đủ vừa tải (không phải cỡ nhỏ -300x200…); không lớp wp-image-N, không
    # srcset/sizes: WordPress không tự thêm cỡ nhỏ đã mất GPS (quyết định 5A).
    assert f'src="{UPLOADS}cong-inox.webp"' in content
    assert "wp-image-" not in content
    assert "srcset" not in content and "sizes" not in content
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


def test_ten_file_theo_the_da_chuan_hoa_va_tranh_trung(fake_wp, wp_client, site, web):
    first = DraftImage(
        web, alt="Cổng inox", category="Cổng inox", area="Tân Phú", project_code="CT012"
    )
    second = DraftImage(
        web, alt="Cổng inox gần", category="Cổng inox", area="Tân Phú", project_code="CT012"
    )
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


def test_ma_cong_trinh_sai_mau_khong_vao_ten_file(fake_wp, wp_client, site, web):
    image = DraftImage(
        web, alt="Cổng inox", category="Cổng inox", project_code="Nhà anh Tuấn 12 Lê Lợi"
    )
    send(wp_client, [image])
    assert _file_names(fake_wp) == ["cong-inox.webp"]


def test_draft_image_khong_co_cho_cho_ten_file_goc_hay_thu_muc():
    # Không có trường nào nhận đường dẫn, tên thư mục hay tên file gốc (Lá Chắn T-049 N8).
    fields = set(DraftImage.__dataclass_fields__)
    assert fields == {
        "image", "alt", "caption", "category", "area", "project_code", "ai_generated", "featured"
    }  # fmt: skip


def test_anh_ai_co_tien_to_ten_file_va_tieu_de_khong_ma_cong_trinh(fake_wp, wp_client, site, web):
    image = DraftImage(
        web,
        alt="Minh họa cổng inox 2 cánh",
        caption="Ảnh minh họa (AI): cổng inox",
        category="Cổng inox",
        project_code="CT012",
        ai_generated=True,
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
    # Trình duyệt chỉ thấy đúng 3 thẻ do code dựng, img chỉ có 4 thuộc tính do code đặt.
    assert _browser_tags(content) == [
        ("figure", ["class"]),
        ("img", ["src", "alt", "width", "height"]),
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
        f'<figure class="wp-block-image"><img src="{SRC}" alt="Cổng inox" width="1600" '
        'height="1200"><figcaption>Sau</figcaption></figure>'
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
    first = DraftImage(web, alt="Cổng inox", category="Cổng inox")
    second = DraftImage(web_no_gps, alt="Cửa cuốn", category="Cửa cuốn", featured=True)
    result = send(wp_client, ["<h2>Phần 1</h2>", first, "<p>x</p>", second])

    calls = [(r.method, path(r)) for r in fake_wp.requests]
    assert calls == [
        ("POST", MEDIA),
        ("POST", f"{MEDIA}/101"),
        ("POST", MEDIA),
        ("POST", f"{MEDIA}/102"),
        ("POST", POST),
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
        "thẻ không phải chữ": [DraftImage(web, alt="a", category=5)],
        "thẻ quá dài": [DraftImage(web, alt="a", area="x" * 201)],
        "ai_generated lạ": [DraftImage(web, alt="a", ai_generated="yes")],
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
        "thẻ không phải chữ",
        "thẻ quá dài",
        "ai_generated lạ",
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
