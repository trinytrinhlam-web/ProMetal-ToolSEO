# T-010 · File cấu hình chịu lỗi và các lỗi Thấp còn lại

| Mục | Nội dung |
|---|---|
| Giao cho | Thợ Máy (`tho-may`) |
| Người giao | Chỉ Huy |
| Ngày giao | 2026-10-14 |
| Giai đoạn | Giai đoạn 2 |
| Mức ưu tiên | Trung bình |
| Phụ thuộc | T-008 làm lại xong (cùng file `sanitize.py`) |
| Trạng thái | Xong |

## Mục tiêu

Người dùng sửa `ai.toml`/`content.toml` bằng Notepad (sai bảng mã, sai cấu trúc) thì app báo lỗi tiếng Việt dễ hiểu, không hiện traceback. Đóng các lỗi Thấp còn mở.

## Yêu cầu

Nguồn: [T-003-006-008-009-soi-loi.md](../reports/T-003-006-008-009-soi-loi.md) (SL) và [T-003-006-008-009-la-chan.md](../reports/T-003-006-008-009-la-chan.md) (LC). Mỗi lỗi đã có test `xfail`.

1. SL-9, SL-10: đọc TOML bằng `utf-8-sig`; file không phải UTF-8 thì báo lỗi rõ.
2. SL-11, SL-12: `content.toml` sai cấu trúc báo lỗi rõ; `banned` là chuỗi thì báo lỗi, không tách chữ.
3. SL-14 và phần so khớp của SL-13: chuẩn hóa khoảng trắng (NBSP, nhiều dấu cách); so cụm cấm theo ranh giới từ.
4. SL-6: vô hiệu thẻ khung có ký tự vô hình hoặc dấu ＜ toàn chiều rộng.
5. SL-8, LC #1: `redact_secrets` che hết giá trị tới cuối dòng, thêm `Basic`/`Bearer`.
6. LC #3: `rewrite_prompt` không đặt tiêu đề mục ngoài khung.
7. LC #4: `clean_research` chỉ giữ URL hợp lệ `^https?://\S+$` (Thợ Máy); `app/views/write.py:299` escape tiêu đề (Thợ Máy được sửa đúng dòng này).

## Tiêu chí xong

- [ ] Các test `xfail` tương ứng chuyển thành `passed`
- [ ] Báo cáo `docs/team/reports/T-010-tho-may.md`

## Kiểm thử và kiểm định

- Soi Lỗi: Có · Lá Chắn: Có
