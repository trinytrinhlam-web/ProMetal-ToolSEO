"""T-098: đề xuất thay đổi kế hoạch (so bảng, kiểm kết quả AI, cảnh báo; LC-T094-20).

Không gọi mạng, không gọi AI.
"""

from datetime import date

import pytest

from seo_app.content.models import PlanSuggestion, PlanSuggestions
from seo_app.plan import model, propose
from seo_app.plan.model import PlanRow
from seo_app.plan.propose import Action, compare_rows, from_ai
from seo_app.wordpress.client import PublishedItem

TODAY = date(2026, 10, 28)
SITE = "https://suachuacuasat.com"
MARK = "MOI_CHU_TU_KHOA"
POSTS = (
    PublishedItem(id=12, type="page", slug="sua-cua-cuon", link=f"{SITE}/sua-cua-cuon/",
                  title="Sửa cửa cuốn tại nhà"),
    PublishedItem(id=30, type="post", slug="cua-sat-bi-xe", link=f"{SITE}/cua-sat-bi-xe/",
                  title="Cửa sắt bị xệ cạ nền: nguyên nhân và cách chỉnh"),
)  # fmt: skip
CURRENT = (
    PlanRow(key="B-001", keyword="lan can cầu thang sắt", priority="Trung bình",
            planned_date="16/11/2026", title_hint="Lan can cầu thang sắt đẹp", notes="Ghi chú cũ"),
    PlanRow(key="B-002", keyword="sơn tĩnh điện là gì", priority="Thấp", planned_date="20/11/2026"),
    PlanRow(key="B-003", keyword="giá cổng inox 304", status="Đã hẹn giờ", wp_post_id=77,
            planned_date="25/11/2026", planned_time="08:00"),
    PlanRow(key="B-004", keyword="cửa cuốn khe thoáng", status="Đã đăng", wp_post_id=78),
)  # fmt: skip


def by_action(result, action):
    return [p for p in result.items if p.action is action]


def text_of(result) -> str:
    return " ".join(
        [
            *result.notes,
            *(p.reason for p in result.items),
            *(w for p in result.items for w in p.warnings),
        ]
    )


# ------------------------------------------------------------------------------ so bảng


def test_table_adds_new_rows_with_next_key():
    incoming = [PlanRow(keyword="cổng inox 304 mạ vàng có bền không", planned_date="30/11/2026")]
    result = compare_rows(CURRENT, incoming, today=TODAY)
    (add,) = result.items
    assert add.action is Action.ADD and add.key == "B-005" and add.after.key == "B-005"
    assert add.before is None and add.preselected and add.changes == ()
    assert add.after.status == model.STATUS_NEW


def test_table_update_changes_only_given_fields_with_code_reason():
    incoming = [
        PlanRow(keyword="Lan can cầu thang sắt", priority="Cao", planned_date="15/11/2026",
                title_hint=f"Tiêu đề {MARK}")
    ]  # fmt: skip
    (update,) = compare_rows(CURRENT, incoming, today=TODAY).items
    assert update.action is Action.UPDATE and update.key == "B-001"
    assert update.after.notes == "Ghi chú cũ"  # ô trống trong bảng không xóa giá trị đang có
    assert update.after.keyword == "lan can cầu thang sắt"  # khớp theo từ khóa: giữ cách viết cũ
    assert set(update.changes) == {"priority", "planned_date", "title_hint"}
    assert "Ngày dự kiến 16/11/2026 → 15/11/2026" in update.reason
    assert "Ưu tiên Trung bình → Cao" in update.reason
    assert "Tiêu đề dự kiến đổi" in update.reason and MARK not in update.reason
    assert update.preselected


def test_table_unaccented_keyword_does_not_replace_plan_keyword():
    result = compare_rows(CURRENT, [PlanRow(keyword="LAN CAN CAU THANG SAT")], today=TODAY)
    assert result.items == ()


def test_table_matches_by_key_first():
    incoming = [
        PlanRow(key="B-002", keyword="sơn tĩnh điện cho cổng sắt", planned_date="22/11/2026")
    ]
    (update,) = compare_rows(CURRENT, incoming, today=TODAY).items
    assert update.key == "B-002" and update.after.keyword == "sơn tĩnh điện cho cổng sắt"


def test_table_key_not_in_plan_is_new_row_keeping_key():
    (add,) = compare_rows(CURRENT, [PlanRow(key="B-040", keyword="cửa kéo đài loan")]).items
    assert add.action is Action.ADD and add.key == "B-040"


def test_table_never_drops_unless_status_says_so():
    result = compare_rows(CURRENT, [PlanRow(keyword="lan can cầu thang sắt")], today=TODAY)
    assert result.items == ()  # không đổi gì, và các dòng vắng mặt không bị «Bỏ»
    result = compare_rows(CURRENT, [PlanRow(keyword="sơn tĩnh điện là gì", status="Bỏ")])
    (drop,) = result.items
    assert drop.action is Action.DROP and drop.after.status == model.STATUS_DROPPED
    assert not drop.preselected and drop.changes == ("status",)
    assert compare_rows(CURRENT, [PlanRow(keyword="bài chưa có", status="Bỏ")]).items == ()


def test_table_cannot_set_app_fields_or_app_status():
    incoming = [
        PlanRow(keyword="cửa nhôm xingfa", status="Đã đăng", wp_post_id=999),
        PlanRow(key="B-002", keyword="sơn tĩnh điện là gì", status="Đã đăng", wp_post_id=999),
    ]
    (add,) = compare_rows(CURRENT, incoming, today=TODAY).items
    assert add.after.status == model.STATUS_NEW and add.after.wp_post_id is None


def test_table_row_matching_an_already_matched_row_is_skipped():
    incoming = [PlanRow(keyword="sơn tĩnh điện là gì", priority="Cao"),
                PlanRow(keyword="Sơn tĩnh điện là gì", priority="Thấp")]  # fmt: skip
    result = compare_rows(CURRENT, incoming, today=TODAY)
    assert len(result.items) == 1 and result.items[0].after.priority == "Cao"
    assert result.notes == (propose.NOTE_DUPLICATES.format(count=1),)


# ------------------------------------------------------------------------------ cảnh báo


def test_past_date_warning_unticks():
    (add,) = compare_rows(CURRENT, [PlanRow(keyword="cửa nhôm", planned_date="01/10/2026")],
                          today=TODAY).items  # fmt: skip
    assert propose.WARN_PAST in add.warnings and not add.preselected


def test_keyword_duplicate_with_other_row_names_its_key_only():
    (add,) = compare_rows(CURRENT, [PlanRow(key="B-090", keyword="GIÁ CỔNG INOX 304")]).items
    assert propose.WARN_DUPLICATE_ROW.format(key="B-003") in add.warnings


@pytest.mark.parametrize(
    "keyword",
    [
        "sửa cửa cuốn",  # slug trùng bài 12
        "cửa sắt bị xệ cạ nền",  # mọi từ nằm trong tiêu đề bài 30 (≥ 3 từ)
        "Cửa sắt bị xệ cạ nền nguyên nhân và cách chỉnh lại",  # rất giống tiêu đề
    ],
)
def test_duplicate_with_published_post(keyword):
    (add,) = compare_rows(CURRENT, [PlanRow(keyword=keyword)], posts=POSTS, today=TODAY).items
    post_id = 12 if "cuốn" in keyword else 30
    assert propose.WARN_DUPLICATE_POST.format(post_id=post_id) in add.warnings


def test_short_keyword_in_many_titles_is_not_a_duplicate():
    (add,) = compare_rows(CURRENT, [PlanRow(keyword="cửa sắt")], posts=POSTS, today=TODAY).items
    assert not any("bài đã đăng" in w for w in add.warnings)


def test_own_post_is_not_a_duplicate():
    row = PlanRow(key="B-009", keyword="sửa cửa cuốn", wp_post_id=12)
    (update,) = compare_rows([row], [PlanRow(key="B-009", keyword="sửa cửa cuốn", priority="Cao")],
                             posts=POSTS, today=TODAY).items  # fmt: skip
    assert update.warnings == ()


def test_changing_scheduled_or_published_rows_warns():
    incoming = [
        PlanRow(keyword="giá cổng inox 304", planned_date="26/11/2026"),
        PlanRow(keyword="cửa cuốn khe thoáng", status="Bỏ"),
    ]
    update, drop = compare_rows(CURRENT, incoming, today=TODAY).items
    assert propose.WARN_RELEASED in update.warnings and propose.WARN_RELEASED in drop.warnings
    assert not update.preselected and not drop.preselected


def test_update_old_post_kind_warns():
    (add,) = compare_rows(CURRENT, [PlanRow(keyword="cửa kéo", kind="Cập nhật bài cũ")]).items
    assert propose.WARN_UPDATE_OLD in add.warnings


def test_doorway_warning_needs_three_keywords_differing_by_place():
    two = [PlanRow(keyword="sửa cửa cuốn quận 1"), PlanRow(keyword="sửa cửa cuốn quận 3")]
    assert all(not p.warnings for p in compare_rows([], two, today=TODAY).items)
    three = [*two, PlanRow(keyword="sửa cửa cuốn Bình Thạnh")]
    items = compare_rows([], three, today=TODAY).items
    assert all(propose.WARN_DOORWAY in p.warnings for p in items)
    # Từ khóa đã có trong kế hoạch cũng được tính
    current = [PlanRow(key="B-001", keyword="sửa cửa cuốn q7"),
               PlanRow(key="B-002", keyword="sửa cửa cuốn phường Tân Định")]  # fmt: skip
    (add,) = compare_rows(current, [PlanRow(keyword="sửa cửa cuốn huyện Nhà Bè")]).items
    assert propose.WARN_DOORWAY in add.warnings


def test_warnings_and_reasons_never_copy_plan_text():
    incoming = [
        PlanRow(keyword=f"{MARK} cửa cuốn quận 1", planned_date="01/01/2026"),
        PlanRow(keyword=f"{MARK} cửa cuốn quận 2"),
        PlanRow(keyword=f"{MARK} cửa cuốn quận 3", kind="Cập nhật bài cũ"),
        PlanRow(keyword=f"{MARK} cửa cuốn quận 3"),
    ]
    result = compare_rows(CURRENT, incoming, posts=POSTS, today=TODAY)
    assert MARK not in text_of(result)


# ------------------------------------------------------------------------------ AI


def ai(*items, **kwargs):
    return from_ai(PlanSuggestions(items=list(items)), CURRENT, today=TODAY, **kwargs)


def suggestion(**fields):
    """Một mục AI: trường không nêu là chuỗi rỗng (khuôn đòi đủ mọi trường)."""
    fields.setdefault("reason", "Ghi chú yêu cầu.")
    return PlanSuggestion.model_validate(
        {name: "" for name in PlanSuggestion.model_fields} | fields
    )


def test_ai_valid_add_update_drop():
    result = ai(
        suggestion(action="them", keyword="kích thước cổng nhà phố 4m", priority="Trung bình",
                   planned_date="24/11/2026", notes="Khách hay hỏi"),
        suggestion(action="cap_nhat", key="B-001", priority="Cao", planned_date="15/11/2026"),
        suggestion(action="bo", key="b-002", reason="Đã có bài cũ trên web"),
    )  # fmt: skip
    assert result.dropped == 0 and result.notes == ()
    add, update, drop = result.items
    assert add.action is Action.ADD and add.key == "B-005" and add.source == propose.SOURCE_AI
    assert add.after.planned_date == date(2026, 11, 24) and add.preselected
    assert update.after.priority == "Cao" and update.after.notes == "Ghi chú cũ"
    assert set(update.changes) == {"priority", "planned_date"}
    assert drop.action is Action.DROP and drop.key == "B-002" and not drop.preselected
    assert drop.reason == "Đã có bài cũ trên web"


@pytest.mark.parametrize(
    "bad",
    [
        {"action": "xoa", "key": "B-001"},
        {"action": "them", "keyword": "cửa nhôm", "reason": ""},
        {"action": "them", "keyword": "cửa nhôm", "reason": "x" * 301},
        {"action": "them", "keyword": "cửa nhôm", "reason": "<b>vì</b> cần"},
        {"action": "them", "keyword": "cửa nhôm", "intent": "Local service"},
        {"action": "them", "keyword": "cửa nhôm", "planned_date": "15/10"},
        {"action": "them", "keyword": "cửa nhôm", "planned_date": "10/15/2026"},
        {"action": "them", "keyword": "cửa nhôm", "planned_date": "01/01/2040"},
        {"action": "them", "keyword": "cửa nhôm", "planned_time": "25:00"},
        {"action": "them", "key": "B-001", "keyword": "cửa nhôm"},
        {"action": "them"},
        {"action": "them", "keyword": "x"},
        {"action": "them", "keyword": "cửa nhôm", "notes": "<script>alert(1)</script>"},
        {"action": "them", "keyword": "cửa nhôm", "title_hint": "a" * 201},
        {"action": "cap_nhat", "key": "B-999", "priority": "Cao"},
        {"action": "cap_nhat", "key": "", "priority": "Cao"},
        {"action": "bo", "key": "B-404"},
    ],
)
def test_ai_invalid_items_are_dropped_and_only_counted(bad):
    result = ai(suggestion(**bad))
    assert result.items == () and result.dropped == 1
    assert result.notes == (propose.NOTE_AI_DROPPED.format(count=1),)


def test_ai_same_key_twice_keeps_first():
    result = ai(
        suggestion(action="cap_nhat", key="B-001", priority="Cao"),
        suggestion(action="bo", key="B-001"),
    )
    assert [p.action for p in result.items] == [Action.UPDATE] and result.dropped == 1


def test_ai_no_op_update_is_skipped_not_counted():
    result = ai(suggestion(action="cap_nhat", key="B-001", priority="Trung bình"))
    assert result.items == () and result.dropped == 0


def test_ai_more_than_100_items_extra_dropped():
    items = [suggestion(action="them", keyword=f"cửa cuốn mẫu {i}") for i in range(150)]
    result = ai(*items)
    assert len(result.items) == propose.MAX_AI_ITEMS and result.dropped == 50


def test_ai_cannot_set_address_slug_or_target():
    item = suggestion(
        action="them",
        keyword="cửa nhôm",
        reason="Xem https://evil.example",
        notes="Tham khảo https://evil.example/x",
        slug="evil",  # trường lạ: khuôn bỏ qua
        target_id=12,
        target_url="https://evil.example",
    )
    assert "slug" not in item.model_dump() and "target_id" not in item.model_dump()
    (add,) = ai(item).items
    assert add.after.slug == "" and add.after.target_id is None
    assert add.after.notes == "Tham khảo https://evil.example/x"  # chỉ là chữ


def test_ai_reason_is_cleaned_text():
    (add,) = ai(
        suggestion(action="them", keyword="cửa nhôm", reason="Vì\u202e cần\u200b thêm")
    ).items
    assert add.reason == "Vì cần thêm"


def test_ai_suggestions_get_the_same_warnings():
    result = from_ai(
        PlanSuggestions(items=[suggestion(action="them", keyword="sửa cửa cuốn",
                                          planned_date="01/10/2026")]),
        CURRENT, posts=POSTS, today=TODAY,
    )  # fmt: skip
    (add,) = result.items
    assert propose.WARN_PAST in add.warnings
    assert propose.WARN_DUPLICATE_POST.format(post_id=12) in add.warnings


def test_from_ai_requires_the_schema():
    with pytest.raises(TypeError):
        from_ai({"items": []}, CURRENT)
