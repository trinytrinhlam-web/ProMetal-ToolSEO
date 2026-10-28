"""T-100: so danh tính thư mục của file khóa (Soi Lỗi SL-T097-5 và ghi nhận lượt 2 số 1).

Không gọi Google; không có khóa thật.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from seo_app.google import service_account

WINDOWS = pytest.mark.skipif(os.name != "nt", reason="chữ ổ đĩa chỉ có trên Windows")
BS = chr(92)  # dấu gạch chéo ngược (đường dẫn Windows)


@pytest.mark.parametrize(
    ("first", "second", "other"),
    [("H:", "I:", True), ("h:", "H:", False), ("C:", "", False), ("", "", False),
     (BS * 2 + "localhost" + BS + "D$", "D:", False),
     ("D:", BS * 2 + "?" + BS + "Volume{x}", False)],
)  # fmt: skip
def test_other_drive_letter(first, second, other):
    assert service_account._other_drive_letter(first, second) is other


@WINDOWS
def test_same_folder_numbers_on_two_drive_letters_is_not_inside(monkeypatch):
    # Ổ Google Drive for Desktop: mọi ổ cùng st_dev, số thư mục nhỏ lặp lại giữa các ổ.
    monkeypatch.setattr(service_account, "_identity", lambda _path: (428019990, 18))
    key = Path("I:/My Drive/bi-mat/khoa.json")
    assert not service_account._inside_by_identity(key, Path("H:/My Drive"))
    assert service_account._inside_by_identity(key, Path("I:/My Drive"))


def test_identity_walks_the_real_path_not_the_typed_dots(tmp_path):
    project = tmp_path / "du-an"
    outside = tmp_path / "ngoai"
    project.mkdir()
    outside.mkdir()
    typed = Path(f"{project}{os.sep}..{os.sep}ngoai{os.sep}khoa.json")
    assert not service_account._inside_by_identity(typed, project)
    assert service_account._inside_by_identity(project / "con" / "khoa.json", project)
