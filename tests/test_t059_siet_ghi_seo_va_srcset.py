"""T-059 bước 7: siết code theo kết quả thử thật trên website ngày 2026-10-27.

Chỉ dùng site giả (``FakeWordPress``), không gọi WordPress thật. Ảnh là ảnh giả tạo trong bộ nhớ.

1. ``_ability_confirms`` chỉ nhận khuôn trả lời thật của SiteSEO 1.4.2:
   ``{"updated": true, "post": {…}}``; ``post`` bắt buộc, chữ đã lưu đúng từng chữ đã gửi;
   khuôn ``{"success": true}`` không còn được nhận.
2. Ảnh trong bài có sẵn ``srcset`` một ứng viên (chính file đầy đủ): WordPress lõi
   (``wp_filter_content_tags``) không tự thêm các cỡ nhỏ đã mất GPS, kể cả khi phía website gắn
   lớp ``wp-image-<mã>`` vào ``<img>`` (điều đã thấy trên site thật: ``wp-image-951``).
"""

import html
import json
import re
from html.parser import HTMLParser
from urllib.parse import urlsplit

import pytest
import test_wordpress_images as wi
from fake_wordpress import BASE_URL, make_session

from seo_app.images import html as image_html
from seo_app.images.process import make_web_image
from seo_app.sanitize import sanitize_html
from seo_app.wordpress import WordPressClient
from seo_app.wordpress.client import _SEO_ERROR, _SEO_WRITTEN, DraftImage, _ability_confirms

POSTS = "/wp-json/wp/v2/posts"
POST_42 = POSTS + "/42"
ABILITY = "/wp-json/wp-abilities/v1/abilities/siteseo-posts/seo-data-update"
RUN = ABILITY + "/run"
# Chữ như lần thử thật (bước 2 của phiếu): có «< 5 triệu» và «10%».
TITLE = "Cổng inox < 5 triệu, giảm 10% tiền công | Pro-Metal"
DESC = "Cổng inox 2 cánh dưới 5 triệu: giảm 10% tiền công lắp, bảo hành 12 tháng tại Tân Phú."
KEYWORD = "cổng inox giá rẻ"
SECRET = "LOI-MAY-CHU-KHONG-DUOC-CHEP"


def real_answer(title=TITLE, description=DESC, keyword=KEYWORD, **post_changes):
    """Câu trả lời 200 của ``seo-data-update/run`` đúng khuôn đã thấy trên site thật (27/10).

    Ghi chép của Chỉ Huy lược bớt các khóa giữa của ``social`` (``og_title`` … ``twitter_image``);
    mọi giá trị ở đó là ``null`` như bài mới.
    """
    post = {
        "title": title,
        "description": description,
        "canonical_url": None,
        "focus_keyphrase": keyword,
        "seo_score": None,
        "robots": {
            "noindex": False,
            "nofollow": False,
            "noimageindex": False,
            "noarchive": False,
            "nosnippet": False,
        },
        "social": {
            "og_title": None,
            "og_description": None,
            "og_image": None,
            "twitter_title": None,
            "twitter_description": None,
            "twitter_image": None,
        },
    }
    post.update(post_changes)
    return {"updated": True, "post": post}


def body(request):
    return json.loads(request.body) if request.body else None


@pytest.fixture
def client(fake_wp):
    return WordPressClient(
        BASE_URL, "lam", "abcd efgh", session=make_session(fake_wp), write_seo=True
    )


def draft_site(fake, run):
    fake.on("POST", POSTS, (201, {"id": 42, "status": "draft"}, {}))
    fake.on("GET", POST_42, {"id": 42, "status": "draft", "meta": {}})
    fake.on("GET", ABILITY, {"name": "siteseo-posts/seo-data-update"})
    fake.on("POST", RUN, run)


def write_seo(client, **fields):
    client.create_draft("Cổng inox", "<p>Nội dung</p>")
    return client.set_seo_meta(42, **fields)


def run_requests(fake):
    return [r for r in fake.requests if r.method == "POST" and urlsplit(r.url).path == RUN]


# ================================================================ 1. _ability_confirms


def test_khuon_tra_loi_that_cua_siteseo_la_da_ghi(fake_wp, client):
    draft_site(fake_wp, real_answer())
    result = write_seo(client, title=TITLE, description=DESC, focus_keyword=KEYWORD)
    assert result.written is True
    assert result.route == "abilities"
    assert result.message == _SEO_WRITTEN
    # Gửi đúng chữ (có «%», «<»), không thêm trường nào khác (canonical, robots để SiteSEO).
    (sent,) = run_requests(fake_wp)
    assert body(sent) == {
        "input": {
            "postId": 42,
            "title": TITLE,
            "description": DESC,
            "focus_keyphrase": KEYWORD,
        }
    }


def test_chi_gui_mot_truong_thi_chi_so_truong_do(fake_wp, client):
    """SiteSEO trả cả ``post``; trường không gửi giữ giá trị cũ (ở đây: rỗng), không cần khớp."""
    draft_site(fake_wp, real_answer(description="", keyword=""))
    assert write_seo(client, title=TITLE).written is True


@pytest.mark.parametrize(
    "answer",
    [
        pytest.param({"success": True}, id="khuon-success-cu"),
        pytest.param({"success": True, "post": real_answer()["post"]}, id="success-thay-updated"),
        pytest.param({"updated": True}, id="thieu-post"),
        pytest.param({"updated": True, "post": None}, id="post-null"),
        pytest.param({"updated": True, "post": []}, id="post-danh-sach"),
        pytest.param({"updated": True, "post": json.dumps(real_answer()["post"])}, id="post-chu"),
        pytest.param({"updated": True, "post": {}}, id="post-rong"),
        pytest.param({"post": real_answer()["post"]}, id="thieu-updated"),
        pytest.param({**real_answer(), "updated": "true"}, id="updated-chu"),
        pytest.param({**real_answer(), "updated": 1}, id="updated-so"),
        pytest.param({**real_answer(), "updated": None}, id="updated-null"),
        pytest.param({**real_answer(), "updated": False}, id="updated-false"),
        pytest.param({**real_answer(), "success": False}, id="success-false"),
        pytest.param({**real_answer(), "success": None}, id="success-null"),
        pytest.param({**real_answer(), "success": "true"}, id="success-chu"),
        pytest.param({**real_answer(), "code": "forbidden"}, id="co-ma-loi"),
        pytest.param(real_answer(title=TITLE.replace("%", "&#37;")), id="phan-tram-bi-doi"),
        # T-091 (SL-T059-1): «<» thành «&lt;» đúng như SiteSEO lưu nay là đã ghi
        # (tests/test_t091_don_client_wordpress.py); mã hóa khác cách SiteSEO thì vẫn chưa ghi.
        pytest.param(real_answer(title=TITLE.replace("<", "&amp;lt;")), id="dau-nho-hon-bi-doi"),
        pytest.param(real_answer(title=TITLE + " "), id="tieu-de-thua-cach"),
        pytest.param(real_answer(description=None), id="mo-ta-null"),
        pytest.param(real_answer(keyword=""), id="tu-khoa-rong"),
        pytest.param(
            {"updated": True, "post": {**real_answer()["post"], "focus_keyword": KEYWORD,
                                       "focus_keyphrase": None}},
            id="tu-khoa-sai-ten-truong",
        ),
        pytest.param([real_answer()], id="danh-sach"),
        pytest.param(True, id="true-tran"),
    ],
)
def test_khuon_khac_khuon_that_la_chua_ghi(fake_wp, client, answer):
    draft_site(fake_wp, answer)
    result = write_seo(client, title=TITLE, description=DESC, focus_keyword=KEYWORD)
    assert result.written is False
    assert result.reason == "error"
    assert result.message == _SEO_ERROR.format(code="")  # câu cố định, không chép lời máy chủ


def test_cau_tra_loi_loi_khong_chep_loi_may_chu(fake_wp, client):
    draft_site(fake_wp, {"success": True, "message": SECRET})
    result = write_seo(client, title=TITLE)
    assert result.written is False
    assert SECRET not in result.message


def test_khoa_la_them_vao_khuon_that_van_nhan(fake_wp, client):
    """Bản SiteSEO sau thêm khóa (không phải ``success``/``code``) thì vẫn nhận: thứ quyết định là
    ``updated is True`` và chữ đã lưu trong ``post``."""
    draft_site(fake_wp, {**real_answer(), "message": "Saved"})
    assert write_seo(client, title=TITLE, description=DESC, focus_keyword=KEYWORD).written


def test_ability_confirms_truc_tiep():
    fields = {"title": TITLE, "focus_keyword": KEYWORD}
    assert _ability_confirms(real_answer(), fields)
    assert not _ability_confirms({"success": True}, fields)
    assert not _ability_confirms({"updated": True}, fields)
    # Không có gì để so thì không phải lời xác nhận (nơi gọi không bao giờ gửi rỗng).
    assert not _ability_confirms(real_answer(), {})


# ================================================================ 2. srcset của ảnh trong bài

SRC = f"{wi.UPLOADS}cong-inox.webp"
UPLOADS_BASEURL = f"{BASE_URL}/wp-content/uploads/"

# ----- WordPress giả lập: đường dựng srcset khi in bài -----------------------------------------
# Chép từ ``wp-includes/media.php`` (WordPress trunk, đọc ngày 2026-10-27):
# ``wp_filter_content_tags`` → ``wp_img_tag_add_srcset_and_sizes_attr`` →
# ``wp_image_add_srcset_and_sizes`` → ``wp_calculate_image_srcset`` /
# ``wp_calculate_image_sizes``. Bỏ phần không liên quan (iframe,
# ảnh GIF, ảnh sửa trong WordPress, bộ lọc ``apply_filters`` để mặc định).
_WP_CONTENT_TAG = re.compile(r"<(img|iframe)\s[^>]+>")
_WP_IMAGE_CLASS = re.compile(r"wp-image-([0-9]+)", re.IGNORECASE)
_WP_MAX_SRCSET_WIDTH = 2048  # ``max_srcset_image_width`` mặc định


def wp_meta(file_name: str, width: int = 1600, height: int = 1200) -> dict:
    """``wp_get_attachment_metadata`` của ảnh vừa tải: các cỡ WordPress tự tạo (không còn GPS).

    Cỡ như site thật ngày 27/10 (``srcset`` có 800w, 768w, 300w); ``thumbnail`` cắt vuông nên
    lệch tỷ lệ, không vào ``srcset``.
    """
    stem = file_name.rsplit(".", 1)[0]

    def size(w, h):
        return {"file": f"{stem}-{w}x{h}.webp", "width": w, "height": h}

    sizes = {
        "thumbnail": size(150, 150),
        "medium": size(300, 225),
        "medium_large": size(768, 576),
        "large": size(800, 600),
    }
    return {
        "file": f"2026/10/{file_name}",
        "width": width,
        "height": height,
        # WordPress không tạo cỡ lớn hơn ảnh gốc.
        "sizes": {name: item for name, item in sizes.items() if item["width"] < width},
    }


def _wp_constrain(width, height, max_width):
    """``wp_constrain_dimensions( $w, $h, $max_w )`` (chỉ giới hạn bề ngang)."""
    if width <= max_width:
        return width, height
    ratio = max_width / width
    return max(1, round(width * ratio)), max(1, round(height * ratio))


def _wp_matches_ratio(source_w, source_h, target_w, target_h):
    """``wp_image_matches_ratio``: cùng tỷ lệ, lệch không quá 1 px."""
    if source_w > target_w:
        constrained, expected = _wp_constrain(source_w, source_h, target_w), (target_w, target_h)
    else:
        constrained, expected = _wp_constrain(target_w, target_h, source_w), (source_w, source_h)
    return all(abs(a - b) <= 1 for a, b in zip(constrained, expected, strict=True))


def _wp_calculate_image_srcset(size_array, image_src, meta):
    width, height = size_array
    dirname = meta["file"].rsplit("/", 1)[0] + "/"
    candidates = [*meta["sizes"].values()]
    candidates.append(
        {"file": meta["file"].rsplit("/", 1)[1], "width": meta["width"], "height": meta["height"]}
    )
    sources: dict[int, str] = {}
    src_matched = False
    for image in candidates:
        is_src = False
        if not src_matched and dirname + image["file"] in image_src:
            src_matched = is_src = True
        if image["width"] > _WP_MAX_SRCSET_WIDTH and not is_src:
            continue
        if _wp_matches_ratio(width, height, image["width"], image["height"]):
            url = UPLOADS_BASEURL + dirname + image["file"]
            if is_src:  # PHP: array( w => source ) + $sources (ảnh của src đứng đầu)
                sources = {image["width"]: url, **sources}
            else:
                sources[image["width"]] = url
    if not src_matched or len(sources) < 2:
        return ""
    return ", ".join(f"{url.replace(' ', '%20')} {w}w" for w, url in sources.items())


def _wp_image_add_srcset_and_sizes(image, meta):
    if not meta or not meta.get("sizes"):
        return image
    match_src = re.search(r'src="([^"]+)"', image)
    image_src = match_src.group(1).split("?", 1)[0] if match_src else ""
    if not image_src:
        return image
    match_w = re.search(r' width="([0-9]+)"', image)
    match_h = re.search(r' height="([0-9]+)"', image)
    width, height = int(match_w.group(1)) if match_w else 0, int(match_h.group(1)) if match_h else 0
    if not (width and height):
        return image
    srcset = _wp_calculate_image_srcset((width, height), image_src, meta)
    if not srcset:
        return image
    attr = f' srcset="{html.escape(srcset)}"'
    if " sizes=" not in image:
        attr += f' sizes="(max-width: {width}px) 100vw, {width}px"'
    return re.sub(r"<img ([^>]+?)[/ ]*>", lambda m: f"<img {m.group(1)}{attr} />", image, count=1)


def wp_filter_content_tags(content: str, attachments: dict[int, dict]) -> str:
    """Nội dung bài sau bộ lọc ``the_content`` của WordPress lõi (phần ``srcset``).

    Mã ảnh **chỉ** lấy từ lớp ``wp-image-N``; ``srcset`` chỉ được thêm khi
    ``$attachment_id > 0 && ! str_contains( $filtered_image, ' srcset=' )``.
    """

    def filter_tag(match: re.Match) -> str:
        tag = match.group(0)
        if match.group(1) != "img":
            return tag
        class_id = _WP_IMAGE_CLASS.search(tag)
        attachment_id = int(class_id.group(1)) if class_id else 0
        if attachment_id > 0 and " srcset=" not in tag:
            tag = _wp_image_add_srcset_and_sizes(tag, attachments.get(attachment_id))
        return tag

    return _WP_CONTENT_TAG.sub(filter_tag, content)


def site_adds_wp_image_class(content: str, media_id: int = 951) -> str:
    """Điều đã thấy trên site thật: phía website gắn ``class="wp-image-<mã>"`` vào ``<img>``."""
    return content.replace("<img ", f'<img class="wp-image-{media_id}" ', 1)


def wordpress_lazy_attrs(content: str) -> str:
    """WordPress tự thêm ``decoding``/``loading`` vào thẻ ảnh khi in (không cần mã ảnh)."""
    return content.replace("<img ", '<img decoding="async" loading="lazy" ')


def img_attrs(content: str) -> list[dict[str, str | None]]:
    """Thuộc tính của từng thẻ ``<img>`` như trình duyệt đọc (giải mã ``&amp;``, ``&#91;``)."""
    found = []

    class Reader(HTMLParser):
        def handle_starttag(self, tag, attrs):
            if tag == "img":
                found.append(dict(attrs))

    Reader(convert_charrefs=True).feed(content)
    return found


def test_figure_html_co_srcset_mot_ung_vien_la_file_day_du():
    out = image_html.figure_html(src=SRC, alt="Cổng inox", width=1600, height=1200, caption="Sau")
    assert out == (
        f'<figure class="wp-block-image"><img src="{SRC}" alt="Cổng inox" srcset="{SRC} 1x" '
        'width="1600" height="1200"><figcaption>Sau</figcaption></figure>'
    )
    assert sanitize_html(out) == out
    (attrs,) = img_attrs(out)
    candidates = [item.split() for item in attrs["srcset"].split(",")]
    assert candidates == [[SRC, "1x"]]  # trình duyệt chỉ còn một lựa chọn: file 1600 px
    # Không ghi ``sizes`` (vô nghĩa với ứng viên "x") và ``loading`` (WordPress tự đặt theo vị
    # trí ảnh: ảnh đầu bài không bị lười tải); không lớp ``wp-image-N``.
    assert "sizes" not in attrs and "loading" not in attrs and "class" not in attrs


ATTACHMENTS = {951: wp_meta("cong-inox.webp")}


def test_gia_lap_tai_hien_dung_loi_that_27_10():
    """Thẻ cũ (trước T-059: không ``srcset``) và lớp ``wp-image-951`` do website gắn: WordPress
    thêm các cỡ nhỏ như trang thật ngày 27/10. App không gắn lớp thì lõi không thêm gì."""
    old = (
        f'<figure class="wp-block-image"><img src="{SRC}" alt="Cổng" width="1600" '
        'height="1200"></figure>'
    )
    assert wp_filter_content_tags(old, ATTACHMENTS) == old
    out = wp_filter_content_tags(site_adds_wp_image_class(old), ATTACHMENTS)
    (attrs,) = img_attrs(out)
    assert [item.split()[1] for item in attrs["srcset"].split(", ")] == [
        "1600w", "300w", "768w", "800w"
    ]
    assert f"{wi.UPLOADS}cong-inox-300x225.webp 300w" in attrs["srcset"]
    assert attrs["sizes"] == "(max-width: 1600px) 100vw, 1600px"


def _class_after_src(content):
    return re.sub(r"(<img [^>]*)>", r'\1 class="aligncenter size-full wp-image-951">', content,
                  count=1)


@pytest.mark.parametrize(
    "change",
    [
        pytest.param(lambda c: c, id="nguyen-van"),
        pytest.param(site_adds_wp_image_class, id="website-gan-wp-image-dau-the"),
        pytest.param(_class_after_src, id="website-gan-nhieu-lop-cuoi-the"),
        pytest.param(lambda c: site_adds_wp_image_class(c).replace("wp-image", "WP-IMAGE"),
                     id="lop-chu-hoa"),
        pytest.param(lambda c: wordpress_lazy_attrs(site_adds_wp_image_class(c)),
                     id="gan-lop-va-loading-lazy"),
    ],
)
def test_wordpress_khong_doi_srcset_cua_app_du_noi_dung_bi_doi(change):
    out = change(image_html.figure_html(src=SRC, alt="Cổng inox", width=1600, height=1200))
    filtered = wp_filter_content_tags(out, ATTACHMENTS)
    assert filtered == out  # WordPress để nguyên thẻ ảnh: không thêm srcset, sizes
    (attrs,) = img_attrs(filtered)
    assert attrs["srcset"] == f"{SRC} 1x" and "sizes" not in attrs


def test_gioi_han_kses_bo_srcset_thi_loi_quay_lai():
    """Giới hạn (ghi trong báo cáo): tài khoản không có quyền ``unfiltered_html`` thì kses bỏ
    ``srcset`` khi lưu (``$allowedposttags['img']`` không có ``srcset``); website mà gắn lớp
    ``wp-image-<mã>`` thì WordPress lại thêm cỡ nhỏ. Thử lại trên site thật mới biết chắc."""
    out = image_html.figure_html(src=SRC, alt="Cổng inox", width=1600, height=1200)
    saved_by_kses = re.sub(r' srcset="[^"]*"', "", out)
    filtered = wp_filter_content_tags(site_adds_wp_image_class(saved_by_kses), ATTACHMENTS)
    assert "cong-inox-300x225.webp 300w" in filtered


def test_srcset_vo_hieu_shortcode_nhu_src():
    src = f"{wi.UPLOADS}cong[caption]x[/caption].webp"
    out = image_html.figure_html(src=src, alt="Cổng", width=10, height=10)
    assert "[" not in out and "]" not in out
    (attrs,) = img_attrs(out)
    assert attrs["src"] == src
    assert attrs["srcset"] == f"{src} 1x"


def test_dia_chi_co_dau_phay_bi_tu_choi():
    """Dấu phẩy tách ứng viên trong ``srcset``: địa chỉ có dấu phẩy không được dựng thành ảnh."""
    with pytest.raises(image_html.ImageHtmlError):
        image_html.figure_html(src=f"{wi.UPLOADS}a,b.webp", alt="Cổng", width=10, height=10)


def test_dia_chi_co_dau_va_van_dung_trong_ca_hai_thuoc_tinh():
    src = f"{wi.UPLOADS}a.webp?v=1&w=2"
    out = image_html.figure_html(src=src, alt="Cổng", width=10, height=10)
    assert 'src="https://example.com/wp-content/uploads/2026/10/a.webp?v=1&amp;w=2"' in out
    (attrs,) = img_attrs(out)
    assert attrs["src"] == src and attrs["srcset"] == f"{src} 1x"


def test_bo_loc_bo_srcset_thi_dung_khong_gui_anh(monkeypatch):
    """Chốt cuối: ``srcset`` mất sau bộ lọc (WordPress sẽ lại tự thêm cỡ nhỏ) thì không dựng ảnh,
    kể cả khi chữ chú thích giả dạng đúng thuộc tính ``srcset`` (LC-T054-6)."""
    real = image_html.sanitize_html

    def drop_srcset(text):
        return re.sub(r' srcset="[^"]*"', "", real(text), count=1)

    monkeypatch.setattr(image_html, "sanitize_html", drop_srcset)
    with pytest.raises(image_html.ImageHtmlError):
        image_html.figure_html(
            src=SRC, alt="Cổng", width=10, height=10, caption=f' srcset="{SRC} 1x"'
        )


@pytest.fixture
def web():
    return make_web_image(wi._jpeg())


def test_gui_nhap_kem_anh_moi_anh_co_srcset_file_day_du(fake_wp, wp_client, web):
    wi.Site(fake_wp)
    first = DraftImage(web, alt="Cổng inox 2 cánh", featured=True)
    second = DraftImage(web, alt="Cửa cuốn khe thoáng")
    result = wp_client.create_draft_with_images(
        "Sửa cổng inox Tân Phú", ["<p>Mở bài</p>", first, "<p>Giữa</p>", second, first]
    )
    content = wi.sent_content(fake_wp)
    images = img_attrs(content)
    assert len(images) == 3
    urls = [image.source_url for image in result.images]
    assert [attrs["src"] for attrs in images] == [urls[0], urls[1], urls[0]]
    for attrs in images:
        # Một ứng viên, đúng file đầy đủ vừa tải (không phải cỡ -300x225…), GPS còn trong file.
        assert attrs["srcset"] == f"{attrs['src']} 1x"
        assert "sizes" not in attrs and "class" not in attrs
        assert (attrs["width"], attrs["height"]) == (str(web.width), str(web.height))
    assert "wp-image-" not in content
    # Website gắn ``wp-image-<mã>`` cho từng ảnh: WordPress giả lập không đổi gì. Cùng nội dung bỏ
    # srcset thì WordPress thêm cỡ nhỏ (bộ giả lập nhận đúng mã ảnh, đúng file).
    attachments, tagged = {}, content
    for image in result.images:
        attachments[image.id] = wp_meta(image.file_name, web.width, web.height)
        src_attr = f'src="{image.source_url}"'
        tagged = tagged.replace(f"<img {src_attr}", f'<img class="wp-image-{image.id}" {src_attr}')
    assert tagged.count("wp-image-") == 3
    assert wp_filter_content_tags(tagged, attachments) == tagged
    without_srcset = re.sub(r' srcset="[^"]*"', "", tagged)
    assert wp_filter_content_tags(without_srcset, attachments).count("-300x225.webp 300w") == 3
