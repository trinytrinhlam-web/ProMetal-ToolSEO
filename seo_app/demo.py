"""Dữ liệu mẫu cho giao diện DEMO.

Chỉ để xem trước cách phần mềm hoạt động. Khi một chức năng được làm thật, phần mẫu tương ứng
ở đây sẽ được xóa. File này không gọi mạng, không dùng AI thật.
"""

from __future__ import annotations

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

STEPS = ["Chuẩn bị", "Dàn ý", "Viết & kiểm tra", "SEO", "Xuất bản"]

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
