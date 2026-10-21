"""Soi Lỗi T-077 (rút gọn): tên công cụ AI gõ khác dạng chuẩn; ``get_many`` đọc xong mới xử lý.

Tên thư mục nay đọc thêm kiểu không tách chữ hoa và có thêm 4 tên công cụ gõ tách đôi ("Mid
Journey", "Fire Fly", "Co Pilot", "See Dream"). Đối chứng: tên ảnh thật viết liền kiểu CamelCase
(tên người, tên đường, khu căn hộ, có dấu hay không dấu, gõ hoa nhầm giữa chữ) và một nửa của tên
công cụ đứng riêng ("See", "Fire", "Co"…) vẫn là ảnh thật. ``get_many``: mọi câu SQL, kể cả
``COMMIT`` do Python tự chạy, nằm trong giao dịch đã kiểm, xong hết trước khi kiểm dòng đầu tiên.

Tên người, địa chỉ đều là giả. File SQLite dựng trong ``tmp_path``, không gọi mạng. Chưa thấy lỗi
mới; lỗi sau này (nếu có) đánh dấu ``xfail(strict=True)`` kèm mã ``SL-T077-n`` (xem
``docs/team/reports/T-077-soi-loi.md``).
"""

from __future__ import annotations

import sqlite3
from contextlib import closing

import pytest

import seo_app.storage.image_tags as image_tags_module
from seo_app.images.folders import ImageRef
from seo_app.images.tags import ImageTags, is_ai_name, tags_for_image
from seo_app.storage.image_tags import ImageTagStore, ref_key

BASE = "CT012 - Cổng inox - Quận 7/truoc"


@pytest.fixture(autouse=True)
def _never_touch_real_tag_file(monkeypatch, tmp_path_factory):
    """Không bao giờ đọc/ghi file thẻ thật ``data/image_tags.sqlite``."""
    folder = tmp_path_factory.mktemp("soi-loi-t077")
    monkeypatch.setattr(image_tags_module, "DEFAULT_IMAGE_TAGS_FILE", folder / "image_tags.sqlite")


def assert_real(name: str) -> None:
    """Thư mục ``name`` (dưới gốc), thư mục gốc tên ``name`` và tên file bắt đầu bằng ``name``
    đều là ảnh thật; ảnh trong thư mục giữ mã công trình, khu vực, trước/sau."""
    tags = tags_for_image(ImageRef(0, f"{BASE}/{name}/IMG_0001.jpg")).tags
    assert not tags.is_ai, name
    assert (tags.project_code, tags.area, tags.phase) == ("CT012", "Quận 7", "truoc"), name
    assert is_ai_name(f"G:/My Drive/{name}") is False, name
    assert not tags_for_image(ImageRef(0, f"{BASE}/{name} 01.jpg")).tags.is_ai, name


# Một nửa của tên công cụ tách đôi, đứng riêng hay kèm chữ khác (không kèm nửa còn lại).
TOOL_HALVES = ["See", "Fire", "Co", "Mid", "Fly", "Dream", "Pilot", "Journey", "SEE", "co"]
HALF_CONTEXTS = ["{h}", "Nha {h}", "{h} Home", "Sweet {h}", "Cong ty {h}", "{h} Phuong", "{h}2024"]


@pytest.mark.parametrize("half", TOOL_HALVES)
def test_half_of_a_split_tool_name_alone_stays_real(half):
    for context in HALF_CONTEXTS:
        assert_real(context.format(h=half))


# Tên ảnh thật viết liền: đọc kiểu không tách chữ hoa ra một chữ dài, không trùng dấu hiệu nào.
REAL_CAMEL_CASE_NAMES = [
    "NguyenVanHai",
    "NguyễnVănHải",
    "AnhHai",
    "ChiHaiYen",
    "NhaAnhTuan",
    "NhaChiMinh",
    "LeVanSy",
    "LêVănSỹ",
    "NguyenThiMinhKhai",
    "PhamVanDong",
    "HuynhTanPhat",
    "SuVanHanh",
    "AuCo",
    "LacLongQuan",
    "HaiBaTrung",
    "NoTrangLong",
    "VinhomesGrandPark",
    "MasteriThaoDien",
    "PhuMyHung",
    "SunriseCity",
    "CoopMart",
    "BachHoaXanh",
    "HighlandsCoffee",
    "CuaSoRa",
    "SoRaBanCong",
    "NhaCoHai",
    "NguYenVanA",  # gõ hoa nhầm giữa chữ
    "PhuOngNam",
    "DreamHome",
    "MidTown",
    "FireStation",
    "SeeYouCafe",
    "PilotPen",
]


@pytest.mark.parametrize("name", REAL_CAMEL_CASE_NAMES)
def test_real_camel_case_names_stay_real(name):
    assert_real(name)


def test_get_many_runs_every_statement_inside_the_checked_transaction_before_row_checks(tmp_path):
    """Ba thư mục gốc, mỗi gốc hai câu ``IN``: thứ tự câu SQL đúng như SQLite thấy (theo dõi bằng
    ``set_trace_callback``, thấy cả ``COMMIT`` Python tự chạy): ``BEGIN``, câu kiểm
    ``sqlite_master``, 6 câu đọc, ``COMMIT``; mọi câu sau ``BEGIN`` chạy trong giao dịch; kết nối
    đã đóng trước khi kiểm dòng đầu tiên, sau đó không còn câu SQL nào."""
    store = ImageTagStore(path=tmp_path / "data" / "image_tags.sqlite")
    chunk = image_tags_module._QUERY_CHUNK
    refs = [ImageRef(root, f"{BASE}/anh-{n}.jpg") for root in (0, 1, 2) for n in range(chunk + 3)]
    store.set(refs[0], ImageTags(area="Quận 7"))
    with closing(sqlite3.connect(store.path)) as conn, conn:
        conn.executemany(
            "INSERT OR REPLACE INTO manual_tags VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    ref.root_index,
                    ref_key(ref),
                    ref.rel_path,
                    "that",
                    "CT013",
                    "Cổng sắt",
                    "Quận 8",
                    "sau",
                    "2026-10-21T10:00:00+07:00",
                    1.0,
                )
                for ref in refs
            ],
        )
    events: list[tuple[str, str, bool | None]] = []
    real_connect = sqlite3.connect

    class Tracing(sqlite3.Connection):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.set_trace_callback(
                lambda sql: events.append(("sql", sql.split(" WHERE")[0], self.in_transaction))
            )

        def close(self):
            events.append(("close", "", None))
            super().close()

    real_row_to_tag = ImageTagStore._row_to_tag

    def row_to_tag(self, row):
        events.append(("row", "", None))
        return real_row_to_tag(self, row)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(
            image_tags_module.sqlite3,
            "connect",
            lambda *args, **kwargs: real_connect(*args, factory=Tracing, **kwargs),
        )
        patch.setattr(ImageTagStore, "_row_to_tag", row_to_tag)
        found = store.get_many(refs)

    assert set(found) == set(refs)
    assert {item.tags.area for item in found.values()} == {"Quận 8"}
    # Câu SQL theo dõi được đã thay sẵn giá trị tham số vào chỗ ``?``.
    statements = [(sql, in_tx) for kind, sql, in_tx in events if kind == "sql"]
    sqls = [sql for sql, _ in statements]
    assert sqls[:2] == ["PRAGMA trusted_schema = OFF", "BEGIN"]
    assert sqls[2].startswith("SELECT type, name, tbl_name, substr(sql, 1, ")
    assert "FROM sqlite_master" in sqls[2]
    reads = sqls[3:-1]
    assert len(reads) == 6  # 3 thư mục gốc × 2 nhóm (400 khóa + 3 khóa)
    assert all(sql.startswith("SELECT root_index, substr(ref_key, 1, ") for sql in reads)
    assert sqls[-1] == "COMMIT"
    assert all(in_tx for _, in_tx in statements[2:])  # sau BEGIN: mọi câu, cả COMMIT
    kinds = [kind for kind, _, _ in events]
    first_row = kinds.index("row")
    assert kinds[:first_row] == ["sql"] * len(statements) + ["close"]
    assert "sql" not in kinds[first_row:]
