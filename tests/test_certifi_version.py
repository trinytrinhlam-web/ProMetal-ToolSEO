"""T-075: bộ chứng chỉ ``certifi`` đã vá GHSA-6q48-6c7w-9gw2 (PYSEC-2026-4320).

``certifi`` bản dưới 2026.10.19 còn tin gốc «emSign ECC Root CA - G3»; 8 chứng chỉ trung gian
dưới gốc này bị lộ khóa riêng (Lá Chắn T-061, LC-T061-1). Client WordPress (``requests``) và
Gemini (``google-genai``) kiểm chứng chỉ website bằng ``certifi.where()``, nên gốc này phải biến
mất khỏi bộ chứng chỉ đã cài. Không gọi mạng: chỉ đọc file ``cacert.pem`` trên máy.
"""

import hashlib
import ssl
from importlib.metadata import version
from pathlib import Path

import certifi
import requests
from packaging.version import Version

_BAN_DA_VA = Version("2026.10.19")
_NHAN_BI_LO = "emSign ECC Root CA - G3"
# SHA-256 của chính chứng chỉ gốc «emSign ECC Root CA - G3» (tính từ bộ certifi 2026.7.22, chép
# đúng dạng dòng "SHA256 Fingerprint" trong file đó). Dò theo dấu vân tay để không lọt khi nhãn
# đổi tên. Đây là giá trị công khai, không phải bí mật.
_VAN_TAY_BI_LO = (
    "86:a1:ec:ba:08:9c:4a:8d:3b:be:27:34:c6:12:ba:34:"
    "1d:81:3e:04:3c:f9:e8:a8:62:cd:5c:57:a3:6b:be:6b"
).replace(":", "")


def test_certifi_tu_ban_da_va():
    # So bằng ``Version``: ``certifi.__version__`` có số 0 đầu ("2026.07.22"), metadata thì không.
    ban = Version(certifi.__version__)
    assert ban == Version(version("certifi"))
    assert ban >= _BAN_DA_VA


def test_bo_chung_chi_khong_con_nhan_emsign_ecc_g3():
    noi_dung = Path(certifi.where()).read_text(encoding="utf-8")
    assert "-----BEGIN CERTIFICATE-----" in noi_dung, "không đọc được bộ chứng chỉ của certifi"
    assert _NHAN_BI_LO not in noi_dung


def test_bo_chung_chi_khong_con_goc_emsign_ecc_g3_khi_nap():
    # Nạp đúng như thư viện mạng làm, rồi so dấu vân tay từng chứng chỉ gốc đã nạp.
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.load_verify_locations(cafile=certifi.where())
    van_tay = {hashlib.sha256(der).hexdigest() for der in ctx.get_ca_certs(binary_form=True)}
    assert len(van_tay) > 100, "bộ chứng chỉ nạp được quá ít, có thể đọc sai file"
    assert _VAN_TAY_BI_LO not in van_tay


def test_client_wordpress_dung_bo_chung_chi_cua_certifi():
    # ``requests`` (client WordPress) mặc định kiểm chứng chỉ bằng bộ này; nếu thư viện đổi
    # sang kho khác thì test này báo để xem lại phiếu T-075.
    assert Path(requests.utils.DEFAULT_CA_BUNDLE_PATH) == Path(certifi.where())
