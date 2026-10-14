"""Quy trình viết bài với AI: nghiên cứu → dàn ý → viết → tự rà soát → viết lại từng phần.

Bài viết được giữ dưới dạng danh sách ``Section``: phần 0 là mở bài, các phần sau là các mục.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from seo_app.ai import AIError, AIRouter
from seo_app.content import prompts
from seo_app.content.models import (
    Competitor,
    Draft,
    Flag,
    Outline,
    OutlineItem,
    Research,
    Review,
    Scores,
    Section,
    SectionText,
)
from seo_app.content.rules import ContentRules, find_banned
from seo_app.sanitize import clean_ai_text, strip_tags

INTRO_HEADING = "Mở bài"


def clean_draft(draft: Draft) -> Draft:
    """Kết quả AI là dữ liệu chưa tin cậy: bỏ thẻ HTML và link ẩn trước khi dùng."""
    return Draft(
        title=strip_tags(draft.title).strip(),
        intro=clean_ai_text(draft.intro),
        sections=[
            Section(heading=strip_tags(s.heading).strip(), body=clean_ai_text(s.body))
            for s in draft.sections
        ],
    )


def _clean_list(items: Sequence[str]) -> list[str]:
    return [clean_ai_text(item) for item in items]


def clean_research(research: Research) -> Research:
    """Kết quả nghiên cứu (có cả chữ chép từ trang đối thủ) cũng là dữ liệu chưa tin cậy."""
    return Research(
        intent=_clean_list(research.intent),
        article_type=clean_ai_text(research.article_type),
        competitors=[
            Competitor(
                title=strip_tags(c.title).strip(),
                url=strip_tags(c.url).strip(),
                covers=clean_ai_text(c.covers),
                missing=clean_ai_text(c.missing),
            )
            for c in research.competitors
        ],
        new_angles=_clean_list(research.new_angles),
        questions=_clean_list(research.questions),
    )


def clean_outline(outline: Outline) -> Outline:
    return Outline(
        title=strip_tags(outline.title).strip(),
        items=[
            OutlineItem(
                heading=strip_tags(item.heading).strip(),
                points=_clean_list(item.points),
                image=clean_ai_text(item.image),
            )
            for item in outline.items
        ],
    )


def clean_review(review: Review) -> Review:
    """Câu thay thế và lời nhận xét AI đề xuất cũng được lọc như thân bài."""
    flags = [
        flag.model_copy(
            update={
                "replacement": clean_ai_text(flag.replacement),
                "reason": strip_tags(flag.reason).strip(),
            }
        )
        for flag in review.flags
    ]
    return Review(scores=review.scores, flags=flags, summary=strip_tags(review.summary).strip())


def draft_to_parts(draft: Draft) -> list[Section]:
    return [Section(heading=INTRO_HEADING, body=draft.intro), *draft.sections]


def banned_flags(parts: Sequence[Section], rules: ContentRules) -> list[Flag]:
    """Câu chứa cụm từ cấm — tìm bằng máy, không cần AI."""
    return [
        Flag(
            section=i,
            sentence=sentence,
            reason=f"Có cụm sáo rỗng «{phrase}».",
            replacement="",
        )
        for i, part in enumerate(parts)
        for sentence, phrase in find_banned(part.body, rules.banned)
    ]


def clean_flags(parts: Sequence[Section], flags: Sequence[Flag]) -> list[Flag]:
    """Bỏ các gợi ý chỉ sai phần, chép sai câu, hoặc trùng nhau."""
    seen: set[str] = set()
    result = []
    for flag in flags:
        sentence = flag.sentence.strip()
        if not sentence or sentence in seen or not 0 <= flag.section < len(parts):
            continue
        if sentence not in parts[flag.section].body:
            # AI đôi khi ghi nhầm số phần: tìm câu đó ở phần khác.
            owner = next((i for i, p in enumerate(parts) if sentence in p.body), None)
            if owner is None:
                continue
            flag = flag.model_copy(update={"section": owner})
        seen.add(sentence)
        result.append(flag.model_copy(update={"sentence": sentence}))
    return result


def apply_flag(body: str, sentence: str, replacement: str) -> str:
    if replacement:
        return body.replace(sentence, replacement)
    return body.replace(sentence + " ", "").replace(sentence, "").strip()


def apply_replacements(
    parts: Sequence[Section], flags: Sequence[Flag]
) -> tuple[list[Section], list[Flag]]:
    """Áp các gợi ý có câu thay thế; trả về (bài đã sửa, các gợi ý còn lại cho người dùng)."""
    new_parts = [p.model_copy() for p in parts]
    remaining = []
    for flag in flags:
        part = new_parts[flag.section]
        if flag.replacement.strip() and flag.sentence in part.body:
            part.body = apply_flag(part.body, flag.sentence, flag.replacement.strip())
        else:
            remaining.append(flag)
    return new_parts, remaining


def clamp_scores(scores: Scores) -> Scores:
    return Scores(**{k: max(0, min(100, int(v))) for k, v in scores.model_dump().items()})


class ContentWriter:
    def __init__(self, ai: AIRouter, rules: ContentRules) -> None:
        self.ai = ai
        self.rules = rules
        self.system = prompts.system_prompt(rules)

    def _run(self, task: str, prompt: str, schema):
        provider, config = self.ai.get(task)
        return provider.generate(config, system=self.system, prompt=prompt, schema=schema)

    # 1-2. Ý định tìm kiếm + đối thủ
    def research(self, keyword: str) -> Research:
        return clean_research(self._run("research", prompts.research_prompt(keyword), Research))

    # 4. Dàn ý
    def outline(self, keyword: str, research: Research, material: Mapping[str, str]) -> Outline:
        prompt = prompts.outline_prompt(keyword, research, material)
        return clean_outline(self._run("outline", prompt, Outline))

    # 4. Viết toàn bài (sau khi người dùng duyệt dàn ý)
    def write(
        self, keyword: str, research: Research, material: Mapping[str, str], outline: Outline
    ) -> tuple[str, list[Section]]:
        draft = clean_draft(
            self._run("write", prompts.write_prompt(keyword, research, material, outline), Draft)
        )
        if not draft.intro and not any(s.body for s in draft.sections):
            raise AIError("AI trả về bài rỗng (không có mở bài, không có nội dung). Bấm thử lại.")
        # Tiêu đề dàn ý có thể do người dùng sửa tay, nên vẫn lọc lại khi dùng làm tiêu đề bài.
        return draft.title or strip_tags(outline.title).strip(), draft_to_parts(draft)

    # 5. Rà soát theo checklist
    def review(self, keyword: str, title: str, parts: Sequence[Section]) -> Review:
        review = clean_review(
            self._run("review", prompts.review_prompt(keyword, title, parts, self.rules), Review)
        )
        flags = clean_flags(parts, [*banned_flags(parts, self.rules), *review.flags])
        return Review(scores=clamp_scores(review.scores), flags=flags, summary=review.summary)

    def write_and_review(
        self, keyword: str, research: Research, material: Mapping[str, str], outline: Outline
    ) -> tuple[str, list[Section], Review, int]:
        """Viết bài, AI tự rà soát và sửa một lượt, rồi chấm lại.

        Trả về (tiêu đề, bài, kết quả rà soát lần cuối, số câu AI đã tự sửa).
        """
        title, parts = self.write(keyword, research, material, outline)
        first = self.review(keyword, title, parts)
        fixable = [f for f in first.flags if f.replacement.strip()]
        if not fixable:
            return title, parts, first, 0
        parts, _ = apply_replacements(parts, fixable)
        return title, parts, self.review(keyword, title, parts), len(fixable)

    # Viết lại một phần theo yêu cầu của người dùng
    def rewrite_section(
        self,
        keyword: str,
        title: str,
        parts: Sequence[Section],
        index: int,
        styles: Sequence[str] = (),
        note: str = "",
    ) -> str:
        prompt = prompts.rewrite_prompt(keyword, title, parts, index, styles, note)
        body = clean_ai_text(self._run("rewrite", prompt, SectionText).body)
        if not body:
            raise AIError("AI trả về bản viết lại rỗng. Bấm thử lại hoặc đổi yêu cầu.")
        return body
