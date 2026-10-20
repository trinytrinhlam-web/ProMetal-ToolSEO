# T-xxx · <Tên việc ngắn gọn>

> Sao chép file này thành `docs/team/tickets/T-xxx-ten-ngan.md`. Số phiếu tăng dần, không dùng lại số cũ.

| Mục | Nội dung |
|---|---|
| Giao cho | <Tên agent> (`<mã>`) |
| Người giao | Chỉ Huy |
| Ngày giao | YYYY-MM-DD |
| Giai đoạn | <Giai đoạn N trong Lộ trình của CLAUDE.md> |
| Mức ưu tiên | Cao / Trung bình / Thấp |
| Phụ thuộc | <T-yyy phải xong trước, hoặc "Không"> |
| Trạng thái | Mới / Đã giao / Đang làm / Chờ kiểm thử / Chờ bảo mật / Chờ duyệt / Xong / Trả lại |

## Mục tiêu

<Một hai câu: làm xong thì người dùng thấy được gì, hoặc dự án có thêm gì.>

## Bối cảnh

<Những gì agent cần biết mà không có sẵn trong CLAUDE.md: quyết định liên quan, file cần đọc trước, phiếu trước đó.>

## Phạm vi

- **Được sửa:** <danh sách file hoặc thư mục>
- **Không được sửa:** <những chỗ dễ bị đụng nhầm>
- **Ngoài phạm vi:** <việc liên quan nhưng để phiếu khác>

## Yêu cầu

1. <Yêu cầu cụ thể, kiểm tra được>
2. ...

## Yêu cầu bảo mật riêng

<Các dòng trong danh sách kiểm tra của `security.md` mục 4 liên quan nhất tới phiếu này, ví dụ W1, W3, A1. Ghi "Theo mặc định" nếu không có gì đặc biệt.>

## Tiêu chí xong

- [ ] <Tiêu chí kiểm tra được>
- [ ] Test liên quan (`uv run pytest <file>`) qua và `uv run ruff check .` sạch; toàn bộ test do Chỉ Huy chạy trên Windows khi gộp
- [ ] Có test cho phần logic mới
- [ ] Báo cáo nộp tại `docs/team/reports/T-xxx-<mã-agent>.md`

## Kiểm thử và kiểm định

- Soi Lỗi: <Có / Không, kèm điểm cần thử kỹ>
- Lá Chắn: <Có / Rút gọn (chỉ soát bí mật)>

## Ghi chú của Chỉ Huy

<Lịch sử: trả lại vì sao, đổi phạm vi khi nào…>
