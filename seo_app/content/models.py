"""Khuôn dữ liệu AI phải trả về ở từng bước viết bài (đã kiểm tra trước khi dùng)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Competitor(BaseModel):
    title: str = Field(description="Tiêu đề bài đứng đầu Google")
    url: str = Field(description="Đường dẫn bài đó, chép đúng từ kết quả tìm kiếm")
    covers: str = Field(description="Bài đó đã nói được gì, một câu")
    missing: str = Field(description="Bài đó còn thiếu gì người đọc cần, một câu")


class Research(BaseModel):
    intent: list[str] = Field(description="2-4 câu: người tìm là ai, muốn biết/làm gì")
    article_type: str = Field(description="Dạng bài hợp nhất, ví dụ: so sánh có bảng, hướng dẫn")
    competitors: list[Competitor]
    new_angles: list[str] = Field(description="2-4 điều bài mình phải có mà đối thủ thiếu")
    questions: list[str] = Field(description="Câu hỏi người tìm hay thắc mắc thêm")


class OutlineItem(BaseModel):
    heading: str = Field(description="Tiêu đề mục (H2)")
    points: list[str] = Field(description="Các ý chính sẽ viết trong mục")
    image: str = Field(description="Ảnh nên đặt ở mục này để làm gì; để trống nếu không cần")


class Outline(BaseModel):
    title: str = Field(description="Tiêu đề bài (H1)")
    items: list[OutlineItem]


class Section(BaseModel):
    heading: str
    body: str = Field(description="Nội dung mục, định dạng Markdown, không lặp lại tiêu đề")


class Draft(BaseModel):
    title: str
    intro: str = Field(description="Đoạn mở bài, Markdown")
    sections: list[Section] = Field(description="Đúng thứ tự và tiêu đề như dàn ý")


class SectionText(BaseModel):
    body: str = Field(description="Nội dung mới của mục, Markdown, không lặp lại tiêu đề")


class Flag(BaseModel):
    section: int = Field(description="Số thứ tự phần: 0 = mở bài, 1 = mục thứ nhất, …")
    sentence: str = Field(description="Câu có vấn đề, chép NGUYÊN VĂN từ bài")
    reason: str = Field(description="Vì sao cần sửa, ngắn gọn")
    replacement: str = Field(description="Câu thay thế; để trống nếu nên bỏ hẳn câu này")


class Scores(BaseModel):
    friendly: int = Field(description="Thân thiện, 0-100")
    natural: int = Field(description="Tự nhiên, không máy móc, 0-100")
    readable: int = Field(description="Dễ đọc, 0-100")
    specific: int = Field(description="Cụ thể, có ích, 0-100")
    seo: int = Field(description="Chuẩn SEO, 0-100")


class Review(BaseModel):
    scores: Scores
    flags: list[Flag]
    summary: str = Field(description="Nhận xét chung một câu")


class PlanSuggestion(BaseModel):
    """Một đề xuất thay đổi kế hoạch AI trả về (T-098). Code kiểm từng mục (``seo_app.plan.propose
    .from_ai``), mục sai bị bỏ. Không có trường slug, trang đích, địa chỉ web: AI không đưa được
    địa chỉ nào vào kế hoạch (LC-T094-20). Mọi trường là chữ (kể cả ngày) để một mục viết sai
    không làm hỏng cả câu trả lời; trường không đổi là chuỗi rỗng. Không đặt giá trị mặc định
    (như các khuôn AI khác): khuôn «strict» của OpenAI đòi đủ mọi trường."""

    action: str = Field(description='"them" (bài mới), "cap_nhat" (sửa bài có sẵn) hoặc "bo"')
    key: str = Field(
        description="Mã bài có sẵn trong kế hoạch hiện tại (bắt buộc khi cap_nhat, bo); "
        "chuỗi rỗng khi them"
    )
    keyword: str = Field(description="Từ khóa chính (bắt buộc khi them); rỗng nếu không đổi")
    secondary: str = Field(description="Từ khóa phụ, ý cần có; rỗng nếu không đổi")
    intent: str = Field(description="Ý định; rỗng nếu không đổi")
    kind: str = Field(description="Loại trang; rỗng nếu không đổi")
    priority: str = Field(description="Cao, Trung bình hoặc Thấp; rỗng nếu không đổi")
    planned_date: str = Field(description="Ngày dự kiến dd/mm/yyyy; rỗng nếu không đổi")
    planned_time: str = Field(description="Giờ đăng HH:MM; rỗng nếu không đổi")
    title_hint: str = Field(description="Tiêu đề dự kiến; rỗng nếu không đổi")
    notes: str = Field(description="Ghi chú; rỗng nếu không đổi")
    reason: str = Field(description="Lý do ngắn, một câu, bằng lời của người dùng đọc được")


class PlanSuggestions(BaseModel):
    """Khuôn AI trả về khi đọc kế hoạch dạng chữ tự do (T-098)."""

    items: list[PlanSuggestion] = Field(description="Các thay đổi đề xuất, tối đa 100 mục")


SCORE_LABELS = {
    "friendly": "Thân thiện",
    "natural": "Tự nhiên, không máy móc",
    "readable": "Dễ đọc",
    "specific": "Cụ thể, có ích",
    "seo": "Chuẩn SEO",
}
