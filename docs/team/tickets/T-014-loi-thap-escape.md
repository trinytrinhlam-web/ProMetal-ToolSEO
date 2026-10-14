# T-014 · Các lỗi Thấp còn lại của bộ escape link

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy |
| Ngày giao | 2026-10-14 |
| Giai đoạn | Giai đoạn 2 |
| Mức ưu tiên | Thấp |
| Phụ thuộc | Không |
| Trạng thái | Xong (2026-10-14) |

## Yêu cầu

Nguồn: [T-008r3-012-soi-loi.md](../reports/T-008r3-012-soi-loi.md) (R4-2, R4-3, R4-4) và [T-008r3-012-la-chan.md](../reports/T-008r3-012-la-chan.md) (#1).

1. `escape_link_syntax` / `unescape_link_syntax` coi `\r` như xuống dòng (R4-2, LC #1); giữ đúng tính nghịch đảo.
2. R4-3: không chèn `\` trong đoạn `code` (nếu làm được an toàn; nếu không, ghi rõ lý do).
3. R4-4: `[chữ](chữ có dấu cách)` không phải link thì không cắt phần trong ngoặc.

## Tiêu chí xong

- [ ] Test `xfail` R4-2..R4-4 chuyển thành `passed` (hoặc giải thích trong báo cáo)
- [ ] Báo cáo `docs/team/reports/T-014-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có · Lá Chắn: Có
