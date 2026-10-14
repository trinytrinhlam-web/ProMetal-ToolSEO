"""Lời dặn (prompt) gửi AI ở từng bước. Viết bằng tiếng Việt vì bài viết bằng tiếng Việt."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from seo_app.content.models import Outline, Research, Section
from seo_app.content.rules import ContentRules

NO_MATERIAL = "(người dùng chưa nhập)"


def system_prompt(rules: ContentRules) -> str:
    business = rules.business_profile or "(chưa có hồ sơ doanh nghiệp: không nêu thông tin riêng)"
    banned = ", ".join(f"«{p}»" for p in rules.banned)
    return f"""Bạn là biên tập viên SEO viết bài tiếng Việt cho website của một xưởng cơ khí.
Chỉ dùng thông tin về doanh nghiệp có trong hồ sơ dưới đây.

<ho_so_doanh_nghiep>
{business}
</ho_so_doanh_nghiep>

Giọng văn: {rules.tone}. {rules.address}.

Nguyên tắc:
- Bài phải có ích thật cho người đọc: trả lời đúng điều họ tìm, có ví dụ và tình huống cụ thể.
- Không bịa số liệu, giá, thời gian bảo hành, tên khách hàng hay nguồn. Chỉ dùng số liệu từ
  "chất liệu thật" của xưởng hoặc kiến thức phổ thông chắc chắn đúng. Chỗ cần số liệu thật mà
  chưa có thì ghi đúng dạng [cần bổ sung: mô tả ngắn cần gì].
- Không nhồi từ khóa. Không dùng các cụm sáo rỗng: {banned}.
- Không mở bài bằng câu rào đón; câu đầu tiên đã phải có thông tin."""


def _material(material: Mapping[str, str]) -> str:
    lines = [f"- {label}: {text.strip() or NO_MATERIAL}" for label, text in material.items()]
    return "\n".join(lines) or NO_MATERIAL


def _research(research: Research) -> str:
    competitors = "\n".join(
        f"- {c.title}: đã có «{c.covers}»; còn thiếu «{c.missing}»" for c in research.competitors
    )
    return (
        "Ý định tìm kiếm:\n"
        + "\n".join(f"- {line}" for line in research.intent)
        + f"\nDạng bài hợp nhất: {research.article_type}\n"
        + f"Các bài đứng đầu Google:\n{competitors}\n"
        + "Bài mình phải có thêm:\n"
        + "\n".join(f"- {a}" for a in research.new_angles)
        + "\nCâu hỏi người đọc hay có:\n"
        + "\n".join(f"- {q}" for q in research.questions)
    )


def _outline(outline: Outline) -> str:
    lines = [f"Tiêu đề bài: {outline.title}"]
    for i, item in enumerate(outline.items, start=1):
        lines.append(f"{i}. {item.heading}")
        lines += [f"   - {p}" for p in item.points]
    return "\n".join(lines)


def article_text(title: str, parts: Sequence[Section]) -> str:
    """Toàn bài dạng Markdown, có đánh số phần để AI chỉ đúng chỗ khi rà soát."""
    out = [f"# {title}"]
    for i, part in enumerate(parts):
        out.append(f"\n## [Phần {i}] {part.heading}\n\n{part.body}")
    return "\n".join(out)


def research_prompt(keyword: str) -> str:
    return f"""Từ khóa: «{keyword}» (người tìm ở Việt Nam).

1. Xác định ý định tìm kiếm: người gõ từ khóa này là ai, đang ở giai đoạn nào, cần biết gì.
2. Tìm trên web các bài đang đứng đầu Google Việt Nam cho từ khóa này (3-5 bài). Với mỗi bài:
   họ đã nói gì, còn thiếu gì mà người đọc thật sự cần. Chỉ ghi bài bạn đã thực sự đọc được.
3. Đề xuất những điều bài của xưởng phải có thêm để hơn các bài đó, ưu tiên những điều chỉ
   một xưởng làm thật mới có (ảnh công trình, kinh nghiệm thi công, lỗi hay gặp)."""


def outline_prompt(keyword: str, research: Research, material: Mapping[str, str]) -> str:
    return f"""Từ khóa: «{keyword}»

{_research(research)}

Chất liệu thật của xưởng:
{_material(material)}

Hãy lập dàn ý bài viết: tiêu đề bài (H1) có từ khóa một cách tự nhiên, rồi 4-7 mục H2.
Mỗi mục ghi các ý chính sẽ viết, và nếu nên có ảnh thì ghi ảnh đó để minh họa điều gì
(ưu tiên ảnh thật của xưởng). Đặt chất liệu thật vào đúng mục cần nó. Nếu người đọc hay
có nhiều câu hỏi lẻ, thêm mục Hỏi đáp ở cuối. Không cần mục "Mở bài" hay "Kết luận" riêng."""


def write_prompt(
    keyword: str, research: Research, material: Mapping[str, str], outline: Outline
) -> str:
    return f"""Từ khóa: «{keyword}»

{_research(research)}

Chất liệu thật của xưởng:
{_material(material)}

Dàn ý đã được duyệt:
{_outline(outline)}

Viết toàn bài theo đúng dàn ý trên: giữ nguyên tiêu đề và thứ tự các mục.
- Mở bài 2-4 câu, trả lời ngay điều người tìm cần nhất.
- Mỗi mục đi thẳng vào ý; dùng gạch đầu dòng hoặc bảng khi giúp dễ so sánh.
- Đưa chất liệu thật của xưởng vào tự nhiên, như lời thợ kể.
- Câu ngắn, đoạn ngắn (2-4 câu), dễ đọc trên điện thoại."""


def review_prompt(keyword: str, title: str, parts: Sequence[Section], rules: ContentRules) -> str:
    checklist = "\n".join(f"- {c}" for c in rules.checklist)
    return f"""Từ khóa chính: «{keyword}»

Đọc bài dưới đây như một người đọc thật, rồi rà soát theo checklist:
{checklist}

Chấm điểm 0-100 cho từng tiêu chí: thân thiện, tự nhiên (không máy móc), dễ đọc,
cụ thể có ích, chuẩn SEO. Chấm thật, đừng nể.

Liệt kê những câu cần sửa (tối đa 8 câu quan trọng nhất): câu sáo rỗng, chung chung không
có ví dụ, lệch giọng, nhồi từ khóa, hoặc có số liệu/nguồn có vẻ bịa. Chép NGUYÊN VĂN câu
đó (đúng từng ký tự, kể cả dấu ** nếu có) và ghi số phần. Câu thay thế phải cùng giọng
văn, cụ thể hơn, không bịa số liệu. Không đánh dấu các chỗ [cần bổ sung: ...].

{article_text(title, parts)}"""


def rewrite_prompt(
    keyword: str,
    title: str,
    parts: Sequence[Section],
    index: int,
    styles: Sequence[str],
    note: str,
) -> str:
    wishes = [*styles, note.strip()] if note.strip() else list(styles)
    wish = "; ".join(wishes) or "viết lại cho hay hơn, tự nhiên hơn"
    target = parts[index]
    return f"""Từ khóa chính: «{keyword}»

Toàn bài (để bạn nắm mạch):
{article_text(title, parts)}

Hãy viết lại riêng phần [Phần {index}] «{target.heading}» theo yêu cầu: {wish}.
Giữ các ý chính và số liệu thật đang có; giữ nguyên các chỗ [cần bổ sung: ...]. Không lặp
lại điều các phần khác đã nói."""
