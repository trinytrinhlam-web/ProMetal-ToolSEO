"""T-125 (Họa Sĩ): mục Search Console ở Cài đặt → 📗 Google (thiết kế T-120 mục 1.2, 4.4; Lá Chắn
T-124 B.1 a, b, c, d; LC-T120-12, -19, -21, -23; T-121: quyền cao hơn «Hạn chế»).

- «Tìm thuộc tính», «Kiểm tra» chỉ chạy khi bấm; mở Cài đặt không gọi mạng (ca mở trang ở
  ``test_t125_tracking_page.py``).
- Kết quả «Tìm thuộc tính» giữ trong phiên, chỉ chọn được mục dùng được, và **đúng đối tượng đó**
  được truyền vào ``save_property``; ghi thật vào ``.env`` tạm qua Google giả.
- Biến môi trường ``GSC_SITE_URL`` có mặt (kể cả rỗng) thì cảnh báo đè ``.env``.
- Chữ từ Google (thuộc tính, tên máy) hiện chữ thuần; câu của lõi qua ``escape_markdown``.
"""

from __future__ import annotations

import pytest
import test_app_pages as pages
import test_t125_tracking_page as page_tests
import test_tracking_refresh as trk
from fake_google import FakeGoogle
from streamlit.testing.v1 import AppTest

import seo_app.config as config
from seo_app.google.search_console import SearchConsoleClient, SearchConsoleError, SiteEntry
from seo_app.google.service_account import SEARCH_CONSOLE_SCOPE, load_service_account
from seo_app.text import escape_markdown
from seo_app.tracking import refresh as refresh_module
from seo_app.tracking.refresh import (
    HOST_SAME_SITE,
    MSG_OVERRIDDEN,
    MSG_PERMISSION_HIGH,
    MSG_SAVED,
    ConnectionCheck,
    HostShare,
    PropertyList,
    SaveResult,
)

env = pages.env
private_key = page_tests.private_key
key_file = page_tests.key_file
data_files = page_tests.data_files

WORDPRESS = page_tests.WORDPRESS
DOMAIN = page_tests.DOMAIN
PREFIX = "https://suachuacuasat.com/"
STAGING = "https://www.staging-m.suachuacuasat.com/"
ODD = "https://suachuacuasat.com/[x](https://evil.example)/"  # chữ Google: hiện như chữ thuần
EMAIL = "seo-app@du-an-thu.iam.gserviceaccount.com"
FOUND = PropertyList(
    (
        SiteEntry(DOMAIN, "siteRestrictedUser", "domain", True),
        SiteEntry(PREFIX, "siteOwner", "prefix", True),
        SiteEntry(STAGING, "siteRestrictedUser", "prefix", False),
        SiteEntry("https://suachuacuasat.com/moi/", "siteUnverifiedUser", "prefix", True),
        SiteEntry(ODD, "siteFullUser", "", False),
    ),
    skipped=1,
    account_email=EMAIL,
)


@pytest.fixture
def ready(monkeypatch, key_file, tmp_path):
    """Đã khai báo website và file khóa; ``.env`` là file tạm riêng của test."""
    env_path = tmp_path / ".env"
    env_path.write_text("WORDPRESS_URL=" + WORDPRESS + "\n", encoding="utf-8")
    monkeypatch.setattr(config, "DEFAULT_ENV_FILE", env_path)
    monkeypatch.setenv("WORDPRESS_URL", WORDPRESS)
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_FILE", str(key_file))
    return env_path


class Spy:
    """Thay một hàm của ``refresh``: ghi lại tham số, trả ``result``."""

    def __init__(self, result) -> None:
        self.result = result
        self.calls: list[tuple[tuple, dict]] = []

    def __call__(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return self.result


def open_settings(project_root) -> AppTest:
    return pages.open_page(project_root, "settings.py")


def run(target) -> AppTest:
    at = target.run()
    assert not at.exception, at.exception
    return at


def texts(at: AppTest, kind: str) -> list[str]:
    return [element.value for element in getattr(at, kind)]


def properties_table(at: AppTest):
    return next(frame.value for frame in at.dataframe if "Thuộc tính" in frame.value.columns)


def test_doi_chung_bam_nut_thi_moi_tao_client(project_root, ready, monkeypatch):
    """Đối chứng cho ca «mở Cài đặt không gọi mạng» (``test_t125_tracking_page``): cùng cách giả
    ``SearchConsoleClient.from_settings``, mở trang 0 lần; bấm «Tìm thuộc tính», «Kiểm tra» thì
    mỗi nút tạo đúng một client (lỗi giả ra câu cố định)."""
    monkeypatch.setenv("GSC_SITE_URL", DOMAIN)
    calls = page_tests.NetworkCalls(SearchConsoleError)
    monkeypatch.setattr(SearchConsoleClient, "from_settings", classmethod(calls))
    at = open_settings(project_root)
    assert calls.count == 0
    run(at.button(key="gsc-find-btn").click())
    assert calls.count == 1
    run(at.button(key="gsc-check-btn").click())
    assert calls.count == 2
    assert len([text for text in texts(at, "error") if "không được gọi" in text]) == 2


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (DOMAIN, "tên miền"),
        (PREFIX, "tiền tố địa chỉ"),
        (STAGING, "không phủ địa chỉ website"),
        ("http://suachuacuasat.com/", "sai dạng"),
    ],
    ids=["ten-mien", "tien-to", "staging", "http"],
)
def test_thuoc_tinh_dang_dung_noi_theo_loai_khong_in_gia_tri(
    project_root, ready, monkeypatch, value, expected
):
    """Không gọi mạng: kiểm dạng, phủ website ngay trên máy; không in giá trị trong .env."""
    monkeypatch.setenv("GSC_SITE_URL", value)
    at = open_settings(project_root)
    shown = texts(at, "markdown") + texts(at, "caption")
    assert any(expected in text for text in texts(at, "caption"))
    assert not any(value in text for text in shown)


def test_chua_co_file_khoa_thi_khoa_nut(project_root, monkeypatch, tmp_path):
    monkeypatch.setattr(config, "DEFAULT_ENV_FILE", tmp_path / ".env")
    at = open_settings(project_root)
    assert at.button(key="gsc-find-btn").disabled and at.button(key="gsc-check-btn").disabled
    assert any("Chưa chọn thuộc tính" in text for text in texts(at, "markdown"))


def test_tim_thuoc_tinh_chi_khi_bam_giu_ket_qua_bang_chu_thuan(project_root, ready, monkeypatch):
    find = Spy(FOUND)
    monkeypatch.setattr(refresh_module, "find_properties", find)
    at = open_settings(project_root)
    assert find.calls == []  # mở trang: không hỏi Google
    run(at.button(key="gsc-find-btn").click())
    assert len(find.calls) == 1
    assert at.session_state["gsc-found"] is FOUND  # giữ đúng đối tượng trong phiên
    frame = properties_table(at)
    assert list(frame["Thuộc tính"]) == [entry.site_url for entry in FOUND.entries]
    status = dict(zip(frame["Thuộc tính"], frame["Dùng cho website"], strict=True))
    assert status[DOMAIN].startswith("✔") and status[STAGING].startswith("✘ không phải website")
    assert status["https://suachuacuasat.com/moi/"] == "✘ chưa xác minh"
    assert status[ODD].startswith("✘ không đúng dạng")
    choice = at.selectbox(key="gsc-choice")
    assert choice.options == [DOMAIN, PREFIX]  # chỉ mục dùng được
    assert any(escape_markdown(MSG_PERMISSION_HIGH) in text for text in texts(at, "warning"))
    assert EMAIL in [block.value for block in at.code]
    assert "https://evil.example" not in "\n".join(texts(at, "markdown"))
    run(at)  # chạy lại trang (đổi ô khác): không hỏi Google lần nữa
    assert len(find.calls) == 1


def test_luu_truyen_dung_doi_tuong_tim_thay_vao_save_property(project_root, ready, monkeypatch):
    """Lá Chắn T-124 B.1 a, LC-T120-12: ``save_property`` nhận đúng ``PropertyList`` của lần tìm,
    không dựng lại từ chữ trên trang."""
    monkeypatch.setattr(refresh_module, "find_properties", Spy(FOUND))
    save = Spy(SaveResult(True, MSG_SAVED))
    monkeypatch.setattr(refresh_module, "save_property", save)
    at = open_settings(project_root)
    run(at.button(key="gsc-find-btn").click())
    run(at.selectbox(key="gsc-choice").set_value(PREFIX))
    run(at.button(key="gsc-save").click())
    (args, kwargs) = save.calls[0]
    assert args[0] == PREFIX and args[1] is FOUND and kwargs == {}
    assert any(escape_markdown(MSG_SAVED) in text for text in texts(at, "success"))


def test_chua_tim_ma_bam_luu_thi_khong_ghi(project_root, ready, monkeypatch):
    """Ô chọn bị gán thẳng (không qua «Tìm thuộc tính»): không có nút lưu, không ghi gì."""
    save = Spy(SaveResult(True, MSG_SAVED))
    monkeypatch.setattr(refresh_module, "save_property", save)
    at = open_settings(project_root)
    at.session_state["gsc-choice"] = PREFIX
    run(at)
    assert not any(button.key == "gsc-save" for button in at.button)
    assert save.calls == []
    assert "GSC_SITE_URL" not in ready.read_text(encoding="utf-8")


def test_khong_co_muc_dung_duoc_thi_khong_cho_chon(project_root, ready, monkeypatch):
    unusable = PropertyList((SiteEntry(STAGING, "siteRestrictedUser", "prefix", False),))
    monkeypatch.setattr(refresh_module, "find_properties", Spy(unusable))
    at = open_settings(project_root)
    run(at.button(key="gsc-find-btn").click())
    assert not any(box.key == "gsc-choice" for box in at.selectbox)
    assert any("Chưa có thuộc tính nào dùng được" in text for text in texts(at, "info"))


def test_tim_thuoc_tinh_loi_hien_cau_co_dinh_da_escape(project_root, ready, monkeypatch):
    failed = PropertyList(message="Google từ chối **quyền** [x](https://evil.example).")
    monkeypatch.setattr(refresh_module, "find_properties", Spy(failed))
    at = open_settings(project_root)
    run(at.button(key="gsc-find-btn").click())
    assert escape_markdown(failed.message) in texts(at, "error")
    assert not any(box.key == "gsc-choice" for box in at.selectbox)


def search_console(monkeypatch, key_file, tmp_path) -> trk.Search:
    """Google giả thật sự (client, lệnh ``sites``) cho «Tìm thuộc tính»."""
    project = tmp_path / "du-an"  # file khóa ở «bi-mat», ngoài thư mục dự án
    account = load_service_account(key_file, scope=SEARCH_CONSOLE_SCOPE, project_root=project)
    fake = FakeGoogle()
    google = trk.Search(fake)
    google.sites = [
        {"siteUrl": DOMAIN, "permissionLevel": "siteRestrictedUser"},
        {"siteUrl": STAGING, "permissionLevel": "siteRestrictedUser"},
    ]
    monkeypatch.setattr(refresh_module, "_default_client", trk.Factory(account, fake))
    return google


def test_luu_that_vao_env_qua_google_gia(project_root, ready, monkeypatch, key_file, tmp_path):
    search_console(monkeypatch, key_file, tmp_path)
    at = open_settings(project_root)
    run(at.button(key="gsc-find-btn").click())
    assert at.selectbox(key="gsc-choice").options == [DOMAIN]
    run(at.button(key="gsc-save").click())
    assert f"GSC_SITE_URL={DOMAIN}" in ready.read_text(encoding="utf-8")
    assert any(escape_markdown(MSG_SAVED) in text for text in texts(at, "success"))
    # Thuộc tính đang dùng: nói theo loại, không in giá trị trong .env (Soi Lỗi T-084, U2)
    assert any("Đã chọn thuộc tính" in text for text in texts(at, "markdown"))
    assert any("tên miền" in text for text in texts(at, "caption"))
    assert DOMAIN not in [block.value for block in at.code]


@pytest.mark.parametrize("value", ["", DOMAIN], ids=["bien-rong", "bien-co-gia-tri"])
def test_bien_moi_truong_de_env_thi_canh_bao(
    project_root, ready, monkeypatch, key_file, tmp_path, value
):
    """LC-T120-23: biến ``GSC_SITE_URL`` **có mặt** là đè ``.env``, kể cả rỗng."""
    monkeypatch.setenv("GSC_SITE_URL", value)
    search_console(monkeypatch, key_file, tmp_path)
    at = open_settings(project_root)
    assert any("biến môi trường GSC_SITE_URL" in text for text in texts(at, "warning"))
    run(at.button(key="gsc-find-btn").click())
    run(at.button(key="gsc-save").click())
    assert any(escape_markdown(MSG_OVERRIDDEN) in text for text in texts(at, "warning"))


def test_kiem_tra_hien_cau_co_dinh_canh_bao_quyen_ten_may_chu_thuan(
    project_root, ready, monkeypatch
):
    monkeypatch.setenv("GSC_SITE_URL", DOMAIN)
    check = Spy(
        ConnectionCheck(
            True,
            (
                "Tài khoản dịch vụ thấy thuộc tính này, quyền «Chủ sở hữu».",
                MSG_PERMISSION_HIGH,
                "Có số liệu đã chốt tới hết ngày 31/10/2026 (ngày theo giờ Google).",
            ),
            permission="siteOwner",
            hosts=(
                HostShare("www.staging-m.suachuacuasat.com", 6),
                HostShare("suachuacuasat.com", 4, HOST_SAME_SITE),
            ),
        )
    )
    monkeypatch.setattr(refresh_module, "check_connection", check)
    at = open_settings(project_root)
    assert check.calls == []
    run(at.button(key="gsc-check-btn").click())
    assert len(check.calls) == 1
    (box,) = [text for text in texts(at, "success") if "Tài khoản dịch vụ thấy" in text]
    assert "31/10/2026" in box and escape_markdown(MSG_PERMISSION_HIGH) not in box
    assert any(escape_markdown(MSG_PERMISSION_HIGH) in text for text in texts(at, "warning"))
    hosts = next(frame.value for frame in at.dataframe if "Tên máy" in frame.value.columns)
    assert list(hosts["Tên máy"]) == ["www.staging-m.suachuacuasat.com", "suachuacuasat.com"]
    assert list(hosts["Ghi chú"]) == ["", HOST_SAME_SITE]


def test_kiem_tra_loi_hien_loi_da_escape(project_root, ready, monkeypatch):
    monkeypatch.setenv("GSC_SITE_URL", DOMAIN)
    message = "Search Console từ chối **lệnh** [x](https://evil.example)."
    monkeypatch.setattr(refresh_module, "check_connection", Spy(ConnectionCheck(False, (message,))))
    at = open_settings(project_root)
    run(at.button(key="gsc-check-btn").click())
    assert any(escape_markdown(message) in text for text in texts(at, "error"))
