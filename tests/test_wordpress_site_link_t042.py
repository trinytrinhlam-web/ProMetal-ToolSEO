"""T-042 (LC-T037-1 a, b): link lấy từ site không được có ``" ' < > ` `` trần hay ký tự vô
hình; tiêu đề/meta lấy từ site được bỏ ký tự vô hình. Không gọi mạng."""

import pytest
from fake_wordpress import BASE_URL

from seo_app.wordpress import PublishedItem, is_site_link
from seo_app.wordpress.client import _clean_text, _published_from

B = "https://suachuacuasat.com"


@pytest.mark.parametrize(
    "link",
    [
        B + '/a"onmouseover="alert(1)',
        B + "/a'><script>x</script>",
        B + "/a<b",
        B + "/a>b",
        B + "/a`b",
        B + "/‮gnp.exe",  # đảo chiều
        B + "/a​b",  # rộng 0
        B + "/a﻿b",  # BOM
        B + "/a­b",  # gạch nối mềm
        B + "/a⁦b",  # cô lập hướng chữ
        "https://suachuacuasat.com​/a",
    ],
)
def test_site_link_refuses_quotes_brackets_and_invisible(link):
    assert not is_site_link(link, B)


@pytest.mark.parametrize(
    "link",
    [
        B + "/",
        B + "/cua-sat-2-canh/",
        B + "/?p=42",
        B + "/c%E1%BB%ADa-s%E1%BA%AFt/",
        B + "/a%22b",  # dấu " đã mã hóa thì được
        B + "/a#muc-1",
        "HTTPS://SUACHUACUASAT.COM/x",
        B + "/cửa-sắt/",  # chữ có dấu (không phải ký tự vô hình)
    ],
)
def test_site_link_still_accepts_normal_links(link):
    assert is_site_link(link, B)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Cửa​ sắt", "Cửa sắt"),
        ("‮Cửa sắt", "Cửa sắt"),
        ("Cửa­ sắt﻿", "Cửa sắt"),
        ("A &lt;b&gt;⁦ B", "A <b> B"),
        ("Bình thường", "Bình thường"),
    ],
)
def test_clean_text_drops_invisible_chars(raw, expected):
    assert _clean_text(raw, 300) == expected


def test_published_item_from_site_drops_invisible_chars_and_bad_links():
    raw = {
        "id": 5,
        "status": "publish",
        "slug": "a",
        "link": f"{BASE_URL}/a/",
        "title": {"rendered": "Ti​êu‮ đề"},
        "meta": {"_siteseo_titles_title": "M​eta", "_siteseo_titles_desc": "﻿Mô tả"},
    }
    item = _published_from(raw, "post", BASE_URL)
    assert item is not None
    assert (item.title, item.meta_title, item.meta_desc) == ("Tiêu đề", "Meta", "Mô tả")
    assert _published_from({**raw, "link": f'{BASE_URL}/a"x'}, "post", BASE_URL) is None
    assert _published_from({**raw, "link": f"{BASE_URL}/a​"}, "post", BASE_URL) is None


@pytest.mark.parametrize("field", ["title", "meta_title", "meta_desc"])
def test_published_item_refuses_invisible_chars(field):
    """File cache bị sửa tay chèn ký tự vô hình: dựng lại ``PublishedItem`` thì sai khuôn
    (cache bị coi là hỏng và tải lại)."""
    values = {"id": 1, "type": "post", "slug": "a", "link": f"{BASE_URL}/a/", "title": "A"}
    values[field] = "x‮y"
    with pytest.raises(ValueError):
        PublishedItem(**values)
