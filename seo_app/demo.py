"""Dữ liệu mẫu và tiện ích cho các trang DEMO.

Chỉ dùng để xem trước giao diện. Mỗi khi một giai đoạn làm xong, trang tương ứng chuyển sang
dữ liệu thật và phần mẫu ở đây được xóa đi. Không có hàm nào ở đây gọi mạng.
"""

from __future__ import annotations

import random
from datetime import date, datetime, timedelta

import streamlit as st

# ----------------------------------------------------------------- giao diện


def banner(phase: int, what: str) -> None:
    """Khung báo đây là trang demo."""
    st.info(
        f"🧪 **BẢN DEMO** — dữ liệu mẫu, các nút chưa gửi gì đi đâu. "
        f"{what} sẽ được làm thật ở **Giai đoạn {phase}**.",
    )


def button(label: str, phase: int, *, key: str | None = None, primary: bool = False) -> None:
    """Nút demo: bấm vào chỉ hiện thông báo nhỏ."""
    if st.button(label, key=key, type="primary" if primary else "secondary"):
        st.toast(f"Bản demo: «{label}» sẽ hoạt động ở Giai đoạn {phase}.", icon="🧪")


# --------------------------------------------------------- kế hoạch từ khóa

KEYWORDS = [
    # từ khóa, ý định, cụm chủ đề, ưu tiên, trạng thái, ngày dự kiến
    ("so sánh inox 201 và 304", "Tìm hiểu, so sánh", "Inox", "Cao", "Đang viết", 0),
    ("cửa sắt 2 cánh", "Mua hàng", "Cửa sắt", "Cao", "Đã đăng", -12),
    ("giá cổng inox 304", "Mua hàng", "Cổng inox", "Cao", "Đã hẹn giờ", 3),
    ("cách chống gỉ cửa sắt", "Tìm hiểu", "Bảo dưỡng", "Trung bình", "Nháp", 5),
    ("hàng rào sắt mỹ thuật", "Mua hàng", "Hàng rào", "Trung bình", "Đã hẹn giờ", 7),
    ("lan can cầu thang sắt", "Mua hàng", "Lan can", "Trung bình", "Chưa viết", 10),
    ("sơn tĩnh điện là gì", "Tìm hiểu", "Bảo dưỡng", "Thấp", "Chưa viết", 14),
    (
        "cổng sắt hộp mạ kẽm có bền không",
        "Tìm hiểu, so sánh",
        "Cổng sắt",
        "Trung bình",
        "Chưa viết",
        17,
    ),
    ("kích thước cửa cổng tiêu chuẩn", "Tìm hiểu", "Cổng sắt", "Thấp", "Chưa viết", 21),
]

STATUSES = ["Chưa viết", "Đang viết", "Nháp", "Đã hẹn giờ", "Đã đăng"]


def keyword_rows(today: date) -> list[dict]:
    return [
        {
            "Từ khóa": kw,
            "Ý định tìm kiếm": intent,
            "Cụm chủ đề": cluster,
            "Ưu tiên": priority,
            "Trạng thái": status,
            "Ngày dự kiến": today + timedelta(days=offset),
        }
        for kw, intent, cluster, priority, status, offset in KEYWORDS
    ]


# ------------------------------------------------------------------ viết bài

DEMO_KEYWORD = "so sánh inox 201 và 304"

INTENT = {
    "Ý định chính": "Tìm hiểu, so sánh trước khi mua: người đọc sắp làm cổng/lan can và muốn "
    "biết nên chọn loại inox nào.",
    "Người đọc": "Chủ nhà đang xây/sửa nhà, chưa rành vật liệu.",
    "Họ cần biết": "Khác nhau ở đâu, loại nào bền ở môi trường nào, chênh giá thế nào, "
    "cách nhận biết khi nhận hàng.",
    "Dạng bài phù hợp": "Bài so sánh có bảng, ví dụ thực tế, phần hỏi đáp.",
}

COMPETITORS = [
    {
        "Vị trí": 1,
        "Tiêu đề": "Inox 201 và 304 khác nhau như thế nào?",
        "Đã nói": "Thành phần hóa học, bảng so sánh chung",
        "Còn thiếu": "Không có ví dụ công trình thật, không nói môi trường gần biển",
    },
    {
        "Vị trí": 2,
        "Tiêu đề": "Cách phân biệt inox 201 và 304 đơn giản",
        "Đã nói": "Thử bằng nam châm, thuốc thử",
        "Còn thiếu": "Không cảnh báo nam châm dễ cho kết quả sai",
    },
    {
        "Vị trí": 3,
        "Tiêu đề": "Nên làm cổng inox 201 hay 304?",
        "Đã nói": "Khuyên dùng 304",
        "Còn thiếu": "Không có chi phí thực tế, không có ảnh sau vài năm sử dụng",
    },
]

NEW_ANGLES = [
    "Ảnh thật cổng inox 201 và 304 sau 3 năm ở cùng một khu phố (ảnh của xưởng).",
    "Bảng chọn nhanh theo nơi lắp: trong nhà / ngoài trời / gần biển.",
    "Cảnh báo cách thử bằng nam châm hay bị sai, và cách kiểm tra đáng tin hơn.",
]

REAL_MATERIAL = {
    "Kinh nghiệm của xưởng": "Nhiều khách ở gần biển làm cổng 201 cho rẻ, khoảng 1–2 năm "
    "đã có đốm gỉ ở mối hàn. [bạn bổ sung ví dụ cụ thể]",
    "Số liệu của bạn": "[ví dụ: chênh lệch giá làm một bộ cổng 4 m giữa 201 và 304 — "
    "lấy từ báo giá thật của xưởng]",
    "Câu hỏi khách hay hỏi": "Inox 304 có bị gỉ không? Làm sao biết thợ có dùng đúng 304 "
    "không? Lan can trong nhà có cần 304 không?",
}

OUTLINE = """## Inox 201 và 304 khác nhau ở đâu?
- Thành phần: 304 nhiều niken hơn → chống gỉ tốt hơn
- Bảng so sánh nhanh: độ bền, giá, nơi nên dùng

## Nên chọn loại nào cho từng vị trí?
- Cổng, hàng rào ngoài trời
- Nhà gần biển, khu công nghiệp
- Lan can, tay vịn trong nhà

## Ảnh thật sau 3 năm sử dụng (của xưởng)

## Cách kiểm tra khi nhận hàng
- Vì sao thử bằng nam châm dễ sai
- Cách kiểm tra đáng tin hơn

## Chi phí: chênh lệch thực tế [số liệu của xưởng]

## Hỏi đáp
"""

DRAFT_ARTICLE = """**Inox 304 chống gỉ tốt hơn inox 201 vì chứa nhiều niken hơn — nhưng không phải \
vị trí nào cũng cần 304.** Ở xưởng, chúng tôi thấy nhiều khách gần biển chọn 201 cho rẻ, rồi chỉ \
sau 1–2 năm mối hàn đã lấm tấm gỉ. Ngược lại, lan can trong nhà làm bằng 201 vẫn dùng tốt nhiều năm.

#### Inox 201 và 304 khác nhau ở đâu?
Khác biệt chính nằm ở thành phần: inox 304 có hàm lượng niken cao hơn, nhờ đó lớp bảo vệ bề mặt \
bền hơn khi gặp hơi ẩm, muối và hóa chất…

*(phần còn lại của bài — bản demo chỉ hiện đoạn đầu)*"""

CHECKLIST = [
    ("Mở bài trả lời ngay câu hỏi chính, không vòng vo", True, ""),
    ("Không dùng câu sáo rỗng («Trong thời đại…», «Hãy cùng tìm hiểu…»)", True, ""),
    ("Có điều mới so với các bài đang đứng đầu", True, "ảnh thật + bảng chọn theo vị trí"),
    ("Mỗi ý chung chung đều có ví dụ cụ thể", True, ""),
    ("Không bịa số liệu, nguồn", False, "Còn 1 chỗ cần số liệu thật: mục Chi phí"),
    ("Từ khóa xuất hiện tự nhiên, không nhồi", True, "4 lần / 1.450 chữ"),
    ("Có phần hỏi đáp từ câu hỏi thật của khách", True, ""),
]

META = {
    "title": "So sánh inox 201 và 304: nên chọn loại nào cho cổng, lan can?",
    "description": "Inox 304 bền hơn 201 nhưng không phải chỗ nào cũng cần. Bảng chọn theo vị "
    "trí lắp, ảnh thật sau 3 năm và cách kiểm tra khi nhận hàng.",
    "slug": "so-sanh-inox-201-va-304",
}

SCHEMA_PREVIEW = """{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "So sánh inox 201 và 304: nên chọn loại nào cho cổng, lan can?",
  "author": {"@type": "Organization", "name": "ProMetal"},
  "image": "https://…/cong-inox-304-sau-3-nam.webp"
}
+ FAQPage (3 câu hỏi)"""

INTERNAL_LINKS = [
    {"Cụm từ trong bài": "cổng inox 304", "Liên kết tới bài": "Giá cổng inox 304 mới nhất"},
    {"Cụm từ trong bài": "sơn tĩnh điện", "Liên kết tới bài": "Sơn tĩnh điện là gì?"},
    {"Cụm từ trong bài": "lan can cầu thang", "Liên kết tới bài": "Lan can cầu thang sắt"},
]

# ----------------------------------------------------------------- thử mù

BLIND_PROMPT = "Viết đoạn mở bài (khoảng 80 chữ) cho bài «So sánh inox 201 và 304»."

BLIND_OUTPUTS = {
    "A": "Inox 304 chống gỉ tốt hơn 201 nhờ nhiều niken hơn, nhưng đắt hơn. Nếu làm cổng "
    "ngoài trời hoặc nhà gần biển, 304 đáng tiền; còn lan can trong nhà, 201 vẫn đủ dùng nhiều "
    "năm. Bài này so sánh hai loại theo từng vị trí lắp, kèm ảnh thật sau 3 năm sử dụng.",
    "B": "Inox là vật liệu phổ biến trong xây dựng hiện nay. Có nhiều loại inox khác nhau, "
    "trong đó 201 và 304 là hai loại thường gặp nhất. Mỗi loại có ưu nhược điểm riêng. "
    "Hãy cùng tìm hiểu sự khác biệt giữa chúng qua bài viết dưới đây.",
    "C": "Cùng là cổng inox, có nhà dùng 10 năm vẫn sáng, có nhà 2 năm đã gỉ mối hàn — khác "
    "biệt thường nằm ở loại inox. 304 chứa nhiều niken hơn nên bền hơn trong môi trường ẩm, "
    "mặn. Dưới đây là cách chọn đúng loại cho từng vị trí, và cách kiểm tra khi nhận hàng.",
}

BLIND_MODELS = {"A": "Anthropic (Claude)", "B": "Google (Gemini)", "C": "OpenAI (GPT)"}

# -------------------------------------------------------------------- ảnh

IMAGES = [
    {
        "Ảnh gốc": "IMG_2041.JPG",
        "Tên mới": "cong-inox-304-sau-3-nam.webp",
        "Dung lượng": "4,2 MB → 180 KB",
        "Vị trí GPS": "Đã xóa",
        "Alt (AI gợi ý)": "Cổng inox 304 hai cánh sau 3 năm, bề mặt còn sáng, không gỉ",
    },
    {
        "Ảnh gốc": "IMG_2044.JPG",
        "Tên mới": "moi-han-cong-inox-201-bi-gi.webp",
        "Dung lượng": "3,8 MB → 165 KB",
        "Vị trí GPS": "Đã xóa",
        "Alt (AI gợi ý)": "Cận cảnh mối hàn cổng inox 201 có đốm gỉ nâu",
    },
    {
        "Ảnh gốc": "DSC0193.jpg",
        "Tên mới": "lan-can-cau-thang-inox-201-trong-nha.webp",
        "Dung lượng": "2,9 MB → 140 KB",
        "Vị trí GPS": "Không có",
        "Alt (AI gợi ý)": "Lan can cầu thang inox 201 trong nhà, tay vịn gỗ",
    },
]

# ---------------------------------------------------------------- lịch đăng


def schedule_rows(now: datetime) -> list[dict]:
    day = now.replace(hour=8, minute=0, second=0, microsecond=0)
    rows = [
        (day + timedelta(days=3), "Giá cổng inox 304 mới nhất", "Đã hẹn giờ", "Cổng inox"),
        (day + timedelta(days=7), "Hàng rào sắt mỹ thuật: 12 mẫu đẹp", "Đã hẹn giờ", "Hàng rào"),
        (None, "Cách chống gỉ cửa sắt tại nhà", "Nháp", "Bảo dưỡng"),
        (None, "So sánh inox 201 và 304", "Nháp", "Inox"),
        (day - timedelta(days=12), "Cửa sắt 2 cánh: chọn mẫu nào?", "Đã đăng", "Cửa sắt"),
    ]
    return [
        {
            "Ngày giờ đăng": when.strftime("%H:%M %d/%m/%Y") if when else "—",
            "Tiêu đề": title,
            "Trạng thái": status,
            "Chuyên mục": category,
        }
        for when, title, status, category in rows
    ]


# --------------------------------------------------------------- thứ hạng

ARTICLES = [
    "Cửa sắt 2 cánh: chọn mẫu nào?",
    "Giá cổng inox 304 mới nhất",
    "Sơn tĩnh điện là gì?",
]


def ranking_rows() -> list[dict]:
    return [
        {"Bài viết": ARTICLES[0], "Click": 412, "Hiển thị": 9800, "CTR": "4,2%", "Vị trí TB": 6.1},
        {"Bài viết": ARTICLES[1], "Click": 158, "Hiển thị": 5200, "CTR": "3,0%", "Vị trí TB": 9.4},
        {"Bài viết": ARTICLES[2], "Click": 37, "Hiển thị": 2100, "CTR": "1,8%", "Vị trí TB": 14.7},
    ]


def keyword_ranking_rows() -> list[dict]:
    return [
        {"Từ khóa": "cửa sắt 2 cánh", "Click": 210, "Hiển thị": 4100, "Vị trí TB": 4.8},
        {"Từ khóa": "mẫu cửa sắt 2 cánh đẹp", "Click": 122, "Hiển thị": 3300, "Vị trí TB": 6.9},
        {
            "Từ khóa": "cửa sắt 2 cánh giá bao nhiêu",
            "Click": 80,
            "Hiển thị": 2400,
            "Vị trí TB": 8.2,
        },
    ]


def weekly_trend(today: date, weeks: int = 12) -> list[dict]:
    """Số liệu mẫu theo tuần (cố định, không ngẫu nhiên mỗi lần mở)."""
    rng = random.Random(2026)
    rows = []
    position = 18.0
    for i in range(weeks):
        position = max(3.0, position - rng.uniform(0.3, 1.6))
        clicks = int(8 + (20 - position) * 3 + rng.uniform(-4, 4))
        rows.append(
            {
                "Tuần": (today - timedelta(weeks=weeks - 1 - i)).isoformat(),
                "Click": max(0, clicks),
                "Vị trí TB": round(position, 1),
            }
        )
    return rows


# ---------------------------------------------------------------- cài đặt

AI_TASKS = [
    {"Việc": "Nghiên cứu, phân tích đối thủ", "Nhà cung cấp": "Anthropic", "Ghi chú": "cần đọc kỹ"},
    {"Việc": "Viết bài", "Nhà cung cấp": "Anthropic", "Ghi chú": "chọn sau khi thử mù"},
    {
        "Việc": "Rà soát theo checklist",
        "Nhà cung cấp": "OpenAI",
        "Ghi chú": "khác hãng với bên viết",
    },
    {
        "Việc": "Meta title, description",
        "Nhà cung cấp": "Google Gemini",
        "Ghi chú": "việc ngắn, rẻ",
    },
    {"Việc": "Viết alt ảnh", "Nhà cung cấp": "Google Gemini", "Ghi chú": "cần đọc được ảnh"},
    {"Việc": "Tạo ảnh", "Nhà cung cấp": "OpenAI", "Ghi chú": "chỉ dùng khi không có ảnh thật"},
]
