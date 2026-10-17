"""T-042 (SL-T037-3): thiếu hoặc sai header ``X-WP-TotalPages`` không làm danh sách bị cắt
lặng lẽ, ở cả ``list_published`` lẫn chuyên mục/thẻ (``_get_all_pages``). Chỉ site giả."""

import pytest
from fake_wordpress import BASE_URL, query

from seo_app.wordpress import WordPressError
from seo_app.wordpress.client import MAX_PAGES, PER_PAGE


def raw_post(id_):
    return {
        "id": id_,
        "status": "publish",
        "slug": f"bai-{id_}",
        "link": f"{BASE_URL}/bai-{id_}/",
        "title": {"rendered": f"Bài {id_}"},
    }


def term(id_):
    return {"id": id_, "name": f"Mục {id_}", "slug": f"muc-{id_}", "count": 1, "parent": 0}


def paged(total, make, *, header=None, beyond="empty"):
    """Site có ``total`` mục; ``header`` gửi kèm (None: không gửi). ``beyond``: trang quá số
    trang trả gì ("empty": danh sách rỗng, "400": lỗi của WordPress)."""

    def handler(request):
        page = int(query(request)["page"][0])
        start = (page - 1) * PER_PAGE
        rows = [make(i + 1) for i in range(start, min(start + PER_PAGE, total))]
        headers = {} if header is None else {"X-WP-TotalPages": header}
        if not rows and page > 1 and beyond == "400":
            return 400, {"code": "rest_post_invalid_page_number", "message": "x"}, headers
        return 200, rows, headers

    return handler


BAD_HEADERS = [None, "", "abc", "60.0", "-5", "0", "1e2", " ", "٣"]


@pytest.mark.parametrize("header", BAD_HEADERS)
@pytest.mark.parametrize("beyond", ["empty", "400"])
def test_published_reads_on_without_header(fake_wp, wp_client, header, beyond):
    fake_wp.on("GET", "/wp-json/wp/v2/posts", paged(250, raw_post, header=header, beyond=beyond))
    fake_wp.on("GET", "/wp-json/wp/v2/pages", [])
    items = wp_client.list_published()
    assert len(items) == 250
    assert items.truncated is False


@pytest.mark.parametrize("header", [None, "abc"])
@pytest.mark.parametrize("beyond", ["empty", "400"])
def test_exact_multiple_of_page_size_without_header(fake_wp, wp_client, header, beyond):
    """300 mục = 3 trang đầy: phải xin trang 4 để biết đã hết (rỗng hoặc lỗi "quá số trang")."""
    fake_wp.on("GET", "/wp-json/wp/v2/posts", paged(300, raw_post, header=header, beyond=beyond))
    fake_wp.on("GET", "/wp-json/wp/v2/pages", [])
    items = wp_client.list_published()
    assert len(items) == 300
    assert items.truncated is False
    pages = [query(r)["page"][0] for r in fake_wp.requests if r.path_url.startswith(
        "/wp-json/wp/v2/posts")]
    assert pages == ["1", "2", "3", "4"]


def test_without_header_stops_at_max_pages_and_flags(fake_wp, wp_client):
    total = (MAX_PAGES + 3) * PER_PAGE
    fake_wp.on("GET", "/wp-json/wp/v2/posts", paged(total, raw_post))
    fake_wp.on("GET", "/wp-json/wp/v2/pages", [])
    items = wp_client.list_published()
    assert len(items) == MAX_PAGES * PER_PAGE
    assert items.truncated is True
    assert len(fake_wp.requests) == MAX_PAGES + 1  # MAX_PAGES trang bài + 1 trang "trang"


def test_server_ignoring_page_param_does_not_loop_and_flags(fake_wp, wp_client):
    rows = [raw_post(i + 1) for i in range(PER_PAGE)]
    fake_wp.on("GET", "/wp-json/wp/v2/posts", rows)  # trang nào cũng y hệt, không header
    fake_wp.on("GET", "/wp-json/wp/v2/pages", [])
    items = wp_client.list_published()
    assert len(items) == PER_PAGE
    assert items.truncated is True
    assert len(fake_wp.requests) == 3  # bài trang 1, bài trang 2 (trùng: dừng), "trang"


def test_valid_header_is_still_trusted(fake_wp, wp_client):
    """Header đúng nói 1 trang dù trang đủ 100 mục (site có đúng 100 bài): không xin thêm."""
    fake_wp.on("GET", "/wp-json/wp/v2/posts", paged(PER_PAGE, raw_post, header="1"))
    fake_wp.on("GET", "/wp-json/wp/v2/pages", [])
    items = wp_client.list_published()
    assert len(items) == PER_PAGE
    assert items.truncated is False
    assert len(fake_wp.requests) == 2


def test_other_errors_on_later_pages_still_raise(fake_wp, wp_client):
    def handler(request):
        page = int(query(request)["page"][0])
        if page == 2:
            return 400, {"code": "rest_invalid_param", "message": "x"}, {}
        return 200, [raw_post(i + 1) for i in range(PER_PAGE)], {}

    fake_wp.on("GET", "/wp-json/wp/v2/posts", handler)
    with pytest.raises(WordPressError):
        wp_client.list_published()


def test_page_out_of_range_on_first_page_still_raises(fake_wp, wp_client):
    fake_wp.on(
        "GET",
        "/wp-json/wp/v2/posts",
        (400, {"code": "rest_post_invalid_page_number", "message": "x"}, {}),
    )
    with pytest.raises(WordPressError):
        wp_client.list_published()


@pytest.mark.parametrize("header", [None, "", "abc", "0"])
def test_categories_read_on_without_header(fake_wp, wp_client, header):
    fake_wp.on("GET", "/wp-json/wp/v2/categories", paged(230, term, header=header))
    terms = wp_client.list_categories()
    assert [t.id for t in terms] == list(range(1, 231))


def test_tags_with_valid_header(fake_wp, wp_client):
    fake_wp.on("GET", "/wp-json/wp/v2/tags", paged(150, term, header="2"))
    assert len(wp_client.list_tags()) == 150
