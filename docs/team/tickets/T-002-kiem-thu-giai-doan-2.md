# T-002 · Kiểm thử Giai đoạn 2 phần 1 và các test an toàn

| Mục | Nội dung |
|---|---|
| Giao cho | Soi Lỗi (`soi-loi`) |
| Người giao | Chỉ Huy |
| Ngày giao | 2026-10-14 |
| Giai đoạn | Giai đoạn 2 phần 1 (và các test an toàn của Giai đoạn 1) |
| Mức ưu tiên | Cao |
| Phụ thuộc | Không |
| Trạng thái | Xong |

## Mục tiêu

Biết chắc phần AI viết bài vừa đưa lên `main` chạy đúng với cả trường hợp xấu, và các "test an toàn" bắt buộc đã có đủ.

## Bối cảnh

- Phần mới: `seo_app/ai/`, `seo_app/content/`, trang Soạn bài `app/views/write.py`, test `tests/test_ai.py`, `tests/test_content_*.py`, `tests/fake_ai.py`.
- Danh sách test an toàn bắt buộc: hồ sơ `.claude/agents/soi-loi.md` mục "Cách kiểm thử" bước 4.

## Phạm vi

- **Được sửa:** `tests/**`, và tạo `docs/team/reports/T-002-soi-loi.md`.
- **Không được sửa:** code ứng dụng. Thấy lỗi thì ghi vào báo cáo.

## Yêu cầu

1. Chạy `uv run pytest` và `uv run ruff check .`, ghi kết quả.
2. Lập bảng: mỗi test an toàn bắt buộc đã có chưa (tên test hoặc "Thiếu").
3. Viết thêm test còn thiếu cho Giai đoạn 2 phần 1: AI trả về rỗng, sai định dạng, lỗi mạng; nội dung tiếng Việt; HTML/script trong kết quả AI; viết lại một phần không đụng phần khác.
4. Test viết thêm mà **hỏng** vì code có lỗi: giữ test, đánh dấu `xfail` kèm lý do và số lỗi trong báo cáo (không xóa, không `skip`).

## Yêu cầu bảo mật riêng

S2, W1, W3, A2, D3.

## Tiêu chí xong

- [ ] Báo cáo tại `docs/team/reports/T-002-soi-loi.md`
- [ ] Bảng đối chiếu test an toàn bắt buộc
- [ ] Test mới chạy được trên máy không có `.env`, không gọi mạng
- [ ] `uv run pytest`, `uv run ruff check .` sạch (trừ `xfail` có lý do)

## Kiểm thử và kiểm định

- Lá Chắn: Rút gọn (soát test mới không chứa bí mật, không gọi mạng)
