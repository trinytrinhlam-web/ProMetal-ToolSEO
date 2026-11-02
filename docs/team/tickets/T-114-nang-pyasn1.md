# T-114 · Nâng `pyasn1` 0.6.4 → 0.6.5 (4 khuyến cáo mức High, LC-T078-3)

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy B |
| Ngày giao | 2026-10-31 |
| Giai đoạn | Chung (bảo mật thư viện) |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | Chủ dự án duyệt 2026-10-31 («Nâng ngay») |
| Trạng thái | Xong (gộp `main` 2026-10-31) |

## Mục tiêu

Thư viện phụ `pyasn1` (đi kèm `google-auth`) lên bản 0.6.5, vá 4 khuyến cáo mức High công bố 2026-10-31.

## Bối cảnh

- Lá Chắn T-078 (`docs/team/reports/T-078-la-chan.md`), **LC-T078-3 (Thấp)**: `pyasn1` 0.6.4 có 4 khuyến cáo High (dữ liệu ASN.1 dựng cố ý làm CPU chạy rất lâu). App không có đường dùng tới: dựng thông tin xác thực Google bằng khóa giả, `pyasn1` không được nạp. Lá Chắn đã thử nâng 0.6.5 trên bản sao: chỉ đổi đúng gói này, quét lại sạch.
- **Chủ dự án duyệt 2026-10-31: nâng ngay.**

## Phạm vi

- **Được sửa:** `uv.lock` (chỉ `pyasn1`), `pyproject.toml` chỉ khi cần ép bản tối thiểu (`pyasn1>=0.6.5` ở `override-dependencies` hoặc khai báo, kèm chú thích tiếng Việt; ghi lý do chọn), test nhỏ nếu cần.
- **Không được sửa:** code ứng dụng, phiên bản gói khác.

## Yêu cầu

1. `uv lock --upgrade-package pyasn1` (máy Windows, `uv` 0.13.4, mạng nhà/công ty); `uv.lock` chỉ đổi `pyasn1` (kiểm diff, ghi vào báo cáo).
2. `uv sync`; chạy test Google Sheets, kế hoạch, cấu hình, trang app (T-097, T-100, T-101, T-109 nếu có ở `main`) + `uv run ruff check .`.
3. `pip-audit` (hoặc cách Lá Chắn dùng ở T-075, T-078) trên môi trường mới: không còn khuyến cáo `pyasn1`; ghi kết quả.
4. Báo cáo ghi phiên bản cũ → mới, mã khuyến cáo, cách kiểm.

## Yêu cầu bảo mật riêng

D1, D3, S1.

## Tiêu chí xong

- [ ] Yêu cầu 1–4
- [ ] Toàn bộ test do Chỉ Huy chạy khi gộp
- [ ] Báo cáo `docs/team/reports/T-114-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: không cần (chỉ đổi khóa thư viện, Chỉ Huy chạy toàn bộ test). Lá Chắn: Rút gọn (D1, S1).

## Ghi chú của Chỉ Huy

- Lập 2026-10-31 theo LC-T078-3 và quyết định của chủ dự án («Nâng ngay», 31/10).
- 2026-10-31 13:32 (Chỉ Huy B): Thợ Máy (`134c9ab`, `1d29e60`: chỉ đổi `pyasn1` trong `uv.lock`), Lá Chắn ĐẠT (`3423f82`, LC-T078-3 đóng). Gộp `main`, Windows 21.819 test qua, 0 hỏng.
