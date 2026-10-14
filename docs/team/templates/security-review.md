# Biên bản bảo mật T-xxx · <Tên việc>

> Lá Chắn sao chép file này thành `docs/team/reports/T-xxx-la-chan.md`. Quy trình và mức độ lỗi: `docs/team/security.md`.

| Mục | Nội dung |
|---|---|
| Người kiểm định | Lá Chắn (`la-chan`) · model: <model đã dùng> |
| Phiếu được kiểm | [T-xxx](../tickets/T-xxx-ten-ngan.md) |
| Phạm vi | <diff `abc123..def456`, hoặc "toàn bộ repo tại commit abc123"> |
| Ngày | YYYY-MM-DD |
| **Kết luận** | **ĐẠT / ĐẠT CÓ ĐIỀU KIỆN / KHÔNG ĐẠT** |

## Tóm tắt (cho chủ dự án)

<2–3 câu bằng lời thường: có an toàn không, nếu không thì nguy cơ là gì và cần làm gì.>

## Lỗi phát hiện

| # | Mức | Mô tả | Vị trí | Đường đi thật (đầu vào → hậu quả) | Cách sửa đề xuất |
|---|---|---|---|---|---|
| 1 | Nghiêm trọng/Cao/Trung bình/Thấp | | `file:dòng` | | |

_(Ghi "Không phát hiện lỗi" nếu không có.)_

## Danh sách kiểm tra

| Mã | Kết quả | Bằng chứng / ghi chú |
|---|---|---|
| S1 | Đạt / Không đạt / Không áp dụng | |
| S2 | | |
| S3 | | |
| W1 | | |
| W2 | | |
| W3 | | |
| W4 | | |
| A1 | | |
| A2 | | |
| A3 | | |
| U1 | | |
| U2 | | |
| U3 | | |
| F1 | | |
| F2 | | |
| F3 | | |
| D1 | | |
| D2 | | |
| D3 | | |

## Kết quả công cụ quét

| Công cụ | Kết quả | Đã xác minh |
|---|---|---|
| pip-audit | <số lỗ hổng / "chưa chạy được: lý do"> | |
| bandit | | |
| detect-secrets | | |
| Soát lịch sử git | | |
| pytest / ruff | | |

## Báo nhầm đã loại

<Cảnh báo công cụ đã xác minh là không phải lỗi, kèm lý do.>

## Điều kiện (nếu ĐẠT CÓ ĐIỀU KIỆN)

<Lỗi nào phải sửa, ở phiếu nào, trước mốc nào.>
