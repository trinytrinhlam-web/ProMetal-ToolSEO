# T-011 · Sửa cụm từ cấm bắt nhầm câu bình thường

| Mục | Nội dung |
|---|---|
| Giao cho | Ngòi Bút (`ngoi-but`) |
| Người giao | Chỉ Huy |
| Ngày giao | 2026-10-14 |
| Giai đoạn | Giai đoạn 2 |
| Mức ưu tiên | Thấp |
| Phụ thuộc | T-010 (so khớp trọn từ đã có) |
| Trạng thái | Xong |

## Mục tiêu

Cụm cấm «Hãy cùng», «Nhìn chung» không còn bắt nhầm «Hãy cùng lúc…», «nhìn chung cư…», «Nhìn chung quanh…» (SL-13 trong [T-003-006-008-009-soi-loi.md](../reports/T-003-006-008-009-soi-loi.md)).

## Phạm vi

- **Được sửa:** `config/content.toml`, gỡ `xfail` của `test_normal_phrases_that_contain_a_banned_substring` khi đã qua.

## Tiêu chí xong

- [ ] 3 test `xfail` SL-13 chuyển thành `passed`, câu sáo thật vẫn bị bắt
- [ ] Bổ sung mục "T-011" ở cuối `docs/team/reports/T-003-ngoi-but.md`
