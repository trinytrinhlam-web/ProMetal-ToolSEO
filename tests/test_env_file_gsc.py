"""T-124: ghi thuộc tính Search Console ``GSC_SITE_URL`` vào ``.env`` (``seo_app/env_file.py``).

- LC-T120-12: chỉ ghi thuộc tính vừa nhận từ lệnh ``sites`` trong cùng phiên (``offered``) và qua
  bộ kiểm chặt riêng; không chèn được biến khác vào ``.env``; câu báo không chép giá trị.
- LC-T120-23: biết khi biến môi trường ``GSC_SITE_URL`` có mặt (kể cả rỗng) đè ``.env``.
- Cùng bộ ghi với khóa AI, mã Google Sheet (``_write_value``): giữ mọi dòng khác, ghi nguyên tử.

Chỉ dùng file tạm, không gọi mạng.
"""

from __future__ import annotations

import pytest
from dotenv import dotenv_values

import seo_app.config as config
from seo_app.env_file import (
    GSC_SITE_URL_MAX,
    GSC_SITE_URL_VAR,
    EnvFileError,
    clear_gsc_site_url,
    gsc_site_url_overridden,
    set_gsc_site_url,
    validate_gsc_site_url,
)
from seo_app.google.search_console import MAX_SITE_URL_CHARS, parse_property

DOMAIN = "sc-domain:suachuacuasat.com"
PREFIX = "https://suachuacuasat.com/"
OFFERED = (DOMAIN, PREFIX)


@pytest.fixture
def env_path(tmp_path, monkeypatch):
    """Trỏ ``DEFAULT_ENV_FILE`` sang file tạm (không bao giờ đụng ``.env`` thật)."""
    path = tmp_path / ".env"
    monkeypatch.setattr(config, "DEFAULT_ENV_FILE", path)
    return path


def read(path):
    with path.open("r", encoding="utf-8", newline="") as fh:
        return fh.read()


def write(path, text):
    with path.open("w", encoding="utf-8", newline="") as fh:
        fh.write(text)


# ---------------------------------------------------------------- bộ kiểm


@pytest.mark.parametrize(
    "value",
    [DOMAIN, PREFIX, "sc-domain:a.vn", "https://www.suachuacuasat.com/", "sc-domain:x-y.com.vn"],
    ids=["ten-mien", "tien-to", "ngan", "www", "gach-noi"],
)
def test_bo_kiem_nhan_dung_dang(value):
    assert validate_gsc_site_url(value) == value
    parse_property(value)  # cùng dạng client Search Console nhận


@pytest.mark.parametrize(
    "value",
    [
        "",
        " " + DOMAIN,
        DOMAIN + " ",
        DOMAIN + "\n",
        DOMAIN + "\nAPP_PASSWORD_HASH=x",
        DOMAIN + "\rX=1",
        DOMAIN + "#ghi-chu",
        DOMAIN + "=",
        '"' + DOMAIN + '"',
        "'" + DOMAIN + "'",
        DOMAIN.upper(),
        "SC-DOMAIN:suachuacuasat.com",
        "sc-domain:",
        "sc-domain:suachuacuasát.com",
        "sc-domain:suachuacuasat.com/",
        "sc-domain:suachuacuasat.com:443",
        "http://suachuacuasat.com/",
        "https://suachuacuasat.com",
        "https://suachuacuasat.com/blog/",
        "https://suachuacuasat.com:443/",
        "https://u@suachuacuasat.com/",
        "https://suachuacuasat.com/?a=1",
        "https://suachuacuasat.com/" + chr(0x200B),
        "sc-domain:" + "a" * 254,
        "${GSC_SITE_URL}",
        "$(whoami)",
    ],
    ids=[f"sai-{n:02d}" for n in range(26)],
)
def test_bo_kiem_tu_choi_va_khong_chep_gia_tri(value):
    with pytest.raises(EnvFileError) as error:
        validate_gsc_site_url(value)
    text = str(error.value)
    assert "suachuacuasat" not in text and "APP_PASSWORD_HASH" not in text
    assert "\n" not in text and "\r" not in text


@pytest.mark.parametrize("value", [None, 1, b"sc-domain:a.vn", ["sc-domain:a.vn"]], ids=str)
def test_bo_kiem_tu_choi_khong_phai_chu(value):
    with pytest.raises(EnvFileError, match="Chưa chọn thuộc tính"):
        validate_gsc_site_url(value)


def test_tran_do_dai_bang_client():
    assert GSC_SITE_URL_MAX == MAX_SITE_URL_CHARS


# ---------------------------------------------------------------- ghi, xóa


def test_ghi_thuoc_tinh_vua_tim_thay(env_path):
    write(env_path, "WORDPRESS_URL=https://suachuacuasat.com\n# ghi chú\nGSC_SITE_URL=\n")
    set_gsc_site_url(DOMAIN, offered=OFFERED)
    assert read(env_path) == (
        "WORDPRESS_URL=https://suachuacuasat.com\n# ghi chú\n"
        "GSC_SITE_URL=sc-domain:suachuacuasat.com\n"
    )
    assert config.load_settings(environ={}).gsc_site_url == DOMAIN


def test_ghi_them_vao_cuoi_va_tao_file(env_path):
    set_gsc_site_url(PREFIX, offered=OFFERED)
    assert dotenv_values(env_path) == {GSC_SITE_URL_VAR: PREFIX}
    write(env_path, "A=1")
    set_gsc_site_url(DOMAIN, offered=[DOMAIN])
    assert read(env_path) == "A=1\nGSC_SITE_URL=sc-domain:suachuacuasat.com\n"


def test_thay_moi_dong_lap_va_giu_crlf(env_path):
    write(env_path, "GSC_SITE_URL=sc-domain:cu.vn\r\nB=2\r\nexport GSC_SITE_URL = x\r\n")
    set_gsc_site_url(DOMAIN, offered=iter(OFFERED))
    values = dotenv_values(env_path)
    assert values == {GSC_SITE_URL_VAR: DOMAIN, "B": "2"}
    assert "\r\nB=2\r\n" in read(env_path)


def test_explicit_path(tmp_path, env_path):
    other = tmp_path / "khac.env"
    set_gsc_site_url(DOMAIN, offered=OFFERED, env_file=other)
    assert dotenv_values(other) == {GSC_SITE_URL_VAR: DOMAIN}
    assert not env_path.exists()


@pytest.mark.parametrize(
    "offered",
    [
        (),
        ("sc-domain:khac.vn",),
        (DOMAIN.upper(),),
        (DOMAIN + " ",),
        DOMAIN,
        DOMAIN.encode(),
        None,
        7,
    ],
    ids=["rong", "khac", "chu-hoa", "dau-cach", "chuoi", "byte", "none", "so"],
)
def test_chi_ghi_thuoc_tinh_trong_danh_sach_vua_tim(env_path, offered):
    write(env_path, "GSC_SITE_URL=\n")
    with pytest.raises(EnvFileError, match="Tìm thuộc tính") as error:
        set_gsc_site_url(DOMAIN, offered=offered)
    assert "suachuacuasat" not in str(error.value)
    assert read(env_path) == "GSC_SITE_URL=\n"


def test_danh_sach_co_muc_khong_phai_chu_bi_bo_qua(env_path):
    set_gsc_site_url(DOMAIN, offered=[None, 1, b"x", DOMAIN])
    assert dotenv_values(env_path) == {GSC_SITE_URL_VAR: DOMAIN}


def test_gia_tri_sai_bi_chan_truoc_khi_xet_danh_sach(env_path):
    bad = DOMAIN + "\nAPP_PASSWORD_HASH=x"
    with pytest.raises(EnvFileError, match="không đúng dạng"):
        set_gsc_site_url(bad, offered=[bad])
    assert not env_path.exists()


def test_xoa_de_trong_giu_vi_tri(env_path):
    write(env_path, "A=1\nGSC_SITE_URL=sc-domain:suachuacuasat.com\nB=2\n")
    clear_gsc_site_url()
    assert read(env_path) == "A=1\nGSC_SITE_URL=\nB=2\n"
    assert config.load_settings(environ={}).gsc_site_url == ""


def test_xoa_khi_chua_co_dong_hay_file_khong_lam_gi(env_path):
    clear_gsc_site_url()
    assert not env_path.exists()
    write(env_path, "A=1\n")
    clear_gsc_site_url()
    assert read(env_path) == "A=1\n"


# ---------------------------------------------------------------- biến môi trường đè .env


@pytest.mark.parametrize(
    ("environ", "expected"),
    [
        ({}, False),
        ({"GSC_SITE_URL": ""}, True),
        ({"GSC_SITE_URL": "   "}, True),
        ({"GSC_SITE_URL": DOMAIN}, True),
        ({"gsc_site_url": DOMAIN, "GSC_SITE_URL_X": DOMAIN}, False),
    ],
    ids=["khong-co", "rong", "dau-cach", "co-gia-tri", "ten-gan-giong"],
)
def test_bao_bien_moi_truong_de_env(environ, expected):
    assert gsc_site_url_overridden(environ) is expected


def test_bien_moi_truong_rong_de_gia_tri_trong_env(env_path):
    set_gsc_site_url(DOMAIN, offered=OFFERED)
    assert config.load_settings(environ={"GSC_SITE_URL": ""}).gsc_site_url == ""
    assert gsc_site_url_overridden({"GSC_SITE_URL": ""})


def test_mac_dinh_doc_os_environ(monkeypatch):
    monkeypatch.delenv("GSC_SITE_URL", raising=False)
    assert not gsc_site_url_overridden()
    monkeypatch.setenv("GSC_SITE_URL", "")
    assert gsc_site_url_overridden()
