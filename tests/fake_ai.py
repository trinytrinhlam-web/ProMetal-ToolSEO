"""AI giả cho test: trả về dữ liệu soạn sẵn theo khuôn, không gọi mạng."""

from __future__ import annotations

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

STIFF = "Có thể thấy rằng việc chọn inox phù hợp là vô cùng quan trọng."
VAGUE = "Inox 304 rất tốt."
VAGUE_FIX = "Cổng 304 ở gần biển vẫn sáng sau nhiều mùa mưa."

RESEARCH = Research(
    intent=["Người đọc sắp làm cổng và phân vân giữa hai loại inox."],
    article_type="So sánh có bảng",
    competitors=[
        Competitor(
            title="Inox 201 và 304 khác nhau thế nào?",
            url="https://example.com/inox",
            covers="Bảng thành phần",
            missing="Không có ví dụ công trình thật",
        )
    ],
    new_angles=["Ảnh thật cổng sau 3 năm"],
    questions=["Inox 304 có bị gỉ không?"],
)

OUTLINE = Outline(
    title="So sánh inox 201 và 304",
    items=[
        OutlineItem(heading="Khác nhau ở đâu?", points=["Thành phần", "Độ bền"], image=""),
        OutlineItem(heading="Nên chọn loại nào?", points=["Theo vị trí"], image="Cổng sau 3 năm"),
        OutlineItem(heading="Chi phí", points=["Chênh lệch"], image=""),
    ],
)

DRAFT = Draft(
    title="So sánh inox 201 và 304: chọn loại nào cho cổng?",
    intro=f"Inox 304 bền hơn 201 ở nơi ẩm. {VAGUE}",
    sections=[
        Section(heading="Khác nhau ở đâu?", body=f"304 nhiều niken hơn. {STIFF}"),
        Section(heading="Nên chọn loại nào?", body="Gần biển thì chọn 304."),
        Section(heading="Chi phí", body="Chênh khoảng [cần bổ sung: giá cổng 4 m của xưởng]."),
    ],
)

SCORES = Scores(friendly=86, natural=70, readable=88, specific=81, seo=90)


class FakeProvider:
    """Ghi lại mọi lần gọi; lần rà soát đầu trả về 1 câu sửa được, các lần sau không còn gì."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str, str]] = []  # (việc, system, prompt)
        self.reviews = 0
        self.rewrites = 0

    def generate(self, task, *, system, prompt, schema):
        self.calls.append((task.name, system, prompt))
        if schema is Research:
            return RESEARCH
        if schema is Outline:
            return OUTLINE
        if schema is Draft:
            return DRAFT
        if schema is SectionText:
            self.rewrites += 1
            return SectionText(body=f"Bản viết lại số {self.rewrites}.")
        if schema is Review:
            self.reviews += 1
            flags = (
                [Flag(section=0, sentence=VAGUE, reason="Chung chung", replacement=VAGUE_FIX)]
                if self.reviews == 1
                else []
            )
            return Review(scores=SCORES, flags=flags, summary="Khá ổn.")
        raise AssertionError(f"Không có dữ liệu giả cho {schema}")

    def tasks(self) -> list[str]:
        return [name for name, _, _ in self.calls]
