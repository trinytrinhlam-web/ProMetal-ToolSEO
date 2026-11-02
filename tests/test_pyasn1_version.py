"""T-114: thư viện phụ ``pyasn1`` đã vá 4 khuyến cáo mức High công bố 2026-10-31.

``pyasn1`` dưới 0.6.5 giải mã dữ liệu ASN.1 dựng cố ý rất chậm (CPU chạy lâu theo bình phương cỡ
dữ liệu): GHSA-fm9c-5rcf-2q5p, GHSA-9m75-vc3g-4x39, GHSA-mm57-4v3p-rchx, GHSA-2qm8-x737-gmw5
(Lá Chắn T-078, LC-T078-3). Gói này đi kèm ``google-auth`` qua ``pyasn1-modules``, app không gọi
trực tiếp, nên không ghim trong ``pyproject.toml``: hai test dưới đây giữ không cho lùi về bản lỗi.
Test đọc ``uv.lock`` (bản hai máy cài khi mở ``run.bat`` / ``run.command``) và bản đang cài.
Không gọi mạng.
"""

import tomllib
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from packaging.version import Version

_BAN_DA_VA = Version("0.6.5")
_UV_LOCK = Path(__file__).resolve().parent.parent / "uv.lock"


def test_uv_lock_khoa_pyasn1_tu_ban_da_va():
    goi = tomllib.loads(_UV_LOCK.read_text(encoding="utf-8"))["package"]
    ban = [Version(g["version"]) for g in goi if g["name"] == "pyasn1"]
    # Nếu sau này google-auth bỏ hẳn pyasn1 thì danh sách rỗng: không còn gì để vá.
    assert all(b >= _BAN_DA_VA for b in ban), ban


def test_pyasn1_da_cai_tu_ban_da_va():
    try:
        ban = Version(version("pyasn1"))
    except PackageNotFoundError:  # không còn cài pyasn1 thì không còn bản lỗi
        return
    assert ban >= _BAN_DA_VA
