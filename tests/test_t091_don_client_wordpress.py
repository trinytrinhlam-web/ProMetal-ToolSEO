"""T-091: dọn client WordPress sau T-059.

1. Surrogate lẻ trong chữ website (SL-T088-1): thay bằng «�» ở ``WordPressClient._json``, chỗ duy
   nhất đọc JSON của website (test hộp đen của Soi Lỗi ở ``tests/test_soi_loi_t088.py``).
2. ``_positive_id`` có giới hạn trên ``MAX_ID`` (2⁶³−1).
3. SL-T059-1: SiteSEO 1.4.2 lưu ``wp_unslash(sanitize_text_field(chữ))``; app nhận đúng bản đó là
   đã ghi, báo rõ khi SiteSEO bỏ mất ký tự; đoạn không đoán chắc được thì chỉ nhận khớp từng chữ.
   Site giả ở đây trả **chữ cố định** (không dùng lại hàm của client); site giả SiteSEO độc lập
   của Soi Lỗi ở ``tests/test_soi_loi_t059.py``.
4. ``check_connection`` báo tài khoản có quyền ``unfiltered_html`` không.

Chỉ site giả (``FakeWordPress``), không gọi WordPress thật.
"""

from __future__ import annotations

import json

import pytest
from fake_wordpress import BASE_URL, FakeWordPress, make_session

from seo_app.wordpress import ConnectionInfo, WordPressClient, WordPressError
from seo_app.wordpress import client as client_module
from seo_app.wordpress.client import (
    _SEO_WRITTEN,
    _SEO_WRITTEN_CHANGED,
    MAX_ID,
    _php_stripslashes,
    _positive_id,
    _siteseo_saved_form,
    _without_lone_surrogates,
)

SURROGATE = chr(0xD800)
LOW_SURROGATE = chr(0xDFFF)
REPLACEMENT = "\N{REPLACEMENT CHARACTER}"
POSTS = "/wp-json/wp/v2/posts"
POST_42 = POSTS + "/42"
ABILITY = "/wp-json/wp-abilities/v1/abilities/siteseo-posts/seo-data-update"
RUN = ABILITY + "/run"
ME = "/wp-json/wp/v2/users/me"


@pytest.fixture
def client(fake_wp):
    return WordPressClient(
        BASE_URL, "lam", "abcd efgh", session=make_session(fake_wp), write_seo=True
    )


def connection_site(fake, *, name="ProMetal", capabilities=None, user="Lâm"):
    fake.on("GET", "/wp-json/", {"name": name, "home": BASE_URL, "namespaces": ["wp/v2"]})
    fake.on("GET", ABILITY, (404, {"code": "rest_no_route"}, {}))
    fake.on("GET", ME, {"name": user, "roles": ["editor"],
                        "capabilities": {"edit_posts": True} if capabilities is None
                        else capabilities})


# ================================================================ 1. surrogate lẻ (SL-T088-1)


def test_ten_site_va_tai_khoan_co_surrogate_thanh_ky_tu_thay_the(fake_wp, client):
    connection_site(fake_wp, name=f"Pro{SURROGATE}Metal", user=f"L{LOW_SURROGATE}âm")
    info = client.check_connection()
    assert info.site_name == f"Pro{REPLACEMENT}Metal"
    assert info.user_name == f"L{REPLACEMENT}âm"
    (info.site_name + info.user_name).encode("utf-8")


def test_dia_chi_anh_co_surrogate_khong_bi_ghep_thanh_file_khac():
    """Thay, không bỏ: «a\\ud800.webp» bỏ ký tự đi là «a.webp», có thể là một ảnh khác."""
    data = {"id": 101, "source_url": f"{BASE_URL}/wp-content/uploads/a{SURROGATE}.webp"}
    cleaned = _without_lone_surrogates(data)
    assert cleaned["source_url"].endswith(f"/a{REPLACEMENT}.webp")
    assert not cleaned["source_url"].endswith("/a.webp")


def test_lam_sach_ca_ten_khoa_danh_sach_long_nhau():
    data = {
        f"k{SURROGATE}": [f"x{SURROGATE}", {"y": [f"{LOW_SURROGATE}z", 1, None, True]}],
        "so": 7,
        "ok": "Cửa sắt",
    }
    cleaned = _without_lone_surrogates(data)
    assert cleaned == {
        f"k{REPLACEMENT}": [f"x{REPLACEMENT}", {"y": [f"{REPLACEMENT}z", 1, None, True]}],
        "so": 7,
        "ok": "Cửa sắt",
    }
    json.dumps(cleaned, ensure_ascii=False).encode("utf-8")
    assert _without_lone_surrogates(f"a{SURROGATE}") == f"a{REPLACEMENT}"
    assert _without_lone_surrogates(5) == 5


def test_json_long_sau_khong_tran_ngan_xep():
    """Đi bằng ngăn xếp: dữ liệu lồng sâu hơn giới hạn đệ quy của Python vẫn làm sạch được."""
    data: list = [SURROGATE]
    for _ in range(5_000):
        data = [data]
    _without_lone_surrogates(data)
    inner = data
    for _ in range(5_000):
        inner = inner[0]
    assert inner == [REPLACEMENT]


def test_ky_tu_ngoai_bmp_hop_le_giu_nguyen(fake_wp, client):
    """Cặp surrogate đúng (emoji «\\ud83d\\ude00» trong JSON) là một ký tự hợp lệ: giữ nguyên."""
    connection_site(fake_wp, name="ProMetal \N{GRINNING FACE}")
    assert client.check_connection().site_name == "ProMetal \N{GRINNING FACE}"


def test_chu_co_dau_gach_nguoc_u_khong_bi_doi(fake_wp, client):
    """Chữ thật «\\ud800» (gạch ngược + chữ, JSON «\\\\ud800») không phải surrogate: giữ nguyên."""
    text = "Mã " + chr(0x5C) + "ud800 trong ghi chú"
    connection_site(fake_wp, name=text)
    assert client.check_connection().site_name == text


def test_khong_co_ma_thoat_surrogate_thi_khong_di_qua_du_lieu(fake_wp, client, monkeypatch):
    calls = []
    monkeypatch.setattr(client_module, "_without_lone_surrogates", calls.append)
    connection_site(fake_wp)
    client.check_connection()
    assert calls == []


# ================================================================ 2. giới hạn trên của mã


def test_positive_id_gioi_han_tren():
    assert MAX_ID == 2**63 - 1
    assert _positive_id(MAX_ID) == MAX_ID
    assert _positive_id(1) == 1
    for value in (MAX_ID + 1, 2**64, 10**30, 0, -1, True, 1.0, "7", None):
        assert _positive_id(value) is None


def test_ma_bai_qua_lon_bi_tu_choi_nhu_ma_sai(fake_wp, client):
    fake_wp.on("POST", POSTS, (201, {"id": MAX_ID + 1, "status": "draft"}, {}))
    with pytest.raises(WordPressError, match="không đúng dạng"):
        client.create_draft("A", "B")
    assert client._created_post_ids == set()


def test_ma_bai_bang_gioi_han_van_nhan(fake_wp, client):
    fake_wp.on("POST", POSTS, (201, {"id": MAX_ID, "status": "draft"}, {}))
    assert client.create_draft("A", "B").id == MAX_ID


# ================================================================ 3. SL-T059-1


@pytest.mark.parametrize(
    ("sent", "saved"),
    [
        ("Cửa sắt tại nhà | Pro-Metal", "Cửa sắt tại nhà | Pro-Metal"),
        ("Giá < 5 triệu", "Giá &lt; 5 triệu"),
        ("Cổng < 5 triệu, giảm 10% tiền công", "Cổng &lt; 5 triệu, giảm 10% tiền công"),
        ('Giá < 5 "rẻ" & \'x\'', "Giá &lt; 5 &quot;rẻ&quot; &amp; &#039;x&#039;"),
        ("Giá & rẻ < 5", "Giá & rẻ &lt; 5"),  # «&» trước «<» không bị đổi
        ("A < 1 < 2", "A &lt; 1 &lt; 2"),
        ("Giá <\t5", "Giá &lt; 5"),  # tab sau «<» cũng là khoảng trắng; tab gộp thành dấu cách
        ("Tăng 10%BE độ bền", "Tăng 10 độ bền"),
        ("Tăng 10%be độ bền", "Tăng 10 độ bền"),
        ("a%4%41b", "a"),  # bỏ «%41» thì lộ «%4b»: bỏ tiếp, như vòng lặp của PHP
        ("Giảm %41 < 5", "Giảm &lt; 5"),
        ("Giảm 5" + chr(0x5C) + "% thôi", "Giảm 5% thôi"),
        ("Đường dẫn C:" + chr(0x5C) * 2 + "x", "Đường dẫn C:" + chr(0x5C) + "x"),
        ("Cuối" + chr(0x5C), "Cuối"),
    ],
)
def test_ban_luu_cua_siteseo(sent, saved):
    assert _siteseo_saved_form(sent) == saved


@pytest.mark.parametrize(
    "sent",
    [
        "Cửa < 2m và cổng > 3m",  # «< … >»: strip_tags của PHP có thể bỏ, không đoán
        "Giá <5 triệu",  # «<» liền chữ (client chặn trước khi gửi; ở đây phòng thêm)
        "Giá <",
    ],
)
def test_khong_doan_chac_thi_khong_co_ban_luu(sent):
    assert _siteseo_saved_form(sent) is None


def test_stripslashes_cua_php():
    backslash = chr(0x5C)
    assert _php_stripslashes(f"a{backslash}b") == "ab"
    assert _php_stripslashes(f"a{backslash * 2}b") == f"a{backslash}b"
    assert _php_stripslashes(f"a{backslash}0b") == "a\x00b"
    assert _php_stripslashes(f"a{backslash}") == "a"
    assert _php_stripslashes("Cửa sắt") == "Cửa sắt"


def seo_site(fake, saved_title=None, saved_description=""):
    fake.on("POST", POSTS, (201, {"id": 42, "status": "draft"}, {}))
    fake.on("GET", POST_42, {"id": 42, "status": "draft", "meta": {}})
    fake.on("GET", ABILITY, {"name": "siteseo-posts/seo-data-update"})
    post = {"title": saved_title, "description": saved_description, "focus_keyphrase": "",
            "canonical_url": None, "seo_score": None}
    fake.on("POST", RUN, {"updated": True, "post": post})


def write_title(fake, client, sent, saved):
    seo_site(fake, saved)
    client.create_draft("A", "B")
    return client.set_seo_meta(42, title=sent)


@pytest.mark.parametrize(
    ("sent", "saved"),
    [
        ("Cửa sắt giá < 2 triệu", "Cửa sắt giá &lt; 2 triệu"),
        ("Cổng inox < 5 triệu, giảm 10% tiền công | Pro-Metal",
         "Cổng inox &lt; 5 triệu, giảm 10% tiền công | Pro-Metal"),
    ],
)
def test_dau_nho_hon_thanh_ma_ky_tu_la_da_ghi_va_bao_binh_thuong(fake_wp, client, sent, saved):
    """«&lt;» hiện ra y như «<» trên trang: báo đã ghi như thường."""
    result = write_title(fake_wp, client, sent, saved)
    assert result.written and result.message == _SEO_WRITTEN


@pytest.mark.parametrize(
    ("sent", "saved"),
    [
        ("Tăng 10%BE độ bền cho cổng sắt", "Tăng 10 độ bền cho cổng sắt"),
        ("Giảm giá 5" + chr(0x5C) + "% cho cổng sắt", "Giảm giá 5% cho cổng sắt"),
    ],
)
def test_siteseo_bo_ky_tu_thi_bao_da_ghi_kem_nhac_xem_lai(fake_wp, client, sent, saved):
    result = write_title(fake_wp, client, sent, saved)
    assert result.written
    assert result.message == _SEO_WRITTEN_CHANGED
    assert "xem lại" in result.message and sent not in result.message


@pytest.mark.parametrize(
    ("sent", "saved"),
    [
        ("Cửa sắt giá < 2 triệu", "Cửa sắt giá &lt;2 triệu"),  # lệch một dấu cách
        ("Cửa sắt giá < 2 triệu", "Cửa sắt giá &amp;lt; 2 triệu"),  # mã hóa hai lần
        ("Cửa sắt giá < 2 triệu", "Cửa sắt giá &#60; 2 triệu"),  # mã khác SiteSEO
        ('Giá < 5 "rẻ" \'x\'', "Giá &lt; 5 &quot;rẻ&quot; &#x27;x&#x27;"),  # html.escape của Python
        ("Tăng 10%BE độ bền", "Tăng 10%BE độ bền thêm"),
        ("Tăng 10%BE độ bền", "Tăng 10% độ bền"),
        ("Cửa < 2m và cổng > 3m", "Cửa 3m"),  # không đoán chắc: chỉ nhận khớp từng chữ
        ("Cửa sắt", None),
        ("Cửa sắt", ""),
    ],
)
def test_khac_ban_luu_cua_siteseo_van_la_chua_ghi(fake_wp, client, sent, saved):
    result = write_title(fake_wp, client, sent, saved)
    assert result.written is False and result.reason == "error"


def test_doan_khong_doan_chac_ma_luu_nguyen_van_la_da_ghi(fake_wp, client):
    sent = "Cửa < 2m và cổng > 3m"
    result = write_title(fake_wp, client, sent, sent)
    assert result.written and result.message == _SEO_WRITTEN


def test_mo_ta_cung_so_theo_ban_luu(fake_wp, client):
    seo_site(fake_wp, "Cửa sắt", "Giá &lt; 3 triệu, lắp trong ngày.")
    client.create_draft("A", "B")
    result = client.set_seo_meta(42, title="Cửa sắt", description="Giá < 3 triệu, lắp trong ngày.")
    assert result.written and result.message == _SEO_WRITTEN


# ================================================================ 4. unfiltered_html


@pytest.mark.parametrize(
    ("capabilities", "expected"),
    [
        ({"edit_posts": True, "unfiltered_html": True}, True),
        ({"edit_posts": True, "unfiltered_html": False}, False),
        ({"edit_posts": True}, False),
        ({"unfiltered_html": "true"}, False),
        ({"unfiltered_html": 1}, False),
        ([], False),
    ],
)
def test_check_connection_bao_quyen_unfiltered_html(fake_wp, client, capabilities, expected):
    connection_site(fake_wp, capabilities=capabilities)
    info = client.check_connection()
    assert info.can_unfiltered_html is expected
    if expected:
        assert info.unfiltered_html_status == ""
    else:
        assert "unfiltered_html" in info.unfiltered_html_status
        assert "GPS" in info.unfiltered_html_status


def test_connection_info_cu_van_tao_duoc_va_mac_dinh_la_khong_co_quyen():
    info = ConnectionInfo("ProMetal", BASE_URL, "Lâm", ("editor",), True, True, True)
    assert info.can_unfiltered_html is False
    assert info.unfiltered_html_status


def test_check_connection_van_chi_doc(fake_wp, client):
    connection_site(fake_wp, capabilities={"unfiltered_html": True})
    client.check_connection()
    assert {r.method for r in fake_wp.requests} == {"GET"}


def test_fake_wordpress_tra_dung_ma_thoat_surrogate():
    """Kiểm dụng cụ test: site giả gửi surrogate lẻ dưới dạng mã thoát JSON «\\ud800»."""
    fake = FakeWordPress()
    fake.on("GET", "/wp-json/", {"name": SURROGATE})
    session = make_session(fake)
    raw = session.get(f"{BASE_URL}/wp-json/").content
    assert chr(0x5C).encode() + b"ud800" in raw
