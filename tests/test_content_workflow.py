"""Quy trình viết bài với AI giả: dàn ý, viết, tự rà soát, áp gợi ý, viết lại từng phần."""

import pytest
from fake_ai import DRAFT, OUTLINE, RESEARCH, STIFF, VAGUE, VAGUE_FIX, FakeProvider

from seo_app.ai import AIError, AIRouter, TaskConfig
from seo_app.ai import registry as ai_registry
from seo_app.config import Settings
from seo_app.content import ContentWriter, Section
from seo_app.content.models import Flag
from seo_app.content.rules import ContentRules
from seo_app.content.workflow import apply_replacements, clean_flags, draft_to_parts

TASKS = {
    name: TaskConfig(name=name, provider="anthropic", model="claude-opus-5-5")
    for name in ("research", "outline", "write", "rewrite", "review")
}
RULES = ContentRules(
    business_profile="- Tên thương hiệu: Pro-Metal",
    address="Xưng «chúng tôi»",
    tone="Thân thiện",
    banned=("Có thể thấy rằng", "vô cùng quan trọng"),
    checklist=("Không bịa số liệu",),
)
MATERIAL = {"Kinh nghiệm của xưởng": "Khách gần biển làm cổng 201 hay gỉ mối hàn"}


@pytest.fixture
def fake(monkeypatch):
    provider = FakeProvider()
    monkeypatch.setattr(ai_registry, "make_provider", lambda name, settings: provider)
    return provider


@pytest.fixture
def writer(fake):
    return ContentWriter(AIRouter(TASKS, Settings()), RULES)


def parts() -> list[Section]:
    return draft_to_parts(DRAFT)


def test_draft_to_parts_puts_intro_first():
    result = parts()
    assert result[0].heading == "Mở bài"
    assert [p.heading for p in result[1:]] == [i.heading for i in OUTLINE.items]


def test_clean_flags_fixes_section_number_and_drops_bad_quotes():
    flags = [
        Flag(section=3, sentence=STIFF, reason="", replacement=""),  # sai số phần
        Flag(section=1, sentence=STIFF, reason="", replacement=""),  # trùng
        Flag(section=1, sentence="Câu không có trong bài.", reason="", replacement=""),
        Flag(section=9, sentence=VAGUE, reason="", replacement=""),  # ngoài bài
    ]
    cleaned = clean_flags(parts(), flags)
    assert [(f.section, f.sentence) for f in cleaned] == [(1, STIFF)]


def test_apply_replacements_only_applies_flags_with_a_replacement():
    flags = [
        Flag(section=0, sentence=VAGUE, reason="", replacement=VAGUE_FIX),
        Flag(section=1, sentence=STIFF, reason="", replacement=""),
    ]
    fixed, remaining = apply_replacements(parts(), flags)
    assert VAGUE_FIX in fixed[0].body and VAGUE not in fixed[0].body
    assert remaining == [flags[1]]
    assert parts()[0].body == DRAFT.intro  # bài gốc không bị đổi


def test_write_and_review_fixes_once_then_reviews_again(writer, fake):
    title, result, review, fixed = writer.write_and_review(
        "so sánh inox 201 và 304", RESEARCH, MATERIAL, OUTLINE
    )
    assert title == DRAFT.title
    assert fake.tasks() == ["write", "review", "review"]
    assert fixed == 1
    assert VAGUE_FIX in result[0].body
    # Câu chứa cụm từ cấm được máy tìm ra, kể cả khi AI không đánh dấu.
    assert [(f.section, f.sentence) for f in review.flags] == [(1, STIFF)]
    assert review.scores.natural == 70


def test_scores_are_kept_between_0_and_100(writer, fake, monkeypatch):
    from fake_ai import SCORES

    monkeypatch.setattr(SCORES, "seo", 140)
    review = writer.review("kw", "Tiêu đề", parts())
    assert review.scores.seo == 100


def test_prompts_carry_material_profile_and_rules(writer, fake):
    writer.outline("so sánh inox 201 và 304", RESEARCH, MATERIAL)
    _, system, prompt = fake.calls[-1]
    assert "Pro-Metal" in system
    assert "[cần bổ sung:" in system
    assert "«Có thể thấy rằng»" in system
    assert MATERIAL["Kinh nghiệm của xưởng"] in prompt
    assert "Không có ví dụ công trình thật" in prompt  # đối thủ còn thiếu gì
    assert "(người dùng chưa nhập)" not in prompt


def test_rewrite_section_sends_wishes_and_target(writer, fake):
    body = writer.rewrite_section(
        "kw", "Tiêu đề", parts(), 2, ["Ngắn hơn"], "nhắc tới khách ở Thủ Đức"
    )
    assert body == "Bản viết lại số 1."
    _, _, prompt = fake.calls[-1]
    assert "[Phần 2] «Nên chọn loại nào?»" in prompt
    assert "Ngắn hơn; nhắc tới khách ở Thủ Đức" in prompt


def test_missing_task_in_config_is_reported(fake):
    router = AIRouter({"write": TASKS["write"]}, Settings())
    with pytest.raises(AIError, match=r"\[tasks.review\]"):
        ContentWriter(router, RULES).review("kw", "t", parts())
