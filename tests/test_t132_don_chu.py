"""T-132 · Dọn chữ Giai đoạn 4 (Thợ Máy).

- Hàm công khai ``WordPressClient.recheck_draft`` thay chỗ trang Soạn bài gọi hàm riêng
  ``client._own_draft`` (hỏi lại bài còn là nháp sau khi ghi SEO qua Abilities, LC-T042-2); câu báo
  khi không hỏi được không còn nói «trước khi ghi SEO… Chưa ghi gì» ngay sau «Đã ghi SEO».
- Chú thích dưới ô «Dùng schema Hỏi đáp (FAQ) này cho bài»: app chưa gửi schema lên website.
- Bộ dò giá (SL-T036-11) và dò link (LC-T036-2) của gợi ý meta: ca mới, ca không được bắt oan.

Trang Kết nối (SL-T106-1) ở ``tests/test_t132_trang_ket_noi.py``. Chỉ WordPress giả, AI giả.
"""

from __future__ import annotations

import ast
from urllib.parse import parse_qs, urlsplit

import pytest
import requests
import test_app_images as ui
import test_t041_seo_ui as seo_ui
from fake_wordpress import BASE_URL, make_session

from seo_app.onpage.meta import accept_ai_title, has_link, mentions_price
from seo_app.text import escape_markdown
from seo_app.wordpress import WordPressClient, WordPressError
from seo_app.wordpress import client as client_module

POSTS = "/wp-json/wp/v2/posts"
POST_42 = f"{POSTS}/42"
MODIFIED = "2026-11-05T01:02:03"
KEYWORD = "cửa sắt bị xệ"
SERVER_TEXT = "<b>chuỗi lạ từ máy chủ</b> /home/site/wp-config.php"

# Fixture của bước SEO (T-041): mật khẩu thử, cache ảnh xem trước và danh sách bài trong thư mục
# tạm (ba fixture tự dùng), AI giả, WordPress giả (bài nháp 501, Abilities bật).
env = seo_ui.env
previews = seo_ui.previews
site_cache = seo_ui.site_cache
seo_ai = seo_ui.seo_ai
wordpress = seo_ui.wordpress


# ====================================================================== 1. recheck_draft


@pytest.fixture
def client(fake_wp):
    return WordPressClient(BASE_URL, "lam", "abcd efgh ijkl", session=make_session(fake_wp))


def created(client: WordPressClient, fake_wp) -> int:
    fake_wp.on("POST", POSTS, (201, {"id": 42, "status": "draft", "modified_gmt": MODIFIED}, {}))
    assert client.create_draft("Tiêu đề", "<p>Nội dung</p>").id == 42
    return 42


def answer(status: str = "draft", modified: str = MODIFIED) -> dict:
    return {"id": 42, "status": status, "meta": {}, "modified_gmt": modified}


@pytest.mark.parametrize("post_id", [42, True, "42", 42.0, None], ids=repr)
def test_recheck_draft_chi_cho_nhap_client_vua_tao(fake_wp, client, post_id):
    """Bài client này chưa tạo (hay mã sai kiểu, ``True`` không phải bài 1): từ chối, 0 lệnh."""
    with pytest.raises(WordPressError) as caught:
        client.recheck_draft(post_id)
    assert str(caught.value) == client_module._RECHECK_NOT_OWN
    assert fake_wp.requests == []


def test_recheck_draft_con_nhap_chi_mot_lenh_doc(fake_wp, client):
    post_id = created(client, fake_wp)
    fake_wp.on("GET", POST_42, answer())
    before = len(fake_wp.requests)
    assert client.recheck_draft(post_id) is None
    (request,) = fake_wp.requests[before:]
    assert request.method == "GET" and urlsplit(request.url).path == POST_42
    assert parse_qs(urlsplit(request.url).query) == {
        "context": ["edit"], "_fields": ["id,status,meta,modified_gmt"]
    }  # fmt: skip
    assert post_id in client._created_post_ids
    assert client._modified[post_id] == MODIFIED  # không bị đánh dấu «không biết»


def test_recheck_draft_bai_da_dang_thi_bao_va_thoi_coi_la_cua_app(fake_wp, client):
    post_id = created(client, fake_wp)
    fake_wp.on("GET", POST_42, answer("publish"))
    with pytest.raises(WordPressError) as caught:
        client.recheck_draft(post_id)
    assert str(caught.value) == client_module._SEO_NOT_DRAFT
    assert post_id not in client._created_post_ids
    before = len(fake_wp.requests)
    with pytest.raises(WordPressError, match="Chỉ hỏi lại được bài nháp app vừa tạo"):
        client.recheck_draft(post_id)
    assert len(fake_wp.requests) == before


def test_recheck_draft_bai_bi_sua_ngoai_app_thi_danh_dau_khong_biet(fake_wp, client):
    """Như ``_own_draft`` (T-115): giờ sửa khác lần ghi cuối thì ``release_draft`` không chuyển."""
    post_id = created(client, fake_wp)
    fake_wp.on("GET", POST_42, answer(modified="2026-11-05T09:09:09"))
    client.recheck_draft(post_id)
    assert client._modified[post_id] is None and post_id in client._created_post_ids


@pytest.mark.parametrize(
    ("reply", "code"),
    [
        ((500, {"code": "x", "message": SERVER_TEXT}, {}), " (mã 500)"),
        ((502, SERVER_TEXT.encode(), {}), " (mã 502)"),
        (requests.exceptions.ConnectionError("mất mạng"), ""),
        (requests.exceptions.ReadTimeout("hết giờ"), ""),
    ],
    ids=["500", "502-html", "mat-mang", "het-gio"],
)
def test_recheck_draft_hoi_khong_duoc_thi_cau_rieng(fake_wp, client, reply, code):
    """Không hỏi được: câu riêng của lần hỏi lại (đã ghi rồi), không phải câu «trước khi ghi SEO…
    Chưa ghi gì» của ``_SEO_CHECK_FAILED``; không chép lời máy chủ."""
    post_id = created(client, fake_wp)
    fake_wp.on("GET", POST_42, lambda _request: reply)
    with pytest.raises(WordPressError) as caught:
        client.recheck_draft(post_id)
    message = str(caught.value)
    assert message == client_module._RECHECK_FAILED.format(code=code)
    assert "Chưa ghi gì" not in message and "trước khi ghi" not in message
    assert "chuỗi lạ" not in message and "/home/site" not in message


def test_cau_hoi_lai_chi_co_mot_cho_dien_ma():
    """``_own_draft`` điền mã HTTP bằng ``str.format``: câu chỉ được có đúng chỗ ``{code}``."""
    assert client_module._RECHECK_FAILED.format(code=" (mã 503)").count("(mã 503)") == 1


# ------------------------------------------------------------- trang Soạn bài gọi hàm công khai


def test_trang_soan_bai_khong_goi_ham_rieng_cua_client(project_root):
    """T-132: ``write_seo`` gọi ``client.recheck_draft``; không còn chỗ nào trong ``app/`` đọc thuộc
    tính riêng (``client._…``) của client WordPress."""
    private = []
    for path in (project_root / "app").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        private += [
            (path.name, node.lineno, node.attr)
            for node in ast.walk(tree)
            if isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "client"
            and node.attr.startswith("_")
        ]
    assert private == []
    write = project_root / "app" / "views" / "write.py"
    callers = {
        function.name
        for function in ast.walk(ast.parse(write.read_text(encoding="utf-8")))
        if isinstance(function, ast.FunctionDef)
        for node in ast.walk(function)
        if isinstance(node, ast.Attribute) and node.attr == "recheck_draft"
    }
    assert callers == {"write_seo"}


def test_hoi_lai_sau_khi_ghi_seo_khong_duoc_thi_cau_khong_tu_mau_thuan(
    project_root, seo_ai, wordpress
):
    """Ghi SEO qua Abilities xong, lần hỏi lại bài lỗi 500: câu kết quả nói đã ghi rồi không hỏi lại
    được (không còn «trước khi ghi SEO… Chưa ghi gì» ngay sau «Đã ghi SEO»), không chép lời máy
    chủ; lần hỏi trước khi ghi vẫn có (2 lệnh đọc bài như cũ)."""
    reads = []

    def post_501(request):
        reads.append(request)
        if len(reads) == 1:  # kiểm còn nháp trước khi ghi
            return {"id": seo_ui.POST_ID, "status": "draft", "meta": {}}
        return (500, {"code": "x", "message": SERVER_TEXT}, {})

    wordpress.fake.on("GET", f"{seo_ui.POSTS}/{seo_ui.POST_ID}", post_501)
    at = seo_ui.send_with_seo(project_root, seo_ai, toggle=True)
    assert len(reads) == 2
    (info,) = [i.value for i in at.info if "Kiểm lại ngay sau khi ghi SEO" in i.value]
    assert info.startswith(escape_markdown("Đã ghi SEO vào hộp SiteSEO của bài nháp."))
    assert escape_markdown("Không hỏi lại được bài trên WordPress (mã 500)") in info
    assert "Chưa ghi gì" not in info and "trước khi ghi" not in info
    assert "chuỗi lạ" not in info and "wp-config" not in info


# ====================================================================== 2. chú thích schema FAQ


def test_o_schema_faq_noi_ro_app_chua_gui_len_website(project_root, seo_ai):
    snap = ui.article()
    snap.parts.append(seo_ui.FAQ_PART)
    at = seo_ui.to_seo(project_root, snap)
    assert any(box.key == "seo_use_faq" for box in at.checkbox)
    captions = [c.value for c in at.caption]
    assert any("app chưa gửi schema lên website" in c for c in captions), captions


def test_khong_co_o_schema_thi_khong_co_chu_thich(project_root, seo_ai):
    at = seo_ui.to_seo(project_root)
    assert not any(box.key == "seo_use_faq" for box in at.checkbox)
    assert not any("chưa gửi schema" in c.value for c in at.caption)


# ====================================================================== 3. dò giá (SL-T036-11)

PRICE = [
    "5 trăm", "chỉ 5 trăm", "giá 5 trăm/m2", "5 trăm.", "chỉ 5 trăm thôi", "tầm 2 trăm một bộ",
    "1.5 trăm", "triệu rưỡi", "tỷ rưỡi", "trăm rưỡi", "giá tính bằng VNĐ", "50 USD", "đô la Mỹ",
    "tính theo vnd",
]  # fmt: skip
NOT_PRICE = [
    "hơn 5 trăm công trình", "cách 3 trăm mét", "5 trăm năm", "2 trăm khách hàng",
    "3 trăm mẫu cửa", "4 trăm m2", "hai trăm người", "vndirect", "usda", "đô thị", "tỉ lệ",
]  # fmt: skip


@pytest.mark.parametrize("price", PRICE)
def test_cach_noi_gia_moi_bi_bat(price):
    assert mentions_price(f"Sửa cửa sắt {price} tại nhà", KEYWORD)
    assert accept_ai_title(f"Cửa sắt bị xệ: sửa {price} tại nhà", KEYWORD) is None


@pytest.mark.parametrize("ok", NOT_PRICE)
def test_so_dem_khong_bi_coi_la_gia(ok):
    assert not mentions_price(f"Cửa sắt bị xệ {ok} đẹp", KEYWORD)


def test_gia_nam_tron_trong_tu_khoa_van_bo_qua():
    """LC-T040-1 giữ nguyên với dạng mới: chữ nằm trọn trong từ khóa chính không tính."""
    assert not mentions_price("Cửa cuốn trả bằng VNĐ: chọn loại nào bền", "cửa cuốn trả bằng vnđ")
    assert mentions_price("Cửa cuốn trả bằng VNĐ: chỉ 5 trăm", "cửa cuốn trả bằng vnđ")


# ====================================================================== 4. dò link (LC-T036-2)

LINK = {
    "kirin": "evil.рф",
    "kirin-ca-hai": "пример.рф",
    "han": "ví-dụ.中国",
    "punycode-duoi": "evil.xn--p1ai",
    "punycode-nhan": "XN--P1AI.com",
    "hoa": "EVIL.SHOP",
    "hoa-la": "EVIL.WTF",
    "hoa-gach": "PRO-METAL.ONLINE",
    "cham-han": "evil\N{IDEOGRAPHIC FULL STOP}com",
    "cham-han-nua-kho": "evil\N{HALFWIDTH IDEOGRAPHIC FULL STOP}com",
    "cham-han-hoa": "EVIL\N{IDEOGRAPHIC FULL STOP}SHOP",
    "ngoac-vuong": "evil[.]com",
    "ngoac-tron": "evil(.)com",
    "dot": "evil[dot]com",
    "dot-hoa": "EVIL(DOT)SHOP",
}
NOT_LINK = {
    "tp-hcm-cham": "TP.HCM.",
    "tp-hcm-ngoac": "(TP.HCM)",
    "tp-hn": "TP.HN",
    "q-gv": "Q.GV",
    "q-bt": "Q.BT",
    "h-cc": "H.CC",
    "tp-bmt": "TP.BMT",
    "tx-tdm": "TX.TDM",
    "chu-viet": "xong.tiếp",
    "chu-viet-hoa": "XONG.TIẾP",
    "ngoac-rieng": "giá (.) đẹp",
    "hoa-dau": "Cửa.Sắt",
}


@pytest.mark.parametrize("link", LINK.values(), ids=LINK.keys())
def test_dang_ten_mien_la_bi_bat(link):
    assert has_link(f"Xem {link} ngay")
    assert accept_ai_title(f"Cửa sắt bị xệ: xem {link} để biết cách sửa", KEYWORD) is None


@pytest.mark.parametrize("ok", NOT_LINK.values(), ids=NOT_LINK.keys())
def test_viet_tat_dia_danh_khong_bi_coi_la_link(ok):
    assert not has_link(f"Cửa sắt bị xệ {ok} đẹp")


# ====================================================================== 5. lượt 2 (SL-T132-1, -2)
# Chữ lạ viết bằng chr(0x…): trông y hệt chữ Latin nên không gõ thẳng vào mã.
CYR_O, CYR_IE, GREEK_O = chr(0x043E), chr(0x0435), chr(0x03BF)
SMALL_CAP_O, DOTLESS_I, SCRIPT_G = chr(0x1D0F), chr(0x0131), chr(0x0261)
MICRO_SIGN = chr(0x00B5)  # NFKC đổi thành «μ» Hy Lạp

MIXED_LINK = {
    "nhan-e-kirin": CYR_IE + "vil.shop",
    "nhan-hoa-e-kirin": CYR_IE.upper() + "VIL.SHOP",
    "duoi-o-hoa-nho": "evil.c" + SMALL_CAP_O + "m",
    "duoi-i-khong-cham": "evil.b" + DOTLESS_I + "z",
    "duoi-g-viet-tay": "evil.or" + SCRIPT_G,
    "duoi-o-hy-lap-hoa": "EVIL.C" + GREEK_O.upper() + "M",
    "nhieu-tang-nhan-viet": "ví-dụ.evil.c" + CYR_O + "m",
    "nhieu-tang": "shop.evil.c" + CYR_O + "m",
    "ba-tang-ngan": "a.b.c" + CYR_O + "m",
}
GREEK_CYRILLIC_OK = {
    "micro-thieu-cach": "Sơn dày 60" + MICRO_SIGN + "m.Bền màu",
    "mu-co-phay": "Sơn dày 60μm, bền màu",
    "mu-cuoi-cau": "Lớp mạ 80μm. Bảo hành 5 năm",
    "gost-thieu-cach": "Thép đạt chuẩn ГОСТ.Bền chắc",
    "gost-so": "Thép chuẩn ГОСТ 8240, dày 2 ly",
    "he-so-mu": "Hệ số ma sát μ = 0.3",
    "pi": "Diện tích π.r² của cột tròn",
    "phi-ong": "Ống Ø60.Mạ kẽm nhúng nóng",
    "ohm": "Điện trở 5Ω.Chống giật",
    "alpha-beta": "Thép α.β",
}


@pytest.mark.parametrize("link", MIXED_LINK.values(), ids=MIXED_LINK.keys())
def test_ten_mien_tron_chu_la_o_nhan_hay_duoi_bi_bat(link):
    """SL-T132-1 mở rộng: chữ lạ ở nhãn (đuôi chữ ASCII), chữ Latin ngoài tiếng Việt trông y hệt
    chữ thường, tên miền nhiều tầng."""
    assert has_link(f"Xem {link} ngay")
    assert accept_ai_title(f"Cửa sắt bị xệ: xem {link} để biết cách sửa", KEYWORD) is None


@pytest.mark.parametrize("link", ["evil{.}com", "EVIL{DOT}SHOP"], ids=["cham", "dot-hoa"])
def test_dau_cham_ngoac_nhon_bi_bat(link):
    """Soi Lỗi GN-3: dấu chấm kiểu né trong ngoặc nhọn, như «evil[.]com», «evil(dot)com»."""
    assert has_link(f"Xem {link} ngay")


@pytest.mark.parametrize("ok", GREEK_CYRILLIC_OK.values(), ids=GREEK_CYRILLIC_OK.keys())
def test_cau_thuong_co_chu_hy_lap_kirin_khong_bi_coi_la_link(ok):
    """Đơn vị «μm», ký hiệu «π», «Ω», «Ø», chuẩn «ГОСТ» trong câu thường (cả khi thiếu dấu cách sau
    dấu chấm): đuôi là chữ Việt hay viết hoa chữ đầu, hoặc không có đuôi chữ cái, thì không phải
    tên miền."""
    assert not has_link(ok)


@pytest.mark.parametrize(
    "price",
    ["hai đôla", "20 Đôla", "tính bằng đô - la", "50 ĐÔ-LA"],
    ids=["chu", "hoa", "gach-cach", "hoa-gach"],
)
def test_dola_cac_cach_viet_bi_bat(price):
    assert mentions_price(f"Sửa cửa sắt {price} tại nhà", KEYWORD)


@pytest.mark.parametrize(
    "ok", ["đô lá", "thủ đô Hà Nội", "khu đô thị"], ids=["la", "thu-do", "do-thi"]
)
def test_do_khong_phai_tien(ok):
    assert not mentions_price(f"Cửa sắt bị xệ {ok} đẹp", KEYWORD)
