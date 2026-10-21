"""Nháp lưu ảnh đã chọn cho chỗ cần ảnh (T-055): ``seo_app/storage/drafts.py``.

Mọi test dùng thư mục tạm, ảnh giả (vài byte, không phải ảnh thật) và không gọi mạng. Junction
chạy thật trên Windows; symlink chạy trên Mac/Linux.
"""

from __future__ import annotations

import json
import os
import sqlite3
import unicodedata
from pathlib import Path
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from seo_app.content import OutlineItem
from seo_app.images.alt import AI_ALT_PREFIX, AI_CAPTION_PREFIX
from seo_app.images.folders import (
    ImageEntry,
    ImageFolderError,
    ImageLibrary,
    ImageRef,
    SubFolder,
)
from seo_app.images.tags import SOURCE_AI, SOURCE_REAL, ImageTags, tags_for_image
from seo_app.storage import drafts
from seo_app.storage.drafts import (
    MAX_ALT_CHARS,
    MAX_CAPTION_CHARS,
    MAX_PROMPT_CHARS,
    MAX_ROOT_INDEX,
    SCHEMA_VERSION,
    CheckedImage,
    DraftError,
    DraftImage,
    DraftPart,
    DraftSnapshot,
    DraftStore,
    check_chosen_image,
    check_draft_images,
    clean_loaded,
    new_draft_id,
)
from seo_app.storage.image_tags import ImageTagStore, ImageTagStoreError

IS_WINDOWS = os.name == "nt"
windows_only = pytest.mark.skipif(not IS_WINDOWS, reason="junction chỉ có trên Windows")
posix_only = pytest.mark.skipif(IS_WINDOWS, reason="symlink thử trên Mac/Linux")

PROJECT = "CT012 - Cổng inox - Tân Phú"
REAL_PATH = f"{PROJECT}/truoc/IMG_0001.jpg"
AFTER_PATH = f"{PROJECT}/sau/IMG_0002.jpg"
AI_FOLDER_PATH = "Ảnh AI/cong-minh-hoa.png"
AI_FILE_PATH = f"{PROJECT}/Gemini_Generated_Image_abc.png"
USB_PATH = "kho/IMG_0100.jpg"
FAKE_JPEG = b"\xff\xd8\xff fake jpeg"
IMAGE_KEYS = {
    "source",
    "root_index",
    "rel_path",
    "category",
    "alt",
    "alt_approved",
    "caption",
    "prompt",
}


# ----- tiện ích ----------------------------------------------------------------------------


def write(path: Path, data: bytes = FAKE_JPEG) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


@pytest.fixture
def roots(tmp_path: Path) -> tuple[Path, Path]:
    """Hai thư mục gốc: "Drive" (công trình, thư mục ảnh AI) và "USB" (ảnh chưa có thẻ)."""
    drive = tmp_path / "may" / "Drive"
    usb = tmp_path / "may" / "USB"
    write(drive / REAL_PATH)
    write(drive / AFTER_PATH, FAKE_JPEG * 2)
    write(drive / AI_FOLDER_PATH, b"\x89PNG fake")
    write(drive / AI_FILE_PATH, b"\x89PNG fake")
    write(usb / USB_PATH)
    return drive, usb


@pytest.fixture
def library(roots) -> ImageLibrary:
    return ImageLibrary(roots)


@pytest.fixture
def store(tmp_path: Path) -> DraftStore:
    return DraftStore(path=tmp_path / "data" / "drafts.sqlite")


@pytest.fixture
def tag_store(tmp_path: Path) -> ImageTagStore:
    return ImageTagStore(path=tmp_path / "data" / "image_tags.sqlite")


def real_image(**changes) -> DraftImage:
    data = dict(
        source=SOURCE_REAL,
        root_index=0,
        rel_path=REAL_PATH,
        category="Cổng inox",
        alt="Bản lề cổng inox bị gỉ trước khi sửa",
        alt_approved=True,
        caption="Bản lề gỉ sau 3 năm mưa nắng",
    )
    data.update(changes)
    return DraftImage(**data)


def generated_image(**changes) -> DraftImage:
    data = dict(
        source=SOURCE_AI,
        category="Cổng inox",
        prompt="Cổng inox hai cánh trước một nhà phố,\nánh sáng buổi sáng, ảnh chụp thực tế",
        alt="Minh họa cổng inox hai cánh",
        alt_approved=True,
        caption="Ảnh minh họa (AI): cổng inox hai cánh",
    )
    data.update(changes)
    return DraftImage(**data)


def snapshot_with(*images: DraftImage | None) -> DraftSnapshot:
    """Nháp có phần mở bài (không cần ảnh) và mỗi ảnh một phần."""
    parts = [DraftPart(heading="Mở bài", versions=["Cổng kêu ken két mỗi sáng."])]
    for number, image in enumerate(images, start=1):
        parts.append(
            DraftPart(
                heading=f"Mục {number}",
                versions=[f"Thân mục {number}, bản 1.", f"Thân mục {number}, bản 2."],
                current=1,
                image=f"ảnh cho mục {number}",
                chosen_image=image,
            )
        )
    return DraftSnapshot(
        step=2,
        keyword="sửa cổng inox",
        material={"Kinh nghiệm của xưởng": "Bản lề gỉ sau 3 năm."},
        outline_title="Sửa cổng inox tại nhà",
        outline=[OutlineItem(heading="Mục 1", points=["bản lề"], image="ảnh cho mục 1")],
        article_title="Sửa cổng inox tại nhà",
        parts=parts,
    )


def read_row(store: DraftStore, draft_id: str) -> str:
    with sqlite3.connect(store.path) as conn:
        (data,) = conn.execute("SELECT data FROM drafts WHERE id = ?", (draft_id,)).fetchone()
    return data


def write_row(store: DraftStore, draft_id: str, data: dict | str) -> None:
    text = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)
    with sqlite3.connect(store.path) as conn:
        conn.execute("UPDATE drafts SET data = ? WHERE id = ?", (text, draft_id))
    conn.close()


def text_only(snapshot: DraftSnapshot) -> dict:
    """Mọi thứ trừ ảnh đã chọn (để so phần chữ của bài)."""
    data = snapshot.model_dump(exclude={"saved_at"})
    for part in data["parts"]:
        part.pop("chosen_image")
    return data


def save_with_raw_image(store: DraftStore, raw_image: object) -> tuple[DraftSnapshot, str]:
    """Lưu nháp hai ảnh hợp lệ rồi sửa tay ảnh ở phần 1 thành ``raw_image``."""
    saved = store.save(snapshot_with(real_image(), generated_image()))
    obj = json.loads(read_row(store, saved.id))
    obj["parts"][1]["chosen_image"] = raw_image
    write_row(store, saved.id, obj)
    return saved, saved.id


# ----- lưu và mở lại -------------------------------------------------------------------------


def test_round_trip_keeps_every_image_field(store):
    snap = snapshot_with(real_image(), generated_image(), None)
    saved = store.save(snap)
    loaded = store.load(saved.id)
    assert loaded.schema_version == SCHEMA_VERSION == 2
    assert loaded.dropped_images == 0
    assert loaded.parts[0].chosen_image is None
    assert loaded.parts[1].chosen_image == real_image()
    assert loaded.parts[2].chosen_image == generated_image()
    assert loaded.parts[3].chosen_image is None
    assert text_only(loaded) == text_only(saved)


def test_saved_json_has_only_index_and_relative_path(store, roots, tmp_path):
    saved = store.save(snapshot_with(real_image(), real_image(root_index=1, rel_path=USB_PATH)))
    raw = read_row(store, saved.id)
    for folder in (tmp_path, *roots):
        for form in (str(folder), folder.as_posix(), json.dumps(str(folder))[1:-1]):
            assert form not in raw
    stored = json.loads(raw)
    images = [part["chosen_image"] for part in stored["parts"] if part["chosen_image"]]
    assert [set(image) for image in images] == [IMAGE_KEYS, IMAGE_KEYS]
    assert [(image["root_index"], image["rel_path"]) for image in images] == [
        (0, REAL_PATH),
        (1, USB_PATH),
    ]
    assert stored["schema_version"] == 2


NASTY_TEXT = (
    "Cổng <b>inox</b> <script>alert(1)</script> [bấm đây](https://evil.example) www.evil.vn "
    "a@b.vn\nxuống dòng\x00\u202egpj.exe\u200b"
)


def test_save_load_save_is_stable(store):
    """Bộ lọc chạy lại không đổi gì: mở rồi lưu lại cho đúng JSON cũ (trừ giờ lưu). Ảnh AI mà alt
    thiếu tiền tố thì lần mở đầu thêm tiền tố (SL-T055-2, test riêng ở dưới); ở đây alt đã có."""
    image = real_image(alt=NASTY_TEXT, caption=NASTY_TEXT, prompt=NASTY_TEXT)
    generated = generated_image(alt=f"{AI_ALT_PREFIX} {NASTY_TEXT}", prompt=NASTY_TEXT)
    first = store.save(snapshot_with(image, generated))
    raw_first = json.loads(read_row(store, first.id))
    second = store.save(store.load(first.id))
    raw_second = json.loads(read_row(store, second.id))
    raw_first.pop("saved_at")
    raw_second.pop("saved_at")
    assert raw_first == raw_second


def test_clean_loaded_keeps_images_and_dropped_count(store):
    saved, draft_id = save_with_raw_image(store, {"root_index": -1})
    loaded = store.load(draft_id)
    assert loaded.dropped_images == 1
    again = clean_loaded(loaded)
    assert again.dropped_images == 1
    assert again.parts[2].chosen_image == loaded.parts[2].chosen_image == generated_image()


def test_new_snapshot_has_no_dropped_images():
    assert DraftSnapshot().dropped_images == 0
    assert snapshot_with(real_image()).dropped_images == 0


# ----- F1: chỉ số gốc + đường dẫn tương đối --------------------------------------------------


BAD_REL_PATHS = [
    "../IMG_0001.jpg",
    f"{PROJECT}/../../ngoai.jpg",
    f"{PROJECT}/./truoc/IMG_0001.jpg",
    "C:/Users/chu/Pictures/a.jpg",
    "C:a.jpg",
    "/etc/a.jpg",
    "//may-chu/chia-se/a.jpg",
    "\\\\may-chu\\chia-se\\a.jpg",
    "truoc\\IMG_0001.jpg",
    f"{PROJECT}/truoc/IMG_0001.txt",
    f"{PROJECT}/truoc/",
    ".an/IMG.jpg",
    "CON.jpg",
    "a\x00.jpg",
    "a\u202egpj.jpg",
    "x" * 2000 + ".jpg",
]


@pytest.mark.parametrize("rel_path", BAD_REL_PATHS)
def test_bad_relative_paths_are_rejected_when_created(rel_path):
    with pytest.raises(ValidationError):
        real_image(rel_path=rel_path)
    with pytest.raises(ValidationError):
        DraftPart(heading="h", versions=["a"], chosen_image={"root_index": 0, "rel_path": rel_path})


def test_absolute_path_of_real_file_is_rejected(roots):
    with pytest.raises(ValidationError):
        real_image(rel_path=str(roots[0] / REAL_PATH))
    with pytest.raises(ValidationError):
        real_image(rel_path=(roots[0] / REAL_PATH).as_posix())


@pytest.mark.parametrize("root_index", [-1, True, "0", 1.5, 10**30, MAX_ROOT_INDEX + 1])
def test_bad_root_index_is_rejected_when_created(root_index):
    with pytest.raises(ValidationError):
        real_image(root_index=root_index)


def test_path_without_root_index_is_rejected():
    with pytest.raises(ValidationError):
        DraftImage(source=SOURCE_REAL, rel_path=REAL_PATH)


def test_ref_is_rebuilt_image_ref():
    assert real_image().ref == ImageRef(0, REAL_PATH)
    assert generated_image().ref is None
    assert generated_image().is_generated and not real_image().is_generated


def test_image_broken_after_creation_is_caught(store):
    """Đối tượng ảnh bị sửa sau khi tạo (``model_copy``, gán thẳng; không kiểm): gắn vào phần thì
    bị kiểm lại ngay; gán thẳng vào phần thì ``save`` kiểm lại, không lưu bừa."""
    bad = real_image().model_copy(update={"rel_path": "../../ngoai.jpg"})
    with pytest.raises(ValidationError):
        DraftPart(heading="h", versions=["a"], chosen_image=bad)
    snap = snapshot_with(real_image())
    snap.parts[1].chosen_image = bad
    with pytest.raises(DraftError, match="sai khuôn"):
        store.save(snap)


# ----- nháp hỏng phần ảnh không làm mất phần chữ ------------------------------------------


BROKEN_IMAGES = [
    {"source": "that", "root_index": -1, "rel_path": REAL_PATH},
    {"source": "that", "root_index": "0", "rel_path": REAL_PATH},
    {"source": "that", "root_index": True, "rel_path": REAL_PATH},
    {"source": "that", "root_index": 1.5, "rel_path": REAL_PATH},
    {"source": "that", "root_index": 10**30, "rel_path": REAL_PATH},
    {"source": "that", "root_index": MAX_ROOT_INDEX + 1, "rel_path": REAL_PATH},
    {"source": "that", "root_index": 0, "rel_path": "../../bi-mat.jpg"},
    {"source": "that", "root_index": 0, "rel_path": "C:/Windows/win.ini"},
    {"source": "that", "root_index": 0, "rel_path": "\\\\may-chu\\a.jpg"},
    {"source": "that", "root_index": 0, "rel_path": "ghi-chu.txt"},
    {"source": "that", "root_index": 0, "rel_path": ""},
    {"source": "that", "rel_path": REAL_PATH},  # thiếu số gốc
    {"source": "that", "root_index": 0, "rel_path": REAL_PATH, "abs_path": "C:/x.jpg"},
    {"source": "that", "root_index": 0, "rel_path": REAL_PATH, "alt": 123},
    {"source": "that", "root_index": 0, "rel_path": REAL_PATH, "alt_approved": "yes"},
    {"source": "that", "root_index": 0, "rel_path": REAL_PATH, "prompt": ["x"]},
    {"source": "that", "root_index": 0, "rel_path": ["a", "b.jpg"]},
    "C:/Users/chu/a.jpg",
    42,
    [0, REAL_PATH],
]


@pytest.mark.parametrize("raw_image", BROKEN_IMAGES)
def test_broken_image_is_dropped_and_text_kept(store, raw_image):
    saved, draft_id = save_with_raw_image(store, raw_image)
    loaded = store.load(draft_id)
    assert loaded.dropped_images == 1
    assert loaded.parts[1].chosen_image is None
    assert loaded.parts[2].chosen_image == generated_image()  # ảnh khác giữ nguyên
    assert text_only(loaded) == text_only(saved)


def test_every_image_broken_still_opens_with_all_text(store):
    saved = store.save(snapshot_with(real_image(), generated_image(), real_image()))
    obj = json.loads(read_row(store, saved.id))
    for part, bad in zip(obj["parts"][1:], BROKEN_IMAGES, strict=False):
        part["chosen_image"] = bad
    write_row(store, saved.id, obj)
    loaded = store.load(saved.id)
    assert loaded.dropped_images == 3
    assert all(part.chosen_image is None for part in loaded.parts)
    assert text_only(loaded) == text_only(saved)


def test_broken_text_outside_images_still_fails_whole_draft(store):
    """Chỉ phần ảnh được nương tay; phần chữ sai khuôn vẫn báo lỗi như trước (T-016)."""
    saved, draft_id = save_with_raw_image(store, {"root_index": -1})
    obj = json.loads(read_row(store, draft_id))
    obj["parts"][1]["current"] = 99
    write_row(store, draft_id, obj)
    with pytest.raises(DraftError, match="bị hỏng"):
        store.load(draft_id)


def test_strict_validation_without_file_context():
    """Không qua ``DraftStore.load`` (dữ liệu do code tạo): ảnh sai khuôn là lỗi, không lặng lẽ
    bỏ."""
    data = snapshot_with(real_image()).model_dump()
    data["parts"][1]["chosen_image"]["root_index"] = -1
    with pytest.raises(ValidationError):
        DraftSnapshot.model_validate(data)


# ----- nháp khuôn cũ --------------------------------------------------------------------------


def v1_draft(draft_id: str) -> dict:
    """Nháp đúng như bản T-016/T-021 lưu (khuôn 1, chưa có ảnh đã chọn)."""
    return {
        "schema_version": 1,
        "id": draft_id,
        "saved_at": "2026-10-19T09:15:00+07:00",
        "step": 2,
        "keyword": "sửa cổng inox",
        "material": {"Kinh nghiệm của xưởng": "Bản lề gỉ sau 3 năm."},
        "research": None,
        "research_keyword": "",
        "outline_title": "Sửa cổng inox tại nhà",
        "outline": [
            {"heading": "Dấu hiệu cổng hỏng", "points": ["bản lề kêu"], "image": "ảnh bản lề gỉ"}
        ],
        "article_title": "Sửa cổng inox tại nhà: khi nào cần thay bản lề",
        "parts": [
            {"heading": "Mở bài", "versions": ["Cổng kêu ken két."], "current": 0, "image": ""},
            {
                "heading": "Dấu hiệu cổng hỏng",
                "versions": ["Bản lề gỉ.", "Bản lề gỉ, cánh xệ."],
                "current": 1,
                "image": "ảnh bản lề gỉ",
            },
        ],
        "review": None,
        "auto_fixed": 0,
        "ignored_flags": ["Bản lề gỉ."],
    }


def put_v1(store: DraftStore, data: dict) -> None:
    store.save(DraftSnapshot(id=data["id"], keyword="tạm"))  # tạo bảng và dòng
    write_row(store, data["id"], data)


def test_v1_draft_still_opens_and_is_upgraded(store):
    data = v1_draft(new_draft_id())
    put_v1(store, data)
    loaded = store.load(data["id"])
    assert loaded.schema_version == SCHEMA_VERSION
    assert loaded.dropped_images == 0
    assert loaded.article_title == data["article_title"]
    assert [part.text for part in loaded.parts] == ["Cổng kêu ken két.", "Bản lề gỉ, cánh xệ."]
    assert [part.image for part in loaded.parts] == ["", "ảnh bản lề gỉ"]
    assert all(part.chosen_image is None for part in loaded.parts)
    assert loaded.ignored_flags == ["Bản lề gỉ."]
    # Lưu lại thì ghi khuôn mới.
    store.save(loaded)
    assert json.loads(read_row(store, data["id"]))["schema_version"] == SCHEMA_VERSION


def test_v1_draft_with_image_data_drops_only_the_image(store):
    """Khuôn 1 không có ảnh: dữ liệu ảnh trong nháp khuôn 1 là sửa tay, bỏ ảnh, giữ chữ."""
    data = v1_draft(new_draft_id())
    data["parts"][1]["chosen_image"] = real_image().model_dump()
    put_v1(store, data)
    loaded = store.load(data["id"])
    assert loaded.dropped_images == 1
    assert loaded.parts[1].chosen_image is None
    assert loaded.parts[1].text == "Bản lề gỉ, cánh xệ."


def test_v1_draft_counts_only_real_image_data_as_dropped(store):
    """SL-T055-3: ``"chosen_image": null`` trong nháp khuôn 1 là "chưa chọn ảnh", không mất ảnh nào
    nên không đếm; dữ liệu ảnh thật sự (dù hỏng) thì vẫn đếm."""
    data = v1_draft(new_draft_id())
    data["parts"][0]["chosen_image"] = None
    data["parts"][1]["chosen_image"] = None
    put_v1(store, data)
    assert store.load(data["id"]).dropped_images == 0
    data["parts"][1]["chosen_image"] = {"rel_path": "../x.jpg"}
    put_v1(store, data)
    loaded = store.load(data["id"])
    assert loaded.dropped_images == 1
    assert all(part.chosen_image is None for part in loaded.parts)


@pytest.mark.parametrize("version", [0, 3, 999, -1, "abc", None, [2]])
def test_unknown_schema_versions_are_rejected(store, version):
    saved = store.save(snapshot_with(real_image()))
    obj = json.loads(read_row(store, saved.id))
    obj["schema_version"] = version
    write_row(store, saved.id, obj)
    with pytest.raises(DraftError, match="bị hỏng"):
        store.load(saved.id)


def test_constructing_old_version_upgrades():
    assert DraftSnapshot(schema_version=1).schema_version == SCHEMA_VERSION
    with pytest.raises(ValidationError):
        DraftSnapshot(schema_version=3)


# ----- kiểm lại trên máy: ImageRef dựng lại + stat_image -------------------------------------


def test_check_rebuilds_ref_and_asks_the_library(store, library, roots):
    saved = store.save(snapshot_with(real_image(), generated_image()))
    checked = check_draft_images(store.load(saved.id), library)
    assert set(checked) == {1, 2}
    real = checked[1]
    assert isinstance(real, CheckedImage)
    assert real.ref == ImageRef(0, REAL_PATH)
    assert real.available and real.message == ""
    assert isinstance(real.entry, ImageEntry)
    assert real.entry.size == len(FAKE_JPEG)
    assert not real.is_generated and not real.is_ai
    generated = checked[2]
    assert generated.is_generated and not generated.available
    assert generated.ref is None and generated.entry is None and generated.message == ""
    assert generated.tags == ImageTags(source=SOURCE_AI, category="Cổng inox")


def test_check_goes_through_stat_image(store, library, monkeypatch):
    calls = []
    original = ImageLibrary.stat_image

    def spy(self, ref):
        calls.append(ref)
        return original(self, ref)

    monkeypatch.setattr(ImageLibrary, "stat_image", spy)
    saved = store.save(snapshot_with(real_image(), real_image(root_index=1, rel_path=USB_PATH)))
    check_draft_images(store.load(saved.id), library)
    assert calls == [ImageRef(0, REAL_PATH), ImageRef(1, USB_PATH)]
    assert all(type(ref) is ImageRef for ref in calls)


@pytest.mark.parametrize("root_index", [2, 7, MAX_ROOT_INDEX])
def test_root_index_out_of_range_is_kept_but_unavailable(store, library, tag_store, root_index):
    """Số gốc trong khoảng cho phép nhưng chưa khai báo (bớt một thư mục khỏi IMAGE_FOLDERS): giữ
    lựa chọn trong nháp, báo không dùng được; không tin số gốc."""
    saved = store.save(snapshot_with(real_image(root_index=root_index)))
    loaded = store.load(saved.id)
    assert loaded.dropped_images == 0
    result = check_draft_images(loaded, library, tag_store=tag_store)[1]
    assert not result.available
    assert result.message == "Không có thư mục ảnh với số thứ tự này."


def test_missing_file_comes_back_when_restored(store, library, roots):
    saved = store.save(snapshot_with(real_image()))
    loaded = store.load(saved.id)
    image_file = roots[0] / REAL_PATH
    image_file.rename(image_file.with_name("tam.jpg"))
    gone = check_draft_images(loaded, library)[1]
    assert not gone.available and "Không tìm thấy ảnh" in gone.message
    # Nháp vẫn giữ lựa chọn; trả file về chỗ cũ thì dùng lại được.
    assert store.load(saved.id).parts[1].chosen_image == real_image()
    image_file.with_name("tam.jpg").rename(image_file)
    assert check_draft_images(loaded, library)[1].available


def test_unplugged_root_is_unavailable_without_absolute_path(store, roots, tmp_path):
    saved = store.save(snapshot_with(real_image(root_index=1, rel_path=USB_PATH)))
    roots[1].rename(roots[1].with_name("USB-da-rut"))
    result = check_draft_images(store.load(saved.id), ImageLibrary(roots))[1]
    assert not result.available
    assert "Chưa thấy thư mục ảnh số 2" in result.message
    assert str(tmp_path) not in result.message and tmp_path.as_posix() not in result.message


def test_too_large_file_is_unavailable(store, roots):
    saved = store.save(snapshot_with(real_image()))
    small_library = ImageLibrary(roots, max_file_bytes=4)
    result = check_draft_images(store.load(saved.id), small_library)[1]
    assert not result.available and "quá lớn" in result.message


def forbid(monkeypatch, *names: str) -> None:
    def forbidden(*args, **kwargs):
        raise AssertionError("không được quét thư mục hay đọc file ở đây")

    for name in names:
        monkeypatch.setattr(ImageLibrary, name, forbidden)


def spy_list_folder(monkeypatch) -> list[tuple]:
    calls: list[tuple] = []
    original = ImageLibrary.list_folder

    def spy(self, root_index, rel_dir="", **kwargs):
        calls.append((root_index, rel_dir, kwargs.get("recursive", False)))
        return original(self, root_index, rel_dir, **kwargs)

    monkeypatch.setattr(ImageLibrary, "list_folder", spy)
    return calls


def test_check_reads_no_file_and_lists_only_folders_on_the_path(store, library, monkeypatch):
    """Không mở file ảnh nào (Drive "chỉ trực tuyến" không bị tải về). Để thẻ theo đúng tên thư
    mục trên ổ (SL-T055-1) chỉ xem tên các thư mục trên đường tới ảnh nháp ghi là ảnh thật: không
    đệ quy, mỗi thư mục một lần cho cả nháp. Ảnh nháp ghi AI, gốc AI: không cần xem."""
    forbid(monkeypatch, "read_image_bytes")
    calls = spy_list_folder(monkeypatch)
    images = (
        real_image(),
        real_image(rel_path=AFTER_PATH),
        generated_image(),
        real_image(source=SOURCE_AI, root_index=1, rel_path=USB_PATH),
    )
    saved = store.save(snapshot_with(*images))
    loaded = store.load(saved.id)
    checked = check_draft_images(loaded, library)
    assert all(checked[i].available for i in (1, 2, 4))
    assert calls == [(0, "", False), (0, PROJECT, False)]
    calls.clear()
    assert check_draft_images(loaded, library, ai_roots={0})[1].is_ai
    assert calls == []


def test_scanned_images_need_no_folder_listing(store, library, monkeypatch):
    listing = library.list_folder(0, PROJECT, recursive=True)
    forbid(monkeypatch, "list_folder", "read_image_bytes")
    saved = store.save(snapshot_with(real_image(), real_image(rel_path=AFTER_PATH)))
    checked = check_draft_images(store.load(saved.id), library, scanned=listing.images)
    assert checked[1].available and checked[2].available


def make_junction(link: Path, target: Path) -> None:
    import _winapi

    _winapi.CreateJunction(str(target), str(link))
    assert link.is_junction()


@windows_only
def test_image_through_junction_is_unavailable(store, roots, tmp_path):
    outside = tmp_path / "ngoai"
    write(outside / "bi-mat.jpg")
    make_junction(roots[0] / "lien-ket", outside)
    saved = store.save(snapshot_with(real_image(rel_path="lien-ket/bi-mat.jpg")))
    result = check_draft_images(store.load(saved.id), ImageLibrary(roots))[1]
    assert not result.available
    assert "liên kết" in result.message
    assert str(outside) not in result.message


@posix_only
def test_image_through_symlink_is_unavailable(store, roots, tmp_path):
    outside = tmp_path / "ngoai"
    write(outside / "bi-mat.jpg")
    (roots[0] / "lien-ket").symlink_to(outside, target_is_directory=True)
    saved = store.save(snapshot_with(real_image(rel_path="lien-ket/bi-mat.jpg")))
    result = check_draft_images(store.load(saved.id), ImageLibrary(roots))[1]
    assert not result.available
    assert "liên kết" in result.message


def test_check_reruns_validation_on_changed_object(library):
    bad = real_image().model_copy(update={"rel_path": "../../ngoai.jpg"})
    with pytest.raises(ValidationError):
        check_chosen_image(bad, library)


def test_check_needs_the_right_types(library):
    with pytest.raises(TypeError):
        check_draft_images({"parts": []}, library)
    with pytest.raises(TypeError):
        check_chosen_image(real_image(), [Path("C:/")])
    with pytest.raises(TypeError):
        check_chosen_image({"root_index": 0, "rel_path": REAL_PATH}, library)


# ----- khóa theo ImageRef của kết quả quét ---------------------------------------------------


def variant_case(rel_path: str) -> str:
    return rel_path.upper()


def test_scanned_ref_becomes_the_key(store, library, roots):
    listing = library.list_folder(0, f"{PROJECT}/truoc")
    scanned = listing.images[0].ref
    assert scanned == ImageRef(0, REAL_PATH)
    other_case = variant_case(REAL_PATH)
    saved = store.save(snapshot_with(real_image(rel_path=other_case)))
    loaded = store.load(saved.id)

    with_scan = check_draft_images(loaded, library, scanned=listing.images)[1]
    assert with_scan.ref == scanned  # đúng ImageRef của kết quả quét, không phải chữ trong nháp
    assert with_scan.available  # stat_image chạy trên ImageRef của kết quả quét

    without_scan = check_draft_images(loaded, library)[1]
    case_insensitive = (roots[0] / other_case).exists()
    assert without_scan.available == case_insensitive
    if case_insensitive:
        # Chưa quét: tên thư mục lấy đúng như trên ổ (SL-T055-1), tên file giữ như nháp (tên file
        # không đổi thẻ). Thẻ theo tên thư mục thật.
        real_dirs = ImageRef(0, f"{PROJECT}/truoc/{other_case.rsplit('/', 1)[1]}")
        assert without_scan.ref == real_dirs and without_scan.entry.ref == real_dirs
        assert without_scan.tags.project_code == "CT012" and not without_scan.is_ai
    else:
        assert without_scan.ref == ImageRef(0, other_case)


def test_scanned_refs_match_other_unicode_form(store, library):
    nfd = unicodedata.normalize("NFD", REAL_PATH)
    assert nfd != REAL_PATH
    saved = store.save(snapshot_with(real_image(rel_path=nfd)))
    result = check_draft_images(store.load(saved.id), library, scanned=[ImageRef(0, REAL_PATH)])[1]
    assert result.ref == ImageRef(0, REAL_PATH)
    assert result.available


def test_scanned_ref_of_other_root_is_not_used(store, library):
    saved = store.save(snapshot_with(real_image()))
    result = check_draft_images(store.load(saved.id), library, scanned=[ImageRef(1, REAL_PATH)])[1]
    assert result.ref == ImageRef(0, REAL_PATH)


def test_scanned_junk_is_ignored(store, library):
    saved = store.save(snapshot_with(real_image()))
    junk = [None, "C:/a.jpg", REAL_PATH, (0, REAL_PATH), 42]
    result = check_draft_images(store.load(saved.id), library, scanned=junk)[1]
    assert result.ref == ImageRef(0, REAL_PATH) and result.available


def test_from_library_takes_scan_ref_and_tags(library, tag_store):
    entry = library.list_folder(0, f"{PROJECT}/truoc").images[0]
    tags = tag_store.resolve(entry.ref).tags
    image = DraftImage.from_library(entry, tags, alt="Bản lề gỉ", alt_approved=True)
    assert (image.root_index, image.rel_path) == (entry.ref.root_index, entry.ref.rel_path)
    assert image.source == SOURCE_REAL and image.category == "Cổng inox"
    assert image.alt == "Bản lề gỉ" and image.alt_approved
    assert DraftImage.from_library(entry.ref, tags) == DraftImage.from_library(entry, tags)
    ai_entry = library.list_folder(0, "Ảnh AI").images[0]
    ai = DraftImage.from_library(ai_entry, tag_store.resolve(ai_entry.ref).tags)
    assert ai.source == SOURCE_AI


@pytest.mark.parametrize("bad", ["C:/a.jpg", Path("a.jpg"), (0, REAL_PATH), None])
def test_from_library_rejects_non_refs(bad):
    with pytest.raises(TypeError):
        DraftImage.from_library(bad, ImageTags())
    with pytest.raises(TypeError):
        DraftImage.from_library(ImageRef(0, REAL_PATH), {"source": "that"})


# ----- nguồn ảnh theo hướng an toàn ----------------------------------------------------------


def check_one(store, library, image, **kwargs) -> CheckedImage:
    saved = store.save(snapshot_with(image))
    return check_draft_images(store.load(saved.id), library, **kwargs)[1]


def assert_ai_without_project(tags: ImageTags) -> None:
    assert tags.is_ai
    assert (tags.project_code, tags.area, tags.phase) == ("", "", "")


def test_real_draft_in_real_folder_uses_current_tags(store, library, tag_store):
    result = check_one(store, library, real_image(), tag_store=tag_store)
    assert result.tags == ImageTags(
        source=SOURCE_REAL,
        project_code="CT012",
        category="Cổng inox",
        area="Tân Phú",
        phase="truoc",
    )
    assert result.tag_error == ""


def test_draft_says_ai_wins_over_real_folder(store, library, tag_store):
    result = check_one(store, library, real_image(source=SOURCE_AI), tag_store=tag_store)
    assert_ai_without_project(result.tags)
    assert result.tags.category == "Cổng inox"


def test_draft_says_ai_wins_over_manual_real_tag(store, library, tag_store):
    tag_store.set(ImageRef(0, REAL_PATH), ImageTags(source=SOURCE_REAL, project_code="CT012"))
    result = check_one(store, library, real_image(source=SOURCE_AI), tag_store=tag_store)
    assert_ai_without_project(result.tags)


@pytest.mark.parametrize("rel_path", [AI_FOLDER_PATH, AI_FILE_PATH])
def test_ai_folder_or_file_wins_over_draft_real(store, library, tag_store, rel_path):
    result = check_one(store, library, real_image(rel_path=rel_path), tag_store=tag_store)
    assert result.available
    assert_ai_without_project(result.tags)


def test_ai_folder_wins_without_tag_store(store, library):
    assert_ai_without_project(check_one(store, library, real_image(rel_path=AI_FOLDER_PATH)).tags)


def test_manual_ai_tag_wins_over_draft_real(store, library, tag_store):
    tag_store.set(ImageRef(0, REAL_PATH), ImageTags(source=SOURCE_AI, category="Cổng inox"))
    result = check_one(store, library, real_image(), tag_store=tag_store)
    assert_ai_without_project(result.tags)


def test_ai_root_wins_over_draft_real(store, library):
    result = check_one(store, library, real_image(), ai_roots={0})
    assert_ai_without_project(result.tags)
    not_this_root = check_one(store, library, real_image(), ai_roots={1, "0", None})
    assert not not_this_root.tags.is_ai


@pytest.mark.parametrize(
    "source", ["AI", "real", "That", "THAT", "", " that", None, 1, True, ["that"]]
)
def test_unknown_source_values_read_as_ai(store, library, source):
    saved, draft_id = save_with_raw_image(store, {**real_image().model_dump(), "source": source})
    loaded = store.load(draft_id)
    assert loaded.dropped_images == 0
    assert loaded.parts[1].chosen_image.source == SOURCE_AI
    assert_ai_without_project(check_draft_images(loaded, library)[1].tags)


def test_missing_source_reads_as_ai(store):
    raw = real_image().model_dump()
    del raw["source"]
    saved, draft_id = save_with_raw_image(store, raw)
    assert store.load(draft_id).parts[1].chosen_image.source == SOURCE_AI


@pytest.mark.parametrize("source", [SOURCE_REAL, SOURCE_AI, "khác"])
def test_generated_image_is_always_ai(source):
    image = DraftImage(source=source, prompt="cổng inox", category="Cổng inox")
    assert image.source == SOURCE_AI
    assert image.is_generated


def test_generated_image_tags_are_ai_only(library):
    result = check_chosen_image(generated_image(), library)
    assert result.tags == ImageTags(source=SOURCE_AI, category="Cổng inox")
    result = check_chosen_image(generated_image(category=""), library)
    assert result.tags == ImageTags(source=SOURCE_AI)


def test_draft_cannot_add_or_change_tags_of_real_image(store, library, tag_store):
    # Hạng mục ghi trong nháp không đè thẻ hiện tại, cũng không thêm thẻ cho ảnh chưa có thẻ.
    result = check_one(store, library, real_image(category="Cửa cuốn"), tag_store=tag_store)
    assert result.tags.category == "Cổng inox"
    usb = real_image(root_index=1, rel_path=USB_PATH, category="Cửa cuốn")
    result = check_one(store, library, usb, tag_store=tag_store)
    assert result.tags == ImageTags(source=SOURCE_REAL)


def test_ai_tags_fall_back_to_draft_category(store, library):
    """Ảnh USB chưa có thẻ, nháp ghi ảnh AI và hạng mục: dùng hạng mục của nháp (đã kiểm)."""
    usb = real_image(source=SOURCE_AI, root_index=1, rel_path=USB_PATH, category="Cửa cuốn")
    result = check_one(store, library, usb)
    assert result.tags == ImageTags(source=SOURCE_AI, category="Cửa cuốn")


def test_tag_store_error_falls_back_to_folder_tags(store, library, tag_store, monkeypatch):
    def broken(self, refs):
        raise ImageTagStoreError("File thẻ ảnh bị lỗi.")

    monkeypatch.setattr(ImageTagStore, "get_many", broken)
    result = check_one(store, library, real_image(), tag_store=tag_store)
    assert result.tag_error == "File thẻ ảnh bị lỗi."
    assert result.tags.project_code == "CT012"
    assert check_one(store, library, real_image(source=SOURCE_AI), tag_store=tag_store).is_ai


def test_tag_store_is_read_once_per_draft(store, library, tag_store, monkeypatch):
    calls = []
    original = ImageTagStore.resolve_many

    def spy(self, refs):
        refs = list(refs)
        calls.append(refs)
        return original(self, refs)

    monkeypatch.setattr(ImageTagStore, "resolve_many", spy)
    images = (real_image(), real_image(rel_path=AFTER_PATH), generated_image())
    saved = store.save(snapshot_with(*images))
    checked = check_draft_images(store.load(saved.id), library, tag_store=tag_store)
    assert len(calls) == 1 and len(calls[0]) == 2
    assert checked[2].tags.phase == "sau"


def test_same_image_in_two_parts(store, library, tag_store):
    saved = store.save(snapshot_with(real_image(), real_image(source=SOURCE_AI)))
    checked = check_draft_images(store.load(saved.id), library, tag_store=tag_store)
    assert not checked[1].is_ai and checked[2].is_ai
    assert checked[1].ref == checked[2].ref


# ----- thẻ theo tên thư mục thật trên ổ, không theo chữ hoa thường trong nháp (SL-T055-1) -------


# "CongAI": thư mục ảnh AI chỉ nhờ tách chữ hoa ("Cong AI", T-052); "congai", "CONGAI" thì không.
# Không dùng "GenAI": từ T-070 "genai" viết kiểu nào cũng là ảnh AI (LC-T055-4).
CAMEL_AI_PATH = f"{PROJECT}/CongAI/cong.png"


def assert_ai_only_by_case(ai_path: str, other_case: str) -> None:
    """Điều kiện đầu (LC-T055-4): ``ai_path`` là ảnh AI chỉ nhờ chữ hoa, cùng tên viết hoa thường
    khác (``other_case``) thì không, nên thẻ phải theo đúng tên trên ổ thì test mới qua. Đổi cách
    nhận tên ảnh AI làm mất điều này thì test hỏng ở đây, không qua oan."""
    assert tags_for_image(ImageRef(0, ai_path)).tags.is_ai
    assert not tags_for_image(ImageRef(0, other_case)).tags.is_ai


def case_insensitive_disk(folder: Path) -> bool:
    probe = folder / "Thu-Hoa-Thuong"
    probe.mkdir()
    try:
        return (folder / "thu-hoa-thuong").exists()
    finally:
        probe.rmdir()


@pytest.mark.parametrize("with_store", [False, True], ids=["khong-kho-the", "co-kho-the"])
def test_case_variant_of_ai_folder_reads_real_name_and_stays_ai(
    store, library, roots, tag_store, with_store
):
    variant = CAMEL_AI_PATH.replace("CongAI", "congai")
    assert_ai_only_by_case(CAMEL_AI_PATH, variant)
    write(roots[0] / CAMEL_AI_PATH, b"\x89PNG fake")
    if not case_insensitive_disk(roots[0]):
        pytest.skip("ổ phân biệt hoa thường: 'congai' là thư mục khác, không trỏ tới 'CongAI'")
    kwargs = {"tag_store": tag_store} if with_store else {}
    result = check_one(store, library, real_image(rel_path=variant), **kwargs)
    assert result.available
    assert result.ref == ImageRef(0, CAMEL_AI_PATH) and result.entry.ref == result.ref
    assert_ai_without_project(result.tags)
    assert result.image.alt.startswith(AI_ALT_PREFIX) and not result.image.alt_approved


class FakeDisk:
    """Giả ``ImageLibrary.stat_image``/``list_folder`` (chạy như nhau trên mọi máy): thư mục gốc có
    thư mục con ``names``; ``stat_image`` luôn thấy ảnh (như ổ không phân biệt hoa thường)."""

    def __init__(self, monkeypatch, names=(), error: str = "") -> None:
        self.names = names
        self.error = error
        self.calls = 0

        def stat_image(_library, ref):
            return ImageEntry(ref=ref, name=ref.name, size=10, modified=0.0)

        def list_folder(_library, root_index, rel_dir="", **kwargs):
            self.calls += 1
            if self.error:
                raise ImageFolderError(self.error)
            subfolders = tuple(SubFolder(rel_path=name, name=name) for name in self.names)
            return SimpleNamespace(subfolders=subfolders)

        monkeypatch.setattr(ImageLibrary, "stat_image", stat_image)
        monkeypatch.setattr(ImageLibrary, "list_folder", list_folder)


def test_exact_folder_name_wins_on_case_sensitive_disk(monkeypatch, library):
    """Ổ phân biệt hoa thường có cả "CongAI" lẫn "congai": nháp ghi "congai" là đúng thư mục
    "congai" (một thư mục khác, không phải thư mục ảnh AI)."""
    assert_ai_only_by_case("CongAI/cong.png", "congai/cong.png")
    FakeDisk(monkeypatch, names=("CongAI", "congai"))
    result = check_chosen_image(real_image(rel_path="congai/cong.png"), library)
    assert result.available and result.ref == ImageRef(0, "congai/cong.png")
    assert not result.is_ai


def test_single_case_insensitive_match_takes_real_name(monkeypatch, library):
    assert_ai_only_by_case("CongAI/cong.png", "congai/cong.png")
    FakeDisk(monkeypatch, names=("Ảnh khác", "CongAI"))
    result = check_chosen_image(real_image(rel_path="congai/cong.png"), library)
    assert result.available and result.ref == ImageRef(0, "CongAI/cong.png")
    assert result.is_ai


@pytest.mark.parametrize(
    "names",
    [(), ("CongAI", "CONGAI"), ("Ảnh khác",)],
    ids=["quet-chua-toi", "hai-ten-cung-khoa", "khong-thay"],
)
def test_unconfirmed_folder_name_is_unavailable(monkeypatch, library, store, tmp_path, names):
    """Không lấy được tên thật (thư mục quá nhiều mục hay quét quá giờ nên chưa thấy, hai tên chỉ
    khác hoa thường): ảnh không dùng được, không đoán theo chữ trong nháp; nháp vẫn giữ lựa chọn."""
    assert_ai_only_by_case("CongAI/cong.png", "congai/cong.png")  # đoán theo nháp là ra ảnh thật
    FakeDisk(monkeypatch, names=names)
    image = real_image(rel_path="congai/cong.png")
    saved = store.save(snapshot_with(image))
    result = check_draft_images(store.load(saved.id), library)[1]
    assert not result.available and result.entry is None
    assert "Chưa kiểm được tên thư mục" in result.message
    assert str(tmp_path) not in result.message
    assert store.load(saved.id).parts[1].chosen_image == image


def test_folder_listing_error_is_reported_once_per_folder(monkeypatch, library, store):
    disk = FakeDisk(monkeypatch, error="Không đọc được thư mục này (không có quyền).")
    images = (real_image(rel_path="a/x.jpg"), real_image(rel_path="a/y.jpg"))
    checked = check_draft_images(store.load(store.save(snapshot_with(*images)).id), library)
    assert [checked[i].message for i in (1, 2)] == [disk.error] * 2
    assert not checked[1].available and disk.calls == 1


def test_image_in_root_needs_no_folder_listing(monkeypatch, store, library, roots):
    write(roots[1] / "IMG_9.jpg")
    forbid(monkeypatch, "list_folder")
    result = check_one(store, library, real_image(root_index=1, rel_path="img_9.JPG"))
    assert result.available or not case_insensitive_disk(roots[1])


# ----- thẻ dựng lại qua ImageTags ------------------------------------------------------------


@pytest.mark.parametrize(
    ("category", "expected"),
    [
        ("Cổng inox", "Cổng inox"),
        ("Thay bánh xe cửa kéo", "Thay bánh xe cửa kéo"),
        ("cong INOX", ""),  # không đúng dạng chuẩn ImageTags trả về
        ("Nhà anh Tuấn 0909 123 456", ""),  # chữ tự do (có thể là thông tin khách): bỏ
        ("Cổng inox - 12 Lê Lợi", ""),
        ("<b>Cổng inox</b>", ""),
        ("x" * 10_000, ""),
        (123, ""),
        (None, ""),
        (["Cổng inox"], ""),
    ],
)
def test_category_is_rebuilt_through_image_tags(store, category, expected):
    raw = {**real_image().model_dump(), "category": category}
    saved, draft_id = save_with_raw_image(store, raw)
    loaded = store.load(draft_id)
    assert loaded.dropped_images == 0
    assert loaded.parts[1].chosen_image.category == expected


def test_draft_project_fields_are_not_stored():
    """Nháp chỉ lưu nguồn và hạng mục; mã công trình, khu vực, trước/sau luôn đọc lại lúc mở."""
    with pytest.raises(ValidationError):
        DraftImage(source=SOURCE_REAL, root_index=0, rel_path=REAL_PATH, project_code="CT012")
    with pytest.raises(ValidationError):
        DraftImage(source=SOURCE_REAL, root_index=0, rel_path=REAL_PATH, area="Tân Phú")


# ----- alt, chú thích, prompt là chữ chưa tin cậy --------------------------------------------


def test_alt_and_caption_are_cleaned_one_line():
    image = real_image(alt=NASTY_TEXT, caption=NASTY_TEXT)
    for text in (image.alt, image.caption):
        assert "\n" not in text and "\x00" not in text and "\u202e" not in text
        assert "<script" not in text and "<b>" not in text
        assert "](" not in text  # link Markdown đã bị vô hiệu
        assert "www.evil.vn" not in text  # địa chỉ trần bị chèn ký tự rộng 0 (T-031)
    assert image.alt.startswith("Cổng inox")


def test_text_limits():
    long_word = "cửa " * 2000
    image = real_image(alt=long_word, caption=long_word, prompt=long_word)
    assert 0 < len(image.alt) <= MAX_ALT_CHARS
    assert 0 < len(image.caption) <= MAX_CAPTION_CHARS
    assert 0 < len(image.prompt) <= MAX_PROMPT_CHARS
    assert len(real_image(prompt="a" * 1_000_000).prompt) == MAX_PROMPT_CHARS


def test_long_texts_in_file_are_cut_not_dropped(store):
    raw = {**real_image().model_dump(), "alt": "a " * 5000, "prompt": "p" * 50_000}
    saved, draft_id = save_with_raw_image(store, raw)
    loaded = store.load(draft_id)
    assert loaded.dropped_images == 0
    image = loaded.parts[1].chosen_image
    assert len(image.alt) <= MAX_ALT_CHARS and len(image.prompt) == MAX_PROMPT_CHARS


def test_prompt_keeps_lines_and_drops_hidden_characters():
    prompt = "  Dòng 1\r\nDòng 2\rDòng 3\tcột\x00\x07\u200b\u202e\ufeff\ud800  "
    assert DraftImage(prompt=prompt).prompt == "Dòng 1\nDòng 2\nDòng 3\tcột"


def test_prompt_is_kept_as_plain_text():
    """Prompt chỉ là chữ: không chạy, không diễn giải mẫu hay biểu thức."""
    prompt = "{{7*7}} ${HOME} __import__('os').system('x') <img src=x onerror=alert(1)>"
    assert DraftImage(prompt=prompt).prompt == prompt


@pytest.mark.parametrize("field", ["alt", "caption", "prompt"])
def test_lone_surrogate_is_dropped_so_saving_works(store, field):
    image = real_image(**{field: "trước\ud800sau"})
    value = getattr(image, field)
    assert "\ud800" not in value and "trước" in value
    saved = store.save(snapshot_with(image))  # không báo "ký tự lạ"
    assert getattr(store.load(saved.id).parts[1].chosen_image, field) == value


def test_lone_surrogate_escape_in_file_fails_like_before(store):
    """Giới hạn có từ T-016 (ghi trong báo cáo): JSON có mã ``\\ud800`` lẻ là JSON sai, bộ đọc của
    pydantic từ chối cả nháp trước khi tới phần ảnh. App không bao giờ ghi ra dạng này."""
    saved = store.save(snapshot_with(real_image()))
    obj = json.loads(read_row(store, saved.id))
    obj["parts"][1]["chosen_image"]["alt"] = "trước\ud800sau"
    write_row(store, saved.id, json.dumps(obj))
    with pytest.raises(DraftError, match="bị hỏng"):
        store.load(saved.id)


@pytest.mark.parametrize("alt", ["", "   ", "<b></b>", "\x00\u200b"])
def test_empty_alt_cannot_be_approved(alt):
    assert real_image(alt=alt, alt_approved=True).alt_approved is False


@pytest.mark.parametrize("value", ["yes", 1, "true", None])
def test_alt_approved_must_be_a_real_bool(value):
    with pytest.raises(ValidationError):
        real_image(alt_approved=value)


@pytest.mark.parametrize(
    "text",
    [
        NASTY_TEXT,
        "[a](b) [c]: <d> ![e](f)",
        "https://a.vn/x?y=1 và mailto:a@b.vn",
        "&lt;script&gt; &amp;lt;",
        "\\](\\[",
        "cửa  inox\t\tcổng",
    ],
)
def test_cleaning_is_idempotent(text):
    image = real_image(alt=text, caption=text, prompt=text)
    again = DraftImage(**image.model_dump())
    assert again == image
    assert DraftImage(**again.model_dump()) == again


# ----- chữ đi kèm ảnh AI luôn có tiền tố (SL-T055-2) ------------------------------------------


AI_ALT = "Minh họa bản lề cổng inox bị gỉ trước khi sửa"
AI_CAPTION = "Ảnh minh họa (AI): bản lề gỉ sau 3 năm mưa nắng"


def ai_case(case: str, tag_store: ImageTagStore) -> tuple[DraftImage, dict]:
    """(ảnh có alt "đã duyệt" tả ảnh thật, tham số cho check) theo một cách ảnh thành ảnh AI."""
    if case == "nhap-ghi-AI":
        return real_image(source=SOURCE_AI), {}
    if case == "thu-muc-AI":
        return real_image(rel_path=AI_FOLDER_PATH), {}
    if case == "doi-sang-AI-sau-khi-duyet":
        tag_store.set(ImageRef(0, REAL_PATH), ImageTags(source=SOURCE_AI, category="Cổng inox"))
        return real_image(), {"tag_store": tag_store}
    if case == "goc-AI":
        return real_image(), {"ai_roots": {0}}
    # Ảnh tạo bằng AI mà nháp (sửa tay) ghi alt, chú thích không có tiền tố.
    return generated_image(alt=real_image().alt, caption=real_image().caption), {}


@pytest.mark.parametrize(
    "case", ["nhap-ghi-AI", "thu-muc-AI", "doi-sang-AI-sau-khi-duyet", "goc-AI", "anh-tao-bang-AI"]
)
def test_ai_image_text_gets_prefix_and_needs_review(store, library, tag_store, case):
    image, kwargs = ai_case(case, tag_store)
    assert image.alt_approved
    result = check_one(store, library, image, **kwargs)
    assert result.is_ai
    assert result.image.alt == AI_ALT
    assert result.image.caption == AI_CAPTION
    assert not result.image.alt_approved  # chữ đã đổi: người dùng đọc lại rồi duyệt
    assert result.image.prompt == image.prompt and result.image.ref == image.ref


def test_ai_text_with_prefix_is_kept_and_stays_approved(store, library):
    image = real_image(source=SOURCE_AI, alt=AI_ALT, caption=AI_CAPTION)
    saved = store.save(snapshot_with(image, generated_image()))
    loaded = store.load(saved.id)
    assert [part.chosen_image for part in loaded.parts[1:]] == [image, generated_image()]
    checked = check_draft_images(loaded, library)
    assert checked[1].image == image and checked[2].image == generated_image()
    assert checked[1].image.alt_approved and checked[2].image.alt_approved


def test_real_image_text_is_untouched(store, library, tag_store):
    result = check_one(store, library, real_image(), tag_store=tag_store)
    assert not result.is_ai
    assert result.image == real_image()


def test_opening_draft_that_says_ai_already_adds_prefix(store):
    """Nháp ghi ảnh AI: mở nháp (chưa cần kiểm trên máy) đã có tiền tố và bỏ "đã duyệt"; lưu rồi mở
    lại không đổi gì thêm."""
    saved = store.save(snapshot_with(real_image(source=SOURCE_AI), real_image()))
    loaded = store.load(saved.id)
    ai, real = loaded.parts[1].chosen_image, loaded.parts[2].chosen_image
    assert (ai.alt, ai.caption, ai.alt_approved) == (AI_ALT, AI_CAPTION, False)
    assert real == real_image()
    again = store.load(store.save(loaded).id)
    assert again.parts[1].chosen_image == ai and again.parts[2].chosen_image == real


@pytest.mark.parametrize(
    ("alt", "caption", "expected"),
    [
        ("minh họa", "minh họa:", ("", "")),  # chỉ có tiền tố: không còn gì để giữ
        ("Minh hoạ cổng inox", "", ("Minh họa cổng inox", "")),  # tiền tố viết khác: ghi lại
        (
            "Ảnh minh họa cổng inox",
            "Minh họa: cổng",
            ("Minh họa cổng inox", "Ảnh minh họa (AI): cổng"),
        ),
        ("", "Cổng inox hai cánh", ("", "Ảnh minh họa (AI): cổng inox hai cánh")),
    ],
)
def test_ai_text_prefix_edge_cases(library, alt, caption, expected):
    image = generated_image(alt=alt, caption=caption, alt_approved=bool(alt))
    result = check_chosen_image(image, library).image
    assert (result.alt, result.caption) == expected
    assert not result.alt_approved


def test_long_ai_alt_keeps_prefix_within_limit(library):
    image = generated_image(alt="cổng inox hai cánh " * 100, caption="cửa cuốn " * 300)
    result = check_chosen_image(image, library).image
    assert result.alt.startswith(f"{AI_ALT_PREFIX} cổng inox") and len(result.alt) <= MAX_ALT_CHARS
    assert result.caption.startswith(AI_CAPTION_PREFIX)
    assert len(result.caption) <= MAX_CAPTION_CHARS


def test_unknown_fields_rejected():
    with pytest.raises(ValidationError):
        DraftImage(source=SOURCE_REAL, root_index=0, rel_path=REAL_PATH, ghi_chu="trường lạ")
    with pytest.raises(ValidationError):
        DraftImage(source=SOURCE_REAL, root_index=0, rel_path=REAL_PATH, path="C:/a.jpg")


def test_module_exports():
    for name in (
        "DraftImage",
        "CheckedImage",
        "check_draft_images",
        "check_chosen_image",
        "MAX_ROOT_INDEX",
    ):
        assert name in drafts.__all__
