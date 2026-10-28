"""Quy trình viết bài với AI: nghiên cứu → dàn ý → viết → tự rà soát → viết lại từng phần.

Bài viết được giữ dưới dạng danh sách ``Section``: phần 0 là mở bài, các phần sau là các mục.
"""

from __future__ import annotations

import dataclasses
import re
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from seo_app.ai import AIError, AIRouter
from seo_app.content import prompts
from seo_app.content.models import (
    Competitor,
    Draft,
    Flag,
    Outline,
    OutlineItem,
    PlanSuggestions,
    Research,
    Review,
    Scores,
    Section,
    SectionText,
)
from seo_app.content.rules import ContentRules, MetaRules, find_banned, load_meta_rules
from seo_app.onpage import meta as onpage_meta
from seo_app.sanitize import break_autolinks, clean_ai_text, escape_link_syntax, strip_tags

if TYPE_CHECKING:  # chỉ để ghi kiểu: onpage.links → storage → drafts → workflow (vòng nhập)
    from datetime import date

    from seo_app.onpage.links import Candidates, LinkReview
    from seo_app.plan.model import PlanRow
    from seo_app.plan.propose import ProposalSet

INTRO_HEADING = "Mở bài"

# Việc AI đọc kế hoạch dạng chữ tự do (T-098). Mục [tasks.plan] của config/ai.toml do T-103 thêm;
# máy chưa có mục đó thì tạm dùng hãng, mô hình, effort của việc «outline» (thiết kế T-094 mục 6:
# cùng mô hình với outline cho tới khi chủ dự án đổi), max_tokens ít nhất PLAN_MAX_TOKENS.
PLAN_TASK = "plan"
PLAN_FALLBACK_TASK = "outline"
PLAN_MAX_TOKENS = 16000
PLAN_EMPTY = "Chưa có nội dung kế hoạch để AI đọc. Dán ghi chú định hướng rồi bấm lại."
PLAN_TOO_LONG = "Ghi chú kế hoạch dài quá {limit:,} ký tự. Chia nhỏ rồi gửi từng phần."
PLAN_BAD_SHAPE = "AI trả về đề xuất không đúng khuôn. Bấm thử lại."
PERSONAL_INFO = (
    "Chữ kế hoạch có {phones} số điện thoại và {emails} email (có thể của khách). Chưa gửi cho AI: "
    "che các chỗ đó trước, hoặc xác nhận vẫn gửi."
)


class PersonalInfoError(AIError):
    """Chữ kế hoạch có số điện thoại, email: chưa gửi AI, chờ người dùng che hay đồng ý (A3,
    LC-T094-21). Câu báo chỉ nêu số lượng, không chép chữ tìm thấy."""


def clean_ai_line(text: str) -> str:
    """Chữ một dòng do AI tạo (tiêu đề bài, tiêu đề mục): lọc như thân bài rồi gộp thành một dòng.

    Tiêu đề cũng được hiển thị bằng Markdown (``## tiêu đề``, ``:gray[tiêu đề]``) nên cũng phải
    không thể thành link (Soi Lỗi R3-3).
    """
    return " ".join(clean_ai_text(text).split())


def clean_draft(draft: Draft) -> Draft:
    """Kết quả AI là dữ liệu chưa tin cậy: bỏ thẻ HTML và link ẩn trước khi dùng."""
    return Draft(
        title=clean_ai_line(draft.title),
        intro=clean_ai_text(draft.intro),
        sections=[
            Section(heading=clean_ai_line(s.heading), body=clean_ai_text(s.body))
            for s in draft.sections
        ],
    )


def _clean_list(items: Sequence[str]) -> list[str]:
    return [clean_ai_text(item) for item in items]


# Đường dẫn bài đối thủ: chỉ nhận một địa chỉ http(s) liền mạch (không dấu cách, không < > "),
# để không ghép được thêm cú pháp Markdown (ảnh từ máy chủ lạ…) khi hiển thị (Lá Chắn #4).
_PLAIN_URL = re.compile(r"https?://[^\s<>\"]+", re.IGNORECASE)


def _clean_url(url: str) -> str:
    url = strip_tags(url).strip()
    return url if _PLAIN_URL.fullmatch(url) else ""


def clean_research(research: Research) -> Research:
    """Kết quả nghiên cứu (có cả chữ chép từ trang đối thủ) cũng là dữ liệu chưa tin cậy.

    Tên bài đối thủ chỉ bỏ thẻ: trang Soạn bài hiển thị nó qua ``markdown_link`` (escape mọi ký
    tự Markdown), nếu escape thêm ở đây thì dấu "\\" sẽ hiện ra.
    """
    return Research(
        intent=_clean_list(research.intent),
        article_type=clean_ai_text(research.article_type),
        competitors=[
            Competitor(
                title=strip_tags(c.title).strip(),
                url=_clean_url(c.url),
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
        title=clean_ai_line(outline.title),
        items=[
            OutlineItem(
                heading=clean_ai_line(item.heading),
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
                "reason": clean_ai_text(flag.reason),
            }
        )
        for flag in review.flags
    ]
    return Review(scores=review.scores, flags=flags, summary=clean_ai_text(review.summary))


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
        # Bài đã có ký tự ngắt ở địa chỉ trần (T-031); câu AI chép lại thường không có.
        sentence = break_autolinks(flag.sentence.strip())
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
    """Thay (hoặc bỏ) một câu trong một phần của bài.

    Chỗ nối có thể ghép hai mảnh "sạch" thành thứ nguy hiểm: "<" cuối phần trước với
    "a href=…>" của câu thay thế thành thẻ HTML, "[chữ]" với "(địa chỉ)" thành link. Vì vậy lọc
    trên KẾT QUẢ SAU KHI GHÉP, ở cả hai nhánh: bỏ thẻ (``strip_tags``, Lá Chắn T-015 #1) rồi
    escape cú pháp link. Câu thay thế cũng được bỏ thẻ trước khi ghép. Cái giá: HTML người
    dùng tự gõ trong phần này cũng bị bỏ khi áp gợi ý (thân bài là Markdown).
    """
    if replacement:
        joined = body.replace(sentence, strip_tags(replacement))
    else:
        joined = body.replace(sentence + " ", "").replace(sentence, "").strip()
    return escape_link_syntax(strip_tags(joined))


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
    def __init__(
        self, ai: AIRouter, rules: ContentRules, meta_rules: MetaRules | None = None
    ) -> None:
        """``meta_rules``: mục ``[meta]`` của ``config/content.toml``; ``None`` thì đọc file mỗi
        lần gợi ý meta (sửa file rồi bấm lại là có hiệu lực, như các mục khác)."""
        self.ai = ai
        self.rules = rules
        self.meta_rules = meta_rules
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
        return draft.title or clean_ai_line(outline.title), draft_to_parts(draft)

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

    # 6. Gợi ý meta title / meta description (T-036)
    def meta(
        self,
        keyword: str,
        title: str,
        parts: Sequence[Section],
        which: str = "both",
        current_title: str = "",
        current_description: str = "",
        brand_suffix: object = None,
    ) -> prompts.MetaSuggestions:
        """AI gợi ý meta; code kiểm từng gợi ý (``seo_app/onpage/meta.py``), bỏ gợi ý hỏng.

        ``which`` = "title" hoặc "description": viết lại riêng phần đó, danh sách của phần kia
        trả về rỗng (người dùng giữ nguyên phần kia). Phần được yêu cầu mà mọi gợi ý đều hỏng
        thì báo ``AIError`` để người dùng bấm viết lại. ``brand_suffix``: hậu tố thương hiệu;
        ``None`` thì lấy ``brand_suffix`` trong mục ``[meta]`` (cấu hình sai thì dùng mặc định
        ``onpage_meta.BRAND_SUFFIX``). Gợi ý có cụm trong ``[meta].avoid`` (ngoài từ khóa chính)
        bị bỏ. Mục ``[meta]`` sai dạng: ``ContentRulesError`` (một loại ``AIError``).
        """
        if which not in prompts.META_PARTS:
            raise ValueError(f"which phải là một trong {prompts.META_PARTS}")
        keyword = onpage_meta.normalize_meta(keyword)
        if not keyword:
            raise AIError("Chưa có từ khóa chính nên chưa gợi ý meta được. Nhập từ khóa trước.")
        meta_rules = self.meta_rules if self.meta_rules is not None else load_meta_rules()
        if brand_suffix is None:
            brand_suffix = meta_rules.brand_suffix
        prompt = prompts.meta_prompt(
            keyword, title, parts, which, current_title, current_description, brand_suffix
        )
        raw = self._run("meta", prompt, prompts.MetaSuggestions)
        titles: list[str] = []
        descriptions: list[str] = []
        if which in ("both", "title"):
            titles = onpage_meta.filter_ai_titles(
                raw.titles, keyword, self.rules.banned, brand_suffix, meta_rules.avoid
            )
            if not titles:
                raise AIError(
                    "Các meta title AI gợi ý đều không đạt (thiếu từ khóa, dài/ngắn quá, có link,"
                    " giá hoặc cụm sáo rỗng). Bấm viết lại."
                )
        if which in ("both", "description"):
            descriptions = onpage_meta.filter_ai_descriptions(
                raw.descriptions, keyword, self.rules.banned, meta_rules.avoid
            )
            if not descriptions:
                raise AIError(
                    "Các meta description AI gợi ý đều không đạt (thiếu từ khóa, dài/ngắn quá,"
                    " có link, giá hoặc cụm sáo rỗng). Bấm viết lại."
                )
        return prompts.MetaSuggestions(titles=titles, descriptions=descriptions)

    # 6. Gợi ý liên kết nội bộ (T-039 kiểm, T-041 gọi AI)
    def internal_links(
        self, title: str, parts: Sequence[Section], candidates: Candidates
    ) -> LinkReview:
        """AI gợi ý chỗ đặt link tới các bài đích do code chọn (``links.select_candidates``).

        Điều kiện Lá Chắn T-039 số 2a: AI chỉ nhận ID và tiêu đề bài đích (không địa chỉ) trong
        khung dữ liệu, chỉ trả ``LinkSuggestions``; code kiểm từng gợi ý (``check_suggestions``),
        không dùng trường nào khác của câu trả lời. Việc ``links`` trong ``config/ai.toml`` bật
        ``web_search`` thì từ chối (lời dặn có tiêu đề lấy từ website). Không có bài đích nào thì
        không gọi AI. Gợi ý đạt là ``InternalLink`` (``LinkReview.links``); link chỉ được chèn
        qua ``apply_links``/``place_links``.
        """
        from seo_app.onpage import links  # nhập muộn: links → storage → drafts → workflow

        if not candidates.items:
            return links.LinkReview((), (), ())
        _, task = self.ai.get("links")
        if task.web_search:
            raise AIError(
                "Việc gợi ý liên kết nội bộ không được bật web_search: xóa dòng web_search ở mục "
                "[tasks.links] trong file config/ai.toml."
            )
        prompt = prompts.internal_links_prompt(title, parts, candidates.for_prompt())
        raw = self._run("links", prompt, links.LinkSuggestions)
        return links.check_suggestions(raw, parts, candidates)

    # Kế hoạch: AI đọc ghi chú định hướng dạng chữ tự do, đề xuất thay đổi (T-098)
    def plan_changes(
        self,
        current: Sequence[PlanRow],
        text: str,
        *,
        today: date | None = None,
        posts: Sequence[object] = (),
        allow_personal: bool = False,
    ) -> ProposalSet:
        """AI đọc chữ tự do ``text`` (ghi chú định hướng người dùng dán) và đề xuất thay đổi kế
        hoạch ``current``; code kiểm từng đề xuất (``seo_app.plan.propose.from_ai``), thêm cảnh
        báo (trùng bài đã đăng trong ``posts``, ngày đã qua…).

        An toàn: chữ qua bộ làm sạch của kế hoạch, ≤ ``MAX_PASTE_CHARS`` ký tự; kế hoạch hiện tại và
        chữ dán mỗi thứ một khung dữ liệu (``prompts.plan_prompt``), lời dặn hệ thống có
        ``DATA_RULES``. Việc ``plan`` **không bao giờ** tìm web, dù ``config/ai.toml`` bật
        (LC-T094-19). Chữ có số điện thoại, email thì báo ``PersonalInfoError`` và không gửi, trừ
        khi ``allow_personal`` (người dùng đã thấy cảnh báo và đồng ý; hoặc che bằng
        ``seo_app.plan.model.mask_personal_info`` rồi gửi lại) (A3, LC-T094-21).
        """
        from seo_app.plan import model as plan_model  # nhập muộn: plan → content (vòng nhập)
        from seo_app.plan import propose

        body = plan_model.clean_text(text, multiline=True)
        if not body:
            raise AIError(PLAN_EMPTY)
        if len(body) > plan_model.MAX_PASTE_CHARS:
            raise AIError(PLAN_TOO_LONG.format(limit=plan_model.MAX_PASTE_CHARS))
        sent = "\n".join([body, *(row.keyword for row in current)])
        phones, emails = plan_model.personal_info(sent)
        if (phones or emails) and not allow_personal:
            raise PersonalInfoError(PERSONAL_INFO.format(phones=phones, emails=emails))
        today = today or plan_model.today_vn()
        provider, task = self._plan_task()
        prompt = prompts.plan_prompt(current, body, today)
        raw = provider.generate(task, system=self.system, prompt=prompt, schema=PlanSuggestions)
        if not isinstance(raw, PlanSuggestions):
            raise AIError(PLAN_BAD_SHAPE)
        try:
            return propose.from_ai(raw, current, posts=posts, today=today)
        except plan_model.PlanKeyError as exc:  # hết Mã bài trống: câu cố định, như mọi lỗi AI
            raise AIError(str(exc)) from None

    def _plan_task(self):
        """Provider và cấu hình cho việc ``plan``: mục ``[tasks.plan]`` nếu có, không thì cấu hình
        của ``outline`` đổi tên (tạm tới T-103). Luôn tắt tìm web."""
        tasks = getattr(self.ai, "tasks", {})
        name = PLAN_TASK if PLAN_TASK in tasks else PLAN_FALLBACK_TASK
        provider, task = self.ai.get(name)
        if name != PLAN_TASK:
            task = dataclasses.replace(
                task, name=PLAN_TASK, max_tokens=max(task.max_tokens, PLAN_MAX_TOKENS)
            )
        return provider, dataclasses.replace(task, web_search=False)
