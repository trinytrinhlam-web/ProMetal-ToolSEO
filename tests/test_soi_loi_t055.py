"""Soi Lỗi T-055: nháp lưu ảnh đã chọn (``seo_app/storage/drafts.py``).

Bổ sung cho ``tests/test_drafts_images.py`` của Thợ Máy, tập trung vào nháp bị sửa tay:

- F1: số gốc, đường dẫn lạ trong nháp không bao giờ làm app đụng tới file ngoài thư mục ảnh (theo
  dõi cả ``os.lstat``/``os.stat``/``os.open``), mọi lần kiểm đi qua ``ImageLibrary``.
- Nguồn ảnh: nháp không kéo ảnh AI về "ảnh thật"; thẻ dựng lại qua ``ImageTags``.
- Alt, chú thích, prompt đọc từ nháp; nháp khuôn 1 do code của ``main`` lưu thật;
  ``schema_version``.

Lượt 2 (sau khi Thợ Máy sửa SL-T055-1 → 3): tên thư mục thật trên ổ (``_FolderNames``: Mac NFD,
đổi tên/xóa/tráo liên kết giữa chừng, không mở file ảnh, danh sách bị cắt) và tiền tố ảnh AI
(không lặp, không mất "đã duyệt" oan).

Lượt 3 (LC-T055-4): từ T-070 "genai" viết kiểu nào cũng là ảnh AI, nên cặp tên thử đổi sang
``CongAI`` (ảnh AI chỉ nhờ tách chữ hoa) / ``congai``, ``Congai`` (ảnh thật); test dựa vào cặp này
kiểm điều kiện đầu bằng ``assert_ai_only_by_case``.

Lỗi tìm được đánh dấu ``xfail(strict=True)`` kèm mã SL-T055-x (xem
``docs/team/reports/T-055-soi-loi.md``). Mọi test dùng thư mục tạm, ảnh giả, không gọi mạng.
"""

from __future__ import annotations

import builtins
import dataclasses
import io
import json
import os
import sqlite3
import unicodedata
from pathlib import Path
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from seo_app.content import OutlineItem
from seo_app.images import folders
from seo_app.images.alt import AI_ALT_PREFIX, AI_CAPTION_PREFIX
from seo_app.images.folders import ImageEntry, ImageFolderError, ImageLibrary, ImageRef, SubFolder
from seo_app.images.tags import SOURCE_AI, SOURCE_REAL, FolderTags, ImageTags, tags_for_image
from seo_app.storage import drafts
from seo_app.storage.drafts import (
    MAX_ALT_CHARS,
    MAX_CAPTION_CHARS,
    MAX_PROMPT_CHARS,
    SCHEMA_VERSION,
    DraftError,
    DraftImage,
    DraftPart,
    DraftSnapshot,
    DraftStore,
    check_chosen_image,
    check_draft_images,
)
from seo_app.storage.image_tags import ImageTagStore

IS_WINDOWS = os.name == "nt"
windows_only = pytest.mark.skipif(not IS_WINDOWS, reason="thuộc tính ẩn, tên ngắn 8.3 của Windows")

PROJECT = "CT012 - Cổng inox - Tân Phú"
REAL_PATH = f"{PROJECT}/truoc/IMG_0001.jpg"
AI_FOLDER = "Ảnh AI"
AI_PATH = f"{AI_FOLDER}/cong-minh-hoa.png"
# "CongAI": thư mục ảnh AI chỉ nhờ tách chữ hoa ("Cong AI", T-052); "congai", "Congai" thì không.
# Không dùng "GenAI": từ T-070 "genai" viết kiểu nào cũng là ảnh AI (LC-T055-4).
CAMEL_AI_PATH = f"{PROJECT}/CongAI/cong.png"
CASE_VARIANT = CAMEL_AI_PATH.replace("CongAI", "congai")  # nháp ghi chữ thường
OUTSIDE_NAME = "bi-mat-ngoai-goc.jpg"
FAKE_JPEG = b"\xff\xd8\xff anh gia"
OUTSIDE_BYTES = b"\xff\xd8\xff BI MAT NGOAI GOC"
REAL_ALT = "Bản lề cổng inox bị gỉ trước khi sửa"


# ----- tiện ích ----------------------------------------------------------------------------


def write(path: Path, data: bytes = FAKE_JPEG) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


@pytest.fixture
def root(tmp_path: Path) -> Path:
    """Thư mục ảnh duy nhất; file bí mật nằm cạnh (ngoài gốc) để thử đường dẫn ra ngoài."""
    drive = tmp_path / "may" / "Drive"
    write(drive / REAL_PATH)
    write(drive / AI_PATH, b"\x89PNG anh AI gia")
    write(drive / CAMEL_AI_PATH, b"\x89PNG anh AI gia")
    write(tmp_path / "may" / OUTSIDE_NAME, OUTSIDE_BYTES)
    write(tmp_path / OUTSIDE_NAME, OUTSIDE_BYTES)
    return drive


@pytest.fixture
def library(root: Path) -> ImageLibrary:
    return ImageLibrary([root])


@pytest.fixture
def store(tmp_path: Path) -> DraftStore:
    return DraftStore(path=tmp_path / "data" / "drafts.sqlite")


@pytest.fixture
def tag_store(tmp_path: Path) -> ImageTagStore:
    return ImageTagStore(path=tmp_path / "data" / "image_tags.sqlite")


def snapshot_with(*images: DraftImage | None) -> DraftSnapshot:
    parts = [DraftPart(heading="Mở bài", versions=["Cổng kêu ken két mỗi sáng."])]
    for number, image in enumerate(images, start=1):
        parts.append(
            DraftPart(
                heading=f"Mục {number}",
                versions=[f"Thân mục {number}."],
                image=f"ảnh cho mục {number}",
                chosen_image=image,
            )
        )
    return DraftSnapshot(
        step=2,
        keyword="sửa cổng inox",
        outline=[OutlineItem(heading="Mục 1", points=["bản lề"], image="ảnh cho mục 1")],
        article_title="Sửa cổng inox tại nhà",
        parts=parts,
    )


def real_image(**changes) -> DraftImage:
    data = dict(
        source=SOURCE_REAL,
        root_index=0,
        rel_path=REAL_PATH,
        category="Cổng inox",
        alt=REAL_ALT,
        alt_approved=True,
        caption="Bản lề gỉ sau 3 năm mưa nắng",
    )
    data.update(changes)
    return DraftImage(**data)


def read_row(store: DraftStore, draft_id: str) -> str:
    with sqlite3.connect(store.path) as conn:
        (data,) = conn.execute("SELECT data FROM drafts WHERE id = ?", (draft_id,)).fetchone()
    conn.close()
    return data


def write_row(store: DraftStore, draft_id: str, data: dict | str) -> None:
    text = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)
    with sqlite3.connect(store.path) as conn:
        conn.execute("UPDATE drafts SET data = ? WHERE id = ?", (text, draft_id))
    conn.close()


def hand_edit_image(store: DraftStore, raw_image: object) -> tuple[DraftSnapshot, str]:
    """Lưu nháp có một ảnh hợp lệ (phần 1) rồi sửa tay ảnh đó thành ``raw_image``."""
    saved = store.save(snapshot_with(real_image()))
    obj = json.loads(read_row(store, saved.id))
    obj["parts"][1]["chosen_image"] = raw_image
    write_row(store, saved.id, obj)
    return saved, saved.id


def hand_edit_text(store: DraftStore, replace: tuple[str, str]) -> str:
    """Sửa tay chữ JSON thô của nháp (cho các dạng ``json.dumps`` không viết ra được)."""
    saved = store.save(snapshot_with(real_image()))
    raw = read_row(store, saved.id)
    old, new = replace
    assert old in raw
    write_row(store, saved.id, raw.replace(old, new, 1))
    return saved.id


def text_of(snapshot: DraftSnapshot) -> list[str]:
    return [part.text for part in snapshot.parts]


class FileSpy:
    """Ghi mọi đường dẫn mà ``os.lstat``/``os.stat``/``os.open`` được gọi tới trong lúc thử."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.paths: list[str] = []
        for name in ("lstat", "stat", "open"):
            original = getattr(os, name)
            monkeypatch.setattr(os, name, self._wrap(original))

    def _wrap(self, original):
        def spy(path, *args, **kwargs):
            if isinstance(path, str | bytes | os.PathLike):
                self.paths.append(os.fsdecode(os.fspath(path)))
            return original(path, *args, **kwargs)

        return spy

    def touched(self, text: str) -> list[str]:
        needle = text.casefold()
        return [path for path in self.paths if needle in path.casefold()]


def is_case_insensitive(folder: Path) -> bool:
    probe = next(folder.iterdir())
    return (folder / probe.name.swapcase()).exists() and probe.name.swapcase() != probe.name


def assert_ai_only_by_case(ai_path: str, other_case: str) -> None:
    """Điều kiện đầu (LC-T055-4): ``ai_path`` là ảnh AI chỉ nhờ chữ hoa, cùng tên viết hoa thường
    khác (``other_case``) thì không, nên thẻ phải theo đúng tên trên ổ thì test mới qua. Đổi cách
    nhận tên ảnh AI làm mất điều này thì test hỏng ở đây, không qua oan."""
    assert tags_for_image(ImageRef(0, ai_path)).tags.is_ai
    assert not tags_for_image(ImageRef(0, other_case)).tags.is_ai


# ----- F1: số gốc sửa tay -------------------------------------------------------------------


BAD_ROOT_INDEXES = [
    -1,
    -(2**63),
    -(2**63) - 1,
    2**63 - 1,
    2**63,
    2**64,
    10**30,
    1000,
    "0",
    "1",
    0.0,
    1.0,
    True,
    False,
    [0],
    {"so": 0},
]


@pytest.mark.parametrize("root_index", BAD_ROOT_INDEXES, ids=repr)
def test_hand_edited_root_index_drops_image_keeps_text(store, library, monkeypatch, root_index):
    raw = {**real_image().model_dump(), "root_index": root_index}
    saved, draft_id = hand_edit_image(store, raw)
    loaded = store.load(draft_id)
    assert loaded.dropped_images == 1
    assert loaded.parts[1].chosen_image is None
    assert text_of(loaded) == text_of(saved)
    spy = FileSpy(monkeypatch)
    assert check_draft_images(loaded, library) == {}
    assert spy.paths == []  # không có ảnh nào thì không đụng ổ đĩa


@pytest.mark.parametrize(
    "number_text", ["1e3", "1e400", "-1e400", "NaN", "Infinity", "-Infinity", "0.5", "1E2"]
)
def test_hand_edited_root_index_json_numbers(store, number_text):
    """Số dạng mũ, NaN, vô cực (chỉ viết được bằng tay vào JSON) không thành số gốc."""
    draft_id = hand_edit_text(store, ('"root_index":0', f'"root_index":{number_text}'))
    loaded = store.load(draft_id)
    assert loaded.dropped_images == 1
    assert loaded.parts[1].chosen_image is None
    assert text_of(loaded)[1] == "Thân mục 1."


def test_negative_zero_is_root_zero(store, library):
    draft_id = hand_edit_text(store, ('"root_index":0', '"root_index":-0'))
    loaded = store.load(draft_id)
    assert loaded.parts[1].chosen_image.root_index == 0
    assert check_draft_images(loaded, library)[1].available


@pytest.mark.parametrize(
    "replace",
    [
        ('"root_index":0', '"root_index":' + "9" * 5000),  # quá giới hạn chữ số của Python
        ('"alt":"', '"alt":' + "[" * 300 + "]" * 300 + ',"x":"'),  # lồng quá sâu
    ],
    ids=["so-5000-chu-so", "long-300-tang"],
)
def test_json_level_breakage_in_image_is_a_draft_error_not_a_crash(store, replace):
    """Giới hạn đã biết (cùng loại surrogate lẻ Thợ Máy đã ghi): JSON hỏng ở mức đọc file thì cả
    nháp báo "bị hỏng" bằng ``DraftError`` (không phải lỗi khác làm sập app), không lộ chữ trong
    file."""
    draft_id = hand_edit_text(store, replace)
    with pytest.raises(DraftError, match="bị hỏng") as info:
        store.load(draft_id)
    assert "999" not in str(info.value) and "[[" not in str(info.value)


# ----- F1: đường dẫn sửa tay, không bao giờ đụng file ngoài gốc -------------------------------


def outside_forms(tmp_path: Path) -> list[str]:
    """Mọi cách viết trỏ tới file bí mật ngoài thư mục ảnh."""
    outside = tmp_path / "may" / OUTSIDE_NAME
    forms = [
        f"../{OUTSIDE_NAME}",
        f"../../{OUTSIDE_NAME}",
        f"{PROJECT}/../../{OUTSIDE_NAME}",
        f"..\\{OUTSIDE_NAME}",
        f"{PROJECT}\\..\\..\\{OUTSIDE_NAME}",
        f"./../{OUTSIDE_NAME}",
        f"%2e%2e/{OUTSIDE_NAME}",
        f"..%2f{OUTSIDE_NAME}",
        f"．．/{OUTSIDE_NAME}",  # dấu chấm toàn khổ (NFKC thành "..")
        f"‥/{OUTSIDE_NAME}",  # "‥" một ký tự
        f"..​/{OUTSIDE_NAME}",
        f"​../{OUTSIDE_NAME}",
        f"..‮/{OUTSIDE_NAME}",
        f"... /{OUTSIDE_NAME}",
        f"~/{OUTSIDE_NAME}",
        f"$HOME/{OUTSIDE_NAME}",
        f"%USERPROFILE%/{OUTSIDE_NAME}",
        str(outside),
        outside.as_posix(),
        "\\\\?\\" + str(outside),
        "//?/" + outside.as_posix(),
        "\\\\.\\" + str(outside),
        "\\\\localhost\\" + str(outside).replace(":", "$", 1),
        "file:///" + outside.as_posix(),
        outside.as_posix().lstrip("/").replace(":", "", 1),  # bỏ dấu ổ: thành đường dẫn "tương đối"
        f"{outside.drive}{OUTSIDE_NAME}" if outside.drive else f"C:{OUTSIDE_NAME}",
        f"{OUTSIDE_NAME}::$DATA",
        f"{OUTSIDE_NAME}.",
        f"{OUTSIDE_NAME} ",
        f"{OUTSIDE_NAME}\x00.jpg",
        f"{OUTSIDE_NAME}\n",
    ]
    return forms


def test_outside_forms_count_matches_parametrize(tmp_path):
    assert len(outside_forms(tmp_path)) == 31


@pytest.mark.parametrize("index", range(31))
def test_hand_edited_path_never_touches_file_outside_root(
    store, library, root, tmp_path, monkeypatch, index
):
    rel_path = outside_forms(tmp_path)[index]
    raw = {**real_image().model_dump(), "rel_path": rel_path}
    saved, draft_id = hand_edit_image(store, raw)
    spy = FileSpy(monkeypatch)
    loaded = store.load(draft_id)
    assert text_of(loaded) == text_of(saved)
    checked = check_draft_images(loaded, library)
    for result in checked.values():
        # Giữ được (tên thư mục lạ nhưng hợp lệ, ví dụ "~"): vẫn chỉ là một chỗ bên trong gốc.
        assert not result.available
        assert str(tmp_path) not in result.message
    # Mọi lần hỏi ổ đĩa về tên file bí mật đều ở **bên trong** thư mục ảnh (và không thấy gì).
    inside = root.resolve()
    for path in spy.touched(OUTSIDE_NAME):
        assert Path(os.path.normpath(path)).is_relative_to(inside), path


def test_kept_odd_names_stay_inside_root(store, library, root, monkeypatch):
    """Tên thư mục lạ nhưng hợp lệ ("~", "%2e%2e", "$HOME") là thư mục **bên trong** gốc: tạo thật
    ở đó thì đọc đúng file trong gốc, không bao giờ giãn ra thư mục nhà hay biến môi trường."""
    for name in ("~", "%2e%2e", "$HOME", "%USERPROFILE%"):
        write(root / name / OUTSIDE_NAME, b"\xff\xd8 trong goc")
    monkeypatch.setenv("HOME", str(root.parent))
    monkeypatch.setenv("USERPROFILE", str(root.parent))
    for name in ("~", "%2e%2e", "$HOME", "%USERPROFILE%"):
        image = real_image(rel_path=f"{name}/{OUTSIDE_NAME}")
        result = check_chosen_image(image, library)
        assert result.available, name
        assert library.read_image_bytes(result.ref) == b"\xff\xd8 trong goc"


def test_loading_a_draft_never_touches_the_image_folders(store, root, monkeypatch):
    """Mở nháp (``load``) chỉ đọc file nháp; ổ ảnh chỉ được hỏi khi gọi ``check_draft_images``."""
    saved = store.save(snapshot_with(real_image(), real_image(rel_path=AI_PATH)))
    spy = FileSpy(monkeypatch)
    store.load(saved.id)
    assert spy.touched(str(root)) == []
    assert spy.touched("IMG_0001") == []


def test_case_variant_reads_the_same_file_inside_root(library, root):
    if not is_case_insensitive(root):
        pytest.skip("ổ phân biệt hoa thường: tên khác hoa thường là file khác")
    result = check_chosen_image(real_image(rel_path=REAL_PATH.upper()), library)
    assert result.available
    assert library.read_image_bytes(result.ref) == FAKE_JPEG


def set_hidden(path: Path) -> None:
    import ctypes

    hidden = 0x2
    assert ctypes.windll.kernel32.SetFileAttributesW(str(path), hidden)


@windows_only
def test_hidden_file_in_draft_is_unavailable(library, root):
    hidden = write(root / "an" / "IMG_9.jpg")
    set_hidden(hidden)
    result = check_chosen_image(real_image(rel_path="an/IMG_9.jpg"), library)
    assert not result.available and "ẩn" in result.message


def short_path(path: Path) -> str:
    import ctypes

    buffer = ctypes.create_unicode_buffer(1024)
    ctypes.windll.kernel32.GetShortPathNameW(str(path), buffer, 1024)
    return buffer.value


@windows_only
def test_short_8_3_name_in_draft_is_rejected(library, root):
    """Tên ngắn 8.3 (``THUMUC~1/ANHRAT~1.JPG``) là tên khác của cùng một file: không dùng được."""
    target = write(root / "Thu muc dai ten lam nhe" / "Anh rat dai ten.jpg")
    short_file, short_root = short_path(target), short_path(root)
    if "~" not in short_file:
        pytest.skip("ổ này tắt tên ngắn 8.3")
    rel = Path(short_file).relative_to(short_root).as_posix()
    result = check_chosen_image(real_image(rel_path=rel), library)
    assert not result.available


# ----- nguồn ảnh: nháp không kéo ảnh AI về ảnh thật -------------------------------------------


def current_ai(case: str, tag_store: ImageTagStore) -> tuple[str, dict]:
    """(đường dẫn, tham số cho check) theo cách "thẻ hiện tại nói AI"."""
    if case == "thu-muc-AI":
        return AI_PATH, {"tag_store": tag_store}
    if case == "the-sua-tay-AI":
        tag_store.set(ImageRef(0, REAL_PATH), ImageTags(source=SOURCE_AI, category="Cổng inox"))
        return REAL_PATH, {"tag_store": tag_store}
    if case == "goc-AI":
        return REAL_PATH, {"ai_roots": {0}}
    return REAL_PATH, {"tag_store": tag_store}  # "that": thẻ hiện tại nói ảnh thật


@pytest.mark.parametrize("draft_source", [SOURCE_REAL, SOURCE_AI])
@pytest.mark.parametrize("current", ["that", "thu-muc-AI", "the-sua-tay-AI", "goc-AI"])
def test_source_matrix_ai_wins(store, library, tag_store, draft_source, current):
    rel_path, kwargs = current_ai(current, tag_store)
    saved = store.save(snapshot_with(real_image(source=draft_source, rel_path=rel_path)))
    result = check_draft_images(store.load(saved.id), library, **kwargs)[1]
    expect_ai = draft_source == SOURCE_AI or current != "that"
    assert result.is_ai is expect_ai
    if expect_ai:
        assert (result.tags.project_code, result.tags.area, result.tags.phase) == ("", "", "")


def test_ai_folder_above_project_folder_wins(library, root, tag_store):
    """Thư mục AI ở tầng trên một thư mục mang tên công trình: vẫn là ảnh AI, không mang mã CT."""
    write(root / AI_FOLDER / PROJECT / "truoc" / "x.jpg")
    image = real_image(rel_path=f"{AI_FOLDER}/{PROJECT}/truoc/x.jpg")
    result = check_chosen_image(image, library, tag_store=tag_store)
    assert result.available and result.is_ai
    assert result.tags.project_code == ""


def broken_tags() -> ImageTags:
    """Thẻ sai khuôn (đi vòng ``__post_init__``), như thể đọc từ nguồn bị sửa."""
    tags = object.__new__(ImageTags)
    for name, value in dict(
        source=SOURCE_REAL, project_code="<b>CT1</b>", category="x", area="Sao Hỏa", phase="?"
    ).items():
        object.__setattr__(tags, name, value)
    return tags


def test_bad_current_tags_are_rebuilt_and_fall_back_to_ai(library, monkeypatch):
    """Thẻ hiện tại sai khuôn: dựng lại qua ``ImageTags(...)`` thì hỏng, nên về ảnh AI (an toàn),
    chỉ giữ hạng mục đã kiểm của nháp."""
    monkeypatch.setattr(drafts, "tags_for_image", lambda ref: FolderTags(tags=broken_tags()))
    result = check_chosen_image(real_image(), library)
    assert result.available
    assert result.tags == ImageTags(source=SOURCE_AI, category="Cổng inox")


@pytest.mark.parametrize("with_store", [False, True], ids=["khong-kho-the", "co-kho-the"])
def test_sl_t055_1_case_variant_cannot_launder_ai_folder(library, root, tag_store, with_store):
    """SL-T055-1 (Trung bình). Thư mục "CongAI" là thư mục ảnh AI (T-052 tách chữ hoa). Nháp sửa
    tay ghi ``.../congai/cong.png``, nguồn "that": trên Windows/Mac ``stat_image`` vẫn tìm ra đúng
    file (không phân biệt hoa thường) nhưng thẻ đọc từ **chữ trong nháp** nên ra ảnh thật, còn mang
    mã công trình CT012 và khu vực Tân Phú. Mong đợi: là ảnh AI (hoặc không dùng được)."""
    assert_ai_only_by_case(CAMEL_AI_PATH, CASE_VARIANT)
    if not is_case_insensitive(root):
        pytest.skip("ổ phân biệt hoa thường: tên khác hoa thường là file khác")
    kwargs = {"tag_store": tag_store} if with_store else {}
    result = check_chosen_image(real_image(rel_path=CASE_VARIANT), library, **kwargs)
    assert result.is_ai or not result.available
    assert result.tags.project_code == ""


def test_sl_t055_1_case_only_folder_rename_keeps_ai(store, library, root):
    """SL-T055-1, đường không cần sửa tay: chọn ảnh khi thư mục tên "Congai" (chưa nhận là AI),
    sau đó đổi tên thư mục thành "CongAI" (thành thư mục ảnh AI). Mở lại nháp, chưa quét: ra ảnh
    thật."""
    assert_ai_only_by_case("CongAI/cong.png", "Congai/cong.png")
    old = write(root / "Congai" / "cong.png", b"\x89PNG")
    if not is_case_insensitive(root):
        pytest.skip("ổ phân biệt hoa thường: tên khác hoa thường là file khác")
    ref = ImageRef(0, "Congai/cong.png")
    picked = DraftImage.from_library(ref, tags_for_image(ref).tags, alt=REAL_ALT)
    assert picked.source == SOURCE_REAL
    saved = store.save(snapshot_with(picked))
    old.parent.rename(root / "CongAI")
    result = check_draft_images(store.load(saved.id), library)[1]
    assert result.is_ai or not result.available


def test_scanned_refs_fix_case_variant(library, root, tag_store):
    """Đường đã đúng hôm nay: có kết quả quét (``scanned``) thì khóa về đúng ``ImageRef`` trên ổ và
    thẻ ra ảnh AI. SL-T055-1 chỉ xảy ra khi mở nháp mà chưa truyền ``scanned``."""
    assert_ai_only_by_case(CAMEL_AI_PATH, CASE_VARIANT)
    if not is_case_insensitive(root):
        pytest.skip("ổ phân biệt hoa thường: tên khác hoa thường là file khác")
    listing = library.list_folder(0, f"{PROJECT}/CongAI")
    result = check_chosen_image(
        real_image(rel_path=CASE_VARIANT), library, tag_store=tag_store, scanned=listing.images
    )
    assert result.ref == ImageRef(0, CAMEL_AI_PATH)
    assert result.is_ai and result.tags.project_code == ""


# ----- alt, chú thích, prompt đọc từ nháp -----------------------------------------------------


@pytest.mark.parametrize(
    "case", ["nhap-that-thu-muc-AI", "doi-sang-AI-sau-khi-duyet", "anh-tao-bang-AI-sua-tay"]
)
def test_sl_t055_2_approved_alt_of_ai_image_has_prefix(store, library, tag_store, case):
    """SL-T055-2 (Trung bình). Alt duyệt khi ảnh còn là ảnh thật («Bản lề cổng inox…») vẫn giữ
    ``alt_approved=True`` khi mở lại nháp mà ảnh nay là ảnh AI (thư mục AI, người dùng bấm "đổi sang
    ảnh AI", T-070 nhận thêm tên AI), hoặc nháp sửa tay. Quy tắc C6 (Lá Chắn T-051): alt ảnh AI luôn
    bắt đầu «Minh họa» do code bảo đảm. Mong đợi: alt đã duyệt của ảnh AI bắt đầu «Minh họa», nếu
    không thì không còn "đã duyệt" (người dùng phải duyệt lại)."""
    kwargs: dict = {"tag_store": tag_store}
    if case == "nhap-that-thu-muc-AI":
        image = real_image(rel_path=AI_PATH)
    elif case == "doi-sang-AI-sau-khi-duyet":
        image = real_image()  # duyệt alt khi còn là ảnh thật …
        tag_store.set(ImageRef(0, REAL_PATH), ImageTags(source=SOURCE_AI))  # … rồi đổi sang AI
    else:
        image = DraftImage(source=SOURCE_AI, prompt="cổng inox", alt=REAL_ALT, alt_approved=True)
    saved = store.save(snapshot_with(image))
    result = check_draft_images(store.load(saved.id), library, **kwargs)[1]
    assert result.is_ai
    assert not result.image.alt_approved or result.image.alt.startswith(AI_ALT_PREFIX)


def test_approved_alt_with_prefix_stays_approved(store, library):
    """Đối chứng cho SL-T055-2: alt ảnh AI đã có tiền tố thì vẫn là "đã duyệt"."""
    image = real_image(rel_path=AI_PATH, source=SOURCE_AI, alt="Minh họa cổng inox hai cánh")
    saved = store.save(snapshot_with(image))
    result = check_draft_images(store.load(saved.id), library)[1]
    assert result.is_ai and result.image.alt_approved


EVIL_TEXTS = [
    '<img src=x onerror="alert(1)">Cổng inox',
    "<script>alert(1)</script>Cổng inox",
    "![ảnh](javascript:alert(1)) Cổng inox",
    "[bấm](data:text/html;base64,PHNjcmlwdD4=) Cổng inox",
    "<a href='javascript:alert(1)'>Cổng inox</a>",
    "<iframe src=//evil.example></iframe>Cổng inox",
    "Cổng inox‮⁦​﻿\x1b[31m\x07",
    "Cổng inox\r\n\r\n# Tiêu đề\n- danh sách\n```code```",
]


@pytest.mark.parametrize("text", EVIL_TEXTS)
def test_alt_and_caption_from_draft_are_inert(store, text):
    raw = {**real_image().model_dump(), "alt": text, "caption": text}
    saved, draft_id = hand_edit_image(store, raw)
    image = store.load(draft_id).parts[1].chosen_image
    for value in (image.alt, image.caption):
        assert "Cổng inox" in value
        lowered = value.casefold()
        for bad in ("<script", "<img", "<iframe", "<a ", "onerror", "javascript:", "data:", "]("):
            assert bad not in lowered, (bad, value)
        assert "\n" not in value and "\r" not in value
        assert not any(ch in value for ch in "‮⁦﻿\x1b\x07")


@pytest.mark.parametrize("text", EVIL_TEXTS)
def test_prompt_from_draft_is_plain_text(store, text):
    """Prompt giữ chữ (để sao chép đúng), chỉ bỏ ký tự điều khiển/vô hình; không chạy gì."""
    raw = {**real_image().model_dump(), "prompt": text}
    saved, draft_id = hand_edit_image(store, raw)
    prompt = store.load(draft_id).parts[1].chosen_image.prompt
    assert "Cổng inox" in prompt
    assert not any(ch in prompt for ch in "‮⁦​﻿\x1b\x07\r")


def test_template_and_code_like_text_is_kept_literally(store):
    text = "{prompt} {0.__class__} ${HOME} %(x)s `rm -rf /` __import__('os')"
    raw = {**real_image().model_dump(), "alt": text, "caption": text, "prompt": text}
    saved, draft_id = hand_edit_image(store, raw)
    image = store.load(draft_id).parts[1].chosen_image
    assert image.prompt == text
    assert "{prompt}" in image.alt and "${HOME}" in image.caption


@pytest.mark.parametrize(
    ("field", "limit"),
    [("alt", MAX_ALT_CHARS), ("caption", MAX_CAPTION_CHARS), ("prompt", MAX_PROMPT_CHARS)],
)
def test_huge_text_in_draft_is_bounded(store, field, limit):
    """Chữ dài cỡ cả MB trong nháp sửa tay (vẫn dưới giới hạn 5 MB của nháp): cắt, không bỏ ảnh."""
    raw = {**real_image().model_dump(), field: "cửa cuốn " * 200_000}
    saved, draft_id = hand_edit_image(store, raw)
    loaded = store.load(draft_id)
    assert loaded.dropped_images == 0
    assert 0 < len(getattr(loaded.parts[1].chosen_image, field)) <= limit


# ----- nháp khuôn cũ, schema_version ---------------------------------------------------------


# Nháp khuôn 1 do chính code của ``main`` (trước T-055, ``origin/main`` 08e803e) lưu ra, chép
# nguyên văn (chỉ thay mã nháp cho dễ đọc): có nghiên cứu, dàn ý, rà soát, câu bỏ qua.
REAL_V1_DRAFT = (
    '{"schema_version":1,"id":"00000000000000000000000000000055",'
    '"saved_at":"2026-10-20T18:11:11.680195+07:00","step":3,"keyword":"sửa cổng inox Tân Phú",'
    '"material":{"Kinh nghiệm của xưởng":"Bản lề gỉ sau 3 năm.",'
    '"Câu khách hay hỏi":"Có cần tháo cả cánh không?"},'
    '"research":{"intent":["Chủ nhà thấy cổng kêu, muốn biết sửa hay thay."],'
    '"article_type":"hướng dẫn","competitors":[{"title":"Sửa cổng inox giá rẻ",'
    '"url":"https://vi-du.vn/sua-cong","covers":"Giá sửa","missing":"Ảnh thật"}],'
    '"new_angles":["Ảnh trước/sau thật"],"questions":["Giá bao nhiêu?"]},'
    '"research_keyword":"sửa cổng inox Tân Phú","outline_title":"Sửa cổng inox tại nhà",'
    '"outline":[{"heading":"Dấu hiệu cổng hỏng","points":["bản lề kêu","cánh xệ"],'
    '"image":"ảnh bản lề gỉ"}],'
    '"article_title":"Sửa cổng inox tại nhà: khi nào cần thay bản lề",'
    '"parts":[{"heading":"Mở bài","versions":["Cổng kêu ken két mỗi sáng."],"current":0,'
    '"image":""},{"heading":"Dấu hiệu cổng hỏng","versions":["Bản lề gỉ.",'
    '"Bản lề gỉ, cánh xệ."],"current":1,"image":"ảnh bản lề gỉ"}],'
    '"review":{"scores":{"friendly":80,"natural":75,"readable":90,"specific":70,"seo":85},'
    '"flags":[{"section":1,"sentence":"Bản lề gỉ.","reason":"ngắn",'
    '"replacement":"Bản lề gỉ sét."}],"summary":"Ổn."},"auto_fixed":1,'
    '"ignored_flags":["Bản lề gỉ."]}'
)
REAL_V1_ID = "00000000000000000000000000000055"


def put_raw(store: DraftStore, draft_id: str, raw: str) -> None:
    store.save(DraftSnapshot(id=draft_id, keyword="tạm"))
    write_row(store, draft_id, raw)


def test_real_v1_draft_from_main_opens_and_resaves_as_v2(store, library):
    put_raw(store, REAL_V1_ID, REAL_V1_DRAFT)
    loaded = store.load(REAL_V1_ID)
    assert loaded.schema_version == SCHEMA_VERSION == 3
    assert loaded.dropped_images == 0
    assert loaded.step == 3 and loaded.auto_fixed == 1
    assert loaded.keyword == "sửa cổng inox Tân Phú"
    assert loaded.material["Câu khách hay hỏi"] == "Có cần tháo cả cánh không?"
    assert loaded.article_title == "Sửa cổng inox tại nhà: khi nào cần thay bản lề"
    assert text_of(loaded) == ["Cổng kêu ken két mỗi sáng.", "Bản lề gỉ, cánh xệ."]
    assert [part.image for part in loaded.parts] == ["", "ảnh bản lề gỉ"]
    assert loaded.review.summary == "Ổn." and loaded.ignored_flags == ["Bản lề gỉ."]
    assert all(part.chosen_image is None for part in loaded.parts)
    assert check_draft_images(loaded, library) == {}
    # Chọn ảnh rồi lưu lại: thành khuôn 2, mở lại giữ nguyên lựa chọn.
    loaded.parts[1].chosen_image = real_image()
    resaved = store.save(loaded)
    stored = json.loads(read_row(store, REAL_V1_ID))
    assert stored["schema_version"] == 3
    again = store.load(REAL_V1_ID)
    assert again.parts[1].chosen_image == real_image()
    assert text_of(again) == text_of(resaved)


def test_v1_keeps_every_text_field_like_v2(store):
    """Mở bằng khuôn 1 hay sau khi nâng lên khuôn 2: chữ của bài như nhau."""
    put_raw(store, REAL_V1_ID, REAL_V1_DRAFT)
    first = store.load(REAL_V1_ID)
    store.save(first)
    second = store.load(REAL_V1_ID)
    dump = {"exclude": {"saved_at"}}
    assert first.model_dump(**dump) == second.model_dump(**dump)


def test_schema_version_guard_for_old_test_line():
    """Canh dòng ``tests/test_soi_loi_t016_t020.py:744`` (Thợ Máy sửa 2 → 3, Chỉ Huy B duyệt): ca
    đó cần "phiên bản kế tiếp chưa biết". Khi khuôn lên 3, test này đỏ để nhắc sửa cả dòng đó."""
    assert SCHEMA_VERSION + 1 == 4
    with pytest.raises(ValidationError):
        DraftSnapshot(schema_version=SCHEMA_VERSION + 1)
    assert DraftSnapshot(schema_version=1).schema_version == SCHEMA_VERSION


@pytest.mark.parametrize("version", [SCHEMA_VERSION + 1, 10**6, -(2**63)])
def test_future_versions_fail_whole_draft_without_leaking(store, version):
    saved = store.save(snapshot_with(real_image()))
    obj = json.loads(read_row(store, saved.id))
    obj["schema_version"] = version
    write_row(store, saved.id, obj)
    with pytest.raises(DraftError, match="bị hỏng") as info:
        store.load(saved.id)
    assert REAL_PATH not in str(info.value)


def test_sl_t055_3_v1_null_images_are_not_counted_as_dropped(store):
    """SL-T055-3 (Thấp). Nháp khuôn 1 có ``"chosen_image": null`` ở mỗi phần (sửa tay, hoặc chép nửa
    chừng từ khuôn 2): không có ảnh nào bị mất, nhưng ``dropped_images`` đếm mỗi phần một ảnh nên
    giao diện sẽ báo "N ảnh đã chọn bị hỏng nên đã bỏ". Mong đợi: 0."""
    data = json.loads(REAL_V1_DRAFT)
    for part in data["parts"]:
        part["chosen_image"] = None
    put_raw(store, REAL_V1_ID, json.dumps(data, ensure_ascii=False))
    loaded = store.load(REAL_V1_ID)
    assert loaded.dropped_images == 0


def test_round_trip_many_images_keeps_every_choice(store, library, root):
    """Lưu rồi mở lại giữ nguyên lựa chọn: nhiều phần, tên tiếng Việt, ảnh AI tạo mới, phần không
    chọn ảnh."""
    names = [f"{PROJECT}/sau/Ảnh {i} – cổng đã sơn.jpg" for i in range(5)]
    for name in names:
        write(root / name)
    images = [
        real_image(rel_path=name, alt=f"Cổng sau khi sơn lần {i}") for i, name in enumerate(names)
    ]
    images.insert(2, DraftImage(source=SOURCE_AI, prompt="cổng\nhai cánh", alt="Minh họa cổng"))
    images.insert(4, None)
    saved = store.save(snapshot_with(*images))
    loaded = store.load(saved.id)
    assert [part.chosen_image for part in loaded.parts[1:]] == images
    checked = check_draft_images(loaded, library)
    assert set(checked) == {1, 2, 3, 4, 6, 7}
    assert all(checked[i].available for i in (1, 2, 4, 6, 7))
    assert checked[3].is_generated and checked[3].is_ai


# ===== Lượt 2: tên thư mục thật trên ổ (SL-T055-1 đã sửa bằng ``_FolderNames``) ================


class CaseSensitiveDisk:
    """Giả ổ **phân biệt** hoa thường (Linux, APFS bản phân biệt, thư mục NTFS bật phân biệt hoa
    thường): ``stat_image`` chỉ thấy đúng tên trong ``files`` (mỗi file một cỡ để biết là file
    nào); ``list_folder`` của thư mục gốc chỉ trả ``seen`` và báo đã cắt (thư mục quá 5.000 mục hay
    quét quá 10 giây nên tên còn lại chưa được xem)."""

    def __init__(self, monkeypatch, files: dict[str, int], seen: tuple[str, ...]) -> None:
        def stat_image(_library, ref):
            if ref.rel_path not in files:
                raise ImageFolderError("Không tìm thấy ảnh hoặc thư mục này.")
            return ImageEntry(ref=ref, name=ref.name, size=files[ref.rel_path], modified=0.0)

        def list_folder(_library, root_index, rel_dir="", **kwargs):
            assert rel_dir == ""
            subfolders = tuple(SubFolder(rel_path=name, name=name) for name in seen)
            return SimpleNamespace(subfolders=subfolders, truncated=True)

        monkeypatch.setattr(ImageLibrary, "stat_image", stat_image)
        monkeypatch.setattr(ImageLibrary, "list_folder", list_folder)


@pytest.mark.parametrize(
    ("draft_path", "seen"),
    [("congai/cong.png", ("CongAI",)), ("CongAI/cong.png", ("congai",))],
    ids=["nhap-congai-chi-thay-CongAI", "nhap-CongAI-chi-thay-congai"],
)
def test_sl_t055_4_real_name_must_point_to_the_checked_file(monkeypatch, library, draft_path, seen):
    """SL-T055-4 (Thấp). Ổ phân biệt hoa thường có cả ``CongAI/cong.png`` (ảnh AI) lẫn
    ``congai/cong.png`` (một file khác). ``stat_image`` thấy đúng file nháp ghi; danh sách thư mục
    gốc bị cắt nên chỉ thấy tên kia. ``_FolderNames`` lấy tên kia làm "tên thật" (trùng không phân
    biệt hoa thường, đúng một) và đổi ``ref``, ``entry.ref`` sang **file khác** mà không kiểm lại:
    ảnh vẫn "dùng được", đọc ảnh sau này ra ảnh khác ảnh đã chọn; ca thứ hai còn làm ảnh nháp ghi
    trong thư mục ``CongAI`` thành ảnh thật. Mong đợi: ``ref`` dùng được thì đúng là file đã
    kiểm."""
    # Còn ``xfail`` thì câu này hỏng cũng bị tính là "hỏng như dự kiến"; các test SL-T055-1 ở trên
    # (không ``xfail``) kiểm cùng cặp tên. Gỡ ``xfail`` (đã sửa SL-T055-4) thì câu này có hiệu lực.
    assert_ai_only_by_case("CongAI/cong.png", "congai/cong.png")
    files = {"CongAI/cong.png": 111, "congai/cong.png": 222}
    CaseSensitiveDisk(monkeypatch, files, seen)
    result = check_chosen_image(real_image(rel_path=draft_path), library)
    if result.available:
        assert result.ref == ImageRef(0, draft_path)
        assert result.entry.size == files[result.ref.rel_path]
    if draft_path.startswith("CongAI/"):
        assert result.is_ai


def test_sl_t055_4_folder_swapped_during_check_on_real_disk(monkeypatch, library, root):
    """SL-T055-4 trên ổ thật (Windows, Mac): giữa lúc ``stat_image`` và lúc xem tên thư mục, thư mục
    chứa ảnh bị đổi tên đi và một thư mục khác được đổi tên thành tên trùng hoa thường. ``ref``
    chuyển sang file của thư mục kia, ``entry`` vẫn là số liệu của file cũ."""
    write(root / "Congai" / "cong.png", b"\x89PNG anh da chon")
    write(root / "Khac" / "cong.png", b"\x89PNG mot anh khac han, dai hon")
    if not (root / "congai").exists():
        pytest.skip("ổ phân biệt hoa thường: nháp 'congai' không trỏ tới 'Congai'")
    original = ImageLibrary.list_folder

    def swap_then_list(self, root_index, rel_dir="", **kwargs):
        if rel_dir == "":
            os.rename(root / "Congai", root / "Congai cu")
            os.rename(root / "Khac", root / "CongAI")
        return original(self, root_index, rel_dir, **kwargs)

    monkeypatch.setattr(ImageLibrary, "list_folder", swap_then_list)
    result = check_chosen_image(real_image(rel_path="congai/cong.png"), library)
    monkeypatch.undo()
    if result.available:
        assert library.stat_image(result.ref).size == result.entry.size


def test_sl_t055_5_plain_real_image_usable_when_parent_listing_is_cut(monkeypatch, library):
    """SL-T055-5 (Thấp). Nháp ghi đúng tên như trên ổ (không khác hoa thường), ảnh còn nguyên.
    Thư mục gốc có hơn 5.000 mục (hay ổ chậm, quét quá 10 giây) nên thư mục công trình chưa nằm
    trong phần đã xem: lượt 1 ảnh dùng được, lượt 2 báo "Chưa kiểm được tên thư mục" cho **mọi**
    ảnh thật trong đó. Thử trên ổ thật Windows: gốc 5.200 ảnh tên bắt đầu bằng số (xếp trước
    "CT012…") thì ảnh không dùng được; giao diện quét gốc cũng dừng ở 5.000 mục nên không mở tới
    thư mục chứa ảnh như câu báo khuyên. Mong đợi: ảnh vẫn dùng được, thẻ ảnh thật."""
    original = ImageLibrary.list_folder

    def cut(self, root_index, rel_dir="", **kwargs):
        listing = original(self, root_index, rel_dir, **kwargs)
        return dataclasses.replace(listing, subfolders=(), truncated=True)

    monkeypatch.setattr(ImageLibrary, "list_folder", cut)
    result = check_chosen_image(real_image(), library)
    assert result.available, result.message
    assert result.ref == ImageRef(0, REAL_PATH) and not result.is_ai
    assert result.tags.project_code == "CT012"


class MacDisk:
    """Giả ổ Mac (APFS mặc định): tìm tên không phân biệt hoa thường và dạng Unicode,
    ``list_folder`` trả tên đúng như lưu trên ổ (ở đây là dạng NFD)."""

    def __init__(self, monkeypatch, files: list[str]) -> None:
        stored = [unicodedata.normalize("NFD", name) for name in files]
        self.listed: list[str] = []

        def key(text: str) -> str:
            return unicodedata.normalize("NFC", text).casefold()

        def stat_image(_library, ref):
            if not any(key(name) == key(ref.rel_path) for name in stored):
                raise ImageFolderError("Không tìm thấy ảnh hoặc thư mục này.")
            return ImageEntry(ref=ref, name=ref.name, size=10, modified=0.0)

        def list_folder(_library, root_index, rel_dir="", **kwargs):
            self.listed.append(rel_dir)
            depth = len(rel_dir.split("/")) if rel_dir else 0
            found: dict[str, str] = {}
            for name in stored:
                parts = name.split("/")
                if len(parts) > depth + 1 and key("/".join(parts[:depth])) == key(rel_dir):
                    found["/".join(parts[: depth + 1])] = parts[depth]
            subfolders = tuple(SubFolder(rel_path=path, name=sub) for path, sub in found.items())
            return SimpleNamespace(subfolders=subfolders, truncated=False)

        monkeypatch.setattr(ImageLibrary, "stat_image", stat_image)
        monkeypatch.setattr(ImageLibrary, "list_folder", list_folder)


def test_mac_nfd_folder_names_keep_ai_and_real_tags(monkeypatch, library):
    """Mac lưu tên dạng NFD, nháp ghi NFC (và chữ thường "congai"): vẫn lấy đúng tên trên ổ, ảnh
    trong "CongAI" là ảnh AI không mã công trình; ảnh thật giữ mã công trình, khu vực."""
    assert_ai_only_by_case(CAMEL_AI_PATH, CASE_VARIANT)
    disk = MacDisk(monkeypatch, [CAMEL_AI_PATH, REAL_PATH])
    ai = check_chosen_image(real_image(rel_path=CASE_VARIANT), library)
    assert ai.available and ai.is_ai and ai.tags.project_code == ""
    assert ai.ref.rel_path == unicodedata.normalize("NFD", CAMEL_AI_PATH)
    real = check_chosen_image(real_image(), library)
    assert real.available and not real.is_ai
    assert (real.tags.project_code, real.tags.area) == ("CT012", "Tân Phú")
    assert disk.listed[0] == ""


def test_ntfs_nfc_and_nfd_sibling_folders_are_told_apart(library, root):
    """Ổ không gộp dạng Unicode (NTFS, ext4) có thể có cả "Tân Phú" dạng NFC lẫn NFD cạnh nhau: tên
    trong nháp trùng hẳn thì lấy đúng thư mục đó, không báo "chưa kiểm được"."""
    nfc = "Tân Phú"
    nfd = unicodedata.normalize("NFD", nfc)
    assert_ai_only_by_case(f"{nfc}/CongAI/a.png", f"{nfc}/congai/a.png")
    write(root / nfc / "CongAI" / "a.png", b"\x89PNG")
    write(root / nfd / "truoc" / "a.png", b"\x89PNG")
    if len({path.name for path in root.iterdir()} & {nfc, nfd}) != 2:
        pytest.skip("ổ gộp NFC/NFD (Mac): không có hai thư mục riêng")
    if not is_case_insensitive(root / nfc):
        pytest.skip("ổ phân biệt hoa thường: 'congai' là thư mục khác")
    ai = check_chosen_image(real_image(rel_path=f"{nfc}/congai/a.png"), library)
    assert ai.available and ai.is_ai and ai.ref.rel_path == f"{nfc}/CongAI/a.png"
    real = check_chosen_image(real_image(rel_path=f"{nfd}/TRUOC/a.png"), library)
    assert real.available and not real.is_ai and real.ref.rel_path == f"{nfd}/truoc/a.png"


def test_check_opens_no_image_file(monkeypatch, library):
    """Kiểm tên thư mục chỉ mở thư mục (đọc tên, ``stat``), không mở file ảnh nào: Drive "chỉ trực
    tuyến" không bị tải về. Theo dõi ``os.open``, ``open`` và chỗ giữ thư mục của Windows."""
    assert_ai_only_by_case(CAMEL_AI_PATH, CASE_VARIANT)
    opened: list[str] = []
    real_os_open, real_open, real_hold = os.open, builtins.open, folders._win_hold_dir

    def spy_os_open(path, *args, **kwargs):
        opened.append(os.fsdecode(path))
        return real_os_open(path, *args, **kwargs)

    def spy_open(path, *args, **kwargs):
        opened.append(os.fsdecode(path) if isinstance(path, str | bytes | os.PathLike) else "")
        return real_open(path, *args, **kwargs)

    def spy_hold(path):
        opened.append(str(path))
        return real_hold(path)

    monkeypatch.setattr(os, "open", spy_os_open)
    monkeypatch.setattr(builtins, "open", spy_open)
    monkeypatch.setattr(io, "open", spy_open)
    monkeypatch.setattr(folders, "_win_hold_dir", spy_hold)
    monkeypatch.setattr(ImageLibrary, "read_image_bytes", None)
    result = check_chosen_image(real_image(rel_path=CASE_VARIANT), library)
    monkeypatch.undo()
    if result.available:  # ổ không phân biệt hoa thường: đã xem tên thư mục
        assert opened and result.is_ai and result.ref.rel_path == CAMEL_AI_PATH
    assert not [path for path in opened if path.lower().endswith((".png", ".jpg", ".jpeg"))]


@pytest.mark.parametrize("change", ["doi-ten", "xoa"])
def test_folder_renamed_or_deleted_during_check(monkeypatch, library, root, tmp_path, change):
    """Thư mục trên đường tới ảnh bị đổi tên hay xóa giữa lúc ``stat_image`` và lúc xem tên: ảnh
    không dùng được, câu báo không có đường dẫn máy, không sập."""
    original = ImageLibrary.list_folder

    def change_then_list(self, root_index, rel_dir="", **kwargs):
        if rel_dir == PROJECT:
            target = root / PROJECT / "CongAI"
            if change == "xoa":
                (target / "cong.png").unlink()
                target.rmdir()
            else:
                os.rename(target, root / PROJECT / "CongAI cu")
        return original(self, root_index, rel_dir, **kwargs)

    monkeypatch.setattr(ImageLibrary, "list_folder", change_then_list)
    result = check_chosen_image(real_image(rel_path=CASE_VARIANT), library)
    assert not result.available
    assert str(tmp_path) not in result.message and "\\" not in result.message


@windows_only
def test_junction_swapped_in_during_check_is_unavailable(monkeypatch, library, root, tmp_path):
    """Thư mục công trình bị tráo thành junction trỏ ra ngoài gốc giữa lúc ``stat_image`` và lúc
    xem tên: không đi theo, ảnh không dùng được, không lộ đường dẫn."""
    import _winapi
    import shutil

    outside = tmp_path / "ngoai"
    write(outside / "CongAI" / "cong.png", OUTSIDE_BYTES)
    original = ImageLibrary.list_folder

    def swap_then_list(self, root_index, rel_dir="", **kwargs):
        if rel_dir == "":
            shutil.rmtree(root / PROJECT)
            _winapi.CreateJunction(str(outside), str(root / PROJECT))
        return original(self, root_index, rel_dir, **kwargs)

    monkeypatch.setattr(ImageLibrary, "list_folder", swap_then_list)
    try:
        result = check_chosen_image(real_image(rel_path=CASE_VARIANT), library)
    finally:
        monkeypatch.undo()
        if (root / PROJECT).is_junction():
            os.rmdir(root / PROJECT)  # gỡ junction, không đụng thư mục đích
    assert not result.available
    assert str(tmp_path) not in result.message


# ===== Lượt 2: tiền tố ảnh AI (SL-T055-2 đã sửa) ==============================================


PREFIXED_ALT = "Minh họa cổng inox hai cánh"


def ai_way(case: str, tag_store: ImageTagStore) -> tuple[DraftImage, dict]:
    """Ảnh có alt đã duyệt **đã có** tiền tố, chú thích chưa có, theo từng cách thành ảnh AI."""
    texts = {"alt": PREFIXED_ALT, "alt_approved": True, "caption": "Cổng hai cánh mới sơn"}
    if case == "nhap-ghi-AI":
        return real_image(source=SOURCE_AI, **texts), {}
    if case == "thu-muc-AI-hoa-thuong":
        return real_image(rel_path=CASE_VARIANT, **texts), {}
    if case == "the-sua-tay-AI":
        tag_store.set(ImageRef(0, REAL_PATH), ImageTags(source=SOURCE_AI))
        return real_image(**texts), {"tag_store": tag_store}
    if case == "goc-AI":
        return real_image(**texts), {"ai_roots": {0}}
    return DraftImage(source=SOURCE_AI, prompt="cổng", **texts), {}


@pytest.mark.parametrize(
    "case", ["nhap-ghi-AI", "thu-muc-AI-hoa-thuong", "the-sua-tay-AI", "goc-AI", "anh-tao-bang-AI"]
)
def test_prefixed_alt_never_loses_approval(store, library, root, tag_store, case):
    """Không mất "đã duyệt" oan: alt đã có «Minh họa» thì giữ nguyên và vẫn đã duyệt; chú thích
    được thêm tiền tố mà không kéo theo alt."""
    image, kwargs = ai_way(case, tag_store)
    if case == "thu-muc-AI-hoa-thuong":
        assert_ai_only_by_case(CAMEL_AI_PATH, CASE_VARIANT)
        if not is_case_insensitive(root):
            pytest.skip("ổ phân biệt hoa thường: 'congai' là thư mục khác")
    saved = store.save(snapshot_with(image))
    result = check_draft_images(store.load(saved.id), library, **kwargs)[1]
    assert result.is_ai
    assert (result.image.alt, result.image.alt_approved) == (PREFIXED_ALT, True)
    assert result.image.caption == f"{AI_CAPTION_PREFIX}: cổng hai cánh mới sơn"


def test_prefix_is_not_repeated_over_many_save_open_cycles(store, library, root):
    """Mở nháp, kiểm, lưu lại bằng ``checked.image`` (như giao diện sẽ làm) nhiều lần: tiền tố chỉ
    thêm một lần, không thành «Minh họa minh họa…»; duyệt lại một lần thì giữ "đã duyệt"."""
    assert_ai_only_by_case(CAMEL_AI_PATH, CASE_VARIANT)
    if not is_case_insensitive(root):
        pytest.skip("ổ phân biệt hoa thường: 'congai' là thư mục khác")
    images = (
        real_image(rel_path=CASE_VARIANT),  # thư mục AI, nháp ghi ảnh thật, chữ thường
        real_image(source=SOURCE_AI),  # nháp ghi AI
        DraftImage(source=SOURCE_AI, prompt="cổng", alt="Cổng inox", alt_approved=True),
    )
    draft_id = store.save(snapshot_with(*images)).id
    seen = []
    for cycle in range(5):
        loaded = store.load(draft_id)
        checked = check_draft_images(loaded, library)
        parts = list(loaded.parts)
        for index, item in checked.items():
            image = item.image
            if cycle == 1:
                image = image.model_copy(update={"alt_approved": True})  # người dùng duyệt lại
            parts[index] = parts[index].model_copy(update={"chosen_image": image})
        draft_id = store.save(loaded.model_copy(update={"parts": parts})).id
        seen.append(
            [
                (c.is_ai, c.image.alt, c.image.caption, c.image.alt_approved)
                for c in checked.values()
            ]
        )
    for row in seen:
        for is_ai, alt, caption, _approved in row:
            assert is_ai
            assert alt.startswith(f"{AI_ALT_PREFIX} ")
            assert AI_ALT_PREFIX.casefold() not in alt[len(AI_ALT_PREFIX) :].casefold()
            assert not caption or (
                caption.startswith(AI_CAPTION_PREFIX) and caption.count("minh họa") == 1
            )
    assert [approved for *_rest, approved in seen[0]] == [False, False, False]
    assert seen[2] == seen[3] == seen[4]
    assert all(approved for *_rest, approved in seen[4])


@pytest.mark.parametrize("value", [False, 0, "", [], {}], ids=repr)
def test_v1_non_null_image_values_are_still_counted(store, value):
    """Đối chứng cho SL-T055-3: chỉ ``null`` là "chưa chọn ảnh"; giá trị khác (sửa tay) vẫn đếm."""
    data = json.loads(REAL_V1_DRAFT)
    data["parts"][0]["chosen_image"] = None
    data["parts"][1]["chosen_image"] = value
    put_raw(store, REAL_V1_ID, json.dumps(data, ensure_ascii=False))
    loaded = store.load(REAL_V1_ID)
    assert loaded.dropped_images == 1
    assert loaded.parts[1].text == "Bản lề gỉ, cánh xệ."
