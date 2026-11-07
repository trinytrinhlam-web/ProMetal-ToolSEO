"""Soi Lỗi T-132 (rút gọn): dọn chữ Giai đoạn 4.

- Bộ dò link (LC-T036-2) và dò giá (SL-T036-11) của gợi ý meta: câu thường không bị bắt oan, các
  dạng lọt (``xfail(strict=True)``, mã ``SL-T132-n``).
- ``WordPressClient.recheck_draft``: chỉ đọc, chỉ nháp chính client này tạo, câu báo cố định.

Chỉ WordPress giả, không AI, không mạng. Ký tự lạ viết bằng ``chr(0x…)``.
"""

from __future__ import annotations

import ast
import enum
from datetime import UTC, datetime
from email.utils import format_datetime
from pathlib import Path

import pytest
import requests
from fake_wordpress import BASE_URL, FakeWordPress, make_session

from seo_app.onpage.meta import accept_ai_description, accept_ai_title, has_link, mentions_price
from seo_app.wordpress import WordPressClient, WordPressError
from seo_app.wordpress import client as client_module
from seo_app.wordpress.client import ReleaseError

KEYWORD = "cửa sắt bị xệ"
POSTS = "/wp-json/wp/v2/posts"
MODIFIED = "2026-11-05T01:02:03"
SERVER_TEXT = "<b>MOI-may-chu</b> /home/site/wp-config.php"
CYR_O = chr(0x043E)  # «о» Kirin, trông y hệt «o»
CYR_ES = chr(0x0441)  # «с» Kirin, trông y hệt «c»
GREEK_O = chr(0x03BF)  # «ο» Hy Lạp


# ====================================================================== 1. dò link (LC-T036-2)
ORDINARY = {
    "tp-hcm-q-gv": "Sửa cửa sắt tại TP.HCM, Q.Gò Vấp, giao nhanh",
    "q7-tp-cach": "Thi công cửa inox 304 tại Q.7, TP. HCM",
    "phuong-quan": "Sửa cửa tại P.12, Q.Tân Bình, TP.Thủ Đức",
    "thieu-cach-sau-cham": "Bảo hành 12 tháng.Liên hệ ngay",
    "hang-xingfa": "Cửa nhôm Xingfa.Hệ 55 bền đẹp",
    "hang-austdoor": "Cửa cuốn Austdoor.Bảo hành chính hãng",
    "v-v": "Cửa kéo Đài Loan, v.v. đều sửa được",
    "tp-viet-thuong": "Tp.HCM, Tp.Hà Nội, tp.hcm",
    "hoa-co-dau": "SỬA CỬA SẮT TẠI NHÀ.UY TÍN",
    "hoa-loan": "CỬA KÉO ĐÀI LOAN.GIÁ TỐT",
    "inox-sus": "Hàng INOX.SUS304 chuẩn",
    "nam-kinh-nghiem": "Đội thợ 10 năm.Kinh nghiệm thật",
    "do-day": "Cửa sắt 1.2mm, sơn 2 lớp",
    "inox-son": "Inox 304.Sơn tĩnh điện",
}


@pytest.mark.parametrize("text", ORDINARY.values(), ids=ORDINARY.keys())
def test_cau_thuong_khong_bi_coi_la_link(text):
    """Viết tắt địa danh, hãng, câu thiếu dấu cách sau dấu chấm, câu HOA có dấu: không phải link."""
    assert not has_link(text)


LATIN_LINKS = {"com": "evil.com", "shop": "evil.shop", "hoa": "EVIL.SHOP", "ru": "evil.рф"}


@pytest.mark.parametrize("domain", LATIN_LINKS.values(), ids=LATIN_LINKS.keys())
def test_doi_chung_ten_mien_that_bi_bat(domain):
    """Đối chứng cho ``test_sl_t132_1_…``: cùng câu, tên miền chữ thật thì gợi ý bị bỏ."""
    assert has_link(f"Xem {domain} ngay")
    assert accept_ai_title(f"Cửa sắt bị xệ: xem {domain} để biết cách sửa", KEYWORD) is None


HOMOGLYPH = {
    "com-o-kirin": "evil.c" + CYR_O + "m",
    "com-c-o-kirin": "evil." + CYR_ES + CYR_O + "m",
    "com-o-hy-lap": "evil.c" + GREEK_O + "m",
    "shop-o-kirin": "evil.sh" + CYR_O + "p",
    "shop-hoa-o-kirin": "EVIL.SH" + CYR_O.upper() + "P",
}


@pytest.mark.xfail(
    strict=True,
    reason="SL-T132-1: đuôi tên miền trộn chữ Latin với chữ Kirin/Hy Lạp («evil.cоm») lọt bộ dò "
    "link: _foreign_tld chỉ bắt đuôi KHÔNG có chữ Latin nào",
)
@pytest.mark.parametrize("domain", HOMOGLYPH.values(), ids=HOMOGLYPH.keys())
def test_sl_t132_1_duoi_ten_mien_tron_chu_bi_bat(domain):
    """«evil.cоm» (chữ «о» Kirin) hiện ra y hệt «evil.com» trong kết quả Google. Gợi ý AI mang nó
    phải bị bỏ như «evil.com»; hiện gợi ý được nhận (``has_odd_chars`` không coi chữ Kirin là
    lạ)."""
    assert has_link(f"Xem {domain} ngay")
    assert accept_ai_title(f"Cửa sắt bị xệ: xem {domain} để biết cách sửa", KEYWORD) is None


# ====================================================================== 2. dò giá (SL-T036-11)
NOT_PRICE = {
    "mau": "5 trăm mẫu cửa",
    "khach-hang": "5 trăm khách hàng",
    "tho": "đội 5 trăm thợ",
    "met": "cách 3 trăm mét",
    "m2": "4 trăm m²",
    "tieng-ruoi": "hai tiếng rưỡi",
    "nam-ruoi": "ba năm rưỡi",
    "do-thi": "khu đô thị mới",
    "usda": "chuẩn USDA",
}


@pytest.mark.parametrize("text", NOT_PRICE.values(), ids=NOT_PRICE.keys())
def test_so_dem_don_vi_khong_bi_coi_la_gia(text):
    assert not mentions_price(f"Đã làm {text} tại TP.HCM", KEYWORD)


PRICE = {"so-do-la": "50 đô la", "so-do-gach-la": "50 đô-la", "do-la-rieng": "tính bằng đô la"}


@pytest.mark.parametrize("text", PRICE.values(), ids=PRICE.keys())
def test_doi_chung_do_la_bi_bat(text):
    """Đối chứng cho ``test_sl_t132_2_…``: «đô la» viết rời đã bị bắt."""
    assert mentions_price(f"Sửa cửa sắt {text} tại nhà", KEYWORD)


DOLA = {
    "so-dola": "chỉ 20 đôla",
    "dola-rieng": "giá tính bằng đôla",
    "do-gach-la": "tính bằng đô-la",
}


@pytest.mark.xfail(
    strict=True,
    reason="SL-T132-2: «đôla» viết liền, «đô-la» đứng riêng chưa bị coi là nói giá",
)
@pytest.mark.parametrize("text", DOLA.values(), ids=DOLA.keys())
def test_sl_t132_2_dola_viet_lien_bi_bat(text):
    assert mentions_price(f"Sửa cửa sắt {text} tại nhà", KEYWORD)
    description = f"Cửa sắt bị xệ, cánh cửa sát nền? Thợ đến tận nhà, {text}, bảo hành rõ ràng."
    assert accept_ai_description(description, KEYWORD) is None


# ====================================================================== 3. recheck_draft
def new_client(fake: FakeWordPress) -> WordPressClient:
    return WordPressClient(BASE_URL, "lam", "abcd efgh ijkl", session=make_session(fake))


def created(client: WordPressClient, fake: FakeWordPress, post_id: int = 42) -> int:
    fake.on("POST", POSTS, (201, {"id": post_id, "status": "draft", "modified_gmt": MODIFIED}, {}))
    assert client.create_draft("Tiêu đề", "<p>Nội dung</p>").id == post_id
    fake.requests.clear()
    return post_id


def assert_fixed(error, *forbidden):
    text = str(error.value)
    for item in ("MOI-may-chu", "wp-config", "/home/site", BASE_URL, "lam", *forbidden):
        assert item not in text
    assert error.value.__cause__ is None


def test_nhap_cua_client_khac_khong_hoi_lai_duoc(fake_wp):
    """Hai client (hai lần bấm): client sau không hỏi lại được nháp client trước tạo, 0 lệnh."""
    first, second = new_client(fake_wp), new_client(fake_wp)
    post_id = created(first, fake_wp)
    with pytest.raises(WordPressError) as caught:
        second.recheck_draft(post_id)
    assert str(caught.value) == client_module._RECHECK_NOT_OWN
    assert fake_wp.requests == []


class _Id(enum.IntEnum):
    ONE = 1


@pytest.mark.parametrize(
    "post_id", [True, 1.0, _Id.ONE, "1"], ids=["true", "float", "intenum", "chu"]
)
def test_ma_bai_sai_kieu_khong_hoi_lai_ca_khi_nhap_1_co_that(fake_wp, post_id):
    """Client có nháp mã 1 thật: ``True``, ``1.0``, ``IntEnum`` bằng 1 về giá trị nhưng không phải
    ``int``: từ chối, 0 lệnh."""
    client = new_client(fake_wp)
    created(client, fake_wp, 1)
    with pytest.raises(WordPressError, match="Chỉ hỏi lại được bài nháp app vừa tạo"):
        client.recheck_draft(post_id)
    assert fake_wp.requests == []


ODD_ANSWERS = {
    "danh-sach": [{"id": 42, "status": "draft"}],
    "rong": {},
    "bai-khac": {"id": 43, "status": "draft"},
    "ma-chu": {"id": "42", "status": "draft"},
    "ma-bool": {"id": True, "status": "draft"},
    "hen-gio": {"id": 42, "status": "future"},
    "cho-duyet": {"id": 42, "status": "pending"},
    "rieng-tu": {"id": 42, "status": "private"},
    "thung-rac": {"id": 42, "status": "trash"},
    "chu-hoa": {"id": 42, "status": "Draft"},
}


@pytest.mark.parametrize("name", list(ODD_ANSWERS))
def test_cau_tra_loi_khong_phai_nhap_cua_bai_thi_thoi_coi_la_cua_app(fake_wp, name):
    """Website trả gì khác «bài 42 đang là nháp»: báo câu cố định, client thôi coi bài là của app;
    sau đó mọi lệnh ghi (SEO, ảnh đại diện, hẹn giờ/đăng) đều bị từ chối, 0 lệnh."""
    client = new_client(fake_wp)
    post_id = created(client, fake_wp)
    fake_wp.on("GET", f"{POSTS}/42", ODD_ANSWERS[name])
    with pytest.raises(WordPressError) as caught:
        client.recheck_draft(post_id)
    assert str(caught.value) == client_module._SEO_NOT_DRAFT
    assert [r.method for r in fake_wp.requests] == ["GET"]
    fake_wp.requests.clear()
    with pytest.raises(WordPressError):
        client.set_seo_meta(post_id, title="Tiêu đề SEO")
    with pytest.raises(WordPressError):
        client.set_featured_image(post_id, 7)
    with pytest.raises(ReleaseError):
        client.release_draft(post_id, mode="publish")
    with pytest.raises(WordPressError):
        client.recheck_draft(post_id)
    assert fake_wp.requests == []


FAILURES = {
    "chuyen-huong": ((302, b"", {"Location": "https://evil.example/x"}), " (mã 302)"),
    "401": ((401, {"code": "x", "message": SERVER_TEXT}, {}), " (mã 401)"),
    "403": ((403, {"code": "x", "message": SERVER_TEXT}, {}), " (mã 403)"),
    "404": ((404, {"code": "rest_post_invalid_id", "message": SERVER_TEXT}, {}), " (mã 404)"),
    "500": ((500, SERVER_TEXT.encode(), {}), " (mã 500)"),
    "het-gio": (requests.exceptions.ReadTimeout(SERVER_TEXT), ""),
}


@pytest.mark.parametrize("name", list(FAILURES))
def test_hoi_khong_duoc_thi_cau_co_dinh_va_van_la_nhap_cua_app(fake_wp, name):
    """Không hỏi được: câu ``_RECHECK_FAILED`` (kèm mã HTTP nếu có), không chép lời máy chủ hay
    địa chỉ chuyển hướng; chưa biết gì nên client vẫn giữ bài là nháp của app (lần sau hỏi lại)."""
    reply, code = FAILURES[name]
    client = new_client(fake_wp)
    post_id = created(client, fake_wp)
    fake_wp.on("GET", f"{POSTS}/42", lambda _request: reply)
    with pytest.raises(WordPressError) as caught:
        client.recheck_draft(post_id)
    assert str(caught.value) == client_module._RECHECK_FAILED.format(code=code)
    assert_fixed(caught, "evil")
    assert post_id in client._created_post_ids
    assert all(r.method == "GET" for r in fake_wp.requests)
    assert "evil.example" not in "".join(r.url for r in fake_wp.requests)


NOW = datetime(2026, 11, 2, 1, 0, tzinfo=UTC)


def test_sau_khi_dang_khong_hoi_lai_duoc(fake_wp, monkeypatch):
    """``release_draft`` đã giành mã bài (gửi lệnh đăng): ``recheck_draft`` từ chối, 0 lệnh."""
    monkeypatch.setattr(client_module, "_utc_now", lambda: NOW)
    client = new_client(fake_wp)
    post_id = created(client, fake_wp)
    date = {"Date": format_datetime(NOW, usegmt=True)}
    fake_wp.on(
        "GET",
        f"{POSTS}/42",
        lambda _r: (200, {"id": 42, "status": "draft", "modified_gmt": MODIFIED}, date),
    )
    fake_wp.on("POST", f"{POSTS}/42", {"id": 42, "status": "publish", "link": BASE_URL + "/bai/"})
    client.release_draft(post_id, mode="publish")
    fake_wp.requests.clear()
    with pytest.raises(WordPressError, match="Chỉ hỏi lại được bài nháp app vừa tạo"):
        client.recheck_draft(post_id)
    assert fake_wp.requests == []


def test_recheck_draft_chi_doc_qua_own_draft():
    """Cây cú pháp: ``recheck_draft`` không tự gửi lệnh nào, chỉ gọi ``self._own_draft``; trong
    ``_own_draft`` chỉ có một lệnh ``self._request("GET", …)``."""
    tree = ast.parse(Path(client_module.__file__).read_text(encoding="utf-8"))
    methods = {
        node.name: node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name in {"recheck_draft", "_own_draft"}
    }
    calls = {
        name: [ast.unparse(c.func) for c in ast.walk(node) if isinstance(c, ast.Call)]
        for name, node in methods.items()
    }
    assert "self._own_draft" in calls["recheck_draft"]
    assert not any("_request" in c or "session" in c for c in calls["recheck_draft"])
    requests_made = [
        c for c in ast.walk(methods["_own_draft"])
        if isinstance(c, ast.Call) and ast.unparse(c.func) == "self._request"
    ]  # fmt: skip
    assert [ast.literal_eval(c.args[0]) for c in requests_made] == ["GET"]
