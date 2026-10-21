"""Soi Lỗi T-070 (rút gọn): dọn lỗi thẻ ảnh sau T-052.

Thử ba phần của phiếu: dấu hiệu ảnh AI trong tên thư mục và tên file (LC-T052-1, ``is_ai_name``),
kho thẻ sửa tay gặp file SQLite độc (LC-T052-2), ``get_many`` ép ảnh AI theo đúng ảnh được hỏi
(LC-T052-3). Tên khách, tên công ty, địa chỉ đều là giả. File SQLite dựng trong ``tmp_path``,
không gọi mạng.

Lỗi tìm thấy được đánh dấu ``xfail(strict=True)`` kèm mã ``SL-T070-n`` (xem
``docs/team/reports/T-070-soi-loi.md``): sửa xong thì test tự báo XPASS để gỡ dấu.
"""

from __future__ import annotations

import shutil
import sqlite3
import unicodedata
from contextlib import closing
from pathlib import Path, PurePosixPath, PureWindowsPath

import pytest

import seo_app.images.tags as tags_module
import seo_app.storage.image_tags as image_tags_module
from seo_app.images.folders import ImageRef
from seo_app.images.tags import (
    AREAS,
    SOURCE_AI,
    ImageTags,
    TagError,
    is_ai_name,
    tags_for_folder,
    tags_for_image,
)
from seo_app.storage.image_tags import ImageTagStore, _is_healthy
from seo_app.text import remove_accents

BASE = "CT012 - Cổng inox - Quận 7/truoc"
AI_ONLY = ImageTags(source=SOURCE_AI, category="Cổng inox")


@pytest.fixture(autouse=True)
def _never_touch_real_tag_file(monkeypatch, tmp_path_factory):
    """Không bao giờ đọc/ghi file thẻ thật ``data/image_tags.sqlite``."""
    folder = tmp_path_factory.mktemp("soi-loi-t070")
    monkeypatch.setattr(image_tags_module, "DEFAULT_IMAGE_TAGS_FILE", folder / "image_tags.sqlite")


def tags_of(rel_path: str) -> ImageTags:
    return tags_for_image(ImageRef(0, rel_path)).tags


# ===== LC-T052-1 · tên thư mục và tên file của ảnh AI ===========================================

# Ngoài danh sách của Thợ Máy (``tests/test_images_tags.py``): viết hoa/thường, không dấu, NFD,
# dính số, dính gạch, tên công cụ kèm hãng hay phiên bản.
AI_FOLDERS = [
    "Hình minh họa",
    "Minh Hoạ",
    "anh-minh-hoa",
    "anh_minh_hoa",
    "Ảnh minh họa 01",
    "minhhoa01",
    "minh-hoa-ai",
    "Ảnh-minh-họa",
    "Ảnh minh  họa",
    unicodedata.normalize("NFD", "Hình minh họa"),
    "TRI TUE NHAN TAO",
    "tri-tue-nhan-tao",
    "TriTueNhanTao",
    "trituenhantao",
    unicodedata.normalize("NFD", "Ảnh trí tuệ nhân tạo"),
    "Gen AI",
    "Gen-AI",
    "gen_ai",
    "genai2024",
    "GenAI-01",
    "Ảnh genai",
    "COPILOT",
    "Microsoft Copilot",
    "designer",
    "bing",
    "BingImageCreator",
    "bing-image-creator",
    "Leonardo.Ai",
    "leonardo ai",
    "ideogram",
    "FLUX.1",
    "flux1",
    "Flux1-dev",
    "flux-dev",
    "KLING AI",
    "Kling2.1",
    "dreamina",
    "Comfy UI",
    "RunwayML",
    "Krea AI",
    "krea.ai",
    "seedream4",
    "Seedream 4.0",
    "canva",
    "Midjourney6",
    "midjourney v6",
    "NanoBanana",
    "Imagen3",
    "DALLE3",
    "dalle3",
    "DALL·E",
    "gpt4o",
    "GPT Image",
    "StableDiffusion",
    "sdxl1.0",
    "Adobe Firefly",
    "Sora",
    "Hailuo",
    "Jimeng",
    "Recraft",
    "NightCafe",
    "SeaArt",
    "Meta AI",
    "Ảnh render",
    "render 3D",
    "ＡＩ",  # chữ toàn chiều rộng
    "𝐀𝐈",  # chữ toán học
]


@pytest.mark.parametrize("ai_dir", AI_FOLDERS)
def test_more_ai_folder_names_are_ai_at_any_depth(ai_dir):
    for rel_path in (f"{BASE}/{ai_dir}/x.png", f"{ai_dir}/{BASE}/x.png"):
        assert tags_of(rel_path) == AI_ONLY, rel_path
    assert is_ai_name(ai_dir) is True


AI_FILES = [
    "designer (1).jpeg",
    "copilot-image.png",
    "OIG1.jpg",
    "OIG2.jpg",
    "OIG4.jpg",
    "Ideogram_cong.png",
    "flux-dev_00001_.png",
    "flux_00001_.png",
    "FLUX.1-schnell.png",
    "grok-image-1234.jpg",
    "grok_1234.jpg",
    "Dreamina_1234.png",
    "ComfyUI_temp_abc_00001_.png",
    "Runway 2025-03-15.png",
    "Krea_cong.png",
    "seedream_cong.png",
    "Canva_cong.png",
    "Gemini_Generated_Image_abc123.png",
    "ChatGPT Image Mar 15, 2025, 10_20_30 AM.png",
    "DALL·E 2024-03-15 10.20.30 - A modern gate.webp",
    "Firefly 20240315102030.png",
    "ai_cong.png",
    "AI-cong.png",
    "GenAI_001.png",
    "sora_cong.png",
    "hailuo_cong.png",
    "anh-minh-hoa.jpg",
]


@pytest.mark.parametrize("file_name", AI_FILES)
def test_more_default_ai_file_names_are_ai(file_name):
    assert tags_of(f"{BASE}/{file_name}") == AI_ONLY


# Đối chứng: tên có chữ gần giống dấu hiệu nhưng không trùng trọn một từ, hay có dấu.
REAL_FOLDERS = [
    "Imagine Coffee",
    "Kreative Space",
    "Fluxion",
    "Chị Kréa",
    "AIA Building",
    "Aeon Mall",
    "Vinhomes Grand Park",
    "Ảnh chụp",
    "Hiện trạng",
    "khoai",
    "Kho hàng",
    "Nhà anh Hoà",
    "Bai Thuong",
]


@pytest.mark.parametrize("name", REAL_FOLDERS)
def test_names_close_to_ai_markers_stay_real(name):
    tags = tags_for_folder(f"CT015 - {name} - Q7/truoc").tags
    assert not tags.is_ai, name
    assert (tags.project_code, tags.area, tags.phase) == ("CT015", "Quận 7", "truoc"), name
    assert is_ai_name(name) is False


@pytest.mark.parametrize(
    "file_name",
    [
        "IMG_0001.jpg",
        "DSC_0001.JPG",
        "PXL_20250315_102030.jpg",
        "20250315_102030.jpg",
        "IMG-20250315-WA0001.jpg",
        "Screenshot_20250315.png",
        "z5432109876_abc.jpg",
        "xAI3kQ.jpg",
        "MAI_1.jpg",
    ],
)
def test_camera_and_chat_file_names_stay_real(file_name):
    tags = tags_of(f"{BASE}/{file_name}")
    assert not tags.is_ai and tags.area == "Quận 7", file_name


def test_no_word_of_the_tag_lists_is_ever_an_ai_marker():
    """Không khu vực, hạng mục hay chữ trước/sau nào trong danh sách (có dấu hay không dấu) bị coi
    là dấu hiệu ảnh AI: thẻ đọc từ danh sách không bao giờ tự làm ảnh thành ảnh AI."""
    words = set(AREAS)
    for name in ("_CATEGORY_ACTIONS", "_CATEGORY_OBJECTS", "_CATEGORY_MATERIALS"):
        words.update(getattr(tags_module, name))
    for aliases in tags_module._AREA_ALIASES.values():
        words.update(aliases)
    for texts in tags_module._PHASE_WORDS.values():
        words.update(texts)
    assert len(words) > 100
    flagged = [
        variant
        for word in sorted(words)
        for variant in (word, remove_accents(word), f"{word} 01")
        if is_ai_name(variant)
    ]
    assert flagged == []


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("", False),
        (".", False),
        ("..", False),
        ("C:\\", False),
        ("G:/My Drive/Ảnh AI/", True),
        ("G:\\My Drive\\Ảnh AI\\\\", True),
        ("\\\\may-chu\\chia-se\\Ảnh AI", True),
        ("G:/AI/Ảnh công trình", False),  # chỉ xét tên cuối
        (PureWindowsPath("G:/Drive/minh họa"), True),
        (PurePosixPath("/Users/khach/Genai"), True),
        ("Ảnh\u200bAI", True),  # ký tự vô hình chen giữa
    ],
)
def test_is_ai_name_last_name_only(name, expected):
    assert is_ai_name(name) is expected


@pytest.mark.parametrize("bad", [None, b"AI", 1, ImageRef(0, "AI/x.png")])
def test_is_ai_name_rejects_non_text(bad):
    with pytest.raises(TypeError):
        is_ai_name(bad)


# ===== LC-T052-2 · file SQLite độc ngoài 14 kiểu của Thợ Máy ===================================

REF = ImageRef(0, "CT012 - Cổng inox - Tân Phú/truoc/IMG_0001.jpg")
TAGS = ImageTags(project_code="CT012", category="Cổng inox", area="Tân Phú")


def make_app_file(path: Path, *pragmas: str) -> None:
    """File đúng như app tạo (dùng chính câu ``CREATE TABLE`` của app)."""
    with closing(sqlite3.connect(path)) as conn:
        for pragma in pragmas:
            conn.execute(pragma)
        with conn:
            for sql in image_tags_module._CREATE_TABLES:
                conn.execute(sql)
            conn.execute(
                "INSERT INTO info VALUES ('schema_version', ?)", (image_tags_module.SCHEMA_VERSION,)
            )


def edit_master(path: Path, *statements: str) -> None:
    """Sửa thẳng ``sqlite_master`` (``writable_schema``), như một chương trình lạ có thể làm."""
    with closing(sqlite3.connect(path)) as conn:
        conn.execute("PRAGMA writable_schema = ON")
        for statement in statements:
            conn.execute(statement)
        conn.commit()


def _duplicate_table_row(path: Path) -> None:
    make_app_file(path)
    edit_master(
        path, "INSERT INTO sqlite_master SELECT * FROM sqlite_master WHERE name = 'manual_tags'"
    )


def _rootpage(value: str):
    def build(path: Path) -> None:
        make_app_file(path)
        edit_master(path, f"UPDATE sqlite_master SET rootpage = {value} WHERE name = 'manual_tags'")

    return build


def _with_stat1(path: Path) -> None:
    make_app_file(path)
    with closing(sqlite3.connect(path)) as conn:
        conn.execute("ANALYZE")
        conn.commit()


def _trigger_inside_wal(path: Path) -> None:
    """File chính sạch; file ``-wal`` dựng sẵn (chưa ghi vào file chính) có thêm trigger."""
    source = path.with_name("nguon.sqlite")
    make_app_file(source, "PRAGMA journal_mode = WAL")
    conn = sqlite3.connect(source)
    try:
        conn.execute("PRAGMA wal_autocheckpoint = 0")
        conn.execute(
            "CREATE TRIGGER t AFTER INSERT ON manual_tags BEGIN "
            "UPDATE manual_tags SET area = 'Quận 1'; END"
        )
        conn.commit()
        shutil.copyfile(source, path)
        shutil.copyfile(f"{source}-wal", f"{path}-wal")
    finally:
        conn.close()
    source.unlink()


STRANGE_FILES = {
    "dong-bang-lap-lai": _duplicate_table_row,
    "rootpage-trung-bang-info": _rootpage(
        "(SELECT rootpage FROM sqlite_master WHERE name = 'info')"
    ),
    "rootpage-la-trang-1": _rootpage("1"),
    "rootpage-0": _rootpage("0"),
    "rootpage-ngoai-file": _rootpage("99999"),
    "co-sqlite_stat1": _with_stat1,
    "trigger-trong-file-wal": _trigger_inside_wal,
}


@pytest.mark.parametrize("case", list(STRANGE_FILES))
def test_more_strange_files_are_moved_aside_and_store_recovers(tmp_path, case):
    path = tmp_path / "image_tags.sqlite"
    STRANGE_FILES[case](path)
    assert _is_healthy(path) is False
    store = ImageTagStore(path=path)
    store.set(REF, TAGS)
    assert store.recovered_from is not None and store.recovered_from.exists()
    assert store.get(REF).tags == TAGS
    assert store.resolve(REF).error == ""


@pytest.mark.parametrize(
    "pragma", ["PRAGMA encoding = 'UTF-16le'", "PRAGMA journal_mode = WAL"], ids=["utf16", "wal"]
)
def test_valid_file_in_other_encoding_or_wal_mode_is_kept(tmp_path, pragma):
    path = tmp_path / "image_tags.sqlite"
    make_app_file(path, pragma)
    assert _is_healthy(path) is True
    store = ImageTagStore(path=path)
    store.set(REF, TAGS)
    assert store.recovered_from is None
    assert store.get(REF).tags == TAGS


def _hide_trigger_behind_duplicate_row(path: Path, body: str) -> None:
    """File app tạo + một dòng chỉ mục tự sinh lặp lại + trigger ở dòng thứ 6 của
    ``sqlite_master``. ``_app_tables`` đọc ``LIMIT`` (số dòng mong đợi + 1) = 5 dòng và so theo
    tập hợp, nên dòng lặp che mất trigger."""
    make_app_file(path)
    edit_master(
        path,
        "INSERT INTO sqlite_master SELECT * FROM sqlite_master "
        "WHERE name = 'sqlite_autoindex_manual_tags_1'",
        "INSERT INTO sqlite_master (type, name, tbl_name, rootpage, sql) VALUES "
        f"('trigger', 't', 'manual_tags', 0, "
        f"'CREATE TRIGGER t AFTER INSERT ON manual_tags BEGIN {body}; END')",
    )


MUTATE = "UPDATE manual_tags SET area = ''Quận 1''"
# Đệ quy có giới hạn (1e8 dòng): giới hạn số bước (hạ thấp trong test) dừng nó, không treo test.
RECURSIVE = (
    "SELECT count(*) FROM (WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM n "
    "WHERE x < 100000000) SELECT x FROM n)"
)


@pytest.mark.xfail(
    strict=True,
    reason=(
        "SL-T070-1: _app_tables đọc sqlite_master với LIMIT 5 và so theo tập hợp; một dòng chỉ "
        "mục tự sinh lặp lại (writable_schema) đẩy trigger ra ngoài LIMIT, file độc qua kiểm"
    ),
)
def test_sl_t070_1_duplicate_master_row_cannot_hide_a_trigger(tmp_path):
    path = tmp_path / "image_tags.sqlite"
    _hide_trigger_behind_duplicate_row(path, MUTATE)
    with closing(sqlite3.connect(path)) as conn:  # trigger có thật trong file
        assert conn.execute("SELECT count(*) FROM sqlite_master WHERE type = 'trigger'").fetchone()
    assert _is_healthy(path) is False


@pytest.mark.xfail(
    strict=True,
    reason=(
        "SL-T070-1: trigger ẩn sau dòng lặp chạy ở mỗi lần set: đổi khu vực vừa lưu "
        "(Tân Phú → Quận 1), file không bị đổi tên kể cả khi tạo kho mới"
    ),
)
def test_sl_t070_1_hidden_trigger_never_changes_saved_tags(tmp_path):
    path = tmp_path / "image_tags.sqlite"
    _hide_trigger_behind_duplicate_row(path, MUTATE)
    for _ in range(2):  # lần 2: như khởi động lại app
        store = ImageTagStore(path=path)
        store.set(REF, TAGS)
        assert store.get(REF).tags.area == "Tân Phú"


@pytest.mark.xfail(
    strict=True,
    reason=(
        "SL-T070-1: trigger đệ quy ẩn sau dòng lặp: mỗi lần set bị giới hạn số bước dừng rồi báo "
        "lỗi, nhưng _is_healthy vẫn cho qua nên file không bao giờ bị đổi tên: kẹt mãi"
    ),
)
def test_sl_t070_1_hidden_recursive_trigger_does_not_jam_store(tmp_path, monkeypatch):
    monkeypatch.setattr(image_tags_module, "_MAX_VM_STEPS", 200_000)
    path = tmp_path / "image_tags.sqlite"
    _hide_trigger_behind_duplicate_row(path, RECURSIVE)
    store = ImageTagStore(path=path)
    errors = 0
    for _ in range(3):
        try:
            store.set(REF, TAGS)
        except image_tags_module.ImageTagStoreError:
            errors += 1
    assert errors <= 1
    assert store.get(REF).tags == TAGS


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "SL-T070-2: _guard chỉ đếm số bước máy ảo; một bước có thể tốn rất lâu (randomblob, "
        "zeroblob, printf %.*c cỡ chục MB), nên truy vấn ít bước mà chạy lâu không bị dừng"
    ),
)
def test_sl_t070_2_guard_also_stops_few_but_heavy_steps():
    """32 bước nặng (mỗi bước tạo 25 MB, khoảng 4,5 giây trên máy Windows của chủ dự án) trên kết
    nối đã ``_guard``: phải bị dừng (chạy quá giờ) hoặc bị từ chối (giá trị quá lớn), không được
    chạy xong như thường. Đây là khe còn lại khi file bị thay đúng lúc giữa lần kiểm và lần đọc."""
    with closing(sqlite3.connect(":memory:")) as conn:
        image_tags_module._guard(conn)
        try:
            conn.execute(
                "SELECT sum(length(randomblob(25000000))) FROM (WITH RECURSIVE n(x) AS "
                "(SELECT 1 UNION ALL SELECT x + 1 FROM n WHERE x < 32) SELECT x FROM n)"
            ).fetchone()
        except sqlite3.DatabaseError:
            return
    raise AssertionError("truy vấn nặng chạy xong mà không bị dừng")


# ===== LC-T052-3 · get_many theo đúng ảnh được hỏi =============================================


def test_get_many_and_resolve_many_force_ai_per_ref_asked(tmp_path):
    """Ba cách viết hoa thường của cùng một khóa trong một lần hỏi: chỉ ``KhoAI`` (Kho AI) là ảnh
    AI; ``khoai`` và ``KHOAI`` (củ khoai) giữ thẻ thật đã lưu."""
    store = ImageTagStore(path=tmp_path / "image_tags.sqlite")
    real = ImageRef(0, f"{BASE}/khoai/x.png")
    ai = ImageRef(0, f"{BASE}/KhoAI/x.png")
    upper = ImageRef(0, f"{BASE}/KHOAI/x.png")
    saved = ImageTags(project_code="CT012", category="Cổng inox", area="Quận 7", phase="truoc")
    store.set(real, saved)
    found = store.get_many([ai, real, upper])
    assert found[ai].tags == AI_ONLY
    assert found[real].tags == saved and found[upper].tags == saved
    resolved = store.resolve_many([upper, ai, real])
    assert resolved[ai].tags == AI_ONLY and resolved[ai].manual
    assert resolved[real].tags == saved and resolved[upper].tags == saved
    with pytest.raises(TagError):
        store.set(ai, saved)  # ảnh trong thư mục AI không đổi được thành ảnh thật


# ===== Lỗi mới về tên (LC-T052-1 còn sót) =======================================================


@pytest.mark.xfail(
    strict=True,
    reason=(
        "SL-T070-3: tên file chỉ tách ở dấu cách/gạch (không tách chữ dính số), nên tên công cụ "
        "hay 'AI' dính số phiên bản/số thứ tự không nhận là ảnh AI, dù tên thư mục cùng chữ thì "
        "nhận (AI01, dalle3, flux1, gpt4o, Gemini2…)"
    ),
)
@pytest.mark.parametrize(
    "file_name",
    [
        "AI01.png",
        "AI2.jpg",
        "dalle3_cong-sat.png",
        "flux1-dev_00001_.png",
        "gpt4o_cong-sat.png",
        "seedream4_cong-sat.png",
        "imagen3_cong-sat.png",
        "Gemini2_cong-sat.png",
    ],
)
def test_sl_t070_3_ai_file_name_with_digits_stuck_is_ai(file_name):
    assert tags_of(f"{BASE}/{file_name}") == AI_ONLY


@pytest.mark.xfail(
    strict=True,
    reason=(
        "SL-T070-4: tên riêng thật (khu căn hộ, quán, công ty, tên người) có chữ trùng tên công cụ "
        "một từ (Sora, Night Cafe, Flux, Leonardo, Krea, Runway, Sea Art) làm ảnh thật thành ảnh "
        "AI, mất mã công trình/khu vực/trước-sau, và set() không cho sửa lại thành ảnh thật"
    ),
)
@pytest.mark.parametrize(
    "name",
    [
        "Sora Gardens",  # tên khu căn hộ
        "Quán Night Cafe",
        "Flux Coffee",
        "Nhà anh Leonardo",
        "Nhà anh Krea",
        "Shop Runway",
        "Quán Sea Art",
    ],
)
def test_sl_t070_4_real_proper_names_are_not_ai(name):
    tags = tags_for_folder(f"CT015 - {name} - Q7/truoc").tags
    assert not tags.is_ai
    assert (tags.project_code, tags.area, tags.phase) == ("CT015", "Quận 7", "truoc")


@pytest.mark.xfail(
    strict=True,
    reason=(
        "SL-T070-5: cụm tiếng Việt 'mô phỏng' (ảnh mô phỏng, hình mô phỏng 3D: ảnh dựng, không "
        "phải ảnh chụp công trình) không nhận là ảnh AI, ảnh giữ mã công trình/khu vực thật"
    ),
)
@pytest.mark.parametrize("ai_dir", ["Ảnh mô phỏng", "Hình mô phỏng 3D", "mo phong"])
def test_sl_t070_5_simulated_image_phrase_is_ai(ai_dir):
    assert tags_of(f"{BASE}/{ai_dir}/x.png") == AI_ONLY
