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


SCORE_LABELS = {
    "friendly": "Thân thiện",
    "natural": "Tự nhiên, không máy móc",
    "readable": "Dễ đọc",
    "specific": "Cụ thể, có ích",
    "seo": "Chuẩn SEO",
}
