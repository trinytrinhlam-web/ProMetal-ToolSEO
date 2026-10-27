"""Tab «🖼️ Ảnh» của trang Cài đặt: thư mục ảnh hiện như trang Soạn bài (T-084).

Chỉ tên thư mục gốc (``ImageLibrary.roots()``), đã escape và cô lập hướng chữ; báo tìm thấy hay
không và «đi qua lối tắt»; không bao giờ in đường dẫn đầy đủ hay nội dung ``.env`` (U1, U2, ghi
chú Lá Chắn T-048). Thư mục ảnh và ``.env`` đều nằm trong thư mục tạm; không gọi mạng.
"""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path

import pytest
import test_app_pages as pages
from google.protobuf.json_format import MessageToDict
from streamlit.testing.v1 import AppTest

import seo_app.config as config
from seo_app.images.folders import ImageLibrary
from seo_app.text import escape_markdown

env = pages.env  # mật khẩu thử, không có khóa AI thật
IS_WINDOWS = os.name == "nt"
TAB = "🖼️ Ảnh"
LINK_NOTE = "đi qua lối tắt"


def open_settings(project_root) -> AppTest:
    return pages.open_page(project_root, "settings.py")


def images_tab(at: AppTest):
    return next(tab for tab in at.tabs if tab.label == TAB)


def folder_lines(at: AppTest) -> list[str]:
    """Các dòng của danh sách thư mục ảnh (một ô Markdown, mỗi dòng «số. tên — trạng thái»)."""
    found = [m.value for m in images_tab(at).markdown if m.value.startswith("1. ")]
    assert len(found) == 1, found
    return found[0].split("\n")


def _strings(value) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [s for item in value.values() for s in _strings(item)]
    if isinstance(value, list):
        return [s for item in value for s in _strings(item)]
    return []


def page_strings(at: AppTest) -> str:
    """Mọi chuỗi trong mọi phần tử của trang (chữ, nhãn, gợi ý, giá trị ô nhập…), mọi tab."""
    found: list[str] = []

    def walk(node) -> None:
        proto = getattr(node, "proto", None)
        if proto is not None:
            found.extend(_strings(MessageToDict(proto)))
        for child in getattr(node, "children", {}).values():
            walk(child)

    walk(at.main)
    walk(at.sidebar)
    return "\n".join(found)


def assert_no_path(at: AppTest, *paths: Path) -> None:
    shown = page_strings(at)
    for path in paths:
        for text in {str(path), path.as_posix()}:
            assert text not in shown, text
    assert str(Path.home()) not in shown


def make_link(link: Path, target: Path) -> None:
    """Lối tắt tới thư mục: junction trên Windows (không cần quyền quản trị), symlink nơi khác."""
    if IS_WINDOWS:
        import _winapi

        _winapi.CreateJunction(str(target), str(link))
    else:
        link.symlink_to(target, target_is_directory=True)


# ============================================================================ tên lấy từ máy

# Markdown (link, nghiêng, mã), ký tự rộng 0 (U+200B), đảo hướng RLO (U+202E), chữ Do Thái (RTL).
WEIRD = "[bấm](evil.example) _đậm_ `mã` \u200bẩn \u202egpj.exe \u05d0\u05d1"


def test_folder_names_escaped_isolated_never_html(project_root, tmp_path, monkeypatch):
    """Tên thư mục là dữ liệu chưa tin cậy: không thành link hay định dạng, ký tự vô hình và RLO
    hiện thành «�», cả tên cô lập hướng chữ; không bao giờ vào HTML (U1, LC-T048-4 b)."""
    folder = tmp_path / WEIRD
    folder.mkdir()
    monkeypatch.setenv("IMAGE_FOLDERS", str(folder))
    at = open_settings(project_root)
    [line] = folder_lines(at)
    shown = "\u2068[bấm](evil.example) _đậm_ `mã` \ufffdẩn \ufffdgpj.exe \u05d0\u05d1\u2069"
    assert line == f"1. {escape_markdown(shown)} — ✅ tìm thấy"
    assert "](evil.example)" not in line and "`mã`" not in line and " _đậm_ " not in line
    everything = page_strings(at)
    assert "\u200b" not in everything and "\u202e" not in everything
    for element in [*images_tab(at).markdown, *images_tab(at).caption]:
        assert not element.proto.allow_html
    assert_no_path(at, folder, tmp_path)


def test_folder_names_isolated_one_by_one(project_root, tmp_path, monkeypatch):
    """Mỗi tên một cặp cô lập riêng: tên RTL của thư mục này không đảo chữ của thư mục kia."""
    first, second = tmp_path / "\u05d0\u05d1 \u202eabc", tmp_path / "Anh cong trinh"
    first.mkdir()
    second.mkdir()
    monkeypatch.setenv("IMAGE_FOLDERS", f"{first};{second}")
    at = open_settings(project_root)
    assert folder_lines(at) == [
        "1. \u2068\u05d0\u05d1 \ufffdabc\u2069 — ✅ tìm thấy",
        "2. \u2068Anh cong trinh\u2069 — ✅ tìm thấy",
    ]


# ============================================================== không in đường dẫn, nội dung .env


def test_no_absolute_path_or_env_content_anywhere(project_root, tmp_path, monkeypatch):
    """Yêu cầu 2: đường dẫn khai báo, đường dẫn thật, nội dung .env không hiện ở đâu trên trang
    (mọi tab, mọi nhãn, gợi ý, giá trị ô nhập), chỉ tên thư mục cuối."""
    root = tmp_path / "may" / "Anh cong trinh"
    root.mkdir(parents=True)
    missing = tmp_path / "usb" / "Anh cu"
    fake_key = "sk-ant-api03-KhoaGiaChiDeThu_T084-zzzz9999"
    env_path = tmp_path / ".env"
    folders = f"{root};{missing}"
    env_path.write_text(
        f"IMAGE_FOLDERS={folders}\nANTHROPIC_API_KEY={fake_key}\n", encoding="utf-8"
    )
    monkeypatch.setattr(config, "DEFAULT_ENV_FILE", env_path)
    at = open_settings(project_root)
    lines = folder_lines(at)
    assert lines[0] == "1. \u2068Anh cong trinh\u2069 — ✅ tìm thấy"
    assert lines[1].startswith("2. \u2068Anh cu\u2069 — ⚠️ Chưa thấy thư mục ảnh số 2")
    assert_no_path(at, root, root.parent, missing, missing.parent, tmp_path, env_path)
    shown = page_strings(at)
    for secret in (folders, fake_key, fake_key[-6:], "IMAGE_FOLDERS="):
        assert secret not in shown, secret
    source = (project_root / "app" / "views" / "settings.py").read_text(encoding="utf-8")
    assert not re.search(r"(?<!ImageLibrary)\._folders", source)


def test_os_error_while_reading_roots_shows_fixed_message(project_root, tmp_path, monkeypatch):
    """Lỗi của hệ điều hành (có đường dẫn trong câu lỗi) không làm sập trang, không lộ đường
    dẫn: chỉ hiện câu cố định."""
    root = tmp_path / "Anh cong trinh"
    root.mkdir()
    monkeypatch.setenv("IMAGE_FOLDERS", str(root))

    def denied(self):
        raise PermissionError(13, "Access is denied", str(root))

    monkeypatch.setattr(ImageLibrary, "roots", denied)
    at = open_settings(project_root)
    assert any("Không đọc được thư mục ảnh" in w.value for w in images_tab(at).warning)
    assert_no_path(at, root, tmp_path)


# =============================================================================== gốc không thấy


def test_roots_not_found_explained_without_path(project_root, tmp_path, monkeypatch):
    """Gốc không có trên máy, gốc ghi đường dẫn tương đối, gốc là file: báo đúng lý do bằng câu
    của ImageLibrary (số thứ tự, không đường dẫn); gốc còn lại vẫn «tìm thấy»."""
    found = tmp_path / "Anh cong trinh"
    found.mkdir()
    missing = tmp_path / "o-usb-chua-cam" / "Anh USB"
    a_file = tmp_path / "ghi-chu.txt"
    a_file.write_text("không phải thư mục", encoding="utf-8")
    monkeypatch.setenv("IMAGE_FOLDERS", f"{missing};Anh tuong doi;{a_file};{found}")
    at = open_settings(project_root)
    lines = folder_lines(at)
    assert lines[0].startswith("1. \u2068Anh USB\u2069 — ⚠️ Chưa thấy thư mục ảnh số 1 trên máy")
    assert lines[1].startswith("2. \u2068Anh tuong doi\u2069 — ⚠️ Thư mục ảnh số 2 phải ghi")
    assert lines[2].startswith("3. \u2068ghi\\-chu\\.txt\u2069 — ⚠️ Thư mục ảnh số 3 không phải")
    assert lines[3] == "4. \u2068Anh cong trinh\u2069 — ✅ tìm thấy"
    assert not any(LINK_NOTE in line for line in lines)
    assert not images_tab(at).warning
    assert_no_path(at, missing, missing.parent, a_file, found, tmp_path)


def test_drive_root_shows_number_not_drive_letter(project_root, tmp_path, monkeypatch):
    """Khai báo thẳng ổ đĩa (ví dụ E:/): tên thư mục cuối rỗng nên hiện «Thư mục ảnh 1», không
    hiện ký hiệu ổ."""
    anchor = Path(tmp_path.anchor)
    monkeypatch.setenv("IMAGE_FOLDERS", str(anchor))
    at = open_settings(project_root)
    assert folder_lines(at) == ["1. \u2068Thư mục ảnh 1\u2069 — ✅ tìm thấy"]
    if IS_WINDOWS:
        assert str(anchor) not in "\n".join(folder_lines(at))


def test_no_folders_declared(project_root):
    at = open_settings(project_root)
    tab = images_tab(at)
    assert any("Chưa khai báo" in c.value for c in tab.caption)
    assert not any(m.value.startswith("1. ") for m in tab.markdown)


def test_rest_of_the_tab_unchanged(project_root, tmp_path, monkeypatch):
    """Yêu cầu 3: phần còn lại của tab giữ như bố cục đã duyệt."""
    monkeypatch.setenv("IMAGE_FOLDERS", str(tmp_path))
    tab = images_tab(open_settings(project_root))
    assert tab.markdown[0].value == "**Thư mục ảnh thật**"
    assert [t.label for t in tab.text_input] == [
        "Phong cách chung cho ảnh AI (thêm vào mọi prompt)"
    ]
    assert [s.label for s in tab.select_slider] == ["Chất lượng nén WebP"]


# ==================================================================================== lối tắt


def test_root_through_link_is_reported_without_path(project_root, tmp_path, monkeypatch):
    """Gốc là lối tắt, gốc nằm trong một lối tắt, lối tắt hỏng (trỏ tới chỗ đã xóa): đều báo
    «đi qua lối tắt», không hiện đường dẫn lối tắt hay đích (ghi nhận Lá Chắn T-048)."""
    direct = tmp_path / "Anh that"
    direct.mkdir()
    target = tmp_path / "noi khac" / "Anh tro toi"
    (target / "Cong trinh").mkdir(parents=True)
    link = tmp_path / "Anh qua loi tat"
    make_link(link, target)
    gone = tmp_path / "da xoa"
    gone.mkdir()
    broken = tmp_path / "Loi tat hong"
    make_link(broken, gone)
    shutil.rmtree(gone)
    monkeypatch.setenv("IMAGE_FOLDERS", f"{direct};{link};{link / 'Cong trinh'};{broken}")
    at = open_settings(project_root)
    lines = folder_lines(at)
    assert lines[0] == "1. \u2068Anh that\u2069 — ✅ tìm thấy"
    assert lines[1] == f"2. \u2068Anh qua loi tat\u2069 — ✅ tìm thấy · ↪️ {LINK_NOTE}"
    assert lines[2] == f"3. \u2068Cong trinh\u2069 — ✅ tìm thấy · ↪️ {LINK_NOTE}"
    assert lines[3].startswith("4. \u2068Loi tat hong\u2069 — ⚠️ Chưa thấy thư mục ảnh số 4")
    assert lines[3].endswith(f" · ↪️ {LINK_NOTE}")
    assert [w.value for w in images_tab(at).warning if LINK_NOTE in w.value]
    assert_no_path(at, direct, link, target, target.parent, broken, gone, tmp_path)


@pytest.mark.parametrize("linked", [False, True])
def test_link_warning_only_when_some_root_is_a_link(project_root, tmp_path, monkeypatch, linked):
    real = tmp_path / "Anh that"
    real.mkdir()
    root = real
    if linked:
        root = tmp_path / "Loi tat"
        make_link(root, real)
    monkeypatch.setenv("IMAGE_FOLDERS", str(root))
    at = open_settings(project_root)
    assert (LINK_NOTE in folder_lines(at)[0]) is linked
    assert any(LINK_NOTE in w.value for w in images_tab(at).warning) is linked
