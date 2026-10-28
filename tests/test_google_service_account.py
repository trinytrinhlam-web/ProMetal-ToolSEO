"""T-097: kiểm file khóa tài khoản dịch vụ Google (LC-T094-2, -11, -12, -14, -17).

Khóa RSA sinh lúc chạy test (``fake_google.new_private_key``), file khóa nằm trong thư mục tạm
của pytest (ngoài thư mục dự án). Không gọi Google thật.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from fake_google import EMAIL, key_info, new_private_key

from seo_app import config
from seo_app.google import service_account as sa
from seo_app.google.service_account import (
    SHEETS_SCOPE,
    TOKEN_URI,
    ServiceAccountError,
    load_service_account,
)

MOI = "MOI-NOI-DUNG-FILE-KHONG-DUOC-CHEP"  # chuỗi mồi: không được xuất hiện trong câu báo
NOT_PEM = "khong-phai-pem " + MOI
PEM_BEGIN = "-----BEGIN " + "PRIVATE KEY-----"  # ghép hai nửa: bộ quét bí mật không nhận nhầm
PEM_END = "-----END " + "PRIVATE KEY-----"


@pytest.fixture(scope="module")
def private_key():
    return new_private_key()


@pytest.fixture
def outside(tmp_path):
    """Thư mục «bí mật» ngoài dự án, và một thư mục dự án giả để thử các ca bị chặn."""
    secret_dir = tmp_path / "bi-mat"
    secret_dir.mkdir()
    project = tmp_path / "du-an"
    project.mkdir()
    return secret_dir, project


def write_key(folder: Path, info: object, name: str = "du-an-thu-0123abcd.json") -> Path:
    path = folder / name
    text = info if isinstance(info, str) else json.dumps(info)
    path.write_text(text, encoding="utf-8")
    if os.name != "nt":
        path.chmod(0o600)
    return path


def load(path, project, **kwargs):
    return load_service_account(path, project_root=project, **kwargs)


def assert_fixed(error: pytest.ExceptionInfo, *forbidden: str) -> None:
    text = str(error.value)
    for item in (MOI, EMAIL, *forbidden):
        assert item not in text
    assert error.value.__cause__ is None  # «from None»: không kèm lỗi gốc có dữ liệu


# ================================================================ file đúng


def test_file_khoa_dung_doc_duoc(outside, private_key):
    secret_dir, project = outside
    path = write_key(secret_dir, key_info(private_key))
    account = load(path, project)
    assert account.email == EMAIL
    assert account.file_name == path.name
    assert account.warnings == ()
    credentials = account.credentials
    assert credentials.service_account_email == EMAIL
    assert tuple(credentials.scopes) == (SHEETS_SCOPE,)  # đúng một phạm vi
    assert credentials._token_uri == TOKEN_URI
    assert credentials._subject is None  # không ủy quyền toàn miền
    assert credentials._always_use_jwt_access is False
    assert credentials.universe_domain == "googleapis.com"
    assert credentials.token is None  # chưa xin mã: mã chỉ có khi gọi Sheets


def test_repr_khong_co_khoa_email_duong_dan(outside, private_key):
    secret_dir, project = outside
    info = key_info(private_key)
    account = load(write_key(secret_dir, info), project)
    shown = repr(account) + str(account)
    assert "PRIVATE" not in shown and info["private_key_id"] not in shown
    assert EMAIL not in shown and str(secret_dir) not in shown
    assert "du-an-thu-0123abcd.json" in shown  # chỉ tên file


def test_chi_lay_truong_can_thiet_tu_file(outside, private_key):
    """Trường lạ trong file (``quota_project_id``, ``trust_boundary``…) không vào thư viện."""
    secret_dir, project = outside
    info = key_info(private_key, quota_project_id="du-an-khac", trust_boundary={"x": "y"})
    account = load(write_key(secret_dir, info), project)
    assert account.credentials.quota_project_id is None
    assert account.credentials._trust_boundary is None


def test_file_co_bom_van_doc_duoc(outside, private_key):
    secret_dir, project = outside
    path = secret_dir / "khoa.json"
    path.write_bytes(b"\xef\xbb\xbf" + json.dumps(key_info(private_key)).encode())
    assert load(path, project).email == EMAIL


@pytest.mark.parametrize("domain", [None, "", "googleapis.com"])
def test_universe_domain_trong_hay_mac_dinh(outside, private_key, domain):
    secret_dir, project = outside
    info = key_info(private_key)
    if domain is None:
        info.pop("universe_domain")
    else:
        info["universe_domain"] = domain
    assert load(write_key(secret_dir, info), project).email == EMAIL


# ================================================================ vị trí file (LC-T094-11)


@pytest.mark.parametrize("value", [None, "", "   "])
def test_chua_khai_bao(outside, value):
    _, project = outside
    with pytest.raises(ServiceAccountError, match="Chưa khai báo"):
        load(value, project)


def test_duong_dan_tuong_doi_bi_tu_choi(outside):
    _, project = outside
    with pytest.raises(ServiceAccountError, match="đường dẫn đầy đủ"):
        load("bi-mat/khoa.json", project)


def test_khong_co_file_cau_bao_khong_chep_duong_dan(outside):
    secret_dir, project = outside
    missing = secret_dir / "khong-co-ten-bi-mat.json"
    with pytest.raises(ServiceAccountError, match="Không tìm thấy") as error:
        load(missing, project)
    assert_fixed(error, "khong-co-ten-bi-mat", str(secret_dir))


def test_file_trong_thu_muc_du_an_bi_tu_choi(outside, private_key):
    _, project = outside
    nested = project / "data"
    nested.mkdir()
    path = write_key(nested, key_info(private_key))
    with pytest.raises(ServiceAccountError, match="thư mục phần mềm") as error:
        load(path, project)
    assert_fixed(error, str(project))


def test_mac_dinh_so_voi_thu_muc_du_an_cua_config(outside, private_key, monkeypatch):
    """Không truyền ``project_root``: so với ``config.PROJECT_ROOT`` (tra lúc gọi)."""
    _, project = outside
    path = write_key(project, key_info(private_key))
    monkeypatch.setattr(config, "PROJECT_ROOT", project)
    with pytest.raises(ServiceAccountError, match="thư mục phần mềm"):
        load_service_account(path)
    assert sa._is_within(config.PROJECT_ROOT / "seo_app" / "x.json", config.PROJECT_ROOT)


def test_duong_dan_co_dau_cham_cham_vao_du_an_bi_tu_choi(outside, private_key):
    secret_dir, project = outside
    write_key(project, key_info(private_key), name="khoa.json")
    sneaky = secret_dir / ".." / "du-an" / "khoa.json"
    with pytest.raises(ServiceAccountError, match="thư mục phần mềm"):
        load(sneaky, project)


def _symlink_or_skip(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("Máy này không tạo được symlink (Windows cần quyền Developer Mode)")


def test_symlink_ngoai_tro_vao_du_an_bi_tu_choi(outside, private_key):
    secret_dir, project = outside
    target = write_key(project, key_info(private_key), name="khoa.json")
    link = secret_dir / "khoa-lien-ket.json"
    _symlink_or_skip(link, target)
    with pytest.raises(ServiceAccountError, match="thư mục phần mềm"):
        load(link, project)


def test_symlink_trong_du_an_tro_ra_ngoai_cung_bi_tu_choi(outside, private_key):
    secret_dir, project = outside
    target = write_key(secret_dir, key_info(private_key))
    link = project / "khoa.json"
    _symlink_or_skip(link, target)
    with pytest.raises(ServiceAccountError, match="thư mục phần mềm"):
        load(link, project)


def _junction_or_skip(link: Path, target: Path) -> None:
    if os.name != "nt":
        pytest.skip("Junction chỉ có trên Windows (Mac/Linux thử bằng symlink ở trên)")
    import _winapi

    _winapi.CreateJunction(str(target), str(link))


def test_junction_ngoai_tro_vao_du_an_bi_tu_choi(outside, private_key):
    secret_dir, project = outside
    write_key(project, key_info(private_key), name="khoa.json")
    link = secret_dir / "lien-ket"
    _junction_or_skip(link, project)
    with pytest.raises(ServiceAccountError, match="thư mục phần mềm"):
        load(link / "khoa.json", project)


def test_junction_trong_du_an_tro_ra_ngoai_cung_bi_tu_choi(outside, private_key):
    secret_dir, project = outside
    write_key(secret_dir, key_info(private_key), name="khoa.json")
    link = project / "lien-ket"
    _junction_or_skip(link, secret_dir)
    with pytest.raises(ServiceAccountError, match="thư mục phần mềm"):
        load(link / "khoa.json", project)


def test_junction_vao_thu_muc_anh_bi_tu_choi(outside, private_key, tmp_path):
    secret_dir, project = outside
    images = tmp_path / "Anh"
    images.mkdir()
    write_key(images, key_info(private_key), name="khoa.json")
    link = secret_dir / "lien-ket-anh"
    _junction_or_skip(link, images)
    with pytest.raises(ServiceAccountError, match="thư mục ảnh"):
        load(link / "khoa.json", project, image_folders=(images,))


def test_file_trong_thu_muc_anh_bi_tu_choi(outside, private_key, tmp_path):
    secret_dir, project = outside
    images = tmp_path / "Anh SEO"
    (images / "CT012").mkdir(parents=True)
    path = write_key(images / "CT012", key_info(private_key))
    with pytest.raises(ServiceAccountError, match="thư mục ảnh") as error:
        load(path, project, image_folders=(secret_dir / "khac", images))
    assert_fixed(error, str(images))


def test_thu_muc_anh_viet_khac_hoa_thuong_tren_windows(outside, private_key, tmp_path):
    if os.name != "nt":
        pytest.skip("Chỉ Windows so đường dẫn không phân biệt hoa thường")
    _, project = outside
    images = tmp_path / "Anh"
    images.mkdir()
    path = write_key(images, key_info(private_key))
    with pytest.raises(ServiceAccountError, match="thư mục ảnh"):
        load(path, project, image_folders=(Path(str(images).upper()),))


@pytest.mark.parametrize(
    "folder", ["Google Drive", "My Drive", "Drive của tôi", "OneDrive - Cong ty", "Dropbox",
               "iCloud Drive"]
)
def test_thu_muc_dong_bo_chi_canh_bao(tmp_path, private_key, folder):
    project = tmp_path / "du-an"
    project.mkdir()
    synced = tmp_path / folder / "bi-mat"
    synced.mkdir(parents=True)
    account = load(write_key(synced, key_info(private_key)), project)
    assert account.email == EMAIL  # vẫn dùng được, chỉ cảnh báo
    assert any("đồng bộ lên mây" in warning for warning in account.warnings)
    assert all(str(synced) not in warning for warning in account.warnings)


def test_quyen_file_rong_tren_mac_linux_canh_bao(outside, private_key):
    if os.name == "nt":
        pytest.skip("Windows không dùng quyền kiểu chmod")
    secret_dir, project = outside
    path = write_key(secret_dir, key_info(private_key))
    path.chmod(0o644)
    account = load(path, project)
    (warning,) = account.warnings
    assert "chmod 600" in warning and str(secret_dir) not in warning


def test_thu_muc_khong_phai_file(outside):
    secret_dir, project = outside
    with pytest.raises(ServiceAccountError, match="không phải là một file"):
        load(secret_dir, project)


def test_file_qua_64_kb_bi_tu_choi(outside, private_key):
    secret_dir, project = outside
    info = key_info(private_key, ghi_chu="x" * (sa.MAX_KEY_FILE_BYTES + 1))
    with pytest.raises(ServiceAccountError, match="lớn bất thường"):
        load(write_key(secret_dir, info), project)


def test_file_bi_thay_giua_luc_kiem_va_mo_bi_tu_choi(outside, private_key, monkeypatch):
    """Đường đã kiểm vị trí phải đúng là file vừa mở (cùng thiết bị, cùng số file)."""
    secret_dir, project = outside
    path = write_key(secret_dir, key_info(private_key))
    resolved = os.fspath(path.resolve())
    real_stat = os.stat

    def swapped(target, *args, **kwargs):
        result = real_stat(target, *args, **kwargs)
        if not isinstance(target, int) and os.fspath(target) == resolved:
            values = list(result)
            values[1] += 1  # st_ino khác: file khác nằm ở đường đó
            return os.stat_result(values)
        return result

    monkeypatch.setattr(os, "stat", swapped)
    with pytest.raises(ServiceAccountError, match="vừa bị đổi"):
        load(path, project)


# ================================================================ nội dung file


def test_json_hong_khong_chep_noi_dung(outside):
    secret_dir, project = outside
    path = write_key(secret_dir, '{"type": "service_account", "private_key": "' + MOI)
    with pytest.raises(ServiceAccountError, match="không phải JSON") as error:
        load(path, project)
    assert_fixed(error)


def test_json_trung_khoa_bi_tu_choi(outside, private_key):
    """Hai ``token_uri`` (bộ đọc JSON lấy cái sau): không đoán, từ chối cả file."""
    secret_dir, project = outside
    body = json.dumps(key_info(private_key))[:-1] + ', "token_uri": "https://evil.example/t"}'
    with pytest.raises(ServiceAccountError, match="không phải JSON"):
        load(write_key(secret_dir, body), project)


def test_json_long_qua_sau_khong_lam_sap(outside):
    secret_dir, project = outside
    path = write_key(secret_dir, "[" * 30_000 + "]" * 30_000)  # dưới 64 KB, lồng rất sâu
    with pytest.raises(ServiceAccountError):
        load(path, project)


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"type": "authorized_user"}, "service_account"),
        ({"type": None}, "service_account"),
        ({"client_email": None}, "client_email"),
        ({"client_email": "lam@gmail.com"}, "client_email"),
        ({"client_email": "a@b.iam.gserviceaccount.com.evil.example"}, "client_email"),
        ({"client_email": ["x"]}, "client_email"),
        ({"private_key": None}, "private_key"),
        ({"private_key": NOT_PEM}, "private_key"),
        ({"private_key": PEM_BEGIN + "\n" + MOI + "\n" + PEM_END + "\n"}, "private_key"),
        ({"private_key_id": "co dau cach"}, "private_key"),
        ({"token_uri": None}, "token_uri"),
        ({"token_uri": "https://evil.example/token"}, "token_uri"),
        ({"token_uri": "http://oauth2.googleapis.com/token"}, "token_uri"),
        ({"token_uri": TOKEN_URI + "?x=1"}, "token_uri"),
        ({"token_uri": TOKEN_URI + "/"}, "token_uri"),
        ({"token_uri": "https://oauth2.googleapis.com.evil.example/token"}, "token_uri"),
        ({"universe_domain": "evil.example"}, "universe_domain"),
        ({"universe_domain": "googleapis.com.evil.example"}, "universe_domain"),
    ],
)
def test_noi_dung_sai_bi_tu_choi_cau_co_dinh(outside, private_key, changes, message):
    secret_dir, project = outside
    path = write_key(secret_dir, key_info(private_key, **changes))
    with pytest.raises(ServiceAccountError, match=message) as error:
        load(path, project)
    assert_fixed(error, "evil.example")


def test_khong_phai_object(outside):
    secret_dir, project = outside
    with pytest.raises(ServiceAccountError, match="service_account"):
        load(write_key(secret_dir, "[1, 2, 3]"), project)


# ================================================================ chỉ file đã kiểm (LC-T094-14)


def test_khong_doc_google_application_credentials(outside, private_key, monkeypatch, tmp_path):
    secret_dir, project = outside
    other = write_key(tmp_path, key_info(new_private_key(), client_email=(
        "khac@du-an-khac.iam.gserviceaccount.com")), name="khoa-khac.json")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", str(other))
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "du-an-khac")
    account = load(write_key(secret_dir, key_info(private_key)), project)
    assert account.email == EMAIL
    assert account.credentials.service_account_email == EMAIL


def test_code_khong_dung_tai_khoan_ngam_dinh_hay_uy_quyen():
    """Đọc cây cú pháp code Google (bỏ qua docstring, chú thích): không ``google.auth.default``,
    ``with_subject``, ``before_request``, ``AuthorizedSession``, không phạm vi Drive; không
    ``print``, không ``logging``."""
    import ast

    folder = config.PROJECT_ROOT / "seo_app" / "google"
    names = {"default", "with_subject", "before_request", "AuthorizedSession", "print",
             "logging", "getLogger"}
    files = sorted(folder.glob("*.py"))
    assert {path.name for path in files} >= {"service_account.py", "sheets.py"}
    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                assert node.attr not in names, (path.name, node.attr)
            elif isinstance(node, ast.Name):
                assert node.id not in names, (path.name, node.id)
            elif isinstance(node, ast.alias):
                assert node.name.split(".")[-1] not in names, (path.name, node.name)
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                assert "auth/drive" not in node.value and "cloud-platform" not in node.value
