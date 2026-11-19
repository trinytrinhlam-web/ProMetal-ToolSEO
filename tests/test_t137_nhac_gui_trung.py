"""T-137 (Họa Sĩ): nhắc chống gửi trùng sau khi file nháp bị cất sang một bên (SL-T136-1, G4).

File nháp bị chương trình khác làm hỏng thì kho cất nó sang một bên (``drafts.hong-…sqlite``, T-131,
T-136); dấu «đã gửi» của các bài gửi trước lúc đó đi theo file cũ. Phiếu này thêm:

1. Dấu hiệu theo **tên** file đã cất trong thư mục kho nháp (``moved_aside_names``): khuôn tên chặt,
   xét sau ``dir_has_link``, không mở, không đọc file nào; còn nguyên sau khi tắt mở lại app.
2. Lời nhắc thường trực ở cột «Đã gửi WordPress» (trang Bài viết), thay «Chưa có bài nào…».
3. Ô «Tôi đã xem trên WordPress: bài này chưa có trên website» ở bước Xuất bản, mọi hình thức, cho
   bài chưa có dấu «đã gửi» trong kho hiện tại: không tick sẵn, gắn mã băm bài, chỉ thêm cổng.
4. G4: «chỉ đọc» (mã 8) mà đầu file ghi phiên bản lạ là file lạ: báo «bị lỗi», thao tác sau cất
   file.

Hai đường gửi trùng của Soi Lỗi (G2 T-136): tab mở bài trước lần gửi ở tab khác; F5, tab mới, mở
lại app. Ảnh giả, WordPress giả, AI giả của ``tests/test_app_images.py``, ``tests/test_t102_publish
.py``; kho nháp, bản lưu kế hoạch, danh sách bài trong thư mục tạm; không gọi mạng thật.
"""

from __future__ import annotations

import builtins
import contextlib
import io
import os
import sqlite3
import stat
from datetime import UTC, datetime
from pathlib import Path

import pytest
import streamlit as st
import test_app_images as ui
import test_soi_loi_t112 as sl112
import test_t092_nhap_bi_xoa as t92
import test_t102_publish as t102
from test_t131_kho_nhap import link_dir, unlink_dir_link

from seo_app.storage import drafts, plan_cache, site_index
from seo_app.storage.drafts import (
    DraftError,
    DraftPlanRef,
    DraftSnapshot,
    DraftStore,
    SendState,
    moved_aside_names,
)
from seo_app.text import escape_markdown

# Fixture dùng chung: mật khẩu thử, cache ảnh xem trước tạm, AI giả, thư mục ảnh, WordPress giả
# (``live``: thêm quyền đăng bài, giờ máy chủ cho Hẹn giờ / Đăng ngay).
env = ui.env
previews = ui.previews
fake_ai = ui.fake_ai
root = ui.root
site = ui.site
live = t102.live

button = ui.button
run_ok = ui.run_ok
send_button = t102.send_button
DRAFT, SCHEDULE, PUBLISH = "Nháp", "Hẹn giờ", "Đăng ngay"
GATE = "_wp_moved_ok"
LABEL = "Tôi đã xem trên WordPress: bài này chưa có trên website"
GATE_TEXT = "nên app không biết bài này đã có trên website chưa"
RESET_TEXT = "sau lần bạn tick «Tôi đã xem trên WordPress…»"
HOME_TEXT = "nên danh sách này có thể thiếu bài"
EMPTY = "Chưa có bài nào phần mềm đã gửi lên WordPress."
RECOVERED = "File nháp cũ bị hỏng nên đã được cất sang một bên"
GOOD = "drafts.hong-20251111-090000.sqlite"  # đúng khuôn tên kho đặt khi cất file


@pytest.fixture(autouse=True)
def caches(monkeypatch, tmp_path_factory):
    """Bản lưu kế hoạch, danh sách bài đã đăng trong thư mục tạm (không đụng ``data/`` thật)."""
    folder = tmp_path_factory.mktemp("cache-t137")
    monkeypatch.setattr(plan_cache, "DEFAULT_PLAN_CACHE_FILE", folder / "plan_cache.sqlite")
    monkeypatch.setattr(site_index, "DEFAULT_SITE_INDEX_FILE", folder / "site_index.sqlite")


# ============================================================ dò tên file đã cất


@pytest.fixture
def project(tmp_path: Path, monkeypatch) -> Path:
    """Thư mục dự án giả; ``PROJECT_ROOT`` của kho nháp trỏ vào đó."""
    folder = tmp_path / "du-an"
    (folder / "data").mkdir(parents=True)
    monkeypatch.setattr(drafts, "PROJECT_ROOT", folder)
    return folder


@pytest.fixture
def path(project: Path) -> Path:
    return project / "data" / "drafts.sqlite"


def touch(folder: Path, *names: str) -> None:
    """File rỗng mang tên ``names``: app chỉ xét tên, không đọc nội dung."""
    folder.mkdir(parents=True, exist_ok=True)
    for name in names:
        (folder / name).write_bytes(b"")


def set_byte(file: Path, offset: int, value: int) -> None:
    data = bytearray(file.read_bytes())
    data[offset] = value
    file.write_bytes(bytes(data))


def sent_draft(file: Path, post_id: int = 501) -> tuple[DraftStore, str]:
    """Kho có một nháp đã gửi (bài ``post_id``); trả (kho, mã nháp)."""
    store = DraftStore(path=file)
    snap = store.save(DraftSnapshot(keyword="cổng inox", article_title="Sửa cổng inox Tân Phú"))
    store.save_send_state(snap.id, SendState.now(pending=False, post_id=post_id))
    return store, snap.id


def test_names_the_store_gives_are_found_newest_first(path):
    """Tên do chính kho đặt khi cất file hỏng được nhận (file nhật ký đi kèm thì không); nhiều file
    thì mới nhất trước, cùng giây thì số thứ tự lớn hơn là mới hơn."""
    assert moved_aside_names(path) == ()
    sent_draft(path)
    path.write_bytes(b"day khong phai sqlite")  # chương trình khác ghi đè file nháp
    store = DraftStore(path=path)
    store.list_drafts()  # kho cất file hỏng sang một bên, bắt đầu file mới
    assert store.recovered_from is not None
    moved = store.recovered_from.name
    assert moved_aside_names(path) == (moved,)
    older = [
        "drafts.hong-20251111-080000.sqlite",
        "drafts.hong-20251110-120000-10.sqlite",
        "drafts.hong-20251110-120000-2.sqlite",
        "drafts.hong-20251110-120000.sqlite",
        "drafts.hong-20241231-235959.sqlite",
    ]
    touch(path.parent, *reversed(older), "drafts.hong-20251110-120000.sqlite-journal")
    assert moved_aside_names(path) == (moved, *older)


# Chữ số không phải ASCII ở đúng chỗ ``strptime`` của Python vẫn nhận (năm; chữ số thứ hai của
# giây): chỉ khuôn ``[0-9]`` chặn được, không phải bước kiểm ngày giờ có thật.
FULLWIDTH_YEAR = "".join(chr(0xFF10 + int(d)) for d in "2025")  # chữ số toàn khối
ARABIC_ZERO = chr(0x0660)  # số 0 Ả Rập
NEAR_MISS = {
    "khong-gach": "drafts.hong20251110-120000.sqlite",
    "thieu-so": "drafts.hong-20251110-12000.sqlite",
    "thua-so": "drafts.hong-202511100-120000.sqlite",
    "thang-13": "drafts.hong-20251310-120000.sqlite",
    "29-thang-2": "drafts.hong-20250229-120000.sqlite",
    "gio-24": "drafts.hong-20251110-240000.sqlite",
    "giay-60": "drafts.hong-20251110-125960.sqlite",
    "so-1": "drafts.hong-20251110-120000-1.sqlite",
    "so-0": "drafts.hong-20251110-120000-0.sqlite",
    "so-0-dau": "drafts.hong-20251110-120000-02.sqlite",
    "so-qua-dai": "drafts.hong-20251110-120000-10000.sqlite",
    "nhat-ky": "drafts.hong-20251110-120000.sqlite-journal",
    "wal": "drafts.hong-20251110-120000.sqlite-wal",
    "duoi-khac": "drafts.hong-20251110-120000.bak",
    "them-duoi": "drafts.hong-20251110-120000.sqlite.bak",
    "chu-hoa": "drafts.HONG-20251110-120000.sqlite",
    "kho-the-anh": "image_tags.hong-20251110-120000.sqlite",
    "them-dau": "cu-drafts.hong-20251110-120000.sqlite",
    "khoang-trang": "drafts.hong-20251110-120000 .sqlite",
    "so-toan-khoi": f"drafts.hong-{FULLWIDTH_YEAR}1110-120000.sqlite",
    "so-a-rap": f"drafts.hong-20251110-12000{ARABIC_ZERO}.sqlite",
}


@pytest.mark.parametrize("name", list(NEAR_MISS.values()), ids=list(NEAR_MISS))
def test_near_miss_names_do_not_count(path, name):
    """Tên gần giống mà sai khuôn (ngày giờ không có thật, số thứ tự app không đặt, chữ số không
    phải ASCII, file nhật ký, kho khác…) không tính. Đối chứng: thêm một tên đúng khuôn thì chỉ tên
    đó được nhận."""
    touch(path.parent, name)
    assert moved_aside_names(path) == ()
    touch(path.parent, GOOD)
    assert moved_aside_names(path) == (GOOD,)


def test_data_link_gives_nothing(project, tmp_path):
    """``data/`` là liên kết (junction, symlink) tới thư mục có tên đúng khuôn: không tính, như mọi
    kho (nằm ngoài thư mục phần mềm). Đối chứng: cùng tên trong ``data/`` thường thì nhận."""
    outside = tmp_path / "o-khac"
    touch(outside, GOOD)
    data = project / "data"
    data.rmdir()
    link_dir(data, outside)
    try:
        assert moved_aside_names(data / "drafts.sqlite") == ()
    finally:
        unlink_dir_link(data)
    touch(data, GOOD)
    assert moved_aside_names(data / "drafts.sqlite") == (GOOD,)


def test_missing_or_odd_folder_gives_nothing(project):
    """Thư mục chưa có, hay «data» là một file: rỗng, không lỗi."""
    data = project / "data"
    data.rmdir()
    assert moved_aside_names(data / "drafts.sqlite") == ()
    data.write_bytes(b"")
    assert moved_aside_names(data / "drafts.sqlite") == ()


def test_lists_names_only_never_opens_moved_files(path, monkeypatch):
    """Không mở, không đọc, không hỏi thông tin file đã cất (hướng B.2 của T-136): mọi lần mở file,
    hỏi ``stat``, mở SQLite trong lúc dò không đụng tên nào có ``.hong-``."""
    touch(path.parent, GOOD, f"{GOOD}-journal")
    seen: list[str] = []

    def spy(real):
        def call(target, *args, **kwargs):
            seen.append(str(os.fspath(target)) if isinstance(target, str | os.PathLike) else "")
            return real(target, *args, **kwargs)

        return call

    for owner, name in (
        (os, "open"),
        (os, "stat"),
        (os, "lstat"),
        (builtins, "open"),
        (io, "open"),
        (sqlite3, "connect"),
    ):
        monkeypatch.setattr(owner, name, spy(getattr(owner, name)))
    assert moved_aside_names(path) == (GOOD,)
    assert seen  # bước kiểm liên kết có chạy (hỏi thư mục data)
    assert not [item for item in seen if ".hong-" in item]


def test_default_folder_read_at_call_time():
    """Không truyền đường dẫn: thư mục của ``DEFAULT_DRAFTS_FILE`` tra lúc gọi (test trỏ sang thư
    mục tạm)."""
    folder = drafts.DEFAULT_DRAFTS_FILE.parent
    touch(folder)
    assert moved_aside_names() == ()
    touch(folder, GOOD)
    assert moved_aside_names() == (GOOD,)


# ============================================================ G4: «chỉ đọc» mà đầu file lạ


def sqlite_error(code: int) -> sqlite3.OperationalError:
    exc = sqlite3.OperationalError("lỗi giả")
    exc.sqlite_errorcode = code
    return exc


def test_g4_newer_format_after_open_is_a_strange_file(path):
    """Kho dùng chung đã mở (trang Soạn bài); chương trình khác sửa byte 18 đầu file thành 3:
    SQLite mở file chỉ đọc nên lần lưu báo mã 8. Nay báo «bị lỗi… tải lại trang», không còn «chỉ
    đọc… bỏ chế độ chỉ đọc» (G4); thao tác kế tiếp cất file, kho mới không còn dấu «đã gửi»."""
    store, draft = sent_draft(path)
    set_byte(path, 18, 3)
    with pytest.raises(DraftError) as caught:
        store.save(DraftSnapshot(keyword="cửa cuốn"))
    assert str(caught.value) == drafts._MSG_BROKEN
    assert "chỉ đọc" not in str(caught.value)
    assert store.recovered_from is None and moved_aside_names(path) == ()
    store.list_drafts()
    assert store.recovered_from is not None
    assert moved_aside_names(path) == (store.recovered_from.name,)
    assert store.load_send_state(draft) is None  # dấu «đã gửi» nằm trong file đã cất


def test_g4_real_read_only_file_still_says_read_only(path):
    """Đối chứng: file bị đặt «chỉ đọc» thật (đầu file đúng) vẫn báo «chỉ đọc» và không bị cất;
    bỏ «chỉ đọc» thì kho dùng tiếp, dấu «đã gửi» còn nguyên."""
    store, draft = sent_draft(path)
    os.chmod(path, stat.S_IREAD)
    try:
        with pytest.raises(DraftError) as caught:
            store.save(DraftSnapshot(keyword="cửa cuốn"))
        assert str(caught.value) == drafts._MSG_READONLY
        with contextlib.suppress(DraftError):
            store.list_drafts()
        assert store.recovered_from is None and moved_aside_names(path) == ()
    finally:
        os.chmod(path, stat.S_IREAD | stat.S_IWRITE)
    assert store.load_send_state(draft).post_id == 501


DB_MESSAGES = {
    "ma-8-byte-18": (8, 18, drafts._MSG_BROKEN),
    "ma-8-byte-19": (8, 19, drafts._MSG_BROKEN),
    "ma-8-dau-dung": (8, None, drafts._MSG_READONLY),
    "ma-8-chua-co-file": (8, "missing", drafts._MSG_READONLY),
    "ma-11-byte-18": (11, 18, drafts._MSG_BROKEN),
}


@pytest.mark.parametrize(
    ("code", "header", "expected"), list(DB_MESSAGES.values()), ids=list(DB_MESSAGES)
)
def test_db_message_reads_header_only_for_read_only_code(path, code, header, expected):
    """``_db_message`` có đường dẫn: mã 8 mà byte 18 hay 19 lớn hơn 2 là file lạ; đầu file đúng,
    chưa có file thì vẫn «chỉ đọc». Không truyền đường dẫn: như trước (``test_t136``)."""
    if header != "missing":
        DraftStore(path=path).save(DraftSnapshot(keyword="cổng inox"))
    if isinstance(header, int):
        set_byte(path, header, 3)
    assert drafts._db_message(sqlite_error(code), path) == expected
    assert drafts._db_message(sqlite_error(8)) == drafts._MSG_READONLY


# ============================================================ trang Bài viết


def open_home(project_root):
    return ui.pages.open_page(project_root, "home.py")


def home_reminders(at) -> list[str]:
    return [w.value for w in at.warning if HOME_TEXT in w.value]


def move_aside_now() -> str:
    """Chương trình khác sửa đầu file nháp (byte 18 = 3); một trang mở kho mới (trang Bài viết, Kế
    hoạch) cất file sang một bên. Trả tên file đã cất."""
    file = drafts.DEFAULT_DRAFTS_FILE
    set_byte(file, 18, 3)
    store = DraftStore(file)
    store.list_drafts()
    assert store.recovered_from is not None
    return store.recovered_from.name


def test_home_reminder_stays_until_moved_file_is_removed(project_root):
    """Đường 2 ở trang Bài viết (Soi Lỗi G2): trước T-137 cột «Đã gửi WordPress» ghi «Chưa có bài
    nào…» (sai sự thật). Nay là lời nhắc thường trực (lần vẽ sau, phiên mới vẫn còn), nêu tên ngắn
    của file đã cất, không đường dẫn, nói cách tắt (app không tự xóa). Người dùng dời file đi thì
    lời nhắc hết."""
    sent_draft(drafts.DEFAULT_DRAFTS_FILE)
    name = move_aside_now()
    folder = drafts.DEFAULT_DRAFTS_FILE.parent
    at = open_home(project_root)
    (reminder,) = home_reminders(at)
    assert f"«{escape_markdown(name)}»" in reminder and "app không tự xóa" in reminder
    assert str(folder) not in reminder and folder.name not in reminder
    assert not any(EMPTY in c.value for c in at.caption)
    run_ok(at.run())
    assert len(home_reminders(at)) == 1
    again = open_home(project_root)
    assert len(home_reminders(again)) == 1
    (folder / name).unlink()  # đối chiếu xong, người dùng dời file đi
    run_ok(again.run())
    assert home_reminders(again) == []
    assert any(EMPTY in c.value for c in again.caption)


def test_home_reminder_counts_older_files_and_keeps_sent_list(project_root):
    """Hai file đã cất: nêu tên file mới nhất «và 1 file cũ hơn». Bài gửi sau lúc cất (kho mới có
    dấu «đã gửi») vẫn hiện trong danh sách bên dưới."""
    touch(drafts.DEFAULT_DRAFTS_FILE.parent, "drafts.hong-20251110-120000.sqlite", GOOD)
    sent_draft(drafts.DEFAULT_DRAFTS_FILE, post_id=777)
    at = open_home(project_root)
    (reminder,) = home_reminders(at)
    assert f"«{escape_markdown(GOOD)}» và 1 file cũ hơn" in reminder
    assert "#777" in "\n".join(m.value for m in at.markdown)


def test_home_near_miss_names_change_nothing(project_root):
    """Ca tên gần giống ở trang: không nhắc, vẫn «Chưa có bài nào…»."""
    touch(drafts.DEFAULT_DRAFTS_FILE.parent, *NEAR_MISS.values())
    at = open_home(project_root)
    assert home_reminders(at) == []
    assert any(EMPTY in c.value for c in at.caption)


def test_home_data_link_no_reminder(project_root, tmp_path, monkeypatch):
    """``data/`` là liên kết tới thư mục có tên đúng khuôn: trang không nhắc theo tên ở đó."""
    folder = tmp_path / "du-an"
    folder.mkdir()
    outside = tmp_path / "o-khac"
    touch(outside, GOOD)
    data = folder / "data"
    link_dir(data, outside)
    monkeypatch.setattr(drafts, "PROJECT_ROOT", folder)
    monkeypatch.setattr(drafts, "DEFAULT_DRAFTS_FILE", data / "drafts.sqlite")
    try:
        at = open_home(project_root)
        assert home_reminders(at) == []
    finally:
        unlink_dir_link(data)


# ============================================================ bước Xuất bản


def gate(at):
    """Ô «Tôi đã xem trên WordPress…» (``None``: không hiện)."""
    return next((box for box in at.checkbox if box.key == GATE), None)


def gate_texts(at) -> list[str]:
    return [w.value for w in at.warning if GATE_TEXT in w.value]


def tick(at):
    return run_ok(at.checkbox(key=GATE).check().run())


def writes(fake_site) -> list:
    return [r for r in fake_site.fake.requests if r.method != "GET"]


def ready_in_mode(project_root, monkeypatch, mode: str, snap: DraftSnapshot | None = None):
    """Bài có ảnh đã duyệt ở bước Xuất bản, hình thức ``mode``. Hẹn giờ, Đăng ngay: bật công tắc,
    tick «Tôi đã đọc lại…»; Đăng ngay thêm chữ SEO hợp lệ và «Ghi SEO lên website»."""
    at, _pid = ui.ready_image(project_root, snap)
    if mode == DRAFT:
        return ui.to_publish(at)
    if mode == PUBLISH:
        sl112.seo_like_client(monkeypatch, [])
        sl112.set_seo(at)
    t102.to_mode(at, mode)
    if mode == PUBLISH:
        run_ok(at.toggle(key="seo_write").set_value(True).run())
    return t102.confirm(at)


@pytest.mark.parametrize("mode", [DRAFT, SCHEDULE, PUBLISH], ids=["nhap", "hen-gio", "dang-ngay"])
def test_gate_in_every_mode(project_root, root, fake_ai, live, monkeypatch, mode):
    """Có file đã cất, bài chưa có dấu «đã gửi»: mọi hình thức hiện lời nhắc (tên ngắn, không đường
    dẫn) và ô tick **không** tick sẵn; nút gửi khóa (Hẹn giờ, Đăng ngay: dù đã tick «Tôi đã đọc
    lại…»). Tick rồi gửi: đúng một bài; sau đó bài có dấu «đã gửi», khóa cũ (T-086) thay cổng
    này."""
    touch(drafts.DEFAULT_DRAFTS_FILE.parent, GOOD)
    at = ready_in_mode(project_root, monkeypatch, mode)
    box = gate(at)
    assert box is not None and box.label == LABEL and box.value is False
    (text,) = gate_texts(at)
    assert f"«{escape_markdown(GOOD)}»" in text and "Mã bài WordPress" not in text
    assert str(drafts.DEFAULT_DRAFTS_FILE.parent) not in text
    assert send_button(at).disabled
    assert writes(live.site) == []
    tick(at)
    assert not send_button(at).disabled
    run_ok(send_button(at).click().run())
    assert len(live.site.posts()) == 1
    assert len(t102.release_bodies(live.site)) == (0 if mode == DRAFT else 1)
    assert gate(at) is None and send_button(at).disabled


@pytest.mark.parametrize("names", [(), tuple(NEAR_MISS.values())], ids=["khong-co", "gan-giong"])
def test_no_moved_file_nothing_changes(project_root, root, fake_ai, site, names):
    """Không có file đã cất (hay chỉ có tên gần giống): không lời nhắc, không ô tick, gửi như cũ."""
    touch(drafts.DEFAULT_DRAFTS_FILE.parent, *names)
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    assert gate(at) is None and gate_texts(at) == []
    assert not send_button(at).disabled
    ui.send(at)
    assert len(site.posts()) == 1


def test_gate_unticked_when_article_changes(project_root, root, fake_ai, site):
    """Tick rồi sửa chữ bài: mã băm khác, app bỏ tick và nói vì sao, nút khóa, không gửi gì."""
    touch(drafts.DEFAULT_DRAFTS_FILE.parent, GOOD)
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    tick(at)
    assert not send_button(at).disabled
    first = at.session_state["part_ids"][0]
    at.session_state[f"texts-{first}"] = ["Mở bài đã sửa sau khi tick."]
    at.session_state[f"ver-{first}"] = 0
    run_ok(at.run())
    assert gate(at).value is False
    assert any(RESET_TEXT in w.value for w in at.warning)
    assert send_button(at).disabled
    assert site.fake.requests == []


def test_gate_unticked_when_switching_article(project_root, root, fake_ai, site):
    """Tick ở bài A rồi mở bài B: ô của B không tick; quay lại A: phải tick lại."""
    touch(drafts.DEFAULT_DRAFTS_FILE.parent, GOOD)
    other = ui.store().save(ui.article(keyword="sửa cửa cuốn", article_title="Sửa cửa cuốn kêu to"))
    at, _pid = ui.ready_image(project_root)
    first = at.session_state["draft_id"]
    ui.to_publish(at)
    tick(at)
    assert not send_button(at).disabled
    for draft in (other.id, first):
        at.session_state["step"] = 0
        run_ok(at.run())
        run_ok(button(at, "Mở", key=f"open-{draft}").click().run())
        ui.to_publish(at)
        assert at.session_state["draft_id"] == draft
        assert gate(at).value is False and send_button(at).disabled
    assert site.fake.requests == []


def test_gate_unticked_after_failed_send(project_root, root, fake_ai, site):
    """Tick rồi gửi mà lần gửi hỏng trước khi tạo được bài (website từ chối ảnh): bài vẫn chưa có
    dấu «đã gửi», cổng còn, ô đã bỏ tick (bỏ trước khi gửi, như các ô xác nhận khác): phải xem lại
    rồi tick lại mới gửi tiếp được. Bài không đổi nên không báo «Bài đã thay đổi…»."""
    touch(drafts.DEFAULT_DRAFTS_FILE.parent, GOOD)
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    tick(at)
    site.fake.on("POST", ui.MEDIA, lambda _r: (400, {"code": "x", "message": "Bad request"}, {}))
    ui.send(at)
    assert site.posts() == [] and len(site.uploads()) == 1
    assert ui.store().load_send_state(at.session_state["draft_id"]) is None
    box = gate(at)
    assert box is not None and box.value is False
    assert not any(RESET_TEXT in w.value for w in at.warning)
    assert send_button(at).disabled


@pytest.mark.parametrize("ticked", [False, True], ids=["chua-tick", "doi-chung-da-tick"])
def test_click_through_gate_sends_nothing(project_root, root, fake_ai, site, monkeypatch, ticked):
    """Cú bấm lọt qua nút đang khóa (bấm đúp, SL-T056-1; AppTest không bấm được nút khóa nên giả ở
    ``st.button`` theo khóa ``wp-send``): chưa tick thì lần chạy đó xét lại cổng, không gửi gì.
    Đối chứng: đã tick thì cùng cú bấm gửi thật, đúng một bài (lần sau ô tick đã bỏ, bài có dấu
    «đã gửi»: không gửi thêm)."""
    touch(drafts.DEFAULT_DRAFTS_FILE.parent, GOOD)
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    if ticked:
        tick(at)
    assert send_button(at).disabled is not ticked
    t92.click_through_lock(monkeypatch)
    run_ok(at.run())
    assert len(site.posts()) == (1 if ticked else 0)
    run_ok(at.run())
    assert len(site.posts()) == (1 if ticked else 0)


@pytest.mark.parametrize("kind", ["da-gui", "gui-do"], ids=["da-gui", "gui-do"])
def test_existing_locks_unchanged_with_moved_file(project_root, root, fake_ai, site, kind):
    """Bài đã có trạng thái gửi trong kho hiện tại: khóa có sẵn giữ nguyên (đã gửi: «Tạo thêm…»;
    gửi dở: «Tôi đã kiểm tra trang quản trị…»), không chồng thêm ô mới."""
    touch(drafts.DEFAULT_DRAFTS_FILE.parent, GOOD)
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    state = SendState.now(pending=kind == "gui-do", post_id=777 if kind == "da-gui" else None)
    ui.store().save_send_state(at.session_state["draft_id"], state)
    run_ok(at.run())
    assert gate(at) is None and gate_texts(at) == []
    assert t92.box(at, t92.AGAIN if kind == "da-gui" else t92.CHECKED) is not None
    assert send_button(at).disabled


def test_gate_names_post_id_from_plan_row(project_root, root, fake_ai, site):
    """Bài mở từ dòng kế hoạch có Mã bài WordPress: lời nhắc nêu mã đó để xem đúng bài."""
    touch(drafts.DEFAULT_DRAFTS_FILE.parent, GOOD)
    ref = DraftPlanRef(
        key="B-001",
        sheet_hash="a" * 64,
        status="Đang viết",
        wp_post_id=501,
        opened_at=datetime.now(UTC),
    )
    at, _pid = ui.ready_image(project_root, ui.article(plan=ref))
    ui.to_publish(at)
    (text,) = gate_texts(at)
    assert "Mã bài WordPress 501" in text
    assert gate(at) is not None and send_button(at).disabled


def test_gate_gone_after_moved_file_removed(project_root, root, fake_ai, site):
    """Người dùng dời file đã cất ra khỏi thư mục: lần vẽ sau không còn cổng, gửi như cũ."""
    touch(drafts.DEFAULT_DRAFTS_FILE.parent, GOOD)
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    assert gate(at) is not None and send_button(at).disabled
    (drafts.DEFAULT_DRAFTS_FILE.parent / GOOD).unlink()
    run_ok(at.run())
    assert gate(at) is None and not send_button(at).disabled


# ============================================================ hai đường gửi trùng của Soi Lỗi


@pytest.mark.parametrize("mode", [DRAFT, SCHEDULE], ids=["nhap", "hen-gio"])
def test_route_1_tab_opened_before_send_elsewhere(project_root, root, fake_ai, live, mode):
    """Đường 1: tab này mở bài **trước** lần gửi ở tab khác (bài 777); rồi file nháp bị hỏng, trang
    khác cất nó sang một bên. Khung T-092 nói tab không biết; trước T-137 nút gửi vẫn mở, «Lưu lại
    thành nháp» làm mất khung, Hẹn giờ chỉ cần tick «Tôi đã đọc lại…». Nay nút khóa tới khi tick
    «Tôi đã xem trên WordPress…»; không gửi gì."""
    at, _pid = ui.ready_image(project_root)
    if mode == DRAFT:
        ui.to_publish(at)
    else:
        t102.to_mode(at, SCHEDULE)
    draft = at.session_state["draft_id"]
    ui.store().save_send_state(draft, SendState.now(pending=False, post_id=777))
    move_aside_now()
    run_ok(at.run())
    assert t92.NOT_KNOWN in t92.notice(at)
    assert gate(at) is not None and send_button(at).disabled
    run_ok(button(at, t92.RECREATE, key="draft-recreate").click().run())
    assert t92.notice(at) == "" and draft in t92.saved_ids()
    assert gate(at) is not None and send_button(at).disabled
    if mode == SCHEDULE:
        t102.confirm(at)
        assert send_button(at).disabled
    assert writes(live.site) == []
    tick(at)  # người dùng đã xem trên WordPress: mở được
    assert not send_button(at).disabled
    assert writes(live.site) == []


@pytest.mark.parametrize("restart", [False, True], ids=["f5-tab-moi", "mo-lai-app"])
def test_route_2_new_session_after_move(project_root, root, fake_ai, site, restart):
    """Đường 2: bài đã gửi (một bài trên website); file nháp bị cất; F5, tab mới hay tắt app mở lại
    (kho dùng chung tạo lại). «Bài đang soạn dở» rỗng; trang Bài viết nhắc thay «Chưa có bài
    nào…»; viết lại bài rồi sang Xuất bản: nút khóa tới khi tick, website vẫn một bài."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    ui.send(at)
    assert len(site.posts()) == 1
    move_aside_now()
    if restart:
        st.cache_resource.clear()
    fresh = ui.pages.open_page(project_root, "write.py")
    assert not [b for b in fresh.button if (b.key or "").startswith("open-")]
    home = open_home(project_root)
    assert len(home_reminders(home)) == 1
    assert not any(EMPTY in c.value for c in home.caption)
    again, _pid = ui.ready_image(project_root)
    ui.to_publish(again)
    assert gate(again) is not None and send_button(again).disabled
    assert len(site.posts()) == 1


def test_g4_on_compose_page_then_file_moved_and_lock_kept(project_root, root, fake_ai, site):
    """G4 trên trang: tab đang mở bài; tab khác gửi xong (bài 777); chương trình khác sửa byte 18.
    Lần tự lưu kế báo «bị lỗi… tải lại trang» (không «chỉ đọc»); lần chạy sau kho cất file, trang
    báo ``MSG_RECOVERED``; tab đã đọc được «đã gửi 777» trước đó nên vẫn khóa «Tạo thêm…»; trang
    Bài viết nhắc."""
    at, _pid = ui.ready_image(project_root)
    ui.to_publish(at)
    draft = at.session_state["draft_id"]
    ui.store().save_send_state(draft, SendState.now(pending=False, post_id=777))
    set_byte(drafts.DEFAULT_DRAFTS_FILE, 18, 3)
    first = at.session_state["part_ids"][0]
    at.session_state[f"texts-{first}"] = ["Mở bài sửa sau khi file nháp bị sửa đầu."]
    at.session_state[f"ver-{first}"] = 0
    run_ok(at.run())
    problems = [c.value for c in at.caption if "Chưa lưu được nháp" in c.value]
    assert problems and drafts._MSG_BROKEN in problems[0]
    assert not any("chỉ đọc" in text for text in problems)
    run_ok(at.run())
    assert any(RECOVERED in w.value for w in at.warning)
    assert len(moved_aside_names()) == 1
    assert t92.box(at, t92.AGAIN) is not None and send_button(at).disabled
    assert len(home_reminders(open_home(project_root))) == 1
    assert site.posts() == []


# ============================================================ README


def test_readme_paragraph_matches_page(project_root):
    """README mục «Gửi nháp»: một đoạn lời thường nêu đúng nhãn ô tick, cột nhắc, khuôn tên file và
    cách tắt nhắc (app không tự xóa); câu app báo khi cất file đúng câu trong README."""
    text = (project_root / "README.md").read_text(encoding="utf-8")
    start = text.index("**File nháp bị cất sang một bên**")
    paragraph = text[start : text.index("\n", start)]
    assert LABEL in paragraph and "Đã gửi WordPress" in paragraph
    assert "drafts.hong-" in paragraph and "app không tự xóa" in paragraph
    assert f"«{RECOVERED}…»" in paragraph and drafts.MSG_RECOVERED.startswith(RECOVERED)
