# T-009 · Đưa lời dặn AI mới của Ngòi Bút vào code

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy |
| Ngày giao | 2026-10-14 |
| Giai đoạn | Giai đoạn 2 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-003 (đã có đề xuất) |
| Trạng thái | Xong |

## Mục tiêu

Lời dặn AI tách bạch dữ liệu ngoài khỏi chỉ thị, cấm chèn link/HTML, giữ chỗ cần ảnh khi viết bài, theo đề xuất của Ngòi Bút.

## Bối cảnh

[T-003-ngoi-but.md](../reports/T-003-ngoi-but.md) mục 3 (nguyên văn `prompts.py` mới) và danh sách test gợi ý. Lỗi gốc: T-001 #2, T-002 #8.

## Phạm vi

- **Được sửa:** `seo_app/content/prompts.py`, `tests/**` (gỡ xfail `test_outside_data_in_prompts_is_marked_as_data_not_instructions`, thêm test).
- **Không được sửa:** `config/` (của Ngòi Bút).

## Tiêu chí xong

- [ ] Không còn test `xfail` nào trong repo
- [ ] Test: dữ liệu chứa thẻ khung (`</du_lieu_tham_khao>`) không thoát được khỏi khung
- [ ] Báo cáo `docs/team/reports/T-009-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có · Lá Chắn: Có (prompt AI)
