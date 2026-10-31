"""Test thêm của Soi Lỗi T-105: ``set_password`` / bộ ghi ``.env`` khi chương trình khác **sửa**
``.env`` đúng lúc bộ ghi vừa thay file (khác SL-T104-1: ở đó file bị **giữ**, đọc lại lỗi).

- SL-T105-1 (Thấp, có từ trước, từ T-104): bộ ghi thay ``.env`` xong, đọc lại **được** nhưng
  nội dung đã khác chữ vừa ghi, vì chương trình khác (đồng bộ thư mục trả bản cũ, trang Cài đặt lưu
  khóa cùng lúc…) vừa ghi đè. Bộ ghi trả bản cũ (đúng), nhưng câu báo nói «File .env có dòng sai
  định dạng … thiếu dấu nháy đóng» (``set_password``) / «File .env có định dạng lạ …» (trang Cài
  đặt): người dùng đi tìm một dòng sai không có, đúng loại lỗi SL-T104-1 đã sửa cho trường hợp file
  bị giữ. Bộ ghi phân biệt được: chữ đọc lại khác chữ vừa ghi là file bị sửa; chữ giống mà đọc ra
  khác mới là định dạng.

Lỗi tìm được đánh dấu ``xfail(strict=True)`` kèm mã SL-T105-x. Chỉ dùng ``.env`` trong thư mục tạm.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from test_hash_password_script import load_script

import seo_app.config as config
import seo_app.env_file as env_file
from seo_app.auth import hash_password
from seo_app.env_file import EnvFileError, set_api_key

KEY = "APP_PASSWORD_HASH"
OLD = hash_password("-".join(["mat", "khau", "cu", "SL105"]), iterations=1_000)
OTHER = f"WORDPRESS_URL=https://a.vn\n{KEY}={OLD}\nIMAGE_FOLDERS=D:/Anh\n"
CHANGED_BY_OTHER_PROGRAM = f"WORDPRESS_URL=https://a.vn\n{KEY}=khac\nIMAGE_FOLDERS=D:/Anh\n"


def _overwritten_after_replace(monkeypatch) -> None:
    """Ngay sau lần thay ``.env`` đầu tiên, «chương trình khác» ghi đè nội dung hợp lệ khác."""
    real = env_file._atomic_write
    done: list[int] = []

    def write_then_other_program(path, content):
        real(path, content)
        if not done:
            done.append(1)
            Path(path).write_bytes(CHANGED_BY_OTHER_PROGRAM.encode("utf-8"))

    monkeypatch.setattr(env_file, "_atomic_write", write_then_other_program)


@pytest.mark.xfail(
    strict=True,
    reason=(
        "SL-T105-1 (soi-loi, có từ T-104): chương trình khác ghi đè .env ngay sau khi bộ ghi thay "
        "file; đọc lại được mà khác chữ vừa ghi, set_password vẫn báo «dòng sai định dạng … thiếu "
        "dấu nháy đóng» (không đúng nguyên nhân)"
    ),
)
def test_sl_t105_1_set_password_other_program_changed_env(
    project_root, tmp_path, monkeypatch, capsys
):
    env = tmp_path / ".env"
    env.write_bytes(OTHER.encode("utf-8"))
    script = load_script(project_root)
    monkeypatch.setattr(script, "DEFAULT_ENV_FILE", env)
    monkeypatch.setattr(script.getpass, "getpass", lambda prompt="": "mat-khau-moi-SL105")
    monkeypatch.delenv(KEY, raising=False)
    _overwritten_after_replace(monkeypatch)
    code = script.main([])
    out = capsys.readouterr().out
    assert code == 1
    assert env.read_bytes() == OTHER.encode("utf-8")  # bộ ghi trả bản cũ (đã đúng)
    assert "sai định dạng" not in out and "dấu nháy" not in out
    assert str(tmp_path) not in out and "Traceback" not in out


@pytest.mark.xfail(
    strict=True,
    reason=(
        "SL-T105-1 (soi-loi, có từ T-104): trang Cài đặt lưu khóa AI đúng lúc chương trình khác "
        "ghi đè .env; câu báo «File .env có định dạng lạ … sửa tay» (không đúng nguyên nhân)"
    ),
)
def test_sl_t105_1_settings_writer_other_program_changed_env(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_bytes(OTHER.encode("utf-8"))
    monkeypatch.setattr(config, "DEFAULT_ENV_FILE", env)
    _overwritten_after_replace(monkeypatch)
    with pytest.raises(EnvFileError) as info:
        set_api_key("GEMINI_API_KEY", "AIzaKhoaGiaSL105", env)
    assert env.read_bytes() == OTHER.encode("utf-8")
    assert "định dạng lạ" not in str(info.value) and "sửa tay" not in str(info.value)
