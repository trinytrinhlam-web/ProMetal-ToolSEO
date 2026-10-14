"""Trang Soạn bài: tự lưu nháp, mở lại, xóa (T-017). AI giả, kho nháp trong thư mục tạm."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
import test_app_pages as pages
from fake_ai import RESEARCH, SCORES
from test_app_pages import button, go_to_article, write_page

import seo_app.storage.drafts as drafts
from seo_app.content.models import Flag, OutlineItem, Review
from seo_app.storage import DraftPart, DraftSnapshot, DraftStore

env = pages.env  # mật khẩu thử, không có khóa AI thật
fake_ai = pages.fake_ai
KW = "so sánh inox 201 và 304"
REVIEW = Review(
    scores=SCORES,
    flags=[Flag(section=1, sentence="Lau bằng nước ngọt.", reason="Ngắn", replacement="")],
    summary="Khá ổn.",
)


def store() -> DraftStore:
    return DraftStore(drafts.DEFAULT_DRAFTS_FILE)


def sample(**changes) -> DraftSnapshot:
    data = dict(
        step=2,
        keyword="cổng inox gần biển",
        material={"Kinh nghiệm của xưởng": "Khách ở Hội An làm cổng 201, 2 năm đã gỉ"},
        research=RESEARCH,
        research_keyword="cổng inox gần biển",
        outline_title="Cổng inox gần biển: chọn loại nào?",
        outline=[
            # Dấu "\" là chữ thật người dùng gõ: mở nháp không được bỏ nó đi (không unescape).
            OutlineItem(heading=r"Giá \[cổng\] 4 m", points=["Theo mét"], image=""),
            OutlineItem(heading="Bảo dưỡng", points=[], image="Cổng sau 3 năm"),
        ],
        article_title="Cổng inox gần biển: 201 hay 304?",
        parts=[
            DraftPart(heading="Mở đầu", versions=["Bản một.", "Bản hai."], current=1),
            DraftPart(heading="Bảo dưỡng", versions=["Lau bằng nước ngọt."], image="Cổng"),
        ],
        review=REVIEW,
        auto_fixed=2,
        ignored_flags={"Câu đã bỏ qua."},
    )
    data.update(changes)
    return DraftSnapshot(**data)


def test_autosave_after_ai_and_shows_saved_time(project_root, fake_ai):
    at = write_page(project_root)
    assert store().list_drafts().drafts == []  # trang trống: chưa lưu gì
    at = go_to_article(at)
    listing = store().list_drafts().drafts
    assert len(listing) == 1
    saved = store().load(listing[0].id)
    assert saved.keyword == KW
    assert saved.step == 2
    pids = at.session_state["part_ids"]
    assert [p.text for p in saved.parts] == [at.session_state[f"texts-{pid}"][0] for pid in pids]
    assert any(c.value.startswith("💾 Đã lưu lúc") for c in at.caption)


def test_user_edits_are_saved_without_a_button(project_root, fake_ai):
    at = go_to_article(write_page(project_root))
    pid = at.session_state["part_ids"][1]
    button(at, "Viết lại phần này", key=f"do-rw-{pid}").click().run()
    draft_id = at.session_state["draft_id"]
    assert store().load(draft_id).parts[1].current == 1
    button(at, "↶", key=f"undo-{pid}").click().run()
    assert store().load(draft_id).parts[1].current == 0
    assert len(store().list_drafts().drafts) == 1  # cùng một nháp, không nhân bản


def test_keyword_and_material_survive_moving_between_steps(project_root, fake_ai):
    at = write_page(project_root)
    at.text_area(key="real-Số liệu của bạn").input("Cổng 4 m giá 18 triệu").run()
    at = go_to_article(at)
    at.run()
    at.run()  # Streamlit xóa giá trị ô không vẽ sau vài lần chạy; trang phải giữ lại
    assert at.session_state["keyword"] == KW
    assert at.session_state["real-Số liệu của bạn"] == "Cổng 4 m giá 18 triệu"
    uid = at.session_state["outline_ids"][0]
    assert at.session_state[f"h-{uid}"]
    saved = store().load(at.session_state["draft_id"])
    assert saved.keyword == KW
    assert saved.material == {"Số liệu của bạn": "Cổng 4 m giá 18 triệu"}


def test_open_sample_draft_restores_step_and_versions(project_root):
    snap = store().save(sample())
    at = write_page(project_root)
    # Chất liệu đang gõ dở của bài khác phải bị xóa khi mở nháp
    at.text_area(key="real-Câu hỏi khách hay hỏi").input("câu của bài khác").run()
    button(at, "Mở", key=f"open-{snap.id}").click().run()
    assert not at.exception, at.exception

    ss = at.session_state
    assert ss["draft_id"] == snap.id
    assert ss["step"] == 2
    assert ss["keyword"] == "cổng inox gần biển"
    assert ss["real-Kinh nghiệm của xưởng"] == "Khách ở Hội An làm cổng 201, 2 năm đã gỉ"
    assert "real-Câu hỏi khách hay hỏi" not in ss
    first, second = ss["part_ids"]
    assert ss[f"texts-{first}"] == ["Bản một.", "Bản hai."]
    assert ss[f"ver-{first}"] == 1
    assert ss[f"img-{second}"] == "Cổng"
    assert ss["ignored_flags"] == {"Câu đã bỏ qua."}
    assert ss["auto_fixed"] == 2
    headings = [ss[f"h-{u}"] for u in ss["outline_ids"]]
    assert headings == [r"Giá \[cổng\] 4 m", "Bảo dưỡng"]
    assert any("Bản hai." in m.value for m in at.markdown)

    # Mở xong không lưu lại ngay: giờ lưu giữ nguyên
    assert store().load(snap.id).saved_at == snap.saved_at
    # Quay lại bản trước vẫn dùng được, và được lưu
    button(at, "↶", key=f"undo-{first}").click().run()
    assert store().load(snap.id).parts[0].current == 0


def test_open_draft_then_outline_step_keeps_text(project_root):
    snap = store().save(sample(step=1))
    at = write_page(project_root)
    button(at, "Mở", key=f"open-{snap.id}").click().run()
    assert at.session_state["step"] == 1
    values = [t.value for t in at.text_input]
    assert r"Giá \[cổng\] 4 m" in values
    assert "Cổng inox gần biển: chọn loại nào?" in values


def test_draft_list_shows_text_without_markdown(project_root):
    title = "[bấm vào đây](https://example.com) **đậm**"
    snap = store().save(sample(article_title=title))
    at = write_page(project_root)
    assert any(t.value == title for t in at.text)
    assert not any("example.com" in m.value for m in at.markdown)
    assert any("Lưu lúc" in t.value for t in at.text)
    assert button(at, "Mở", key=f"open-{snap.id}")


def test_delete_asks_first_then_removes(project_root):
    keep = store().save(sample(keyword="giữ lại"))
    gone = store().save(sample(keyword="xóa đi"))
    at = write_page(project_root)
    assert any(p.proto.popover.label == "🗑️ Xóa" for p in at.get("popover"))
    button(at, "Xóa hẳn", key=f"del-{gone.id}").click().run()
    ids = [d.id for d in store().list_drafts().drafts]
    assert ids == [keep.id]
    assert not at.exception


def test_deleting_open_draft_clears_page_and_does_not_recreate(project_root):
    snap = store().save(sample(step=0))
    at = write_page(project_root)
    button(at, "Mở", key=f"open-{snap.id}").click().run()
    button(at, "Xóa hẳn", key=f"del-{snap.id}").click().run()
    assert not at.exception, at.exception
    assert store().list_drafts().drafts == []
    assert at.session_state["keyword"] == ""
    assert "draft_id" not in at.session_state


def test_opening_missing_draft_shows_error(project_root):
    at = write_page(project_root)
    at.session_state["_open_draft"] = "0" * 32
    at.run()
    assert any("Không tìm thấy nháp" in e.value for e in at.error)
    assert not at.exception


def test_new_article_from_home_starts_new_draft(project_root, fake_ai):
    at = go_to_article(write_page(project_root))
    first = at.session_state["draft_id"]
    at.session_state["_start_keyword"] = "cửa sắt mỹ thuật"
    at.run()
    assert at.session_state.get("draft_id") != first
    assert len(store().list_drafts().drafts) == 2
    assert store().load(first).keyword == KW  # nháp cũ không bị ghi đè


def test_corrupt_drafts_file_is_reported(project_root):
    path = drafts.DEFAULT_DRAFTS_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"day khong phai sqlite")
    at = write_page(project_root)
    assert any("bị hỏng nên đã được cất sang một bên" in w.value for w in at.warning)
    assert not at.exception
    at.run()  # chỉ báo một lần
    assert not any("cất sang một bên" in w.value for w in at.warning)


@pytest.mark.parametrize("step", range(5))
def test_every_step_renders_with_open_draft(project_root, step):
    snap = store().save(sample(step=step))
    at = write_page(project_root)
    button(at, "Mở", key=f"open-{snap.id}").click().run()
    assert not at.exception, at.exception
    assert at.session_state["step"] == step


def test_saved_time_uses_vietnam_time(project_root):
    snap = store().save(sample(step=0))
    at = write_page(project_root)
    button(at, "Mở", key=f"open-{snap.id}").click().run()
    expected = snap.saved_at.astimezone(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%H:%M")
    assert any(c.value == f"💾 Đã lưu lúc {expected}" for c in at.caption)
    assert snap.saved_at.tzinfo is not None
    assert snap.saved_at <= datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))


def test_new_article_clears_material_but_old_draft_keeps_it(project_root, fake_ai):
    at = write_page(project_root)
    at.text_area(key="real-Kinh nghiệm của xưởng").input("Cổng 201 gần biển hay gỉ").run()
    at = go_to_article(at)
    first = at.session_state["draft_id"]
    at.session_state["_start_keyword"] = "cửa sắt mỹ thuật"
    at.session_state["step"] = 0
    at.run()
    assert not at.exception, at.exception
    assert at.session_state["keyword"] == "cửa sắt mỹ thuật"
    assert at.text_area(key="real-Kinh nghiệm của xưởng").value == ""
    new = store().load(at.session_state["draft_id"])
    assert new.material == {}
    assert store().load(first).material == {"Kinh nghiệm của xưởng": "Cổng 201 gần biển hay gỉ"}
