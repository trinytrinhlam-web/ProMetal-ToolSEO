# Bảng việc

Chủ dự án xem file này để biết agent nào đang làm gì. Chỉ Huy cập nhật mỗi khi giao, nhận hoặc đóng phiếu.

_Cập nhật: 2026-10-14_

## Đang làm

| Phiếu | Việc | Agent | Trạng thái | Báo cáo |
|---|---|---|---|---|
| [T-008](tickets/T-008-gia-co-bo-loc.md) | Gia cố bộ lọc: làm lại SL-1..SL-5 | Thợ Máy | Trả lại, đang làm | [Soi Lỗi](reports/T-003-006-008-009-soi-loi.md) |

## Chờ

| Phiếu | Việc | Agent | Chờ gì |
|---|---|---|---|
| [T-010](tickets/T-010-cau-hinh-chiu-loi-va-loi-thap.md) | File cấu hình chịu lỗi, các lỗi Thấp còn lại | Thợ Máy | T-008 làm lại xong |

## Việc đang làm ngoài hệ thống phiếu

Các việc này bắt đầu trước khi có đội agent. Khi xong, Chỉ Huy lập phiếu kiểm định cho Lá Chắn.

| Việc | Ở đâu |
|---|---|
| Giai đoạn 2 phần 2: provider OpenAI / Gemini, thử mù mô hình | Một phiên Claude khác trong dự án |
| Hồ sơ doanh nghiệp `config/business_profile.md` | PR #3 trên GitHub, chờ gộp |

## Xong

| Phiếu | Việc | Agent | Ngày xong | Kết quả |
|---|---|---|---|---|
| [T-009](tickets/T-009-dua-loi-dan-moi-vao-code.md) | Đưa lời dặn AI mới vào code | Thợ Máy | 2026-10-14 | [Báo cáo](reports/T-009-tho-may.md) · Lá Chắn: [**ĐẠT**](reports/T-003-006-008-009-la-chan.md) |
| [T-006](tickets/T-006-sua-loi-nho-giai-doan-2.md) | Sửa lỗi Trung bình/Thấp Giai đoạn 2 | Thợ Máy | 2026-10-14 | [Báo cáo](reports/T-006-tho-may.md) · Lá Chắn: **ĐẠT** |
| [T-003](tickets/T-003-ra-soat-prompt-noi-dung.md) | Rà soát prompt, quy tắc văn phong | Ngòi Bút | 2026-10-14 | [Báo cáo](reports/T-003-ngoi-but.md) · Lá Chắn: **ĐẠT** |
| [T-004](tickets/T-004-loc-html-ket-qua-ai.md) | Lọc HTML/link trong kết quả AI | Thợ Máy | 2026-10-14 | [Báo cáo](reports/T-004-tho-may.md) · Soi Lỗi: [3 lỗ hở nhỏ](reports/T-004-T-005-soi-loi.md) → T-008 · Lá Chắn: [**ĐẠT**](reports/T-004-T-005-la-chan.md) |
| [T-005](tickets/T-005-escape-hien-thi-bai.md) | Hiển thị bài AI an toàn | Họa Sĩ | 2026-10-14 | [Báo cáo](reports/T-005-hoa-si.md) · Soi Lỗi: xác nhận · Lá Chắn: **ĐẠT** |
| [T-001](tickets/T-001-kiem-dinh-bao-mat-nen.md) | Kiểm định bảo mật toàn bộ code | Lá Chắn | 2026-10-14 | [Biên bản](reports/T-001-la-chan.md): KHÔNG ĐẠT (1 Cao). Nay **ĐẠT** (sau T-004, T-005, T-006, T-009). |
| [T-007](tickets/T-007-xoa-gps-anh-dai-dien.md) | Xóa GPS trong ảnh | Thợ Máy | 2026-10-14 | **Hủy**: chủ dự án muốn giữ vị trí trong ảnh (sổ rủi ro, `security.md` mục 6) |
| [T-002](tickets/T-002-kiem-thu-giai-doan-2.md) | Kiểm thử Giai đoạn 2 phần 1 | Soi Lỗi | 2026-10-14 | [Báo cáo](reports/T-002-soi-loi.md): 69 test mới, 8 lỗi (đánh dấu `xfail`), test chặn mạng thật. Chỉ Huy soát: test chỉ dùng khóa giả. |

## Số phiếu tiếp theo: T-011
