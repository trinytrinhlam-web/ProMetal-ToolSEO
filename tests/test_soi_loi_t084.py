"""Soi Lỗi T-084: tab «🖼️ Ảnh» của trang Cài đặt không in đường dẫn đầy đủ thư mục ảnh (U1, U2).

Ngoài test của Họa Sĩ (``tests/test_settings_images.py``):

- hai hàm chép từ trang Soạn bài (``folder_name_md``, ``through_link`` trong ``settings.py``) phải
  khớp bản gốc (``name_md``/``shown_name``, ``_through_link`` trong ``write.py``): so cây cú pháp
  và so kết quả trên nhiều tên, nhiều đường dẫn (kể cả tên không tạo được trên Windows);
- khai báo lạ trong ``IMAGE_FOLDERS``: ``.``, ``..``, ``~``, ổ đĩa không có ``\\``, đường dẫn
  ``\\\\?\\``, tên thiết bị (``NUL``, ``CON``), dấu nháy, ký tự NUL, chỉ có ``;``;
- tên thư mục lạ tạo được trên Windows (``$…$``, ``---``, tên rất dài, ký tự đảo hướng, BOM, gạch
  nối mềm, chữ Hangul trống, dấu kết hợp chồng nhau); lối tắt nối tiếp lối tắt;
- quét cả trang Cài đặt (mọi tab, mọi nhãn, gợi ý, giá trị ô nhập) với **mọi** biến của ``.env``
  đều có giá trị, kể cả sau khi bấm «Kiểm tra» khóa và «Lưu» khóa sai.

Lỗi tìm được: ``xfail(strict=True)`` mã SL-T084-x (``docs/team/reports/T-084-soi-loi.md``). Thư
mục ảnh và ``.env`` nằm trong thư mục tạm; không gọi mạng.
"""

from __future__ import annotations

import ast
import os
import unicodedata
from pathlib import Path

import pytest
import test_app_pages as pages
import test_settings_images as si

import seo_app.config as config
from seo_app.text import escape_markdown

env = pages.env  # mật khẩu thử, không có khóa AI thật
IS_WINDOWS = os.name == "nt"
VIEWS = Path(__file__).resolve().parent.parent / "app" / "views"


# ======================================================== hai bản hàm chép phải khớp bản gốc


def _load(path: Path, functions: set[str], names: set[str]) -> dict:
    """Chỉ lấy các hàm, hằng cần so từ file trang (nhập file trang là chạy cả trang)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    body = [
        node
        for node in tree.body
        if (isinstance(node, ast.FunctionDef) and node.name in functions)
        or (
            isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id in names for t in node.targets)
        )
    ]
    assert len(body) == len(functions) + len(names), [getattr(n, "name", "=") for n in body]
    namespace = {"unicodedata": unicodedata, "escape_markdown": escape_markdown, "Path": Path}
    exec(compile(ast.Module(body=body, type_ignores=[]), str(path), "exec"), namespace)
    namespace["__ast__"] = {getattr(node, "name", "_HIDDEN_IN_NAME"): node for node in body}
    return namespace


@pytest.fixture(scope="module")
def copies() -> tuple[dict, dict]:
    settings = _load(VIEWS / "settings.py", {"folder_name_md", "through_link"}, {"_HIDDEN_IN_NAME"})
    write = _load(
        VIEWS / "write.py", {"shown_name", "name_md", "_through_link"}, {"_HIDDEN_IN_NAME"}
    )
    return settings, write


# Tên lạ, kể cả tên không tạo được trên Windows nhưng có trên Mac/Linux hay ổ mạng.
NAMES = [
    "Ảnh công trình",
    "[bấm](evil.example) _đậm_ `mã`",
    ":red[CẢNH BÁO] :material/delete: $x^2$",
    "<img src=x onerror=alert(1)> &lt;b&gt;",
    "**đậm** # tiêu đề > trích | bảng ~gạch~",
    "\u200b\u200c\u200d\u2060\ufeff\u00ad",
    "\u202egpj.exe \u202d\u2066\u2067\u2068\u2069\u061c\u200e\u200f",
    "dòng\nmới\r\tthụt\x00nul\x7f\u0085\u2028\u2029",
    "\ud800 nửa cặp \udfff",
    "\ue000 riêng \U000f0000 \U000e0001 \U000e0041",
    "\u05d0\u05d1 \u0627\u0644",
    "a" * 300,
    "\u3164\u3164 e\u0301\u0301\u0301",
    "   nhiều    dấu   cách   ",
    "",
]


def test_copied_name_rule_matches_write_page(copies):
    """``folder_name_md`` (Cài đặt) cho đúng kết quả của ``name_md`` (Soạn bài) với mọi tên, cùng
    bộ loại ký tự ẩn: hai trang hiện cùng một tên giống hệt nhau."""
    settings, write = copies
    assert settings["_HIDDEN_IN_NAME"] == write["_HIDDEN_IN_NAME"]
    for name in NAMES:
        assert settings["folder_name_md"](name) == write["name_md"](name), repr(name)


def test_copied_link_check_is_same_code(copies):
    """``through_link`` (Cài đặt) và ``_through_link`` (Soạn bài) cùng thân hàm (so cây cú pháp, bỏ
    tên hàm): sửa một bên mà quên bên kia thì test này hỏng."""
    settings, write = copies
    mine, theirs = settings["__ast__"]["through_link"], write["__ast__"]["_through_link"]
    assert ast.dump(ast.Module(body=mine.body, type_ignores=[])) == ast.dump(
        ast.Module(body=theirs.body, type_ignores=[])
    )


def test_copied_link_check_same_answers(copies, tmp_path):
    settings, write = copies
    real = tmp_path / "Anh that"
    (real / "con").mkdir(parents=True)
    link = tmp_path / "Loi tat"
    si.make_link(link, real)
    chain = tmp_path / "Loi tat 2"
    si.make_link(chain, link)
    paths = [real, real / "con", link, link / "con", chain, chain / "con", tmp_path / "khong co"]
    paths += [Path("tuong doi"), Path("~"), Path(tmp_path.anchor), Path("C:/a\x00b")]
    for path in paths:
        assert settings["through_link"](path) == write["_through_link"](path), path
    assert [settings["through_link"](p) for p in paths[:7]] == [
        False,
        False,
        True,
        True,
        True,
        True,
        False,
    ]


# ================================================================ khai báo lạ trong IMAGE_FOLDERS


def leaks(at, *paths: Path) -> list[str]:
    shown = si.page_strings(at)
    found = [str(p) for p in paths if str(p) in shown or p.as_posix() in shown]
    return found + ([str(Path.home())] if str(Path.home()) in shown else [])


DECLARATIONS = [
    (".", "1. \u2068Thư mục ảnh 1\u2069 — ⚠️ Thư mục ảnh số 1 phải ghi đường dẫn đầy đủ"),
    ("..", "1. \u2068\\.\\.\u2069 — ⚠️ Thư mục ảnh số 1 phải ghi đường dẫn đầy đủ"),
    ("{tmp}\\Anh tot\\..", "1. \u2068\\.\\.\u2069 — ✅ tìm thấy"),
    ("{tmp}/Anh tot/", "1. \u2068Anh tot\u2069 — ✅ tìm thấy"),
    ("{tmp}\\Anh tot\\..\\Anh tot\\.", "1. \u2068Anh tot\u2069 — ✅ tìm thấy"),
    ('"{tmp}\\Anh tot"', '1. \u2068Anh tot"\u2069 — ⚠️ Thư mục ảnh số 1 phải ghi đường dẫn'),
    ("  ;  {tmp}\\Anh tot  ;;  ", "1. \u2068Anh tot\u2069 — ✅ tìm thấy"),
]
WINDOWS_DECLARATIONS = [
    ("C:Anh", "1. \u2068Anh\u2069 — ⚠️ Thư mục ảnh số 1 phải ghi đường dẫn đầy đủ"),
    ("\\\\?\\{tmp}\\Anh tot", "1. \u2068Anh tot\u2069 — ✅ tìm thấy"),
    ("\\\\.\\C:\\", "1. \u2068Thư mục ảnh 1\u2069 — ✅ tìm thấy"),
    ("NUL", "1. \u2068NUL\u2069 — ⚠️ Thư mục ảnh số 1 phải ghi đường dẫn đầy đủ"),
    ("C:\\NUL", "1. \u2068NUL\u2069 — ⚠️ Chưa thấy thư mục ảnh số 1"),
    ("C:\\Windows\\CON", "1. \u2068CON\u2069 — ⚠️ Chưa thấy thư mục ảnh số 1"),
]


@pytest.mark.parametrize(
    ("declared", "line"),
    DECLARATIONS + (WINDOWS_DECLARATIONS if IS_WINDOWS else []),
    ids=lambda value: value if isinstance(value, str) and len(value) < 30 else None,
)
def test_odd_declaration_shown_without_path(project_root, tmp_path, monkeypatch, declared, line):
    """Khai báo lạ: trang không lỗi, dòng đầu đúng câu (tên cuối hay «Thư mục ảnh N», lý do cố
    định), không hiện đường dẫn khai báo, thư mục tạm, thư mục nhà."""
    (tmp_path / "Anh tot").mkdir()
    monkeypatch.setenv("IMAGE_FOLDERS", declared.replace("{tmp}", str(tmp_path)))
    at = si.open_settings(project_root)
    assert not at.exception
    assert si.folder_lines(at)[0].startswith(line)
    assert leaks(at, tmp_path, tmp_path / "Anh tot") == []


def test_home_folder_shows_only_its_name(project_root, monkeypatch):
    """``~`` (thư mục nhà): chỉ hiện tên thư mục cuối (tên tài khoản máy), không hiện đường dẫn."""
    monkeypatch.setenv("IMAGE_FOLDERS", "~")
    at = si.open_settings(project_root)
    assert si.folder_lines(at) == [
        f"1. \u2068{escape_markdown(Path.home().name)}\u2069 — ✅ tìm thấy"
    ]
    assert leaks(at) == []


@pytest.mark.parametrize("raw", [";;;", " ; ; ", ""])
def test_only_separators_is_not_declared(project_root, monkeypatch, raw):
    monkeypatch.setenv("IMAGE_FOLDERS", raw)
    tab = si.images_tab(si.open_settings(project_root))
    assert any("Chưa khai báo" in c.value for c in tab.caption)


def test_nul_in_env_file_entry(project_root, tmp_path, monkeypatch):
    """File ``.env`` hỏng có ký tự NUL trong một mục: mục đó hiện «�» và «Chưa thấy», mục còn lại
    vẫn hiện; không lỗi trang, không đường dẫn."""
    good = tmp_path / "Anh tot"
    good.mkdir()
    env_path = tmp_path / ".env"
    env_path.write_text(f"IMAGE_FOLDERS={good};C:/Anh\x00hong\n", encoding="utf-8")
    monkeypatch.setattr(config, "DEFAULT_ENV_FILE", env_path)
    at = si.open_settings(project_root)
    assert not at.exception
    lines = si.folder_lines(at)
    assert lines[0] == "1. \u2068Anh tot\u2069 — ✅ tìm thấy"
    assert lines[1].startswith("2. \u2068Anh\ufffdhong\u2069 — ⚠️ Chưa thấy thư mục ảnh số 2")
    assert leaks(at, tmp_path, good, env_path) == []


# ======================================================================== tên lạ tạo được


ODD_NAMES = [
    "$x^2$ ---",
    "a" * 120,
    "\u202egpj.exe \u2066\u2067\u061c\u200e\u200f",
    "\ufeffBOM \u00admềm",
    "\u3164\u3164\u3164",
    "e\u0301\u0301\u0301\u0301",
    "[a](evil.example) ~~gạch~~ ==đánh dấu== ^mũ^ {b} @x #1",
]


@pytest.mark.parametrize("name", ODD_NAMES, ids=range(len(ODD_NAMES)))
def test_odd_folder_name_matches_write_page_rule(project_root, tmp_path, monkeypatch, copies, name):
    """Tên lạ thật trên ổ: dòng hiện đúng như luật hiện tên của trang Soạn bài; không HTML."""
    folder = tmp_path / name
    folder.mkdir()
    monkeypatch.setenv("IMAGE_FOLDERS", str(folder))
    at = si.open_settings(project_root)
    assert si.folder_lines(at) == [f"1. {copies[1]['name_md'](name)} — ✅ tìm thấy"]
    for element in [*si.images_tab(at).markdown, *si.images_tab(at).caption]:
        assert not element.proto.allow_html
    assert leaks(at, tmp_path, folder) == []


def test_link_to_link_is_reported(project_root, tmp_path, monkeypatch):
    """Lối tắt trỏ tới một lối tắt khác (nối tiếp), và thư mục nằm trong chuỗi đó: đều «đi qua lối
    tắt», không hiện đường dẫn nào trong chuỗi."""
    real = tmp_path / "Anh that"
    (real / "con").mkdir(parents=True)
    first = tmp_path / "Loi tat 1"
    si.make_link(first, real)
    second = tmp_path / "Loi tat 2"
    si.make_link(second, first)
    monkeypatch.setenv("IMAGE_FOLDERS", f"{second};{second / 'con'}")
    at = si.open_settings(project_root)
    assert si.folder_lines(at) == [
        f"1. \u2068Loi tat 2\u2069 — ✅ tìm thấy · ↪️ {si.LINK_NOTE}",
        f"2. \u2068con\u2069 — ✅ tìm thấy · ↪️ {si.LINK_NOTE}",
    ]
    assert leaks(at, tmp_path, real, first, second) == []


# ================================================= cả trang Cài đặt, mọi biến .env đều có giá trị


def test_whole_settings_page_never_shows_env_values_or_paths(project_root, tmp_path, monkeypatch):
    """Mọi biến của ``.env`` có giá trị (đường dẫn, khóa, mật khẩu, địa chỉ có tên và mật khẩu):
    cả trang Cài đặt (mọi tab) không hiện giá trị nào, không hiện thư mục tạm hay thư mục nhà, kể
    cả sau khi bấm «Kiểm tra» từng khóa (mạng bị chặn trong test) và «Lưu» một khóa sai."""
    root = tmp_path / "may" / "Anh cong trinh"
    root.mkdir(parents=True)
    service = tmp_path / "bi-mat" / "service-account-t084.json"
    # Giá trị giả để dò (không phải khóa thật); tên biến và giá trị để ở hai danh sách riêng cho
    # công cụ quét bí mật khỏi báo nhầm.
    names = [
        "WORDPRESS_URL",
        "WORDPRESS_USERNAME",
        "WORDPRESS_APP_PASSWORD",
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_SERVICE_ACCOUNT_FILE",
        "GOOGLE_SHEET_ID",
        "GSC_SITE_URL",
        "IMAGE_FOLDERS",
    ]
    markers = [
        "https://wp-user-t084" + ":wp-pass-t084" + "@example.invalid/sub",
        "wp-user-t084",
        "abcd efgh ijkl t084",
        "sk-ant-" + "dauthu-T084-aaaa1111",
        "sk-proj-" + "dauthu-T084-bbbb2222",
        "AIza" + "dauthu-T084-cccc3333",
        str(service),
        "sheet-id-t084-dddd4444",
        "sc-domain:marker-t084.example",
        f"{root};{tmp_path / 'usb' / 'Anh cu'}",
    ]
    values = dict(zip(names, markers, strict=True))
    for name in values:
        monkeypatch.delenv(name, raising=False)
    env_path = tmp_path / ".env"
    env_path.write_text("".join(f"{k}={v}\n" for k, v in values.items()), encoding="utf-8")
    monkeypatch.setattr(config, "DEFAULT_ENV_FILE", env_path)

    def assert_clean(at) -> None:
        assert not at.exception
        shown = si.page_strings(at)
        for name, value in values.items():
            for part in {value, *value.split(";")}:
                assert part not in shown, name
        for secret in ("wp-pass-t084", "aaaa1111", "bbbb2222", "cccc3333", "dddd4444"):
            assert secret not in shown
        assert leaks(at, tmp_path, root, service, env_path) == []

    at = si.open_settings(project_root)
    assert_clean(at)
    for key in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"):
        at.button(key=f"api-key-check-btn-{key}").click().run()
        assert_clean(at)
    at.text_input(key="api-key-input-OPENAI_API_KEY").input("khoa co dau cach o giua").run()
    at.button(key="api-key-save-OPENAI_API_KEY").click().run()
    assert any("dấu cách" in e.value for e in at.error)
    assert_clean(at)


# ============================================== lỗi có từ trước: .env không đọc được (SL-T084-1)


@pytest.mark.xfail(
    strict=True,
    reason="SL-T084-1: .env không phải UTF-8 làm app sập, hiện traceback có đường dẫn thư mục app",
)
@pytest.mark.parametrize(
    "content",
    [
        "IMAGE_FOLDERS=C:/Ánh công trình\n".encode("cp1252"),  # Notepad cũ lưu kiểu «ANSI»
        b"\xff\xfeI\x00M\x00",  # UTF-16 có BOM
    ],
    ids=["ansi", "utf16"],
)
def test_env_file_not_utf8_fixed_message_no_traceback(project_root, tmp_path, monkeypatch, content):
    """File ``.env`` lưu sai bảng mã (Notepad cũ lưu «ANSI», hay UTF-16): ``load_settings`` ném
    ``UnicodeDecodeError`` ngoài khối bắt ``ConfigError`` của ``app/main.py``, nên mọi trang (kể
    cả Cài đặt, cả trước màn đăng nhập) chỉ hiện lỗi tiếng Anh kèm traceback có đường dẫn tuyệt đối
    của thư mục cài app và thư viện. Mong đợi: câu tiếng Việt cố định (như ``env_file`` đã có khi
    lưu khóa: «File .env không đọc được dạng UTF-8…»), không traceback, không đường dẫn."""
    from streamlit.testing.v1 import AppTest

    env_path = tmp_path / ".env"
    env_path.write_bytes(content)
    monkeypatch.setattr(config, "DEFAULT_ENV_FILE", env_path)
    at = AppTest.from_file(str(project_root / "app" / "main.py"), default_timeout=30)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert any("UTF-8" in e.value for e in at.error)
    assert str(project_root) not in si.page_strings(at)
