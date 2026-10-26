"""Dữ liệu mẫu cho giao diện DEMO.

Chỉ để xem trước cách phần mềm hoạt động. Khi một chức năng được làm thật, phần mẫu tương ứng
ở đây sẽ được xóa. File này không gọi mạng, không dùng AI thật.
"""

from __future__ import annotations

from datetime import date, timedelta

# ------------------------------------------------------------ danh sách bài

ARTICLES_IN_PROGRESS = [
    {
        "keyword": "so sánh inox 201 và 304",
        "title": "So sánh inox 201 và 304: nên chọn loại nào cho cổng, lan can?",
        "step": 3,
        "score": 84,
        "updated": "10 phút trước",
        "note": "Còn 2 câu nghe máy móc, 1 chỗ thiếu số liệu",
    },
    {
        "keyword": "cách chống gỉ cửa sắt",
        "title": "Cách chống gỉ cửa sắt tại nhà: 5 việc làm mỗi mùa mưa",
        "step": 2,
        "score": None,
        "updated": "hôm qua",
        "note": "Dàn ý chờ bạn duyệt",
    },
    {
        "keyword": "giá cổng inox 304",
        "title": "Giá cổng inox 304: cách tính và những khoản hay bị bỏ sót",
        "step": 5,
        "score": 91,
        "updated": "2 ngày trước",
        "note": "Sẵn sàng gửi WordPress",
    },
]

SENT_TO_WORDPRESS = [
    {"Bài": "Cửa sắt 2 cánh: chọn mẫu nào cho nhà phố?", "Trạng thái": "Đã đăng", "Ngày": "24/09"},
    {"Bài": "Hàng rào sắt mỹ thuật: 12 mẫu đẹp", "Trạng thái": "Hẹn giờ", "Ngày": "13/10"},
]

STEPS = ["Chuẩn bị", "Dàn ý", "Viết & kiểm tra", "SEO", "Xuất bản"]

# --------------------------------------------------------------- kế hoạch

PLAN_ROWS = [
    # từ khóa, ý định, ưu tiên, trạng thái, ngày (lệch so với hôm nay)
    ("so sánh inox 201 và 304", "So sánh trước khi mua", "Cao", "Đang viết", 0),
    ("giá cổng inox 304", "Mua hàng", "Cao", "Sẵn sàng", 2),
    ("cách chống gỉ cửa sắt", "Tìm hiểu", "Trung bình", "Đang viết", 5),
    ("lan can cầu thang sắt", "Mua hàng", "Trung bình", "Chưa viết", 10),
    ("sơn tĩnh điện là gì", "Tìm hiểu", "Thấp", "Chưa viết", 14),
    ("cổng sắt hộp mạ kẽm có bền không", "So sánh trước khi mua", "Trung bình", "Chưa viết", 17),
]


def plan_rows(today: date) -> list[dict]:
    return [
        {
            "Từ khóa": kw,
            "Ý định": intent,
            "Ưu tiên": priority,
            "Trạng thái": status,
            "Ngày dự kiến": today + timedelta(days=offset),
        }
        for kw, intent, priority, status, offset in PLAN_ROWS
    ]


PLAN_PASTE_EXAMPLE = """Tháng 10–11: tập trung cổng và lan can inox, khách nhà phố ở Đà Nẵng.
- Đẩy "lan can cầu thang sắt" lên ưu tiên cao, viết trước 15/10
- Thêm bài: "cổng inox 304 mạ vàng có bền không", "kích thước cổng nhà phố 4m"
- Bỏ bài "sơn tĩnh điện là gì" (đã có bài cũ trên web)"""

PLAN_CHANGES = [
    {
        "Áp dụng": True,
        "Loại": "➕ Thêm mới",
        "Từ khóa": "cổng inox 304 mạ vàng có bền không",
        "Chi tiết": "Ưu tiên Trung bình · ngày 20/10",
    },
    {
        "Áp dụng": True,
        "Loại": "➕ Thêm mới",
        "Từ khóa": "kích thước cổng nhà phố 4m",
        "Chi tiết": "Ưu tiên Trung bình · ngày 24/10",
    },
    {
        "Áp dụng": True,
        "Loại": "✏️ Cập nhật",
        "Từ khóa": "lan can cầu thang sắt",
        "Chi tiết": "Ưu tiên Trung bình → Cao · ngày 16/10 → 15/10",
    },
    {
        "Áp dụng": False,
        "Loại": "🗑️ Bỏ",
        "Từ khóa": "sơn tĩnh điện là gì",
        "Chi tiết": "Lý do: đã có bài cũ trên website",
    },
]

BUSINESS_BRIEF = {
    "Doanh nghiệp": "ProMetal — xưởng gia công cửa, cổng, lan can sắt và inox",
    "Khu vực phục vụ": "Đà Nẵng và các tỉnh lân cận",
    "Khách hàng chính": "Chủ nhà phố đang xây/sửa nhà; một phần là nhà thầu nhỏ",
    "Điểm khác biệt": "Khảo sát tận nơi, ảnh công trình thật, bảo hành mối hàn",
}

# ----------------------------------------------------------------- bước 5: Xuất bản

CATEGORIES = ["Inox", "Cổng inox", "Lan can", "Bảo dưỡng"]

# ---------------------------------------------------------------- cài đặt

TONE_SETTINGS = {
    "xung_ho": "Xưởng xưng «chúng tôi», gọi người đọc là «bạn»",
    "banned": [
        "Trong thời đại…",
        "Hãy cùng tìm hiểu…",
        "Có thể thấy rằng…",
        "vô cùng quan trọng",
        "quý khách hàng",
    ],
}
