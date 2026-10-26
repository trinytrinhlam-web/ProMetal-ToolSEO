"""T-041 (Thợ Máy): nháp nhớ lựa chọn ở bước SEO (``DraftSnapshot.seo``).

- meta title, meta description kèm các bản trước (để quay lại), slug, liên kết nội bộ (cột
  «Dùng»), có dùng schema FAQ không; tự lưu cùng nháp, nháp cũ (không có phần SEO) vẫn mở được;
- điều kiện Lá Chắn T-039 số 2b: liên kết ghi bằng ``asdict(InternalLink)``, đọc lại qua
  ``InternalLink(**d)``, sai khuôn thì bỏ riêng liên kết đó;
- dữ liệu đọc từ file là chưa tin cậy: chữ được chuẩn hóa, ``extra="forbid"``, phần SEO hỏng chỉ
  làm mất phần SEO (chữ và ảnh của bài giữ nguyên).

Thư mục tạm, không đụng ``data/`` thật, không gọi mạng.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from pathlib import Path

import pytest
from pydantic import ValidationError

from seo_app.onpage.links import InternalLink
from seo_app.storage import DraftPart, DraftSnapshot, DraftStore
from seo_app.storage.drafts import (
    MAX_DRAFT_LINKS,
    MAX_META_VERSIONS,
    MAX_SEO_TEXT_CHARS,
    SCHEMA_VERSION,
    DraftLink,
    DraftMetaVersions,
    DraftSeo,
)

TITLE = "Cửa sắt bị xệ: dấu hiệu sớm và cách xử lý gọn"
DESC = "Cửa sắt bị xệ, cạ nền khi đóng mở? Xem 5 dấu hiệu sớm và việc bạn tự làm được."


@pytest.fixture
def store(tmp_path: Path) -> DraftStore:
    return DraftStore(path=tmp_path / "data" / "drafts.sqlite")


def full_seo() -> DraftSeo:
    return DraftSeo(
        title=DraftMetaVersions(versions=["Bản AI đầu", TITLE], current=1),
        description=DraftMetaVersions(versions=[DESC]),
        slug="cua-sat-bi-xe",
        links=[
            DraftLink.from_link(InternalLink(section=1, anchor="bản lề mòn", post_id=10)),
            DraftLink.from_link(
                InternalLink(section=2, anchor="cửa cuốn lệch ray", post_id=11), use=False
            ),
        ],
        use_faq=True,
    )


def snapshot(seo: DraftSeo | None = None) -> DraftSnapshot:
    parts = [DraftPart(heading="Mở bài", versions=["Cửa sắt bị xệ do bản lề mòn."])]
    if seo is None:
        return DraftSnapshot(keyword="cửa sắt bị xệ", article_title="Bài", parts=parts)
    return DraftSnapshot(keyword="cửa sắt bị xệ", article_title="Bài", parts=parts, seo=seo)


def read_row(store: DraftStore, draft_id: str) -> dict:
    with sqlite3.connect(store.path) as conn:
        (data,) = conn.execute("SELECT data FROM drafts WHERE id = ?", (draft_id,)).fetchone()
    return json.loads(data)


def write_row(store: DraftStore, draft_id: str, data: dict) -> None:
    with sqlite3.connect(store.path) as conn:
        conn.execute("UPDATE drafts SET data = ? WHERE id = ?", (json.dumps(data), draft_id))


def saved_with(store: DraftStore, change) -> str:
    """Lưu một nháp đủ phần SEO, sửa tay JSON bằng ``change(obj)``, trả mã nháp."""
    saved = store.save(snapshot(full_seo()))
    obj = read_row(store, saved.id)
    change(obj)
    write_row(store, saved.id, obj)
    return saved.id


# ============================================================ lưu, mở lại


def test_round_trip_keeps_every_seo_choice(store):
    saved = store.save(snapshot(full_seo()))
    loaded = store.load(saved.id)
    assert loaded.seo == full_seo()
    assert loaded.seo.title.text == TITLE and loaded.seo.description.text == DESC
    assert [(link.to_link(), link.use) for link in loaded.seo.links] == [
        (InternalLink(section=1, anchor="bản lề mòn", post_id=10), True),
        (InternalLink(section=2, anchor="cửa cuốn lệch ray", post_id=11), False),
    ]
    assert loaded.schema_version == SCHEMA_VERSION
    resaved = store.save(loaded)
    assert store.load(resaved.id).model_dump(exclude={"saved_at"}) == loaded.model_dump(
        exclude={"saved_at"}
    )


def test_links_saved_as_asdict_without_address(store):
    saved = store.save(snapshot(full_seo()))
    links = read_row(store, saved.id)["seo"]["links"]
    assert links[0] == {**asdict(InternalLink(1, "bản lề mòn", 10)), "use": True}
    assert all(set(link) == {"section", "anchor", "post_id", "use"} for link in links)
    raw = json.dumps(links)
    assert "http" not in raw and "href" not in raw


def test_old_draft_without_seo_opens_with_empty_seo(store):
    saved = store.save(snapshot())
    obj = read_row(store, saved.id)
    del obj["seo"]
    obj["schema_version"] = 1
    for part in obj["parts"]:
        part.pop("chosen_image", None)
    write_row(store, saved.id, obj)
    loaded = store.load(saved.id)
    assert loaded.seo == DraftSeo()
    assert loaded.seo.title.text == "" and loaded.seo.links == [] and not loaded.seo.use_faq
    assert loaded.parts[0].text == "Cửa sắt bị xệ do bản lề mòn."


def test_new_snapshot_has_empty_seo():
    assert snapshot().seo == DraftSeo()
    assert DraftSeo().title.versions == [] and DraftSeo().slug == ""


# ============================================================ dữ liệu sửa tay


@pytest.mark.parametrize(
    "bad_link",
    [
        {"section": -1, "anchor": "bản lề", "post_id": 3, "use": True},
        {"section": 1, "anchor": "bản lề", "post_id": 0, "use": True},
        {"section": 1, "anchor": "", "post_id": 3, "use": True},
        {"section": 1, "anchor": "a" * 101, "post_id": 3, "use": True},
        {"section": "1", "anchor": "bản lề", "post_id": 3, "use": True},
        {"section": 1, "anchor": "bản lề", "post_id": 3.0, "use": True},
        {"section": True, "anchor": "bản lề", "post_id": 3, "use": True},
        {"section": 1, "anchor": "bản lề", "post_id": 3, "use": "true"},
        {"section": 1, "anchor": 5, "post_id": 3, "use": True},
        {"section": 1, "anchor": "bản lề", "post_id": 3, "href": "https://evil.example/"},
        {"section": 1, "anchor": "bản lề"},
        "không phải một liên kết",
        None,
    ],
)
def test_broken_link_is_dropped_alone(store, bad_link):
    draft_id = saved_with(store, lambda obj: obj["seo"]["links"].insert(1, bad_link))
    loaded = store.load(draft_id)
    assert [link.post_id for link in loaded.seo.links] == [10, 11]
    assert loaded.seo.title.text == TITLE and loaded.keyword == "cửa sắt bị xệ"


def test_too_many_links_from_file_keep_first(store):
    def many(obj):
        obj["seo"]["links"] = [
            {"section": 0, "anchor": f"cụm từ {i}", "post_id": i + 1, "use": True}
            for i in range(MAX_DRAFT_LINKS + 5)
        ]

    loaded = store.load(saved_with(store, many))
    assert len(loaded.seo.links) == MAX_DRAFT_LINKS


@pytest.mark.parametrize(
    "change",
    [
        lambda seo: seo.update(title="Cửa sắt"),
        lambda seo: seo.update(description={"versions": "không phải danh sách"}),
        lambda seo: seo.update(slug=123),
        lambda seo: seo.update(use_faq="true"),
        lambda seo: seo.update(links="không phải danh sách"),
        lambda seo: seo.update(khoa_la="sk-ant-abc"),
        lambda seo: seo["title"].update(versions=[1, 2]),
    ],
)
def test_broken_seo_block_is_dropped_article_kept(store, change):
    draft_id = saved_with(store, lambda obj: change(obj["seo"]))
    loaded = store.load(draft_id)
    assert loaded.seo == DraftSeo()
    assert loaded.keyword == "cửa sắt bị xệ" and loaded.parts[0].text.startswith("Cửa sắt")


@pytest.mark.parametrize("seo", [None, "chuỗi", [], 5])
def test_seo_of_wrong_type_is_dropped(store, seo):
    loaded = store.load(saved_with(store, lambda obj: obj.update(seo=seo)))
    assert loaded.seo == DraftSeo()


def test_odd_chars_in_saved_meta_are_cleaned(store):
    def odd(obj):
        obj["seo"]["title"]["versions"] = ["Cửa\x00 sắt​  bị xệ\n<b>x</b>", "%%x%%"]
        obj["seo"]["slug"] = " cua-sat\x1b "

    loaded = store.load(saved_with(store, odd))
    assert loaded.seo.title.versions == ["Cửa sắt bị xệ <b>x</b>", "%%x%%"]
    assert loaded.seo.title.current == 1  # bản đang dùng vẫn là bản cuối
    assert loaded.seo.slug == "cua-sat"


def test_long_meta_text_is_capped(store):
    def long_text(obj):
        obj["seo"]["description"]["versions"] = ["a" * (MAX_SEO_TEXT_CHARS * 10)]

    loaded = store.load(saved_with(store, long_text))
    assert len(loaded.seo.description.text) == MAX_SEO_TEXT_CHARS


# ============================================================ tạo trong code (giao diện)


def test_bad_link_from_code_is_an_error():
    with pytest.raises(ValidationError):
        DraftLink(section=-1, anchor="bản lề", post_id=3)
    with pytest.raises(ValidationError):
        DraftSeo(links=[{"section": 1, "anchor": "", "post_id": 3}])
    with pytest.raises(ValidationError):
        DraftSnapshot(seo={"title": "chuỗi"})
    with pytest.raises(ValidationError):
        DraftSeo(links=[{"section": 0, "anchor": "a b", "post_id": i + 1}
                        for i in range(MAX_DRAFT_LINKS + 1)])  # fmt: skip


def test_from_link_requires_internal_link():
    with pytest.raises(TypeError):
        DraftLink.from_link({"section": 1, "anchor": "bản lề", "post_id": 3})  # type: ignore[arg-type]


def test_save_with_bad_seo_gives_draft_error(store):
    snap = snapshot(full_seo())
    snap.seo.links.append(DraftLink.model_construct(section=-1, anchor="x", post_id=3, use=True))
    from seo_app.storage import DraftError

    with pytest.raises(DraftError, match="sai khuôn"):
        store.save(snap)


# ============================================================ các bản meta


def test_meta_versions_keep_recent_and_clamp_current():
    many = DraftMetaVersions(versions=[f"Bản {i}" for i in range(MAX_META_VERSIONS + 5)], current=7)
    assert len(many.versions) == MAX_META_VERSIONS
    assert many.versions[0] == "Bản 5" and many.current == 2
    assert many.text == "Bản 7"
    assert DraftMetaVersions(versions=["a", "b"], current=9).current == 1
    assert DraftMetaVersions(versions=[], current=3).current == 0
    assert DraftMetaVersions().text == ""
    with pytest.raises(ValidationError):
        DraftMetaVersions(versions=["a"], current=-1)


@pytest.mark.parametrize(
    ("current", "kept_text", "kept_index"),
    [(0, "Bản 0", 0), (3, "Bản 3", 0), (5, "Bản 5", 0), (6, "Bản 6", 1), (24, "Bản 24", 19)],
)
def test_meta_versions_never_drop_the_version_in_use(current, kept_text, kept_index):
    """SL-T041-4: cắt còn 20 bản thì bỏ các bản cũ nhất, trừ bản đang dùng."""
    versions = DraftMetaVersions(versions=[f"Bản {i}" for i in range(25)], current=current)
    assert len(versions.versions) == MAX_META_VERSIONS
    assert versions.text == kept_text and versions.current == kept_index
    assert versions.versions[-1] == "Bản 24"  # bản mới nhất luôn còn


def test_meta_versions_are_normalized_like_meta():
    versions = DraftMetaVersions(versions=["  Cửa\tsắt\n bị xệ ", "Của"])  # NFD
    assert versions.versions == ["Cửa sắt bị xệ", "Của"]
