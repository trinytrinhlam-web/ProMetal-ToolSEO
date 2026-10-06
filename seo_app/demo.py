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

# ------------------------------------------------------- bước 1: chuẩn bị

KEYWORD = "so sánh inox 201 và 304"

INTENT = [
    "Người đọc sắp làm cổng hoặc lan can và đang phân vân giữa hai loại inox.",
    "Họ cần biết: khác nhau ở đâu, chỗ nào cần 304, chênh giá ra sao, cách kiểm tra khi nhận hàng.",
    "Dạng bài hợp nhất: so sánh có bảng, chia theo vị trí lắp, có hỏi đáp.",
]

INTENT_ALT = [
    "Người đọc muốn được tư vấn nhanh: «nhà tôi nên dùng loại nào?».",
    "Họ ít quan tâm thành phần hóa học, quan tâm độ bền thực tế và tiền.",
    "Dạng bài hợp nhất: trả lời ngay ở đầu bài, rồi giải thích theo từng tình huống.",
]

COMPETITOR_GAPS = [
    (
        "Bài #1 — «Inox 201 và 304 khác nhau như thế nào?»",
        "Chỉ có bảng thành phần, không ví dụ công trình thật",
    ),
    (
        "Bài #2 — «Cách phân biệt inox 201 và 304»",
        "Khuyên thử nam châm nhưng không nói cách này dễ sai",
    ),
    (
        "Bài #3 — «Nên làm cổng inox 201 hay 304?»",
        "Không có chi phí, không có ảnh sau vài năm sử dụng",
    ),
]

NEW_ANGLES = [
    "Ảnh thật cổng 201 và 304 sau 3 năm ở cùng một khu phố",
    "Bảng chọn nhanh theo vị trí lắp: trong nhà / ngoài trời / gần biển",
    "Vì sao thử nam châm dễ sai, và cách kiểm tra đáng tin hơn",
]

REAL_MATERIAL = {
    "Kinh nghiệm của xưởng": "Nhiều khách ở gần biển làm cổng 201 cho rẻ, khoảng 1–2 năm đã có "
    "đốm gỉ ở mối hàn.",
    "Số liệu của bạn": "",
    "Câu hỏi khách hay hỏi": "Inox 304 có bị gỉ không? Làm sao biết thợ dùng đúng 304? Lan can "
    "trong nhà có cần 304 không?",
}

# ------------------------------------------------------------ bước 2: dàn ý

OUTLINE = [
    {
        "heading": "Inox 201 và 304 khác nhau ở đâu?",
        "image": False,
        "alt": "Điểm khác biệt chính giữa inox 201 và 304",
    },
    {
        "heading": "Nên chọn loại nào cho từng vị trí?",
        "image": True,
        "alt": "Chọn inox theo vị trí: cổng, lan can, nhà gần biển",
    },
    {
        "heading": "Cách kiểm tra inox khi nhận hàng",
        "image": True,
        "alt": "Kiểm tra inox 304 khi thợ giao hàng",
    },
    {
        "heading": "Chi phí chênh lệch thực tế",
        "image": False,
        "alt": "Làm cổng inox 304 đắt hơn 201 bao nhiêu?",
    },
    {"heading": "Hỏi đáp", "image": False, "alt": "Câu hỏi thường gặp về inox 201 và 304"},
]

# ------------------------------------------------------ bước 3: bài viết

# Mỗi phần có 2 phiên bản để nút «Viết lại» trong bản demo có cái để đổi.
SECTIONS = [
    {
        "id": "mo-bai",
        "heading": "Mở bài",
        "versions": [
            "**Inox 304 chống gỉ tốt hơn inox 201 vì chứa nhiều niken hơn — nhưng không phải chỗ "
            "nào cũng cần 304.** Ở xưởng, chúng tôi gặp nhiều khách gần biển chọn 201 cho rẻ, rồi "
            "chỉ 1–2 năm sau mối hàn đã lấm tấm gỉ. Ngược lại, lan can trong nhà làm bằng 201 vẫn "
            "dùng tốt nhiều năm.",
            "Cùng là cổng inox, có nhà dùng mười năm vẫn sáng, có nhà hai năm đã gỉ mối hàn. Khác "
            "biệt thường nằm ở loại inox: 304 hay 201. Bài này giúp bạn chọn đúng loại cho từng "
            "vị trí, để không tốn tiền oan mà cũng không phải sửa sớm.",
        ],
    },
    {
        "id": "khac-nhau",
        "heading": "Inox 201 và 304 khác nhau ở đâu?",
        "versions": [
            "Khác biệt lớn nhất nằm ở thành phần: inox 304 có nhiều niken hơn, nên lớp bảo vệ bề "
            "mặt bền hơn khi gặp hơi ẩm và muối. Có thể thấy rằng việc lựa chọn loại inox phù "
            "hợp là một yếu tố vô cùng quan trọng đối với mỗi công trình.\n\n"
            "| | Inox 201 | Inox 304 |\n|---|---|---|\n"
            "| Chống gỉ | Khá, kém ở nơi ẩm mặn | Tốt |\n"
            "| Giá | Rẻ hơn | Cao hơn |\n"
            "| Hợp nhất | Trong nhà, khô ráo | Ngoài trời, gần biển |",
            "Nói gọn: **304 bền hơn vì nhiều niken và crom hơn, 201 rẻ hơn vì ít niken hơn.** Hai "
            "chất này giữ cho lớp màng bảo vệ trên bề mặt bền hơn, nên 304 chịu mưa, hơi muối tốt "
            "hơn hẳn.\n\n"
            "| | Inox 201 | Inox 304 |\n|---|---|---|\n"
            "| Chống gỉ | Khá, kém ở nơi ẩm mặn | Tốt |\n"
            "| Giá | Rẻ hơn | Cao hơn |\n"
            "| Hợp nhất | Trong nhà, khô ráo | Ngoài trời, gần biển |",
        ],
    },
    {
        "id": "chon-loai",
        "heading": "Nên chọn loại nào cho từng vị trí?",
        "versions": [
            "- **Cổng, hàng rào gần biển:** nên dùng 304, kể cả khi đắt hơn.\n"
            "- **Cổng trong phố:** 304 vẫn đáng tiền nếu bạn muốn dùng lâu; 201 dùng được "
            "nhưng nên lau rửa định kỳ.\n"
            "- **Lan can, tay vịn trong nhà:** 201 là đủ, tiết kiệm được một khoản đáng kể.",
            "Cách nhớ nhanh: **càng gần nước mặn, gió biển, càng nên chọn 304.** Cổng và hàng rào "
            "ngoài trời là nơi đáng đầu tư nhất. Còn lan can trong nhà, nơi khô ráo và ít va "
            "chạm, 201 dùng rất ổn — để dành tiền cho những chỗ cần hơn.",
        ],
    },
    {
        "id": "kiem-tra",
        "heading": "Cách kiểm tra inox khi nhận hàng",
        "versions": [
            "Nhiều người thử bằng nam châm: hút là 201, không hút là 304. Cách này dễ sai, vì inox "
            "304 sau khi uốn, dập vẫn có thể hơi hút nam châm. Ngoài ra, quý khách hàng cũng nên "
            "lưu ý thêm một số vấn đề khác. Cách đáng tin hơn là thử bằng dung dịch thử inox "
            "chuyên dụng, hoặc yêu cầu xưởng ghi rõ mác thép trong hợp đồng.",
            "Đừng chỉ tin vào nam châm: inox 304 đã uốn, dập vẫn có thể hơi hút, nên dễ kết luận "
            "nhầm. Hai cách chắc hơn: dùng dung dịch thử inox chuyên dụng, và "
            "ghi rõ «inox 304» kèm độ dày trong hợp đồng để có căn cứ bảo hành.",
        ],
    },
    {
        "id": "chi-phi",
        "heading": "Chi phí chênh lệch thực tế",
        "versions": [
            "Với một bộ cổng 4 m, làm bằng 304 thường đắt hơn 201 khoảng **[số liệu của xưởng]**. "
            "Khoản chênh này nên so với chi phí sửa, sơn lại nếu cổng gỉ sớm.",
            "Chênh lệch giữa 201 và 304 cho cùng một bộ cổng 4 m là khoảng "
            "**[số liệu của xưởng]**. Nếu nhà bạn gần biển, khoản này thường rẻ hơn tiền sửa "
            "cổng gỉ sau vài năm.",
        ],
    },
    {
        "id": "hoi-dap",
        "heading": "Hỏi đáp",
        "versions": [
            "**Inox 304 có bị gỉ không?** Có thể có đốm gỉ nhẹ nếu bám bụi sắt hay muối lâu ngày, "
            "nhưng lau là sạch, không ăn sâu như 201.\n\n"
            "**Lan can trong nhà có cần 304 không?** Thường là không — 201 đủ bền nếu nhà khô ráo.",
            "**304 có gỉ không?** Hiếm, và nếu có chỉ là đốm bề mặt, lau là hết.\n\n"
            "**Trong nhà có cần 304?** Đa số không. Hãy dành 304 cho cổng và những chỗ dính mưa.",
        ],
    },
]

# Câu bị AI kiểm tra văn phong đánh dấu: (id phần, câu, lý do, câu thay thế)
TONE_FLAGS = [
    (
        "khac-nhau",
        "Có thể thấy rằng việc lựa chọn loại inox phù hợp là một yếu tố vô cùng quan trọng đối "
        "với mỗi công trình.",
        "Nghe máy móc: câu chung chung, không thêm thông tin gì.",
        "Chọn sai loại, bạn có thể phải sơn sửa cổng chỉ sau vài mùa mưa.",
    ),
    (
        "kiem-tra",
        "Ngoài ra, quý khách hàng cũng nên lưu ý thêm một số vấn đề khác.",
        "Câu thừa, nghe như văn bản hành chính; «quý khách hàng» lệch giọng cả bài (xưng «bạn»).",
        "",  # để trống = bỏ hẳn câu này
    ),
]

MISSING_DATA = ("chi-phi", "Chỗ «[số liệu của xưởng]» cần số liệu thật — AI không tự điền.")

QUALITY_BASE = {
    "Thân thiện": 86,
    "Dễ đọc": 88,
    "Cụ thể, có ích": 81,
    "Chuẩn SEO": 90,
}
NATURAL_MAX = 92  # điểm «Tự nhiên» khi không còn câu máy móc
NATURAL_PENALTY = 9  # trừ mỗi câu máy móc còn lại

# Chỗ cần ảnh trong bài: gắn với phần nào, ảnh nói về gì, mặc định ảnh thật hay AI
IMAGE_SLOTS = [
    {
        "id": "anh-dau-bai",
        "section": "mo-bai",
        "purpose": "Ảnh đầu bài: cổng inox 304 sau 3 năm sử dụng",
        "kind": "Ảnh thật",
        "file": "cong-inox-304-sau-3-nam.webp",
        "alt": "Cổng inox 304 hai cánh sau 3 năm, bề mặt vẫn sáng, không gỉ",
        "prompt": "Realistic photo of a modern two-leaf stainless steel gate in front of a "
        "Vietnamese townhouse, brushed finish still shiny after years of use, overcast daylight, "
        "eye-level view, 16:9, no text, no logo.",
    },
    {
        "id": "anh-vi-tri",
        "section": "chon-loai",
        "purpose": "So sánh mối hàn cổng 201 và 304 ở cùng khu phố",
        "kind": "Ảnh thật",
        "file": "moi-han-cong-inox-201-bi-gi.webp",
        "alt": "Mối hàn cổng inox 201 có đốm gỉ nâu, bên cạnh cổng 304 còn sáng",
        "prompt": "Realistic close-up photo comparing two stainless steel gate welds side by "
        "side: the left weld has small brown rust spots, the right weld is clean and shiny, "
        "natural light, 16:9, no text, no logo.",
    },
    {
        "id": "anh-nam-cham",
        "section": "kiem-tra",
        "purpose": "Minh họa thử inox bằng nam châm",
        "kind": "Ảnh AI",
        "file": "",
        "alt": "Thử thanh inox bằng nam châm nhỏ khi nhận hàng",
        "prompt": "Realistic close-up photo of a hand holding a small round magnet against a "
        "brushed stainless steel gate bar, metal workshop softly blurred in the background, "
        "natural daylight, shallow depth of field, 16:9, no text, no logo, no watermark.",
    },
]

FOLDER_IMAGES = [
    "cong-inox-304-sau-3-nam.webp",
    "moi-han-cong-inox-201-bi-gi.webp",
    "lan-can-cau-thang-inox-201-trong-nha.webp",
    "xuong-han-cong-inox.webp",
]

# ----------------------------------------------------------------- bước 4: SEO

META_TITLES = [
    "So sánh inox 201 và 304: nên chọn loại nào cho cổng, lan can?",
    "Inox 201 hay 304? Cách chọn đúng cho từng vị trí trong nhà",
    "Inox 201 và 304 khác gì? Bảng chọn nhanh + ảnh thật sau 3 năm",
]

META_DESCRIPTIONS = [
    "Inox 304 bền hơn 201 nhưng không phải chỗ nào cũng cần. Bảng chọn theo vị trí lắp, ảnh "
    "thật sau 3 năm và cách kiểm tra khi nhận hàng.",
    "Nhà gần biển, cổng ngoài trời hay lan can trong nhà? Xem nên dùng inox 201 hay 304, chênh "
    "giá bao nhiêu và cách tránh bị tráo hàng.",
]

SLUG = "so-sanh-inox-201-va-304"

INTERNAL_LINKS = [
    {"Dùng": True, "Cụm từ trong bài": "cổng inox 304", "Trỏ tới bài": "Giá cổng inox 304"},
    {"Dùng": True, "Cụm từ trong bài": "lan can cầu thang", "Trỏ tới bài": "Lan can cầu thang sắt"},
    {"Dùng": False, "Cụm từ trong bài": "chống gỉ", "Trỏ tới bài": "Cách chống gỉ cửa sắt"},
]

SCHEMA = """{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "So sánh inox 201 và 304: nên chọn loại nào cho cổng, lan can?",
  "image": "https://…/cong-inox-304-sau-3-nam.webp",
  "author": {"@type": "Organization", "name": "ProMetal"}
}
+ FAQPage: 2 câu hỏi trong mục Hỏi đáp"""

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

AI_TASKS = [
    {"Việc": "Nghiên cứu, phân tích đối thủ", "Hãng": "Anthropic"},
    {"Việc": "Viết bài, viết lại từng phần", "Hãng": "Anthropic"},
    {"Việc": "Kiểm tra văn phong", "Hãng": "OpenAI"},
    {"Việc": "Meta title, description", "Hãng": "Google Gemini"},
    {"Việc": "Viết alt và prompt ảnh", "Hãng": "Google Gemini"},
    {"Việc": "Tạo ảnh AI", "Hãng": "OpenAI"},
]

BLIND_OUTPUTS = {
    "A": SECTIONS[0]["versions"][0].replace("**", ""),
    "B": "Inox là vật liệu phổ biến trong xây dựng hiện nay. Có nhiều loại inox khác nhau, trong "
    "đó 201 và 304 là hai loại thường gặp nhất. Hãy cùng tìm hiểu sự khác biệt qua bài viết dưới "
    "đây.",
    "C": SECTIONS[0]["versions"][1],
}
BLIND_MODELS = {"A": "Anthropic", "B": "Google Gemini", "C": "OpenAI"}
