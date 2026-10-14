# Bảng việc

Chủ dự án xem file này để biết agent nào đang làm gì. Chỉ Huy cập nhật mỗi khi giao, nhận hoặc đóng phiếu.

_Cập nhật: 2026-10-14_

## Đang làm

| Phiếu | Việc | Agent | Trạng thái | Báo cáo |
|---|---|---|---|---|
| [T-004](tickets/T-004-loc-html-ket-qua-ai.md) | **Cao:** lọc HTML/link trong kết quả AI, bộ lọc trước WordPress | Thợ Máy | Đang làm | |
| [T-005](tickets/T-005-escape-hien-thi-bai.md) | **Cao:** hiển thị bài AI an toàn trên trang Soạn bài | Họa Sĩ | Đang làm | |

## Chờ

| Phiếu | Việc | Agent | Chờ gì |
|---|---|---|---|
| [T-003](tickets/T-003-ra-soat-prompt-noi-dung.md) | Rà soát prompt, tách dữ liệu ngoài khỏi chỉ thị | Ngòi Bút | Sẵn sàng giao |
| [T-006](tickets/T-006-sua-loi-nho-giai-doan-2.md) | Sửa các lỗi Trung bình/Thấp của Giai đoạn 2 | Thợ Máy | T-004 xong (mục 5, 6 đã được duyệt) |
| [T-007](tickets/T-007-xoa-gps-anh-dai-dien.md) | Xóa GPS trong ảnh trước khi tải lên | Thợ Máy | Chủ dự án chọn cách (a) hoặc (b) |

## Việc đang làm ngoài hệ thống phiếu

Các việc này bắt đầu trước khi có đội agent. Khi xong, Chỉ Huy lập phiếu kiểm định cho Lá Chắn.

| Việc | Ở đâu |
|---|---|
| Giai đoạn 2 phần 2: provider OpenAI / Gemini, thử mù mô hình | Một phiên Claude khác trong dự án |
| Hồ sơ doanh nghiệp `config/business_profile.md` | PR #3 trên GitHub, chờ gộp |

## Xong

| Phiếu | Việc | Agent | Ngày xong | Kết quả |
|---|---|---|---|---|
| [T-001](tickets/T-001-kiem-dinh-bao-mat-nen.md) | Kiểm định bảo mật toàn bộ code | Lá Chắn | 2026-10-14 | [Biên bản](reports/T-001-la-chan.md): KHÔNG ĐẠT, 1 Cao, 4 Trung bình, 3 Thấp. Không lộ bí mật, không có đường đăng công khai. |
| [T-002](tickets/T-002-kiem-thu-giai-doan-2.md) | Kiểm thử Giai đoạn 2 phần 1 | Soi Lỗi | 2026-10-14 | [Báo cáo](reports/T-002-soi-loi.md): 69 test mới, 8 lỗi (đánh dấu `xfail`), test chặn mạng thật. Chỉ Huy soát: test chỉ dùng khóa giả. |

## Số phiếu tiếp theo: T-008
